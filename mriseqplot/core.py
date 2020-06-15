import warnings
import numpy as np
import matplotlib.pyplot as plt
from mriseqplot.style import SeqStyle
from typing import Callable, List


class Sequence:
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
        Axes are represented as a dictionary with axes names being the keys. Upon
        initialization all waveforms set to zero-filled arrays the same length as t.
        """
        self.t = t
        self.channels = {}
        self.axes_names = {}
        self.axes_styles = {}
        for channel in channels:
            self.channels[channel] = np.zeros_like(t)
            self.axes_styles[channel] = SeqStyle()
            self.axes_names[channel] = channel

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
        overlap = np.logical_and(self.channels[channel_name], unit)
        if overlap.any():
            warnings.warn(f"Got an overlap in {channel_name} using {callback.__name__}")
        self.channels[channel_name] = self.channels[channel_name] + unit

    def _format_axes(self, axes, labels):
        # set consistent y-limit as maximum from all plots
        ylim = [0.0, 0.0]
        for signal in self.channels.values():
            ylim[0] = min(ylim[0], np.min(signal))
            ylim[1] = max(ylim[1], np.max(signal))

        for ax, style, ax_name in zip(axes, self.axes_styles.values(), labels,):
            ax.set_yticks([])
            ax.set_ylabel(
                ax_name,
                fontsize=style.font_size,
                rotation=0,
                verticalalignment="center",
                horizontalalignment="right",
                multialignment="center",
            )
            if not style.axes_ticks:
                ax.set_xticks([])
            ax.set_xlabel("t", fontsize=style.font_size)
            ax.xaxis.set_label_coords(1.02, 0.4)

            for side in ["left", "top", "right"]:
                ax.spines[side].set_visible(False)
            ax.spines["bottom"].set_position("zero")

            for side in ["bottom", "left", "top", "right"]:
                ax.spines[side].set_linewidth(style.axes_width)
                ax.spines[side].set_color(style.axes_color)

            ax.axes.set_xlim(self.t[0], self.t[-1])
            ax.axes.set_ylim(ylim[0], ylim[1])

            ax.axes.arrow(
                0,
                0,
                np.squeeze(self.t[-1]),
                0,
                head_width=0.15,
                head_length=0.1,
                fc=style.axes_color,
                ec=style.axes_color,
                clip_on=False,
            )
        return axes

    def _plot_channel(self, ax, signal, style):
        # plotting of the data
        signal_dims = signal.shape
        for dim in range(signal_dims[1]):
            plt_time = self.t
            plt_signal = signal[:, dim]

            # remove all points where it hits zero to avoid drawing on the axis
            remove_ind = np.where(plt_signal == 0)
            plt_signal = np.delete(plt_signal, remove_ind)
            plt_time = np.delete(plt_time, remove_ind)

            ax.fill_between(
                plt_time,
                plt_signal,
                0,
                color=style.color_fill,
                edgecolor=[1, 0, 0, 1],
                linewidth=style.axes_width + style.axes_width * 0.5,
                zorder=style.zorder,
                clip_on=False,
            )
            ax.plot(
                plt_time,
                plt_signal,
                color=style.color,
                linewidth=style.width,
                clip_on=False,
                zorder=style.zorder + 10,
            )
        return ax

    def plot_scheme(self, ax2channel=None):
        """ Plot the sequence diagram

        Parameters
        ----------
        ax2channel : iterable, optional
            Mapping from subplot / axes labels to channels.
            If not given, every channel will be plotted in its own subplot and channel
            name will be used as subplots's ylabel.
        """
        if ax2channel is None:
            # trivial map
            ax2channel = {name: name for name in self.channels.keys()}

        fig, axes = plt.subplots(nrows=len(ax2channel), sharex=True, sharey=True)

        if len(self.channels) == 1:  # a little ugly workaround
            axes = [axes]

        axes = self._format_axes(axes, ax2channel.keys())

        for ax, (label, channels) in zip(axes, ax2channel.items()):
            # only one channel for this axis
            if isinstance(channels, str):
                name_channel = channels
                self._plot_channel(
                    ax, self.channels[name_channel], self.axes_styles[name_channel]
                )
            # this axis represents a number of channels
            elif isinstance(channels, (list, tuple)):
                for name_channel in channels:
                    self._plot_channel(
                        ax, self.channels[name_channel], self.axes_styles[name_channel]
                    )

        plt.show()
