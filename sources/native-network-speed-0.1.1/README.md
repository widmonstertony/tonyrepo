# Tony Native Network Speed 0.1.1 — iPadOS 16

Legacy: superseded by [1.1.0](../native-network-speed-1.1.0/README.md). Later use
exposed stale-rate parsing and embedded status-bar duplication issues. Retained
for history, not recommended for installation or rollback.

历史版本：后续发现冻结和窗口重复问题，请使用 1.1.0，不建议安装或回退此版。

Original Objective-C source and standalone builder for the verified
iPad14,6 / iPadOS 16.1 native right-side status-bar patch. It displays
download/upload bytes per second before the existing Wi-Fi/battery area.
K/M represent KiB/s and MiB/s; `0K` is normal when idle or below 1 KiB/s.

No separate window, draggable HUD, game injection, packet capture, network
request or system-daemon hook. SpringBoard is the only injection target.
The default is enabled; Settings → Network speed provides a switch.
Sampling runs once per second and includes en0 and pdp_ip interfaces, not
VPN interfaces. Visible UI work is dispatched to the main queue.

The payload is exactly the user-verified 0.1.1 device-signed binary; only
package metadata has changed from the local-preview label. arm64 and arm64e
slices are both required: an arm64-only dylib did not load into this device's
arm64e SpringBoard. Failed 0.1.0 and diagnostic helpers are not published.

```sh
python3 build.py --sdk /path/to/iPhoneOS.sdk --output build/local.deb
```

Compilation creates a local candidate, not proof of real-device behavior.
Use a suitable device signer; exact-release repackaging checks its hash.
The included sources need no scripts outside this repository. See the
separate iPadOS17 package/source directory for that profile.

## 中文

这是已在 iPad14,6 / iPadOS 16.1 重启 SpringBoard 后验收的 0.1.1 原始代码，
正式包保留原样二进制，只整理正式名称与说明。网速嵌在右侧原生状态栏，不是悬浮窗。
默认开启，可在设置的「右上角实时网速 / Network speed」开关关闭。
完整源码、构建脚本和验收记录一并提供；没有上传失败测试包或临时诊断程序。
安装后需重启一次 SpringBoard。若虚拟 Mac 正在此 iPad 上运行，先保存并关闭它。
