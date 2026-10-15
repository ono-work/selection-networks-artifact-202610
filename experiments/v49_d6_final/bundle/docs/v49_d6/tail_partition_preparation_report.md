# V(4,9) Depth-6 Tail Partition Preparation Report

## Phase 1

Topology-pruning regression status: `PASSED`.

The optional pruning layer is safe to enable for the special hard-mode tail
runner. It remains disabled by default and is not part of the ordinary baseline
ASP model.

Regression artifact:
`experiments/v49_d6_topology_pruning/regression_report.md`

## Phase 2

L5 census coverage status: `PASSED`.

| parent branch | compatible L5 matchings | nonempty categories |
| --- | ---: | ---: |
| A5_residual_L5eq3 | 1060 | 9 |
| B6_residual_L5eq3 | 974 | 57 |
| B6_residual_L5eq4 | 672 | 9 |

Coverage certificate:
`experiments/v49_d6_l5_tail_census/coverage_certificate.json`

## Phase 3

Generated child solver branches: 75.

Partition plan:
`experiments/v49_d6_tail_partitioned/reports/partition_plan.md`

## Commands

Pilot without topology pruning:

```sh
./scripts/run_v49_d6_tail_partitioned.sh --mode pilot --timeout-seconds 1800 --workers 6 --clingo-threads 1
```

Pilot with topology pruning:

```sh
./scripts/run_v49_d6_tail_partitioned.sh --mode pilot --timeout-seconds 1800 --workers 6 --clingo-threads 1 --enable-topology-pruning
```

Process monitoring in tmux:

```sh
tmux new-session -A -s v49-d6-tail
ps -u "$USER" -o pid,ppid,pcpu,pmem,etime,cmd --sort=-pcpu | grep -E 'clingo|run_v49_d6_tail_partitioned'
```

Report viewing:

```sh
tail -f experiments/v49_d6_tail_partitioned/reports/partition_plan.md
```

No solver pilot or long-run was launched during this preparation task.
