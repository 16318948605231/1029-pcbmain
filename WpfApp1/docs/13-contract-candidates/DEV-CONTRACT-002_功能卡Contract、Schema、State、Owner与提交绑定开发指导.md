# 功能卡 Contract、Schema、State、Owner 与提交绑定开发指导

> 文档 ID：`DEV-CONTRACT-002`；版本：`0.2.3-prep`；状态：`DesignReview`。本页是现有 C-01～C-08 候选合同到 72 个功能卡的绑定登记，不是批准 Schema、API、枚举或生产资格。

本页解决“一个功能卡到底依赖哪些权威、谁执行、谁判定、谁提交、失败如何传播”的设计欠账。它不复制字段表，不创建通用业务对象，也不把候选语义变成可直接编译的 DTO。唯一合同正文仍是 [CONTRACT-CANDIDATES](CONTRACT-CANDIDATES.md)，公共能力由 [INTERFACE-MAP](../shared-modules/INTERFACE-MAP.md) 和对应 SM/PKG 指导拥有，工艺含义由 PG/FS 拥有。

## 1. 绑定原则

1. 每个功能卡绑定原领域与页面投影 Owner；涉及生产事实时绑定唯一原提交 Owner。目标生成、纯计算或只读查询不会因本表出现“提交”而取得事实写权，也不要求每个算法阶段各提交一份事实；公共模块只交出其公开能力。
2. `C-01` 身份/尝试、`C-02` 程序/资产、`C-03` 坐标/计量、`C-04` 结果/提交、`C-05` UI、`C-07` 性能/恢复、`C-08` 路由/覆盖按任务需要绑定；`C-06` 只在适配器/部署切片加入，不能由功能卡猜硬件 SDK。
3. 计算成功、业务合格、事实提交、设备回执和质量放行是不同事件。任何功能卡不得用 UI 保存、用 AI 分数代替量测、用 ACK 代替 Applied/Committed 或用缺项压成零值。
4. 所有状态均是现有状态候选的映射提示，不新增平行状态机；真正枚举、CAS、幂等键、事务边界和错误码由原 Contract Owner 串行采纳。
5. 本表“PG确认”表示使用该工艺已采纳的适用性、量测和判定规则，由原应用/领域 Owner接收；是否需要人工审核由原政策决定，不能据此增加每板人工审批。保存合法NG/Unknown/未测的事实与诊断，必须沿040的证据政策和提交权限；既不以质量通过作为入库前提，也不允许结构损坏、身份冲突或无写权请求绕过提交门。

## 2. 绑定剖面（Profile）

|Profile|C候选绑定|输入与输出边界|执行/判定/提交Owner|状态与失败断言|
|---|---|---|---|---|
| `B-GEO` | C-01/02/03/04/07/08 | 输入快照、目标/程序、原帧/有效域、坐标/标定；输出类型化候选/量测和无效原因 | SM-010/011 + 对应PG；SM-019规则比较；有生产提交时沿SM-020 | Prepared→Executing→Evaluated / Unevaluated；PG必检完整性如实随结果保留，不作所有结果的保存前提。040核身份/权限/最小提交证据；Replay完整性及质量放行另判，迟到/取消/回执未知保持原attempt |
| `B-AI` | C-01/02/03/04/07/08 | B-GEO全部输入 + 模型/特征库/预处理/阈值闭包；输出Candidate/Heatmap/拒识和模型证据 | PKG-052仅执行获准的AI候选；SM-026治理；PG/SM-019决定是否纳入工艺链，SM-020按原Owner提交 | Prepared→Executing→CandidateProduced / Rejected / Unevaluated；低置信/OOD/OOM/超时不可伪造PASS，AI不可替代缺失量测 |
| `B-3D` | C-01/02/03/04/07/08 | HeightField/点云、参考面、有效支持、坐标/标定、标准件绑定；输出带不确定度的可见表面量测 | SM-012/010执行；PG持工艺含义；SM-019/020持规则/事实 | Prepared→Executing→Measured / Unevaluated；缺测/遮挡/内部不可见不补值，不由2D推3D |
| `B-OCR` | C-01/02/03/04/05/07/08 | 文字ROI/原帧/期待字段来源、字符集/词表/模型闭包；输出RawRead、NormalizedRead、Suggestion、Content/Shape结果 | SM-011持识读执行；SM-024仅在已接入时传递外部来源，不持识别算法；PG持期待字段/质量语义；SM-020持证据 | RawRead→Normalized→Compared / Rejected；期待值不能覆盖原读，低分/字典外/超时进入拒识/人工 |
| `B-STAT` | C-01/04/05/07/08 | 已提交事实、明确观察单位/分母/水位/权限和统计Profile；输出报告/NotQualified投影 | SM-023计算/投影；原质量Owner决定；不写InspectionFact | Requested→Computing→Qualified / NotQualified / Insufficient；缺项/分母不足不删除样本 |
| `B-ASSIST` | C-01/04/05/07/08 | 已授权证据、相似样本/候选、角色和可选模型闭包；输出Suggestion/Candidate/Draft | SM-026只提供建议/检索/排序；SM-022人工复判或PG处置Owner作出决定并按批准事务提交；不写机判/质量放行/设备命令 | Requested→Suggested→Accepted / Rejected / Expired；证据不足、AI不可用或权限失效必须保留人工路径，采纳不等于事实已提交 |
| `B-QUERY` | C-01/04/05/07/08 | 类型化身份/过滤/游标/水位/权限/证据读取意图；输出只读页、Partial或错误 | SM-020/021/023按各自读取权；不建立万能SQL/第二事实库 | Requested→Reading→Complete / Partial / Failed；索引迟到/断网/权限不足显式返回 |

## 3. 72个功能卡绑定矩阵

每行均对应一个现有 PG 功能卡。`Profile` 只提供合同/Owner/状态绑定的最小结构；功能名称、工艺公差、不可观测范围和验收样本仍以链接的 PG/FS 为准。页面由对应 PageContract 消费该 Profile 的只读投影，不能由本表推导新页面命令。

|功能卡|Profile|C候选与直接消费者|提交/回执边界|
|---|---|---|---|
| [pg-001-f01 F01 批次/料号/面别核对](../process-guides/processes/PG-001_incoming-material.md#pg-001-f01) | `B-OCR` | `C-01/02/03/04/05/07/08`；SM-011识读、SM-017身份解析，工艺含义由 PG 保留。 | SM-017保存IdentityResolutionReceipt；只有PG/质量Owner确认后才由SM-020提交InspectionFact/Evidence，未知回执查原operation。 |
| [pg-001-f02 F02 表面污染/划伤/异物候选](../process-guides/processes/PG-001_incoming-material.md#pg-001-f02) | `B-AI` | `C-01/02/03/04/07/08`；SM-011/013 等经典能力先行；PKG-052 仅按 DEV-AI-064 提供 Candidate/Shadow/Advice，SM-026治理，工艺含义由 PG 保留。 | SM-020仅保存候选/证据；原PG/质量Owner决定是否形成事实。 |
| [pg-001-f03 F03 外形/厚度](../process-guides/processes/PG-001_incoming-material.md#pg-001-f03) | `B-GEO` | `C-01/02/03/04/07/08`；执行 SM-010/011，工艺含义由 PG 保留。 | SM-020提交PG确认的InspectionFact/Evidence；未知回执查原operation，不重试生成新事实。 |
| [pg-002-f01 F01 孔目标对应](../process-guides/processes/PG-002_drill.md#pg-002-f01) | `B-GEO` | `C-01/02/03/04/07/08`；SM-014制造来源、SM-008坐标和SM-011候选组合，孔型语义由 PG 保留。 | 保存目标↔候选映射和未匹配证据；只有PG确认的量测/判定才由SM-020提交InspectionFact/Evidence。 |
| [pg-002-f02 F02 孔径/圆度/槽宽](../process-guides/processes/PG-002_drill.md#pg-002-f02) | `B-GEO` | `C-01/02/03/04/07/08`；执行 SM-010/011，工艺含义由 PG 保留。 | SM-020提交PG确认的InspectionFact/Evidence；未知回执查原operation，不重试生成新事实。 |
| [pg-002-f03 F03 位置/缺多孔](../process-guides/processes/PG-002_drill.md#pg-002-f03) | `B-GEO` | `C-01/02/03/04/07/08`；执行 SM-010/011，工艺含义由 PG 保留。 | SM-020提交PG确认的InspectionFact/Evidence；未知回执查原operation，不重试生成新事实。 |
| [pg-003-f01 F01 开口几何](../process-guides/processes/PG-003_laser-via.md#pg-003-f01) | `B-GEO` | `C-01/02/03/04/07/08`；执行 SM-010/011，工艺含义由 PG 保留。 | SM-020提交PG确认的InspectionFact/Evidence；未知回执查原operation，不重试生成新事实。 |
| [pg-003-f02 F02 底部/残留可见性](../process-guides/processes/PG-003_laser-via.md#pg-003-f02) | `B-AI` | `C-01/02/03/04/07/08`；SM-011/013 等经典能力先行；PKG-052 仅按 DEV-AI-064 提供 Candidate/Shadow/Advice，SM-026治理，工艺含义由 PG 保留。 | SM-020仅保存候选/证据；原PG/质量Owner决定是否形成事实。 |
| [pg-003-f03 F03 深度/锥形候选](../process-guides/processes/PG-003_laser-via.md#pg-003-f03) | `B-3D` | `C-01/02/03/04/07/08`；执行 SM-012/010，工艺含义由 PG 保留。 | SM-020提交PG确认的InspectionFact/Evidence；未知回执查原operation，不重试生成新事实。 |
| [pg-004-f01 F01 层堆叠核对](../process-guides/processes/PG-004_layer-registration.md#pg-004-f01) | `B-GEO` | `C-01/02/03/04/07/08`；SM-014执行结构与层引用校验，工艺含义由 PG 保留。 | 保存结构校验回执/冲突；不把层栈一致性直接写成InspectionFact，程序/质量Owner决定后续提交。 |
| [pg-004-f02 F02 可见基准偏差](../process-guides/processes/PG-004_layer-registration.md#pg-004-f02) | `B-GEO` | `C-01/02/03/04/07/08`；执行 SM-010/011，工艺含义由 PG 保留。 | SM-020提交PG确认的InspectionFact/Evidence；未知回执查原operation，不重试生成新事实。 |
| [pg-004-f03 F03 积层目标生成](../process-guides/processes/PG-004_layer-registration.md#pg-004-f03) | `B-GEO` | `C-01/02/03/04/07/08`；SM-014生成来源目标，SM-016管理程序草稿，工艺含义由 PG 保留。 | 保存版本化目标草稿和来源闭包；不直接提交InspectionFact，需由035验证/发布链接收。 |
| [pg-005-f01 F01 填充覆盖](../process-guides/processes/PG-005_via-fill.md#pg-005-f01) | `B-AI` | `C-01/02/03/04/07/08`；SM-011/013 等经典能力先行；PKG-052 仅按 DEV-AI-064 提供 Candidate/Shadow/Advice，SM-026治理，工艺含义由 PG 保留。 | SM-020仅保存候选/证据；原PG/质量Owner决定是否形成事实。 |
| [pg-005-f02 F02 凹陷/凸起](../process-guides/processes/PG-005_via-fill.md#pg-005-f02) | `B-3D` | `C-01/02/03/04/07/08`；执行 SM-012/010，工艺含义由 PG 保留。 | SM-020提交PG确认的InspectionFact/Evidence；未知回执查原operation，不重试生成新事实。 |
| [pg-005-f03 F03 研磨纹理/残料](../process-guides/processes/PG-005_via-fill.md#pg-005-f03) | `B-AI` | `C-01/02/03/04/07/08`；SM-011/013 等经典能力先行；PKG-052 仅按 DEV-AI-064 提供 Candidate/Shadow/Advice，SM-026治理，工艺含义由 PG 保留。 | SM-020仅保存候选/证据；原PG/质量Owner决定是否形成事实。 |
| [pg-006-f01 F01 开窗/对位](../process-guides/processes/PG-006_soldermask-legend.md#pg-006-f01) | `B-GEO` | `C-01/02/03/04/07/08`；执行 SM-010/011，工艺含义由 PG 保留。 | SM-020提交PG确认的InspectionFact/Evidence；未知回执查原operation，不重试生成新事实。 |
| [pg-006-f02 F02 破损/异物/露铜候选](../process-guides/processes/PG-006_soldermask-legend.md#pg-006-f02) | `B-AI` | `C-01/02/03/04/07/08`；SM-011/013 等经典能力先行；PKG-052 仅按 DEV-AI-064 提供 Candidate/Shadow/Advice，SM-026治理，工艺含义由 PG 保留。 | SM-020仅保存候选/证据；原PG/质量Owner决定是否形成事实。 |
| [pg-006-f03 F03 字符内容/位置](../process-guides/processes/PG-006_soldermask-legend.md#pg-006-f03) | `B-OCR` | `C-01/02/03/04/05/07/08`；SM-011执行识读/视觉候选，期待字段及工艺含义由PG保留；SM-024仅在已接入时承接外部来源。 | SM-020提交PG确认的InspectionFact/Evidence；未知回执查原operation，不重试生成新事实。 |
| [pg-007-f01 F01 处理区域核对](../process-guides/processes/PG-007_surface-finish.md#pg-007-f01) | `B-GEO` | `C-01/02/03/04/07/08`；SM-013计算观测覆盖，SM-011仅提供区域候选，工艺含义由 PG 保留。 | 保存应处理/已观测/未知域和覆盖证据；覆盖不足不直接判缺陷，SM-020只提交PG确认的事实。 |
| [pg-007-f02 F02 污染/氧化样态候选](../process-guides/processes/PG-007_surface-finish.md#pg-007-f02) | `B-AI` | `C-01/02/03/04/07/08`；SM-011/013 等经典能力先行；PKG-052 仅按 DEV-AI-064 提供 Candidate/Shadow/Advice，SM-026治理，工艺含义由 PG 保留。 | SM-020仅保存候选/证据；原PG/质量Owner决定是否形成事实。 |
| [pg-007-f03 F03 划伤/缺损](../process-guides/processes/PG-007_surface-finish.md#pg-007-f03) | `B-AI` | `C-01/02/03/04/07/08`；SM-011/013 等经典能力先行；PKG-052 仅按 DEV-AI-064 提供 Candidate/Shadow/Advice，SM-026治理，工艺含义由 PG 保留。 | SM-020仅保存候选/证据；原PG/质量Owner决定是否形成事实。 |
| [pg-008-f01 F01 覆盖膜开窗](../process-guides/processes/PG-008_fpc-coverlay.md#pg-008-f01) | `B-GEO` | `C-01/02/03/04/07/08`；执行 SM-010/011，工艺含义由 PG 保留。 | SM-020提交PG确认的InspectionFact/Evidence；未知回执查原operation，不重试生成新事实。 |
| [pg-008-f02 F02 补强存在/方向/边界](../process-guides/processes/PG-008_fpc-coverlay.md#pg-008-f02) | `B-GEO` | `C-01/02/03/04/07/08`；执行 SM-010/011，工艺含义由 PG 保留。 | SM-020提交PG确认的InspectionFact/Evidence；未知回执查原operation，不重试生成新事实。 |
| [pg-008-f03 F03 翘起/弯折区](../process-guides/processes/PG-008_fpc-coverlay.md#pg-008-f03) | `B-3D` | `C-01/02/03/04/07/08`；执行 SM-012/010，工艺含义由 PG 保留。 | SM-020提交PG确认的InspectionFact/Evidence；未知回执查原operation，不重试生成新事实。 |
| [pg-009-f01 F01 过渡区边界](../process-guides/processes/PG-009_rigid-flex.md#pg-009-f01) | `B-GEO` | `C-01/02/03/04/07/08`；执行 SM-010/011，工艺含义由 PG 保留。 | SM-020提交PG确认的InspectionFact/Evidence；未知回执查原operation，不重试生成新事实。 |
| [pg-009-f02 F02 局部外观/弯折限制区](../process-guides/processes/PG-009_rigid-flex.md#pg-009-f02) | `B-AI` | `C-01/02/03/04/07/08`；SM-011/013 等经典能力先行；PKG-052 仅按 DEV-AI-064 提供 Candidate/Shadow/Advice，SM-026治理，工艺含义由 PG 保留。 | SM-020仅保存候选/证据；原PG/质量Owner决定是否形成事实。 |
| [pg-009-f03 F03 局部台阶/尺寸](../process-guides/processes/PG-009_rigid-flex.md#pg-009-f03) | `B-3D` | `C-01/02/03/04/07/08`；执行 SM-012/010，工艺含义由 PG 保留。 | SM-020提交PG确认的InspectionFact/Evidence；未知回执查原operation，不重试生成新事实。 |
| [pg-010-f01 F01 外形/槽位](../process-guides/processes/PG-010_outline.md#pg-010-f01) | `B-GEO` | `C-01/02/03/04/07/08`；执行 SM-010/011，工艺含义由 PG 保留。 | SM-020提交PG确认的InspectionFact/Evidence；未知回执查原operation，不重试生成新事实。 |
| [pg-010-f02 F02 毛刺/崩边候选](../process-guides/processes/PG-010_outline.md#pg-010-f02) | `B-AI` | `C-01/02/03/04/07/08`；SM-011/013 等经典能力先行；PKG-052 仅按 DEV-AI-064 提供 Candidate/Shadow/Advice，SM-026治理，工艺含义由 PG 保留。 | SM-020仅保存候选/证据；原PG/质量Owner决定是否形成事实。 |
| [pg-010-f03 F03 V槽几何](../process-guides/processes/PG-010_outline.md#pg-010-f03) | `B-3D` | `C-01/02/03/04/07/08`；执行 SM-012/010，工艺含义由 PG 保留。 | SM-020提交PG确认的InspectionFact/Evidence；未知回执查原operation，不重试生成新事实。 |
| [pg-011-f01 F01 双面外观覆盖](../process-guides/processes/PG-011_final-avi.md#pg-011-f01) | `B-GEO` | `C-01/02/03/04/07/08`；SM-013负责双面覆盖/完整性，SM-011/012负责各面方法，工艺含义由 PG 保留。 | 保存两面结果与完整性；缺一面不得全板放行，SM-020提交PG确认的InspectionFact/Evidence。 |
| [pg-011-f02 F02 翘曲量测](../process-guides/processes/PG-011_final-avi.md#pg-011-f02) | `B-3D` | `C-01/02/03/04/07/08`；执行 SM-012/010，工艺含义由 PG 保留。 | SM-020提交PG确认的InspectionFact/Evidence；未知回执查原operation，不重试生成新事实。 |
| [pg-011-f03 F03 终检项目聚合](../process-guides/processes/PG-011_final-avi.md#pg-011-f03) | `B-GEO` | `C-01/02/03/04/07/08`；SM-019执行确定性聚合，SM-020负责提交，SM-023仅作统计投影，工艺含义由 PG 保留。 | 只提交按批准规则形成的聚合事实和引用；统计报告不能替代机判/放行，未知回执查原operation。 |
| [pg-012-f01 F01 Web坐标](../process-guides/processes/PG-012_r2r.md#pg-012-f01) | `B-GEO` | `C-01/02/03/04/07/08`；SM-008坐标、SM-017区段/尝试身份，R2R包解释工艺语义。 | 保存带epoch/计数质量的坐标映射；不直接写InspectionFact，后续覆盖/量测由原Owner提交。 |
| [pg-012-f02 F02 区段覆盖/接带](../process-guides/processes/PG-012_r2r.md#pg-012-f02) | `B-AI` | `C-01/02/03/04/07/08`；SM-013按并集计算覆盖与缺口，AI仅可提供候选，R2R包定义接带/废料语义。 | 保存覆盖、重叠、缺口和接带证据；SM-020仅提交PG确认的事实，AI候选不能替代覆盖完整性。 |
| [pg-012-f03 F03 局部非刚性变换](../process-guides/processes/PG-012_r2r.md#pg-012-f03) | `B-AI` | `C-01/02/03/04/07/08`；SM-008/011先执行经典局部配准，PKG-052仅候选对照，R2R包定窗口/时域。 | 保存变换候选、可逆性/支撑和失效域；只有经PG/质量Owner确认的量测事实才交SM-020提交。 |
| [pg-013-f01 F01 开口几何与位置](../process-guides/processes/PG-013_stencil.md#pg-013-f01) | `B-GEO` | `C-01/02/03/04/07/08`；执行 SM-010/011，工艺含义由 PG 保留。 | SM-020提交PG确认的InspectionFact/Evidence；未知回执查原operation，不重试生成新事实。 |
| [pg-013-f02 F02 堵孔/污染](../process-guides/processes/PG-013_stencil.md#pg-013-f02) | `B-AI` | `C-01/02/03/04/07/08`；SM-011/013 等经典能力先行；PKG-052 仅按 DEV-AI-064 提供 Candidate/Shadow/Advice，SM-026治理，工艺含义由 PG 保留。 | SM-020仅保存候选/证据；原PG/质量Owner决定是否形成事实。 |
| [pg-013-f03 F03 厚度/侧壁](../process-guides/processes/PG-013_stencil.md#pg-013-f03) | `B-3D` | `C-01/02/03/04/07/08`；执行 SM-012/010，工艺含义由 PG 保留。 | SM-020提交PG确认的InspectionFact/Evidence；未知回执查原operation，不重试生成新事实。 |
| [pg-014-f01 F01 焊盘/开口目标](../process-guides/processes/PG-014_spi.md#pg-014-f01) | `B-GEO` | `C-01/02/03/04/07/08`；032制造资料、034参考能力与035程序草稿；055B保留印刷意图、pad/开口/沉积组和独立参考语义。 | 目标生成输出工程草稿，经035原协议保存/发布；不形成InspectionFact。生产使用已激活的精确程序，不能用未保存候选替换在途输入。 |
| [pg-014-f02 F02 参考面与高度质量](../process-guides/processes/PG-014_spi.md#pg-014-f02) | `B-3D` | `C-01/02/03/04/07/08`；055A/B选择采集/参考路线；012同步帧组、013质量、027表面数据、028重建（DEV-VIS-027方法）、029/030参考与量测、018实际覆盖各守原职责。 | 返回本尝试的HeightField/参考、实际支持及失败证据，交后续量测/规则；本阶段不自行提交板级事实。结果由F05沿039/040接收，缺支持不补值。 |
| [pg-014-f03 F03 锡膏分割/连桥](../process-guides/processes/PG-014_spi.md#pg-014-f03) | `B-GEO` + `B-3D` | `C-01/02/03/04/07/08`；055C持材料解释/关联与桥判据；025三态分割、030几何/关系、018实际支持；3D输入沿055A/B，AI只在已批准候选路径接入。 | 返回固定F/B/U、局部物理关系及连通/未知证据供F04/F05；不是纯高度量测，也不把每个候选当一份已提交事实。 |
| [pg-014-f04 F04 量测](../process-guides/processes/PG-014_spi.md#pg-014-f04) | `B-3D` | `C-01/02/03/04/07/08`；055C定义面积/体积/高度/偏移及各分母；030执行有限支持积分、矩与分位，029/055持参考/资格能力。 | 返回具名量、单位、原支持和质量给039；合法超差与不可测分别保留。由F05沿040提交，纯计算不持提交权、不等待自身未来回执。 |
| [pg-014-f05 F05 判定/SPC/反馈](../process-guides/processes/PG-014_spi.md#pg-014-f05) | `B-GEO` + `B-STAT` | `C-01/02/03/04/05/07/08`；055D/PG持工艺；039规则→原领域Owner机判→040提交；042精确查询→045统计；原设备应用Owner授权命令→047交付，037/048绑定实际印刷尝试/生效范围。设备适配切片另接C-06。 | 统计/建议只能读已提交事实，不能反向阻塞其提交。提案、交付、ACK、Applied及后效各守原身份/权威；保存Unknown查原提交，设备Unknown查原命令。分母不足只阻相应统计/建议，不抹原事实、不自动调机。 |
| [pg-015-f01 F01 资料一致性](../process-guides/processes/PG-015_pcba-incoming.md#pg-015-f01) | `B-GEO` | `C-01/02/03/04/07/08`；SM-014负责制造资料接入/结构一致性校验，SM-015提供封装/参考资产，SM-017仅负责目标身份关联；不由 SM-010/011 把视觉候选冒充资料事实，工艺含义由 PG 保留。 | 保存来源差异、缺失/冲突和目标草稿引用；只有 PG 确认后 SM-020 才提交 InspectionFact/Evidence，未知回执查原operation，不重试生成新事实。 |
| [pg-015-f02 F02 标记/方向](../process-guides/processes/PG-015_pcba-incoming.md#pg-015-f02) | `B-OCR` | `C-01/02/03/04/05/07/08`；SM-011执行识读/视觉候选，期待字段及工艺含义由PG保留；SM-024仅在已接入时承接外部来源。 | SM-020提交PG确认的InspectionFact/Evidence；未知回执查原operation，不重试生成新事实。 |
| [pg-015-f03 F03 首件位置](../process-guides/processes/PG-015_pcba-incoming.md#pg-015-f03) | `B-3D` | `C-01/02/03/04/07/08`；执行 SM-012/010，工艺含义由 PG 保留。 | SM-020提交PG确认的InspectionFact/Evidence；未知回执查原operation，不重试生成新事实。 |
| [pg-016-f01 F01 胶点关联/路径连续性](../process-guides/processes/PG-016_dispense.md#pg-016-f01) | `B-GEO` | `C-01/02/03/04/07/08`；执行 SM-010/011，工艺含义由 PG 保留。 | SM-020提交PG确认的InspectionFact/Evidence；未知回执查原operation，不重试生成新事实。 |
| [pg-016-f02 F02 点尺寸/路宽/禁胶区](../process-guides/processes/PG-016_dispense.md#pg-016-f02) | `B-GEO` | `C-01/02/03/04/07/08`；执行 SM-010/011，工艺含义由 PG 保留。 | SM-020提交PG确认的InspectionFact/Evidence；未知回执查原operation，不重试生成新事实。 |
| [pg-016-f03 F03 高度/体积](../process-guides/processes/PG-016_dispense.md#pg-016-f03) | `B-3D` | `C-01/02/03/04/07/08`；执行 SM-012/010，工艺含义由 PG 保留。 | SM-020提交PG确认的InspectionFact/Evidence；未知回执查原operation，不重试生成新事实。 |
| [pg-017-f01 F01 元件存在/定位](../process-guides/processes/PG-017_pre-reflow-aoi.md#pg-017-f01) | `B-GEO` | `C-01/02/03/04/07/08`；执行 SM-010/011，工艺含义由 PG 保留。 | SM-020提交PG确认的InspectionFact/Evidence；未知回执查原operation，不重试生成新事实。 |
| [pg-017-f02 F02 身份/极性/标记](../process-guides/processes/PG-017_pre-reflow-aoi.md#pg-017-f02) | `B-OCR` | `C-01/02/03/04/05/07/08`；SM-011执行识读/视觉候选，期待字段及工艺含义由PG保留；SM-024仅在已接入时承接外部来源。 | SM-020提交PG确认的InspectionFact/Evidence；未知回执查原operation，不重试生成新事实。 |
| [pg-017-f03 F03 引脚/高度](../process-guides/processes/PG-017_pre-reflow-aoi.md#pg-017-f03) | `B-GEO`（2D引脚几何）；`B-3D`（需要高度的子项） | `C-01/02/03/04/07/08`；2D位置/间距由SM-011/010提供，3D表面/高度由SM-012/010提供；057B/C与PG分别保留方法和工艺含义。缺3D只影响高度依赖项，原必检高度仍记未覆盖；遮挡脚沿原针号未知，不重排其它脚。 | 原039分别消费有效2D量、不可见脚和不可用高度；合法部分/未知沿原应用与SM-020证据政策提交，不宣称全卡或全板合格。未知回执查原operation，不重试生成新事实。 |
| [pg-018-f01 F01 装配核对](../process-guides/processes/PG-018_post-reflow-aoi.md#pg-018-f01) | `B-GEO` | `C-01/02/03/04/07/08`；执行 SM-010/011，工艺含义由 PG 保留。 | SM-020提交PG确认的InspectionFact/Evidence；未知回执查原operation，不重试生成新事实。 |
| [pg-018-f02 F02 焊点域与形貌](../process-guides/processes/PG-018_post-reflow-aoi.md#pg-018-f02) | `B-AI` | `C-01/02/03/04/07/08`；SM-011/013 等经典能力先行；PKG-052 仅按 DEV-AI-064 提供 Candidate/Shadow/Advice，SM-026治理，工艺含义由 PG 保留。 | SM-020仅保存候选/证据；原PG/质量Owner决定是否形成事实。 |
| [pg-018-f03 F03 引脚翘起/共面](../process-guides/processes/PG-018_post-reflow-aoi.md#pg-018-f03) | `B-3D` | `C-01/02/03/04/07/08`；执行 SM-012/010，工艺含义由 PG 保留。 | SM-020提交PG确认的InspectionFact/Evidence；未知回执查原operation，不重试生成新事实。 |
| [pg-018-f04 F04 板级缺陷聚合](../process-guides/processes/PG-018_post-reflow-aoi.md#pg-018-f04) | `B-ASSIST` | `C-01/04/05/07/08`；PG/SM-019执行确定性聚合，SM-026仅可提供排序/解释建议，工艺含义由 PG 保留。 | SM-020按PG确认的InspectionFact/Evidence提交；AI建议单独保存，不能替代聚合或放行。 |
| [pg-019-f01 F01 插装身份/方向](../process-guides/processes/PG-019_insertion.md#pg-019-f01) | `B-GEO` | `C-01/02/03/04/07/08`；执行 SM-010/011，工艺含义由 PG 保留。 | SM-020提交PG确认的InspectionFact/Evidence；未知回执查原operation，不重试生成新事实。 |
| [pg-019-f02 F02 到位/高度](../process-guides/processes/PG-019_insertion.md#pg-019-f02) | `B-3D` | `C-01/02/03/04/07/08`；执行 SM-012/010，工艺含义由 PG 保留。 | SM-020提交PG确认的InspectionFact/Evidence；未知回执查原operation，不重试生成新事实。 |
| [pg-019-f03 F03 引脚可见端](../process-guides/processes/PG-019_insertion.md#pg-019-f03) | `B-AI` | `C-01/02/03/04/07/08`；SM-011/013 等经典能力先行；PKG-052 仅按 DEV-AI-064 提供 Candidate/Shadow/Advice，SM-026治理，工艺含义由 PG 保留。 | SM-020仅保存候选/证据；原PG/质量Owner决定是否形成事实。 |
| [pg-020-f01 F01 通孔焊点关联](../process-guides/processes/PG-020_wave-solder.md#pg-020-f01) | `B-GEO` | `C-01/02/03/04/07/08`；SM-014提供制造/网表来源，SM-008提供坐标与面别变换，SM-011只提供可见目标候选；三者形成针/孔/焊点的关联证据，工艺含义由 PG 保留，不能直接当量测事实。 | 保存目标关联、镜像/面别依据、未观测集合和候选证据；SM-020仅在 PG 确认后提交 InspectionFact/Evidence，未知回执查原operation，不重试生成新事实。 |
| [pg-020-f02 F02 锡形/桥连候选](../process-guides/processes/PG-020_wave-solder.md#pg-020-f02) | `B-AI` | `C-01/02/03/04/07/08`；SM-011/013 等经典能力先行；PKG-052 仅按 DEV-AI-064 提供 Candidate/Shadow/Advice，SM-026治理，工艺含义由 PG 保留。 | SM-020仅保存候选/证据；原PG/质量Owner决定是否形成事实。 |
| [pg-020-f03 F03 引脚露出/残留](../process-guides/processes/PG-020_wave-solder.md#pg-020-f03) | `B-GEO` | `C-01/02/03/04/07/08`；执行 SM-010/011，工艺含义由 PG 保留。 | SM-020提交PG确认的InspectionFact/Evidence；未知回执查原operation，不重试生成新事实。 |
| [pg-021-f01 F01 覆盖/禁涂区](../process-guides/processes/PG-021_coating.md#pg-021-f01) | `B-GEO` | `C-01/02/03/04/07/08`；SM-013负责应涂/禁涂/实际可见域的覆盖完整性与分母，SM-011仅提供涂层区域候选，SM-010/012按批准语义提供几何/面积计算；工艺含义由 PG 保留。 | 保存覆盖、侵入、未知域及有效性证据；SM-020提交PG确认的InspectionFact/Evidence，未知回执查原operation，不重试生成新事实。 |
| [pg-021-f02 F02 气泡/表面候选](../process-guides/processes/PG-021_coating.md#pg-021-f02) | `B-AI` | `C-01/02/03/04/07/08`；SM-011/013 等经典能力先行；PKG-052 仅按 DEV-AI-064 提供 Candidate/Shadow/Advice，SM-026治理，工艺含义由 PG 保留。 | SM-020仅保存候选/证据；原PG/质量Owner决定是否形成事实。 |
| [pg-021-f03 F03 厚度能力入口](../process-guides/processes/PG-021_coating.md#pg-021-f03) | `B-3D` | `C-01/02/03/04/07/08`；执行 SM-012/010，工艺含义由 PG 保留。 | SM-020提交PG确认的InspectionFact/Evidence；未知回执查原operation，不重试生成新事实。 |
| [pg-022-f01 F01 灌封表面](../process-guides/processes/PG-022_final-assembly.md#pg-022-f01) | `B-3D` | `C-01/02/03/04/07/08`；执行 SM-012/010，工艺含义由 PG 保留。 | SM-020提交PG确认的InspectionFact/Evidence；未知回执查原operation，不重试生成新事实。 |
| [pg-022-f02 F02 装配完整性](../process-guides/processes/PG-022_final-assembly.md#pg-022-f02) | `B-GEO` | `C-01/02/03/04/07/08`；SM-014提供装配清单/制造资料，SM-015提供元件/连接器/紧固件参考资产，SM-011仅生成可见目标候选，SM-017提供装配身份解析与关系校验，生产关联写入沿原Orchestrator/身份入口；存在/方向/到位语义由 PG 保留。 | 保存清单来源、逐目标覆盖、候选与未观测原因；SM-020提交PG确认的InspectionFact/Evidence，扭矩/接触/密封等非视觉项目不得由此生成事实，未知回执查原operation。 |
| [pg-022-f03 F03 标签/外形](../process-guides/processes/PG-022_final-assembly.md#pg-022-f03) | `B-OCR` + `B-GEO` | `C-01/02/03/04/05/07/08`；SM-011识读、SM-010外形量测、SM-017提供身份关系校验，PG保留期待来源和工艺语义；专属投影由[UI-PCS-026](../process-guides/guidance/14-page-contracts/UI-PCS-026_Final_Assembly_Workbench.md)消费。 | SM-020提交PG确认的InspectionFact/Evidence；未知回执查原operation，不重试生成新事实。 |
| [pg-023-f01 F01 任务领取/证据导航](../process-guides/processes/PG-023_review-rework.md#pg-023-f01) | `B-QUERY` | `C-01/04/05/07/08`；执行 SM-020/021/023，工艺含义由 PG 保留。 | SM-020/021只读查询；不拥有提交权。 |
| [pg-023-f02 F02 人工复判](../process-guides/processes/PG-023_review-rework.md#pg-023-f02) | `B-ASSIST` | `C-01/04/05/07/08`；SM-022持领取、证据查看和人工意见，SM-026仅可提供辅助建议，工艺含义由 PG 保留。 | SM-022/原PG Owner按批准事务提交人工意见；SM-020保存意见与证据关联，AI不能自动改判。 |
| [pg-023-f03 F03 返修/重检/处置](../process-guides/processes/PG-023_review-rework.md#pg-023-f03) | `B-ASSIST` | `C-01/04/05/07/08`；PG-023及原质量/设备Owner负责处置和新尝试，SM-026仅提供建议，工艺含义由 PG 保留。 | SM-020保存处置请求/回执及新尝试关联；不得把建议或网络ACK当作返修完成/质量放行。 |

<a id="spi-function-owner-binding"></a>
### 3.1 SPI复合功能的阶段绑定与拒绝反例

上述五行消费[PG014 §13](../process-guides/processes/PG-014_spi.md#spi-method-reception)及055A/B/C/D唯一方法；数字是现有PKG编号。这里只校准功能卡与执行/提交的接缝，不复制算法公式、统计估计器、设备状态或字段定义。

- **保存门与质量门：** 必检焊盘存在高度Unknown，最小提交证据齐全且原失败证据政策允许保存时，040保存带原缺口的合法结果；039不能将其聚合为完整PASS，页面也不能把保存成功显示为质量放行。反过来，数值均在限内但身份冲突、必要持久证据缺失或无写权时，不能保存为合格事实。对应[039 §6](../shared-modules/packages/PKG-039_Evaluation.md#evaluation-implementation)与[040 §9–10](../shared-modules/packages/PKG-040_ResultEvidence.md#result-evidence-two-stage)。
- **结果与统计的顺序：** 040提交成功但回执响应丢失时，生产调用方保持原提交Unknown并查询；042/045只有在能精确读到原已提交事实时才可纳入统计，不以页面回执是否到达决定事实存在，也不读取尚未提交的候选。统计计算、建议审批、设备应用都不是040提交的前置依赖。
- **建议与设备的顺序：** 045/055D有合格偏移建议但设备基准版本已变，原设备应用Owner按原版本/作用域守卫拒绝该请求；047不得把过期值换新ID强发。设备只回ACK时仍没有Applied或后效证明；晚到SPI的旧在制板由037/048按实际印刷版本归类。详见[055D §5–6](<../process-guides/guidance/06-domains/DEV-DOM-055D_SPI Rule SPC与Printer Feedback开发指导.md#spi-feedback-receipt>)。

正式字段、类型、枚举和程序/质量/设备权限仍由原C-01～C-08逐项采纳。以上是修正既有绑定，既不授权页面直接发命令，也不表示其它67个功能卡已完成同深度复核。

## 4. 功能卡必须填写的精确合同字段

在 Contract/FS/TaskCard 被正式采纳前，普通程序员只能使用本节作为检查表，不能把以下语义自行转成字段名：

- **身份**：实体、父子/拼板/面/视角/卷段、ProcessAttempt、InspectionAttempt、operation、epoch、重检与重发关系。
- **输入快照**：程序/制造资料/参考库/标定/模型/词表/预处理及每项 revision+hash+来源；缺依赖必须阻断。
- **目标与坐标**：目标/功能/ROI、单位、面别、坐标图、参考面、有效域、原始/派生输入和不可见范围。
- **输出语义**：原始读数、候选、量测、质量/有效性、缺项/拒识、规则比较、证据和来源；AI分数不直接成为质量事实。
- **状态与Owner**：前态、允许者、原子变更、事件/回执、超时/取消/迟到/重启、终态和恢复；执行、提交、复判、质量、设备和外部交付分开。
- **提交事务**：CalculationIdentity 与 CommitIdentity、预写/保全/提交/发布断点、幂等键、未知回执查回、历史读取和保持策略。
- **性能/恢复**：P50/P95/P99、峰值内存/GPU、队列/背压、资源租约、取消排空、断网/磁盘满/版本撤回/重复回执。
- **页面投影**：PageContract、权限、命令矩阵、八态、三语、AutomationId、只读证据/草稿编辑边界；页面不持有原生句柄。

## 5. 逐卡审查顺序与并行边界

A0：合同/Schema/State/Owner 由原权威单写者采纳；A1：PG/算法/数据/页面/开源研究可在不改候选字段的前提下并行；A2：提交与恢复由父任务串行接收；A3：真实 WPF、性能、Replay/Golden、HIL 分别验收。

允许并行：不同 PG 的功能卡、各自只读样本计划、页面原型和源码研究；禁止并行：C-01～08字段/枚举、同一公共 API、SM-020提交、语言资源、模型/数据目录、同一 PG 文件根。GPU/native句柄/数据库写入也需资源租约，不能因文件不冲突而并发占满。

## 6. 关闭条件与当前未决

每行进入实现前必须有：采纳后的 Contract/Schema/State/Owner、对应 FunctionSpec/PageContract、正常/失败样例、Replay/Golden、性能 Profile、提交回执测试和文档审计记录。当前 72 行只完成绑定设计，仍是 DesignReview；真实工艺阈值、样本/标准件、传感器、AsunImage 公共签名、WPF 和设备/HIL 证据按受影响任务关闭。

本页与 [DEV-AI-064](../shared-modules/guidance/07-ai/DEV-AI-064_逐任务AI选型与证据矩阵开发指导.md)、[DEV-PLAN-014](../09-development-plan/DEV-PLAN-014_全量研发工作包与并行依赖DAG.md)、[OPEN-GATES](../00-baseline/OPEN-GATES.md)互相引用；不另建 Schema 或状态机。

