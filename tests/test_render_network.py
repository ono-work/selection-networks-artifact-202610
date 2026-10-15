import json
from pathlib import Path

from src.render_network import (
    Provenance,
    Witness,
    load_witness,
    render_markdown,
    render_tikz,
    target_satisfied,
    trace_network,
    write_witness_files,
)
from src.verify import verify_binary


ROOT = Path(__file__).resolve().parents[1]
U_NETWORK = ROOT / "experiments" / "milestone_3b_smoke" / "U_t3_n6" / "depth_03" / "network.json"
U_SUMMARY = ROOT / "experiments" / "milestone_3b_smoke" / "U_t3_n6" / "summary.csv"
U_VERIFIER = ROOT / "experiments" / "milestone_3b_smoke" / "U_t3_n6" / "depth_03" / "verifier.json"
V_NETWORK = ROOT / "experiments" / "milestone_3b_smoke" / "V_t3_n6" / "depth_05" / "network.json"
V_SUMMARY = ROOT / "experiments" / "milestone_3b_smoke" / "V_t3_n6" / "summary.csv"
V_VERIFIER = ROOT / "experiments" / "milestone_3b_smoke" / "V_t3_n6" / "depth_05" / "verifier.json"


def test_markdown_rendering_is_deterministic():
    witness = Witness("U", 3, 1, 1, [[(1, 2)]])
    provenance = Provenance((0,), 1, True)
    verifier = {"ok": True, "message": "verified all binary inputs"}

    first = render_markdown(witness, verifier=verifier, provenance=provenance)
    second = render_markdown(witness, verifier=verifier, provenance=provenance)

    assert first == second
    assert "- Layer 1: (1,2)" in first
    assert "- shorter depths checked UNSAT: 0" in first
    assert "one depth-optimal witness selected from a SAT model" in first


def test_tikz_rendering_is_deterministic():
    witness = Witness("V", 2, 1, 1, [[(1, 2)]])

    expected = """\\begin{tikzpicture}[x=1.15cm,y=0.55cm,line cap=round]
  \\node[anchor=west] at (0,1) {V-type $n=2$, $t=1$, depth 1};
  \\draw (0,-1) -- (2,-1);
  \\node[anchor=east] at (-0.15,-1) {1};
  \\draw (0,-2) -- (2,-2);
  \\node[anchor=east] at (-0.15,-2) {2};
  \\node[anchor=south] at (1,-0.5) {L1};
  \\draw (1,-1) -- (1,-2);
  \\fill (1,-1) circle (0.07);
  \\fill (1,-2) circle (0.07);
\\end{tikzpicture}
"""
    assert render_tikz(witness) == expected


def test_trace_through_one_comparator_network_is_hand_checkable():
    witness = Witness("V", 2, 1, 1, [[(1, 2)]])

    trace = trace_network(witness, (9, 2))

    assert trace.input_values == (9, 2)
    assert trace.states == ((9, 2), (2, 9))
    assert trace.final_output == (2, 9)
    assert trace.target_satisfied is True
    assert target_satisfied("U", 1, (9, 2), (2, 9)) is True


def test_witness_dossier_generation_for_confirmed_targets(tmp_path):
    targets = [
        (U_NETWORK, U_SUMMARY, U_VERIFIER, "U_n6_t3_d3.md", "U_n6_t3_d3.tex"),
        (V_NETWORK, V_SUMMARY, V_VERIFIER, "V_n6_t3_d5.md", "V_n6_t3_d5.tex"),
    ]

    for network, summary, verifier, md_name, tex_name in targets:
        md_path, tex_path = write_witness_files(
            network_json=network,
            summary_csv=summary,
            verifier_json=verifier,
            markdown_path=tmp_path / md_name,
            tikz_path=tmp_path / tex_name,
            traces=[
                ("binary input with exactly t zeros: 010101", "010101"),
                ("binary input with fewer than t zeros: 111010", "111010"),
                ("distinct integer input: 9,2,7,1,5,3", "9,2,7,1,5,3"),
            ],
        )

        markdown = md_path.read_text(encoding="utf-8")
        tikz = tex_path.read_text(encoding="utf-8")
        assert "independent verifier result: True" in markdown
        assert "target satisfied | True" in markdown
        assert "\\begin{tikzpicture}" in tikz
        assert md_path.name == md_name
        assert tex_path.name == tex_name


def test_generated_witness_networks_pass_independent_python_verifier():
    for network_path in (U_NETWORK, V_NETWORK):
        witness = load_witness(network_path)
        result = verify_binary(witness.network, witness.n, witness.t, witness.kind)
        assert result.ok, result.message


def test_renderer_does_not_claim_comparator_count_optimality():
    for path in (
        ROOT / "experiments" / "witnesses" / "U_n6_t3_d3.md",
        ROOT / "experiments" / "witnesses" / "V_n6_t3_d5.md",
    ):
        text = path.read_text(encoding="utf-8")
        assert "comparator-count optimal." not in text
        assert "size-optimal" not in text
        assert "minimum-size" in text
        assert "not claimed" in text


def test_target_artifact_metadata_matches_expected_instances():
    expected = {
        U_NETWORK: ("U", 6, 3, 3),
        V_NETWORK: ("V", 6, 3, 5),
    }
    for path, metadata in expected.items():
        data = json.loads(path.read_text(encoding="utf-8"))
        assert (data["kind"], data["n"], data["t"], data["depth"]) == metadata
