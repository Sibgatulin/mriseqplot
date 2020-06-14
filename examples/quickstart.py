import numpy as np
from mriseqplot.core import SeqDiagram
from mriseqplot.shapes import trapezoid
from mriseqplot.shapes import rf_sinc
from mriseqplot.style import SeqStyle

# define the time axis
t = np.linspace(-0.2, 6, 10000)[:, None]

# create sequence diagram object
sequence = SeqDiagram(
    t, ["RF/ADC", "Slice Selection", "Phase Encoding", "Frequency Encoding"]
)

# set custom style for phase encoding and slice selection
style_ph = SeqStyle()
style_ph.color = [0.7, 0, 0]
style_ph.color_fill = [0.7, 0, 0, 0.2]
sequence.axes_styles["Phase Encoding"] = style_ph

style_ss = SeqStyle()
style_ss.color = [0.0, 0, 0.7]
style_ss.color_fill = [0.0, 0, 0.7, 0.2]
sequence.axes_styles["Slice Selection"] = style_ss

style_rf = SeqStyle()
style_rf.color_fill = [0.2, 0.7, 0.2, 0.4]
sequence.axes_styles["RF/ADC"] = style_rf

sequence.add_element(
    "RF/ADC", rf_sinc, 1, t_start=0.2, duration=0.8, side_lobes=2,
)

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
