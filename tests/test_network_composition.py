from src.network_composition import compose_binary_candidate_merge, embed_network_on_wires, relabel_network, shift_network


def test_relabel_network_orders_endpoints():
    assert relabel_network([[(1, 2)]], {1: 5, 2: 3}) == [[(3, 5)]]


def test_embed_network_on_wires():
    assert embed_network_on_wires([[(1, 3), (2, 4)]], [2, 4, 6, 8]) == [[(2, 6), (4, 8)]]


def test_shift_network():
    assert shift_network([[(1, 2)], [(2, 3)]], 4) == [[(5, 6)], [(6, 7)]]


def test_compose_binary_candidate_merge_depth_and_embedding():
    left = [[(1, 2)]]
    right = [[(1, 2)]]
    final = [[(1, 3), (2, 4)]]
    network = compose_binary_candidate_merge(n1=3, n2=3, t=2, left_network=left, right_network=right, final_network=final)
    assert network == [[(1, 2)], [(4, 5)], [(1, 4), (2, 5)]]
