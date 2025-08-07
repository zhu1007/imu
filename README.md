# Raspberry Pi Pico IMU Data Acquisition Project  
> 作者：Cheng  
> 开发环境：Thonny + MicroPython  

---------------------------------------------------------------------------------

## 1. 文件说明
| 文件 | 作用 |
|---|---|
| `main.py` | 上电自动运行，完成 **网络** 与 **CAN 总线** 的初始化；所有引脚使用 **GP 编号** 定义 |
| `canbus.py` | 基于官方参考代码扩展，新增 **中断接收** 逻辑；驱动 Pico-CAN-B 模块 |
| `udp_send.py` | 负责 UDP 数据收发处理 |

---------------------------------------------------------------------------------

## 2. 常见问题 & 解决方案

| 现象 | 解决步骤 |
|---|---|
| **Thonny 无法识别串口**<br>`unable to connect to COM3: port not found` | 1. 点击 Thonny 的 **停止/重启后端** 按钮 → 拔插 USB 重试。<br>2. 仍失败：长按 Pico 上的 **Bootsel** 键并重新连接 USB → 将 `pico_nuke_pimoroni_pico_plus2_w_rp2350-1.4.uf2` 拖入 Pico 磁盘 **彻底擦除** → 再拖入 `mp_firmware_unofficial_latest.uf2` 重新烧录固件。 |
| **Wi-Fi 报错** `[CYW43] Bus error condition detected 0xff0f / 0xff07` | 检查引脚连接，务必使用 **GP 编号**（参考 [Pico Pinout](https://pico.nxez.com/pinout/pico/)）。<br>避免占用 **Pico-CAN-B 已占用的引脚**。 |
| **上传后代码未生效** | 上传后 **手动刷新** Pico 文件列表，确认代码已同步。 |
| **Wi-Fi 连接慢** | 属正常现象，上电后约 **10 s** 完成连接。 |

---------------------------------------------------------------------------------

## 3. 参考链接
- [Pico-CAN-B 官方 Wiki](https://www.waveshare.net/wiki/Pico-CAN-B)  
- [Pico 引脚功能（Pinout）](https://pico.nxez.com/pinout/pico/)

