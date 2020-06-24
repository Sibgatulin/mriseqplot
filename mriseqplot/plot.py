import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.transforms as transforms
from matplotlib.path import Path
from matplotlib.patches import FancyArrowPatch
from ipdb import set_trace

defaults_mpl = {
    "axes.linewidth": 2,
    "font.size": 20,
}
for k, v in defaults_mpl.items():
    # update mpl's defaults
    mpl.rcParams[k] = v

rcParams = {
    "arrow_width": 0.15,  # data coords
    "arrow_length": 0.01,  # axes coords
    "axes_ticks": False,
}

# need to set up default global style
def _format_axes_base(axes):
    """ Formats the axes according to the selected style.
        Only performs data independent formatting """

    for ax in axes:
        ax.set_yticks([])
        if not rcParams["axes_ticks"]:
            ax.set_xticks([])
        ax.set_xlabel("t")
        ax.xaxis.set_label_coords(1.05, 0.4)

        for side in ["left", "top", "right", "bottom"]:
            ax.spines[side].set_visible(False)
        ax.spines["bottom"].set_position("zero")

        trans = transforms.blended_transform_factory(ax.transAxes, ax.transData)
        ax.arrow(
            x=1.0,  # transAxes: axes coords
            y=0.0,  # transData: data coords
            dx=np.finfo(float).eps,  # must be smth
            dy=0,
            transform=trans,
            head_width=rcParams["arrow_width"],  # data coords
            head_length=rcParams["arrow_length"],  # axes coords
            fc=mpl.rcParams["axes.edgecolor"],
            ec=mpl.rcParams["axes.edgecolor"],
            clip_on=False,
        )
    return axes


def _plot_label(ax, x, y, text):
    ax.text(
        x, y, text, horizontalalignment="center", verticalalignment="bottom",
    )
    return ax


def _plot_hline(ax, xs, y, text=None, arrow_style="<|-|>"):
    if text is not None:
        x_label = np.mean(xs)
        y_label = y  # why would it ever be a vector?
        _plot_label(ax, x_label, y_label, text)

    dx = xs[1] - xs[0]
    dy = np.finfo(float).eps
    # the most versatile way to create all sorts of arrows
    ax.annotate(
        "", xy=(xs[0], y), xytext=(xs[1], y), arrowprops=dict(arrowstyle=arrow_style),
    )
    return ax


def _plot_vline(axes_to_span, t, **kwargs):
    """ Add vertical lines to specified axes

    Unlike many (all) other ``add_`` methods, this method operates on axes
    (i.e. subplots), which justifies it acting on all axes at once, rather than
    adding individual vertical plots to each channel, as elements are added.
    As of now it expects actual axes to work on, rather than their labels
    (which are defined as ax2channel keys)

    Parameters
    ----------
    axes_to_span : iterable of matplotlib's axes
        Axes to draw a vertical line over
    t : float
        Point in time where to add a line
    **kwargs
        Other optional arguments are passed to plt.Line2D constructor
    """
    for ax in axes_to_span:
        trans = transforms.blended_transform_factory(ax.transData, ax.transAxes)
        line = plt.Line2D([t, t], [0, 1], transform=trans, **kwargs)
        ax.add_artist(line)


def _time_axis_as_disconected_path(channels):
    """ Build a mpl.path.Path object which shows axis where all channels are empty
    Parameters
    ----------
    channels : iterable of numpy arrays of shape (n, ) or (n, m)
    """

    tmp_stack = np.concatenate(np.broadcast_arrays(*channels), axis=1)
    all_nan = np.isnan(tmp_stack).all(axis=1)
    verts_x = np.linspace(0, 1, len(all_nan))  # equiv. to the length of the time axis
    verts = [(xi, 0) for xi in verts_x]
    codes = [Path.LINETO if nan else Path.MOVETO for nan in all_nan]
    path = Path([(0, 0)] + verts, [Path.MOVETO] + codes)
    return FancyArrowPatch(path=path)
