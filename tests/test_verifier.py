from src.verify import randomized_integer_sanity, verify_binary


def test_verifier_rejects_invalid_non_matching_layer():
    result = verify_binary([[(1, 2), (2, 3)]], n=3, t=1, kind="V")
    assert not result.ok
    assert "not a matching" in result.message


def test_depth_zero_verification_behavior():
    assert verify_binary([], n=3, t=0, kind="V").ok

    result = verify_binary([], n=2, t=1, kind="V")
    assert not result.ok
    assert result.counterexample == (1, 0)
    assert result.output == (1, 0)
    assert result.expected == (0,)


def test_v_and_u_verification_on_small_hand_written_networks():
    one_comparator = [[(1, 2)]]
    assert verify_binary(one_comparator, n=2, t=1, kind="V").ok
    assert verify_binary(one_comparator, n=2, t=1, kind="U").ok
    assert verify_binary(one_comparator, n=2, t=2, kind="V").ok
    assert verify_binary(one_comparator, n=2, t=2, kind="U").ok

    sort_three = [[(1, 2)], [(2, 3)], [(1, 2)]]
    assert verify_binary(sort_three, n=3, t=2, kind="V").ok
    assert verify_binary(sort_three, n=3, t=2, kind="U").ok


def test_exhaustive_binary_verification_finds_failure():
    result = verify_binary([[(1, 2)]], n=3, t=2, kind="U")
    assert not result.ok
    assert result.counterexample is not None
    assert result.output is not None


def test_randomized_integer_sanity_is_separate_optional_check():
    sort_three = [[(1, 2)], [(2, 3)], [(1, 2)]]
    result = randomized_integer_sanity(
        sort_three,
        n=3,
        t=2,
        kind="V",
        trials=20,
        value_range=(-3, 3),
        seed=1,
    )
    assert result.ok
