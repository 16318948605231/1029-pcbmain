# DevExpress 与 UI 工作台官方研究基线
- 文档 ID：`REF-004`
- 状态：`Reference`
- 版本：`2.0.0`
- 用途：实施研究输入，不改变 Asun 架构权威

> **2026-09-18 官方版本核验：** DevExpress 文档当前列出 v25.2–v26.1 支持 .NET 10；WPF `DockLayoutManager` 当前文档为 v26.1，并支持 Docking、Layout 保存/恢复和 MVVM。实际项目仍须以仓库锁定的 DevExpress patch/package 版本验证具体 API。来源：https://docs.devexpress.com/WPF/401165/dotnet-core-support 、 https://docs.devexpress.com/WPF/DevExpress.Xpf.Docking.DockLayoutManager 、 https://docs.devexpress.com/WPF/403213/mvvm-support 。

## 1. 官方 DevExpress 能力

- DockLayoutManager：https://docs.devexpress.com/WPF/DevExpress.Xpf.Docking.DockLayoutManager
- MVVM Support：https://docs.devexpress.com/WPF/403213/mvvm-support
- Layout persistence：https://docs.devexpress.com/WPF/7059/controls-and-libraries/layout-management/dock-windows/saving-and-restoring-the-layout-of-dock-panels-and-controls
- GitHub WPF demos：https://github.com/DevExpress/demos-wpf
- MVVM Docking / IMVVMDockingProperties：https://github.com/DevExpress-Examples/wpf-docklayoutmanager-use-imvvmdockingproperties-to-build-dock-ui-with-mvvm
- LayoutAdapter：https://github.com/DevExpress-Examples/wpf-docklayoutmanager-use-layoutadapter-to-build-dock-ui-with-mvvm
- Complex Dock UI：https://github.com/DevExpress-Examples/wpf-docklayoutmanager-create-a-complex-dock-ui
- Visual Studio-like Dock UI：https://github.com/DevExpress-Examples/wpf-docklayout-manager-build-a-layout-similar-to-visual-studio

## 2. 本项目吸收规则

官方资料证明的是控件/框架能力；不证明本项目页面已经实现，也不替代实际 DevExpress 版本的 API 验证。研发时优先验证 Docking、DocumentGroup、TabbedGroup、AutoHide、Layout persistence、MVVM command/service wiring，然后才设计具体页面。

## 3. 禁止

不得因为控件存在就堆叠复杂面板；页面必须从操作员任务、数据关系、状态、异常恢复和证据追溯出发。


## 4. GitHub 研究许可证边界

DevExpress GitHub Examples 只用于公开示例研究，不自动授予将示例复制进入产品的许可。任何引入均须按实际仓库/包附带许可证、版权声明、依赖树和分发条件单独核对；研究结果不改变 Asun 的 Contract、Owner、Acceptance。
## Research Evidence / License / SPDX

官方 DevExpress 资料及公开示例仅作为 Research Evidence。引用时记录固定文档 URL/版本/访问日期；示例代码是否可复制必须依据实际示例仓库 License/许可证与 SPDX 信息单独核对，不能把官方示例视为自动获得产品代码授权。


边界：外部研究内容**不作为本项目生产实现权威**，不得覆盖内部 Contract/Schema/Qualification 规则。
