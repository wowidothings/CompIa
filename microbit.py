# micro:bit v2 - Complete Kinematics Data Collector
from microbit import *
import radio
import math

# ========== CONFIGURATION ==========
CALIBRATION_SAMPLES = 100  # Samples for baseline calibration
SAMPLE_RATE_MS = 100       # ~10 Hz data collection
CALIBRATE_HOLD_MS = 3000   # 3s hold for A+B calibration

# ========== BLE UART SETUP ==========
class BLEUART:
    def __init__(self):
        radio.on()
        radio.config(
            group=0,
            power=6,
            address=0x75626974,
            queue=10,
            data_rate=radio.RATE_1MBIT
        )
        self.rx_buffer = []

    def any(self):
        return len(self.rx_buffer) > 0

    def read(self):
        return self.rx_buffer.pop(0) if self.any() else None

    def send(self, data):
        radio.send_bytes(data.encode())

    def check_incoming(self):
        incoming = radio.receive_bytes()
        if incoming:
            self.rx_buffer.append(incoming.decode().strip())

# ========== KINEMATICS SYSTEM ==========
class Kinematics:
    def __init__(self):
        self.offset = (0, 0, 0)
        self.velocity = [0.0, 0.0, 0.0]
        self.position = [0.0, 0.0, 0.0]
        self.last_time = 0

    def calibrate(self):
        display.show("C")
        x, y, z = [], [], []
        for _ in range(CALIBRATION_SAMPLES):
            acc = accelerometer.get_values()
            x.append(acc[0])
            y.append(acc[1])
            z.append(acc[2])
            sleep(10)
        self.offset = (
            sum(x) // CALIBRATION_SAMPLES,
            sum(y) // CALIBRATION_SAMPLES,
            sum(z) // CALIBRATION_SAMPLES
        )
        display.show(Image.YES)

    def integrate(self, ax, ay, az, dt):
        # Remove offset and integrate
        ax_adj = ax - self.offset[0]
        ay_adj = ay - self.offset[1]
        az_adj = az - self.offset[2]

        # Update velocity
        self.velocity[0] += ax_adj * dt
        self.velocity[1] += ay_adj * dt
        self.velocity[2] += az_adj * dt

        # Update position
        self.position[0] += self.velocity[0] * dt
        self.position[1] += self.velocity[1] * dt
        self.position[2] += self.velocity[2] * dt

# ========== MAIN PROGRAM ==========
uart = BLEUART()
kinematics = Kinematics()
kinematics.calibrate()

while True:
    # Handle manual calibration
    if button_a.is_pressed() and button_b.is_pressed():
        sleep(CALIBRATE_HOLD_MS)
        if button_a.is_pressed() and button_b.is_pressed():
            kinematics.calibrate()
            display.scroll("CALIBRATED")

    # Check for BLE commands
    uart.check_incoming()
    if uart.any():
        cmd = uart.read()
        if cmd.startswith("START:"):
            duration = int(cmd.split(":")[1])

            # 3-second countdown
            for i in range(3, 0, -1):
                display.show(str(i))
                sleep(1000)
            display.clear()

            # Reset integration
            kinematics.velocity = [0.0, 0.0, 0.0]
            kinematics.position = [0.0, 0.0, 0.0]
            start_time = running_time()

            # Data collection loop
            while (running_time() - start_time) < duration * 1000:
                current_time = running_time()
                dt = (current_time - kinematics.last_time) / 1000
                if dt <= 0: dt = 0.001

                # Get sensor data
                ax, ay, az = accelerometer.get_values()
                kinematics.integrate(ax, ay, az, dt)

                # Format data: ax,ay,az,vx,vy,vz,px,py,pz,timestamp
                data = (
                    str(ax) + "," + str(ay) + "," + str(az) + "," +
                    str(kinematics.velocity[0]) + "," +
                    str(kinematics.velocity[1]) + "," +
                    str(kinematics.velocity[2]) + "," +
                    str(kinematics.position[0]) + "," +
                    str(kinematics.position[1]) + "," +
                    str(kinematics.position[2]) + "," +
                    str(current_time)
                )

                uart.send(data + "\n")
                kinematics.last_time = current_time
                sleep(SAMPLE_RATE_MS)

            display.show(Image.DIAMOND)
            sleep(1000)
            display.clear()
