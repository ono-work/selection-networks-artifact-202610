"""Constructive upper-bound closure for U/V selection networks up to n=17."""

from __future__ import annotations

import argparse
import csv
import json
import math
import subprocess
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from src.network_composition import compose_binary_candidate_merge, load_network, network_to_payload
from src.verify import verify_binary

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "experiments" / "baseline_n11_17" / "constructive_upper_bounds"
DOC = ROOT / "docs" / "n11_17" / "constructive_upper_bound_closure.md"
GEN_DIR = OUT_DIR / "generated_networks"
MAX_N = 17
SORT_DEPTH = {1: 0, 2: 1, 3: 3, 4: 3, 5: 5, 6: 5, 7: 6, 8: 6, 9: 7, 10: 7, 11: 8, 12: 8, 13: 9, 14: 9, 15: 9, 16: 9, 17: 10}
SOURCE_REPORTS = [
    ROOT / "docs" / "n10" / "u_selection_decisions.md",
    ROOT / "docs" / "n10" / "v_selection_decisions.md",
    ROOT / "docs" / "n10" / "n10_v_selection_decisions.md",
    ROOT / "docs" / "n10" / "n10_depth_summary.md",
    ROOT / "experiments" / "baseline_n10" / "n10_depth_summary.json",
    ROOT / "docs" / "n11_17" / "u_milestone1_n11_n12.md",
    ROOT / "docs" / "n11_17" / "u_milestone1_depth6_upper_bounds.md",
    ROOT / "docs" / "n11_17" / "u_n12_central_depth7_upper_bounds.md",
    ROOT / "docs" / "n11_17" / "u_upper_bounds_n13_n14_depth7.md",
    ROOT / "docs" / "n11_17" / "u_upper_bounds_n13_n14_depth8.md",
    ROOT / "docs" / "n11_17" / "selection_bounds_summary.md",
    ROOT / "docs" / "n11_17" / "selection_bounds_notes.md",
]


def rel(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


@dataclass
class Derivation:
    id: str
    kind: str
    n: int
    t: int
    depth: int
    rule: str
    sources: list[str] = field(default_factory=list)
    source_entries: list[tuple[str, int, int]] = field(default_factory=list)
    provenance_type: str = "THEOREM_DERIVED"
    primary_source: str = ""
    network_path: str | None = None
    verifier_status: str = "not_applicable"
    notes: str = ""


@dataclass
class Entry:
    kind: str
    n: int
    t: int
    best_upper_bound: int | None = None
    derivations: list[str] = field(default_factory=list)
    exact_status: str = "UPPER_BOUND_ONLY"
    lower_bound_if_known: int | None = None
    lower_bound_provenance: str = ""


class Closure:
    def __init__(self, max_n: int = MAX_N):
        self.max_n = max_n
        self.entries: dict[tuple[str, int, int], Entry] = {}
        self.derivations: dict[str, Derivation] = {}
        self.rule_applications: list[dict[str, Any]] = []
        self._next_id = 1
        for kind in ["U", "V"]:
            for n in range(1, max_n + 1):
                for t in range(1, n + 1):
                    self.entries[(kind, n, t)] = Entry(kind, n, t)

    def add_bound(self, kind: str, n: int, t: int, depth: int, rule: str, *, sources: list[str] | None = None, source_entries: list[tuple[str, int, int]] | None = None, provenance_type: str = "THEOREM_DERIVED", primary_source: str = "", network_path: str | None = None, verifier_status: str = "not_applicable", notes: str = "", exact_status: str | None = None) -> bool:
        if not (1 <= n <= self.max_n and 1 <= t <= n and kind in {"U", "V"}):
            return False
        key = (kind, n, t)
        entry = self.entries[key]
        improved = entry.best_upper_bound is None or depth < entry.best_upper_bound
        tied = entry.best_upper_bound == depth
        if not (improved or tied):
            return False
        der_id = f"d{self._next_id}"
        self._next_id += 1
        der = Derivation(der_id, kind, n, t, depth, rule, sources or [], source_entries or [], provenance_type, primary_source, network_path, verifier_status, notes)
        self.derivations[der_id] = der
        if improved:
            entry.best_upper_bound = depth
            entry.derivations = [der_id]
            if exact_status:
                entry.exact_status = exact_status
        else:
            entry.derivations.append(der_id)
        self.rule_applications.append({
            "derivation_id": der_id,
            "improved": improved,
            "kind": kind,
            "n": n,
            "t": t,
            "depth": depth,
            "rule": rule,
            "sources": der.sources,
            "source_entries": [f"{k}({tt},{nn})" for k, nn, tt in der.source_entries],
            "provenance_type": provenance_type,
        })
        return improved

    def best(self, kind: str, n: int, t: int) -> int | None:
        return self.entries[(kind, n, t)].best_upper_bound

    def preferred_derivation(self, entry: Entry) -> Derivation | None:
        if not entry.derivations:
            return None
        priority = {"ARTIFACT_VERIFIED": 0, "GENERATED_VERIFIED": 1, "THEOREM_DERIVED": 2, "SORTING_FALLBACK": 3}
        return min((self.derivations[d] for d in entry.derivations), key=lambda d: (priority.get(d.provenance_type, 9), d.id))


def ceil_log2(n: int) -> int:
    return 0 if n <= 1 else math.ceil(math.log2(n))


def u2_power_depth(power: int) -> int:
    k = int(math.log2(power))
    return k + math.ceil(math.log2(k)) - 1 if k >= 1 else 0


def v2_power_depth(power: int) -> int:
    """VDepth(2,2^k) = k + ceil(log2(k)); citation still TODO."""
    k = int(math.log2(power))
    return k + math.ceil(math.log2(k)) if k >= 1 else 0


def load_network_facts() -> dict[tuple[str, int, int], dict[str, Any]]:
    facts: dict[tuple[str, int, int], dict[str, Any]] = {}
    for path in ROOT.glob("experiments/**/network.json"):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            continue
        kind = data.get("kind")
        n = data.get("n")
        t = data.get("t")
        depth = data.get("depth")
        if kind not in {"U", "V"} or not isinstance(n, int) or not isinstance(t, int) or not isinstance(depth, int):
            continue
        if n > MAX_N:
            continue
        key = (kind, n, t)
        old = facts.get(key)
        if old is None or depth < old["depth"]:
            result_path = path.with_name("result.json")
            verifier_path = path.with_name("verifier.json")
            facts[key] = {
                "kind": kind,
                "n": n,
                "t": t,
                "depth": depth,
                "network_path": rel(path),
                "result_path": rel(result_path) if result_path.exists() else None,
                "verifier_path": rel(verifier_path) if verifier_path.exists() else None,
                "verifier_status": "VERIFIED_SAT" if verifier_path.exists() else "artifact_present_not_replayed",
            }
    return facts


def apply_initial_facts(c: Closure, network_facts: dict[tuple[str, int, int], dict[str, Any]]) -> None:
    for n in range(1, MAX_N + 1):
        d = ceil_log2(n)
        for kind in ["U", "V"]:
            c.add_bound(kind, n, 1, d, "ONE_SELECTION", provenance_type="THEOREM_DERIVED", primary_source="ceil(log2 n)", notes="one-selection tournament upper bound")
        c.add_bound("U", n, n, 0, "U_ALL_WIRE_TRIVIAL", provenance_type="THEOREM_DERIVED", primary_source="definition", exact_status="EXACT_TRIVIAL")
        for t in range(1, n + 1):
            sd = SORT_DEPTH[n]
            c.add_bound("V", n, t, sd, "SORTING_FALLBACK", provenance_type="SORTING_FALLBACK", primary_source=f"SortDepth({n})={sd}", notes="full sorting network upper bound")
            if t != n:
                c.add_bound("U", n, t, sd, "SORTING_FALLBACK", provenance_type="SORTING_FALLBACK", primary_source=f"SortDepth({n})={sd}", notes="full sorting network upper bound")
    for power in [2, 4, 8, 16, 32]:
        if power <= MAX_N:
            c.add_bound("U", power, 2, u2_power_depth(power), "U2_POWER_OF_TWO_FORMULA", provenance_type="THEOREM_DERIVED", primary_source="U(2,2^k) formula")
            c.add_bound("V", power, 2, v2_power_depth(power), "V2_POWER_OF_TWO_FORMULA", provenance_type="THEOREM_DERIVED", primary_source="V(2,2^k) formula; citation TODO", notes="formula equality used here as an upper-bound fact; paper-ready citation TODO")
    for n in range(2, MAX_N + 1):
        K = 1 << ceil_log2(n)
        d = u2_power_depth(K)
        c.add_bound("U", n, 2, d, "U2_POWER_OF_TWO_PADDING", provenance_type="THEOREM_DERIVED", primary_source=f"UDepth(2,{K}) <= {d}", notes="padding/restriction from next power of two")
    # n=32 is outside the displayed table but supplies the n=17 padding anchor.
    c.add_bound("V", 17, 2, v2_power_depth(32), "PADDING_RESTRICTION", sources=["VDepth(2,32) = 8 by V2_POWER_OF_TWO_FORMULA"], provenance_type="THEOREM_DERIVED", primary_source="V(2,2^5) formula + padding; citation TODO", notes="external n=32 anchor; formula citation TODO")
    for (kind, n, t), fact in network_facts.items():
        c.add_bound(kind, n, t, fact["depth"], "KNOWN_NETWORK_ARTIFACT", provenance_type="ARTIFACT_VERIFIED" if fact["verifier_status"] == "VERIFIED_SAT" else "THEOREM_DERIVED", primary_source=fact["network_path"], network_path=fact["network_path"], verifier_status=fact["verifier_status"], notes="existing network.json artifact")


def iterate_closure(c: Closure) -> None:
    changed = True
    while changed:
        changed = False
        snapshot = {k: e.best_upper_bound for k, e in c.entries.items() if e.best_upper_bound is not None}
        # A padding/restriction from larger m to smaller n.
        for (kind, m, t), d in list(snapshot.items()):
            for n in range(t, m):
                changed |= c.add_bound(kind, n, t, d, "PADDING_RESTRICTION", sources=[f"{kind}Depth({t},{m}) <= {d}"], source_entries=[(kind, m, t)], provenance_type="THEOREM_DERIVED")
        # B U duality.
        for (kind, n, t), d in list(snapshot.items()):
            if kind == "U" and n - t >= 1:
                changed |= c.add_bound("U", n, n - t, d, "U_DUALITY", sources=[f"UDepth({t},{n}) <= {d}"], source_entries=[("U", n, t)], provenance_type="THEOREM_DERIVED", notes="U only")
        # C V implies U.
        for (kind, n, t), d in list(snapshot.items()):
            if kind == "V":
                changed |= c.add_bound("U", n, t, d, "V_IMPLIES_U", sources=[f"VDepth({t},{n}) <= {d}"], source_entries=[("V", n, t)], provenance_type="THEOREM_DERIVED")
        # D V t monotonicity.
        for (kind, n, t), d in list(snapshot.items()):
            if kind == "V":
                for s in range(1, t):
                    changed |= c.add_bound("V", n, s, d, "V_T_MONOTONICITY", sources=[f"VDepth({t},{n}) <= {d}"], source_entries=[("V", n, t)], provenance_type="THEOREM_DERIVED")
        # E/F/G binary merges.
        for n in range(2, c.max_n + 1):
            for t in range(1, n + 1):
                final_u = c.best("U", 2 * t, t) if 2 * t <= c.max_n else None
                final_v = c.best("V", 2 * t, t) if 2 * t <= c.max_n else None
                for n1 in range(t, n - t + 1):
                    n2 = n - n1
                    if n2 < t:
                        continue
                    lu = c.best("U", n1, t)
                    ru = c.best("U", n2, t)
                    if lu is not None and ru is not None and final_u is not None:
                        depth = max(lu, ru) + final_u
                        changed |= c.add_bound("U", n, t, depth, "U_BINARY_MERGE", sources=[f"U({t},{n1})", f"U({t},{n2})", f"U({t},{2*t})"], source_entries=[("U", n1, t), ("U", n2, t), ("U", 2*t, t)], provenance_type="THEOREM_DERIVED")
                    if lu is not None and ru is not None and final_v is not None:
                        depth = max(lu, ru) + final_v
                        changed |= c.add_bound("V", n, t, depth, "U_TO_V_BINARY_MERGE", sources=[f"U({t},{n1})", f"U({t},{n2})", f"V({t},{2*t})"], source_entries=[("U", n1, t), ("U", n2, t), ("V", 2*t, t)], provenance_type="THEOREM_DERIVED")
                    lv = c.best("V", n1, t)
                    rv = c.best("V", n2, t)
                    if lv is not None and rv is not None and final_v is not None:
                        depth = max(lv, rv) + final_v
                        changed |= c.add_bound("V", n, t, depth, "V_BINARY_MERGE_GENERIC", sources=[f"V({t},{n1})", f"V({t},{n2})", f"V({t},{2*t})"], source_entries=[("V", n1, t), ("V", n2, t), ("V", 2*t, t)], provenance_type="THEOREM_DERIVED")


def maybe_generate_networks(c: Closure, network_facts: dict[tuple[str, int, int], dict[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    GEN_DIR.mkdir(parents=True, exist_ok=True)
    manifest: list[dict[str, Any]] = []
    verification: list[dict[str, Any]] = []
    generated_by_key: dict[tuple[str, int, int], str] = {}
    # Generate only direct primary binary-merge entries whose components have existing/generated artifacts.
    for key, entry in sorted(c.entries.items()):
        der = c.preferred_derivation(entry)
        if der is None or der.rule not in {"U_BINARY_MERGE", "U_TO_V_BINARY_MERGE", "V_BINARY_MERGE_GENERIC"}:
            continue
        if entry.best_upper_bound is None or entry.best_upper_bound > 8:
            continue
        component_paths: list[str] = []
        ok = True
        for comp in der.source_entries:
            comp_path = None
            fact = network_facts.get(comp)
            if fact:
                comp_path = fact["network_path"]
            elif comp in generated_by_key:
                comp_path = generated_by_key[comp]
            if comp_path is None:
                ok = False
                break
            component_paths.append(comp_path)
        if not ok or len(component_paths) != 3:
            continue
        kind, n, t = key
        try:
            left = load_network(ROOT / component_paths[0])
            right = load_network(ROOT / component_paths[1])
            final = load_network(ROOT / component_paths[2])
            n1 = left["n"]
            n2 = right["n"]
            network = compose_binary_candidate_merge(n1=n1, n2=n2, t=t, left_network=left["layers"], right_network=right["layers"], final_network=final["layers"])
            if len(network) != entry.best_upper_bound:
                continue
        except Exception:
            continue
        name = f"{kind}_t{t}_n{n}_depth{len(network)}_by_{der.rule.lower()}"
        out = GEN_DIR / name
        out.mkdir(parents=True, exist_ok=True)
        network_path = out / "network.json"
        network_path.write_text(json.dumps(network_to_payload(network, kind=kind, n=n, t=t), indent=2, sort_keys=True) + "\n", encoding="utf-8")
        construction = {"derivation_id": der.id, "rule": der.rule, "components": component_paths, "kind": kind, "n": n, "t": t, "depth": len(network)}
        (out / "construction.json").write_text(json.dumps(construction, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        verdict = verify_binary(network, n=n, t=t, kind=kind) if n <= 17 else None
        verifier_payload = None if verdict is None else verdict.__dict__
        verifier_status = "not_run" if verdict is None else ("VERIFIED" if verdict.ok else "FAILED")
        (out / "verifier.json").write_text(json.dumps(verifier_payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        (out / "README.md").write_text(f"# {name}\n\nGenerated by constructive upper-bound closure. Verifier status: `{verifier_status}`.\n", encoding="utf-8")
        rec = {"kind": kind, "n": n, "t": t, "depth": len(network), "path": rel(network_path), "rule": der.rule, "verifier_status": verifier_status}
        manifest.append(rec)
        verification.append({**rec, "verifier": verifier_payload})
        if verifier_status == "VERIFIED":
            generated_by_key[key] = rel(network_path)
            der.network_path = rel(network_path)
            der.provenance_type = "GENERATED_VERIFIED"
            der.verifier_status = "VERIFIED"
    return manifest, verification


def source_audit() -> dict[str, Any]:
    return {
        "found": [rel(p) for p in SOURCE_REPORTS if p.exists()],
        "missing": [rel(p) for p in SOURCE_REPORTS if not p.exists()],
        "sorting_depth_citation_status": sorting_citation_status(),
    }


def sorting_citation_status() -> str:
    notes = ROOT / "docs" / "n11_17" / "selection_bounds_notes.md"
    if notes.exists() and "TODO_SORTING_DEPTH_CITATION" in notes.read_text(errors="ignore"):
        return f"local note candidate: {rel(notes)}; n=17 TODO_SORTING_DEPTH_CITATION"
    summary = ROOT / "docs" / "n11_17" / "selection_bounds_summary.md"
    if summary.exists():
        return f"local note candidate: {rel(summary)}"
    return "TODO_SORTING_DEPTH_CITATION"


def read_aborted_jobs() -> list[dict[str, Any]]:
    out = []
    for path in (ROOT / "experiments" / "baseline_n11_17" / "decisions").glob("U_t*_n*/depth_*/partial_status.json"):
        try:
            out.append(json.loads(path.read_text(encoding="utf-8")) | {"path": rel(path)})
        except Exception:
            pass
    return out


def lower_bounds_map() -> dict[tuple[str, int, int], int]:
    path = ROOT / "experiments" / "selection_bounds_n11_17" / "bounds_table.csv"
    m: dict[tuple[str, int, int], int] = {}
    if path.exists():
        with path.open(newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                try:
                    m[(row["kind"], int(row["n"]), int(row["t"]))] = int(row["lower_bound"])
                except Exception:
                    continue
    # VDepth(2,10)=6 from saved depth-5 UNSAT plus verified V(3,10) depth-6 witness.
    if (ROOT / "experiments/baseline_n10/n10_depth_summary.json").exists():
        for n in range(10, MAX_N + 1):
            m[("V", n, 2)] = max(m.get(("V", n, 2), 0), 6)
    return m


def lower_bound_provenance(key: tuple[str, int, int], lb: int) -> str:
    kind, n, t = key
    if kind == "V" and t == 2 and n >= 10 and lb >= 6:
        return ("VDepth(2,10)=6: experiments/baseline_n10/decisions/V_t2_n10/depth_05/ " +
                "verified V(3,10) depth-6 witness; N_MONOTONICITY_LOWER_FROM_N10")
    return "experiments/selection_bounds_n11_17/bounds_table.csv"


def write_outputs(c: Closure, manifest: list[dict[str, Any]], verification: list[dict[str, Any]], network_facts: dict[tuple[str, int, int], dict[str, Any]]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    audit = source_audit()
    lbs = lower_bounds_map()
    for key, lb in lbs.items():
        if key in c.entries:
            c.entries[key].lower_bound_if_known = lb
            c.entries[key].lower_bound_provenance = lower_bound_provenance(key, lb)
            if c.entries[key].best_upper_bound == lb:
                c.entries[key].exact_status = "EXACT"
    aborted = read_aborted_jobs()
    (OUT_DIR / "aborted_jobs_summary.json").write_text(json.dumps({"jobs": aborted}, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (OUT_DIR / "generated_networks_manifest.json").write_text(json.dumps({"generated_networks": manifest}, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (OUT_DIR / "verification_summary.json").write_text(json.dumps({"generated_networks": verification}, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    derivation_payload = {did: der.__dict__ for did, der in c.derivations.items()}
    (OUT_DIR / "derivation_trees.json").write_text(json.dumps(derivation_payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    with (OUT_DIR / "rule_applications.csv").open("w", newline="", encoding="utf-8") as f:
        fieldnames = ["derivation_id", "improved", "kind", "n", "t", "depth", "rule", "sources", "source_entries", "provenance_type"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in c.rule_applications:
            writer.writerow({k: json.dumps(row[k]) if isinstance(row.get(k), list) else row.get(k, "") for k in fieldnames})
    all_entries = []
    for kind in ["U", "V"]:
        path = OUT_DIR / f"upper_bounds_{kind}.csv"
        with path.open("w", newline="", encoding="utf-8") as f:
            fieldnames = ["kind", "n", "t", "best_upper_bound", "provenance_type", "primary_rule", "primary_source", "exact_status", "lower_bound_if_known", "lower_bound_provenance", "gap_if_known", "network_artifact_available", "generated_network_path", "verifier_status", "sorting_fallback", "notes"]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for n in range(1, MAX_N + 1):
                for t in range(1, n + 1):
                    e = c.entries[(kind, n, t)]
                    der = c.preferred_derivation(e)
                    lb = e.lower_bound_if_known
                    gap = None if lb is None or e.best_upper_bound is None else e.best_upper_bound - lb
                    row = {
                        "kind": kind,
                        "n": n,
                        "t": t,
                        "best_upper_bound": e.best_upper_bound,
                        "provenance_type": der.provenance_type if der else "",
                        "primary_rule": der.rule if der else "",
                        "primary_source": der.primary_source if der else "",
                        "exact_status": e.exact_status,
                        "lower_bound_if_known": lb,
                        "lower_bound_provenance": e.lower_bound_provenance,
                        "gap_if_known": gap,
                        "network_artifact_available": bool(der and der.network_path),
                        "generated_network_path": der.network_path if der else "",
                        "verifier_status": der.verifier_status if der else "",
                        "sorting_fallback": SORT_DEPTH[n],
                        "notes": der.notes if der else "",
                    }
                    writer.writerow(row)
                    all_entries.append(row)
    payload = {"generated_at": datetime.now(timezone.utc).isoformat(), "source_audit": audit, "theoretical_facts": {"V2_POWER_OF_TWO_FORMULA": {"formula": "VDepth(2,2^k) = k + ceil(log2 k)", "k_min": 1, "anchors_through_n": 32, "values": {"2": 1, "4": 3, "8": 5, "16": 6, "32": 8}, "provenance_type": "THEOREM_DERIVED", "citation_status": "citation TODO"}}, "entries": all_entries, "aborted_jobs": aborted}
    (OUT_DIR / "upper_bounds_all.json").write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_report(c, audit, manifest, verification, aborted)


def table_for(c: Closure, kind: str, min_n: int = 1) -> str:
    lines = []
    for n in range(min_n, MAX_N + 1):
        vals = [str(c.entries[(kind, n, t)].best_upper_bound) for t in range(1, n + 1)]
        lines.append(f"| {n} | " + " | ".join(vals) + " |")
    return "\n".join(lines)


def write_report(c: Closure, audit: dict[str, Any], manifest: list[dict[str, Any]], verification: list[dict[str, Any]], aborted: list[dict[str, Any]]) -> None:
    def notable(kind: str, n: int, t: int) -> str:
        e = c.entries[(kind, n, t)]
        der = c.preferred_derivation(e)
        return f"`{kind}({t},{n}) <= {e.best_upper_bound}` via `{der.rule if der else 'n/a'}`"
    frontier = []
    for kind in ["U", "V"]:
        for n in range(11, MAX_N + 1):
            for t in range(1, n + 1):
                e = c.entries[(kind, n, t)]
                if e.best_upper_bound is None or t in {1, n}:
                    continue
                lb = e.lower_bound_if_known
                gap = None if lb is None else e.best_upper_bound - lb
                if lb is None or gap > 0:
                    frontier.append((kind, n, t, e.best_upper_bound, lb, gap, e.best_upper_bound - 1))
    frontier = sorted(frontier, key=lambda x: (x[1], x[0], x[2]))[:40]
    md = [
        "# Constructive upper-bound closure for selection networks up to n=17",
        "",
        "## Scope",
        "",
        "This report builds U-type and V-type upper bounds by applying construction and closure rules to existing exact/verified witnesses, theoretical facts, and sorting fallback bounds. No solver run is introduced here. Existing small-t scouting jobs were checked first; the only partial stopped job recorded here is listed in the aborted-job summary when present.",
        "",
        "## Closure rules",
        "",
        "- `PADDING_RESTRICTION`: if `Depth_K(t,m) <= d` and `t <= n <= m`, then `Depth_K(t,n) <= d`.",
        "- `V2_POWER_OF_TWO_FORMULA`: `VDepth(2,2^k) = k + ceil(log2 k)` for k>=1. Citation status: `citation TODO`.",
        "- `U_DUALITY`: if `UDepth(t,n) <= d`, then `UDepth(n-t,n) <= d`; U only.",
        "- `V_IMPLIES_U`: if `VDepth(t,n) <= d`, then `UDepth(t,n) <= d`.",
        "- `V_T_MONOTONICITY`: if `VDepth(t,n) <= d` and `s <= t`, then `VDepth(s,n) <= d`; not applied to U.",
        "- `U_BINARY_MERGE`: `UDepth(t,n1+n2) <= max(U(t,n1), U(t,n2)) + U(t,2t)`.",
        "- `U_TO_V_BINARY_MERGE`: `VDepth(t,n1+n2) <= max(U(t,n1), U(t,n2)) + V(t,2t)`.",
        "- `V_BINARY_MERGE_GENERIC`: `VDepth(t,n1+n2) <= max(V(t,n1), V(t,n2)) + V(t,2t)`.",
        "- `SORTING_FALLBACK`: full sorting networks provide U/V upper bounds; n=17 sorting citation remains explicit below.",
        "",
        "## Initial facts and source audit",
        "",
        f"- Found sources: {', '.join('`'+x+'`' for x in audit['found'])}",
        f"- Missing sources: {', '.join('`'+x+'`' for x in audit['missing']) if audit['missing'] else 'none'}",
        f"- Sorting-depth citation status: `{audit['sorting_depth_citation_status']}`.",
        f"- Aborted job records: {len(aborted)}.",
        "",
        "## U-type upper-bound table",
        "",
        "Rows are n and cells are t=1..n best upper bounds.",
        "",
        table_for(c, "U"),
        "",
        "## U-type upper-bound table for n=11..17",
        "",
        table_for(c, "U", 11),
        "",
        "## V-type upper-bound table",
        "",
        table_for(c, "V"),
        "",
        "## V-type upper-bound table for n=11..17",
        "",
        table_for(c, "V", 11),
        "",
        "## Improvements over raw scouting",
        "",
        f"- {notable('U', 16, 2)}; U(2,n) for n<=16 is covered by the power-of-two formula plus padding/restriction.",
        "- `VDepth(2,n)=6` for 10<=n<=16: upper provenance is `V2_POWER_OF_TWO_FORMULA` plus `PADDING_RESTRICTION`; lower provenance is exact `VDepth(2,10)=6` plus `N_MONOTONICITY_LOWER_FROM_N10`.",
        f"- {notable('U', 14, 3)}; compare against depth-7 ASP scouting artifacts before treating this as a solver result.",
        f"- {notable('U', 14, 4)}; constructive closure records an upper bound even where blind scouting was hard.",
        "",
        "## Frontier entries for lower-bound work",
        "",
        "| kind | n | t | best D | known L | gap | candidate UNSAT depth | suggested next action |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |",
    ]
    for kind, n, t, D, L, gap, cand in frontier:
        md.append(f"| {kind} | {n} | {t} | {D} | {'' if L is None else L} | {'' if gap is None else gap} | {cand} | Check existing depth-{cand} artifacts, then plan certificate or witness construction. |")
    md.extend([
        "",
        "## Generated network verification summary",
        "",
    ])
    if manifest:
        md.append("| kind | n | t | depth | rule | verifier status | path |")
        md.append("| --- | ---: | ---: | ---: | --- | --- | --- |")
        for row in manifest:
            md.append(f"| {row['kind']} | {row['n']} | {row['t']} | {row['depth']} | `{row['rule']}` | `{row['verifier_status']}` | `{row['path']}` |")
    else:
        md.append("No generated networks were verified in this run; numeric construction bounds are still recorded where applicable.")
    md.extend([
        "",
        "## Caveats",
        "",
        "- This is an upper-bound closure table, not an exact-depth table.",
        "- The V(2,2^k) formula citation is TODO; it needs a paper-ready citation or an included proof before the final manuscript.",
        "- Padding gives upper bounds, not exactness.",
        "- U-duality is U-only.",
        "- V t-monotonicity is not applied to U.",
        "- n=17 sorting-depth citation status remains TODO if the source audit says so.",
        "- Runtime observations from previous scouting are not mathematical evidence except for verified SAT artifacts and saved UNSAT solver outputs.",
    ])
    DOC.parent.mkdir(parents=True, exist_ok=True)
    DOC.write_text("\n".join(md) + "\n", encoding="utf-8")


def build_closure(generate_networks: bool = True) -> tuple[Closure, dict[tuple[str, int, int], dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    c = Closure()
    facts = load_network_facts()
    apply_initial_facts(c, facts)
    iterate_closure(c)
    manifest, verification = maybe_generate_networks(c, facts) if generate_networks else ([], [])
    # Generated network derivations may update provenance, but we do not re-close on generated artifacts.
    return c, facts, manifest, verification


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.parse_args()
    c, facts, manifest, verification = build_closure(generate_networks=False)
    write_outputs(c, manifest, verification, facts)
    subprocess.run(["ps", "-eo", "pid,ppid,stat,etime,cmd"], check=False, capture_output=True, text=True)
    print(json.dumps({"output_dir": rel(OUT_DIR), "report": rel(DOC), "generated_networks": len(manifest), "entries": len(c.entries)}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
