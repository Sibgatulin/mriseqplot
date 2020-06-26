import argparse
import numpy as np
import matplotlib.pyplot as plt
from mriseqplot.core import Channel, Diagram
from mriseqplot.shapes import rect, rf_sinc, trapezoid

parser = argparse.ArgumentParser()
parser.add_argument(
    "--colors",
    action="store_true",
    help="Produce a coloured diagram as opposed to black and white one",
)
parser.add_argument(
    "--colorblind", action="store_true", help="Use Seaborn colorblind palette",
)
args = parser.parse_args()
print(args)
if args.colors:
    colors = [
        [0.0, 0.0, 0.0],
        [0.9, 0.5, 0.0],
        [0.7, 0.0, 0.0],
        [0.0, 0.0, 0.7],
        [0.0, 0.0, 0.0],
    ]
    style = dict(colors=colors, alpha=0.2)
elif args.colorblind:
    style = {}
    import seaborn as sns

    sns.set_palette("colorblind")
else:
    style = dict(colors=["k"] * 5, alpha=0.0)

# define the time axis
t = np.linspace(-0.2, 4.5, 10000)[:, None]

rf = Channel(t)
rf.add_element(rf_sinc, 1, t_start=0.2, duration=0.8, side_lobes=2)

adc = Channel(t)
adc.add_element(rect, ampl=1, t_start=2.2, duration=1.6)

grad_phase = Channel(t)
grad_phase.add_element(
    trapezoid,
    # some broadcasting magic for stacked gradients
    ampl=np.linspace(-1, 1, 10)[None, :],
    t_start=1.2,
    t_flat_out=1.4,
    t_ramp_down=1.8,
)
grad_freq = Channel(t)
grad_freq.add_element(
    trapezoid, ampl=-1, t_start=1.2, t_flat_out=1.4, t_ramp_down=1.8,
)
grad_freq.add_element(
    trapezoid, ampl=0.5, t_start=2, t_flat_out=2.2, t_ramp_down=3.8,
)

grad_slice = Channel(t)
grad_slice.add_element(trapezoid, t_start=0, t_flat_out=0.2, t_ramp_down=1)
grad_slice.add_element(trapezoid, ampl=-1, t_start=1.2, t_flat_out=1.4, t_ramp_down=1.8)

axes_map = {
    "RF/ADC": [rf, adc],
    "Phase\nEncoding": grad_phase,
    "Slice\nSelection": grad_slice,
    "Frequency\nEncoding": grad_freq,
}

sequence = Diagram(axes_map)
sequence.plot_scheme(**style)
sequence._plot_vline(axes_idx=slice(None), t=3.0, linestyle=":", color="k", alpha=0.5)
sequence._plot_vline(axes_idx=slice(None), t=0.6, linestyle=":", color="k", alpha=0.5)
sequence._plot_label(ax_idx=0, x=0.6, y=-0.6, text="90° Excitation Pulse")
sequence._plot_label(ax_idx=0, x=3.0, y=0.3, text="Data Sampling")
sequence._plot_hline(
    ax_idx=0, xs=[0.6, 3.0], y=1.4, text="Echo-Time (TE)", facecolor="k"
)
sequence.axes[0].set_ylim([-1, 2])
plt.show()
