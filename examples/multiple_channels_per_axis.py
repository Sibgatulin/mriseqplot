import argparse
import numpy as np
import matplotlib.pyplot as plt
from mriseqplot.core import Sequence
from mriseqplot.style import SeqStyle
from mriseqplot.shapes import adc, rf_sinc, trapezoid

parser = argparse.ArgumentParser()
parser.add_argument(
    "--colors",
    action="store_true",
    help="Produce a coloured diagram as opposed to black and white one",
)
args = parser.parse_args()

# define the time axis
t = np.linspace(-0.2, 4.5, 10000)[:, None]

# create sequence diagram object
sequence = Sequence(t, ["RF", "ADC", "Slice", "Phase", "Frequency"])

# set custom style for phase encoding and slice selection
if args.colors:
    style_ph = SeqStyle()
    style_ph.color = [0.7, 0, 0]
    style_ph.color_fill = [0.7, 0, 0, 0.2]
    style_ph.zorder = 10
    sequence.axes_styles["Phase"] = style_ph

    style_ss = SeqStyle()
    style_ss.color = [0.0, 0, 0.7]
    style_ss.color_fill = [0.0, 0, 0.7, 0.2]
    sequence.axes_styles["Slice"] = style_ss

    style_rf = SeqStyle()
    style_rf.color_fill = [0.6, 0.8, 0.6, 1.0]
    style_rf.zorder = 10
    sequence.axes_styles["RF"] = style_rf

    style_adc = SeqStyle()
    style_adc.color_fill = [0.9, 0.9, 0.6, 1.0]
    sequence.axes_styles["ADC"] = style_adc
else:
    style_clear = SeqStyle()
    style_clear.color = [0.0, 0, 0]
    style_clear.color_fill = [1.0, 1.0, 1.0, 1.0]
    style_clear.zorder = 10
    sequence.axes_styles["Frequency"] = style_clear
    sequence.axes_styles["Phase"] = style_clear
    sequence.axes_styles["Slice"] = style_clear
    sequence.axes_styles["RF"] = style_clear
    sequence.axes_styles["ADC"] = style_clear

sequence.add_element(
    "RF", rf_sinc, 1, t_start=0.2, duration=0.8, side_lobes=2,
)
sequence.add_annotation("RF", 0.6, -0.6, text="90° Excitation Pulse")
sequence.add_annotation("RF", [0.6, 3.0], [1.4, 1.4], text="Echo-Time (TE)", arrow=True)

sequence.add_element(
    "ADC", adc, ampl=1, t_start=2.2, duration=1.6,
)
sequence.add_annotation("ADC", 3.0, 0.5, text="Data Sampling")

sequence.add_element(
    "Phase",
    trapezoid,
    # some broadcasting magic for stacked gradients
    ampl=np.linspace(-1, 1, 10)[None, :],
    t_start=1.2,
    t_flat_out=1.4,
    t_ramp_down=1.8,
)

sequence.add_element(
    "Frequency", trapezoid, ampl=-1, t_start=1.2, t_flat_out=1.4, t_ramp_down=1.8,
)
sequence.add_element(
    "Frequency", trapezoid, ampl=0.5, t_start=2, t_flat_out=2.2, t_ramp_down=3.8,
)

sequence.add_element("Slice", trapezoid, t_start=0, t_flat_out=0.2, t_ramp_down=1)
sequence.add_element(
    "Slice", trapezoid, ampl=-1, t_start=1.2, t_flat_out=1.4, t_ramp_down=1.8
)

axes_map = {
    "RF/ADC": ["RF", "ADC"],
    "Phase\nEncoding": "Phase",
    "Slice\nSelection": "Slice",
    "Frequency\nEncoding": "Frequency",
}
fig, axes = sequence.plot_scheme(axes_map)
sequence.add_vline(axes, t=3.0, linestyle=":", color="k", alpha=0.5)
sequence.add_vline(axes, t=0.6, linestyle=":", color="k", alpha=0.5)
plt.show()
