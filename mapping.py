import math
from math import floor
from rplidar import RPLidar
import mqtt_publisher   

lidar = RPLidar('/dev/serial/by-id/usb-Silicon_Labs_CP2102_USB_to_UART_Bridge_Controller_0001-if00-port0')
scan_data = [0] * 360

# Initialize lists to store data for each part
data_front = []
data_fl = []
data_fr = []
data_left = []
data_right = []

buffer = 0

# Function to classify the angle and store the distance in the respective list
def classify_and_store(angle, distance):
    if (331 <= angle <= 360) or (0 <= angle <= 30):
        data_front.append(distance)
    elif 301 <= angle <= 330:
        data_fl.append(distance)
    elif 31 <= angle <= 60:
        data_fr.append(distance)
    elif 270 <= angle <= 300:
        data_left.append(distance)
    elif 61 <= angle <= 90:
        data_right.append(distance)

# Function to determine xx and yy based on distance thresholds
def determine_values(distance):
    if distance <= 500:
        return "01"
    elif 500 < distance <= 1000:
        return "02"
    elif 1000 < distance <= 1500:
        return "03"
    elif 1500 < distance <= 2000:
        return "04"
    else:
        return "00"

# Function to create the data string based on the side and distance
def create_data_string(side, min_distance):
    t = ""
    xx = ""
    yy = ""

    if side == "Front":
        t = "P"
        xx = "00"
        yy = determine_values(min_distance)
    elif side == "Front Left":
        t = "N"
        xx = determine_values(min_distance)
        yy = determine_values(min_distance)
    elif side == "Front Right":
        t = "P"
        xx = determine_values(min_distance)
        yy = determine_values(min_distance)
    elif side == "Left":
        t = "N"
        xx = determine_values(min_distance)
        yy = "00"
    elif side == "Right":
        t = "P"
        xx = determine_values(min_distance)
        yy = "00"

    return f"A55A21010{t}{xx}P{yy}"

# Function to create the data string based on the side and distance
def create_data_coordinate(side, min_distance):
    t = ""
    xx = ""
    yy = ""

    if side == "Front":
        t = "P"
        xx = "00"
        yy = determine_values(min_distance)
    elif side == "Front Left":
        t = "N"
        xx = determine_values(min_distance)
        yy = determine_values(min_distance)
    elif side == "Front Right":
        t = "P"
        xx = determine_values(min_distance)
        yy = determine_values(min_distance)
    elif side == "Left":
        t = "N"
        xx = determine_values(min_distance)
        yy = "00"
    elif side == "Right":
        t = "P"
        xx = determine_values(min_distance)
        yy = "00"

    return f"{t}{xx}P{yy}"



try:
    client = mqtt_publisher.connect_mqtt()
    for scan in lidar.iter_scans():
        # Clear lists for new scan data
        data_front.clear()
        data_fl.clear()
        data_fr.clear()
        data_left.clear()
        data_right.clear()

        for (_, angle, distance) in scan:
            xx = min(359, floor(angle))
            scan_data[xx] = distance

            # Classify and store distance in respective list
            classify_and_store(xx, distance)

        # Combine all data into one list
        all_data = [data_front, data_fl, data_fr, data_left, data_right]
        all_sides = ["Front", "Front Left", "Front Right", "Left", "Right"]
        data_strings = []

        # Check each list and create data string based on distance
        for data, side in zip(all_data, all_sides):
            if data:  # Check if the list is not empty
                min_distance = min(data)
                data_string = create_data_coordinate(side, min_distance)
                data_strings.append(data_string)
            # else:
                # data_strings.append(None)

        # Print all data strings
        # print('Data strings:', data_strings)

        # Send Every 1 sec
        if(buffer > 10):
            print('Data strings:', f"A55A230{len(data_strings)}0{''.join(data_strings)}")
            mqtt_publisher.publish(client,f"A55A230{len(data_strings)}0{''.join(data_strings)}")
            buffer = 0
        else:
            buffer = buffer + 1

except KeyboardInterrupt:
    print('Stopping.')

lidar.stop()
lidar.stop_motor()
lidar.disconnect()
