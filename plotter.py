from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

class LivePlotter(FigureCanvas):
    def __init__(self):
        self.fig, self.axs = Figure(), []
        super().__init__(self.fig)
        self._setup_plots()

    def _setup_plots(self):
        self.fig.clear()
        self.axs = self.fig.subplots(3, 1)
        self.axs[0].set_title("Acceleration (m/s²)")
        self.axs[1].set_title("Velocity (m/s)")
        self.axs[2].set_title("Position (m)")
        self.lines = {
            'accel': [ax.plot([], [])[0] for ax in self.axs],
            'velocity': [ax.plot([], [])[0] for ax in self.axs],
            'position': [ax.plot([], [])[0] for ax in self.axs]
        }
        self.timestamps = []
        self.data = {'accel': [], 'velocity': [], 'position': []}

    def update_plot(self, new_data):
        parts = new_data.split(',')
        t = float(parts[-1])
        self.timestamps.append(t)
        # Update acceleration, velocity, position data
        self.data['accel'].append(list(map(float, parts[0:3])))
        self.data['velocity'].append(list(map(float, parts[3:6])))
        self.data['position'].append(list(map(float, parts[6:9])))
        # Redraw plots
        for i, key in enumerate(['accel', 'velocity', 'position']):
            self.lines[key][i].set_data(self.timestamps, [d[i] for d in self.data[key]])
            self.axs[i].relim()
            self.axs[i].autoscale_view()
        self.draw()