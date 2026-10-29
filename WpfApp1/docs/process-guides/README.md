# 各制程与检测机台开发指导

按工艺目的组织，2D/3D、在线/离线和双面是能力变体。下面是全制程平台的候选产品覆盖，不表示全部机台已经选为首批产品；研究顺序已由用户确定，首台投产机型和交期仍待产品决定。23份指导自0.3.0基线起持续细化（版本见各页），现有72项功能分别链接本页专项实施卡，细化算法、模块、操作与拟验收；具体型号、质量阈值和未批准契约仍需冻结。

| 指导 | 制程 | 机台/能力变体 | 当前成熟度 |
|---|---|---|---|
| [PG-001](<processes/PG-001_incoming-material.md>) | PCB来料与材料表面 | 片料/板料2D外观工位；厚度需独立量测输入 | DesignReview |
| [PG-002](<processes/PG-002_drill.md>) | 机械钻孔后检测 | 透射/反射2D孔检；深度/沉孔按真实3D输入扩展 | DesignReview |
| [PG-003](<processes/PG-003_laser-via.md>) | 激光微孔与HDI开口 | 高分辨率2D微孔工位；可观测3D形貌变体 | DesignReview |
| [PG-004](<processes/PG-004_layer-registration.md>) | 层间对位与积层核对 | 可见基准/窗口光学对位检测工位 | DesignReview |
| [PG-005](<processes/PG-005_via-fill.md>) | 塞孔、填孔与研磨后形貌 | 表面2D+高度量测工位 | DesignReview |
| [PG-006](<processes/PG-006_soldermask-legend.md>) | 阻焊与字符印刷后检测 | 彩色/多通道2D外观工位；3D厚度另议 | DesignReview |
| [PG-007](<processes/PG-007_surface-finish.md>) | 表面处理后可见外观 | 表面镀覆/沉金等2D外观检测工位 | DesignReview |
| [PG-008](<processes/PG-008_fpc-coverlay.md>) | FPC覆盖膜与补强贴合 | 片式FPC覆盖膜/补强2D与适用3D检测 | DesignReview |
| [PG-009](<processes/PG-009_rigid-flex.md>) | 软硬结合过渡区 | 软硬结合板局部2D/3D外观与尺寸工位 | DesignReview |
| [PG-010](<processes/PG-010_outline.md>) | 成型、铣边与V-Cut | 2D轮廓尺寸工位；槽深/残厚需合适量测能力 | DesignReview |
| [PG-011](<processes/PG-011_final-avi.md>) | PCB终检AVI与翘曲 | 成品板双面2D外观及适用高度工位 | DesignReview |
| [PG-012](<processes/PG-012_r2r.md>) | FPC卷料与连续走带检测 | 线扫/连续面扫R2R工位 | DesignReview |
| [PG-013](<processes/PG-013_stencil.md>) | 钢网制造与清洗后检测 | 钢网2D开口外观；3D厚度/壁面按设备能力配置 | DesignReview |
| [PG-014](<processes/PG-014_spi.md>) | 锡膏印刷后SPI | 在线/离线3D SPI；2D仅限具备证据的外观项目 | DesignReview |
| [PG-015](<processes/PG-015_pcba-incoming.md>) | PCBA来料与首件核对 | 元件/治具/板级首件2D核对工作站 | DesignReview |
| [PG-016](<processes/PG-016_dispense.md>) | 点胶、胶路与胶点检测 | 点胶后2D/3D视觉工位 | DesignReview |
| [PG-017](<processes/PG-017_pre-reflow-aoi.md>) | 贴片后炉前AOI | 在线/离线2D或3D炉前AOI | DesignReview |
| [PG-018](<processes/PG-018_post-reflow-aoi.md>) | 回流焊后AOI | 2D多角度/3D炉后AOI；双面为能力变体 | DesignReview |
| [PG-019](<processes/PG-019_insertion.md>) | 插件与压接后检测 | 插件/压接2D与高度量测工位 | DesignReview |
| [PG-020](<processes/PG-020_wave-solder.md>) | 波峰焊与选择焊后检测 | 底面/斜视2D与适用3D焊点检测 | DesignReview |
| [PG-021](<processes/PG-021_coating.md>) | 三防涂覆后检测 | UV/可见光覆盖与适用3D检测工位 | DesignReview |
| [PG-022](<processes/PG-022_final-assembly.md>) | 灌封与最终装配视觉终检 | 灌封表面/连接器/紧固件/标签终检工位 | DesignReview |
| [PG-023](<processes/PG-023_review-rework.md>) | 跨制程复判、返修与复测 | 独立复判工作站；机旁复判；返修记录终端 | DesignReview |

下列仅保留入口：已完成蚀刻线路检测[等待接入](<device-specs/pcb-bare-board/README.md>)；[X-Ray](<device-specs/02d-xray/README.md>)、[CT/AXI](<device-specs/03d-axi-ct/README.md>)、[ICT](<device-specs/ict/README.md>)、[FCT](<device-specs/fct/README.md>)暂缓。此轮不新增其详细方案，历史资料保留。

[公共模块](../shared-modules/README.md)与本目录分别维护。`guidance/`保存迁移后的既有领域/功能/页面文件，ID不变；`processes/`解释工艺与机台组合；[端到端链路](END-TO-END-FLOWS.md)规定跨模块交接。既有[设备规格层](<device-specs/README.md>)继续承载具体设备Profile和既有细项，不能单按2D/3D目录代替工艺定义。

研究按下节用户确认顺序推进；现有SPI/AOI继续作为复用和迁移验证消费者，首台投产和具体实现顺序另按产品决定冻结。不能从“23份文档已存在”推出可同时自动开发。

## 2026-09-27 未开发机台研究与细化

各文档保持DesignReview：新增内容给出了被测量定义、输入条件、计算/操作链和失败断言，尚未将候选参数/接口自动批准。证据、来源页码及缺口集中在[REF-007](../references/REF-007_未开发机台竞品研究与设计落点.md)，开源源码/测试的借鉴见[REF-002](../references/REF-002_GitHub_DevExpress与OpenSource研究基线.md)。

| 用户确认顺序 | 直接阅读 | 本轮细化位置 |
|---|---|---|
| 1 钻孔/微孔 | [PG-002](processes/PG-002_drill.md)、[PG-003](processes/PG-003_laser-via.md) | §9–11：孔型/工序、目标对应、物理几何、可见孔底/深度、异常与验收 |
| 2 阻焊与终检 | [PG-006](processes/PG-006_soldermask-legend.md)、[PG-011](processes/PG-011_final-avi.md) | §9–11：层极性、应涂/开窗/字符、材料分区、双面与翘曲、复判链 |
| 3 钢网 | [PG-013](processes/PG-013_stencil.md) | §9–11：制造/实物参考、尺寸/位置、清洁度、厚度/孔壁的能力条件 |
| 4 点胶/涂覆 | [PG-016](processes/PG-016_dispense.md)、[PG-021](processes/PG-021_coating.md) | §9–14：点/路/结点、截面与有效体积、表面/多视角/膜厚、P0–P7快编及组合失败；UI-PCS-022/023专属页面设计 |
| 5 插件与焊后 | [PG-019](processes/PG-019_insertion.md)、[PG-020](processes/PG-020_wave-solder.md) | §9–14：针型/稳定针序、轴/端/基准、指定截面间距、锡峰/针端、同网禁连、P0–P7及组合失败；UI-PCS-024/025与交互样例 |
| 相关工序补齐 | PG-001/004/005/007/008/009/010/012/015/022 | §9：来料、对位、填孔、表面处理、柔性/软硬结合、外形、卷料、首件和最终装配的执行细项；专用手册不足处明确保留未知 |

PG-002/003在各自快速编程段后另有[方法/数据/性能/UI准入](processes/PG-002_drill.md#pg-002-ai-data-performance-ui)与[微孔对应准入](processes/PG-003_laser-via.md#pg-003-ai-data-performance-ui)，用于把规则、经典视觉、AI候选、真值分组、负载预算和页面操作接到可编码切片；数值阈值、正式Contract和真实样本仍由对应Profile采纳。PG-001/004/005/007/008已增加同等深度的[来料附录](processes/PG-001_incoming-material.md#pg-001-ai-data-performance-ui)、[层间对位附录](processes/PG-004_layer-registration.md#pg-004-ai-data-performance-ui)、[填孔形貌附录](processes/PG-005_via-fill.md#pg-005-ai-data-performance-ui)、[表面处理附录](processes/PG-007_surface-finish.md#pg-007-ai-data-performance-ui)和[FPC覆盖膜附录](processes/PG-008_fpc-coverlay.md#pg-008-ai-data-performance-ui)；PG-009/010/012/014/015已补充[软硬结合](processes/PG-009_rigid-flex.md#pg-009-ai-data-performance-ui)、[成型外形](processes/PG-010_outline.md#pg-010-ai-data-performance-ui)、[R2R卷料](processes/PG-012_r2r.md#pg-012-ai-data-performance-ui)、[SPI](processes/PG-014_spi.md#pg-014-ai-data-performance-ui)和[PCBA来料](processes/PG-015_pcba-incoming.md#pg-015-ai-data-performance-ui)附录。
PG-002/003在各自快速编程段后另有[方法/数据/性能/UI准入](processes/PG-002_drill.md#pg-002-ai-data-performance-ui)与[微孔对应准入](processes/PG-003_laser-via.md#pg-003-ai-data-performance-ui)，用于把规则、经典视觉、AI候选、真值分组、负载预算和页面操作接到可编码切片；数值阈值、正式Contract和真实样本仍由对应Profile采纳。PG-001/004/005/007/008已增加同等深度的[来料附录](processes/PG-001_incoming-material.md#pg-001-ai-data-performance-ui)、[层间对位附录](processes/PG-004_layer-registration.md#pg-004-ai-data-performance-ui)、[填孔形貌附录](processes/PG-005_via-fill.md#pg-005-ai-data-performance-ui)、[表面处理附录](processes/PG-007_surface-finish.md#pg-007-ai-data-performance-ui)和[FPC覆盖膜附录](processes/PG-008_fpc-coverlay.md#pg-008-ai-data-performance-ui)；PG-009/010/012/014/015已补充[软硬结合](processes/PG-009_rigid-flex.md#pg-009-ai-data-performance-ui)、[成型外形](processes/PG-010_outline.md#pg-010-ai-data-performance-ui)、[R2R卷料](processes/PG-012_r2r.md#pg-012-ai-data-performance-ui)、[SPI](processes/PG-014_spi.md#pg-014-ai-data-performance-ui)和[PCBA来料](processes/PG-015_pcba-incoming.md#pg-015-ai-data-performance-ui)附录；PG-006/011/013进一步补齐[阻焊字符](processes/PG-006_soldermask-legend.md#pg-006-ai-data-performance-ui)、[终检双面](processes/PG-011_final-avi.md#pg-011-ai-data-performance-ui)和[钢网](processes/PG-013_stencil.md#pg-013-ai-data-performance-ui)准入附录。

除PG-002/003/006/011/013原有专属段外，PG-001/004/005/007/008/009/010/012/014/015/016/017/018/019/020/021/022/023现已补充各自快速编程段，分别说明制造资料、金板/样图、旧程序差异、人工确认、覆盖试检和原程序发布边界；当前23份PG均有方法、数据、性能、页面、组合故障和准入附录。这表示设计语义已落入原PG，不表示契约、代码、WPF或生产资格已完成。

本轮新增方案未覆盖到正式FS的功能，仍需沿[端到端链路§8.2](END-TO-END-FLOWS.md#82-指导到可编码切片的顺序)逐项绑定FunctionSpec、Contract/Schema、Owner、PageContract、输入样本和PerformanceProfile。无需为每台机台复制共用库或另起一套主模型；公共细化见[共享模块目录](../shared-modules/README.md)。


点胶与涂覆分别使用[UI-PCS-022](guidance/14-page-contracts/UI-PCS-022_Dispense_Workbench.md)和[UI-PCS-023](guidance/14-page-contracts/UI-PCS-023_Coating_Workbench.md)。[双工艺交互样例](prototypes/UI-PCS-022-023_dispense-coating.html)已完成定向浏览器检查，具体范围见UI-PCS-022/023 §8；生产证据、工程草稿和新增未提交输入分别呈现。两页保持DesignReview，正式端口、完整功能和真实WPF/算法验证仍未完成。

插件/压接用[UI-PCS-024](guidance/14-page-contracts/UI-PCS-024_Insertion_Workbench.md)，波峰/选择焊后用[UI-PCS-025](guidance/14-page-contracts/UI-PCS-025_THT_Solder_Workbench.md)。[双模式交互样例](prototypes/UI-PCS-024-025_pin-tht.html)可查看镜像/缺针/未知、针端与锡峰、禁连和草稿取消等行为；检查证据统一在UI-PCS-024§8。专属规则留在各PG，共用几何只见IM-036 §19.4；HTML不证明真实WPF/算法效果。

灌封与最终装配用[UI-PCS-026](guidance/14-page-contracts/UI-PCS-026_Final_Assembly_Workbench.md)，覆盖成品/板件关联、灌封表面、装配清单、标签/外形、必检与外部记录边界。工艺唯一依据为[PG-022](processes/PG-022_final-assembly.md)，专属布局、操作和异常时间线已形成DesignReview；原型、正式端口、真实WPF与产品验收仍需完成。
