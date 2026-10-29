# 全量功能与 PageContract 一致性审计
- 文档 ID：`AUD-064`
- 版本：`1.0.0`
- 状态：`PASS_WITH_EXTERNAL_GATES`
- 审计基线：`ARCH-PCBA-VISION-001 v0.5.3` + `Asun Vision Development Standard v2.1.5`
- 范围：除硬件具体 SDK 外的全量开发准备文档、开发步骤、FunctionSpec、PageContract、工具、权威绑定和语义链路

## 1. 覆盖

逐项检查 69 FS 与 Function Registry、Project/Namespace、CanonicalPort、Guide、PageContract、PerformanceProfile、AlgorithmBaseline 是否一致。

## 2. 页面侧

逐页检查 21 个 PageContract 是否具备八态、Command/Query、权限、AutomationId、键盘、DPI、UIA、本地化、异常恢复，以及生产事实只经受控 Application/Domain 入口提交。

## 3. 特别反例

- FS 的 Registry PageContract 与 AI read order 不一致；
- 页面显示“完成”但后台是 `Unknown/Blocked/NotQualified`；
- 布局持久化改变生产业务状态；
- Review 页面直接改写 Fact；
- 视觉 Viewport 持有 HALCON 原生对象并执行生产判定；
- DevExpress 控件只是普通 WPF 控件的替代，没有任务/数据/状态语义。

## 4. UI 设计原则

所有页面遵循“状态→对象→结果→下一动作”，利用 DevExpress Docking/Document/Layout/Grid/TreeList/MVVM 等能力构建工作台，不以控件数量代替信息架构。
