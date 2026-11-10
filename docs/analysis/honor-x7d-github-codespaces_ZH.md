# HONOR X7d 4G：GitHub Codespaces 只读研究工作区

参见[英文指南](honor-x7d-github-codespaces.md)及
[越南语快速指南](../../.devcontainer/README.md)。

## 创建 Codespace

1. 打开 GitHub 仓库，选择 `tools/honor-x7d-firmware-readonly-analysis`
   分支（PR #3）。
2. 点击 **Code → Codespaces → Create codespace on this branch**。
3. GitHub 根据 `.devcontainer/devcontainer.json` 准备 Ubuntu 24.04、
   Python 3.12、Rust stable、Git LFS 及离线固件分析依赖。
4. 创建后自动运行两个 Python 单元测试套件，并在 Git 检出目录之外建立：
   `/workspaces/ghostlock-private/firmware/` 与
   `/workspaces/ghostlock-private/reports/`。

当前提交的是**工作区配置**，不是已经在机主账号内启动的 Codespace。
现有 GitHub 连接不具备创建或控制 Codespace 的功能。
Codespaces 使用时间和存储可能收费，请检查个人账号配额。

## 隐私及证据来源

仅处理经检查并有权使用的文件。不要上传 `userdata.img`、
`metadata.img`、`cache.img`、密钥分区或含个人资料的原始镜像。
工作区在 GitHub 云端运行；私有目录降低误提交风险，但**不是保密
保险箱或永久备份**。GitHub 文档说明 `/workspaces` 在容器重建后
保留，但删除 Codespace 或存储保留政策仍可能删除数据。

机主已在本对话中确认 **MagicOS 9.0.0.226**。此前误发的 GitHub
设备报告**不可作为设备识别或 root 结果的依据**。上传
`boot(2).img` 中的 kernel 字符串不等于手机实际测得的
`uname -r`。

云端 Codespace 通常无法直接读取插在本地电脑上的手机 USB 端口。
可在电脑本地收集并检查只读 ADB 报告，再决定是否传入云端。
不要公开设备唯一标识符。

## 离线读取 firmware 参数

将审查过的 boot、vendor_boot、版本文件复制到 Codespace 的
`ghostlock-private/firmware` 目录。在仓库根目录执行：

```bash
python3 tools/inspect_honor_firmware.py \
  --boot "/workspaces/ghostlock-private/firmware/boot(2).img" \
  --vendor-boot "/workspaces/ghostlock-private/firmware/vendor_boot(2).img" \
  --version-tag "/workspaces/ghostlock-private/firmware/version_by_CI(1).tag" \
  --out "/workspaces/ghostlock-private/reports/x7d-226-offline.json"
```

离线 Python 测试：

```bash
python3 -m unittest discover -s tools -p 'test_inspect_honor_firmware.py' -v
python3 -m unittest discover -s tools -p 'test_probe_honor_x7d_4g.py' -v
```

`.github/workflows/honor-firmware-tools.yml` 在指定的代码更改及
Pull Request 上检查 JSON/Bash 语法并运行 Python 测试，
不依赖 Android 编译。Rust `tools/extract_rs` 已在仓库内，
仅供**离线诊断**，本工作区不会自动执行漏洞利用、刷机、
生成攻击偏移或上传 firmware。

## 验证范围

CI 成功只代表脚本和语法检查通过，不证明 Codespace 容器镜像
已经构建成功。必须由用户在 GitHub 上实际创建 Codespace 才能
验证镜像与 Feature 安装。**未连接实体手机，也未验证 root。**

**明确保持不变：** Android App、C++ native 漏洞利用、GLK1 协议、
kernel profile、支持设备目录、`main`。
