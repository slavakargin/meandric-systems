"""Tests for meandric systems package (0-indexed convention)."""

import pytest
from meandric import (
    partition_to_pairing,
    pairing_to_partition,
    tree_pair_to_meandric,
    meandric_to_tree_pair,
    meandric_components,
    reduce_tree_pair,
    reduce_meandric,
    is_reduced,
    multiply_tree_pairs,
    multiply_meandric,
    invert_tree_pair,
    invert_meandric,
    X0_DOMAIN, X0_RANGE,
    X1_DOMAIN, X1_RANGE,
)


# ── partition ↔ pairing round-trips ────────────────────────────────────

PARTITION_PAIRING_CASES = [
    (['0', '1'],                [(0, 1)]),
    (['0', '10', '11'],         [(0, 3), (1, 2)]),
    (['00', '01', '1'],         [(0, 1), (2, 3)]),
    (['0', '10', '110', '111'], [(0, 5), (1, 2), (3, 4)]),
    (['00', '01', '10', '11'],  [(0, 5), (1, 4), (2, 3)]),
]


@pytest.mark.parametrize("partition, pairing", PARTITION_PAIRING_CASES)
def test_partition_to_pairing(partition, pairing):
    assert partition_to_pairing(partition) == pairing


@pytest.mark.parametrize("partition, pairing", PARTITION_PAIRING_CASES)
def test_pairing_to_partition(partition, pairing):
    assert pairing_to_partition(pairing) == partition


@pytest.mark.parametrize("partition, pairing", PARTITION_PAIRING_CASES)
def test_round_trip_partition(partition, pairing):
    assert pairing_to_partition(partition_to_pairing(partition)) == partition


@pytest.mark.parametrize("partition, pairing", PARTITION_PAIRING_CASES)
def test_round_trip_pairing(partition, pairing):
    assert partition_to_pairing(pairing_to_partition(pairing)) == pairing


# ── x_0 ───────────────────────────────────────────────────────────────

def test_x0_meandric():
    top, bot = tree_pair_to_meandric(X0_DOMAIN, X0_RANGE)
    assert top == [(0, 3), (1, 2)]
    assert bot == [(0, 1), (2, 3)]


def test_x0_one_component():
    top, bot = tree_pair_to_meandric(X0_DOMAIN, X0_RANGE)
    comps = meandric_components(top, bot)
    assert len(comps) == 1
    assert sorted(comps[0]) == [0, 1, 2, 3]


def test_x0_round_trip():
    top, bot = tree_pair_to_meandric(X0_DOMAIN, X0_RANGE)
    d, r = meandric_to_tree_pair(top, bot)
    assert d == X0_DOMAIN
    assert r == X0_RANGE


# ── x_1 ───────────────────────────────────────────────────────────────

def test_x1_meandric():
    top, bot = tree_pair_to_meandric(X1_DOMAIN, X1_RANGE)
    assert top == [(0, 5), (1, 2), (3, 4)]
    assert bot == [(0, 3), (1, 2), (4, 5)]


def test_x1_two_components():
    top, bot = tree_pair_to_meandric(X1_DOMAIN, X1_RANGE)
    comps = meandric_components(top, bot)
    assert len(comps) == 2
    sizes = sorted(len(c) for c in comps)
    assert sizes == [2, 4]


def test_x1_trivial_loop():
    """The pair (1,2) in both top and bottom gives the trivial loop."""
    top, bot = tree_pair_to_meandric(X1_DOMAIN, X1_RANGE)
    comps = meandric_components(top, bot)
    small = [c for c in comps if len(c) == 2][0]
    assert sorted(small) == [1, 2]


def test_x1_round_trip():
    top, bot = tree_pair_to_meandric(X1_DOMAIN, X1_RANGE)
    d, r = meandric_to_tree_pair(top, bot)
    assert d == X1_DOMAIN
    assert r == X1_RANGE


# ── identity ──────────────────────────────────────────────────────────

def test_identity_all_trivial_loops():
    """The identity has the same tree pair, so all loops are trivial."""
    partition = ['00', '01', '10', '11']
    top, bot = tree_pair_to_meandric(partition, partition)
    assert top == bot
    comps = meandric_components(top, bot)
    assert all(len(c) == 2 for c in comps)


# ── edge cases ────────────────────────────────────────────────────────

def test_single_caret():
    assert partition_to_pairing(['0', '1']) == [(0, 1)]
    assert pairing_to_partition([(0, 1)]) == ['0', '1']


def test_mismatched_leaves_raises():
    with pytest.raises(ValueError):
        tree_pair_to_meandric(['0', '1'], ['00', '01', '1'])

# ── reduction ─────────────────────────────────────────────────────────

def test_x0_already_reduced():
    top, bot = tree_pair_to_meandric(X0_DOMAIN, X0_RANGE)
    assert is_reduced(top, bot)


def test_x1_already_reduced():
    top, bot = tree_pair_to_meandric(X1_DOMAIN, X1_RANGE)
    assert is_reduced(top, bot)


def test_reduce_x0_exp_leaf0():
    """x_0 expanded at leaf 0: no trivial loop, but reducible."""
    top, bot = tree_pair_to_meandric(
        ['00', '01', '10', '11'], ['000', '001', '01', '1'])
    assert not is_reduced(top, bot)
    rt, rb = reduce_meandric(top, bot)
    t0, b0 = tree_pair_to_meandric(X0_DOMAIN, X0_RANGE)
    assert (rt, rb) == (t0, b0)


def test_reduce_x0_exp_leaf1():
    """x_0 expanded at leaf 1: trivial loop, reducible."""
    top, bot = tree_pair_to_meandric(
        ['0', '100', '101', '11'], ['00', '010', '011', '1'])
    assert not is_reduced(top, bot)
    rt, rb = reduce_meandric(top, bot)
    t0, b0 = tree_pair_to_meandric(X0_DOMAIN, X0_RANGE)
    assert (rt, rb) == (t0, b0)


def test_reduce_identity():
    top, bot = tree_pair_to_meandric(
        ['00', '01', '10', '11'], ['00', '01', '10', '11'])
    rt, rb = reduce_meandric(top, bot)
    assert rt == [] and rb == []


def test_reduce_tree_pair_direct():
    d, r = reduce_tree_pair(
        ['00', '01', '10', '11'], ['000', '001', '01', '1'])
    assert d == X0_DOMAIN
    assert r == X0_RANGE


# ── multiplication ────────────────────────────────────────────────────

def test_x0_squared():
    d, r = multiply_tree_pairs(X0_DOMAIN, X0_RANGE, X0_DOMAIN, X0_RANGE)
    assert d == ['0', '10', '110', '111']
    assert r == ['000', '001', '01', '1']


def test_x0_times_x0_inv_is_identity():
    d_inv, r_inv = invert_tree_pair(X0_DOMAIN, X0_RANGE)
    d, r = multiply_tree_pairs(X0_DOMAIN, X0_RANGE, d_inv, r_inv)
    assert d == r  # identity: domain == range


def test_x1_times_x1_inv_is_identity():
    d_inv, r_inv = invert_tree_pair(X1_DOMAIN, X1_RANGE)
    d, r = multiply_tree_pairs(X1_DOMAIN, X1_RANGE, d_inv, r_inv)
    assert d == r


def test_multiply_meandric_x0_squared():
    t0, b0 = tree_pair_to_meandric(X0_DOMAIN, X0_RANGE)
    top, bot = multiply_meandric(t0, b0, t0, b0)
    d, r = meandric_to_tree_pair(top, bot)
    assert d == ['0', '10', '110', '111']
    assert r == ['000', '001', '01', '1']


def test_invert_meandric_swaps():
    t0, b0 = tree_pair_to_meandric(X0_DOMAIN, X0_RANGE)
    ti, bi = invert_meandric(t0, b0)
    assert ti == b0 and bi == t0


def test_x0_cubed():
    d2, r2 = multiply_tree_pairs(X0_DOMAIN, X0_RANGE, X0_DOMAIN, X0_RANGE)
    d3, r3 = multiply_tree_pairs(d2, r2, X0_DOMAIN, X0_RANGE)
    assert is_reduced(
        *tree_pair_to_meandric(d3, r3))


def test_multiply_identity_left():
    """id * x_0 = x_0."""
    identity = ['0', '1']
    d, r = multiply_tree_pairs(identity, identity, X0_DOMAIN, X0_RANGE)
    assert d == X0_DOMAIN
    assert r == X0_RANGE


def test_multiply_identity_right():
    """x_0 * id = x_0."""
    identity = ['0', '1']
    d, r = multiply_tree_pairs(X0_DOMAIN, X0_RANGE, identity, identity)
    assert d == X0_DOMAIN
    assert r == X0_RANGE

# ── Element class ─────────────────────────────────────────────────────

from meandric import Element, X0, X1, ID


def test_x0_times_x0_inv():
    assert (X0 * X0.inv()).is_identity()


def test_x1_times_x1_inv():
    assert (X1 * X1.inv()).is_identity()


def test_identity_neutral():
    assert ID * X0 == X0
    assert X0 * ID == X0


def test_power():
    assert X0 ** 3 == X0 * X0 * X0


def test_power_zero():
    assert (X0 ** 0).is_identity()


def test_negative_power():
    assert X0 ** (-1) == X0.inv()
    assert X0 ** (-2) == X0.inv() * X0.inv()


def test_conjugation():
    u = X1 ** X0  # x0^{-1} x1 x0
    assert u == X0.inv() * X1 * X0


def test_commutator():
    comm = X0.inv() * X1.inv() * X0 * X1
    assert not comm.is_identity()
    assert comm.n_leaves() == 5


def test_n_components_x0():
    assert X0.n_components() == 1


def test_n_components_x1():
    assert X1.n_components() == 2


def test_associativity():
    a = (X0 * X1) * X0
    b = X0 * (X1 * X0)
    assert a == b