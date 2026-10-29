# ContractCandidate 详细实施基线
- 文档 ID：`DEV-CONTRACT-BASE-001`
- 版本：`1.2.34-prep`
- 状态：`DesignReview`
- 架构基线：`ARCH-PCBA-VISION-001 v0.5.3`

当前C-01～C-08是待采纳的语义候选；尚未具备正式字段、类型、状态/Owner和批准记录，旧ImplementationSpecificationReady状态失效。不得据此让各会话自行补DTO或恢复旧实现队列。适用架构以[平台设计基线](../00-baseline/PLATFORM-DESIGN-BASELINE.md)为准。

本文不是第二套 schema；它是 C-01~C-08 的**字段语义、边界、验证规则和消费者映射**。正式代码必须把这些语义绑定到仓库唯一权威 Schema。Formal code must bind to that single approved Schema and Contract Owner; this register is **not a second schema** and cannot be used to create parallel DTOs, states or fact stores.

## C-01 身份与状态

覆盖：Product/ProductRevision/WorkOrder/Lot/Board/Panel/PanelUnit/Layer/Side/Roll/RollSegment/Carrier/StationInstance/ProcessAttempt/InspectionAttempt/BoardRun，以及 Scope、Parent、Causality、Epoch、Owner。

### 必须验证
- ID 唯一；版本和 hash 对应同一内容；Parent 不形成循环；Scope 不交叉越权。
- 状态必须满足正交状态约束；不能把质量状态、执行状态、设备状态压成一个枚举。
- 重复事件幂等；乱序按批准策略处理；时间域/epoch 不匹配拒绝。

观察解析、实体/观察/尝试分层、拆板/翻面/载具换件及原身份Owner绑定的具体行为与来源字段差异见[PKG-037 §6–7](../shared-modules/packages/PKG-037_Identity.md#identity-implementation)。原Orchestrator身份入口持有生产绑定写权，037负责独立解析/关系能力，不新增IdentityStore。该包D1–D6列出尚缺的正式字段、CAS唯一位置、幂等摘要和宿主接板模式，仍在本C-01/C-04采纳，不让实现者自造DTO或把barcode、BoardRunId、载具位置统一成实体主键。

## C-02 Program/Recipe/Manifest

覆盖 ProductRevision、ManufacturingGeometrySnapshot、SourceSetManifest、LayerStack/BuildUp/ViaDefinition、InspectionProgram、Recipe、MachineProfile、Calibration、Library 与 EffectiveRuntimeManifest。

### 必须验证
- 所有生产依赖明确 `id + version + sha256`。
- `latest`、隐式 default、同 version 异 hash、循环依赖均拒绝。
- ManufacturingGeometrySnapshot 必须引用 approved BoardModel，不重复建 Geometry 主库。

源发布Schema与平台的具体采纳差异见[PKG-035 §12](../shared-modules/packages/PKG-035_ProgramPackage.md#program-source-adoption)：语法接受不代表精确引用、业务键唯一、兼容范围、审批或真实内容有效。该Schema只表示Released产物，不能复用为草稿；源AOI必需BoardModel/检测模型/标定的形态须按真实程序种类审查，不能让独立复判或非计量工作站填虚假对象。上述覆盖列表不是要求所有程序携带同一个万能对象图；当前仍待C-02正式采纳，不因此新建另一份Schema。

## C-03 Coordinate/3D/Metrology

覆盖 CoordinateGraph/FOV/Stitching/HeightField/Rigid/Affine/NonRigid/WebCoordinate、MeasurementDefinition/Quality/Uncertainty/Qualification。

### 必须验证
- 单位、方向、参考坐标和有效域显式；domain/out-of-domain 必须拒绝。
- Raw/Canonical/Display 三层分离。
- MeasurementPairing、ReferenceFrame、Direction、Finite/Infinite support 显式。

## C-04 Pipeline/Decision/Commit

覆盖 Stage/MeasurementSet/CoverageResult/InspectionFact/RuleEvaluation/InspectionDecision/MachineDecision/Evidence/Receipt/Feedback。

### 必须验证
- CalculationIdentity 与 CommitIdentity 分离。
- 只有批准 Producer/CommitOwner/ActivationOwner 能执行相应生产副作用。
- 重算/重试不生成重复事实；ACK 不等价 Applied/Committed。
- 保存合法结果的身份/授权/最小证据门、PG必检完整性、Replay输入完整性、最终质量放行分别绑定；NG/Unknown/未测不因未通过质量门而一律拒绝保存，保存成功也不授质量通过。原实现语义见[040 §6–11](../shared-modules/packages/PKG-040_ResultEvidence.md#result-evidence-two-stage)，复合功能接缝见[DEV-CONTRACT-002 §3.1](DEV-CONTRACT-002_功能卡Contract、Schema、State、Owner与提交绑定开发指导.md#spi-function-owner-binding)。

计量试验报告的具体接收语义见[计量资格合同采纳](#qualification-contract-semantics)；纯FS018返回与宿主存证/资格签发分开，不能从报告含“资格”推导事实写权。

## C-05 WPF product workspace

覆盖 PageContract/ApplicationPort/Query/Command/Permission/AutomationId/八态/Shortcut/Localization/DPI/UIA。

### 必须验证
- 页面不得持有 HALCON/AsunImage 原生对象。
- Command 必须映射到受控 Application Port；权限校验不能只在 UI。
- 八态和异常恢复必须可自动化测试。

## C-06 Deployment/Security/Plugin/Adapter

覆盖进程 Owner、IPC、签名、证书、PluginManifest、Adapter capability/version/permission/resource。

通用身份授权和审计的模块级 API、求值、租户/用途隔离、当前 fence、审计回查及资源排空唯一见 [IM-004 authorization](../independent-modules/authorization/DEVELOPMENT-GUIDE.md) §3–7；本 C-06 只承载产品安全与适配映射，不定义第二个授权核心。Policy Allowed、Eligibility、审计持久性和资源终态分开；历史决策不恢复当前授权，宿主 CommitOwner 必须在实际提交线性化点与撤权协调。生产身份、审计存储及原子 fence 只阻相关集成切片，不阻无 UI 求值/协调/合成恢复 Core。

### 必须验证
- SDK 类型不得穿透领域层。
- 未签名/篡改/能力不兼容/证书失效必须阻断。
- 卸载插件后状态可解释地进入 NotReady，而不是崩溃/静默降级。

## C-07 Performance/Recovery

覆盖 PerformanceProfile、ContinuousInspectionProfile、queue、backpressure、resource、HIL、long-run、RPO/RTO。

### 必须验证
- 每条生产链都有 P50/P95/P99、内存峰值、队列上限、取消、恢复指标。
- 备份存在不等于可恢复；恢复演练需要独立证据。

## C-08 Product assembly/route/coverage/cross-site/external test

覆盖 ProductAssembly/ProcessRoute/InspectionCoverage/Station/CrossSiteEvent/ExternalTestRegistration/QualityPlan/RequiredEvidenceSet/RouteAssessmentContext。

### 必须验证
- RouteAssessment 只能消费已提交事实与明确水位；不直接读取当前 UI/原图/临时 Recipe。
- Coverage 缺口、迟到、未知条件必须可见。
- 外部测试结果必须有来源、适用范围、版本、时间和 commit semantics。

## Viewer细化的原候选采纳项（2026-09-28）

详细算法/公开API/控件交互只维护于[IM-060 viewport](../independent-modules/viewport/DEVELOPMENT-GUIDE.md)，产品工作区接入见[DEV-UI-042 §9–13](<../shared-modules/guidance/05-ui/DEV-UI-042_视觉/3D工作区与ROI交互开发指导.md#viewer-execution>)。本节列原C归属，不定义新Schema/Scene库或第二Owner。

| 原候选 | 需同一Owner采纳的差异 | 消费者/阻断范围 |
|---|---|---|
| C-03 | 源像素中心/边界、crop/LOD实际映射、DIP/物理像素和已呈现代、3D原索引/可见性/插值来源 | 007/027/049；缺定义阻断相应命中/联动/计量，不阻断已获准独立2D查看 |
| C-04 | exact结果/证据关系与Actual/Reference/派生角色、读取保持、hash范围/完整性及导出闭包 | 040/041与宿主，049不接私表或新事实Store |
| C-05 | 只读/编辑意图隔离、呈现/请求回执区别、图层/探针投影、操作能力/未装配、盲审全路径裁剪、布局与快捷键 | 049/UI013/测量工具；不能据源API清单直接采纳其未说明的语义 |
| C-06/07 | 授权变更和缓存交付、共享等待取消/排空/释放者、字节预算/线程与GPU完成、后端丢失后的能力变化 | 原安全/资源Owner和049适配，不能只隐藏按钮或提前返池 |

C-05“页面不得持有原生对象”约束页面/VM与公开投影；不禁止内部显示适配按明确寿命拥有渲染所需native对象。精准类型/错误码/授权新鲜度/后端线程/性能数值仍在原合同及GATE-001采纳，当前不构造可直接调用的猜测签名。

<a id="roi-topology-contract-semantics"></a>
## ROI拓扑、转换及观察支持的原候选采纳项（2026-09-29）

方法唯一在[024 §5–11](<../shared-modules/guidance/03-vision/DEV-VIS-024_ROI与Inspection Target Selection开发指导.md#roi-topology-raster-method>)；020几何、007坐标、049显示、025/030特征量测及035/原编辑Owner分别保持职责。以下是字段语义候选，不把源控件类型、枚举或审计协议直接复制成平台Schema。

| 原候选 | 必须保留的语义 | 真实消费/禁止混淆 |
|---|---|---|
| C-01/02/03 | Target与ROI身份/修订、原形状/稳定环点/引用、坐标/单位、operand角色、用途和原表示 | PG002/013→020；Difference不重排，布尔新交点不凭最近邻继承旧引用 |
| C-02/03/04 | 目标grid/中心与边界归属、填充/裁剪/邻接、方法/后端/误差政策、原及输出组件/洞/岛、域与来源 | 020→025/030；对象tuple数不等组件数，XLD往返不默认Exact，原/输出hash不同不直接证明几何不同 |
| C-03/04/08 | 几何D、帧存在域、观察V及D−V、全部输出/未完成域、具名位置/面积/拓扑误差 | 原工艺/039保留必检；缺图不改Exclude、背景或0，合法Empty不等失败或工艺通过 |
| C-05/06/07 | 预览/当前代/权限/基线、原提交回查、输入/附件租约、输出复杂度/展开/native预算及真实排空 | UI002只投影；未结束绘制/未应用输入禁止保存试算，不早归还native所用资源 |

两消费者必须用同020能力解释转换；源公开协议的Exact/SemanticProjection或事务证据若未能按其约定接入，就保留不支持/待适配，不删除必要证明再冒称兼容。正式字段、公共签名、系统参数隔离、算法误差与用途资格沿原Owner采纳，缺者只阻断对应转换用途。


## 参考库与AOI快编的原候选采纳项（2026-09-28）

详细机制维护于[034](../shared-modules/packages/PKG-034_ReferenceLibrary.md#reference-library-resolution)与[057A](<../process-guides/guidance/06-domains/DEV-DOM-057A_AOI CAD PnP与Target自动生成开发指导.md#aoi-target-synthesis>)。这里登记精确合同缺口，不新增Schema/Store/Owner；正式枚举/API不可由各会话自行发明。

| 原候选 | 必须采纳的具体语义 | 消费者及阻断范围 |
|---|---|---|
| C-01/02/08 | 料号命名空间/有范围别名、装配变体、拼板/面/位号稳定实例、应装/应不装/未知、BOM/POS排除和必检全集 | 032/034/057A；缺身份/全集只阻相应自动关联/生产发布，不阻已知域工程查看 |
| C-02 | 精确父引用、typed组合/必要子项/变体、继承与显式覆盖/null/删除/恢复/锁定、字段来源和耦合组 | 033/034/035/036同一合同；同值不同来源不能简单去重 |
| C-02/03 | 封装局部坐标/Pin1、针脚与pad关系、来源旋转/镜像、派生ROI依赖和采集适用性 | 007/020及AOI；缺约定拒绝相关映射，不能各写一套底面公式 |
| C-02/04 | 每提案最终匹配处置、检索范围/完整性、生成与试检区别、逐程序原请求/摘要/回执关联 | 034/036/035；库成功不代表程序成功，纯FS-056不产生生产事实 |
| C-02/06/07 | 发布保持/退役与历史引用、跨程序部分Unknown、取消/排空、资源限额/索引水位 | 033/034/041和原权限Owner；水位非锁，查询不到非无引用 |
| C-05 | 逐字段来源编辑、批量固定范围、候选理由/三值、真实完成阶段、生产与工程模式 | 可选034控件/UI012/UI020，页面无额外质量或写库权限 |

旧客户端不能漏掉新必要语义继续提交；兼容策略按原版本合同冻结，不能仅新增可空字段却把空解释成已确认。对账/几何合成可先用批准合成夹具做软件验证，来源数据政策/真实库内容/质量阈值/现场资格各自采纳，不让外部条件替代尚未完成的内部设计。


## 覆盖与扫描规划的原候选采纳项（2026-09-28）

详尽计算在[DEV-MET-034](../shared-modules/guidance/04-metrology/DEV-MET-034_Coverage与Sampling开发指导.md#coverage-sampling-implementation)，有限候选/时序求解在[019](../shared-modules/packages/PKG-019_ScanPlanning.md#scan-candidates-constraints)；下表只列原C归属，不另建Observation/Plan/事实Schema。

| 原候选 | 需要精确采纳的语义 | 消费者/影响 |
|---|---|---|
| C-01/02/08 | 完整义务库存、板面/物理表面/尝试、多角色AND/整组OR、批准N/A、三层采样总体及补抽 | 工艺→018/019，缺全集不能报100%，缺政策只阻相关抽样/发布 |
| C-03 | 度量空间、点/线/面积/表面、稳健支撑/误差集、halo、split许可、保守量化和空域 | 007/020/018/019，图像显示或包围框不作覆盖证明 |
| C-02/04 | 精确计划/候选/观察/Task关联、六阶段来源、单目标/多目标共享、重采选择/作废、逐来源水位/完成屏障；提交前CoverageResult与提交后规则/回执关联分开 | 012采集、013成像质量、038/040及018，NG完整与缺测分开，撤销贡献可重算；不让覆盖内容包含自身未生成回执 |
| C-02/07 | solver版本/参数/实际采纳计划、有限候选范围、可行性/最优性/bound/Gap、量化误差/资源和单deadline | 019与独立验证器，不能只读solver状态或seed |
| C-02/04/06 | 019返回候选/验证，宿主通过035唯一草稿协议保存typed计划内容或保持引用、依赖和报告；CAS/原回执、历史读取/当前适用、运行未执行子图及在途屏障 | 019/035与原设备Owner；不新增PlanStore，不反向依赖035；计划读取不重求解、不授予运动 |
| C-05/07 | P4图层/Gap/时间线/未证最优/八态、只读UI006、启动取消握手/排空与有界回调 | UI012及可选控件，旧页面关闭不取消其他宿主 |

精确字段/错误码/canonical/资源回执由原Owner串行采纳。现有FS019为兼容绑定，不足以覆盖全部019功能；派发卡须逐项绑定相关正文和具体断言。源项目固定三分钟、候选数、签名域或工具类名均不是平台已批准接口。

## 采集与成像质量的原候选采纳项（2026-09-28）

详细执行只维护[012序列指导](../shared-modules/guidance/02-platform/DEV-PLT-015_设备、相机、光源、运动与采集开发指导.md#acquisition-sequence-implementation)和[013质量](../independent-modules/image-quality/DEVELOPMENT-GUIDE.md#image-quality-implementation)。本表登记正式字段/语义缺口，不新增Schema、FrameSet、Metric库或生产状态机。

| 原候选 | 必须采纳的精确差异 | 消费者与影响 |
|---|---|---|
| C-01/02/04 | 观察/曝光/原生照明/投影step分别关联；设备启动代、计数语义、重复/冲突/晚到与封口；显式Motion不适用 | 012/各设备/038；缺定义只阻受影响采集模式，不用假字段满足旧合同 |
| C-03/06/07 | 时间事件/单位/频率/域/同步代、误差界、rolling shutter范围；真实设置来源与证据能力 | 012/007/宿主；同时间值不证明同步，CRC不授身份 |
| C-03/04 | 013逐指标方法/尺度/原量/单位/有效域/计数/归一化及缺失；原图/派生图、可观测/适用/产品判定分开。055A/027补绑定H0/H1/H2、完整曝光/图案组、原生/批准派生/仅显示/未知支持、跨FOV贡献和冲突及逐目标物理面积分母 | OCR/028/018、SPI055B/055C及UI；高位深统计、各mask原因和原单元支持不可省略，不新建FrameSet或状态库 |
| C-01/04/06/07 | 结构封口、质量报告、资源排空正交；只读原帧先于质量，交付里程碑与最终排空可分别观察；一次最终返回须有独立保全资源及Owner，缺口/停止未知保留 | 012/006/013由宿主编排，无消费等待终结、终结等待归还的环路或第二Owner |
| C-02/04/07 | 重拍范围/原子观察组、历史保留/选择、计数/时间/内存预算及未知动作恢复 | 原应用/012/035；不覆盖旧attempt，不按NG无限采样 |
| C-05/07 | 原曝光/帧/指标/时间线联动、三语/八态、旧选择隔离、只读诊断与工程动作分开 | UI014及可选012/013控件，关闭页面不越权停机或提前归还 |

原AOI单一byte格式、必需指标全集、签名handle/canonical和质量到FrameSet V2字段不是本平台已批准合同。保持PKG目录依赖，由宿主连接原公开能力；正式版本兼容、资源保持及生产政策按受影响切片冻结。

## 曝光与照明独立优化的原候选采纳项（2026-09-28）

新增061是工程能力归属，不新增设备/质量/程序Owner。唯一细节见[061](../shared-modules/packages/PKG-061_ImagingOptimization.md)，正式共享合同仍由原Owner串行采纳。

| 原候选 | 需要精确采纳的语义 | 消费者及影响 |
|---|---|---|
| C-01/02/03 | 完整目标×方法×条件；候选整序列/原step身份；有量纲离散值、锁定/量化/耦合与能力修订 | 061、013、036/工艺；不猜五通道或单位换算，不将单步最优拼为完整组 |
| C-02/06/07 | 当前物理包络、跨trial热窗口/预算、工程用途/观察端口、实际配置/独占及退出恢复条件 | 宿主/012/设备Owner；061不直接配置设备，不因超时重发未知动作 |
| C-03/04 | 原指标可观测/缺失/失败、基线与推荐准入区别、Pareto/相等/区间比较、原证据与派生向量 | 013/下游原报告→061；不拿置信/分歧当硬误差界，不造质量总分 |
| C-02/04/07 | 候选与独立trial去重、真实物件/帧关联、搜索与保留集、候选顺序/回应/检查点、预算及失败原因 | 历史/实时观察桥与061；相同图hash不替代采集身份，seed不保证物理可复现 |
| C-02/04/06 | 建议/设备恢复/草稿保存/激活分离；完整参数组补丁、CAS、Unknown查询、当前验证适用与失效范围 | 036/035/工程宿主；工程报告不成为生产事实或自动激活 |
| C-05/07 | 模式/步骤/最差ROI/前沿比较、三语八态、关闭隔离、无设备历史控件与有权试采入口 | UI012/独立试验台，不以选择候选触发设备 |

源AOI私有canonical/签名/文件来源合同、优化store及生成接口不自动迁入；本平台先在原合同明确检查点保存归属和回执后实施，不因借鉴Optuna而新建第二研究/批准数据库。未确定的实际阈值/范围只阻相关实采或推荐，纯有限集合/历史语义仍可先做软件验证。

<a id="mosaic-contract-semantics"></a>
## 多FOV几何、显示及用途的原合同采纳项 — 2026-09-28

| 原候选 | 必须采纳的语义 | 原Owner/消费者与拒绝反例 |
|---|---|---|
| C-01/03 | 源/预期FOV/观察角色/尝试、原域与各种方法域、相容图层、pair方向/参考平面/画布偏移/裁切与LOD | 006/007/016/017；错板/相位拼组、半像素/双校正、自动画布平移漏应用拒绝 |
| C-03/04 | 先验/匹配点及分布、未连通分量、退化/独立验证、用途/Partial和真实缺口、未知covariance | 022/017→018/计量/工艺；不删除最大分量之外源、不以Error均值或0协方差造资格 |
| C-03/05/07 | 虚拟目录、半开tile/实际LOD/halo、多源贡献与原插值支持、显示派生与测量支持 | 017→049/UI002；主来源不等于完整溯源，零分母不当0值有效 |
| C-02/04/06 | 首次无输出的输入计划、几何/辐射/显示版本、原资产保持/草稿CAS及回执、工程Partial保存与生产采用分开 | 宿主/033/035/041；017无第二Store/标定/质量Owner，结果不等待自身回执 |
| C-07 | 稀疏图/内部求解、tile/halo/缓存/CPU-GPU预算、取消准入与原生排空、损坏缓存恢复 | 017/006/049；超时不返池，重试不找latest，显示LOD降低不改变检测义务 |

精确类型/序列化/兼容及参数语义由原Owner串行冻结；模块正文唯一为[IM-023](../independent-modules/mosaic/DEVELOPMENT-GUIDE.md)；[DEV-VIS-029](../shared-modules/guidance/03-vision/DEV-VIS-029_多FOV拼接与全局坐标开发指导.md#mosaic-implementation)只作应用接入与显示研究。本节不批准新生产用途、不改原机判/覆盖/提交协议，不以设计名词创建平行Schema。

<a id="mosaic-multiband-contract-semantics"></a>
### 多源显示内核与分量预算补充

沿原C-03/05/07承接[029 §11.3–11.8](../shared-modules/guidance/03-vision/DEV-VIS-029_多FOV拼接与全局坐标开发指导.md#mosaic-multiband-method)。以下仅补同一合同的语义，不另建多带DTO或融合Owner：

| 交接内容 | 必须区分的事实与接收端 |
|---|---|
| 固定显示方法 | 源/观察层、几何/补偿/采样支持、全局画布相位/核/层数、标签与4邻接分量修订；017→049，同一tile不能临时减层或重求标签 |
| 保护和有效性 | 原U、完整单源保护域/选源及冲突、数值支持C/W/Z分别表示；工艺提供保护意图，017直接取源或返回冲突，不把C/Z变018实采覆盖 |
| 来源及数值输出 | 原值、未量化派生值、最终显示值/裁切标记、精确展开或保守可能贡献及未展开原因；不能以标签源代替带符号的邻域贡献 |
| 总工作与实际资源 | 各tile/分量/参与源/层工作区与累计工作、逻辑读取/物理解码/缓存、中间I/O、同时存活缓冲/在途集合分别计账；单矩形K·A或顺序工作区不能代表全请求成本 |
| 有界退出 | 规划/标签优化/分量计算各阶段、实际评估量、总deadline、取消准入与native排空；已有几何/原图可读不表示显示路线完成，无全局最优证明不写最优 |

方法细节及碎片域反例只在029维护；017/006负责计算与资源，049/UI仅投影，033/035/041保持原保存/回执权威。Profile、正式类型、公开HALCON适配及真实并发仍须逐切片冻结，文档采纳不授予产品资格。

<a id="matching-contract-semantics"></a>
## 定位、对应与备用的原候选采纳项 — 2026-09-28

| 原候选 | 必须采纳的语义 | 消费者与阻断范围 |
|---|---|---|
| C-01/02/03 | 稳定scope/slot/物理特征、required政策、原模型/原点/支持/训练及实际参数、原帧/成像角色与计算/采集attempt区别 | 033/022/钢网/AOI；缺身份/关系不自动关联，不阻合法独立诊断 |
| C-03/04 | 算子参考点域与支撑/halo、原矩阵约定/crop/缩放、原candidate索引/模型关联、抑制/截断及策略完整性 | 006/007/020/022/017；top1或少返回不能证唯一，非法项不洗成空 |
| C-03/04 | 一对一对应/独立物理支撑、变换群/退化/对称等价、逐点/最大残差、独立验证及用途/目标质量 | 022→工艺/计量/018；score不充协方差，缺质量只阻依赖用途 |
| C-02/03/04 | 主备用冻结顺序/闭集、特征到目标方向、整链与单次预算、停止原因及全尝试来源 | 022/036/宿主；终局歧义/未知停，不降门或跨模型比score |
| C-02/04/06 | 父子位姿/ROI失效、相对与绝对关系、历史可读/当前采用、资产保持/草稿CAS/Unknown原回执 | 033/035/原权限Owner；022无第二库/Store，不反向依赖生产实现 |
| C-05/07 | 实例/同handle互斥、多模型租约顺序、native排空/迟到、候选字节/组合与UI八态/语言 | 006/执行宿主/022控件；reentrant不授共享handle并发，UI关闭不早释放 |

正式类型/字段/序列化及状态/Owner由原权威串行采纳；唯一实施正文为[023 §7–14](../shared-modules/guidance/03-vision/DEV-VIS-023_定位、注册与Alignment开发指导.md#matching-implementation)，本节不创建LocalizationStore或新的机判/放行权限。

<a id="matching-validation-evidence-contract"></a>
### 匹配验证证据的用途与当前输入绑定

沿[023 §9.3.1](../shared-modules/guidance/03-vision/DEV-VIS-023_定位、注册与Alignment开发指导.md#matching-validation-evidence-kinds)，C-02/03/04/05分别承接模型/方法跨样本评价、本次位姿复核、选解规则与原用途决定；不是再加一个同名“验证已通过”状态或新质量Store。类型与字段仍由原合同Owner采纳。

模型评价绑定模型/方法/训练调参/划分及范围；本次复核绑定实体/采集组、帧/修订/坐标链、完整search/解释、预先冻结的未拟合目标身份/名义及实际观测、逐解释预测/残差/支持和规则。两类报告不能仅凭相同模型hash互换。复核参与消歧时保留使用关系，不能继续计作未参与选择的独立盲测。来源/模型/候选/选择/规则改变时，原依赖关系决定失效与新请求，保存Unknown仍查询原身份/载荷。

跨样本通过不能排除本帧E2；当前复核缺失/异源/过期、未完成规则或仍歧义时，依赖该证据的用途保持阻断。无此必需性的其它获批Profile不被本澄清撤销。UI显示各自事实并发原宿主采用请求，033的技术保存与023的复核报告都不产生新的生产批准权。

<a id="matching-variants-contract-semantics"></a>
### scaled、aniso、planar与local方法变体的原合同补充

方法唯一在[023](../shared-modules/guidance/03-vision/DEV-VIS-023_定位、注册与Alignment开发指导.md#matching-variants-method)。原C-02/03/04/07须先区分模型资产实际能力、训练参数请求/实际可查询值、搜索策略及获准用途，再编排公共操作；被调用函数名不能提升普通模型资产的能力。

| 原语义组 | 必须保留及拒绝的歧义 |
|---|---|
| 变换类别与结果形状 | scaled相似、aniso模板轴双尺度子集、planar每候选完整投影矩阵、local绝对取样场/可选整形及轮廓分别适配；不把aniso叫任意仿射，不给local捏造单一Angle/Scale/HomMat2D |
| 原点/图像链 | 训练domain重心、相对原点偏移、训练框/裁图/缩放、原生矩阵约定及007中心桥；模型原点不等外接框中心，搜索crop只加一次 |
| 场与实际支持 | 整形grid→搜索图取样方向、源图尺寸/索引、插值所需邻域、扩边与有效mask；不把绝对场当位移或负场当逆，真实local非零原点/扩边索引未核前不冻结其生产映射 |
| 几何与工艺用途 | 允许自由度、投影使用域/无穷远、条件数、局部场插值/折叠/全域单射与逆用途资格；低残差或采样正Jacobian不等全域可逆，原偏位/尺寸/极性不由整形覆写 |
| 模型及资源 | 同实例执行租约、setter/clear互斥、各变体实际取消能力、真实排空、结果类型/数目/场字节及总deadline；不能从shape超时声明外推所有变体 |

007仍管坐标表达，022管训练/搜索及受限资格，020管几何支持，033管封存内容引用，工艺Owner决定缺陷和用途。正式字段、类型/序列化仍沿原C采纳，未确认的公共API不写猜测签名；UI只显示这些既有结果和原回执。

<a id="matching-local-topology-contract-semantics"></a>
### 声明局部场、全域检查与逆查询的原合同补充

唯一方法是[023 LF-PL-AC-1](../shared-modules/guidance/03-vision/DEV-VIS-023_定位、注册与Alignment开发指导.md#matching-local-topology-method)。保持C-02/03/04/07原权威，不把研究标识直接当生产枚举或生成第二场Schema。

| 原语义组 | 需采纳的明确内容 |
|---|---|
| 场/方法/支持 | 原始绝对取样内容及精度、grid与源frame链、D_req/整cell闭域D/洞/组件、源灰度核及实际邻域支持、固定顶点/片ID和连续扩展修订；三层语义不能混为一项插值 |
| 资格与未完成 | 逐片定向/数值条件、全片对闭交集范围/方法、数值策略/位长和完成范围、几何嵌入/图像支持/误差/工艺用途分别表示；不能将空结果、数值未决或预算未完成编码成合格 |
| 逆与ROI | 查询方向/域/来源、完整候选和原公共face归并、唯一原像/无根/多根/未决、边界单侧J、ROI跨片与完整缺口；位置唯一不表示导数唯一，近似不标Exact |
| 资源与回执 | 原场与索引/派生几何租约、全域快照发布、节点/候选对/源支持/输出片/总I/O预算、真实排空和晚到修订检查；分块不能遗漏远片相交 |

022编排、020几何关系与切片、007受限变换、006/038资源仍各守原责任；跨包用原合同，不引入反向实现依赖。FPC夹持/偏贴与钢网原孔位/尺寸仍是原工艺事实，声明场的数学资格不授予毫米精度或质量放行。


<a id="model-assets-contract-semantics"></a>
## 技术模型资产及原治理接入 — 2026-09-28

| 原候选 | 必须采纳语义 | 原Owner/消费者 |
|---|---|---|
| C-01/02 | 命名域/稳定ID/revision/核心摘要、内容角色/逻辑路径/长度/hash、运行/来源/验证依赖、精确ref及alias冻结 | 033/034/035；不可变绑定，名称/别名非身份 |
| C-02/03/04 | 生产者格式/输入输出/参数语义、真实读写及转换来源；内容先封存、报告后引用避免hash环 | 022/024/015/052/053等原Owner；033不训练/发质量批准 |
| C-02/04/06 | 操作摘要/CAS/逐项原子范围、持久保持/原回执/Unknown，用途决定/撤回/离线边界与在途来源 | 033/041/035及原授权/质量；无第二状态机或生产Store |
| C-03/07 | 外部文件/区间/递归依赖、路径/链接/碰撞/资源预算、物化闭包与受控格式验证 | 033技术校验与实际生产者；缺依赖/预算不足不伪完整 |
| C-01/07 | 内容读租约、持久保持、native租约分离；并发加载/等待者取消/旧代排空 | 041/033/实际适配；generation变化不授早释放 |
| C-05/06/07 | 版本/依赖/资格分层显示、导出角色权限、影响索引水位、旧响应/关闭与三语八态 | 033可选控件/UI002；模型可读不授训练图权限或生产采用 |

平台正式字段、状态与生命周期仍由原Schema/Owner采纳；模块自身实现唯一为[IM-014指导](../independent-modules/model-assets/DEVELOPMENT-GUIDE.md)，[033](../shared-modules/packages/PKG-033_ModelAssets.md#model-assets-implementation)只保留应用映射。模块新资产JCS投影、集合/顺序语义、预算和旧身份隔离已在IM-014 §4/9/附录A冻结；平台Schema/Owner、真实Store/Authority/格式映射仍待对应Owner接收。不复制源AOI两套生命周期，不将AsunImage/DevExpress依赖核验纳入准入。

<a id="model-assets-canonical-contract-semantics"></a>
### 技术摘要范围、规则版本与同内容读回

[IM-014唯一方法](../independent-modules/model-assets/DEVELOPMENT-GUIDE.md#9-新资产-jcs旧资产原规则与版本迁移)细化原C-01/02/03/04/06/07的模块消费边界，不建立新通用Schema。新模型资产技术核心摘要使用RFC8785 JCS `model-core-jcs-v1`；旧Manifest、Security JSON/Proto不转换为JCS，继续使用创建时规则和身份。C-01～C-08中的平台字段/Schema、Owner与持久状态仍待原合同采纳；不得借平台字段未冻结改写模块投影，也不得用新规则验旧hash后误报损坏或原地升级身份。

| 必须冻结的语义 | 原Owner/约束 |
|---|---|
| 原文件与技术预像 | 原字节长度/hash、摘要域与算法/投影版本、实际影响解释的语义与精确角色/依赖；033只接受冻结投影，业务ID/修订绑定不被blob去重合并 |
| 入口与集合/顺序 | 解码后递归重复、未知字段、Unicode/路径/碰撞、数字/时间/空值；逐数组是集合还是顺序及唯一键。字符表/通道/预处理链不排序，不能把默认STJ或JS整数键枚举当JCS |
| 请求与已知实际信息 | 原请求显式/auto、取得阶段/公共查询来源、未采集/不支持/失败/取消分别表达；报告后新知不追写已封存核心 |
| 无环报告与精确读回 | 核心→文件/固定依赖；报告→同核心/样本/方法/执行配置；聚合→核心/报告。033/041保持下新实例真实读取及具名功能结果，不能以普通文件/原缓存重开冒充 |
| 恢复、旧资产与资源 | 原操作摘要/CAS/Unknown、私有物化与真实排空、旧规则解析/未知协议历史可读范围、新修订迁移/原引用保持；不新增033业务批准或停机权 |

Matching/OCR实际查询和序列化归各生产者，052实际执行、053训练/评估/用途分别保持原Owner；IM-014/存储负责技术内容与保持，035负责程序采用。模块投影和预算已冻结；平台接线、真实格式schema/参数集、原旧verifier与运行资格仍按真实资产由原Owner接收和验证。

## 受控推理执行的合同采纳项（2026-09-28）

模块技术语义唯一在[IM-047](../independent-modules/ai-inference/DEVELOPMENT-GUIDE.md)，[052](../shared-modules/packages/PKG-052_Inference.md#inference-execution)只作应用映射；继续使用C-01～07，不增加推理专用第二Schema/状态机。下列字段语义需原Owner采纳为正式签名/类型，当前不是可自行造DTO的授权。

| 候选 | 必须绑定的内容 | 交接/不变量 |
|---|---|---|
| C-01/02/04 | 原operation/attempt、itemId/ordinal/目标/物理观察、用途/当前资格、模型与实际后端/配置 | 宿主/033/053→052；图hash非物理观察，候选bool不授生产权 |
| C-03/07 | 原帧/张量/上游证据分别绑定，dtype/layout/stride/有效域、通道/归一化/裁剪/像素约定/反变换 | 006/007及预处理适配；hash不强令相等，pool尾部不入有效内容 |
| C-03/04 | 兼容组批清单、输出种类/shape/类表、tile/offset/完整性/截断、拒识与合法零候选 | 052→工艺；缺项不左移，关联不可信不猜，空框非PASS |
| C-01/06/07 | 队列/字节/设备预算、deadline、取消域、实例/等待者/真实native排空及generation | 038/052；取消不跨batch误杀，不用新代清旧租约 |
| C-04/06 | 当前读取/提交/取消权限、原回执Unknown/重算、新方法回退、内容保持 | 原Owner/040/041；查询不重推理，取消不推翻已持久成功 |
| C-05/07 | 逐item诊断、测量Scope/Unknown、原两侧比较、UI八态/三语/键盘 | UI014与工程宿主；未测资源不填0，解释不成为事实 |

<a id="statistics-contract-semantics"></a>
## SPC输入、基线与结果投影的原合同采纳项 — 2026-09-28

模块公开 API、固定路线、生命周期与准备结论唯一见 [IM-043 statistics](../independent-modules/statistics/DEVELOPMENT-GUIDE.md)；SPC 公式、常数和适用性引用 [DEV-DOM-058A §2–7](<../shared-modules/guidance/06-domains/DEV-DOM-058A_QualityControl SPC与分母定义开发指导.md#spc-core>)。计量实验的数值消费沿下方033/055接收节，不将实验因素解释为SPC子组。本表只采纳产品序列化/事实映射，不定义第二套指标 Schema、状态或 Store；未采纳产品字段不阻断无关 Core 规格准备。

| 原候选 | 原Owner必须采纳的语义 | 消费者与限制 |
|---|---|---|
| C-01/04/08 | 观察单位/目标成员、去重依据、首检/复测选择、源事实及更正关系；固定截点范围与批次封口分别证明 | 工艺/质量Owner→042→045；同板多缺陷不增加板数，已读完查询不代表批次收齐 |
| C-02/03/04 | 指标/方法修订、单位/规格、合理子组及缺口、Phase I基线候选和Phase II生效版本、规则/常数来源、方法资格 | 原质量方法Owner→045；统计定义不强制包成AOI生产程序，候选基线不自动生效 |
| C-04/07 | 查询/输入闭包、统计计算/结果与原持久回执关系；完整性、指标适用性和源质量各自表达；有界读取与恢复 | 042/045/原持久Owner；纯计算不假造生产Commit，结果Unknown先查原操作，不盲重算 |
| C-04/05/06 | 统计→图表/报告的范围/来源绑定、当前读取用途、显示选择与新计算意图区分 | 045→UI008/046；图表抽稀/隐藏行不改变分母，单件无统计报告不依赖045 |
| C-05/07 | 请求代次、取消/实际排空、分组/排序/窗口/图点预算及三语资格/缺口原因 | IM-043无自身UI；UI008等宿主消费结果。旧响应不盖新图，宿主关闭不隐式终止其它消费者 |

正式字段/签名/序列化和具体批准政策由对应原Owner串行冻结；方法能力缺口和真实Profile分开记录。该表没有批准自动工艺调参、质量放行或新的设备副作用。


<a id="drill-microvia-method-contracts"></a>
## 钻孔/微孔的被测量与关联语义采纳 — 2026-09-28

工艺算法在PG-002/003、函数调用在FS-023/024/025/031维护；本节只列原合同缺口，不新增孔/层栈Schema或生产Owner。

| 原候选 | 必须正式绑定的语义 | 消费边界 |
|---|---|---|
| C-01/02 | 板/拼板/面/层对/制造阶段、物理观察及重复FOV关系、冻结设计目标全集、方法/程序快照 | PG只解释当前工序；同XY不同层/阶段不合并，hash相同不证明同物理孔 |
| C-03/04 | 原坐标链和独立基准、分量frame、量测定义/方向、实际有效/支持/遮挡域、原/拟合轮廓及采样索引 | 原007/几何/计量Owner供能力；径向偏距不自动成为图纸位置度，拟合RMS不等于圆度/位置不确定度 |
| C-03/04/07 | 完整候选集/关联分量、方法对应几何、映射/未配对/歧义见证、搜索未完成、节点/字节/deadline上限 | PG002关联策略；关联门不是合格公差，唯一数值解不证明物理身份，超预算不截断后报唯一 |
| C-03/04 | 孔口/孔底/侧壁的实际模态和可见域、参考平面/底部支持、方向及定义、逐量值适用性和不确定度依据 | PG003消费027/029/032；2D轮廓及层厚不能补深度，参考无效只阻依赖量 |
| C-04/05/07 | 每目标每功能的Required/实际支撑/缺口、存在信号与原因判别、原量值/候选→039评价→040提交关系 | UI015/016只投影；无开口信号与确定缺孔分开，模型失败不自动等于不存在，取消/Unknown沿原操作恢复 |

关联目标函数/歧义带、被测量资格、工艺公差及真实Profile仍是待采纳内容。字段不足按原合同Owner处理，不据此让实现会话各造相似事件或换用未登记状态。


<a id="assignment-contract-semantics"></a>
## 固定图求解与两工艺页面的原合同采纳

纯计算实施的唯一权威为[IM-037 assignment 指导](../independent-modules/assignment/DEVELOPMENT-GUIDE.md)，[PKG-062](../shared-modules/packages/PKG-062_Assignment.md#assignment-implementation)仅维护产品接入映射。模块自身的公开契约、精确费用、算法与证明状态由该唯一指导冻结；原C-03/04/07另行采纳产品左右键/边引用、序列化及事实映射，不创建第二套Core DTO，也不阻断无关Core。PG负责原边证据/方法几何、物理排他、费用及分量级歧义政策；037/048不被替换，022联合位姿不变成固定cost问题。模块无生产Owner或持久Store，图内证明不等于物理资格或质量放行。

C-05继续绑定UI015钻孔和UI016微孔投影：同一竞争分量/主替代边、原/拟合/剔除边界、逐功能义务与支持/缺口；微孔另含层对/阶段/孔口孔底/侧壁、R/V/A与定义域、板法向/设备轴深度、端点锥角/实际壁面区别。页面不拖动历史对应、不改原mask、不因缺3D把必需项改未配置；原操作Unknown先查询，输入改变才是新工程意图。正式端口/类型仍由原Owner串行接收。

062数值与停止的产品接收：保留模块返回的精确费用尺度、已完成K/C/替代证明阶段、实际停止原因和方法修订，不以显示舍入改变δ判断；取消不抹去已完成证明，也不提升未完成阶段。具体数值、全图势和固定残量环设计唯一见[assignment §4](../independent-modules/assignment/DEVELOPMENT-GUIDE.md#4-处理流程与算法约束)，本候选映射不重复规定求解公式或另建Schema。


<a id="mask-avi-contract-semantics"></a>
## 阻焊三态/有向几何与终检精确汇合的采纳点

唯一技术正文在[PG-006 §16](../process-guides/processes/PG-006_soldermask-legend.md#mask-method-implementation)、[025](../shared-modules/packages/PKG-025_Segmentation.md)及[PG-011 §12/14](../process-guides/processes/PG-011_final-avi.md#avi-exact-side-join)。本节只将语义送回原C-01～08，不新增DTO/Schema/Store/状态机或写入者。

| 原合同 | 本次需要绑定的语义 | 不能推断的替代 |
|---|---|---|
| C-01/02 | 板/单元/面/阶段与物理采集、计算、评价修订；阻焊合法开窗组/桥意图、材料方法；终检原义务库存与明确分面输入闭包/后继关系 | 同条码最近结果、相同UI选中、latest或最高分不能决定实体/配对；未配置选配与必需缺能力分开 |
| C-03 | W/输出域/halo、M/N/Q及逐功能支持；原边/处理边与单位、有向截线/对应/有限范围/重合；平移秩/残差、桥拓扑/宽度；翘曲表面/支撑/参考/法向/有效采样 | 原生对象不泄漏；空哨兵不是负余量，8邻接不是有限宽度，LS/TLS样本PV不是最小区域或行业弓曲率 |
| C-04/07 | 原始/派生分割与组件映射、完整或预算截断、原几何/候选/未知；来源封口、精确汇合修订、撤销生效范围及原提交接受栅栏/回执 | 事件已到不是全部事实已封口；提交完整不等于功能可评价；本地check-then-write不证明跨服务撤销原子性 |
| C-05 | 原结果/草稿与来源身份分开；材料三态、面积界、原有向量/拟合、桥证据、双面修订/义务/翘曲条件、原回执读权限 | UI不重算量值/配对/Required，不在证据弹窗换源而保留旧标题；所有权未知不强行“重试通过” |
| C-06/08 | 分割系统参数的实际作用域/并发约束、资源预算与停止排空；双面重测兼容、质量撤销/纠正和044的独立领取事务 | 算法仅返ReviewCandidate，不创建ReviewClaim；新评价不掩盖旧提交Unknown，不重发历史出板动作 |

正式字段/公差/接受策略仍由原Owner采纳；本轮不以改文档宣称接口冻结。可继续纯计算设计、独立数学/界面实验和已明确的无设备切片，受影响生产接受协议未明确前不授予生产写入资格。

圆形开窗补充沿C-03/C-04/C-05采纳[PG006 §16.4.1](../process-guides/processes/PG-006_soldermask-legend.md#mask-circle-opening)：名义/实际模型圆及焊盘角色、独立frame、圆形/关联资格、中心偏移/半径变化/模型圆盘包含余量和原边有符号残差须分别映射。模型圆不得替代原边侵占/未知；单圆没有可辨旋转角。与直线法向模型、原交点量测复用021/030既有端口语义，不新增阻焊拟合Schema或公共事实Owner。

终检C-04/C-07沿[PG011 §12.4](../process-guides/processes/PG-011_final-avi.md#avi-exact-side-join)区分动态收集投影与冻结评价：缺b1的e1/c1既已冻结，原b1到达只能产生关联后继评价/计算，不修改原输入，也不新增虚假的物理采集。聚合等待截止/取消与分面来源封口/native排空是不同回执，允许不完整终态的原政策须明确；该聚合回执不能替代038来源停止证明。撤销接受栅栏仍是原Owner可自主推进的内部合同工作，不把未定跨服务协议统一标成等待客户。


<a id="stencil-method-contracts"></a>
## 钢网观察、前后比较与维护建议的原合同采纳

唯一方法正文在[PG-013](../process-guides/processes/PG-013_stencil.md)、FS-039～042和[FS-043 §28](../process-guides/guidance/12-function-specs/FS-043_Maintenance_advice.md#stencil-maintenance-comparison)；本节只登记原C的语义缺口，不新增钢网通用Schema、状态机、存储或生产Owner。

|原合同|必须精确绑定的语义|边界|
|---|---|---|
|C-01/02|钢网/开口/父子关系/制造修订、参考用途、清洗事件与前后物理尝试、冻结必检域及独立基准|PCB焊盘不替代加工意图；清洗后不自动变程序修订；同图重算不变独立周期|
|C-03/04|实际投影或指定表面/截面定义、通光/非通光/未知、支撑/面积、原边/拟合边、全局位移/局部搜索、原完整关联图及几何方法|透射轮廓不自动成为上下表面轮廓，拟合残差不消除原缺陷；非通光不直接证明污染原因|
|C-03/04/07|厚度所需双表面及有向同位置关系、台阶基准、实际壁面支持/截面/锥度或局部缺口、逐量测资格与未测域|单面高度不是网厚；两孔口差不是壁面粗糙度；2D有效不补3D必检缺口|
|C-04/05/07|前后精确配对/可比政策、原D与共同已知K、具名差量及未知界、来源/规则/趋势范围与独立观察单位|K不替换整孔分母；未知界不等统计置信区间；UI不重算配对/几何/改善或寿命|
|C-04/06/08|每条规则的充分性/命中/冲突、提案计算与原保存身份、当前资格接受栅栏、人工批准/实际维护/复检/质量处置关系|历史不足只阻断需要历史的规则；批准不是设备执行；原Unknown先查，不用重算换键清除|

正式类型、序列化、原端口签名、许可与撤销接受协议由对应Owner串行冻结；这部分是可继续推进的内部设计工作。真实方法可比资格、量测/清洁度门限、工艺维护政策与样本按用途分别提供，不能把所有未决项转成等待客户。页面及HTML只消费原投影，不授予清洗或质量放行权限。


<a id="dispense-coating-method-contracts"></a>
## 点胶/涂覆方法的原合同采纳

方法正文唯一在[030积分](../shared-modules/guidance/04-metrology/DEV-MET-031_通用计量引擎开发指导.md#supported-numerical-integral)、[PG016](../process-guides/processes/PG-016_dispense.md#dispense-method-implementation)和[PG021](../process-guides/processes/PG-021_coating.md#coating-method-implementation)。以下回到C-01～08，不创建新FS/DTO/Store、膜厚Owner或万能胶对象。

|原候选|需正式采纳的语义|真实链与禁止路径|
|---|---|---|
|C-01/02|独立基准、物理表面/阶段/观察、点/边/结点意图/锚区、材料时窗、C/K/T/I、必需功能/观察角色及冻结原输入|PG/035/037；同XY、同hash、同条码不能替代原物理身份，快编候选不成制造意图|
|C-03/04|方法先形成的候选几何、062固定完整图/δ/替代；有限截面全部段/对应/法向/有效区间|021/022/025/030/062→PG016；尺寸NG不先筛掉，歧义/预算未完成不造唯一|
|C-03/04/07|D/E/U与面积度量、原单元/插值支撑、共同分片、裁切/正负定义、条件界和实际未完成范围|027/029/020/030/018；有效点不等有效单元，绝对值不等signed，部分量不扩大成总体积|
|C-03/04|同表面各视角的正/反支持与冲突来源、融合政策和闭包；真实表面面积、膜厚层/测线/原对应/采样支持|025/007/027/030→PG021；分块融合不丢反证据，UV不填厚度域，多帧不重复面积|
|C-04/05/06|原计算/保存/提交身份、草稿修订不复用、晚到后继关系、固定范围回执查询与当前允许新写分开|035/038/039/040及UI022/023；换选择/状态不丢原Unknown，查询不重采/调胶/重喷|
|C-07/08|关联边/相交对/片数/native字节/期限、完成域和取消排空；材料/数值/工业资格及逐功能完整性|原Owner/Qualification；资源截断不删义务，条件区间判规则不代表全项完整|

保守多视角融合仍是待原方法Owner采纳的明确设计候选，不能因本表写出公式就宣布生产默认获批；正式签名、数值Profile和接受协议继续按原合同流程串行冻结。


<a id="pin-tht-method-contracts"></a>
## 插件/压接与THT焊后方法的原合同接收

方法唯一在[PG019 §16](../process-guides/processes/PG-019_insertion.md#pin-method-implementation)、[PG020 §16](../process-guides/processes/PG-020_wave-solder.md#tht-method-implementation)及公共031/025/062。以下是原C-01～08的字段语义采纳位置，未新增Schema、针脚通用对象、独立事实库或质量Owner。

|原合同|需精确绑定的语义|消费者/不得推断的替代|
|---|---|---|
|C-01/02|稳定针图/父子臂/空位/组/设计邻接、板壳双坐标、图纸量定义/指定截面、焊后阶段/针孔盘和许可来源、冻结必检|PG019/020、035/037；显示镜像不重编号，net不自动授权连焊，前工序不填当前遮挡|
|C-03/04|已资格化物理候选与完整固定一对一图、费用方法/近等价、范围完整性和未匹配/歧义；多目标材料组件及原接界另立关系|062只解针/孔映射；材料组件不强制一对一，重复克隆不能代替真实关系|
|C-03/04|独立参考、端/轴/面角色、方向/单位、有限观察支持和模型外推资格、指定h、端离轴残差、逐项未知、固定组分母|029/030→PG；单面PCA/extent不是中心/针端，子集极差不充全组共面度|
|C-03/04/07|材料F/B/U及原/派生支持、局部W与固定锚区、已知/可能空间邻边、下/上图资格、路径/切断见证及涉及目标集合|025/原几何合同→PG020；2D投影/closing/补洞不证明真实材料连续；一物多关系不能重复计物体|
|C-04/05|针端/锡峰/接界分别的来源、可见局部积分D/E/U与定义；只读显示、草稿编辑、AI候选和原事实分离|UI024/025只消费投影；上下界面缺失不造体积/裸针长，视觉不出电性/孔内填充事实|
|C-06/07/08|原提交/返修新尝试、外部力/电事件关联及Unknown恢复；候选/边/局部图/面片/native预算与真实排空|原应用/038/040/048；ACK不代表压接执行，回执丢失不重压/重焊；预算不足不删针/细桥或义务|

空间邻边与锚区不确定性、精确参数/方法资格和正式端口仍需原Owner冻结；不能由页面示意字段生成DTO。已明确的2D/有限模型可继续无设备设计验证，真正依赖光学/客户图纸/材料门限的资格单独保留。保存工程未决与生产发布/激活分开，不把图论反例通过变成生产许可。


<a id="spi-feedback-contracts"></a>
## SPI反馈对原合同的接收范围

[055D §1–9](<../process-guides/guidance/06-domains/DEV-DOM-055D_SPI Rule SPC与Printer Feedback开发指导.md#spi-feedback-implementation>)和FS055规定本切片语义，不创建新Feedback事实库/状态机。C-01绑定印刷事务/检测尝试/拼板/面/轨道及设备实例；C-02绑定建议方法、设备参数单位/作用方向/绝对或增量、耦合组、基准值/版本、有效期和能力。C-03/04保留原量测/统计输入与资格、候选偏移及转换来源，不把上游图像句柄传入交付服务。C-05投影保存提案、授权请求、原命令查询、应用证据和后效，按钮不能成为权限Owner。

C-06/07/08须分别承接出站意图/固定负载/业务身份、交付尝试/租约、远端业务响应/逐项应用证据、可回查/幂等/执行条件、印刷实际使用版本或合格生效边界及后效总体/修订。无ACK是未知，不等拒绝；配方接收不等激活；部分应用不等整组成功；效果改善不等因果或质量放行。精确Schema/命令Owner、远端能力与质量政策继续按GATE-001采纳，不由CFX字段或页面显示词决定。缺远端CAS不能伪造同等保证，缺回查/幂等只阻断相关动作，可继续离线Advice/模拟恢复设计。


<a id="spi-reference-metrology-contracts"></a>
## SPI目标、参考及量测对原合同的接收范围

唯一方法分别在[055B](<../process-guides/guidance/06-domains/DEV-DOM-055B_SPI Reference Plane与Pad_Stencils Target开发指导.md#spi-reference-target-implementation>)、[055C](<../process-guides/guidance/06-domains/DEV-DOM-055C_SPI Paste Segmentation与Metrology开发指导.md#spi-paste-method>)。C-01/02保持来源pad/开口父子/沉积组及明确印刷意图、运行实体/尝试和方法修订的分离；DNP不自动排除。C-03绑定物理材料基底/台阶、独立seed/check、原高度与参考实际支持、法向/单位/坐标、局部/模型预测用途，材料与高度未知分别保留。参考值不因算法返回低残差就获资格。

C-03/04/07需承接原F/B/U与形态增删、材料多对多关系/合格一对一子问题、固定局部桥W/锚及已知/可能边；材料窗口的已证无膏零贡献与几何高度积分分开，具名E/U和误差域不得互换。量测保留面积比/覆盖/外溢、具名高度统计权重、signed/plus/minus与材料量、原分母、完整/部分/条件界、面积/体积中心定义及退化。公共030已在[031 §10](../shared-modules/guidance/04-metrology/DEV-MET-031_通用计量引擎开发指导.md#supported-moments-centers)接收混合/二阶矩的方法设计；精确API和原C仍待正式采纳，不在SPI复制数学引擎。

C-03固定度量是连续材料面积、像素面积单元还是离散点质量，保持坐标架/面积元/原分片、孔洞/未知、材料E_F/B与几何E_geom、局部原点、矩归一/单位及正部零交线来源。C-04分别表达完整/部分中心、中心无定义、面积矩有效但主方向不可辨、模π轴及等效椭圆的具名性质；无中心不写(0,0)，无方向不写0°，signed矩不当物理质心。C-07承接稳定累计计划、分片/交点/两遍存取预算、误差/近零门、实际已完成域及native排空。SPI 055C与PG016是同一030的两个无UI消费者：产品决定中心方法及其关联/规则影响，030不调关联、不提交事实、不加载面积请求不需要的高度资源。

连续面积高度分位沿[031 §11](../shared-modules/guidance/04-metrology/DEV-MET-031_通用计量引擎开发指导.md#continuous-area-height-quantiles)接同一C-03/04/07：固定投影面积度量、方向/参考、E/F/U_h/U_s与B排除、原分片仿射模型、p及左逆/0与1端点、常值原子和事件、部分/全域/条件包络性质、未知质量及高程界的来源。数值包络与未知域条件界、统计置信区间分开；误差重叠的CDF比较、平台及相邻浮点数不能靠任意epsilon判成功，单次归约未完成不能以部分和比较全分母。035绑定方法修订，030返回具名计算，055C/PG016选域/规则；不扩为一般曲面或长度分位，不生成私有量测Schema。

C-05/06/08绑定原历史/草稿、B/L/R耦合差异、方法/来源失效、试算发起快照、资源预算/取消排空及提交恢复。UI018/019只投影，固定分类/域的解析关系不自动延伸到材料重分类后的误差。纯计算与已提交事实不混用状态，源更正走新评价/修订，历史原值不覆盖。上述仍是字段语义候选，正式签名、方法/材料资格、数值Profile和物理样本按原Owner采纳。

### 参考拟合与有限曲面消费的原合同补充

[028参考方法](../shared-modules/guidance/03-vision/DEV-VIS-028_3D对象模型、配准与表面分析开发指导.md#reference-surface-method)与[031二阶signed积分](../shared-modules/guidance/04-metrology/DEV-MET-031_通用计量引擎开发指导.md#quadratic-reference-signed-integral)继续使用原C-03/04/07，不新增统一曲面对象或生产Owner。

- 输入分别承载原Surface/真实有效支持/坐标单位、物理基底来源、R0/X/T/C、方法P/H/Q及冻结参数、方向与逐目标预测许可。P正交目标和H/Q轴向回归目标不可只用同一个“plane”标识混合。
- 结果分别承载原候选R、实际refit I、最终门内J、未参与选择的独立C及原索引/残差；有限候选预算、候选实际顺序、物理多基底歧义和数值tie含义保持。HALCON第四系数到平台d的转换必须有明确约定，不靠同号复制。
- Q保存六项基底、中心/正尺度、系数、求解/秩条件、预测域与误差来源；参数能重建模型不等隐藏基底已实测。现有031层的通用primitive/原索引能力与029拟合编排保持单Owner，不在产品复制。
- 030请求同时冻结测量方向、相应投影面积元、上下场模型、定量/有效/未知域及被积量；Z差与法向面积不能混乘。[二阶有界归约](../shared-modules/guidance/04-metrology/DEV-MET-031_通用计量引擎开发指导.md#quadratic-reference-bounded-reduction)承载正负/CDF/同域分位的上下界、原子/端点约定、内部及输出精度、实际工作/预算停止、完整或部分范围；存储模型数值证书与物理误差分开。全部根初始化及父片替换前保留旧界，未达精度不变完整数值/0/工艺NG。signed结果不赋予材料、正部中心或条件分位资格；SPI FS045主/备仍为同物理参考plane。
- 取消/超时、真实native退出、租约归还及晚到隔离分别承载；有缓存模型仍逐目标核适用域。Profile/物理材料/实际公开桥未冻结只阻依赖部分，不能由本段补造生产字段或默认值。

<a id="qualification-contract-semantics"></a>
## 公共计量实验与资格的原合同采纳

唯一方法正文是[033 §6–14](<../shared-modules/guidance/04-metrology/DEV-MET-033_MSA、GR&R与计量资格开发指导.md#metrology-qualification-method>)，独立能力边界在[055 §8](../shared-modules/packages/PKG-055_Qualification.md#metrology-qualification-integration)，共享数值操作在[IM-043 §7.1.3.1–3](../independent-modules/statistics/DEVELOPMENT-GUIDE.md#qualification-numerical-operations)。以下是原C内待采纳的输入/输出语义，不定义第二实验Schema、统计库或QualificationStore。

| 原候选 | 必须绑定的请求/返回内容 | 原Owner与失败边界 |
|---|---|---|
| C-01/02/08 | 实验/物理件/板/印刷状态、目标、观察/采集/重放、卸装/操作者/日期/机台、计划格与完成/失败/排除；随机/固定水平和总体 | 053/原观察Owner供冻结记录，055校验模型可识别性；不同Pad/重印不充同件重复，复制同帧不增光学独立n |
| C-02/03 | 量名/单次或平均/支持域/单位/坐标、方法/标定/原参考证书精确版本及hash、材料/量程/环境、参考赋值与相关组 | 030/031供原量测，原计量Owner定用途；参考失效可用于历史解释，不授新用途；缺参考仍可有受限散布描述，不能给溯源偏差 |
| C-02/03/04 | 既有四参数键及模型/交互/负分量策略、行/格计数、具名SS/df、原与边界估计、残差/秩、标准不确定度/协方差/贡献、覆盖方法及未验证原因 | 045返回数值、055解释实验；不预设每条路线有置信界，局部小计不能叫完整预算，估计量变更形成新方法/计算身份 |
| C-04/06 | 原参考证书、评估报告和资格决定的独立身份/内容/关系；用途批准、签发/撤销的原权限、发布时刻与适用起点及受影响范围 | 纯FS018只返回，宿主沿040/041保存证据，原计量Owner审定；055不签发、停机或改旧事实，提交Unknown查原回执 |
| C-05/07 | 试验格/失败定位、原/边界估计并列、绝对量与比例分母、数值/适用/批准各状态、请求代次及取消；N/组数/p/协方差规模和读取/返回预算 | 原UI006/可选控件只投影；部分诊断不能作为完整资格，语言/取消跨实例隔离，QR/矩阵验证成本另计 |

补充接收点：

- C-02/03/04沿[IM-043 §7.1.3.3–4](../independent-modules/statistics/DEVELOPMENT-GUIDE.md#qualification-numerical-backend)绑定设计缩放/秩/残差/PSD误差政策、分布请求域/端点/不收敛诊断及实际数值方法/provider身份；不向公共合同泄漏第三方矩阵对象。缺阈值可给原谱/诊断，不能给合格布尔值；Beta无公开收敛状态不能伪造字段。取消响应与真实计算结束/资源归还分开。
- 同一C-02/03/04/07沿[IM-043 §7.1.3.5–6](../independent-modules/statistics/DEVELOPMENT-GUIDE.md#qualification-tail-distribution-method)明确分位/尾概率、原Lower/Upper、原概率/观测数值表示、F分子/分母df顺序、方法/Policy/支持域/实际构建身份。原始α/2直交Upper，不能把先算近1概率丢失的尾信息当恢复成功；内部变量范围、最终表示范围、数学端点和有限观测的大尾舍入分别可追溯。无公开迭代次数/根证书不伪造Converged；候选字段先由原Owner正式采纳，不能把第三方C++类型、ABI异常或模板Policy泄漏给055。
- 上述操作的C-06/07资源语义按[IM-043固定运行限制](../independent-modules/statistics/DEVELOPMENT-GUIDE.md#qualification-tail-runtime-evidence)区分等待截止、实际结束和可否内部取消；root/series设置不冒充请求总工作上界，裸无异常/数值0不直接转为成功。正式返回不得承诺后端尚未提供的真实计数/硬期限，未结束调用仍归原038额度和生命周期；这项采纳不改变033实验条件或质量权威。
- C-02/03/04/06沿[033 §15](<../shared-modules/guidance/04-metrology/DEV-MET-033_MSA、GR&R与计量资格开发指导.md#reference-certificate-adoption>)绑定源格式/命名域、原件/投影/实物/报告/用途决定的关系、逐特征量/单位/u或U-k-p、条件与时间、精确附件、canonical及签名覆盖域。保存与真实性/适用性分开；不迁入源AOI的强制字段或权限制度，不填未知有效期和覆盖因子。内容去重不合并实物身份或资格决定；提交Unknown仍查原操作，撤销不改签名原件。

上述由SPI采集/材料/体积与PCB孔槽/钢网共同消费，不能由某机台另填公共字段。FS018的Project/Port/Page/WP保留；其历史“confidence bounds”结果族不构成无条件区间保证。正式类型、后端、分布算法与数值Profile尚待逐切片采纳，真实材料/参考/验收界另按实际资格处理；两类欠账分开。

<a id="aoi-method-contract-semantics"></a>
## AOI本体、引脚与焊点方法的原合同接收

唯一方法为[057B](<../process-guides/guidance/06-domains/DEV-DOM-057B_AOI Component Pin Lead Polarity OCR开发指导.md#aoi-component-method>)、[057C](<../process-guides/guidance/06-domains/DEV-DOM-057C_AOI Solder Joint与Pre_Post Reflow开发指导.md#aoi-solder-method-implementation>)及公共[031 §12](../shared-modules/guidance/04-metrology/DEV-MET-031_通用计量引擎开发指导.md#plane-height-offset-relations)。以下沿既有C，不创DTO/第二状态/Store。FS057–062原工程、端口、页面和既有参数名保持；名称不足表达具体方法时由原Owner明确映射，不让产品实现临时塞字段或复用不相容score。

| 原C | 待采纳的精确语义 | 主要权威/禁止路径 |
|---|---|---|
| C-01/02 | 应装/应不装/未知、位号/针序/脚与盘多重关系、观察/炉前后/返修身份、封装/方法/必要视角及批准替代整组 | 037/032/034/原应用；PnP缺行不等DNP，图像检出顺序不重新编号 |
| C-03/04 | 独立板参考与本体位姿、候选完整性/物理去重、完整对应与替代证明、模对称角与定向证据集合、固定D/W/未知及分母 | 022/025/062供能力、应用解释；注册不吞偏位，数值唯一不授物理身份 |
| C-03/04/07 | 两面规范系数/方向/位置/支持/外推、模型和实际局部量、名义厚度及同射线/法向对应、误差/数值资格 | 029/031拟合与参考、030关系；顶面推下层不能变实测接触，极差/TLS/座落定义分别保留 |
| C-03/04 | 条件命中与材料类别、三态AND/OR、必需采集完整性、具名分位/积分及有限支撑、局部锚区/禁连多对多、多视冲突与前后可比性 | 025/030供计算、AOI定用途、039定规则/完整性；不得以逻辑OR掩盖缺采集，亮度不变物理坡角 |
| C-05/06/07/08 | 工程试算/固定历史、参数依赖失效、逐对象证据、原操作/Unknown查询、请求代次、分块/关联/native资源与取消排空 | UI020只投影；040保存与质量放行分别裁定，旧结果不覆盖新尝试 |

批准替代必须存在同一候选的全部必需证据，不跨候选拼PASS；多对多焊料关系不送一对一分配器删边。单条有效量、方法适用性、全目标/板完整性和质量判定分别返回与消费，部分/未知可合法保存而不放行。具体类型/公共适配、误差/工艺参数、真实样本与UI按原Owner逐项完成，当前仍语义候选。

<a id="cross-process-correlation-contracts"></a>
## 跨工序关联与质量消费的原合同采纳 — 2026-09-29

唯一关联方法在[048](../shared-modules/packages/PKG-048_ProcessCorrelation.md)，质量问题/总体/外部接收与处置交接在[058B](<../shared-modules/guidance/06-domains/DEV-DOM-058B_Cross-Process Correlation与Disposition闭环开发指导.md#quality-correlation-consumption>)。沿原C采纳，不生成CorrelationFactStore、统一生产状态或第二身份Owner。

| 原C | 本切片必须保留的语义 | 交接与不变量 |
|---|---|---|
| C-01/02/08 | 物理身份命名空间、板/子板/载具/面、工序与检查/计算/返修尝试、前驱/拆分/换件/有效关系修订、固定选择及窗口政策 | 037/原实体与工艺Owner→048；跨站事务ID不要求相同，相同码/位置/时间不自证实物关系 |
| C-02/03/04 | 源字段存在性/显式值/原内容、外部消息与接纳引用、设计Pad/脚/焊点多重关系、量种/参考/单位/方法及可比性 | 047/原接收Owner、032/工艺→048与质量应用；默认Passed/Human/RepairSuccessful或生成Guid不能替代原声明/业务身份；总检查数不补缺目标明细 |
| C-04/07 | 预计分析单位、两侧读取/已证/可比/实际统计集合、逐原因缺口、候选完成范围、统计独立层级/方法支持及误差能力 | 048提供关系与缺口，045提供具名统计；一板多Pad、多对多边数不增独立样本，未支持的区间不填通用confidence |
| C-04/06/07 | 各源固定截至点、事件/适用/已知时间、历史分析/后继更正、索引/更正扇出、实际完成/取消排空、原保存/提案回执 | 042/原Owner/048/应用按各自生命周期；迟到只形成后继投影，未知保存查原操作，不用latest内容重投旧键 |
| C-05/08 | 原机判/人判/返修/复检/正式处置/设备接纳/实物去向分别投影，查询权限与缓存失效 | UI021/Quality Hub只读；改善提案不签发处置，关联已证不授权设备动作或质量放行 |

FS065保留ICrossProcessCorrelation、Asun.Domain.Quality及JoinPolicyId/TimeWindowPolicyId/MinimumSampleCount。它们属于应用组合和原政策引用；精确字段/公开API、外部采纳证明、跨源读取/更正协议及具体统计方法仍须原Owner逐项完成，缺项只影响依赖能力，不阻断已有独立证据查看。

048的[方法细化](../shared-modules/packages/PKG-048_ProcessCorrelation.md#process-correlation-method)进一步约束上述原C：时间携带域/epoch及可比较的不确定区间，窗口开闭与越界溢出沿批准政策；固定源向量包含事实、身份关系和参数维度，最大序号不代替无缺口前缀。基数必须针对未截断的候选集合，预计成员×必需角色的义务状态与数值可比性分开计数；量测/统计用途的总体选择仍由原质量/工艺方法Owner给出，048与045分别验证关系和统计资格。更正影响同时覆盖旧/新键及此前无边的成员，受影响范围无法有界确定时返回待重建范围，不继续发布旧结果为当前准确。缓存TTL、输入封口、计算结束和业务完成分别表达；原保存协议负责原子发布完整投影，其中可合法包含未决/缺项，不能把“保存完整”混同“全体检查完成”。

<a id="factory-input-contract-semantics"></a>
## 外部入站采纳的原合同交接

唯一方法为[PLT013 §8](<../shared-modules/guidance/02-platform/DEV-PLT-013_跨模块事件与外部互联开发指导.md#factory-input-adoption>)；047接收、041交付持久化、原检测/返修应用采纳、037身份及048后续消费分别持原职责。以下沿C-01～08采纳，不定义第二份通用Envelope、生产事实或跨服务总状态机。

| 原C | 本切片须绑定的语义 | 关键接收断言 |
|---|---|---|
| C-01/02/08 | 受信连接/路由与作用域、原消息/业务发生/本地接收三种身份、外部版本/目标/attempt、来源时间/接收时间 | 消息Source不授权，构造Guid/Now/成功值不补原声明；新信封不自动增一次业务发生 |
| C-02/03/04 | 原字节/内容引用、字段存在/null/原token/显式值、允许消息和规范默认/扩展政策、解析/映射版本 | 先有界严格检查再构造；重复/别名冲突不靠覆盖顺序解决，整数ID不经double丢精度，默认来源可区分 |
| C-04/06/08 | 接收登记、固定业务接纳操作及载荷、原应用幂等/可查询回执、逐项或整批语义 | 应用已提交但回执丢失时查原操作；旧映射请求不被升级改写；批量局部成功不代表全批成功 |
| C-06/07 | 原件/展开/结构预算、端点/分区队列和背压、有效租约代次、实际取消排空、回执及去重保留 | 旧worker回调不推进新租约；离页不结束服务或撤销远端事实；无回查/幂等能力不能盲重试未知副作用 |
| C-05/08 | 原件读取/脱敏、状态投影与当前权限、恢复及重投作用域 | UI区分协议确认/持久收件/业务采纳/设备应用；撤权后不从缓存继续披露，不把未知显示成不存在 |

正式签名、预算数值、字段支持域/规范默认、批量原子性、协议确认点及部署事务能力仍待逐切片冻结。缺这些时可开展离线解析/映射和故障设计，不能以本表批准直接SDK反序列化或跨服务恰好一次保证。

<a id="cross-process-statistics-contract-semantics"></a>
## 具名配对统计的原合同语义

只回接原C，由[IM-043 §7.1.3.7–8](../independent-modules/statistics/DEVELOPMENT-GUIDE.md#cross-process-statistics-method)提供唯一数值方法，[058B §10](<../shared-modules/guidance/06-domains/DEV-DOM-058B_Cross-Process Correlation与Disposition闭环开发指导.md#quality-named-statistics-consumption>)负责问题/总体。此表不是新DTO、Store或万能统计状态；原FS065端口/项目与三个参数键不变。

| 原C | 必须绑定的内容 | 接收不变量 |
|---|---|---|
| C-01/02/04 | 具名问题/方法修订、分析单位与独立组层级、左右角色/差方向、量定义/参考/单位、单标签全集及指定复判轮 | 关联边/消息/板内Pad不增独立n；post−pre不随UI排序反转；只有同物理状态/分类定义才作双评者对照 |
| C-03/04/07 | 固定来源/成员、预计/已证/可比/单侧有效/完整配对范围、缺失/排除原因、单位权重政策及输入完整性 | 同一行两侧配对后再排名；Unknown不补0/正常，合法NG不自动排除；不同方法成员不合成一个假共同矩阵 |
| C-04/07 | 描述值可计算性、常数/近常数、精度/范围诊断、条件推断假设与df/尾侧/α、已支持域和未支持原因 | 点值可用不保证p/CI可用；r舍入为1不推出p0；SD0不生成零宽资格区间；κ负值合法，单类κ未定义 |
| C-04/06/07 | 原请求/计算/保存各自身份、参数快照、后继来源、输入多遍租约、排序/表/整数位数预算与真实排空 | 改参数/来源不复用旧计算内容；历史切换不覆盖旧记录；Unknown查原保存，不释放尚在计算的输入/槽位 |
| C-05/08 | 点值、样本/覆盖、p、区间、κ、原机判/人判及提案资格的独立投影 | 页面/报告不把它们统称confidence或准确率；提案预览和保存消费同一固定证据集合，后继修订重新核资格 |

当前无权重描述和具名条件 t 的公开 API、固定数值路线、有限支持域及规模预算语义已在 IM-043 §7.1.3 冻结；实际代码/后端构建和数值验证另验。产品正式字段、用途/方法授权与现场 Profile 由原 Owner 采纳，只阻断相应接入。高级推断分支按模块明确未支持，不由第三方 API 或 MinimumSampleCount 默许。


<a id="fixed-pair-exact-numerics-contract"></a>
## 固定片精确算术的原合同采纳增量

沿[024唯一方法](../shared-modules/guidance/03-vision/DEV-VIS-024_ROI与Inspection%20Target%20Selection开发指导.md#roi-local-exact-numerics)细化原C-03/04/07；不新增通用有理DTO、数值包或第二几何Owner。须冻结来源数值格式/共同二进尺度、原顶点与原face身份、精确判定和最终显示舍入的区别、允许的一次构造范围、位长/算术量/全候选预算、结果完整性与错误类别。物理不确定度和存储数精确是不同证据，输出舍成0不能将内部非零点合并为端点。

020持具体谓词/构造适配，022仍持全域编排/完整候选资格，007只消费原受限坐标合同；未知/超预算/取消不编码为无交或无根。固定片上界不授权递归有理布尔/任意外部大数，也不承诺BigInteger中途抢占、CLR工作集或工业毫秒值。具体公开签名、类型/序列化与错误映射仍须原Owner采纳，数学研究不直接授予生产资格。

<a id="ocr-decoding-association-contract"></a>
## OCR模式、解码与目标关联的原合同采纳增量

沿[021A唯一方法](../shared-modules/guidance/03-vision/DEV-VIS-021A_OCR与DeepOCR独立能力开发指导.md#ocr-decoding-association-method)细化C-02/03/04/05/07，保持024执行、033内容、053训练评价、PG/057B工艺比较及039/040原事实/提交职责。

| 原语义组 | 必须采纳且不可混合的内容 |
|---|---|
| 输入/模式/关联 | 原输入/目标/词/方法尝试身份，detection/auto/recognition形状与基数；显式裁图/展平/排序置换，低分或无词不删除必检义务 |
| 坐标/文字单位 | 原图/外部crop/内部预处理/score/alignment域分别标识；未知逆映射不猜。token、Unicode scalar、UTF-16及字素单位分别冻结，不以字符串Length推字符候选数 |
| 模型/解码 | 资产/字符表顺序/Blank/映射/预后处理及模型输出类型；CTC布局/有效T、logit或概率、tie/折叠顺序/分数语义/后处理分支与预算。HALCON内部网络不据Paddle推断 |
| 原读/派生/评价 | 后端原读、模型mapping结果、批准规范化、期望来源/比较和人工意见独立；缺原读不能从映射后串逆推，期待料号不能成为解码或关联代价 |
| 终态/恢复 | 合法空词、无效时序/格式、低分拒识、图像无效、歧义、取消/超时分开；每输入可追溯，原提交Unknown查询原操作，不用重新推理代替回执 |

表中是待采纳语义而非正式字段名；字典与多码点/语言分支、真实公共返回/坐标/置信行为必须由具名后端Golden核对，不能以抽象通用OCR成功状态省略这些条件。


<a id="training-text-evaluation-contract"></a>
## 训练恢复、导出与文字评价的原合同增量

原C-02/03/04/05/07/08按[060训练方法](../shared-modules/guidance/07-ai/DEV-AI-060_AI运行治理开发指导.md#ai-training-export-method)和[063原串评价](../shared-modules/guidance/07-ai/DEV-AI-063_数据集、GroundTruth与统计验证开发指导.md#ocr-text-evaluation-method)采纳下列语义，不在本页另建TrainState/Checkpoint Store或生产DTO。

| 语义/Owner | 应表达且不能合并的内容 |
|---|---|
| 053训练请求/实际执行 | 原任务、数据/标签/划分、字典/类表顺序、预后处理、代码/方法与请求/实际参数；安全边界、已消费样本/实际更新、缺状态和停止原因。配置seed不冒PRNG状态，epoch不冒精确数据游标 |
| 033/041内容与保持；053恢复记录 | 同一安全边界的角色/文件完整闭包、保持及提交回执、可恢复子集；warm start/有限继续/exact声明范围、父checkpoint及新attempt。权重/optimizer各自hash对但step不一致不算完整恢复；Unknown查原操作 |
| 053选择/转换评价；052/024真实执行 | validation用途/成员、best选择规则、源/派生资产、转换工具与支持、校准用途、输出shape/类表/数值域、逐项语义/拒识/坐标及缺项比对；数值接近不自动等价，test_dataloader名称不授最终测试资格 |
| 053文字评价 | 义务/真值/原读和关联终态、scalar及原UTF-16映射、严格编码错误、原串/批准派生、具名成本/tie与计数、条件/端到端/接受/空真值各集合及分母。缺输出不编空串，空分母不加epsilon，跨对象不串接 |
| 原用途/程序/生产Owner | checkpoint完整、best、报告完成均不自动授生产采用；权限/撤回/离线与在途边界仍按原政策。UI和报表只投影，文本对齐不授字形计量或工艺判定权 |

以上仍待原Schema/Owner逐字段采纳。可读原状态与实际API、模型/转换支持、恢复对照及数据用途分别验证；不因数学例或文件结构检查通过批准真实模型/部署。不存在某内部恢复状态的证据时只收窄所述恢复用途，不推断所有后端均不支持。


<a id="ocr-geometry-tiling-contract"></a>
## OCR外部几何、支持及分块的原合同消费

原C-02/03/04/05/07按[021A §16](../shared-modules/guidance/03-vision/DEV-VIS-021A_OCR与DeepOCR独立能力开发指导.md#ocr-external-geometry-tiling-method)补齐以下语义映射；不是新的Schema、DTO或批准字段。007/020、024、062及原工艺Owner不变，024不新增对062的强制依赖。

| 原责任 | 原合同应保留的区别 |
|---|---|
| 007/020外部变换与支持；024单词整理 | 源/目标frame、crop/extent、真实四角、像素约定与变换链；插值/预滤波实际足迹及逐级有效支持、合成补边、未知内部逆。可回投几何不等于已证完整字形支持 |
| 024分块/同词候选及恢复 | tile/core/halo、所有输入/输出索引、原Q/E与资格来源、完整可能关系、物理组与原观察、负责tile；截断/接缝/分组未决；恢复邻域、已用次数、原预算及新旧外围关系。稳定ID不证明同词，技术代表不删原冲突 |
| PG目标/建图；062计算 | 完整必检单词/已批准固定子槽位、独立位姿、合法域、实际边/费用/δ和输入图修订；062返回主解及替代证明，PG另核上游资格。几何唯一、识读完成、期待比较和质量判定分别表达 |
| PG/039完整性与040提交 | 原必检集合、各阶段完成/缺项/未决范围及原因；预算截断/取消不作无字。图/输入变化使对应结果失效，Unknown查询原回执，重算不是重复写事实的授权 |
| C-05只读交互投影 | 原图/派生域、支持缺口、候选/关联冲突、原读/派生/期待与恢复原因；当前选择与计算身份分离，切语言不改算法，页面不获得几何/事实写入权 |

几何误差界、真实词间距先验、合法域、费用尺度/δ和采样支持各有独立来源/适用范围，不将识别分数转成它们。当前严格合并/固定槽位是有限方法；未知布局、容量/拆合词及未资格后端不由合同字段齐全补证。正式字段和公共签名在原Owner当前切片采纳，不复制本文表格形成第二套类型。


<a id="code-reading-evidence-contract"></a>
## 条码返回保全、质量与身份的原合同消费

按[021B方法](../shared-modules/guidance/03-vision/DEV-VIS-021B_条码解码与印制质量独立能力开发指导.md#code-reading-evidence-method)在原C-01/02/03/04/05/07绑定下列语义，不建新的BarcodeStore/全局句柄库或Schema。

| 原责任 | 必须表达的区别 |
|---|---|
| 023返回与本次结果租约 | 输入/ROI/目标与attempt、实际后端/码制/方法、成功索引或opaque handle的本次映射、可见候选/排除/中止与数量上限；native handle不出适配层，不作跨进程持久键 |
| 023内容证据；应用/037解释 | 解码数据/byte、参考/纠错码字、ECI协议输出、引擎串、派生显示/HRI、应用字段及原区间/来源；不可得/未知/合法空值分开，不能重新编码字符串伪造byte |
| 023软件质量；原计量/工艺资格 | 标准版本/码制/结果族/原标签顺序与维度、等级/量值/诊断/特殊标记的类型、原成像与完整支持、实际软件值及资格/未完成原因；不统一把负值当缺失或整体取min |
| 原身份/采集/运行Owner | 来源闭合、物理观察归属及解析/绑定回执分别表达；补拍的新帧/采集尝试不自动新建BoardRun或检测尝试。sequence ID/parity不冒实体身份，派生组装留逐片证据 |
| 023资源/宿主调度与C-05投影 | 租约覆盖搜索至所有返回复制、隔离/真实排空、有限尝试及累计额度；UI显示分层原值/未决/质量，语言不改编码。Unknown查原提交，保存模型不替代持久观察 |

原字段/签名和状态词仍由原合同采纳；本表不宣布所有码制均已绑定。原raw封送、质量特殊值、搜索终态和真实原图评级须分别Golden；缺条件只限制对应能力。037不新增视觉库强依赖，023资产/身份/设备服务由宿主在明确可选端口组合，不通过容器暗取服务。

<a id="gs1-content-method-contract"></a>
## GS1内容解释的原合同承载

[037 §9](../shared-modules/packages/PKG-037_Identity.md#gs1-content-parsing-method)沿原C-01/02/03/04/05/07表达内容解释，不新增独立事实库或状态机。观察保留实际输入层/模式、原证据及编码、完整性和作用域；方法引用固定引擎/原生构建、词典/内嵌表、验证开关及输入政策。语法输出保留AI原序/重复、值、失败与不支持原因、日期精度和业务未决项；相同内容不产生实体合并依据。

来源区间区分适配可证明的转换映射和无法映射的逐AI位置；后者只引用整条Observation，不用HRI偏移虚构原byte或图像坐标。没有公共span API时不私添伪造字段，需精确位置的功能继续受限。DL原URI及忽略项保留，内容解析没有联网或设备命令副作用。

适配每请求独占上下文、错误/输出复制及失败隔离沿原资源责任；完成语法不等accepted，更不等持久绑定回执。GS1 C引擎/.NET包装、固定内嵌或严格外部词典、严格URI入口、AI业务映射仍是待原依赖/格式/Profile采纳的候选，037原直接依赖002和原Orchestrator写权不变。实际ABI、失败回退注入、字典变更回放和两个消费者集成另验；本节不定义新C#签名或枚举。


<a id="variation-inspection-contract"></a>
## 良品变化模型的原合同语义

原C-02/03/04/05/07按[IM-030唯一指导](../independent-modules/variation-inspection/DEVELOPMENT-GUIDE.md)及[应用映射](../shared-modules/guidance/03-vision/DEV-VIS-026_2D分割、Blob与缺陷候选开发指导.md#variation-inspection-method)承载以下语义；不是新增Schema、句柄Store或批准API。026直接依赖保持006/014/020/022/033；PG应用或宿主调用025/030并消费原039/040，公共核心不读取产品私表。

| 原责任 | 应表达并分别校验的内容 |
|---|---|
| 006/014/020/022输入与026方法 | 原输入/目标/参考格及块映射、实际类型/通道/位深/预处理、独立注册和逐级全部取样足迹；完整R、已扣批准I的D及预冻结来源。I不授权填造R内输入，缺支持不改D |
| 026建模/比较 | 模式、全量有序训练或direct来源、实际调用安排、A/B亮暗与比较方向、精确模型内容及用途；原亮/暗两槽、E/N/U、方向义务、输入失败/未执行与原始/派生分别保留 |
| 026生产者；033/041技术资产 | 运行/重建/证据闭包、训练数据是否已清及实际可用能力、请求/实际参数/不可查询、暂存检查与同封存核心fresh读回分开。native handle不进入公共合同 |
| 原PG/025/030/039/040 | 工艺应用连接/过滤与原域关联、按资格量测及工艺事件，内容/字形/位置/身份各义务独立；无响应不等PASS，单方向/部分块不当全域完成，Unknown沿原提交回查 |
| C-05投影与原资源Owner | 训练/运行实例隔离、实际native退出、预算/租约/旧代结果、模型换代边界；语言/预览不修改模型或事实，保存/评价/采用/激活分别有回执 |

训练统计的ddof/MAD缩放及整数阈值量化不补猜为合同常数，实际HALCON输出/公开能力另绑定。空间块同训练集合/全局参考格/真实halo的有限资格和任意缺失域支持不得混写；未支持的部分域/继续训练用途保持明确限制。当前语义仍由原合同Owner采纳，不能用字段齐全推方法资格或量产通过。


<a id="edges2d-association-contract"></a>
## 有向边、轮廓与拟合证据的原合同承载

原C-02/03/04/05/07按[025 §7](../shared-modules/guidance/03-vision/DEV-VIS-025_2D边缘、轮廓与几何特征开发指导.md#edges2d-association-method)补齐下列区别，不新增Schema/DTO、原生句柄Store或领域Owner。021直接依赖仍006/007/020，其它程序/质量/支撑来源由宿主提供冻结输入；PG调用062和030，不将运行流向自动改成模块依赖。

| 原职责 | 原合同须能区别的语义 |
|---|---|
| 006/007/020与宿主输入 | 观察角色/物理状态、原帧与坐标平面/单位/映射、计划slot/有向轴/实际几何、逐级真实profile支持与方法修订；未执行、输入无效、已完整执行无返回分开 |
| 021卡尺及局部组合 | 原入口/选择与极性政策、带符号幅值/真实基数、原返回索引及排序置换；完整pair和独立单边诊断分开，未配对边不可得不伪造。诊断须预登记且关联资格明确，空pair不成物理缺边事实 |
| 021轮廓与primitive | 父轮廓/原点序、连续段/断点、分段或平滑方法、实际映射/未知、拟合输入/排除理由/原点残差、支撑并与缺口/稳定性；近似类型标记、有效模型、工艺量资格不混 |
| 021 Metrology | 请求对象Index及本次instance ordinal/类型步长、查询来源和实际坐标模式/scale；测区与原找边无映射、used_edges非全候选、模型轮廓image、实例上限/有限搜索非穷尽分别承载 |
| PG/062/030与039/040 | 物理映射后拟合的固定几何先于全局关联，改变几何需重建图；原观察/模型/具名量/工艺判据/生产提交分别有权威；未知支持不删必检分母 |
| C-05投影及资源Owner | 原图/剖面/方向/单边-pair/模型/支撑的只读联动、方法选择影响及恢复；取消/超时只停止后续派发，native真实退出前持有图/句柄，旧代不覆盖新任务 |

具体返回参数/封装、端点误差、Metrology used_edges及distance_threshold在world/scale下的口径继续按公开适配和真实Golden核验；不从方法名或schema字段推断已支持。无精确贡献/slot映射只限制依赖该证据的用途，不能造假补全，也不扩大成全部提边不可开发。


<a id="localization-scope-contract"></a>
## 宿主语言、编辑解析与报告快照的原合同承载

独立模块契约与算法唯一见 [IM-003 localization](../independent-modules/localization/DEVELOPMENT-GUIDE.md) §3–5；本节沿原 C-05 及资源/输出适用合同定义产品映射，不新增并列核心 DTO、资源事实库或生产 Owner。[040 §13](<../shared-modules/guidance/05-ui/DEV-UI-040_WPF+DevExpress Design System开发指导.md#localization-scope-method>)只维护应用接入。Core 无其它模块实现前置，产品 Schema 不阻断无关 Core。

| 原职责 | 原合同须分别表达的语义 |
|---|---|
| 宿主/003请求与生命周期 | 宿主实例/epoch、单调请求代次、请求语言与终态、资源已发布修订、逐受控区域已呈现/未完成；A→B→A不能按语言相等复用请求 |
| 003资源输入与解析 | 模块/key契约/精确语言/版本/hash向量、关键/可空声明、typed参数及必出现集合、fallback政策；requested/resolved与缺口分开，RM非null结果不证明精确来源 |
| 原格式/参数Owner | 资源语言、显示FormatProfile、编辑开始冻结的ParseProfile、持久化表示分别引用；类型/单位/精度/时间语义与约束版本由原Owner给定，不由译文决定 |
| C-05可选控件 | 受控区域/公开入口及呈现回执、排队/执行/退出、最新批和失败恢复；异常退出不等阻塞隔离，同Dispatcher卡住时独立监测不冒呈现完成或资源归还 |
| 原046报告闭包与输出Owner | 整份报告固定资源/格式快照及保持、实际resolved来源、原事实和模板引用；屏幕切语言不改变在途报告，旧资源缺失不能以新版本冒原恢复 |
| C-07预算及释放方 | 包/条目/长度/参数/输出上限、缓存与快照租约、排队/执行/呈现期限；超时/取消/epoch不证明正在运行的回调或渲染已退出 |

模块资源格式、fallback、typed format、快照/呈现/排空与公开 v0.2 API 已在唯一指导冻结；原 D1–D5 不再并列定义核心。产品映射分别承载普通文案与 NativeTemplate 用途、key/hash/来源、固定格式快照、原事实引用及逐区域呈现/实际退出回执。DX ID/槽位/调用文化、已开原生窗入口和 IME 变体须在相应 WPF 适配切片逐项绑定；未具备者明确 NotSupported，不能称只等实测。客户词条审批、发行信任、报告存储政策、平台正式字段及消费者 Profile 仍由对应 Owner 采纳，只阻对应用途。语言投影不改变生产判定、授权、编辑草稿或质量放行。

