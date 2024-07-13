import math
from math import floor
from rplidar import RPLidar

lidar = RPLidar('COM3')
scan_data = [0]*360
max_dist = 4000
angle_min = 0

try:
    for scan in lidar.iter_scans():
        max_dist = 4000
        angle_min = 0
        for (_, angle, distance) in scan:
            xx = min(359, floor(angle))
            scan_data[xx] = distance
            # if distance < max_dist:
            #     max_dist = distance
            if scan_data[xx] != 0:
                if scan_data[xx] < max_dist:
                    max_dist = scan_data[xx]
                    angle_min = xx
                    # if ((315 <= xx <= 360) or (0 <= xx <= 45)):
                    #     real_dist = (max_dist) * (math.cos(math.radians(angle_min)))
                    #     print('\nreal_dis: ', real_dist, ' | lidar_dis:', max_dist, ' | angle: ', angle_min) 
                        # print (angle_min)

                    # index = int(angle_min/5)                
        # print (scan_data)
        print('\ndis: ', max_dist, ' |  angle: ', angle_min)

    # min(scan_data)
except KeyboardInterrupt:print('Stoping.')

lidar.stop()
lidar.stop_motor()
lidar.disconnect()

