import network
import socket
import time

class NetworkUDP:
    def __init__(self, wifi_ssid, wifi_password, target_ip, target_port, local_port):
        self.wifi_ssid = wifi_ssid
        self.wifi_password = wifi_password
        self.target_ip = target_ip
        self.target_port = target_port
        self.local_port = local_port
        self.wlan = network.WLAN(network.STA_IF)
        
    def connect_wifi(self):
        """连接到WiFi网络"""
        self.wlan.active(True)
        if not self.wlan.isconnected():
            print(f'正在连接到: {self.wifi_ssid}')
            self.wlan.connect(self.wifi_ssid, self.wifi_password)
            
            # 等待连接
            max_wait = 10
            while max_wait > 0:
                if self.wlan.status() < 0 or self.wlan.status() >= 3:
                    break
                max_wait -= 1
                print('等待连接...')
                time.sleep(1)
            
            # 检查连接状态
            if self.wlan.status() != 3:
                raise RuntimeError('WiFi连接失败')
            else:
                print('WiFi已连接')
                status = self.wlan.ifconfig()
                print(f'IP地址: {status[0]}')
        else:
            print('WiFi已连接')
            status = self.wlan.ifconfig()
            print(f'IP地址: {status[0]}')
    
    def is_wifi_connected(self):
        """检查WiFi连接状态"""
        return self.wlan.isconnected() and self.wlan.status() == 3
    
    def send(self, data):
        """通过UDP发送数据"""
        if not self.is_wifi_connected():
            raise RuntimeError('WiFi未连接，无法发送数据')
            
        # 创建UDP套接字
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.bind(('0.0.0.0', self.local_port))
        
        try:
            # 发送数据
            s.sendto(data.encode(), (self.target_ip, self.target_port))
            print(f'已发送: {data}')
        except Exception as e:
            print(f'发送失败: {e}')
        finally:
            # 关闭套接字
            s.close()
