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
print(top)   # [(1, 2), (3, 4)]
print(bot)   # [(1, 4), (2, 3)]

# Count connected components
comps = meandric_components(top, bot)
print(f"{len(comps)} component(s): {comps}")
# 1 component(s): [[1, 2, 3, 4]]

# Plot
fig, ax = plot_element(X0_DOMAIN, X0_RANGE, title='$x_0$')
fig.savefig('x0.png', dpi=150, bbox_inches='tight')
```

## Data formats

| Object | Representation | Example |
|--------|---------------|---------|
| Binary tree | Dyadic partition (sorted leaf addresses) | `['0', '10', '11']` |
| Noncrossing pairing | List of `(i, j)` pairs, 1-indexed | `[(1, 2), (3, 4)]` |
| Thompson group element | `(domain, range_)` pair of partitions | `(['0','10','11'], ['00','01','1'])` |
| Meandric system | `(top, bottom)` pair of pairings | `([(1,2),(3,4)], [(1,4),(2,3)])` |

## API

### Conversions

- `partition_to_pairing(prefixes)` — tree → noncrossing pairing
- `pairing_to_partition(pairs)` — noncrossing pairing → tree
- `tree_pair_to_meandric(domain, range_)` — element → meandric system
- `meandric_to_tree_pair(top, bottom)` — meandric system → element

### Analysis

- `meandric_components(top, bottom)` — connected components (closed curves)

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
