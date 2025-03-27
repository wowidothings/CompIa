#plotter.py
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from datetime import datetime
import pandas as pd
import os

class LivePlotter(FigureCanvas):
    def __init__(self):
        self.fig = Figure(figsize=(8, 6))
        super().__init__(self.fig)
        self._setup_plots()
        self.data_dir = "data"
        self._init_data_storage()
        
    def _init_data_storage(self):
        """Initialize data structures for live plotting"""
        self.timestamps = []
        self.accel_data = []
        self.velocity_data = []
        self.position_data = []
        
    def _setup_plots(self):
        """Initialize matplotlib axes and lines"""
        self.axs = self.fig.subplots(3, 1)
        titles = ["Acceleration (m/s²)", "Velocity (m/s)", "Position (m)"]
        self.lines = {'live': [], 'historical': []}
        
        for i, ax in enumerate(self.axs):
            ax.set_title(titles[i])
            ax.set_xlabel("Time (ms)")
            ax.grid(True)
            # Live data lines (blue)
            live_line, = ax.plot([], [], 'b-', label='Live')
            # Historical data lines (orange, dashed)
            hist_line, = ax.plot([], [], 'C1--', label='Historical')
            self.lines['live'].append(live_line)
            self.lines['historical'].append(hist_line)
            ax.legend()
            
        self.fig.tight_layout()

    def update_plot(self, new_data):
        """Update plots with new real-time data"""
        parts = new_data.split(',')
        if len(parts) != 10:
            return
            
        try:
            t = float(parts[-1])
            self.timestamps.append(t)
            
            # Store parsed values
            self.accel_data.append(list(map(float, parts[0:3])))
            self.velocity_data.append(list(map(float, parts[3:6])))
            self.position_data.append(list(map(float, parts[6:9])))
            
            # Update live plots
            self._update_axes(0, self.accel_data)
            self._update_axes(1, self.velocity_data)
            self._update_axes(2, self.position_data)
            
            self.draw()
        except ValueError:
            pass

    def _update_axes(self, ax_idx, data):
        """Helper to update specific subplot"""
        self.lines['live'][ax_idx].set_data(
            self.timestamps,
            [d[ax_idx] for d in data]
        )
        self.axs[ax_idx].relim()
        self.axs[ax_idx].autoscale_view()

    def save_session(self):
        """Save current session data and plot"""
        if not self.timestamps:
            return
            
        # Create data directory if needed
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Generate timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        
        # Save CSV
        df = pd.DataFrame({
            't': self.timestamps,
            'ax': [d[0] for d in self.accel_data],
            'ay': [d[1] for d in self.accel_data],
            'az': [d[2] for d in self.accel_data],
            'vx': [d[0] for d in self.velocity_data],
            'vy': [d[1] for d in self.velocity_data],
            'vz': [d[2] for d in self.velocity_data],
            'px': [d[0] for d in self.position_data],
            'py': [d[1] for d in self.position_data],
            'pz': [d[2] for d in self.position_data]
        })
        df.to_csv(f"{self.data_dir}/{timestamp}_session.csv", index=False)
        
        # Save plot
        self.fig.savefig(f"{self.data_dir}/{timestamp}_graph.png")
        
        # Clear live data for next session
        self._init_data_storage()

    def load_historical_plot(self, csv_path):
        """Load and plot historical data from CSV"""
        try:
            df = pd.read_csv(csv_path)
            
            # Update historical plots
            self._update_historical_axis(0, df['t'], df[['ax', 'ay', 'az']])
            self._update_historical_axis(1, df['t'], df[['vx', 'vy', 'vz']])
            self._update_historical_axis(2, df['t'], df[['px', 'py', 'pz']])
            
            self.draw()
        except Exception as e:
            print(f"Error loading historical data: {e}")

    def _update_historical_axis(self, ax_idx, times, data):
        """Helper to update historical plots"""
        for i, col in enumerate(data.columns):
            self.lines['historical'][ax_idx].set_data(times, data[col])
            
        self.axs[ax_idx].relim()
        self.axs[ax_idx].autoscale_view()