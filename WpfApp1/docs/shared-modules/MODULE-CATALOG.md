# 独立交付模块总体设计与功能清单

- 文档 ID：`PLATFORM-PACKAGES-001`；版本：`0.5.1-prep`；日期：2026-09-28；状态：`DesignReview`
- 消费者：平台架构、每个模块的实现Owner、多会话调度和产品装配。

## 1. 本次独立推导的结果

本表保留历史 PKG 迁移目录：原规划为 **62个公共交付包、6类工具宿主**。它是旧责任和文档的迁移索引，不是当前最终的完全独立模块数量，也不等于62个 EXE 或 DLL。当前重新按独立职责、公开契约、生命周期和第二消费者筛选出的架构候选为 **52项**，唯一权威见[独立模块架构审查与候选清单](../independent-modules/INDEPENDENT-MODULE-ARCHITECTURE.md)。后续真实接口或消费者证据要求拆合时，先修订该架构文件，再同步本表及对应指导。

用户的19条想法是输入来源，不是模块全集。此前28份SM是能力与责任分组，也不是28个固定DLL。PKG页把历史交付职责具体化，继承SM的事实Owner，不产生第二套Contract/Schema/状态机。组合根、制程目标解释、任务编排、规则放行、复判闭环和跨工序关联等 PKG 保留在调用应用层；它们可以调用独立模块，但不能反向定义独立模块边界。

| 类别 | 编号 | 个数 | 拆分依据 |
|---|---|---:|---|
| 基础软件、帧与坐标 | 001–007 | 7 | 配置、语言、权限、诊断、资源、几何各自生命周期与消费者不同 |
| 相机/光源/运动/投影/序列 | 008–012 | 5 | 单设备独立使用，序列负责实际时序与帧关联；厂商SDK仍暂缓 |
| 成像质量、校正、拼接与覆盖规划 | 013–019 | 7 | 质量、像素处理、标定资产、重采样、拼图、完整性与路径不是同一状态Owner |
| ROI与2D识别 | 020–026 | 7 | 几何编辑、特征、定位、读码、OCR、分割和变化模型可分别消费 |
| 3D数据、重建、参考、量测与配准 | 027–031、060 | 6 | 数据、重建、基准、被测量、单表面特征与双/多表面位姿分开；复用既有测量资产 |
| 制造资料、库与编程 | 032–036 | 5 | 制造快照、模型字节资产、参考业务库、程序发布和编程建议分权 |
| 运行、结果与数据服务 | 037–043 | 7 | 身份、调度、规则、事实提交、技术存储、查询、实验回放互不代权 |
| 复判、质量、报告与互联 | 044–048 | 5 | 人工意见、统计、渲染、消息交付、跨工序关系分别可部署/复用 |
| 视觉UI与通用编辑 | 049–051 | 3 | 影像交互、设计系统和参数编辑独立，业务逻辑留核心 |
| AI、资格与交付 | 052–056 | 5 | 推理、治理、助手、资格和升级各有独立资源/权限/失败边界 |
| 成像试验与优化 | 061 | 1 | 跨多次成像设置搜索/独立验证，快编和独立试验台共同消费；不混入单帧质量或设备执行 |
| 纯图分配与歧义证明 | 062 | 1 | 钻孔/微孔共享同一无UI求解，不携带图像、实体身份或工艺判据 |
| 复核补齐的传感、信号与报警 | 057–059 | 3 | 轮廓位置/批次、离散/模拟信号、报警处理各有明确消费者与独立生命周期 |

合并选择也有依据：一维/二维码共享读码及质量能力契约，1D/2D后端与UI面板可选装配，不为每种码制建顶层模块；二维/三维量测复用一个类型化关系引擎和现有控件，按输入能力选适配；统计与报表拆开，数据库与业务事实提交拆开；“万能查询”不取得任意表写权；MES互联与完整MES产品分开。

## 2. 每个模块的功能与开发指导

下面每行保留历史 PKG 的职责导航。属于当前独立模块的能力，其公开契约、代码工程、测试和准入只由对应 `docs/independent-modules/<key>/DEVELOPMENT-GUIDE.md` 定义；PKG 和 SM 仅承担产品接入或迁移映射。正式创建前按该唯一指导定位工程，不从历史候选目录创建第二套同义实现。Core、必要公开契约、可选 Adapter/WPF 与测试按职责拆工程，不机械创建空项目。

> **迁移目录说明（2026-10-04）：** 下表仍保留62个历史 PKG，便于旧文档、Owner 和依赖迁移。`PKG-001/012/018/019/032/034/035/036/037/038/039/044/048/054` 以及各 PG 的领域应用语义不属于当前52项完全独立候选；它们由调用应用/宿主组合，不能据本表的“指导”列新建同名独立模块。当前完全独立目录和唯一指导以 [`docs/independent-modules`](../independent-modules/) 及其架构审查为准。

| 模块 | 功能范围 | 原责任分组 | 真实规划消费者 | 指导 |
|---|---|---|---|---|
| PKG-001 应用装配与模块宿主 | 模块发现与显式装配；依赖检查；启停排序；健康汇总；退出排空 | [SM-001](<modules/SM-001_composition.md>) | 机台主程序、独立复判站 | [开发指导](<packages/PKG-001_Composition.md>) |
| PKG-002 / IM-002 配置参数与版本快照 | 显式定义；类型单位校验；规范摘要/差异；CAS保存；迁移；原操作查询与历史 | [SM-002](<modules/SM-002_configuration.md>) | 设备参数工具、离线算法工具、生产宿主 | [接入映射](<packages/PKG-002_Configuration.md>)；[唯一实施指导](../independent-modules/configuration/DEVELOPMENT-GUIDE.md) |
| PKG-003 / IM-003 语言资源与专业术语 | 语言包加载；资源键解析；格式化；语言切换通知；缺词诊断 | [SM-003](<modules/SM-003_localization.md>) | 所有模块控件、报告与诊断查看 | [接入映射](<packages/PKG-003_Localization.md>)；[唯一实施指导](../independent-modules/localization/DEVELOPMENT-GUIDE.md) |
| PKG-004 / IM-004 身份上下文与动作授权 | 显式身份/用途；动作/对象范围授权；权限变化；二人复核；审计恢复 | [SM-004](<modules/SM-004_authorization.md>) | 程序发布、复判提交、导出及设备调试 | [接入映射](<packages/PKG-004_Authorization.md>)；[唯一实施指导](../independent-modules/authorization/DEVELOPMENT-GUIDE.md) |
| PKG-005 日志指标与诊断关联 | 结构化日志；指标；trace关联；错误映射；受控查询/导出；容量管理 | [SM-005](<modules/SM-005_diagnostics.md>) | 全部能力包、维护工具与长稳测试 | [IM-005指导](../independent-modules/diagnostics/DEVELOPMENT-GUIDE.md) · [接入映射](<packages/PKG-005_Diagnostics.md>) |
| PKG-006 图像帧与大数据资源 | 帧描述；租约借还；tile读取；布局校验；缓存；域与来源携带 | [SM-006](<modules/SM-006_frames.md>) | 相机采集、拼接、算法、Viewport | [IM-006指导](../independent-modules/image-frame/DEVELOPMENT-GUIDE.md) · [接入映射](<packages/PKG-006_Frames.md>) |
| PKG-007 坐标变换与有量纲几何 | 坐标系登记；变换组合/求逆；单位换算；方向与面别；误差传播 | [SM-008](<modules/SM-008_coordinates.md>) | 定位、ROI、计量、CAM与覆盖 | [IM-007指导](../independent-modules/coordinate-geometry/DEVELOPMENT-GUIDE.md) · [接入映射](<packages/PKG-007_Coordinates.md>) |
| PKG-008 相机能力与采集控制 | 发现连接；能力查询；曝光增益/格式ROI；触发；采集缓冲；断开恢复 | [SM-007](<modules/SM-007_acquisition.md>) | AOI采集、独立相机调试 | [应用映射](<packages/PKG-008_Camera.md>)；[唯一指导](../independent-modules/camera-acquisition/DEVELOPMENT-GUIDE.md) |
| PKG-009 光源能力与照明序列 | 通道分组；电流/亮度/脉宽；预设；触发；状态/故障；受控关闭 | [SM-007](<modules/SM-007_acquisition.md>) | 相机序列、设备工具、不同制程多光检测 | [应用映射](<packages/PKG-009_Lighting.md>)；[唯一指导](../independent-modules/lighting-control/DEVELOPMENT-GUIDE.md) |
| PKG-010 运动能力与位置反馈 | 轴配置；回零；定位/插补；比较触发；反馈；停止/复位 | [SM-007](<modules/SM-007_acquisition.md>) | 采集规划、维护点动、不同机台位置控制 | [应用映射](<packages/PKG-010_Motion.md>)；[唯一指导](../independent-modules/motion-control/DEVELOPMENT-GUIDE.md) |
| PKG-011 结构光投影能力 | 图案生成/装载、内容/步序校验、受控投影、实际回执、黑场与恢复；解码/重建归 IM-032 | [SM-007](<modules/SM-007_acquisition.md>) | 3D AOI、SPI结构光与离线序列验证 | [IM-011 唯一指导](../independent-modules/structured-light/DEVELOPMENT-GUIDE.md)；[应用映射](packages/PKG-011_Projection.md) |
| PKG-012 多设备采集编排与帧集 | 采集计划执行；资源占用；触发关联；帧集封口；缺帧诊断；取消恢复 | [SM-007](<modules/SM-007_acquisition.md>) | AOI多光/多方向、钢网/PCB扫描 | [开发指导](<packages/PKG-012_Acquisition.md>) |
| PKG-013 / IM-020 成像质量与可观察性 | 饱和/欠曝；模糊；对比；遮挡/有效域；质量适用域；质量报告 | [SM-011](<modules/SM-011_vision-features.md>) | OCR/读码、2D检测、3D重建前置 | [映射页](<packages/PKG-013_ImageQuality.md>) / [唯一实施指导](../independent-modules/image-quality/DEVELOPMENT-GUIDE.md) |
| PKG-014 通道运算与预处理 | 通道选择；加减乘除；颜色变换；平场；滤波；有界运算图 | [SM-011](<modules/SM-011_vision-features.md>) | Blob/OCR、外观与快速编程 | [IM-021指导](../independent-modules/image-preprocessing/DEVELOPMENT-GUIDE.md) · [接入映射](<packages/PKG-014_ImageProcessing.md>) |
| PKG-015 标定资产与资格管理 | 标定采样；求解；残差评估；适用域；资产保存；失效/复验 | [SM-009](<modules/SM-009_calibration.md>) | 相机校正、3D重建、计量工具 | [唯一模块指导](../independent-modules/calibration-assets/DEVELOPMENT-GUIDE.md) / [应用映射](packages/PKG-015_Calibration.md) |
| PKG-016 图像畸变校正 | 映射生成/缓存；输入布局验证；重采样；有效域传播；点校正 | [SM-009](<modules/SM-009_calibration.md>) | OCR/几何定位、拼接与计量 | [IM-022指导](../independent-modules/image-rectification/DEVELOPMENT-GUIDE.md) · [接入映射](<packages/PKG-016_Rectification.md>) |
| PKG-017 多FOV注册与大图拼接 | 相对注册；全局变换；tile目录；来源反查；接缝检测；显示融合 | [SM-013](<modules/SM-013_coverage.md>) | PCB大板、钢网、AOI整板查看 | [唯一模块指导](../independent-modules/mosaic/DEVELOPMENT-GUIDE.md) / [应用映射](packages/PKG-017_Mosaic.md) |
| PKG-018 目标覆盖与完成性 | 目标域登记；所需模态/视角；计划覆盖；实际覆盖；缺口与重复归并 | [SM-013](<modules/SM-013_coverage.md>) | 所有制程的必检完整性、采集规划 | [开发指导](<packages/PKG-018_Coverage.md>) |
| PKG-019 FOV与扫描路径规划 | FOV候选；覆盖优化；路径排序；可达性；时间/资源估算；计划修订 | [SM-013](<modules/SM-013_coverage.md>) | PCB/钢网扫描、AOI多视角采集 | [开发指导](<packages/PKG-019_ScanPlanning.md>) |
| PKG-020 ROI几何与编辑事务 | IM-024维护几何、原子编辑、命中、序列化及可选控件；宿主持有Target/配方/提交 | [SM-010](<modules/SM-010_roi-measurement.md>) | 算法参数页、计量、程序编辑 | [唯一指导](../independent-modules/roi-geometry/DEVELOPMENT-GUIDE.md)；[接入映射](<packages/PKG-020_RoiGeometry.md>) |
| PKG-021 二维边缘轮廓与基础特征 | 边缘/轮廓提取；极性筛选；特征关联；线/圆候选；支撑/残差 | [SM-011](<modules/SM-011_vision-features.md>) | 孔/开口、引脚和元件定位 | [应用映射](packages/PKG-021_Features2D.md)、[IM-025唯一指导](../independent-modules/features-2d/DEVELOPMENT-GUIDE.md) |
| PKG-022 Mark与模板定位 | 模型创建/装载；shape/NCC/变形路线；局部Mark；多点位姿；有限备用 | [SM-011](<modules/SM-011_vision-features.md>) | PCB/钢网全局定位、元件局部定位 | [IM-026指导](../independent-modules/alignment-2d/DEVELOPMENT-GUIDE.md) · [接入映射](<packages/PKG-022_Matching.md>) |
| PKG-023 一维二维码解码与质量 | 1D/2D解码；有限训练；原字节；歧义；适用标准质量；诊断 | [SM-011](<modules/SM-011_vision-features.md>) | 来料标签、板码与终装标识 | [应用映射](packages/PKG-023_CodeReading.md) / [IM-027唯一指导](../independent-modules/barcode/DEVELOPMENT-GUIDE.md) |
| PKG-024 OCR文字检测识别与OCV | 文本检测；行序；传统/Deep OCR；原读；字形比较；有界推荐 | [SM-011](<modules/SM-011_vision-features.md>) | 元件丝印、PCB字符、终装标签 | [应用映射](packages/PKG-024_TextRecognition.md) / [IM-028唯一指导](../independent-modules/ocr/DEVELOPMENT-GUIDE.md) |
| PKG-025 / IM-029 Blob分割与区域特征 | 固定/自动/局部阈值；三态/支撑；原派生形态；跨tile连通；特征与类型化筛选 | [SM-011](<modules/SM-011_vision-features.md>) | 首批阻焊/涂覆；后续锡膏/胶体、污染与表面缺陷 | [映射页](packages/PKG-025_Segmentation.md) / [唯一实施指导](../independent-modules/segmentation/DEVELOPMENT-GUIDE.md) |
| PKG-026 / IM-030 良品变化模型与印刷差异 | Standard/Robust/Direct；阈值/亮暗槽；评价/有界建议；模型包/生命周期 | [SM-011](<modules/SM-011_vision-features.md>) | PCB丝印、标签与稳定纹理检查 | [映射页](packages/PKG-026_VariationInspection.md) / [唯一实施指导](../independent-modules/variation-inspection/DEVELOPMENT-GUIDE.md) |
| PKG-027 高度场点云与表面数据 | 网格/点云描述；有效性/不确定度；坐标映射；拓扑检查；有界访问 | [SM-012](<modules/SM-012_surface.md>) | 3D计量、重建、Viewport | [应用映射](<packages/PKG-027_SurfaceData.md>)；[IM-031唯一指导](<../independent-modules/surface-data/DEVELOPMENT-GUIDE.md>) |
| PKG-028 三维重建与多方向融合 | 输入序列校验；结构光/适用重建；方向质量；融合；冲突/无效域 | [SM-012](<modules/SM-012_surface.md>) | 3D AOI、SPI与离线高度实验 | [应用映射](<packages/PKG-028_Reconstruction.md>)；[IM-032唯一指导](<../independent-modules/reconstruction-3d/DEVELOPMENT-GUIDE.md>) |
| PKG-029 局部基准面与板弯补偿 | 基准域；P/H/Q；独立检查；支撑/预测域；重开 | [SM-012](modules/SM-012_surface.md) | 焊点/引脚高度、胶体/SPI体积 | [应用映射](packages/PKG-029_ReferenceSurface.md) / [IM-035唯一指导](../independent-modules/reference-surface/DEVELOPMENT-GUIDE.md) |
| PKG-030 通用二维三维量测 | 距离/角度/尺寸；高度；面积/矩/体积；截面；支持域数值归约 | [SM-010](modules/SM-010_roi-measurement.md) | PCB孔/钢网、AOI引脚、胶体和SPI | [应用映射](packages/PKG-030_Metrology.md) / [IM-036唯一指导](../independent-modules/metrology/DEVELOPMENT-GUIDE.md) |
| PKG-031 三维几何特征与拓扑处理 | 单表面筛点/显式采样/法向；primitive；连通/拓扑/截面；距离属性 | [SM-012](<modules/SM-012_surface.md>) | 基准面、3D量测、连接器与表面候选 | [应用映射](packages/PKG-031_Features3D.md) / [IM-034唯一指导](../independent-modules/surface-features-3d/DEVELOPMENT-GUIDE.md) |
| PKG-032 制造资料归一与来源适配 | CAM/PnP/BOM结果接入；单位面别；稳定元素；层映射；差异/校验 | [SM-014](<modules/SM-014_manufacturing-input.md>) | PCB目标生成、AOI PnP与钢网 | [开发指导](<packages/PKG-032_ManufacturingInput.md>) |
| PKG-033 模型模板资产版本与解析 | 不可变存取；版本/hash；依赖解析；运行租约；资格引用；回收 | [SM-015](<modules/SM-015_reference-library.md>) | 模板/OCR、AI模型、标定资产 | [应用映射](<packages/PKG-033_ModelAssets.md>) / [IM-014唯一指导](../independent-modules/model-assets/DEVELOPMENT-GUIDE.md) |
| PKG-034 元件封装与检测参考库 | 类型/封装；几何/方向规则；供应商变体；检索匹配；候选复用；版本发布 | [SM-015](<modules/SM-015_reference-library.md>) | AOI快速编程、钢网/PCB参考管理 | [开发指导](<packages/PKG-034_ReferenceLibrary.md>) |
| PKG-035 程序配方与发布快照 | 草稿；差异/CAS；资产闭包；验证；发布；激活请求；历史读取 | [SM-016](<modules/SM-016_program-package.md>) | 所有机台运行、离线编程站 | [开发指导](<packages/PKG-035_ProgramPackage.md>) |
| PKG-036 快速编程编排与建议差异 | 资料对账；生成器调用；候选ROI/参数；库复用；差异传播；试检/回退 | [SM-026](<modules/SM-026_ai-assistance.md>) | PCB/钢网编程、AOI/胶路专用生成器 | [开发指导](<packages/PKG-036_QuickProgramming.md>) |
| PKG-037 板件子板面别与尝试身份 | 原始码关联；产品/批次；子板面别；尝试；复测关系；歧义 | [SM-017](<modules/SM-017_identity.md>) | 所有机台、复判与MES关联 | [开发指导](<packages/PKG-037_Identity.md>) |
| PKG-038 检测任务图与资源调度 | 类型化DAG；依赖传播；预算；并发背压；取消；排空；阶段状态 | [SM-018](<modules/SM-018_execution.md>) | 各制程检测、离线算法与Replay | [开发指导](<packages/PKG-038_Execution.md>) |
| PKG-039 规则计算与完整性聚合 | 有量纲比较；容差/边界；组合规则；缺项；解释；决定输入 | [SM-019](<modules/SM-019_evaluation.md>) | SPI/AOI判定、PCB尺寸与复判建议 | [开发指导](<packages/PKG-039_Evaluation.md>) |
| PKG-040 / IM-015 结果证据提交与历史追溯 | 纯校验/计划；证据保存/关系；事实提交与回执；定向读取/保持 | `IM-015`；[SM-020](<modules/SM-020_result-evidence.md>) 产品责任分组 | 生产提交、独立复判/Replay、质量报表 | [唯一开发指导](../independent-modules/inspection-evidence/DEVELOPMENT-GUIDE.md) / [产品接入映射](<packages/PKG-040_ResultEvidence.md>) |
| PKG-041 / IM-066 通用数据库与硬盘文件存储适配 | PostgreSQL/Npgsql连接与会话；事务；版本迁移；健康；硬盘文件对象；备份恢复适配；错误语义 | `IM-066` 技术 Owner；[SM-020](<modules/SM-020_result-evidence.md>) 等领域业务消费者 | 结果库元数据、配置/模型元数据、互联队列和硬盘证据文件 | [唯一开发指导](../independent-modules/storage-database/DEVELOPMENT-GUIDE.md) / [产品接入映射](<packages/PKG-041_Storage.md>) |
| PKG-042 / IM-045 受控数据查询与流式导出 | 版本目录/条件；固定源/授权；keyset/count/group；意图保存；有界硬盘发布 | [SM-020](<modules/SM-020_result-evidence.md>) | 复判检索、SPC数据、生产追溯 | [应用映射](packages/PKG-042_Query.md)；[唯一模块指导](../independent-modules/query/DEVELOPMENT-GUIDE.md) |
| PKG-043 历史重放与差异实验 | 历史闭包解析；相同版本重放；变更试验；结果对比；缺证据诊断 | [SM-021](<modules/SM-021_replay.md>) | 算法回归、客户问题复现、离线调参 | [唯一开发指导](../independent-modules/replay/DEVELOPMENT-GUIDE.md) / [产品接入映射](<packages/PKG-043_Replay.md>) |
| PKG-044 人工复判任务与意见 | IM-067通用事务/恢复/控件的产品接入；返修/处置留应用 | [SM-022](<modules/SM-022_review.md>) | 机旁复判、独立ReviewStation | [IM-067唯一实施](../independent-modules/human-review/DEVELOPMENT-GUIDE.md)、[应用映射](<packages/PKG-044_Review.md>) |
| PKG-045 SPC统计与过程监测 | IM-043 的产品接入映射；数值/分类、控制图与有限计量/具名配对共用无UI核心 | [SM-023](<modules/SM-023_quality.md>) | SPI/AOI质量、PCB尺寸分析、计量实验 | [唯一模块指导](../independent-modules/statistics/DEVELOPMENT-GUIDE.md)；[应用映射](packages/PKG-045_Statistics.md) |
| PKG-046 模板报表与输出渲染 | 模板版本；参数绑定；分页；多格式导出；预览；取消；输出审计 | [SM-023](<modules/SM-023_quality.md>) | SPC报告、机台检测报告与客户追溯 | [IM-044唯一指导](../independent-modules/reporting/DEVELOPMENT-GUIDE.md)；[产品接入映射](packages/PKG-046_Reporting.md) |
| PKG-047 MES及线体互联交付 | 端点/映射；鉴权；可靠队列；幂等；业务回执；死信/重投 | [SM-024](<modules/SM-024_integration.md>) | 多个机台、独立MES互联中心 | [IM-046唯一指导](../independent-modules/integration-transport/DEVELOPMENT-GUIDE.md)；[产品接入映射](<packages/PKG-047_FactoryIntegration.md>) |
| PKG-048 跨工序关联与质量追踪 | 实体/面别映射；空间关联；时序/尝试；迟到；差异；因果限制 | [SM-023](<modules/SM-023_quality.md>) | SPI与AOI关联、PCB制造与终检追踪 | [开发指导](<packages/PKG-048_ProcessCorrelation.md>) |
| PKG-049 二维三维影像与ROI交互控件 | 2D/3D呈现；pan/zoom；ROI交互；叠加；LOD；选择与来源导航 | [SM-025](<modules/SM-025_presentation.md>) | 独立测量工具、所有机台/复判页 | [IM-060唯一指导](../independent-modules/viewport/DEVELOPMENT-GUIDE.md)；[产品接入映射](packages/PKG-049_Viewport.md) |
| PKG-050 / IM-061 公共界面样式与语义控件 | 主题/Token；图标；状态投影；导航原语；提示；键盘/UIA；布局规则 | [SM-025](<modules/SM-025_presentation.md>) | 全部WPF页面、独立工具宿主 | [唯一模块指导](../independent-modules/design-system/DEVELOPMENT-GUIDE.md)；[应用映射](packages/PKG-050_DesignSystem.md) |
| PKG-051 通用参数编辑与试验面板 | 类型化编辑；单位/范围；依赖显示；草稿差异；试算；撤销/应用 | [SM-025](<modules/SM-025_presentation.md>) | 算法工具、设备参数、配方编辑 | [IM-062唯一指导](../independent-modules/parameter-editor/DEVELOPMENT-GUIDE.md)；[应用映射](packages/PKG-051_ParameterEditor.md) |
| PKG-052 受控AI推理执行 | 模型加载；预处理绑定；批次推理；资源预算；拒识；输出解释元数据 | [SM-026](<modules/SM-026_ai-assistance.md>) | 缺陷候选、OCR对照、工程辅助 | [唯一模块指导](../independent-modules/ai-inference/DEVELOPMENT-GUIDE.md) / [应用映射](packages/PKG-052_Inference.md) |
| PKG-053 AI数据集评估与模型治理 | 数据分组；标注版本；训练/评估记录；挑战集；上线阶段；漂移/回退 | [SM-026](<modules/SM-026_ai-assistance.md>) | 缺陷模型、OCR模型、辅助建议 | [IM-048唯一指导](../independent-modules/ai-dataset-governance/DEVELOPMENT-GUIDE.md)；[应用映射](packages/PKG-053_AiGovernance.md) |
| PKG-054 工程辅助建议与工具编排 | 问题上下文；证据检索；受限工具；建议；影响分析；人工采纳 | [SM-026](<modules/SM-026_ai-assistance.md>) | 工程调参、维护诊断、复判解释 | [开发指导](<packages/PKG-054_Assistant.md>) |
| PKG-055 算法计量与性能资格工具 | 实验设计；真值/标准件；重复性/GRR；性能；挑战集；证据归档 | [SM-027](<modules/SM-027_qualification.md>) | 各模块验收、机台FAT/SAT和同板对标 | [IM-049唯一指导](../independent-modules/qualification/DEVELOPMENT-GUIDE.md)；[应用映射](packages/PKG-055_Qualification.md) |
| PKG-056 部署更新与可恢复迁移 | 包组合；依赖完整性；配置/数据迁移；健康切换；失败回退；保留 | [SM-028](<modules/SM-028_delivery.md>) | 所有机台、独立工具和互联服务 | [IM-050唯一指导](../independent-modules/delivery-migration/DEVELOPMENT-GUIDE.md)；[应用映射](packages/PKG-056_Delivery.md) |
| PKG-057 激光轮廓与三维传感器采集 | 轮廓/批次；强度/编码器；多头；实际位置；缺线；完整表面接入 | [SM-007](<modules/SM-007_acquisition.md>) | 采用轮廓传感器的AOI/点胶、独立激光工具 | [IM-040指导](../independent-modules/profile-acquisition/DEVELOPMENT-GUIDE.md) · [接入映射](<packages/PKG-057_ProfileAcquisition.md>) |
| PKG-058 通用设备信号与I/O | DI/DO/AI/AO；计数/锁存能力；量纲/质量；受控输出；时序/恢复 | [SM-007](<modules/SM-007_acquisition.md>) | PCB/PCBA输入与触发观察、独立维护工具 | [IM-041指导](../independent-modules/device-signals/DEVELOPMENT-GUIDE.md) · [接入映射](<packages/PKG-058_DeviceSignals.md>) |
| PKG-059 报警生命周期与处置记录 | 条件观察；发生/确认/结束；再发生；抑制策略；历史/恢复关联 | [SM-005](<modules/SM-005_diagnostics.md>) | 机台运行、独立互联/存储服务管理 | [IM-068唯一指导](../independent-modules/alarms/DEVELOPMENT-GUIDE.md)；[应用接入映射](packages/PKG-059_Alarms.md) |
| PKG-060 三维配准与位姿质量 | Pair/固定评价；刚体图/锚点；覆盖/留出/可观测性；发布/一次应用 | [SM-012](modules/SM-012_surface.md) | 多视角表面整合、独立3D比较与量测工具 | [应用映射](packages/PKG-060_Registration3D.md) / [IM-033唯一指导](../independent-modules/registration-3d/DEVELOPMENT-GUIDE.md) |
| PKG-061 / IM-042 曝光增益与照明优化 | 合法空间/锁定；有界搜索；观察关联；逐任务约束；Pareto/独立验证；建议及恢复交接 | [SM-007](modules/SM-007_acquisition.md) | AOI/钢网成像优化适配器、独立视觉工程试验台 | [映射页](packages/PKG-061_ImagingOptimization.md) / [唯一实施指导](../independent-modules/imaging-optimization/DEVELOPMENT-GUIDE.md) |
| PKG-062 / IM-037 有界二部图分配与歧义检查 | 有限图校验；最大基数/最小费用；替代解见证；完整性/取消/预算 | [SM-011](modules/SM-011_vision-features.md) | 钻孔目标关联、激光微孔层对内目标关联 | [映射页](packages/PKG-062_Assignment.md) / [唯一实施指导](../independent-modules/assignment/DEVELOPMENT-GUIDE.md) |

## 3. 六类独立工具宿主

这些是能力包的组合应用，不是另一套业务核心，也不占用公共模块的数量。

| 宿主 | 组合与独有责任 |
|---|---|
| 离线编程站 | 资料/库/程序/快编/试检/视图；无设备命令能力，草稿/发布/线上激活分开 |
| 独立复判站 | 队列/证据/意见/返修任务；与机旁复判共用PKG-044，不能改机判 |
| 质量/SPC工作站 | 查询/统计/报告/跨工序关联；只读生产事实，保留总体与水位 |
| MES互联服务与管理端 | PKG-047服务无UI也工作；客户协议可选；管理端不拥有机器控制权 |
| 视觉工程试验台 | 参数编辑、图像/表面、算法、Replay与资格实验；工程结果不能混入生产 |
| 维护与部署工具 | 诊断、配置、校准/设备工具的授权入口、备份/升级/恢复；具体设备仍由受控适配提供 |

机台主应用按PG组合相应模块；不强制每个PG一个进程。跨进程仅在设备隔离、native故障、资源/部署需求有依据时采用，不因“完全独立”将所有DLL改为微服务。

## 4. 依赖与研发顺序

下面是各包所需公开能力的直接依赖；它细化DEV-PLAN-014既有WP，不转移WP/事实Owner。依赖层数只用于检查循环和找可并行候选，不代表固定批次或必须等整层完成。表中并列多种输入/设备时表示支持这些路径所需的公开端口集合，不是所有消费者的强制运行依赖：2D量测无需加载三维后端，单相机任务无需轴卡/投影器。每个实施切片在任务卡固定实际必需集合与可选集合，禁止运行时偷偷增加依赖。

| 包 | 直接依赖PKG | 能力层次 |
|---|---|---:|
| PKG-001 | PKG-002, PKG-003, PKG-004, PKG-005 | 3 |
| PKG-002 | — | 1 |
| PKG-003 | — | 1 |
| PKG-004 | PKG-002, PKG-005 | 2 |
| PKG-005 | — | 1 |
| PKG-006 | PKG-005 | 2 |
| PKG-007 | — | 1 |
| PKG-008 | PKG-002, PKG-005, PKG-006 | 3 |
| PKG-009 | PKG-002, PKG-005 | 2 |
| PKG-010 | PKG-002, PKG-005, PKG-007 | 2 |
| PKG-011 | PKG-002, PKG-005 | 2 |
| PKG-012 | PKG-006, PKG-008, PKG-009, PKG-010, PKG-011, PKG-057, PKG-058 | 5 |
| PKG-013 | PKG-006, PKG-014 | 4 |
| PKG-014 | PKG-006 | 3 |
| PKG-015 | PKG-006, PKG-007, PKG-033 | 4 |
| PKG-016 | PKG-006, PKG-007, PKG-015 | 5 |
| PKG-017 | PKG-006, PKG-007, PKG-016, PKG-022 | 6 |
| PKG-018 | PKG-007, PKG-020 | 3 |
| PKG-019 | PKG-007, PKG-018 | 4 |
| PKG-020 | PKG-007 | 2 |
| PKG-021 | PKG-006, PKG-007, PKG-020 | 3 |
| PKG-022 | PKG-006, PKG-007, PKG-020, PKG-033 | 4 |
| PKG-023 | PKG-006, PKG-020 | 3 |
| PKG-024 | PKG-006, PKG-014, PKG-020, PKG-033 | 4 |
| PKG-025 | PKG-006, PKG-014, PKG-020 | 4 |
| PKG-026 | PKG-006, PKG-014, PKG-020, PKG-022, PKG-033 | 5 |
| PKG-027 | PKG-006, PKG-007 | 3 |
| PKG-028 | PKG-006, PKG-007, PKG-013, PKG-015, PKG-027 | 5 |
| PKG-029 | PKG-007, PKG-020, PKG-027, PKG-031 | 5 |
| PKG-030 | PKG-007, PKG-020, PKG-021, PKG-027, PKG-029, PKG-031 | 6 |
| PKG-031 | PKG-007, PKG-020, PKG-027 | 4 |
| PKG-032 | PKG-007 | 2 |
| PKG-033 | PKG-002, PKG-041 | 3 |
| PKG-034 | PKG-007, PKG-032, PKG-033 | 4 |
| PKG-035 | PKG-002, PKG-004, PKG-033, PKG-034, PKG-041 | 5 |
| PKG-036 | PKG-018, PKG-019, PKG-032, PKG-034, PKG-035, PKG-061 | 6 |
| PKG-037 | PKG-002 | 2 |
| PKG-038 | PKG-005, PKG-006 | 3 |
| PKG-039 | PKG-002 | 2 |
| PKG-040 | PKG-004, PKG-037, PKG-041 | 3 |
| PKG-041 | PKG-005 | 2 |
| PKG-042 | PKG-004, PKG-041 | 3 |
| PKG-043 | PKG-035, PKG-038, PKG-040 | 6 |
| PKG-044 | PKG-004, PKG-037, PKG-040, PKG-042 | 4 |
| PKG-045 | PKG-039, PKG-042 | 4 |
| PKG-046 | PKG-003, PKG-042 | 4 |
| PKG-047 | PKG-004, PKG-040, PKG-041 | 4 |
| PKG-048 | PKG-037, PKG-040, PKG-042 | 4 |
| PKG-049 | PKG-006, PKG-007, PKG-020, PKG-027 | 4 |
| PKG-050 | PKG-003 | 2 |
| PKG-051 | PKG-002, PKG-003, PKG-049, PKG-050 | 5 |
| PKG-052 | PKG-006, PKG-033, PKG-038 | 4 |
| PKG-053 | PKG-004, PKG-033, PKG-052 | 5 |
| PKG-054 | PKG-004, PKG-042, PKG-053 | 6 |
| PKG-055 | PKG-007, PKG-043 | 7 |
| PKG-056 | PKG-001, PKG-041 | 4 |
| PKG-057 | PKG-002, PKG-005, PKG-006, PKG-007, PKG-027 | 4 |
| PKG-058 | PKG-002, PKG-005, PKG-007 | 2 |
| PKG-059 | PKG-002, PKG-004, PKG-005, PKG-041 | 3 |
| PKG-060 | PKG-007, PKG-027, PKG-031 | 5 |
| PKG-061 | PKG-002, PKG-005, PKG-013 | 5 |
| PKG-062 | — | 1 |

实践顺序：类型/坐标/配置/帧/诊断→所需成像/特征/量测与身份/结果→第一条离线完整链→第二制程/3D复用→多包滚动并行→各产品完整操作/故障/部署→真实设备和同板资格。库/程序/快速编程、AI数据、UI原型可以在冻结输入下同步准备，不把全部公共库写完才接产品。一个包一个写入Owner；Core/Adapter/UI由该Owner连续完成，确需控件子任务时先隔离文件和契约，不让多个会话同时改同一包核心。

## 5. 当前设计深度与继续审核

本轮明确旧PKG目录的功能归属、输入处理输出、失败断言、依赖、宿主与迁移位置，尚未宣告62个包的全部精确API/性能值和生产算法已冻结。完全独立能力的数量、准入和逐项指导以[52项独立模块架构](../independent-modules/INDEPENDENT-MODULE-ARCHITECTURE.md)为准。原19项映射保留为用户来源追踪；任何后续工作从独立模块架构选择模块和真实消费者，再进入唯一专业指导/合同。AOI源文档以REF-008副本为比较输入，不能从源工程的已基线/已实现状态推断平台已完成。

逐包复核须覆盖：功能变体是否全；每个字段/坐标/单位/资源是否明确；消费者能否接收；无UI是否完整；失败/取消/断连/重启是否闭合；参数/UI/算法是否同源；质量、性能及国际对标是否有可执行实验。未决的内部设计工作继续推进，只有具体客户/传感器/真实样本条件才记为外部门禁。

<a id="boundary-derivation"></a>
## 6. 数量如何推导，为什么这样拆合

先从“资料/身份→编程→成像/采集→几何/识别/量测→判定/提交→复判/追溯→维护/交付”及无UI/带UI消费者提取功能，再看职责、状态写入权、资源寿命、变化频率和发布边界。具备明确消费关系且可单独测试/发布的能力成为PKG；产品判据与真实流程留PG，厂商驱动是可选Adapter，窗口/按钮不是计数单位。一个PKG可以包含Core和可选Wpf等多个程序集，程序集数在实现任务冻结，不能与PKG数混算。

本轮初稿56包经第二次反向检查补为59包：既有DeepSight公开指导显示完整轮廓序列与预览不同；设备I/O不是轴位置或相机像素；报警确认与条件消失也不是日志追加。各有不同消费者和错误路径，因此新增057/058/059，已有ID不重排。来源及阅读范围见[REF-008](../references/REF-008_PCBA-AOI指导副本与平台采纳映射.md#module-boundary-evidence)。后续3D反向复核又发现配准缺少独立交付归属，因此补为60包（060），理由见下表；不是由增加文档数量推导功能完成度。曝光/照明复核进一步发现优化试验被笼统放入036，而其独立工程消费者不应依赖程序编辑，因此新增061，当时为61包；012执行、013评价、035采纳仍各守原Owner。钻孔/微孔的两个消费者又共同需要固定图分配和替代解证明，因此新增062，最终形成62个历史PKG。062是无状态纯图计算，不应依赖021提边、022位姿拟合或037/048事实关联；建图和物理解释仍在PG。当前独立模块数量以本表上方链接的架构文件为准。

| 易重叠/易遗漏的能力 | 当前拆合决定 | 用于否定错误划分的反例 |
|---|---|---|
| Camera / ProfileAcquisition / Reconstruction | 008管像素采集，057管有实际采样位置的轮廓/高度输入，028管从适用原始观测重建；共享006/027数据 | 已有物理高度仍强制投影相机；轮廓缺一线后直接前移行号，都会破坏计量 |
| 设备信号、运动、采集编排 | 058给值/质量/时序/受控I/O；010给轴语义；012组合当前设备端口 | 一个采集计划不需要运动，不能因共用模块而强制初始化轴卡；同PLC也不能被两个包各自独占连接 |
| 诊断、报警、设备与质量状态 | 005记录诊断，059管理发生/确认；设备条件/处置权仍各原Owner | 点击确认ERROR日志不能恢复运动，也不能质量放行 |
| 预处理、图像质量、Blob、工艺判断 | 014变换像素，013量化可观察性，025给区域/特征，PG解释焊桥/污染等 | 红色高亮或大区域不是自动缺陷；预处理不能覆盖原始证据 |
| 标定、校正、坐标、基准面 | 015管理标定资产/适用性，016按映射重采样，007计算变换，029估计当前局部基准 | 换局部平面不能修改全局标定；显示镜像不是物理坐标变换 |
| 三维特征、配准、参考、重建 | 031处理单表面；060估计多表面位姿/图质量；029核基准资格；028重建/融合；007只计算已有变换 | 单平面低残差却缺位姿自由度，不能由Features非空或全局Scores代替；校准已确定的多方向融合不必自由ICP |
| 固定图分配、提边、定位和实体关联 | 062独立求解固定cost图；021提供特征；022联合对应/位姿；037/048维持原事实关系 | 同一图无需相机可求解；未知Mark位姿的费用随整体解改变，不能偷换成一次分配 |
| ROI、特征、量测、Viewport | 020定义/编辑几何，021/031提取候选，030执行被测量，049显示交互 | 测量不能依赖窗口加载；绘图缩放/LOD不改变计算输入 |
| 模型资产与参考库/程序 | 033保存字节与引用；034维护封装/变体业务；035发布闭包 | 相同模型文件在两个用途复用，不得合并两套工艺规则或使用最新版本偷换旧程序 |
| 成像质量、采集、成像优化、快编 | 013给原质量量，012按计划执行，061搜索/试验/建议，036接入程序编排 | 同一优化控件可在没有程序库的试验台运行；设备ACK不证明收敛，优化器无权发布程序 |
| 覆盖、路径、快速编程 | 018核目标域，019算扫描计划，036调用产品生成器并给差异 | 多拍一张不能抵消必检目标缺一项；快速编程不强制AI或覆盖人工修改 |
| 存储、事实、查询、报表 | 041技术适配，040结果/证据事务，042受控查询，046渲染输出 | 数据库“更新一行”不授予改机判；报表导出不能改生产分母 |
| 统计、跨工序、人工意见、最终处置 | 045/048为投影，044为意见；处置政策及正式Owner按产品契约绑定 | 相关性/人工复判通过不能自动成为正式放行；不为凑模块建万能质量主对象 |
| 物料输送、夹具、PLC/安全 | 通用信号用058，轴用010，互联用047；各机型Application持有实际转运/夹具流程 | 连续卷材与停板设备不能套同一进出板状态机；软件IO控件不能代替安全PLC |
| 校准/维护/升级与工具宿主 | 015/055/056等给能力，六类工具组合；不另复制“维护核心” | 同一校准资产不得因设备工具和生产页面各有入口产生两个权威 |

若后续证实一种专用行为被多个产品实际复用，先把数据/所有权/状态及至少两个消费者冻结，再新增或调整PKG；同样，两个包只能一起版本化/测试且无独立消费者时考虑合并。拆合修订主表、双方指导、依赖和任务卡，由原契约/集成Owner处理，不让不同会话各自重划边界。

一份模块指导的完成判据不是“有五个标题”：每项功能必须有可执行输入、精确参数/接口、步骤/方法依据、输出与资源、事件、失败恢复、无UI及可选UI调用、负载/性能、正常和反例及第二消费者。当前各包已具边界和功能规划，详略不同；逐字段/变体/完整UI与试验不足处继续完善，不能把这些设计稿一次性标为可编码。
