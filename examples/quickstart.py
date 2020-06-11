import numpy as np
from mriseqplot.core import SeqDiagram
from mriseqplot.shapes import trapezoid


t = np.linspace(0, 6, 1000)[:, None]  # needed for broadcasting later
sequence = SeqDiagram(t, ["Phase Encoding", "Frequency Encoding"])
sequence.add_element(
    "Phase Encoding",
    trapezoid,
    ampl=np.array([1, 1.5])[None, :],  # some broadcasting magic for stacked gradients
    t_start=1,
    t_flat_out=1,
    t_ramp_down=2,
)
sequence.add_element(
    "Frequency Encoding", trapezoid, ampl=-1, t_start=2, t_flat_out=2.2, t_ramp_down=2.8
)
sequence.add_element(
    "Frequency Encoding", trapezoid, t_start=3, t_flat_out=3.2, t_ramp_down=4.8
)
sequence.plot_scheme()
