import sys
from PyQt6.QtCore import QSettings, QUrl
from PyQt6.QtGui import QDesktopServices
from PyQt6.QtWidgets import (
    QApplication, QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QFormLayout, QDialogButtonBox
)

class SettingsDialog(QDialog):
    """
    Dialog for managing API keys for various weather providers.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("API Provider Settings")
        self.setModal(True)
        self.settings = QSettings("EMS AWD", "WeatherApp")

        # Providers and their signup URLs
        self.providers = {
            "Open-Meteo": {"url": "", "required": False, "key": ""},
            "Mock API": {"url": "", "required": False, "key": ""},
            "OpenWeatherMap": {"url": "https://home.openweathermap.org/api_keys", "required": True, "key": ""},
            "WeatherAPI": {"url": "https://www.weatherapi.com/", "required": True, "key": ""},
            "AccuWeather": {"url": "https://developer.accuweather.com/", "required": True, "key": ""}
        }

        layout = QVBoxLayout()
        form_layout = QFormLayout()

        self.key_edits = {}
        for provider, info in self.providers.items():
            if info["required"]:
                # Key input
                key_edit = QLineEdit()
                key_edit.setPlaceholderText("Enter API key")
                key_edit.setText(self.settings.value(f"{provider}/key", ""))
                self.key_edits[provider] = key_edit

                # Horizontal layout for key and link
                hbox = QHBoxLayout()
                hbox.addWidget(key_edit)

                # Hyperlink button
                link_btn = QPushButton("Get API Key")
                link_btn.setStyleSheet("text-decoration: underline; color: blue; border: none; font-size: 12px;")
                link_btn.clicked.connect(lambda checked, url=info["url"]: self.open_url(url))
                hbox.addWidget(link_btn)

                form_layout.addRow(f"{provider} API Key:", hbox)
            else:
                # No key required, just info
                info_label = QLabel("No API key required for this service")
                info_label.setStyleSheet("color: green;")
                form_layout.addRow(provider, info_label)

        layout.addLayout(form_layout)

        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.save_settings)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

        self.setLayout(layout)
        self.resize(500, 300)

    def open_url(self, url):
        if url:
            QDesktopServices.openUrl(QUrl(url))

    def save_settings(self):
        """Save the API keys to persistent storage."""
        for provider, key_edit in self.key_edits.items():
            self.settings.setValue(f"{provider}/key", key_edit.text())
        self.accept()

    def get_key(self, provider):
        """Get the stored API key for a provider."""
        return self.settings.value(f"{provider}/key", "")

    def is_enabled(self, provider):
        """Check if a provider is enabled (has API key if required)."""
        if provider in self.providers:
            if self.providers[provider]["required"]:
                return bool(self.get_key(provider))
        return True


if __name__ == "__main__":
    app = QApplication(sys.argv)
    dialog = SettingsDialog()
    dialog.show()
    sys.exit(app.exec())