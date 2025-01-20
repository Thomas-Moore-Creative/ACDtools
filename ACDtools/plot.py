"""
plot.py

This module contains a collection of functions for ploting and making figures.
Author = {"name": "Thomas Moore", "affiliation": "CSIRO", "email": "thomas.moore@csiro.au", "orcid": "0000-0003-3930-1946"}
"""
# Standard library imports
import os
import datetime


# Third-party imports
import numpy as np
import xarray as xr
import cartopy
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from cartopy.mpl.ticker import LongitudeFormatter, LatitudeFormatter
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import cmocean
import cmocean.cm as cmo

# Local application imports (if needed)
#from .my_local_module import my_function

def tropical_pacific(central_longitude=180,figsize=(16,16),extent=[130, 290, -60, 30],
                    xticks=[150, 180, 210,240,270],yticks=[-60,-30, -10, 0, 10],
                    xstride=10,ystride=10,my_plot_title='my_plot_title',optional_plot_data=None,
                    cbar_kwargs = {'orientation':'horizontal', 'shrink':0.6, "pad" : .05, 'aspect':40},
                    **kwargs):
    """
    plot_PlateCarree()
    - Make a geographic plot with the PlateCarree projection.
    - This function is tailored for "pacific centred" plots but could be used more generally.

    :param central_longitude: central_longitude value - default is 180
    :type central_longitude: int or float
    :param figsize: "figsize" kwarg for `plt.subplots`
    :type figsize: tuple of ints or floats
    :param extent: geographical extent of plot boundaries
    :type extent: list of 4 ints or floats as [x1,x2,y1,y2]
    :param xticks: list of x tick labels to draw
    :type xticks: list of ints or floats or empty list
    :param yticks: list of y tick labels to draw
    :type yticks: list of ints or floats or empty list
    :param xstride: stride of longitude grid in degrees - default is 10
    :type xstride: int
    :param ystride: stride of longitude grid in degrees - default is 10
    :type ystride: int
    :param optional_plot_data: xarray object to plot in 2D
    :type optional_plot_data: 2D xarray object
    :return: plot
    :rtype: plot
    :raises TypeError: TBD

    :typical use: plot_PlateCarree(optional_plot_data=plot_data,x='longitude',y='latitude',levels=100,cmap = cmocean.cm.thermal,robust=True,vmin=0, vmax=31)
    """
    long_list = np.arange(-180, 180, xstride)
    lat_list = np.arange(-90, 90, ystride)
                        
    proj = ccrs.PlateCarree(central_longitude=central_longitude)

    fig, ax = plt.subplots(subplot_kw=dict(projection=proj), figsize=figsize)
    #fig.canvas.draw()
    
    resolution='50m'
    land = cartopy.feature.NaturalEarthFeature('physical', 'land', \
        scale=resolution, edgecolor='k', facecolor=cfeature.COLORS['land'])
    ax.add_feature(land)


    gl = ax.gridlines(crs=proj, draw_labels=False, alpha=0.3, linewidth=0.5)
    gl.xlocator = mticker.FixedLocator(long_list)
    gl.ylocator = mticker.FixedLocator(lat_list)

    ax.set_xticks(xticks, crs=ccrs.PlateCarree())
    ax.set_yticks(yticks, crs=ccrs.PlateCarree())
    lon_formatter = LongitudeFormatter(zero_direction_label=True)
    lat_formatter = LatitudeFormatter()
    ax.xaxis.set_major_formatter(lon_formatter)
    ax.yaxis.set_major_formatter(lat_formatter)
    if optional_plot_data is not None:
        ##### plotting filled contours#####
        optional_plot_data.plot.contourf(ax=ax, transform=ccrs.PlateCarree(), cbar_kwargs=cbar_kwargs, **kwargs)
    ax.set_extent(extent, crs=ccrs.PlateCarree())
    plt.title(my_plot_title)
    fig.tight_layout()
    plt.show()
    return ax
    