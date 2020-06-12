import numpy as np
from mriseqplot.core import SeqDiagram
from mriseqplot.shapes import trapezoid
from mriseqplot.style import SeqStyle

# define the time axis
t = np.linspace(-0.2, 6, 10000)[:, None]

# create sequence diagram object
sequence = SeqDiagram(t, ["Slice Selection", "Phase Encoding", "Frequency Encoding"])

# set custom style for phase encoding and slice selection
style_ph = SeqStyle()
style_ph.color = [0.7, 0, 0]
sequence.axes_styles["Phase Encoding"] = style_ph

style_ss = SeqStyle()
style_ss.color = [0.0, 0, 0.7]
sequence.axes_styles["Slice Selection"] = style_ss

sequence.add_element(
    "Phase Encoding",
    trapezoid,
    # some broadcasting magic for stacked gradients
    ampl=np.array(np.linspace(-1, 1, 10))[None, :],
    t_start=1.2,
    t_flat_out=1.4,
    t_ramp_down=1.8,
)

sequence.add_element(
    "Frequency Encoding",
    trapezoid,
    ampl=-1,
    t_start=1.2,
    t_flat_out=1.4,
    t_ramp_down=1.8,
)
sequence.add_element(
    "Frequency Encoding",
    trapezoid,
    ampl=0.5,
    t_start=2,
    t_flat_out=2.2,
    t_ramp_down=3.8,
)

sequence.add_element(
    "Slice Selection", trapezoid, t_start=0, t_flat_out=0.2, t_ramp_down=1
)
sequence.add_element(
    "Slice Selection", trapezoid, ampl=-1, t_start=1.2, t_flat_out=1.4, t_ramp_down=1.8
)
sequence.plot_scheme()
