# main.py
from machine import Pin
import time  # 新增：导入time模块
import network_send

# 使用Pico W板载LED
LED = Pin("LED", Pin.OUT)

def generate_data(counter):
    """生成要发送的数据（示例函数）"""
    # 这里可以根据需求生成不同的数据
    return f"自定义数据包 #{counter}\n时间: {time.localtime()}\n"

def main():
    """主程序"""
    # 初始化LED
    LED.off()
    
    try:
        # 启动网络服务，传入数据生成函数
        network_send.run_network_service(LED, data_generator=generate_data)
    finally:
        print("程序已停止")

# 程序入口
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("程序被中断")
    except Exception as e:
        print(f"未处理的错误: {e}")
        import machine
        machine.reset()