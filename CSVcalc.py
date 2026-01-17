import serial
import csv
import time

# Configuration
SERIAL_PORT = "/dev/cu.usbmodem1103" 
BAUD_RATE = 115200
FILE_NAME = "arm_stability_data.csv"

# --- NEW VARIABLES ---
WINDOW_SIZE = 5  # Change this to adjust how many samples to check
flex_history = [] 

def calculate_direction(history):
    """Determines UP or DOWN based on trend of the history list."""
    if len(history) < WINDOW_SIZE:
        return "STABLE" # Not enough data yet
    
    # Check if every value is >= the one before it (Increasing/Equal)
    is_up = all(history[i] >= history[i-1] for i in range(1, len(history)))
    if is_up:
        return "UP"
    
    # Check if every value is <= the one before it (Decreasing/Equal)
    is_down = all(history[i] <= history[i-1] for i in range(1, len(history)))
    if is_down:
        return "DOWN"
    
    return "FLUCTUATING"

try:
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
    print(f"Connected to {SERIAL_PORT}. Press Ctrl+C to stop recording.")

    with open(FILE_NAME, mode='w', newline='') as f:
        writer = csv.writer(f)
        
        # Added "Stability" and "Trend_Direction" to header
        header = ["Timestamp", "Flex_Value", "Accel_X", "Accel_Y", "Accel_Z", 
                  "Intensity", "Direction", "Stability", "Trend_Direction"]
        writer.writerow(header)

        while True:
            if ser.in_waiting > 0:
                line = ser.readline().decode('utf-8', errors='ignore').strip()
                
                if line:
                    data_points = line.split(',')
                    
                    if len(data_points) == 6:
                        try:
                            # Parse data
                            current_flex = float(data_points[0])
                            accel_x = float(data_points[1])
                            accel_y = float(data_points[2])
                            accel_z = float(data_points[3])
                            
                            # 1. Update Flex History
                            flex_history.append(current_flex)
                            if len(flex_history) > WINDOW_SIZE:
                                flex_history.pop(0) # Keep list at WINDOW_SIZE
                            
                            # 2. Calculate Direction Trend
                            trend = calculate_direction(flex_history)
                            
                            # 3. Calculate Stability
                            stability = accel_x + accel_y + accel_z
                            
                            curr_time = time.strftime("%H:%M:%S")
                            
                            # 4. Append new columns to the row
                            row = [curr_time] + data_points + [stability, trend]
                            
                            writer.writerow(row)
                            f.flush() 
                            
                            print(f"[{curr_time}] Flex: {current_flex} | Trend: {trend} | Stability: {stability:.2f}")
                            
                        except ValueError:
                            print(f"Skipping line due to non-numeric data: {line}")
                    else:
                        print(f"Malformed data received: {line}")

except KeyboardInterrupt:
    print("\nRecording stopped. File saved.")
    ser.close()
except Exception as e:
    print(f"Error: {e}")