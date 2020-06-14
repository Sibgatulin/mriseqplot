import numpy as np
from mriseqplot.core import Sequence
from mriseqplot.shapes import trapezoid
from mriseqplot.shapes import rf_sinc


# define the time axis
t = np.linspace(-0.2, 4.5, 10000)[:, None]

# create sequence diagram object
sequence = Sequence(t, ["RF", "ADC", "Slice", "Phase", "Frequency"])

sequence.add_element(
    "RF", rf_sinc, 1, t_start=0.2, duration=0.8, side_lobes=2,
)
sequence.add_element(
    "ADC",
    trapezoid,
    # temp solution until we introduce proper box shape
    ampl=np.array([-0.5, 0.5])[None, :],
    t_start=2.2,
    t_flat_out=2.2,
    t_ramp_down=3.8,
)

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
sequence.plot_scheme(axes_map)
