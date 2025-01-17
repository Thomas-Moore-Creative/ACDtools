"""
ocean.py

This module contains a collection of functions for calculating oceanographic metrics.
Author = {"name": "Thomas Moore", "affiliation": "CSIRO", "email": "thomas.moore@csiro.au", "orcid": "0000-0003-3930-1946"}
"""
# Standard library imports
import os
import datetime


# Third-party imports
import numpy as np
import xarray as xr

# Local application imports (if needed)
#from .my_local_module import my_function

def threshold_depth(da,chosen_threshold=90,depth_name='pres'):
    """
    Given a gridded oceanographic data array (da) with some x,y, and z dimensions and a threshold value (threshold)
    will calculate both the depth of the first threshold crossing as well as the total number of crossings in each water column.

    Parameters
    ----------
    da : DataArray
        An xarray gridded oceanographic data array with some x,y, and z dimensions.
    chosen_threshold : float
        Chosen threshold value. Default is 90.0
    depth_name : str
        Name of the depth dimension in the da.  Default is 'pres'.
        

    Returns
    -------
    list of data arrays [first_depth_below_threshold, count_drops_below_threshold]
        first_depth_below_threshold is the shallowest depth in the water column where the threshold is reached.
        count_drops_below_threshold is how many times in the water column values drop below the threshold.
    
    Examples:
        >>> [first_depth_below_threshold, count_drops_below_threshold] = threshold_depth(my_da,chosen_threshold=20,depth_name='depth')
    """
    threshold = chosen_threshold
    # Create a mask for where oxygen falls below the threshold
    mask = da <= threshold
    # find grid point depth of first threshold value
    depths_where_below_threshold = da[depth_name].where(mask)
    first_depth_below_threshold = depths_where_below_threshold.min(dim=depth_name)
    first_depth_below_threshold = first_depth_below_threshold.where(mask.any(dim=depth_name), np.nan)
    # count crossings
    drops_below_threshold = mask.astype(int).diff(dim=depth_name) == 1
    count_drops_below_threshold = drops_below_threshold.sum(dim=depth_name)
    return first_depth_below_threshold,count_drops_below_threshold

def layer_statistics(da,var_name,layer_depth = 300,depth_name = 'pres'):
    """
    Given a gridded oceanographic data array (da) with some x,y, and z dimensions and a depth value (layer_depth)
    will calculate statistics and integrated values from the surface to the chosen depth level

    Parameters
    ----------
    da : DataArray
        A gridded oceanographic data array xarray object with some x,y, and z dimensions.
    layer_depth : float
        Chosen value for depth of the layer. Default is 300.
    depth_name : str
        Name of the depth dimension in the da.  Default is 'pres'.
    var_name :  str
        Name of the variable
        
    Returns
    -------
    layer_stats_ds - dataset with statistics and integrated values across the layer
    
    Examples:
        >>> layer_stats_ds = layer_statistics(da,var_name='oxy',layer_depth = 300,depth_name = 'pres')
    """
    layer = da.where(da[depth_name]<=layer_depth,drop=True)
    # stats
    layer_stats = [layer.mean(depth_name).rename(var_name+'_mean'),layer.min('pres').rename(var_name+'_min'),layer.max('pres').rename(var_name+'_max')]
    # Create Dataset dynamically
    layer_stats_ds = xr.Dataset()
    for da in layer_stats:
        layer_stats_ds[da.name] = da  # Use the DataArray's name as the variable name
    # integral
    dz = layer[depth_name].diff(depth_name)
    layer_sum_integral = (layer*dz).sum(dim=depth_name)
    layer_sum_integral = layer_sum_integral.where(layer_sum_integral != 0)
    layer_trapezoidal_integral = layer.integrate(depth_name)
    layer_stats_ds[var_name+'_layer_sum_integral'] = layer_sum_integral
    layer_stats_ds[var_name+'_layer_trapezoidal_integral'] = layer_trapezoidal_integral
    return layer_stats_ds

def interpolate_oxygen_target_depth(da, target=90.0, depth_coord='pres'):
    """
    Interpolates the depth at which a specified target oxygen value occurs 
    along a given depth coordinate in an xarray DataArray.

    This function identifies the shallowest crossing of the target value
    and performs linear interpolation to determine the precise depth where 
    the target value is reached. If the values bounding the target are 
    identical, an error is raised to prevent division by zero.

    Parameters
    ----------
    da : xarray.DataArray
        The input DataArray containing oxygen concentration values, indexed 
        by the depth coordinate.
    target : float, optional
        The target oxygen concentration value for which to find the depth.
        Default is 90.0.
    depth_coord : str, optional
        The name of the depth coordinate in the DataArray. Default is 'pres'.

    Returns
    -------
    float
        The interpolated depth at which the target oxygen value occurs.

    Raises
    ------
    ValueError
        If the values bounding the target oxygen value (value_A and value_B) 
        are identical, which would result in a division by zero.

    Examples
    --------
    >>> import xarray as xr
    >>> import numpy as np
    >>> depth = np.linspace(0, 1000, 11)
    >>> oxygen = np.array([200, 180, 150, 120, 100, 90, 80, 70, 60, 50, 40])
    >>> da = xr.DataArray(oxygen, coords={"pres": depth}, dims=["pres"])
    >>> interpolate_oxygen_target_depth(da, target=90)
    500.0

    Notes
    -----
    - The function assumes that the depth coordinate is monotonic and increasing.
    - If there are multiple crossings of the target value, the function returns
      the shallowest crossing.
    """
    mask = da <= target
    just_below_target = mask * ~(mask.shift({depth_coord: 1}, fill_value=False))
    just_above_target = ~mask * (mask.shift({depth_coord: -1}, fill_value=False))
    # depths for shallowest target value crossing
    depth_A = just_above_target[depth_coord].where(just_above_target).min(depth_coord)
    depth_B = just_below_target[depth_coord].where(just_below_target).min(depth_coord)
    # Get the values corresponding to the bounds for shallowest target value crossing
    value_A = da.where(just_above_target).min(depth_coord)
    value_B = da.where(just_below_target).min(depth_coord)
    # test that values are not the same anywhere
    equal_mask = value_A == value_B
    if equal_mask.any():
        raise ValueError("Cannot interpolate with identical values (value_A == value_B).")
    # Linear interpolation formula
    interpolated_depth = depth_A + ((target - value_A) / (value_B - value_A)) * (depth_B - depth_A)
    return interpolated_depth

