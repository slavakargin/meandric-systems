"""Word length in Thompson's group :math:`F` with respect to the finite
generating set :math:`\\{x_0, x_1\\}`.

This implements the **Fordham / Belk--Brown** length formula, which reads the
word length of an element directly off its reduced tree pair, without any search
over the Cayley graph.

The construction
----------------
Given a reduced tree pair ``(domain, range_)`` (each a sorted list of dyadic-leaf
addresses), form the **two-way forest diagram**: a *top* forest built from the
domain tree and a *bottom* forest built from the range tree, with the two forests
aligned by the leaf bijection (the ``k``-th domain leaf is paired with the
``k``-th range leaf).  Each forest carries a pointer marking its basepoint.

The length splits as

.. math::  \\ell(f) = \\ell_0(f) + \\ell_1(f),

where :math:`\\ell_1(f)` is the total number of carets in the two forests and
:math:`\\ell_0(f)` is a sum of per-space weights.  Every space between two
adjacent (aligned) leaves receives a *top* label from the domain forest and a
*bottom* label from the range forest, drawn from ``{L, N, R, I}`` with priority
``L > N > R > I``:

* **L** -- exterior and to the left of that forest's pointer;
* **N** -- the leaf on the right of the space is the left child of a caret
  (equivalently, the leftmost leaf of a nontrivial tree), and the space is not
  already ``L``;
* **R** -- exterior and to the right of the pointer, and not ``N``;
* **I** -- interior (under a caret) and not ``N``.

The contribution of a space is :data:`WEIGHT[(top_label, bottom_label)]`.  Only
spaces in the **support** of ``f`` are summed (see :func:`_support_window`).

Conventions and invariants
---------------------------
Word length is *convention-independent*: it depends only on the (reduced) tree
pair and on the symmetric generating set :math:`\\{x_0^{\\pm1}, x_1^{\\pm1}\\}`.
The order of multiplication (``f*g`` vs ``g*f``) and the choice of ``x`` versus
``a = x^{-1}`` do **not** affect the length of a single element.  In particular
:math:`\\ell(f) = \\ell(f^{-1})`, which is visible here as the symmetry of the
weight table together with swapping the two forests.

Validation
----------
``word_length`` has been checked to agree exactly with breadth-first search on
the Cayley graph over the entire ball of radius 8 (11237 elements), and against
bidirectional-BFS true distances for several hundred further elements of length
up to 15.  It reproduces the worked examples of the reference text:
:math:`a_1a_3a_4a_3 \\mapsto 10`, the left/right combs :math:`\\mapsto 3, 7`, and
the mixed example :math:`\\mapsto 5`.

References
----------
S. Cleary and J. Taback; B. Fordham, *Minimal length elements of Thompson's
group F*; J. Belk, *Thompson's Group F* (Cornell thesis, 2004); J. Belk and
K. Brown, *Forest diagrams for elements of Thompson's group F*.
"""

from __future__ import annotations

__all__ = ["word_length", "WEIGHT"]


# Weight table; rows indexed by the top (domain) label, columns by the bottom
# (range) label.  Symmetric, reflecting ell(f) = ell(f^{-1}).
WEIGHT = {
    ('L', 'L'): 2, ('L', 'N'): 1, ('L', 'R'): 1, ('L', 'I'): 1,
    ('N', 'L'): 1, ('N', 'N'): 2, ('N', 'R'): 2, ('N', 'I'): 2,
    ('R', 'L'): 1, ('R', 'N'): 2, ('R', 'R'): 2, ('R', 'I'): 0,
    ('I', 'L'): 1, ('I', 'N'): 2, ('I', 'R'): 0, ('I', 'I'): 0,
}


def _is_spine(addr: str) -> bool:
    """True if a caret address lies on the outer spine of the tree.

    The spine carets are the root (``''``) and any all-zeros or all-ones
    address; these are exactly the carets removed when passing from a tree on
    ``[0, 1]`` to its forest in the two-way diagram.
    """
    return addr == '' or set(addr) <= {'0'} or set(addr) <= {'1'}


def _forest_carets(partition: list[str]) -> int:
    """Number of *forest* (non-spine) carets of a partition."""
    nodes = set()
    for leaf in partition:
        for j in range(len(leaf)):
            nodes.add(leaf[:j])          # '', leaf[:1], ..., leaf[:-1]
    return sum(1 for node in nodes if not _is_spine(node))


def _forest_data(partition: list[str]):
    """Return ``(gap, spaces)`` for one forest.

    ``gap`` is the pointer position, counted as the number of leaves in
    ``[0, 1/2]`` (i.e. leaves whose address starts with ``'0'``).  ``spaces`` is
    a list, one entry per space ``i`` (between leaf ``i`` and leaf ``i+1``), each
    a dict with keys ``'interior'`` (the space lies under a caret) and
    ``'left_child'`` (the leaf on its right is the left child of a forest caret).
    """
    n = len(partition)
    gap = sum(1 for leaf in partition if leaf.startswith('0'))
    spaces = []
    for i in range(n - 1):
        a, b = partition[i], partition[i + 1]
        k = 0
        while k < len(a) and k < len(b) and a[k] == b[k]:
            k += 1
        lca = a[:k]                       # longest common prefix = LCA caret
        interior = not _is_spine(lca)     # space is interior iff its LCA is a forest caret
        left_child = b.endswith('0') and not _is_spine(b[:-1])
        spaces.append({'interior': interior, 'left_child': left_child})
    return gap, spaces


def _label(space, i: int, gap: int) -> str:
    """Assign the L/N/R/I label of space ``i`` for one forest (priority L>N>R>I)."""
    interior = space['interior']
    if (not interior) and i < gap:
        return 'L'
    if space['left_child']:
        return 'N'
    if not interior:                      # exterior, i >= gap, not N
        return 'R'
    return 'I'


def _support_window(gap_top, spaces_top, gap_bot, spaces_bot, n):
    """Return the half-open range ``[lo, hi)`` of spaces in the support of ``f``.

    The support is the convex hull, in space-index coordinates, of all *features*
    of the diagram: the two pointer positions and every interior space (every
    space under a caret of either forest).  A space outside this hull is exterior
    in both forests and lies on the same side of both pointers, hence is fixed by
    ``f`` and contributes nothing; including it would, via the ``(L,L)`` and
    ``(R,R)`` entries of the weight table, overcount.  The hull is clamped to the
    valid space indices ``0, ..., n-2``.
    """
    interior = [i for i, s in enumerate(spaces_top) if s['interior']]
    interior += [i for i, s in enumerate(spaces_bot) if s['interior']]
    lo_candidates = [min(gap_top, gap_bot)]
    hi_candidates = [max(gap_top, gap_bot)]
    if interior:
        lo_candidates.append(min(interior))
        hi_candidates.append(max(interior) + 1)
    lo = max(min(lo_candidates), 0)
    hi = min(max(hi_candidates), n - 1)
    return lo, hi


def word_length(domain: list[str], range_: list[str]) -> int:
    """Word length of the element ``(domain, range_)`` over ``{x_0, x_1}``.

    ``domain`` and ``range_`` are sorted lists of dyadic-leaf addresses with the
    same number of leaves; the pair need not be reduced, but an unreduced pair
    carries shared carets that inflate the count, so callers should pass reduced
    data (the :class:`~meandric.core.Element` constructor reduces automatically).

    Returns ``0`` for the identity.
    """
    D, R = list(domain), list(range_)
    n = len(D)
    if len(R) != n:
        raise ValueError("domain and range must have the same number of leaves")

    ell1 = _forest_carets(D) + _forest_carets(R)

    gap_top, spaces_top = _forest_data(D)
    gap_bot, spaces_bot = _forest_data(R)
    lo, hi = _support_window(gap_top, spaces_top, gap_bot, spaces_bot, n)

    ell0 = 0
    for i in range(lo, hi):
        top = _label(spaces_top[i], i, gap_top)
        bot = _label(spaces_bot[i], i, gap_bot)
        ell0 += WEIGHT[(top, bot)]

    return ell0 + ell1
