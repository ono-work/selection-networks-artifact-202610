"""Strict provenance closure for the VDepth/UDepth tables, 1 <= t <= n <= 10.

STRICT MODE (the only mode). Nothing is seeded from a finished depth table,
from a previous run's summary JSON, or from "the paper says so". Every fact
entering the closure carries an explicit provenance type:

  1 structural   boundary value from a definition/theorem of the paper
  2 sorting      sorting-network inheritance from literature SDepth(n)
  3 unsat        direct network UNSAT / exhaustive-search lower bound
  4 witness      verified SAT witness upper bound
  5 game         finite-state additive weight-game evaluation (Theorem 3)
  6 nakano       Nakano-derived lower/upper bound
  7 propagated   DERIVED by the closure, never an input

The published tables appear in this file only as VERIFY_V / VERIFY_U, used
exclusively as the target to check the closure against. They are never
added to the closure state.

Usage:
    python3 experiments/provenance_closure/closure.py
"""
import json
import math
from pathlib import Path

HERE = Path(__file__).parent
NMAX = 10

# Literature sorting depths, n = 1..10 (Section IV of the paper).
SDEPTH = {1: 0, 2: 1, 3: 3, 4: 3, 5: 5, 6: 5, 7: 6, 8: 6, 9: 7, 10: 7}

# ---------------------------------------------------------------------
# VERIFICATION TARGET ONLY -- never injected into the closure.
# ---------------------------------------------------------------------
VERIFY_V = {
    1: {1: 0}, 2: {1: 1, 2: 1}, 3: {1: 2, 2: 3, 3: 3}, 4: {1: 2, 2: 3, 3: 3, 4: 3},
    5: {1: 3, 2: 4, 3: 5, 4: 5, 5: 5}, 6: {1: 3, 2: 4, 3: 5, 4: 5, 5: 5, 6: 5},
    7: {1: 3, 2: 5, 3: 6, 4: 6, 5: 6, 6: 6, 7: 6},
    8: {1: 3, 2: 5, 3: 6, 4: 6, 5: 6, 6: 6, 7: 6, 8: 6},
    9: {1: 4, 2: 6, 3: 6, 4: 7, 5: 7, 6: 7, 7: 7, 8: 7, 9: 7},
    10: {1: 4, 2: 6, 3: 6, 4: 7, 5: 7, 6: 7, 7: 7, 8: 7, 9: 7, 10: 7},
}
VERIFY_U = {
    1: {1: 0}, 2: {1: 1, 2: 0}, 3: {1: 2, 2: 2, 3: 0}, 4: {1: 2, 2: 2, 3: 2, 4: 0},
    5: {1: 3, 2: 3, 3: 3, 4: 3, 5: 0}, 6: {1: 3, 2: 4, 3: 3, 4: 4, 5: 3, 6: 0},
    7: {1: 3, 2: 4, 3: 4, 4: 4, 5: 4, 6: 3, 7: 0},
    8: {1: 3, 2: 4, 3: 4, 4: 4, 5: 4, 6: 4, 7: 3, 8: 0},
    9: {1: 4, 2: 5, 3: 5, 4: 5, 5: 5, 6: 5, 7: 5, 8: 4, 9: 0},
    10: {1: 4, 2: 5, 3: 5, 4: 5, 5: 5, 6: 5, 7: 5, 8: 5, 9: 4, 10: 0},
}

with open(HERE / "game_values_n_le_10.json") as f:
    GAME = json.load(f)


def game_A(kind, t, n):
    return GAME.get(f"{kind}_{t}_{n}")


def ceil_log2(x):
    return math.ceil(math.log2(x)) if x > 0 else 0


def floor_log2(x):
    return math.floor(math.log2(x)) if x > 0 else 0


def cells():
    for n in range(1, NMAX + 1):
        for t in range(1, n + 1):
            yield t, n


# ---------------------------------------------------------------------
# Always-available facts: structural, sorting inheritance, Nakano.
# These require no per-cell network computation of ours.
# ---------------------------------------------------------------------
def always_available():
    F = []
    for n in range(1, NMAX + 1):
        c = ceil_log2(n)
        # Corollary 1: VDepth(1,n) = UDepth(1,n) = ceil(log2 n)
        F.append(("V", 1, n, "exact", c, 1, "Corollary 1"))
        F.append(("U", 1, n, "exact", c, 1, "Corollary 1"))
        # UDepth(n,n) = 0 (identity network)
        F.append(("U", n, n, "exact", 0, 1, "definition: identity network"))
        # Theorem 1(f): VDepth(n-1,n) = VDepth(n,n) = SDepth(n)
        F.append(("V", n, n, "exact", SDEPTH[n], 1, "Thm 1(f) + literature SDepth"))
        if n >= 2:
            F.append(("V", n - 1, n, "exact", SDEPTH[n], 1, "Thm 1(f) + literature SDepth"))
        # sorting-network inheritance: upper bound for every t
        for t in range(1, n + 1):
            F.append(("V", t, n, "upper", SDEPTH[n], 2, "sorting inheritance"))
            F.append(("U", t, n, "upper", SDEPTH[n], 2, "sorting inheritance"))
    # Nakano exact t=2 family at n = 2^k
    for k in (1, 2, 3):
        n = 2 ** k
        F.append(("V", 2, n, "exact", k + ceil_log2(k), 6, "Nakano Thm 5 (t=2 power-of-two family)"))
        F.append(("U", 2, n, "exact", k + ceil_log2(k) - 1, 6, "Nakano Thm 5 (t=2 power-of-two family)"))
    # Nakano general t=2 corollary (two-sided), n >= 2
    for n in range(2, NMAX + 1):
        fl, cl = floor_log2(n), ceil_log2(n)
        lo = fl + (ceil_log2(fl) if fl >= 1 else 0)
        hi = cl + ceil_log2(cl)
        F.append(("V", 2, n, "lower", lo, 6, "Nakano Cor 4 (general t=2)"))
        F.append(("V", 2, n, "upper", hi, 6, "Nakano Cor 4 (general t=2)"))
        F.append(("U", 2, n, "lower", lo - 1, 6, "Nakano Cor 4 (general t=2, shifted)"))
        F.append(("U", 2, n, "upper", hi - 1, 6, "Nakano Cor 4 (general t=2, shifted)"))
    return F


# ---------------------------------------------------------------------
# Candidate direct inputs, each backed by an artifact in this repository.
# id -> (kind, t, n, bound, value, ptype, description)
# ---------------------------------------------------------------------
def build_pool():
    P = {}

    # --- (3) direct network UNSAT lower bounds, from scanned artifacts ---
    unsat = [
        ("V", 2, 5, 4, "milestone_3b_smoke V_t3_n5-style run; d3 UNSAT"),
        ("V", 2, 6, 4, "baseline/smoke; d3 UNSAT"),
        ("V", 2, 7, 5, "n10_selection_depth_completion/jobs/V_t2_n7_d4 (audited)"),
        ("V", 2, 8, 5, "baseline_n8; d4 UNSAT"),
        ("V", 2, 9, 6, "n10_selection_depth_completion/jobs/V_t2_n9_d5 (audited)"),
        ("V", 2, 10, 6, "baseline_n10/decisions/V_t2_n10; d5 UNSAT"),
        ("V", 3, 5, 5, "milestone_3b_smoke/V_t3_n5; d4 UNSAT (re-run confirmed)"),
        ("V", 3, 6, 5, "baseline/smoke; d4 UNSAT"),
        ("V", 3, 7, 6, "baseline_n7; d5 UNSAT"),
        ("V", 3, 8, 6, "baseline_n8; d5 UNSAT"),
        ("V", 3, 9, 6, "baseline_n9/decisions/V_t3_n9; d5 UNSAT"),
        ("V", 4, 5, 5, "smoke; d4 UNSAT"),
        ("V", 4, 6, 5, "smoke; d4 UNSAT"),
        ("V", 4, 7, 6, "baseline_n7; d5 UNSAT"),
        ("V", 4, 8, 6, "baseline_n8; d5 UNSAT"),
        ("U", 2, 5, 3, "smoke; d2 UNSAT"),
        ("U", 2, 6, 4, "smoke; d3 UNSAT"),
        ("U", 2, 8, 4, "baseline_n8; d3 UNSAT"),
        ("U", 2, 9, 5, "n10_selection_depth_completion/jobs/U_t2_n9_d4 (audited)"),
        ("U", 2, 10, 5, "baseline_n10/decisions/U_t2_n10; d4 UNSAT"),
        ("U", 3, 5, 3, "smoke; d2 UNSAT"),
        ("U", 3, 6, 3, "smoke; d2 UNSAT"),
        ("U", 3, 7, 4, "baseline_n7; d3 UNSAT"),
        ("U", 3, 8, 4, "baseline_n8; d3 UNSAT"),
        ("U", 3, 9, 5, "baseline_n9/decisions/U_t3_n9; d4 UNSAT"),
        ("U", 4, 5, 3, "smoke; d2 UNSAT"),
        ("U", 4, 6, 4, "smoke; d3 UNSAT"),
        ("U", 4, 8, 4, "baseline_n8; d3 UNSAT"),
        ("U", 4, 9, 5, "baseline_n9/decisions/U_t4_n9; d4 UNSAT"),
    ]
    for k, t, n, v, d in unsat:
        P[f"L_{k}{t}_{n}"] = (k, t, n, "lower", v, 3, d)

    # V(4,9) >= 7: the monolithic depth-6 run TIMED OUT (7200 s); the bound
    # comes from the partitioned closure campaign, audited AFFIRMATIVE.
    P["L_V4_9"] = ("V", 4, 9, "lower", 7, 3,
                   "v49_d6_final: partitioned closure campaign, 75 tail leaves UNSAT, "
                   "audit VERIFIED (monolithic depth-6 run timed out)")

    # --- (4) verified SAT witness upper bounds ---
    wit = [
        ("V", 2, 5, 4), ("V", 2, 6, 4), ("V", 2, 8, 5), ("V", 3, 5, 5), ("V", 3, 6, 5),
        ("V", 3, 7, 6), ("V", 3, 8, 6), ("V", 4, 5, 5), ("V", 4, 6, 5), ("V", 4, 7, 6),
        ("V", 4, 8, 6), ("V", 3, 9, 6), ("V", 4, 9, 7), ("V", 3, 10, 6),
        ("U", 2, 5, 3), ("U", 2, 6, 4), ("U", 2, 8, 4), ("U", 3, 5, 3), ("U", 3, 6, 3),
        ("U", 3, 7, 4), ("U", 3, 8, 4), ("U", 4, 5, 3), ("U", 4, 6, 4), ("U", 4, 8, 4),
        ("U", 3, 9, 5), ("U", 4, 9, 5),
        ("U", 2, 10, 5), ("U", 3, 10, 5), ("U", 4, 10, 5), ("U", 5, 10, 5),
    ]
    for k, t, n, v in wit:
        P[f"W_{k}{t}_{n}"] = (k, t, n, "upper", v, 4, f"verified depth-{v} witness")

    # --- (5) finite-state additive-game lower bounds, every cell ---
    for t, n in cells():
        for k in ("U", "V"):
            a = game_A(k, t, n)
            if a is not None and a > 0:
                P[f"G_{k}{t}_{n}"] = (k, t, n, "lower", a, 5, f"A_{k}({t},{n})={a}")
    return P


POOL = build_pool()
INF = 10 ** 9


def run_closure(active_ids, trace_cell=None):
    """Strict closure. Returns (LB, UB, why) with why[(kind,t,n)] listing
    the provenance of the binding lower and upper bound."""
    LB, UB, why = {}, {}, {}

    def note(key, side, ptype, desc):
        why.setdefault(key, {})[side] = (ptype, desc)

    def add_lower(k, t, n, v, ptype, desc):
        key = (k, t, n)
        if v > LB.get(key, -1):
            LB[key] = v
            note(key, "lower", ptype, desc)

    def add_upper(k, t, n, v, ptype, desc):
        key = (k, t, n)
        if v < UB.get(key, INF):
            UB[key] = v
            note(key, "upper", ptype, desc)

    def add(k, t, n, bound, v, ptype, desc):
        if bound in ("lower", "exact"):
            add_lower(k, t, n, v, ptype, desc)
        if bound in ("upper", "exact"):
            add_upper(k, t, n, v, ptype, desc)

    for k, t, n, bound, v, ptype, desc in always_available():
        add(k, t, n, bound, v, ptype, desc)
    for cid in active_ids:
        k, t, n, bound, v, ptype, desc = POOL[cid]
        add(k, t, n, bound, v, ptype, f"[{cid}] {desc}")

    changed, it = True, 0
    while changed:
        changed, it = False, it + 1
        if it > 200:
            raise RuntimeError("closure did not converge")
        for t, n in cells():
            # (a) UDepth <= VDepth
            u, v = ("U", t, n), ("V", t, n)
            if LB.get(u, 0) > LB.get(v, 0):
                LB[v] = LB[u]; note(v, "lower", 7, "Thm 1(a) from U"); changed = True
            if UB.get(v, INF) < UB.get(u, INF):
                UB[u] = UB[v]; note(u, "upper", 7, "Thm 1(a) from V"); changed = True
            # (b) n-monotonicity
            for k in ("U", "V"):
                if n + 1 <= NMAX and t <= n + 1:
                    lo, hi = (k, t, n), (k, t, n + 1)
                    if LB.get(lo, 0) > LB.get(hi, 0):
                        LB[hi] = LB[lo]; note(hi, "lower", 7, f"Thm 1(b) from {k}({t},{n})"); changed = True
                    if UB.get(hi, INF) < UB.get(lo, INF):
                        UB[lo] = UB[hi]; note(lo, "upper", 7, f"Thm 1(b) from {k}({t},{n+1})"); changed = True
            # (c) V t-monotonicity
            if t + 1 <= n:
                lo, hi = ("V", t, n), ("V", t + 1, n)
                if LB.get(lo, 0) > LB.get(hi, 0):
                    LB[hi] = LB[lo]; note(hi, "lower", 7, f"Thm 1(c) from V({t},{n})"); changed = True
                if UB.get(hi, INF) < UB.get(lo, INF):
                    UB[lo] = UB[hi]; note(lo, "upper", 7, f"Thm 1(c) from V({t+1},{n})"); changed = True
            # (d) U mirror duality
            if 1 <= n - t <= n:
                a, b = ("U", t, n), ("U", n - t, n)
                if LB.get(a, 0) > LB.get(b, 0):
                    LB[b] = LB[a]; note(b, "lower", 7, f"Thm 1(d) from U({t},{n})"); changed = True
                if UB.get(a, INF) < UB.get(b, INF):
                    UB[b] = UB[a]; note(b, "upper", 7, f"Thm 1(d) from U({t},{n})"); changed = True
    return LB, UB, why


def unclosed(LB, UB):
    """Cells not pinned to their verified exact value."""
    bad = []
    for n in range(1, NMAX + 1):
        for t in range(1, n + 1):
            for k, VER in (("V", VERIFY_V), ("U", VERIFY_U)):
                lo, hi = LB.get((k, t, n), 0), UB.get((k, t, n), INF)
                tgt = VER[n][t]
                if lo != tgt or hi != tgt:
                    bad.append((k, t, n, lo, hi, tgt))
    return bad


COST = {3: 0, 4: 1, 5: 2, 6: 3, 1: 4, 2: 5}  # try removing UNSAT first, game last


def find_irredundant(pool_ids):
    """Greedily remove inputs (most expensive provenance first) while the
    closure still reproduces every verified cell. Result is irredundant:
    no single remaining input can be dropped. Not claimed minimal."""
    keep = set(pool_ids)
    order = sorted(pool_ids, key=lambda c: (COST[POOL[c][5]], c))
    for cid in order:
        trial = keep - {cid}
        LB, UB, _ = run_closure(trial)
        if not unclosed(LB, UB):
            keep = trial
    return keep


if __name__ == "__main__":
    print("=" * 72)
    print("STEP 1  Closure from the FULL evidence pool (strict; no table injection)")
    print("=" * 72)
    LB, UB, _ = run_closure(set(POOL))
    bad = unclosed(LB, UB)
    print(f"  pool size = {len(POOL)}; unclosed cells = {len(bad)}")
    for b in bad:
        print("   ", b)

    print()
    print("=" * 72)
    print("STEP 2  The previously claimed 9-input set")
    print("=" * 72)
    claimed = {"L_V2_7", "L_V2_9", "L_V3_5", "L_V3_7", "L_V4_9", "L_U4_6",
               "G_U2_9", "G_U3_9", "G_U4_9"}
    claimed |= {c for c in POOL if POOL[c][5] == 4}  # keep all witnesses
    LB2, UB2, _ = run_closure(claimed)
    bad2 = unclosed(LB2, UB2)
    print(f"  6 UNSAT seeds + 3 game inputs (+ all witnesses): unclosed = {len(bad2)}")
    for k, t, n, lo, hi, tgt in bad2:
        print(f"    {k}({t},{n}): closure gives [{lo},{hi}], target {tgt}")

    print()
    print("=" * 72)
    print("STEP 3  Irredundant input set (greedy, UNSAT removed first)")
    print("=" * 72)
    keep = find_irredundant(set(POOL))
    by = {}
    for cid in keep:
        by.setdefault(POOL[cid][5], []).append(cid)
    names = {3: "direct UNSAT lower bound", 4: "verified witness upper bound",
             5: "finite-state game lower bound"}
    for pt in sorted(by):
        print(f"\n  --- type {pt}: {names.get(pt, pt)}  ({len(by[pt])}) ---")
        for cid in sorted(by[pt]):
            k, t, n, bound, v, _, d = POOL[cid]
            print(f"    {cid:12s} {k}({t},{n}) {bound} = {v}   {d}")
    print(f"\n  TOTALS: UNSAT={len(by.get(3,[]))}, witness={len(by.get(4,[]))}, "
          f"game={len(by.get(5,[]))}, all={len(keep)}")

    LBk, UBk, whyk = run_closure(keep)
    print(f"  joint check: unclosed with irredundant set = {len(unclosed(LBk,UBk))}")

    print()
    print("=" * 72)
    print("STEP 4  One-at-a-time irredundancy re-check")
    print("=" * 72)
    ok = True
    for cid in sorted(keep):
        LBr, UBr, _ = run_closure(keep - {cid})
        nb = unclosed(LBr, UBr)
        if not nb:
            print(f"    !! {cid} is still removable (NOT irredundant)")
            ok = False
    print("    all retained inputs are individually load-bearing" if ok else "    FAILED")

    print()
    print("=" * 72)
    print("STEP 5  Raw game value vs exact depth: match counts")
    print("=" * 72)
    allm, nonb = [], []
    for n in range(1, NMAX + 1):
        for t in range(1, n + 1):
            for k, VER in (("V", VERIFY_V), ("U", VERIFY_U)):
                if game_A(k, t, n) == VER[n][t]:
                    allm.append((k, t, n, VER[n][t]))
                    if not (t == 1 or t == n - 1 or t == n):
                        nonb.append((k, t, n, VER[n][t]))
    print(f"  raw A matches exact depth      : {len(allm)}")
    print(f"  excluding t=1, t=n-1, t=n      : {len(nonb)}")
    per = {}
    for k, t, n, v in nonb:
        per[n] = per.get(n, 0) + 1
    print(f"  non-boundary per n             : " +
          ", ".join(f"n={n}:{per.get(n,0)}" for n in range(1, NMAX + 1)))
    print(f"  non-boundary matches: {sorted(nonb, key=lambda x:(x[2],x[1],x[0]))}")

    json.dump({
        "irredundant_inputs": sorted(keep),
        "by_type": {str(k): sorted(v) for k, v in by.items()},
        "raw_matches": [f"{k}({t},{n})={v}" for k, t, n, v in allm],
        "nonboundary_matches": [f"{k}({t},{n})={v}" for k, t, n, v in nonb],
        "claimed_9_unclosed": [f"{k}({t},{n}) got [{lo},{hi}] want {tgt}"
                                for k, t, n, lo, hi, tgt in bad2],
    }, open(HERE / "closure_report.json", "w"), indent=1)
    print("\nWrote closure_report.json")
