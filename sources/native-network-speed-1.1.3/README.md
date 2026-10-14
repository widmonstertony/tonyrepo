# Tony Native Network Speed 1.1.3

## 中文

修复 iPad7,2 / iPadOS 17.7.11 在 YouTube 全屏 App 界面看不到网速的问题。这里的“全屏 App”是普通首页、视频及推荐页，不是隐藏原生状态栏的沉浸式视频播放。

根因是旧版把 `SBMainSwitcherWindow` 中的系统场景状态栏一律当作快照排除。但系统也用这个容器承载当前全屏 App 的原生状态栏。1.1.3 要求精确的系统宿主、可见且未遮挡的原生页面，以及与全局原生状态栏完全重合的屏幕坐标。缩小、偏移或嵌在 App 小窗口中的栏仍被排除。全局原生栏可见时优先使用它；始终只移动同一个标签。

仅注入 SpringBoard，不创建悬浮窗口，不修改隐藏栏的 alpha，不注入 YouTube 或 CoC。保留每秒接口字节采样、失败清除旧值、定位等原生图标至少 7 点间距。横屏音量反转仍是独立包，不在此插件中。

2026-10-13 实机验收：iPad7,2 / 17.7.11 / YouTube 21.41.5，横屏左。首页、普通视频页及 YouTube 结束后重开均显示一份网速；连续 9 次采样无失败，画面数值变化。切到台前调度 CoC 18.647.2 后实际进入村庄，小窗口内没有第二份标签，外层仍只有一份。CoC 插件哈希与已发布版一致，未改其包或配置，没有发现本轮新增 CoC / SpringBoard 崩溃报告。

同一 rootless arm64/arm64e 包仍包含原来的 iPad14,6 / 16.1 配置；新的场景分支仅适用于上述 iPadOS 17 配置。为保护运行虚拟 Mac 的设备，本轮没有给它安装 1.1.3，也没有重启或重新实测该设备；它的此前 1.1.0 验收仍可查。不要把这描述成“两台都实测了 1.1.3”。其他型号、系统及方向不宣称已经验收。

安装后需用户允许的一次 SpringBoard 重启。包内无自动重启脚本；在虚拟 Mac 宿主上先保存并关闭虚拟 Mac。源码与验收记录均包含在本目录，失败候选、临时诊断、原始设备日志、截图和 SDK 不发布。

## English

Fixes the missing network label in YouTube's ordinary full-app interface on iPad7,2 / iPadOS 17.7.11. This does not force a status bar over immersive video playback that hides the native bar.

The old owner guard rejected every bar under `SBMainSwitcherWindow` as a snapshot. That system container also presents the current full-screen App's native status bar. The new path requires the exact system host, a visible non-occluded native page, and a screen-space rectangle matching the global native bar. Scaled cards, inset windows and embedded App bars remain ineligible. A visible global bar takes priority; one retained label moves between eligible native bars.

SpringBoard-only. No new window, hidden-bar alpha override, YouTube/CoC injection, game changes or volume hooks. Preserves one-second interface-byte sampling, stale-value clearing on failure and at least 7-point native icon clearance.

Device acceptance on 2026-10-13 covers iPad7,2 / 17.7.11 / YouTube 21.41.5 in landscape-left: Home, a normal video page, a cold YouTube relaunch, nine live counter observations and visibly changing rates. CoC 18.647.2 entered its village in Stage Manager; only one outer label, none inside its App window. The existing CoC payload hash was unchanged and no new CoC or SpringBoard crash report was found during this test.

The same rootless arm64/arm64e package retains the qualified iPad14,6 / 16.1 profile; the new hosted-scene branch is iPadOS-17-only. Version 1.1.3 was not installed or live-tested on that VM-hosting device in this round. Its previous 1.1.0 receipt is preserved. Other profiles and orientations are not claimed tested. See `verification.json` for the exact acceptance scope.

## Build and checks

Supply your own iOS SDK. The builder never installs or restarts anything.

```sh
python3 build.py --sdk /path/to/iPhoneOS.sdk --output /tmp/network-speed-unsigned.deb
```

Compile and run each `test_*.c` with `-Wall -Wextra -Werror -fsanitize=address,undefined`. Tests cover exact device profiles, variable route records, direct owner guards, native icon bounds, collection-getter ABI and hosted-bar geometry, including rotated coordinate spaces.

Device signing is separate. `--signed-payload` accepts only the exact accepted payload SHA. Verify the published package and compare both compiled architecture slices' code/data sections:

```sh
python3 test_release.py
python3 test_release.py --compare-built /path/to/TonyNetStatus.dylib
```

Only original source, the accepted DEB and a summarized acceptance receipt are released. No Apple SDK, external libraries, failed candidates, probe packages, screenshots or raw device logs are redistributed.
