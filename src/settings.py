""" Module that stores current settings used in TSTools plugin
"""
import datetime as dt
import os

import numpy as np


# General settings
location = os.getcwd()
map_tool = True

# List of raster images added - used to track for symbology
image_layers = []

# Series index for symbology and images table
series_index_symbology = 0
series_index_table = 0

# Series to plot options "band" QComboBox
plot_series = []
plot_band_indices = []
plot_bands = []

# Dictionary to store plot settings
plot = {
    # Should we plot when we click canvas?
    'plot_layer': True,
    # Axis selector for controls
    'axis_select': 0,
    # Which band to plot on which axes
    'y_axis_1_band': np.zeros(1, dtype=np.bool),
    'y_axis_2_band': np.zeros(1, dtype=np.bool),
    # Plot scaling options
    'y_axis_scale_auto': [True, True],
    'x_scale_fix': False,
    'x_scale_range': None,
    'scale_factor': 0.25,
    # Plot min, max
    'y_min': [0, 0],
    'y_max': [10000, 10000],
    'x_min': dt.date.today().year,
    'x_max': dt.date.today().year + 1,
    # Show mask, model fit, time series breaks
    'mask': True,
    'fit': True,
    'break': True,
    # Mask values
    'mask_val': None,
    # Tolerance for clicking data points
    'picker_tol': 2
}

# Dictionary to store plot symbology options
plot_symbol = {
    'enabled': False,
    'indices': None,
    'markers': None,
    'colors': None
}

save_plot = {

    'fname': 'time_series_plot',
    'format': 'png',
    'transparent': False,
    'facecolor': 'w',
    'edgecolor': 'w'

}

# Enable/disable symbology control for all Series
symbol_control = True
# Dictionary to store raster symbology settings
symbol = []
# Defaults for `symbol`
default_symbol = {
    # RGB color options
    'band_red': 4,
    'band_green': 3,
    'band_blue': 2,
    # Min/max values for all bands
    'min': np.zeros(1, dtype=np.int),
    'max': np.ones(1, dtype=np.int) * 10000,
    # Contrast enhancement
    #   NoEnhancement                           0
    #   StretchToMinimumMaximum                 1
    #   StretchAndClipToMinimumMaximum          2
    #   ClipToMinimumMaximum                    3
    'contrast': 1,
}

canvas = {
    # Show outline of clicked pixel
    'show_click': True,
    # QgsVectorLayer ID for polygon outline of clicked pixel
    'click_layer_id': None
}
