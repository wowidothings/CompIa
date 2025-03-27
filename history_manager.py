# history_manager.py
import os
import pandas as pd
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QListWidget, QPushButton

class HistoryDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Session History")
        self.layout = QVBoxLayout()
        
        # List of sessions
        self.list_widget = QListWidget()
        self.load_sessions()
        
        # Load button
        self.load_btn = QPushButton("Load Selected")
        self.load_btn.clicked.connect(self.load_selected)
        
        self.layout.addWidget(self.list_widget)
        self.layout.addWidget(self.load_btn)
        self.setLayout(self.layout)

    def load_sessions(self):
        """Populate list with saved sessions"""
        self.list_widget.clear()
        if not os.path.exists("data"):
            os.makedirs("data")
        for f in os.listdir("data"):
            if f.endswith(".csv"):
                self.list_widget.addItem(f.replace("_session.csv", ""))

    def load_selected(self):
        """Load selected session data"""
        selected = self.list_widget.currentItem()
        if selected:
            timestamp = selected.text()
            self.parent().load_historical_data(timestamp)
            self.close()