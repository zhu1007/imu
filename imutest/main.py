import time
from  canbus import MCP2515
from machine import PWM,Pin
import udp_send

# 网络配置
WIFI_SSID = '5059_2.4G'
WIFI_PASSWORD = '50595059'

# PWM波
pwm_pin = PWM(Pin(1))
frequency = 100
pwm_pin.freq(frequency)
duty_cycle = 32767
pwm_pin.duty_u16(duty_cycle)

# UDP配置
UDP_TARGET_IP = '192.168.3.35'  # 目标IP地址
UDP_TARGET_PORT = 12345          # 目标端口
UDP_LOCAL_PORT = 54321           # 本地端口

# CAN配置
can = MCP2515()
can.Init(speed="125KBPS")
can_id = 0x01

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

    print("开始接收CAN总线数据并通过UDP发送...")
    while True:
        # 接收CAN总线数据
        can_data = can.Receive(can_id)

        # 将接收到的CAN数据转换为字符串，以便通过UDP发送
        data_str = ' '.join(map(str, can_data))

        if data_str:
            # 发送接收到的CAN数据
            network_udp.send(data_str)
            print(f"已发送CAN数据: {data_str}")
        else:
            print("未接收到CAN数据")

        time.sleep(1)  # 每秒检查一次

except KeyboardInterrupt:
    print('程序已停止')
except Exception as e:
    print(f'发生错误: {e}')
