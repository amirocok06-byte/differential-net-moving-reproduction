# Differential Net-Moving 复现包

本仓库整理本地 Differential Net-Moving / DiffNet 原型及其审计记录。

本仓库有意限定为“部分复现包”。它不是论文作者的官方实现，不包含完整的 Xplace 或 DREAMPlace 源码树，不包含 ISPD2015 benchmark 数据，也不声称完成论文的完整复现。

## 仓库内容

- `src/diffnet_prototype/`：本地编写或重构的 Python 原型模块、测试和小型审计工具。
- `src/diffnet_prototype/dreamplace-integration.patch`：两个可选的 DREAMPlace 集成钩子补丁；不包含上游 checkout。
- `configs/`：范围和配置说明。目前没有完整且严格对应论文的参数文件。
- `results/manifests/`：仅保存小型 JSON manifest 和元数据；不包含 tensor、checkpoint、DEF/LEF 数据或二进制文件。
- `results/small-logs/`：明确标注的小型 GP/GGR 日志；这些不是 Innovus Table I 结果。
- `docs/`：来源、假设、歧义和性能解释。
- `audit/`：初步审计报告和独立 CLI 复核报告。
- `scripts/`：安全的本地单元测试说明；不代表存在完整 benchmark runner。

## 来源与边界

原型来源于本地未清理的 DREAMPlace 研究分支，commit 为 `6627f3327e6cc17db7782c0b90073a498531ca3c`。Xplace 仅在来源文档中通过上游 URL 和 commit 引用；其源码树和生成数据均未纳入本仓库。

本包记录的状态为 `PARTIAL_REPRODUCTION`：本机存在部分 Xplace 预处理、placement、GGR 证据以及单个设计的 DiffNet 原型工件，但尚未形成完整的 20-design DiffNet/Xplace-Route/Innovus 链路，也没有可比的 `DRWL/#DRVias/#DRVs/PT/RT` 结果。

## 运行小型测试

如需运行集成测试，请使用已安装 PyTorch 的兼容 Python 环境，并从上游 DREAMPlace checkout 目录运行；只有在需要集成测试时才应用集成补丁。本包的原型测试规模很小，不会下载数据，也不会运行 placement benchmark：

```bash
./scripts/run_unit_tests.sh /path/to/DREAMPlace
```

这些测试只能证明辅助函数行为，不能证明论文端到端复现完成。
