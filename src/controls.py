# -*- coding: utf-8 -*-
# vim: set expandtab:ts=4
"""
/***************************************************************************
 CCDCToolsDialog
                                 A QGIS plugin
 Plotting & visualization tools for CCDC Landsat time series analysis
                             -------------------
        begin                : 2013-03-15
        copyright            : (C) 2013 by Chris Holden
        email                : ceholden@bu.edu
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *

import numpy as np

import datetime as dt
import fnmatch
from functools import partial
from itertools import izip
import os

from ui_controls import Ui_Controls as Ui_Widget
from SavePlotDialog import SavePlotDialog
import settings as setting

def str2num(s):
    try:
        return int(s)
    except ValueError:
        return float(s)

class ControlPanel(QWidget, Ui_Widget):

    symbology_applied = pyqtSignal()
    plot_options_changed = pyqtSignal()
    refetch_data = pyqtSignal()
    plot_save_request = pyqtSignal()

    def __init__(self, iface):
        # Qt setup
        self.iface = iface
        QWidget.__init__(self)
        self.setupUi(self)

    def init_options(self):
        # Show/don't show clicks
        self.cbox_showclick.setChecked(setting.canvas['show_click']) 

    def init_plot_options(self, ts):
        print 'Plot options init'
        # Click a point, add the layer
        self.cbox_plotlayer.setChecked(setting.plot['plot_layer'])
        # Signal handled by CCDCController

        # Raster band select
        if self.combox_band.count() == 0:
            self.combox_band.addItems(ts.band_names)
        self.combox_band.setCurrentIndex(setting.plot['band'])
        self.combox_band.currentIndexChanged.connect(partial(
            self.set_band_select))

        # Ylim min and max - Auto scale
        self.cbox_scale.setChecked(setting.plot['auto_scale'])
        self.cbox_scale.stateChanged.connect(self.set_auto_scale)
        # Manual scale & auto-scale display
        self.edit_min.setText(str(setting.plot['min'][setting.plot['band']]))
        self.edit_max.setText(str(setting.plot['max'][setting.plot['band']]))
        self.edit_min.editingFinished.connect(self.set_plot_min)
        self.edit_max.editingFinished.connect(self.set_plot_max)
        
        ### Fmask, fit & breaks on/off
        self.cbox_fmask.setChecked(setting.plot['fmask'])
        self.cbox_fmask.stateChanged.connect(self.set_plot_fmask)

        self.cbox_modelfit.setChecked(setting.plot['fit'])
        self.cbox_modelfit.stateChanged.connect(self.set_model_fit)
        
        self.cbox_breakpoint.setChecked(setting.plot['break'])
        self.cbox_breakpoint.stateChanged.connect(self.set_break_point)

        ### Save button options
        self.but_plot_save.clicked.connect(self.init_save_plot_dialog)

    def update_plot_options(self):
        """ Updates some of the plot options - mostly the text fields for
        min/max based on if user changes pixel or band
        """
        # Enable/disable user edit of min/max
        self.edit_min.setEnabled(not setting.plot['auto_scale'])
        self.edit_max.setEnabled(not setting.plot['auto_scale'])
        # Update min/max
        self.edit_min.setText(str(setting.plot['min'][setting.plot['band']]))
        self.edit_max.setText(str(setting.plot['max'][setting.plot['band']]))

    def set_band_select(self, index):
        """ Slot for band plot selection combo-box
        """
        setting.plot['band'] = index
        self.plot_options_changed.emit()

    def set_auto_scale(self, state):
        """ Slot for turning on/off automatic scaling of data
        """
        if state == Qt.Checked:
            setting.plot['auto_scale'] = True
        elif state == Qt.Unchecked:
            setting.plot['auto_scale'] = False
        self.plot_options_changed.emit()

    def set_plot_min(self):
        """ Slot for setting plot Y-axis minimum
        """
        setting.plot['min'][setting.plot['band']] = str2num(
            self.edit_min.text())
        self.plot_options_changed.emit()

    def set_plot_max(self):
        """ Slot for setting plot Y-axis maximum
        """
        setting.plot['max'][setting.plot['band']] = str2num(
            self.edit_max.text())
        self.plot_options_changed.emit()
    
    def set_plot_fmask(self, state):
        """ Slot for enabling/disabling masking of data by Fmask
        """
        if state == Qt.Checked:
            setting.plot['fmask'] = True
        elif state == Qt.Unchecked:
            setting.plot['fmask'] = False
        self.refetch_data.emit()
        self.plot_options_changed.emit()

    def set_model_fit(self, state):
        """ Slot for enabling/disabling model fit on plot
        """
        if state == Qt.Checked:
            setting.plot['fit'] = True
        elif state == Qt.Unchecked:
            setting.plot['fit'] = False
        self.plot_options_changed.emit()

    def set_break_point(self, state):
        """ Slot for showing/hiding model break points on plot
        """
        if state == Qt.Checked:
            setting.plot['break'] = True
        elif state == Qt.Unchecked:
            setting.plot['break'] = False
        self.plot_options_changed.emit()

    def init_save_plot_dialog(self):
        """ Slot for saving Matplotlib plot. Brings up plot save dialog and
        listens for signal to save figure.
        """
        self.save_plot = SavePlotDialog(self)
        self.save_plot.save_plot_requested.connect(self.save_plot_dialog_save)
        self.save_plot.save_plot_closed.connect(self.save_plot_dialog_close)
        self.save_plot.exec_()

    def save_plot_dialog_save(self):
        """ Slot for disconnecting signals to save plot dialog upon either
        canceling or saving the plot
        """
        self.plot_save_request.emit()

    def save_plot_dialog_close(self):
        """ Slot for closing down plot dialog after saving/canceling
        """
        self.save_plot.save_plot_requested.disconnect()
        self.save_plot.save_plot_closed.disconnect()
        self.save_plot.close()


    def init_symbology(self, ts):
        print 'Symbology init...'
        ### UI
        # Control symbology
        self.cbox_symbolcontrol.setChecked(setting.symbol['control'])

        # Band min/max
        setting.symbol['min'] = np.zeros(ts.n_band, dtype=np.int)
        setting.symbol['max'] = np.ones(ts.n_band, dtype=np.int) * 10000
        setting.p_symbol['min'] = np.zeros(ts.n_band, dtype=np.int)
        setting.p_symbol['max'] = np.ones(ts.n_band, dtype=np.int) * 10000

        # Contrast enhancement
        self.combox_cenhance.setCurrentIndex(setting.symbol['contrast'])
        
        # Band selections
        if self.combox_red.count() == 0:
            self.combox_red.addItems(ts.band_names)
        if setting.symbol['band_red'] < len(ts.band_names):
            self.combox_red.setCurrentIndex(setting.symbol['band_red'])
        
        if self.combox_green.count() == 0:
            self.combox_green.addItems(ts.band_names)
        if setting.symbol['band_green'] < len(ts.band_names):
            self.combox_green.setCurrentIndex(setting.symbol['band_green'])
        
        if self.combox_blue.count() == 0:
            self.combox_blue.addItems(ts.band_names)
        if setting.symbol['band_blue'] < len(ts.band_names):
            self.combox_blue.setCurrentIndex(setting.symbol['band_blue'])
        
        # Min / max
        self.edit_redmin.setText(str(
            setting.symbol['min'][setting.symbol['band_red']]))
        self.edit_redmax.setText(str(
            setting.symbol['max'][setting.symbol['band_red']]))
        self.edit_greenmin.setText(str(
            setting.symbol['min'][setting.symbol['band_green']]))
        self.edit_greenmax.setText(str(
            setting.symbol['max'][setting.symbol['band_green']]))
        self.edit_bluemin.setText(str(
            setting.symbol['min'][setting.symbol['band_blue']]))
        self.edit_bluemax.setText(str(
            setting.symbol['max'][setting.symbol['band_blue']]))

        ### Signals
        # Allow control of symbology
        self.cbox_symbolcontrol.stateChanged.connect(self.set_symbol_control)
        # Select image bands for symbology RGB colors
        self.combox_red.currentIndexChanged.connect(partial(
            self.set_symbol_band, 'red'))
        self.combox_green.currentIndexChanged.connect(partial(
            self.set_symbol_band, 'green'))
        self.combox_blue.currentIndexChanged.connect(partial(
            self.set_symbol_band, 'blue'))
        # Manual set of min/max
        self.edit_redmin.editingFinished.connect(partial(
            self.set_symbol_minmax, self.edit_redmin, 'red', 'min'))
        self.edit_redmax.editingFinished.connect(partial(
            self.set_symbol_minmax, self.edit_redmax, 'red', 'max'))
        self.edit_greenmin.editingFinished.connect(partial(
            self.set_symbol_minmax, self.edit_greenmin, 'green', 'min'))
        self.edit_greenmax.editingFinished.connect(partial(
            self.set_symbol_minmax, self.edit_greenmax, 'green', 'max'))
        self.edit_bluemin.editingFinished.connect(partial(
            self.set_symbol_minmax, self.edit_bluemin, 'blue', 'min'))
        self.edit_bluemax.editingFinished.connect(partial(
            self.set_symbol_minmax, self.edit_bluemax, 'blue', 'max'))
        # Contrast enhancement
        self.combox_cenhance.currentIndexChanged.connect(
            self.set_symbol_enhance)
        # Apply settings
        self.but_symbol_apply.clicked.connect(self.apply_symbology)

    def set_symbol_control(self, state):
        """ Turns on or off control of symbology 
        """
        if state == Qt.Checked:
            setting.symbol['control'] = True
            self.but_symbol_apply.setEnabled(True)
        elif state == Qt.Unchecked:
            setting.symbol['control'] = False
            self.but_symbol_apply.setEnabled(False)

    def set_symbol_band(self, color, index):
        """ Assigns image band to symbology color and updates the QLineEdit 
        min/max display to the min/max for the image band chosen for symbology 
        color.
        """
        if color == 'red':
            setting.p_symbol['band_red'] = index
        elif color == 'green':
            setting.p_symbol['band_green'] = index
        elif color == 'blue':
            setting.p_symbol['band_blue'] = index
        
        self.edit_redmin.setText(
            str(setting.p_symbol['min'][setting.p_symbol['band_red']]))
        self.edit_redmax.setText(
            str(setting.p_symbol['max'][setting.p_symbol['band_red']]))
        self.edit_greenmin.setText(
            str(setting.p_symbol['min'][setting.p_symbol['band_green']]))
        self.edit_greenmax.setText(
            str(setting.p_symbol['max'][setting.p_symbol['band_green']]))
        self.edit_bluemin.setText(
            str(setting.p_symbol['min'][setting.p_symbol['band_blue']]))
        self.edit_bluemax.setText(
            str(setting.p_symbol['max'][setting.p_symbol['band_blue']]))

    def set_symbol_minmax(self, field, color, minmax):
        """ Assigns minimum or maximum value for a given color 
        """
        # Determine which image band we're using for symbology color
        if color == 'red':
            band = setting.p_symbol['band_red']
        elif color == 'green':
            band = setting.p_symbol['band_green']
        elif color == 'blue':
            band = setting.p_symbol['band_blue']

        # Grab value from text field
        print field.text()
        try:
            value = str2num(field.text())
            # Set min or max
            setting.p_symbol[minmax][band] = value
        except:
            field.setText(str(setting.p_symbol.get(minmax)[band]))
            
        
    def set_symbol_enhance(self, index):
        """ Assigns color enhancement from combo box of methods 
        """
        setting.p_symbol['contrast'] = index

    def apply_symbology(self):
        """ Fetches current symbology tab values and applies to rasters in time
        series.
        """
        if setting.symbol['control']:
            # Copy over pre-apply attributes to the 'live' symbology dictionary
            setting.symbol = setting.p_symbol.copy()
            if setting.symbol['control']:
                # Emit that we applied settings
                self.symbology_applied.emit()

    def update_table(self, ts):
        print 'Table updates...'
        # Set header labels
        self.image_table.setHorizontalHeaderLabels(
            ['Add/Remove', 'Date', 'ID'])
        
        # Propagate table
        self.image_table.setRowCount(ts.length)
        for row, (date, img) in enumerate(izip(ts.dates, ts.image_ids)):
            cbox = QTableWidgetItem()
            cbox.setFlags(Qt.ItemIsUserCheckable |
                          Qt.ItemIsEnabled)
            cbox.setCheckState(Qt.Unchecked)
            cbox.setTextAlignment(Qt.AlignHCenter)
            self.image_table.setItem(row, 0, cbox)

            _date = QTableWidgetItem(date.strftime('%Y-%j'))
            _date.setFlags(Qt.ItemIsEnabled)
            _date.setTextAlignment(Qt.AlignHCenter)
            _date.setTextAlignment(Qt.AlignVCenter)
            self.image_table.setItem(row, 1, _date)

            _img = QTableWidgetItem(img)
            _img.setFlags(Qt.ItemIsEnabled)
            _img.setTextAlignment(Qt.AlignHCenter)
            _img.setTextAlignment(Qt.AlignVCenter)
            self.image_table.setItem(row, 2, _img)

        cbox = self.image_table.cellWidget(0, 0)

    def disconnect(self):
        # TODO
        pass