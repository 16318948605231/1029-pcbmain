# SPI Programming Workbench

> 2026-09-27 平台归位：当前职责与范围按[平台设计基线](<../../../00-baseline/PLATFORM-DESIGN-BASELINE.md>)及[所属指导目录](<../../README.md>)绑定。本页保留原ID与细化内容；原状态 `ImplementationSpecificationReady` 仅作历史记录，精确契约/Owner/参数未获批前不作为生产实施准入。
- 文档 ID：`UI-PCS-019`
- 类型：`PageContract`
- 版本：`2.3.2-prep`；日期：2026-09-29
- 状态：`DocMapped / DesignReview`
- 技术路线：WPF + DevExpress
- Scope：CAD/PAD/stencil target generation, parameter proposals, verification

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

**假阳性关注点**：SPI 编程显示保存但焊点参考缺失;自动生成覆盖率但未检项未标记;试检通过但样本不代表

## 10. Page-specific freeze

**页面角色：** `SPI Programming Workbench`

### 关键 Command

`ImportStencil` · `GeneratePadTargets` · `ConfigureMethod` · `BatchApply` · `ValidateProgram` · `PreviewCoverage` · `SubmitApproval`

上述 Command 只定义 UI 意图；实际权限、Owner 和副作用必须由 Application Port/State-Owner Contract 决定。

### 关键 Query / 对象

`PadTarget` · `StencilOpening` · `InspectionProgram` · `CoverageSpec`

### 页面硬边界

['Programming is Draft/Approval workflow']

### 页面完成条件

- 每个关键 Command 都能映射到 Application Port、Permission 和审计事件；
- 每个关键 Query 都能定位到唯一事实/投影来源；
- 八态都有页面特定的下一动作；
- AutomationId、键盘、DPI、本地化、异常恢复和 UIA 均有可执行测试；
- 页面无法通过视觉绑定、ViewModel 或布局恢复直接修改生产事实。

## 11. 本页视觉与连续操作设计（2026-09-27）

视觉Token、主题、字体、间距、图标、动效与双验收统一引用[DEV-UI-040](<../../../shared-modules/guidance/05-ui/DEV-UI-040_WPF+DevExpress Design System开发指导.md>)。本节为设计要求，未宣称已有获批效果稿或真实WPF验收。

**构图：** 左侧焊盘/开口目标树，中部板图与覆盖预览，右侧方法/参考面参数，底部差异/校验。主动作位置固定，数值/单位和状态对齐，面板边界与选中细节遵循统一主题；用Dock/Document组织工作区，用Grid/Tree处理目标和结果，用分组Editors展示参数，避免单页随意拼控件。

**高级交互：** 批量变更预览明确焊盘范围，参考面采样点与锡膏域可同时检查；覆盖图解释未覆盖原因。异步图像/数据载入使用目标身份和请求版本校验，取消旧请求后迟到结果不覆盖新选择；效果过渡不延迟实际状态变化。

**高频任务：** 导入→关联目标→配方法→试算→批量差异预览→验证→提交审批。本页已列Command只表达意图，动作权限/幂等/Owner在原Application Port验证；不增加同义端口或把ViewModel当事实写入者。

**失效与恢复：** 缺钢网资料按声明模式处理，不能复制焊盘冒充开口；资料修订要求重新验证。

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

**拟验收断言：** 批量设置不修改未选焊盘和当前运行板；自动生成目标不等于程序已发布。另在真实WPF完成三语、100/125/150%DPI及产品最小窗口、键盘完整路径、稳定AutomationId、主题切换、Dock/浮窗恢复、慢加载、连点/取消、关闭释放；精美视觉按DEV-UI-040的六项评审单独通过。上述是待执行验收，性能数值与分辨率仍由页面Profile冻结。


<a id="spi-programming-method-projection"></a>
## 12. SPI目标、参考和P0–P7的连续编辑

[PG014唯一阶段表](../../processes/PG-014_spi.md#pg-014-ai-data-performance-ui)约束流程；[055B](<../06-domains/DEV-DOM-055B_SPI Reference Plane与Pad_Stencils Target开发指导.md#spi-reference-ui>)和[055C](<../06-domains/DEV-DOM-055C_SPI Paste Segmentation与Metrology开发指导.md#spi-paste-method>)提供参数/关系和失效语义。生成器与页面不能自行采纳新Schema或产品限值。

| 当前工作 | 页面必须提供的可执行操作和回馈 |
|---|---|
| P0来源/P1意图 | 选择精确板/钢网/面/实例来源，展示明确印刷意图与缺能力；装配DNP不默认勾成不印刷。未确认选择换语言后保留，只有确认才改变草稿 |
| P2对应 | 焊盘树展开开口子窗口/批准沉积组，原图联动显式映射与几何候选；同名、缺窗口、多目标材料关系保持未决，不给最高分自动通过 |
| P3方法/域 | 分开名义/搜索/量测/参考排除/局部桥W，选目标定位seed/内外点/check及基底材料与台阶来源；值/单位/来源/锁定同时可见。补偿前后只是对照，不覆盖原高度 |
| P4计划/P5试检 | 显示必检×视角/模态与缺口、执行/内存预算；冻结草稿发起试算，结果带发起输入/修订及实际E/U，不被之后参数或新图覆盖 |
| P6差异 | B/L/R在同一耦合组比较来源/值/锁定；材料路线与台阶、坐标与ROI、开口组与分母不能拆开各选一个最优。采纳后依赖失效返回P4/P5，不沿用旧验证徽标 |
| P7交接 | 原035保存/审批/发布/激活分开投影，CAS冲突保留本地修改；保存未知查原操作，不另造发布。没有能力/资格时可保存合法未决草稿，不宣称生产就绪 |

保留已发布/原生产只读文档与当前工程草稿、试算快照及取消记录；生成R不直接写L，来源同值换修订仍重核。禁止以拖动参考面使体积接近100%作为自动找底。批量动作固定目标全集/草稿修订并预览未适用与失效范围，取消后的旧回调不得覆盖新预览；A→B→A有不同请求代。

P3/P4补充055A路线与图案/曝光组来源、Actual能力/同步及峰值预算；修改后标明参考/量测依赖失效，P5试算绑定原帧组与逐目标支持，不能逐相位混曝光或自动换H0/H1/H2。

左目标/来源树、中部原图和覆盖、右侧分组参数、底部差异/恢复沿§11构图。常用“定位问题、预览影响、试算、查看差异”保持可见，高级拟合/统计/预算逐级展开；色彩配文字。语言/主题/停靠恢复不丢输入、改变草稿或触发试算。失写权限后仍可保留本地草稿只导航离开；保存/丢弃等写操作由应用重新核权，不能靠disabled按钮实现安全。

上述要求已有§13对应的合成HTML操作链；真实导入、生成器、ROI编辑、公共端口及WPF仍未实现，不能将原型作为完整产品页面验收。


<a id="spi-programming-interactive"></a>

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

## 13. 可操作工程草稿、差异与恢复 — 2026-09-29

[SPI原型](../../prototypes/UI-PCS-018-019_spi.html)的“快速编程”对应本页；生产、方法和历史共用布局但保持独立身份，见[UI018§13](UI-PCS-018_SPI_Production_Workbench.md#spi-interactive-workspaces)。本轮合成操作不调用真实视觉、035保存、发布/激活或设备端口；方法公式与阶段权威仍在055A/B/C/D及PG014，不在页面重定工艺。

### 13.1 P0–P7连续任务

| 阶段 / HTML锚点 | 输入、实际操作与返回 |
|---|---|
| P0 `source/actual/freeze` | 制造资料、参考图、旧程序三种合成来源均固定修订、TOP、mm、5pad/7开口和实际输入夹具。来源同值换修订或Actual变化使P0重新固定，依赖候选/覆盖/试算/审阅失效；不凭内容相同复用资格 |
| P1 `intent/confirm-intent/bind-design` | 待选意图与确认分离，切语言/主题保留待选。参考图必须绑定独立DEMO-DESIGN/r1，不能从图反推制造全集。DNP仍印刷，TP1有明确非印刷意图；可显式选择2D面积用途或面积+材料体积必检 |
| P2 `mapping/confirm-mapping` | 表与板图保留pad→子窗/沉积组，图上可选择稳定目标；未决对应禁确认。同名跨实例不合并，桥组件不强拆一对一 |
| P3 `edit/generate` | 编辑搜索外扩/路线/基底/域组成的本地整组，生成R只创建候选。黄色搜索框随外扩展示，不改变名义pad或开口。未实现真实拖动ROI、导入器或生成算法 |
| 初次P6 `choice-*/reason-*/lock-*/apply-merge` | 比较B/L/R两个完整耦合组，来源/字段/值/单位/锁定和理由可见，JSON只在高级诊断。采纳完成形成新草稿修订并返回P4；不借首次差异预览授最终审阅资格 |
| P4 `confirm-plan` | 明示5pad/7开口义务与路线/实际输入。当前可完成合成3D试算只绑定H0、铜基底和材料窗口；H1/H2、未绑定台阶基底或几何积分不能替代材料体积义务。计划确认不等于输入可测 |
| P5 `validate/trial/cancel` | 检查当前意图、量定义和实际输入后冻结完整草稿/来源/Actual/请求ID。650ms仅模拟在途；发起新试算即撤销旧试算/审核/交接资格。缺必需3D、冲突、无基底资格不能取得通过，但可保存未决草稿 |
| 最终P6 `ack-review` | 只有当前修订试算和计划有效、意图一致时记录工程审阅；旧回调/旧修订不授资格 |
| P7 `save/handoff/confirm-handoff` | 保存、试算、审阅分别显示修订，当前性和写权限再次检查后才记录模拟交接。此记录不是审批、发布、激活或生产就绪 |

### 13.2 三方差异和依赖一致性

“采集/参考/方法/域”组绑定H0/H1/H2、物理基底、材料E_F∪B或几何E_geom、搜索外扩、方法修订和来源；“目标/意图/分母”组绑定完整pad/开口集合、印刷必检意图、名义分母和来源。一个组不可逐字段混拼，保留整个L也不能与P1确认意图不一致。合并、配置检查、试算、最终审阅和交接处理器均重核，不能通过UI取消disabled绕过。

实际冲突例：B外扩0.10mm，人工L改0.12，生成R为0.15，三者各自带方法/来源；这些是合成比较值，不是默认工艺参数。冲突或主动舍弃R须填写理由。锁定即使值等于B也保留人工意图；锁定组只能保留L，恢复继承令旧候选陈旧，须重新生成。已保存的参数、生成基线和锁定理由一起保存或恢复，不只回退可见字段。

### 13.3 保存、取消与离页

保存使用独立的预期/远端CAS代次。模拟远端冲突只改代次、不改值；保存被拒仍保留本地参数，查看远端后显式更新预期并撤销旧验证。真实远端值有变化须回原035/三方差异，原型没有实现远端合并服务。“保存应答丢失”冻结原操作ID、快照和实际已保存修订，阻止再次提交；“查询原保存”仅读取该操作，可在只读状态恢复已发生保存的回执，不取得新写权。

请求取消后保留在途对象，等待定时任务模拟退出后写独立取消记录，不当作试算通过。角色/权限变化及保留草稿跨区离开均先保留用户的新选择并请求取消；晚到只归原发起快照，不跳回原页、不释放PermissionDenied。请求号和草稿时钟单调，恢复已保存草稿也不重用旧代。

未保存离页提供“保存并离开 / 恢复已保存草稿并离开 / 保留草稿并离开”。无写权限、取消排空或保存未知时前两者禁用，处理器再次核验；保留只导航，不保存、不丢弃。恢复已保存语义后撤销P0确认和全部依赖验证；未知保存先查询原ID。刷新将丢失内存演示草稿/新记录，不声称跨重启恢复。

本页实际采用同一三语资源表；表单输入、未确认意图、冲突理由、弹窗主题/语言变化均不隐式确认。Alt+2进入编程，Tab循序进入来源/阶段/参数/差异/恢复，对话框约束焦点。真实WPF使用宿主语言服务、DevExpress Dock/Layout/Editors与原035服务；不把本页JS状态抽成公共库。

### 13.4 共用证据和剩余验收

当前及历史HTML hash、已复核输入、版本化脚本/报告、实际截图与各自验证范围只在[UI018§14唯一入口](UI-PCS-018_SPI_Production_Workbench.md#spi-interactive-evidence)，不另造同义报告。两页接收说明为2.3.2-prep、DocMapped/DesignReview，两项确定缺陷的退修及定向验证见[UI018§14.1](UI-PCS-018_SPI_Production_Workbench.md#spi-interactive-rework)，两个指定反例已独立短复测接收；HTML字节未再变化，旧完整套件结果仅绑定退修前candidate04。

原型已实际操作合成来源/意图、对应与搜索域预览、B/L/R、锁定/理由、必检缺口、取消/迟到、CAS与Unknown、只读离页、固定历史。尚缺真实资料导入/ROI编辑/生成器、完整P3数值/来源/预算编辑、批量多对象应用与逐项错误、实际多路线采集和量测、035合同/持久化/权限、正式审批/发布/激活、真实WPF/DPI/UIA及产品验收。连续面积分位按C1.1.3与031§11引用为独立量，当前无对应运行值；不妨碍已有离散算例和页面交互评审。
