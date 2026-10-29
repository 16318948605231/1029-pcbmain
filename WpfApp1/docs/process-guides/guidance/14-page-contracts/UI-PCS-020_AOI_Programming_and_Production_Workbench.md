# AOI Programming and Production Workbench

> 2026-09-27 平台归位：当前职责与范围按[平台设计基线](<../../../00-baseline/PLATFORM-DESIGN-BASELINE.md>)及[所属指导目录](<../../README.md>)绑定。本页保留原ID与细化内容；原状态 `ImplementationSpecificationReady` 仅作历史记录，精确契约/Owner/参数未获批前不作为生产实施准入。
- 文档 ID：`UI-PCS-020`
- 类型：`PageContract`
- 版本：`2.2.2-prep`
- 状态：`DocMapped`
- 技术路线：WPF + DevExpress
- Scope：CAD/PnP target generation, component/pin/polarity/OCR/solder joint and review

## 1. Information architecture

首屏必须同时让操作员回答：当前产品/板/工单、当前状态、当前对象、当前结果、下一动作。页面采用 `DockLayoutManager` + document workspace + contextual inspectors；布局本身不得成为业务状态。

## 2. Primary regions

```text
Command/Ribbon
  → Context Header
  → Main Document/Viewport
  → Target/Result Navigation
  → Inspector / Evidence / Timeline
  → Status / Recovery
```

## 3. DevExpress usage rule

必须优先发挥 DevExpress 的工作台能力：Docking/Document、Layout、Grid/TreeList、Editors、MVVM/commands、layout persistence、contextual panels；禁止仅做原生 WPF 控件同名替换。DevExpress 官方文档明确支持 DockLayoutManager 的 docking、layout 保存恢复与 MVVM；官方示例也展示复杂 Dock UI、LayoutAdapter、MVVM docking 和 Visual Studio 类工作台结构。

## 4. Eight states

页面必须定义：Ready / Busy / Empty / Stale / Blocked / RecoverableError / PermissionDenied / Completed。每种状态都有可执行下一动作、AutomationId、键盘行为和证据入口。

## 5. Command model

所有生产配置/判定/处置动作通过 Application Port；批量操作必须先显示影响范围与跳过对象；危险/不可逆动作必须二次确认并展示 version/hash/authority。

## 6. Visual interaction

页面/VM及公开投影不持有 HALCON/AsunImage 原生对象；049内部显示适配可按明确寿命/租约拥有渲染资源，使用 immutable frame/evidence/overlay 投影。大图采用 tile/pyramid/LOD；ROI 操作必须有 hover/active/committed 三态，拖动过程不触发生产副作用。

## 7. Operator simplification

系统自动带出已知信息、自动定位对象、自动预选可用方法、自动汇总异常；操作员优先处理 exceptions，而不是重复输入系统已知参数。高级参数渐进披露，工程参数与生产常用参数分层。

## 8. Keyboard/UIA/Localization/DPI

定义稳定 AutomationId；Program/Recipe 支持焦点顺序、候选对照及批量预览。进入独立复判上下文后才采用UI005的领取/草稿/显式提交规则，Accept/Reject不能跨模式作为隐式提交。真实WPF验证DPI、三语、最小窗口和UIA。

## 9. Acceptance

- 页面不拥有生产事实；
- 所有关键状态均可测试；
- 所有关键 Command 有权限和审计；
- 视觉证据可从结果反查，结果可反查目标；
- 复杂工作台可保存/恢复布局，但布局恢复不能改变业务状态；
- UI 性能必须绑定 PerformanceProfile。



### 人因验收（2026-10-29）

按 [DEV-UI-045](../../../shared-modules/guidance/05-ui/DEV-UI-045_操作员工作流简化与人因开发指导.md) §7 要求登记本页面支持的典型流程人因指标实测。

| 流程 | 人因指标验收 |
|---|---|
| **本页主要流程** | 实测 §7.1 七项指标（步骤数、跨区移动、必须记忆信息、视觉搜索时间、错误恢复动作数、键盘可达比例、可见下一步）+ 样本量 + 离散度 + 熟练度档位 |
| **与人工基线对比** | 须满足 §7.5 六项可比性前提（同任务/口径/版本/熟练度/失败计入/未决计入）；不满足则标"不可比" |
| **目标值** | 来自批准 Profile；`TargetPending` 时可测量但不得判定"达标"或"优于人工" |
| **失败/未决归类** | 明确失败阶段与未决原因；每类至少一个具体示例 |

**强制要求**：每个实测值必须附样本量与熟练度档位；未采集时显式写"未采集"，禁止留白或用竞品数据填充。与人工基线对比时，§7.5 六项前提**全部满足**才可判定"优于人工"，否则标"不可比"。

**假阳性关注点**：AOI 编程显示完成但元件库缺失;焊接判定标准未批准;假阳性率未实测

## 10. Page-specific freeze

**页面角色：** `AOI Programming and Production Workbench`

### 关键 Command

`ImportCAD` · `ImportPnP` · `GenerateTargets` · `OpenComponent` · `ConfigureInspection` · `RunBoard` · `ReviewCandidate` · `SubmitApproval`

上述 Command 只定义 UI 意图；实际权限、Owner 和副作用必须由 Application Port/State-Owner Contract 决定。

### 关键 Query / 对象

`PackageLibrary` · `ComponentTarget` · `InspectionProgram` · `ReviewClaim`

### 页面硬边界

['Recipe/Program and review semantics are separate']

### 页面完成条件

- 每个关键 Command 都能映射到 Application Port、Permission 和审计事件；
- 每个关键 Query 都能定位到唯一事实/投影来源；
- 八态都有页面特定的下一动作；
- AutomationId、键盘、DPI、本地化、异常恢复和 UIA 均有可执行测试；
- 页面无法通过视觉绑定、ViewModel 或布局恢复直接修改生产事实。

## 11. 本页视觉与连续操作设计（2026-09-27）

视觉Token、主题、字体、间距、图标、动效与双验收统一引用[DEV-UI-040](<../../../shared-modules/guidance/05-ui/DEV-UI-040_WPF+DevExpress Design System开发指导.md>)。本节为设计要求，未宣称已有获批效果稿或真实WPF验收。

**构图：** 位号/封装树与板图、元件参考/当前对照、引脚/焊点Inspector，编程/生产模式标题显式区分。主动作位置固定，数值/单位和状态对齐，面板边界与选中细节遵循统一主题；用Dock/Document组织工作区，用Grid/Tree处理目标和结果，用分组Editors展示参数，避免单页随意拼控件。

**高级交互：** 选择元件同步针序、极性、OCR差异及3D；炉前/炉后方法适用阶段常显。异步图像/数据载入使用目标身份和请求版本校验，取消旧请求后迟到结果不覆盖新选择；效果过渡不延迟实际状态变化。

**高频任务：** 导入CAD/PnP→核对位号→配置并试算→审批；生产按冻结程序检测并转复核。本页已列Command只表达意图，动作权限/幂等/Owner在原Application Port验证；不增加同义端口或把ViewModel当事实写入者。

**失效与恢复：** 封装/位号冲突阻断相关目标；缺针端高度拒绝共面项目，不把锡峰替代针高。

| 页面状态 | 本页必须呈现及允许的下一动作 |
|---|---|
| Ready | 主要对象/版本与当前可用任务可见，按上述高频路径开始；缺必要输入不能先进入Ready |
| Busy | 显示当前阶段、对象和真实进度；允许的取消/暂停由应用能力提供，防止重复副作用 |
| Empty | 区分尚未选择、确实无结果、筛选无匹配；给出选对象/载入/清筛选的对应动作 |
| Stale | 明示截至版本/时间与陈旧原因；保留可查内容，影响权威动作时禁用并给刷新入口 |
| Blocked | 显示本页具体缺项及受影响任务，按上面的恢复流程定位；不影响的只读入口可继续 |
| RecoverableError | 显示错误、影响对象、保留内容和可执行恢复；提交未知先查询回执后决定重试 |
| PermissionDenied | 命令显示无权限原因，服务端/应用端仍复核；允许只读范围不因按钮禁用而丢失 |
| Completed | 显示计算完成/提交完成/批准完成中的真实一种及下一动作，不把它们合并为质量通过 |

**拟验收断言：** 炉前程序不能使用炉后焊点规则；同一页面两模式不共享可变运行配方。另在真实WPF完成三语、100/125/150%DPI及产品最小窗口、键盘完整路径、稳定AutomationId、主题切换、Dock/浮窗恢复、慢加载、连点/取消、关闭释放；精美视觉按DEV-UI-040的六项评审单独通过。上述是待执行验收，性能数值与分辨率仍由页面Profile冻结。

<a id="aoi-library-workflow"></a>
## 12. AOI套库与快编的工艺任务

共用快编使用[UI012 §13](../../../shared-modules/guidance/14-page-contracts/UI-PCS-012_NPI_Auto_Program.md#library-programming-ui)，工艺生成规则唯一在[057A](<../06-domains/DEV-DOM-057A_AOI CAD PnP与Target自动生成开发指导.md#aoi-target-synthesis>)。本页只补AOI专用交互，不复制库/程序Owner或通用diff编辑器。

工程标题固定产品修订/装配变体、板面/拼板、炉前或炉后、草稿修订和当前来源版本；生产标题固定当前BoardRun/实际程序引用，另开工程草稿不改变运行显示。左树可按拼板单元/位号或库/封装分组，所有分组仍定位完整实例，两个R1不能混为同一编辑对象。

连续任务：导入对账→定位缺行/重复/面别→查看候选封装/Pin1和元件身份→选字段来源→局部ROI/文字/引脚与3D对照→试检→查看全义务覆盖与差异→提交审批。模板与实例独立显示，拖ROI只编辑当前草稿；“写回库”是有来源/用途的单独库草稿动作，不能自动修改所有引用者。

Inspector按身份/装配意图、本体、针序/焊盘、极性/文字、可见焊接、3D基准/高度分类。每组显示方法适用阶段和必要输入；无高度时2D仍可查看，3D项显示缺项；BGA隐藏焊接显示未覆盖原因，不能用不可见绿色框暗示已检。应不装位置显示独立意图和适用检查，不能从树中悄悄消失。

选Pin1/引脚行联动局部几何及实际图，默认对照不使用会掩盖偏移的自动对齐；允许工程对齐时明确变换及只影响显示。文字原读、期待内容和核对状态分列，改期待字符属于受控程序变更，不能在试检结果格直接改成PASS。参考图/当前图、库模板/当前草稿均有明确角色标签。

批量按精确范围预览：同料号、同封装和同检测模板是不同筛选；先列硬冲突、局部锁定及跳过，不因图像相似自动全选。共享派生ROI修改列出下游失效范围。保存/传播未知显示逐程序回执入口，当前生产版与候选版双栏清楚可查。

拟交互验收：双面拼板同位号不串编辑，来源已翻X不再镜像，底面Pin1仍可识别，炉前不可套炉后判据，局部模板选择不改其它实例，DNP误装义务仍可见，生产检测中生成库新版只显示建议，关闭工程页不取消生产。UI005复判意见不会回填成库标准或自动发布；工艺结果/人判仍是各自Owner。完整高保真/WPF控件、全部弹窗及实际性能继续按专用切片完成。

<a id="aoi-interactive-workflow"></a>

### 图标可访问性验收

遵循 [DEV-UI-047 §2.3](../../../shared-modules/guidance/05-ui/DEV-UI-047_视觉设计系统规格.md#23-图标可访问性补齐全库空缺)：

| 项 | 验收要求 |
|---|---|
| 可访问名称 | 每个图标按钮/树节点/状态标记有非空可访问名称(`Name`/`HelpText`/SuperTip)，不能只有图形 |
| 装饰图标 | 纯装饰图标标记为装饰并从可访问树剔除 |
| 悬停提示 | 图标操作使用 DevExpress SuperTip(标题/作用/限制/快捷键/恢复步骤)，随语言切换 |
| 危险动作 | 图标 + 文字 + 颜色三重表达，不依赖单一图形 |
| 状态标记 | 状态色块同时有文字标签或图形形状差异 |
| 对比度 | 图标本身满足 §1.3 图形 3:1 门槛 |
| 高对比模式 | 不因系统高对比模式失效 |

**判据**：屏幕阅读器朗读时，每个可操作图标都有可理解的名称；任何"只有图标、看不出是什么"的位置是缺陷。

## 13. AOI有限交互原型与可操作指导（2026-09-29）

本节把§11–12落实为可运行的[合成HTML原型](../../prototypes/UI-PCS-020_aoi.html)，仍为`DocMapped / DesignReview`。它服务[PG017炉前](../../processes/PG-017_pre-reflow-aoi.md)与[PG018炉后](../../processes/PG-018_post-reflow-aoi.md)的页面设计审查，不实现生产检测。算法权威保持[057B元件/针序/极性/OCR](<../06-domains/DEV-DOM-057B_AOI Component Pin Lead Polarity OCR开发指导.md#aoi-component-method>)、[057C本体/引脚/可见焊点](<../06-domains/DEV-DOM-057C_AOI Solder Joint与Pre_Post Reflow开发指导.md#aoi-solder-method-implementation>)及[IM-036 §19.4](../../../independent-modules/metrology/DEVELOPMENT-GUIDE.md#194-连续截面沿程轴与有限层面计算c1)。本文仅规定投影和操作，不创建新算法、正式字段或第二套Owner。

### 13.1 工作区、身份与固定样例

页面顶部常显上下文、来源及合成标识；工程区另显炉前/炉后、草稿修订和来源代次。生产基线`DEMO-B0042 / POST-03 / DEMO-AOI/r7 / DEMO-COMMIT-AOI-042`保持只读。工程切到炉前不能把该炉后生产提交重命名为炉前结果。

| 工作区 / HTML定位 | 可执行操作 | 权威与隔离 |
|---|---|---|
| 生产观察 `view-production` | 完整实例搜索、面筛选、板图/局部/截面、逐针及证据、打开独立复判 | 固定原观察；显示镜像不改板面、坐标或Pin1身份 |
| 工程编程 `view-engineering` | P0–P7、整组差异、试检、保存及审批请求 | engineer角色可改本页内存草稿；离页不改生产程序 |
| 方法调查 `view-method` | 选择材料/局部桥/厚度对应反例，保存独立调查卡 | `lab`与生产、工程参数独立；保存卡不回写量值或规则 |
| 固定历史 `view-history` | 打开原提交、试检、取消、调查、请求与人工意见快照 | 读取记录时绑定原ID/内容，不能用当前参数重算历史 |
| 独立复判 `open-review` | 领取、理由草稿、预览、显式模拟提交、原回执查询 | 按UI005语义；复判项绑定原提交及完整实例，原观察和机判不改 |

原型的六实例固定为`TOP/I1/U1`偏位候选、`TOP/I2/U1`针2缺高度、`BOTTOM/I1/U1`外形模180°且极性未决、`TOP/I1/R7`缺件候选、`TOP/I2/BGA1`底部焊接不可见、`TOP/I1/DNP1`应不装仍须检查残留。位号相同不等于同一实例；搜索/筛选不缩减必检全集。外露脚面板共享有限挑战样例，不宣称逐实例真实采集；无外露脚的R7/BGA/DNP切局部或截面时给出不可评价/不可见说明，不画其它实例的脚或高度。

原型没有任意CAD文件解析、真实ROI拖动、图库或数据库。所有导入、角色、请求和故障均为明确标注的本页内存演示；刷新页面会重建样例，不能当作持久化。没有设备启动动作。

### 13.2 P0–P7的前置、动作、结果和恢复

HTML `id`是本轮可自动化定位点；真实WPF须映射为稳定AutomationId，并由原Application Port复核权限/状态。步骤导航只切页面，不能使前置自动通过。键盘Tab进入输入或按钮、Enter/Space激活，弹窗Escape只关闭/保留草稿，不隐式提交。

| 阶段 / 动作定位 | 输入与前置 | 操作后的内容 / 异常恢复 |
|---|---|---|
| P0 `import-cad`、`import-pnp`、`process` | engineer；无在途试检或Unknown请求 | 载入固定CAD/PnP样例；列缺R7、I2/U1重复、底面来源已翻X，不再次镜像来源。选择工序是来源变化，失效旧资格 |
| P0 `correct-source`、`freeze` | 两来源均有；对账完成 | 显式载入已对账来源r2后方可冻结；保留来源行身份，不由程序员猜补缺行。真实解析/行级选择仍待实现 |
| P1 `intent`、`confirm-intent` | 当前来源已冻结 | 选择已定义可见范围或包含隐藏焊接的挑战范围；DNP和隐藏义务明确，确认后旧对应/试检失效 |
| P2 `package`、`bind` | 意图已确认；来源仍为冻结代次 | A封装可绑定；B针序不兼容禁用绑定。展示A本体满足/OCR失败、B本体失败/OCR满足反例，不跨替代料拼PASS |
| P3 `generate`、`edit`、`apply-merge` | 已绑定，当前来源有效；冲突已解决 | 生成B/L/R两个完整组，显式应用到草稿。外扩0–1 mm仅为输入演示范围，非工艺限值；非法数字禁用确认 |
| P4 `input`、`confirm-plan` | 候选已应用且未陈旧 | 逐完整实例列检测项和输入安排；缺高度、缺必要视角、隐藏必检项均阻断试检，分母保留 |
| P5 `trial`、`cancel` | 当前修订计划已确认 | 冻结配置/来源/阶段特定工程观察后启动700 ms模拟；期间禁止修改和重复启动。取消、离页或撤权只留下取消快照，迟到不授予试检资格 |
| P6 `step-review`、`ack` | 当前修订试检完成 | 查看整组差异与保留的偏位、OCR差异、缺脚高度、隐藏未覆盖等挑战。确认的是本次工程审阅，不能把挑战改PASS；修改参数后必须重新计划、试检和审阅 |
| 保存 `save`、`footer-save` | engineer，无在途/Unknown；CAS期望版本匹配 | 可保存未完成草稿，不授予生产资格。模拟冲突后`rebase`预览期望/远端版本，`confirm-rebase`只接收演示版本再保存；真实远端内容差异/合并待原Port实现 |
| P7 `to-handoff`、`approval`、`send-approval` | 当前来源/候选/计划有效，试检、审阅、保存均对应当前修订 | 预览修订、来源、工序及逐项计划后显式提交模拟审批请求。成功仅显示请求收悉；没有批准、发布、激活或切换生产版本 |

可重现的正常路径：切工程师→工程→导入两来源→载入对账来源→冻结→确认意图→绑定A→生成并应用→确认计划→试检→审阅→保存→P7预览并提交请求。任意来源变化后从P0重冻，不从历史“已完成”继续。

**阶段特定义务：** 炉前共11项：TOP/I1/U1的本体、OCR、逐脚、高度4项；TOP/I2/U1的本体、逐脚2项；BOTTOM/I1/U1的本体、极性2项；R7存在性、BGA本体、DNP残留各1项。炉后另加TOP/I1/U1的可见焊接1项，共12项。选择隐藏要求另加BGA的4个具名隐藏项，得到11/15或12/16，不能删除这4项后声称覆盖。数字只定义此有限演示，不是生产必检目录。

缺高度时两个逐脚项和独立基准高度项没有所需输入；缺必要视角时极性以及炉后的焊接项缺输入。恢复输入不恢复旧试检/审阅。11/11或12/12表示**计划输入安排**，不代表测量全部有效或质量通过。试检快照为`DEMO-ENGINEERING-OBSERVATIONS`，带工序、义务及挑战，炉前没有炉后solder观察；不复制`POST-03`为工程结果。

### 13.3 B/L/R、人工锁定与依赖失效

本轮两个组作用于当前六实例工程样例，不提供单实例、跨程序传播或写回库能力。生产选择不改变工程编辑范围。真实批量功能继续执行§12的精确影响/跳过预览要求。

| 完整耦合组 | B / L / R及演示 |
|---|---|
| geometry | 外扩margin、方法版本、独立datum；初始B外扩0.10、方法r1，新R外扩0.15、方法r2、datum均r3。手工改L=0.12再生成产生冲突，不能只选margin而拼接其它组字段 |
| identity | 期待OCR文本、批准替代集合版本、pinmap版本；按整组比较，即使某字段数值相同也保留来源。此演示没有任意身份字段编辑器 |

B是上次生成基线，L是当前草稿，R是新候选。L=B可预选R；L=R可保留L；双方改变且不同须显式选择。主动保留与R不同的L要填理由；`lock-geometry`/`lock-identity`要求理由，锁定组只能选L。重新生成和语言切换保持锁和理由；解锁失效相关候选，须重新生成。应用后更新基线R，保留人工选择值作为L。

`refresh-source`或侧栏`aside-refresh-source`模拟“数值相同但来源代次变化”。它递增epoch，清冻结/意图/绑定，候选标陈旧，并使计划、试检、审阅、审批交接失效；不得以数值未变跳过。草稿revision和clock单调增加。恢复已存配置时epoch大于当前及已存代次，重新冻结/绑定/试检，不恢复旧资格。

### 13.4 原观察与方法调查的可判定示例

原观察保持原量值；调查区可切换有限反例，保存为独立历史卡。下述数字均为合成教学数据，不是HALCON执行、真实样品或验收阈值。

| 观察 / 操作 | UI必须呈现的意义与恢复 |
|---|---|
| 本体70F/20B/10U；`lab-body`切全未知或空位见证 | 固定D=100，未知补全界[0.70,0.80]；全未知[0,1]；0F/60B/40U为[0,0.40]而非确定缺件。这不是置信区间；未知与背景分开 |
| 名义X=10.000，观察X=10.300 mm | 保留板轴偏位+0.300；显示镜像、局部示意不把本体对齐为0。找目标的W与评价D不同，不能扩大/缩小D以消除偏位 |
| 外形模180°、极性未决 | 对称姿态不证明Pin1或物理极性。极性使用独立文字/色带/Pin1证据，冲突保留，不能多数票或取最高分替代 |
| OCR ABB，期待AB8；替代A/B反例 | 原读不被期待内容替换；同一个批准候选的必要项必须全满足。本轮替代完整性为固定反例展示，非动态替代求解器 |
| `detail-pins`与针行/局部针选择 | 稳定针号1/2/3，针2未测不重排3为2；[0.10,未知,0.18] mm的已知子集极差0.080仅注明2/3，不叫完整共面；需查看其它有效视图 |
| `image-section`的顶面与datum | 独立板面`DEMO-BOARD/r3`；模型z=1+0.1x+0.2y，中心1.0、角点0.7/0.9/1.1/1.3 mm，不能把模型外推角高或不可见底面称实测 |
| 可见焊料分位0.200 mm、D=10 mm²占比界[0.60,0.80] | 分位不是最大值；缺高度不补0重排；材料/高度有效域、分位方法与p仍须原方法参数冻结，不从示意数值推完整体积 |
| `lab-bridge`及`graph-lower`/`graph-upper` | FUF下不连/上可连，仍未知；FBF局部断开；FFF有连接候选；空间边未知也不能仅凭节点F宣称连通。W23内锚区与间隙受限，不把全局绕路当局部桥 |
| 焊点多对多与多视冲突 | P1↔P2、P2↔P3、P1↔P3关系并存，不以一对一删边；多视保留同物理焊点的来源和冲突，不能选有利视图消除NG或当独立统计样本 |
| `correspondence`切射线/法向偏置 | 相同示意层对应分别0.125/0.080 mm，不把法向偏置厚度直接当板轴高度差；层对应、方向、支持及未知边界由031提供 |
| BGA底部与DNP | BGA本体可见不代表隐藏焊接可检；DNP仍有残留/误装义务。复判不可凭本体意见关闭这些未观察义务 |

真实生产实现从057B/C批准投影读取原FOV、材料域、搜索域、基准、针/盘对应、视角和方法/参数版本；HTML的SVG与数字不能补齐这些输入。优先经AsunImage公共能力/HALCON及既有025/029/030/031使用，不在UI实现图像算法或持有SDK对象。

### 13.5 独立复判、Unknown与八态恢复

复判唯一规则来自[UI005](../../../shared-modules/guidance/14-page-contracts/UI-PCS-005_Review_Workspace.md)及[057D](<../06-domains/DEV-DOM-057D_AOI Review Rework与Disposition开发指导.md>)。本轮非盲审演示，复判弹窗展示绑定原提交/完整实例的本体证据；意见项是本体/可见外观，其它原因保留。reviewer选择`claim`领取→填写理由及意见→`preview-review`→`submit-review`显式提交。隐藏/DNP仅允许“无法判断/需补证据”。`expire`使领取失效但保留草稿；重新领取后重新预览。没有“本地改PASS”、整板关闭、处置放行或将意见写回库的动作。

保存、审批预览、复判预览均有回执丢失演示。Unknown保留原ID、冻结请求内容与修订；`query-save`/`query-review`只查原请求，不创建新请求。查询可在演示只读角色下恢复原回执；真实查询权限仍由原Port决定。Unknown期间不能编辑对应请求内容或恢复已存草稿来逃逸未决副作用。请求收悉、人工意见收悉与批准/质量放行分开。

| 派生状态 | 本轮触发 / 下一动作 |
|---|---|
| Ready | 当前步骤可操作；继续冻结、绑定、计划等，不声称所有阶段齐备 |
| Busy | 对象异步载入或试检在途；旧对象回调须核selectionSeq与完整ID，试检可取消 |
| Empty | 搜索无匹配；`clear-search`恢复完整范围和首个实例，旧回调不得覆盖 |
| Stale | 来源/参数改变导致旧候选失效；保留只读内容，回P0重冻或重新生成 |
| Blocked | 来源未齐/未对账、必要输入缺失或隐藏必检未覆盖；定位缺项，保留全集 |
| RecoverableError | CAS冲突或原回执未知；查看版本或原ID再恢复，不能重复提交 |
| PermissionDenied | 工程页切只读角色；保留草稿/证据并允许查询/离页，撤权使在途试检失效 |
| Completed | 当前审批请求已收悉；仍显示生产r7和剩余批准/激活边界 |

这些状态由行为派生，没有手工八态选择器。离开脏工程页必须选择保留或恢复已存配置；保留离页时取消本次试检。试检快照回调核取消标志、原请求、修订、epoch、当前角色与前置；失败仅入取消历史，不授予当前trial。保存Unknown或试检在途禁用恢复配置，避免丢失未决请求。调查卡、固定历史与复判保持独立。

### 13.6 原Command、DevExpress映射与剩余实现

`ImportCAD`/`ImportPnP`对应P0意图；`GenerateTargets`对应P2–P3；`OpenComponent`对应生产完整实例及原证据；`ConfigureInspection`对应工程组/计划；`RunBoard`在本原型仅演示未发布工程试检，不能调用真实产线；`ReviewCandidate`进入独立复判而非工程审阅的自动人判；`SubmitApproval`仅移交审批请求。保存/CAS/领取/查询定位点是既有职责的交互设计候选，**不新增正式Application Port、接口字段或Permission名称**。精确API、Owner与事务合同仍按原合同采纳后实现。

真实WPF按25.2.3使用DockLayoutManager/Document组织四工作区，GridControl/TreeList呈现完整实例、义务与差异，LayoutControl分组Editor和上下文Inspector；语言入口由宿主统一提供。图像使用049投影/租约边界。保存布局仅存视觉安排，不保存业务资格或恢复生产状态。窄屏降为顺序面板，差异B/L/R按同组垂直排列，关键试检、保存、提交与恢复不因视觉简化隐藏。

本轮沿用[REF-004官方研究基线](../../../references/REF-004_DevExpress与UI工作台官方研究基线.md)，实际阅读固定示例`DevExpress_layout_upgrade/bf801b30a0e7cdf6c1e54a708ec324087b758b4a/CS/MainWindow.xaml(.cs)`，借鉴稳定布局命名及保存/恢复与业务状态分离，未复制其业务结构。已安装布局/Grid技能的26.1示例仅取设计原则；目标保持本机25.2.3，不安装包或核验依赖准入。本轮没有可调用dxdocs工具；官方DockLayoutManager目标版本页面访问被Cloudflare拒绝，未据此声明API已核实。具体25.2.3属性、MVVM命令/调度、UIA、Dock/浮窗/DPI、资源释放与真实WPF行为留到实施阶段验证，不阻断本次HTML设计审查。

本轮未覆盖任意文件解析/单位变换、真实图像与ROI编辑、实例参数批量传播/库写回、真实HALCON算法与多视融合、正式Port/Schema/Permission/Claim服务、内容CAS合并、持久化/重启恢复、批准发布激活、真实WPF与性能Profile、设备/HIL/计量和客户现场资格。不能以HTML交互或下节证据替代这些验收。

### 13.7 本轮验证与证据入口

输入、只读研究范围、首轮失败、后续修复与最终精确HTML候选统一记录在[本任务验证记录](../../../../.work/aoi-ui-method-20260929/README.md)。候选目录保存各自HTML快照、SHA-256、结果及截图，旧失败版本原样保留。浏览器检查仅针对合成HTML；原型通过自验后仍待父任务独立接收，不改变DocMapped状态。

<a id="aoi-interactive-rework"></a>
### 13.8 独立审核退修：数值编辑与复判回执（2026-09-29）

`2.2.0-prep`经[独立浏览器审核](../../../../.work/aoi-ui-independent-20260929/review.md)发现两项P2：数值框逐字符`0.1`重绘为`1.0`并可提交，以及复判请求Unknown仍显示“草稿，尚未提交”。原候选、独立报告与失败证据保持原样；本次`2.2.1-prep`只修对应交互，未将此前16条自验当作这两项已通过。

- **输入草稿与提交值分开。** `edit-margin`采用明确小数点规则的文本编辑缓冲，保留原节点/选择/光标；input只更新局部校验与确认按钮，不重建弹窗。`0.`、`.`、空白等中间态保留但不能提交；逗号、指数、非法字符、负值及超出0–1的值拒绝，三语说明格式。显式确认使用同一解析器重新校验，边界判定不因浮点舍入把`1.0000000000000001`当1接纳。允许`0`、`1`、`1.000`、`.14`等完整表示；不是工艺阈值资格。语言切换保留原输入草稿。Escape放弃当前编辑，不改已有参数或资格；合法确认才写草稿并使候选、计划、试检、审阅/审批依赖失效。
- **复判状态单一且按原请求派生。** `review-status`优先显示pending的“提交结果未知；查询原回执”，收悉后才显示“本项意见已记录；整板未闭合”。没有pending/submitted才显示未提交草稿，领取失效另提示重领并预览。字段标题统一为“人工意见”，不把已发送或已记录内容仍命名为未提交草稿。三语切换不改变状态；只读查询保留原ID，未知期间禁止编辑和重复提交，原观察/机判不变。

定向自验使用新候选目录的`verify-rework.cjs`，以真实键盘逐字符、全选替换、中间插入/删除、Tab/Enter/Escape、语言切换验证输入及依赖失效；另外核三语草稿/领取失效/Unknown/原ID查询收悉和正常提交。结果与精确HTML/Page hash见同一[验证记录](../../../../.work/aoi-ui-method-20260929/README.md)，未机械重跑旧16条代替本轮输入/状态验收。

[独立定向复测](../../../../.work/aoi-ui-rework-independent-20260929/review.md)随后以自己的脚本验证两P2及直接影响：三语390/1500宽逐字符和编辑键、语言保持、精确边界/中间态拒绝、Escape不改资格、有效确认使候选/计划/试检/审阅失效，以及未提交/领取失效/Unknown/原ID查询/正常回执。全部限定断言通过，原观察和历史保持；主任务实际查看英文窄窗0.14、繁中Unknown及英文原回执收悉截图。HTML仍为`e7c1726fa748567b4f0e45fe737cc8a20898bcbbc6bf8331b753090e79db181e`；独立受审Page `2.2.1-prep`保留[原字节](../../../../.work/quality-correlation-adoption-20260929/before/UI-PCS-020_AOI_Programming_and_Production_Workbench.md)，本次`2.2.2-prep`仅回接结论。旧失败不覆盖；接收仅限HTML任务设计，真实WPF/UIA/DPI、完整键盘辅助操作、算法/权限/持久化/设备及工业资格仍按§13.6执行。
