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
        
        # Header matching your C code output
        # sFlex, sX, sY, sZ, movement_intensity, dir
        header = ["Timestamp", "Flex_Value", "Accel_X", "Accel_Y", "Accel_Z", "Intensity", "Direction", "Stability"]
        writer.writerow(header)

        while True:
            if ser.in_waiting > 0:
                # Read line and clean whitespace
                line = ser.readline().decode('utf-8', errors='ignore').strip()
                
                if line:
                    data_points = line.split(',')
                    
                    # Verify we received all 6 expected values
                    if len(data_points) == 6:
                        try:
                            accel_x = float(data_points[1])
                            accel_y = float(data_points[2])
                            accel_z = float(data_points[3])
                            stabilty = accel_x+ accel_y + accel_z
                        except ValueError:
                            stabilty = 0.0
                        # Add a timestamp for time-series analysis
                        curr_time = time.strftime("%H:%M:%S")
                        row = [curr_time] + data_points + [stabilty]
                        
                        # Save to CSV
                        writer.writerow(row)
                        f.flush() 
                        
                        # Print to terminal for real-time monitoring
                        print(f"[{curr_time}] X:{data_points[1]} Y:{data_points[2]} Z:{data_points[3]} | {data_points[5]}")
                    else:
                        # Log if a line was corrupted or incomplete
                        print(f"Malformed data received: {line}")

except KeyboardInterrupt:
    print("\nRecording stopped. File saved.")
    ser.close()
except Exception as e:
    print(f"Error: {e}")