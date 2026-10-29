# Review/Rework/Quality工作区开发指导

> 2026-09-27 平台归位：当前职责与范围按[平台设计基线](<../../../../../00-baseline/PLATFORM-DESIGN-BASELINE.md>)及[所属指导目录](<../../../../README.md>)绑定。本页保留原ID与细化内容；原状态 `ImplementationSpecificationReady` 仅作历史记录，精确契约/Owner/参数未获批前不作为生产实施准入。
- 文档 ID：`DEV-UI-044`
- 版本：`1.0.0-prep`
- 状态：`DocMapped`
- 架构基线：`ARCH-PCBA-VISION-001 v0.5.3`
- 适用范围：复判、证据、缺陷、返修、处置、质量统计
- 直接依赖：`DEV-PLT-012`, `DEV-UI-041`
- 主要输出：证据联动、批量操作、键盘 workflow、审计

>
本文均以 `ARCH-PCBA-VISION-001 v0.5.3` 为架构输入。该架构当前仍为候选基线/DocMapped，未因本开发准备包而自动获得架构批准或生产资格。若本包与未来获批架构、既有权威 Schema、状态/Owner 规范或实际仓库实现冲突，以获批权威资产为准，并必须登记冲突后再实现。


## 统一实施规则

1. **单一权威**：架构文档负责关系与边界；Schema 负责数据结构；状态/角色规范负责状态与 Owner；PageContract 负责 UI 行为；本开发指导负责实施语义、禁止路径、算法选择、性能、测试与验收；Validator/Test/Manifest 分别负责机器校验、验证和交付快照。
2. **不得复制第二套事实**：不得在产品目录、`spi/`、ViewModel、数据库或临时 JSON 中建立与既有 Schema/状态机/Owner 平行的定义。
3. **事实与投影分离**：UI、报告、统计、质量中心、AI 解释均不得成为事实的第二写入权威。
4. **生产副作用后移**：能在离线/Replay/Shadow 完成的验证，不要先绑定真实设备。
5. **所有失败可见**：失败、拒识、覆盖不足、资格不足、配置失效都必须形成显式状态或事实，禁止默认降级为 Success/OK。
6. **性能有预算**：算法、UI、IO、缓存和并发必须在设计时给出预算；不得在最后阶段才测性能。
7. **可回放优先**：能进入 Replay 的输入、参数、模型、库快照、标定、环境和算法版本尽量冻结为可引用资产。
8. **AI 不获得隐含权威**：AI 只能在既定 Contract 和 AuthorityScope 内产生建议/候选或受控 revision。
9. **真实硬件证据单独计门**：没有 HIL/实机/Golden Sample 证据时，文档状态只能为“准备完成/软件可验证”，不能写“生产通过”。

## 1. 设计目标

UI 必须让操作员第一眼看到“当前状态、当前对象、结果、下一步”。复杂性进入上下文，而不是堆成几十个按钮。

```text
状态 → 对象 → 结果 → 下一动作
```

## 2. DevExpress 使用原则

不是把 .NET 控件替换成 DevExpress 控件，而是主动使用 WPF+DevExpress 的工作台能力：Docking、Layout、Grid/TreeList、Editors、Search/Filter、Document/Tabbed Workspace、MVVM、Command、数据虚拟化、可保存布局等。DevExpress 官方 WPF demos 可作为实现研究基线：https://www.devexpress.com/Products/NET/Controls/WPF/。

## 3. 页面八态

`Ready / Busy / Empty / Stale / Blocked / RecoverableError / PermissionDenied / Completed` 必须显式设计，不得以禁用按钮或空白代替业务状态。

## 4. 高保真工作台骨架

```text
┌────────────────────────────────────────────────────────┐
│ 产品 / 板号 / Recipe / Station / Overall Result / State│
├─────────────┬───────────────────────────┬──────────────┤
│ Target Tree │ 2D/3D Viewport             │ Inspector    │
│ Search      │ ROI / Measure / Evidence   │ Properties   │
│ Filter      │ Overlay / Coordinate       │ Parameters   │
├─────────────┴───────────────────────────┴──────────────┤
│ Timeline / Defect / Evidence / Log / SPC / Next Action │
└────────────────────────────────────────────────────────┘
```

## 5. 操作流程

默认路径尽量是“自动带出 → 只让用户处理异常/需要确认的项”。高级参数采用渐进披露。批量动作必须提供影响范围和差异预览。任何会改变生产配置的动作必须有明确的 Draft/Validate/Approve/Release 状态。

## 6. UI 自动化

所有关键 Command、目标节点、结果单元格、错误状态都有稳定 `AutomationId`。键盘必须可完成高频复判/编程路径；DPI、最小分辨率和三语文本必须纳入真实验收。

<a id="review-workstation-commands"></a>
## 7. 复判工作站的接入与命令隔离

复判控件通过[044唯一机制](../../../../packages/PKG-044_Review.md#review-transaction-flow)和[UI005完整操作](../../../14-page-contracts/UI-PCS-005_Review_Workspace.md#review-operator-flow)接入。页面不复制Queue/Claim/Decision Store，不因嵌入机台HMI便取得设备动作权；独立站不直开机台数据库。命令绑定当前Case/Item/原证据及期望修订，所有异步结果带选择代。

选择意见只改草稿，提交才产生独立人判；批量赋值和多项草稿提交分开。Claim过期时禁止新提交，但此前成功回执仍可在当前访问权限下查回。后台续租与提交串行协调，不能换代后悄改原请求。未知状态、未发送草稿和已提交意见各自保留，关闭页面不虚构回滚。

可选返修页由产品组合实际动作/材料、板身份/位置和新尝试关系；只读质量页与原最终处置Owner分离。图像/3D控件、原ROI补标和参数编辑复用各独立包，HUD/主题/语言沿宿主注入，不另造全局当前板。
