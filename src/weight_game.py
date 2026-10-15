"""Additive certificate-weight depth game for selection-network lower bounds.

Implements the game of the paper's Section "An Additive Weight-Game Lower
Bound" (Theorem: A_U(t,n) <= UDepth(t,n), A_V(t,n) <= VDepth(t,n)).

State: a tuple of length T = t+1, counts[w-1] = number of wires currently
carrying weight w, for w = 1..T (weight T is absorbing/saturated).

One round = a matching on the n current tokens; unmatched tokens are
unaffected, and each matched pair (a,b) with a <= b becomes
(min(a,b), min(T, a+b)). The search restricts to maximum matchings (proved
in the paper to lose no reachable domination) and prunes any state
dominated by another state already in the frontier (also proved sound:
domination is preserved by mirroring a matching pattern by sorted rank).

Domination targets, derived from componentwise domination of the sorted
target vector (1,...,t,(t+1)^{n-t}) [V] or (1^t,(t+1)^{n-t}) [U]:
  U-type Q_U(t,n): dominated iff count[T] >= n - t.
  V-type Q_V(t,n): dominated iff, letting S = all tokens with weight < T,
                   |S| <= t and sorted(S) ascending satisfies S_i >= i.
"""
from functools import lru_cache


def initial_state(n, T):
    c = [0] * T
    c[0] = n
    return tuple(c)


def dominates(counts_a, counts_b):
    """True if the weight multiset represented by counts_a dominates that of
    counts_b: sorted-ascending componentwise >=. Equivalent (standard fact)
    to: for every threshold v, #{tokens >= v} in a is >= that in b. We
    check via tail sums, which is exactly this threshold characterization
    and only needs the two count-vectors (same length T)."""
    tail_a = tail_b = 0
    for v in range(len(counts_a) - 1, -1, -1):
        tail_a += counts_a[v]
        tail_b += counts_b[v]
        if tail_a < tail_b:
            return False
    return True


def target_counts(kind, t, n, T):
    c = [0] * T
    if kind == "U":
        c[0] += t
        c[T - 1] += n - t
    else:
        for i in range(1, t + 1):
            c[i - 1] += 1
        c[T - 1] += n - t
    return tuple(c)


def u_dominates_target(counts, t, n, T):
    return counts[T - 1] >= (n - t)


def v_dominates_target(counts, t, n, T):
    if n - counts[T - 1] > t:
        return False
    s = []
    for w in range(1, T):
        s.extend([w] * counts[w - 1])
    s.sort()
    return all(val >= i for i, val in enumerate(s, start=1))


def _full_pairing_states(counts, T):
    """Set of all resulting count-vectors after pairing up every token in
    `counts` (assumes sum(counts) is even). Builds the result array
    directly via backtracking, deduplicating through a set."""
    results = set()
    work = list(counts)
    out = [0] * T

    def dist(j, rem, w, cur_i):
        if rem == 0:
            rec(cur_i + 1)
            return
        if j == T:
            return
        if work[j] == 0:
            dist(j + 1, rem, w, cur_i)
            return
        maxamt = min(work[j], rem)
        mx = min(T, w + (j + 1))
        for amt in range(maxamt, -1, -1):
            if amt > 0:
                work[j] -= amt
                out[w - 1] += amt
                out[mx - 1] += amt
            dist(j + 1, rem - amt, w, cur_i)
            if amt > 0:
                work[j] += amt
                out[w - 1] -= amt
                out[mx - 1] -= amt

    def rec(i):
        while i < T and work[i] == 0:
            i += 1
        if i == T:
            results.add(tuple(out))
            return
        w = i + 1
        r = work[i]
        for s in range(r // 2 + 1):
            remaining = r - 2 * s
            mx_self = min(T, 2 * w)
            if s > 0:
                out[w - 1] += s
                out[mx_self - 1] += s
            dist(i + 1, remaining, w, i)
            if s > 0:
                out[w - 1] -= s
                out[mx_self - 1] -= s

    rec(0)
    return results


def successors(counts, T):
    """All states reachable in one round from `counts` (maximum matchings
    only; see the module docstring for why this loses no domination)."""
    n = sum(counts)
    results = set()
    leftover_choices = [None]
    if n % 2 == 1:
        leftover_choices = [i for i in range(T) if counts[i] > 0]
    for lo in leftover_choices:
        base = list(counts)
        if lo is not None:
            base[lo] -= 1
        for new_counts in _full_pairing_states(tuple(base), T):
            nc = list(new_counts)
            if lo is not None:
                nc[lo] += 1
            results.add(tuple(nc))
    return results


@lru_cache(maxsize=None)
def successors_cached(counts, T):
    return frozenset(successors(counts, T))


def prune_frontier(states):
    """Keep only the Pareto-maximal (non-dominated) states."""
    states = list(states)
    keep = []
    for i, s in enumerate(states):
        if not any(s2 != s and dominates(s2, s) for j, s2 in enumerate(states) if j != i):
            keep.append(s)
    return list(set(keep))


def compute_A(kind, t, n, max_rounds=20, prune=True):
    """Returns (A, trace): A is the minimum rounds to dominate the target
    (or None if not reached within max_rounds), trace is a list of
    (round, frontier_size, sample_states) for reproducibility logging."""
    T = t + 1
    assert 1 <= t <= n
    start = initial_state(n, T)
    target = target_counts(kind, t, n, T)
    if dominates(start, target):
        return 0, [(0, 1, start)]
    frontier = {start}
    trace = [(0, 1, start)]
    for rnd in range(1, max_rounds + 1):
        newfrontier = set()
        for s in frontier:
            newfrontier |= successors_cached(s, T)
        if prune:
            newfrontier = set(prune_frontier(newfrontier))
        trace.append((rnd, len(newfrontier), sorted(newfrontier)[:3]))
        for s in newfrontier:
            if dominates(s, target):
                return rnd, trace
        frontier = newfrontier
        if not frontier:
            break
    return None, trace
