# 是否开启功能
enable_cpu = True
enable_net = True
enable_srsran = True
enable_pqos = True


# 特殊用途的核心从末尾开始分配
core_bind_dict = {
    'monitor_cpu_usage': 19,
    'monitor_llc_and_bandwidth': 19,
    'srsran_metrics': 18,
    'net_monitor': 17
}


# 网卡名
nic_name = 'eno1'

# 数据保留到小数点后几位
decimal_place = 2

# 输出csv的路径
log_dir = './logs/'


# 运行时间
running_time = None
