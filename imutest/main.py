import time
from canbus import MCP2515
from machine import PWM, Pin
from udp_send import NetworkUDP
import _thread  # 用于中断中安全操作缓冲区

# 网络配置
WIFI_SSID = '5059_2.4G'
WIFI_PASSWORD = '50595059'

# PWM配置（初始不启动，等待指令）
PWM_PIN_NUM = 0
PWM_FREQUENCY = 20
PWM_DUTY = 32767  # 50%占空比（0-65535）
pwm_pin = Pin(PWM_PIN_NUM)
pwm = None

# 板载LED
led_onboard = Pin("LED", Pin.OUT)
led_onboard.value(0)

# UDP配置
UDP_TARGET_IP = '192.168.3.35'
UDP_TARGET_PORT = 12345
UDP_LOCAL_PORT = 54321

# CAN配置
can = MCP2515()
can.Init(speed="500KBPS")
can.enable_interrupt()  # 使能CAN接收中断


# 中断相关配置
CAN_INT_PIN = 21  # 假设MCP2515的INT引脚连接到GPIO2
can_int_pin = Pin(CAN_INT_PIN, Pin.IN, Pin.PULL_UP)  # 上拉输入

# 数据缓冲区（用于中断和主循环之间的数据传递）
can_data_buffer = []
buffer_lock = _thread.allocate_lock()  # 缓冲区锁，保证线程安全


def can_interrupt_handler(pin):
    """CAN中断回调函数（中断中尽量简洁）"""
    global can_data_buffer, buffer_lock
    # 读取中断数据
    data = can.check_and_clear_interrupt()
    if data:
        # 加锁保护缓冲区操作
        with buffer_lock:
            can_data_buffer.append(data)


# 配置中断触发（下降沿触发，MCP2515中断通常为低电平有效）
can_int_pin.irq(trigger=Pin.IRQ_FALLING, handler=can_interrupt_handler)


try:
    # 初始化网络
    network_udp = NetworkUDP(
        wifi_ssid=WIFI_SSID,
        wifi_password=WIFI_PASSWORD,
        target_ip=UDP_TARGET_IP,
        target_port=UDP_TARGET_PORT,
        local_port=UDP_LOCAL_PORT
    )
    network_udp.connect_wifi()

    print("等待接收 'imustart' 指令...")
    # 等待启动指令
    while True:
        recv_data = network_udp.recv()
        if recv_data == 'imustart':
            pwm = PWM(pwm_pin)
            pwm.freq(PWM_FREQUENCY)
            pwm.duty_u16(PWM_DUTY)
            led_onboard.value(1)
            break
        

    # 主循环：处理缓冲区数据并通过UDP发送
    print("开始处理CAN数据...")
    while True:
        # 检查缓冲区是否有数据
        if can_data_buffer:
            with buffer_lock:  # 加锁防止中断中修改
                data = can_data_buffer.pop(0)  # 取出最早的数据
            
            # 打印CAN ID
            #print(f"收到CAN消息 - ID: 0x{data['id']:X}, 数据: {data['data']}")
            
            # 发送数据（修改为包含ID的格式）
            data_str = f"ID:0x{data['id']:X} Data:{' '.join(map(str, data['data']))}"
            network_udp.send(data_str)

except KeyboardInterrupt:
    print('程序已停止')
except Exception as e:
    print(f'发生错误: {e}')
finally:
    if pwm:
        pwm.deinit()
    led_onboard.value(0)
    # 禁用中断
    can_int_pin.irq(handler=None)