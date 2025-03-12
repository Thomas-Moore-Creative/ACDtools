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
from cartopy import feature as cfeature
from cartopy.feature import NaturalEarthFeature
from cartopy.mpl.ticker import LongitudeFormatter, LatitudeFormatter
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import cmocean
import cmocean.cm as cmo
import seaborn as sns
# holoviews
# import holoviews as hv
# import geoviews as gv
# from holoviews import opts

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
    return ax, fig

def add_points_and_labels(ax, latitudes, longitudes, labels):
    """
    Adds points and labels to an existing Cartopy map.
    Args:
        ax: Matplotlib axes object with a Cartopy map.
        latitudes: List of latitude values.
        longitudes: List of longitude values.
        locations: List of location names corresponding to the lat/lon values.

    Example:
        add_points_and_labels(ax, latitudes, longitudes, labels)
        # Show the plot
        plt.show()   
    """
    for lat, lon, loc in zip(latitudes, longitudes, labels):
        ax.scatter(lon, lat, color='red', s=50, transform=ccrs.PlateCarree(), label=loc)
        if loc == 'American Samoa':
            lat += -1.5
            lon += -1.0
        if loc == 'Samoa':
            lat += -2.0
            lon += -5.0
        if loc == 'Wallis and Futuna':
            lat += 1.0
            lon += -1.0

        ax.text(lon + 1, lat, loc, fontsize=10, color='black', transform=ccrs.PlateCarree())

def add_outside_text(fig, text, position='bottom-right', fontsize=10, color='gray', style='italic', weight=None):
    """
    Adds a line of text outside the bounding box of a plot.
    
    Args:
        fig: The Matplotlib figure object.
        text: The text to add (string).
        position: Where to place the text ('bottom', 'top', 'top-right', 'bottom-right', or custom tuple for (x, y)).
        fontsize: Font size of the text.
        color: Color of the text.
        style: Font style of the text (e.g., 'italic', 'normal').
        weight: Font weight of the text (e.g., 'bold', 'normal').
    """
    # Define default positions for 'top', 'bottom', 'top-right', and 'bottom-right'
    positions = {
        'bottom': (0.5, 0.03),       # Just above the bottom of the plot
        'top': (0.5, 0.92),          # Just below the top of the plot
        'top-right': (0.98, 0.92),   # Near the top-right corner of the plot
        'bottom-right': (0.98, 0.03) # Near the bottom-right corner of the plot
    }
    
    # Use predefined positions or custom coordinates
    x, y = positions.get(position, position if isinstance(position, tuple) else (0.5, 0.02))
    
    # Add text to the figure
    fig.text(
        x, y, 
        text, 
        ha='right' if 'right' in position else 'center',  # Align right for 'top-right' and 'bottom-right'
        fontsize=fontsize, 
        color=color, 
        style=style, 
        weight=weight
    )

def add_inside_text(ax, text, position='bottom', fontsize=10, color='gray', style='italic', weight=None):
    """
    Adds a line of text just inside the bounding box of a plot, with improved alignment and positioning.
    
    Args:
        ax: The Matplotlib axes object.
        text: The text to add (string).
        position: Where to place the text ('bottom', 'top', 'top-right', 'bottom-right', 'bottom-left', or custom tuple for (x, y)).
        fontsize: Font size of the text.
        color: Color of the text.
        style: Font style of the text (e.g., 'italic', 'normal').
        weight: Font weight of the text (e.g., 'bold', 'normal').
    """
    # Get the bounding box of the plot within the figure
    bbox = ax.get_position()
    
    # Define positions relative to the plot's bounding box
    # Adjusted offsets for closer placement to bounds
    positions = {
        'bottom': (bbox.x0 + (bbox.x1 - bbox.x0) / 2, bbox.y0 + 0.005),  # Bottom center
        'top': (bbox.x0 + (bbox.x1 - bbox.x0) / 2, bbox.y1 - 0.005),    # Top center
        'top-right': (bbox.x1 - 0.02, bbox.y1 - 0.015),                 # Slightly lower top-right corner
        'bottom-right': (bbox.x1 - 0.02, bbox.y0 + 0.005),             # Bottom-right corner
        'bottom-left': (bbox.x0 + 0.02, bbox.y0 + 0.005)               # Slightly inward and aligned left
    }
    
    # Determine alignment based on position
    alignment = {
        'top-right': 'right',
        'bottom-right': 'right',
        'bottom-left': 'left',
        'top': 'center',
        'bottom': 'center'
    }
    
    # Use predefined positions or custom coordinates
    x, y = positions.get(position, position if isinstance(position, tuple) else (0.5, bbox.y0 + 0.005))
    
    # Add text to the figure
    ax.figure.text(
        x, y, 
        text, 
        ha=alignment.get(position, 'center'),  # Adjust alignment based on position
        fontsize=fontsize, 
        color=color, 
        style=style, 
        weight=weight
    )

def add_diagonal_text(
    ax, 
    text, 
    fontsize=20, 
    color="white", 
    rotation=45, 
    alpha=0.5, 
    box_color="black", 
    spacing=0, 
    position="center"
):
    """
    Adds a semi-transparent block of text diagonally across a Matplotlib plot with flexible positioning.
    
    Args:
        ax: The Matplotlib axes object to add the text to.
        text: The text to display (string).
        fontsize: Font size of the text (default: 20).
        color: Color of the text (default: "white").
        rotation: Angle to rotate the text (default: 45).
        alpha: Transparency level of the text and background (0 to 1, default: 0.5).
        box_color: Background color of the text box (default: "black").
        spacing: Number of spaces to add between characters (default: 0).
        position: Text position ('center', 'top-center', 'bottom-center', 
                  'top-left', 'top-right', 'bottom-left', 'bottom-right').
    """
    # Add spacing between characters
    spaced_text = (" " * spacing).join(text)

    # Define position mappings in axes-relative coordinates
    position_coords = {
        "center": (0.5, 0.5),
        "top-center": (0.5, 0.9),
        "bottom-center": (0.5, 0.1),
        "top-left": (0.1, 0.9),
        "top-right": (0.9, 0.9),
        "bottom-left": (0.1, 0.1),
        "bottom-right": (0.9, 0.1),
    }

    # Get coordinates for the selected position
    x, y = position_coords.get(position, (0.5, 0.5))  # Default to 'center' if position is invalid

    # Add text to the plot
    ax.text(
        x, y,                          # Position based on the selected alignment
        spaced_text,                   # Text with spacing
        fontsize=fontsize,             # Font size
        color=color,                   # Text color
        rotation=rotation,             # Rotate text
        ha="center",                   # Horizontal alignment
        va="center",                   # Vertical alignment
        alpha=alpha,                   # Transparency for text
        bbox=dict(
            facecolor=box_color,       # Background color
            alpha=alpha,               # Transparency for background
            edgecolor="none",          # No border
            boxstyle="round,pad=0.5"   # Rounded rectangle with padding
        ),
        transform=ax.transAxes         # Use axes-relative coordinates
    )

def add_contours(
    ax, 
    data, 
    lat_name="lat", 
    lon_name="lon", 
    levels=None, 
    colors=None, 
    linewidths=0.8, 
    linestyles="solid", 
    labels=False, 
    transform=ccrs.PlateCarree()
):
    """
    Adds line contours from a single data array to an existing Cartopy plot with customizable colors.
    
    Args:
        ax: The Cartopy Axes object to plot on.
        data: 2D data array with associated latitude and longitude coordinates.
        lat_name: Name of the latitude coordinate in the data array (default: "lat").
        lon_name: Name of the longitude coordinate in the data array (default: "lon").
        levels: Contour levels (default: None, automatic levels).
        colors: List of colors for contour lines (default: None, uses Matplotlib defaults).
        linewidths: Line width of contour lines (default: 0.8).
        linestyles: Line style for contour lines (default: "solid").
        labels: Whether to label the contours (default: False).
        transform: Coordinate reference system of the data (default: PlateCarree).
    """
    # Extract latitude and longitude from the data array
    lats = data[lat_name]
    lons = data[lon_name]
    
    # Create the meshgrid
    lon2d, lat2d = np.meshgrid(lons, lats)
    
    # Add contour lines with custom colors
    lines = ax.contour(
        lon2d, lat2d, data, 
        levels=levels, 
        colors=colors,        # Custom colors
        linewidths=linewidths, 
        linestyles=linestyles, 
        transform=transform
    )
    
    # Add contour labels if requested
    if labels:
        ax.clabel(lines, inline=True, fontsize=8, fmt="%.1f")

def tropical_pacific_hv(
    data, 
    lon_name='longitude', 
    lat_name='latitude',
    central_longitude=180,
    extent=[130, 290, -60, 30],
    title='Tropical Pacific',
    cmap='Viridis',
    colorbar=True,
    **kwargs
):
    """
    Create a tropical Pacific plot using HoloViews and GeoViews.

    Parameters:
    - data: xarray.DataArray
        2D data to plot (must include longitude and latitude).
    - lon_name: str
        Name of the longitude coordinate in the data.
    - lat_name: str
        Name of the latitude coordinate in the data.
    - central_longitude: float
        Central longitude for the map projection.
    - extent: list of floats
        Plot extent in the format [lon_min, lon_max, lat_min, lat_max].
    - title: str
        Title of the plot.
    - cmap: str
        Colormap to use for the plot.
    - colorbar: bool
        Whether to include a colorbar.
    - **kwargs:
        Additional keyword arguments passed to gv.Image.

    Returns:
    - plot: HoloViews/GeoViews object
        Interactive plot.
    """
    # Set up the PlateCarree projection for visualization
    projection = ccrs.PlateCarree(central_longitude=central_longitude)
    
    # Define the CRS of the data (assuming 0-360 longitude range)
    data_crs = ccrs.PlateCarree(central_longitude=0)
    
    # Create the GeoViews Feature for land
    land_feature = NaturalEarthFeature(
        category='physical',
        name='land',
        scale='50m',
        edgecolor='black',
        facecolor='lightgray'
    )
    land = gv.Feature(land_feature, crs=projection)
    
    # Ensure data is an xarray.DataArray
    if not isinstance(data, xr.DataArray):
        raise ValueError("Input data must be an xarray.DataArray")
    
    # Create a GeoViews Image for the data
    gv_image = gv.Image(data, kdims=[lon_name, lat_name], vdims=data.name, crs=data_crs).opts(
        cmap=cmap,
        colorbar=colorbar,
        projection=projection,
        tools=['hover'],
        frame_width=600,
        **kwargs
    )
    
    # Combine the data plot with the land feature
    plot = (gv_image * land).opts(
        opts.Overlay(
            title=title,
            xlim=(extent[0], extent[1]),
            ylim=(extent[2], extent[3]),
            xlabel='Longitude',
            ylabel='Latitude',
        )
    )
    
    return plot

def heatmap(heatmap_df, figsize=(20, 8), cmap='RdBu_r', vmin=-2, vmax=2, title='my plot title', annot_data=None, **kwargs):
    """
    Plot a heatmap with optional annotations.

    Parameters:
    - heatmap_df (pandas.DataFrame): The input dataframe for the heatmap.
    - figsize (tuple, optional): The size of the figure (width, height). Default is (20, 8).
    - cmap (str, optional): The colormap to use for the heatmap. Default is 'RdBu_r'.
    - vmin (float, optional): The minimum value for the color scale. Default is -2.
    - vmax (float, optional): The maximum value for the color scale. Default is 2.
    - title (str, optional): The title of the plot. Default is 'my plot title'.
    - annot_data (pandas.DataFrame, optional): The dataframe containing the annotations to be displayed on the heatmap.
                                               If None, no annotations will be shown. Default is None.

    Returns:
    None
    """
    # Plotting the heatmap with annotations
    plt.figure(figsize=figsize)
    # First layer: heatmap without annotations
    sns.heatmap(heatmap_df, annot=False, cmap=cmap, square=True, vmin=vmin, vmax=vmax, linewidth=.5)
    if annot_data is not None:
        # Second layer: add annotations on top (with vertical alignment at center)
        sns.heatmap(heatmap_df, annot=annot_data, annot_kws={'va': 'center'}, fmt="", cbar=False, cmap=cmap, square=True,
                    vmin=vmin, vmax=vmax, linewidth=.5)
    plt.title(title)
    plt.show()