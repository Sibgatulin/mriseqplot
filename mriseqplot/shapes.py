import numpy as np


def trapezoid(t, t_start, t_flat_out, t_ramp_down):
    """ A symmetrical trapezoid of unit height
    Parameters
    ----------
    t : array_like, 1D
        Vector of time values, specifying the entire domain of the sequence
    t_start : float
        Moment in time when the gradient is switched on and starts to linearly ramp up
    t_flat_out : float
        Moment in time when the gradient is fully on and stays constant after
    t_ramp_down : float
        Moment in time when the gradient starts to ramp down. Ramp down time in this
        function is considered to be the same as the rump up.

    Returns
    -------
    x : np.array, 1D
        Array of the same dtype as t, representing the trapezoid gradient
    """
    x = np.zeros_like(t)
    dt_ramp = t_flat_out - t_start
    idx_ramp_up = (t_start < t) & (t <= t_flat_out)
    idx_flat = (t_flat_out < t) & (t <= t_ramp_down)
    idx_ramp_down = (t_ramp_down < t) & (t <= t_ramp_down + dt_ramp)
    x[idx_ramp_up] = (t[idx_ramp_up] - t_start) / dt_ramp
    x[idx_flat] = 1
    x[idx_ramp_down] = (t_ramp_down - t[idx_ramp_down]) / dt_ramp + 1
    return x
