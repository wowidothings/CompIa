#main_window.py
from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QSpinBox, QPushButton, QTabWidget, QMessageBox  
from ble_connecter import BLEWorker
from plotter import LivePlotter
from history_manager import HistoryDialog


class MainWindow(QMainWindow):
    def __init__(self, ble_address):
        super().__init__()
        self.setWindowTitle("Micro:bit Kinematics Analyzer")
        self.resize(1200, 800)
        self.ble_worker = BLEWorker(ble_address)
        self._setup_ui()
        self.history_btn.clicked.connect(self.show_history)
        

    def _setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QHBoxLayout(central_widget)
        
        
        # Control Panel
        control_panel = QWidget()
        control_layout = QVBoxLayout(control_panel)
        self.duration_spin = QSpinBox()
        self.duration_spin.setRange(0, 60)
        self.start_btn = QPushButton("Start")
        self.download_btn = QPushButton("Download PNG")
        self.history_btn = QPushButton("History")
        
        control_layout.addWidget(self.duration_spin)
        control_layout.addWidget(self.start_btn)
        control_layout.addWidget(self.download_btn)
        control_layout.addWidget(self.history_btn)
        
        # Plot Area
        self.tabs = QTabWidget()
        self.realtime_plot = LivePlotter()
        self.history_plot = LivePlotter()
        self.tabs.addTab(self.realtime_plot, "Live Data")
        self.tabs.addTab(self.history_plot, "History")
        
        layout.addWidget(control_panel, stretch=1)
        layout.addWidget(self.tabs, stretch=4)
        
        # Connect Signals
        self.start_btn.clicked.connect(self.start_collection)
        self.ble_worker.data_received.connect(self.realtime_plot.update_plot)
        self.ble_worker.connection_changed.connect(self._handle_connection)
        self.download_btn.clicked.connect(self.save_current_plot)  


    def start_collection(self):
        self.ble_worker.set_duration(self.duration_spin.value())
        self.ble_worker.start()

    def _handle_connection(self, is_connected):
        self.start_btn.setEnabled(not is_connected)
        self.duration_spin.setEnabled(not is_connected)
        
    # In MainWindow class to save and show history and load historical data
    def show_history(self):
        dialog = HistoryDialog(self)
        dialog.exec()

    def save_current_plot(self):  
        # Save either live or historical plot based on active tab  
        if self.tabs.currentIndex() == 0:  # Live Data tab  
            self.realtime_plot.save_session()  
            QMessageBox.information(self, "Saved", "Plot and CSV saved successfully!")
        else:  # History tab  
            self.history_plot.save_session()  
            QMessageBox.information(self, "Saved", "Plot and CSV saved successfully!")

    def load_historical_data(self, timestamp):
        """Load and plot historical data"""
        # Load CSV
        df = pd.read_csv(f"data/{timestamp}_session.csv")
        
        # Convert to lists for plotting
        time = df["t"].tolist()
        accel = df[["ax", "ay", "az"]].values.tolist()
        velocity = df[["vx", "vy", "vz"]].values.tolist()
        position = df[["px", "py", "pz"]].values.tolist()
        
        # Update plots
        self.history_plot.update_historical_plot(time, accel, velocity, position)
