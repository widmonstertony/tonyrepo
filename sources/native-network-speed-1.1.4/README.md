# Tony Native Network Speed 1.1.4 — manual install notice

## 中文

本版只更新安装提示，不改网速运行功能。运行二进制、SpringBoard 注入过滤和原有设置开关与已实机验收的 1.1.3 **逐字节相同**。包版本是 1.1.4，运行诊断仍显示 1.1.3，这是有意保留原二进制的结果。

新增两处提醒：

- 安装配置完成时，在安装详情日志输出完整中英文说明：需要时由用户确认后手动重启 SpringBoard；虚拟 Mac 宿主先保存并关闭虚拟 Mac；不必重启整台 iPad 或退出越狱。
- 设置列表中直接显示只读文字「网速更新后请手动重启 SpringBoard」。原网速开关原位保留，不替换成新的页面。

这是**提示版，不是 Sileo 原生重启按钮或弹窗**。不执行重启命令，不向包管理器发送重启完成状态，不改 Sileo 设置，不创建后台任务。用户自行决定何时重启。本包不会自动重启；其他同时排队的软件包、包管理器自身操作不受本包控制。

没有发送标准 `finish:restart` 的原因：Sileo 官方源码会在启用 AutoComplete 或安装浮层未呈现时调用完成动作，原生 restart 完成动作随后执行重启。仅添加这个标记不能保证“必须用户点击”。因此本版只输出可读说明、保留常驻设置提醒，不发出重启完成信号。[官方完成动作代码](https://github.com/Sileo/Sileo/blob/c9f70158a037dc76b91c450e72af2de0514dd3ee/Sileo/UI/DownloadsViewController/DownloadsTableViewController.swift)。

2026-10-13 验证：在 iPad7,2 /17.7.11 用直接 dpkg 安装，实际看到中英文输出；安装前后 SpringBoard 进程保持不变。设置中的常驻文字实机可见，原有开关仍开启；网速采样持续、一份外层标签、7 点图标间距。网速与 CoC 插件哈希保持原样，没有操作虚拟 Mac 宿主。不把直接 dpkg 的输出检查冒充为 Sileo 原生弹窗/按钮实测。完整记录见 verification.json，运行功能的详细验收仍见 [1.1.3](../native-network-speed-1.1.3/README.md)。

## English

Packaging-only update: the runtime binary, injection filter and existing Settings switch are byte-identical to accepted 1.1.3. Package version is 1.1.4; runtime diagnostics intentionally remain 1.1.3.

The configure script prints bilingual manual SpringBoard restart instructions to the installation details log, including saving and closing a hosted virtual Mac first. A separate read-only Settings row shows the reminder without changing the original switch.

This is a notice, **not a native Sileo restart button or dialog**. No restart command, GUI restart finish signal, Sileo preference modification or background task. Sileo's standard finish action can run automatically when AutoComplete is enabled or its installation popup is not presented, so emitting that action would not guarantee manual confirmation. This package does not control other queued packages or package-manager actions.

Acceptance on iPad7,2 /17.7.11: direct dpkg installation printed both languages, SpringBoard process remained unchanged, the static Settings reminder was visually confirmed, the existing enabled switch remained, live network sampling and one label continued, and the network/CoC payload hashes were unchanged. The VM host was untouched. Native Sileo button/dialog testing is not claimed.

## Build and checks

Run `python3 test_install_notice.py` and `python3 test_release.py`. The first exercises the print-only script with CLI, Sileo/Cydia, malformed and AutoComplete environments and abort actions; the second verifies the exact package, executable script mode and byte equality of all three original payload files against 1.1.3.

Supply your own SDK for a runtime rebuild, or the exact accepted signed 1.1.3 payload for a release repack:

```sh
python3 build.py --sdk /path/to/iPhoneOS.sdk --output /tmp/network-speed-local.deb
python3 build.py --signed-payload /path/to/accepted-1.1.3.dylib --output /tmp/network-speed-1.1.4.deb
```

The builder never installs or restarts. No SDK, PreferenceLoader/Sileo binary, failed prototype, raw device log or screenshot is redistributed. The original runtime C tests are unchanged from 1.1.3.
