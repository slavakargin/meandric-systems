"""Meandric systems from Thompson's group F."""
from meandric.core import (
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
    Element,
    X0, X1, ID,
)
from meandric.plot import plot_meandric, plot_element
from meandric.elements import X0_DOMAIN, X0_RANGE, X1_DOMAIN, X1_RANGE

__version__ = "0.1.0"

__all__ = [
    "partition_to_pairing",
    "pairing_to_partition",
    "tree_pair_to_meandric",
    "meandric_to_tree_pair",
    "meandric_components",
    "reduce_tree_pair",
    "reduce_meandric",
    "is_reduced",
    "multiply_tree_pairs",
    "multiply_meandric",
    "invert_tree_pair",
    "invert_meandric",
    "plot_meandric",
    "plot_element",
    "X0_DOMAIN",
    "X0_RANGE",
    "X1_DOMAIN",
    "X1_RANGE",
    "Element",
    "X0", "X1", "ID",
]
