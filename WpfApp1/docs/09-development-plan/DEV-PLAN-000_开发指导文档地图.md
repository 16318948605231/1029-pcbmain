# 开发指导文档地图

- 文档 ID：`DEV-PLAN-000`；版本：`1.8.0`；日期：2026-09-27；状态：`Navigation`

本页负责ID定位、路径迁移和功能指导覆盖定位，不是另一个项目入口。唯一入口为[PROJECT_ENTRY](../../PROJECT_ENTRY.md)。按[平台架构](../00-baseline/PLATFORM-DESIGN-BASELINE.md)→SM/PG→Contract/Owner→Page/FS→验收读取。目录完整不等于批准、实现或生产合格。

独立模块架构新主目录：[52项完全独立候选与逐项指导](../independent-modules/INDEPENDENT-MODULE-ARCHITECTURE.md)，旧62个PKG及28SM仅作迁移/责任映射；19条输入不限制数量；[REF-008 AOI91份指导副本与逐份对应](../references/REF-008_PCBA-AOI指导副本与平台采纳映射.md)。PKG页由历史目录唯一索引，不把原AOI ID纳入本平台活动ID表。

## 全量开发准备的当前深化

开发顺序/依赖见DEV-PLAN-001/014，文件隔离和接收见DEV-PLAN-002/003，工程落点候选见DEV-PLAN-006，首条链见DEV-PLAN-015。计划已按28SM/23PG重新覆盖；表内历史FS代码名在切片冻结时统一绑定，不能直接当批准项目。

快速编程共享语义见[DEV-AI-062](../shared-modules/guidance/07-ai/DEV-AI-062_自动编程与ProgramSynthesis开发指导.md)；[钻孔](../process-guides/processes/PG-002_drill.md#quick-programming)、[微孔](../process-guides/processes/PG-003_laser-via.md#quick-programming)、[钢网](../process-guides/processes/PG-013_stencil.md#quick-programming)已有专属资料/生成/参数/未决和拟验收。23份PG现均有对应方法/数据/性能/UI/组合故障/准入附录（包括PG-023的 `pg-023-ai-data-performance-ui`），逐页锚点可从[制程目录](../process-guides/README.md)进入；附录仍不替代正式契约、真实样本、WPF、设备和生产资格。其它PG尚未全部实现代码；完整UI原型、逐任务AI、精确契约/公共API仍在持续Goal内，不以文档章节称全量完成。

文字模块实施：[IM-028 ocr](../independent-modules/ocr/DEVELOPMENT-GUIDE.md)；产品关联/比较与研究：[DEV-VIS-021A](../shared-modules/guidance/03-vision/DEV-VIS-021A_OCR与DeepOCR独立能力开发指导.md)，固定来源见REF-002。阻焊/终检的[材料有效域/字符](../process-guides/processes/PG-006_soldermask-legend.md#mask-detailed-semantics)与[双面关联/完整性](../process-guides/processes/PG-011_final-avi.md#avi-coverage-pairing)仍由应用维护。[交互原型与检查范围](../process-guides/guidance/14-page-contracts/UI-PCS-015_PCB_Inspection_Workbench.md#14-已执行的原型检查与剩余验收)可评审，不能视为真实WPF完成。

逐任务 AI 路线唯一登记：[DEV-AI-064](../shared-modules/guidance/07-ai/DEV-AI-064_逐任务AI选型与证据矩阵开发指导.md)覆盖 23 个 PG、72 个功能卡，逐项给出经典基线、HALCON/DeepOCR/PaddleOCR/异常或3D候选边界、数据分组、拒识回退、性能证据和Owner。该矩阵关闭文档登记缺口，不关闭真实样本、公共签名、训练/部署、WPF、设备或质量资格。


点胶/涂覆专项：[点/路/结点及快速编程](../process-guides/processes/PG-016_dispense.md#dispense-path-semantics)、[物理表面/覆盖/膜厚及快速编程](../process-guides/processes/PG-021_coating.md#coating-domain-semantics)；共享定义在[DEV-MET-031 §5](../shared-modules/guidance/04-metrology/DEV-MET-031_通用计量引擎开发指导.md#profile-and-integral)。专属页面UI-PCS-022/023已有任务/布局/命令/八态设计及[交互样例与验证范围](../process-guides/guidance/14-page-contracts/UI-PCS-022_Dispense_Workbench.md#83-已执行检查与未覆盖项)，真实WPF/算法尚未验收；写入边界见DEV-PLAN-014 §8。

插件/THT专项：[PG-019针型/针序与快编](../process-guides/processes/PG-019_insertion.md#pin-inspection-semantics)、[PG-020焊点/关系与快编](../process-guides/processes/PG-020_wave-solder.md#tht-inspection-semantics)；公共轴/端/截面见DEV-MET-031 §6。UI-PCS-024/025有专属布局/命令/八态和[交互样例验证](../process-guides/guidance/14-page-contracts/UI-PCS-024_Insertion_Workbench.md#prototype-evidence)，实际WPF尚未实现；源码/官方依据在REF-002/007，切片顺序在DEV-PLAN-014 §9。

USER-002的19项独立能力、原序号和唯一实施指导见[公共目录专项表](../shared-modules/README.md#user-002-modules)。条码DEV-VIS-021B与通道DEV-VIS-021C新增，其他能力在原指导深化；28SM是能力归属而非DLL数量。

## 功能覆盖与实施深度

当前23项制程的既有功能表逐行链接到原PG内的专项实施卡。复合项的每种量测/结果在卡内分别规定，不能因同一行存在而省略其子项。新增功能必须先补本表和唯一指导，再按DEV-GOV-010十二项准入；此导航不定义Schema、参数或实现状态。

公共功能：28份SM的“独立发布与逐操作接入”节定义核心/控件/宿主分工及操作验收，详见[公共模块目录](../shared-modules/README.md)。69份既有FS和26份PageContract仍是细化来源，未自动变为批准接口。下表“专项卡已细化”仅表示当前文档包含功能特定步骤/模块/操作/拟验收；正式契约/API、产品阈值、样本与性能Profile仍按各卡及OPEN-GATES关闭。

| 制程 | 功能 | 唯一专项指导 | 当前实施深度 |
|---|---|---|---|
| PG-001 | 批次/料号/面别核对 | [F01](<../process-guides/processes/PG-001_incoming-material.md#pg-001-f01>)；细化来源 FS-001, FS-061 | DesignReview；专项卡已细化，准入未冻结 |
| PG-001 | 表面污染/划伤/异物候选 | [F02](<../process-guides/processes/PG-001_incoming-material.md#pg-001-f02>)；细化来源 FS-022 | DesignReview；专项卡已细化，准入未冻结 |
| PG-001 | 外形/厚度 | [F03](<../process-guides/processes/PG-001_incoming-material.md#pg-001-f03>)；细化来源 FS-017, FS-018 | DesignReview；专项卡已细化，准入未冻结 |
| PG-002 | 孔目标对应 | [F01](<../process-guides/processes/PG-002_drill.md#pg-002-f01>)；细化来源 FS-023, FS-024 | DesignReview；专项卡已细化，准入未冻结 |
| PG-002 | 孔径/圆度/槽宽 | [F02](<../process-guides/processes/PG-002_drill.md#pg-002-f02>)；细化来源 FS-023, FS-009, FS-017 | DesignReview；专项卡已细化，准入未冻结 |
| PG-002 | 位置/缺多孔 | [F03](<../process-guides/processes/PG-002_drill.md#pg-002-f03>)；细化来源 FS-024 | DesignReview；专项卡已细化，准入未冻结 |
| PG-003 | 开口几何 | [F01](<../process-guides/processes/PG-003_laser-via.md#pg-003-f01>)；细化来源 FS-025, FS-031 | DesignReview；专项卡已细化，准入未冻结 |
| PG-003 | 底部/残留可见性 | [F02](<../process-guides/processes/PG-003_laser-via.md#pg-003-f02>)；细化来源 FS-025, FS-031 | DesignReview；专项卡已细化，准入未冻结 |
| PG-003 | 深度/锥形候选 | [F03](<../process-guides/processes/PG-003_laser-via.md#pg-003-f03>)；细化来源 FS-031, FS-012 | DesignReview；专项卡已细化，准入未冻结 |
| PG-004 | 层堆叠核对 | [F01](<../process-guides/processes/PG-004_layer-registration.md#pg-004-f01>)；细化来源 FS-029 | DesignReview；专项卡已细化，准入未冻结 |
| PG-004 | 可见基准偏差 | [F02](<../process-guides/processes/PG-004_layer-registration.md#pg-004-f02>)；细化来源 FS-026 | DesignReview；专项卡已细化，准入未冻结 |
| PG-004 | 积层目标生成 | [F03](<../process-guides/processes/PG-004_layer-registration.md#pg-004-f03>)；细化来源 FS-030 | DesignReview；专项卡已细化，准入未冻结 |
| PG-005 | 填充覆盖 | [F01](<../process-guides/processes/PG-005_via-fill.md#pg-005-f01>)；细化来源 FS-022 | DesignReview；专项卡已细化，准入未冻结 |
| PG-005 | 凹陷/凸起 | [F02](<../process-guides/processes/PG-005_via-fill.md#pg-005-f02>)；细化来源 FS-012, FS-017 | DesignReview；专项卡已细化，准入未冻结 |
| PG-005 | 研磨纹理/残料 | [F03](<../process-guides/processes/PG-005_via-fill.md#pg-005-f03>)；细化来源 FS-022 | DesignReview；专项卡已细化，准入未冻结 |
| PG-006 | 开窗/对位 | [F01](<../process-guides/processes/PG-006_soldermask-legend.md#pg-006-f01>)；细化来源 FS-027, FS-026 | DesignReview；专项卡已细化，准入未冻结 |
| PG-006 | 破损/异物/露铜候选 | [F02](<../process-guides/processes/PG-006_soldermask-legend.md#pg-006-f02>)；细化来源 FS-027, FS-022 | DesignReview；专项卡已细化，准入未冻结 |
| PG-006 | 字符内容/位置 | [F03](<../process-guides/processes/PG-006_soldermask-legend.md#pg-006-f03>)；细化来源 FS-061 | DesignReview；专项卡已细化，准入未冻结 |
| PG-007 | 处理区域核对 | [F01](<../process-guides/processes/PG-007_surface-finish.md#pg-007-f01>)；细化来源 FS-022 | DesignReview；专项卡已细化，准入未冻结 |
| PG-007 | 污染/氧化样态候选 | [F02](<../process-guides/processes/PG-007_surface-finish.md#pg-007-f02>)；细化来源 FS-022 | DesignReview；专项卡已细化，准入未冻结 |
| PG-007 | 划伤/缺损 | [F03](<../process-guides/processes/PG-007_surface-finish.md#pg-007-f03>)；细化来源 FS-022, FS-017 | DesignReview；专项卡已细化，准入未冻结 |
| PG-008 | 覆盖膜开窗 | [F01](<../process-guides/processes/PG-008_fpc-coverlay.md#pg-008-f01>)；细化来源 FS-036, FS-035 | DesignReview；专项卡已细化，准入未冻结 |
| PG-008 | 补强存在/方向/边界 | [F02](<../process-guides/processes/PG-008_fpc-coverlay.md#pg-008-f02>)；细化来源 FS-037 | DesignReview；专项卡已细化，准入未冻结 |
| PG-008 | 翘起/弯折区 | [F03](<../process-guides/processes/PG-008_fpc-coverlay.md#pg-008-f03>)；细化来源 FS-038 | DesignReview；专项卡已细化，准入未冻结 |
| PG-009 | 过渡区边界 | [F01](<../process-guides/processes/PG-009_rigid-flex.md#pg-009-f01>)；细化来源 FS-036, FS-026 | DesignReview；专项卡已细化，准入未冻结 |
| PG-009 | 局部外观/弯折限制区 | [F02](<../process-guides/processes/PG-009_rigid-flex.md#pg-009-f02>)；细化来源 FS-038, FS-022 | DesignReview；专项卡已细化，准入未冻结 |
| PG-009 | 局部台阶/尺寸 | [F03](<../process-guides/processes/PG-009_rigid-flex.md#pg-009-f03>)；细化来源 FS-017, FS-012 | DesignReview；专项卡已细化，准入未冻结 |
| PG-010 | 外形/槽位 | [F01](<../process-guides/processes/PG-010_outline.md#pg-010-f01>)；细化来源 FS-017, FS-024 | DesignReview；专项卡已细化，准入未冻结 |
| PG-010 | 毛刺/崩边候选 | [F02](<../process-guides/processes/PG-010_outline.md#pg-010-f02>)；细化来源 FS-022, FS-017 | DesignReview；专项卡已细化，准入未冻结 |
| PG-010 | V槽几何 | [F03](<../process-guides/processes/PG-010_outline.md#pg-010-f03>)；细化来源 FS-017, FS-012 | DesignReview；专项卡已细化，准入未冻结 |
| PG-011 | 双面外观覆盖 | [F01](<../process-guides/processes/PG-011_final-avi.md#pg-011-f01>)；细化来源 FS-028, FS-019 | DesignReview；专项卡已细化，准入未冻结 |
| PG-011 | 翘曲量测 | [F02](<../process-guides/processes/PG-011_final-avi.md#pg-011-f02>)；细化来源 FS-028, FS-012, FS-017 | DesignReview；专项卡已细化，准入未冻结 |
| PG-011 | 终检项目聚合 | [F03](<../process-guides/processes/PG-011_final-avi.md#pg-011-f03>)；细化来源 FS-028, FS-066 | DesignReview；专项卡已细化，准入未冻结 |
| PG-012 | Web坐标 | [F01](<../process-guides/processes/PG-012_r2r.md#pg-012-f01>)；细化来源 FS-034 | DesignReview；专项卡已细化，准入未冻结 |
| PG-012 | 区段覆盖/接带 | [F02](<../process-guides/processes/PG-012_r2r.md#pg-012-f02>)；细化来源 FS-034, FS-019 | DesignReview；专项卡已细化，准入未冻结 |
| PG-012 | 局部非刚性变换 | [F03](<../process-guides/processes/PG-012_r2r.md#pg-012-f03>)；细化来源 FS-035 | DesignReview；专项卡已细化，准入未冻结 |
| PG-013 | 开口几何与位置 | [F01](<../process-guides/processes/PG-013_stencil.md#pg-013-f01>)；细化来源 FS-039, FS-009 | DesignReview；专项卡已细化，准入未冻结 |
| PG-013 | 堵孔/污染 | [F02](<../process-guides/processes/PG-013_stencil.md#pg-013-f02>)；细化来源 FS-042, FS-043 | DesignReview；专项卡已细化，准入未冻结 |
| PG-013 | 厚度/侧壁 | [F03](<../process-guides/processes/PG-013_stencil.md#pg-013-f03>)；细化来源 FS-040, FS-041 | DesignReview；专项卡已细化，准入未冻结 |
| PG-014 | 焊盘/开口目标 | [F01](<../process-guides/processes/PG-014_spi.md#pg-014-f01>)；细化来源 FS-046 | DesignReview；专项卡已细化，准入未冻结 |
| PG-014 | 参考面与高度质量 | [F02](<../process-guides/processes/PG-014_spi.md#pg-014-f02>)；细化来源 FS-044, FS-045 | DesignReview；专项卡已细化，准入未冻结 |
| PG-014 | 锡膏分割/连桥 | [F03](<../process-guides/processes/PG-014_spi.md#pg-014-f03>)；细化来源 FS-047 | DesignReview；专项卡已细化，准入未冻结 |
| PG-014 | 量测 | [F04](<../process-guides/processes/PG-014_spi.md#pg-014-f04>)；细化来源 FS-048, FS-049, FS-050, FS-051, FS-052 | DesignReview；专项卡已细化，准入未冻结 |
| PG-014 | 判定/SPC/反馈 | [F05](<../process-guides/processes/PG-014_spi.md#pg-014-f05>)；细化来源 FS-053, FS-054, FS-055 | DesignReview；专项卡已细化，准入未冻结 |
| PG-015 | 资料一致性 | [F01](<../process-guides/processes/PG-015_pcba-incoming.md#pg-015-f01>)；细化来源 FS-056, FS-001 | DesignReview；专项卡已细化，准入未冻结 |
| PG-015 | 标记/方向 | [F02](<../process-guides/processes/PG-015_pcba-incoming.md#pg-015-f02>)；细化来源 FS-059, FS-061 | DesignReview；专项卡已细化，准入未冻结 |
| PG-015 | 首件位置 | [F03](<../process-guides/processes/PG-015_pcba-incoming.md#pg-015-f03>)；细化来源 FS-056, FS-057 | DesignReview；专项卡已细化，准入未冻结 |
| PG-016 | 胶点关联/路径连续性 | [F01](<../process-guides/processes/PG-016_dispense.md#pg-016-f01>)；细化来源 FS-010, FS-017 | DesignReview；专项卡已细化，准入未冻结 |
| PG-016 | 点尺寸/路宽/禁胶区 | [F02](<../process-guides/processes/PG-016_dispense.md#pg-016-f02>)；细化来源 FS-017, FS-010 | DesignReview；专项卡已细化，准入未冻结 |
| PG-016 | 高度/体积 | [F03](<../process-guides/processes/PG-016_dispense.md#pg-016-f03>)；细化来源 FS-012, FS-017 | DesignReview；专项卡已细化，准入未冻结 |
| PG-017 | 元件存在/定位 | [F01](<../process-guides/processes/PG-017_pre-reflow-aoi.md#pg-017-f01>)；细化来源 FS-056, FS-057 | DesignReview；专项卡已细化，准入未冻结 |
| PG-017 | 身份/极性/标记 | [F02](<../process-guides/processes/PG-017_pre-reflow-aoi.md#pg-017-f02>)；细化来源 FS-058, FS-059, FS-061 | DesignReview；专项卡已细化，准入未冻结 |
| PG-017 | 引脚/高度 | [F03](<../process-guides/processes/PG-017_pre-reflow-aoi.md#pg-017-f03>)；细化来源 FS-060, FS-017 | DesignReview；专项卡已细化，准入未冻结 |
| PG-018 | 装配核对 | [F01](<../process-guides/processes/PG-018_post-reflow-aoi.md#pg-018-f01>)；细化来源 FS-057, FS-058, FS-059, FS-061 | DesignReview；专项卡已细化，准入未冻结 |
| PG-018 | 焊点域与形貌 | [F02](<../process-guides/processes/PG-018_post-reflow-aoi.md#pg-018-f02>)；细化来源 FS-062 | DesignReview；专项卡已细化，准入未冻结 |
| PG-018 | 引脚翘起/共面 | [F03](<../process-guides/processes/PG-018_post-reflow-aoi.md#pg-018-f03>)；细化来源 FS-060, FS-017 | DesignReview；专项卡已细化，准入未冻结 |
| PG-018 | 板级缺陷聚合 | [F04](<../process-guides/processes/PG-018_post-reflow-aoi.md#pg-018-f04>)；细化来源 FS-062, FS-066 | DesignReview；专项卡已细化，准入未冻结 |
| PG-019 | 插装身份/方向 | [F01](<../process-guides/processes/PG-019_insertion.md#pg-019-f01>)；细化来源 FS-058, FS-059, FS-061 | DesignReview；专项卡已细化，准入未冻结 |
| PG-019 | 到位/高度 | [F02](<../process-guides/processes/PG-019_insertion.md#pg-019-f02>)；细化来源 FS-017, FS-012 | DesignReview；专项卡已细化，准入未冻结 |
| PG-019 | 引脚可见端 | [F03](<../process-guides/processes/PG-019_insertion.md#pg-019-f03>)；细化来源 FS-060, FS-017 | DesignReview；专项卡已细化，准入未冻结 |
| PG-020 | 通孔焊点关联 | [F01](<../process-guides/processes/PG-020_wave-solder.md#pg-020-f01>)；细化来源 FS-060, FS-062 | DesignReview；专项卡已细化，准入未冻结 |
| PG-020 | 锡形/桥连候选 | [F02](<../process-guides/processes/PG-020_wave-solder.md#pg-020-f02>)；细化来源 FS-062, FS-022 | DesignReview；专项卡已细化，准入未冻结 |
| PG-020 | 引脚露出/残留 | [F03](<../process-guides/processes/PG-020_wave-solder.md#pg-020-f03>)；细化来源 FS-060, FS-017, FS-022 | DesignReview；专项卡已细化，准入未冻结 |
| PG-021 | 覆盖/禁涂区 | [F01](<../process-guides/processes/PG-021_coating.md#pg-021-f01>)；细化来源 FS-010, FS-019 | DesignReview；专项卡已细化，准入未冻结 |
| PG-021 | 气泡/表面候选 | [F02](<../process-guides/processes/PG-021_coating.md#pg-021-f02>)；细化来源 FS-022 | DesignReview；专项卡已细化，准入未冻结 |
| PG-021 | 厚度能力入口 | [F03](<../process-guides/processes/PG-021_coating.md#pg-021-f03>)；细化来源 FS-017, FS-012 | DesignReview；专项卡已细化，准入未冻结 |
| PG-022 | 灌封表面 | [F01](<../process-guides/processes/PG-022_final-assembly.md#pg-022-f01>)；细化来源 FS-022, FS-012 | DesignReview；专项卡已细化，准入未冻结 |
| PG-022 | 装配完整性 | [F02](<../process-guides/processes/PG-022_final-assembly.md#pg-022-f02>)；细化来源 FS-057, FS-058 | DesignReview；专项卡已细化，准入未冻结 |
| PG-022 | 标签/外形 | [F03](<../process-guides/processes/PG-022_final-assembly.md#pg-022-f03>)；细化来源 FS-061, FS-017 | DesignReview；专项卡已细化，准入未冻结 |
| PG-023 | 任务领取/证据导航 | [F01](<../process-guides/processes/PG-023_review-rework.md#pg-023-f01>)；细化来源 FS-063 | DesignReview；专项卡已细化，准入未冻结 |
| PG-023 | 人工复判 | [F02](<../process-guides/processes/PG-023_review-rework.md#pg-023-f02>)；细化来源 FS-063, FS-066 | DesignReview；专项卡已细化，准入未冻结 |
| PG-023 | 返修/重检/处置 | [F03](<../process-guides/processes/PG-023_review-rework.md#pg-023-f03>)；细化来源 FS-063, FS-066 | DesignReview；专项卡已细化，准入未冻结 |

未展开范围维持原决定：X-Ray/CT、ICT、FCT仅入口；蚀刻光板线路内部算法等待已有项目。现有客户项目成功交付后才迁入平台。此表不构成新增机型投产或实现授权。

## 当前有ID的指导与引用文档

| ID | 当前文件 | 状态/用途 |
|---|---|---|
| `DEV-AI-060` | [DEV-AI-060_AI运行治理开发指导](<../shared-modules/guidance/07-ai/DEV-AI-060_AI运行治理开发指导.md>) | DocMapped |
| `DEV-AI-061` | [DEV-AI-061_AI辅助复判开发指导](<../shared-modules/guidance/07-ai/DEV-AI-061_AI辅助复判开发指导.md>) | DocMapped |
| `DEV-AI-062` | [DEV-AI-062_自动编程与ProgramSynthesis开发指导](<../shared-modules/guidance/07-ai/DEV-AI-062_自动编程与ProgramSynthesis开发指导.md>) | DesignReview |
| `DEV-AI-063` | [DEV-AI-063_数据集、GroundTruth与统计验证开发指导](<../shared-modules/guidance/07-ai/DEV-AI-063_数据集、GroundTruth与统计验证开发指导.md>) | DocMapped |
| `DEV-AI-064` | [DEV-AI-064_逐任务AI选型与证据矩阵开发指导](<../shared-modules/guidance/07-ai/DEV-AI-064_逐任务AI选型与证据矩阵开发指导.md>) | DesignReview |
| `DEV-AI-065` | [DEV-AI-065_AI能力路线与三态仲裁规范](<../shared-modules/guidance/07-ai/DEV-AI-065_AI能力路线与三态仲裁规范.md>) | DesignReview |
| `DEV-CONTRACT-002` | [DEV-CONTRACT-002_功能卡Contract、Schema、State、Owner与提交绑定开发指导](<../13-contract-candidates/DEV-CONTRACT-002_功能卡Contract、Schema、State、Owner与提交绑定开发指导.md>) | DesignReview |
| `DEV-CONTRACT-BASE-001` | [CONTRACT-CANDIDATES](<../13-contract-candidates/CONTRACT-CANDIDATES.md>) | DesignReview |
| `DEV-DOM-050` | [DEV-DOM-050_PCB Inspection领域开发指导](<../process-guides/guidance/06-domains/DEV-DOM-050_PCB Inspection领域开发指导.md>) | DocMapped |
| `DEV-DOM-050A` | [DEV-DOM-050A_PCB Pattern与Surface Inspection开发指导](<../process-guides/guidance/06-domains/DEV-DOM-050A_PCB Pattern与Surface Inspection开发指导.md>) | DocMapped |
| `DEV-DOM-050B` | [DEV-DOM-050B_PCB Drill Inspection开发指导](<../process-guides/guidance/06-domains/DEV-DOM-050B_PCB Drill Inspection开发指导.md>) | DocMapped |
| `DEV-DOM-050C` | [DEV-DOM-050C_PCB Laser Via Inspection开发指导](<../process-guides/guidance/06-domains/DEV-DOM-050C_PCB Laser Via Inspection开发指导.md>) | DocMapped |
| `DEV-DOM-050D` | [DEV-DOM-050D_PCB LayerRegistration SolderMask FinalAVI开发指导](<../process-guides/guidance/06-domains/DEV-DOM-050D_PCB LayerRegistration SolderMask FinalAVI开发指导.md>) | DocMapped |
| `DEV-DOM-051` | [DEV-DOM-051_HDI Inspection领域开发指导](<../process-guides/guidance/06-domains/DEV-DOM-051_HDI Inspection领域开发指导.md>) | DocMapped |
| `DEV-DOM-051A` | [DEV-DOM-051A_HDI BuildUp与LayerStack开发指导](<../process-guides/guidance/06-domains/DEV-DOM-051A_HDI BuildUp与LayerStack开发指导.md>) | DocMapped |
| `DEV-DOM-051B` | [DEV-DOM-051B_HDI LaserVia与FinePattern开发指导](<../process-guides/guidance/06-domains/DEV-DOM-051B_HDI LaserVia与FinePattern开发指导.md>) | DocMapped |
| `DEV-DOM-052` | [DEV-DOM-052_FPC与R2R领域开发指导](<../process-guides/guidance/06-domains/DEV-DOM-052_FPC与R2R领域开发指导.md>) | DocMapped |
| `DEV-DOM-052A` | [DEV-DOM-052A_FPC R2R NonRigid变形与WebCoordinate开发指导](<../process-guides/guidance/06-domains/DEV-DOM-052A_FPC R2R NonRigid变形与WebCoordinate开发指导.md>) | DocMapped |
| `DEV-DOM-052B` | [DEV-DOM-052B_FPC Coverlay Stiffener BendRegion开发指导](<../process-guides/guidance/06-domains/DEV-DOM-052B_FPC Coverlay Stiffener BendRegion开发指导.md>) | DocMapped |
| `DEV-DOM-053` | [DEV-DOM-053_Rigid-Flex领域开发指导](<../process-guides/guidance/06-domains/DEV-DOM-053_Rigid-Flex领域开发指导.md>) | DocMapped |
| `DEV-DOM-054` | [DEV-DOM-054_Stencil Inspection领域开发指导](<../process-guides/guidance/06-domains/DEV-DOM-054_Stencil Inspection领域开发指导.md>) | DocMapped |
| `DEV-DOM-054A` | [DEV-DOM-054A_Stencil 3D Geometry与Aperture Inspection开发指导](<../process-guides/guidance/06-domains/DEV-DOM-054A_Stencil 3D Geometry与Aperture Inspection开发指导.md>) | DocMapped |
| `DEV-DOM-054B` | [DEV-DOM-054B_Stencil Aperture堵孔污染与维护建议开发指导](<../process-guides/guidance/06-domains/DEV-DOM-054B_Stencil Aperture堵孔污染与维护建议开发指导.md>) | DocMapped |
| `DEV-DOM-055` | [DEV-DOM-055_SPI产品开发指导](<../process-guides/guidance/06-domains/DEV-DOM-055_SPI产品开发指导.md>) | DocMapped |
| `DEV-DOM-055A` | [DEV-DOM-055A_SPI 3D Acquisition与HeightField质量开发指导](<../process-guides/guidance/06-domains/DEV-DOM-055A_SPI 3D Acquisition与HeightField质量开发指导.md>) | DocMapped |
| `DEV-DOM-055B` | [DEV-DOM-055B_SPI Reference Plane与Pad_Stencils Target开发指导](<../process-guides/guidance/06-domains/DEV-DOM-055B_SPI Reference Plane与Pad_Stencils Target开发指导.md>) | DocMapped |
| `DEV-DOM-055C` | [DEV-DOM-055C_SPI Paste Segmentation与Metrology开发指导](<../process-guides/guidance/06-domains/DEV-DOM-055C_SPI Paste Segmentation与Metrology开发指导.md>) | DocMapped |
| `DEV-DOM-055D` | [DEV-DOM-055D_SPI Rule SPC与Printer Feedback开发指导](<../process-guides/guidance/06-domains/DEV-DOM-055D_SPI Rule SPC与Printer Feedback开发指导.md>) | DocMapped |
| `DEV-DOM-056` | [DEV-DOM-056_SPI实现级算法鲁棒性开发指导](<../process-guides/guidance/06-domains/DEV-DOM-056_SPI实现级算法鲁棒性开发指导.md>) | DocMapped |
| `DEV-DOM-057` | [DEV-DOM-057_AOI炉前炉后领域开发指导](<../process-guides/guidance/06-domains/DEV-DOM-057_AOI炉前炉后领域开发指导.md>) | DocMapped |
| `DEV-DOM-057A` | [DEV-DOM-057A_AOI CAD PnP与Target自动生成开发指导](<../process-guides/guidance/06-domains/DEV-DOM-057A_AOI CAD PnP与Target自动生成开发指导.md>) | DocMapped |
| `DEV-DOM-057B` | [DEV-DOM-057B_AOI Component Pin Lead Polarity OCR开发指导](<../process-guides/guidance/06-domains/DEV-DOM-057B_AOI Component Pin Lead Polarity OCR开发指导.md>) | DocMapped |
| `DEV-DOM-057C` | [DEV-DOM-057C_AOI Solder Joint与Pre_Post Reflow开发指导](<../process-guides/guidance/06-domains/DEV-DOM-057C_AOI Solder Joint与Pre_Post Reflow开发指导.md>) | DocMapped |
| `DEV-DOM-057D` | [DEV-DOM-057D_AOI Review Rework与Disposition开发指导](<../process-guides/guidance/06-domains/DEV-DOM-057D_AOI Review Rework与Disposition开发指导.md>) | DocMapped |
| `DEV-DOM-058` | [DEV-DOM-058_QualityControl全流程质量管控开发指导](<../shared-modules/guidance/06-domains/DEV-DOM-058_QualityControl全流程质量管控开发指导.md>) | DocMapped |
| `DEV-DOM-058A` | [DEV-DOM-058A_QualityControl SPC与分母定义开发指导](<../shared-modules/guidance/06-domains/DEV-DOM-058A_QualityControl SPC与分母定义开发指导.md>) | DocMapped |
| `DEV-DOM-058B` | [DEV-DOM-058B_Cross-Process Correlation与Disposition闭环开发指导](<../shared-modules/guidance/06-domains/DEV-DOM-058B_Cross-Process Correlation与Disposition闭环开发指导.md>) | DocMapped |
| `DEV-GOV-001` | [DEV-GOV-001_开发指导体系总则](<../01-governance/DEV-GOV-001_开发指导体系总则.md>) | Normative |
| `DEV-GOV-002` | [DEV-GOV-002_文档权威与变更控制](<../01-governance/DEV-GOV-002_文档权威与变更控制.md>) | Normative |
| `DEV-GOV-003` | [DEV-GOV-003_术语命名与标识体系](<../01-governance/DEV-GOV-003_术语命名与标识体系.md>) | ImplementationSpecificationReady |
| `DEV-GOV-004` | [DEV-GOV-004_Contract_Schema_Validator开发标准](<../01-governance/DEV-GOV-004_Contract_Schema_Validator开发标准.md>) | ImplementationSpecificationReady |
| `DEV-GOV-005` | [DEV-GOV-005_模块独立性与复用标准](<../01-governance/DEV-GOV-005_模块独立性与复用标准.md>) | Normative |
| `DEV-GOV-006` | [DEV-GOV-006_外部实现与GitHub研究标准](<../01-governance/DEV-GOV-006_外部实现与GitHub研究标准.md>) | Normative |
| `DEV-GOV-007` | [DEV-GOV-007_AI编码与自动化开发标准](<../01-governance/DEV-GOV-007_AI编码与自动化开发标准.md>) | Normative |
| `DEV-GOV-008` | [DEV-GOV-008_质量门禁与Acceptance标准](<../01-governance/DEV-GOV-008_质量门禁与Acceptance标准.md>) | Normative |
| `DEV-GOV-009` | [DEV-GOV-009_术语与文档自动审计规则](<../01-governance/DEV-GOV-009_术语与文档自动审计规则.md>) | ImplementationSpecificationReady |
| `DEV-GOV-010` | [DEV-GOV-010_实施级规格唯一标准](<../01-governance/DEV-GOV-010_实施级规格唯一标准.md>) | Normative |
| `DEV-GOV-011` | [DEV-GOV-011_质疑式反向审计与无已知缺口标准](<../01-governance/DEV-GOV-011_质疑式反向审计与无已知缺口标准.md>) | Normative |
| `DEV-GOV-012` | [DEV-GOV-012_规范性语言与禁止推断标准](<../01-governance/DEV-GOV-012_规范性语言与禁止推断标准.md>) | Normative |
| `DEV-GOV-013` | [DEV-GOV-013_变更影响分析与追踪标准](<../01-governance/DEV-GOV-013_变更影响分析与追踪标准.md>) | Normative |
| `DEV-GOV-014` | [DEV-GOV-014_活动基线与历史文档使用规则](<../01-governance/DEV-GOV-014_活动基线与历史文档使用规则.md>) | Normative |
| `DEV-GOV-015` | [DEV-GOV-015_AI确定性实施与来源锁定标准](<../01-governance/DEV-GOV-015_AI确定性实施与来源锁定标准.md>) | Normative |
| `DEV-MET-030` | [DEV-MET-030_Calibration与标定资格开发指导](<../shared-modules/guidance/04-metrology/DEV-MET-030_Calibration与标定资格开发指导.md>) | DocMapped |
| `DEV-MET-031` | [DEV-MET-031_通用计量引擎开发指导](<../shared-modules/guidance/04-metrology/DEV-MET-031_通用计量引擎开发指导.md>) | DesignReview |
| `DEV-MET-032` | [DEV-MET-032_PCBMetrology专业计量开发指导](<../process-guides/guidance/04-metrology/DEV-MET-032_PCBMetrology专业计量开发指导.md>) | DocMapped |
| `DEV-MET-033` | [DEV-MET-033_MSA、GR&R与计量资格开发指导](<../shared-modules/guidance/04-metrology/DEV-MET-033_MSA、GR&R与计量资格开发指导.md>) | DocMapped |
| `DEV-MET-034` | [DEV-MET-034_Coverage与Sampling开发指导](<../shared-modules/guidance/04-metrology/DEV-MET-034_Coverage与Sampling开发指导.md>) | DocMapped |
| `DEV-PLAN-000` | [DEV-PLAN-000_开发指导文档地图](<DEV-PLAN-000_开发指导文档地图.md>) | Navigation |
| `DEV-PLAN-001` | [DEV-PLAN-001_研发实施步骤与并行开发计划](<DEV-PLAN-001_研发实施步骤与并行开发计划.md>) | DesignReview |
| `DEV-PLAN-002` | [DEV-PLAN-002_功能与模块并行度矩阵](<DEV-PLAN-002_功能与模块并行度矩阵.md>) | DesignReview |
| `DEV-PLAN-003` | [DEV-PLAN-003_研发任务切片与AI任务模板](<DEV-PLAN-003_研发任务切片与AI任务模板.md>) | DesignReview |
| `DEV-PLAN-004` | [DEV-PLAN-004_开发启动前置检查与启动门槛](<DEV-PLAN-004_开发启动前置检查与启动门槛.md>) | Normative |
| `DEV-PLAN-005` | [DEV-PLAN-005_69项功能实现蓝图](<DEV-PLAN-005_69项功能实现蓝图.md>) | DocMapped |
| `DEV-PLAN-006` | [DEV-PLAN-006_Repository_Project_Namespace_Blueprint](<DEV-PLAN-006_Repository_Project_Namespace_Blueprint.md>) | DesignReview |
| `DEV-PLAN-007` | [DEV-PLAN-007_AI_Code_Task_Traceability](<DEV-PLAN-007_AI_Code_Task_Traceability.md>) | DocMapped |
| `DEV-PLAN-008` | [DEV-PLAN-008_全量功能代码落点注册表](<DEV-PLAN-008_全量功能代码落点注册表.md>) | Normative |
| `DEV-PLAN-009` | [DEV-PLAN-009_AI代码任务协议与停止条件](<DEV-PLAN-009_AI代码任务协议与停止条件.md>) | Normative |
| `DEV-PLAN-010` | [DEV-PLAN-010_开放门禁与禁止推断登记册](<DEV-PLAN-010_开放门禁与禁止推断登记册.md>) | Normative |
| `DEV-PLAN-011` | [DEV-PLAN-011_全量功能确定性实施矩阵](<DEV-PLAN-011_全量功能确定性实施矩阵.md>) | Normative |
| `DEV-PLAN-012` | [DEV-PLAN-012_全量PerformanceProfile绑定矩阵](<DEV-PLAN-012_全量PerformanceProfile绑定矩阵.md>) | Normative |
| `DEV-PLAN-013` | [DEV-PLAN-013_从零到生产的不可跳步开发主序列](<DEV-PLAN-013_从零到生产的不可跳步开发主序列.md>) | DesignReview |
| `DEV-PLAN-014` | [DEV-PLAN-014_全量研发工作包与并行依赖DAG](<DEV-PLAN-014_全量研发工作包与并行依赖DAG.md>) | DesignReview |
| `DEV-PLAN-016` | [DEV-PLAN-016_核心运行闭环实施与合同冻结顺序](<DEV-PLAN-016_核心运行闭环实施与合同冻结顺序.md>) | DesignReview |
| `DEV-PLAN-015` | [DEV-PLAN-015_从仓库零点启动第一条可运行纵向切片](<DEV-PLAN-015_从仓库零点启动第一条可运行纵向切片.md>) | DesignReview |
| `DEV-PLT-010` | [DEV-PLT-010_BoardIdentity与BoardRun开发指导](<../shared-modules/guidance/02-platform/DEV-PLT-010_BoardIdentity与BoardRun开发指导.md>) | DocMapped |
| `DEV-PLT-011` | [DEV-PLT-011_Inspection Pipeline与Attempt开发指导](<../shared-modules/guidance/02-platform/DEV-PLT-011_Inspection Pipeline与Attempt开发指导.md>) | DocMapped |
| `DEV-PLT-012` | [DEV-PLT-012_Evidence Graph与Result Commit开发指导](<../shared-modules/guidance/02-platform/DEV-PLT-012_Evidence Graph与Result Commit开发指导.md>) | DocMapped |
| `DEV-PLT-013` | [DEV-PLT-013_跨模块事件与外部互联开发指导](<../shared-modules/guidance/02-platform/DEV-PLT-013_跨模块事件与外部互联开发指导.md>) | DocMapped |
| `DEV-PLT-014` | [DEV-PLT-014_性能预算与并发流水线开发指导](<../shared-modules/guidance/02-platform/DEV-PLT-014_性能预算与并发流水线开发指导.md>) | DesignReview |
| `DEV-PLT-015` | [DEV-PLT-015_设备、相机、光源、运动与采集开发指导](<../shared-modules/guidance/02-platform/DEV-PLT-015_设备、相机、光源、运动与采集开发指导.md>) | DocMapped |
| `DEV-PLT-016` | [DEV-PLT-016_部署、Supervisor与本机隔离开发指导](<../shared-modules/guidance/02-platform/DEV-PLT-016_部署、Supervisor与本机隔离开发指导.md>) | DocMapped |
| `DEV-PLT-017` | [DEV-PLT-017_插件SDK与扩展点开发指导](<../shared-modules/guidance/02-platform/DEV-PLT-017_插件SDK与扩展点开发指导.md>) | DocMapped |
| `DEV-PLT-018` | [DEV-PLT-018_数据、报告、归档与数据主权开发指导](<../shared-modules/guidance/02-platform/DEV-PLT-018_数据、报告、归档与数据主权开发指导.md>) | DocMapped |
| `DEV-QLF-070` | [DEV-QLF-070_Golden Sample与Replay开发指导](<../shared-modules/guidance/08-qualification/DEV-QLF-070_Golden Sample与Replay开发指导.md>) | DocMapped |
| `DEV-QLF-071` | [DEV-QLF-071_Performance Benchmark与容量资格开发指导](<../shared-modules/guidance/08-qualification/DEV-QLF-071_Performance Benchmark与容量资格开发指导.md>) | DocMapped |
| `DEV-QLF-072` | [DEV-QLF-072_HIL、故障恢复与长稳开发指导](<../shared-modules/guidance/08-qualification/DEV-QLF-072_HIL、故障恢复与长稳开发指导.md>) | DocMapped |
| `DEV-QLF-073` | [计量Qualification与GR&R开发指导](<../shared-modules/guidance/08-qualification/DEV-QLF-073_视觉/计量Qualification与GR&R开发指导.md>) | DocMapped |
| `DEV-QLF-074` | [DEV-QLF-074_产品Acceptance与Production Gate开发指导](<../shared-modules/guidance/08-qualification/DEV-QLF-074_产品Acceptance与Production Gate开发指导.md>) | DocMapped |
| `DEV-UI-040` | [DEV-UI-040_WPF+DevExpress Design System开发指导](<../shared-modules/guidance/05-ui/DEV-UI-040_WPF+DevExpress Design System开发指导.md>) | DocMapped |
| `DEV-UI-041` | [DEV-UI-041_高保真PageContract与工作台开发指导](<../shared-modules/guidance/05-ui/DEV-UI-041_高保真PageContract与工作台开发指导.md>) | DocMapped |
| `DEV-UI-042` | [3D工作区与ROI交互开发指导](<../shared-modules/guidance/05-ui/DEV-UI-042_视觉/3D工作区与ROI交互开发指导.md>) | DocMapped |
| `DEV-UI-043` | [Recipe编程工作台开发指导](<../shared-modules/guidance/05-ui/DEV-UI-043_Program/Recipe编程工作台开发指导.md>) | DocMapped |
| `DEV-UI-044` | [Quality工作区开发指导](<../shared-modules/guidance/05-ui/DEV-UI-044_Review/Rework/Quality工作区开发指导.md>) | DocMapped |
| `DEV-UI-045` | [DEV-UI-045_操作员工作流简化与人因开发指导](<../shared-modules/guidance/05-ui/DEV-UI-045_操作员工作流简化与人因开发指导.md>) | DocMapped |
| `DEV-UI-046` | [DEV-UI-046_DevExpress高阶能力使用矩阵](<../shared-modules/guidance/05-ui/DEV-UI-046_DevExpress高阶能力使用矩阵.md>) | DocMapped |
| `DEV-UI-047` | [DEV-UI-047_视觉设计系统规格（色板/图标/排版/动效/无障碍/状态矩阵）](<../shared-modules/guidance/05-ui/DEV-UI-047_视觉设计系统规格.md>) | DesignReview |
| `DEV-UI-048` | [DEV-UI-048_AI结论的界面呈现规范（三态编码/置信度/冲突证据包/人工介入提示）](<../shared-modules/guidance/05-ui/DEV-UI-048_AI结论的界面呈现规范.md>) | DesignReview |
| `DEV-VIS-020` | [DEV-VIS-020_Vision Contract与AsunImage边界开发指导](<../shared-modules/guidance/03-vision/DEV-VIS-020_Vision Contract与AsunImage边界开发指导.md>) | DocMapped |
| `DEV-VIS-021` | [DEV-VIS-021_HALCON算子选择与算法决策矩阵开发指导](<../shared-modules/guidance/03-vision/DEV-VIS-021_HALCON算子选择与算法决策矩阵开发指导.md>) | DocMapped |
| `DEV-VIS-021A` | [DEV-VIS-021A](<../shared-modules/guidance/03-vision/DEV-VIS-021A_OCR与DeepOCR独立能力开发指导.md>) | ApplicationMapping / Research；模块实施见IM-028 |
| `DEV-VIS-021B` | [DEV-VIS-021B](<../shared-modules/guidance/03-vision/DEV-VIS-021B_条码解码与印制质量独立能力开发指导.md>) | ApplicationMapping / Research；模块实施见IM-027 |
| `DEV-VIS-021C` | [DEV-VIS-021C](<../shared-modules/guidance/03-vision/DEV-VIS-021C_图像通道与预处理独立能力开发指导.md>) | DesignReview |
| `DEV-VIS-022` | [Pyramid与Viewport开发指导](<../shared-modules/guidance/03-vision/DEV-VIS-022_图像帧、Tile/Pyramid与Viewport开发指导.md>) | DocMapped |
| `DEV-VIS-022A` | [DEV-VIS-022A_HALCON版本验证与算法Benchmark开发指导](<../shared-modules/guidance/03-vision/DEV-VIS-022A_HALCON版本验证与算法Benchmark开发指导.md>) | DocMapped |
| `DEV-VIS-023` | [DEV-VIS-023_定位、注册与Alignment开发指导](<../shared-modules/guidance/03-vision/DEV-VIS-023_定位、注册与Alignment开发指导.md>) | DocMapped |
| `DEV-VIS-024` | [DEV-VIS-024_ROI与Inspection Target Selection开发指导](<../shared-modules/guidance/03-vision/DEV-VIS-024_ROI与Inspection Target Selection开发指导.md>) | DocMapped |
| `DEV-VIS-025` | [DEV-VIS-025_2D边缘、轮廓与几何特征开发指导](<../shared-modules/guidance/03-vision/DEV-VIS-025_2D边缘、轮廓与几何特征开发指导.md>) | DocMapped |
| `DEV-VIS-026` | [DEV-VIS-026_2D分割、Blob与缺陷候选开发指导](<../shared-modules/guidance/03-vision/DEV-VIS-026_2D分割、Blob与缺陷候选开发指导.md>) | DocMapped |
| `DEV-VIS-027` | [DEV-VIS-027_3D HeightField与重建开发指导](<../shared-modules/guidance/03-vision/DEV-VIS-027_3D HeightField与重建开发指导.md>) | DocMapped |
| `DEV-VIS-028` | [DEV-VIS-028_3D对象模型、配准与表面分析开发指导](<../shared-modules/guidance/03-vision/DEV-VIS-028_3D对象模型、配准与表面分析开发指导.md>) | DocMapped |
| `DEV-VIS-029` | [DEV-VIS-029_多FOV拼接与全局坐标开发指导](<../shared-modules/guidance/03-vision/DEV-VIS-029_多FOV拼接与全局坐标开发指导.md>) | DocMapped |
| `DEV-VIS-030` | [HALCON-Operator-Decision-Matrix_v1.0](<../shared-modules/guidance/03-vision/HALCON-Operator-Decision-Matrix_v1.0.md>) | DocMapped |
| `FS-001` | [FS-001_Identity_Resolution](<../shared-modules/guidance/12-function-specs/FS-001_Identity_Resolution.md>) | DocMapped |
| `FS-002` | [FS-002_Effective_Runtime_Manifest](<../shared-modules/guidance/12-function-specs/FS-002_Effective_Runtime_Manifest.md>) | DocMapped |
| `FS-003` | [FS-003_Pipeline_execution](<../shared-modules/guidance/12-function-specs/FS-003_Pipeline_execution.md>) | DocMapped |
| `FS-004` | [FS-004_Evidence_commit](<../shared-modules/guidance/12-function-specs/FS-004_Evidence_commit.md>) | DocMapped |
| `FS-005` | [FS-005_Cross_module_event](<../shared-modules/guidance/12-function-specs/FS-005_Cross_module_event.md>) | DocMapped |
| `FS-006` | [FS-006_Board_flow](<../shared-modules/guidance/12-function-specs/FS-006_Board_flow.md>) | DocMapped |
| `FS-007` | [FS-007_Shape_localization](<../shared-modules/guidance/12-function-specs/FS-007_Shape_localization.md>) | DocMapped |
| `FS-008` | [FS-008_Subpixel_edge_extraction](<../shared-modules/guidance/12-function-specs/FS-008_Subpixel_edge_extraction.md>) | DocMapped |
| `FS-009` | [FS-009_Ellipse_circle_fit](<../shared-modules/guidance/12-function-specs/FS-009_Ellipse_circle_fit.md>) | DocMapped |
| `FS-010` | [FS-010_Local_segmentation](<../shared-modules/guidance/12-function-specs/FS-010_Local_segmentation.md>) | DocMapped |
| `FS-011` | [FS-011_2D_candidate_scoring](<../shared-modules/guidance/12-function-specs/FS-011_2D_candidate_scoring.md>) | DocMapped |
| `FS-012` | [FS-012_3D_HeightField_build](<../shared-modules/guidance/12-function-specs/FS-012_3D_HeightField_build.md>) | DocMapped |
| `FS-013` | [FS-013_Stereo_surface_reconstruction](<../shared-modules/guidance/12-function-specs/FS-013_Stereo_surface_reconstruction.md>) | DocMapped |
| `FS-014` | [FS-014_3D_registration](<../shared-modules/guidance/12-function-specs/FS-014_3D_registration.md>) | DocMapped |
| `FS-015` | [FS-015_Multi_FOV_stitch](<../shared-modules/guidance/12-function-specs/FS-015_Multi_FOV_stitch.md>) | DocMapped |
| `FS-016` | [FS-016_Calibration](<../shared-modules/guidance/12-function-specs/FS-016_Calibration.md>) | DocMapped |
| `FS-017` | [FS-017_Feature_measurement](<../shared-modules/guidance/12-function-specs/FS-017_Feature_measurement.md>) | DocMapped |
| `FS-018` | [FS-018_Uncertainty_budget](<../shared-modules/guidance/12-function-specs/FS-018_Uncertainty_budget.md>) | DocMapped |
| `FS-019` | [FS-019_Coverage_calculation](<../shared-modules/guidance/12-function-specs/FS-019_Coverage_calculation.md>) | DocMapped |
| `FS-020` | [FS-020_Pattern_width_space](<../process-guides/guidance/12-function-specs/FS-020_Pattern_width_space.md>) | DocMapped |
| `FS-021` | [FS-021_Pad_geometry](<../process-guides/guidance/12-function-specs/FS-021_Pad_geometry.md>) | DocMapped |
| `FS-022` | [FS-022_Surface_defect_candidate](<../process-guides/guidance/12-function-specs/FS-022_Surface_defect_candidate.md>) | DocMapped |
| `FS-023` | [FS-023_Drill_diameter](<../process-guides/guidance/12-function-specs/FS-023_Drill_diameter.md>) | DocMapped |
| `FS-024` | [FS-024_Drill_position](<../process-guides/guidance/12-function-specs/FS-024_Drill_position.md>) | DocMapped |
| `FS-025` | [FS-025_Laser_via_opening](<../process-guides/guidance/12-function-specs/FS-025_Laser_via_opening.md>) | DocMapped |
| `FS-026` | [FS-026_Layer_registration](<../process-guides/guidance/12-function-specs/FS-026_Layer_registration.md>) | DocMapped |
| `FS-027` | [FS-027_Solder_mask_defect](<../process-guides/guidance/12-function-specs/FS-027_Solder_mask_defect.md>) | DesignReview |
| `FS-028` | [FS-028_Final_AVI](<../process-guides/guidance/12-function-specs/FS-028_Final_AVI.md>) | DocMapped |
| `FS-029` | [FS-029_Layer_stack_validation](<../process-guides/guidance/12-function-specs/FS-029_Layer_stack_validation.md>) | DocMapped |
| `FS-030` | [FS-030_Build_up_layer_target](<../process-guides/guidance/12-function-specs/FS-030_Build_up_layer_target.md>) | DocMapped |
| `FS-031` | [FS-031_Laser_via_metrology](<../process-guides/guidance/12-function-specs/FS-031_Laser_via_metrology.md>) | DocMapped |
| `FS-032` | [FS-032_Fine_line_space](<../process-guides/guidance/12-function-specs/FS-032_Fine_line_space.md>) | DocMapped |
| `FS-033` | [FS-033_HDI_metrology](<../process-guides/guidance/12-function-specs/FS-033_HDI_metrology.md>) | DocMapped |
| `FS-034` | [FS-034_R2R_coordinate](<../process-guides/guidance/12-function-specs/FS-034_R2R_coordinate.md>) | DocMapped |
| `FS-035` | [FS-035_NonRigid_local_transform](<../process-guides/guidance/12-function-specs/FS-035_NonRigid_local_transform.md>) | DocMapped |
| `FS-036` | [FS-036_Coverlay_inspection](<../process-guides/guidance/12-function-specs/FS-036_Coverlay_inspection.md>) | DocMapped |
| `FS-037` | [FS-037_Stiffener_inspection](<../process-guides/guidance/12-function-specs/FS-037_Stiffener_inspection.md>) | DocMapped |
| `FS-038` | [FS-038_Bend_region](<../process-guides/guidance/12-function-specs/FS-038_Bend_region.md>) | DocMapped |
| `FS-039` | [FS-039_Aperture_geometry](<../process-guides/guidance/12-function-specs/FS-039_Aperture_geometry.md>) | DocMapped |
| `FS-040` | [FS-040_Stencil_thickness](<../process-guides/guidance/12-function-specs/FS-040_Stencil_thickness.md>) | DocMapped |
| `FS-041` | [FS-041_Wall_condition](<../process-guides/guidance/12-function-specs/FS-041_Wall_condition.md>) | DocMapped |
| `FS-042` | [FS-042_Blocked_aperture](<../process-guides/guidance/12-function-specs/FS-042_Blocked_aperture.md>) | DocMapped |
| `FS-043` | [FS-043_Maintenance_advice](<../process-guides/guidance/12-function-specs/FS-043_Maintenance_advice.md>) | DocMapped |
| `FS-044` | [FS-044_3D_acquisition_quality](<../process-guides/guidance/12-function-specs/FS-044_3D_acquisition_quality.md>) | DocMapped |
| `FS-045` | [FS-045_Reference_plane](<../process-guides/guidance/12-function-specs/FS-045_Reference_plane.md>) | DocMapped |
| `FS-046` | [FS-046_Pad_target_generation](<../process-guides/guidance/12-function-specs/FS-046_Pad_target_generation.md>) | DocMapped |
| `FS-047` | [FS-047_Paste_segmentation](<../process-guides/guidance/12-function-specs/FS-047_Paste_segmentation.md>) | DocMapped |
| `FS-048` | [FS-048_Paste_volume](<../process-guides/guidance/12-function-specs/FS-048_Paste_volume.md>) | DocMapped |
| `FS-049` | [FS-049_Paste_area](<../process-guides/guidance/12-function-specs/FS-049_Paste_area.md>) | DocMapped |
| `FS-050` | [FS-050_Paste_height](<../process-guides/guidance/12-function-specs/FS-050_Paste_height.md>) | DocMapped |
| `FS-051` | [FS-051_Paste_offset](<../process-guides/guidance/12-function-specs/FS-051_Paste_offset.md>) | DocMapped |
| `FS-052` | [FS-052_Paste_shape](<../process-guides/guidance/12-function-specs/FS-052_Paste_shape.md>) | DocMapped |
| `FS-053` | [FS-053_SPI_rule_evaluation](<../process-guides/guidance/12-function-specs/FS-053_SPI_rule_evaluation.md>) | DocMapped |
| `FS-054` | [FS-054_SPC](<../process-guides/guidance/12-function-specs/FS-054_SPC.md>) | DocMapped |
| `FS-055` | [FS-055_Printer_feedback](<../process-guides/guidance/12-function-specs/FS-055_Printer_feedback.md>) | DocMapped |
| `FS-056` | [FS-056_CAD_PnP_target_generation](<../process-guides/guidance/12-function-specs/FS-056_CAD_PnP_target_generation.md>) | DocMapped |
| `FS-057` | [FS-057_Component_presence](<../process-guides/guidance/12-function-specs/FS-057_Component_presence.md>) | DocMapped |
| `FS-058` | [FS-058_Component_identity](<../process-guides/guidance/12-function-specs/FS-058_Component_identity.md>) | DocMapped |
| `FS-059` | [FS-059_Polarity_orientation](<../process-guides/guidance/12-function-specs/FS-059_Polarity_orientation.md>) | DocMapped |
| `FS-060` | [FS-060_Pin_lead_inspection](<../process-guides/guidance/12-function-specs/FS-060_Pin_lead_inspection.md>) | DocMapped |
| `FS-061` | [FS-061_OCR_marking](<../process-guides/guidance/12-function-specs/FS-061_OCR_marking.md>) | DocMapped |
| `FS-062` | [FS-062_Solder_joint_post_reflow](<../process-guides/guidance/12-function-specs/FS-062_Solder_joint_post_reflow.md>) | DocMapped |
| `FS-063` | [FS-063_Review_rework](<../process-guides/guidance/12-function-specs/FS-063_Review_rework.md>) | DocMapped |
| `FS-064` | [FS-064_SPC_chart](<../shared-modules/guidance/12-function-specs/FS-064_SPC_chart.md>) | DocMapped |
| `FS-065` | [FS-065_Cross_process_correlation](<../shared-modules/guidance/12-function-specs/FS-065_Cross_process_correlation.md>) | DocMapped |
| `FS-066` | [FS-066_Disposition_projection](<../shared-modules/guidance/12-function-specs/FS-066_Disposition_projection.md>) | DocMapped |
| `FS-067` | [FS-067_AI_assisted_review](<../shared-modules/guidance/12-function-specs/FS-067_AI_assisted_review.md>) | DocMapped |
| `FS-068` | [FS-068_Program_synthesis](<../shared-modules/guidance/12-function-specs/FS-068_Program_synthesis.md>) | DocMapped |
| `FS-069` | [FS-069_AI_validation](<../shared-modules/guidance/12-function-specs/FS-069_AI_validation.md>) | DocMapped |
| `GATE-001` | [REQUIRED-REPOSITORY-AUTHORITIES](<../00-baseline/REQUIRED-REPOSITORY-AUTHORITIES.md>) | DesignReview |
| `PG-001` | [PG-001_incoming-material](<../process-guides/processes/PG-001_incoming-material.md>) | DesignReview |
| `PG-002` | [PG-002_drill](<../process-guides/processes/PG-002_drill.md>) | DesignReview |
| `PG-003` | [PG-003_laser-via](<../process-guides/processes/PG-003_laser-via.md>) | DesignReview |
| `PG-004` | [PG-004_layer-registration](<../process-guides/processes/PG-004_layer-registration.md>) | DesignReview |
| `PG-005` | [PG-005_via-fill](<../process-guides/processes/PG-005_via-fill.md>) | DesignReview |
| `PG-006` | [PG-006_soldermask-legend](<../process-guides/processes/PG-006_soldermask-legend.md>) | DesignReview |
| `PG-007` | [PG-007_surface-finish](<../process-guides/processes/PG-007_surface-finish.md>) | DesignReview |
| `PG-008` | [PG-008_fpc-coverlay](<../process-guides/processes/PG-008_fpc-coverlay.md>) | DesignReview |
| `PG-009` | [PG-009_rigid-flex](<../process-guides/processes/PG-009_rigid-flex.md>) | DesignReview |
| `PG-010` | [PG-010_outline](<../process-guides/processes/PG-010_outline.md>) | DesignReview |
| `PG-011` | [PG-011_final-avi](<../process-guides/processes/PG-011_final-avi.md>) | DesignReview |
| `PG-012` | [PG-012_r2r](<../process-guides/processes/PG-012_r2r.md>) | DesignReview |
| `PG-013` | [PG-013_stencil](<../process-guides/processes/PG-013_stencil.md>) | DesignReview |
| `PG-014` | [PG-014_spi](<../process-guides/processes/PG-014_spi.md>) | DesignReview |
| `PG-015` | [PG-015_pcba-incoming](<../process-guides/processes/PG-015_pcba-incoming.md>) | DesignReview |
| `PG-016` | [PG-016_dispense](<../process-guides/processes/PG-016_dispense.md>) | DesignReview |
| `PG-017` | [PG-017_pre-reflow-aoi](<../process-guides/processes/PG-017_pre-reflow-aoi.md>) | DesignReview |
| `PG-018` | [PG-018_post-reflow-aoi](<../process-guides/processes/PG-018_post-reflow-aoi.md>) | DesignReview |
| `PG-019` | [PG-019_insertion](<../process-guides/processes/PG-019_insertion.md>) | DesignReview |
| `PG-020` | [PG-020_wave-solder](<../process-guides/processes/PG-020_wave-solder.md>) | DesignReview |
| `PG-021` | [PG-021_coating](<../process-guides/processes/PG-021_coating.md>) | DesignReview |
| `PG-022` | [PG-022_final-assembly](<../process-guides/processes/PG-022_final-assembly.md>) | DesignReview |
| `PG-023` | [PG-023_review-rework](<../process-guides/processes/PG-023_review-rework.md>) | DesignReview |
| `PLATFORM-DESIGN-001` | [PLATFORM-DESIGN-BASELINE](<../00-baseline/PLATFORM-DESIGN-BASELINE.md>) | DesignReview |
| `PLATFORM-FLOW-001` | [END-TO-END-FLOWS](<../process-guides/END-TO-END-FLOWS.md>) | DesignReview |
| `PLATFORM-INTERFACE-001` | [INTERFACE-MAP](<../shared-modules/INTERFACE-MAP.md>) | DesignReview |
| `REF-001` | [REF-001_外部实现研究与官方资料基线](<../references/REF-001_外部实现研究与官方资料基线.md>) | Reference |
| `REF-002` | [REF-002_GitHub_DevExpress与OpenSource研究基线](<../references/REF-002_GitHub_DevExpress与OpenSource研究基线.md>) | Reference |
| `REF-003` | [REF-003_HALCON_24.11_Operator_Verification](<../references/REF-003_HALCON_24.11_Operator_Verification.md>) | Reference（HALCON 24.11历史资料；项目实现按AsunImage/HALCON 26.05及ImageLibDotNet公共签名核验） |
| `REF-004` | [REF-004_DevExpress与UI工作台官方研究基线](<../references/REF-004_DevExpress与UI工作台官方研究基线.md>) | Reference |
| `REF-005` | [REF-005_GitHub_PCB_AOI_研究基线](<../references/REF-005_GitHub_PCB_AOI_研究基线.md>) | Reference |
| `REF-006` | [REF-006_制程与公共模块的竞品证据映射](<../references/REF-006_制程与公共模块的竞品证据映射.md>) | Reference |
| `SM-001` | [SM-001_composition](<../shared-modules/modules/SM-001_composition.md>) | DesignReview |
| `SM-002` | [SM-002_configuration](<../shared-modules/modules/SM-002_configuration.md>) | DesignReview |
| `SM-003` | [SM-003_localization](<../shared-modules/modules/SM-003_localization.md>) | DesignReview |
| `SM-004` | [SM-004_authorization](<../shared-modules/modules/SM-004_authorization.md>) | DesignReview |
| `SM-005` | [SM-005_diagnostics](<../shared-modules/modules/SM-005_diagnostics.md>) | DesignReview |
| `SM-006` | [SM-006_frames](<../shared-modules/modules/SM-006_frames.md>) | DesignReview |
| `SM-007` | [SM-007_acquisition](<../shared-modules/modules/SM-007_acquisition.md>) | DesignReview |
| `SM-008` | [SM-008_coordinates](<../shared-modules/modules/SM-008_coordinates.md>) | DesignReview |
| `SM-009` | [SM-009_calibration](<../shared-modules/modules/SM-009_calibration.md>) | DesignReview |
| `SM-010` | [SM-010_roi-measurement](<../shared-modules/modules/SM-010_roi-measurement.md>) | DesignReview |
| `SM-011` | [SM-011_vision-features](<../shared-modules/modules/SM-011_vision-features.md>) | DesignReview |
| `SM-012` | [SM-012_surface](<../shared-modules/modules/SM-012_surface.md>) | DesignReview |
| `SM-013` | [SM-013_coverage](<../shared-modules/modules/SM-013_coverage.md>) | DesignReview |
| `SM-014` | [SM-014_manufacturing-input](<../shared-modules/modules/SM-014_manufacturing-input.md>) | DesignReview |
| `SM-015` | [SM-015_reference-library](<../shared-modules/modules/SM-015_reference-library.md>) | DesignReview |
| `SM-016` | [SM-016_program-package](<../shared-modules/modules/SM-016_program-package.md>) | DesignReview |
| `SM-017` | [SM-017_identity](<../shared-modules/modules/SM-017_identity.md>) | DesignReview |
| `SM-018` | [SM-018_execution](<../shared-modules/modules/SM-018_execution.md>) | DesignReview |
| `SM-019` | [SM-019_evaluation](<../shared-modules/modules/SM-019_evaluation.md>) | DesignReview |
| `SM-020` | [SM-020_result-evidence](<../shared-modules/modules/SM-020_result-evidence.md>) | DesignReview |
| `SM-021` | [SM-021_replay](<../shared-modules/modules/SM-021_replay.md>) | DesignReview |
| `SM-022` | [SM-022_review](<../shared-modules/modules/SM-022_review.md>) | DesignReview |
| `SM-023` | [SM-023_quality](<../shared-modules/modules/SM-023_quality.md>) | DesignReview |
| `SM-024` | [SM-024_integration](<../shared-modules/modules/SM-024_integration.md>) | DesignReview |
| `SM-025` | [SM-025_presentation](<../shared-modules/modules/SM-025_presentation.md>) | DesignReview |
| `SM-026` | [SM-026_ai-assistance](<../shared-modules/modules/SM-026_ai-assistance.md>) | DesignReview |
| `SM-027` | [SM-027_qualification](<../shared-modules/modules/SM-027_qualification.md>) | DesignReview |
| `SM-028` | [SM-028_delivery](<../shared-modules/modules/SM-028_delivery.md>) | DesignReview |
| `UI-PCS-001` | [UI-PCS-001_Production_Overview](<../shared-modules/guidance/14-page-contracts/UI-PCS-001_Production_Overview.md>) | DocMapped |
| `UI-PCS-002` | [UI-PCS-002_Vision_Workspace](<../shared-modules/guidance/14-page-contracts/UI-PCS-002_Vision_Workspace.md>) | DocMapped |
| `UI-PCS-003` | [UI-PCS-003_Program_Editor](<../shared-modules/guidance/14-page-contracts/UI-PCS-003_Program_Editor.md>) | DocMapped |
| `UI-PCS-004` | [UI-PCS-004_Recipe_Editor](<../shared-modules/guidance/14-page-contracts/UI-PCS-004_Recipe_Editor.md>) | DocMapped |
| `UI-PCS-005` | [UI-PCS-005_Review_Workspace](<../shared-modules/guidance/14-page-contracts/UI-PCS-005_Review_Workspace.md>) | DocMapped |
| `UI-PCS-006` | [UI-PCS-006_Metrology_Workspace](<../shared-modules/guidance/14-page-contracts/UI-PCS-006_Metrology_Workspace.md>) | DocMapped |
| `UI-PCS-007` | [UI-PCS-007_Calibration_Workspace](<../shared-modules/guidance/14-page-contracts/UI-PCS-007_Calibration_Workspace.md>) | DocMapped |
| `UI-PCS-008` | [UI-PCS-008_SPC_Workspace](<../shared-modules/guidance/14-page-contracts/UI-PCS-008_SPC_Workspace.md>) | DocMapped |
| `UI-PCS-009` | [UI-PCS-009_Manifest_Inspector](<../shared-modules/guidance/14-page-contracts/UI-PCS-009_Manifest_Inspector.md>) | DocMapped |
| `UI-PCS-010` | [UI-PCS-010_Device_Station](<../shared-modules/guidance/14-page-contracts/UI-PCS-010_Device_Station.md>) | DocMapped |
| `UI-PCS-011` | [UI-PCS-011_Quality_Hub](<../shared-modules/guidance/14-page-contracts/UI-PCS-011_Quality_Hub.md>) | DocMapped |
| `UI-PCS-012` | [UI-PCS-012_NPI_Auto_Program](<../shared-modules/guidance/14-page-contracts/UI-PCS-012_NPI_Auto_Program.md>) | DocMapped |
| `UI-PCS-013` | [UI-PCS-013_Evidence_Viewer](<../shared-modules/guidance/14-page-contracts/UI-PCS-013_Evidence_Viewer.md>) | DocMapped |
| `UI-PCS-014` | [UI-PCS-014_Engineering_Diagnostics](<../shared-modules/guidance/14-page-contracts/UI-PCS-014_Engineering_Diagnostics.md>) | DocMapped |
| `UI-PCS-015` | [UI-PCS-015_PCB_Inspection_Workbench](<../process-guides/guidance/14-page-contracts/UI-PCS-015_PCB_Inspection_Workbench.md>) | DesignReview |
| `UI-PCS-016` | [UI-PCS-016_HDI_FPC_RigidFlex_Workbench](<../process-guides/guidance/14-page-contracts/UI-PCS-016_HDI_FPC_RigidFlex_Workbench.md>) | DocMapped |
| `UI-PCS-017` | [UI-PCS-017_Stencil_Inspection_Workbench](<../process-guides/guidance/14-page-contracts/UI-PCS-017_Stencil_Inspection_Workbench.md>) | DocMapped |
| `UI-PCS-018` | [UI-PCS-018_SPI_Production_Workbench](<../process-guides/guidance/14-page-contracts/UI-PCS-018_SPI_Production_Workbench.md>) | DocMapped |
| `UI-PCS-019` | [UI-PCS-019_SPI_Programming_Workbench](<../process-guides/guidance/14-page-contracts/UI-PCS-019_SPI_Programming_Workbench.md>) | DocMapped |
| `UI-PCS-020` | [UI-PCS-020_AOI_Programming_and_Production_Workbench](<../process-guides/guidance/14-page-contracts/UI-PCS-020_AOI_Programming_and_Production_Workbench.md>) | DocMapped |
| `UI-PCS-021` | [UI-PCS-021_Quality_Control_Workbench](<../shared-modules/guidance/14-page-contracts/UI-PCS-021_Quality_Control_Workbench.md>) | DocMapped |
| `UI-PCS-022` | [UI-PCS-022_Dispense_Workbench](<../process-guides/guidance/14-page-contracts/UI-PCS-022_Dispense_Workbench.md>) | DesignReview |
| `UI-PCS-023` | [UI-PCS-023_Coating_Workbench](<../process-guides/guidance/14-page-contracts/UI-PCS-023_Coating_Workbench.md>) | DesignReview |
| `UI-PCS-024` | [UI-PCS-024_Insertion_Workbench](<../process-guides/guidance/14-page-contracts/UI-PCS-024_Insertion_Workbench.md>) | DesignReview |
| `UI-PCS-025` | [UI-PCS-025_THT_Solder_Workbench](<../process-guides/guidance/14-page-contracts/UI-PCS-025_THT_Solder_Workbench.md>) | DesignReview |
| `UI-PCS-026` | [UI-PCS-026_Final_Assembly_Workbench](<../process-guides/guidance/14-page-contracts/UI-PCS-026_Final_Assembly_Workbench.md>) | DesignReview |

## 迁移对照（原文档保留ID，旧位置不再维护活动副本）

路径相对仓库根目录。原161份DEV/FS/Page指导与87份设备资料归位；后者包括仅保留入口有效的历史设备资料。表是导航映射，不要求复制历史内容到新文件。

| 原路径 | 当前文件 |
|---|---|
| `docs/02-platform/DEV-PLT-010_BoardIdentity与BoardRun开发指导.md` | [docs/shared-modules/guidance/02-platform/DEV-PLT-010_BoardIdentity与BoardRun开发指导.md](<../shared-modules/guidance/02-platform/DEV-PLT-010_BoardIdentity与BoardRun开发指导.md>) |
| `docs/02-platform/DEV-PLT-011_Inspection Pipeline与Attempt开发指导.md` | [docs/shared-modules/guidance/02-platform/DEV-PLT-011_Inspection Pipeline与Attempt开发指导.md](<../shared-modules/guidance/02-platform/DEV-PLT-011_Inspection Pipeline与Attempt开发指导.md>) |
| `docs/02-platform/DEV-PLT-012_Evidence Graph与Result Commit开发指导.md` | [docs/shared-modules/guidance/02-platform/DEV-PLT-012_Evidence Graph与Result Commit开发指导.md](<../shared-modules/guidance/02-platform/DEV-PLT-012_Evidence Graph与Result Commit开发指导.md>) |
| `docs/02-platform/DEV-PLT-013_跨模块事件与外部互联开发指导.md` | [docs/shared-modules/guidance/02-platform/DEV-PLT-013_跨模块事件与外部互联开发指导.md](<../shared-modules/guidance/02-platform/DEV-PLT-013_跨模块事件与外部互联开发指导.md>) |
| `docs/02-platform/DEV-PLT-014_性能预算与并发流水线开发指导.md` | [docs/shared-modules/guidance/02-platform/DEV-PLT-014_性能预算与并发流水线开发指导.md](<../shared-modules/guidance/02-platform/DEV-PLT-014_性能预算与并发流水线开发指导.md>) |
| `docs/02-platform/DEV-PLT-015_设备、相机、光源、运动与采集开发指导.md` | [docs/shared-modules/guidance/02-platform/DEV-PLT-015_设备、相机、光源、运动与采集开发指导.md](<../shared-modules/guidance/02-platform/DEV-PLT-015_设备、相机、光源、运动与采集开发指导.md>) |
| `docs/02-platform/DEV-PLT-016_部署、Supervisor与本机隔离开发指导.md` | [docs/shared-modules/guidance/02-platform/DEV-PLT-016_部署、Supervisor与本机隔离开发指导.md](<../shared-modules/guidance/02-platform/DEV-PLT-016_部署、Supervisor与本机隔离开发指导.md>) |
| `docs/02-platform/DEV-PLT-017_插件SDK与扩展点开发指导.md` | [docs/shared-modules/guidance/02-platform/DEV-PLT-017_插件SDK与扩展点开发指导.md](<../shared-modules/guidance/02-platform/DEV-PLT-017_插件SDK与扩展点开发指导.md>) |
| `docs/02-platform/DEV-PLT-018_数据、报告、归档与数据主权开发指导.md` | [docs/shared-modules/guidance/02-platform/DEV-PLT-018_数据、报告、归档与数据主权开发指导.md](<../shared-modules/guidance/02-platform/DEV-PLT-018_数据、报告、归档与数据主权开发指导.md>) |
| `docs/03-vision/DEV-VIS-020_Vision Contract与AsunImage边界开发指导.md` | [docs/shared-modules/guidance/03-vision/DEV-VIS-020_Vision Contract与AsunImage边界开发指导.md](<../shared-modules/guidance/03-vision/DEV-VIS-020_Vision Contract与AsunImage边界开发指导.md>) |
| `docs/03-vision/DEV-VIS-021_HALCON算子选择与算法决策矩阵开发指导.md` | [docs/shared-modules/guidance/03-vision/DEV-VIS-021_HALCON算子选择与算法决策矩阵开发指导.md](<../shared-modules/guidance/03-vision/DEV-VIS-021_HALCON算子选择与算法决策矩阵开发指导.md>) |
| `docs/03-vision/DEV-VIS-022A_HALCON版本验证与算法Benchmark开发指导.md` | [docs/shared-modules/guidance/03-vision/DEV-VIS-022A_HALCON版本验证与算法Benchmark开发指导.md](<../shared-modules/guidance/03-vision/DEV-VIS-022A_HALCON版本验证与算法Benchmark开发指导.md>) |
| `docs/03-vision/DEV-VIS-023_定位、注册与Alignment开发指导.md` | [docs/shared-modules/guidance/03-vision/DEV-VIS-023_定位、注册与Alignment开发指导.md](<../shared-modules/guidance/03-vision/DEV-VIS-023_定位、注册与Alignment开发指导.md>) |
| `docs/03-vision/DEV-VIS-024_ROI与Inspection Target Selection开发指导.md` | [docs/shared-modules/guidance/03-vision/DEV-VIS-024_ROI与Inspection Target Selection开发指导.md](<../shared-modules/guidance/03-vision/DEV-VIS-024_ROI与Inspection Target Selection开发指导.md>) |
| `docs/03-vision/DEV-VIS-025_2D边缘、轮廓与几何特征开发指导.md` | [docs/shared-modules/guidance/03-vision/DEV-VIS-025_2D边缘、轮廓与几何特征开发指导.md](<../shared-modules/guidance/03-vision/DEV-VIS-025_2D边缘、轮廓与几何特征开发指导.md>) |
| `docs/03-vision/DEV-VIS-026_2D分割、Blob与缺陷候选开发指导.md` | [docs/shared-modules/guidance/03-vision/DEV-VIS-026_2D分割、Blob与缺陷候选开发指导.md](<../shared-modules/guidance/03-vision/DEV-VIS-026_2D分割、Blob与缺陷候选开发指导.md>) |
| `docs/03-vision/DEV-VIS-027_3D HeightField与重建开发指导.md` | [docs/shared-modules/guidance/03-vision/DEV-VIS-027_3D HeightField与重建开发指导.md](<../shared-modules/guidance/03-vision/DEV-VIS-027_3D HeightField与重建开发指导.md>) |
| `docs/03-vision/DEV-VIS-028_3D对象模型、配准与表面分析开发指导.md` | [docs/shared-modules/guidance/03-vision/DEV-VIS-028_3D对象模型、配准与表面分析开发指导.md](<../shared-modules/guidance/03-vision/DEV-VIS-028_3D对象模型、配准与表面分析开发指导.md>) |
| `docs/03-vision/DEV-VIS-029_多FOV拼接与全局坐标开发指导.md` | [docs/shared-modules/guidance/03-vision/DEV-VIS-029_多FOV拼接与全局坐标开发指导.md](<../shared-modules/guidance/03-vision/DEV-VIS-029_多FOV拼接与全局坐标开发指导.md>) |
| `docs/03-vision/HALCON-Operator-Decision-Matrix_v1.0.md` | [docs/shared-modules/guidance/03-vision/HALCON-Operator-Decision-Matrix_v1.0.md](<../shared-modules/guidance/03-vision/HALCON-Operator-Decision-Matrix_v1.0.md>) |
| `docs/03-vision/DEV-VIS-022_图像帧、Tile/Pyramid与Viewport开发指导.md` | [docs/shared-modules/guidance/03-vision/DEV-VIS-022_图像帧、Tile/Pyramid与Viewport开发指导.md](<../shared-modules/guidance/03-vision/DEV-VIS-022_图像帧、Tile/Pyramid与Viewport开发指导.md>) |
| `docs/04-metrology/DEV-MET-030_Calibration与标定资格开发指导.md` | [docs/shared-modules/guidance/04-metrology/DEV-MET-030_Calibration与标定资格开发指导.md](<../shared-modules/guidance/04-metrology/DEV-MET-030_Calibration与标定资格开发指导.md>) |
| `docs/04-metrology/DEV-MET-031_通用计量引擎开发指导.md` | [docs/shared-modules/guidance/04-metrology/DEV-MET-031_通用计量引擎开发指导.md](<../shared-modules/guidance/04-metrology/DEV-MET-031_通用计量引擎开发指导.md>) |
| `docs/04-metrology/DEV-MET-032_PCBMetrology专业计量开发指导.md` | [docs/process-guides/guidance/04-metrology/DEV-MET-032_PCBMetrology专业计量开发指导.md](<../process-guides/guidance/04-metrology/DEV-MET-032_PCBMetrology专业计量开发指导.md>) |
| `docs/04-metrology/DEV-MET-033_MSA、GR&R与计量资格开发指导.md` | [docs/shared-modules/guidance/04-metrology/DEV-MET-033_MSA、GR&R与计量资格开发指导.md](<../shared-modules/guidance/04-metrology/DEV-MET-033_MSA、GR&R与计量资格开发指导.md>) |
| `docs/04-metrology/DEV-MET-034_Coverage与Sampling开发指导.md` | [docs/shared-modules/guidance/04-metrology/DEV-MET-034_Coverage与Sampling开发指导.md](<../shared-modules/guidance/04-metrology/DEV-MET-034_Coverage与Sampling开发指导.md>) |
| `docs/05-ui/DEV-UI-040_WPF+DevExpress Design System开发指导.md` | [docs/shared-modules/guidance/05-ui/DEV-UI-040_WPF+DevExpress Design System开发指导.md](<../shared-modules/guidance/05-ui/DEV-UI-040_WPF+DevExpress Design System开发指导.md>) |
| `docs/05-ui/DEV-UI-041_高保真PageContract与工作台开发指导.md` | [docs/shared-modules/guidance/05-ui/DEV-UI-041_高保真PageContract与工作台开发指导.md](<../shared-modules/guidance/05-ui/DEV-UI-041_高保真PageContract与工作台开发指导.md>) |
| `docs/05-ui/DEV-UI-045_操作员工作流简化与人因开发指导.md` | [docs/shared-modules/guidance/05-ui/DEV-UI-045_操作员工作流简化与人因开发指导.md](<../shared-modules/guidance/05-ui/DEV-UI-045_操作员工作流简化与人因开发指导.md>) |
| `docs/05-ui/DEV-UI-046_DevExpress高阶能力使用矩阵.md` | [docs/shared-modules/guidance/05-ui/DEV-UI-046_DevExpress高阶能力使用矩阵.md](<../shared-modules/guidance/05-ui/DEV-UI-046_DevExpress高阶能力使用矩阵.md>) |
| `docs/05-ui/DEV-UI-042_视觉/3D工作区与ROI交互开发指导.md` | [docs/shared-modules/guidance/05-ui/DEV-UI-042_视觉/3D工作区与ROI交互开发指导.md](<../shared-modules/guidance/05-ui/DEV-UI-042_视觉/3D工作区与ROI交互开发指导.md>) |
| `docs/05-ui/DEV-UI-043_Program/Recipe编程工作台开发指导.md` | [docs/shared-modules/guidance/05-ui/DEV-UI-043_Program/Recipe编程工作台开发指导.md](<../shared-modules/guidance/05-ui/DEV-UI-043_Program/Recipe编程工作台开发指导.md>) |
| `docs/05-ui/DEV-UI-044_Review/Rework/Quality工作区开发指导.md` | [docs/shared-modules/guidance/05-ui/DEV-UI-044_Review/Rework/Quality工作区开发指导.md](<../shared-modules/guidance/05-ui/DEV-UI-044_Review/Rework/Quality工作区开发指导.md>) |
| `docs/06-domains/DEV-DOM-050A_PCB Pattern与Surface Inspection开发指导.md` | [docs/process-guides/guidance/06-domains/DEV-DOM-050A_PCB Pattern与Surface Inspection开发指导.md](<../process-guides/guidance/06-domains/DEV-DOM-050A_PCB Pattern与Surface Inspection开发指导.md>) |
| `docs/06-domains/DEV-DOM-050B_PCB Drill Inspection开发指导.md` | [docs/process-guides/guidance/06-domains/DEV-DOM-050B_PCB Drill Inspection开发指导.md](<../process-guides/guidance/06-domains/DEV-DOM-050B_PCB Drill Inspection开发指导.md>) |
| `docs/06-domains/DEV-DOM-050C_PCB Laser Via Inspection开发指导.md` | [docs/process-guides/guidance/06-domains/DEV-DOM-050C_PCB Laser Via Inspection开发指导.md](<../process-guides/guidance/06-domains/DEV-DOM-050C_PCB Laser Via Inspection开发指导.md>) |
| `docs/06-domains/DEV-DOM-050D_PCB LayerRegistration SolderMask FinalAVI开发指导.md` | [docs/process-guides/guidance/06-domains/DEV-DOM-050D_PCB LayerRegistration SolderMask FinalAVI开发指导.md](<../process-guides/guidance/06-domains/DEV-DOM-050D_PCB LayerRegistration SolderMask FinalAVI开发指导.md>) |
| `docs/06-domains/DEV-DOM-050_PCB Inspection领域开发指导.md` | [docs/process-guides/guidance/06-domains/DEV-DOM-050_PCB Inspection领域开发指导.md](<../process-guides/guidance/06-domains/DEV-DOM-050_PCB Inspection领域开发指导.md>) |
| `docs/06-domains/DEV-DOM-051A_HDI BuildUp与LayerStack开发指导.md` | [docs/process-guides/guidance/06-domains/DEV-DOM-051A_HDI BuildUp与LayerStack开发指导.md](<../process-guides/guidance/06-domains/DEV-DOM-051A_HDI BuildUp与LayerStack开发指导.md>) |
| `docs/06-domains/DEV-DOM-051B_HDI LaserVia与FinePattern开发指导.md` | [docs/process-guides/guidance/06-domains/DEV-DOM-051B_HDI LaserVia与FinePattern开发指导.md](<../process-guides/guidance/06-domains/DEV-DOM-051B_HDI LaserVia与FinePattern开发指导.md>) |
| `docs/06-domains/DEV-DOM-051_HDI Inspection领域开发指导.md` | [docs/process-guides/guidance/06-domains/DEV-DOM-051_HDI Inspection领域开发指导.md](<../process-guides/guidance/06-domains/DEV-DOM-051_HDI Inspection领域开发指导.md>) |
| `docs/06-domains/DEV-DOM-052A_FPC R2R NonRigid变形与WebCoordinate开发指导.md` | [docs/process-guides/guidance/06-domains/DEV-DOM-052A_FPC R2R NonRigid变形与WebCoordinate开发指导.md](<../process-guides/guidance/06-domains/DEV-DOM-052A_FPC R2R NonRigid变形与WebCoordinate开发指导.md>) |
| `docs/06-domains/DEV-DOM-052B_FPC Coverlay Stiffener BendRegion开发指导.md` | [docs/process-guides/guidance/06-domains/DEV-DOM-052B_FPC Coverlay Stiffener BendRegion开发指导.md](<../process-guides/guidance/06-domains/DEV-DOM-052B_FPC Coverlay Stiffener BendRegion开发指导.md>) |
| `docs/06-domains/DEV-DOM-052_FPC与R2R领域开发指导.md` | [docs/process-guides/guidance/06-domains/DEV-DOM-052_FPC与R2R领域开发指导.md](<../process-guides/guidance/06-domains/DEV-DOM-052_FPC与R2R领域开发指导.md>) |
| `docs/06-domains/DEV-DOM-053_Rigid-Flex领域开发指导.md` | [docs/process-guides/guidance/06-domains/DEV-DOM-053_Rigid-Flex领域开发指导.md](<../process-guides/guidance/06-domains/DEV-DOM-053_Rigid-Flex领域开发指导.md>) |
| `docs/06-domains/DEV-DOM-054A_Stencil 3D Geometry与Aperture Inspection开发指导.md` | [docs/process-guides/guidance/06-domains/DEV-DOM-054A_Stencil 3D Geometry与Aperture Inspection开发指导.md](<../process-guides/guidance/06-domains/DEV-DOM-054A_Stencil 3D Geometry与Aperture Inspection开发指导.md>) |
| `docs/06-domains/DEV-DOM-054B_Stencil Aperture堵孔污染与维护建议开发指导.md` | [docs/process-guides/guidance/06-domains/DEV-DOM-054B_Stencil Aperture堵孔污染与维护建议开发指导.md](<../process-guides/guidance/06-domains/DEV-DOM-054B_Stencil Aperture堵孔污染与维护建议开发指导.md>) |
| `docs/06-domains/DEV-DOM-054_Stencil Inspection领域开发指导.md` | [docs/process-guides/guidance/06-domains/DEV-DOM-054_Stencil Inspection领域开发指导.md](<../process-guides/guidance/06-domains/DEV-DOM-054_Stencil Inspection领域开发指导.md>) |
| `docs/06-domains/DEV-DOM-055A_SPI 3D Acquisition与HeightField质量开发指导.md` | [docs/process-guides/guidance/06-domains/DEV-DOM-055A_SPI 3D Acquisition与HeightField质量开发指导.md](<../process-guides/guidance/06-domains/DEV-DOM-055A_SPI 3D Acquisition与HeightField质量开发指导.md>) |
| `docs/06-domains/DEV-DOM-055B_SPI Reference Plane与Pad_Stencils Target开发指导.md` | [docs/process-guides/guidance/06-domains/DEV-DOM-055B_SPI Reference Plane与Pad_Stencils Target开发指导.md](<../process-guides/guidance/06-domains/DEV-DOM-055B_SPI Reference Plane与Pad_Stencils Target开发指导.md>) |
| `docs/06-domains/DEV-DOM-055C_SPI Paste Segmentation与Metrology开发指导.md` | [docs/process-guides/guidance/06-domains/DEV-DOM-055C_SPI Paste Segmentation与Metrology开发指导.md](<../process-guides/guidance/06-domains/DEV-DOM-055C_SPI Paste Segmentation与Metrology开发指导.md>) |
| `docs/06-domains/DEV-DOM-055D_SPI Rule SPC与Printer Feedback开发指导.md` | [docs/process-guides/guidance/06-domains/DEV-DOM-055D_SPI Rule SPC与Printer Feedback开发指导.md](<../process-guides/guidance/06-domains/DEV-DOM-055D_SPI Rule SPC与Printer Feedback开发指导.md>) |
| `docs/06-domains/DEV-DOM-055_SPI产品开发指导.md` | [docs/process-guides/guidance/06-domains/DEV-DOM-055_SPI产品开发指导.md](<../process-guides/guidance/06-domains/DEV-DOM-055_SPI产品开发指导.md>) |
| `docs/06-domains/DEV-DOM-056_SPI实现级算法鲁棒性开发指导.md` | [docs/process-guides/guidance/06-domains/DEV-DOM-056_SPI实现级算法鲁棒性开发指导.md](<../process-guides/guidance/06-domains/DEV-DOM-056_SPI实现级算法鲁棒性开发指导.md>) |
| `docs/06-domains/DEV-DOM-057A_AOI CAD PnP与Target自动生成开发指导.md` | [docs/process-guides/guidance/06-domains/DEV-DOM-057A_AOI CAD PnP与Target自动生成开发指导.md](<../process-guides/guidance/06-domains/DEV-DOM-057A_AOI CAD PnP与Target自动生成开发指导.md>) |
| `docs/06-domains/DEV-DOM-057B_AOI Component Pin Lead Polarity OCR开发指导.md` | [docs/process-guides/guidance/06-domains/DEV-DOM-057B_AOI Component Pin Lead Polarity OCR开发指导.md](<../process-guides/guidance/06-domains/DEV-DOM-057B_AOI Component Pin Lead Polarity OCR开发指导.md>) |
| `docs/06-domains/DEV-DOM-057C_AOI Solder Joint与Pre_Post Reflow开发指导.md` | [docs/process-guides/guidance/06-domains/DEV-DOM-057C_AOI Solder Joint与Pre_Post Reflow开发指导.md](<../process-guides/guidance/06-domains/DEV-DOM-057C_AOI Solder Joint与Pre_Post Reflow开发指导.md>) |
| `docs/06-domains/DEV-DOM-057D_AOI Review Rework与Disposition开发指导.md` | [docs/process-guides/guidance/06-domains/DEV-DOM-057D_AOI Review Rework与Disposition开发指导.md](<../process-guides/guidance/06-domains/DEV-DOM-057D_AOI Review Rework与Disposition开发指导.md>) |
| `docs/06-domains/DEV-DOM-057_AOI炉前炉后领域开发指导.md` | [docs/process-guides/guidance/06-domains/DEV-DOM-057_AOI炉前炉后领域开发指导.md](<../process-guides/guidance/06-domains/DEV-DOM-057_AOI炉前炉后领域开发指导.md>) |
| `docs/06-domains/DEV-DOM-058A_QualityControl SPC与分母定义开发指导.md` | [docs/shared-modules/guidance/06-domains/DEV-DOM-058A_QualityControl SPC与分母定义开发指导.md](<../shared-modules/guidance/06-domains/DEV-DOM-058A_QualityControl SPC与分母定义开发指导.md>) |
| `docs/06-domains/DEV-DOM-058B_Cross-Process Correlation与Disposition闭环开发指导.md` | [docs/shared-modules/guidance/06-domains/DEV-DOM-058B_Cross-Process Correlation与Disposition闭环开发指导.md](<../shared-modules/guidance/06-domains/DEV-DOM-058B_Cross-Process Correlation与Disposition闭环开发指导.md>) |
| `docs/06-domains/DEV-DOM-058_QualityControl全流程质量管控开发指导.md` | [docs/shared-modules/guidance/06-domains/DEV-DOM-058_QualityControl全流程质量管控开发指导.md](<../shared-modules/guidance/06-domains/DEV-DOM-058_QualityControl全流程质量管控开发指导.md>) |
| `docs/07-ai/DEV-AI-060_AI运行治理开发指导.md` | [docs/shared-modules/guidance/07-ai/DEV-AI-060_AI运行治理开发指导.md](<../shared-modules/guidance/07-ai/DEV-AI-060_AI运行治理开发指导.md>) |
| `docs/07-ai/DEV-AI-061_AI辅助复判开发指导.md` | [docs/shared-modules/guidance/07-ai/DEV-AI-061_AI辅助复判开发指导.md](<../shared-modules/guidance/07-ai/DEV-AI-061_AI辅助复判开发指导.md>) |
| `docs/07-ai/DEV-AI-062_自动编程与ProgramSynthesis开发指导.md` | [docs/shared-modules/guidance/07-ai/DEV-AI-062_自动编程与ProgramSynthesis开发指导.md](<../shared-modules/guidance/07-ai/DEV-AI-062_自动编程与ProgramSynthesis开发指导.md>) |
| `docs/07-ai/DEV-AI-063_数据集、GroundTruth与统计验证开发指导.md` | [docs/shared-modules/guidance/07-ai/DEV-AI-063_数据集、GroundTruth与统计验证开发指导.md](<../shared-modules/guidance/07-ai/DEV-AI-063_数据集、GroundTruth与统计验证开发指导.md>) |
| `docs/07-ai/DEV-AI-064_逐任务AI选型与证据矩阵开发指导.md` | [docs/shared-modules/guidance/07-ai/DEV-AI-064_逐任务AI选型与证据矩阵开发指导.md](<../shared-modules/guidance/07-ai/DEV-AI-064_逐任务AI选型与证据矩阵开发指导.md>) |
| `docs/07-ai/DEV-AI-065_AI能力路线与三态仲裁规范.md` | [docs/shared-modules/guidance/07-ai/DEV-AI-065_AI能力路线与三态仲裁规范.md](<../shared-modules/guidance/07-ai/DEV-AI-065_AI能力路线与三态仲裁规范.md>) |
| `docs/13-contract-candidates/DEV-CONTRACT-002_功能卡Contract、Schema、State、Owner与提交绑定开发指导.md` | [docs/13-contract-candidates/DEV-CONTRACT-002_功能卡Contract、Schema、State、Owner与提交绑定开发指导](<../13-contract-candidates/DEV-CONTRACT-002_功能卡Contract、Schema、State、Owner与提交绑定开发指导.md>) |
| `docs/08-qualification/DEV-QLF-070_Golden Sample与Replay开发指导.md` | [docs/shared-modules/guidance/08-qualification/DEV-QLF-070_Golden Sample与Replay开发指导.md](<../shared-modules/guidance/08-qualification/DEV-QLF-070_Golden Sample与Replay开发指导.md>) |
| `docs/08-qualification/DEV-QLF-071_Performance Benchmark与容量资格开发指导.md` | [docs/shared-modules/guidance/08-qualification/DEV-QLF-071_Performance Benchmark与容量资格开发指导.md](<../shared-modules/guidance/08-qualification/DEV-QLF-071_Performance Benchmark与容量资格开发指导.md>) |
| `docs/08-qualification/DEV-QLF-072_HIL、故障恢复与长稳开发指导.md` | [docs/shared-modules/guidance/08-qualification/DEV-QLF-072_HIL、故障恢复与长稳开发指导.md](<../shared-modules/guidance/08-qualification/DEV-QLF-072_HIL、故障恢复与长稳开发指导.md>) |
| `docs/08-qualification/DEV-QLF-074_产品Acceptance与Production Gate开发指导.md` | [docs/shared-modules/guidance/08-qualification/DEV-QLF-074_产品Acceptance与Production Gate开发指导.md](<../shared-modules/guidance/08-qualification/DEV-QLF-074_产品Acceptance与Production Gate开发指导.md>) |
| `docs/08-qualification/DEV-QLF-073_视觉/计量Qualification与GR&R开发指导.md` | [docs/shared-modules/guidance/08-qualification/DEV-QLF-073_视觉/计量Qualification与GR&R开发指导.md](<../shared-modules/guidance/08-qualification/DEV-QLF-073_视觉/计量Qualification与GR&R开发指导.md>) |
| `docs/12-function-specs/FS-001_Identity_Resolution.md` | [docs/shared-modules/guidance/12-function-specs/FS-001_Identity_Resolution.md](<../shared-modules/guidance/12-function-specs/FS-001_Identity_Resolution.md>) |
| `docs/12-function-specs/FS-002_Effective_Runtime_Manifest.md` | [docs/shared-modules/guidance/12-function-specs/FS-002_Effective_Runtime_Manifest.md](<../shared-modules/guidance/12-function-specs/FS-002_Effective_Runtime_Manifest.md>) |
| `docs/12-function-specs/FS-003_Pipeline_execution.md` | [docs/shared-modules/guidance/12-function-specs/FS-003_Pipeline_execution.md](<../shared-modules/guidance/12-function-specs/FS-003_Pipeline_execution.md>) |
| `docs/12-function-specs/FS-004_Evidence_commit.md` | [docs/shared-modules/guidance/12-function-specs/FS-004_Evidence_commit.md](<../shared-modules/guidance/12-function-specs/FS-004_Evidence_commit.md>) |
| `docs/12-function-specs/FS-005_Cross_module_event.md` | [docs/shared-modules/guidance/12-function-specs/FS-005_Cross_module_event.md](<../shared-modules/guidance/12-function-specs/FS-005_Cross_module_event.md>) |
| `docs/12-function-specs/FS-006_Board_flow.md` | [docs/shared-modules/guidance/12-function-specs/FS-006_Board_flow.md](<../shared-modules/guidance/12-function-specs/FS-006_Board_flow.md>) |
| `docs/12-function-specs/FS-007_Shape_localization.md` | [docs/shared-modules/guidance/12-function-specs/FS-007_Shape_localization.md](<../shared-modules/guidance/12-function-specs/FS-007_Shape_localization.md>) |
| `docs/12-function-specs/FS-008_Subpixel_edge_extraction.md` | [docs/shared-modules/guidance/12-function-specs/FS-008_Subpixel_edge_extraction.md](<../shared-modules/guidance/12-function-specs/FS-008_Subpixel_edge_extraction.md>) |
| `docs/12-function-specs/FS-009_Ellipse_circle_fit.md` | [docs/shared-modules/guidance/12-function-specs/FS-009_Ellipse_circle_fit.md](<../shared-modules/guidance/12-function-specs/FS-009_Ellipse_circle_fit.md>) |
| `docs/12-function-specs/FS-010_Local_segmentation.md` | [docs/shared-modules/guidance/12-function-specs/FS-010_Local_segmentation.md](<../shared-modules/guidance/12-function-specs/FS-010_Local_segmentation.md>) |
| `docs/12-function-specs/FS-011_2D_candidate_scoring.md` | [docs/shared-modules/guidance/12-function-specs/FS-011_2D_candidate_scoring.md](<../shared-modules/guidance/12-function-specs/FS-011_2D_candidate_scoring.md>) |
| `docs/12-function-specs/FS-012_3D_HeightField_build.md` | [docs/shared-modules/guidance/12-function-specs/FS-012_3D_HeightField_build.md](<../shared-modules/guidance/12-function-specs/FS-012_3D_HeightField_build.md>) |
| `docs/12-function-specs/FS-013_Stereo_surface_reconstruction.md` | [docs/shared-modules/guidance/12-function-specs/FS-013_Stereo_surface_reconstruction.md](<../shared-modules/guidance/12-function-specs/FS-013_Stereo_surface_reconstruction.md>) |
| `docs/12-function-specs/FS-014_3D_registration.md` | [docs/shared-modules/guidance/12-function-specs/FS-014_3D_registration.md](<../shared-modules/guidance/12-function-specs/FS-014_3D_registration.md>) |
| `docs/12-function-specs/FS-015_Multi_FOV_stitch.md` | [docs/shared-modules/guidance/12-function-specs/FS-015_Multi_FOV_stitch.md](<../shared-modules/guidance/12-function-specs/FS-015_Multi_FOV_stitch.md>) |
| `docs/12-function-specs/FS-016_Calibration.md` | [docs/shared-modules/guidance/12-function-specs/FS-016_Calibration.md](<../shared-modules/guidance/12-function-specs/FS-016_Calibration.md>) |
| `docs/12-function-specs/FS-017_Feature_measurement.md` | [docs/shared-modules/guidance/12-function-specs/FS-017_Feature_measurement.md](<../shared-modules/guidance/12-function-specs/FS-017_Feature_measurement.md>) |
| `docs/12-function-specs/FS-018_Uncertainty_budget.md` | [docs/shared-modules/guidance/12-function-specs/FS-018_Uncertainty_budget.md](<../shared-modules/guidance/12-function-specs/FS-018_Uncertainty_budget.md>) |
| `docs/12-function-specs/FS-019_Coverage_calculation.md` | [docs/shared-modules/guidance/12-function-specs/FS-019_Coverage_calculation.md](<../shared-modules/guidance/12-function-specs/FS-019_Coverage_calculation.md>) |
| `docs/12-function-specs/FS-020_Pattern_width_space.md` | [docs/process-guides/guidance/12-function-specs/FS-020_Pattern_width_space.md](<../process-guides/guidance/12-function-specs/FS-020_Pattern_width_space.md>) |
| `docs/12-function-specs/FS-021_Pad_geometry.md` | [docs/process-guides/guidance/12-function-specs/FS-021_Pad_geometry.md](<../process-guides/guidance/12-function-specs/FS-021_Pad_geometry.md>) |
| `docs/12-function-specs/FS-022_Surface_defect_candidate.md` | [docs/process-guides/guidance/12-function-specs/FS-022_Surface_defect_candidate.md](<../process-guides/guidance/12-function-specs/FS-022_Surface_defect_candidate.md>) |
| `docs/12-function-specs/FS-023_Drill_diameter.md` | [docs/process-guides/guidance/12-function-specs/FS-023_Drill_diameter.md](<../process-guides/guidance/12-function-specs/FS-023_Drill_diameter.md>) |
| `docs/12-function-specs/FS-024_Drill_position.md` | [docs/process-guides/guidance/12-function-specs/FS-024_Drill_position.md](<../process-guides/guidance/12-function-specs/FS-024_Drill_position.md>) |
| `docs/12-function-specs/FS-025_Laser_via_opening.md` | [docs/process-guides/guidance/12-function-specs/FS-025_Laser_via_opening.md](<../process-guides/guidance/12-function-specs/FS-025_Laser_via_opening.md>) |
| `docs/12-function-specs/FS-026_Layer_registration.md` | [docs/process-guides/guidance/12-function-specs/FS-026_Layer_registration.md](<../process-guides/guidance/12-function-specs/FS-026_Layer_registration.md>) |
| `docs/12-function-specs/FS-027_Solder_mask_defect.md` | [docs/process-guides/guidance/12-function-specs/FS-027_Solder_mask_defect.md](<../process-guides/guidance/12-function-specs/FS-027_Solder_mask_defect.md>) |
| `docs/12-function-specs/FS-028_Final_AVI.md` | [docs/process-guides/guidance/12-function-specs/FS-028_Final_AVI.md](<../process-guides/guidance/12-function-specs/FS-028_Final_AVI.md>) |
| `docs/12-function-specs/FS-029_Layer_stack_validation.md` | [docs/process-guides/guidance/12-function-specs/FS-029_Layer_stack_validation.md](<../process-guides/guidance/12-function-specs/FS-029_Layer_stack_validation.md>) |
| `docs/12-function-specs/FS-030_Build_up_layer_target.md` | [docs/process-guides/guidance/12-function-specs/FS-030_Build_up_layer_target.md](<../process-guides/guidance/12-function-specs/FS-030_Build_up_layer_target.md>) |
| `docs/12-function-specs/FS-031_Laser_via_metrology.md` | [docs/process-guides/guidance/12-function-specs/FS-031_Laser_via_metrology.md](<../process-guides/guidance/12-function-specs/FS-031_Laser_via_metrology.md>) |
| `docs/12-function-specs/FS-032_Fine_line_space.md` | [docs/process-guides/guidance/12-function-specs/FS-032_Fine_line_space.md](<../process-guides/guidance/12-function-specs/FS-032_Fine_line_space.md>) |
| `docs/12-function-specs/FS-033_HDI_metrology.md` | [docs/process-guides/guidance/12-function-specs/FS-033_HDI_metrology.md](<../process-guides/guidance/12-function-specs/FS-033_HDI_metrology.md>) |
| `docs/12-function-specs/FS-034_R2R_coordinate.md` | [docs/process-guides/guidance/12-function-specs/FS-034_R2R_coordinate.md](<../process-guides/guidance/12-function-specs/FS-034_R2R_coordinate.md>) |
| `docs/12-function-specs/FS-035_NonRigid_local_transform.md` | [docs/process-guides/guidance/12-function-specs/FS-035_NonRigid_local_transform.md](<../process-guides/guidance/12-function-specs/FS-035_NonRigid_local_transform.md>) |
| `docs/12-function-specs/FS-036_Coverlay_inspection.md` | [docs/process-guides/guidance/12-function-specs/FS-036_Coverlay_inspection.md](<../process-guides/guidance/12-function-specs/FS-036_Coverlay_inspection.md>) |
| `docs/12-function-specs/FS-037_Stiffener_inspection.md` | [docs/process-guides/guidance/12-function-specs/FS-037_Stiffener_inspection.md](<../process-guides/guidance/12-function-specs/FS-037_Stiffener_inspection.md>) |
| `docs/12-function-specs/FS-038_Bend_region.md` | [docs/process-guides/guidance/12-function-specs/FS-038_Bend_region.md](<../process-guides/guidance/12-function-specs/FS-038_Bend_region.md>) |
| `docs/12-function-specs/FS-039_Aperture_geometry.md` | [docs/process-guides/guidance/12-function-specs/FS-039_Aperture_geometry.md](<../process-guides/guidance/12-function-specs/FS-039_Aperture_geometry.md>) |
| `docs/12-function-specs/FS-040_Stencil_thickness.md` | [docs/process-guides/guidance/12-function-specs/FS-040_Stencil_thickness.md](<../process-guides/guidance/12-function-specs/FS-040_Stencil_thickness.md>) |
| `docs/12-function-specs/FS-041_Wall_condition.md` | [docs/process-guides/guidance/12-function-specs/FS-041_Wall_condition.md](<../process-guides/guidance/12-function-specs/FS-041_Wall_condition.md>) |
| `docs/12-function-specs/FS-042_Blocked_aperture.md` | [docs/process-guides/guidance/12-function-specs/FS-042_Blocked_aperture.md](<../process-guides/guidance/12-function-specs/FS-042_Blocked_aperture.md>) |
| `docs/12-function-specs/FS-043_Maintenance_advice.md` | [docs/process-guides/guidance/12-function-specs/FS-043_Maintenance_advice.md](<../process-guides/guidance/12-function-specs/FS-043_Maintenance_advice.md>) |
| `docs/12-function-specs/FS-044_3D_acquisition_quality.md` | [docs/process-guides/guidance/12-function-specs/FS-044_3D_acquisition_quality.md](<../process-guides/guidance/12-function-specs/FS-044_3D_acquisition_quality.md>) |
| `docs/12-function-specs/FS-045_Reference_plane.md` | [docs/process-guides/guidance/12-function-specs/FS-045_Reference_plane.md](<../process-guides/guidance/12-function-specs/FS-045_Reference_plane.md>) |
| `docs/12-function-specs/FS-046_Pad_target_generation.md` | [docs/process-guides/guidance/12-function-specs/FS-046_Pad_target_generation.md](<../process-guides/guidance/12-function-specs/FS-046_Pad_target_generation.md>) |
| `docs/12-function-specs/FS-047_Paste_segmentation.md` | [docs/process-guides/guidance/12-function-specs/FS-047_Paste_segmentation.md](<../process-guides/guidance/12-function-specs/FS-047_Paste_segmentation.md>) |
| `docs/12-function-specs/FS-048_Paste_volume.md` | [docs/process-guides/guidance/12-function-specs/FS-048_Paste_volume.md](<../process-guides/guidance/12-function-specs/FS-048_Paste_volume.md>) |
| `docs/12-function-specs/FS-049_Paste_area.md` | [docs/process-guides/guidance/12-function-specs/FS-049_Paste_area.md](<../process-guides/guidance/12-function-specs/FS-049_Paste_area.md>) |
| `docs/12-function-specs/FS-050_Paste_height.md` | [docs/process-guides/guidance/12-function-specs/FS-050_Paste_height.md](<../process-guides/guidance/12-function-specs/FS-050_Paste_height.md>) |
| `docs/12-function-specs/FS-051_Paste_offset.md` | [docs/process-guides/guidance/12-function-specs/FS-051_Paste_offset.md](<../process-guides/guidance/12-function-specs/FS-051_Paste_offset.md>) |
| `docs/12-function-specs/FS-052_Paste_shape.md` | [docs/process-guides/guidance/12-function-specs/FS-052_Paste_shape.md](<../process-guides/guidance/12-function-specs/FS-052_Paste_shape.md>) |
| `docs/12-function-specs/FS-053_SPI_rule_evaluation.md` | [docs/process-guides/guidance/12-function-specs/FS-053_SPI_rule_evaluation.md](<../process-guides/guidance/12-function-specs/FS-053_SPI_rule_evaluation.md>) |
| `docs/12-function-specs/FS-054_SPC.md` | [docs/process-guides/guidance/12-function-specs/FS-054_SPC.md](<../process-guides/guidance/12-function-specs/FS-054_SPC.md>) |
| `docs/12-function-specs/FS-055_Printer_feedback.md` | [docs/process-guides/guidance/12-function-specs/FS-055_Printer_feedback.md](<../process-guides/guidance/12-function-specs/FS-055_Printer_feedback.md>) |
| `docs/12-function-specs/FS-056_CAD_PnP_target_generation.md` | [docs/process-guides/guidance/12-function-specs/FS-056_CAD_PnP_target_generation.md](<../process-guides/guidance/12-function-specs/FS-056_CAD_PnP_target_generation.md>) |
| `docs/12-function-specs/FS-057_Component_presence.md` | [docs/process-guides/guidance/12-function-specs/FS-057_Component_presence.md](<../process-guides/guidance/12-function-specs/FS-057_Component_presence.md>) |
| `docs/12-function-specs/FS-058_Component_identity.md` | [docs/process-guides/guidance/12-function-specs/FS-058_Component_identity.md](<../process-guides/guidance/12-function-specs/FS-058_Component_identity.md>) |
| `docs/12-function-specs/FS-059_Polarity_orientation.md` | [docs/process-guides/guidance/12-function-specs/FS-059_Polarity_orientation.md](<../process-guides/guidance/12-function-specs/FS-059_Polarity_orientation.md>) |
| `docs/12-function-specs/FS-060_Pin_lead_inspection.md` | [docs/process-guides/guidance/12-function-specs/FS-060_Pin_lead_inspection.md](<../process-guides/guidance/12-function-specs/FS-060_Pin_lead_inspection.md>) |
| `docs/12-function-specs/FS-061_OCR_marking.md` | [docs/process-guides/guidance/12-function-specs/FS-061_OCR_marking.md](<../process-guides/guidance/12-function-specs/FS-061_OCR_marking.md>) |
| `docs/12-function-specs/FS-062_Solder_joint_post_reflow.md` | [docs/process-guides/guidance/12-function-specs/FS-062_Solder_joint_post_reflow.md](<../process-guides/guidance/12-function-specs/FS-062_Solder_joint_post_reflow.md>) |
| `docs/12-function-specs/FS-063_Review_rework.md` | [docs/process-guides/guidance/12-function-specs/FS-063_Review_rework.md](<../process-guides/guidance/12-function-specs/FS-063_Review_rework.md>) |
| `docs/12-function-specs/FS-064_SPC_chart.md` | [docs/shared-modules/guidance/12-function-specs/FS-064_SPC_chart.md](<../shared-modules/guidance/12-function-specs/FS-064_SPC_chart.md>) |
| `docs/12-function-specs/FS-065_Cross_process_correlation.md` | [docs/shared-modules/guidance/12-function-specs/FS-065_Cross_process_correlation.md](<../shared-modules/guidance/12-function-specs/FS-065_Cross_process_correlation.md>) |
| `docs/12-function-specs/FS-066_Disposition_projection.md` | [docs/shared-modules/guidance/12-function-specs/FS-066_Disposition_projection.md](<../shared-modules/guidance/12-function-specs/FS-066_Disposition_projection.md>) |
| `docs/12-function-specs/FS-067_AI_assisted_review.md` | [docs/shared-modules/guidance/12-function-specs/FS-067_AI_assisted_review.md](<../shared-modules/guidance/12-function-specs/FS-067_AI_assisted_review.md>) |
| `docs/12-function-specs/FS-068_Program_synthesis.md` | [docs/shared-modules/guidance/12-function-specs/FS-068_Program_synthesis.md](<../shared-modules/guidance/12-function-specs/FS-068_Program_synthesis.md>) |
| `docs/12-function-specs/FS-069_AI_validation.md` | [docs/shared-modules/guidance/12-function-specs/FS-069_AI_validation.md](<../shared-modules/guidance/12-function-specs/FS-069_AI_validation.md>) |
| `docs/14-page-contracts/UI-PCS-001_Production_Overview.md` | [docs/shared-modules/guidance/14-page-contracts/UI-PCS-001_Production_Overview.md](<../shared-modules/guidance/14-page-contracts/UI-PCS-001_Production_Overview.md>) |
| `docs/14-page-contracts/UI-PCS-002_Vision_Workspace.md` | [docs/shared-modules/guidance/14-page-contracts/UI-PCS-002_Vision_Workspace.md](<../shared-modules/guidance/14-page-contracts/UI-PCS-002_Vision_Workspace.md>) |
| `docs/14-page-contracts/UI-PCS-003_Program_Editor.md` | [docs/shared-modules/guidance/14-page-contracts/UI-PCS-003_Program_Editor.md](<../shared-modules/guidance/14-page-contracts/UI-PCS-003_Program_Editor.md>) |
| `docs/14-page-contracts/UI-PCS-004_Recipe_Editor.md` | [docs/shared-modules/guidance/14-page-contracts/UI-PCS-004_Recipe_Editor.md](<../shared-modules/guidance/14-page-contracts/UI-PCS-004_Recipe_Editor.md>) |
| `docs/14-page-contracts/UI-PCS-005_Review_Workspace.md` | [docs/shared-modules/guidance/14-page-contracts/UI-PCS-005_Review_Workspace.md](<../shared-modules/guidance/14-page-contracts/UI-PCS-005_Review_Workspace.md>) |
| `docs/14-page-contracts/UI-PCS-006_Metrology_Workspace.md` | [docs/shared-modules/guidance/14-page-contracts/UI-PCS-006_Metrology_Workspace.md](<../shared-modules/guidance/14-page-contracts/UI-PCS-006_Metrology_Workspace.md>) |
| `docs/14-page-contracts/UI-PCS-007_Calibration_Workspace.md` | [docs/shared-modules/guidance/14-page-contracts/UI-PCS-007_Calibration_Workspace.md](<../shared-modules/guidance/14-page-contracts/UI-PCS-007_Calibration_Workspace.md>) |
| `docs/14-page-contracts/UI-PCS-008_SPC_Workspace.md` | [docs/shared-modules/guidance/14-page-contracts/UI-PCS-008_SPC_Workspace.md](<../shared-modules/guidance/14-page-contracts/UI-PCS-008_SPC_Workspace.md>) |
| `docs/14-page-contracts/UI-PCS-009_Manifest_Inspector.md` | [docs/shared-modules/guidance/14-page-contracts/UI-PCS-009_Manifest_Inspector.md](<../shared-modules/guidance/14-page-contracts/UI-PCS-009_Manifest_Inspector.md>) |
| `docs/14-page-contracts/UI-PCS-010_Device_Station.md` | [docs/shared-modules/guidance/14-page-contracts/UI-PCS-010_Device_Station.md](<../shared-modules/guidance/14-page-contracts/UI-PCS-010_Device_Station.md>) |
| `docs/14-page-contracts/UI-PCS-011_Quality_Hub.md` | [docs/shared-modules/guidance/14-page-contracts/UI-PCS-011_Quality_Hub.md](<../shared-modules/guidance/14-page-contracts/UI-PCS-011_Quality_Hub.md>) |
| `docs/14-page-contracts/UI-PCS-012_NPI_Auto_Program.md` | [docs/shared-modules/guidance/14-page-contracts/UI-PCS-012_NPI_Auto_Program.md](<../shared-modules/guidance/14-page-contracts/UI-PCS-012_NPI_Auto_Program.md>) |
| `docs/14-page-contracts/UI-PCS-013_Evidence_Viewer.md` | [docs/shared-modules/guidance/14-page-contracts/UI-PCS-013_Evidence_Viewer.md](<../shared-modules/guidance/14-page-contracts/UI-PCS-013_Evidence_Viewer.md>) |
| `docs/14-page-contracts/UI-PCS-014_Engineering_Diagnostics.md` | [docs/shared-modules/guidance/14-page-contracts/UI-PCS-014_Engineering_Diagnostics.md](<../shared-modules/guidance/14-page-contracts/UI-PCS-014_Engineering_Diagnostics.md>) |
| `docs/14-page-contracts/UI-PCS-015_PCB_Inspection_Workbench.md` | [docs/process-guides/guidance/14-page-contracts/UI-PCS-015_PCB_Inspection_Workbench.md](<../process-guides/guidance/14-page-contracts/UI-PCS-015_PCB_Inspection_Workbench.md>) |
| `docs/14-page-contracts/UI-PCS-016_HDI_FPC_RigidFlex_Workbench.md` | [docs/process-guides/guidance/14-page-contracts/UI-PCS-016_HDI_FPC_RigidFlex_Workbench.md](<../process-guides/guidance/14-page-contracts/UI-PCS-016_HDI_FPC_RigidFlex_Workbench.md>) |
| `docs/14-page-contracts/UI-PCS-017_Stencil_Inspection_Workbench.md` | [docs/process-guides/guidance/14-page-contracts/UI-PCS-017_Stencil_Inspection_Workbench.md](<../process-guides/guidance/14-page-contracts/UI-PCS-017_Stencil_Inspection_Workbench.md>) |
| `docs/14-page-contracts/UI-PCS-018_SPI_Production_Workbench.md` | [docs/process-guides/guidance/14-page-contracts/UI-PCS-018_SPI_Production_Workbench.md](<../process-guides/guidance/14-page-contracts/UI-PCS-018_SPI_Production_Workbench.md>) |
| `docs/14-page-contracts/UI-PCS-019_SPI_Programming_Workbench.md` | [docs/process-guides/guidance/14-page-contracts/UI-PCS-019_SPI_Programming_Workbench.md](<../process-guides/guidance/14-page-contracts/UI-PCS-019_SPI_Programming_Workbench.md>) |
| `docs/14-page-contracts/UI-PCS-020_AOI_Programming_and_Production_Workbench.md` | [docs/process-guides/guidance/14-page-contracts/UI-PCS-020_AOI_Programming_and_Production_Workbench.md](<../process-guides/guidance/14-page-contracts/UI-PCS-020_AOI_Programming_and_Production_Workbench.md>) |
| `docs/14-page-contracts/UI-PCS-021_Quality_Control_Workbench.md` | [docs/shared-modules/guidance/14-page-contracts/UI-PCS-021_Quality_Control_Workbench.md](<../shared-modules/guidance/14-page-contracts/UI-PCS-021_Quality_Control_Workbench.md>) |
| `docs/14-device-specs/CAPABILITY_MATRIX.md` | [docs/process-guides/device-specs/CAPABILITY_MATRIX.md](<../process-guides/device-specs/CAPABILITY_MATRIX.md>) |
| `docs/14-device-specs/DEVICE_SPEC_TEMPLATE.md` | [docs/process-guides/device-specs/DEVICE_SPEC_TEMPLATE.md](<../process-guides/device-specs/DEVICE_SPEC_TEMPLATE.md>) |
| `docs/14-device-specs/README.md` | [docs/process-guides/device-specs/README.md](<../process-guides/device-specs/README.md>) |
| `docs/14-device-specs/02d-aoi/CAPABILITIES.md` | [docs/process-guides/device-specs/02d-aoi/CAPABILITIES.md](<../process-guides/device-specs/02d-aoi/CAPABILITIES.md>) |
| `docs/14-device-specs/02d-aoi/DEVICE_SPEC.md` | [docs/process-guides/device-specs/02d-aoi/DEVICE_SPEC.md](<../process-guides/device-specs/02d-aoi/DEVICE_SPEC.md>) |
| `docs/14-device-specs/02d-aoi/FEATURES.md` | [docs/process-guides/device-specs/02d-aoi/FEATURES.md](<../process-guides/device-specs/02d-aoi/FEATURES.md>) |
| `docs/14-device-specs/02d-aoi/MEASUREMENTS.md` | [docs/process-guides/device-specs/02d-aoi/MEASUREMENTS.md](<../process-guides/device-specs/02d-aoi/MEASUREMENTS.md>) |
| `docs/14-device-specs/02d-aoi/QUALITY.md` | [docs/process-guides/device-specs/02d-aoi/QUALITY.md](<../process-guides/device-specs/02d-aoi/QUALITY.md>) |
| `docs/14-device-specs/02d-aoi/README.md` | [docs/process-guides/device-specs/02d-aoi/README.md](<../process-guides/device-specs/02d-aoi/README.md>) |
| `docs/14-device-specs/02d-aoi/UI_WORKFLOW.md` | [docs/process-guides/device-specs/02d-aoi/UI_WORKFLOW.md](<../process-guides/device-specs/02d-aoi/UI_WORKFLOW.md>) |
| `docs/14-device-specs/02d-aoi/VENDOR_ADAPTER.md` | [docs/process-guides/device-specs/02d-aoi/VENDOR_ADAPTER.md](<../process-guides/device-specs/02d-aoi/VENDOR_ADAPTER.md>) |
| `docs/14-device-specs/02d-xray/CAPABILITIES.md` | [docs/process-guides/device-specs/02d-xray/CAPABILITIES.md](<../process-guides/device-specs/02d-xray/CAPABILITIES.md>) |
| `docs/14-device-specs/02d-xray/DEVICE_SPEC.md` | [docs/process-guides/device-specs/02d-xray/DEVICE_SPEC.md](<../process-guides/device-specs/02d-xray/DEVICE_SPEC.md>) |
| `docs/14-device-specs/02d-xray/FEATURES.md` | [docs/process-guides/device-specs/02d-xray/FEATURES.md](<../process-guides/device-specs/02d-xray/FEATURES.md>) |
| `docs/14-device-specs/02d-xray/MEASUREMENTS.md` | [docs/process-guides/device-specs/02d-xray/MEASUREMENTS.md](<../process-guides/device-specs/02d-xray/MEASUREMENTS.md>) |
| `docs/14-device-specs/02d-xray/QUALITY.md` | [docs/process-guides/device-specs/02d-xray/QUALITY.md](<../process-guides/device-specs/02d-xray/QUALITY.md>) |
| `docs/14-device-specs/02d-xray/README.md` | [docs/process-guides/device-specs/02d-xray/README.md](<../process-guides/device-specs/02d-xray/README.md>) |
| `docs/14-device-specs/02d-xray/UI_WORKFLOW.md` | [docs/process-guides/device-specs/02d-xray/UI_WORKFLOW.md](<../process-guides/device-specs/02d-xray/UI_WORKFLOW.md>) |
| `docs/14-device-specs/02d-xray/VENDOR_ADAPTER.md` | [docs/process-guides/device-specs/02d-xray/VENDOR_ADAPTER.md](<../process-guides/device-specs/02d-xray/VENDOR_ADAPTER.md>) |
| `docs/14-device-specs/03d-aoi/CAPABILITIES.md` | [docs/process-guides/device-specs/03d-aoi/CAPABILITIES.md](<../process-guides/device-specs/03d-aoi/CAPABILITIES.md>) |
| `docs/14-device-specs/03d-aoi/DEVICE_SPEC.md` | [docs/process-guides/device-specs/03d-aoi/DEVICE_SPEC.md](<../process-guides/device-specs/03d-aoi/DEVICE_SPEC.md>) |
| `docs/14-device-specs/03d-aoi/FEATURES.md` | [docs/process-guides/device-specs/03d-aoi/FEATURES.md](<../process-guides/device-specs/03d-aoi/FEATURES.md>) |
| `docs/14-device-specs/03d-aoi/MEASUREMENTS.md` | [docs/process-guides/device-specs/03d-aoi/MEASUREMENTS.md](<../process-guides/device-specs/03d-aoi/MEASUREMENTS.md>) |
| `docs/14-device-specs/03d-aoi/QUALITY.md` | [docs/process-guides/device-specs/03d-aoi/QUALITY.md](<../process-guides/device-specs/03d-aoi/QUALITY.md>) |
| `docs/14-device-specs/03d-aoi/README.md` | [docs/process-guides/device-specs/03d-aoi/README.md](<../process-guides/device-specs/03d-aoi/README.md>) |
| `docs/14-device-specs/03d-aoi/UI_WORKFLOW.md` | [docs/process-guides/device-specs/03d-aoi/UI_WORKFLOW.md](<../process-guides/device-specs/03d-aoi/UI_WORKFLOW.md>) |
| `docs/14-device-specs/03d-aoi/VENDOR_ADAPTER.md` | [docs/process-guides/device-specs/03d-aoi/VENDOR_ADAPTER.md](<../process-guides/device-specs/03d-aoi/VENDOR_ADAPTER.md>) |
| `docs/14-device-specs/03d-axi-ct/CAPABILITIES.md` | [docs/process-guides/device-specs/03d-axi-ct/CAPABILITIES.md](<../process-guides/device-specs/03d-axi-ct/CAPABILITIES.md>) |
| `docs/14-device-specs/03d-axi-ct/DEVICE_SPEC.md` | [docs/process-guides/device-specs/03d-axi-ct/DEVICE_SPEC.md](<../process-guides/device-specs/03d-axi-ct/DEVICE_SPEC.md>) |
| `docs/14-device-specs/03d-axi-ct/FEATURES.md` | [docs/process-guides/device-specs/03d-axi-ct/FEATURES.md](<../process-guides/device-specs/03d-axi-ct/FEATURES.md>) |
| `docs/14-device-specs/03d-axi-ct/MEASUREMENTS.md` | [docs/process-guides/device-specs/03d-axi-ct/MEASUREMENTS.md](<../process-guides/device-specs/03d-axi-ct/MEASUREMENTS.md>) |
| `docs/14-device-specs/03d-axi-ct/QUALITY.md` | [docs/process-guides/device-specs/03d-axi-ct/QUALITY.md](<../process-guides/device-specs/03d-axi-ct/QUALITY.md>) |
| `docs/14-device-specs/03d-axi-ct/README.md` | [docs/process-guides/device-specs/03d-axi-ct/README.md](<../process-guides/device-specs/03d-axi-ct/README.md>) |
| `docs/14-device-specs/03d-axi-ct/UI_WORKFLOW.md` | [docs/process-guides/device-specs/03d-axi-ct/UI_WORKFLOW.md](<../process-guides/device-specs/03d-axi-ct/UI_WORKFLOW.md>) |
| `docs/14-device-specs/03d-axi-ct/VENDOR_ADAPTER.md` | [docs/process-guides/device-specs/03d-axi-ct/VENDOR_ADAPTER.md](<../process-guides/device-specs/03d-axi-ct/VENDOR_ADAPTER.md>) |
| `docs/14-device-specs/03d-spi/CAPABILITIES.md` | [docs/process-guides/device-specs/03d-spi/CAPABILITIES.md](<../process-guides/device-specs/03d-spi/CAPABILITIES.md>) |
| `docs/14-device-specs/03d-spi/DEVICE_SPEC.md` | [docs/process-guides/device-specs/03d-spi/DEVICE_SPEC.md](<../process-guides/device-specs/03d-spi/DEVICE_SPEC.md>) |
| `docs/14-device-specs/03d-spi/FEATURES.md` | [docs/process-guides/device-specs/03d-spi/FEATURES.md](<../process-guides/device-specs/03d-spi/FEATURES.md>) |
| `docs/14-device-specs/03d-spi/FEATURE_EXECUTION_CONTRACT.md` | [docs/process-guides/device-specs/03d-spi/FEATURE_EXECUTION_CONTRACT.md](<../process-guides/device-specs/03d-spi/FEATURE_EXECUTION_CONTRACT.md>) |
| `docs/14-device-specs/03d-spi/FEATURE_TRACEABILITY.md` | [docs/process-guides/device-specs/03d-spi/FEATURE_TRACEABILITY.md](<../process-guides/device-specs/03d-spi/FEATURE_TRACEABILITY.md>) |
| `docs/14-device-specs/03d-spi/MEASUREMENTS.md` | [docs/process-guides/device-specs/03d-spi/MEASUREMENTS.md](<../process-guides/device-specs/03d-spi/MEASUREMENTS.md>) |
| `docs/14-device-specs/03d-spi/PARAMETER_AUTHORITY.md` | [docs/process-guides/device-specs/03d-spi/PARAMETER_AUTHORITY.md](<../process-guides/device-specs/03d-spi/PARAMETER_AUTHORITY.md>) |
| `docs/14-device-specs/03d-spi/QUALIFICATION_GATES.md` | [docs/process-guides/device-specs/03d-spi/QUALIFICATION_GATES.md](<../process-guides/device-specs/03d-spi/QUALIFICATION_GATES.md>) |
| `docs/14-device-specs/03d-spi/QUALITY.md` | [docs/process-guides/device-specs/03d-spi/QUALITY.md](<../process-guides/device-specs/03d-spi/QUALITY.md>) |
| `docs/14-device-specs/03d-spi/README.md` | [docs/process-guides/device-specs/03d-spi/README.md](<../process-guides/device-specs/03d-spi/README.md>) |
| `docs/14-device-specs/03d-spi/UI_WORKFLOW.md` | [docs/process-guides/device-specs/03d-spi/UI_WORKFLOW.md](<../process-guides/device-specs/03d-spi/UI_WORKFLOW.md>) |
| `docs/14-device-specs/03d-spi/VENDOR_ADAPTER.md` | [docs/process-guides/device-specs/03d-spi/VENDOR_ADAPTER.md](<../process-guides/device-specs/03d-spi/VENDOR_ADAPTER.md>) |
| `docs/14-device-specs/03d-spi/inspection-features/F001-paste-presence.md` | [docs/process-guides/device-specs/03d-spi/inspection-features/F001-paste-presence.md](<../process-guides/device-specs/03d-spi/inspection-features/F001-paste-presence.md>) |
| `docs/14-device-specs/03d-spi/inspection-features/F002-paste-area.md` | [docs/process-guides/device-specs/03d-spi/inspection-features/F002-paste-area.md](<../process-guides/device-specs/03d-spi/inspection-features/F002-paste-area.md>) |
| `docs/14-device-specs/03d-spi/inspection-features/F003-paste-height.md` | [docs/process-guides/device-specs/03d-spi/inspection-features/F003-paste-height.md](<../process-guides/device-specs/03d-spi/inspection-features/F003-paste-height.md>) |
| `docs/14-device-specs/03d-spi/inspection-features/F004-paste-volume.md` | [docs/process-guides/device-specs/03d-spi/inspection-features/F004-paste-volume.md](<../process-guides/device-specs/03d-spi/inspection-features/F004-paste-volume.md>) |
| `docs/14-device-specs/03d-spi/inspection-features/F005-paste-offset.md` | [docs/process-guides/device-specs/03d-spi/inspection-features/F005-paste-offset.md](<../process-guides/device-specs/03d-spi/inspection-features/F005-paste-offset.md>) |
| `docs/14-device-specs/03d-spi/inspection-features/F006-paste-shape.md` | [docs/process-guides/device-specs/03d-spi/inspection-features/F006-paste-shape.md](<../process-guides/device-specs/03d-spi/inspection-features/F006-paste-shape.md>) |
| `docs/14-device-specs/03d-spi/inspection-features/F007-paste-coplanarity.md` | [docs/process-guides/device-specs/03d-spi/inspection-features/F007-paste-coplanarity.md](<../process-guides/device-specs/03d-spi/inspection-features/F007-paste-coplanarity.md>) |
| `docs/14-device-specs/03d-spi/inspection-features/F008-bridging-risk.md` | [docs/process-guides/device-specs/03d-spi/inspection-features/F008-bridging-risk.md](<../process-guides/device-specs/03d-spi/inspection-features/F008-bridging-risk.md>) |
| `docs/14-device-specs/fct/CAPABILITIES.md` | [docs/process-guides/device-specs/fct/CAPABILITIES.md](<../process-guides/device-specs/fct/CAPABILITIES.md>) |
| `docs/14-device-specs/fct/DEVICE_SPEC.md` | [docs/process-guides/device-specs/fct/DEVICE_SPEC.md](<../process-guides/device-specs/fct/DEVICE_SPEC.md>) |
| `docs/14-device-specs/fct/FEATURES.md` | [docs/process-guides/device-specs/fct/FEATURES.md](<../process-guides/device-specs/fct/FEATURES.md>) |
| `docs/14-device-specs/fct/MEASUREMENTS.md` | [docs/process-guides/device-specs/fct/MEASUREMENTS.md](<../process-guides/device-specs/fct/MEASUREMENTS.md>) |
| `docs/14-device-specs/fct/QUALITY.md` | [docs/process-guides/device-specs/fct/QUALITY.md](<../process-guides/device-specs/fct/QUALITY.md>) |
| `docs/14-device-specs/fct/README.md` | [docs/process-guides/device-specs/fct/README.md](<../process-guides/device-specs/fct/README.md>) |
| `docs/14-device-specs/fct/UI_WORKFLOW.md` | [docs/process-guides/device-specs/fct/UI_WORKFLOW.md](<../process-guides/device-specs/fct/UI_WORKFLOW.md>) |
| `docs/14-device-specs/fct/VENDOR_ADAPTER.md` | [docs/process-guides/device-specs/fct/VENDOR_ADAPTER.md](<../process-guides/device-specs/fct/VENDOR_ADAPTER.md>) |
| `docs/14-device-specs/ict/CAPABILITIES.md` | [docs/process-guides/device-specs/ict/CAPABILITIES.md](<../process-guides/device-specs/ict/CAPABILITIES.md>) |
| `docs/14-device-specs/ict/DEVICE_SPEC.md` | [docs/process-guides/device-specs/ict/DEVICE_SPEC.md](<../process-guides/device-specs/ict/DEVICE_SPEC.md>) |
| `docs/14-device-specs/ict/FEATURES.md` | [docs/process-guides/device-specs/ict/FEATURES.md](<../process-guides/device-specs/ict/FEATURES.md>) |
| `docs/14-device-specs/ict/MEASUREMENTS.md` | [docs/process-guides/device-specs/ict/MEASUREMENTS.md](<../process-guides/device-specs/ict/MEASUREMENTS.md>) |
| `docs/14-device-specs/ict/QUALITY.md` | [docs/process-guides/device-specs/ict/QUALITY.md](<../process-guides/device-specs/ict/QUALITY.md>) |
| `docs/14-device-specs/ict/README.md` | [docs/process-guides/device-specs/ict/README.md](<../process-guides/device-specs/ict/README.md>) |
| `docs/14-device-specs/ict/UI_WORKFLOW.md` | [docs/process-guides/device-specs/ict/UI_WORKFLOW.md](<../process-guides/device-specs/ict/UI_WORKFLOW.md>) |
| `docs/14-device-specs/ict/VENDOR_ADAPTER.md` | [docs/process-guides/device-specs/ict/VENDOR_ADAPTER.md](<../process-guides/device-specs/ict/VENDOR_ADAPTER.md>) |
| `docs/14-device-specs/metrology/CAPABILITIES.md` | [docs/process-guides/device-specs/metrology/CAPABILITIES.md](<../process-guides/device-specs/metrology/CAPABILITIES.md>) |
| `docs/14-device-specs/metrology/DEVICE_SPEC.md` | [docs/process-guides/device-specs/metrology/DEVICE_SPEC.md](<../process-guides/device-specs/metrology/DEVICE_SPEC.md>) |
| `docs/14-device-specs/metrology/FEATURES.md` | [docs/process-guides/device-specs/metrology/FEATURES.md](<../process-guides/device-specs/metrology/FEATURES.md>) |
| `docs/14-device-specs/metrology/MEASUREMENTS.md` | [docs/process-guides/device-specs/metrology/MEASUREMENTS.md](<../process-guides/device-specs/metrology/MEASUREMENTS.md>) |
| `docs/14-device-specs/metrology/QUALITY.md` | [docs/process-guides/device-specs/metrology/QUALITY.md](<../process-guides/device-specs/metrology/QUALITY.md>) |
| `docs/14-device-specs/metrology/README.md` | [docs/process-guides/device-specs/metrology/README.md](<../process-guides/device-specs/metrology/README.md>) |
| `docs/14-device-specs/metrology/UI_WORKFLOW.md` | [docs/process-guides/device-specs/metrology/UI_WORKFLOW.md](<../process-guides/device-specs/metrology/UI_WORKFLOW.md>) |
| `docs/14-device-specs/metrology/VENDOR_ADAPTER.md` | [docs/process-guides/device-specs/metrology/VENDOR_ADAPTER.md](<../process-guides/device-specs/metrology/VENDOR_ADAPTER.md>) |
| `docs/14-device-specs/pcb-bare-board/CAPABILITIES.md` | [docs/process-guides/device-specs/pcb-bare-board/CAPABILITIES.md](<../process-guides/device-specs/pcb-bare-board/CAPABILITIES.md>) |
| `docs/14-device-specs/pcb-bare-board/DEVICE_SPEC.md` | [docs/process-guides/device-specs/pcb-bare-board/DEVICE_SPEC.md](<../process-guides/device-specs/pcb-bare-board/DEVICE_SPEC.md>) |
| `docs/14-device-specs/pcb-bare-board/FEATURES.md` | [docs/process-guides/device-specs/pcb-bare-board/FEATURES.md](<../process-guides/device-specs/pcb-bare-board/FEATURES.md>) |
| `docs/14-device-specs/pcb-bare-board/MEASUREMENTS.md` | [docs/process-guides/device-specs/pcb-bare-board/MEASUREMENTS.md](<../process-guides/device-specs/pcb-bare-board/MEASUREMENTS.md>) |
| `docs/14-device-specs/pcb-bare-board/QUALITY.md` | [docs/process-guides/device-specs/pcb-bare-board/QUALITY.md](<../process-guides/device-specs/pcb-bare-board/QUALITY.md>) |
| `docs/14-device-specs/pcb-bare-board/README.md` | [docs/process-guides/device-specs/pcb-bare-board/README.md](<../process-guides/device-specs/pcb-bare-board/README.md>) |
| `docs/14-device-specs/pcb-bare-board/UI_WORKFLOW.md` | [docs/process-guides/device-specs/pcb-bare-board/UI_WORKFLOW.md](<../process-guides/device-specs/pcb-bare-board/UI_WORKFLOW.md>) |
| `docs/14-device-specs/pcb-bare-board/VENDOR_ADAPTER.md` | [docs/process-guides/device-specs/pcb-bare-board/VENDOR_ADAPTER.md](<../process-guides/device-specs/pcb-bare-board/VENDOR_ADAPTER.md>) |

## 本轮研究与细化定位

- [REF-007 未开发机台竞品研究与设计落点](../references/REF-007_未开发机台竞品研究与设计落点.md)：20份新增官方资料、既有点胶PDF、观察/推导/未知与PG/SM消费者。
- [REF-002](../references/REF-002_GitHub_DevExpress与OpenSource研究基线.md)：补OpenCV、Open3D、scikit-image固定源码/测试/依赖/许可证阅读；不引入产品依赖。
- [制程目录](../process-guides/README.md)列研究顺序及19份PG的细化位置；[公共目录](../shared-modules/README.md)列16份SM的新增独立能力要求。原ID与既有FS绑定保持不变，新增功能未绑定部分仍需正式切片冻结。

## 历史来源

[原架构源](../00-baseline/ARCH-PCBA-VISION-001_v0.5.3_source.md)、architecture_review、10-audit、01-validation、PHASE1台账和既有Master用于追溯，不计入当前设计通过。DEV-PLAN-001～015仍保留原实现映射，仅按用户选定切片重新准入，不能据旧69项/波次自动开展全平台编码。references/competitors与用户心得是来源资料，不扫描为规范ID集合。
