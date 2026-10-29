# DevExpress 高阶能力使用矩阵

> 2026-09-27 平台归位：当前职责与范围按[平台设计基线](<../../../00-baseline/PLATFORM-DESIGN-BASELINE.md>)及[所属指导目录](<../../README.md>)绑定。本页保留原ID与细化内容；原状态 `Normative` 仅作历史记录，精确契约/Owner/参数未获批前不作为生产实施准入。
- 文档 ID：`DEV-UI-046`
- 版本：`2.1.0`
- 状态：`DocMapped`
- 技术基线：WPF + DevExpress 25.2.3；按用户决定采用，不验证依赖或授权

## 1. 目标

UI 标准不允许“把 WPF Button 换成 DevExpress Button”作为完成标准。必须从工作台、信息密度、数据操作、布局持久化、MVVM、批量操作和上下文交互层面使用 DevExpress 的强项。

## 2. Capability → UI responsibility

| DevExpress capability | Asun usage | 禁止用途 |
|---|---|---|
| DockLayoutManager | 主工作台 docking/document/panel 管理 | 承载业务状态 |
| LayoutGroup/LayoutPanel/DocumentGroup | 构建工程化 workspace | 用大量绝对坐标堆页面 |
| GridControl/TreeList | 结果、目标树、批量操作、虚拟化数据展示 | 作为事实 Store |
| Editors | 参数编辑、验证状态、单位/范围呈现 | 绕过 Contract 的自由字段 |
| MVVM support | Command/Query/Service wiring | ViewModel 直接写 Store |
| Layout persistence | 用户/角色布局偏好 | 恢复布局改变生产配置 |
| Contextual panels | Inspector/Evidence/Diagnostics | 隐藏关键安全状态 |
| 下拉命令 + PopupMenu/Flyout 交互 | 组织关联次要命令、减少占用 | 隐藏关键命令、增加无意义步骤 |
| SuperTip | 解释作用、限制、快捷键与恢复 | 唯一承载关键错误/安全状态 |
| DevExpress 状态栏 | 窗体底部状态、进度与提示 | 用多枚 Label 拼接假状态栏 |

DevExpress 当前文档说明 DockLayoutManager 支持 docking、layout 保存/恢复以及 MVVM；官方 GitHub 示例展示 `IMVVMDockingProperties`、`LayoutAdapter`、复杂 Dock UI、浮动/自动隐藏和 Visual Studio 类工作区，可作为实现研究输入。

## 3. UI performance rule

任何高成本图像/3D/数据库计算不得在 UI thread 执行。Grid/TreeList 等大数据展示使用分页/虚拟化/增量查询策略；viewport 与证据加载必须可取消。

## 4. Visual design rule

“炫技”与精美是明确目标：统一主题与细腻排版、精致图标和动效，结合状态可视化、2D/3D联动、证据对照、批量预览、异常聚焦、布局持久化和流畅反馈。视觉、交互效率和任务正确性均须独立验收；具体规范见DEV-UI-040第10–12节。

具体提示、语言和验收规则引用 DEV-UI-040；本矩阵描述用途，具体类/属性按 25.2.3 WPF 文档查阅。
