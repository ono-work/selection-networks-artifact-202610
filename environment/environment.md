# Original Experimental Environment

All computations reported in the paper were run on a single machine.

| Item | Value |
| --- | --- |
| Machine | `thor` |
| OS | Linux 6.17.0-1021-nvidia (Ubuntu), SMP PREEMPT_DYNAMIC |
| Architecture | aarch64 |
| Python | 3.12.3 |
| clingo | 5.8.0 (pyclingo), installed as the Python package `clingo` in a project virtualenv |
| Solver invocation | `.venv/bin/python -m clingo --outf=2 --time-limit=<T> -n 1 solver/common.lp solver/target_{v|u}.lp <instance.lp>` |

Notes:

- There was **no standalone `clingo` binary**. All solver runs used the
  pyclingo module entry point `python -m clingo`. Reproduction instructions
  in this artifact do the same (`pip install clingo==5.8.0`).
- The original source repository was a git checkout at commit
  `7c06ad41aa6b9037ce471cebc143dae24897f5f5` with substantial uncommitted
  work; `original_git_status.txt` in this directory is the verbatim
  `git status --porcelain` of that working tree at packaging time
  (2026-10-15). The experiment outputs copied into this artifact are the
  authoritative record of those runs.
- **Historical path change.** The original checkout lived at
  `/home/ono/Codex` and was later moved to `/home/ono/Agent`. Historical
  logs, `command.txt` files, and certificates may contain either absolute
  prefix; the two refer to the same repository. Evidence files in this
  artifact were copied byte-for-byte and intentionally **not** rewritten.
- Independent witness verification (`src/verify.py`) is pure Python and has
  no solver dependency.
