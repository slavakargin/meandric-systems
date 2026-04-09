"""
Example: Meandric systems for Thompson's group generators.

This script can be run as-is in Google Colab or Jupyter.
To install the package first:

    !pip install -e /path/to/meandric-systems

Or just copy src/meandric/ into your working directory.
"""

# %% Imports
from meandric import (
    partition_to_pairing,
    pairing_to_partition,
    tree_pair_to_meandric,
    meandric_to_tree_pair,
    meandric_components,
    plot_element,
    plot_meandric,
    X0_DOMAIN, X0_RANGE,
    X1_DOMAIN, X1_RANGE,
)

# %% Generator x_0
print("=== x_0 ===")
top, bot = tree_pair_to_meandric(X0_DOMAIN, X0_RANGE)
print(f"Domain: {X0_DOMAIN}  →  top pairing: {top}")
print(f"Range:  {X0_RANGE}  →  bot pairing: {bot}")
print(f"Components: {meandric_components(top, bot)}")

fig, ax = plot_element(X0_DOMAIN, X0_RANGE, title='$x_0$')

# %% Generator x_1
print("\n=== x_1 ===")
top, bot = tree_pair_to_meandric(X1_DOMAIN, X1_RANGE)
print(f"Domain: {X1_DOMAIN}  →  top pairing: {top}")
print(f"Range:  {X1_RANGE}  →  bot pairing: {bot}")
comps = meandric_components(top, bot)
print(f"Components ({len(comps)}): {comps}")

fig, ax = plot_element(X1_DOMAIN, X1_RANGE, title='$x_1$')

# %% The identity: all trivial loops
print("\n=== Identity on 4-leaf tree ===")
partition = ['00', '01', '10', '11']
top, bot = tree_pair_to_meandric(partition, partition)
print(f"Pairing: {top}")
comps = meandric_components(top, bot)
print(f"Components ({len(comps)}): {comps}")
print("All trivial loops — as expected for the identity.")

fig, ax = plot_element(partition, partition, title='Identity')

# %% Custom element: x_0^2
print("\n=== x_0^2 ===")
# x_0^2 maps [0,1/4,1/2,3/4,1] -> [0,1/4,3/8,1/2,1]
# but we need a common refinement; using the reduced pair:
x0sq_domain = ['0', '10', '110', '111']
x0sq_range  = ['000', '001', '01', '1']
top, bot = tree_pair_to_meandric(x0sq_domain, x0sq_range)
print(f"Domain: {x0sq_domain}  →  {top}")
print(f"Range:  {x0sq_range}  →  {bot}")
comps = meandric_components(top, bot)
print(f"Components ({len(comps)}): {comps}")

fig, ax = plot_element(x0sq_domain, x0sq_range, title='$x_0^2$')

# %% Round-trip test
print("\n=== Round-trip test ===")
for name, dom, rng in [("x_0", X0_DOMAIN, X0_RANGE),
                        ("x_1", X1_DOMAIN, X1_RANGE)]:
    top, bot = tree_pair_to_meandric(dom, rng)
    d2, r2 = meandric_to_tree_pair(top, bot)
    ok = (d2 == dom and r2 == rng)
    print(f"  {name}: {'✓' if ok else '✗'}")
