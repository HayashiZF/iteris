<h1 align="center">Iteris Codex 插件</h1>

<p align="center">
  <strong>原作者: Frenzymath · PKU @ AI4Math</strong><br>
  面向计算数学的 agentic research loops（<a href="https://github.com/frenzymath/iteris">原仓库</a>）
</p>

<p align="center">
  <a href="README.md">English README</a>
  · <a href="https://frenzymath.com/blog/iteris/">博客</a>
  · <a href="https://github.com/frenzymath/iteris">Iteris</a>
  · <a href="docs/user-guide.md">用户指南</a>
  · <a href="#快速开始">快速开始</a>
  · <a href="#安全模型">安全模型</a>
</p>

<p align="center">
  <img alt="Version" src="https://img.shields.io/badge/version-0.1.0-blue">
  <img alt="License" src="https://img.shields.io/badge/license-Apache--2.0-green">
</p>

Iteris 是一个面向研究工作的 goal-driven agent workspace toolkit。它把题目材料、长期事实、任务池、验证记录、运行日志和最终结果组织在项目本地目录中，让研究者可以监督长期运行的 agentic research loop。

本仓库是原 Iteris 项目的精简版本，包含为 `Codex` 精选的 skills 和 subagents 提示词，用以复制类似的 agentic research loop 运行环境，但无需安装 `iteris` CLI。


## 快速开始

使用一键命令进行本地安装（将 `plugins/`、`.agents/` 和 `.codex/` 下载到当前目录）：

* **Linux/macOS:**
  ```bash
  curl -fsSL https://raw.githubusercontent.com/HayashiZF/iteris/plugin-codex/install.sh | bash
  ```
* **Windows (PowerShell):**
  ```powershell
  curl.exe -fsSL https://raw.githubusercontent.com/HayashiZF/iteris/plugin-codex/install.sh | sh
  ```

使用一键命令进行全局安装（下载并合并 `.codex/` 到 `~/`，其他目录仍下载到当前目录）：

* **Linux/macOS:**
  ```bash
  curl -fsSL https://raw.githubusercontent.com/HayashiZF/iteris/plugin-codex/install.sh | bash -s -- -global
  ```
* **Windows (PowerShell):**
  ```powershell
  curl.exe -fsSL https://raw.githubusercontent.com/HayashiZF/iteris/plugin-codex/install.sh | sh -s -- -global
  ```

## 环境要求

- Python 3.10+
- Git 和 ripgrep
- Codex (`codex`) 或 Claude Code (`claude`)




## 引用

如果你在科研工作中使用 Iteris，请引用：

```bibtex
@misc{chen2026iterisagenticresearchloops,
      title={Iteris: Agentic Research Loops for Computational Mathematics},
      author={Leheng Chen and Zihao Liu and Wanyi He and Bin Dong},
      year={2026},
      eprint={2606.02484},
      archivePrefix={arXiv},
      primaryClass={cs.AI},
      url={https://arxiv.org/abs/2606.02484},
}
```

## 许可证

Apache-2.0。参见 [LICENSE](LICENSE)。
