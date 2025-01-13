import sys
import numpy as np
import matplotlib.pyplot as plt
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel, QLineEdit, QPushButton, QHBoxLayout, QComboBox
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

# PID Controller Class
class PIDController:
    def __init__(self, Kp, Ki, Kd):
        self.Kp = Kp  # Proportional gain
        self.Ki = Ki  # Integral gain
        self.Kd = Kd  # Derivative gain
        self.previous_error = 0  # Previous error
        self.integral = 0  # Integral term

    # Compute PID output
    def compute(self, setpoint, measured_value):
        error = setpoint - measured_value  # Current error
        self.integral += error  # Accumulate error (integral term)
        derivative = error - self.previous_error  # Error rate of change (derivative term)
        output = self.Kp * error + self.Ki * self.integral + self.Kd * derivative  # PID output
        self.previous_error = error  # Update previous error
        return output

# Boiler Simulation Class
class BoilerSimulation:
    def __init__(self):
        self.temperature = 20.0  # Initial temperature
        self.heat = 0.0  # Initial heat
        self.fixed_noise = 0.0  # Fixed noise value

    # Update boiler temperature
    def update(self, heat_input, dt, disturbance_type, noise_std, periodic_amplitude, periodic_frequency, time):
        # Simple model: temperature change is proportional to heat input
        self.temperature += heat_input * dt

        # Add disturbance based on selected type
        if disturbance_type == "Random Noise":
            disturbance = np.random.normal(0, noise_std)  # Random noise
        elif disturbance_type == "Periodic":
            disturbance = periodic_amplitude * np.sin(periodic_frequency * time)  # Periodic disturbance
        elif disturbance_type == "Fixed Noise":
            disturbance = self.fixed_noise  # Fixed noise
        else:
            disturbance = 0  # No disturbance

        self.temperature += disturbance  # Add disturbance
        return self.temperature

# Main Window Class
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Set window title and size
        self.setWindowTitle("Boiler Temperature PID Control")
        self.setGeometry(100, 100, 800, 600)

        # PID Controller and Boiler Simulation objects
        self.pid = PIDController(Kp=1.0, Ki=0.1, Kd=0.01)
        self.boiler = BoilerSimulation()
        self.setpoint = 50.0  # Target temperature
        self.dt = 0.1  # Time step
        self.running = False  # Control whether running
        self.disturbance_type = "Random Noise"  # Default disturbance type
        self.noise_std = 0.5  # Default noise standard deviation
        self.periodic_amplitude = 2.0  # Default periodic disturbance amplitude
        self.periodic_frequency = 0.1  # Default periodic disturbance frequency

        # Layout
        layout = QVBoxLayout()

        # Control panel layout
        control_layout = QHBoxLayout()

        # Setpoint input
        self.setpoint_label = QLabel("Setpoint:")
        self.setpoint_input = QLineEdit("50.0")
        control_layout.addWidget(self.setpoint_label)
        control_layout.addWidget(self.setpoint_input)

        # Proportional gain (Kp) input
        self.kp_label = QLabel("Kp:")
        self.kp_input = QLineEdit("1.0")
        control_layout.addWidget(self.kp_label)
        control_layout.addWidget(self.kp_input)

        # Integral gain (Ki) input
        self.ki_label = QLabel("Ki:")
        self.ki_input = QLineEdit("0.1")
        control_layout.addWidget(self.ki_label)
        control_layout.addWidget(self.ki_input)

        # Derivative gain (Kd) input
        self.kd_label = QLabel("Kd:")
        self.kd_input = QLineEdit("0.01")
        control_layout.addWidget(self.kd_label)
        control_layout.addWidget(self.kd_input)

        # Start button
        self.start_button = QPushButton("Start")
        self.start_button.clicked.connect(self.start)
        control_layout.addWidget(self.start_button)

        # Stop button
        self.stop_button = QPushButton("Stop")
        self.stop_button.clicked.connect(self.stop)
        control_layout.addWidget(self.stop_button)

        layout.addLayout(control_layout)

        # Disturbance settings layout
        disturbance_layout = QHBoxLayout()

        # Disturbance type selection
        self.disturbance_type_label = QLabel("Disturbance Type:")
        self.disturbance_type_combo = QComboBox()
        self.disturbance_type_combo.addItems(["Random Noise", "Periodic", "Fixed Noise"])
        self.disturbance_type_combo.currentTextChanged.connect(self.set_disturbance_type)
        disturbance_layout.addWidget(self.disturbance_type_label)
        disturbance_layout.addWidget(self.disturbance_type_combo)

        # Random noise standard deviation input
        self.noise_std_label = QLabel("Noise Std Dev:")
        self.noise_std_input = QLineEdit("0.5")
        disturbance_layout.addWidget(self.noise_std_label)
        disturbance_layout.addWidget(self.noise_std_input)

        # Periodic disturbance amplitude input
        self.periodic_amplitude_label = QLabel("Periodic Amplitude:")
        self.periodic_amplitude_input = QLineEdit("2.0")
        disturbance_layout.addWidget(self.periodic_amplitude_label)
        disturbance_layout.addWidget(self.periodic_amplitude_input)

        # Periodic disturbance frequency input
        self.periodic_frequency_label = QLabel("Periodic Frequency:")
        self.periodic_frequency_input = QLineEdit("0.1")
        disturbance_layout.addWidget(self.periodic_frequency_label)
        disturbance_layout.addWidget(self.periodic_frequency_input)

        # Fixed noise value input
        self.fixed_noise_label = QLabel("Fixed Noise Value:")
        self.fixed_noise_input = QLineEdit("0.5")
        disturbance_layout.addWidget(self.fixed_noise_label)
        disturbance_layout.addWidget(self.fixed_noise_input)

        layout.addLayout(disturbance_layout)

        # Current temperature display
        self.current_temp_label = QLabel("Current Temperature: 20.0 °C")
        layout.addWidget(self.current_temp_label)

        # Plot area
        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        self.ax = self.figure.add_subplot(111)
        self.ax.set_xlabel("Time (s)")
        self.ax.set_ylabel("Temperature (°C)")
        self.ax.set_ylim(0, 100)
        self.line, = self.ax.plot([], [])  # Initialize curve
        self.time_data = []  # Time data
        self.temp_data = []  # Temperature data

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

    # Start button click event
    def start(self):
        self.running = True
        self.setpoint = float(self.setpoint_input.text())  # Read setpoint
        self.pid.Kp = float(self.kp_input.text())  # Read proportional gain
        self.pid.Ki = float(self.ki_input.text())  # Read integral gain
        self.pid.Kd = float(self.kd_input.text())  # Read derivative gain
        self.noise_std = float(self.noise_std_input.text())  # Read noise standard deviation
        self.periodic_amplitude = float(self.periodic_amplitude_input.text())  # Read periodic amplitude
        self.periodic_frequency = float(self.periodic_frequency_input.text())  # Read periodic frequency
        self.boiler.fixed_noise = float(self.fixed_noise_input.text())  # Read fixed noise value

    # Stop button click event
    def stop(self):
        self.running = False

    # Set disturbance type
    def set_disturbance_type(self, text):
        self.disturbance_type = text

    # Update plot
    def update_plot(self):
        if self.running:
            # Compute PID output
            heat_input = self.pid.compute(self.setpoint, self.boiler.temperature)
            time = len(self.time_data) * self.dt  # Current time
            # Update boiler temperature
            temperature = self.boiler.update(
                heat_input, self.dt, self.disturbance_type, self.noise_std, self.periodic_amplitude, self.periodic_frequency, time
            )
            self.time_data.append(time)  # Record time
            self.temp_data.append(temperature)  # Record temperature

            # Update current temperature display
            self.current_temp_label.setText(f"Current Temperature: {temperature:.2f} °C")

            # Update curve data
            self.line.set_data(self.time_data, self.temp_data)

            # Set x-axis range
            max_time = max(self.time_data) if self.time_data else 1
            min_time = 0
            if max_time <= min_time:
                max_time = min_time + 1  # Ensure minimum range

            self.ax.set_xlim(min_time, max_time)
            self.ax.relim()
            self.ax.autoscale_view()
            self.canvas.draw()  # Redraw plot

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())