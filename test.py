import psutil
import time

for i in range(20):
    print(f"usage:{psutil.cpu_percent()}--->time percent:{psutil.cpu_times_percent()}--->diff:{psutil.cpu_percent()-psutil.cpu_times_percent()[0]-psutil.cpu_times_percent()[1]}")

    time.sleep(1)