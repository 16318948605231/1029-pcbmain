# Repository Project / Namespace Blueprint

- 文档 ID：`DEV-PLAN-006`
- 版本：`2.3.0-prep`；日期：2026-09-27；状态：`DesignReview`


## 1. 当前状态与唯一落点

本页维护制程/应用工程规划及28SM历史责任映射。当前52项独立模块的工程、命名空间、公开契约和测试位置只由各模块唯一DEVELOPMENT-GUIDE.md冻结；本页不提供另一套候选根。旧FS/DEV-PLAN-008的历史实现名不能据此另建工程。每切片获准实现前由集成人同步实际消费者/FS/测试/PageContract引用；保留既有代码，迁移另行界定。

技术按唯一入口：VS2026、C#/.NET10、WPF、DevExpress25.2.3、AsunImage。使用本机DevExpress，不从NuGet下载；AsunImage仅公共边界，不检查内部或授权。

## 2. 建议目录与依赖

```text
contracts/v1/                       唯一持久化/传输Schema和catalog（逐切片采纳）
src/Modules/<module-key>/Contracts/  公开类型与接口；不复制JSON权威定义
src/Modules/<module-key>/Core/       独立功能，不引用产品/WPF/厂商SDK
src/Modules/<module-key>/Wpf/        确有复用需求的可选控件
src/Adapters/<adapter-key>/         AsunImage/已有控件/存储等批准公共适配
src/Processes/<process-key>/Domain/ 专属目标、测量意义、规则和程序生成
src/Processes/<process-key>/Application/ 用公开能力编排任务
src/Processes/<process-key>/Wpf/     机台特有页面与投影
src/Apps/<host-key>/                组合根、设备/软件配置与工作台装配
tests/Modules/<module-key>/         模块专属测试、必要宿主及基准
tests/Processes/<process-key>/      领域、应用和UI验收
tests/Integration/<flow-key>/       由集成人维护的跨模块链
```

目录表示所有权，不要求每层必建csproj。模块最少有可独立交付Core，明确公开契约；有真实控件消费者再交付Wpf。若公开类型直接随Core发布且无反向依赖需要，不为凑数建空Contracts包。跨模块只引用所需公开契约，不能所有Core互引；WPF接收投影/应用端口，不拿领域私表或HALCON裸句柄。

组合根→制程Application→公共能力契约；制程Domain只保留自身规则与值对象；适配器实现被注入端口；UI→Application契约/显示投影。不能把“Domain→Platform→SDK”写成强制直接引用SDK的单链。Schema生成类型与手写公开类型的唯一生成关系须冻结，不维护两套字段定义。

## 3. 公共模块名称候选与写入根

下表只保留原28SM责任分组和旧程序集名，不能作为建项路径。当前独立模块依[独立模块架构](../independent-modules/INDEPENDENT-MODULE-ARCHITECTURE.md)定位各自唯一指导；具体工程、namespace及允许路径按指导当前binding，不从历史PKG/SM命名推断。Contracts/Wpf只在有实际发布边界时创建，UI与存储适配不混入Core。

| 模块 | module-key | Core程序集候选 | 职责 |
|---|---|---|---|
| SM-001 | `Composition` | `Asun.Composition.Core` | 装配与生命周期 |
| SM-002 | `Configuration` | `Asun.Configuration.Core` | 配置快照 |
| SM-003 | `Localization` | `Asun.Localization.Core` | 语言资源 |
| SM-004 | `Authorization` | `Asun.Authorization.Core` | 权限服务 |
| SM-005 | `Diagnostics` | `Asun.Diagnostics.Core` | 日志/追踪/诊断 |
| SM-006 | `Frames` | `Asun.Frames.Core` | 帧与租约 |
| SM-007 | `Acquisition` | `Asun.Acquisition.Core` | 采集边界 |
| SM-008 | `Coordinates` | `Asun.Coordinates.Core` | 坐标与单位 |
| SM-009 | `Calibration` | `Asun.Calibration.Core` | 标定 |
| SM-010 | `RoiMeasurement` | `Asun.RoiMeasurement.Core` | ROI与量测 |
| SM-011 | `VisionFeatures` | `Asun.VisionFeatures.Core` | 特征能力 |
| SM-012 | `Surface` | `Asun.Surface.Core` | 表面/高度 |
| SM-013 | `Coverage` | `Asun.Coverage.Core` | 计划与实际覆盖 |
| SM-014 | `ManufacturingInput` | `Asun.ManufacturingInput.Core` | 制造输入适配 |
| SM-015 | `ReferenceLibrary` | `Asun.ReferenceLibrary.Core` | 参考资产 |
| SM-016 | `ProgramPackage` | `Asun.ProgramPackage.Core` | 程序包 |
| SM-017 | `Identity` | `Asun.Identity.Core` | 身份与尝试 |
| SM-018 | `Execution` | `Asun.Execution.Core` | 计算任务图 |
| SM-019 | `Evaluation` | `Asun.Evaluation.Core` | 规则求值 |
| SM-020 | `ResultEvidence` | `Asun.ResultEvidence.Core` | 结果证据持久化 |
| SM-021 | `Replay` | `Asun.Replay.Core` | 回放 |
| SM-022 | `Review` | `Asun.Review.Core` | 复判协作 |
| SM-023 | `Quality` | `Asun.Quality.Core` | 统计与跨工序投影 |
| SM-024 | `Integration` | `Asun.Integration.Core` | 外部交付 |
| SM-025 | `Presentation` | `Asun.Presentation.Core` | 设计系统与视觉控件 |
| SM-026 | `AiAssistance` | `Asun.AiAssistance.Core` | AI建议 |
| SM-027 | `Qualification` | `Asun.Qualification.Core` | 资格验证 |
| SM-028 | `Delivery` | `Asun.Delivery.Core` | 升级交付 |

SM-025的DesignSystem和Viewport可按独立消费者拆子包，但共享样式/图标/资源由一Owner维护。SM-010对已有ROI控件采用公开桥接，不复制其内部；SM-007的厂商连接放适配器，不能将深视控件依赖塞进全部机台。SM-023名称不代表拥有质量放行权。

## 4. 制程与复用验证

`<process-key>`沿用PG文件名中的工序名，例如`drill`、`stencil`、`dispense`、`coating`；编号用于追溯而不进入业务对象语义。公共库不得引用PG项目。首两个消费者引用同一版本公共包，不复制源码。若第二消费者迫使公共库依赖第一个产品类型，退回边界设计；领域扩展通过该制程契约或注入策略完成。

独立UI模块提供宿主注入的主题、语言、导航与受控命令；页面选择不改变生产当前板。产品宿主负责全局语言入口，控件不各带一套语言按钮。语言资源按模块归属、稳定键名注册；共享词条由集成人处理。

## 5. 发布与版本

同进程独立DLL是默认设计候选；进程隔离须有崩溃/资源/不可信边界依据，不能因“独立模块”自动做微服务。公开契约发生单位、可空、资源所有权、取消或顺序语义变化，必须按破坏性影响评审；内部算法替换也须更新方法版本与数值回归。包可单独构建/测试/发布，宿主固定依赖组合，不运行时跟随latest。

工程生成、solution、公共props、依赖版本、schema生成输出、安装包、全局资源索引由集成Owner串行维护。具体DEV-PLAN-008/FS代码位置同步之前，不能凭本页候选创建平行实现。


<a id="ocr-package"></a>
## 6. OCR独立模块与产品消费位置

规划消费者为PG-006 PCB字符、PG-015/017/018元件标记及来料/终装文字。唯一模块根为`src/Modules/ocr/`、测试根为`tests/Modules/ocr/`；Core namespace为`Asun.Modules.Ocr`，Core/HalconAdapter/Wpf及各测试csproj按IM-028 §16绑定。Core仅BCL，真实HALCON经既有AsunImage适配，可选WPF不负责核心初始化；不在VisionFeatures或产品目录复制另一识读器。

模块公开签名、Core/HalconAdapter/Wpf的唯一工程及验证绑定按[IM-028 ocr §16](../independent-modules/ocr/DEVELOPMENT-GUIDE.md#16-逐切片准入与剩余门)，不从本页另选TextRecognition工程根。全部模块任务沿永久原会话；WP-09/10/11/12只作应用分工映射，共享Schema、产品接口/Owner另串行采纳。Paddle是离线研究候选，未成为已选运行依赖。FS-061/IOCRMarking仍负责AOI组合；[DEV-VIS-021A](../shared-modules/guidance/03-vision/DEV-VIS-021A_OCR与DeepOCR独立能力开发指导.md)维护产品关联/比较与来源研究。本轮不创建工程或授权产品代码。


## 7. 点胶/涂覆的工程落点补充（公共路径改按PKG，产品路径保留）

公共截面计算复用`RoiMeasurement`及既有ROI公共适配，表面/基底复用`Surface`，完整性复用`Coverage`。共享视觉投影在`Presentation`内确定剖面/证据视图的独立子包，复用现有控件能力，不另建胶路测量器。点胶和涂覆页面分别归`src/Processes/dispense/Wpf/`和`src/Processes/coating/Wpf/`，领域/应用/测试按§2目录对应。

具体分包与写入边界、两个消费者和退出断言见[DEV-PLAN-014 §8](DEV-PLAN-014_全量研发工作包与并行依赖DAG.md#dispense-coating-slices)。允许路径必须在正式任务卡列到本次文件，不能将整棵Adapters或Presentation目录同时授给多个会话。没有建立这些工程，也不自动迁移已有ROI控件或客户项目。

## 8. 插件与THT的工程落点补充（公共路径改按PKG，产品路径保留）

共享坐标、轴/端点/截面、表面支撑、连通候选与覆盖分别沿Coordinates、RoiMeasurement、Surface、VisionFeatures、Coverage；控件沿Presentation，不新增“通用针/焊点事实库”。插件在`src/Processes/insertion/`，波峰/选择焊在`src/Processes/wave-solder/`，各自Domain/Application/Wpf及对应测试。AOI FS-060/062仍是原应用组合，不挪为公共核心。

精确开发顺序、允许/禁止路径与接收断言见[DEV-PLAN-014 §9](DEV-PLAN-014_全量研发工作包与并行依赖DAG.md#insertion-tht-slices)。这里只定义候选落点；正式端口、项目/程序集及引用由原Owner冻结，未创建工程或迁移客户项目。

<a id="independent-capability-packages"></a>
## 9. USER-002的原分包候选（当前独立模块以PKG为准）

28SM是能力归属，不是一对一固定DLL数。下面只在真实消费者/契约冻结时创建必要包，Core类型无UI依赖、Wpf可选、具体AsunImage/SDK/数据库/报告渲染在Adapter。允许公开契约随Core发布；不机械新增空Contracts项目。不存在通用包访问所有工艺私表/VM的捷径。

| 能力 | 唯一模块实施入口 | 宿主边界 |
|---|---|---|
| 相机/光源/运动/结构光 | [相机](../independent-modules/camera-acquisition/DEVELOPMENT-GUIDE.md)、[光源](../independent-modules/lighting-control/DEVELOPMENT-GUIDE.md)、[运动](../independent-modules/motion-control/DEVELOPMENT-GUIDE.md)、[结构光](../independent-modules/structured-light/DEVELOPMENT-GUIDE.md) | 多设备编排由应用持有，厂商实现按各Adapter门 |
| 模板匹配/Mark | [IM-026 alignment-2d](../independent-modules/alignment-2d/DEVELOPMENT-GUIDE.md) | 应用选输入、用途及位姿采用，不建另一Matching根 |
| 条码/二维码与OCR | [IM-027 barcode](../independent-modules/barcode/DEVELOPMENT-GUIDE.md)、[IM-028 ocr](../independent-modules/ocr/DEVELOPMENT-GUIDE.md) | 1D/2D同barcode模块，训练建议不静默改生产配置 |
| 预处理/分割/良品差异 | [IM-021](../independent-modules/image-preprocessing/DEVELOPMENT-GUIDE.md)、[IM-029](../independent-modules/segmentation/DEVELOPMENT-GUIDE.md)、[IM-030](../independent-modules/variation-inspection/DEVELOPMENT-GUIDE.md) | 各自Core/Adapter/UI工程按当前binding，不按VisionFeatures再拆同义工程 |
| 相机标定/校正/拼接 | [IM-013](../independent-modules/calibration-assets/DEVELOPMENT-GUIDE.md)、[IM-022](../independent-modules/image-rectification/DEVELOPMENT-GUIDE.md)、[IM-023](../independent-modules/mosaic/DEVELOPMENT-GUIDE.md) | 相机光学与拼接几何/运动资格分开，应用提供原采集事实 |
| 统计/报告 | [IM-043](../independent-modules/statistics/DEVELOPMENT-GUIDE.md)、[IM-044](../independent-modules/reporting/DEVELOPMENT-GUIDE.md) | 渲染与统计Core分开，结果都是原事实投影 |
| 查询/存储 | [IM-045](../independent-modules/query/DEVELOPMENT-GUIDE.md)、[IM-066](../independent-modules/storage-database/DEVELOPMENT-GUIDE.md) | PostgreSQL/Npgsql和硬盘文件实现留存储Adapter，业务事实仍原Owner |
| 外部集成/MES | [IM-046](../independent-modules/integration-transport/DEVELOPMENT-GUIDE.md) | 客户协议/领域映射由应用提供，可靠交付技术合同唯一 |
| 通用人工复判 | [IM-067](../independent-modules/human-review/DEVELOPMENT-GUIDE.md) | ReviewStation可独立部署，质量最终处置/返修/设备动作归应用 |
| ROI/计量/影像窗口/测量工作台 | [IM-024](../independent-modules/roi-geometry/DEVELOPMENT-GUIDE.md)、[IM-036](../independent-modules/metrology/DEVELOPMENT-GUIDE.md)、[IM-060](../independent-modules/viewport/DEVELOPMENT-GUIDE.md)、[IM-065](../independent-modules/measurement-workbench/DEVELOPMENT-GUIDE.md) | 独立公开组合，工作台不复制算法或资源Owner，不依赖隐藏窗口 |

本表是细化候选，不重排历史FS目录绑定或默认创项目；正式采用前由集成Owner同步真实项目/命名空间/引用。相互依赖只引用所需公开契约，不因同SM编号把所有子包绑成强制安装集合。不同包可独立版本/发布，但宿主固定经过集成验证的组合。

## 10. 独立模块重新规划后的唯一工程候选

本页原先提出的`src/Modules/<key>/`、`src/Processes/<process-key>/`和`src/Apps/<host-key>/`仅是历史目录候选，不是当前代码落点。当前解决方案已在`AsunVision.slnx`、`src/`和`tests/`形成实际项目边界；实现任务必须从该真实基线映射已准入模块，不能为迁就本蓝图再复制一套目录。52项候选的拆分及依赖方向见[独立模块架构](../independent-modules/INDEPENDENT-MODULE-ARCHITECTURE.md)，正式程序集、命名空间和项目引用在具体切片冻结。

Core/Contracts/Adapter/Wpf按必要性分项目；UI包PKG-049/050/051无强制纯算法Core空工程。能力依赖是公开端口，不强制所有上游实现程序集同时加载。PKG的具体依赖拆到子能力后无环，SM的装配先决与实际编译引用分开，不能把Composition装配所有包解释成所有包反向编译依赖Composition。
