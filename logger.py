import serial
import csv
import time

# Update this to match your port from earlier
SERIAL_PORT = "/dev/cu.usbmodem1103" 
BAUD_RATE = 115200
FILE_NAME = "flex_sensor_data.csv"

try:
    # Open the serial port
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
    print(f"Connected to {SERIAL_PORT}. Press Ctrl+C to stop recording.")

    # Open (or create) the CSV file
    with open(FILE_NAME, mode='w', newline='') as f:
        writer = csv.writer(f)
        
        # Write the header row
        writer.writerow(["Timestamp", "Raw_ADC", "Filtered_ADC", "Angle"])

        while True:
            if ser.in_waiting > 0:
                # Read a line from the Nucleo
                line = ser.readline().decode('utf-8').strip()
                
                if line:
                    # Split the comma-separated string from your C code
                    data_points = line.split(',')
                    
                    # Add a timestamp so you can graph it over time
                    row = [time.strftime("%H:%M:%S")] + data_points
                    
                    # Write to file and "flush" (saves immediately)
                    writer.writerow(row)
                    f.flush() 
                    
                    print(f"Logged: {row}")

except KeyboardInterrupt:
    print("\nRecording stopped. File saved.")
    ser.close()
except Exception as e:
    print(f"Error: {e}")