import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.transforms as transforms
import scipy.ndimage as ndi

defaults_mpl = {
    "axes.linewidth": 2,
    "font.size": 20,
}
for k, v in defaults_mpl.items():
    # update mpl's defaults
    mpl.rcParams[k] = v

rcParams = {
    "arrow_width": 0.15,  # data coords
    "arrow_length": 0.20,  # data coords
    "axes_ticks": False,
}

# need to set up default global style


def _plot_label(ax, x, y, text, **kwargs):
    ax.text(
        x, y, text, horizontalalignment="center", verticalalignment="bottom", **kwargs
    )
    return ax


def _plot_hline(ax, xs, y, text=None, arrow_style="<|-|>", text_kws={}, **kwargs):
    if text is not None:
        x_label = np.mean(xs)
        y_label = y  # why would it ever be a vector?
        _plot_label(ax, x_label, y_label, text, **text_kws)

    # the most versatile way to create all sorts of arrows
    arrow_kws = {"arrowstyle": arrow_style, **kwargs}
    ax.annotate(
        "", xy=(xs[0], y), xytext=(xs[1], y), arrowprops=arrow_kws,
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


def _project_channel_on_time_axis(channels):
    """ Build a mpl.path.Path object which shows axis where all channels are empty
    Parameters
    ----------
    channels : iterable of numpy arrays of shape (n, ) or (n, m)
    """

    tmp_stack = np.concatenate(np.broadcast_arrays(*channels), axis=1)
    all_nan = np.isnan(tmp_stack).all(axis=1)
    all_nan_dil = ndi.binary_dilation(all_nan, np.ones(3,))
    axis = np.where(all_nan_dil, 0, np.nan)
    return axis
