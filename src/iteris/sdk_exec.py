"""SDK-backed headless executor helpers for Codex and Claude."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from iteris.executors import EXECUTOR_CLAUDE, EXECUTOR_CODEX


def _write_event(handle: Any, payload: dict[str, Any]) -> None:
    handle.write(json.dumps(payload, ensure_ascii=False) + "\n")
    handle.flush()


def run_headless_executor_from_env() -> int:
    """Run one SDK-backed headless executor from environment variables.

    This helper is designed to execute inside a child Python process so the
    parent can retain its existing timeout, stderr capture, and process-group
    management around a single subprocess regardless of backend.
    """
    executor = os.environ["ITERIS_SDK_EXECUTOR"]
    project_root = Path(os.environ["ITERIS_PROJECT_ROOT"]).resolve()
    prompt_path = Path(os.environ["ITERIS_SDK_PROMPT_PATH"]).resolve()
    events_path = Path(os.environ["ITERIS_SDK_EVENTS_PATH"]).resolve()
    prompt = prompt_path.read_text(encoding="utf-8")
    model = os.environ.get("ITERIS_SDK_MODEL") or None
    reasoning_effort = os.environ.get("ITERIS_SDK_REASONING_EFFORT") or None

    events_path.parent.mkdir(parents=True, exist_ok=True)
    with events_path.open("w", encoding="utf-8") as events_handle:
        if executor == EXECUTOR_CODEX:
            return _run_codex_sdk(
                project_root=project_root,
                prompt=prompt,
                model=model,
                reasoning_effort=reasoning_effort,
                events_handle=events_handle,
            )
        if executor == EXECUTOR_CLAUDE:
            return _run_claude_sdk(
                project_root=project_root,
                prompt=prompt,
                model=model,
                reasoning_effort=reasoning_effort,
                events_handle=events_handle,
            )
        raise RuntimeError(f"unsupported sdk executor: {executor}")


def _run_codex_sdk(
    *,
    project_root: Path,
    prompt: str,
    model: str | None,
    reasoning_effort: str | None,
    events_handle: Any,
) -> int:
    from openai_codex import ApprovalMode, Codex, CodexConfig, ReasoningEffort, Sandbox

    config_overrides: tuple[str, ...] = ()
    if reasoning_effort:
        config_overrides = (f"model_reasoning_effort={reasoning_effort}",)

    with Codex(
        config=CodexConfig(
            cwd=str(project_root),
            env=os.environ.copy(),
            config_overrides=config_overrides,
        )
    ) as codex:
        thread = codex.thread_start(
            cwd=str(project_root),
            model=model,
            approval_mode=ApprovalMode.deny_all,
            sandbox=Sandbox.full_access,
            config={"model_reasoning_effort": reasoning_effort} if reasoning_effort else None,
        )
        _write_event(events_handle, {"type": "thread.started", "thread_id": thread.id})
        turn = thread.turn(
            prompt,
            cwd=str(project_root),
            model=model,
            effort=ReasoningEffort(reasoning_effort) if reasoning_effort else None,
            sandbox=Sandbox.full_access,
            approval_mode=ApprovalMode.deny_all,
        )
        completed_usage: dict[str, Any] | None = None
        completed_status: str | None = None
        for event in turn.stream():
            wire_event = _codex_stream_event_to_json(event)
            if wire_event is not None:
                _write_event(events_handle, wire_event)
            method = getattr(event, "method", "")
            payload = getattr(event, "payload", None)
            if method == "turn/completed" and payload is not None:
                turn_payload = getattr(payload, "turn", None)
                usage = getattr(payload, "token_usage", None)
                completed_usage = _model_dump(usage) if usage is not None else None
                if turn_payload is not None:
                    completed_status = str(getattr(turn_payload, "status", "") or "")
        return 0 if (completed_status or "").lower().endswith("completed") else 1


def _run_claude_sdk(
    *,
    project_root: Path,
    prompt: str,
    model: str | None,
    reasoning_effort: str | None,
    events_handle: Any,
) -> int:
    import anyio
    from claude_agent_sdk import (
        AssistantMessage,
        ClaudeAgentOptions,
        ResultMessage,
        TextBlock,
        ToolResultBlock,
        ToolUseBlock,
        query,
    )

    async def _main() -> int:
        session_id: str | None = None
        options = ClaudeAgentOptions(
            cwd=str(project_root),
            model=model,
            permission_mode="bypassPermissions",
            allowed_tools=["Bash", "Read", "Edit", "Write", "Glob", "Grep", "LS", "WebFetch", "Task"],
            effort=reasoning_effort if reasoning_effort in {"low", "medium", "high", "xhigh", "max"} else None,
            env=os.environ.copy(),
        )
        async for message in query(prompt=prompt, options=options):
            if isinstance(message, AssistantMessage):
                session_id = message.session_id or session_id
                payload = {
                    "type": "assistant",
                    "session_id": session_id,
                    "message": {
                        "model": message.model,
                        "content": [_claude_block_to_json(block) for block in message.content],
                    },
                }
                if message.usage:
                    payload["message"]["usage"] = message.usage
                _write_event(events_handle, payload)
                continue
            if isinstance(message, ResultMessage):
                session_id = message.session_id or session_id
                _write_event(
                    events_handle,
                    {
                        "type": "result",
                        "subtype": message.subtype,
                        "session_id": session_id,
                        "result": message.result,
                        "is_error": message.is_error,
                        "usage": message.usage,
                        "model_usage": message.model_usage,
                        "errors": message.errors,
                    },
                )
                return 1 if message.is_error else 0
            _write_event(events_handle, {"type": "sdk_message", "message": repr(message)})
        return 1

    return int(anyio.run(_main))


def _model_dump(value: Any) -> dict[str, Any]:
    if hasattr(value, "model_dump"):
        return value.model_dump(by_alias=True, exclude_none=True, mode="json")
    if hasattr(value, "__dict__"):
        return {key: val for key, val in vars(value).items() if val is not None}
    raise TypeError(f"cannot serialize sdk value {type(value).__name__}")


def _codex_stream_event_to_json(event: Any) -> dict[str, Any] | None:
    method = getattr(event, "method", "")
    payload = getattr(event, "payload", None)
    if method == "turn/started":
        turn = getattr(payload, "turn", None)
        return {"type": "turn.started", "turn": _model_dump(turn)} if turn is not None else {"type": "turn.started"}
    if method == "turn/completed":
        turn = getattr(payload, "turn", None)
        token_usage = getattr(payload, "token_usage", None)
        return {
            "type": "turn.completed",
            "turn": _model_dump(turn) if turn is not None else {},
            "usage": _model_dump(token_usage) if token_usage is not None else {},
        }
    if method == "item/completed":
        item = getattr(payload, "item", None)
        if item is None:
            return None
        return {"type": "item.completed", "item": _thread_item_to_json(item)}
    if method == "item/agentMessage/delta":
        delta = getattr(payload, "delta", None)
        if delta:
            return {"type": "item.delta", "item": {"type": "agent_message_delta", "text": str(delta)}}
    if method == "turn/errored":
        err = getattr(payload, "error", None)
        return {"type": "turn.error", "error": _model_dump(err) if err is not None else {}}
    return None


def _thread_item_to_json(item: Any) -> dict[str, Any]:
    root = getattr(item, "root", item)
    item_type = getattr(root, "type", None)
    data = _model_dump(root)
    if item_type == "agentMessage" and "text" in data:
        return {"type": "agent_message", "text": data.get("text", ""), **data}
    if item_type == "commandExecution":
        command = data.get("command") or ""
        output = data.get("aggregatedOutput") or data.get("aggregated_output") or ""
        exit_code = data.get("exitCode", data.get("exit_code"))
        status = data.get("status")
        return {
            "type": "command_execution",
            "command": command,
            "aggregated_output": output,
            "exit_code": exit_code,
            "status": status,
            **data,
        }
    if item_type == "fileChange":
        changes = data.get("changes") or []
        return {"type": "file_change", "changes": changes, **data}
    if item_type == "webSearch":
        return {
            "type": "web_search",
            "query": data.get("query"),
            "action": data.get("action"),
            **data,
        }
    return {"type": str(item_type or "item"), **data}


def _claude_block_to_json(block: Any) -> dict[str, Any]:
    from claude_agent_sdk import TextBlock, ToolResultBlock, ToolUseBlock

    if isinstance(block, TextBlock):
        return {"type": "text", "text": block.text}
    if isinstance(block, ToolUseBlock):
        return {"type": "tool_use", "id": block.id, "name": block.name, "input": block.input}
    if isinstance(block, ToolResultBlock):
        return {"type": "tool_result", "tool_use_id": block.tool_use_id, "content": block.content, "is_error": block.is_error}
    return {"type": type(block).__name__, "repr": repr(block)}


if __name__ == "__main__":
    raise SystemExit(run_headless_executor_from_env())
