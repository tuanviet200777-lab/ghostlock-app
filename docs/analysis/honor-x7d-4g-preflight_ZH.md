# HONOR X7d 4G：只读内核兼容性调查

**截至 2026-11-10：尚未验证，不属于已确认支持的设备。**
本文和配套脚本不是 root 方案。内核版本与安全补丁日期都不能证明
CVE-2026-43499 在具体设备上可利用。

## 公开信息和设备未知项

根据 HONOR 官方产品规格，X7d 4G 采用 Snapdragon 685，
MagicOS 9.0（Android 15），4G 型号有 **LGN-LX1、LGN-LX2、
LGN-LX3**。名称近似的 X7d **5G (LGN-NX1)** 属于不同型号。
第三方 LGN-LX2 记录提到内核 `5.15.180`，但这**不是**用户手机的
完整 `uname -r`，不能据此判断漏洞状态。

目前 GhostLock 的
`app/src/main/assets/kernel_profiles/index.conf` 中没有
已验证的 X7d 4G profile。配置必须与完整 `uname -r`
精确匹配，不能直接套用其他手机的配置。

## 无需 root 的只读信息收集

电脑需要 Python 3.9+、Android platform-tools（`adb`）、USB
数据线和手机上的调试授权。在仓库目录中运行：

```sh
python3 tools/probe_honor_x7d_4g.py > honor-x7d-4g-report.json
python3 -m unittest discover -s tools -p 'test_probe_honor_x7d_4g.py'
```

脚本仅调用固定白名单中的 `adb shell getprop` 查询、
`uname -r` 和 `cat /proc/version`。不会在手机上写入内容、
安装应用、启动 Shizuku、尝试 root 或刷写分区。
默认只接受一台已授权设备，连接多台时可用 `--serial` 指定。

输出不包含 ADB 序列号；脚本不收集 IMEI、账号、Android ID
或网络标识。不过，在共享报告前仍应检查构建属性和 fingerprint。
`support_status` 固定为 `UNVERIFIED_DO_NOT_RUN_EXPLOIT`，
不代表检测结果。

## 后续证据门槛

1. 在手机“关于手机”或包装盒上核对型号，避免混淆 4G 与 5G。
2. 保存完整 `kernel_release`、构建版本及安全补丁信息。
3. 仅使用与该构建匹配的可信原厂固件或内核材料进行离线分析，
   不得借用其他 Snapdragon 设备、其他内核版本的 offsets。
4. 检查厂商是否已针对相关问题回移安全修复；仅凭
   `uname -r` 或补丁日期无法下结论。
5. 只有配置字段、主机验证以及经明确授权的真机验证都通过后，
   才能把候选 profile 标记为 supported。
   未验证的攻击可能导致崩溃、重启或数据损失。

**明确保持不变：** 不修改攻击、竞争、后端及 payload 代码；
不放宽配置的精确匹配，不自动启动 root，不宣称设备已获支持。
本次只引入只读工具、单元测试与文档。

## 资料来源

- [HONOR 官方 X7d 规格](https://www.honor.com/global/phones/honor-x7d/spec/)
- [第三方 LGN-LX2 设备记录（非用户设备）](https://www.deviceinfo.app/devices/honor/x7d/)
- [4G / 5G 型号公开报道](https://www.thetechoutlook.com/tech-whispers/honor-x7d-4g-and-x7d-5g-smartphone-models-certified-by-the-tdra-authority-honor-x7d-4g-also-listed-on-the-google-play-console-database/)
- [GhostLock 配置移植指南](../kernel_profiles/README.md)

## 测试范围

在安装 Python 的主机上运行
`python3 -m unittest discover -s tools -p 'test_probe_honor_x7d_4g.py'`；
然后检查获授权 X7d 4G 的 JSON 报告。
单元测试使用 mock，不依赖手机。
尚无真机验证、构建或成功 root 的证明。
