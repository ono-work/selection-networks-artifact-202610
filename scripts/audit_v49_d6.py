"""Read-only provenance audit for VDepth(4,9)=7 (depth-6 nonexistence).

Reconstructs the genealogy from the depth-6 candidate space down to stored
UNSAT artifacts, at branch granularity, and checks that a branch re-run under
a longer time limit really is the *same* candidate set (by hashing the solver
instance, not by trusting the job name).

Writes: v49_d6_branch_ledger.csv

Runs no solver and modifies no existing artifact.
"""
import csv
import hashlib
import json
from pathlib import Path

ROOT = Path("experiments")
L5 = ROOT / "v49_d6_l5_partitioned"
HERE = Path(__file__).parent


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()[:16] if p.exists() else ""


def find_instance(bid: str, where: str):
    """Locate instance.lp for branch `bid` under subtree `where`."""
    hits = [p for p in (L5 / where).rglob("instance.lp") if p.parent.name == bid]
    return hits[0] if hits else None


def branch_results():
    """branch_id -> list of (location, status, runtime, limit, instance_path)"""
    out = {}
    for p in L5.rglob("*.json"):
        try:
            d = json.load(open(p))
        except Exception:
            continue
        for o in (d if isinstance(d, list) else [d]):
            if not isinstance(o, dict):
                continue
            bid, st = o.get("branch_id") or o.get("id"), o.get("status")
            if not (bid and st):
                continue
            loc = p.relative_to(L5).parts[0]
            out.setdefault(str(bid), set()).add(
                (loc, str(st), round(o.get("runtime_seconds") or 0),
                 o.get("time_limit") or o.get("timeout_seconds"))
            )
    return out


def tail_leaves():
    """parent -> list of (leaf_id, status, candidate_count)"""
    led = ROOT / "v49_d6_final" / "tail_closure_ledger.csv"
    parents, leaves = {}, {}
    for r in csv.DictReader(open(led)):
        nid, par, st = r["node_id"], r["parent_node_id"], r["status"]
        cnt = r.get("compatible_L5_matching_count") or ""
        if r["closure_method"] == "EXHAUSTIVE_CENSUS":
            parents[nid] = {"child_count": int(r["child_count"] or 0),
                            "candidates": int(cnt or 0),
                            "cond": r["structural_condition"]}
        elif r["closure_method"] == "SOLVER_UNSAT":
            leaves.setdefault(par, []).append((nid, st, int(cnt or 0)))
    return parents, leaves


def main():
    res = branch_results()
    parents, leaves = tail_leaves()
    rows = []
    unresolved = []
    for bid in sorted(res):
        recs = sorted(res[bid])
        statuses = {s for _, s, _, _ in recs}
        final = "UNSAT" if "UNSAT" in statuses else "TIMEOUT"
        # identity check: does the re-run use the same instance as the first run?
        ib = find_instance(bid, "branches")
        il = find_instance(bid, "longrun")
        same = ""
        if ib and il:
            same = "SAME" if sha(ib) == sha(il) else "DIFFERENT"
        elif ib and not il:
            same = "no-rerun"
        handoff = ""
        if final == "TIMEOUT":
            if bid in parents:
                p = parents[bid]
                handoff = (f"partitioned into {p['child_count']} leaves "
                           f"({p['candidates']} candidate L5 matchings)")
                lv = leaves.get(bid, [])
                allu = all(s == "UNSATISFIABLE" for _, s, _ in lv)
                handoff += f"; {len(lv)} leaves, all UNSAT={allu}"
                if not (len(lv) == p["child_count"] and allu):
                    unresolved.append(bid)
            else:
                handoff = "NO SUCCESSOR FOUND"
                unresolved.append(bid)
        rows.append({
            "branch_id": bid,
            "runs": " | ".join(f"{l}:{s}({rt}s/limit {lim})" for l, s, rt, lim in recs),
            "instance_identity_first_vs_rerun": same,
            "final_status": final,
            "handoff": handoff,
        })

    with open(HERE / "v49_d6_branch_ledger.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)

    closed_direct = [r for r in rows if r["final_status"] == "UNSAT"]
    handed_off = [r for r in rows if r["final_status"] == "TIMEOUT"]
    print(f"branches total              : {len(rows)}")
    print(f"  closed by direct solver UNSAT : {len(closed_direct)}")
    print(f"  timed out, handed to tail     : {len(handed_off)}")
    for r in handed_off:
        print(f"      {r['branch_id']}: {r['handoff']}")
    ident = {r["instance_identity_first_vs_rerun"] for r in rows}
    print(f"  re-run instance identity      : {sorted(ident)}")
    diff = [r["branch_id"] for r in rows if r["instance_identity_first_vs_rerun"] == "DIFFERENT"]
    if diff:
        print(f"      !! differing instances: {diff}")
    print(f"\ntail parents: {len(parents)}  total leaves: {sum(len(v) for v in leaves.values())}")
    for p, info in parents.items():
        lv = leaves.get(p, [])
        print(f"  {p}: child_count={info['child_count']} leaves_found={len(lv)} "
              f"candidates={info['candidates']} allUNSAT={all(s=='UNSATISFIABLE' for _,s,_ in lv)} "
              f"leaf_candidate_sum={sum(c for _,_,c in lv)}")
        print(f"      cond: {info['cond']}")
    print(f"\nUNRESOLVED: {unresolved if unresolved else 'none'}")
    print(f"ledger -> {HERE/'v49_d6_branch_ledger.csv'}")


if __name__ == "__main__":
    main()
