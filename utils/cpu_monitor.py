import psutil
import csv
import os
import time
import config

def get_average_cpu_usage():
    return psutil.cpu_percent(0)


def get_cpu_usage_per_core():
    return psutil.cpu_percent(percpu=True)

def get_mem_usage(decimal_place=config.decimal_place):
    mem_used = psutil.virtual_memory().used /1024 / 1024 /1024
    mem_used = round(mem_used, decimal_place)
    return mem_used

def ge_mem_percent():
    return psutil.virtual_memory().percent

def record_cpu_usage(log_dir, stop_event, cpu_core=None, interval=1.0):
    
    # 绑定进程到特定的CPU核心
    if cpu_core:
        p = psutil.Process()
        p.cpu_affinity([cpu_core])
    
    print(f"CPU monitoring process is running on core {cpu_core}.")
    
    
    log_filename = os.path.join(log_dir, 'cpu_usage.csv')
    with open(log_filename, mode='w', newline='') as log_file:
        
        log_writer = csv.writer(log_file)
        headers = ['timestamp'] + [f'cpu_{i}' for i in range(psutil.cpu_count())] + ['mem usage (GB)']
        log_writer.writerow(headers)
        
        while not stop_event.is_set():
            try:
                timestamp = time.time()
                cpu_percentages = psutil.cpu_percent(percpu=True)
                worker_core_usage = [
                    cpu_percentages[core] for core in range(psutil.cpu_count())
                ]
                data_line= [timestamp] + worker_core_usage + [get_mem_usage()]
                # print(data_line)
                log_writer.writerow(data_line)
                # log_file.flush()
                time.sleep(interval)
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"Error during monitoring: {e}")
                break
        log_file.flush()
        print("CPU monitoring process is shutting down.")
