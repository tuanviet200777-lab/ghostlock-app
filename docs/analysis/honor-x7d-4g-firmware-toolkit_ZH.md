# HONOR X7d 4G：只读固件信息检查工具

**目的：** 离线读取上传的固件文件格式、校验和、启动镜像内核版本，
并可与另行取得的只读 ADB 报告比较。**不尝试 root，不执行漏洞利用，
不刷机，不修改手机分区，也不连接网络。** 仅使用 Python 3.9+ 标准库。

机主在本对话中确认实际系统版本为 **MagicOS 9.0.0.226**。
此前误提交的 GitHub 报告**不可作为该手机的身份、内核或 root
执行结果的证据**。

## 变更范围与数据流（M 级）

此批次仅增加 §tools/inspect_honor_firmware.py§、
§tools/test_inspect_honor_firmware.py§ 和英/中文说明文档。
原始固件文件 → 只读文件头及 SHA-256 检查 → Android Boot v3/v4
受限范围内的内核版本字符串候选 → 可选 ADB 字段比较 → 本地 JSON。

**不修改** Android App、Rust extractor、C++ native、Kernel Profile、
§index.conf§、GLK1 格式或任何漏洞利用代码。不生成攻击偏移值。

## 在电脑上离线分析文件

将固件文件保存在电脑本地目录。于仓库根目录执行：

§§§sh
mkdir -p build
python3 tools/inspect_honor_firmware.py \
  --boot "/path/to/boot(2).img" \
  --vendor-boot "/path/to/vendor_boot(2).img" \
  --version-tag "/path/to/version_by_CI(1).tag" \
  --image "/path/to/vbmeta.img" \
  --image "/path/to/vendor_dlkm.img" \
  --out build/honor-x7d-4g-local-report.json \
  --summary-out build/honor-x7d-identity-summary.txt
§§§

可选的 §--summary-out§ 会另外保存一份越南语可读的证据摘要；
不改变原始 JSON。没有实体手机的 ADB 数据时，摘要标为“尚未比对”；
即使内核版本字符串一致，也**不能证明 GhostLock 支持 root**。
该摘要不会复制 ADB 原始属性或私有标识符。

§build/§ 已列入 Git 忽略规则。工具提取文件大小、SHA-256、
部分头部字段以及 kernel 中可能存在的 §Linux version§ 字符串。
**镜像中的内核版本不等于已确认的手机运行内核版本。**
Android sparse 展开后大小仅根据头部计算，并未逐块验证；
AVB 标识检查也**不等于验证数字签名**。

工具拒绝读取指定的敏感文件，包括 §userdata.img§、
§metadata.img§、§cache.img§、§persist.img§ 和部分密钥分区。
但其他镜像也可能包含私有或受版权保护的内容，禁止未经检查
就发布到公开仓库。

## 设计：最小化设备内核版本检查（M 级）

**原因：** 原 ADB 诊断会读取较多设备属性，包括 build fingerprint，
但当前仅需要手机实际运行的内核 release 字符串。应避免不必要的数据收集。

**范围：** `tools/probe_honor_x7d_4g.py` 新增可选 `--minimal`，
仅运行 `adb devices`（确认设备已授权）及
`adb shell uname -r`（只读内核版本）。`tools/inspect_honor_firmware.py`
将“未读取系统版本属性”和“明确不匹配”区分，并拒绝不安全的内核
版本字符串。更新对应的 Python 单元测试与英/中文说明文档。
保持旧的完整报告默认行为与 v1 schema，不要求 root、不写入设备。

**验证：** 使用 mock 确认只发出允许的 ADB 命令；
测试 match/mismatch/unknown，确认非法字符串不会进入输出；
GitHub Actions 运行两个 Python 测试组及 Dev Container 构建。
CI 不连接真实手机。

**明确保持不变：** Android APK、Rust extractor、C++ 漏洞利用、
kernel profiles、GLK1、设备支持名单。版本字符串匹配不能证明 root。

## 可选：用实际手机的只读 ADB 报告对照

电脑安装 Android platform-tools，连接机主自己的手机，
并完成 USB 调试授权后：

§§§sh
python3 tools/probe_honor_x7d_4g.py > build/honor-x7d-device-private.json
§§§

随后离线比对：

§§§sh
python3 tools/inspect_honor_firmware.py \
  --boot "/path/to/boot(2).img" \
  --device-report build/honor-x7d-device-private.json \
  --out build/honor-x7d-compared-private.json
§§§

§kernel_release_match§ 的结果为 §match§、§mismatch§ 或 §unknown§。
§match§ 只能说明版本字符串一致，**不能证明**二进制完全相同、
固件来自官方、内核存在漏洞或 root 已成功。

原始 ADB JSON 可能含有 build fingerprint。对比工具不会在
派生报告中复制 fingerprint、IMEI、序列号、账号或网络标识；
请仍然检查任何准备分享的报告。

## 已执行验证与结果

§§§sh
python3 -m unittest discover -s tools -p 'test_inspect_honor_firmware.py' -v
§§§

2026-11-10 已在本地 Python 3 环境中运行：**9/9 测试通过**。
已用会话中上传的文件实际运行只读分析：

| 上传文件 | 观察值 |
| --- | --- |
| §version_by_CI(1).tag§ | §9.0.0.226§ |
| §boot(2).img§ | Android Boot v4；SHA-256 §fa2be60595d903ac90c06638a650a5ce754f065e622307b298e18da93e7237d3§ |
| boot 镜像内部 kernel | §5.15.194-android13-8-00038-g853eb7b6b965-ab15936612§；ARM64 标识 |
| §vendor_boot(2).img§ | Android Vendor Boot v4 |
| §vbmeta.img§ | AVB 头，**未验证签名** |
| §vendor_dlkm.img§ | Android sparse 头 |

**没有连接实际手机或运行 root。** 仅测试新的 Python 工具；
未执行仓库级 NDK、Android、Rust、lint 或真机门禁测试。

## 进一步离线研究

仓库原有的 §tools/extract_rs§ 是独立的 Rust 内核分析器，
可使用 §--analysis§ 模式对 BTF 和 symbol 的可用性进行静态检查。
这种结果仍只是诊断材料，不能证明某设备可运行 GhostLock。
不能仅因工具能够解析镜像，就启用漏洞利用或把 profile 标记为
受支持。

**明确保持不变：** Native 漏洞利用、Kotlin 运行路径、GLK1
传输协议、内核偏移、已支持机型列表和手机分区。
