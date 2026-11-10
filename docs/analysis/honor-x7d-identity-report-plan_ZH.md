# 方案：HONOR X7d 固件身份摘要（只读）

**级别：** M，仅修改离线 Python 输出、测试和文档，不涉及攻击流程。

## 动机与证据范围

机主希望明确知道 MagicOS 9.0.0.226 的 HONOR X7d 4G 当前验证到了哪一步。
已检查的 boot 镜像包含 ARM64 kernel 版本字符串，但这并非从实体手机
采集的 `uname -r`；通用 APK 编译成功不代表设备受支持。

## 修改范围和数据流

- `tools/inspect_honor_firmware.py`：增加可选 `--summary-out`，
  保存简短的只读、可读摘要，不改变原有 JSON。
- `tools/test_inspect_honor_firmware.py`：验证无设备报告、匹配、
  不匹配、未知以及隐私字段不会外泄。
- `docs/analysis/honor-x7d-4g-firmware-toolkit.md` 及中文版、
  `.devcontainer/README.md`：给出使用说明。
- 本方案及英文版。

原有固件解析器 -> 可选的 ADB 字符串比对 -> JSON + 可选文本摘要。
不新增设备查询、网络访问、自动上传或执行漏洞利用。

即使 kernel 版本字符串相同，也不能证明固件真伪、二进制相同、
漏洞存在、GhostLock 兼容或成功 root。

## 验证与保留

用合成数据运行 Python 单元测试，并检查 GitHub Actions 的实际结果。
不修改 Android、C++/Rust 攻击代码、GLK1、profile、内核偏移、
设备数据或固件内容。选项默认为关闭，可独立回退。
