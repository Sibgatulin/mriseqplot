import numpy as np
from mriseqplot.core import SeqDiagram
from mriseqplot.shapes import trapezoid


t = np.linspace(0, 6, 100)
sequence = SeqDiagram(t, ["PEG", "FEG"])
sequence.add_element("PEG", trapezoid, ampl=2, t_start=1, t_flat_out=1, t_ramp_down=2)
sequence.add_element(
    "FEG", trapezoid, ampl=-1, t_start=2, t_flat_out=2.2, t_ramp_down=2.8
)
sequence.add_element("FEG", trapezoid, t_start=3, t_flat_out=3.2, t_ramp_down=4.8)
sequence.plot_scheme()
