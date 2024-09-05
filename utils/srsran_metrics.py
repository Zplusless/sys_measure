import socket
import json
import psutil
import os

def record_srsran_metrics(stop_event=None, UDP_IP="127.0.0.1", UDP_PORT=55555, cpu_core=None):
    # 绑定进程到特定的CPU核心
    if cpu_core:
        p = psutil.Process()
        p.cpu_affinity([cpu_core])

    print(f"srsRAN metrics process is running on core {cpu_core}.")

    # Create a UDP socket
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        # Bind the socket to the IP address and port
        sock.bind((UDP_IP, UDP_PORT))
        # Set the socket to non-blocking mode
        sock.settimeout(1)

        print("UDP Receiver started...")

        # Initialize a list to store received JSON data
        received_json_list = []

        while_flag = True
        try:
            while while_flag:
                if stop_event:
                    while_flag = not stop_event.is_set()
                try:
                    # Receive message from the sender
                    data, addr = sock.recvfrom(1024)
                
                    # Decode the received message as JSON
                    json_data = json.loads(data.decode('utf-8'))
                    # Print the received JSON data
                    print("Received JSON:", json_data)
                    # Append the received JSON data to the list
                    received_json_list.append(json_data)
                except json.JSONDecodeError:
                    print("Received data is not in JSON format:", data.decode('utf-8'))
                except socket.timeout:
                    continue
        except KeyboardInterrupt:
            print('exit with ctrl-c')
        finally:
            # Save the list of received JSON data to a file when Ctrl+C is pressed  
            os.makedirs('logs', exist_ok=True)
            with open('logs/srsran_metrics_data.json', 'w') as file:
                json.dump(received_json_list, file, indent=4)
            print("srsRAN METRICS: Data saved to 'logs/srsran_metrics_data.json'. Exiting...")      
            return 0


if __name__ == '__main__':
    record_srsran_metrics(UDP_IP="127.0.0.1", UDP_PORT=55555, cpu_core=0)