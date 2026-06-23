<h1 align="center">Iteris Codex Plugin</h1>

<p align="center">
  <strong>Original Authors: Frenzymath · PKU @ AI4Math</strong><br>
  Agentic research loops for computational mathematics (<a href="https://github.com/frenzymath/iteris">Original Repository</a>)
</p>

<p align="center">
  <a href="README.zh-CN.md">中文说明</a>
  · <a href="https://frenzymath.com/blog/iteris/">Blog</a>
  · <a href="https://github.com/frenzymath/iteris">Iteris</a>
  · <a href="docs/user-guide.md">User guide</a>
  · <a href="#quick-start">Quick start</a>
  · <a href="#security-model">Security model</a>
</p>

<p align="center">
  <img alt="Version" src="https://img.shields.io/badge/version-0.1.0-blue">
  <img alt="License" src="https://img.shields.io/badge/license-Apache--2.0-green">
</p>

Iteris is a goal-driven research agent workspace toolkit. It keeps source
materials, durable facts, task pools, verification records, live logs, and final
artifacts in one project-local layout so researchers can supervise long-running
agentic research loops.

This repo is a distilled version of the original Iteris project, consisting of curated skills and subagents prompts for `Codex` to replicate a similar agentic research loop runtime, but without the installation of `iteris` CLI.


## Quick Start

To install locally using a one-liner (downloads `plugins/`, `.agents/`, and `.codex/` to the current directory):

```bash
curl -fsSL https://raw.githubusercontent.com/HayashiZF/iteris/plugin-codex/install.sh | bash
```

To install globally (downloads/merges `.codex/` to `~/` and others to the current directory):

```bash
curl -fsSL https://raw.githubusercontent.com/HayashiZF/iteris/plugin-codex/install.sh | bash -s -- -global
```

## Requirements

- Python 3.10+
- Git and ripgrep
- Codex (`codex`) or Claude Code (`claude`)




## Citation

If you use Iteris in research, please cite:

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

## License

Apache-2.0. See [LICENSE](LICENSE).
