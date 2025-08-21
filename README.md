# Raspberry Pi Pico IMU Data Acquisition Project  
> 作者：Cheng  Xls

> 开发环境：Thonny + MicroPython  

---------------------------------------------------------------------------------

## 1. 文件说明
| 文件 | 作用 |
|---|---|
| `main.py` | 上电自动运行，完成 **网络** 与 **CAN 总线** 的初始化，通过UDP接受；所有引脚使用 **GP 编号** 定义 |
| `canbus.py` | 基于Pico-CAN-B 模块参考模块扩展，新增 **中断接收** 逻辑  |
| `udp_send.py` | UDP 数据收发处理模块 |

---------------------------------------------------------------------------------

## 2. 常见问题 & 解决方案

| 现象 | 解决步骤 |
|---|---|
| **Thonny 无法识别串口**<br>`unable to connect to COM3: port not found` | 1. 点击 Thonny 的 **停止/重启后端** 按钮 → 拔插 USB 重试。<br>2. 仍失败：长按 Pico 上的 **Bootsel** 键并重新连接 USB → 将 `pico_nuke_pimoroni_pico_plus2_w_rp2350-1.4.uf2` 拖入 Pico 磁盘 **彻底擦除** → 再拖入 `mp_firmware_unofficial_latest.uf2` 重新烧录固件。 |
|**Thonny 报错**<br>`[CYW43] Bus error condition detected 0xff0f` | 检查引脚连接，务必使用 **GP 编号**（参考 [Pico Pinout](https://pico.nxez.com/pinout/pico/)）。<br>避免占用 **Pico-CAN-B 已占用的引脚**。 |
| **上传后代码未生效** | 上传后 **手动刷新** Pico 文件列表，确认代码已同步。 |
| **Wi-Fi 连接慢** | 属正常现象，上电后约 **10 s** 完成连接。 |

---------------------------------------------------------------------------------

## 3. 参考链接
- [Pico-CAN-B 官方 Wiki](https://www.waveshare.net/wiki/Pico-CAN-B)  
- [Pico 引脚功能（Pinout）](https://pico.nxez.com/pinout/pico/)
- [IMU端stm32代码](https://xlsnas.myds.me:3001/WangYiMeng/wym_imu)

---------------------------------------------------------------------------------

## 4. 版本说明
Version 1.0:实现UDP接受到开始命令后发送PWM波，然后利用CAN总线接收单个ID的消息并发送，未接入IMU

Version 2.0:实现了利用接收IMU数据并且打包成json上传，但是IMU发送数据的间隔应大于等于2ms，MCP2515双缓冲区存疑
