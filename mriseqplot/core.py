import numpy as np
import matplotlib.pyplot as plt
from typing import Callable, List
from mriseqplot.plot import _format_axes_base, _project_channel_on_time_axis, rcParams


class Sequence:
    """ Class to define and collect sequences of events (e.g gradient wavefronts)
    that all share the same time axis. This class is not meant to handle the job of
    representation of the events (refered to as channels).
    """

    def __init__(self, t, channels: List[str]):
        """ Initialize sequence diagram
        Parameters
        ----------
        t : np.array, 1D
            Sets the grid for all waveforms to be computed on
        channels : list of strings
            Names of the individual lines of the diagram. Example:
            ["RF", "PEG", "FEG", "SSG"]. As of now the order defines the order in which
            the lines will appear on the plot.
        ax2channel : dict, optional
            Defines the layout of the desired diagram.
            Maps from subplots (axes) represented by their labels to channels.
            If not given, every channel will be plotted in its own subplot and channel
            name will be used as subplots's ylabel.

        Axes are represented as a dictionary with axes names being the keys. Upon
        initialization all waveforms set to zero-filled arrays the same length as t.
        """
        self.t = t
        self.channels = {}
        for channel in channels:
            self.channels[channel] = np.full_like(t, np.nan, dtype=float)

    def add_element(self, channel_name: str, callback: Callable, ampl=1, **kwargs):
        """ Generic function to add an element to a waveform
        Parameters
        ----------
        channel_name : str
            Name of the axis to add an element to. Will raise a KeyError if the name
            was not given upon initialization
        callback : callable
            Function to compute the (unit amplitude) waveform of the element.
            Signature: fun(self.t, **kwargs)
        ampl : float, optional
            Desired amplitude of the element. Default: 1
        **kwargs : dict
            All keyword arguments which will be passed to the callback

        The function tests if the new waveform overlaps with anything present in the
        chosen axis and issues a warning if it does
        """
        unit = ampl * callback(self.t, **kwargs)

        # Stacking along a new dim needs explicit broadcasting if arrays mismatch
        tmp_stack = np.stack(
            np.broadcast_arrays(self.channels[channel_name], unit), axis=-1
        )
        # np.nan + anything is np.nan -> use nansum.
        sum_no_nan = np.nansum(tmp_stack, axis=-1)
        # Caveat: nansum substitutes all np.nan for 0s, which is undesirable
        # -> need to keep nans in both arrays manually
        both_nan = np.isnan(tmp_stack).all(axis=-1)
        self.channels[channel_name] = np.where(both_nan, np.nan, sum_no_nan)


class Diagram:
    """ Class to map a sequence of events on a figure and to handle the representation
    """

    def __init__(self, sequence, ax2channel=None):
        """
        Parameters
        ----------
        sequence : Sequence
        ax2channel : dict, optional
            Defines the layout of the desired diagram.
            Maps from subplots (axes) represented by their labels to channels.
            If not given, every channel will be plotted in its own subplot and channel
            name will be used as subplots's ylabel.
        """
        self.seq = sequence
        if ax2channel is None:
            # trivial map
            self.ax_names = [name for name in sequence.channels.keys()]
            self.channel_names = [name for name in sequence.channels.keys()]
        else:  # convert single labels to iterables
            self.ax_names = [ax_name for ax_name in ax2channel.keys()]
            self.channel_names = [
                [ch] if isinstance(ch, str) else ch for ch in ax2channel.keys()
            ]
        self.fig, self.axes = plt.subplots(
            nrows=len(self.ax_names), sharex=True, sharey=True
        )

    def plot_scheme(self):
        """ Plot the sequence diagram """
        # transAxes is easier to use when axes do not have arbitrary offset between
        plt.subplots_adjust(hspace=0)
        self._format_axes_base()
        self._format_axes_data()
        for ax, (label, channels) in zip(self.axes, self.ax2channel.items()):
            for name_channel in channels:
                self._plot_channel(ax, name_channel)

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

        # set consistent y-limit as maximum from all plots
        ylim = [0.0, 0.0]
        for signal in self.seq.channels.values():
            ylim[0] = min(ylim[0], padding_factor * np.nanmin(signal))
            ylim[1] = max(ylim[1], padding_factor * np.nanmax(signal))
        for ax in self.axes:
            ax.set_ylim(ylim)

        for ax, ax_name in zip(self.axes, self.ax_names):
            ax.set_ylabel(
                ax_name,
                rotation=0,
                verticalalignment="center",
                horizontalalignment="right",
                multialignment="center",
            )

    def _plot_time_axes(self):
        for ax, names_channel_per_ax in zip(self.axes, self.channel_names):
            channels_per_ax = [self.seq.channels[k] for k in names_channel_per_ax]
            axis = _project_channel_on_time_axis(channels_per_ax)
            # color needs fixing
            ax.plot(
                self.seq.t, axis, color=mpl.rcParams["axes.edgecolor"],
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

    def _plot_channel(self, ax, name_channel):
        signal = self.seq.channels[name_channel]
        style = self.axes_styles[name_channel]

        # plotting of the data
        signal_dims = signal.shape
        for dim in range(signal_dims[1]):
            plt_signal = signal[:, dim]

            ax.fill_between(
                self.t[:, 0],
                plt_signal,
                0,
                facecolor=style.color_fill,
                # edgecolor=[0, 0, 0, 0], # isn't it such by default?
                # do we ever want to see the line at all?
                # linewidth=style.axes_width + style.axes_width * 0,  # excuse me?
                # zorder=style.zorder + 5,
                # clip_on=False, # what's the use case?
            )

            ax.plot(
                self.t[:, 0],
                plt_signal,
                color=style.color,
                # linewidth=style.width, # mpl.rcParams["lines.linewidth"]
                # clip_on=False, # what's the use case?
                # do we need zorder here if it's plotted *after* fill_between?
                # zorder=style.zorder + 10,  # always on top of fill
            )
        # return ax
