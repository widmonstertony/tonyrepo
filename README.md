# Tony Repo — iOS/iPadOS 16–17 Rootless APT Source

Personal APT repository for original jailbreak hacks, fixes, tools, and
experiments by tony. ThermalLightControl supports iOS/iPadOS 16–17 rootless
jailbreaks and can be installed through Sileo or Zebra.

Repository URL:

```text
https://widmonstertony.github.io/tonyrepo/
```

Add the URL to Sileo or Zebra and refresh sources.

[Add to Sileo](sileo://source/https://widmonstertony.github.io/tonyrepo/) ·
[Add to Zebra](zbra://sources/add/https://widmonstertony.github.io/tonyrepo/) ·
[Open repository page](https://widmonstertony.github.io/tonyrepo/)

## Packages

- **Tony Native Network Speed 1.1.4** — packaging-only manual restart reminders in installation details and Settings, without a restart command or GUI restart finish action. Runtime/filter/existing switch are byte-identical to accepted 1.1.3, including the verified YouTube full-app fix, one live outer label and unchanged CoC. The qualified iPadOS16.1 profile remains; the VM host was not touched. [Source and exact acceptance](sources/native-network-speed-1.1.4/README.md) · [Installation](depictions/native-network-speed.html).
- **Tony Reverse Volume Keys 1.0.1** — separate, optional package for the qualified iPad7,2 / 17.7.11 only. Reverses landscape hardware keys, leaves portrait normal, preserves existing audio/game settings. Not bundled with network speed and not installed on the VM-hosting iPad. [Source and acceptance](sources/reverse-volume-1.0.1/README.md) · [Installation](depictions/reverse-volume.html).
- **Clash Stability 1.2.0** — one installer automatically selects the unchanged accepted payload/signature for qualified iPad14,6 /16.1 or iPad7,2 /17.7.11 profiles. One injected dylib, villages visually verified on both, user manually confirmed both working. No respring or changes to the game/other tweaks. One active CoC APT entry; historical accepted rollback files retained. [Installer source and exact acceptance](sources/clash-stability-universal-1.2.0/README.md) · [Installation](depictions/clash-stability.html).
- **GO 信息显示 / GO Info 0.4.0 (preview)** — reversible bag/detail IV display with prominent 3★/4★ labels, plus an in-game Discord panel and confirmed per-app route positioning, joystick and GPX import. Discovers interfaces by runtime types and signatures instead of game-version or UUID allowlists; missing or ambiguous matches are disabled. Installed on iPadOS 17.7.11 / Pokémon GO 0.435.0, detail IV independently checked and user-confirmed working; full scrolling, long-running and cross-device verification remain incomplete. Configure **Settings → GO 信息显示**; automatic saved-state recovery is retained. In-game positioning validation is pending; this does **not** fix game startup crashes. Only the binary is published here; plugin source remains private. [Compatibility and installation](depictions/go-info.html).
- **ThermalLightControl 3.7.1** — one universal arm64/arm64e package for iPadOS 16–17. It covers the CoreBrightness, CoreAnimation, EDR, notification, and per-frame RTPLC paths that can force SDR output down in games, while preserving CPU/GPU throttling, temperature monitoring, warnings, watchdog, and emergency shutdown.
- **VirtualMac Audio Stability Fix 1.0.2** — preserves VirtualMac microphone and speaker support, reactivates audio after media-service interruptions, and prevents the iPadOS 16.1 MediaExperience/Now Playing teardown race.
- **Virtual Mac 1.2.3+609.pause2** — a modified build of the upstream MIT-licensed project with native in-memory Pause/Resume controls and a startup menu-refresh fix. Supported only on the upstream-compatible M1/M2 iPads running iPadOS 14.5–16.3.1.

## Grass Mac Browser

The native Universal 2 macOS client is maintained in the separate
[`widmonstertony/newt66y-mac-universal`](https://github.com/widmonstertony/newt66y-mac-universal)
repository. One package runs natively on both Intel (`x86_64`) and Apple
silicon (`arm64`) Macs.

[Download v1.4.0](https://github.com/widmonstertony/newt66y-mac-universal/releases/tag/v1.4.0) ·
[Bilingual installation guide](https://github.com/widmonstertony/newt66y-mac-universal#readme)

## NewT66y 2.3.7 local universal builder

This repository does **not** redistribute NewT66y, its IPA, app bundle, icon, or a
package containing the app. The public builder only repackages a copy that the
user has lawfully obtained into either a universal iPad/PlayCover IPA or a
rootless jailbreak package on the user's Mac. The generated app includes the
original NewTWebFix navigation, input, Touch Bar, and VidCatch download bridge.

1. Download or clone this repository on a Mac.
2. Put your own `1024app_ios_2.3.7.ipa` beside
   `tools/newt66y-local-builder/Build-NewT66y.command`, or drag the IPA onto that
   command file in Terminal.
3. Run `Build-Universal-IPA.command` for one IPA that can be installed on iPad
   and imported by PlayCover 3.1.0, or run `Build-NewT66y.command` for a
   rootless `.deb`.
4. Install the locally generated result only on your own device. On iPad,
   downloaded videos appear under `Files > On My iPad > 小草补丁V8 > VidCatch`.

Full instructions and the legal/provenance notice are in
[`tools/newt66y-local-builder/README.md`](tools/newt66y-local-builder/README.md).
The generated package is intentionally ignored by Git and must not be committed
to this public repository.

ThermalLightControl supports iOS/iPadOS 16–17 rootless jailbreaks. Other packages
retain the narrower compatibility ranges stated in their descriptions.

> Sustained high brightness at elevated temperatures increases power consumption,
> display wear, and overheating risk. Monitor device temperature and disable
> ThermalLightControl if the device becomes unusually hot.

---

# Tony Repo 中文说明 — iOS/iPadOS 16–17 Rootless 越狱源

这是 tony 发布个人原创 hack、修复、工具与实验项目的长期越狱源。
ThermalLightControl 现支持 iOS/iPadOS 16–17 rootless 越狱环境。将上面的地址添加到
Sileo 或 Zebra 后刷新软件源即可；其他软件包仍以各自说明的兼容范围为准。

[一键添加到 Sileo](sileo://source/https://widmonstertony.github.io/tonyrepo/) ·
[一键添加到 Zebra](zbra://sources/add/https://widmonstertony.github.io/tonyrepo/) ·
[打开软件源页面](https://widmonstertony.github.io/tonyrepo/)

- **Tony Native Network Speed 1.1.4**：仅新增安装详情日志和设置中的手动重启提醒，不执行重启、不发送包管理器重启完成动作。运行二进制、原开关与已验收 1.1.3 逐字节相同，保留 YouTube 修复、最外层单份实时网速和原样 CoC。仍共用同一包，保留 iPad14,6 /16.1 配置，本轮未操作虚拟 Mac 宿主。[说明](depictions/native-network-speed.html) · [完整源码与准确验收范围](sources/native-network-speed-1.1.4/README.md)。
- **Tony Reverse Volume Keys 1.0.1**：横屏音量反转为独立可选插件，只适配那台 iPad7,2 / 17.7.11，竖屏不变。不合入网速包、不改音频会话、不注入 CoC，也未安装到虚拟 Mac 宿主 iPad。[说明](depictions/reverse-volume.html) · [源码与验收](sources/reverse-volume-1.0.1/README.md)。
- **Clash Stability 1.2.0**：一个安装包自动选择 iPad14,6 /16.1 或 iPad7,2 /17.7.11 的已验收程序，程序与签名逐字节不变；只注入一份，两台已看到村庄并由用户手动确认正常。无需重启 SpringBoard，不改游戏或其他插件。APT 只保留一个 CoC 入口，旧正式包保留供回退。[安装说明](depictions/clash-stability.html) · [通用安装器源码与准确验收](sources/clash-stability-universal-1.2.0/README.md)。
- **GO 信息显示 0.4.0（预览版）**：背包／详情 IV、3★／4★ 加粗突出，内置 Discord 与需确认的游戏内路线定位、摇杆、GPX 导入。改为按运行时类型和签名自动适配，不锁游戏版本号或框架 UUID；入口缺失或有歧义时停用，不猜数值。已在 iPadOS 17.7.11 / Pokémon GO 0.435.0 安装、独立核对详情 IV，并由用户确认可用；本轮未完整独立验收滚动、长时运行及跨设备兼容性，游戏内定位实机验收仍待完成。入口「设置 → GO 信息显示」，保留自动配置恢复。此包**不修复游戏启动闪退**；本源只发布安装包，插件源码继续保持 private。[查看兼容性与安装说明](depictions/go-info.html)。
- **ThermalLightControl 3.7.1**：同一个 arm64/arm64e 通用安装包支持 iPadOS 16–17，覆盖游戏可能触发的 CoreBrightness、CoreAnimation、EDR、通知直达与逐帧 RTPLC 降亮路径，同时保留 CPU/GPU 降频、温度监控、过热警告、watchdog 和紧急关机保护。
- **VirtualMac Audio Stability Fix 1.0.2**：保留 VirtualMac 的麦克风与扬声器功能，在媒体服务中断后自动恢复音频，并修复 iPadOS 16.1 上 MediaExperience/正在播放模块销毁时的竞态崩溃。
- **Virtual Mac 1.2.3+609.pause2**：基于上游 MIT 开源项目的修改版，加入原生内存暂停/恢复以及虚拟机启动后自动刷新菜单的修复。仅支持上游兼容的 M1/M2 iPad 与 iPadOS 14.5–16.3.1。

## 小草 Mac 浏览器

原生 Universal 2 macOS 客户端已放在独立的
[`widmonstertony/newt66y-mac-universal`](https://github.com/widmonstertony/newt66y-mac-universal)
仓库。同一个安装包同时原生支持 Intel (`x86_64`) 与 Apple silicon
(`arm64`) Mac。

[下载 v1.4.0](https://github.com/widmonstertony/newt66y-mac-universal/releases/tag/v1.4.0) ·
[中英文安装说明](https://github.com/widmonstertony/newt66y-mac-universal#readme)

## NewT66y 2.3.7 本地通用构建工具

本仓库**不提供或再分发**小草/NewT66y 的 IPA、App、图标或包含 App 的安装包。
公开内容只有原创打包脚本；用户必须在自己的 Mac 上提供自己合法取得的
`1024app_ios_2.3.7.ipa`。脚本可以在本地生成一份同时供 iPad 与 PlayCover 3.1.0
使用的通用 IPA，或者生成 rootless `.deb`。生成的 App 包含 NewTWebFix 的导航、
输入、Touch Bar 与 VidCatch 下载桥接；iPad 下载文件保存在“文件 > 在我的 iPad 上
> 小草补丁V8 > VidCatch”。

请阅读
[`tools/newt66y-local-builder/README.md`](tools/newt66y-local-builder/README.md)
中的完整操作步骤。生成的 `.deb` 已被 Git 忽略，只能传到自己的设备本地安装，
不得提交到本公开仓库。

ThermalLightControl 支持 iOS/iPadOS 16–17 rootless 越狱环境；其他软件包仍以各自说明为准。
