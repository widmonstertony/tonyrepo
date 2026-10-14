# Tony Native Network Speed 1.1.0 — universal

## 中文

同一个 rootless DEB、同一份 arm64/arm64e 二进制，运行时选择已验证的设备路径：

- iPad14,6 / iPadOS 16.1：`UIStatusBarWindow` → `_UIStatusBarForegroundView`。
- iPad7,2 / iPadOS 17.7.11：`SBStatusBarWindow` → `STUIStatusBarForegroundView`。

其他型号或系统版本保持不启用，不冒充已支持。仅注入 SpringBoard；只在最外层原生状态栏放一份网速，排除 App 窗口、复用池和外接屏。原生状态栏隐藏时不强行显示。每秒读接口累计字节计算速率；解析失败清除旧值，不继续显示过期速率。与定位等原生右侧图标保留至少 7 点间距。

横屏音量键是**独立**的 `com.tony.reversevolume` 插件，仅供已验证的那台 iPad7,2 使用，不包含在此包内。不替换、不注入、不修改 CoC。无需停用越狱或重启整个 iPad；加载新版仍需一次 SpringBoard 重启。安装器没有任何自动重启脚本。

2026-10-13：上述两台已加载同一个 1.1.0 二进制，确认单份外层标签、持续更新、原生图标至少 7 点间距。iPad7,2 已检查主屏幕、台前调度设置窗口和 CoC 村庄无重复；iPad14,6 已检查运行虚拟 Mac 的台前调度界面，无内层重复。为避免影响承载当前工作环境的虚拟 Mac，未在 iPad14,6 上另外切换重开 CoC；该设备 CoC 包保持原样、未观察到新增崩溃。完整验收范围见 verification.json。

修复旧版的两个根因：合法的短路由记录被误判导致采样冻结；把 App 内嵌状态栏误当外层导致重复。定位图标纳入原生避让范围。1.1.0 取代旧网速版本，不建议回退 0.1.1。

## English

One rootless DEB and one arm64/arm64e binary select the qualified iPadOS 16.1 or 17.7.11 native status-bar path at runtime. Supported combinations are exactly iPad14,6 / 16.1 and iPad7,2 / 17.7.11; all other combinations remain inactive.

SpringBoard-only injection, one label in the outer system status bar, no floating windows or embedded-app duplicates. Uses interface byte counters once per second; failures clear stale rates. Respects native status-bar visibility and leaves at least 7 points before native right-side icons.

Landscape volume reversal remains a separate package for the qualified iPad7,2 only. This package contains no volume or game hooks, no CoC changes and no automatic restart scripts. Reloading a newly installed binary requires a SpringBoard restart, not a full device reboot or leaving jailbreak mode. Never restart the iPad hosting the active macOS VM automatically.

Accepted with the same 1.1.0 payload on both qualified devices on 2026-10-13. The iPad7,2 checks include Home, Settings and an actual CoC village in Stage Manager. The iPad14,6 check covers Stage Manager with the hosted macOS VM; CoC was not relaunched there to avoid disrupting that VM. Its existing CoC adapter was not modified and no new crash reports were observed. See verification.json for exact scope, rather than assuming every application/orientation was tested.

Fixes the old parser rejecting valid short route records and freezing rates, embedded status-bar duplicates, and missing clearance for location icons. Supersedes the legacy 0.1.1 release.

## Build and offline checks

Supply your own iOS SDK. No SDK, Apple libraries, device crash logs, screenshots or other third-party binaries are redistributed here.

```sh
python3 build.py --sdk /path/to/iPhoneOS.sdk --output /tmp/network-speed-unsigned.deb
clang -Wall -Wextra -Werror -fsanitize=address,undefined test_device_profile.c -o /tmp/profile-test
/tmp/profile-test
```

Also compile/run `test_route_messages.c`, `test_outer_window.c` and `test_native_bounds.c`. Device signing is separate; compare both architecture slices' code/data sections against the local build before packaging the signed payload. All installation, approval and acceptance steps are separate from the builder.

Offline release verification from a clone of this repository:

```sh
python3 test_release.py
# After a local build, compare code/data in both architecture slices:
python3 test_release.py --compare-built build/TonyNetStatus.dylib
```

Only the DEB's exact accepted payload SHA is accepted by `--signed-payload`;
unsigned local rebuilds are deliberately not described as device-tested releases.
