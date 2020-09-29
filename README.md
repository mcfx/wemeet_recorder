# wemeet_recorder

腾讯会议录屏器

## 使用方法

建议在 Linux 下操作。

首先安装 VirtualBox，然后安装一个 Windows 虚拟机（建议 Win7 或者 Win10 LTSC 等）。虚拟机最好不要加声卡，而是用 VB-CABLE 这种虚拟声卡。虚拟机内部安装 python3、ffmpeg、腾讯会议，以及 ![screen-capture-recorder-to-video-windows-free](https://github.com/rdp/screen-capture-recorder-to-video-windows-free)。然后用 pip 安装 pywin32 和 requests 两个包。

接下来把 client 拷进虚拟机，然后想办法让他开机自动运行。

client 和 server 需要填的参数可以看看代码。

### 需要注意的问题

- 最好禁用掉麦克风

- 虚拟机核给够，不然可能会卡（如果硬盘够的话，也许可以考虑先改成无损压缩，然后之后再慢慢压）

## 其他使用方法

把 client 里操作腾讯会议的部分拷出来，然后配其他东西使用。这坨东西理论上应该在其他环境也能跑，但是这基本没有判断各种特殊情况，所以可能有时会出锅。