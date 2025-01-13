import sys
import numpy as np
import matplotlib.pyplot as plt
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel, QLineEdit, QPushButton, QHBoxLayout, QComboBox
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

class PIDController:
    def __init__(self, Kp, Ki, Kd):
        self.Kp = Kp
        self.Ki = Ki
        self.Kd = Kd
        self.previous_error = 0
        self.integral = 0

    def compute(self, setpoint, measured_value):
        error = setpoint - measured_value
        self.integral += error
        derivative = error - self.previous_error
        output = self.Kp * error + self.Ki * self.integral + self.Kd * derivative
        self.previous_error = error
        return output

class BoilerSimulation:
    def __init__(self):
        self.temperature = 20.0  # Initial temperature
        self.heat = 0.0

    def update(self, heat_input, dt, disturbance_type, noise_std, periodic_amplitude, periodic_frequency, time):
        # Simple model: temperature change is proportional to heat input
        self.temperature += heat_input * dt - 0.1 * (self.temperature - 20) * dt

        # Add disturbance based on the selected type
        if disturbance_type == "Random Noise":
            disturbance = np.random.normal(0, noise_std)  # Random noise
        elif disturbance_type == "Periodic":
            disturbance = periodic_amplitude * np.sin(periodic_frequency * time)  # Periodic disturbance
        else:
            disturbance = 0  # No disturbance

        self.temperature += disturbance
        return self.temperature

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Boiler Temperature PID Control")
        self.setGeometry(100, 100, 800, 600)

        # PID Controller
        self.pid = PIDController(Kp=1.0, Ki=0.1, Kd=0.01)
        self.boiler = BoilerSimulation()
        self.setpoint = 50.0
        self.dt = 0.1
        self.running = False
        self.disturbance_type = "Random Noise"  # Default disturbance type
        self.noise_std = 0.5  # Default noise standard deviation
        self.periodic_amplitude = 2.0  # Default periodic amplitude
        self.periodic_frequency = 0.1  # Default periodic frequency

        # Layout
        layout = QVBoxLayout()

        # Control Panel
        control_layout = QHBoxLayout()

        self.setpoint_label = QLabel("Setpoint:")
        self.setpoint_input = QLineEdit("50.0")
        control_layout.addWidget(self.setpoint_label)
        control_layout.addWidget(self.setpoint_input)

        self.kp_label = QLabel("Kp:")
        self.kp_input = QLineEdit("1.0")
        control_layout.addWidget(self.kp_label)
        control_layout.addWidget(self.kp_input)

        self.ki_label = QLabel("Ki:")
        self.ki_input = QLineEdit("0.1")
        control_layout.addWidget(self.ki_label)
        control_layout.addWidget(self.ki_input)

        self.kd_label = QLabel("Kd:")
        self.kd_input = QLineEdit("0.01")
        control_layout.addWidget(self.kd_label)
        control_layout.addWidget(self.kd_input)

        self.start_button = QPushButton("Start")
        self.start_button.clicked.connect(self.start)
        control_layout.addWidget(self.start_button)

        self.stop_button = QPushButton("Stop")
        self.stop_button.clicked.connect(self.stop)
        control_layout.addWidget(self.stop_button)

        layout.addLayout(control_layout)

        # Disturbance Settings
        disturbance_layout = QHBoxLayout()

        self.disturbance_type_label = QLabel("Disturbance Type:")
        self.disturbance_type_combo = QComboBox()
        self.disturbance_type_combo.addItems(["Random Noise", "Periodic"])
        self.disturbance_type_combo.currentTextChanged.connect(self.set_disturbance_type)
        disturbance_layout.addWidget(self.disturbance_type_label)
        disturbance_layout.addWidget(self.disturbance_type_combo)

        self.noise_std_label = QLabel("Noise Std:")
        self.noise_std_input = QLineEdit("0.5")
        disturbance_layout.addWidget(self.noise_std_label)
        disturbance_layout.addWidget(self.noise_std_input)

        self.periodic_amplitude_label = QLabel("Periodic Amplitude:")
        self.periodic_amplitude_input = QLineEdit("2.0")
        disturbance_layout.addWidget(self.periodic_amplitude_label)
        disturbance_layout.addWidget(self.periodic_amplitude_input)

        self.periodic_frequency_label = QLabel("Periodic Frequency:")
        self.periodic_frequency_input = QLineEdit("0.1")
        disturbance_layout.addWidget(self.periodic_frequency_label)
        disturbance_layout.addWidget(self.periodic_frequency_input)

        layout.addLayout(disturbance_layout)

        # Current Temperature Display
        self.current_temp_label = QLabel("Current Temperature: 20.0 °C")
        layout.addWidget(self.current_temp_label)

        # Plot
        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        self.ax = self.figure.add_subplot(111)
        self.ax.set_xlabel("Time (s)")
        self.ax.set_ylabel("Temperature (°C)")
        self.ax.set_ylim(0, 100)
        self.line, = self.ax.plot([], [])
        self.time_data = []
        self.temp_data = []

        layout.addWidget(self.canvas)

        # Set layout
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        # Timer for updating the plot
        from PyQt5.QtCore import QTimer
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_plot)
        self.timer.start(100)  # Update every 100 ms

    def start(self):
        self.running = True
        self.setpoint = float(self.setpoint_input.text())
        self.pid.Kp = float(self.kp_input.text())
        self.pid.Ki = float(self.ki_input.text())
        self.pid.Kd = float(self.kd_input.text())
        self.noise_std = float(self.noise_std_input.text())
        self.periodic_amplitude = float(self.periodic_amplitude_input.text())
        self.periodic_frequency = float(self.periodic_frequency_input.text())

    def stop(self):
        self.running = False

    def set_disturbance_type(self, text):
        self.disturbance_type = text

    def update_plot(self):
        if self.running:
            heat_input = self.pid.compute(self.setpoint, self.boiler.temperature)
            time = len(self.time_data) * self.dt
            temperature = self.boiler.update(
                heat_input, self.dt, self.disturbance_type, self.noise_std, self.periodic_amplitude, self.periodic_frequency, time
            )
            self.time_data.append(time)
            self.temp_data.append(temperature)

            # Update current temperature display
            self.current_temp_label.setText(f"Current Temperature: {temperature:.2f} °C")

            self.line.set_data(self.time_data, self.temp_data)

            # Avoid setting identical xlims
            max_time = max(self.time_data) if self.time_data else 1
            min_time = 0
            if max_time <= min_time:
                max_time = min_time + 1  # Ensure a minimum range

            self.ax.set_xlim(min_time, max_time)
            self.ax.relim()
            self.ax.autoscale_view()
            self.canvas.draw()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())