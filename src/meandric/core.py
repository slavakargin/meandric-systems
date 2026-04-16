"""
Core bijections: binary trees ↔ Dyck paths ↔ noncrossing pairings.

A binary tree is encoded as a **dyadic partition**: a sorted list of binary
strings giving the addresses of the leaves in left-to-right order.
For example, ``['0', '10', '11']`` represents the subdivision
{[0, 1/2], [1/2, 3/4], [3/4, 1]}.

A noncrossing pairing is a list of pairs ``(i, j)`` with ``i < j``,
forming a perfect matching on {0, 1, ..., 2n-1}.

Convention: the Dyck path steps 1, 2, ..., 2n-1 keep their labels,
while the last step (2n) is relabeled to 0.  In pictures, point 0
is placed on the left.

A meandric system is a pair ``(top, bottom)`` of noncrossing pairings
on the same set {0, 1, ..., 2n-1}.
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
#
# Convention: step i (0-based, 0 ≤ i < 2n) gets label (i+1) % (2n).
# So steps 0..2n-2 are labeled 1..2n-1, and step 2n-1 is labeled 0.

def _step_to_label(i: int, n2: int) -> int:
    return (i + 1) % n2


def _label_to_step(label: int, n2: int) -> int:
    return (label - 1) % n2


def _dyck_to_pairing(path: list[str]) -> list[tuple[int, int]]:
    """Match each U with the D that returns the path to the same level."""
    n2 = len(path)
    pairs: list[tuple[int, int]] = []
    stack: list[int] = []
    for i, step in enumerate(path):
        label = _step_to_label(i, n2)
        if step == 'U':
            stack.append(label)
        else:
            u_label = stack.pop()
            pair = (min(u_label, label), max(u_label, label))
            pairs.append(pair)
    return sorted(pairs)


def _pairing_to_dyck(pairs: list[tuple[int, int]], n: int) -> list[str]:
    """Reconstruct a Dyck path of length 2n from a noncrossing pairing."""
    n2 = 2 * n
    partner: dict[int, int] = {}
    for a, b in pairs:
        partner[a] = b
        partner[b] = a
    path: list[str] = []
    for i in range(n2):
        label = _step_to_label(i, n2)
        partner_step = _label_to_step(partner[label], n2)
        path.append('U' if i < partner_step else 'D')
    return path


# ── Public: partition ↔ pairing ────────────────────────────────────────

def partition_to_pairing(prefixes: list[str]) -> list[tuple[int, int]]:
    """Convert a dyadic partition (binary tree) to a noncrossing pairing.

    Examples
    --------
    >>> partition_to_pairing(['0', '10', '11'])
    [(0, 3), (1, 2)]
    >>> partition_to_pairing(['00', '01', '1'])
    [(0, 1), (2, 3)]
    """
    tree = _partition_to_tree(prefixes)
    path = _tree_to_dyck(tree)
    return _dyck_to_pairing(path)


def pairing_to_partition(pairs: list[tuple[int, int]]) -> list[str]:
    """Convert a noncrossing pairing back to a dyadic partition.

    Examples
    --------
    >>> pairing_to_partition([(0, 3), (1, 2)])
    ['0', '10', '11']
    >>> pairing_to_partition([(0, 1), (2, 3)])
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
    """Convert a Thompson group element to a meandric system.

    Examples
    --------
    >>> tree_pair_to_meandric(['0', '10', '11'], ['00', '01', '1'])
    ([(0, 3), (1, 2)], [(0, 1), (2, 3)])
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

    Examples
    --------
    >>> meandric_to_tree_pair([(0, 3), (1, 2)], [(0, 1), (2, 3)])
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

    Examples
    --------
    >>> meandric_components([(0, 3), (1, 2)], [(0, 1), (2, 3)])
    [[0, 1, 2, 3]]
    """
    n = len(top)
    n2 = 2 * n
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
    for start in range(n2):
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

# ── Reduction ─────────────────────────────────────────────────────────

def _find_reducible_leaf(domain: list[str], range_: list[str]) -> int:
    """Find a leaf index k such that both partitions have a caret at (k, k+1).

    A caret at k means partition[k] = p+'0' and partition[k+1] = p+'1'
    for some prefix p.  Returns -1 if no such k exists (system is reduced).
    """
    for k in range(len(domain) - 1):
        dp, rp = domain[k], range_[k]
        dn, rn = domain[k + 1], range_[k + 1]
        if (dp.endswith('0') and dn.endswith('1') and dp[:-1] == dn[:-1] and
            rp.endswith('0') and rn.endswith('1') and rp[:-1] == rn[:-1]):
            return k
    return -1


def _reduce_once(domain: list[str], range_: list[str]) -> tuple[list[str], list[str]]:
    """Remove one pair of matching carets, if any."""
    k = _find_reducible_leaf(domain, range_)
    if k < 0:
        return domain, range_
    new_domain = domain[:k] + [domain[k][:-1]] + domain[k + 2:]
    new_range = range_[:k] + [range_[k][:-1]] + range_[k + 2:]
    return new_domain, new_range


def reduce_tree_pair(domain, range_):
    """Fully reduce a Thompson group element by removing all matching carets."""
    while True:
        new_d, new_r = _reduce_once(domain, range_)
        if new_d is domain:
            return domain, range_
        domain, range_ = new_d, new_r


def reduce_meandric(top, bottom):
    """Reduce a meandric system to its canonical (reduced) form."""
    domain = pairing_to_partition(top)
    range_ = pairing_to_partition(bottom)
    rd, rr = reduce_tree_pair(domain, range_)
    return partition_to_pairing(rd), partition_to_pairing(rr)


def is_reduced(top, bottom):
    """Check whether a meandric system is already reduced."""
    domain = pairing_to_partition(top)
    range_ = pairing_to_partition(bottom)
    return _find_reducible_leaf(domain, range_) < 0

# ── Multiplication and inverse ────────────────────────────────────────

def _merge_trees(t1, t2):
    """Common refinement of two binary trees."""
    if t1 is None and t2 is None:
        return None
    if t1 is None:
        return t2
    if t2 is None:
        return t1
    return (_merge_trees(t1[0], t2[0]), _merge_trees(t1[1], t2[1]))


def _get_grafts(original, refined):
    """For each leaf of original, record the subtree that refined puts there."""
    grafts = []
    def walk(orig, ref):
        if orig is None:
            grafts.append(ref)
        else:
            walk(orig[0], ref[0])
            walk(orig[1], ref[1])
    walk(original, refined)
    return grafts


def _apply_grafts(tree, grafts):
    """Replace each leaf of tree with the corresponding graft."""
    counter = [0]
    def walk(t):
        if t is None:
            g = grafts[counter[0]]
            counter[0] += 1
            return g
        return (walk(t[0]), walk(t[1]))
    return walk(tree)


def multiply_tree_pairs(
    d1: list[str], r1: list[str],
    d2: list[str], r2: list[str],
) -> tuple[list[str], list[str]]:
    """Multiply two Thompson group elements given as partition pairs.

    Computes the product (D1, R1) * (D2, R2) by expanding until
    R1 = D2, then returning the reduced (D1', R2').

    Examples
    --------
    >>> multiply_tree_pairs(['0','10','11'], ['00','01','1'],
    ...                     ['0','10','11'], ['00','01','1'])
    (['0', '10', '110', '111'], ['000', '001', '01', '1'])
    """
    t_r1 = _partition_to_tree(r1)
    t_d2 = _partition_to_tree(d2)
    t_c = _merge_trees(t_r1, t_d2)

    grafts_1 = _get_grafts(t_r1, t_c)
    t_d1_exp = _apply_grafts(_partition_to_tree(d1), grafts_1)

    grafts_2 = _get_grafts(t_d2, t_c)
    t_r2_exp = _apply_grafts(_partition_to_tree(r2), grafts_2)

    return reduce_tree_pair(_tree_to_partition(t_d1_exp),
                            _tree_to_partition(t_r2_exp))


def multiply_meandric(
    top1: list[tuple[int, int]], bot1: list[tuple[int, int]],
    top2: list[tuple[int, int]], bot2: list[tuple[int, int]],
) -> tuple[list[tuple[int, int]], list[tuple[int, int]]]:
    """Multiply two Thompson group elements given as meandric systems.

    Examples
    --------
    >>> t0, b0 = ([(0, 3), (1, 2)], [(0, 1), (2, 3)])
    >>> multiply_meandric(t0, b0, t0, b0)  # x_0^2
    ([(0, 5), (1, 2), (3, 4)], [(0, 1), (2, 5), (3, 4)])
    """
    d1, r1 = pairing_to_partition(top1), pairing_to_partition(bot1)
    d2, r2 = pairing_to_partition(top2), pairing_to_partition(bot2)
    rd, rr = multiply_tree_pairs(d1, r1, d2, r2)
    return partition_to_pairing(rd), partition_to_pairing(rr)


def invert_tree_pair(
    domain: list[str], range_: list[str]
) -> tuple[list[str], list[str]]:
    """Invert a Thompson group element: swap domain and range."""
    return range_, domain


def invert_meandric(
    top: list[tuple[int, int]], bottom: list[tuple[int, int]]
) -> tuple[list[tuple[int, int]], list[tuple[int, int]]]:
    """Invert a meandric system: swap top and bottom."""
    return bottom, top

# ── Element class ─────────────────────────────────────────────────────

class Element:
    """A Thompson group F element with convenient syntax.

    Usage:
        x0, x1 = X0, X1
        y0 = x0.inv()
        z = y0 * y1 * x0 * x1
        v = z ** 3
        u = v ** x0        # conjugation: x0^{-1} * v * x0
    """

    def __init__(self, domain: list[str], range_: list[str]):
        d, r = reduce_tree_pair(domain, range_)
        self.domain = d
        self.range = r

    def __mul__(self, other: 'Element') -> 'Element':
        d, r = multiply_tree_pairs(
            self.domain, self.range, other.domain, other.range)
        return Element(d, r)

    def __pow__(self, exp):
        if isinstance(exp, int):
            if exp == 0:
                return Element(['0', '1'], ['0', '1'])
            if exp < 0:
                return self.inv() ** (-exp)
            result = self
            for _ in range(exp - 1):
                result = result * self
            return result
        if isinstance(exp, Element):
            return exp.inv() * self * exp
        return NotImplemented

    def inv(self) -> 'Element':
        return Element(self.range, self.domain)

    def meandric(self):
        return tree_pair_to_meandric(self.domain, self.range)

    def components(self):
        top, bot = self.meandric()
        return meandric_components(top, bot)

    def n_components(self) -> int:
        return len(self.components())

    def n_leaves(self) -> int:
        return len(self.domain)

    def is_identity(self) -> bool:
        return self.domain == self.range

    def __eq__(self, other):
        if not isinstance(other, Element):
            return NotImplemented
        return self.domain == other.domain and self.range == other.range

    def __repr__(self):
        return f"Element({self.domain}, {self.range})"

    def __str__(self):
        top, bot = self.meandric()
        return f"top={top} bot={bot} ({self.n_components()} comp)"
    
    def plot(self, title=None, **kwargs):
        from meandric.plot import plot_meandric
        top, bot = self.meandric()
        if title is None:
            title = f"{self.n_components()} comp, {self.n_leaves()} leaves"
        return plot_meandric(top, bot, title=title, **kwargs)


X0 = Element(['0', '10', '11'], ['00', '01', '1'])
X1 = Element(['0', '10', '110', '111'], ['0', '100', '101', '11'])
ID = Element(['0', '1'], ['0', '1'])