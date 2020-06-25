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
if args.colors:
    style = {}
if args.colorblind:
    style = {}
    import seaborn as sns

    sns.set_palette("colorblind")
else:
    style = dict(colors=["k"] * 5, alpha=0.0)

t = np.linspace(-0.2, 20, 10000)[:, None]
axes_map = {
    "RF/ADC": ["RF", "ADC"],
    "Phase\nEncoding": "Phase",
    "Slice\nSelection": "Slice",
    "Frequency\nEncoding": "Frequency",
}

rf = Channel(t).add_element(rf_sinc, 1, t_start=0.2, duration=0.8, side_lobes=2)
grad_slice = Channel(t).add_element(trapezoid, t_start=0, t_flat_out=0.2, t_ramp_down=1)
grad_slice.add_element(trapezoid, ampl=-1, t_start=1.2, t_flat_out=1.4, t_ramp_down=1.8)

n_epi_steps = 8
t_epi_start = 2.2
dt_line = 1.6  # duration of the entire readout gradient (the bottom)
dt_flat = 1.4  # duration of the full-on readout gradient (the top)
dt_ramp_up = 0.5 * (dt_line - dt_flat)
dt_line0 = 0.8  # duration of the entire dephasing readout gradient
dt_flat0 = 0.6  # duration of the full-on dephasing readout gradient
t_start_block = t_epi_start + dt_line0
dt_ramp_up0 = 0.5 * (dt_line0 - dt_flat0)
dt_blip_bottom = dt_line - dt_flat
dt_blip_top = 0.8 * dt_blip_bottom
dt_blip_ramp = 0.5 * (dt_blip_bottom - dt_blip_top)
# Readout
# Dephasing first
grad_freq = Channel(t).add_element(
    trapezoid,
    ampl=-1,
    t_start=t_epi_start,
    t_flat_out=t_epi_start + dt_ramp_up0,
    t_ramp_down=t_epi_start + dt_ramp_up0 + dt_flat0,
)
# Now the train of identical gradients
for idx in range(n_epi_steps):
    ampl = (-1) ** (idx % 2)
    t_start_grad = t_start_block + dt_line * idx
    grad_freq.add_element(
        trapezoid,
        ampl,
        t_start=t_start_grad,
        t_flat_out=t_start_grad + dt_ramp_up,
        t_ramp_down=t_start_grad + dt_ramp_up + dt_flat,
    )
# Phase
# Dephasing first
grad_phase = Channel(t).add_element(
    trapezoid,
    ampl=-2,
    t_start=t_epi_start,
    t_flat_out=t_epi_start + dt_ramp_up0,
    t_ramp_down=t_epi_start + dt_ramp_up0 + dt_flat0,
)
# Now the train of identical gradients
for idx in range(1, n_epi_steps):
    t_start_grad = t_start_block + dt_line * idx - 0.5 * dt_blip_bottom
    grad_phase.add_element(
        trapezoid,
        ampl=0.5,
        t_start=t_start_grad,
        t_flat_out=t_start_grad + dt_blip_ramp,
        t_ramp_down=t_start_grad + dt_blip_ramp + dt_blip_top,
    )
# ADC
adc = Channel(t)
for idx in range(n_epi_steps):
    t_start_adc = t_start_block + dt_line * idx + 0.5 * dt_blip_bottom
    adc.add_element(rect, ampl=0.5, t_start=t_start_adc, duration=dt_flat)

axes_map = {
    "RF/ADC": [rf, adc],
    "Phase\nEncoding": grad_phase,
    "Slice\nSelection": grad_slice,
    "Frequency\nEncoding": grad_freq,
}
sequence = Diagram(axes_map)
sequence.plot_scheme(**style)
# annotations to highlight the relation between elements
sequence._plot_vline(slice(None), t=t_epi_start, linestyle=":", color="C0", alpha=0.5)
sequence._plot_vline(
    slice(None), t=t_start_block, linestyle="--", color="C1", alpha=0.5
)
sequence._plot_vline(
    slice(None),
    t=t_start_block + dt_ramp_up + dt_flat,
    linestyle="--",
    color="C2",
    alpha=0.5,
)
sequence._plot_vline(
    slice(None),
    t=t_start_block + dt_ramp_up + dt_flat + dt_blip_bottom,
    linestyle="--",
    color="C2",
    alpha=0.5,
)
plt.show()
