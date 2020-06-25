import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.transforms as transforms
from typing import Callable
from mriseqplot.plot import _project_channel_on_time_axis, rcParams


class Channel:
    """ Class to define and collect sequences of events (e.g. gradient wavefronts)
    that all share the same time axis. This class is not meant to handle the job of
    representation of the events (aptly referred to as channels).
    """

    def __init__(self, t):
        """ Initialize a sequence of events
        Parameters
        ----------
        t : np.array, 1D
            Sets the grid for all waveforms to be computed on
        """
        # does not copy data, assigns a pointer
        self.time = t
        self.data = np.full_like(t, np.nan, dtype=float)
        # a little field which helps to represent and identify the channel
        self._elements = []

    def add_element(self, callback: Callable, ampl=1, **kwargs):
        """ Generic function to add an element to a waveform
        Parameters
        ----------
        callback : callable
            Function to compute the (unit amplitude) waveform of the element.
            Signature: fun(self.t, **kwargs)
        ampl : float, optional
            Desired amplitude of the element. Default: 1
        **kwargs : dict
            All keyword arguments which will be passed to the callback
        """
        unit = ampl * callback(self.time, **kwargs)

        # Stacking along a new dim needs explicit broadcasting if arrays mismatch
        tmp_stack = np.stack(np.broadcast_arrays(self.data, unit), axis=-1)
        # np.nan + anything is np.nan -> use nansum.
        sum_no_nan = np.nansum(tmp_stack, axis=-1)
        # Caveat: nansum substitutes all np.nan for 0s, which is undesirable
        # -> need to keep nans in both arrays manually
        both_nan = np.isnan(tmp_stack).all(axis=-1)
        self.data = np.where(both_nan, np.nan, sum_no_nan)
        self._elements.append(callback.__name__)
        return self

    def __repr__(self):
        return f"channel with {self._elements}"


class Diagram:
    """ Class to map a sequence of events on a figure and to handle the representation
    """

    def __init__(self, ax2channel):
        """ Map channels to axes on a figure

        Parameters
        ----------
        ax2channel : dict
            Defines the layout of the desired diagram.
            Maps from subplots (axes) represented by their labels to channels.
        """
        # convert single channels to iterables
        self.ax2ch = {
            k: [ch] if isinstance(ch, Channel) else ch for k, ch in ax2channel.items()
        }
        self.fig, self.axes = plt.subplots(
            nrows=len(self.ax2ch), sharex=True, sharey=True
        )
        self.channels = [ch for chs in self.ax2ch.values() for ch in chs]
        # test how it works if len(self.channels) == 1
        # Potentially makes sense to use np.allclose(self.channels[0].time, ch.time)
        # but I compare not just the equivalence but actually being the same array 🤷
        if not all([self.channels[0].time is ch.time for ch in self.channels[1:]]):
            raise ValueError("Not all of the given channels share the same time axis")
        self.t = self.channels[0].time

    def plot_scheme(self, colors=None, alpha=0.3, time_axis_on_top=False):
        """ Plot the sequence diagram

        Parameters
        ----------
        colors : iterable, optional
            Iterable of valid matplotlib colors for every channel. If not given, default
            matplotlib's color cycle is used (i.e. Tableau Colors from the 'tab10'
            categorical palette)
        alpha : float, optional
            Global alpha channel value for the filling under every channel's profile
        time_axis_on_top : bool, optional
            If to draw the time axis on top of the waveforms, or only where no event
            present. Default: False
        """

        if colors is None:
            colors = [f"C{idx}" for idx in range(len(self.channels))]
        if len(colors) != len(self.channels):
            raise ValueError("If given, colors must match total number of channels")
        color_cycle = colors[::-1]  # reversed copy

        # transAxes is easier to use when axes do not have arbitrary offset between
        plt.subplots_adjust(hspace=0)
        self._format_axes_base()
        self._format_axes_data()
        for ax, channels in zip(self.axes, self.ax2ch.values()):
            for channel in channels:
                self._plot_channel(ax, channel, color=color_cycle.pop(), alpha=alpha)
        self._plot_time_axes(time_axis_on_top)

    def _format_axes_base(self):
        """ Formats the axes according to the selected style.
            Only performs data independent formatting """
        for ax in self.axes:
            ax.set_yticks([])
            if not rcParams["axes_ticks"]:
                ax.set_xticks([])
            ax.set_xlabel("t")
            ax.xaxis.set_label_coords(1.05, 0.4)

            for side in ["left", "top", "right", "bottom"]:
                ax.spines[side].set_visible(False)

    def _format_axes_data(self, padding_factor=1.1):
        """ Data specific axes formatting, such as ylim setting and ylabels """
        # set consistent y-limit as maximum from all plots
        ylim = [0.0, 0.0]
        for signal in self.channels:
            ylim[0] = min(ylim[0], padding_factor * np.nanmin(signal.data))
            ylim[1] = max(ylim[1], padding_factor * np.nanmax(signal.data))
        for ax in self.axes:
            ax.set_ylim(ylim)

        for ax, ax_name in zip(self.axes, self.ax2ch.keys()):
            ax.set_ylabel(
                ax_name,
                rotation=0,
                verticalalignment="center",
                horizontalalignment="right",
                multialignment="center",
            )

    def _plot_time_axes(self, time_axis_on_top=False):
        """ Plot time axes for each axis

        Parameters
        ----------
        time_axis_on_top : bool, optional
            If True, the time axis will be drawn on top of the channels,
            otherwise will only be visible where no waveform is present

        """
        for ax, channels in zip(self.axes, self.ax2ch.values()):
            if time_axis_on_top:
                axis = np.zeros_like(self.t)
            else:
                signals = [ch.data for ch in channels]
                axis = _project_channel_on_time_axis(signals)

            # color needs fixing
            ax.plot(
                self.t, axis, color=mpl.rcParams["axes.edgecolor"],
            )
            ax.arrow(
                x=self.t[-1],
                y=0.0,
                dx=np.finfo(float).eps,  # must be smth
                dy=0,
                head_width=rcParams["arrow_width"],  # data coords
                head_length=rcParams["arrow_length"],  # axes coords
                fc=mpl.rcParams["axes.edgecolor"],
                ec=mpl.rcParams["axes.edgecolor"],
                # clip_on=False, # why exactly?
            )

    def _plot_channel(self, ax, channel, color, alpha=0.3):
        """ Plot given channel on a given axis with given color, simple, huh? """
        # That  needs to be tested against channels of shape (n,). How did it work?
        for signal in channel.data.T:
            ax.fill_between(
                self.t[:, 0],
                signal,
                alpha=alpha,
                facecolor=color,  # temporarily simplification
            )
            ax.plot(
                self.t[:, 0],
                signal,
                color=color,
                # linewidth=style.width, # mpl.rcParams["lines.linewidth"]
            )

    # I am still not sold on whether these must be methods of the class at all
    def _plot_label(self, ax_idx, x, y, text, **kwargs):
        self.axes[ax_idx].text(
            x,
            y,
            text,
            horizontalalignment="center",
            verticalalignment="bottom",
            **kwargs,
        )

    def _plot_hline(
        self, ax_idx, xs, y, text=None, arrow_style="<|-|>", text_kws={}, **kwargs
    ):
        if text is not None:
            x_label = np.mean(xs)
            y_label = y  # why would it ever be a vector?
            self._plot_label(ax_idx, x_label, y_label, text, **text_kws)

        # the most versatile way to create all sorts of arrows
        arrow_kws = {"arrowstyle": arrow_style, **kwargs}
        self.axes[ax_idx].annotate(
            "", xy=(xs[0], y), xytext=(xs[1], y), arrowprops=arrow_kws,
        )

    def _plot_vline(self, axes_idx, t, **kwargs):
        """ Add vertical lines to specified axes

        Parameters
        ----------
        axes_idx : iterable of integers or slice
            Indices of the axes to draw a vertical line over
        t : float
            Point in time where to add a line
        **kwargs
            Other optional arguments are passed to plt.Line2D constructor
        """
        for ax in self.axes[axes_idx]:
            trans = transforms.blended_transform_factory(ax.transData, ax.transAxes)
            line = plt.Line2D([t, t], [0, 1], transform=trans, **kwargs)
            ax.add_artist(line)
