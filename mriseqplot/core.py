import warnings
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.transforms as transforms
from mriseqplot.style import SeqStyle
from typing import Callable, List
from mriseqplot.plot import _format_axes_base


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
        self.anno = {}
        self.channels = {}
        self.axes_styles = {}
        for channel in channels:
            self.channels[channel] = np.zeros_like(t)
            self.axes_styles[channel] = SeqStyle()
            self.anno[channel] = []

    def add_annotation(self, channel_name: str, t, ampl, **kwargs):
        text = kwargs.get("text", None)
        arrow = kwargs.get("arrow", None)
        style = kwargs.get("style", None)

        item = {"t": t, "ampl": ampl, "text": text, "arrow": arrow, "style": style}
        self.anno[channel_name].append(item)

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

    def _format_axes_data(self, axes, ax2channel, padding_factor=1.1):
        labels = ax2channel.keys()
        chan_axes = ax2channel.values()

        # set consistent y-limit as maximum from all plots
        ylim = [0.0, 0.0]
        for signal in self.channels.values():
            ylim[0] = min(ylim[0], padding_factor * np.min(signal))
            ylim[1] = max(ylim[1], padding_factor * np.max(signal))
        for chan_anno in self.anno.values():
            for anno in chan_anno:
                ampl = anno["ampl"]
                if isinstance(ampl, float):
                    ampl = [ampl]  # make list
                ylim[0] = min(ylim[0], min(ampl))
                ylim[1] = max(ylim[1], max(ampl))

        for ax, style, ax_name in zip(axes, self.axes_styles.values(), labels,):
            ax.set_ylabel(
                ax_name,
                fontsize=style.font_size,
                rotation=0,
                verticalalignment="center",
                horizontalalignment="right",
                multialignment="center",
            )

            # don't understand why keeping the default leaves blank space before arrow
            # and messes with the label position... 🤔
            ax.set_xlim(self.t[0], self.t[-1])
            ax.set_ylim(ylim[0], ylim[1])

        return axes

    def _plot_annotations(self, ax, name_channel):
        annotation = self.anno[name_channel]
        style = self.axes_styles[name_channel]

        for anno in annotation:
            t = anno["t"]
            ampl = anno["ampl"]

            # get style
            draw_style = style
            if anno["style"] is not None:
                draw_style = anno["style"]  # use channel style

    def _plot_channel(self, ax, name_channel):
        signal = self.channels[name_channel]
        style = self.axes_styles[name_channel]

        # plotting of the data
        signal_dims = signal.shape
        for dim in range(signal_dims[1]):
            plt_time = self.t
            plt_signal = signal[:, dim]

            # remove all points where it hits zero to avoid drawing on the axis
            remove_ind = np.argwhere(plt_signal == 0)
            edges_left = np.argwhere(np.diff(remove_ind, axis=0) > 1)
            edges_left = edges_left[:, 0]  # keep the left edge at zero
            edges_right = edges_left + 1  # keep the right edge at zero
            remove_ind = np.delete(
                remove_ind, np.concatenate((edges_left, edges_right))
            )
            # TODO: probably needs checking if remove_ind is within bounds
            # or just removal of all indices out of bounds
            plt_signal = np.delete(plt_signal, remove_ind)
            plt_time = np.delete(plt_time, remove_ind)

            ax.fill_between(
                plt_time,
                plt_signal,
                0,
                facecolor=style.color_fill,
                edgecolor=[0, 0, 0, 0],
                linewidth=style.axes_width + style.axes_width * 0,
                zorder=style.zorder + 5,
                clip_on=False,
            )

            ax.plot(
                plt_time,
                plt_signal,
                color=style.color,
                linewidth=style.width,
                clip_on=False,
                zorder=style.zorder + 10,  # always on top of fill
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

        axes = _format_axes_base(axes)
        axes = self._format_axes_data(axes, ax2channel)
        for ax, (label, channels) in zip(axes, ax2channel.items()):
            # only one channel for this axis
            if isinstance(channels, str):
                name_channel = channels
                self._plot_channel(ax, name_channel)
                self._plot_annotations(ax, name_channel)
            # this axis represents a number of channels
            elif isinstance(channels, (list, tuple)):
                for name_channel in channels:
                    self._plot_channel(ax, name_channel)
                    self._plot_annotations(ax, name_channel)

            style = self.axes_styles[name_channel]
            if style.axes_overlayed:
                # manually draw x-axes, first find the points where no data was drawn
                axis_data = np.arange(0, len(self.t))
                for line in ax.lines:
                    x_data = line.get_xdata()
                    ind = np.argwhere(x_data == self.t)
                    ind = ind[:, 0]
                    axis_data[ind[1:-1]] = -1

                # cut into sections and draw step by step
                sections = axis_data == -1
                cur_section = np.array([], dtype=np.int64)
                for iPoint in np.arange(0, len(self.t)):

                    if not sections[iPoint]:
                        cur_section = np.hstack([cur_section, axis_data[iPoint]])

                    if ((sections[iPoint]) or (iPoint == len(self.t) - 1)) and (
                        len(cur_section) > 0
                    ):
                        ax.plot(
                            self.t[cur_section],
                            np.zeros([len(cur_section), 1]),
                            color=style.axes_color,
                            linewidth=style.axes_width,
                            clip_on=False,
                            zorder=100,
                        )
                        cur_section = np.array([], dtype=np.int64)
            else:
                ax.plot(
                    np.array([self.t[0], self.t[-1]]),
                    np.array([0, 0]),
                    color=style.axes_color,
                    linewidth=style.axes_width,
                    clip_on=False,
                    zorder=100,
                )
        # transAxes is easier to use when axes do not have arbitrary offset between
        plt.subplots_adjust(hspace=0)
        return fig, axes

    def add_vline(self, axes_to_span, t, **kwargs):
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
        fig = plt.gcf()
        for ax in axes_to_span:
            trans = transforms.blended_transform_factory(ax.transData, ax.transAxes)
            line = plt.Line2D([t, t], [0, 1], transform=trans, **kwargs)
            fig.add_artist(line)
