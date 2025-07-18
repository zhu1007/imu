# network_utils.py
import network
import socket
import time

# WiFi配置
WIFI_SSID = "5059_2.4G"
WIFI_PASSWORD = "50595059"

# 服务器配置
SERVER_PORT = 8080  # TCP端口号

def connect_wifi(led):
    """连接WiFi"""
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    
    # 如果之前已连接，先断开
    if wlan.isconnected():
        wlan.disconnect()
        time.sleep(1)
    
    print(f"正在连接WiFi: {WIFI_SSID}")
    wlan.connect(WIFI_SSID, WIFI_PASSWORD)
    
    # 等待连接（最长30秒）
    max_wait = 30
    while max_wait > 0:
        if wlan.isconnected():
            break
        max_wait -= 1
        print('.', end='')
        time.sleep(0.5)
    
    if wlan.isconnected():
        print("\nWiFi连接成功!")
        ip = wlan.ifconfig()[0]
        print(f"IP地址: {ip}")
        blink_led(led, 3)  # 成功提示
        return wlan, ip
    else:
        print("\nWiFi连接失败! 状态码:", wlan.status())
        blink_led(led, 5)  # 错误提示
        return None, None

def disconnect_wifi(wlan):
    """断开WiFi连接"""
    if wlan and wlan.isconnected():
        wlan.disconnect()
        wlan.active(False)

def start_server(ip):
    """启动TCP服务器"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_address = (ip, SERVER_PORT)
    sock.bind(server_address)
    sock.listen(1)
    print(f"服务器已启动，监听 {ip}:{SERVER_PORT}")
    return sock

def run_network_service(led, data_generator=None):
    """运行网络服务，接收数据生成函数作为参数"""
    wlan = None
    
    try:
        # 连接WiFi
        wlan, ip = connect_wifi(led)
        if not wlan or not ip:
            print("WiFi连接失败，程序终止")
            return
        
        # 启动服务器
        server_sock = start_server(ip)
        
        client_sock = None
        
        try:
            while True:
                # 等待客户端连接
                if client_sock is None:
                    print("等待客户端连接...")
                    client_sock, client_addr = server_sock.accept()
                    print(f"客户端已连接: {client_addr}")
                    blink_led(led, 5, 0.1)
                
                # 数据发送循环
                try:
                    counter = 0
                    while True:
                        # 使用传入的函数生成数据，默认为内置格式
                        if data_generator:
                            message = data_generator(counter)
                        else:
                            message = f"默认数据包 #{counter}\n时间戳: {time.ticks_ms()} ms\n"
                        
                        # 尝试发送数据
                        client_sock.send(message.encode('utf-8'))
                        print(f"已发送数据包 #{counter}")
                        
                        # LED指示发送
                        led.on()
                        time.sleep(0.05)
                        led.off()
                        
                        counter += 1
                        time.sleep(1)  # 每秒发送一次
                
                except OSError as e:
                    print(f"发送错误: {e}")
                    client_sock.close()
                    client_sock = None
                    print("等待新的客户端连接...")
        
        finally:
            if client_sock:
                client_sock.close()
            server_sock.close()
            print("服务器已关闭")
    
    finally:
        disconnect_wifi(wlan)
        print("WiFi已断开")

def blink_led(led, times, delay=0.2):
    """LED闪烁指示状态"""
    for _ in range(times):
        led.on()
        time.sleep(delay)
        led.off()
        time.sleep(delay)