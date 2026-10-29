# 视觉/3D工作区与ROI交互接入指导

- 文档 ID：`DEV-UI-042`；版本：`1.3.0-appmap`；状态：`DocMapped`。
- 适用范围：产品2D/3D工作区、证据查看、ROI/测量意图与公开模块装配。
- Viewport公开API、显示数学、后端路线、资源生命周期、控件及测试的唯一实施权威为[IM-060 viewport](../../../../independent-modules/viewport/DEVELOPMENT-GUIDE.md)。本页维护宿主任务流和产品接入，不另建Viewer/Scene/Session或ROI引擎。
- 生产事实、权限、ROI和量测分别回原Owner；PageContract约束产品页面。各切片成熟度按IM-060及DEV-GOV-010，不从本文DocMapped或原PCBA架构号推断批准、实现或运行资格。

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

所有关键 Command、目标节点、结果单元格、错误状态都有稳定 `AutomationId`。键盘必须可完成高频复判/编程路径；DPI、固定1920×1080验证视口（扣除任务栏/非客户区）和三语文本必须纳入真实验收；不扩展其它分辨率矩阵。

## 7. 视觉 UI 边界

页面/ViewModel和公共投影只消费不可变引用及有界租约，不接收HALCON/AsunImage裸句柄，不拥有生产Decision。内部显示适配可以在明确线程和生命周期内拥有所需native资源；它不能把这些资源泄漏给宿主或从生产缓冲区长期偷借。大图使用已有Frames的tile/pyramid能力，Overlay和命中绑定同一实际呈现的变换快照，详见下文。

## 8. 离线载入与可测试边界

用户要求：无需相机也能载入图片，执行所有输入齐备且可离线运行的功能。离线入口复用批准的帧/高度场、参数、算法、ROI 和渲染契约，不另建一条算法实现或结果权威。

| 场景 | 要求 |
|---|---|
| 文件入口 | 可选择已支持的图像或数据文件，显示来源和离线标识；具体格式、尺寸/位深/通道、批量范围由帧导入契约明确 |
| 有效载入 | 显示图像并可执行缩放、ROI、参数、适用算法、测量与结果查看；以同一输入/参数比较生产软件路径和离线路径的适用结果 |
| 输入缺失 | 只有 2D 图像时不能虚构高度、单位、相机标定或板属性；3D/物理计量所需数据缺失时，明确功能不可执行的原因及需要补充的输入 |
| 运行隔离 | 离线验证不自动发送设备命令、改变生产配方、提交生产判定或放行；工程结果按既有证据边界保存和标识，原文件不被覆盖 |
| 替换与失败 | 载入支持取消；损坏、不支持、过大或不完整文件给出可恢复提示。替换输入前处理未保存编辑，旧结果不得继续冒充新输入结果 |
| 资源与并发 | 解码/计算不阻塞 UI；旧图、帧/高度场及叠加层有明确释放责任，快速连续载入不得出现新图配旧结果 |

离线验收覆盖可离线的完整功能链及错误/取消/重复载入；每项设备或采集时序依赖标明需模拟还是需真实硬件验证。没有物理输入的功能不能靠合成值宣称已验收。实际文件格式、对象所有权、来源标识和提交策略继续落入已有 Contract/PageContract，不在本文定义平行 Schema。

<a id="viewer-execution"></a>
## 9. 独立视口的职责与真实调用

[IM-060 §1–6](../../../../independent-modules/viewport/DEVELOPMENT-GUIDE.md#3-分层和独立交付形状)唯一规定root/factory/session、公开端口、权限、状态与排空。独立测量工具、历史证据页和复判宿主消费同一模块，分别声明读/探针/草稿能力；设备动作、质量放行、结果提交和测量事实留宿主原Owner。

### 9.1 接收、呈现、交互、离开

宿主取得精确源和角色，构造实例预算/权限→Attach或全量Update→核同代源/叠加/标题→接收选择/探针/ROI候选→离开时Unbind并观察原session/root归还。源Owner只归还本消费者借用，不因一个窗口关闭取消其它消费者。具体公开操作及两个Host见IM-060 §4.7/§10–11。

### 9.2 权限和用途贯穿缓存

宿主把当前授权/用途/访问域交模块公开权限端口；显示、探针、导出/候选交付分别检查。缓存命中不授予读取权，撤权/盲审规则按产品Owner执行，界面退订不证明后台原Task退出。恢复仍查原scope/Owner，不新建无限实例绕过未知。

<a id="viewer-coordinate-interaction"></a>
## 10. 显示坐标、命中和数值探针

### 10.1 三套尺度与实际呈现代

源像素中心/外边界、DIP和物理像素的约定、Fit/1:1/指针锚和double矩阵唯一见[IM-060 §7](../../../../independent-modules/viewport/DEVELOPMENT-GUIDE.md#7-2d-显示与坐标实现要求)。应用不得另加0.5、以截图像素代替原采样或以显示旋转更改物理标定。身份、矩阵、层和命中来自同一实际呈现快照。

### 10.2 点选、选区和键盘

[IM-060 §7.6/§9–10](../../../../independent-modules/viewport/DEVELOPMENT-GUIDE.md#9-roi-交互和编辑边界)维护候选排序、手势/capture、编辑能力、焦点和键盘；产品页不绑定自己的几何引擎或Viewer放行快捷键。ROI提交仍由原几何/领域Owner确认。

### 10.3 原值、插值与颜色

[IM-060 §7.4/§7.6](../../../../independent-modules/viewport/DEVELOPMENT-GUIDE.md#7-2d-显示与坐标实现要求)规定原值/mask/支撑与LUT。界面保留原值、插值标签、单位、有效性和缺口；0或未知颜色不能推断PASS。物理标尺需当前原坐标资产，不从显示变换估计mm。

<a id="viewer-2d3d-comparison"></a>
## 11. 二维／三维与多证据对照

[IM-060 §8](../../../../independent-modules/viewport/DEVELOPMENT-GUIDE.md#8-3dlod-和-2d3d-联动)维护3D/LOD/原索引/拾取和多源联动；实际设备/标定关联由来源Owner证明。产品声明Actual/Reference/Overview/CurrentFov角色，纯2D或无缺陷Item仍可显示原图；缺高度/映射/同期依据时说明不可用，不造3D测量或按UTC猜同期。

<a id="viewer-resource-lifecycle"></a>
## 12. 分块加载、缓存与停止

有界TileRange、加载顺序、原Task、backend/Presenter借用、独立关闭槽和实际归还只见[IM-060 §3.6/§4.6/§6/§7.5](../../../../independent-modules/viewport/DEVELOPMENT-GUIDE.md#6-线程取消超时和资源排空)。源缓存归image-frame；显示专有CPU/GPU/Overlay/UI副本分别计费，不能重复退款共享backing。应用保留原root及回执到归还确认，不用窗口关闭、Dispatcher空队列或移交Accepted替代ResourcesReleased。

## 13. 导出、布局、独立接入与验收

宿主导出Owner接收模块typed导出意图，未装配与无权限分别显示；截图只是显示投影。产品工作台组合见[UI013](../../../guidance/14-page-contracts/UI-PCS-013_Evidence_Viewer.md#viewer-specific-operations)，可嵌入控件/Binding/三语/布局/键盘UIA唯一见[IM-060 §10](../../../../independent-modules/viewport/DEVELOPMENT-GUIDE.md#10-可选-wpfdevexpress-ui-契约)。布局只保存合法视觉偏好，不存token、像素、Claim或质量权利；实际固定1920×1080/WPF/资源压力/产品任务及现场验收仍须分别执行，不从文档映射宣称通过。
