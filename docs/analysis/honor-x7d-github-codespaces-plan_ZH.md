# 设计计划：GitHub Codespaces / HONOR 只读固件研究

状态：机主通过“làm đi”批准准备 Codespaces 配置。变更落在 PR #3
对应功能分支，不直接修改 `main`。

变更前分支基线：
`3fb1874b77936cae526c8164ba348ecf683607f1`。

## 需求

目前 Python 只读固件识别工具和 Rust extractor 已在仓库内，但每次
研究都需要自行准备环境。Codespaces 用于统一 Ubuntu、Python、
Rust 与离线分析依赖；**不会执行 root、漏洞利用、刷机或设备写入**。

## 范围

- `.devcontainer/devcontainer.json`：Codespaces、Python 3.12、
  Rust stable、Git LFS。
- `.devcontainer/Dockerfile`：Ubuntu 24.04 与只读分析依赖。
- `.devcontainer/post-create.sh`：初始化与 Git 分离的私有数据目录，
  运行现有 Python 测试。
- `.devcontainer/README.md`：越南语操作与隐私提示。
- `.github/workflows/honor-firmware-tools.yml`：只读 Python 工具的
  测试及 Dev Container 配置语法检查；还增加仅在 PR / 手动触发时运行的真实镜像构建，
  通过 `devcontainers/ci@v0.3` 安装 Features、运行只读测试，`push: never` 不发布容器镜像。
- `docs/analysis/honor-x7d-github-codespaces.md` 与 `_ZH.md`：
  操作、保密和边界。
- `docs/analysis/honor-x7d-github-codespaces-plan.md` 与本文件：
  设计与验证记录。

不触碰 Android app、C++ native、Rust extractor 行为、kernel profile、
GLK1 wire 格式、支持机型名单。

## 数据流及变更行为

1. 机主在 GitHub 的 PR #3 功能分支创建 Codespace。
2. 容器安装 Python、Rust、基础构建及固件头部分析所需软件。
3. postCreate 在 `/workspaces/ghostlock-private/` 下创建
   `firmware/`、`reports/`，它们**不属于仓库 Git 检出目录**，
   因而不会被根目录中的 `git add .` 意外提交。
4. 用户只上传经确认允许处理的固件文件；不上传
   `userdata.img`、密钥分区、隐私 dump。
5. 现有只读 inspector 生成 JSON 报告，仅保留于私有目录。
6. GitHub Actions 在相关 PR/代码推送时执行 Python 测试。

## 安全、兼容与回退

- Codespaces 不会自动访问机主电脑的 USB 手机。任何设备只读 ADB
  报告在电脑本地收集，分享前由机主核查。
- Codespaces 云端存储会产生配额/收费，且不是永久备份。
  `/workspaces` 通常在容器重建后保留，但删除 Codespace 可能
  导致数据消失。
- 不自动执行 C++ 漏洞利用，不生成攻击偏移、不刷机、不改变 profile。
- 关闭 PR 或撤销本分支配置提交即可回退；`main` 不变。

## 验证计划

| 项目 | 验证目标 |
| --- | --- |
| JSON 语法 | `.devcontainer/devcontainer.json` |
| Bash 语法 | `.devcontainer/post-create.sh` |
| Python 单元测试 | `test_inspect_honor_firmware.py`、
`test_probe_honor_x7d_4g.py` |
| GitHub Actions | 查看 PR 对应检查的实际结果 |
| Dev Container CI 构建 | 在 runner 上构建完整镜像并运行无设备测试，不代表实际创建 Codespace |
| 真正创建 Codespace | 由机主在 GitHub 上启动后验证 Feature 安装 |
| Git diff | 确认仅修改上述工具/文档配置，不影响 native |

**注意：** JSON/CI 检查成功不代表 Dev Container 镜像已经成功构建；
本次没有实体手机验证、root 成功或漏洞利用执行。

**明确保留不变：** C++ 漏洞利用、GLK1、Kernel Profile、
支持设备目录、Rust 分析器逻辑、Android 应用和原始固件分区字节。
