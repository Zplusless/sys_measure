import time, datetime
import psutil
import csv
import config
import socket

# 最后的1表示第2个网卡，如果网速显示不正常，可以尝试变化一下数字，一般是1
# key = list(psutil.net_io_counters(pernic=True).keys())[1]
# print(key)




class Measure:
    def __init__(self, nic, ) -> None:
        
        self.t_p= None
        self.t_n = None
        self.data = [['time', 'net_in(kbps)', 'net_out(kbps)', "MEM(MB)", "MEM%", "CPU%", 'CPU_freq(MHz)']]

        # 网卡状态
        self.nic_name = nic
        self.in_old = None
        self.out_old = None
        self.in_new = None
        self.out_new = None

        self.renew_nic_state()

    
    def milisecond(self, t):
        return datetime.datetime.fromtimestamp(t).strftime("%H:%M:%S.%f")

    def renew_nic_state(self):

        # if not self.t_n:
        #     self.in_new = psutil.net_io_counters(pernic=True).get(self.nic_name).bytes_recv
        #     self.out_new = psutil.net_io_counters(pernic=True).get(self.nic_name).bytes_sent  
        #     self.t_n=time.time()  
        # else:
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
        
        # net_in = str(net_in).split('.')[0] + '.' + str(net_in).split('.')[1][:decimal_place]
        # net_out = str(net_out).split('.')[0] + '.' + str(net_out).split('.')[1][:decimal_place]
        net_in = round(net_in, decimal_place)
        net_out = round(net_out, decimal_place)

        # memory ---> MB
        mem_used = psutil.virtual_memory().used /1024 / 1024 
        mem_used = round(mem_used, decimal_place)

        mem_percent = psutil.virtual_memory().percent

        # CPU
        cpu_percent = psutil.cpu_percent(0)
        cpu_freq = psutil.cpu_freq()[0]

        return self.milisecond(self.t_n), net_in, net_out, mem_used, mem_percent, cpu_percent, cpu_freq


    def task(self):
        while self.run:
            # print(f"{psutil.cpu_percent(0)},{psutil.virtual_memory().percent},{milisecond(time.time())}")
            # log = [psutil.cpu_percent(0), psutil.virtual_memory().percent, psutil.virtual_memory().used, milisecond(time.time())]
            time.sleep(1)
            self.renew_nic_state()
            self.record()

    def record(self):
        ans = self.get_state()
        self.data.append(ans)


    def write_data(self):
        with open(config.csv_dir+f'overhead_measurement_{socket.gethostname()}_{self.milisecond(time.time())[:8]}.csv'.replace(':','-'), 'w') as f:
            wtr = csv.writer(f)
            wtr.writerows(self.data)

    def init(self): 
        # self.id = log_id
        self.run = True
        self.data = [['time', 'net_in(kB)', 'net_out(kB)', "MEM(MB)", "MEM%", "CPU%", 'CPU_freq(Hz)']]
        return 0

    def insert_mark(self, msg):
        self.data.append([self.milisecond(time.time()), msg, "================================================"])
        return 0
    
    def end(self):
        self.run = False
        time.sleep(1.5) # 让while循环的数据全部写入list
        return 0

if __name__ == "__main__":
    nm = Measure(config.nic_name)
    try:
        while 1:
            time.sleep(1)
            nm.renew_nic_state()
            nm.record()
            ans = nm.get_state()
            
            # print(f'{ans[0]}:  net_in:{ans[1]}   net_out:{ans[2]}   mem: {ans[3]}({ans[4]})   cpu: {ans[5]}--{ans[6][0]}Hz')
            print(ans)
    except KeyboardInterrupt:
        nm.write_data()
        print('end!')
