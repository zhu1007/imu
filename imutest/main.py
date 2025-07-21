import time
import udp_send

# 网络配置
WIFI_SSID = '5059_2.4G'
WIFI_PASSWORD = '50595059'

# UDP配置
UDP_TARGET_IP = '192.168.3.35'  # 目标IP地址
UDP_TARGET_PORT = 12345          # 目标端口
UDP_LOCAL_PORT = 54321           # 本地端口

try:
    # 初始化网络和UDP发送器
    network_udp = udp_send.NetworkUDP(
        wifi_ssid=WIFI_SSID,
        wifi_password=WIFI_PASSWORD,
        target_ip=UDP_TARGET_IP,
        target_port=UDP_TARGET_PORT,
        local_port=UDP_LOCAL_PORT
    )
    
    # 连接WiFi
    network_udp.connect_wifi()
    
    # 发送测试数据
    while True:
        # 这里定义要发送的数据
        message = f'Hello from Raspberry Pi Pico! Time: {time.time()}'
        network_udp.send(message)
        time.sleep(2)  # 每2秒发送一次
        
except KeyboardInterrupt:
    print('程序已停止')
except Exception as e:
    print(f'发生错误: {e}')
