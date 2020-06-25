import numpy as np
import matplotlib as mpl
import scipy.ndimage as ndi

defaults_mpl = {
    "axes.linewidth": 2,
    "font.size": 20,
}
for k, v in defaults_mpl.items():
    # update mpl's defaults
    mpl.rcParams[k] = v

rcParams = {
    "arrow_width": 0.15,  # data coords
    "arrow_length": 0.20,  # data coords
    "axes_ticks": False,
}

# need to set up default global style


def _project_channel_on_time_axis(channels):
    """ Build a mpl.path.Path object which shows axis where all channels are empty
    Parameters
    ----------
    channels : iterable of numpy arrays of shape (n, ) or (n, m)
    """
    tmp_stack = np.concatenate(np.broadcast_arrays(*channels), axis=1)
    all_nan = np.isnan(tmp_stack).all(axis=1)
    all_nan_dil = ndi.binary_dilation(all_nan, np.ones(3,))
    axis = np.where(all_nan_dil, 0, np.nan)
    return axis
