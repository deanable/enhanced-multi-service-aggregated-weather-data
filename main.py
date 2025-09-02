import sys
import logging
from PyQt6.QtWidgets import QApplication
from emsawd.ui.main_window import MainWindow
from emsawd.core.logging_config import setup_logging

def main():
    """
    Main function to initialize and run the application.
    """
    setup_logging()
    logging.info("Application starting up.")

    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()

    logging.info("Main window shown. Starting event loop.")
    exit_code = app.exec()
    logging.info(f"Application exiting with code {exit_code}.")
    sys.exit(exit_code)

if __name__ == "__main__":
    main()
