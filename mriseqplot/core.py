import numpy as np
import matplotlib.pyplot as plt
from mriseqplot.style import SeqStyle
from typing import Callable, List
from mriseqplot.plot import _format_axes_base, _project_channel_on_time_axis, rcParams


class Sequence:
    def __init__(self, t, channels: List[str], ax2channel=None):
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
        self.axes_styles = {}
        for channel in channels:
            self.channels[channel] = np.full_like(t, np.nan, dtype=float)
            self.axes_styles[channel] = SeqStyle()

        if ax2channel is None:
            # trivial map
            self.ax2channel = {name: [name] for name in channels}
        else:  # convert single labels to iterables
            self.ax2channel = {
                k: [v] if isinstance(v, str) else v for k, v in ax2channel.items()
            }

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

    def _format_axes_data(self, axes, padding_factor=1.1):
        labels = self.ax2channel.keys()
        chan_axes = self.ax2channel.values()

        # set consistent y-limit as maximum from all plots
        ylim = [0.0, 0.0]
        for signal in self.channels.values():
            ylim[0] = min(ylim[0], padding_factor * np.nanmin(signal))
            ylim[1] = max(ylim[1], padding_factor * np.nanmax(signal))
        for ax in axes:
            ax.set_ylim(ylim)

        for ax, style, ax_name in zip(axes, self.axes_styles.values(), labels):
            ax.set_ylabel(
                ax_name,
                fontsize=style.font_size,
                rotation=0,
                verticalalignment="center",
                horizontalalignment="right",
                multialignment="center",
            )
        for ax, channel_names in zip(axes, chan_axes):
            channels = [self.channels[k] for k in channel_names]
            axis = _project_channel_on_time_axis(channels)
            ax.plot(
                self.t, axis, lw=style.axes_width, color=style.axes_color,
            )
            ax.arrow(
                x=self.t[-1],
                y=0.0,
                dx=np.finfo(float).eps,  # must be smth
                dy=0,
                head_width=rcParams["arrow_width"],  # data coords
                head_length=rcParams["arrow_length"],  # axes coords
                fc=style.axes_color,
                ec=style.axes_color,
                # clip_on=False, # why exactly?
            )

        return axes

    def _plot_channel(self, ax, name_channel):
        signal = self.channels[name_channel]
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
                linewidth=style.width,
                # clip_on=False, # what's the use case?
                # do we need zorder here if it's plotted *after* fill_between?
                # zorder=style.zorder + 10,  # always on top of fill
            )
        return ax

    def plot_scheme(self):
        """ Plot the sequence diagram """
        fig, axes = plt.subplots(nrows=len(self.ax2channel), sharex=True, sharey=True)

        # Following workaround might not make sense in the light of all changes,
        # TODO: write a test
        if len(self.channels) == 1:  # a little ugly workaround
            axes = [axes]

        axes = _format_axes_base(axes)
        axes = self._format_axes_data(axes)
        for ax, (label, channels) in zip(axes, self.ax2channel.items()):
            for name_channel in channels:
                self._plot_channel(ax, name_channel)

        # transAxes is easier to use when axes do not have arbitrary offset between
        plt.subplots_adjust(hspace=0)
        return fig, axes
