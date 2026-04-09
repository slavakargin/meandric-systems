"""Tests for meandric systems package."""

import pytest
from meandric import (
    partition_to_pairing,
    pairing_to_partition,
    tree_pair_to_meandric,
    meandric_to_tree_pair,
    meandric_components,
    X0_DOMAIN, X0_RANGE,
    X1_DOMAIN, X1_RANGE,
)


# ── partition ↔ pairing round-trips ────────────────────────────────────

PARTITION_PAIRING_CASES = [
    (['0', '1'],               [(1, 2)]),
    (['0', '10', '11'],        [(1, 2), (3, 4)]),
    (['00', '01', '1'],        [(1, 4), (2, 3)]),
    (['0', '10', '110', '111'],[(1, 2), (3, 4), (5, 6)]),
    (['00', '01', '10', '11'], [(1, 4), (2, 3), (5, 6)]),
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
    assert top == [(1, 2), (3, 4)]
    assert bot == [(1, 4), (2, 3)]


def test_x0_one_component():
    top, bot = tree_pair_to_meandric(X0_DOMAIN, X0_RANGE)
    comps = meandric_components(top, bot)
    assert len(comps) == 1
    assert sorted(comps[0]) == [1, 2, 3, 4]


def test_x0_round_trip():
    top, bot = tree_pair_to_meandric(X0_DOMAIN, X0_RANGE)
    d, r = meandric_to_tree_pair(top, bot)
    assert d == X0_DOMAIN
    assert r == X0_RANGE


# ── x_1 ───────────────────────────────────────────────────────────────

def test_x1_meandric():
    top, bot = tree_pair_to_meandric(X1_DOMAIN, X1_RANGE)
    assert top == [(1, 2), (3, 4), (5, 6)]
    assert bot == [(1, 2), (3, 6), (4, 5)]


def test_x1_two_components():
    top, bot = tree_pair_to_meandric(X1_DOMAIN, X1_RANGE)
    comps = meandric_components(top, bot)
    assert len(comps) == 2
    sizes = sorted(len(c) for c in comps)
    assert sizes == [2, 4]


def test_x1_trivial_loop():
    """The pair {1,2} in both top and bottom gives the trivial loop."""
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
    """Simplest nontrivial tree: one caret, two leaves."""
    assert partition_to_pairing(['0', '1']) == [(1, 2)]
    assert pairing_to_partition([(1, 2)]) == ['0', '1']


def test_mismatched_leaves_raises():
    with pytest.raises(ValueError):
        tree_pair_to_meandric(['0', '1'], ['00', '01', '1'])
