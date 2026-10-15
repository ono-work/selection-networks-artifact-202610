from pathlib import Path

from src.run_v49_d6_tail_partitioned import (
    ScreeningResult,
    branch_definitions,
    build_screening_queue,
    screening_command,
    write_screening_report,
)


def test_screening_queue_is_parent_round_robin_by_census_then_branch_id() -> None:
    jobs = build_screening_queue(branch_definitions())
    assert len(jobs) == 75
    assert [job.queue_position for job in jobs] == list(range(1, 76))

    by_parent = {}
    for job in jobs:
        by_parent.setdefault(job.definition.parent_branch_id, []).append(job.definition)
    for rows in by_parent.values():
        assert rows == sorted(rows, key=lambda definition: (definition.category_matching_count, definition.branch_id))

    assert [job.definition.parent_branch_id for job in jobs[:9]] == [
        "A5_residual_L5eq3",
        "B6_residual_L5eq3",
        "B6_residual_L5eq4",
        "A5_residual_L5eq3",
        "B6_residual_L5eq3",
        "B6_residual_L5eq4",
        "A5_residual_L5eq3",
        "B6_residual_L5eq3",
        "B6_residual_L5eq4",
    ]


def test_screening_command_pins_required_mode_and_topology_pruning(tmp_path: Path) -> None:
    assert screening_command(tmp_path) == [
        "./scripts/run_v49_d6_tail_partitioned.sh",
        "--mode",
        "screening",
        "--enable-topology-pruning",
        "--output-dir",
        str(tmp_path),
    ]


def test_screening_report_contains_required_sections(tmp_path: Path) -> None:
    jobs = build_screening_queue(branch_definitions())
    first = jobs[0].definition
    result = ScreeningResult(
        queue_position=1,
        dispatch_time="2026-07-07T00:00:00Z",
        branch_id=first.branch_id,
        parent_family=first.parent_branch_id,
        census_matching_count=first.category_matching_count,
        status="TIMEOUT",
        runtime_seconds=600.0,
        timeout_seconds=600,
        command=["clingo"],
        peak_rss_kb=123,
        cpu_snapshots=2,
        clingo_result="UNKNOWN",
        verifier_ok=None,
        instance_path="instance.lp",
        raw_json_path="solver.json",
        stderr_path="stderr.log",
        resource_log_path="resources.jsonl",
        metadata_path="metadata.json",
        branch_definition_path="branch_definition.json",
        result_path="result.json",
        network_path=None,
        stats=None,
        choices=None,
        conflicts=None,
        restarts=None,
        solving_time=None,
    )
    metadata = {
        "command_line": screening_command(tmp_path),
        "clingo_version": "clingo-test",
        "host": {"gpu_use": "none"},
        "git_head": "HEAD",
        "dirty_worktree_state": "dirty",
    }
    report = tmp_path / "screening_report.md"
    write_screening_report(report, jobs, [result], metadata, None)
    text = report.read_text(encoding="utf-8")
    assert "Dynamic worker-pool scheduling" in text
    assert "| TIMEOUT | 1 |" in text
    assert "remaining timed-out branches" in text
    assert "run a longer wave on specifically named timeout branches" in text
