import time
from canbus import MCP2515
from machine import PWM, Pin
from udp_send import NetworkUDP
# 网络配置
WIFI_SSID = '5059_2.4G'
WIFI_PASSWORD = '50595059'

# PWM配置（初始不启动，等待指令）
PWM_PIN_NUM = 1
PWM_FREQUENCY = 100
PWM_DUTY = 32767  # 50%占空比（0-65535）
pwm_pin = Pin(PWM_PIN_NUM)  # 先初始化引脚，不启动PWM
pwm = None  # PWM对象将在收到指令后创建

# 板载LED（用于指示状态）
led_onboard = Pin("LED", Pin.OUT)
led_onboard.value(0)  # 初始熄灭

# UDP配置
UDP_TARGET_IP = '192.168.3.35'
UDP_TARGET_PORT = 12345
UDP_LOCAL_PORT = 54321

# CAN配置
can = MCP2515()
can.Init(speed="125KBPS")
can_id = 0x01

try:
    # 初始化网络和UDP（包含收发功能）
    network_udp = NetworkUDP(
        wifi_ssid=WIFI_SSID,
        wifi_password=WIFI_PASSWORD,
        target_ip=UDP_TARGET_IP,
        target_port=UDP_TARGET_PORT,
        local_port=UDP_LOCAL_PORT
    )
    network_udp.connect_wifi()

    print("等待接收 'imustart' 指令...")
    # 等待启动指令阶段
    while True:
        # 检查是否收到UDP指令
        recv_data = network_udp.recv()
        if recv_data == 'imustart':
            # 启动PWM
            pwm = PWM(pwm_pin)
            pwm.freq(PWM_FREQUENCY)
            pwm.duty_u16(PWM_DUTY)
            # 点亮LED表示启动成功
            led_onboard.value(1)
            break
        time.sleep(0.01)  # 短延时，降低CPU占用

    # 持续接收CAN数据并通过UDP发送
    print("开始接收CAN数据...")
    while True:
        # 接收CAN数据（非阻塞，无数据时返回空列表）
        can_data = can.Receive(can_id)
        # 有数据则发送
        if can_data:
            data_str = ' '.join(map(str, can_data))
            network_udp.send(data_str)
            print(f"已发送CAN数据: {data_str}")
        # 无数据时短暂延时，避免空循环占用过高CPU
        else:
            time.sleep(0.01)

except KeyboardInterrupt:
    print('程序已停止')
except Exception as e:
    print(f'发生错误: {e}')
finally:
    # 清理资源
    if pwm:
        pwm.deinit()  # 关闭PWM
    led_onboard.value(0)  # 熄灭LED