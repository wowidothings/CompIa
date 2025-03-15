import sys
from PyQt6.QtWidgets import QApplication
from main_window import MainWindow

MICROBIT_ADDRESS = "YOUR_MICROBIT_BLE_ADDRESS"  # Replace this!

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow(MICROBIT_ADDRESS)
    window.show()
    sys.exit(app.exec())