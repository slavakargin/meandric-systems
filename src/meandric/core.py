"""
Core bijections: binary trees ↔ Dyck paths ↔ noncrossing pairings.

A binary tree is encoded as a **dyadic partition**: a sorted list of binary
strings giving the addresses of the leaves in left-to-right order.
For example, ``['0', '10', '11']`` represents the subdivision
{[0, 1/2], [1/2, 3/4], [3/4, 1]}.

A noncrossing pairing is a list of pairs ``(i, j)`` with ``i < j``,
1-indexed, forming a perfect matching on {1, ..., 2n}.

A meandric system is a pair ``(top, bottom)`` of noncrossing pairings
on the same set {1, ..., 2n}.
"""

from __future__ import annotations


# ── Tree ↔ internal tuple representation ───────────────────────────────

def _partition_to_tree(prefixes: list[str]):
    """Convert sorted prefix list to nested tuple tree.

    A leaf is represented as ``None``, an internal node as ``(left, right)``.
    """
    if len(prefixes) == 1:
        return None
    left = [p[1:] for p in prefixes if p[0] == '0']
    right = [p[1:] for p in prefixes if p[0] == '1']
    if not left or not right:
        raise ValueError(f"Invalid partition: {prefixes}")
    return (_partition_to_tree(left), _partition_to_tree(right))


def _tree_to_partition(tree, prefix: str = '') -> list[str]:
    """Extract sorted leaf prefixes from nested tuple tree."""
    if tree is None:
        return [prefix]
    left, right = tree
    return (_tree_to_partition(left, prefix + '0') +
            _tree_to_partition(right, prefix + '1'))


# ── Tree ↔ Dyck path ──────────────────────────────────────────────────
#
# The encoding rule is:
#
#     encode(v) = U · encode(L) · D · encode(R)
#
# where a leaf encodes as the empty word.  The left subtree sits
# *inside* the matched parentheses U...D, while the right subtree
# follows *after* D.  See the notes for a detailed discussion of
# why this asymmetry is forced by the Dyck path constraint.

def _tree_to_dyck(tree) -> list[str]:
    """Encode a binary tree as a Dyck path (list of 'U'/'D' steps)."""
    if tree is None:
        return []
    left, right = tree
    return ['U'] + _tree_to_dyck(left) + ['D'] + _tree_to_dyck(right)


def _dyck_to_tree(path: list[str]):
    """Reconstruct a binary tree from a Dyck path."""
    if not path:
        return None
    level = 0
    for i, step in enumerate(path):
        level += 1 if step == 'U' else -1
        if level == 0:
            left = _dyck_to_tree(path[1:i])
            right = _dyck_to_tree(path[i + 1:])
            return (left, right)
    raise ValueError(f"Unbalanced path: {path}")


# ── Dyck path ↔ noncrossing pairing ───────────────────────────────────

def _dyck_to_pairing(path: list[str]) -> list[tuple[int, int]]:
    """Match each U with the D that returns the path to the same level."""
    pairs: list[tuple[int, int]] = []
    stack: list[int] = []
    for i, step in enumerate(path):
        if step == 'U':
            stack.append(i + 1)          # 1-indexed
        else:
            pairs.append((stack.pop(), i + 1))
    return sorted(pairs)


def _pairing_to_dyck(pairs: list[tuple[int, int]], n: int) -> list[str]:
    """Reconstruct a Dyck path of length 2n from a noncrossing pairing."""
    partner: dict[int, int] = {}
    for a, b in pairs:
        partner[a] = b
        partner[b] = a
    return ['U' if partner[i] > i else 'D' for i in range(1, 2 * n + 1)]


# ── Public: partition ↔ pairing ────────────────────────────────────────

def partition_to_pairing(prefixes: list[str]) -> list[tuple[int, int]]:
    """Convert a dyadic partition (binary tree) to a noncrossing pairing.

    Parameters
    ----------
    prefixes : list of str
        Sorted list of binary strings (leaf addresses).

    Returns
    -------
    list of (int, int)
        Noncrossing perfect matching on {1, ..., 2n}, where *n* is the
        number of internal nodes (= ``len(prefixes) - 1``).

    Examples
    --------
    >>> partition_to_pairing(['0', '10', '11'])
    [(1, 2), (3, 4)]
    >>> partition_to_pairing(['00', '01', '1'])
    [(1, 4), (2, 3)]
    """
    tree = _partition_to_tree(prefixes)
    path = _tree_to_dyck(tree)
    return _dyck_to_pairing(path)


def pairing_to_partition(pairs: list[tuple[int, int]]) -> list[str]:
    """Convert a noncrossing pairing back to a dyadic partition.

    Parameters
    ----------
    pairs : list of (int, int)
        Noncrossing perfect matching, 1-indexed.

    Returns
    -------
    list of str
        Sorted list of binary-string leaf addresses.

    Examples
    --------
    >>> pairing_to_partition([(1, 2), (3, 4)])
    ['0', '10', '11']
    >>> pairing_to_partition([(1, 4), (2, 3)])
    ['00', '01', '1']
    """
    n = len(pairs)
    path = _pairing_to_dyck(pairs, n)
    tree = _dyck_to_tree(path)
    return _tree_to_partition(tree)


# ── Public: tree pair ↔ meandric system ────────────────────────────────

def tree_pair_to_meandric(
    domain: list[str], range_: list[str]
) -> tuple[list[tuple[int, int]], list[tuple[int, int]]]:
    """Convert a Thompson group element (pair of partitions) to a
    meandric system (pair of noncrossing pairings).

    The domain pairing goes on top, the range pairing on the bottom.

    Parameters
    ----------
    domain, range_ : list of str
        Dyadic partitions with the same number of leaves.

    Returns
    -------
    (top, bottom) : pair of list of (int, int)

    Examples
    --------
    >>> tree_pair_to_meandric(['0', '10', '11'], ['00', '01', '1'])
    ([(1, 2), (3, 4)], [(1, 4), (2, 3)])
    """
    if len(domain) != len(range_):
        raise ValueError(
            f"Trees must have the same number of leaves: "
            f"{len(domain)} vs {len(range_)}"
        )
    top = partition_to_pairing(domain)
    bottom = partition_to_pairing(range_)
    return top, bottom


def meandric_to_tree_pair(
    top: list[tuple[int, int]], bottom: list[tuple[int, int]]
) -> tuple[list[str], list[str]]:
    """Convert a meandric system back to a Thompson group element.

    Parameters
    ----------
    top, bottom : list of (int, int)
        Noncrossing pairings (same cardinality).

    Returns
    -------
    (domain, range_) : pair of list of str

    Examples
    --------
    >>> meandric_to_tree_pair([(1, 2), (3, 4)], [(1, 4), (2, 3)])
    (['0', '10', '11'], ['00', '01', '1'])
    """
    domain = pairing_to_partition(top)
    range_ = pairing_to_partition(bottom)
    return domain, range_


# ── Meandric system analysis ──────────────────────────────────────────

def meandric_components(
    top: list[tuple[int, int]], bottom: list[tuple[int, int]]
) -> list[list[int]]:
    """Find connected components of the meandric system.

    Starting from any point, we alternately follow top and bottom arcs
    until we return to the start.  Each such orbit is one closed curve
    of the meandric system.

    Parameters
    ----------
    top, bottom : list of (int, int)
        Noncrossing pairings on {1, ..., 2n}.

    Returns
    -------
    list of list of int
        Each inner list contains the points visited by one closed curve,
        in traversal order (without repeating the start).

    Examples
    --------
    >>> meandric_components([(1, 2), (3, 4)], [(1, 4), (2, 3)])
    [[1, 2, 3, 4]]
    >>> meandric_components([(1, 2), (3, 4), (5, 6)],
    ...                     [(1, 2), (3, 6), (4, 5)])
    [[1, 2], [3, 4, 5, 6]]
    """
    n = len(top)
    top_partner: dict[int, int] = {}
    bot_partner: dict[int, int] = {}
    for a, b in top:
        top_partner[a] = b
        top_partner[b] = a
    for a, b in bottom:
        bot_partner[a] = b
        bot_partner[b] = a

    visited: set[int] = set()
    components: list[list[int]] = []
    for start in range(1, 2 * n + 1):
        if start in visited:
            continue
        comp: list[int] = []
        pos = start
        use_top = True
        while True:
            comp.append(pos)
            visited.add(pos)
            partner = top_partner if use_top else bot_partner
            pos = partner[pos]
            use_top = not use_top
            if pos == start:
                break
        components.append(comp)
    return components
