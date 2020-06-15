import numpy as np


def rf_sinc(t, t_start, duration, side_lobes):
    y = np.zeros_like(t)
    idx_rf = (t > t_start) & (t < t_start + duration)
    t_rf = t[idx_rf] - t_start - duration / 2
    y[idx_rf] = np.sin(t_rf / duration * 2 * np.pi * (side_lobes + 1)) / t_rf
    y[idx_rf] = y[idx_rf] / np.max(y[idx_rf])
    return y


def adc(t, t_start, duration):
    y = np.zeros_like(t)
    idx_rf = np.argwhere((t > t_start) & (t < t_start + duration))
    idx_rf = idx_rf[:, 0]
    y[idx_rf] = 1
    y[idx_rf[0]] = np.finfo(np.float32).eps  # edges down to zero
    y[idx_rf[-1]] = np.finfo(np.float32).eps  # edges down to zero
    return y


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
