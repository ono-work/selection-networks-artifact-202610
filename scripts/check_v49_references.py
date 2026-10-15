#!/usr/bin/env python3
"""Integrity check for the V(4,9) depth-6 nonexistence evidence.

Verifies, against the copies stored in this artifact, that:

  1. every file listed in evidence_manifest.json exists in the frozen
     bundle with the recorded SHA-256, and also exists as a live copy;
  2. every entry of bundle.sha256 verifies;
  3. every evidence file referenced by proof_dependency_graph.json exists,
     and every hash record in the graph matches -- except two documented
     divergences (see KNOWN_DIVERGENCES below);
  4. every absolute-path branch artifact referenced by the closure
     coverage certificate exists (after mapping the historical repository
     prefixes /home/ono/Codex and /home/ono/Agent into this artifact).

Repository-relative paths (experiments/..., docs/..., tests/..., src/...,
solver/...) are resolved against the bases listed in BASES, in order.

Usage:
  python3 scripts/check_v49_references.py
Exit code 0 iff all checks pass.
"""
import csv
import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FINAL = ROOT / "experiments/v49_d6_final"

# Evidence paths are repository-relative and this artifact preserves the
# original repository-relative layout, so everything resolves at ROOT.
BASES = [ROOT]

# Two files changed in the original repository after the frozen bundle was
# written; both divergences are documented in provenance/ARTIFACT_INVENTORY.md:
#   - coverage_certificate.json: absolute path prefix rewrite only
#     (/home/ono/Codex -> /home/ono/Agent), no content change;
#   - src/experiment.py: extended after bundling (run_depth_decision,
#     stderr capture); the bundle preserves the version used.
KNOWN_DIVERGENCES = {
    "experiments/v49_d6_closure_audit/coverage_certificate.json",
    "src/experiment.py",
}


def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for ch in iter(lambda: f.read(1 << 20), b""):
            h.update(ch)
    return h.hexdigest()


def resolve(rel: str):
    for base in BASES:
        p = base / rel
        if p.exists():
            return p
    return None


def main():
    problems = []
    expected_divergences_seen = set()

    # ---- 1. evidence manifest ------------------------------------------------
    man = json.load(open(FINAL / "evidence_manifest.json"))
    n_bundle_ok = 0
    for rec in man["files"]:
        bp = FINAL / rec["bundle_path"]
        if not bp.exists():
            problems.append(f"bundle file missing: {rec['bundle_path']}")
            continue
        if sha256(bp) != rec["sha256"]:
            problems.append(f"bundle hash mismatch: {rec['bundle_path']}")
            continue
        n_bundle_ok += 1
        live = resolve(rec["path"])
        if live is None:
            problems.append(f"live copy missing: {rec['path']}")
        elif sha256(live) != rec["sha256"]:
            if rec["path"] in KNOWN_DIVERGENCES:
                expected_divergences_seen.add(rec["path"])
            else:
                problems.append(f"live hash mismatch: {rec['path']}")
    print(f"evidence_manifest: {n_bundle_ok}/{len(man['files'])} bundle files verified")

    # ---- 2. bundle.sha256 ----------------------------------------------------
    n_ok = 0
    for line in open(FINAL / "bundle.sha256"):
        line = line.strip()
        if not line:
            continue
        digest, rel = line.split(maxsplit=1)
        p = FINAL / rel
        if not p.exists() or sha256(p) != digest:
            problems.append(f"bundle.sha256 failure: {rel}")
        else:
            n_ok += 1
    print(f"bundle.sha256    : {n_ok} entries verified")

    # ---- 3. proof dependency graph -------------------------------------------
    g = json.load(open(FINAL / "proof_dependency_graph.json"))
    n_ev, n_hash = 0, 0
    for node in g["nodes"]:
        for rel in node.get("evidence_files", []):
            if resolve(rel) is None:
                problems.append(f"graph evidence missing ({node['id']}): {rel}")
            else:
                n_ev += 1
        for h in node.get("hashes", []):
            p = resolve(h["path"])
            if p is None:
                problems.append(f"graph hash target missing: {h['path']}")
            elif sha256(p) != h["sha256"]:
                if h["path"] in KNOWN_DIVERGENCES:
                    expected_divergences_seen.add(h["path"])
                else:
                    problems.append(f"graph hash mismatch: {h['path']}")
            else:
                n_hash += 1
    print(f"dependency graph : {n_ev} evidence files present, "
          f"{n_hash} hash records match")

    # ---- 4. closure certificate branch artifacts -----------------------------
    cert = json.load(open(ROOT / "experiments/v49_d6_closure_audit/"
                          "coverage_certificate.json"))
    refs = sorted({m.group(1) for m in re.finditer(
        r'"/home/ono/(?:Codex|Agent)/(experiments/[^"]+)"', json.dumps(cert))})
    n_ref = 0
    for rel in refs:
        if resolve(rel) is None:
            problems.append(f"closure-certificate artifact missing: {rel}")
        else:
            n_ref += 1
    print(f"closure cert     : {n_ref}/{len(refs)} absolute-path branch "
          f"artifacts resolved")

    # ---- summary ---------------------------------------------------------
    print(f"known divergences observed (expected): "
          f"{sorted(expected_divergences_seen)}")
    if problems:
        print(f"\n{len(problems)} PROBLEMS:", file=sys.stderr)
        for p in problems[:40]:
            print(" ", p, file=sys.stderr)
        sys.exit(1)
    print("V49 REFERENCE CHECK OK")


if __name__ == "__main__":
    main()
