"""Bound propagation for V/U selection-network depth planning.

This module records lower/upper bounds with derivations. It intentionally does
not call a solver; it is a bookkeeping engine for existing evidence and standard
propagation rules.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import math
from typing import Iterable, Literal

Kind = Literal["V", "U"]
Status = Literal["EXACT", "GAP", "ERROR"]
SourceStatus = Literal["CONFIRMED", "MISSING_OR_TODO"]


@dataclass(frozen=True)
class Derivation:
    rule: str
    source: str
    source_status: SourceStatus = "CONFIRMED"
    depends_on: tuple[tuple[str, int, int], ...] = ()
    artifacts: tuple[str, ...] = ()

    def summary(self) -> str:
        status = "" if self.source_status == "CONFIRMED" else " [MISSING_OR_TODO]"
        return f"{self.rule}: {self.source}{status}"


@dataclass
class BoundEntry:
    kind: Kind
    n: int
    t: int
    lower_bound: int | None = None
    upper_bound: int | None = None
    exact_value: int | None = None
    lower_derivations: list[Derivation] = field(default_factory=list)
    upper_derivations: list[Derivation] = field(default_factory=list)
    exact_derivations: list[Derivation] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    @property
    def status(self) -> Status:
        if self.errors or (
            self.lower_bound is not None
            and self.upper_bound is not None
            and self.lower_bound > self.upper_bound
        ):
            return "ERROR"
        if (
            self.lower_bound is not None
            and self.upper_bound is not None
            and self.lower_bound == self.upper_bound
        ):
            return "EXACT"
        return "GAP"

    @property
    def gap_size(self) -> int | None:
        if self.lower_bound is None or self.upper_bound is None:
            return None
        return self.upper_bound - self.lower_bound

    def derivation_summary(self) -> str:
        parts: list[str] = []
        if self.lower_derivations:
            parts.append("LB " + " | ".join(d.summary() for d in self.lower_derivations[-3:]))
        if self.upper_derivations:
            parts.append("UB " + " | ".join(d.summary() for d in self.upper_derivations[-3:]))
        if self.errors:
            parts.append("ERROR " + " | ".join(self.errors))
        return "; ".join(parts)

    def lower_sources(self) -> list[str]:
        return [d.summary() for d in self.lower_derivations]

    def upper_sources(self) -> list[str]:
        return [d.summary() for d in self.upper_derivations]


class BoundTable:
    def __init__(self, n_values: Iterable[int], kinds: Iterable[Kind] = ("V", "U")) -> None:
        self.n_values = sorted(set(n_values))
        self.entries: dict[tuple[Kind, int, int], BoundEntry] = {}
        self.derivations: list[dict[str, object]] = []
        for kind in kinds:
            for n in self.n_values:
                for t in range(1, n + 1):
                    self.entries[(kind, n, t)] = BoundEntry(kind=kind, n=n, t=t)

    def get(self, kind: Kind, n: int, t: int) -> BoundEntry:
        if (kind, n, t) not in self.entries:
            self.entries[(kind, n, t)] = BoundEntry(kind=kind, n=n, t=t)
            if n not in self.n_values:
                self.n_values.append(n)
                self.n_values.sort()
        return self.entries[(kind, n, t)]

    def _record(self, action: str, kind: Kind, n: int, t: int, value: int, derivation: Derivation) -> None:
        self.derivations.append(
            {
                "action": action,
                "kind": kind,
                "n": n,
                "t": t,
                "value": value,
                "rule": derivation.rule,
                "source": derivation.source,
                "source_status": derivation.source_status,
                "depends_on": [list(x) for x in derivation.depends_on],
                "artifacts": list(derivation.artifacts),
            }
        )

    def add_lower_bound(self, kind: Kind, n: int, t: int, value: int, derivation: Derivation) -> bool:
        entry = self.get(kind, n, t)
        changed = False
        if entry.lower_bound is None or value > entry.lower_bound:
            entry.lower_bound = value
            entry.lower_derivations.append(derivation)
            changed = True
            self._record("lower_bound", kind, n, t, value, derivation)
        elif value == entry.lower_bound:
            entry.lower_derivations.append(derivation)
        self._check_entry(entry)
        return changed

    def add_upper_bound(self, kind: Kind, n: int, t: int, value: int, derivation: Derivation) -> bool:
        entry = self.get(kind, n, t)
        changed = False
        if entry.upper_bound is None or value < entry.upper_bound:
            entry.upper_bound = value
            entry.upper_derivations.append(derivation)
            changed = True
            self._record("upper_bound", kind, n, t, value, derivation)
        elif value == entry.upper_bound:
            entry.upper_derivations.append(derivation)
        self._check_entry(entry)
        return changed

    def add_exact_value(self, kind: Kind, n: int, t: int, value: int, derivation: Derivation) -> bool:
        entry = self.get(kind, n, t)
        if entry.exact_value is not None and entry.exact_value != value:
            entry.errors.append(f"conflicting exact values: {entry.exact_value} vs {value}")
        entry.exact_value = value
        entry.exact_derivations.append(derivation)
        changed = False
        changed |= self.add_lower_bound(kind, n, t, value, derivation)
        changed |= self.add_upper_bound(kind, n, t, value, derivation)
        return changed

    def add_one_selection_exact(self, max_n: int) -> None:
        for n in range(1, max_n + 1):
            d = math.ceil(math.log2(n)) if n > 1 else 0
            for kind in ("V", "U"):
                if (kind, n, 1) in self.entries:
                    self.add_exact_value(kind, n, 1, d, Derivation("ONE_SELECTION", f"ceil(log2 {n})"))

    def add_u_all_wire_trivial(self) -> None:
        for n in self.n_values:
            self.add_exact_value("U", n, n, 0, Derivation("U_ALL_WIRE_TRIVIAL", "UDepth(n,n)=0"))

    def apply_sorting_upper_bounds(self, sorting_depths: dict[int, int], source: str, source_status: SourceStatus = "CONFIRMED") -> None:
        for n, depth in sorting_depths.items():
            if n not in self.n_values:
                continue
            for t in range(1, n + 1):
                self.add_upper_bound("V", n, t, depth, Derivation("SORTING_UPPER_BOUND", source, source_status))
                if t != n:
                    self.add_upper_bound("U", n, t, depth, Derivation("SORTING_UPPER_BOUND", source, source_status))
            self.add_exact_value("V", n, n, depth, Derivation("V_FULL_SORTING", "VDepth(n,n)=SortDepth(n)", source_status))
            if n > 1:
                self.add_exact_value("V", n, n - 1, depth, Derivation("V_N_MINUS_ONE_SORTING", "VDepth(n-1,n)=SortDepth(n)", source_status))

    def propagate_n_monotonicity(self) -> None:
        changed = True
        while changed:
            changed = False
            snapshot = list(self.entries.values())
            for e in snapshot:
                if e.lower_bound is not None:
                    for n2 in self.n_values:
                        if n2 < e.n or e.t > n2 or n2 == e.n:
                            continue
                        changed |= self.add_lower_bound(
                            e.kind,
                            n2,
                            e.t,
                            e.lower_bound,
                            Derivation(
                                "N_MONOTONICITY_LOWER",
                                f"{e.kind}Depth({e.t},{e.n}) >= {e.lower_bound}",
                                depends_on=((e.kind, e.n, e.t),),
                            ),
                        )
                if e.upper_bound is not None:
                    for n2 in self.n_values:
                        if n2 > e.n or e.t > n2 or n2 == e.n:
                            continue
                        changed |= self.add_upper_bound(
                            e.kind,
                            n2,
                            e.t,
                            e.upper_bound,
                            Derivation(
                                "N_MONOTONICITY_UPPER",
                                f"{e.kind}Depth({e.t},{e.n}) <= {e.upper_bound}",
                                depends_on=((e.kind, e.n, e.t),),
                            ),
                        )

    def propagate_v_t_monotonicity(self) -> None:
        changed = True
        while changed:
            changed = False
            for e in list(self.entries.values()):
                if e.kind != "V":
                    continue
                if e.upper_bound is not None:
                    for s in range(1, e.t):
                        changed |= self.add_upper_bound(
                            "V",
                            e.n,
                            s,
                            e.upper_bound,
                            Derivation("V_WITNESS_T_MONOTONICITY", f"V({e.t},{e.n}) witness implies V({s},{e.n}) witness", depends_on=(("V", e.n, e.t),)),
                        )
                if e.lower_bound is not None:
                    for t2 in range(e.t + 1, e.n + 1):
                        changed |= self.add_lower_bound(
                            "V",
                            e.n,
                            t2,
                            e.lower_bound,
                            Derivation("V_LOWER_T_MONOTONICITY", f"V({e.t},{e.n}) lower bound applies to V({t2},{e.n})", depends_on=(("V", e.n, e.t),)),
                        )

    def propagate_u_duality(self) -> None:
        changed = True
        while changed:
            changed = False
            for e in list(self.entries.values()):
                if e.kind != "U":
                    continue
                dual_t = e.n - e.t
                if dual_t < 1 or dual_t > e.n:
                    continue
                dual = self.get("U", e.n, dual_t)
                if e.lower_bound is not None:
                    changed |= self.add_lower_bound("U", e.n, dual_t, e.lower_bound, Derivation("U_DUALITY_LOWER", f"UDepth({e.t},{e.n})=UDepth({dual_t},{e.n})", depends_on=(("U", e.n, e.t),)))
                if e.upper_bound is not None:
                    changed |= self.add_upper_bound("U", e.n, dual_t, e.upper_bound, Derivation("U_DUALITY_UPPER", f"UDepth({e.t},{e.n})=UDepth({dual_t},{e.n})", depends_on=(("U", e.n, e.t),)))
                if e.exact_value is not None and dual.exact_value is not None and e.exact_value != dual.exact_value:
                    e.errors.append(f"U-duality conflict with U({dual_t},{e.n})={dual.exact_value}")

    def propagate_v_to_u_upper_bounds(self) -> None:
        for e in list(self.entries.values()):
            if e.kind == "V" and e.upper_bound is not None and ("U", e.n, e.t) in self.entries:
                self.add_upper_bound("U", e.n, e.t, e.upper_bound, Derivation("V_TO_U_UPPER", f"V({e.t},{e.n}) witness is also U({e.t},{e.n}) witness", depends_on=(("V", e.n, e.t),)))

    def propagate_u_to_v_lower_bounds(self) -> None:
        for e in list(self.entries.values()):
            if e.kind == "U" and e.lower_bound is not None and ("V", e.n, e.t) in self.entries:
                self.add_lower_bound(
                    "V",
                    e.n,
                    e.t,
                    e.lower_bound,
                    Derivation(
                        "U_TO_V_LOWER",
                        f"UDepth({e.t},{e.n}) lower bound applies because UDepth <= VDepth",
                        depends_on=(("U", e.n, e.t),),
                    ),
                )

    def propagate_all(self) -> None:
        changed_signature = None
        while True:
            self.propagate_n_monotonicity()
            self.propagate_v_t_monotonicity()
            self.propagate_u_duality()
            self.propagate_v_to_u_upper_bounds()
            self.propagate_u_to_v_lower_bounds()
            signature = tuple(sorted((k, e.lower_bound, e.upper_bound, tuple(e.errors)) for k, e in self.entries.items()))
            if signature == changed_signature:
                break
            changed_signature = signature

    def detect_exact_entries(self) -> list[BoundEntry]:
        exact = []
        for e in self.entries.values():
            self._check_entry(e)
            if e.status == "EXACT":
                exact.append(e)
        return exact

    def _check_entry(self, entry: BoundEntry) -> None:
        if entry.lower_bound is not None and entry.upper_bound is not None and entry.lower_bound > entry.upper_bound:
            msg = f"lower_bound {entry.lower_bound} exceeds upper_bound {entry.upper_bound}"
            if msg not in entry.errors:
                entry.errors.append(msg)
        if entry.exact_value is not None:
            if entry.lower_bound is not None and entry.lower_bound > entry.exact_value:
                entry.errors.append(f"lower_bound {entry.lower_bound} exceeds exact {entry.exact_value}")
            if entry.upper_bound is not None and entry.upper_bound < entry.exact_value:
                entry.errors.append(f"upper_bound {entry.upper_bound} below exact {entry.exact_value}")

    def explain_entry(self, kind: Kind, n: int, t: int) -> str:
        e = self.get(kind, n, t)
        lb = "?" if e.lower_bound is None else str(e.lower_bound)
        ub = "?" if e.upper_bound is None else str(e.upper_bound)
        return f"{kind}({t},{n}): [{lb},{ub}] {e.status}; {e.derivation_summary()}"

    def rows(self, n_min: int | None = None, n_max: int | None = None) -> list[BoundEntry]:
        out = []
        for key in sorted(self.entries):
            e = self.entries[key]
            if n_min is not None and e.n < n_min:
                continue
            if n_max is not None and e.n > n_max:
                continue
            out.append(e)
        return out
