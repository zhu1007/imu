import time
import micropython
from canbus import MCP2515, CANINTF, RX0IF_SET, RX1IF_SET, RXB0CTRL
from machine import PWM, Pin
from udp_send import NetworkUDP
import _thread
import ujson as json

# ========= 常量/配置 =========
WIFI_SSID = "HUAWEI-5079"
WIFI_PASSWORD = "wifimima_5079"

PWM_PIN_NUM = 0
PWM_FREQUENCY = 20
PWM_DUTY = 32767  # 50%

UDP_TARGET_IP = "192.168.3.230"
UDP_TARGET_PORT = 12345
UDP_LOCAL_PORT = 54321

CAN_INT_PIN = 21

# 状态机（用 int 替代字符串）
ST_IDLE = 0
ST_COLLECTING = 1
ST_READY = 2

IMU_COUNT = 4
IMU_IDS = (0, 1, 2, 3)

# ID → 索引映射 (0x10/0x20/0x30/0x40)
ID_TO_IDX = {
    0x10: 0,
    0x20: 1,
    0x30: 2,
    0x40: 3,
}

ALL_MASK = 0b1111  # 四个 IMU 全到齐时

# 分配中断异常缓冲
micropython.alloc_emergency_exception_buf(100)

# ========= 外设 =========
pwm_pin = Pin(PWM_PIN_NUM)
pwm = None

led_onboard = Pin("LED", Pin.OUT)
led_onboard.value(0)

can = MCP2515()
can.Init(speed="500KBPS")
#can.enable_interrupt()

can_int_pin = Pin(CAN_INT_PIN, Pin.IN, Pin.PULL_UP)

# ========= 全局缓冲 =========
msgBuffer = []
imu_raw = [bytearray(8) for _ in range(IMU_COUNT)]
have_mask = 0
state = ST_IDLE
frameID = 0
buffer_lock = _thread.allocate_lock()


# ========= Viper 四元数解码 =========
@micropython.viper
def decode_quat_viper(data: ptr8):
    q0 = int(data[0]) | (int(data[1]) << 8)
    q1 = int(data[2]) | (int(data[3]) << 8)
    q2 = int(data[4]) | (int(data[5]) << 8)
    q3 = int(data[6]) | (int(data[7]) << 8)

    if q0 >= 32768:
        q0 -= 65536
    if q1 >= 32768:
        q1 -= 65536
    if q2 >= 32768:
        q2 -= 65536
    if q3 >= 32768:
        q3 -= 65536

    # 返回 int16，延迟到外层除以 16384
    return (q0, q1, q2, q3)


# ========= JSON 构造 =========
def build_json_fast(ts, frame_id, quat_flat):
    return {
        "Timestamp": ts,  # 秒级时间戳，避免 localtime 的耗时
        "FrameID": frame_id,
        "ID": IMU_IDS,
        "QuatList": quat_flat,
    }


# ========= CAN处理=========
def can_deal(canData):
    global have_mask, state, frameID
    
    msgID = canData['id']
    msgData = canData['data']
    
    if msgID not in ID_TO_IDX:
        return

    idx = ID_TO_IDX[msgID]
    #print("ori-imu-", idx)
    with buffer_lock:
        if msgID == 0x10:
            # 新一轮：清掩码并记录 0x10
            frameID += 1
            have_mask = 0b0001
            state = ST_COLLECTING
            imu_raw[0][:] = bytes(msgData)
            #print("imu-", idx)

        elif state == ST_COLLECTING:
            imu_raw[idx][:] = bytes(msgData)
            have_mask |= 1 << idx
            #print("imu-", idx)
            if have_mask == ALL_MASK:
                state = ST_READY


def can_interrupt_handler(pin):
    intf = can.ReadByte(CANINTF)  # 读取中断标志寄存器

    # RX0有数据
    if intf & RX0IF_SET:
        data = can.read_rx0_buffer()
        msgBuffer.append(data)
        can.WriteBytes(CANINTF, intf & ~RX0IF_SET)

        # print(data)
    # RX1有数据
    if intf & RX1IF_SET:
        data = can.read_rx1_buffer()
        msgBuffer.append(data)
        can.WriteBytes(CANINTF, intf & ~RX1IF_SET)

    # 清除所有已读缓冲区的中断标志
    # intf &= ~(RX0IF_SET | RX1IF_SET)
    # can.WriteBytes(CANINTF, intf)

    # msgList = can.check_and_clear_interrupt()
    # for msg in msgList:
    #     if not msg:
    #         return
    #     if isinstance(msg, dict):
    #         can_deal(msg['id'], msg['data'])
    #     else:
    #         print(msg)


# 绑定中断
can_int_pin.irq(trigger=Pin.IRQ_FALLING, handler=can_interrupt_handler)

# ========= 主循环 =========
try:
    # 网络初始化
    network_udp = NetworkUDP(
        wifi_ssid=WIFI_SSID,
        wifi_password=WIFI_PASSWORD,
        target_ip=UDP_TARGET_IP,
        target_port=UDP_TARGET_PORT,
        local_port=UDP_LOCAL_PORT,
    )
    network_udp.connect_wifi()

    recv = network_udp.recv
    send = network_udp.send

    print("等待接收 'imustart' 指令...")
    led_onboard.value(1)
    while True:
        if recv() == "imustart":
            pwm = PWM(pwm_pin)
            pwm.freq(PWM_FREQUENCY)
            pwm.duty_u16(PWM_DUTY)
            
            break

    print("开始处理CAN数据...")
    quat_flat = [0.0] * (IMU_COUNT * 4)

    while True:
        if msgBuffer:
            can_deal(msgBuffer[0])
            #send(json.dumps(msgBuffer[0]))
            msgBuffer.pop(0)

        if state == ST_READY:
            # 快照：拷贝 4 个 IMU 的原始数据
            local_raw = [bytes(imu_raw[i]) for i in range(IMU_COUNT)]

            with buffer_lock:
                cur_frame = frameID
                state = ST_IDLE
                have_mask = 0
                led_onboard.toggle()

            # 解码
            q0 = tuple(v / 16384 for v in decode_quat_viper(local_raw[0]))
            q1 = tuple(v / 16384 for v in decode_quat_viper(local_raw[1]))
            q2 = tuple(v / 16384 for v in decode_quat_viper(local_raw[2]))
            q3 = tuple(v / 16384 for v in decode_quat_viper(local_raw[3]))

            quat_flat[0:4] = q0
            quat_flat[4:8] = q1
            quat_flat[8:12] = q2
            quat_flat[12:16] = q3

            ts = time.time()
            payload = build_json_fast(ts, cur_frame, quat_flat)
            send(json.dumps(payload))

except KeyboardInterrupt:
    print("程序已停止")
except Exception as e:
    print("发生错误:", e)
finally:
    if pwm:
        pwm.deinit()
    led_onboard.value(0)
    can_int_pin.irq(handler=None)
