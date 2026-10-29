# 平台公共独立模块

**历史公共交付包目录：[62个PKG与6类工具宿主](MODULE-CATALOG.md)。** 当前完全独立模块的架构权威是[52项候选及准入审查](../independent-modules/INDEPENDENT-MODULE-ARCHITECTURE.md)，其逐项指导位于 `docs/independent-modules/`。下列28SM维持责任归属；USER-002的19项表仅作来源追踪，不再代表模块规划全集。

这里维护跨制程可复用能力，制程专用目标、缺陷语义、判定与页面组合见[制程指导](../process-guides/README.md)。已确认复用功能必须独立模块/控件模块交付。独立意味着可引用、构建、测试、发布和集成；允许稳定契约依赖，不要求独立进程。

本目录28项是设计能力边界，不是已存在的28个DLL，不要求一次全部实施。`modules/`定义职责和接入，`guidance/`保留原DEV、FS、PageContract详细指导和ID。依赖列是无环的设计先决能力，运行调用通过宿主装配。各SM自0.3.0基线起持续细化，具体版本见各页，包含独立发布与逐操作接入；各页均为DesignReview；具体接口/阈值未批准时不得据此实现生产权威。

| 模块 | 能力 | 层 | 规划消费者 | 先决能力 |
|---|---|---|---|---|
| [SM-001](<modules/SM-001_composition.md>) | 模块装配与生命周期 | 通用软件 | 所有机台宿主；离线编程；独立模块演示宿主 | — |
| [SM-002](<modules/SM-002_configuration.md>) | 配置参数与版本快照；[唯一实施指导 IM-002](../independent-modules/configuration/DEVELOPMENT-GUIDE.md) | 通用软件 | SPI 参数；AOI 参数；独立控件宿主 | SM-001 |
| [SM-003](<modules/SM-003_localization.md>) | 本地化与术语 | 通用软件 | 全部机台 UI；ROI/激光嵌入宿主；报表 | SM-001 |
| [SM-004](<modules/SM-004_authorization.md>) | 权限决策与操作审计接入 | 通用软件 | 程序发布；复判；设备诊断；管理入口 | SM-001 |
| [SM-005](<modules/SM-005_diagnostics.md>) | 日志诊断与健康信息 | 通用软件 | 所有模块；维护工作站；远程支持包 | SM-001 |
| [SM-006](<modules/SM-006_frames.md>) | 图像高度场与数据租约 | 通用视觉 | SPI；2D/3D AOI；激光计量；离线回放 | SM-001 |
| [SM-007](<modules/SM-007_acquisition.md>) | 设备采集端口与模拟输入 | 通用视觉 | SPI；AOI；PCB 外观/孔检测；激光计量 | SM-001, SM-002, SM-005, SM-006 |
| [SM-008](<modules/SM-008_coordinates.md>) | 坐标单位与变换 | 通用视觉 | 制造数据；SPI；AOI；钻孔/尺寸；卷料 | SM-001 |
| [SM-009](<modules/SM-009_calibration.md>) | 标定资产与有效性管理 | 通用视觉 | SPI高度量测；AOI定位；尺寸/激光计量 | SM-002, SM-008 |
| [SM-010](<modules/SM-010_roi-measurement.md>) | ROI与2D/3D测量工作台接入 | 通用视觉 | SPI编程；AOI编程；PCB/激光尺寸测量 | SM-003, SM-006, SM-008, SM-009 |
| [SM-011](<modules/SM-011_vision-features.md>) | 通用视觉特征与算法执行 | 通用视觉 | AOI存在/定位/OCR；PCB表面/孔；钢网；SPI分割 | SM-002, SM-006, SM-008 |
| [SM-012](<modules/SM-012_surface.md>) | 高度场点云处理与几何质量 | 通用视觉 | SPI；3D AOI；填孔/翘曲/胶路检测 | SM-006, SM-008, SM-009 |
| [SM-013](<modules/SM-013_coverage.md>) | FOV覆盖与采集计划 | PCB/PCBA共享 | AOI；SPI；PCB孔/外观；尺寸计量 | SM-006, SM-008, SM-009 |
| [SM-014](<modules/SM-014_manufacturing-input.md>) | 制造设计数据接入 | PCB/PCBA共享 | SPI焊盘；AOI元件；钢网；PCB孔/轮廓 | SM-002, SM-008 |
| [SM-015](<modules/SM-015_reference-library.md>) | 标准件、元件与算法资产库 | PCB/PCBA共享 | AOI封装；SPI焊盘模板；钢网孔型；各制程模型 | SM-002, SM-008, SM-014 |
| [SM-016](<modules/SM-016_program-package.md>) | 检测程序与配方版本包 | PCB/PCBA共享 | SPI编程；AOI编程；孔/外观/胶路机台 | SM-002, SM-004, SM-014, SM-015 |
| [SM-017](<modules/SM-017_identity.md>) | 板、拼板与检测尝试身份 | PCB/PCBA共享 | SPI；AOI；PCB终检；跨制程质量工作站 | SM-002 |
| [SM-018](<modules/SM-018_execution.md>) | 检测任务执行与调度 | 通用视觉 | SPI量测链；AOI特征链；PCB孔/表面链；离线回放 | SM-001, SM-002, SM-005, SM-006 |
| [SM-019](<modules/SM-019_evaluation.md>) | 测量比较与规则执行 | 通用视觉 | SPI阈值；AOI缺陷；尺寸公差；涂覆覆盖 | SM-002 |
| [SM-020](<modules/SM-020_result-evidence.md>) | 结果与证据持久化 | PCB/PCBA共享 | 所有机台结果提交；独立复判；质量追溯 | SM-002, SM-005, SM-017 |
| [SM-021](<modules/SM-021_replay.md>) | 证据回放与结果比较 | 通用视觉 | SPI算法验证；AOI离线调试；质量问题追溯 | SM-006, SM-016, SM-018, SM-020 |
| [SM-022](<modules/SM-022_review.md>) | 复判与返修任务基础 | PCB/PCBA共享 | AOI复判；SPI异常复核；PCB终检复判 | SM-004, SM-017, SM-020 |
| [SM-023](<modules/SM-023_quality.md>) | 统计、质量关联与报表投影 | PCB/PCBA共享 | SPI SPC；AOI良率；PCB尺寸趋势；跨工序追溯 | SM-017, SM-020 |
| [SM-024](<modules/SM-024_integration.md>) | 外部通信与可靠交付 | 通用软件 | MES上传；线体交接；SPI打印机反馈；质量系统 | SM-002, SM-004, SM-005 |
| [SM-025](<modules/SM-025_presentation.md>) | 公共显示控件与任务投影 | 通用软件 | SPI/AOI生产页；编程；复判；PCB测量页 | SM-003, SM-006, SM-008 |
| [SM-026](<modules/SM-026_ai-assistance.md>) | AI候选与辅助建议 | 通用视觉 | AOI辅助复判；SPI异常解释；编程候选 | SM-002, SM-006, SM-016, SM-020, SM-021 |
| [SM-027](<modules/SM-027_qualification.md>) | 计量与验证分析工具 | 通用视觉 | SPI量测验证；AOI高度验证；PCB尺寸计量 | SM-008, SM-020 |
| [SM-028](<modules/SM-028_delivery.md>) | 版本装配、升级与现场恢复 | 通用软件 | 所有机台；离线编程；复判/质量工作站 | SM-001, SM-002, SM-004, SM-005 |

共享文档中引用SPI/AOI等制程文档，表示真实消费案例，不能导致共享程序集引用制程实现。原跨制程复判/制造接入来源尚在制程详细指导中，由本目录公共边界限制可抽取部分。

- [交接、资源和事实Owner映射](INTERFACE-MAP.md)
- [平台架构](../00-baseline/PLATFORM-DESIGN-BASELINE.md)
- [原文档ID与当前位置](../09-development-plan/DEV-PLAN-000_开发指导文档地图.md)

## 2026-09-27 跨工序复用细化

SM-006、008–015、018–020、023、025、027–028新增§7，落实未开发机台的真实消费者、输入物理含义、测量/区域/表面/覆盖语义、资源、证据、独立宿主验收和客户交付后迁移路线。原28个模块职责保持稳定，没有按机台另建重复公共库。

重点复用链：钻孔/钢网共享几何量测；阻焊/胶路/焊料共享区域与拓扑候选；填孔/翘曲/点胶/插针共享有效表面和参考面候选；各工序共享分功能覆盖、规则执行、证据和只读显示。工艺目标、被测量选择、材料/针型语义和质量阈值仍在[PG指导](../process-guides/README.md)。精确接口未批准部分保持DesignReview，细项见[接口交接§6](INTERFACE-MAP.md#6-未开发机台研究落实后的契约绑定重点)。


## 文字能力独立子包

[DEV-VIS-021A](guidance/03-vision/DEV-VIS-021A_OCR与DeepOCR独立能力开发指导.md)细化SM-011文字能力及可选WPF控件，面向PCB字符、元件标记和来料/终装复用；HALCON Deep OCR明确纳入优先路线，PaddleOCR为固定源码研究候选。职责、生命周期、模型、快速编程、错误接受/拒识、性能和并行边界集中在该页，不新增第二份OCR实现指导。


截面、有效插值、法向高度和积分的唯一实施语义见[IM-036 §19.4–19.5](../independent-modules/metrology/DEVELOPMENT-GUIDE.md#194-连续截面沿程轴与有限层面计算c1)，由SM-010/012/013按原职责协作，SM-025/既有独立控件承载可复用投影。DEV-MET-031仅作导航。点胶/涂覆的业务定义与专属页面保留在制程目录，不建立第二套测量核心。

轴/端点/基准截面与关系量测统一在[IM-036 §19.4](../independent-modules/metrology/DEVELOPMENT-GUIDE.md#194-连续截面沿程轴与有限层面计算c1)。SM-008/010/011/012/013/025支持插针与焊后两个消费者；针型、针号、是否允许连焊及质量判定仍归各PG，不建立通用针/焊点业务对象。

<a id="user-002-modules"></a>
## USER-002：19条用户输入的历史对应（不是模块全集）

用户原文：[USER-002](../references/user-notes/USER-002_独立模块与功能想法_2026-09-27.txt)，与`../references/user-notes/USER-002_独立模块与功能想法_2026-09-27.txt`字节一致。以下是能力/发布单元细化，沿原28个SM归属，不新增第二套平台或强制19个进程。每项都采用无UI核心与可选参数/结果控件；正式公共类型、字段/事件和副作用在原Owner采纳后实现。

| 原序号 | 用户想法 | 独立能力归属候选 | 对应开发指导 | 补充建议 |
|---|---|---|---|---|
| 1 | 一维码与质量 | SM-011 · Barcode1D | [DEV-VIS-021B](<guidance/03-vision/DEV-VIS-021B_条码解码与印制质量独立能力开发指导.md>) | 解码、质量标准/分项、内容核对分别输出 |
| 2 | 二维码与质量 | SM-011 · Code2D | [DEV-VIS-021B](<guidance/03-vision/DEV-VIS-021B_条码解码与印制质量独立能力开发指导.md>) | 全部支持码制作为覆盖目标；评级范围按实际能力 |
| 3 | 模板匹配/大图定位 | SM-011 · Matching | [DEV-VIS-023](<guidance/03-vision/DEV-VIS-023_定位、注册与Alignment开发指导.md#sparse-marks-large-images>) | 局部Mark＋整体位姿；形状/NCC/变形分任务比较 |
| 4 | 光源全量控制 | SM-007 · Lighting | [DEV-PLT-015](<guidance/02-platform/DEV-PLT-015_设备、相机、光源、运动与采集开发指导.md#device-capabilities>) | 设备能力目录、通道/时序/回读及模拟 |
| 5 | 相机全量控制 | SM-007 · Camera | [DEV-PLT-015](<guidance/02-platform/DEV-PLT-015_设备、相机、光源、运动与采集开发指导.md#device-capabilities>) | 设置/实际生效/曝光/帧到达分开 |
| 6 | 文字识别与检测 | SM-011 · Text | [DEV-VIS-021A](<guidance/03-vision/DEV-VIS-021A_OCR与DeepOCR独立能力开发指导.md>) | 传统/Deep OCR优先、Paddle对照，原读不被期待值改写 |
| 7 | 畸变矫正 | SM-009 · Rectification | [DEV-MET-030](<guidance/04-metrology/DEV-MET-030_Calibration与标定资格开发指导.md#distortion-module>) | 标定资产、校正执行、坐标/有效域与可选UI |
| 8 | 运动控制 | SM-007 · Motion | [DEV-PLT-015](<guidance/02-platform/DEV-PLT-015_设备、相机、光源、运动与采集开发指导.md#device-capabilities>) | 独立轴能力与安全/实际到位边界，不把取消当急停 |
| 9 | 高速大图拼接 | SM-013/008 · Mosaic | [DEV-VIS-029](<guidance/03-vision/DEV-VIS-029_多FOV拼接与全局坐标开发指导.md#fast-mosaic>) | 注册/来源/虚拟瓦片与显示融合分开 |
| 10 | SPC图表/报告 | SM-023 · Statistics/Reporting | [DEV-DOM-058A](<guidance/06-domains/DEV-DOM-058A_QualityControl SPC与分母定义开发指导.md#spc-core>) | 统计核心、可选图表/导出；Ca定义、Cp/Cpk与Pp/Ppk分清 |
| 11 | 万能查询 | SM-020公开查询投影 · Query | [DEV-PLT-018](<guidance/02-platform/DEV-PLT-018_数据、报告、归档与数据主权开发指导.md#query-storage>) | 类型化目录/权限/游标/水位/受控导出，非任意SQL |
| 12 | Variation印刷检测 | SM-011 · VariationInspection | [DEV-VIS-026](<guidance/03-vision/DEV-VIS-026_2D分割、Blob与缺陷候选开发指导.md#blob-variation>) | 良品变化模型与可变形匹配独立；防训练污染/过度配准 |
| 13 | 图像通道处理 | SM-011 · ImageProcessing | [DEV-VIS-021C](<guidance/03-vision/DEV-VIS-021C_图像通道与预处理独立能力开发指导.md>) | 通道身份/类型/范围、数值/有效域及版本化预处理 |
| 14 | 2D/3D测量 | SM-010/012 · 既有控件桥 | [SM-010](<modules/SM-010_roi-measurement.md>) | 复用公开能力，核对无UI入口，不改内部或另写一套 |
| 15 | 2D/3D图像窗口 | SM-025 · Viewport | [SM-025](<modules/SM-025_presentation.md>) | 显示/交互与算法分离，原图/LOD/ROI草稿/租约 |
| 16 | Blob与参数调节 | SM-011 · Segmentation | [DEV-VIS-026](<guidance/03-vision/DEV-VIS-026_2D分割、Blob与缺陷候选开发指导.md#blob-variation>) | 固定/自动/局部阈值比较，原域/过滤/标签/边界可追溯 |
| 17 | 数据库全量操作 | `IM-066 storage-database` 技术模块；SM-020等领域Owner为业务消费者 | [DEV-PLT-018](<guidance/02-platform/DEV-PLT-018_数据、报告、归档与数据主权开发指导.md#query-storage>) | PostgreSQL优先验证候选；事务/恢复/只读查询与Owner分权 |
| 18 | MES独立平台 | SM-024 · Integration＋独立Host | [DEV-PLT-013](<guidance/02-platform/DEV-PLT-013_跨模块事件与外部互联开发指导.md#mes-hub>) | 互联中心/客户适配/可靠交付，不自动扩成完整MES产品 |
| 19 | 人工复判软件 | SM-022＋独立ReviewHost | [SM-022](<modules/SM-022_review.md>) | 独立可部署应用与嵌入控件共用核心，机判/人工分开 |

共同交付要求见DEV-GOV-005§6：全部业务操作能无UI调用；参数同源校验、冻结执行快照、版本化能力/输入输出、回调线程/排序/异常/退订、资源/取消/关闭与两个宿主验收。发布目录与先后关系见DEV-PLAN-006/014的新子能力节；新包名为候选，不代表已批准工程/API。

建议补充的共用能力不另起同义模块：参数/配置版本SM-002、语言SM-003、权限SM-004、诊断SM-005、帧租约SM-006、坐标/标定SM-008/009、模型/参考资产SM-015、执行/预算SM-018、规则SM-019、证据/回放SM-020/021、资格SM-027与升级迁移SM-028。每个算法模块复用它们的公开能力，不各自内建模型库、日志、权限和数据表。

本轮是专项细化和来源研究，不是宣告19项均可直接生产编码。全码制能力清单/具体公共签名、硬件厂商参数、客户MES、数据库部署、实际数值和所有UI页面仍按受影响切片冻结；主动研究不能以“等用户给库名”为前置。

