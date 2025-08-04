import time
from canbus import MCP2515
from machine import PWM, Pin
import udp_send

# 全局变量：用于中断与主循环的数据传递
can_data = None  # 存储接收到的CAN数据
data_ready = False  # 数据就绪标志位

# 网络配置
WIFI_SSID = '5059_2.4G'
WIFI_PASSWORD = '50595059'

# PWM波
pwm_pin = PWM(Pin(1))
frequency = 100
pwm_pin.freq(frequency)
duty_cycle = 32767
pwm_pin.duty_u16(duty_cycle)
led_onboard = machine.Pin("LED", machine.Pin.OUT)

# UDP配置
UDP_TARGET_IP = '192.168.3.35'
UDP_TARGET_PORT = 12345
UDP_LOCAL_PORT = 54321

# CAN配置
can = MCP2515()
can.Init(speed="125KBPS")
can_id = 0x01

# 中断引脚配置（MCP2515的INT引脚连接到开发板的Pin(2)，可根据实际修改）
int_pin = Pin(21, Pin.IN, Pin.PULL_UP)  # 上拉输入，确保空闲时为高电平


def can_interrupt_handler(pin):
    """中断服务函数：读取CAN数据并设置标志位"""
    global can_data, data_ready
    try:
        # 读取CAN数据（注意：需确保can.Receive非阻塞，见canbus.py修改说明）
        can_data = can.Receive(can_id)
        if can_data:
            data_ready = True  # 标记数据就绪
    except Exception as e:
        print(f"中断处理错误: {e}")


# 绑定中断：下降沿触发（MCP2515中断时INT引脚拉低）
int_pin.irq(trigger=Pin.IRQ_FALLING, handler=can_interrupt_handler)

led_onboard.value(1)  # 点亮LED

try:
    # 初始化网络和UDP发送器
    network_udp = udp_send.NetworkUDP(
        wifi_ssid=WIFI_SSID,
        wifi_password=WIFI_PASSWORD,
        target_ip=UDP_TARGET_IP,
        target_port=UDP_TARGET_PORT,
        local_port=UDP_LOCAL_PORT
    )
    network_udp.connect_wifi()

    print("开始通过中断接收CAN数据并通过UDP发送...")
    while True:
        if data_ready:
            # 将接收到的CAN数据转换为字符串并发送
            data_str = ' '.join(map(str, can_data))
            network_udp.send(data_str)
            print(f"已发送CAN数据: {data_str}")
            # 重置标志位
            data_ready = False


except KeyboardInterrupt:
    print('程序已停止')
except Exception as e:
    print(f'发生错误: {e}')
finally:
    # 关闭中断（可选）
    int_pin.irq(handler=None)