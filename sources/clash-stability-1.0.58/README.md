# Clash Stability 1.0.58 — runtime fingerprint compatibility

## 中文

新版不再用 CoC 的版本号决定是否启用 iOS 16 适配。三个启动入口现在都调用同一
个运行时指纹函数。它读取并校验完整 `magicx.framework/magicx`、完整 systemhook
和生成的 dyld 文件的 SHA-256、精确大小以及读取前后的文件一致性。
**版本号变了，但这三份已知文件完全不变时，不需要仅为版本号重做插件。**

任意文件变化、读取失败或环境不匹配均拒绝启用，不猜测新偏移，不强制游戏检查
成功。原有设备/系统识别、游戏 bundle ID、版本字段类型、UUID/布局、调用位置、
原生就绪状态和工作线程快照集合校验均保留。没有全局拦截 CFEqual 或伪造 App
版本；新增函数只在此插件的三个指定调用点被调用。

这不能保证所有未来 CoC 更新都兼容：若防护文件或者越狱环境变了，仍需新的已
验证配置；即使指纹不变，其他游戏代码变化仍可能引入不同问题。当前没有实际
测试尚未发布的游戏版本，也不宣称支持新设备、iOS 17 或其他 Dopamine 版本。

### 已验收

- iPad14,6 / iPadOS 16.1 (20B82) / Dopamine 3.0.11 / CoC 18.647.2。
- 实际进入村庄；结束 CoC 后重新进入村庄。重开后的同一进程在返回虚拟 Mac 后
  仍存活至 3 分 19 秒。SpringBoard、虚拟 Mac 均未重启；没有退出越狱或删游戏数据。
- 独立实机文件指纹测试：已知文件通过；仅改一个字节、大小相同的测试副本被
  拒绝。真实游戏文件没有改动。临时测试工具不包含在发布包中。
- [验收记录](verification.json)、[正式 payload/DEB 哈希与调用点](release.json)。
- 旧的 [1.0.57](../../debs/com.codex.clashstability_1.0.57_iphoneos-arm64.deb)
  原样保留，作为回退版本。

### 安装

退出 CoC，更新 Clash Stability，再打开游戏。Choicy 自定义允许列表保持允许
`ClashTraceDiagnostic`。DEB 没有 respring 或重启脚本，不需要退出越狱、重装游戏
或重启虚拟 Mac。安装包只含一个 CoC 过滤器和对应 dylib。

### 代码与构建

`gate.c` 是本次新增运行时指纹函数的 C 源码；`padding.S` 保留已验证的旧自身
图像选择器空间；`build.py` 把新代码写入已验证 1.0.57 的未使用执行空间，并
只修改三个版本比较调用点。所有旧初始化入口和原有修复逻辑保持不变。
完整旧插件 C 源码仍未找回，因此这不是把整个历史插件重新从 C 编译的项目。

在 Mac 上提供 iOS SDK 路径：

```sh
python3 build.py --sdk /path/to/iPhoneOS.sdk --output build/ClashTraceDiagnostic.dylib
python3 test_release.py -v
```

生成的本地结果只有 Mac 临时签名，不能冒充设备已验收的正式 payload。
`package_release.py --payload /path/to/verified-device-signed.dylib --output build/repacked.deb`
只接受 `release.json` 固定哈希的正式 payload。安装直接使用软件源内的 DEB。
没有上传失败包、诊断观察器、游戏/越狱二进制文件、账号信息或设备日志。

## English

1.0.58 replaces the three iOS16 app-version comparison calls with a local
runtime gate. It checks full SHA-256 fingerprints and exact sizes of the known
protection framework, systemhook and generated dyld, with pre/post-read file
identity and timestamp consistency checks. App-version-number-only updates
with these unchanged known files no longer require a version-string patch.

Unknown, unreadable or changed inputs are refused. No offset guessing, blanket
success override, global CFEqual hook or fake app-version value is introduced.
Existing device/build, bundle ID, CFString type, UUID/layout, caller, readiness
and snapshot-set guards remain. Other game changes may still break compatibility;
this is not a guarantee for every future game or jailbreak release.

Regression tested on iPad14,6 / iPadOS16.1 / Dopamine3.0.11 / CoC18.647.2:
village launch and kill/relaunch visually verified, same relaunched process
observed alive at 199 seconds after returning to Virtual Mac. Known-file checks
passed, and a same-sized copy with one byte altered was refused. Real game files
were not modified. No device/userspace/SpringBoard restart, jailbreak exit or
game-data removal. No future real app version was tested.

`gate.c` is the new original C gate source; the checked builder extends the exact
previously verified 1.0.57 binary. The full original legacy C implementation
remains unavailable. The unmodified 1.0.57 DEB stays available for rollback.
Close CoC, install, reopen; retain the Choicy allowlist entry
`ClashTraceDiagnostic`. This package has no reboot/respring scripts.
