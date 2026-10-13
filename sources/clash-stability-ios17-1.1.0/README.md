# Clash Stability iPadOS 17 1.1.0

Isolated adapter for **iPad7,2 / iPadOS 17.7.11 (21H461)** with the known
Dopamine 3.0.10 binary profile and CoC 18.647.2. The iPadOS 16.1 package 1.0.58
is unchanged. This package conflicts with the unified legacy package, rather
than loading two adapters into the game.

The original complete legacy C source is still unavailable. Included here:
original new fingerprint C source, a hash-pinned baseline adaptation builder,
and an exact release packager. The baseline is in the 1.0.57 source directory.
No game, Apple or jailbreak framework binaries are distributed.

Three iOS17 version-only comparisons now verify complete known magicx,
systemhook and generated-dyld files. Different version numbers are accepted
only when these files match; unknown fingerprints fail closed. This is not
a promise of compatibility with every future game or jailbreak update.

The worker snapshot now recognizes **only its own exact kind-4 image** in
addition to the existing qualified kinds 1/5/6. It keeps native-header,
cached UUID, exact path/root, complete exclusion-count and bitmap checks.
There is no global image-list rewrite, fatal suppression, forced success,
system-daemon hook or restart script. The iOS16 instruction region and all
baseline profile constants remain unchanged.

Build on macOS with Xcode command-line tools and your own iOS SDK:

```sh
python3 build.py --sdk /path/to/iPhoneOS.sdk --output build/ClashTraceDiagnostic.dylib
```

Build output is a locally signed candidate, not an acceptance test. Device
signing is required for the exact jailbreak environment. `package.py` admits
only the verified release payload hash; see `verification.json`.

## 中文

此包只适配 iPad7,2 / iPadOS 17.7.11 / 已知 Dopamine 3.0.10 文件组合。
它与旧合并包互斥，不会影响另一台 iPad 上的 16.1 正式版。
按完整文件指纹判断兼容性，不单看游戏版本号；文件改变后仍须重新适配。
修正了旧 17 路径漏掉自身 kind-4 插件的 worker 快照问题，仍严格核对身份、
路径和完整集合，不把所有插件都隐藏，也不伪造检查成功。

安装时让 Sileo/Zebra 移除冲突的旧 Clash Stability；只重开 CoC 即可。
若使用 Choicy 允许列表，需要允许 **ClashTraceDiagnostic**，不是包显示名称。
本包没有重启脚本。完整历史 C 源码仍未找回，公开的是新增 C 指纹函数与可审核
的适配/打包代码。实机结果见验收记录；不保证未来所有游戏版本或账号安全。
