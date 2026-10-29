# Program Editor — PageContract 实施规范

> 2026-09-27 平台归位：当前职责与范围按[平台设计基线](<../../../00-baseline/PLATFORM-DESIGN-BASELINE.md>)及[所属指导目录](<../../README.md>)绑定。本页保留原ID与细化内容；原状态 `ImplementationSpecificationReady` 仅作历史记录，精确契约/Owner/参数未获批前不作为生产实施准入。
- 文档 ID：`UI-PCS-003`
- 版本：`2.1.0`
- 状态：`DocMapped`
- 技术路线：WPF + DevExpress
- 架构基线：`ARCH-PCBA-VISION-001 v0.5.3`

## 1. 页面职责

Program/目标编辑。输入：`Draft Program/TargetSet/Library`；输出/投影：`目标、方法、覆盖、未决项`。页面不是事实权威。

## 2. 工作台布局

`TreeList + Document workspace + Inspector + diff preview`

推荐利用 DevExpress Docking/Layout/Document/TreeList/Grid/Editors/MVVM/Command/Workspace 能力，而不是把 WPF 原生控件逐一替换为同名控件。

## 3. 八态

`Ready / Busy / Empty / Stale / Blocked / RecoverableError / PermissionDenied / Completed` 必须分别定义：显示内容、允许的 Command、恢复动作、AutomationId、审计需求。

## 4. Command 规则

- 所有会改变生产配置/质量状态的 Command 必须进入 Application Port；
- UI 只能发送 Command，不直接修改 Store；
- 批量动作必须显示影响对象数、跳过对象和失败原因；
- 发布/回滚必须显示版本/hash/依赖差异；
- 阻断必须能从 UI 一键跳到证据/原因。

## 5. 高性能视觉交互

- 2D/3D viewport 只消费不可变 frame/overlay DTO；
- 大图使用 Tile/Pyramid/LOD + visible-region cache；
- 叠加层按 z-order 和 selection state 管理；
- 交互线程不执行高成本 HALCON；
- 拖动 ROI 时先本地预览，提交后进入受控 Command；
- 选中缺陷/量测时必须能同步定位到原始证据。

## 6. 键盘与人因

高频任务必须支持键盘完成；Review 支持 next/previous/accept/reject/defer；Program 编辑支持 focus order 和 batch apply；每个快捷键必须有冲突检测。

## 7. UI Automation

关键控件必须有稳定 AutomationId；八态、异常、关键 Command、结果单元格都需要 UIA 验证。三语/DPI/最小窗口尺寸必须在真实 WPF 环境验收。

## 8. 安全

权限校验在 Application/Domain 层重复执行；UI 隐藏按钮不是权限控制。PermissionDenied 页面必须解释“需要什么权限/为何被拒绝”，但不得泄露不应看的客户数据。

## 9. Acceptance

- 首屏能在 3 秒内让受训操作员回答”当前对象/当前状态/结果/下一步”；
- 正常/Busy/Blocked/Error 均有可执行下一动作；
- 视觉/3D操作无明显拖动卡顿，具体帧率/延迟以目标 PerformanceProfile 为准；
- AutomationId、键盘、DPI、本地化、恢复、权限全部有测试证据；
- 不存在 UI 对生产事实的第二写入口。

### 人因验收（2026-10-29）

按 [DEV-UI-045](../05-ui/DEV-UI-045_操作员工作流简化与人因开发指导.md) §7 要求登记本页面支持的典型流程人因指标实测。

| 流程 | 人因指标验收 |
|---|---|
| **编程流程（新建程序）** | 实测 §7.1 七项指标 + 样本量 + 离散度；与人工基线 T1 对比须满足 §7.5 六项可比性前提；目标值来自批准 Profile；失败/未决归类明确 |
| **编程流程（基于旧程序）** | 同上，但典型对象规模含差异项数量；目标差异显示完整且可点击定位 |
| **批量修改参数** | 步骤数、批量预览耗时、错误恢复动作数实测；预览集合冻结且 before/after 可见 |
| **草稿校验与提交** | 校验耗时、错误定位步骤数、冲突解决动作数实测；三值比较(B/C/I)可见且本地输入保留 |

**强制要求**：每个实测值必须附样本量与熟练度档位；未采集时显式写”未采集”，禁止留白或用竞品数据填充。与人工基线对比时，§7.5 六项前提**全部满足**才可判定”优于人工”，否则标”不可比”。目标值为 `TargetPending` 时可测量并报告，但不得判定”达标”。

**假阳性关注点**：批量预览显示”100 项成功”但实际只处理了可见的 20 项；草稿保存成功但校验失败未提示；CAS 冲突时只显示”保存失败”无三值比较。

## 10. Page-specific freeze

**页面角色：** `Program Editor`

### 关键 Command

`AddTarget` · `EditMethod` · `BatchApply` · `ValidateProgram` · `PreviewImpact` · `SaveDraft` · `SubmitForApproval`

上述 Command 只定义 UI 意图；实际权限、Owner 和副作用必须由 Application Port/State-Owner Contract 决定。

### 关键 Query / 对象

`InspectionProgram` · `TargetSet` · `CoverageSpec` · `ParameterProposal`

### 页面硬边界

['Draft-only editing; no Release side effect until approval']

### 页面完成条件

- 每个关键 Command 都能映射到 Application Port、Permission 和审计事件；
- 每个关键 Query 都能定位到唯一事实/投影来源；
- 八态都有页面特定的下一动作；
- AutomationId、键盘、DPI、本地化、异常恢复和 UIA 均有可执行测试；
- 页面无法通过视觉绑定、ViewModel 或布局恢复直接修改生产事实。

## 11. 本页视觉与连续操作设计（2026-09-27）

视觉Token、主题、字体、间距、图标、动效与双验收统一引用[DEV-UI-040](<../05-ui/DEV-UI-040_WPF+DevExpress Design System开发指导.md>)。本节为设计要求，未宣称已有获批效果稿或真实WPF验收。

**构图：** 左侧目标/方法树，中间板图与目标预览，右侧分组参数，底部校验错误及变更差异。主动作位置固定，数值/单位和状态对齐，面板边界与选中细节遵循统一主题；用Dock/Document组织工作区，用Grid/Tree处理目标和结果，用分组Editors展示参数，避免单页随意拼控件。

**高级交互：** 目标筛选与批量选择联动；参数变更预览显示受影响对象数、跳过项及原因，草稿支持撤销。异步图像/数据载入使用目标身份和请求版本校验，取消旧请求后迟到结果不覆盖新选择；效果过渡不延迟实际状态变化。

**高频任务：** 选择目标→编辑方法→批量预览→校验→保存草稿→提交审批。本页已列Command只表达意图，动作权限/幂等/Owner在原Application Port验证；不增加同义端口或把ViewModel当事实写入者。

**失效与恢复：** 引用资料变更使草稿陈旧；展开差异后重新绑定与校验；禁止一键跳过缺项发布。

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

**拟验收断言：** 筛选后批量范围必须可见且与预览一致；编辑当前运行所用程序只生成新草稿，不改运行快照。另在真实WPF完成三语、100/125/150%DPI及产品最小窗口、键盘完整路径、稳定AutomationId、主题切换、Dock/浮窗恢复、慢加载、连点/取消、关闭释放；精美视觉按DEV-UI-040的六项评审单独通过。上述是待执行验收，性能数值与分辨率仍由页面Profile冻结。

<a id="program-runtime-page-flow"></a>

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

## 12. 本页程序生命周期操作细则

**本页职责：** 编辑目标/方法/输入及保存草稿，核心[PKG-035 §6.1](../../packages/PKG-035_ProgramPackage.md#program-lifecycle)，操作流程[DEV-UI-043 §8](<../05-ui/DEV-UI-043_Program/Recipe编程工作台开发指导.md#authoring-release-operations>)。草稿、正在验证的修订、当前机台版本分开显示；UI-PCS-004承担后续发布任务。

批量Apply固定预览集合，显示before/after、单位、跳过与冲突；点击错误行联动目标树/视觉/参数焦点。CAS失败打开B/C/I比较且保存本地输入，删除目标导致必检/ROI/方法悬空时整笔拒绝。验证列表显示请求总数、有效/无效/未执行与过滤后行数，不能以可见行数作通过率。新修订出现后旧验证完成只作为历史，不能刷新主状态为当前已验证。

拟验收序列：A选H1/H2并预览→B改H2→A提交冲突→A看到三值且原输入保留→解决后重新验证→保存新修订，生产中的板仍用原r1。另验预览后改变筛选、取消后晚到、关闭重开草稿；AutomationId按本页既有命令/对象身份冻结，不以行号定位。没有新增发布快捷键或生产事实写入口。
