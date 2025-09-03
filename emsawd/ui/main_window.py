import sys
from datetime import date, timedelta
import pandas as pd
from PyQt6.QtCore import QDate
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QTabWidget, QStatusBar,
    QGroupBox, QGridLayout, QLabel, QComboBox, QDateEdit, QSpinBox,
    QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, QFileDialog, QCheckBox
)

# Backend imports
from emsawd.core.services import WeatherService
from emsawd.repositories.geocoding_repository import GeocodingRepository
from emsawd.repositories.weather_repository import WeatherRepository
from emsawd.repositories.openweather_repository import OpenWeatherRepository
from emsawd.repositories.weatherapi_repository import WeatherAPIRepository
from emsawd.repositories.accuweather_repository import AccuWeatherRepository
from emsawd.core.export_service import ExportService
from .matplotlib_widget import MatplotlibCanvas
from .settings_dialog import SettingsDialog


class MainWindow(QMainWindow):
    """
    The main window for the Historic Weather Data application.
    """
    def __init__(self, parent=None):
        """
        Initializes the main window.
        """
        super().__init__(parent)

        # Initialize backend services
        self.geocoding_repo = GeocodingRepository()
        self.weather_repos = {}
        self.export_service = ExportService()
        self.settings_dialog = SettingsDialog()
        self._populate_api_combo()
        # Default weather_service will be set after populate

        self.setWindowTitle("Historic Weather Data Analyzer")
        self.setGeometry(100, 100, 1200, 800)  # x, y, width, height

        # Create the central widget and layout
        self.central_widget = QWidget()
        self.main_layout = QVBoxLayout(self.central_widget)
        self.setCentralWidget(self.central_widget)

        # Create the input panel
        self._create_input_panel()
        self.main_layout.addWidget(self.input_group_box)

        # Connect signals to slots
        self.preset_combo.currentTextChanged.connect(self._on_preset_changed)
        self.fetch_button.clicked.connect(self._on_fetch_data_clicked)
        self.export_csv_button.clicked.connect(self._on_export_csv_clicked)
        self.export_excel_button.clicked.connect(self._on_export_excel_clicked)
        self.export_jpeg_button.clicked.connect(self._on_export_jpeg_clicked)
        self.api_combo.currentTextChanged.connect(self._on_api_changed)
        self.averages_checkbox.stateChanged.connect(self._on_display_averages_changed)
        self.precip_threshold_spinbox.valueChanged.connect(self._plot_precipitation_graph)
        self.settings_button.clicked.connect(self._show_settings)
        self._on_preset_changed("7 Days") # Set initial state

        # Create the tab widget for different views
        self.tab_widget = QTabWidget()
        self.main_layout.addWidget(self.tab_widget)

        # Create the tabs
        self._create_tabs()

        # Create the status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")

    def _populate_api_combo(self):
        """
        Populates the API provider combo box based on available keys and services.
        """
        self.weather_repos.clear()

        # Always add free ones
        self.weather_repos["Open-Meteo"] = WeatherRepository()

        # Add others if enabled
        if self.settings_dialog.is_enabled("OpenWeatherMap"):
            key = self.settings_dialog.get_key("OpenWeatherMap")
            self.weather_repos["OpenWeatherMap"] = OpenWeatherRepository(key)

        if self.settings_dialog.is_enabled("WeatherAPI"):
            key = self.settings_dialog.get_key("WeatherAPI")
            self.weather_repos["WeatherAPI"] = WeatherAPIRepository(key)

        if self.settings_dialog.is_enabled("AccuWeather"):
            key = self.settings_dialog.get_key("AccuWeather")
            self.weather_repos["AccuWeather"] = AccuWeatherRepository(key)

        self.api_combo.clear()
        self.api_combo.addItems(list(self.weather_repos.keys()))

        # Set initial weather_service
        if self.weather_repos:
            first = list(self.weather_repos.keys())[0]
            self.api_combo.setCurrentText(first)
            self.weather_service = WeatherService(self.geocoding_repo, self.weather_repos[first])

    def _show_settings(self):
        """
        Shows the provider settings dialog.
        """
        from PyQt6.QtWidgets import QDialog
        if self.settings_dialog.exec() == QDialog.DialogCode.Accepted:
            self._populate_api_combo()
            # If current API is removed, switch to first
            current = self.api_combo.currentText()
            if current not in self.weather_repos and self.weather_repos:
                first = list(self.weather_repos.keys())[0]
                self.api_combo.setCurrentText(first)
                self._on_api_changed(first)

    def _create_input_panel(self):
        """
        Creates the input panel with all the user controls.
        """
        self.input_group_box = QGroupBox("Query Configuration")
        layout = QGridLayout()

        # Date Range Presets
        layout.addWidget(QLabel("Date Range Preset:"), 0, 0)
        self.preset_combo = QComboBox()
        self.preset_combo.addItems([
            "Custom", "7 Days", "14 Days", "30 Days",
            "3 Months", "6 Months", "12 Months"
        ])
        layout.addWidget(self.preset_combo, 0, 1)

        # Start Date
        layout.addWidget(QLabel("Start Date:"), 1, 0)
        self.start_date_edit = QDateEdit()
        self.start_date_edit.setCalendarPopup(True)
        self.start_date_edit.setDate(QDate.currentDate().addDays(-7))
        self.start_date_edit.setEnabled(False)
        layout.addWidget(self.start_date_edit, 1, 1)

        # End Date
        layout.addWidget(QLabel("End Date:"), 1, 2)
        self.end_date_edit = QDateEdit()
        self.end_date_edit.setCalendarPopup(True)
        self.end_date_edit.setDate(QDate.currentDate())
        self.end_date_edit.setEnabled(False)
        layout.addWidget(self.end_date_edit, 1, 3)

        # Number of Past Years
        layout.addWidget(QLabel("Number of Past Years:"), 2, 0)
        self.years_spinbox = QSpinBox()
        self.years_spinbox.setRange(1, 20)
        self.years_spinbox.setValue(3)
        layout.addWidget(self.years_spinbox, 2, 1)

        # Location
        layout.addWidget(QLabel("Location (City):"), 2, 2)
        self.location_edit = QLineEdit()
        self.location_edit.setPlaceholderText("e.g., New York")
        layout.addWidget(self.location_edit, 2, 3)

        # Fetch Button
        self.fetch_button = QPushButton("Fetch Historical Data")
        layout.addWidget(self.fetch_button, 3, 0, 1, 2)

        # Export Buttons
        self.export_csv_button = QPushButton("Export to CSV")
        self.export_csv_button.setEnabled(False)
        layout.addWidget(self.export_csv_button, 3, 2)

        self.export_excel_button = QPushButton("Export to Excel")
        self.export_excel_button.setEnabled(False)
        layout.addWidget(self.export_excel_button, 3, 3)

        self.export_jpeg_button = QPushButton("Export Precipitation Graph to JPEG")
        self.export_jpeg_button.setEnabled(False)
        layout.addWidget(self.export_jpeg_button, 6, 2)

        # Weather API Provider
        layout.addWidget(QLabel("Weather API:"), 4, 0)
        self.api_combo = QComboBox()
        layout.addWidget(self.api_combo, 4, 1)

        # Display Averages
        self.averages_checkbox = QCheckBox("Display Averages")
        layout.addWidget(self.averages_checkbox, 4, 2)

        # Provider Settings
        self.settings_button = QPushButton("Provider Settings")
        layout.addWidget(self.settings_button, 4, 3)

        # Precipitation Threshold
        layout.addWidget(QLabel("Precipitation Threshold:"), 5, 0)
        self.precip_threshold_spinbox = QSpinBox()
        self.precip_threshold_spinbox.setRange(0, 50)
        self.precip_threshold_spinbox.setValue(5)
        self.precip_threshold_spinbox.setSuffix(" mm")
        layout.addWidget(self.precip_threshold_spinbox, 5, 1)

        self.input_group_box.setLayout(layout)

    def _on_display_averages_changed(self, state):
        self._plot_temperature_graph()
        self._plot_precipitation_graph()

    def _on_api_changed(self, text):
        self.weather_service = WeatherService(self.geocoding_repo, self.weather_repos[text])

    def _on_fetch_data_clicked(self):
        """
        Handles the button click to fetch and display weather data.
        """
        location = self.location_edit.text()
        if not location:
            self.status_bar.showMessage("Error: Location cannot be empty.", 5000)
            return

        try:
            self.status_bar.showMessage(f"Fetching data for {location}...")
            self.fetch_button.setEnabled(False)

            # Get parameters from UI
            start_date = self.start_date_edit.date().toPyDate()
            end_date = self.end_date_edit.date().toPyDate()
            years = self.years_spinbox.value()

            # Validation for historical data
            today = date.today()
            if end_date > today:
                self.status_bar.showMessage("End date cannot be in the future for historical data.", 5000)
                return
            if start_date > end_date:
                self.status_bar.showMessage("Start date cannot be after end date.", 5000)
                return

            # Call the service
            records = self.weather_service.fetch_weather_for_range(
                location, start_date, end_date, years
            )

            # Populate the data grid with the records
            self.data_df = self._populate_data_grid(records)

            # Plot the graphs and manage button state
            if self.data_df is not None and not self.data_df.empty:
                self._plot_temperature_graph()
                self._plot_precipitation_graph()
                self.export_csv_button.setEnabled(True)
                self.export_excel_button.setEnabled(True)
                self.export_jpeg_button.setEnabled(True)
                self.status_bar.showMessage(f"Successfully loaded {len(records)} records.", 5000)
            else:
                self.export_csv_button.setEnabled(False)
                self.export_excel_button.setEnabled(False)
                # Message is already shown by _populate_data_grid if no data

        except ValueError as e:
            self.status_bar.showMessage(f"Error: {e}", 10000)
            self.export_csv_button.setEnabled(False)
            self.export_excel_button.setEnabled(False)
            self.export_jpeg_button.setEnabled(False)
        except Exception as e:
            self.status_bar.showMessage(f"An unexpected error occurred: {e}", 10000)
            self.export_csv_button.setEnabled(False)
            self.export_excel_button.setEnabled(False)
            self.export_jpeg_button.setEnabled(False)
        finally:
            self.fetch_button.setEnabled(True)


    def _on_preset_changed(self, text: str):
        """
        Handles the logic when the date range preset is changed.
        """
        today = QDate.currentDate()
        self.end_date_edit.setDate(today)

        if text == "Custom":
            self.start_date_edit.setEnabled(True)
            self.end_date_edit.setEnabled(True)
            return

        self.start_date_edit.setEnabled(False)
        self.end_date_edit.setEnabled(False)

        if text == "7 Days":
            self.start_date_edit.setDate(today.addDays(-7))
        elif text == "14 Days":
            self.start_date_edit.setDate(today.addDays(-14))
        elif text == "30 Days":
            self.start_date_edit.setDate(today.addDays(-30))
        elif text == "3 Months":
            self.start_date_edit.setDate(today.addMonths(-3))
        elif text == "6 Months":
            self.start_date_edit.setDate(today.addMonths(-6))
        elif text == "12 Months":
            self.start_date_edit.setDate(today.addMonths(-12))

    def _create_tabs(self):
        """
        Creates the tabs for the data grid and graphs.
        """
        # Data Grid Tab
        self.data_grid_tab = QWidget()
        self.data_grid_layout = QVBoxLayout(self.data_grid_tab)
        self.data_table = QTableWidget()
        self.data_grid_layout.addWidget(self.data_table)
        self.tab_widget.addTab(self.data_grid_tab, "Data Grid")

        # Temperature Graph Tab
        self.temp_chart = MatplotlibCanvas(self)
        self.tab_widget.addTab(self.temp_chart, "Temperature Graph")

        # Precipitation Graph Tab
        self.precip_chart = MatplotlibCanvas(self)
        self.tab_widget.addTab(self.precip_chart, "Precipitation Graph")

    def _populate_data_grid(self, records):
        """
        Populates the QTableWidget with the fetched weather records.
        Returns the created DataFrame.
        """
        if not records:
            self.data_table.setRowCount(0)
            self.data_table.setColumnCount(0)
            self.status_bar.showMessage("No data found for the selected criteria.", 5000)
            return None

        df = pd.DataFrame(records)

        # Reorder and rename columns for display
        df = df.rename(columns={
            'record_date': 'Date',
            'year': 'Year',
            'location': 'Location',
            'max_temp_c': 'Max Temp (°C)',
            'min_temp_c': 'Min Temp (°C)',
            'precipitation_mm': 'Precipitation (mm)'
        })
        # The location is empty in the record, so we'll fill it from the UI input
        df['Location'] = self.location_edit.text()

        headers = ['Date', 'Year', 'Location', 'Max Temp (°C)', 'Min Temp (°C)', 'Precipitation (mm)']
        df = df[headers]

        self.data_table.setRowCount(df.shape[0])
        self.data_table.setColumnCount(df.shape[1])
        self.data_table.setHorizontalHeaderLabels(df.columns)

        for row in range(df.shape[0]):
            for col in range(df.shape[1]):
                item = QTableWidgetItem(str(df.iat[row, col]))
                self.data_table.setItem(row, col, item)

        self.data_table.resizeColumnsToContents()
        header = self.data_table.horizontalHeader()
        if header:
            header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        return df

    def _plot_temperature_graph(self):
        """
        Plots the max temperature line chart.
        """
        self.temp_chart.clear()

        if self.data_df is None or self.data_df.empty:
            self.temp_chart.draw()
            return

        # Prepare data for plotting
        self.data_df['Date'] = pd.to_datetime(self.data_df['Date'])
        self.data_df['MonthDay'] = self.data_df['Date'].dt.strftime('%m-%d')

        pivot_df = self.data_df.pivot(index='MonthDay', columns='Year', values='Max Temp (°C)')

        if self.averages_checkbox.isChecked():
            avg_temps = pivot_df.mean(axis=1)
            self.temp_chart.axes.plot(pivot_df.index.to_numpy(), avg_temps.to_numpy(), label='Average')
        else:
            for year in pivot_df.columns:
                self.temp_chart.axes.plot(pivot_df.index.to_numpy(), pivot_df[year].to_numpy(), label=str(year))

        self.temp_chart.axes.set_title('Maximum Temperature Trends')
        self.temp_chart.axes.set_xlabel('Date (Month-Day)')
        self.temp_chart.axes.set_ylabel('Max Temperature (°C)')
        self.temp_chart.axes.legend()
        self.temp_chart.axes.grid(True)

        # Improve x-axis readability
        if len(pivot_df.index) > 20:
            step = len(pivot_df.index) // 10
            self.temp_chart.axes.set_xticks(self.temp_chart.axes.get_xticks()[::step])

        self.temp_chart.figure.tight_layout()
        self.temp_chart.draw()

    def _plot_precipitation_graph(self):
        """
        Plots the precipitation bar chart.
        """
        self.precip_chart.clear()

        if self.data_df is None or self.data_df.empty:
            self.precip_chart.draw()
            return

        # Use a copy to avoid SettingWithCopyWarning
        df_sorted = self.data_df.sort_values('Date').copy()
        df_sorted['DateStr'] = df_sorted['Date'].dt.strftime('%Y-%m-%d')
        df_sorted['MonthDay'] = df_sorted['Date'].dt.strftime('%m-%d')

        # Apply threshold filter
        threshold = self.precip_threshold_spinbox.value()
        df_filtered = df_sorted[df_sorted['Precipitation (mm)'] >= threshold]

        # Set minimum y-axis scale for readability (minimum 5mm to prevent small values from exaggerating the chart)
        min_y = 5 if df_filtered.empty or df_filtered['Precipitation (mm)'].max() <= 5 else 0
        max_y = df_filtered['Precipitation (mm)'].max() * 1.1 if not df_filtered.empty else 5
        self.precip_chart.axes.set_ylim(bottom=min_y)

        if self.averages_checkbox.isChecked():
            avg_precip = df_filtered.groupby('MonthDay')['Precipitation (mm)'].mean()
            self.precip_chart.axes.bar(avg_precip.index.to_numpy(), avg_precip.to_numpy())
        else:
            self.precip_chart.axes.bar(df_filtered['DateStr'], df_filtered['Precipitation (mm)'].to_numpy())

        self.precip_chart.axes.set_title('Daily Precipitation')
        self.precip_chart.axes.set_xlabel('Date')
        self.precip_chart.axes.set_ylabel('Precipitation (mm)')
        self.precip_chart.axes.grid(axis='y')

        # Improve x-axis readability
        self.precip_chart.figure.autofmt_xdate(rotation=45, ha='right')
        if not self.averages_checkbox.isChecked() and len(df_sorted['DateStr']) > 30:
              step = len(df_sorted['DateStr']) // 15
              self.precip_chart.axes.set_xticks(self.precip_chart.axes.get_xticks()[::step])

        self.precip_chart.figure.tight_layout()
        self.precip_chart.draw()


    def _on_export_csv_clicked(self):
        """
        Handles exporting the current data to a CSV file.
        """
        if self.data_df is None or self.data_df.empty:
            self.status_bar.showMessage("No data available to export.", 5000)
            return

        filepath, _ = QFileDialog.getSaveFileName(
            self, "Save CSV File", "", "CSV Files (*.csv);;All Files (*)"
        )

        if filepath:
            try:
                self.status_bar.showMessage(f"Exporting to {filepath}...")
                self.export_service.export_to_csv(self.data_df, filepath)
                self.status_bar.showMessage("Successfully exported to CSV.", 5000)
            except Exception as e:
                self.status_bar.showMessage(f"Export failed: {e}", 10000)

    def _on_export_excel_clicked(self):
        """
        Handles exporting the current data to an Excel file.
        """
        if self.data_df is None or self.data_df.empty:
            self.status_bar.showMessage("No data available to export.", 5000)
            return

        filepath, _ = QFileDialog.getSaveFileName(
            self, "Save Excel File", "", "Excel Files (*.xlsx);;All Files (*)"
        )

        if filepath:
            try:
                self.status_bar.showMessage(f"Exporting to {filepath}...")
                self.export_service.export_to_excel(self.data_df, filepath)
                self.status_bar.showMessage("Successfully exported to Excel.", 5000)
            except Exception as e:
                self.status_bar.showMessage(f"Export failed: {e}", 10000)

    def _on_export_jpeg_clicked(self):
        """
        Handles exporting the precipitation graph to a JPEG file.
        """
        if self.data_df is None or self.data_df.empty:
            self.status_bar.showMessage("No data available to export.", 5000)
            return

        filepath, _ = QFileDialog.getSaveFileName(
            self, "Save JPEG File", "", "JPEG Files (*.jpeg *.jpg);;All Files (*)"
        )

        if filepath:
            try:
                self.status_bar.showMessage(f"Exporting to {filepath}...")
                self.precip_chart.figure.savefig(filepath, format='jpeg', bbox_inches='tight')
                self.status_bar.showMessage("Successfully exported precipitation graph to JPEG.", 5000)
            except Exception as e:
                self.status_bar.showMessage(f"Export JPEG failed: {e}", 10000)


if __name__ == '__main__':
    # This is for testing the window directly
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())