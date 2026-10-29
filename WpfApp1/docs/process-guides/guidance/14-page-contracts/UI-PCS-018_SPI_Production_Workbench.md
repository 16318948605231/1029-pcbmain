# SPI Production Workbench

> 2026-09-27 平台归位：当前职责与范围按[平台设计基线](<../../../00-baseline/PLATFORM-DESIGN-BASELINE.md>)及[所属指导目录](<../../README.md>)绑定。本页保留原ID与细化内容；原状态 `ImplementationSpecificationReady` 仅作历史记录，精确契约/Owner/参数未获批前不作为生产实施准入。
- 文档 ID：`UI-PCS-018`
- 类型：`PageContract`
- 版本：`2.3.2-prep`；日期：2026-09-29
- 状态：`DocMapped / DesignReview`
- 技术路线：WPF + DevExpress
- Scope：3D acquisition, paste measurement, defects, SPC, feedback

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

2D/3D viewport 不持有 HALCON/AsunImage 原生对象；使用 immutable frame/evidence/overlay DTO。大图采用 tile/pyramid/LOD；ROI 操作必须有 hover/active/committed 三态，拖动过程不触发生产副作用。

## 7. Operator simplification

系统自动带出已知信息、自动定位对象、自动预选可用方法、自动汇总异常；操作员优先处理 exceptions，而不是重复输入系统已知参数。高级参数渐进披露，工程参数与生产常用参数分层。

## 8. Keyboard/UIA/Localization/DPI

定义稳定 AutomationId；Review 至少支持 next/previous/accept/reject/defer；Program/Recipe 编辑支持 focus order 和 batch apply；真实 WPF 环境验证 DPI、三语、最小窗口尺寸和 UIA。

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

**假阳性关注点**：SPI 生产显示完成但 3D 标定失效;体积测量但高度公差未批准;锡膏反光误当体积异常

## 10. Page-specific freeze

**页面角色：** `SPI Production Workbench`

### 关键 Command

`StartBoard` · `SelectPad` · `Open3D` · `RunMeasurement` · `InspectDefect` · `HoldBoard` · `OpenEvidence` · `ViewSPC` · `ViewFeedback`

上述 Command 只定义 UI 意图；实际权限、Owner 和副作用必须由 Application Port/State-Owner Contract 决定。

### 关键 Query / 对象

`PasteMeasurement` · `InspectionDecision` · `ReviewClaim` · `PrinterFeedback` · `Evidence`

### 页面硬边界

传输ACK、业务响应、参数/配方应用和后效分别显示；缺响应保持未知，配方接收不等激活。应用须有匹配的设备/作用域证据，不能单凭ACK成立。

### 页面完成条件

- 每个关键 Command 都能映射到 Application Port、Permission 和审计事件；
- 每个关键 Query 都能定位到唯一事实/投影来源；
- 八态都有页面特定的下一动作；
- AutomationId、键盘、DPI、本地化、异常恢复和 UIA 均有可执行测试；
- 页面无法通过视觉绑定、ViewModel 或布局恢复直接修改生产事实。

## 11. 本页视觉与连续操作设计（2026-09-27）

视觉Token、主题、字体、间距、图标、动效与双验收统一引用[DEV-UI-040](<../../../shared-modules/guidance/05-ui/DEV-UI-040_WPF+DevExpress Design System开发指导.md>)。本节为设计要求，未宣称已有获批效果稿或真实WPF验收。

**构图：** 影像和当前焊盘结果居中，顶部当前板/程序/执行，侧栏缺陷队列，底部量测/SPC/反馈状态。主动作位置固定，数值/单位和状态对齐，面板边界与选中细节遵循统一主题；用Dock/Document组织工作区，用Grid/Tree处理目标和结果，用分组Editors展示参数，避免单页随意拼控件。

**高级交互：** 焊盘、3D、截面、量测表同步；状态分别显示计算、提交、机判、人工意见和反馈应用。异步图像/数据载入使用目标身份和请求版本校验，取消旧请求后迟到结果不覆盖新选择；效果过渡不延迟实际状态变化。

**高频任务：** 开始板检测→查看异常焊盘→定位量测域→打开证据/复判→查反馈状态。本页已列Command只表达意图，动作权限/幂等/Owner在原Application Port验证；不增加同义端口或把ViewModel当事实写入者。

**失效与恢复：** 高度无效显示缺测而非零膏；提交失败保持未提交；反馈未知先查询。

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

**拟验收断言：** 体积/面积/高度单位区分；图上高光不能改变量测原数据；ACK不显示打印机已应用。另在真实WPF完成三语、100/125/150%DPI及产品最小窗口、键盘完整路径、稳定AutomationId、主题切换、Dock/浮窗恢复、慢加载、连点/取消、关闭释放；精美视觉按DEV-UI-040的六项评审单独通过。上述是待执行验收，性能数值与分辨率仍由页面Profile冻结。


<a id="spi-production-method-projection"></a>
## 12. 参考、材料、具名量与反馈的同源投影

按[055B参考](<../06-domains/DEV-DOM-055B_SPI Reference Plane与Pad_Stencils Target开发指导.md#spi-physical-reference>)、[055C计量](<../06-domains/DEV-DOM-055C_SPI Paste Segmentation与Metrology开发指导.md#spi-paste-method>)和[055D反馈](<../06-domains/DEV-DOM-055D_SPI Rule SPC与Printer Feedback开发指导.md#spi-feedback-receipt>)组织本页，公式与业务接受条件不复制到ViewModel。

选一个pad时联动显示其稳定实例/面、开口子项/沉积组、原膏组件和相邻违反关系。中部原图/真实高度证据优先，右侧量表将“量名、数值/单位、完整/部分、参考/分母、原因”分列；面积比100%和覆盖75%可以同时存在。中心标明面积或体积定义；无定义时不在原点画点。桥物体、关联目标和违反关系不同计数，不因一物两目标重复画成两份物料。

底部调查按参考→原F/B/U与几何缺口→原/派生差→局部桥见证→单元E/U与具名量逐级定位。固定局部桥域/锚和有效/可能空间边可开关查看，但图层可见性不改变计算。不能用补洞渲染填掉未知、高度Z夸张改变量值、列表过滤改变必检或SPC分母。对当前未测项显示实际缺视角/基底/材料原因，并定位相应证据。

采集调查先按055A定位H0/H1/H2、原FOV/曝光组/图案清单、Actual与各有效/未知mask；原生、派生和仅显示分层。结构齐、可测、参考适用、提交/排空分列；重拍指新观察，提交未知查原回执。

反馈页签沿ViewFeedback打开固定原命令/提案上下文，显示依据、参数差异/单位/方向、设备/轨道/配方版本、发送/业务响应/逐项应用与效果范围。当前生产值与历史原值分栏；SPI到达较晚的旧在制板不进入新后效。无应答下一步为查询原命令，部分应用定位具体参数，后效缺成员定位范围；不把一个通用“重试”按钮绑定再次调机。需新增查询/建议提交意图时先由原应用端口采纳，不由页面私发协议。

八态补充：Busy标当前阶段/对象并只取消可取消操作；Empty区分无选择与无数据；Stale保留旧修订只读；Blocked定位基底/覆盖/关联；RecoverableError查询原提交/原命令；PermissionDenied限制新写入但保留获准历史；Completed明确计算/提交/应用/效果哪一项完成。命令结果不因语言、主题、布局恢复或双窗口查询重发。三语反馈文字沿055D§7，量名/原因和帮助全部走统一资源。

本节是页面实施输入；本轮合成HTML已按§13–14实现并验证部分交互。真实WPF/UIA、DPI、图像租约/慢证据、撤权与原应用回执尚未验证，不能将浏览器结果当完整PageContract或产品验收。


<a id="spi-interactive-workspaces"></a>
## 13. 四工作区合成交互与操作契约 — 2026-09-29

[SPI双页原型](../../prototypes/UI-PCS-018-019_spi.html)是本页与UI019共用的设计评审产物。工作区为“生产观测 / 快速编程 / 方法调查 / 固定历史”，输入完全合成；SVG表达关系，不是相机图、真实高度重建或测量网格。HTML内的对象和状态只是内存演示，不能作为新DTO、应用端口或业务状态权威。正式职责继续沿055A/B/C/D及原035/039/040/042/045。HALCON计算和AsunImage接入不在浏览器实现；本轮也没有新设备接口或生产写操作。

### 13.1 页面身份、角色与默认工作流

顶部始终显示DEMO-B0042/PRINT-02、原SPI-P17/r7、TOP/L1和当前证据身份。生产页固定`DEMO-SPI-ORIGINAL-r7`；工程页用独立`DEMO-DRAFT-rN`，方法页用`DEMO-METHOD`，不能给新方法结果沿用r7。操作员可选目标、查看原证据、方法示例和原回执；工程师可改草稿。角色和PermissionDenied均在事件处理层复核，八态选择器仅强制展示评审状态，不授予写权或机台就绪。

左树固定六个制造pad、五个印刷必检pad和七个开口子窗：I1/U1/P1→A11/A12，J2/P1/P2→A21/A22与同一D23，R9/P1→A91，I2/U1/P1→A211/A212；TP1明确不印刷。R9装配DNP但仍必检；I1与I2同名U1不合并。搜索、未完成筛选、镜像和排序不得改变这组分母。搜索不匹配时清空选择、图像详情和量测；“清除筛选”结束旧选择请求代、清除载入标记和开口子窗，再恢复首个明确目标；旧回调不能影响恢复后的目标或后续新选择。

选树、图上pad或开口子窗联动稳定ID、开口轮廓、沉积组、原膏、当前量值和剖面。异步选择带单调请求代，A→B→A不能接收首代A；演示100ms仅模拟选择加载，真实应用仍须绑定板/面/尝试/目标/方法与图像租约。方向键在目标间移动，Enter/Space选择；Alt+1–4切工作区，文本编辑不被目标导航截获。弹窗Tab约束在对话框内，Esc只关闭本地弹窗，不撤销保存或设备操作。

### 13.2 原观测、量值与恢复

| 操作入口 / HTML锚点 | 本轮实际行为 | 必须保留的边界 |
|---|---|---|
| `data-target`、`data-pad`、`data-aperture` | 目标/板图/开口选择联动 | 稳定身份，缺观察不补邻pad数据 |
| `height-view`、`section`、`zscale`、`layer-*` | 切高度示意、移动截面及调整显示夸张/图层/镜像 | 原材料/高度和量值不随显示重算；不是3D算法或实际几何剖切 |
| `open-evidence` | 冻结被打开pad、原帧/组/开口与原因 | 弹窗保持原身份，语言切换不换事实 |
| `footer-next` | 一次定位下一个未完成/异常目标 | 完成和非印刷项按当前队列跳过，但仍在原目标集 |
| `query-commit` | 查看提交42或独立未知提交43；查询保留原ID | 42对应原提交样例，43属于DEMO-B0043/PRINT-01，不能将两板状态互填；不重发提交 |
| `open-feedback`、`query-command` | 打开固定提案/命令、逐项应用和后效，查询原回执 | 不发印刷机命令、补发缺项、相反增量或自动回滚 |

以上是浏览器检查锚点；产品AutomationId以`SpiProduction.SelectPad/OpenEvidence/QueryOriginalCommit/ViewFeedback`等页面意图绑定既有应用能力后冻结，不从HTML ID创建正式端口。未绑定的StartBoard、RunMeasurement、HoldBoard、质量放行与设备动作保持未实现。

U1/P1原膏面积1.000、pad面积1.000、交叠0.750 mm²分别显示面积比100%、覆盖75%、外溢0.250 mm²；100%不是通过标记。R9材料已知但高度缺失，体积显示未测。一个C-B23关联两pad：组量0.120、目标局部分配各0.050、未分配桥颈0.020 mm³；局部分配不是两份完整组件量，不能汇总成0.240。已知缺陷和未完成同时保留，本原型没有客户阈值或板级质量判定算法。

反馈固定三种独立命令样例：应用Unknown、仅X应用、XY已应用但后效成员不足。传输、配方接收、X/Y应用、后效分列；查询计数只表示浏览器读样例次数，不产生发送。提案保留b=(+40,−20)µm、独立J=0.001mm/µm、g=.5与候选Δ=(−.020,+.010)mm。后效候选集两块新参数板中仅一块已观察；一块SPI晚到的旧r17在制板明确排除，不以到达顺序归入r18。没有完整后效统计、Cpk或因果改善结论，ViewSPC仍待既有045投影接入。

### 13.3 独立方法调查

方法调查与草稿、生产事实各持独立选择，不由切换样例改变原r7。所有数值只为方法定义反例，非工艺默认值或真实输入。

| 调查页 | 可操作反例与回馈 |
|---|---|
| 材料与量域 | F/B/U按物理面积比例示意；U_s与F内U_h分列。固定D=1mm²，E_F=.4、B=.6，h=.2时材料量.08；参考偏高.01时.076。几何请求另声明B上的真实高度，整体量.20→.19。全B合法材料0、全U无值、F高度洞仅部分量、F负厚度拒识材料量；正部诊断不能恢复材料资格 |
| 采集支持 | H0/H1/H2显式选择，路线切换不挪用另一条结果。查看厂商高度/原生0、派生或闭面，完整曝光组、缺图案、逐步混曝光和多曝光冲突；结构、方法输入、物理参考、提交/排空独立。清单是有限合成输入，未实现原帧导入/解码/同步证明 |
| 局部桥 | 固定W23与A2/A3，F/U/F、F/B/F、F/F/F、未知空间边/锚、域外绕行及closing分别显示下图/上图见证。原材料不随许可或图层改变；守恒数值另标DEMO-CONSERVATION，不冒充当前局部图的新量测 |
| 中心与参考 | 等面积两片x=0/2、高.1/.3显示面积中心1与体积投影中心1.5；部分域中心单列，无材料无中心。铜面.035、阻焊.020、膏顶.135与独立台阶.015给.100mm；台阶未知或膏顶低残差均不能获得基底资格。离散面积加权均高/中位单列；连续面积分位仅引用031§11，无模拟连续运行值 |

“保留独立新来源卡”创建未提交工程预览；历史保留原提交、试算发起、取消和新来源四种身份。打开原记录不改当前方法选择。刷新会清除内存新增记录，本原型不声称持久化、重启恢复、多窗口或跨进程隔离。

### 13.4 布局和可用性

桌面使用影像居中、目标左侧、量测右侧、剖面/关系在下的布局；窄窗优先影像并允许纵向滚动，目标和参数按行堆叠，三方差异逐组纵排。导航可横向滚动但按钮文字不重叠；固定底栏保留身份/状态与下一动作，模态弹窗限制在视口内。三语和明暗切换保留未确认意图、理由、输入值、当前记录与在途计算。CSS仅模拟布局；实际Dock/Document、SuperTip、状态栏与恢复由DevExpress 25.2.3实现切片验证。已使用安装的WPF布局技能区分工作区/表单职责；dxdocs当前无可调用工具，未猜版本API、下载包或更改依赖。

<a id="spi-interactive-evidence"></a>

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

## 14. 本轮唯一验证入口、输入版本与缺项

消费者为UI018、UI019及集成Owner的独立接收复核。写入仅限这两页、同一SPI HTML和`.work/spi-ui-method-20260929/`；未修改PG、方法指导、公共包、Contract、入口/进度、其它原型、产品代码或原资料。无Git元数据，未声称创建工作树。

初始固定A1.1.1、B1.1.0、C1.1.2、D1.1.0及两页2.2.1，原字节保留在[before](../../../../.work/spi-ui-method-20260929/before/)，[初始读集](../../../../.work/spi-ui-method-20260929/inputs-0.1.0.json)保留旧hash。接收主任务增量后定向复读C1.1.3§6.1、PG014§13和031连续分位导航：离散/连续分别命名，未新增连续分位计算。本轮最终[已复核输入与hash](../../../../.work/spi-ui-method-20260929/v0.1.0-candidate-04/reviewed-inputs.json)同时保留初始和当前值，不以整文件变化否定不相关已验行为。

退修前基线HTML SHA-256：`81ce980ec3d7def37ae58695c2fa0ff0a8955faf54c154b32d2ee5b4b8db2197`。运行[版本化验证脚本](../../../../.work/spi-ui-method-20260929/v0.1.0-candidate-04/verify.cjs)，[机器结果](../../../../.work/spi-ui-method-20260929/v0.1.0-candidate-04/verification.json)为PASS，Edge `154.0.4258.37`。该目录保存被验证的HTML/JS/CSS、脚本、报告及截图原字节；01的失败、02/03的历史结果保持原样，不覆盖成最终通过。下述完整验证和十张截图仅绑定该历史基线；独立复核发现的两项缺陷及当前退修见§14.1，不将历史PASS改写成当前全测通过。脚本要求新的版本目录，已有目录即拒绝重写。

实际检查包括三语P0–P7与三类来源、必检与实际输入/量域相容性、真实B/L/R冲突/理由/锁定、同值新来源失效、待确认意图跨语言保持、CAS冲突/原未知查询、试算快照/取消/撤权/离页与迟到、稳定pad/开口及A→B→A、方法算例、原事实/历史隔离。另运行96组三语×四工作区×八态、36组三宽度(1500/1024/390)×三语×四工作区，以及窄窗差异/弹窗的边界断言。无页面脚本错误、外部HTTP请求或页面横向溢出。固定弹窗与导航另查控件自身边界，不能只用页面scrollWidth证明未裁切。

基线代表截图已实际查看：[中文生产](../../../../.work/spi-ui-method-20260929/v0.1.0-candidate-04/production-cn-dark.png)、[英文浅色生产](../../../../.work/spi-ui-method-20260929/v0.1.0-candidate-04/production-en-light.png)、[繁体反馈](../../../../.work/spi-ui-method-20260929/v0.1.0-candidate-04/feedback-tw-light.png)、[英文三方差异](../../../../.work/spi-ui-method-20260929/v0.1.0-candidate-04/merge-en-light.png)、[中文材料调查](../../../../.work/spi-ui-method-20260929/v0.1.0-candidate-04/material-cn-dark.png)、[英文局部桥](../../../../.work/spi-ui-method-20260929/v0.1.0-candidate-04/bridge-en-dark.png)、[窄窗生产](../../../../.work/spi-ui-method-20260929/v0.1.0-candidate-04/narrow-production-en.png)、[窄窗差异](../../../../.work/spi-ui-method-20260929/v0.1.0-candidate-04/narrow-merge-en.png)、[窄窗离页](../../../../.work/spi-ui-method-20260929/v0.1.0-candidate-04/narrow-leave-en.png)、[编程目标预览](../../../../.work/spi-ui-method-20260929/v0.1.0-candidate-04/program-target-cn.png)。视口截图不证明全部内容同屏。

**本轮不覆盖：**真实制造导入/ROI编辑/生成器、实际高度和图像算法、HALCON/AsunImage调用、完整采集图案/曝光编译与同步、工业限值或方法资格、公共API及正式权限/保存事务、真实SPC/反馈协议、设备副作用、多窗口/重启、WPF/UIA/DPI、性能/Golden/HIL及现场验收。候选仍为DocMapped/DesignReview；当前退修的独立接收见§14.1，浏览器合成通过不代表SPI生产或工业资格完成。


<a id="spi-interactive-rework"></a>
### 14.1 独立复核退修与当前定向验证 — 2026-09-29

[独立复核结论](../../../../.work/spi-ui-independent-20260929/REVIEW.md)确认两项P2：在途选择切Empty后清除筛选会遗留载入状态；H1混曝光虽被方法资格阻断，但逐行及汇总错误显示结构完整。锁定选项和窄窗桥接的失败已由独立补核归因为测试断言问题，不作为产品缺陷改UI。独立证据目录保持只读。

作者退修交付两页为`2.3.1-prep / DocMapped / DesignReview`，HTML为`v0.1.1-candidate-01`，SHA-256：`1325d5d6b0ae2998b2c5a1a2c2d2db930551b0da4847e265dbf1b550a867114b`。

- `clear-search`同时递增选择请求代、结束载入、清除筛选及子窗并恢复首个U1。R9旧回调到达后不回填、不遗留loading，也不影响清除后新选I2。
- H1采集清单将“帧接收”与“帧/曝光组身份”分列。要求EXP-A/PAT-02却收到EXP-B/PAT-02时，显示已收到、曝光组身份不一致，汇总结构同样显示身份不一致；缺图案仍显示缺帧。完整但多曝光冲突保留“输入结构完整”和独立的“方法未具资格”，不能把所有方法失败都映射成结构失败。

上述结构语义直接遵循[055A采集后关联](<../06-domains/DEV-DOM-055A_SPI 3D Acquisition与HeightField质量开发指导.md#spi-frame-admission>)及[H1解码与多曝光](<../06-domains/DEV-DOM-055A_SPI 3D Acquisition与HeightField质量开发指导.md#spi-height-admission>)：收到帧或数量齐不等于期望曝光组身份齐；每完整曝光组独立解码，禁止混步。页面没有新增解码器、方法资格或领域规则。

运行[定向回归脚本](../../../../.work/spi-ui-method-20260929/v0.1.1-candidate-01/verify-rework.cjs)，[当前报告](../../../../.work/spi-ui-method-20260929/v0.1.1-candidate-01/verification.json)为PASS，Edge `154.0.4258.37`。先对保留的candidate04冻结浏览器时钟复现旧缺陷，再通过真实点击/选择和推进时钟检查三语：R9在途→Empty→清除→U1量值恢复、清除后再选I2、在途筛选无匹配后恢复；H1完整/混组/缺帧/完整但冲突、H0/H2结构和原生产事实保持。390宽度三语无页面横向溢出，无pageerror或外部HTTP请求。

七张截图均已实际查看：[简中恢复](../../../../.work/spi-ui-method-20260929/v0.1.1-candidate-01/clear-recovered-zh-CN.png)、[繁中恢复](../../../../.work/spi-ui-method-20260929/v0.1.1-candidate-01/clear-recovered-zh-TW.png)、[英文恢复](../../../../.work/spi-ui-method-20260929/v0.1.1-candidate-01/clear-recovered-en-US.png)、[简中混曝光](../../../../.work/spi-ui-method-20260929/v0.1.1-candidate-01/h1-mixed-zh-CN.png)、[繁中混曝光](../../../../.work/spi-ui-method-20260929/v0.1.1-candidate-01/h1-mixed-zh-TW.png)、[英文混曝光](../../../../.work/spi-ui-method-20260929/v0.1.1-candidate-01/h1-mixed-en-US.png)、[英文窄窗](../../../../.work/spi-ui-method-20260929/v0.1.1-candidate-01/h1-mixed-narrow-en.png)。窄窗表格文字折行，结构摘要和命令可见；截图不代表全部内容同屏。

新版本目录保留当前HTML、JS/CSS、回归脚本、报告、截图和两页契约原字节。candidate04完整套件与十张截图保持历史绑定，本次只执行受影响回归，未重跑96状态/36布局矩阵或数学验证。§14所列真实算法、WPF、设备及工业资格范围仍未验证；本次退修已由[独立短复测](../../../../.work/spi-ui-independent-20260929/REVIEW.md)接收：同一HTML hash下三语的在途清除/新选择、混曝光身份、完整但方法不合格和390宽度受影响行均通过，六项定向案例无pageerror。旧失败和测试误判记录保留；本页2.3.2仅同步接收说明，不把2.3.1作者快照或candidate04完整套件改写为新版本全测。
