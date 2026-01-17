import serial
import csv
import time


# Update this to match your specific port
SERIAL_PORT = "/dev/cu.usbmodem1103" 
BAUD_RATE = 115200
FILE_NAME = "arm_stability_data.csv"

try:
    # Open the serial port
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
    print(f"Connected to {SERIAL_PORT}. Press Ctrl+C to stop recording.")

    # Open the CSV file
    with open(FILE_NAME, mode='w', newline='') as f:
        writer = csv.writer(f)
        
        # Updated Header to match ALL 8 values from your C code
        header = [
            "Timestamp", 
            "Flex_Value", 
            "Accel_X", 
            "Accel_Y", 
            "Accel_Z",
            "Stability", 
            "Magnitude", 
            "Direction", 
            "Rep_Count", 
            "Beep_Freq",
            
        ]
        writer.writerow(header)

        while True:
            if ser.in_waiting > 0:
                # Read line and clean whitespace
                line = ser.readline().decode('utf-8', errors='ignore').strip()
                
                if line:
                    data_points = line.split(',')
                    
                    # CHANGED: Now expecting 8 values to match your C printf
                    if len(data_points) == 9:
                        # High-precision timestamp
                        curr_time = time.strftime("%H:%M:%S")
                        row = [curr_time] + data_points
                        
                        # Save to CSV
                        writer.writerow(row)
                        f.flush() 
                        
                        # Monitor output: focus on stability and reps
                        # data_points[1,2,3] are your X, Y, Z values
                        print(f"[{curr_time}] X:{data_points[1]} Y:{data_points[2]} Z:{data_points[3]} | Total Stability: {data_points[4]}")
                    else:
                        # This avoids crashing when the Nucleo sends a partial line during a beep
                        pass 

except KeyboardInterrupt:
    print("\nRecording stopped. File saved.")
    ser.close()
except Exception as e:
    print(f"Error: {e}")