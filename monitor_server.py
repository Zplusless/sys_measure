import cv2
import socket
import struct
import pickle
import mediapipe as mp
import time
import numpy as np
from multiprocessing import Process, Value, Lock, Manager, Event
import csv
import os
import psutil
import argparse

import config




# 使用共享变量和锁来确保进程安全地更新进程计数器
process_counter = Value('i', 0)
lock = Lock()



def main(log_dir='./logs', running_time=None, core_bind_dict=None):

    try:
        # 确保日志目录存在
        os.makedirs(log_dir, exist_ok=True)

        processes = []
        stop_event = Event()

        # 启动CPU利用率监控进程
        if config.enable_cpu:
            from utils.cpu_monitor import record_cpu_usage
            cpu_core = core_bind_dict.get('monitor_cpu_usage', None)
            monitor_process = Process(target=record_cpu_usage, args=(log_dir, stop_event, cpu_core,))
            monitor_process.start()
            processes.append(monitor_process)

        # 启动LLC和内存带宽监控进程
        if config.enable_pqos:
            from utils.pqos_monitor import monitor_pqos_by_core
            cpu_core = core_bind_dict.get('monitor_llc_and_bandwidth', None)
            llc_bw_monitor_process = Process(target=monitor_pqos_by_core, args=(log_dir,stop_event, cpu_core,))
            llc_bw_monitor_process.start()
            processes.append(llc_bw_monitor_process)

        # 启动srsran metrics记录进程
        if config.enable_srsran:
            from utils.srsran_metrics import record_srsran_metrics
            cpu_core = core_bind_dict.get('srsran_metrics', None)
            srsran_metrice_process = Process(target=record_srsran_metrics, args=(stop_event,"127.0.0.1", 55555, cpu_core))
            srsran_metrice_process.start()
            processes.append(srsran_metrice_process)


        # 网速监控
        if config.enable_net:
            from utils.net_monitor import Measure
            cpu_core = core_bind_dict.get('net_monitor', None)
            mn = Measure(config.nic_name)
            net_monitor_process = Process(target=mn.start_measure, args=(stop_event, log_dir, cpu_core,))
            net_monitor_process.start()
            processes.append(net_monitor_process)


        if running_time is not None:
            while running_time>0:
                time.sleep(1)
                print(f"Monitor server will shut down after {running_time} seconds.")
                running_time -= 1

            raise KeyboardInterrupt
        else:
            time_consumed = 0
            while True:
                time.sleep(1)
                time_consumed += 1
                if time_consumed%5==0:
                    print(f"Monitor server has been running for {time_consumed} seconds.")
            

    except KeyboardInterrupt:
        print("Server is shutting down.")
    finally:
        stop_event.set()
        # 终止所有子进程
        for p in processes:
            # p.terminate()
            p.join()

        print("All processes are terminated.")

if __name__ == '__main__':


    import os 
    if os.getuid() != 0:
        raise Exception("Please run this script as root.")
        # exit(1)

    main(log_dir=config.log_dir, running_time=config.running_time,  core_bind_dict=config.core_bind_dict)
