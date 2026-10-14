# Clash Stability 1.2.0 — 一个安装包 / One installer

只统一安装流程，不重写已经通过验收的 CoC 注入程序。一个
`com.codex.clashstability` 包包含两个完整、原样保留设备签名的已验证程序：

| 安装时精确选择 | 使用的原程序 | 已知越狱文件组合 |
|---|---|---|
| iPad14,6 / 16.1 / 20B82 | 1.0.58 | Dopamine 3.0.11 |
| iPad7,2 / 17.7.11 / 21H461 | 1.1.0 | Dopamine 3.0.10 |

型号和系统构建通过 `sysctl` 查询，还必须完整匹配 systemhook / 生成 dyld
的 SHA256；未知组合在解包前拒绝安装。运行时继续由原程序校验游戏和越狱文件指纹。
这不是对所有 iOS 16–17 设备、未来 CoC 更新或账号安全的保证。

## 安装、迁移、卸载

退出 CoC，在 Sileo 中安装 **Clash Stability 1.2.0**，再打开 CoC。
原 iOS16 包直接升级；原 `com.codex.clashstability17` 与通用包互斥，
Sileo 迁移时需确认移除旧 iOS17 包。Choicy 自定义允许列表继续允许
**ClashTraceDiagnostic**，不需要改开关。没有自动重启，也不需要重启 SpringBoard。

仅 `TweakInject/ClashTraceDiagnostic.dylib` 及原 filter 被注入；两个只读程序副本
存放于 `usr/share/clash-stability/profiles`，不会被注入。`postinst` 检查已选副本
的完整散列，再通过同目录临时文件原子替换唯一活动程序，签名逐字节不变。
活动路径在 dpkg 文件清单中，卸载会清理，不留下失去包归属的注入文件。
活动路径是按设备生成的文件，因此没有提供错误的固定 md5sums。
安装时须关闭 CoC；异常中断的安装需要重新配置完成后再打开游戏。

不更改 CoC 游戏文件、数据、Choicy、网速、音量或虚拟 Mac；不加入新运行时
loader、不发送包管理器重启完成动作。历史正式 DEB/源码保留供回退，但 APT
活动索引最终只保留这个 CoC 包，不发布失败的测试包。

## 代码与构建

```sh
python3 sources/clash-stability-universal-1.2.0/test_release.py -v
python3 sources/clash-stability-universal-1.2.0/package.py --output /tmp/clash-universal.deb
```

构建会验证两份原正式 DEB、原程序和原 filter 的散列，拒绝未知输入。
测试涵盖两种选择、未知型号/构建、程序单字节损坏、越狱指纹改变、目录归档、
唯一注入文件、无重启命令和可复现 DEB。实际设备验收另见 `verification.json`。

新增 C 指纹函数和基线适配代码在
[iOS16 source](../clash-stability-1.0.58/README.md) 和
[iOS17 source](../clash-stability-ios17-1.1.0/README.md)。完整旧 C 源码仍未找回；
本目录提供完整通用安装器源码，不假称恢复了旧程序的全部 C 实现。

## English

One package selects exactly one unchanged, previously accepted and device-signed
runtime using the device model, OS build, and full known jailbreak-file SHA256s.
Qualified profiles only: iPad14,6/16.1/20B82 and iPad7,2/17.7.11/21H461.
The two original C fingerprint gates and checked baseline adaptations remain
linked above; the full historical C implementation remains unavailable.

Close CoC before installation and reopen afterward. The old iOS16 package upgrades
in place; Sileo must confirm replacement of the mutually exclusive old iOS17 ID.
Only one original dylib/filter is injectable. Read-only profile copies live outside
the injection directory. configure verifies the selected payload and atomically
replaces the dpkg-owned active file, preserving its complete signature. An interrupted
install must be configured successfully before launching CoC. No restart, runtime
loader, game-file change, or changes to other tweaks are included. Unknown profiles
are refused; no blanket future compatibility or indefinite stability is promised.
