# -*- coding: utf-8 -*-
"""
Radar Widget Classes.

Contains GUI panel classes for radar tracker dashboard

Author: Jason Merlo
Maintainer: Jason Merlo (merlojas@msu.edu)
"""
# === Window / UI ===
import pyqtgraph as pg                  # Graph Elements
from pyqtgraph import QtCore, QtGui     # Qt Elements
from custom_ui import QHLine             # Horizontal dividers
# === GUI Panels ===
from pyratk.widgets import fft_widget, iq_widget

class GraphPanel(pg.LayoutWidget):
    def __init__(self, radar_array):
        pg.LayoutWidget.__init__(self)

        # Copy member objects
        self.radar_array = radar_array

        # Instantiate IQWidget objects and widgets add to GraphPanel
        self.iq_widget_array = []  # [row, col]

        for i, row in enumerate(self.radar_array):
            iqw_row = []

            for j, radar in enumerate(row):
                w = iq_widget.IQWidget(radar)
                iqw_row.append(w)
                self.addWidget(iqw_row[-1])

            self.iq_widget_array.append(iqw_row)
            self.nextRow()

        # Instantiate FFTWidget objects and widgets add to GraphPanel
        self.fft_widget_array = []  # [row, col]

        for i, row in enumerate(self.radar_array):
            fftw_row = []

            for j, radar in enumerate(row):
                w = fft_widget.FftWidget(radar, vmax_len=100,
                                         show_max_plot=False)
                fftw_row.append(w)
                self.addWidget(fftw_row[-1])

            self.fft_widget_array.append(fftw_row)
            self.nextRow()

        # Link scaling of plots
        flat_list = [x for sublist in self.iq_widget_array for x in sublist]
        for idx, graph in enumerate(flat_list):
            if idx > 0:
                graph.iq_plot.setXLink(flat_list[idx-1].iq_plot)
                graph.iq_plot.setYLink(flat_list[idx-1].iq_plot)
        flat_list = [x for sublist in self.fft_widget_array for x in sublist]
        for idx, graph in enumerate(flat_list):
            if idx > 0:
                graph.fft_plot.setXLink(flat_list[idx-1].fft_plot)
                graph.fft_plot.setYLink(flat_list[idx-1].fft_plot)

        # Remove extra margins around plot widgets
        self.layout.setContentsMargins(0, 0, 0, 0)

    def update(self):
        for row in self.iq_widget_array:
            for rw in row:
                rw.update()
        for row in self.fft_widget_array:
            for rw in row:
                rw.update()

    def reset(self):
        for row in self.iq_widget_array:
            for rw in row:
                rw.reset()
        for row in self.fft_widget_array:
            for rw in row:
                rw.reset()


class ControlPanel(pg.LayoutWidget):
    """Handle dataset controls, and label controls."""

    def __init__(self, app, data_mgr, graph_panels):
        pg.LayoutWidget.__init__(self)

        #======================================================================
        # todo TEMPORARY
        self.app = app
        #======================================================================

        self.bold_font = QtGui.QFont("Helvetica", weight=QtGui.QFont.Bold)
        self.bold_font = QtGui.QFont()
        self.bold_font.setBold(True)

        # Copy member objects
        self.app = app
        self.data_mgr = data_mgr
        self.graph_panels = graph_panels

        # Add buttons to screen
        self.add_source_buttons()
        self.nextRow()
        self.layout.addItem(QtGui.QSpacerItem(
            10, 15))
        self.nextRow()

        self.add_control_buttons()
        self.nextRow()
        self.layout.addItem(QtGui.QSpacerItem(
            10, 15))
        self.nextRow()

        self.add_database_buttons()
        self.nextRow()
        self.layout.addItem(QtGui.QSpacerItem(
            10, 15))

        self.nextRow()
        self.add_dataset_buttons()
        self.nextRow()
        self.add_dataset_list()

        # Remove extra margins around button widgets
        self.layout.setContentsMargins(0, 0, 0, 0)

    def add_source_buttons(self):
        # Add label
        self.source_label = QtGui.QLabel('Data Source')
        self.source_label.setFont(self.bold_font)

        # Add Radio buttons
        self.rad_daq = QtGui.QRadioButton("DAQ (Real-time)")
        self.rad_daq.setChecked(True)
        self.rad_dataset = QtGui.QRadioButton("Dataset (Recorded)")
        self.rad_dataset.setEnabled(False)

        self.rad_daq.toggled.connect(self.rad_daq_handler)
        self.rad_dataset.toggled.connect(self.rad_dataset_handler)

        # Add dataset attributes
        self.sample_rate_label = QtGui.QLabel("Sample Rate: ")
        self.sample_chunk_size_label = QtGui.QLabel("Sample Size: ")
        self.daq_type_label = QtGui.QLabel("DAQ Type: ")

        # Add widgets to layout
        self.addWidget(self.source_label)
        self.nextRow()
        self.addWidget(QHLine())
        self.nextRow()
        self.addWidget(self.rad_daq)
        self.nextRow()
        self.addWidget(self.rad_dataset)
        self.nextRow()
        self.layout.addItem(QtGui.QSpacerItem(
            10, 15))
        self.nextRow()
        self.addWidget(self.sample_rate_label)
        self.nextRow()
        self.addWidget(self.sample_chunk_size_label)
        self.nextRow()
        self.addWidget(self.daq_type_label)

        self.update_control_attr_labels()

        # Align widgets to top instead of center
        # self.layout.setAlignment(self.pause_button, QtCore.Qt.AlignTop)
        # self.layout.setAlignment(self.reset_button, QtCore.Qt.AlignTop)

    def add_control_buttons(self):
        # Add label
        self.control_label = QtGui.QLabel('Data Controls')
        self.control_label.setFont(self.bold_font)

        # Add buttons
        self.pause_button = QtGui.QPushButton('Play/Pause')
        self.pause_button.clicked.connect(self.pause_button_handler)
        self.step_right_button = QtGui.QPushButton('>>')
        self.step_right_button.clicked.connect(self.step_right_button_handler)
        self.step_left_button = QtGui.QPushButton('<<')
        self.step_left_button.clicked.connect(self.step_left_button_handler)
        self.reset_button = QtGui.QPushButton('Reset/Clear Dataset')
        self.reset_button.clicked.connect(self.data_mgr.reset)
        self.save_button = QtGui.QPushButton('Save Dataset As...')
        self.save_button.clicked.connect(self.save_dataset_button_handler)

        # Add state indicator
        self.state_label = QtGui.QLabel("State: ")

        # Add widgets to layout
        self.addWidget(self.control_label)
        self.nextRow()
        self.addWidget(QHLine())
        self.nextRow()
        self.addWidget(self.state_label)
        self.nextRow()
        self.addWidget(self.pause_button)
        self.nextRow()
        self.addWidget(self.reset_button)
        self.nextRow()
        self.addWidget(self.save_button)

        # Align widgets to top instead of center
        self.layout.setAlignment(self.pause_button, QtCore.Qt.AlignTop)
        self.layout.setAlignment(self.reset_button, QtCore.Qt.AlignTop)

    def add_database_buttons(self):
        # Add label
        self.database_label = QtGui.QLabel('Database Control')
        self.database_label.setFont(self.bold_font)

        self.load_database_button = QtGui.QPushButton(
            'Load/Create Database...')
        self.load_database_button.clicked.connect(
            self.load_database_button_handler)

        # Add widgets to layout
        self.addWidget(self.database_label)
        self.nextRow()
        self.addWidget(QHLine())
        self.nextRow()

        self.addWidget(self.load_database_button)

    def add_dataset_buttons(self):
        # Add label
        self.dataset_label = QtGui.QLabel('Dataset Control')
        self.dataset_label.setFont(self.bold_font)

        # Add buttons
        self.load_dataset_button = QtGui.QPushButton('Load Selected Dataset')
        self.load_dataset_button.clicked.connect(
            self.load_dataset_button_handler)

        self.edit_dataset_button = QtGui.QPushButton(
            'Edit Selected Dataset')
        self.edit_dataset_button.clicked.connect(
            self.edit_dataset_button_handler)

        self.delete_dataset_button = QtGui.QPushButton(
            'Delete Selected Dataset')
        self.delete_dataset_button.clicked.connect(
            self.delete_dataset_button_handler)

        # =====================================================================
        # =====================================================================

        # Add widgets to layout
        self.addWidget(self.dataset_label)
        self.nextRow()
        self.addWidget(QHLine())
        self.nextRow()

        self.addWidget(self.load_dataset_button)
        self.nextRow()
        self.addWidget(self.edit_dataset_button)
        self.nextRow()
        self.addWidget(self.delete_dataset_button)

        # =====================================================================
        # =====================================================================

    def add_dataset_list(self):
        self.dataset_list = QtGui.QListWidget()

        # Load datasets
        self.update_dataset_list()

        # Add widget to main window
        self.addWidget(self.dataset_list)

# =============================================================================
# === HELPER FUNCTIONS ========================================================
# =============================================================================

    def update_dataset_list(self):
        self.dataset_list.clear()
        for ds_key in self.data_mgr.get_datasets():
            name = ds_key.name.split('/')[-1]
            item = QtGui.QListWidgetItem(name, self.dataset_list)
            item.setData(1, ds_key)

    def menu_pause_set(self):
        '''
        Pauses daq while menus are open for performance.

        Saves state of pause so it may be restored when menu is closed.
        '''
        self.pause_lock_state = self.data_mgr.paused
        self.data_mgr.paused = True

    def menu_pause_restore(self):
        '''
        Pauses daq while menus are open for performance.

        Restores state when menu is closed.
        '''
        self.data_mgr.paused = self.pause_lock_state

    def update_control_attr_labels(self):
        rate_text = "Sample Rate:\t{:} Hz".format(self.data_mgr.sample_rate)
        self.sample_rate_label.setText(rate_text)
        size_text = "Sample Size:\t{:}".format(self.data_mgr.sample_chunk_size)
        self.sample_chunk_size_label.setText(size_text)
        daq_text = "DAQ Type:\t{:}".format(self.data_mgr.daq_type)
        self.daq_type_label.setText(daq_text)

    def update_dataset_attr_labels(self):
        pass

    def update_source_buttons(self):
        if self.data_mgr.source == self.data_mgr.virt_daq:
            self.rad_dataset.setChecked(True)
        else:
            self.rad_daq.setChecked(True)

    def reset_panels(self):
        for panel in self.graph_panels:
            panel.reset()

    def input_changed(self):
        '''
        Handles updating graphs and labels on input switch
        '''
        # self.reset_button_handler()
        # self.data_mgr.reset()
        self.update_control_attr_labels()

# =============================================================================
# === HANDLER FUNCTIONS =======================================================
# =============================================================================

    def rad_daq_handler(self):
        self.data_mgr.source = self.data_mgr.daq
        self.input_changed()

    def rad_dataset_handler(self):
        self.data_mgr.source = self.data_mgr.virt_daq
        self.input_changed()

# === DATABASE HANDLER FUNCTIONS ==============================================

    def load_database_button_handler(self):
        self.menu_pause_set()

        filter = "HDF5 files (*.hdf5)"
        file_desc = QtGui.QFileDialog.getOpenFileName(
            self, 'Database File', filter=filter)
        print("DB File: ", file_desc)

        # Parse return type - Mac returns tuple, windows returns string
        if isinstance(file_desc, tuple):
            name = file_desc[0]
        else:
            name = file_desc

        if name is not '':
            print("Loading Database: ", name)
            self.data_mgr.open_database(name)
            self.update_dataset_list()

        self.menu_pause_restore()

    def save_database_as_button_handler(self):
        self.menu_pause_set()

        name = QtGui.QFileDialog.getSaveFileName(self, 'Save File')
        print("save database as...", name)

        self.menu_pause_restore()

# === DATASET CONTROL HANDLER FUNCTIONS =======================================

    def delete_dataset_button_handler(self):
        self.menu_pause_set()
        # Get selected item.  If multiple selected, load first item in list
        selected_items = self.dataset_list.selectedItems()
        if selected_items:
            item = self.dataset_list.indexFromItem(selected_items[0]).data(1)

            title = 'Delete'
            message = "{:} will be permanently deleted.".format(item)
            options = QtGui.QMessageBox.Yes | QtGui.QMessageBox.No
            default = QtGui.QMessageBox.No

            buttonReply = QtGui.QMessageBox.question(
                self, title, message, options, default)

            if buttonReply == QtGui.QMessageBox.Yes:
                self.data_mgr.delete_dataset(item)
                print("delete dataset...", item)
                self.update_dataset_list()

        self.menu_pause_restore()

    def load_dataset_button_handler(self):
        # Get selected item.  If multiple selected, load first item in list
        selected_items = self.dataset_list.selectedItems()
        if selected_items:
            self.data_mgr.paused = True

            ds = self.dataset_list.indexFromItem(selected_items[0]).data(1)
            self.data_mgr.load_dataset(ds)

            # self.data_mgr.get_samples()
            self.update_source_buttons()
            # self.reset_button_handler()

            self.reset_panels()
            self.update_control_attr_labels()
            self.rad_dataset.setEnabled(True)
            self.data_mgr.paused = False

    def edit_dataset_button_handler(self):
        # Get selected item.  If multiple selected, load first item in list
        selected_items = self.dataset_list.selectedItems()
        if selected_items:
            self.menu_pause_set()

            ds = self.dataset_list.indexFromItem(selected_items[0]).data(1)
            name = ds.name.split('/')[-1]
            try:
                labels = ds.attrs['label'].decode("utf-8")
            except Exception:
                labels = None
            try:
                subject = ds.attrs['subject'].decode("utf-8")
            except Exception:
                subject = None
            try:
                notes = ds.attrs['notes'].decode("utf-8")
            except Exception:
                notes = None

            results = SaveDialog.saveDialog(self.data_mgr,
                                            name=name,
                                            labels=labels,
                                            subject=subject,
                                            notes=notes)

            # Check if a label was removed
            # This is necessary to remove hardlinks
            labels_removed = []
            if results[1] != labels:
                pre_labels = []
                post_labels = []

                # Append all labels to lists
                for pre_label in labels.split(','):
                    pre_labels.append(pre_label)
                for post_label in results[1]:
                    post_labels.append(post_label)

                # Find labels removed (if any)
                labels_removed = pre_labels.copy()
                for label in post_labels:
                    try:
                        labels_removed.remove(label.name.split('/')[-1])
                    except ValueError:
                        pass  # do nothing if post_label isn't in pre_label

            # Check if subject was removed
            # This is necessariy to remove hardlinks
            subject_removed = ""
            if results[2] != subject:
                subject_removed = subject

            # Remove hard-links for attributes removed
            if subject_removed or labels_removed:
                print("(DEBUG) labels_removed: ", labels_removed)
                print("(DEBUG) subject_removed: ", subject_removed)
                self.data_mgr.remove_attributes(name,
                                                labels_removed,
                                                subject_removed)

            # If "save" button selected it TRUE
            if results[-1]:
                self.data_mgr.save_buffer(*(results[:-1]),)
                print("DATASET SAVED AS: ", results[0])

            self.update_dataset_list()

            self.menu_pause_restore()

# === DATA ACQUISITION CONTROL HANDLER FUNCTIONS ==============================

    def pause_button_handler(self):
        self.data_mgr.pause_toggle()

    def step_right_button_handler(self):
        if self.data_mgr.source is self.data_mgr.virt_daq:
            self.data_mgr.virt_daq.get_samples(stride=1, loop=False)
            self.app.processEvents()

    def step_left_button_handler(self):
        if self.data_mgr.source is self.data_mgr.virt_daq:
            self.data_mgr.virt_daq.get_samples(stride=-1, loop=False)
            self.app.processEvents()

    def save_dataset_button_handler(self):
        self.menu_pause_set()

        num_ds = len(self.data_mgr.get_datasets())
        default_name = 'sample_{:}'.format(num_ds)
        results = SaveDialog.saveDialog(self.data_mgr, name=default_name)
        if results[-1]:
            self.data_mgr.save_buffer(*(results[:-1]))
            print("DATASET SAVED AS: ", results[0])

        self.update_dataset_list()

        self.menu_pause_restore()

# === Save/Edit Dialog ========================================================


class SaveDialog(QtGui.QDialog):
    def __init__(self, data_mgr, parent=None):
        super(SaveDialog, self).__init__(parent)
        self.data_mgr = data_mgr
        layout = QtGui.QGridLayout(self)

        # Dataset Name
        self.sample_name_label = QtGui.QLabel('Sample Name:')
        self.sample_name_input = QtGui.QLineEdit()
        layout.addWidget(self.sample_name_label, 0, 0)
        layout.addWidget(self.sample_name_input, 0, 1)

        # Dataset label + button
        self.sample_label_label = QtGui.QLabel('Sample Labels:')
        self.sample_label_input = QtGui.QListWidget()
        self.sample_label_input.setSelectionMode(
            QtGui.QAbstractItemView.ExtendedSelection)
        self.update_label_list()
        layout.addWidget(self.sample_label_label, 2, 0)
        layout.addWidget(self.sample_label_input, 2, 1)

        # Add dataset label button
        self.add_dataset_label_buttom = QtGui.QPushButton('+')
        self.add_dataset_label_buttom.clicked.connect(self.add_label)
        layout.addWidget(self.add_dataset_label_buttom, 2, 2)

        # Dataset subject + button
        self.sample_subject_label = QtGui.QLabel('Sample Subject:')
        self.sample_subject_input = QtGui.QComboBox()
        self.update_subject_list()
        layout.addWidget(self.sample_subject_label, 3, 0)
        layout.addWidget(self.sample_subject_input, 3, 1)

        # Add dataset subject button
        self.add_dataset_subject_buttom = QtGui.QPushButton('+')
        self.add_dataset_subject_buttom.clicked.connect(self.add_subject)
        layout.addWidget(self.add_dataset_subject_buttom, 3, 2)

        # Dataset Notes
        self.sample_notes_label = QtGui.QLabel('Sample Notes:')
        self.sample_notes_input = QtGui.QTextEdit()
        layout.addWidget(self.sample_notes_label, 4, 0)
        layout.addWidget(self.sample_notes_input, 4, 1)

        # OK and Cancel buttons
        buttons = QtGui.QDialogButtonBox(
            QtGui.QDialogButtonBox.Ok | QtGui.QDialogButtonBox.Cancel,
            QtCore.Qt.Horizontal, self)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons, 5, 1)

    # -- label helper functions --- #
    def add_label(self):
        label, ok = QtGui.QInputDialog.getText(self, 'Add New Label', 'Label:')
        if ok:
            self.data_mgr.add_label(label)
        self.update_label_list()

    def update_label_list(self):
        self.sample_label_input.clear()
        for label_key in self.data_mgr.get_labels():
            name = label_key.name.split('/')[-1]
            item = QtGui.QListWidgetItem(name, self.sample_label_input)
            item.setData(1, label_key)

    # -- subject helper functions --- #
    def add_subject(self):
        subject, ok = QtGui.QInputDialog.getText(
            self, 'Add New Subject', 'Subject:')
        if ok:
            self.data_mgr.add_subject(subject)
        self.update_subject_list()

    def update_subject_list(self):
        self.sample_subject_input.clear()
        for subject_key in self.data_mgr.get_subjects():
            name = subject_key.name.split('/')[-1]
            self.sample_subject_input.addItem(name, userData=subject_key)

    @staticmethod
    def saveDialog(parent=None, name=None, labels=None, subject=None,
                   notes=None):
        dialog = SaveDialog(parent)

        # set default text/selections (passed arguments)
        dialog.sample_name_input.setText(name)
        try:
            if labels:
                selected_labels = labels.split(',')
                # print('(DEBUG)',selected_labels)
                for label_text in selected_labels:
                    matched_items = dialog.sample_label_input.findItems(
                        label_text, QtCore.Qt.MatchExactly)
                    matched_items[0].setSelected(True)
        except Exception as e:
            print('(SaveDialog)',e)
        try:
            idx = dialog.sample_subject_input.findText(subject)
            dialog.sample_subject_input.setCurrentIndex(idx)
        except Exception as e:
            print(e)
        notes = dialog.sample_notes_input.setPlainText(notes)

        # Collect results
        result = []

        button_result = dialog.exec_() == QtGui.QDialog.Accepted
        subject_idx = dialog.sample_subject_input.currentIndex()

        result.append(dialog.sample_name_input.text())
        result.append([x.data(1)
                       for x in dialog.sample_label_input.selectedItems()])
        result.append(dialog.sample_subject_input.itemData(subject_idx))
        result.append(dialog.sample_notes_input.toPlainText())
        result.append(button_result)
        return (*(result),)
