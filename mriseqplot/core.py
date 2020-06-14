import warnings
import numpy as np
import matplotlib.pyplot as plt
from mriseqplot.style import SeqStyle
from typing import Callable, List


class SeqDiagram:
    def __init__(self, t, axes: List[str]):
        """ Initialize sequence diagram
        Parameters
        ----------
        t : np.array, 1D
            Sets the grid for all waveforms to be computed on
        axes : list of strings
            Names of the individual lines of the diagram. Example:
            ["RF", "PEG", "FEG", "SSG"]. As of now the order defines the order in which
            the lines will appear on the plot.
        Axes are represented as a dictionary with axes names being the keys. Upon
        initialization all waveforms set to zero-filled arrays the same length as t.
        """
        self.t = t
        self.axes = {}
        self.axes_names = {}
        self.axes_styles = {}
        for axis in axes:
            self.axes[axis] = np.zeros_like(t)
            self.axes_styles[axis] = SeqStyle()
            self.axes_names[axis] = axis

    def add_element(self, axis_name: str, callback: Callable, ampl=1, **kwargs):
        """ Generic function to add an element to a waveform
        Parameters
        ----------
        axis_name : str
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
        overlap = np.logical_and(self.axes[axis_name], unit)
        if overlap.any():
            warnings.warn(f"Got an overlap in {axis_name} using {callback.__name__}")
        self.axes[axis_name] = self.axes[axis_name] + unit

    def _format_axes(self, axes):
        # set consistent y-limit as maximum from all plots
        ylim = [0.0, 0.0]
        for signal in self.axes.values():
            ylim[0] = min(ylim[0], np.min(signal))
            ylim[1] = max(ylim[1], np.max(signal))

        for ax, style, ax_name in zip(
            axes, self.axes_styles.values(), self.axes_names.values(),
        ):
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

    def plot_scheme(self):
        """ Plot the sequence diagram """
        fig, axes = plt.subplots(nrows=len(self.axes), sharex=True, sharey=True)

        if len(self.axes) == 1:  # a little ugly workaround
            axes = [axes]

        axes = self._format_axes(axes)

        for ax, signal, style in zip(
            axes, self.axes.values(), self.axes_styles.values(),
        ):
            # plotting of the data
            signal_dims = signal.shape
            for dim in range(signal_dims[1]):
                plt_time = self.t
                plt_signal = signal[:, dim]

                # remove all points where it hits zero to avoid drawing on the axis
                remove_ind = np.where(plt_signal == 0)
                plt_signal = np.delete(plt_signal, remove_ind)
                plt_time = np.delete(plt_time, remove_ind)

                ax.fill_between(plt_time, plt_signal, color=style.color_fill)
                ax.plot(
                    plt_time,
                    plt_signal,
                    color=style.color,
                    linewidth=style.width,
                    clip_on=False,
                )

        plt.show()
