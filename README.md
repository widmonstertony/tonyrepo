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

- **Tony Native Network Speed 1.1.0** — one identical package/binary verified on iPad14,6 / iPadOS 16.1 and iPad7,2 / 17.7.11. Runtime-qualified native outer status bar only; fixes stale rates, embedded-app duplicates and location-icon overlap. No floating window, volume hooks or game injection. [Source and acceptance](sources/native-network-speed-1.1.0/README.md) · [Installation](depictions/native-network-speed.html).
- **Tony Reverse Volume Keys 1.0.1** — separate, optional package for the qualified iPad7,2 / 17.7.11 only. Reverses landscape hardware keys, leaves portrait normal, preserves existing audio/game settings. Not bundled with network speed and not installed on the VM-hosting iPad. [Source and acceptance](sources/reverse-volume-1.0.1/README.md) · [Installation](depictions/reverse-volume.html).
- **Clash Stability iPadOS 17 1.1.0** — separately verified iPad7,2 / iPadOS 17.7.11 / known Dopamine 3.0.10 file profile, CoC 18.647.2. Includes the new fingerprint gate and precise own-image worker snapshot correction. Village launch and relaunch after SpringBoard restart passed; does not change the iOS16 release. [Source and receipt](sources/clash-stability-ios17-1.1.0/README.md) · [Installation](depictions/clash-stability-ios17.html).
- **GO 信息显示 / GO Info 0.3.2 (preview)** — reversible bag/detail IV display with prominent 3★/4★ labels, plus an in-game Discord panel and confirmed per-app route positioning, joystick and GPX import. Only Pokémon GO 0.431.1 with the matching UnityFramework build is supported. Bag/detail IV was verified on iPadOS 16.1; in-game positioning validation is pending. Configure **Settings → GO 信息显示**; a bundled mobile service automatically restores saved configuration. This package does **not** fix Pokémon GO startup crashes. [Compatibility and installation](depictions/go-info.html).
- **Clash Stability 1.0.58** — runtime fingerprint compatibility for the verified iPad14,6 / iPadOS 16.1 / Dopamine 3.0.11 profile. App-version-number changes no longer block loading when the complete known protection/jailbreak files remain identical; changed fingerprints are refused. CoC 18.647.2 village launch and relaunch verified. [Compatibility](depictions/clash-stability.html) · [New C gate, checked builder and verification](sources/clash-stability-1.0.58/README.md). The full legacy C source remains unavailable. Unmodified 1.0.57 stays available for rollback; 1.0.41 remains for legacy profiles. No new iOS 17 or future-game-version test is claimed.
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

- **Tony Native Network Speed 1.1.0**：两台使用同一个安装包、同一个二进制，运行时适配 iPad14,6 / 16.1 和 iPad7,2 / 17.7.11。只保留最外层一份实时网速，修复冻结、App 窗口重复和定位图标重叠；不是悬浮窗，不合入音量或游戏修改。[说明](depictions/native-network-speed.html) · [完整源码与验收](sources/native-network-speed-1.1.0/README.md)。
- **Tony Reverse Volume Keys 1.0.1**：横屏音量反转为独立可选插件，只适配那台 iPad7,2 / 17.7.11，竖屏不变。不合入网速包、不改音频会话、不注入 CoC，也未安装到虚拟 Mac 宿主 iPad。[说明](depictions/reverse-volume.html) · [源码与验收](sources/reverse-volume-1.0.1/README.md)。
- **Clash Stability iPadOS 17 1.1.0**：另一台 iPad7,2 / iPadOS 17.7.11 / 已知 Dopamine 3.0.10 文件组合 / CoC 18.647.2 已验证进入村庄，并在重启 SpringBoard 后重开成功。独立包避免影响 16.1 的已验收版本。[安装说明](depictions/clash-stability-ios17.html) · [代码与验收记录](sources/clash-stability-ios17-1.1.0/README.md)。
- **GO 信息显示 0.3.2（预览版）**：背包／详情 IV、3★／4★ 加粗突出，内置 Discord 频道及需确认的游戏内路线定位、摇杆、GPX 导入。只适配 Pokémon GO 0.431.1 与匹配的 UnityFramework；背包／详情 IV 已在 iPadOS 16.1 验证，游戏内定位实机验收仍待完成。入口「设置 → GO 信息显示」；随包 mobile 服务自动恢复已保存配置。此包**不修复游戏启动闪退**。[查看兼容性与安装说明](depictions/go-info.html)。
- **Clash Stability 1.0.58**：已加入运行时指纹兼容。完整已知防护/越狱文件未变时，不再因 CoC 版本号变化拒绝加载；指纹变了则拒绝启用。当前 iPad14,6 / iPadOS 16.1 / Dopamine 3.0.11 / CoC 18.647.2 进入村庄及重开游戏均已验收，无需重启或退出越狱。[兼容性说明](depictions/clash-stability.html) · [新增 C 指纹函数、适配代码与验收记录](sources/clash-stability-1.0.58/README.md)。完整旧 C 源码仍未找回；1.0.57 原样保留供回退，1.0.41 保留供原兼容组合使用。不能据此保证所有未来游戏版本或新增 iOS 17 支持。
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
