"""Visualization of meandric systems via matplotlib."""

from __future__ import annotations

import matplotlib.pyplot as plt
import matplotlib.patches as patches

from meandric.core import meandric_components, tree_pair_to_meandric


def plot_meandric(
    top: list[tuple[int, int]],
    bottom: list[tuple[int, int]],
    *,
    title: str | None = None,
    figsize: tuple[float, float] = (10, 5),
    top_color: str = '#1D9E75',
    bot_color: str = '#7F77DD',
    top_label: str = 'domain',
    bot_label: str = 'range',
    show_components: bool = True,
    ax: plt.Axes | None = None,
) -> tuple[plt.Figure, plt.Axes]:
    """Plot a meandric system with arcs above and below a horizontal line.

    Parameters
    ----------
    top, bottom : list of (int, int)
        Noncrossing pairings (1-indexed).
    title : str, optional
        Figure title.
    show_components : bool
        If True, annotate with component structure.
    ax : matplotlib Axes, optional
        If provided, draw into this axes instead of creating a new figure.

    Returns
    -------
    (fig, ax)
    """
    n = len(top)
    num_points = 2 * n

    if ax is None:
        fig, ax = plt.subplots(1, 1, figsize=figsize)
    else:
        fig = ax.get_figure()
    ax.set_aspect('equal')

    # Point spacing: 0, 1, 2, ..., 2n-1 left to right
    spacing = 1.0
    xs = {i: i * spacing for i in range(num_points)}
    xmin = -0.8
    xmax = (num_points - 1) * spacing + 0.8

    # Horizontal line
    ax.plot([xmin, xmax], [0, 0], color='#cccccc', linewidth=0.5, zorder=0)

    # Points
    for i in range(num_points):
        ax.plot(xs[i], 0, 'o', color='#333333', markersize=7, zorder=5)
        ax.text(xs[i], -0.35, str(i), ha='center', va='top', fontsize=10)

    # Arcs
    def draw_arc(a, b, above, color, lw=2.0):
        x1, x2 = xs[a], xs[b]
        cx = (x1 + x2) / 2
        width = abs(x2 - x1)
        height = width * 0.55
        theta1, theta2 = (0, 180) if above else (180, 360)
        arc = patches.Arc(
            (cx, 0), width, height,
            angle=0, theta1=theta1, theta2=theta2,
            color=color, linewidth=lw, zorder=3,
        )
        ax.add_patch(arc)

    for a, b in top:
        draw_arc(a, b, above=True, color=top_color)
    for a, b in bottom:
        draw_arc(a, b, above=False, color=bot_color)

    # Side labels
    max_span_top = max(b - a for a, b in top) if top else 1
    max_span_bot = max(b - a for a, b in bottom) if bottom else 1
    label_y_top = max_span_top * spacing * 0.55 / 2 + 0.3
    label_y_bot = -(max_span_bot * spacing * 0.55 / 2 + 0.3)
    ax.text(xmax + 0.3, label_y_top * 0.6, top_label,
            color=top_color, fontsize=11, va='center')
    ax.text(xmax + 0.3, label_y_bot * 0.6, bot_label,
            color=bot_color, fontsize=11, va='center')

    # Component annotation
    if show_components:
        comps = meandric_components(top, bottom)
        comp_str = f"{len(comps)} component{'s' if len(comps) != 1 else ''}"
        if len(comps) == 1:
            comp_str += " (meander)"
        comp_detail = ';  '.join(
            '{' + ', '.join(str(p) for p in c) + '}' for c in comps
        )
        ax.text(
            (xmin + xmax) / 2, label_y_bot - 0.6,
            f"{comp_str}:  {comp_detail}",
            ha='center', va='top', fontsize=9, color='#666666',
        )

    # Formatting
    ax.set_xlim(xmin, xmax + 1.5)
    y_extent = max(label_y_top, -label_y_bot) + 1.0
    ax.set_ylim(-y_extent, y_extent)
    ax.axis('off')
    if title:
        ax.set_title(title, fontsize=14, pad=12)
    fig.tight_layout()
    return fig, ax


def plot_element(
    domain: list[str],
    range_: list[str],
    *,
    title: str | None = None,
    **kwargs,
) -> tuple[plt.Figure, plt.Axes]:
    """Plot the meandric system of a Thompson group element.

    Parameters
    ----------
    domain, range_ : list of str
        Dyadic partitions (binary-string leaf addresses).
    title : str, optional
        Figure title.

    Returns
    -------
    (fig, ax)

    Examples
    --------
    >>> from meandric.elements import X0_DOMAIN, X0_RANGE
    >>> fig, ax = plot_element(X0_DOMAIN, X0_RANGE, title='$x_0$')
    """
    top, bottom = tree_pair_to_meandric(domain, range_)
    return plot_meandric(top, bottom, title=title, **kwargs)
