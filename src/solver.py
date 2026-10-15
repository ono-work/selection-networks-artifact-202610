"""Minimal clingo invocation and result parsing for ASP smoke checks."""

from __future__ import annotations

import subprocess
from dataclasses import dataclass
from pathlib import Path

CLINGO_COMMAND = (".venv/bin/python", "-m", "clingo")


@dataclass(frozen=True)
class ClingoResult:
    """Parsed clingo status with the original process output."""

    command: tuple[str, ...]
    status: str
    stdout: str
    stderr: str
    returncode: int

    @property
    def satisfiable(self) -> bool:
        return self.status == "SATISFIABLE"

    @property
    def unsatisfiable(self) -> bool:
        return self.status == "UNSATISFIABLE"


def parse_clingo_status(stdout: str) -> str:
    """Return clingo's final SAT/UNSAT status from stdout."""
    for line in reversed(stdout.splitlines()):
        status = line.strip()
        if status in {"SATISFIABLE", "UNSATISFIABLE"}:
            return status
    raise ValueError("clingo output did not contain SATISFIABLE or UNSATISFIABLE")


def run_clingo(program: Path | str) -> ClingoResult:
    """Run the canonical local clingo command against one ASP program."""
    command = (*CLINGO_COMMAND, str(program))
    completed = subprocess.run(
        command,
        check=False,
        capture_output=True,
        text=True,
    )
    status = parse_clingo_status(completed.stdout)
    return ClingoResult(
        command=command,
        status=status,
        stdout=completed.stdout,
        stderr=completed.stderr,
        returncode=completed.returncode,
    )
