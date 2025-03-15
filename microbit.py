from microbit import *
import ble_uart
import math

# --- CONFIGURATION ---
CALIBRATION_SAMPLES = 100  # Samples for baseline calibration
CALIBRATION_DELAY_MS = 3000  # 3 seconds for manual calibration
SAMPLE_RATE_MS = 300  #~30 Hz (adjustable)
DATA_HEADER = "ax,ay,az,vx,vy,vz,px,py,pz,t"

# --- GLOBAL VARIABLES ---
offset = (0, 0, 0)  # Calibration offsets
velocity = [0.0, 0.0, 0.0]
position = [0.0, 0.0, 0.0]
last_time = 0
uart = ble_uart.BLEUART()

# --- CALIBRATION ---
def calibrate():
    global offset
    display.show("C")
    x, y, z = [], [], []
    # Average accelerometer readings while stationary
    for _ in range(CALIBRATION_SAMPLES):
        acc = accelerometer.get_values()
        x.append(acc[0])
        y.append(acc[1])
        z.append(acc[2])
        sleep(10)
    offset = (
        sum(x) / CALIBRATION_SAMPLES,
        sum(y) / CALIBRATION_SAMPLES,
        sum(z) / CALIBRATION_SAMPLES
    )
    display.show(Image.YES)

# --- INTEGRATION FUNCTIONS ---
def integrate(ax, ay, az, dt):
    global velocity, position
    # Update velocity (v = v0 + a*dt)
    velocity[0] += (ax - offset[0]) * dt
    velocity[1] += (ay - offset[1]) * dt
    velocity[2] += (az - offset[2]) * dt
    # Update position (p = p0 + v*dt)
    position[0] += velocity[0] * dt
    position[1] += velocity[1] * dt
    position[2] += velocity[2] * dt

# --- MAIN LOOP ---
calibrate()  # Calibrate on boot

while True:
    # Manual calibration (hold A+B for 3 seconds)
    if button_a.is_pressed() and button_b.is_pressed():
        sleep(CALIBRATION_DELAY_MS)
        if button_a.is_pressed() and button_b.is_pressed():
            calibrate()
            display.scroll("CALIBRATED")

    # Check for incoming BLE commands
    if uart.any():
        command = uart.read().decode().strip()
        if command.startswith("START:"):
            duration = int(command.split(":")[1])
            
            # 3-second countdown
            for i in range(3, 0, -1):
                display.show(str(i))
                sleep(1000)
            display.clear()
            
            # Reset integration variables
            velocity = [0.0, 0.0, 0.0]
            position = [0.0, 0.0, 0.0]
            start_time = running_time()
            last_time = 0
            
            # Collect data for <duration> seconds
            while (running_time() - start_time) < duration * 1000:
                current_time = running_time()
                dt = (current_time - last_time) / 1000  # Convert to seconds
                if dt <= 0: dt = 0.001  # Avoid division by zero
                
                # Read accelerometer and integrate
                ax, ay, az = accelerometer.get_values()
                integrate(ax, ay, az, dt)
                
                # Send data via BLE
                data = f"{ax},{ay},{az},{velocity[0]},{velocity[1]},{velocity[2]},"
                data += f"{position[0]},{position[1]},{position[2]},{current_time}"
                uart.send(data + "\n")
                
                last_time = current_time
                sleep(SAMPLE_RATE_MS)
            
            display.show(Image.DIAMOND)
            sleep(1000)
            display.clear()