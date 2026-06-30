# Meandric Systems from Thompson's Group F

Every element of Thompson's group $F$ is represented by a pair of finite binary trees with the same number of leaves.  This package encodes each tree as a **noncrossing pairing** (via Dyck paths), then places the two pairings on opposite sides of a horizontal line to form a **meandric system** — a collection of closed curves whose topology reflects the combinatorics of the group element.

## Installation

```bash
pip install -e .
```

For development (includes pytest):

```bash
pip install -e ".[dev]"
```

## Quick start

```python
from meandric import (
    tree_pair_to_meandric,
    meandric_components,
    plot_element,
    X0_DOMAIN, X0_RANGE,
    X1_DOMAIN, X1_RANGE,
)

# Encode x_0 as a meandric system
top, bot = tree_pair_to_meandric(X0_DOMAIN, X0_RANGE)
print(top)   # [(0, 3), (1, 2)]
print(bot)   # [(0, 1), (2, 3)]

# Count connected components
comps = meandric_components(top, bot)
print(f"{len(comps)} component(s): {comps}")
# 1 component(s): [[0, 3, 2, 1]]

# Plot
fig, ax = plot_element(X0_DOMAIN, X0_RANGE, title='$x_0$')
fig.savefig('x0.png', dpi=150, bbox_inches='tight')
```

## Word length

`Element.word_length()` returns the length over the generators `{x_0, x_1}`,
read directly off the reduced tree pair by the Fordham / Belk–Brown formula
(no Cayley-graph search):

```python
from meandric import Element, X0, X1

(X0 * X1 * X0.inv()).word_length()   # distance in the word metric
Element.xn(1).inv().word_length()    # 1
```

It is inversion-invariant (`f.word_length() == f.inv().word_length()`) and has
been checked against breadth-first search on the Cayley graph over the entire
ball of radius 8.

## Data formats

| Object | Representation | Example |
|--------|---------------|---------|
| Binary tree | Dyadic partition (sorted leaf addresses) | `['0', '10', '11']` |
| Noncrossing pairing | List of `(i, j)` pairs, 0-indexed | `[(0, 3), (1, 2)]` |
| Thompson group element | `(domain, range_)` pair of partitions | `(['0','10','11'], ['00','01','1'])` |
| Meandric system | `(top, bottom)` pair of pairings | `([(0,3),(1,2)], [(0,1),(2,3)])` |

## Conventions

**Generators.** `X0` and `X1` are Thompson's generators $x_0, x_1$, realised as
piecewise-linear homeomorphisms of $[0,1]$ with $x_n \le \mathrm{id}$ and slope
$\tfrac12$ at the relevant breakpoint (for instance $x_0$ sends
$[0,\tfrac12]\mapsto[0,\tfrac14]$). `Element.xn(n)` builds $x_n$. The inverses
$a_i := x_i^{-1}$ — the "positive" generators in some treatments, with
$a_0(t)=t+1$ on $\mathbb{R}$ — are `Element.xn(i).inv()`.

**Multiplication order.** In a product `f * g` the **left** factor acts **first**:
as functions, `f * g` $= g \circ f$, read left-to-right as "do `f`, then `g`."
This is the *opposite* of the common textbook convention $fg = f\circ g$ (right
factor first); a product written $fg$ there is `g * f` here. (Word length is
unaffected — it depends only on the element, not on how it is spelled.)

**Point labelling.** Leaves are addressed by binary strings (`'0'` = left child,
`'1'` = right). A meandric system for an element whose trees have $k$ carets lives
on the $2k$ points $\{0, 1, \dots, 2k-1\}$, with point $0$ drawn on the left;
pairings are **0-indexed**.

## API

### Conversions

- `partition_to_pairing(prefixes)` — tree → noncrossing pairing
- `pairing_to_partition(pairs)` — noncrossing pairing → tree
- `tree_pair_to_meandric(domain, range_)` — element → meandric system
- `meandric_to_tree_pair(top, bottom)` — meandric system → element

### Analysis

- `meandric_components(top, bottom)` — connected components (closed curves)
- `word_length(domain, range_)` — word length over `{x_0, x_1}` (Fordham / Belk–Brown), also available as the method `Element.word_length()`

### Visualization

- `plot_meandric(top, bottom)` — plot a meandric system
- `plot_element(domain, range_)` — plot from tree pair directly

### Standard elements

- `X0_DOMAIN`, `X0_RANGE` — generator $x_0$
- `X1_DOMAIN`, `X1_RANGE` — generator $x_1$

## Tests

```bash
pytest
```

## Notes

The `notes/` directory contains LaTeX notes with diagrams explaining the bijections in detail, including the encoding asymmetry (why mirror-image trees produce different Dyck paths).

## License

MIT
