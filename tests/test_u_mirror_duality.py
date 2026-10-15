import json
from pathlib import Path

import pytest

from src.network import depth, mirror_dual
from src.verify import verify_binary

FIXTURE_ROOT = Path(__file__).resolve().parents[1] / "experiments" / "milestone_3b_smoke"
EXPECTED_CONFIRMED_U_N_LE_6 = {
    (1, 1),
    (1, 2),
    (1, 3),
    (1, 4),
    (1, 5),
    (1, 6),
    (2, 2),
    (2, 3),
    (2, 4),
    (2, 5),
    (2, 6),
    (3, 3),
    (3, 4),
    (3, 5),
    (3, 6),
    (4, 4),
    (4, 5),
    (4, 6),
}


def _network_from_json(layers):
    return [[tuple(comparator) for comparator in layer] for layer in layers]


def _confirmed_u_networks_n_le_6():
    cases = []
    for path in sorted(FIXTURE_ROOT.glob("U_t*_n*/depth_*/network.json")):
        payload = json.loads(path.read_text(encoding="utf-8"))
        if payload["kind"] != "U" or payload["n"] > 6:
            continue
        cases.append(
            (
                payload["t"],
                payload["n"],
                payload["depth"],
                _network_from_json(payload["layers"]),
                path,
            )
        )
    return cases


def test_confirmed_u_fixture_set_is_complete_for_n_le_6():
    discovered = {
        (t, n)
        for t, n, _depth, _network, _path in _confirmed_u_networks_n_le_6()
    }
    assert discovered == EXPECTED_CONFIRMED_U_N_LE_6


@pytest.mark.parametrize(
    ("t", "n", "expected_depth", "network", "path"),
    _confirmed_u_networks_n_le_6(),
    ids=lambda value: value.name if isinstance(value, Path) else None,
)
def test_confirmed_u_networks_mirror_to_verified_duals(
    t, n, expected_depth, network, path
):
    assert verify_binary(network, n=n, t=t, kind="U").ok, path

    dual = mirror_dual(network, n)

    assert depth(dual) == expected_depth == depth(network)
    assert verify_binary(dual, n=n, t=n - t, kind="U").ok, path
