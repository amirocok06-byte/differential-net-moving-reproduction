# Differential Net-Moving / Xplace baseline 初步审计报告

审计日期：2026-09-20（Asia/Shanghai）

## 1. 总体结论

本机已有一套结构化的复现准备材料，但没有发现已完成的 DiffNet 或 Xplace-Route 论文级 baseline 实验。最准确的状态是：

> Preparation / evidence collection completed in part; paper-level baseline reproduction not yet executed.

不能把当前材料表述为“已经复现论文 baseline”。

## 2. 已完成到哪一步

| 复现环节 | 状态 | 证据与判断 |
|---|---|---|
| 论文识别与版本核对 | 已完成 | `paper/paper-local.pdf`、`paper/paper-author-web.pdf`；论文为 Li 等 DAC 2025。 |
| 论文实验框架定位 | 基本完成 | 论文实验段落写的是 Xplace；局部/全局布线评估涉及 GPU 3D Z-shape router 与 Innovus。 |
| 公开代码定位 | 已完成 | `repositories/Xplace`，`cuhk-eda/Xplace`，快照 commit `49cf66bc75ba9908f145bb6686f03cde692367cf`。未找到作者发布的 DiffNet 专用实现。 |
| DiffNet 专用源码/配置 | 未完成 | `configs/README.md` 和 `scripts/README.md` 明确记录未找到。 |
| ISPD2015 数据 | 部分完成 | 官方归档已下载并解压，SHA256 为 `AF4A352FDADDDF359B8CF997C113B3B0608F57B97CA5B23267C01039837575D9`；当前归档为 16 个设计。 |
| 论文完整 20-design 数据对齐 | 未完成 | Table I 和本地 DREAMPlace 配置均为 20 个设计；官方归档缺少 `mgc_matrix_mult_2`、`mgc_matrix_mult_c`、`mgc_superblue14`、`mgc_superblue19`。 |
| fence-region 去除处理 | 部分完成 | 独立 dirty Xplace worktree 已生成 16 个 `ispd2015_fix` 设计；桌面快照本身没有固定、可追溯的预处理输出。 |
| Xplace 编译/运行 | 部分完成 | 本机存在 `mgc_fft_1`、`mgc_fft_2`、`mgc_des_perf_1` 的 placement 输出和日志；不是完整对齐 benchmark。 |
| DiffNet net-moving 算法 | 部分完成 | 本机存在 DiffNet 原型、two-pin/multi-pin 诊断、归因张量和一设计 staged artifact；不是作者官方实现或完整论文 runner。 |
| 拥塞估计 | 部分完成 | 本机有 `mgc_fft_1` GGR map/metric 和 5-layer tensor；论文 router 版本、参数和输出身份尚未证明。 |
| Innovus global/detailed routing | 未完成 | 没有论文专用 Tcl/config、原始 route logs 或商业工具运行结果。 |
| 结果汇总 | 未完成 | 没有本机 DRWL、DRVias、DRVs、PT/RT 结果表。 |

综合判断：**当前应标记为 `PARTIAL_REPRODUCTION`。**已有真实局部执行与原型链路，但尚无完整 DiffNet、Xplace-Route、Innovus 和可比 DR 指标。

## 3. 论文与复现材料中的主要歧义

### 3.1 DREAMPlace 还是 Xplace

论文摘要/背景中出现 DREAMPlace，但实验实现段落明确写到算法部署在 Xplace 上，初始 global placement 使用 Xplace，最终采用 Xplace-Route 的 routability-driven legalization/detail placement。

处理：当前审计以“Xplace 为实现框架、Xplace-Route 为主要比较 baseline”记录；不把本地 DREAMPlace 配置候选误标为 DiffNet 实现。是否存在未公开的 DREAMPlace port，列为待作者确认问题。

### 3.2 16 个官方 ISPD2015 设计与论文 Table I 的 20 个设计不一致

官方归档已核验为真实 ISPD2015 数据，但缺少论文/本地配置中的四个设计：`mgc_matrix_mult_2`、`mgc_matrix_mult_c`、`mgc_superblue14`、`mgc_superblue19`。

处理：当前只允许声明“支持 16-design ISPD2015 数据准备”，不允许声明“完整复现论文 20-design Table I”。必须找到缺失设计的同源 benchmark 或向作者索取完整数据后再对齐。

### 3.3 fence-region 的处理

论文说明实验 benchmark 去除了 fence-region constraints；官方原始归档仍包含 fence/region 相关语法和 routing blockages。Xplace 需要其特定的 `ispd2015_fix` 预处理路径。CLI 审计发现独立 dirty worktree 已生成 16 个 fixed design。

处理：将预处理标记为部分完成，但不把 dirty worktree 输出视为已冻结、可复现的正式输入；后续应在 provenance-controlled 副本上重新核验并记录输入/输出清单和哈希。

### 3.4 router [18] 与拥塞输出格式

论文只给出 GPU 3D Z-shape global routing algorithm 的文献引用和方法描述，没有在现有材料中找到确定版本、grid/layer/capacity 参数或原始 demand/capacity snapshot。

处理：Xplace 中相关 GGR/CU-GR 接口只能作为框架参考；没有 router 版本与参数时，不把接口存在等同于论文拥塞估计已复现。

### 3.5 DiffNet 内部算法参数缺失

当前缺少完整可复现的 learning-rate、`lambda_2` 调度、two-pin/selected multi-pin 筛选阈值、随机种子、完整迭代次数、停止条件和 virtual-cell 规则。与此同时，本机已存在一部分 prototype、per-net attribution、Poisson/GGR tensor 和 staged artifact，但这些包含论文未明确说明的假设，不能等同于作者实现。

处理：列入 unresolved gaps；不得用 Xplace 默认参数或自行猜测参数替代论文专用配置。

### 3.6 “平均减少 40%”与论文表格归一化口径

论文摘要和正文宣称相对 Xplace-Route 平均 DRVs 减少 40%；正文另有“400% reduction”的表述，疑似措辞/排版错误。Table I 使用 Avg. Ratio，且脚注说明排除了 Xplace 在 superblue12 上的异常 DRV 结果。

处理：后续必须从 PDF 表格逐行重建原始 DRVs，并确认 ratio 的分母、被排除设计和平均方式；在此之前只引用“论文报告的 40% claim”，不把它当作已验证数值。

### 3.7 baseline 的定义

论文同时比较 Xplace（无 routability）与 Xplace-Route（routability-driven）。如果用户所说的 baseline 是“论文方法的直接 baseline”，应优先使用 Xplace-Route；如果是“基础 placement baseline”，则还需报告 Xplace。

处理：后续结果表必须同时列出 `Xplace`、`Xplace-Route`、`DiffNet/Ours`，并说明比较对象。

## 4. 论文性能与本机复现性能对比

### 4.1 论文中可读取的性能主张

论文报告：

- 相比 Xplace-Route，平均 DRVs 减少约 40%；
- DRWL 和 DR vias 保持可比；
- 论文表格指标包括 DRWL/um、#DRVias、#DRVs、placement time 和 routing time；
- 实验环境为 Linux、2.90GHz Intel Xeon、单张 NVIDIA A800；
- 使用同一版本 Cadence Innovus 对 placement 结果做 global/detailed routing。

这些是“论文报告值/主张”，不是本机实测值。

### 4.2 本机复现结果

当前没有完整可比的以下结果文件：

- 完整 20-design Xplace placement output；
- 完整 Xplace-Route placement/routing output；
- 完整 20-design DiffNet/Ours placement output；
- 与论文一致的 congestion demand/capacity snapshot；
- 已执行的 Innovus log/Tcl result；
- 可比的 DRWL、DRVias、DRVs、PT/RT 汇总表。

本机确实存在局部证据，例如 `mgc_fft_1` 的 Xplace GP/GGR 日志，以及 `mgc_des_perf_1` 的 DiffNet prototype/staged artifact；但它们使用 GP/GGR 内部指标或冻结注入流程，不是论文 Table I 的 Innovus detailed-routing 指标。

因此：

| 比较项 | 论文 | 本机复现 | 差值/结论 |
|---|---:|---:|---|
| DRWL | 有论文表格值/汇总 | 无 | 无法计算 |
| #DRVias | 有论文表格值/汇总 | 无 | 无法计算 |
| #DRVs | 报告相对 Xplace-Route 约 40% 改善 | 无 | 无法验证 |
| placement time | 有论文表格/汇总 | 无 | 无法计算 |
| routing time | 有论文表格/汇总 | 无 | 无法计算 |

CLI 逐行重建 Table I 后还发现：论文 Table I 实际包含 20 个设计；打印数值直接计算出的 DRV 改善约为 19–20%（取决于平均口径），并不直接支持正文的 40%/400% 表述。该论文内部口径问题仍需原始结果或作者澄清。

因此当前不能说“复现结果接近论文”，也不能说“复现失败”；正确表述是：**已有局部 reproduction trail，但尚未执行到产生可比性能结果的阶段。**

## 5. 可公开性/敏感内容边界

本审计包只保存审计结论、证据路径和待办事项，不复制 SSH 私钥、GitHub token、系统凭据或完整第三方源码。原始论文 PDF、数据归档和 Xplace 快照仍位于本机原路径，未被复制进本目录。
