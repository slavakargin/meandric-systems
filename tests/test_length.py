"""Tests for word length over {x_0, x_1} (Fordham / Belk--Brown formula)."""

from collections import deque

import pytest

from meandric import Element, X0, X1, ID, word_length


# ── helpers ────────────────────────────────────────────────────────────

def a(i):
    """a_i = x_i^{-1}."""
    return Element.xn(i).inv()


def compose(*fs):
    """f0 ∘ f1 ∘ ... in book order, using the package product (a*b = b∘a)."""
    res = ID
    for f in reversed(fs):
        res = res * f
    return res


def _key(e):
    return (tuple(e.domain), tuple(e.range))


def _bfs(radius):
    """True word lengths via BFS on the Cayley graph; returns (dist, spheres)."""
    gens = [X0, X0.inv(), X1, X1.inv()]
    dist = {_key(ID): 0}
    frontier = deque([ID])
    spheres = [1]
    for r in range(1, radius + 1):
        nxt, count = deque(), 0
        while frontier:
            g = frontier.popleft()
            for s in gens:
                h = g * s
                k = _key(h)
                if k not in dist:
                    dist[k] = r
                    nxt.append(h)
                    count += 1
        spheres.append(count)
        frontier = nxt
    return dist, spheres


# ── basic values ───────────────────────────────────────────────────────

def test_identity():
    assert word_length(ID.domain, ID.range) == 0
    assert ID.word_length() == 0


def test_generators():
    assert X0.word_length() == 1
    assert X1.word_length() == 1
    assert X0.inv().word_length() == 1
    assert X1.inv().word_length() == 1


# ── worked examples from the reference text ─────────────────────────────

@pytest.mark.parametrize("element, expected", [
    (compose(a(1), a(3), a(4), a(3)),                       10),  # strongly positive
    (compose(a(0), a(1).inv(), a(0), a(1), a(0).inv()),      5),  # mixed
    (compose(a(1), a(1), a(1)),                              3),  # left comb
    (compose(a(1), a(2), a(3)),                              7),  # right comb
])
def test_worked_examples(element, expected):
    assert element.word_length() == expected


# ── invariants ──────────────────────────────────────────────────────────

def test_inversion_invariance():
    dist, _ = _bfs(6)
    for (dom, rng) in dist:
        e = Element(list(dom), list(rng))
        assert e.word_length() == e.inv().word_length()


def test_matches_bfs_ball():
    """word_length agrees with the true Cayley distance on the radius-6 ball,
    and the BFS reproduces the known spherical growth of F."""
    dist, spheres = _bfs(6)
    assert spheres == [1, 4, 12, 36, 108, 314, 906]
    for (dom, rng), true_len in dist.items():
        assert word_length(list(dom), list(rng)) == true_len


def test_generator_steps_are_lipschitz():
    """Each Cayley-graph edge changes the length by exactly 1."""
    dist, _ = _bfs(5)
    gens = [X0, X0.inv(), X1, X1.inv()]
    for (dom, rng) in dist:
        e = Element(list(dom), list(rng))
        le = e.word_length()
        for s in gens:
            assert abs((e * s).word_length() - le) == 1
