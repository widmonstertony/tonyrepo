# Tony Reverse Volume Keys 1.0.1

Original SpringBoard-only adapter for iPad7,2 / iPadOS17.7.11. Default mode:
reverse volume-key directions in **both landscape orientations**, preserve
portrait. No app/game injection, audio-session replacement, volume-limit
bypass, system-daemon hook or restart script.

2026-10-13 acceptance: controlled landscape-left key events changed volume
0.25 ->0.1875 ->0.25 in reversed directions, then restored the current pretest
0.5625. The user confirmed all requested physical behavior after discussion
of landscape reversal and portrait normal direction. Portrait was not separately
automated; the opposite landscape was not separately verified. verification.json
distinguishes human confirmation from instrumented checks.

Only these live-observed hardware-action methods are intercepted, after
checking their argument/return encodings:

- `SBVolumeHardwareButtonActions::_handleVolumeButtonDownForIncrease:modifiers:`
- `SBVolumeHardwareButtonActions::_handleVolumeButtonUpForIncrease:`

Modifiers and original return values are preserved. The press-down mapping
is held until release, so rotation or a Settings change during a held key
does not leave an unmatched release. This does not invert Control Center
sliders, Siri or direct `setVolume` calls. Landscape detection uses the actual
main-screen `SBStatusBarWindow` full-window bounds, not an embedded app/window
orientation getter or an always-wide status-bar strip. Its live-observed1366x1024
landscape shape is compared to its1024x1366 portrait shape. Missing, square,
nonfinite or zero geometry fails closed rather than flipping portrait.

Settings switches: **Reverse volume keys** and **Landscape only**. Both
default true for this user's requested behavior; existing saved values
are respected. Domain: `com.tony.reversevolume`. The device's pre-existing
fixed-position volume arrangement setting is preserved; validation must
state that context, not imply compatibility with every other mapper.

Compile locally (not device acceptance):

```sh
python3 build.py --sdk /path/to/iPhoneOS.sdk --output build/local.deb
cc -Wall -Wextra -Werror -fsanitize=address,undefined test_display_geometry.c -o /tmp/tony-volume-geometry
/tmp/tony-volume-geometry
```

Sign for your device. Do not publish or mark verified until actual hardware
event routing and the landscape/portrait cutoff have been checked.

The accepted package is in this repository's `debs/` directory; this source
folder does not duplicate its binary or any SDK. Run `python3 test_release.py`
to verify its exact SHA, four payload files, SpringBoard-only filter and
arm64/arm64e slices. After a rebuild, use
`python3 test_release.py --compare-built build/TonyReverseVolume.dylib` to
compare the compiled code/data sections with the signed accepted payload.

## 中文

默认只在横屏（左右两个方向）对调音量加减，竖屏不变。只处理实体键的按下／松开，
不改控制中心滑块、Siri、音频会话或游戏。按下后的方向持续到松开，避免按住时
切换方向或开关导致松开事件不匹配。开关位于系统设置，默认开启反转和「仅横屏」。
只适配当前已核验的 iPad7,2 / 17.7.11 方法签名，其他环境不强行启用。
不改变已有的固定位置音量设置，也不注入 CoC。
2026-10-13 已通过横屏左向实际音量变化测试，随后用户确认要求的实体键行为
均通过。竖屏结果来自用户确认，另一横屏方向未单独验收；记录不把它们写成自动测试。
1.0.1 改为读取真正外层全屏窗口的横竖尺寸，不再用台前调度中可能不同步的
嵌入 App 方向值。未知尺寸时不反转。构建／签名／离线测试通过不等于实机验收；
实际音量变化、左右横屏与竖屏的分界需逐项验证后才能发布。
