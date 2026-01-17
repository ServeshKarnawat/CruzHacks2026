import serial
import csv
import time

# Configuration
SERIAL_PORT = "/dev/cu.usbmodem1103" 
BAUD_RATE = 115200
FILE_NAME = "arm_stability_data.csv"

# --- DIRECTION & REP SETTINGS ---
WINDOW_SIZE = 5         
STABILITY_THRESHOLD = 2.0  
flex_history = [] 

# --- NEW TRACKING VARIABLES ---
rep_count = 0
last_confirmed_direction = "STABLE" # Tracks the previous significant state

def calculate_direction(history):
    if len(history) < WINDOW_SIZE:
        return "INITIALIZING"
    
    total_change = history[-1] - history[0]
    is_up = all(history[i] >= history[i-1] for i in range(1, len(history)))
    if is_up and total_change >= STABILITY_THRESHOLD:
        return "UP"
    
    is_down = all(history[i] <= history[i-1] for i in range(1, len(history)))
    if is_down and abs(total_change) >= STABILITY_THRESHOLD:
        return "DOWN"
    
    return "STABLE"

try:
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
    print(f"Connected to {SERIAL_PORT}. Press Ctrl+C to stop recording.")

    with open(FILE_NAME, mode='w', newline='') as f:
        writer = csv.writer(f)
        
        # Added "Rep_Count" to the header
        header = ["Timestamp", "Flex_Value", "Accel_X", "Accel_Y", "Accel_Z", 
                  "Intensity", "Direction", "Stability", "Trend_Direction", "Rep_Count"]
        writer.writerow(header)

    with open(FILE_NAME, mode='a', newline='') as f: # Re-open in append mode for loop
        writer = csv.writer(f)
        while True:
            if ser.in_waiting > 0:
                line = ser.readline().decode('utf-8', errors='ignore').strip()
                if line:
                    data_points = line.split(',')
                    if len(data_points) == 6:
                        try:
                            current_flex = float(data_points[0])
                            
                            # 1. Update history and get current trend
                            flex_history.append(current_flex)
                            if len(flex_history) > WINDOW_SIZE:
                                flex_history.pop(0)
                            
                            current_trend = calculate_direction(flex_history)
                            
                            # 2. REP COUNTER LOGIC
                            # If we were going UP and now we are going DOWN, that's one rep
                            if last_confirmed_direction == "UP" and current_trend == "DOWN":
                                rep_count += 1
                                last_confirmed_direction = "DOWN"
                            # If we were going DOWN and now we are going UP, that's another rep
                            elif last_confirmed_direction == "DOWN" and current_trend == "UP":
                                rep_count += 1
                                last_confirmed_direction = "UP"
                            # Initialize the first direction found
                            elif last_confirmed_direction == "STABLE" and current_trend in ["UP", "DOWN"]:
                                last_confirmed_direction = current_trend

                            # 3. Calculate Stability
                            stability = float(data_points[1]) + float(data_points[2]) + float(data_points[3])
                            curr_time = time.strftime("%H:%M:%S")
                            
                            # 4. Save and Print
                            row = [curr_time] + data_points + [stability, current_trend, rep_count]
                            writer.writerow(row)
                            f.flush() 
                            
                            print(f"[{curr_time}] Trend: {current_trend:8} | Reps: {rep_count} | Stab: {stability:.2f}")
                            
                        except ValueError:
                            continue

except KeyboardInterrupt:
    print(f"\nRecording stopped. Final Rep Count: {rep_count}")
    ser.close()