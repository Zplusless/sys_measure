import time, datetime
import psutil
import csv
import config
import socket
import os

# 最后的1表示第2个网卡，如果网速显示不正常，可以尝试变化一下数字，一般是1
# key = list(psutil.net_io_counters(pernic=True).keys())[1]
# print(key)




class Measure:
    def __init__(self, nic, ) -> None:
        
        self.t_p= None
        self.t_n = None
        self.data = None

        # 网卡状态
        self.nic_name = nic
        self.in_old = None
        self.out_old = None
        self.in_new = None
        self.out_new = None

        
        self.init()


    def init(self): 
        # self.id = log_id
        self.data = [['time', 'net_in(kbps)', 'net_out(kbps)']]
        self.renew_nic_state()
        return 0
    
    def start_measure(self, stop_event, log_dir, cpu_core=None,interval=1):

        if cpu_core:
            p = psutil.Process()
            p.cpu_affinity([cpu_core])

        print(f"net monitor is running on core {cpu_core}.")

        self.init()
        log = os.path.join(log_dir, 'net_usage.csv')
        try:
            while not stop_event.is_set():
                time.sleep(interval)
                self.renew_nic_state()
                self.record()
        except KeyboardInterrupt:
            pass
        except Exception as e:
            print(e)
        finally:
            self.write_data(log)
            print('net monitor is shutting down.')



    def milisecond(self, t):
        return datetime.datetime.fromtimestamp(t).strftime("%H:%M:%S.%f")

    def renew_nic_state(self):

        self.in_old = self.in_new
        self.out_old =  self.out_new 
        self.t_p=self.t_n

        self.in_new = psutil.net_io_counters(pernic=True).get(self.nic_name).bytes_recv
        self.out_new = psutil.net_io_counters(pernic=True).get(self.nic_name).bytes_sent  
        self.t_n=time.time()  
    
    def get_state(self, decimal_place=config.decimal_place):
        # log = [psutil.cpu_percent(0), psutil.virtual_memory().percent, psutil.virtual_memory().used, milisecond(time.time())]
        assert self.t_n, self.t_p

        # network --->kbps
        net_in = (self.in_new - self.in_old) /(self.t_n-self.t_p) / 1024 *8
        net_out = (self.out_new - self.out_old) /(self.t_n-self.t_p) / 1024 *8
        
        net_in = round(net_in, decimal_place)
        net_out = round(net_out, decimal_place)

        return self.milisecond(self.t_n), net_in, net_out, 



    def record(self):
        ans = self.get_state()
        self.data.append(ans)

    def write_data(self, log):

        with open(log, 'w') as f:
            wtr = csv.writer(f)
            wtr.writerows(self.data)



    def insert_mark(self, msg):
        self.data.append([self.milisecond(time.time()), msg, "================================================"])
        return 0
    

if __name__ == "__main__":
    nm = Measure(config.nic_name)
    try:
        while 1:
            time.sleep(1)
            nm.renew_nic_state()
            nm.record()
            ans = nm.get_state()

            print(ans)
    except KeyboardInterrupt:
        nm.write_data()
        print('end!')
