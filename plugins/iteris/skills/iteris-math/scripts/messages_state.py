from __future__ import annotations

import argparse
import json
import uuid

from _common import append_jsonl, now_iso, read_jsonl, resolve_root


def send(project_root: str, *, message: str, priority: str = "normal") -> dict:
    root = resolve_root(project_root)
    payload = {
        "msg_id": str(uuid.uuid4()),
        "created_at": now_iso(),
        "priority": priority,
        "message": message,
    }
    append_jsonl(root / "messages" / "inbox.jsonl", payload)
    return payload


def list_messages(project_root: str, unread_only: bool = False) -> list[dict]:
    root = resolve_root(project_root)
    inbox = read_jsonl(root / "messages" / "inbox.jsonl")
    if not unread_only:
        return inbox
    acked = {str(item.get("msg_id")) for item in read_jsonl(root / "messages" / "ack.jsonl") if item.get("msg_id")}
    return [item for item in inbox if str(item.get("msg_id") or "") not in acked]


def ack(project_root: str, *, msg_id: str, disposition: str) -> dict:
    root = resolve_root(project_root)
    payload = {"msg_id": msg_id, "disposition": disposition, "acked_at": now_iso()}
    append_jsonl(root / "messages" / "ack.jsonl", payload)
    return payload


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="cmd", required=True)
    p_send = sub.add_parser("send")
    p_send.add_argument("project_root")
    p_send.add_argument("--message", required=True)
    p_send.add_argument("--priority", default="normal")
    p_list = sub.add_parser("list")
    p_list.add_argument("project_root")
    p_list.add_argument("--unread-only", action="store_true")
    p_ack = sub.add_parser("ack")
    p_ack.add_argument("project_root")
    p_ack.add_argument("--msg-id", required=True)
    p_ack.add_argument("--disposition", required=True)
    args = parser.parse_args(argv)
    if args.cmd == "send":
        payload = send(args.project_root, message=args.message, priority=args.priority)
    elif args.cmd == "list":
        payload = list_messages(args.project_root, unread_only=args.unread_only)
    else:
        payload = ack(args.project_root, msg_id=args.msg_id, disposition=args.disposition)
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
