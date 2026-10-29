# GitHub / DevExpress / Open Source 研究基线
- 文档 ID：`REF-002`
- 版本：`2.26.0`
- 状态：`Reference`
- 日期：2026-09-29（保留历史研究，新增固定源码阅读）
- 用途：实施设计参考，不是本项目权威

## DevExpress WPF

1. DevExpress WPF demos：`https://github.com/DevExpress/demos-wpf`
2. DockLayoutManager + MVVM / IMVVMDockingProperties：`https://github.com/DevExpress-Examples/wpf-docklayoutmanager-use-imvvmdockingproperties-to-build-dock-ui-with-mvvm`
3. LayoutAdapter：`https://github.com/DevExpress-Examples/wpf-docklayoutmanager-use-layoutadapter-to-build-dock-ui-with-mvvm`
4. DocumentManagerService：`https://github.com/DevExpress-Examples/wpf-docklayoutmanager-use-services-that-implement-the-idocumentmanagerservice`
5. 复杂 Dock 布局：`https://github.com/DevExpress-Examples/wpf-docklayoutmanager-create-a-complex-dock-ui`
6. Layout persistence / upgrade：`https://github.com/DevExpress-Examples/wpf-dock-layout-manager-save-and-restore-the-dock-layout-managers-layout`、`https://github.com/DevExpress-Examples/wpf-dock-layout-manager-upgrade-layouts-between-versions`

**吸收原则：** 借鉴工作区/Docking/MVVM/Layout persistence 的工程方法，不复制业务对象；具体 API 必须按实际 DevExpress 版本验证。

## PCB/AOI 开源参考

- `https://github.com/apertus-open-source-cinema/pcb-aoi`：展示了基于参考板图像进行 PCB AOI 原型化的思路；仓库本身为原型、GPL-3.0，不作为本项目代码依赖。
- `https://github.com/PLD-Projects/AOI`：展示 AOI、Qt UI、视觉模型、多线程和外部运动控制的原型组合；用于对照架构关注点，不作为生产实现来源。

## 许可证规则

第三方代码在引入前必须记录 SPDX/许可证、作者/版权要求、二次分发限制、依赖树和安全状态。研究价值不能覆盖 license obligation。
## Research Evidence

所有 GitHub/开源研究结果必须保存 Research Evidence：固定仓库、commit/tag、路径、访问日期、借鉴点与不采用原因。License/许可证、SPDX、版权声明、依赖树和安全状态是引入前的强制门禁。


## Evidence Audit

本页中的每一项外部结论都是研究证据，而非 Asun 的生产标准。进入实现前必须保留证据记录：固定仓库/URL、commit/tag 或文档版本、源码/章节路径、访问日期、许可证/SPDX、依赖和安全状态、借鉴点、未采用原因以及“证据”与“本项目事实”的边界。


边界：外部研究内容**不作为本项目生产实现权威**，不得覆盖内部 Contract/Schema/Qualification 规则。

## 2026-09-27 平台模块和流水线设计的源码证据

本节支持PLATFORM-DESIGN-001、SM-001/006/018和接口交接设计。实际读取源码、测试、项目依赖和许可证文件；没有构建或执行这些仓库测试，也没有把外部代码加入产品。上文旧链接仅为研究线索，未固定源码的条目不能称已验证实现依据。AsunImage/DevExpress按用户决定不安排依赖或授权核验。

| 来源及固定版本 | 实际读取的源码/测试 | 可借鉴和不采用部分 |
|---|---|---|
| [Prism](https://github.com/PrismLibrary/Prism/tree/358118cd640d9a22ff8cf21c8ad197fa038b7990)，commit `358118cd640d9a22ff8cf21c8ad197fa038b7990` | `src/Prism.Core/Modularity/ModuleCatalogBase.cs`、`ModuleDependencySolver.cs`；`tests/Wpf/Prism.Wpf.Tests/Modularity/ModuleCatalogFixture.cs`、`ModuleDependencySolverFixture.cs` | 借鉴初始化前拒绝重复/缺依赖/环、按依赖排序及对应测试。测试含简单/复杂环、森林、重复初始化；不证明本平台现场可靠性，不引入Prism框架 |
| [OpenPnP](https://github.com/openpnp/openpnp/tree/5bd404cfc70f34103a3ca0fbb6b50c2b465f407c)，commit `5bd404cfc70f34103a3ca0fbb6b50c2b465f407c` | `src/main/java/org/openpnp/vision/pipeline/CvPipeline.java`、`CvStage.java`；`src/test/java/CvStageTest.java` | 借鉴阶段结果/耗时和原生图像释放；测试覆盖参数覆盖及单位/类型转换。其Object/Map工作状态、异常作为结果并可继续的机制不直接采用；不证明工业AOI算法合格 |

依赖/许可证读取：Prism的`src/Prism.Core/Prism.Core.csproj`包含PolySharp、Prism.Container.Abstractions、Prism.Events，目标包含net462/47/8/9/10；根`LICENSE`是带条件的Community/Commercial双许可，不视为无限制MIT依赖。OpenPnP的`pom.xml`体现Java/OpenCV/Swing/JNA及串口等生态，根`LICENSE.txt`为GPLv3文本；本轮仅借鉴设计和验证思路，不复制实现、不引入依赖。未做完整传递依赖安全审核；未来如真正引入再按实际使用范围审查。

官方文档（读取日期2026-09-27）：

- [.NET Generic Host](https://learn.microsoft.com/en-us/dotnet/core/extensions/generic-host)：组合根负责DI/配置/日志与启动停止生命周期；不证明其天然拥有板流/质量状态。
- [.NET Channels](https://learn.microsoft.com/en-us/dotnet/core/extensions/channels)：有界容量、反压和满队列策略。生产完整帧与预览分通道；不能随意选Drop模式丢检测输入。
- [.NET插件教程](https://learn.microsoft.com/en-us/dotnet/core/tutorials/creating-app-with-plugin-support)：AssemblyLoadContext处理加载/依赖，不是运行不可信代码的安全边界。独立DLL也不自动需要动态插件或进程。

这些结论只支撑模块依赖、生命周期、资源和流水线的工程方案。HALCON具体算子、DevExpress具体控件API和设备SDK调用仍在对应实现切片读取目标版本官方资料；本节没有虚构它们的签名或性能。

## 未开发机台的几何、区域与高度处理研究 — 2026-09-27

本节直接服务SM-010/011/012/013/027及PG-002/003/006/011/013/016/019/020/021。研究实际源码与测试，借鉴测量定义、失败条件和验证方法；平台实现使用AsunImage，不增加OpenCV、Open3D或Python生产依赖。没有构建或运行下列仓库，也未证明它们适用于工业计量。三个commit均为访问时固定的开发分支快照，不是本平台选定的稳定发行版。

### OpenCV：连通关系与组件标识

- 固定版本：[opencv/opencv@a0cda081f8d769f40ab2f4904738b4787b44d07c](https://github.com/opencv/opencv/tree/a0cda081f8d769f40ab2f4904738b4787b44d07c)，读取时提交日期2026-09-25；[本地阅读摘取](open-source/opencv_opencv/a0cda081f8d769f40ab2f4904738b4787b44d07c/)。只保留本节消费的源码、测试、构建声明与许可证，并非完整可构建仓库。
- 源码：`modules/imgproc/src/connectedcomponents.cpp`的`connectedComponents_sub1`，第5652行起显式区分4/8邻接、单通道、输入/输出深度及并行分支。实现中的标签序号只是计算结果，不能当制造元素ID。
- 测试：`modules/imgproc/test/test_connectedcomponents.cpp`的`missing_background_pixels`（227行）验证全前景图的背景质心为NaN；`single_row`/`single_column`（686/716行）在多算法和4/8邻接下先规范化标签再比较区域；另读取`spaghetti_bbdt_sauf_stats`的跨算法统计断言。
- 设计落点：桥连/残胶/多孔候选必须保留邻接定义和目标关联；比较区域支持域、统计量、几何对应，不依赖标签排序。空背景或空前景不能制造坐标(0,0)的有效缺陷；边缘单行/单列仍需处理。不同工艺的“桥连”由其目标邻接图定义，不能由公共连通域计数直接判定。
- 依赖/许可证：根`LICENSE`为Apache-2.0；源码文件头及第三方声明仍须保留。根`CMakeLists.txt`存在IPP、TBB、OpenCL、CUDA等配置分支，不把一次算法阅读等同完整依赖审查。未引入任何实现，不照搬其默认并行策略或版本特有的CV_Bool接口。

### Open3D：参考平面资格与可重复性

- 固定版本：[isl-org/Open3D@b6c5e196384ad71e75b6e6f9c5da22d046221f1d](https://github.com/isl-org/Open3D/tree/b6c5e196384ad71e75b6e6f9c5da22d046221f1d)，读取时提交日期2026-09-16；[本地阅读摘取](open-source/isl-org_Open3D/b6c5e196384ad71e75b6e6f9c5da22d046221f1d/)。
- 源码：`cpp/open3d/geometry/PointCloudSegmentation.cpp`，`SegmentPlane`第157–278行检查概率、最小采样数和输入点数；跳过零平面候选，按距离选内点、重拟合并返回模型与内点。源码预先生成随机样本以减少线程调度对采样的影响；这不是整个本平台计算天然确定性的证明。
- 测试：`cpp/tests/geometry/PointCloud.cpp`的`SegmentPlaneKnownPlane`、`SegmentPlaneSpecialCase`、`SegmentPlaneDeterministic`（1374/1392/1413行）：解析平面内点、概率边界、固定随机种子重复调用。测试中使用的公差、点云和采样参数只属于该测试。
- 设计落点：基底候选必须记录拟合域、法向、内点比例、残差、样本分布、随机配置及原始点映射；胶点、针顶或凸起不能因占多数而成为板基底。几何拟合成功与可作工艺基准分开；跨线程结果比较按批准的数值容差，业务目标ID保持稳定。SM-012提供拟合候选，PG选择其物理参考面。
- 依赖/许可证：实际根`LICENSE`为MIT（GitHub API的NOASSERTION不能代替阅读）；`CMakeLists.txt`含Eigen3/TBB系统依赖选项、GUI/CUDA/ML构建分支。未做全量传递依赖或安全审核；不引入C++点云运行时，不复制其阈值，也不把降采样点云直接当体积积分输入。

### scikit-image：物理尺度与骨架语义

- 固定版本：[scikit-image/scikit-image@533b7694d2004ae84e49e2cfd0bcfc5f8e562f22](https://github.com/scikit-image/scikit-image/tree/533b7694d2004ae84e49e2cfd0bcfc5f8e562f22)，读取时提交日期2026-09-24；[本地阅读摘取](open-source/scikit-image_scikit-image/533b7694d2004ae84e49e2cfd0bcfc5f8e562f22/)。该版本实际实现位于`src/_skimage2`，不把旧路径的转发模块误称算法源码。
- 源码：`src/_skimage2/measure/_regionprops.py`的`area`（456行）按像素面积缩放，`feret_diameter_max`（530行）使用凸包边界与物理spacing，`perimeter`/`perimeter_crofton`（691/698行）显式拒绝非等距spacing。由此不能推论所有属性都接受同一种尺度补偿。
- 测试：`tests/skimage2/measure/test_regionprops.py`的`test_feret_diameter_max_spacing`与`test_perimeter`/`test_perimeter_crofton`（184/910/924行），覆盖非等距、边界离散化、周长定义和不支持的尺度。借鉴的是定义与边界，不能把这些离散周长当亚像素计量真值。
- 骨架源码：`src/_skimage2/morphology/_skeletonize.py`第18–96行先转bool并选择2D/3D方法；相邻不同灰度可能被合为同一前景。`tests/skimage2/morphology/test_skeletonize.py`的`test_no_foreground`、`test_wrong_ndim`、`test_single_point`、`test_vec_1d`、`test_input_not_modified`覆盖空图、维度、点/细线和不修改输入。已细化到SM-011与PG-016：胶路分支/回环、路径次序、宽度截面必须按设计胶路解析，骨架本身不包含这些工艺含义。
- 依赖/许可证：根`LICENSE.txt`总体BSD-3-Clause，明确另有BSD-2-Clause/MIT文件或函数；重组后的路径不能仅凭旧清单推断全部义务。`pyproject.toml`声明Python>=3.12及NumPy、SciPy、NetworkX、Pillow、ImageIO、Tifffile等；底层部分为编译扩展。只保留研究资料，不作为WPF/.NET产品依赖，不宣称完整许可证/安全审查已完成。

### 从研究到实施的约束

公共模块提供物理单位、有效域、几何候选和质量信息；工艺包持有检测目的、参考版本、容差和缺陷语义；SM-020持有提交后的事实及证据。开源库均没有提供本平台完整的PCB钻孔、钢网、涂覆或THT工业验收实现，不能因为有同名算法就标记机台完成。对应功能的AsunImage公共签名仍按实际实现切片读取，不臆造封装方法。

## 精美工作台与布局恢复的补充依据（2026-09-27）

设计使用已安装DevExpress WPF布局技能的布局分类和边界：Dock工作台与表单布局分开、稳定面板身份、保存/恢复作为视图行为。技能来源版本26.1仅作设计参考；平台仍用25.2.3和本机程序集，不下载包、不核验依赖或授权。当前工具环境没有可调用dxdocs；尝试官方DockLayoutManager与SaveLayoutToStream文档页返回403，未声称已读取25.2.3官方API。具体签名待实现切片从可访问官方/本机公开资料核对，不猜测。

实际读取官方GitHub示例[DevExpress-Examples/wpf-dock-layout-manager-upgrade-layouts-between-versions](https://github.com/DevExpress-Examples/wpf-dock-layout-manager-upgrade-layouts-between-versions/tree/bf801b30a0e7cdf6c1e54a708ec324087b758b4a)，commit `bf801b30a0e7cdf6c1e54a708ec324087b758b4a`；[本地源码摘取](open-source/DevExpress_layout_upgrade/bf801b30a0e7cdf6c1e54a708ec324087b758b4a/CS/)。阅读`MainWindow.xaml`中的面板Name、LayoutVersion、LayoutUpgrade、WorkspaceManager；`MainWindow.xaml.cs`中的Capture/Save/Load/Apply及按恢复版本升级Dock/Grid布局；`DXSample.csproj`体现.NET Framework 4.7.2和DevExpress24.2引用。这些属于该样例历史依赖，不是本项目版本选择。

借鉴：布局有独立版本和稳定面板标识，升级按旧版本转换；平台恢复失败回安全默认布局、保留旧布局以诊断，恢复不能改变运行配方或事实。样例的code-behind、相对文件路径和普通按钮不作为本项目MVVM/精美设计规范。不复制代码进产品，未构建运行样例、未取得自动化测试证据，不以此证明25.2.3或本平台真实WPF行为。DevExpress按用户要求不做依赖/授权核验；引用是研究出处。

本轮新增HALCON区域/读码/OCR官方描述的实际核对和限制写在DEV-VIS-021第6节，由PG功能卡直接消费。UI构图、Token候选和动效是本平台设计方案，不能归因于竞品已验证的工业效果。


## .NET有界通道与资源交接的源码核对 — 2026-09-27

直接服务DEV-PLT-014及SM-006/018/025；固定[dotnet/runtime v10.0.0](https://github.com/dotnet/runtime/tree/60629d14374c56f1cb51819049ad1fa529307f8d)，commit `60629d14374c56f1cb51819049ad1fa529307f8d`。[本地所读源码/测试/声明](open-source/dotnet_runtime/60629d14374c56f1cb51819049ad1fa529307f8d/)为研究摘取，不是可构建仓库；不将该runtime补丁版本固定为平台部署决定。

| 实际阅读位置 | 直接证据 | 设计落点和限制 |
|---|---|---|
| `src/libraries/System.Threading.Channels/src/System/Threading/Channels/BoundedChannel.cs`，TryWrite 363–441 | Wait满时false；DropWrite满时调用丢弃回调并true；另两种Drop移除旧项后加入新项 | 生产帧不能依赖true证明数据保留；预览合并需归还被丢租约 |
| 同文件WriteAsync 515–614 | 满队列Wait路径把item保存在待写操作，再串入等待链 | 有界缓冲不等于所有挂起生产者有界；取得数据前限接纳与资源额度 |
| `.../tests/BoundedChannelTests.cs`，TryWrite_TryRead_Many_Ignore 221–239、DroppedDelegateCalledOnChannelFull_SyncWrites 330–361 | DropWrite调用成功但读到仅早先容量内数据；丢弃回调记录实际丢弃数 | 测试数据是int，不验证平台HALCON对象释放；平台须加租约场景 |
| 同测试CancelPendingWrite_Reading_DataTransferredFromCorrectWriter 476–495 | 容量1，42入队，43待写后取消，44待写，最终读42/44，43任务取消 | 用于设计取消/接纳竞争；取消信号不是可以立即释放任何在用图像的证明 |
| 同测试WaitToWriteAsync_AfterFullThenRead_ReturnsTrue 598–613 | 容量1释放一个位置，两个等待者都返回true | WaitToWriteAsync不预留位置，生产包装仍须重试TryWrite/重新等待 |
| `.../src/System/Threading/Channels/Channel.cs` 40–65 | 公共CreateBounded重载与itemDropped委托构造路径 | 直接复用.NET提供能力，仍需平台独立资源协议；不复制BCL源码到产品 |

实际读根`LICENSE.TXT`为MIT，源项目`System.Threading.Channels.csproj`含.NET当前/历史及netstandard多目标、System.Runtime/Threading/Memory等基础依赖，旧目标另有Tasks.Extensions/Bcl.AsyncInterfaces条件分支；测试项目复用runtime公共测试基础。它们不是本平台要新增的第三方依赖包清单。选择方案：采用.NET10已有Channels，外面实现必要的接纳/租约/持久化语义；无需自研通用锁队列，也不新增消息框架满足同进程帧交接。没有构建/执行外部测试，未检查全runtime依赖安全、没有产生产品性能结论。

归档SHA-256（固定字节，不代表执行验证）：
- `LICENSE.TXT`：`cfc21f5e8bd655ae997eec916138b707b1d290b83272c02a95c9f821b8c87310`。
- `src/libraries/System.Threading.Channels/src/System/Threading/Channels/BoundedChannel.cs`：`4798673d97ee37741287c70b7f017b5f962b956b1a9e214b9089e0940a4ee406`。
- `src/libraries/System.Threading.Channels/src/System/Threading/Channels/Channel.cs`：`a794181b1ef99f1ca6d5bb41005edbf8bb9e4cba6a15e4c55de304e6967e6c17`。
- `src/libraries/System.Threading.Channels/src/System.Threading.Channels.csproj`：`02fb31e28199fc7f17b430df79893d26153e127de2b2d182e12bd949c6a543ef`。
- `src/libraries/System.Threading.Channels/tests/BoundedChannelTests.cs`：`765025b2722caed432f1ccbe7bdefb8be7750ef1274791778950cdcbfb16dc70`。
- `src/libraries/System.Threading.Channels/tests/System.Threading.Channels.Tests.csproj`：`d8b8ad306fe00a305b24e17f1b1b297efe1d4d210cf4b5a09e7cbd806ffab913`。


## HALCON学习能力与PatchCore源码比较 — 2026-09-27

服务DEV-AI-060/063和SM-026，以及表面、胶涂、装配异常候选。当前只得出算法/数据/资源设计约束，不宣称开源比HALCON更好，没有下载模型权重、构建、训练或实测。API公共封装尚未绑定，不扫描AsunImage内部。

### 官方HALCON资料的直接观察

实际读取[Anomaly Detection and Global Context Anomaly Detection](https://www.mvtec.com/doc/halcon/2511/en/toc_deeplearning_anomalydetection.html)和[apply_dl_model](https://www.mvtec.com/doc/halcon/2511/en/apply_dl_model.html)的说明；URL版本仅标识所读来源，不变成平台底层版本要求。[章节文本摘取](official/halcon/20260927/halconanomaly.txt)、[算子说明文本摘取](official/halcon/20260927/halconapply.txt)保留本次获取内容，原HTML保留在任务研究暂存。

- 异常检测学习正常图像共同特征；结构异常与逻辑/全局上下文异常的适用任务不同。仅局部划伤/污染可以评估局部异常路线；数量/位置关系不能假设局部热图天然理解。
- 官方“Data for training”说明训练集为无异常图像；评估应含正常并可含异常，逐图有真值标签，像素评估需要相应掩码。本平台要评估漏检必须另外纳入有真值的异常，不能只有良品。
- 输出是图级anomaly_score和像素异常图；二分类/区域仍需阈值。该分数不直接等于工业缺陷概率、尺寸或放行结论。Global Context可区分local/global/combined输出，模型/参数/归一化方法必须与阈值一起固定。
- `apply_dl_model`按模型batch_size处理；本次所读说明明确少于batch_size时补齐，仍按完整batch需要内存，不能用实际输入只有1张来估计1/N显存。输入图可能须按网络要求预处理；DLSample字典是HALCON内部接口约定，不等于可以将原生字典跨平台模块传播。
- `gen_dl_samples_from_images`、`compute_dl_anomaly_thresholds`、`threshold_dl_anomaly_results`在资料中是**procedure**，不能据名字假造同名C# HALCON算子或AsunImage方法。实际接入需查所用公共入口。

### 开源候选的实际读取

固定[open-edge-platform/anomalib v2.0.0](https://github.com/open-edge-platform/anomalib/tree/030c2df604175e07172873f4fca2dba2888ef569)，commit `030c2df604175e07172873f4fca2dba2888ef569`。[本地摘取](open-source/anomalib/030c2df604175e07172873f4fca2dba2888ef569/)只含本次消费的源码/测试/声明。选择固定发布标签作比较，不宣称是当前最新或平台最终选择。

| 文件/位置 | 实际行为与可迁移认识 | 本平台限制 |
|---|---|---|
| `src/anomalib/models/image/patchcore/torch_model.py`105–185、245–326 | 预训练特征、memory_bank、coreset后最近邻，返回图分数与热图；距离实现显式构造query×bank矩阵 | 模型推理资源随patch/bank增长；不能只统计网络参数或ONNX文件大小 |
| `.../lightning_model.py`158–198、209–227 | 默认resize后center crop再ImageNet归一化；训练步骤累计embedding | 默认中心裁剪可能排除板边缺陷，必须保存ROI映射和覆盖；建库也会占大内存 |
| `src/anomalib/models/components/sampling/k_center_greedy.py`94–151 | 随机初始索引、降维后贪心选择并取原embedding | 重建bank受样本/随机配置影响，bank及其来源必须版本化；不能只冻结backbone |
| `tests/integration/model/test_models.py`47–172、195–224 | 多模型fit/test/train/validate/predict/export的API级检查，dummy数据/max_epochs=1；部分模型skip或Mock | 是集成冒烟设计，不证明PCB缺陷效果/导出数值一致，更不证明生产资格 |
| `tests/unit/metrics/test_adaptive_threshold.py`12–25 | 两组合成标签/分数验证F1阈值期望 | F1最佳点不等于满足客户漏检/误报约束；生产阈值不可在线跟随F1自动调 |
| `tests/unit/data/utils/test_tiler.py`51–157 | tile形状、stride/size限制、重叠重组、图像形状/重建一致断言 | 只支持分块重组的测试思路；不证明异常热图接缝/小缺陷保真 |

已读取根LICENSE为Apache-2.0；pyproject声明Python>=3.10，core可选依赖包含PyTorch、timm、Lightning、torchmetrics、OpenCV、scikit-image等，导出/推理另有可选后端。外部权重、数据集、传递依赖和部署体积未完成审查，代码许可证不能自动授予权重/客户图像使用权。未从这些仓库复制产品实现。

**选型方向：** 先评估HALCON适用异常/分割/分类能力，通过AsunImage公共端口接入；anomalib/PatchCore暂作离线候选基线和可复用训练/实验工具的研究对象。只有同样本、同缺陷尺度、同阈值策略的效果/延迟/资源比较表明必要收益，再讨论独立推理适配器或引入依赖，避免自己从零重写PatchCore。不能将Python完整研究栈直接塞进WPF主进程。

阅读摘取SHA-256：
- `anomalib/LICENSE`：`7ae7504c2b7e895c3f61320a389af7fdde68143cd4dfd7941247640b0b62cc76`。
- `anomalib/pyproject.toml`：`4416685d8d49302fe35e430402a000944f9af8d05b66d7723e4ac9c232ccc02f`。
- `anomalib/src/anomalib/models/components/sampling/k_center_greedy.py`：`f3c198430b6ba42127216caa1f827d706ffc441ecc43f7fcf96622244ec5f7a6`。
- `anomalib/src/anomalib/models/image/patchcore/lightning_model.py`：`b2dab78f0cec2ad68e1bc5efaaa70f469268b706139908c1ae24a072c9ee4113`。
- `anomalib/src/anomalib/models/image/patchcore/torch_model.py`：`45d612ccc82235c0c2e102aa78b29e16cfe2c7eeba3de1ab5098f01ea539fc2d`。
- `anomalib/tests/integration/model/test_models.py`：`aad6405d16de01e2cfe0f7b18b67f2b9d78f0ec8916f1d17f5caa8b67eafcbc6`。
- `anomalib/tests/unit/data/utils/test_tiler.py`：`da5897105346ece84556907642fca975d1db4f6ff30beba68aa8bc29d83e1939`。
- `anomalib/tests/unit/metrics/test_adaptive_threshold.py`：`1f563ba7d88cade2ea500bfe5d9ced20c785d59af92d74a2718f0ae241de20f4`。
- `official/halcon/20260927/halconapply.txt`：`cf3f0b82e28bb5a2f7ce07cf0e4ba07a303725ae403be684c1ca2cb8b1c7e1ad`。
- `official/halcon/20260927/halconanomaly.txt`：`2e8ae0205efe025a517bf2e8524ad3e88e0b63221d17f5a38142d6b44636a149`。


<a id="ocr-research"></a>
## HALCON Deep OCR与PaddleOCR源码评估 — 2026-09-27

用户明确要求综合考虑Deep OCR与百度飞桨OCR。本节消费到的设计在[DEV-VIS-021A](../shared-modules/guidance/03-vision/DEV-VIS-021A_OCR与DeepOCR独立能力开发指导.md)，不是另建一份算法规格。结论为HALCON传统/Deep OCR优先，PaddleOCR作为固定版本对照及可选适配候选；尚无工业样本实测证明优劣，也未添加产品依赖。

### 官方Deep OCR直接依据

实际读取[Deep OCR章节](https://www.mvtec.com/doc/halcon/2511/en/toc_ocr_deepocr.html)、[create_deep_ocr](https://www.mvtec.com/doc/halcon/2511/en/create_deep_ocr.html)、[apply_deep_ocr](https://www.mvtec.com/doc/halcon/2511/en/apply_deep_ocr.html)、[get_deep_ocr_param](https://www.mvtec.com/doc/halcon/2511/en/get_deep_ocr_param.html)、[set_deep_ocr_param](https://www.mvtec.com/doc/halcon/2511/en/set_deep_ocr_param.html)。[归档文本](official/halcon/20260927/toc_ocr_deepocr.txt)及同目录各算子文本保留所读内容；URL中版本仅为来源定位，不恢复平台HALCON版本要求。

- create/apply明确detection、recognition、auto分工；recognition以单词裁剪为输入，alignment须模型支持。apply要求byte、1或3通道，自带预处理。
- apply返回字典、词框、字符候选；同时存在预处理图和score map坐标域。字符confidence是softmax值，官方明确未校准且跨模型不可直接比较。
- get参数说明有default/compact模型、CPU/GPU及batch，默认值只是该文档行为，不作为本平台固定参数。recognition尺寸处理会缩放/补边，detection_tiling可避免整图缩小。
- recognition_alphabet_mapping会在解码时改字符，例如O→0，映到Blank可消除字符；改变内部字符表长度会重置相关层并必须重训。这要求原读/映射输出分列、字典与模型一起冻结。
- 章节描述检测/识别组件分别再训练，提供紧裁词或带旋转框真实背景的不同数据路径；procedure、HDevelop示例和算子不能混写为C#公共方法。
- 官方operator目录未列独立clear_deep_ocr，本次同名URL返回404；没有据惯例发明该API。资源销毁须按实际公共对象生命周期实现。未查看AsunImage内部，未对其进行依赖/授权核验。

### 固定开源来源及实际源码/测试

GitHub发布接口于本次读取返回v3.7.0（发布于2026-06-11），标签解析到commit **`b03f46425e8ff4442b268ce449e3eef758146cd4`**。[固定仓库](https://github.com/PaddlePaddle/PaddleOCR/tree/b03f46425e8ff4442b268ce449e3eef758146cd4)，[本地所读摘取](open-source/PaddleOCR/b03f46425e8ff4442b268ce449e3eef758146cd4/)。这是研究固定点，不是平台已冻结运行版本；摘取不构成完整可构建仓库。

| 实际所读位置 | 观察及平台后果 |
|---|---|
| `paddleocr/_pipelines/ocr.py`58–161、318–391 | 包含PP-OCRv3～v6，默认/语言会选择不同模型；指定模型目录时lang/ocr_version被忽略并警告。请求下发PaddleX，需显式冻结模型/目录及依赖，不能把包装文件当全部执行实现 |
| `tests/pipelines/test_ocr.py`25–227 | table.jpg有框/字符串的冒烟、参数转发及v5/v6语言/默认选择断言。不是工业字符准确率、批处理关联或故障验收 |
| `tests/models/test_text_recognition.py`24–47 | 一张textline检查结果键集合，不能证明字典适用/原读准确/置信校准 |
| `ppocr/postprocess/rec_postprocess.py`23–54、146–201 | 字典顺序、空格、去重复/Blank、保留字符分数均值；某些word分组忽略分隔符，不能据分组重建未经批准的料号 |
| `tests/ppocr/test_rec_postprocess.py`43–155 | 法德重音、下划线分词、数字/中文等案例；可借鉴Unicode边界测试，未覆盖本平台O/0错件、原读/建议与工业拒识 |
| `deploy/cpp_infer/src/modules/text_recognition/processors.cc`25–124、127–271 | 通道/尺寸/归一化/宽度限制、CTC解码和均分；字典越界映空格等示例容错不能静默成为平台合法字符，非有限score必须拒绝 |
| `deploy/cpp_infer/src/pipelines/ocr/pipeline.cc`318–446 | 检测→裁剪→可选方向→按长宽比排序识别→恢复排序→低分过滤；缺失结果要映射到必检目标的拒识，不能只保留成功列表 |
| 同C++文件337–345、394–441 | 跳过无检测图得到indices，方向结果使用results[indices[l]]，写识别结果却使用results[l]/dt_polys_list[l]；存在混用原始/压缩索引的静态风险。拟用首图空、次图有字及交错空图做复现；当前未编译运行，不宣称已复现实机缺陷 |
| 同C++文件360–388 | 裁剪/旋转错误分支调用exit(-1)；demo不能直接嵌入生产宿主。隔离worker或改造错误返回须有真实工程验收 |
| `pyproject.toml`及`deploy/cpp_infer/CMakeLists.txt` | Python>=3.8、PaddleX[ocr-core]>=3.7.0,<3.8.0等；C++依赖Paddle Inference/OpenCV及可选GPU/MKL、原生运行库。传递依赖尚未全部审读，不承诺只需一个C#包 |
| `docs/version3.x/module_usage/text_recognition.en.md`及`.../cpp/OCR_windows.en.md` | 官方给出多个模型、训练/导出、ONNX Runtime等引擎与Windows C++参考。精确模型/后端/导出可用性和预后处理必须再核对，文档表格不是.NET10接入或工业性能证据 |

根LICENSE实际读取为Apache-2.0，源码保留原声明。用于商业交付时按选用代码、修改、依赖、权重与数据分别处理许可证/NOTICE和来源；本轮未下载权重、安装运行环境、训练、执行推理/外部测试或复制产品实现。AsunImage/DevExpress不属于本轮许可检查对象。

可直接借鉴或复用方向：检测/识别拆分、模型资产/训练导出、按尺寸组批、Unicode/字符表测试；若对照收益成立优先复用合适开源能力而非自己重写网络。不能直接照抄demo的退出/过滤/默认选型/错误关联或把开源宣传准确率当生产标准。PP-OCRv6的出现说明本轮需评估固定新模型，但不能由“更新”自动推出“更适合丝印/雷刻”。

归档SHA-256用于确认所读字节；不是算法验证结果：

| 来源文件 | SHA-256 |
|---|---|
| [LICENSE](open-source/PaddleOCR/b03f46425e8ff4442b268ce449e3eef758146cd4/LICENSE) | `3840c5c0c61c294264d2dd77b8777be6ddd90121ef4e0e64abcd22edea581d6e` |
| [pyproject.toml](open-source/PaddleOCR/b03f46425e8ff4442b268ce449e3eef758146cd4/pyproject.toml) | `63e8bfa19e197e47649a95dad422bcb09c1d2959367cafd40b0a7f19e4452412` |
| [ocr.py](open-source/PaddleOCR/b03f46425e8ff4442b268ce449e3eef758146cd4/paddleocr/_pipelines/ocr.py) | `fc870f7a7f1b33756020d75c63c6dc0dc04981df1ff46627a040336ead9a9b88` |
| [test_ocr.py](open-source/PaddleOCR/b03f46425e8ff4442b268ce449e3eef758146cd4/tests/pipelines/test_ocr.py) | `936b9f99f88af16d17d4aed53e29c3c1992d9df3d00cc1fa8f292d39f8dac0a9` |
| [test_text_recognition.py](open-source/PaddleOCR/b03f46425e8ff4442b268ce449e3eef758146cd4/tests/models/test_text_recognition.py) | `3c0216b076c713f8359144fc7119f048ffb6d0e7e57255d144df19658b7b994f` |
| [test_rec_postprocess.py](open-source/PaddleOCR/b03f46425e8ff4442b268ce449e3eef758146cd4/tests/ppocr/test_rec_postprocess.py) | `4e79c66d1e765a54763d38ef532be13c6984ac900694ffd21baf14baf6b43bbf` |
| [rec_postprocess.py](open-source/PaddleOCR/b03f46425e8ff4442b268ce449e3eef758146cd4/ppocr/postprocess/rec_postprocess.py) | `a5e5376514991656f7c7977f4a51ac61224ca6939f8ba41bc18e32ce9d15c872` |
| [processors.cc](open-source/PaddleOCR/b03f46425e8ff4442b268ce449e3eef758146cd4/deploy/cpp_infer/src/modules/text_recognition/processors.cc) | `b301934cbda1446d53d3f2a5bd3f9d36646c7fffa298512e12b4f507be52da96` |
| [pipeline.cc](open-source/PaddleOCR/b03f46425e8ff4442b268ce449e3eef758146cd4/deploy/cpp_infer/src/pipelines/ocr/pipeline.cc) | `e4e60ad4caa7af6d0cb8482fbb57fe9bea68abb1c860bc528e63c430b46c1a68` |
| [CMakeLists.txt](open-source/PaddleOCR/b03f46425e8ff4442b268ce449e3eef758146cd4/deploy/cpp_infer/CMakeLists.txt) | `0dd2c56f2b37440357a20ff452cbc04741e09332749156780c1c8eb043c00b1b` |
| [OCR_windows.en.md](open-source/PaddleOCR/b03f46425e8ff4442b268ce449e3eef758146cd4/docs/version3.x/inference_deployment/local_inference/cpp/OCR_windows.en.md) | `26f23a7d21ad782f8e0a1da34599e167ab68526c1485da8e0ed7d753c5c32e8f` |
| [text_recognition.en.md](open-source/PaddleOCR/b03f46425e8ff4442b268ce449e3eef758146cd4/docs/version3.x/module_usage/text_recognition.en.md) | `070b9c4c0d842609f4557e1c0d75a6ca1b89b752785402b6dcad8cef827603ca` |
| [create_deep_ocr.txt](official/halcon/20260927/create_deep_ocr.txt) | `1818edca6b697a3bfe9ecf91940ac5185e1d051ca84d77d6ac0ededbc6339d8c` |
| [apply_deep_ocr.txt](official/halcon/20260927/apply_deep_ocr.txt) | `8d3917d576d5a4aac836c0c8c39c12c5ba3c0cb4814b9f9bf5d6f4739df657fb` |
| [get_deep_ocr_param.txt](official/halcon/20260927/get_deep_ocr_param.txt) | `4d4fbbbc0fe5fa2098d3ca9151723b90c32c0ebf6a97059f2d4c09166ef2fdd5` |
| [set_deep_ocr_param.txt](official/halcon/20260927/set_deep_ocr_param.txt) | `9ff217d3afb1b1b1ee850a5ecfbeef5a395d8249fadd0c5e67caefcbb8efde1a` |
| [toc_ocr_deepocr.txt](official/halcon/20260927/toc_ocr_deepocr.txt) | `2cb3058ad4e74de7410a133142008897a486edd5c02cf09e60b7b2d44d45e7d9` |

<a id="pcl-line-research"></a>
## 针轴与退化处理的PCL源码研究 — 2026-09-27

固定来源：[PointCloudLibrary/pcl](https://github.com/PointCloudLibrary/pcl/tree/3346843ea6b97697a1577293aa9cdf236b5c7ffb)，release `pcl-1.15.1`（2025-08-26发布），commit `3346843ea6b97697a1577293aa9cdf236b5c7ffb`。只归档本节实际消费的六份源码/测试/构建声明/许可证；不是完整可构建仓库。公开签名与实现、测试一起读取，支持[DEV-MET-031 §6](../shared-modules/guidance/04-metrology/DEV-MET-031_通用计量引擎开发指导.md#axis-datum-relations)及PG-019/020的几何边界。

| 读取位置 | 可确认行为 | 本平台借鉴与限制 |
|---|---|---|
| `sac_model_line.hpp` 51–104行，`isSampleGood` / `computeModelCoefficients` | 两个样本；三个坐标差同时不超过float epsilon才判近重合；输出点和单位方向 | 检查重合/样本数、仅一坐标变化仍有效；epsilon不是毫米计量门槛。平台先查非有限输入及尺度；不把上游函数当完整输入校验 |
| 同文件136–166行，`selectWithinDistance` | 距离与阈值均平方、严格小于；保留原索引 | 保留原始点与内外点对应、冻结边界包含规则；平台拒绝负/非有限阈值，不让平方将负值变成有效门槛 |
| 同文件202–245行，`optimizeModelCoefficients` | 无效模型、内点不足或质心计算无有效点时返回原系数；正常分支使用质心/协方差最大特征向量 | 非空返回不证明细化成功；需检查方法完成、支撑分布、方向与残差；PCA直线不是任意方针侧面的物理中心轴 |
| `test_sample_consensus_line_models.cpp`：RANSAC、OnGroundPlane、SampleValidationPointsEqual/Valid/NotEnoughSamples | 样本/内点数、投影、重合拒绝、只有x变化、点数不足等断言 | 借鉴边界向量，补尺度、退化、针端遮挡、弯段外点、输入修订与几何不变性；上游合成点测试不证明工业精度 |
| 同测试97–99行 | 细化后检查`coeff_refined.size()`，两条方向比值断言仍读取旧`coeff` | 局部断言对象疑点，平台验收必须实际消费细化输出；后续投影测试确实使用`coeff_refined`，不能称上游完全没有细化验证 |

根LICENSE及文件头为BSD-3-Clause形式；实际复制/分发才需保留适用版权和声明。根CMake声明Threads/Eigen3等基础依赖，提供FLANN/nanoflann/OpenMP等可选路线；sample_consensus子系统依赖common/search。不能将单个hpp当成零依赖C#代码，完整传递依赖、原生部署与性能成本需在实际选用时评估。

**本次决定：仅借鉴几何约束和测试方法，不引入PCL运行库，不移植算法。** 平台仍优先HALCON/AsunImage公开能力。未构建、未运行上游测试或本平台针脚算法，没有据此判定PCL比HALCON更优，也没有把几何库当完整插针机实现。

六份归档均与固定Git树blob一致；以下SHA-256固定所读字节，不是运行证据：

| 文件 | SHA-256 |
|---|---|
| [CMakeLists.txt](open-source/PointCloudLibrary_pcl/3346843ea6b97697a1577293aa9cdf236b5c7ffb/CMakeLists.txt) | `e23398d7d7ac4a0a1717e94fcacd4fadd297a049d05dc6809b53744696bba631` |
| [LICENSE.txt](open-source/PointCloudLibrary_pcl/3346843ea6b97697a1577293aa9cdf236b5c7ffb/LICENSE.txt) | `303429f6701ee55a5f53106ea337e9ce4653f1dcda66d190054643bf94e947ae` |
| [sample_consensus/CMakeLists.txt](open-source/PointCloudLibrary_pcl/3346843ea6b97697a1577293aa9cdf236b5c7ffb/sample_consensus/CMakeLists.txt) | `d0e606c102a16ba261ebccde8a12da0e062a905fc0f373f847def7631c408c2e` |
| [sample_consensus/include/pcl/sample_consensus/impl/sac_model_line.hpp](open-source/PointCloudLibrary_pcl/3346843ea6b97697a1577293aa9cdf236b5c7ffb/sample_consensus/include/pcl/sample_consensus/impl/sac_model_line.hpp) | `5d71197a250198ee17fcd4020a09856904e7e27fb2e41d8ce8c75565e7532c0a` |
| [sample_consensus/include/pcl/sample_consensus/sac_model_line.h](open-source/PointCloudLibrary_pcl/3346843ea6b97697a1577293aa9cdf236b5c7ffb/sample_consensus/include/pcl/sample_consensus/sac_model_line.h) | `e87222ed94a2a1bfa5744c5df808fdf03cba7ed54b12db8971425ce3f51139bb` |
| [test/sample_consensus/test_sample_consensus_line_models.cpp](open-source/PointCloudLibrary_pcl/3346843ea6b97697a1577293aa9cdf236b5c7ffb/test/sample_consensus/test_sample_consensus_line_models.cpp) | `3618536dbe28339147d86f67bf6f920bb4242998e3e64dac4616b242035d49a8` |

<a id="add-module-research"></a>
## USER-002独立模块细化的官方与源码依据 — 2026-09-27

本节是对`C:/add.txt`所提能力的主动研究，支撑DEV-GOV-005/006、DEV-VIS-021B/021C/023/026/029、DEV-MET-030、DEV-DOM-058A及DEV-PLT-018。只保留实际消费的文件/摘取，不复制完整仓库；原始用户文件在user-notes/USER-002。官方URL的版本只标识所读行为，不重新规定平台HALCON版本。

### 官方资料与设计选择

| 实际读取 | 直接依据及设计落点 |
|---|---|
| get_bar_code_result、query_bar_code_params | 1D质量结果须persistence解码；普通与复合码分项标签/元组不同，整体与浮点grades按结果名区别；查询参数不是码制枚举。解码/质量/业务身份分离 |
| get_data_code_2d_results、query_data_code_2d_params | 所读ISO/IEC15415:2024等级结果不适用DotCode；不同标准/码制的结果组范围独立，2D模型查询支持的参数/结果。不能承诺所有可解码符号都具相同评级；软件结果依赖前序解码，不等于完整成像检验资格 |
| find_generic_shape_model、find_local_deformable_model | 搜索参考点域与完整模型支撑不同，图像/金字塔边界影响检出；局部变形可输出整平图/变形证据，返回有成本。稀疏Mark小域分开定位，非刚性与质量变化不能混为同一功能 |
| create_variation_model、compare_variation_model | standard均值/标准差可迭代；robust中位数/缩放MAD需一次训练；训练图应同位姿，compare前必须prepare。良品建模/配准/有效域及训练污染防护独立于可变形定位 |
| mult_image | g1*g2*Mult+Add，通常裁切溢出/下溢；特定类型例外，OpenCL可能不同舍入。通道名/类型/范围和派生来源冻结，不能把byte平方默认当增强 |
| gen_radial_distortion_map、map_image | 生成/复用映射与执行分开，特定map路径不检查源坐标边界且插值邻点也须有效。输入布局/映射资格及有效域预先核对，校正不能靠显示看直了验收 |
| gen_projective_mosaic | 给定相对变换进行合成，1基索引；TransformDomain=false忽略输入domain。不能用一次合成调用代替注册/覆盖/计量资格 |
| binary_threshold、dyn_threshold | max_separability/smooth_histo针对双峰；局部阈值对背景窗和Offset敏感，低Offset可能噪声/内存激增。自动不等于全域鲁棒，实际阈值与候选完整性要输出 |
| PostgreSQL History、Transaction Isolation | 起源UC Berkeley；默认Read Committed逐语句快照，Serializable仍可能序列化失败/重试。PostgreSQL只作为优先验证候选，断连/超时先查幂等提交回执，不据此认定未提交 |
| NIST Process Capability | 稳定过程、正态假设/样本量和置信区间；Cp/Cpk/Cpm定义。平台另明确组内/整体σ与Ca本地定义，不能把不稳定混合数据算出一个高值就称过程有能力 |

### 固定源码、测试、依赖和未采用部分

**ZXing-C++**：[v3.1.1固定提交](https://github.com/zxing-cpp/zxing-cpp/tree/287c85df6f961c8efbfb5ffd736cd9457b8b890e)，release发布2026-07-29。实际读取ReadBarcode.cpp、ReaderOptions.h、Barcode.h及Code128单测/blackbox入口。ReadBarcode.cpp中默认tryHarder/rotate/invert/downscale会增加搜索路径，最大符号数提前结束，默认不返回错误符号；输入空/超尺寸抛异常；平台必检目标完整性不能只数成功列表。Barcode.h的ECLevel/UEC是纠错信息，不是ISO印制质量认证。Code128测试明确GS1的HRI文本与symbologyIdentifier、FNC1等区别；blackbox入口只读/打印结果不是质量评级测试。根LICENSE为Apache-2.0；CMake为C++20/Threads、读写和封装选项，写码可涉及Zint；未完成整套传递依赖审核。决定：仅解码对照/接口与测试借鉴，未引入运行时。

**Npgsql**：[v10.0.3固定提交](https://github.com/npgsql/npgsql/tree/d3768398c17877b3a916c3c4d87e8e11698991fc)，release发布2026-05-27。NpgsqlDataSourceBuilder.cs把连接配置/日志与Build委托给内部builder；本轮没有把一个builder文件当完整连接池实现。DataSourceTests检查创建时Closed、打开执行、Dispose对空闲/借出连接与后续访问的约束；CommandTests检查多参数语句、Timeout/soft cancellation等，部分测试明确跳过Multiplexing，不能把其结果泛化为所有模式。src/Npgsql/Npgsql.csproj目标包含net8/9/10、Logging.Abstractions及分析器/源码生成器；LICENSE是PostgreSQL式宽松条款，实际分发需保留声明。决定：PostgreSQL路线的驱动候选，未安装/连接数据库、未运行上游测试，不证明平台事务恢复已完成。

**OpenCV**：沿用已固定`a0cda081f8d769f40ab2f4904738b4787b44d07c`，新增读取templmatch.cpp/test_templmatch.cpp与stitcher.cpp/test_stitcher.cpp。模板实现894–898行在常量模板TM_CCOEFF_NORMED分支返回全1；测试参考实现同样处理，bug_9597检查平方差最小值非负。平台借鉴“缺有效纹理需先拒绝”，不能把该特殊分数解释为高置信定位，也不能说HALCON一定同样返回。Stitcher把estimateTransform与composePanorama分开，SCANS使用仿射估计/warper且不做曝光补偿；setTransform单测比较复用camera参数后的全景输出与原输出相等。它只证明该测试预期，不证明计量或我们的瓦片大图可用。Apache-2.0与依赖沿本页已有LICENSE/CMake阅读，不重拷；决定仅借鉴分阶段/缓存/退化测试，不引入OpenCV。

此前PaddleOCR、Open3D、scikit-image、.NET Channels和DevExpress布局研究继续按原条目复用。相机/光源/轴厂商扩展、客户MES协议、完整查询/恢复资格和全部算子变体仍需对应切片研究，未称本轮完成所有功能的网络/源码比较。源码与测试均为静态读取，未运行上游测试、算法对比或硬件；资料取得时raw站点发生TLS超时，后用GitHub固定blob接口获取，并逐文件验证Git blob一致。

### 所读字节与定位

以下SHA-256固定阅读内容；官方是正文文本摘取，源码是固定Git blob原始字节，不是测试通过证明。

| 来源 | 本地阅读位置 | SHA-256 |
|---|---|---|
| [binary_threshold](https://www.mvtec.com/doc/halcon/2511/en/binary_threshold.html) | [文本](official/halcon/20260927/binary_threshold.txt) | `1a4fc526dac2f848a304091cfa7694da6830cd9ad4927353442826381268c545` |
| [compare_variation_model](https://www.mvtec.com/doc/halcon/2511/en/compare_variation_model.html) | [文本](official/halcon/20260927/compare_variation_model.txt) | `ded0b327ee88e97ec2b26fc52311f25a9eef8e56e57796cdc83cc89cd682bea6` |
| [create_variation_model](https://www.mvtec.com/doc/halcon/2511/en/create_variation_model.html) | [文本](official/halcon/20260927/create_variation_model.txt) | `45f48260b01ba81767ded678f58614257f43977f7410f08e3eb78943bb9774a0` |
| [dyn_threshold](https://www.mvtec.com/doc/halcon/2511/en/dyn_threshold.html) | [文本](official/halcon/20260927/dyn_threshold.txt) | `0bca659056753b66faf0f6f7ac75b4741a221b2aa25ee9d3bb3d977ab8e89232` |
| [find_generic_shape_model](https://www.mvtec.com/doc/halcon/2511/en/find_generic_shape_model.html) | [文本](official/halcon/20260927/find_generic_shape_model.txt) | `af5406b029c966d8aebfd097f821312acc963cb6b51d63d4709d7b9ab45e12b3` |
| [find_local_deformable_model](https://www.mvtec.com/doc/halcon/2511/en/find_local_deformable_model.html) | [文本](official/halcon/20260927/find_local_deformable_model.txt) | `198b0268f3f0192e690901ecb12ec4d2fd385b6917d85e3f2807372ee15ca02d` |
| [gen_projective_mosaic](https://www.mvtec.com/doc/halcon/2511/en/gen_projective_mosaic.html) | [文本](official/halcon/20260927/gen_projective_mosaic.txt) | `551ebff6bafb0a2b90507d11768145e19a8bfd88bd4092a51fc32e961ee6dc4e` |
| [gen_radial_distortion_map](https://www.mvtec.com/doc/halcon/2511/en/gen_radial_distortion_map.html) | [文本](official/halcon/20260927/gen_radial_distortion_map.txt) | `fc7a7846bbaa667d90aaef5d0d9cd77c3fd2d2fb7bd6a9f0677679df4f45aca4` |
| [get_bar_code_result](https://www.mvtec.com/doc/halcon/2511/en/get_bar_code_result.html) | [文本](official/halcon/20260927/get_bar_code_result.txt) | `7882616b89a8ed9a1deec47202b01799aa4b2c71a19593ab2d8fc0a8a9fdff29` |
| [get_data_code_2d_results](https://www.mvtec.com/doc/halcon/2511/en/get_data_code_2d_results.html) | [文本](official/halcon/20260927/get_data_code_2d_results.txt) | `1309bf6a6dfe2a36fa43724441911f738d5e248d9b9a7d8c2e47c23e6417d896` |
| [map_image](https://www.mvtec.com/doc/halcon/2511/en/map_image.html) | [文本](official/halcon/20260927/map_image.txt) | `b274371c91cca2a02ca8dd0119fd46fe8e8e918e0ef7145c070b80543ac38f9a` |
| [mult_image](https://www.mvtec.com/doc/halcon/2511/en/mult_image.html) | [文本](official/halcon/20260927/mult_image.txt) | `4c5519c95ec36c3637070fad1d4982d0aa0a693dbc31c9a5a2ee06f7249cabec` |
| [nist-capability](https://www.itl.nist.gov/div898/handbook/pmc/section1/pmc16.htm) | [文本](official/nist/20260927/pmc16.txt) | `73530080cd0be22e8aa5f5d30985ddd6886a698ed61b842e993797570bc1d091` |
| [postgres-history](https://www.postgresql.org/docs/current/history.html) | [文本](official/postgresql/20260927/history.txt) | `31d8069d1fc05777da2f528e5e41055ae024bffad5fd658a901299d890f06f27` |
| [postgres-isolation](https://www.postgresql.org/docs/current/transaction-iso.html) | [文本](official/postgresql/20260927/transaction-iso.txt) | `34213b6e74b6ff10e573ff602082bf7e2b0c0069b456e803d67b486cf39a819b` |
| [query_bar_code_params](https://www.mvtec.com/doc/halcon/2511/en/query_bar_code_params.html) | [文本](official/halcon/20260927/query_bar_code_params.txt) | `25f9bf3a69a4852c1714c4dd708c268c09652e2d0b12d26f90c844788826716e` |
| [query_data_code_2d_params](https://www.mvtec.com/doc/halcon/2511/en/query_data_code_2d_params.html) | [文本](official/halcon/20260927/query_data_code_2d_params.txt) | `8233e9761842a9747aab27fd3dfe702dd0eb603de0562d9eb62100c6dee4016e` |
| [zxing-cpp/zxing-cpp: LICENSE](https://raw.githubusercontent.com/zxing-cpp/zxing-cpp/287c85df6f961c8efbfb5ffd736cd9457b8b890e/LICENSE) | [源码](open-source/zxing-cpp_zxing-cpp/287c85df6f961c8efbfb5ffd736cd9457b8b890e/LICENSE) | `c6596eb7be8581c18be736c846fb9173b69eccf6ef94c5135893ec56bd92ba08` |
| [zxing-cpp/zxing-cpp: CMakeLists.txt](https://raw.githubusercontent.com/zxing-cpp/zxing-cpp/287c85df6f961c8efbfb5ffd736cd9457b8b890e/CMakeLists.txt) | [源码](open-source/zxing-cpp_zxing-cpp/287c85df6f961c8efbfb5ffd736cd9457b8b890e/CMakeLists.txt) | `6528050c444cc39f1a04b37f2999957d36627246c7640e397c802ab86764dc40` |
| [zxing-cpp/zxing-cpp: core/CMakeLists.txt](https://raw.githubusercontent.com/zxing-cpp/zxing-cpp/287c85df6f961c8efbfb5ffd736cd9457b8b890e/core/CMakeLists.txt) | [源码](open-source/zxing-cpp_zxing-cpp/287c85df6f961c8efbfb5ffd736cd9457b8b890e/core/CMakeLists.txt) | `2ac86c8e97eac0874f1f5efb380e4b750c9eec3928a42d72ebc8b3e3859992f2` |
| [zxing-cpp/zxing-cpp: core/src/ReadBarcode.cpp](https://raw.githubusercontent.com/zxing-cpp/zxing-cpp/287c85df6f961c8efbfb5ffd736cd9457b8b890e/core/src/ReadBarcode.cpp) | [源码](open-source/zxing-cpp_zxing-cpp/287c85df6f961c8efbfb5ffd736cd9457b8b890e/core/src/ReadBarcode.cpp) | `3ebcb0d930512323dd9558653346d267c869c2acd255d922384529e6b9b852b6` |
| [zxing-cpp/zxing-cpp: core/src/Barcode.h](https://raw.githubusercontent.com/zxing-cpp/zxing-cpp/287c85df6f961c8efbfb5ffd736cd9457b8b890e/core/src/Barcode.h) | [源码](open-source/zxing-cpp_zxing-cpp/287c85df6f961c8efbfb5ffd736cd9457b8b890e/core/src/Barcode.h) | `8916a74f1aa8af164162080c770843b022d51f577af2744e309d9f358db8e103` |
| [zxing-cpp/zxing-cpp: core/src/ReaderOptions.h](https://raw.githubusercontent.com/zxing-cpp/zxing-cpp/287c85df6f961c8efbfb5ffd736cd9457b8b890e/core/src/ReaderOptions.h) | [源码](open-source/zxing-cpp_zxing-cpp/287c85df6f961c8efbfb5ffd736cd9457b8b890e/core/src/ReaderOptions.h) | `b02f422ace401fcde9ffaabf4aefdc9532b7b61a846cc92705e55a89431d609e` |
| [zxing-cpp/zxing-cpp: test/unit/oned/ODCode128ReaderTest.cpp](https://raw.githubusercontent.com/zxing-cpp/zxing-cpp/287c85df6f961c8efbfb5ffd736cd9457b8b890e/test/unit/oned/ODCode128ReaderTest.cpp) | [源码](open-source/zxing-cpp_zxing-cpp/287c85df6f961c8efbfb5ffd736cd9457b8b890e/test/unit/oned/ODCode128ReaderTest.cpp) | `c9ea909704c680f41f48f0de44d3d0755268c194dd98ebe666dfd476575cd7f2` |
| [zxing-cpp/zxing-cpp: test/blackbox/TestReaderMain.cpp](https://raw.githubusercontent.com/zxing-cpp/zxing-cpp/287c85df6f961c8efbfb5ffd736cd9457b8b890e/test/blackbox/TestReaderMain.cpp) | [源码](open-source/zxing-cpp_zxing-cpp/287c85df6f961c8efbfb5ffd736cd9457b8b890e/test/blackbox/TestReaderMain.cpp) | `00e723b8db720889d34af80561228ec347e7695f9d639697e79a7e30f51d9a8f` |
| [npgsql/npgsql: LICENSE](https://raw.githubusercontent.com/npgsql/npgsql/d3768398c17877b3a916c3c4d87e8e11698991fc/LICENSE) | [源码](open-source/npgsql_npgsql/d3768398c17877b3a916c3c4d87e8e11698991fc/LICENSE) | `2e1d9cc6ed4eb7fe6fa82091846c06b4f58571a2c3b54777db6baeca10dd2d74` |
| [npgsql/npgsql: src/Npgsql/Npgsql.csproj](https://raw.githubusercontent.com/npgsql/npgsql/d3768398c17877b3a916c3c4d87e8e11698991fc/src/Npgsql/Npgsql.csproj) | [源码](open-source/npgsql_npgsql/d3768398c17877b3a916c3c4d87e8e11698991fc/src/Npgsql/Npgsql.csproj) | `fd36c9e18a2c47656732ed6a6173cfe459f36b706b1798153f82ce4803da2894` |
| [npgsql/npgsql: src/Npgsql/NpgsqlDataSourceBuilder.cs](https://raw.githubusercontent.com/npgsql/npgsql/d3768398c17877b3a916c3c4d87e8e11698991fc/src/Npgsql/NpgsqlDataSourceBuilder.cs) | [源码](open-source/npgsql_npgsql/d3768398c17877b3a916c3c4d87e8e11698991fc/src/Npgsql/NpgsqlDataSourceBuilder.cs) | `978c6fb138a62548eb86038c46961dc8db40150df261c5fba3717e5fd83c3d1e` |
| [npgsql/npgsql: test/Npgsql.Tests/DataSourceTests.cs](https://raw.githubusercontent.com/npgsql/npgsql/d3768398c17877b3a916c3c4d87e8e11698991fc/test/Npgsql.Tests/DataSourceTests.cs) | [源码](open-source/npgsql_npgsql/d3768398c17877b3a916c3c4d87e8e11698991fc/test/Npgsql.Tests/DataSourceTests.cs) | `ab79e557f03ccfa9153bf4303001fc62e3f0a54f55c0be8de82dc7cfac0e58f8` |
| [npgsql/npgsql: test/Npgsql.Tests/CommandTests.cs](https://raw.githubusercontent.com/npgsql/npgsql/d3768398c17877b3a916c3c4d87e8e11698991fc/test/Npgsql.Tests/CommandTests.cs) | [源码](open-source/npgsql_npgsql/d3768398c17877b3a916c3c4d87e8e11698991fc/test/Npgsql.Tests/CommandTests.cs) | `7ebe421b291ad5522885195ffad9be6bb983a5d273cac3fa39a7d28b43f02d72` |
| [opencv/opencv: modules/imgproc/src/templmatch.cpp](https://raw.githubusercontent.com/opencv/opencv/a0cda081f8d769f40ab2f4904738b4787b44d07c/modules/imgproc/src/templmatch.cpp) | [源码](open-source/opencv_opencv/a0cda081f8d769f40ab2f4904738b4787b44d07c/modules/imgproc/src/templmatch.cpp) | `b40906775633dfa25bb4c363d389f42ceb31add2fab369bfc5cff9e72737677b` |
| [opencv/opencv: modules/imgproc/test/test_templmatch.cpp](https://raw.githubusercontent.com/opencv/opencv/a0cda081f8d769f40ab2f4904738b4787b44d07c/modules/imgproc/test/test_templmatch.cpp) | [源码](open-source/opencv_opencv/a0cda081f8d769f40ab2f4904738b4787b44d07c/modules/imgproc/test/test_templmatch.cpp) | `d730ee2122a65616f74c5865522616dc000b91aca532bb464dc8b9fbc919d171` |
| [opencv/opencv: modules/stitching/src/stitcher.cpp](https://raw.githubusercontent.com/opencv/opencv/a0cda081f8d769f40ab2f4904738b4787b44d07c/modules/stitching/src/stitcher.cpp) | [源码](open-source/opencv_opencv/a0cda081f8d769f40ab2f4904738b4787b44d07c/modules/stitching/src/stitcher.cpp) | `84962ab2aa0efb5795a9821d995519dc9787029d127a99525703aed54b62c64a` |
| [opencv/opencv: modules/stitching/test/test_stitcher.cpp](https://raw.githubusercontent.com/opencv/opencv/a0cda081f8d769f40ab2f4904738b4787b44d07c/modules/stitching/test/test_stitcher.cpp) | [源码](open-source/opencv_opencv/a0cda081f8d769f40ab2f4904738b4787b44d07c/modules/stitching/test/test_stitcher.cpp) | `b6b15cebea5627803953a53fdaf95386bdd8ec3e69447b9d53c72a9dc8fa5938` |

<a id="alarm-source-research"></a>
## 报警独立模块的官方与固定源码比较（2026-09-28）

消费者：[PKG-059报警](../shared-modules/packages/PKG-059_Alarms.md)、[PKG-005诊断](../shared-modules/packages/PKG-005_Diagnostics.md)。HALCON不适用于报警事务；本轮考察OPC Foundation自己的实现/规范，目的是核清发生、确认和数据当前性，未选定或引入OPC UA运行库。

官方Part9 §5.7（页面显示v1.05.06）实际正文明确：AckedState与可选ConfirmedState分别表示知悉确认及处理复核；操作针对特定EventId；旧状态仍待确认且新状态也需确认时存在分支；重启不能确定已确认事实时不可假定已确认。它是协议参考，不直接成为平台Contract，也不把ConfirmedState解释为板件质量Release。运行当前条件与人工确认的分离已写入059。

固定仓库提交为 `46fa7d364a0bc44b71a78bbe3cc415edda4a46bd`，不是本平台依赖版本。本轮实际阅读AlarmRateTracker完整实现及其5个速率测试，ConditionStateTests中确认/复核时间戳、订阅更新、Enabled/Retain与分支并发相关测试体；同时读取许可证、Server项目引用与中央依赖声明相关段落。没有构建/运行该仓库，没有读遍其全部报警实现/测试。

| 观察依据 | 可迁移的价值 | 限制与平台决定 |
|---|---|---|
| AlarmRateTracker以Queue记录激活、注入TimeProvider、按窗口裁剪并保存历史最大值 | 统计激活次数与当前活动报警个数是不同指标；时钟可以注入，指标重置与报警状态分开 | 返回的是窗口内次数，不是自动换算成每秒速率；本实现没有队列容量上限，也未校验窗口为正；不能照搬到无界风暴路径 |
| RecordActivation(DateTime)直接入队，TrimOldEntries仅从队首按时间删除 | 易于理解的窗口策略 | 隐含时间顺序前提；若按100s、1s乱序入队，在101s查询10s窗口，队首100保留会使后面的1也保留。是源码推导的反例，未执行上游代码，不宣称上游生产缺陷；本平台先确定按接收单调时钟还是事件时间/水位计数，并验乱序/回拨 |
| AlarmRateTrackerTests有初值、递增、过期、峰值及Reset；峰值测试使用Thread.Sleep | 提供基本可判定行为 | 本平台增加容量/乱序/时间回拨/期限边界，采用受控时钟推进，避免墙钟Sleep造成不稳定；指标Reset不得清除正式报警历史 |
| ConditionStateTests确认/复核字段和Retain、分支并发测试 | 分离状态维度，重建列表不能只靠UI缓存；并发枚举须稳定 | 所读“通知订阅者”测试主要断言时间戳/ChangeMasks，不等于完整远端订阅交付；分支测试偏无异常，不证明全生命周期/持久一致性。平台仍须测试丢回执、冷重开、再发生与两站冲突 |
| LICENSE与Server.csproj | OPC Foundation MIT条款；Server引用Core、Core.Schema、Configuration及Hosting.Abstractions、RateLimiting | 全部直接/传递依赖尚未构建解析，中央版本含更多仓库模块，不能都视作Server必要依赖。不为复用一个计数器引入完整网络服务栈；以后需协议时再限定Adapter/依赖闭包 |

本轮只作设计比较和来源固定，不能据MIT许可或单元测试存在推断适合现场，也不声称该方案性能优于自有实现。平台关键要求是有界性、当前性、单一Owner和可恢复提交；可以复用思想，生产代码复用须按实际组件范围再决定。AsunImage/DevExpress不在本研究授权核验范围。

| 官方/源文件 | 本地阅读文本 | SHA-256 |
|---|---|---|
| [Part9 §5.7](https://reference.opcfoundation.org/Core/Part9/v105/docs/5.7) | [正文摘取](<official/opc-ua/20260928/part9-5.7.txt>) | `d550b709cdefefb86ebbc30dfc663ace434527492643b5ea2fb62c4465ebcb86` |
| [src/Opc.Ua.Server/Alarms/AlarmRateTracker.cs](https://github.com/OPCFoundation/UA-.NETStandard/blob/46fa7d364a0bc44b71a78bbe3cc415edda4a46bd/src/Opc.Ua.Server/Alarms/AlarmRateTracker.cs) | [原文件](<open-source/OPCFoundation_UA-.NETStandard/46fa7d364a0bc44b71a78bbe3cc415edda4a46bd/src/Opc.Ua.Server/Alarms/AlarmRateTracker.cs>) | `a68e0062273a29b63bd218b42e4f75e2decfff856dce22135e246bd230acd0cd` |
| [tests/Opc.Ua.Server.Tests/Alarms/AlarmRateTrackerTests.cs](https://github.com/OPCFoundation/UA-.NETStandard/blob/46fa7d364a0bc44b71a78bbe3cc415edda4a46bd/tests/Opc.Ua.Server.Tests/Alarms/AlarmRateTrackerTests.cs) | [原文件](<open-source/OPCFoundation_UA-.NETStandard/46fa7d364a0bc44b71a78bbe3cc415edda4a46bd/tests/Opc.Ua.Server.Tests/Alarms/AlarmRateTrackerTests.cs>) | `de68cff6ac7cf76166ecb407749554990e5b9d96463b686a1026f3217f441df0` |
| [tests/Opc.Ua.Core.Tests/Stack/State/ConditionStateTests.cs](https://github.com/OPCFoundation/UA-.NETStandard/blob/46fa7d364a0bc44b71a78bbe3cc415edda4a46bd/tests/Opc.Ua.Core.Tests/Stack/State/ConditionStateTests.cs) | [原文件](<open-source/OPCFoundation_UA-.NETStandard/46fa7d364a0bc44b71a78bbe3cc415edda4a46bd/tests/Opc.Ua.Core.Tests/Stack/State/ConditionStateTests.cs>) | `09fd0dfb87d64d20b2086e5247d9caf6276a49d9a6d4453c11a45f1cdf113547` |
| [src/Opc.Ua.Server/Opc.Ua.Server.csproj](https://github.com/OPCFoundation/UA-.NETStandard/blob/46fa7d364a0bc44b71a78bbe3cc415edda4a46bd/src/Opc.Ua.Server/Opc.Ua.Server.csproj) | [原文件](<open-source/OPCFoundation_UA-.NETStandard/46fa7d364a0bc44b71a78bbe3cc415edda4a46bd/src/Opc.Ua.Server/Opc.Ua.Server.csproj>) | `f8db3181509958bdd2a1b37317ad486f2d5a3d153a4f832f9fec738c6799d586` |
| [LICENSE.txt](https://github.com/OPCFoundation/UA-.NETStandard/blob/46fa7d364a0bc44b71a78bbe3cc415edda4a46bd/LICENSE.txt) | [原文件](<open-source/OPCFoundation_UA-.NETStandard/46fa7d364a0bc44b71a78bbe3cc415edda4a46bd/LICENSE.txt>) | `7ef7a25dbc6464d4a40f7a2c6c35ca78f485f9c52cadcad47da8289cce6970a5` |
| [Directory.Packages.props](https://github.com/OPCFoundation/UA-.NETStandard/blob/46fa7d364a0bc44b71a78bbe3cc415edda4a46bd/Directory.Packages.props) | [原文件](<open-source/OPCFoundation_UA-.NETStandard/46fa7d364a0bc44b71a78bbe3cc415edda4a46bd/Directory.Packages.props>) | `bf8b7dfbcd8e119a161b968b49e09f57e2d84a745338b609ea7bd42ed46141a5` |

六份源码/测试/依赖/许可文件均与固定Git树blob哈希一致。先前大响应获取不完整、个别raw请求超时后改为精确树/Blob接口取得缺失文件，已有文件复用；失败请求不算研究完成。

<a id="foundation-source-research"></a>
## 帧资源、坐标桥与标定生命周期研究 — 2026-09-28

直接服务PKG-006/007/015/016/049、DEV-VIS-022、DEV-MET-030与FS-016/UI-PCS-007。本轮读取AOI只读归档中的基础指导，并查阅以下HALCON官方正文及.NET固定源码。所有结论限定为公开文档/源码阅读和数学推导；没有运行上游测试、HALCON程序或平台算法。来源URL版本只固定本次阅读内容，不新增平台底层版本约束；调用仍经AsunImage公共能力。

| 官方正文实际读取部分 | 提取的实现限制 |
|---|---|
| copy_obj / copy_image，Description | 前者只增加引用，后者复制图像全部通道；不能用对象浅复制承诺像素隔离 |
| get_image_pointer1，Description/Attention | 第一通道、row-major、对象寿命内可用；共享矩阵的别名会被指针写入同时影响 |
| gen_image1_extern，Description/Attention | 不复制、不检查指针长度；ClearProc与外部寿命由调用者负责；当前不实现native接入或猜封装签名 |
| affine_trans_point_2d / affine_trans_pixel，Description/Attention | 图像数学row对应Px，column对应Py；像素入口前+0.5后−0.5，需要换基及明确中心/corner约定 |
| affine_trans_image，Description/Attention | 忽略输入domain；corner坐标、左上负坐标仍裁剪；bilinear/bicubic缩小不自动抗混叠，constant/weighted路线有平滑；int_zooming涉及精度/domain，不能各模块任意改全局设置 |
| calibrate_cameras，Description/返回误差 | 优化目标与输出RMSE为重投影pixel误差；不能单独证明物理量误差/资格 |
| project_3d_point，Description | 输入点必须在camera坐标系，输出Row/Column |
| image_points_to_world_plane，Description/Scale | 与给定world的z=0平面求交；WorldPose是world相对camera，输出比例与靶标几何单位关联，标准板通常米；不恢复未知深度 |

官方摘取及SHA-256：

| 官方来源 | 本地正文 | SHA-256 |
|---|---|---|
| [copy_obj](https://www.mvtec.com/doc/halcon/2511/en/copy_obj.html) | [正文](<official/halcon/20260928/copy_obj.txt>) | `88e269f0b3b53fdd259bd732388b9915eca73cfc1c82d7461dc54cc57b295639` |
| [copy_image](https://www.mvtec.com/doc/halcon/2511/en/copy_image.html) | [正文](<official/halcon/20260928/copy_image.txt>) | `fbb42552855eb1a6c577cd5601cacb1a004c56d53ba3f5f6beea9f5025a9de16` |
| [get_image_pointer1](https://www.mvtec.com/doc/halcon/2511/en/get_image_pointer1.html) | [正文](<official/halcon/20260928/get_image_pointer1.txt>) | `8b90e158624fc35e421ca925a577fe91f436e98890f86793e07d02dc8788b99a` |
| [gen_image1_extern](https://www.mvtec.com/doc/halcon/2511/en/gen_image1_extern.html) | [正文](<official/halcon/20260928/gen_image1_extern.txt>) | `4a37ff2fc67579b100aa2775d5bfdd7c94074eb7972da265784b80bfb5cd7808` |
| [affine_trans_pixel](https://www.mvtec.com/doc/halcon/2511/en/affine_trans_pixel.html) | [正文](<official/halcon/20260928/affine_trans_pixel.txt>) | `9010eae61eff0cb9241a564ccb46d0100664cf286277f5e5e3da4af57d9ab725` |
| [affine_trans_point_2d](https://www.mvtec.com/doc/halcon/2511/en/affine_trans_point_2d.html) | [正文](<official/halcon/20260928/affine_trans_point_2d.txt>) | `cbbff72a8607d4df44aaf2ec241574aac65cee6310e3916fe0ecbbc991f475b7` |
| [affine_trans_image](https://www.mvtec.com/doc/halcon/2511/en/affine_trans_image.html) | [正文](<official/halcon/20260928/affine_trans_image.txt>) | `7b21c6f3af6b440d1fdf0f3e2923c8ddc010afca47cc6c9653cb8a0704b331c8` |
| [calibrate_cameras](https://www.mvtec.com/doc/halcon/2511/en/calibrate_cameras.html) | [正文](<official/halcon/20260928/calibrate_cameras.txt>) | `3cdf3574a12a7cf12caf330008a26c40a59f2c039e4fd79f0fc8b5a5f911e769` |
| [project_3d_point](https://www.mvtec.com/doc/halcon/2511/en/project_3d_point.html) | [正文](<official/halcon/20260928/project_3d_point.txt>) | `ae54b9bb5159fe6319ed14d7cac7f75eb9ccbf556e497a8a70a204dc98c3f1c9` |
| [image_points_to_world_plane](https://www.mvtec.com/doc/halcon/2511/en/image_points_to_world_plane.html) | [正文](<official/halcon/20260928/image_points_to_world_plane.txt>) | `80a8f4a407a529191b4943a0ad7c307cbd75506090d075d2615cef613e4643bc` |

固定.NET来源沿用本页既有dotnet/runtime v10.0.0 commit `60629d14374c56f1cb51819049ad1fa529307f8d`。新增实际阅读三份实现全文及MemoryPool测试前210行：

| 文件/阅读结论 | 可迁移点与限制 |
|---|---|
| ArrayMemoryPool.ArrayMemoryPoolBuffer.cs | Rent返回至少请求长度；Memory涵盖实际数组容量；Dispose归还数组，已有Memory不能自动失效；该实现无并发归还保护，不推断多线程重复Dispose安全 |
| ArrayMemoryPool.cs / MemoryPool.cs | Shared pool的Dispose为空操作，不替各buffer归还；Owner的资源生命周期仍须调用者管理 |
| tests/MemoryPool/MemoryPool.cs，前210行 | 含租用唯一性、pin/slice、顺序double-dispose、非法大小等；测试只证明其明确断言，未覆盖平台native超时、多消费者竞争或设备回调寿命 |

采用.NET现有MemoryPool/ArrayPool能力，外层实现平台必要的独立handle/read scope及回收协议，不复制BCL源码建立新池。已有根LICENSE.TXT为MIT；本次三实现使用BCL内ArrayPool、Memory、异常检查和GC等，测试依赖runtime测试设施/xUnit；未完整审查System.Memory全项目依赖或进行安全审计，不新增第三方运行库。完整源码快照不是可构建工程，Git blob仅校验所取字节。

| 固定源码 | SHA-256 | Git blob SHA-1 |
|---|---|---|
| [src/libraries/System.Memory/src/System/Buffers/ArrayMemoryPool.ArrayMemoryPoolBuffer.cs](<open-source/dotnet_runtime/60629d14374c56f1cb51819049ad1fa529307f8d/src/libraries/System.Memory/src/System/Buffers/ArrayMemoryPool.ArrayMemoryPoolBuffer.cs>) · [上游](https://github.com/dotnet/runtime/blob/60629d14374c56f1cb51819049ad1fa529307f8d/src/libraries/System.Memory/src/System/Buffers/ArrayMemoryPool.ArrayMemoryPoolBuffer.cs) | `f8adf476129a03d56e8edc9bbac37e4d92cc8a200601325c0dcaf8d84d8fc0ad` | `8f626343fcaf0b444b695ed0d3222b61f76631eb` |
| [src/libraries/System.Memory/src/System/Buffers/ArrayMemoryPool.cs](<open-source/dotnet_runtime/60629d14374c56f1cb51819049ad1fa529307f8d/src/libraries/System.Memory/src/System/Buffers/ArrayMemoryPool.cs>) · [上游](https://github.com/dotnet/runtime/blob/60629d14374c56f1cb51819049ad1fa529307f8d/src/libraries/System.Memory/src/System/Buffers/ArrayMemoryPool.cs) | `3b483bab11765ebef2da38573634fe02e1f9f1e0f92bcd982c32f55f714442d2` | `0ceca4f5d7082c95b16e4d34c0d12d530df60dfe` |
| [src/libraries/System.Memory/src/System/Buffers/MemoryPool.cs](<open-source/dotnet_runtime/60629d14374c56f1cb51819049ad1fa529307f8d/src/libraries/System.Memory/src/System/Buffers/MemoryPool.cs>) · [上游](https://github.com/dotnet/runtime/blob/60629d14374c56f1cb51819049ad1fa529307f8d/src/libraries/System.Memory/src/System/Buffers/MemoryPool.cs) | `442b8e53403abe639e810b1f17ea8fb89a53de973fd4dd22b2469339868789f7` | `8f037f5adba907913ed733138bda61c5b27d11c2` |
| [src/libraries/System.Memory/tests/MemoryPool/MemoryPool.cs](<open-source/dotnet_runtime/60629d14374c56f1cb51819049ad1fa529307f8d/src/libraries/System.Memory/tests/MemoryPool/MemoryPool.cs>) · [上游](https://github.com/dotnet/runtime/blob/60629d14374c56f1cb51819049ad1fa529307f8d/src/libraries/System.Memory/tests/MemoryPool/MemoryPool.cs) | `8357fb60ea7d3ecf02409a6e39bf9459441a92b0f962df91a560eaf8e005f6ae` | `4ee663dc1dd885a0244d66b197453427b803c679` |

源AOI规范与本平台的差异、读取范围和未采纳部分见[REF-008 §8](REF-008_PCBA-AOI指导副本与平台采纳映射.md#foundation-adoption)。坐标缩放/法向、布局范围等例子可独立算术核验，但不得标为HALCON、AsunImage、并发、标定精度或实机验证。具体缓存/全局系统参数约束仍须映射实际公共入口；本研究不授权修改AsunImage内部。

<a id="measurement-source-research"></a>
## ROI、卡尺与几何拟合的官方/固定源码研究 — 2026-09-28

直接消费方为DEV-VIS-024/025、DEV-MET-031、PKG-020/021/027/030及原控件适配。平台先复用Asun_ROI公开测量能力和AsunImage；本研究不引入Python或另一套拟合引擎。官方URL版本只固定来源，原文固定版本要求不成为平台基线。以下为静态阅读，未运行HALCON或上游测试。

| 实际阅读 | 实施影响 |
|---|---|
| gen_measure_rectangle2 Description/Attention | major axis是扫描方向，Length1/2为半长；中心内部取整；双线性/双三次边缘分别至少1/2像素；预计算/精度受int_zooming影响，不各模块随意修改全局值 |
| measure_pos Description/Attention | 投影平均→高斯导数→亚像素边；阈值是导数幅值，Select只有all/first/last；N边对应N−1个相邻Distance；忽略domain且直边/方向适用性必要 |
| measure_pairs Description/Attention | all的首边决定过渡极性，连续同极性默认与*_strongest的配对规则不同；Intra/Inter距离不可混，忽略domain |
| fit_circle_contour_xld Description | 不分割输入；algebraic/geometric及鲁棒权重不同；geometric族忽略Iterations；端点即使排除拟合仍影响弧起止；3点只是数学必要条件 |
| fit_ellipse_contour_xld Description中方法/端点/迭代/退化段 | 5点只是数学必要条件；部分路线找不到椭圆时拟合线，Radius2=0；长短半轴/角度及弧端点应独立验证 |
| apply_metrology_model Description/Attention | 找边后RANSAC等拟合，多实例顺序不表示质量；camera/plane改变拟合坐标，尺寸变化重算测量区，忽略domain |
| get_metrology_object_result Description | 原语有各自参数序列，设置camera/plane后输出世界坐标；score是已用测量数/最大测量区数，不是概率；按对象/实例取结果 |

文本摘取保留正文，但部分网页公式以图片/SVG呈现，不能从文本空白处猜公式。本轮设计只引用已读自然语言和另外明确推导的数学，不宣称全文所有公式已核。

| 官方页面 | 本地正文 | SHA-256 |
|---|---|---|
| [apply_metrology_model](https://www.mvtec.com/doc/halcon/2511/en/apply_metrology_model.html) | [正文](<official/halcon/20260928/apply_metrology_model.txt>) | `1f7450dd1ee8ab85d0ddf23ab1cd26537361363232c0388bacf277c476b12537` |
| [fit_circle_contour_xld](https://www.mvtec.com/doc/halcon/2511/en/fit_circle_contour_xld.html) | [正文](<official/halcon/20260928/fit_circle_contour_xld.txt>) | `38c63fd473d4f67982e221eef8176219189e56df649307a304f58956ee551218` |
| [fit_ellipse_contour_xld](https://www.mvtec.com/doc/halcon/2511/en/fit_ellipse_contour_xld.html) | [正文](<official/halcon/20260928/fit_ellipse_contour_xld.txt>) | `db187cfa7bb349fe731c1675a813f62ab1ca54805c2040923e19f25efbf53584` |
| [gen_measure_rectangle2](https://www.mvtec.com/doc/halcon/2511/en/gen_measure_rectangle2.html) | [正文](<official/halcon/20260928/gen_measure_rectangle2.txt>) | `f87306092b18b4315883eb5a26549bb03af98f1b490a2d5387a52d65f49aca9b` |
| [get_metrology_object_result](https://www.mvtec.com/doc/halcon/2511/en/get_metrology_object_result.html) | [正文](<official/halcon/20260928/get_metrology_object_result.txt>) | `fe7c462a5ba23dc7b2abc6e597b78bd54eb1fb7d4725e9bc03e84b2291099861` |
| [measure_pairs](https://www.mvtec.com/doc/halcon/2511/en/measure_pairs.html) | [正文](<official/halcon/20260928/measure_pairs.txt>) | `93ffacae24a4f8e56739f5347e9f5b5d9f9604c3bc5eac5ab77cecdf85e4265d` |
| [measure_pos](https://www.mvtec.com/doc/halcon/2511/en/measure_pos.html) | [正文](<official/halcon/20260928/measure_pos.txt>) | `2ec1263c605550e74a6da489486e0c462d5aab158f3d4b6fc72bd6babf19a302` |

开源对照沿用scikit-image commit `533b7694d2004ae84e49e2cfd0bcfc5f8e562f22`（已固定开发快照，不是平台发行版本）。新增fit.py与test_fit.py原字节，阅读范围为实现1–25、560–671、854–985行，测试198–309、616–690行：

- Circle的计算先转浮点、去中心并按尺度归一，再lstsq及rank检查、求半径；可借鉴整数溢出/大偏置小特征/共线检查，不能从类名或说明把代数求解与几何误差优化视为同一方法。
- Ellipse检查样本数、极小尺度、奇异矩阵/特征约束；统一轴序/角度。末段对参数使用nan_to_num；平台不照搬这种数值修补，必须独立拒绝无效或退化参数。这里只是代码观察，不声称已构造上游错误样本或证明其所有输入失败。
- 所读测试包含整数偏移、圆不足/共线、相同点、椭圆大偏置及少点失败。正常噪声圆测试只按其给定精度断言，不能当工业微米精度或小弧条件性证据；新旧估计API的失败报告也不能只看任意返回值是否非空。
- 根LICENSE.txt已读，所取fit/tests归BSD-3-Clause；pyproject前108行声明Python>=3.12、NumPy>=2.1、SciPy及networkx/Pillow等依赖，fit.py还用packaging和内部工具。只借鉴数值预处理/退化/测试思路，不复制产品代码或增加这些生产依赖。没有完整传递依赖安全审计。

| 固定源码/测试 | SHA-256 | Git blob SHA-1 |
|---|---|---|
| [src/_skimage2/measure/fit.py](<open-source/scikit-image_scikit-image/533b7694d2004ae84e49e2cfd0bcfc5f8e562f22/src/_skimage2/measure/fit.py>) · [上游](https://github.com/scikit-image/scikit-image/blob/533b7694d2004ae84e49e2cfd0bcfc5f8e562f22/src/_skimage2/measure/fit.py) | `02a1f272deebf824034f473022fc8c791b55c30aa35ad0b8b92969efb56bcb4f` | `595a6ca5410e1c225373be9a1c3ee2b255761a0f` |
| [tests/skimage2/measure/test_fit.py](<open-source/scikit-image_scikit-image/533b7694d2004ae84e49e2cfd0bcfc5f8e562f22/tests/skimage2/measure/test_fit.py>) · [上游](https://github.com/scikit-image/scikit-image/blob/533b7694d2004ae84e49e2cfd0bcfc5f8e562f22/tests/skimage2/measure/test_fit.py) | `8e7c7e3d91c215a3cebd8923565f877972c6071493592a60f0ddaed099fa8896` | `80a2bf89665408d05bbba25c9a265b03f0b76296` |

现有控件的公共声明、适配边界与实际阅读范围见[REF-008](REF-008_PCBA-AOI指导副本与平台采纳映射.md#roi-metrology-adoption)。源控件固定Profile、混合native/managed实现选择和验证状态均只作差异输入，不是平台已经批准或已运行的证据。

<a id="surface-source-research"></a>
## 三维滤波、配准与距离的官方/固定源码研究 — 2026-09-28

消费者：DEV-VIS-028/029、PKG-029/031/060、DEV-MET-031与FS-014。优先AsunImage/HALCON及已有ROI公共能力；本轮未安装/引入Open3D、未运行native或上游测试。URL中的版本仅固定官方研究来源，不固定平台HALCON版本。

| 官方实际阅读范围 | 已落实的实施限制 |
|---|---|
| register_object_model_3d_pair Description、pose_ref参数及Execution Information | 输出1→2，matching与icp初值不同，无重叠无pose，Score不是概率；约0.1%尺寸数值精度限制；支持中断/超时但公共调用仍需明确传播 |
| register_object_model_3d_global Description、From/To与generic参数及Execution Information | 已知近似关系；global/previous/显式边三种输入；12项刚体矩阵，显式图需连通；Scores为重叠邻居数；无重叠可异常；同样数值尺度限制 |
| sample_object_model_3d Description | fast选原点且复制扩展属性；accurate可造重心且不复制扩展属性；xyz_mapping单位像素；混合拓扑优先级/新点/丢属性 |
| smooth_object_model_3d Description及Execution Information | MLS移动点；abs_sigma覆盖relative；normal朝原点不等于产品正面；mapping滤波断面伪影、偶数窗口升奇数及median正方约束 |
| surface_normals_object_model_3d Description | MLS估法向不移动点；triangles和2D mapping的条件；已有triangle_normal属性不覆盖；无法估计可返回零向量 |
| select_points_object_model_3d Description | 条件交集及拓扑适配；第N近邻距离与平均K近邻不同；num_neighbors_fast是近似 |
| distance_object_model_3d Description/参数语义及Execution Information | 修改From扩展属性；auto类型选择；MaxDistance截断/0不截断；closest index限制；signed依赖法向/方向；voxel近似与缓存 |

原始文本保存正文但部分HTML公式/表格图形未被文本提取，不从空白猜公式。本轮引用所读自然语言和明确独立推导的几何；原生线程安全标注不证明共享可变handle可并发写。

| 官方页 | 本地正文 | SHA-256 |
|---|---|---|
| [distance_object_model_3d](https://www.mvtec.com/doc/halcon/2511/en/distance_object_model_3d.html) | [正文](<official/halcon/20260928/distance_object_model_3d.txt>) | `ab23c92fb9b75a761c497fbd699363f6c42bf90d5e14b681e7821729461b6d88` |
| [register_object_model_3d_global](https://www.mvtec.com/doc/halcon/2511/en/register_object_model_3d_global.html) | [正文](<official/halcon/20260928/register_object_model_3d_global.txt>) | `fba5a8c0926c81fb86ca563fd1139a4496eb09d47ae588946883bf96b8eac6d9` |
| [register_object_model_3d_pair](https://www.mvtec.com/doc/halcon/2511/en/register_object_model_3d_pair.html) | [正文](<official/halcon/20260928/register_object_model_3d_pair.txt>) | `b4e8f664a490f12807fab19ff6b672e4c5bb26727f1c473d21762318e1e8d463` |
| [sample_object_model_3d](https://www.mvtec.com/doc/halcon/2511/en/sample_object_model_3d.html) | [正文](<official/halcon/20260928/sample_object_model_3d.txt>) | `a919da631598ad1763eeb5d24f931f8f21e3dc0f441398a31c8b14b2d93b557c` |
| [select_points_object_model_3d](https://www.mvtec.com/doc/halcon/2511/en/select_points_object_model_3d.html) | [正文](<official/halcon/20260928/select_points_object_model_3d.txt>) | `0497c4a862d6551098426e7d222b3030fd04df37f2aa4dd75ef1d8d612e3837e` |
| [smooth_object_model_3d](https://www.mvtec.com/doc/halcon/2511/en/smooth_object_model_3d.html) | [正文](<official/halcon/20260928/smooth_object_model_3d.txt>) | `431ed62060b7ae91ecbef3722a58b49af1135b329cf0c7c042625233aa5128e2` |
| [surface_normals_object_model_3d](https://www.mvtec.com/doc/halcon/2511/en/surface_normals_object_model_3d.html) | [正文](<official/halcon/20260928/surface_normals_object_model_3d.txt>) | `1eed87799b6bd036c923890cbedc67f7d26da395695d844e668fbd8107455745` |

Open3D沿用固定开发快照`b6c5e196384ad71e75b6e6f9c5da22d046221f1d`，不是平台发行版本。新增5文件归档；实际阅读：Registration实现1–195、TransformationEstimation实现1–123、PointCloud实现367–476及582–691；两个registration测试文件全文（分别46/38行）。既有PointCloud测试718–796及LICENSE全文复读；CMakeLists中构建选项/依赖行定向查看。

- Registration空对应给fitness=0和RMSE=0；fitness分母为源点数，非双向面积覆盖。ICP迭代是左乘update，停止用相邻fitness/RMSE的**绝对差**比较命名为relative的参数；不把名称当相对误差或生产门槛。
- 点面计算用点/目标法向Jacobian，空对应/缺法向或求解失败可能返回identity（入口另有法向检查）；没有变化不能当已正确收敛。秩/噪声/对称等质量仍要独立证明。代码用了Eigen/TBB/内部KDTree，直接移植不是仅复制一个函数。
- 普通Voxel原点为当前min_bound减半体素；AndTrace显式min_bound可固定多尺度坐标并保留贡献。unordered_map输出顺序不能用于稳定身份；测试对输出重排后比较。平台借鉴贡献映射与反例，不直接承诺上游输出排序/源哈希确定性。
- Radius源码按搜索返回邻居数严格大于nb_points；Statistical计算标准差用n−1且最后严格小于阈值、排除均距非正项；不能不核KDTree自身/边界语义就映射成源ROI的排自身、包含等号规则。单点/重合点/边界必须专门验证，不在本次未运行条件下断言上游全局缺陷。
- 本次两个配准测试文件内容均为DISABLED/NotImplemented占位，因此不能作为这些路线的有效测试覆盖证据；这不等于宣称整个Open3D没有其它测试。已读PointCloud的VoxelDownSample测试为实际构造输入/期望，但未运行。
- 根MIT要求保留版权及许可文字；CMake默认测试关闭，另含Python/GUI/ISPC及可选CUDA/SYCL等构建路径。当前只借鉴公开算法结构和验证思路，不加入二进制或传递依赖；如未来直接复制/编译需逐文件与实际依赖范围复核，不靠根MIT推定所有第三方相同许可。

| 固定源码/测试 | SHA-256 | Git blob SHA-1 |
|---|---|---|
| [cpp/open3d/geometry/PointCloud.cpp](<open-source/isl-org_Open3D/b6c5e196384ad71e75b6e6f9c5da22d046221f1d/cpp/open3d/geometry/PointCloud.cpp>) · [上游](https://github.com/isl-org/Open3D/blob/b6c5e196384ad71e75b6e6f9c5da22d046221f1d/cpp/open3d/geometry/PointCloud.cpp) | `9d31ff094145e2be55d17b18da1ada84039522fc7878914c347c118ec5fb1ee1` | `bab5b65766ff4d255008e71d905a1b054d4b4192` |
| [cpp/open3d/pipelines/registration/Registration.cpp](<open-source/isl-org_Open3D/b6c5e196384ad71e75b6e6f9c5da22d046221f1d/cpp/open3d/pipelines/registration/Registration.cpp>) · [上游](https://github.com/isl-org/Open3D/blob/b6c5e196384ad71e75b6e6f9c5da22d046221f1d/cpp/open3d/pipelines/registration/Registration.cpp) | `456dac720f38c0903d275c4d6ec7eb07e9cc73595dd55d9181cd4dc3f43b9f06` | `5c08e4c7c439a259f325eb102a76c79285bb3023` |
| [cpp/open3d/pipelines/registration/TransformationEstimation.cpp](<open-source/isl-org_Open3D/b6c5e196384ad71e75b6e6f9c5da22d046221f1d/cpp/open3d/pipelines/registration/TransformationEstimation.cpp>) · [上游](https://github.com/isl-org/Open3D/blob/b6c5e196384ad71e75b6e6f9c5da22d046221f1d/cpp/open3d/pipelines/registration/TransformationEstimation.cpp) | `f45814c59aeaa2d32d1d4866d4cb10a1dfa060119aef1247bac61fcf9b763f15` | `494c201ea9eeb55b36eaa00c0f02ae643fda4c2a` |
| [cpp/tests/pipelines/registration/Registration.cpp](<open-source/isl-org_Open3D/b6c5e196384ad71e75b6e6f9c5da22d046221f1d/cpp/tests/pipelines/registration/Registration.cpp>) · [上游](https://github.com/isl-org/Open3D/blob/b6c5e196384ad71e75b6e6f9c5da22d046221f1d/cpp/tests/pipelines/registration/Registration.cpp) | `5b9112a01d16aae2c617dd7bff97a6567025fbf8a9d56c6befde5b213ac2848d` | `4b12a8f5f83546677be35b7bdf0609471a8815f1` |
| [cpp/tests/pipelines/registration/TransformationEstimation.cpp](<open-source/isl-org_Open3D/b6c5e196384ad71e75b6e6f9c5da22d046221f1d/cpp/tests/pipelines/registration/TransformationEstimation.cpp>) · [上游](https://github.com/isl-org/Open3D/blob/b6c5e196384ad71e75b6e6f9c5da22d046221f1d/cpp/tests/pipelines/registration/TransformationEstimation.cpp) | `3f01941966c3257c056aec9bafb0e24fc66f8867f3a6d5886f0448a1ae381007` | `75abc6eb5c012e83bba009697b4e573beee858a7` |

适配/来源原文的实际采纳见[REF-008](REF-008_PCBA-AOI指导副本与平台采纳映射.md#surface-adoption)。软件合成数值、计量资格和竞品同板对比仍各自验证，本轮不据源码优劣评价生产表现。

<a id="runtime-source-research"></a>
## 程序发布、Task等待与资源调度的研究 — 2026-09-28

本轮落实[PKG-035](../shared-modules/packages/PKG-035_ProgramPackage.md#program-lifecycle)、[DEV-PLT-011](<../shared-modules/guidance/02-platform/DEV-PLT-011_Inspection Pipeline与Attempt开发指导.md#typed-execution-graph>)及[DEV-PLT-014 §10–11](../shared-modules/guidance/02-platform/DEV-PLT-014_性能预算与并发流水线开发指导.md#resource-liveness)。没有选定EF/数据库，没有引入RateLimiting或任何新生产依赖；不检查AsunImage/DevExpress授权。沿用已有.NET Channels源码结论，不重复拷贝。

### 官方正文及精确归档

阅读范围：WaitAsync API定义/返回语义，WhenAll完成/异常/取消/空集合约定，TimeProvider时间戳与System实现（归档60–98行），EF并发token/0行冲突/插入异常差异（36–179行的相关段），EF事务/SaveChanges/savepoint/provider限制（32–117行）。网页为此次抓取时的官方内容，URL的view参数不构成某个运行时二进制已验证；API关键行为另与固定源码对照。

| 来源 | 本地正文 | SHA-256 |
|---|---|---|
| [efcore-concurrency](https://learn.microsoft.com/en-us/ef/core/saving/concurrency) | [归档](official/dotnet/20260928/efcore-concurrency.txt) | `9ac5612da7c54cc62d46987c01c767b26b736a4c96dcb45bc14663d68851d3a5` |
| [timeprovider-overview](https://learn.microsoft.com/en-us/dotnet/standard/datetime/timeprovider-overview) | [归档](official/dotnet/20260928/timeprovider-overview.txt) | `df48bd6d460328575e58e1b2b7171150bb6c7dc847a3d24a11e9495619c1c592` |
| [task-waitasync](https://learn.microsoft.com/en-us/dotnet/api/system.threading.tasks.task.waitasync?view=net-10.0) | [归档](official/dotnet/20260928/task-waitasync.txt) | `f9593184e126158d43ad1ca7a09c578ceecd567b58146aac6ea6302c40e82219` |
| [task-whenall](https://learn.microsoft.com/en-us/dotnet/api/system.threading.tasks.task.whenall?view=net-10.0) | [归档](official/dotnet/20260928/task-whenall.txt) | `e74fcfd3a01465403d31b324935387dfece8431c7765850cda06499fac2533a4` |
| [efcore-transactions](https://learn.microsoft.com/en-us/ef/core/saving/transactions) | [归档](official/dotnet/20260928/efcore-transactions.txt) | `300bbd9ce7e5526d00a762141d96dd7565a7d7cbbc6d5e599792a59126fcc720` |

### 固定GitHub源码和测试

dotnet/runtime commit `60629d14374c56f1cb51819049ad1fa529307f8d`，根MIT许可证沿既有归档；采用公共.NET行为/设计经验，不拷贝实现进入产品。测试工程依赖仓库Build、xUnit/AssertExtensions等，读取测试不等于已经运行。若未来实际复制代码，保留版权/许可并按目标程序集依赖单独处理。

| 固定文件 | 本次真实阅读与限制 | SHA-256 |
|---|---|---|
| [ConcurrencyLimiter.cs](https://github.com/dotnet/runtime/blob/60629d14374c56f1cb51819049ad1fa529307f8d/src/libraries/System.Threading.RateLimiting/src/System/Threading/RateLimiting/ConcurrencyLimiter.cs) / [本地](open-source/dotnet_runtime/60629d14374c56f1cb51819049ad1fa529307f8d/src/libraries/System.Threading.RateLimiting/src/System/Threading/RateLimiting/ConcurrencyLimiter.cs) | 143–320 排队permit计数、NewestFirst淘汰、归还/取消竞态、排头不足即停止；其它段只定向搜索 | `8d5f8fcbd0be37aa95f182f02b6fcdb5445f70609a5592ea898be9d563568ed4` |
| [Task.cs](https://github.com/dotnet/runtime/blob/60629d14374c56f1cb51819049ad1fa529307f8d/src/libraries/System.Private.CoreLib/src/System/Threading/Tasks/Task.cs) / [本地](open-source/dotnet_runtime/60629d14374c56f1cb51819049ad1fa529307f8d/src/libraries/System.Private.CoreLib/src/System/Threading/Tasks/Task.cs) | 2832–2938 WaitAsync代理/清理；6048–6202 WhenAll剩余计数/错误聚合，未全文审计 | `5b0d6892267269233dcf5c6191f357b0ba6c4257d1e757ca4d2fe93272b29d9b` |
| [ConcurrencyLimiterTests.cs](https://github.com/dotnet/runtime/blob/60629d14374c56f1cb51819049ad1fa529307f8d/src/libraries/System.Threading.RateLimiting/tests/ConcurrencyLimiterTests.cs) / [本地](open-source/dotnet_runtime/60629d14374c56f1cb51819049ad1fa529307f8d/src/libraries/System.Threading.RateLimiting/tests/ConcurrencyLimiterTests.cs) | 69–95、173–241、565–620、645–670；FIFO/淘汰/取消与计数的实际断言，未执行 | `dee01842bae3bba9f45c649d76e286e8fff1afa8d5d4f98c3daf456369425440` |
| [System.Threading.RateLimiting.Tests.csproj](https://github.com/dotnet/runtime/blob/60629d14374c56f1cb51819049ad1fa529307f8d/src/libraries/System.Threading.RateLimiting/tests/System.Threading.RateLimiting.Tests.csproj) / [本地](open-source/dotnet_runtime/60629d14374c56f1cb51819049ad1fa529307f8d/src/libraries/System.Threading.RateLimiting/tests/System.Threading.RateLimiting.Tests.csproj) | 全文：仓库TargetFramework属性、测试Compile及本项目引用；未脱离仓库构建 | `b02f52d5f96d9412195df3401220007b22dafe1c4d30c89f9010e5c99cf08267` |
| [TaskRtTests.cs](https://github.com/dotnet/runtime/blob/60629d14374c56f1cb51819049ad1fa529307f8d/src/libraries/System.Runtime/tests/System.Threading.Tasks.Tests/Task/TaskRtTests.cs) / [本地](open-source/dotnet_runtime/60629d14374c56f1cb51819049ad1fa529307f8d/src/libraries/System.Runtime/tests/System.Threading.Tasks.Tests/Task/TaskRtTests.cs) | 只做WaitAsync/WhenAll定位搜索，未找到对应方法；保留检索范围，不作为行为证据 | `27fa4f56273d730d5cb0266947ac10281b78ec73471281673c55721034c11366` |
| [TaskRtTests_Core.cs](https://github.com/dotnet/runtime/blob/60629d14374c56f1cb51819049ad1fa529307f8d/src/libraries/System.Runtime/tests/System.Threading.Tasks.Tests/Task/TaskRtTests_Core.cs) / [本地](open-source/dotnet_runtime/60629d14374c56f1cb51819049ad1fa529307f8d/src/libraries/System.Runtime/tests/System.Threading.Tasks.Tests/Task/TaskRtTests_Core.cs) | 只做WaitAsync/WhenAll定位搜索，未找到对应方法；不据此推断上游缺测试 | `4bfd3bf2e658b5ed2feadf0996fe39cecba815947b4c03cd3f17e73d82f373ca` |
| [MethodCoverage.cs](https://github.com/dotnet/runtime/blob/60629d14374c56f1cb51819049ad1fa529307f8d/src/libraries/System.Runtime/tests/System.Threading.Tasks.Tests/MethodCoverage.cs) / [本地](open-source/dotnet_runtime/60629d14374c56f1cb51819049ad1fa529307f8d/src/libraries/System.Runtime/tests/System.Threading.Tasks.Tests/MethodCoverage.cs) | 427–447空集合、656–730两个错误、924–988错误+取消；实际断言，未执行；未定位WaitAsync专项测试 | `52b96fffff4fac99b9493e856d41dbb17ce537781a79fc33eb48c7cdafe3f9da` |

### 可借鉴行为与不可扩大结论

- WaitAsync代理超时/取消清理continuation，不终止源Task；源任务仍持有帧和permit。已完成源Task可能直接返回，取消不能倒改既有完成。平台要单独观察源任务及最终释放。
- WhenAll等全部结束，Fault优先于Cancel，空集合成功；不自动取消其它分支。上游断言明确异常顺序不保证，平台逐节点保持原因/身份；无Task不等于必检完成。
- ConcurrencyLimiter按permit和排队，不是按作业条数；NewestFirst可淘汰旧等待者，生产不能静默照搬。单维工具不证明多维资源和join内存无死锁；相应组合算例已放DEV-PLT-014。
- TimeProvider区分UTC和Stopwatch时间戳；平台再定义同epoch期限/重启恢复，不能把UTC回拨或重启用于无限延长。
- EF官方并发例说明比较原token、冲突需业务解决；批量相关字段不因分开列就可安全合并。事务约束仅覆盖受支持provider/连接内操作，不能证明对象存储pin与发布记录原子；发布保持/可见性/恢复协议属于平台设计提案。

以上源码没有提供PCB调度、发布/GC协议、工业实时保证或平台性能证据。当前只验证文档/来源/独立算例，产品并发、存储耐久及WPF行为仍待实现验证。

<a id="evidence-source-research"></a>
## 结果证据、耐久与存储事务研究 — 2026-09-28

消费者为[DEV-PLT-012](<../shared-modules/guidance/02-platform/DEV-PLT-012_Evidence Graph与Result Commit开发指导.md#evidence-commit-protocol>)、[PKG-041](../shared-modules/packages/PKG-041_Storage.md#storage-transactions-durability)和FS-004/UI-PCS-013。复用先前Npgsql LICENSE/csproj、EF事务和PostgreSQL隔离资料，不重复拷贝。PostgreSQL仍是候选，未安装/连接数据库，未改变机器缓存或文件系统配置。

### 官方正文

读取FileStream.Flush的API/Boolean与中间缓冲Remarks；File.Move的跨卷/复制/删除/原子性Remarks；Windows FlushFileBuffers的64–90行语义与缓存/写透说明；PostgreSQL异步提交60–89行及可靠性161–174行的关键约束。PostgreSQL current本次内容为18文档，未据此冻结平台数据库版本。

| 官方资料 | 原文归档 | SHA-256 |
|---|---|---|
| [file-move](https://learn.microsoft.com/en-us/dotnet/api/system.io.file.move?view=net-10.0) | [本地](official/dotnet/20260928/file-move.txt) | `aad5495b21eb19c14cbf647182bee18e08c29d6855d8da405b19247484966ec2` |
| [filestream-flush](https://learn.microsoft.com/en-us/dotnet/api/system.io.filestream.flush?view=net-10.0) | [本地](official/dotnet/20260928/filestream-flush.txt) | `aa1ef8c3aebfb430a1d87bfa820566feb2b1acf4d48c1d165fc9592154ddb311` |
| [wal-reliability](https://www.postgresql.org/docs/current/wal-reliability.html) | [本地](official/postgresql/20260928/wal-reliability.txt) | `d06c0b4303aa8c2119c773c71a3a787e67213e9290cde12a15a72667da82ba37` |
| [flushfilebuffers](https://learn.microsoft.com/en-us/windows/win32/api/fileapi/nf-fileapi-flushfilebuffers) | [本地](official/windows/20260928/flushfilebuffers.txt) | `adf2fb530fe8a9af94d8ff6cc52bec7c8b4dd0b0996c662a5ccc8a0e72240836` |
| [wal-async-commit](https://www.postgresql.org/docs/current/wal-async-commit.html) | [本地](official/postgresql/20260928/wal-async-commit.txt) | `c4fab0a0da429f87cf4a3b0e8c2577de833e10db359517a5db9873bfdcd87b53` |

### 固定源码和真实测试断言

沿用npgsql/npgsql `d3768398c17877b3a916c3c4d87e8e11698991fc`（v10.0.3）；已有LICENSE为PostgreSQL式宽松条款，本轮不将源码移入产品。NpgsqlTransaction.cs读119–180、305–365行；TransactionTests.cs读CommitAsync 47–74、RollbackAsync/Dispose/Close/failed 105–174、超时回滚289–308的实际断言。测试依赖NUnit/仓库测试基类和真实PostgreSQL连接，未运行；Prepared+Multiplexing等分支有显式跳过，不扩大为所有模式覆盖。

| 固定源文件 | 本地副本 | SHA-256 |
|---|---|---|
| [NpgsqlTransaction.cs](https://github.com/npgsql/npgsql/blob/d3768398c17877b3a916c3c4d87e8e11698991fc/src/Npgsql/NpgsqlTransaction.cs) | [本地](open-source/npgsql_npgsql/d3768398c17877b3a916c3c4d87e8e11698991fc/src/Npgsql/NpgsqlTransaction.cs) | `2a44d5f8fcb23459fc1f1f5cacaecce6c1ae1df9cee4f254ff389ae446b9ec6c` |
| [TransactionTests.cs](https://github.com/npgsql/npgsql/blob/d3768398c17877b3a916c3c4d87e8e11698991fc/test/Npgsql.Tests/TransactionTests.cs) | [本地](open-source/npgsql_npgsql/d3768398c17877b3a916c3c4d87e8e11698991fc/test/Npgsql.Tests/TransactionTests.cs) | `e76cc2ffcda3771c0a91a4f8f80d7efb9f2c4a3ac3148482556da92fab7fad0d` |

### 设计取舍及限制

- Npgsql CommitAsync把CancellationToken传入内部提交命令；Dispose对仍pending事务尝试回滚，坏连接清理异常可被捕获。不能从方法名、Dispose返回或客户端取消推定业务确定回滚。平台保留同CommitIdentity回查未知结果；未审connector网络全部实现，不宣称已证明全部断网行为。
- Flush(true)请求中间缓冲落盘；File.Move跨卷是复制/删除，复制覆盖策略不是原子。内容持久与最终目录项发布分别验证；不将WriteThrough/同卷rename API调用本身当物理RPO=0。
- PostgreSQL异步提交可先返回成功、崩溃丢最近事务；async C#调用与数据库异步耐久配置不是同义。底层硬件缓存可能不遵守flush，所以产品耐久要在实际配置实验，不默认调缓存/断电。
- AOI来源区分坏结果持久化、Replay缺项与最小证据。平台据此修正FS-004模板把算法质量不合格当存储拒绝的错误；工艺NG与提交成功可以同时成立。blob去重与逻辑帧关联、通知至少一次与最终设备动作、GC扫描与新引用协调分别定义。

源码/文档不提供本平台跨存储原子性、完整备份恢复或物理RPO证明。工程选择、真实签名/Schema和目标耐久/性能仍按原门禁，不采用源AOI固定SQLite、全局角色、72小时、2秒或百万次作为平台默认。

<a id="replay-source-research"></a>
## 历史重放、数值差异与随机/时间研究 — 2026-09-28

消费者：[DEV-QLF-070](<../shared-modules/guidance/08-qualification/DEV-QLF-070_Golden Sample与Replay开发指导.md#replay-execution>)、043/055及UI014；复用已归档的040存储/038取消资料，不重拷。新增HALCON官方算子页用于公共行为，版本URL只表明研究来源，不冻结平台底层版本、不检查AsunImage内部或依赖许可。

### 官方阅读范围及固定归档

HALCON set_system读取146–166（参数作用域）、1650–1786（reentrant/线程预留）、2855–2926（线程随机种子和cuDNN确定性限制）；NumPy isclose读取参数、Notes有向公式/近零及示例；.NET TimeProvider读取时间/Stopwatch、FakeTimeProvider及计时相关重载。未据API存在声称完成调用适配。

| 官方资料 | 本地正文 | SHA-256 |
|---|---|---|
| [isclose](https://numpy.org/doc/2.3/reference/generated/numpy.isclose.html) | [归档](official/numpy/20260928/isclose.txt) | `fd6863e6e8cd8ef353939310af269f3c999be6b14b161e823da994f3249b9424` |
| [timeprovider-overview](https://learn.microsoft.com/en-us/dotnet/standard/datetime/timeprovider-overview) | [归档](official/dotnet/20260928/timeprovider-overview.txt) | `df48bd6d460328575e58e1b2b7171150bb6c7dc847a3d24a11e9495619c1c592` |
| [set_system](https://www.mvtec.com/doc/halcon/2411/en/set_system.html) | [归档](official/halcon/20260928/set_system.txt) | `ff9caba5f49414241b7734794572ffaad66155196b99457662ead7c8c9547211` |

### 固定Git源码与实际测试

NumPy v2.3.0，commit `0532af47d6a815298b7841de00bdbc547104b237`。numeric.py读1–45依赖及2472–2502实际计算；test_numeric.py读1–31依赖、3028–3113有限/非有限/容差数组/broadcast/精度断言、3151–3162 equal_nan、3190–3233不修改输入/非有限/容差警告等断言。未运行上游测试。LICENSE全文BSD-3-Clause，需保留版权/条款且不借名背书；pyproject前62行说明Python>=3.11、meson-python/Cython构建，numeric依赖NumPy原生核心，测试依赖pytest/hypothesis与编译扩展。本次仅借鉴语义与案例，未安装/引入产品依赖，也未把整个NumPy原生依赖闭包认定已审查。

| 固定文件 | 本地副本 | SHA-256 |
|---|---|---|
| [LICENSE.txt](https://github.com/numpy/numpy/blob/0532af47d6a815298b7841de00bdbc547104b237/LICENSE.txt) | [归档](open-source/numpy_numpy/0532af47d6a815298b7841de00bdbc547104b237/LICENSE.txt) | `1be1df33863f97a7bc1c4d67980bd6c69c9a6fef0a5ee76e6ad6cb91e56e8491` |
| [pyproject.toml](https://github.com/numpy/numpy/blob/0532af47d6a815298b7841de00bdbc547104b237/pyproject.toml) | [归档](open-source/numpy_numpy/0532af47d6a815298b7841de00bdbc547104b237/pyproject.toml) | `511c1f67793f5dc352c324fca4b2021f52b09d1d59060b36883df35f8c5b7aee` |
| [numpy/_core/numeric.py](https://github.com/numpy/numpy/blob/0532af47d6a815298b7841de00bdbc547104b237/numpy/_core/numeric.py) | [归档](open-source/numpy_numpy/0532af47d6a815298b7841de00bdbc547104b237/numpy/_core/numeric.py) | `fc3727bd7bbaa1a1d74a2f50f8157dc86cdfc7bb5cf620b1ebdafd3272439b98` |
| [numpy/_core/tests/test_numeric.py](https://github.com/numpy/numpy/blob/0532af47d6a815298b7841de00bdbc547104b237/numpy/_core/tests/test_numeric.py) | [归档](open-source/numpy_numpy/0532af47d6a815298b7841de00bdbc547104b237/numpy/_core/tests/test_numeric.py) | `a5b142846175d10b5d95c09cca972b7d3a79b4d2326f9b67cc660d3a42ba392e` |

### 采用与不采用的行为

- NumPy有向`atol+rtol*abs(b)`、shape/broadcast及精度类型的测试值得借鉴。平台比较前先按稳定目标/单位/有效性匹配；禁止广播丢失目标/通道，容差必须有单位与依据，不继承默认1e-8。
- 源码`x==y`使同号Inf相等，`equal_nan`可使双NaN相等；通用库此行为不能直接当工艺有效或回归准确。源容差非有限可按全局错误配置只警告；平台策略应直接拒绝非有限/负容差。具体域/拒绝字段进入原合同。
- HALCON随机源线程特定，不能UI线程一次设种子覆盖全部工作线程；reentrant=false失去线程安全；tsp线程预留可能推高总额。cuDNN确定性限于条件，不保证跨版本，不能凭开关宣称跨环境逐位一致。
- TimeProvider提供时间抽象和可控测试时间，不提供确定性并发scheduler；真实Stopwatch性能与模拟时间分开。未安装FakeTimeProvider包，未读取它的实现或运行其测试，不扩大官方概述结论。
- 相同输出不等于真值；原/候选数值接近可跨质量阈值。报告固定全部案例分母，双Invalid仅能满足事先定义的负例拒绝断言，不能补量测或生产资格。

这些来源不证明平台沙箱、native取消、Checkpoint、WPF或工业重复性。具体API、隔离能力、逐方法比较策略与真实样本仍有内部深化工作；不以营销、文档和公式反例冒充产品验收。

<a id="review-source-research"></a>
## 复判多站一致性、队列与操作证据 — 2026-09-28

消费者：[PKG-044](../shared-modules/packages/PKG-044_Review.md#review-transaction-flow)、[AOI返修指导](<../process-guides/guidance/06-domains/DEV-DOM-057D_AOI Review Rework与Disposition开发指导.md#aoi-review-closure>)、PG-023、UI005和FS063/066。本轮不选择etcd或PostgreSQL为平台部署，不安装依赖/服务，不改客户项目。已有数据库/Task/证据来源复用。

### 竞品原件直接核读

Koh Young C-Platform手册PDF第29页文本与渲染均核读：导航图按Failure Item List定位，独立2D/3D，单项Defect/Defect Pass与板级Pass/NG按钮分区。采纳导航/多视图/任务层级；按钮存在不证明Claim/事务/放行的内部协议。Viscom vVision三页宣传资料直接提取，第3页渲染核读；第2页verification images优化归档，第3页vVerify全景、角度彩色图和自定义视图。“100% traceability”是供应商宣传，不能证明我方或其未知内部一致性。该资料标October 2015，不能当2026最新性能数据。

| 只读原PDF | SHA-256 |
|---|---|
| [KohYoung_C-Platform_Operation_Manual_ENG.pdf](competitors/02_PCBA-AOI研究快照/research/operation_manuals/KohYoung/KohYoung_C-Platform_Operation_Manual_ENG.pdf) | `48d3031df057137a77d0aa066fe51025519fe74931e534275015e95aae7e3729` |
| [Viscom_vVision_Operation_Workflow_EN.pdf](competitors/02_PCBA-AOI研究快照/research/operation_manuals/Viscom/Viscom_vVision_Operation_Workflow_EN.pdf) | `2e29fa19440fd6727d7756bf21667e5b888b73313400a7fed85782a6040cef73` |

未重拷/重转Office资料。Poppler渲染物在`.work/review-design-20260928/`，部分未嵌字体产生替代警告；所需布局/文字可识别，不据替代字体核其原设计像素或字体指标。

### 官方行为依据

PostgreSQL SELECT正文读取1846–1886的SKIP LOCKED/行锁边界，以及1927–1953的ORDER BY＋行锁在READ COMMITTED下可因并发变更失序。etcd API guarantees读取28–156的KV/Watch、revision、线性化与超时不确定性。采用线性化点位于调用/响应之间的定义；任何已完成读都不能保证后续写之前状态不再改变，不能把“最近读过”当CAS。

| 官方资料 | 本地正文 | SHA-256 |
|---|---|---|
| [sql-select](https://www.postgresql.org/docs/18/sql-select.html) | [归档](official/postgresql/20260928/sql-select.txt) | `cd15c8a5fe914bad82cfa686a202cf46c2784333503a56d373f75bebe66a923e` |
| [api-guarantees](https://etcd.io/docs/v3.6/learning/api_guarantees/) | [归档](official/etcd/20260928/api-guarantees.txt) | `5491fad9de52badf7290abd6a5d95e29da1746d18bc4a79fc289c2d61df629b6` |

### 固定Git实现、真实测试和限制

etcd v3.6.0 commit `f5d605a93abe2fdfa13880aab0f1f3a4203628dd`。完整读取mutex.go的tryAcquire/Lock/Unlock/IsOwner、session.go的KeepAlive/Done/Orphan/Close；完整读取mutex_test.go和session_test.go实际断言。测试依赖真实etcd集成框架、客户端和testify，未运行。example_mutex_test.go有`forUnitTestsRunInMockedContext`及只打印结果的mock路径，虽然也有实际客户端分支，本轮没有读取其wrapper实现，不将示例输出作为真实互斥验证证据。

客户端目录的example_mutex_test.go实际是Git symlink（mode120000）；初次contents API解引用与原link blob不一致，已拒绝保存，改读真实`tests/integration/...`目标，未把同名副本当第二份测试。LICENSE是Apache-2.0，与先前OpenCV LICENSE逐字节相同，复用原文件并保留etcd URL/Git blob/hash；本轮重复临时副本已去重。阅读其授权、专利/再分发及NOTICE条件，不用仓库知名度代替许可。client/v3/go.mod前42行及tests/go.mod前65行说明Go1.23/toolchain、gRPC/zap、etcd模块及本地replace；未审完整传递依赖闭包、不引入Go运行时。

| 固定源文件 | 本地唯一副本 | SHA-256 |
|---|---|---|
| [LICENSE](https://github.com/etcd-io/etcd/blob/f5d605a93abe2fdfa13880aab0f1f3a4203628dd/LICENSE) | [归档（复用）](open-source/opencv_opencv/a0cda081f8d769f40ab2f4904738b4787b44d07c/LICENSE) | `cfc7749b96f63bd31c3c42b5c471bf756814053e847c10f3eb003417bc523d30` |
| [client/v3/go.mod](https://github.com/etcd-io/etcd/blob/f5d605a93abe2fdfa13880aab0f1f3a4203628dd/client/v3/go.mod) | [归档](open-source/etcd-io_etcd/f5d605a93abe2fdfa13880aab0f1f3a4203628dd/client/v3/go.mod) | `4699fcaee47fa5629a69e1e96223e271ab183579244200631c993c6e640744d6` |
| [client/v3/concurrency/mutex.go](https://github.com/etcd-io/etcd/blob/f5d605a93abe2fdfa13880aab0f1f3a4203628dd/client/v3/concurrency/mutex.go) | [归档](open-source/etcd-io_etcd/f5d605a93abe2fdfa13880aab0f1f3a4203628dd/client/v3/concurrency/mutex.go) | `b0ff0a00592150570f2ab893f61040585561b6e14ee1b9fe55cef8b467866388` |
| [tests/go.mod](https://github.com/etcd-io/etcd/blob/f5d605a93abe2fdfa13880aab0f1f3a4203628dd/tests/go.mod) | [归档](open-source/etcd-io_etcd/f5d605a93abe2fdfa13880aab0f1f3a4203628dd/tests/go.mod) | `617700f26a72e2fb8302a0b85dfeee672da671fe05b098de54a93663a667bc1b` |
| [client/v3/concurrency/session.go](https://github.com/etcd-io/etcd/blob/f5d605a93abe2fdfa13880aab0f1f3a4203628dd/client/v3/concurrency/session.go) | [归档](open-source/etcd-io_etcd/f5d605a93abe2fdfa13880aab0f1f3a4203628dd/client/v3/concurrency/session.go) | `5e1aa4a0b2653ddfa6f6fab5adc24cb7847a36811c6b9531fdc1e3f156c95fbe` |
| [tests/integration/clientv3/concurrency/mutex_test.go](https://github.com/etcd-io/etcd/blob/f5d605a93abe2fdfa13880aab0f1f3a4203628dd/tests/integration/clientv3/concurrency/mutex_test.go) | [归档](open-source/etcd-io_etcd/f5d605a93abe2fdfa13880aab0f1f3a4203628dd/tests/integration/clientv3/concurrency/mutex_test.go) | `6d95a92b9d210de14ff1ed9ecc6eac2e88fb00c75b57f37376786106c267a40f` |
| [tests/integration/clientv3/concurrency/session_test.go](https://github.com/etcd-io/etcd/blob/f5d605a93abe2fdfa13880aab0f1f3a4203628dd/tests/integration/clientv3/concurrency/session_test.go) | [归档](open-source/etcd-io_etcd/f5d605a93abe2fdfa13880aab0f1f3a4203628dd/tests/integration/clientv3/concurrency/session_test.go) | `dbcfbb78a6fe47e8ad5f2f7b3fa8478f0727b7a385d5aa878ee3be50cae300e0` |
| [tests/integration/clientv3/concurrency/example_mutex_test.go](https://github.com/etcd-io/etcd/blob/f5d605a93abe2fdfa13880aab0f1f3a4203628dd/tests/integration/clientv3/concurrency/example_mutex_test.go) | [归档](open-source/etcd-io_etcd/f5d605a93abe2fdfa13880aab0f1f3a4203628dd/tests/integration/clientv3/concurrency/example_mutex_test.go) | `d950b7fff886493f450881760840bfc19e3cc78e6773d7387413de03d8e4b50e` |

### 采用、修正与不外推

- etcd Mutex以租约key的CreateRevision区分取得次序，IsOwner返回可用于该存储事务的条件；可借鉴代/fence防旧worker。它不会自动保护另一个SQL库或物理设备，不能拿一次etcd锁检查当跨库原子提交。平台继续原Review事务/CAS，未引入分布式锁产品。
- 实际测试覆盖等待锁时Session撤销、未领取/重复Unlock拒绝、Orphan/上下文取消和TTL设置；没有因此证明平台Claim秘密恢复、外部授权撤销、批量屏障或设备安全。源码Done也可能因停止刷新关闭，不证明客户端本地观察瞬间就是服务端租约到期时刻。
- Watch可无界延迟、串行化读取可旧；队列/租约订阅只提示，提交点仍按原事务验证。超时/断连可能不知道事务结果，恢复同一操作，不能新键重发。
- PostgreSQL SKIP LOCKED适于队列避竞争但给不一致视图，且不免除表级锁；一次空结果不证明没有待办，也不证明全局优先次序。严格高优先层若持续占满服务能力，普通任务最大等待不能单凭aging保证；平台补容量/资格过滤/可批准公平配额和过载升级。
- 原AOI协议的“Claim过期”只拒绝新写，先前合法成功回执仍在当前权限下可查询；校验摘要不能重建随机秘密；逐项回执不能被UI一次点击包装为整板原子。源固定加密/SQLite/角色、审批/超时数值不直接迁入。

本轮证据只支持设计取舍和反例，不证明已实现或国际竞品指标达成。

<a id="consensus-research"></a>
## 多轮复核、共识与真值研究 — 2026-09-28

固定CVAT `v2.76.0` commit `b78c39f7a5de6450567e77c9e1ffc8f0c428cea7`，来源由GitHub tag与Git tree定位，Git blob和SHA-256核对。官方网站说明采用该commit内`site/content/en/docs/qa-analytics/consensus.md`原文，不混用另一版本页面。raw下载连接失败后改从同blob API取得原字节，没有换commit或运行下载代码。

实际读取：官方说明1–257行（未渲染其中截图）；`intersect_merge.py`1–551行；`merging_manager.py`1–203行；models全22行、LICENSE全22行和pyproject全14行。测试文件仅读1–44、161–225、250–298、616–700行，其他只定位方法名；公共test helper/fixture及上游Datumaro基类未全审，未运行测试。requirements/base.txt定向核文件包含关系及attrs/Datumaro/Django/DRF/Redis/RQ/SciPy，不声称完整传递依赖/安全审查；pyproject仅格式工具设置，不是运行依赖清单。

| 固定源文件 | 本地唯一副本 | SHA-256 |
|---|---|---|
| [LICENSE](https://github.com/cvat-ai/cvat/blob/b78c39f7a5de6450567e77c9e1ffc8f0c428cea7/LICENSE) | [归档](open-source/cvat-ai_cvat/b78c39f7a5de6450567e77c9e1ffc8f0c428cea7/LICENSE) | `f0c98c1710670f97a3dfab70829ec8739c12898463a6eb1bbddfc21821ae9c63` |
| [cvat/apps/consensus/intersect_merge.py](https://github.com/cvat-ai/cvat/blob/b78c39f7a5de6450567e77c9e1ffc8f0c428cea7/cvat/apps/consensus/intersect_merge.py) | [归档](open-source/cvat-ai_cvat/b78c39f7a5de6450567e77c9e1ffc8f0c428cea7/cvat/apps/consensus/intersect_merge.py) | `8fc1113f44d00005313aef32dee8910f8d90663e65f9cf9bfa54adaa747ff0d2` |
| [cvat/apps/consensus/merging_manager.py](https://github.com/cvat-ai/cvat/blob/b78c39f7a5de6450567e77c9e1ffc8f0c428cea7/cvat/apps/consensus/merging_manager.py) | [归档](open-source/cvat-ai_cvat/b78c39f7a5de6450567e77c9e1ffc8f0c428cea7/cvat/apps/consensus/merging_manager.py) | `698eeea4ea5a413dab2fa9fbb14eb09a61043e8b01af29ff4dc1c5bbb70c4dae` |
| [cvat/apps/consensus/models.py](https://github.com/cvat-ai/cvat/blob/b78c39f7a5de6450567e77c9e1ffc8f0c428cea7/cvat/apps/consensus/models.py) | [归档](open-source/cvat-ai_cvat/b78c39f7a5de6450567e77c9e1ffc8f0c428cea7/cvat/apps/consensus/models.py) | `27f3854b73bc0eab8d39eb22dc0758fb005d9b37465ee9dfbed4c83523a91ffb` |
| [cvat/requirements/base.txt](https://github.com/cvat-ai/cvat/blob/b78c39f7a5de6450567e77c9e1ffc8f0c428cea7/cvat/requirements/base.txt) | [归档](open-source/cvat-ai_cvat/b78c39f7a5de6450567e77c9e1ffc8f0c428cea7/cvat/requirements/base.txt) | `7eed9ba6e2456acb05584a32e6d9f31bd0d83843c1234af5c1e7298949ef66c9` |
| [pyproject.toml](https://github.com/cvat-ai/cvat/blob/b78c39f7a5de6450567e77c9e1ffc8f0c428cea7/pyproject.toml) | [归档](open-source/cvat-ai_cvat/b78c39f7a5de6450567e77c9e1ffc8f0c428cea7/pyproject.toml) | `f26abd9d46ae0e617e7478b7f0e30952fca08870409dc18df1567119a8f41220` |
| [site/content/en/docs/qa-analytics/consensus.md](https://github.com/cvat-ai/cvat/blob/b78c39f7a5de6450567e77c9e1ffc8f0c428cea7/site/content/en/docs/qa-analytics/consensus.md) | [归档](open-source/cvat-ai_cvat/b78c39f7a5de6450567e77c9e1ffc8f0c428cea7/site/content/en/docs/qa-analytics/consensus.md) | `a93a08a773c19819e9edf77b0df7d6d23716f16c8854c3fa8ccb8eee23ce2653` |
| [tests/python/rest_api/test_consensus.py](https://github.com/cvat-ai/cvat/blob/b78c39f7a5de6450567e77c9e1ffc8f0c428cea7/tests/python/rest_api/test_consensus.py) | [归档](open-source/cvat-ai_cvat/b78c39f7a5de6450567e77c9e1ffc8f0c428cea7/tests/python/rest_api/test_consensus.py) | `95616b8000293c68c7dd5e64fdebac74f4a0e3e853ef6a19dfbad80826d7b678` |

### 可借鉴与必须修正的边界

- 官方说明推荐完成所有副本后合并，但明确最低条件只需至少一个副本不是annotation/new；manager 73–87行按该条件取实际集合，不能当作平台全体必审已完成。分配数、完成数和进入计算的数据集数应分别保存。
- manager 120–149行清除父任务标注再导入，随后标completed；官方131–148行也明确覆盖且不能Undo。适合该工具的派生标注工作流，不适合平台追加式人判/仲裁，更不能删除原机判。普通任务导出还不含replica，来源保存须专门验证。
- ShapeMerger 453–497行选择标签得票最大值，以参与数据集数为分母并将score舍入两位；平票没有业务仲裁规则。LabelMerger 425–445行保留各标签计数/分数。它们不是校准正确概率，不能按UI近似votes签发处置或真值。
- 几何采用候选匹配/cluster近似约束和同来源检查，图形选择为接近平均包围框的原候选，非工业量测；继承Datumaro及多种比较器，完整正确性/次序独立性尚未验证。平台已有稳定Item先按身份关联；自由标注才允许版本化候选匹配。相似关系不传递、少数微缺陷不能因低分自动删。
- tests 616–700的真实断言同时保留全体支持框score=1及仅一个副本标出的框score=1/n；161–225与250–298有无consensus、无可合并任务、误用replica及权限/状态读取拒绝断言。没有据此证明平票、盲审独立性、审批权限、工业安全或平台恢复。待后台任务helper未审，不把调用语句当完整测试通过。
- MIT根许可允许依约复用并保留版权/许可；源headers也标MIT。实际运行栈是Python/Django/DRF、Redis/RQ及固定Datumaro fork `6ade96fa82043fc5bccd59a27218892899fe10ce`等，不能直接当作.NET独立仲裁DLL。未审全依赖许可/部署，未引入CVAT或外部服务。候选用途是离线标注适配，当前仅借鉴设计与反例。

落点为[044多轮/仲裁](../shared-modules/packages/PKG-044_Review.md#review-rounds-arbitration)、[真值接收](../shared-modules/guidance/07-ai/DEV-AI-063_数据集、GroundTruth与统计验证开发指导.md#review-to-ground-truth)及[UI005](../shared-modules/guidance/14-page-contracts/UI-PCS-005_Review_Workspace.md#review-arbitration-ui)。几何优先复用HALCON/AsunImage与原ROI能力；本研究没有新增视觉算法或生产部署。CVAT是标注工具参考，不是AOI国际性能对标证据；先前已直接核读的Koh Young/Viscom复判界面仍只支持页面布局，不证明内部多人仲裁。

<a id="viewer-source-research"></a>
## 原图Viewer、坐标与显示资源研究 — 2026-09-28

本轮沿已有Asun_ROI公共控件/AsunImage路径，不引入新渲染库。DevExpress WPF布局技能用于Dock工作台与Layout表单职责参考；所读技能标26.1，不是25.2.3 API验收。本会话没有dxdocs可调用工具，未据此猜具体属性/方法；具体版本API仍在实际切片用官方资料绑定，不变成依赖/授权核验。

### 实际读取的官方说明

HALCON引用URL中的版本仅定位所读来源，不恢复平台底层固定版本。最初无版本URL返回404，随后从既有研究定位正确版本路径，仅补抓缺失官方4份，没有重抓固定Git源。文本抽取合并了多语言签名且部分数学公式为网页图像未保留，不能据抽取丢失的公式猜变换；本文采用可读叙述和已有007约定。

| 官方正文 | 本地唯一文本 | SHA-256 |
|---|---|---|
| [convert_coordinates_window_to_image](https://www.mvtec.com/doc/halcon/2511/en/convert_coordinates_window_to_image.html) | [文本](official/halcon/20260928/convert_coordinates_window_to_image.txt) | `e0bda27d5bd7879b1179c04ffb5dede4e4e6eee3db840ef1f14127d37945d5a1` |
| [disp_object_model_3d](https://www.mvtec.com/doc/halcon/2511/en/disp_object_model_3d.html) | [文本](official/halcon/20260928/disp_object_model_3d.txt) | `ab4665d3c3d75ac934d10a6e427b5de6d37ba35f60122bafa3098ffc8403a1df` |
| [get_grayval](https://www.mvtec.com/doc/halcon/2511/en/get_grayval.html) | [文本](official/halcon/20260928/get_grayval.txt) | `f8aa9f50e1dd5146cd3b416f76e0d64035f091bded5402d2512a8897ed584789` |
| [set_part](https://www.mvtec.com/doc/halcon/2511/en/set_part.html) | [文本](official/halcon/20260928/set_part.txt) | `f7ade8e9de2c1482d696d23d15e735f8b313ee44b3494ada3c62bdfededd3fdc` |

- `set_part`24–86及参数/示例、`convert_coordinates_window_to_image`签名/Description/示例、`get_grayval`全文已读：窗口坐标转换依据当前显示part与窗口尺寸，不包含WPF DIP自动约定；set_part特殊值含基于最后显示图的适应模式，不能靠旧窗口状态推当前图。原值读取忽略reduced domain、多通道逐点返回各通道且有开销，平台独立核mask/边界并限制探针调用。
- `disp_object_model_3d`24–185、420–489定向读：展示相机/姿态可自动生成；原点云/三角模型的呈现不同；object/depth查询需persistence，兼容模式不使用这些参数；低显存和失效需显式恢复。只读了上述范围，不声称其它属性/全部三维算子已核实。窗口实际可见不保证可拾取，更不等于物理量测正确。
- 未运行HALCON/WPF/native或目标GPU测试；官方可从任何线程调用算子的说明不授予同一WPF窗口并发访问权，窗口/后端Owner仍串行安排呈现和释放。

### 固定开源源码及真实测试

OpenSeadragon `v6.1.1` commit `201d47833e3f10e9fa55159cd4203630521926b8`，tag/tree/Git blob和SHA-256均保留。实际全文阅读LICENSE、package.json、imageloader.js（625行）、test/modules/imageloader.js（86行）及tilecache-failure-regressions.js（435行）；tilecache.js仅读455–566、611–700、1312–1364、1529–1556，其他为定位搜索。没有运行QUnit/浏览器测试，也没有把测试源码当平台通过证据。

| 固定文件 | 本地唯一副本 | SHA-256 |
|---|---|---|
| [LICENSE.txt](https://github.com/openseadragon/openseadragon/blob/201d47833e3f10e9fa55159cd4203630521926b8/LICENSE.txt) | [归档](open-source/openseadragon_openseadragon/201d47833e3f10e9fa55159cd4203630521926b8/LICENSE.txt) | `17da96b26ac706d2cbd06d4555dedb43026782f4943faf0156fe7acf89454228` |
| [package.json](https://github.com/openseadragon/openseadragon/blob/201d47833e3f10e9fa55159cd4203630521926b8/package.json) | [归档](open-source/openseadragon_openseadragon/201d47833e3f10e9fa55159cd4203630521926b8/package.json) | `7b5a2369a0a15e3b43a2e660c9b66f6659aecb00fb1a65aa1f5ada47c1d38b43` |
| [src/imageloader.js](https://github.com/openseadragon/openseadragon/blob/201d47833e3f10e9fa55159cd4203630521926b8/src/imageloader.js) | [归档](open-source/openseadragon_openseadragon/201d47833e3f10e9fa55159cd4203630521926b8/src/imageloader.js) | `61eeeea51d0ea3aab9efaabb7cb77eb99a7cb34e93482a408d4aa1582dc39e05` |
| [src/tilecache.js](https://github.com/openseadragon/openseadragon/blob/201d47833e3f10e9fa55159cd4203630521926b8/src/tilecache.js) | [归档](open-source/openseadragon_openseadragon/201d47833e3f10e9fa55159cd4203630521926b8/src/tilecache.js) | `226464c57879dc3ed6d34d20f8430e6636ec79eb07d91011636d496edfd2e9cd` |
| [test/modules/imageloader.js](https://github.com/openseadragon/openseadragon/blob/201d47833e3f10e9fa55159cd4203630521926b8/test/modules/imageloader.js) | [归档](open-source/openseadragon_openseadragon/201d47833e3f10e9fa55159cd4203630521926b8/test/modules/imageloader.js) | `57ec0a8da76d0182c933684bc222d01d11e0d3c9877408affd009f23d39d9129` |
| [test/modules/tilecache-failure-regressions.js](https://github.com/openseadragon/openseadragon/blob/201d47833e3f10e9fa55159cd4203630521926b8/test/modules/tilecache-failure-regressions.js) | [归档](open-source/openseadragon_openseadragon/201d47833e3f10e9fa55159cd4203630521926b8/test/modules/tilecache-failure-regressions.js) | `e0733a6b6de3afe87365732687ad0a059014152088c0664eb9a54513dd5308db` |

1. ImageLoader有并发数量、超时、batch/retry及未开始队列clear；`jobLimit`不是排队字节上限，clear不证明在途下载/native已结束。平台需独立计算等待/在途/纹理峰值，并保证单次终结，不照抄JavaScript回调作生产资源协议。imageloader两测试只核默认/配置timeout传播，不覆盖全部取消竞态。
2. tilecache的延迟destroy等待promise完成、异步双缓冲检查旧槽身份再替换、绘制/加载/处理中的tile跳过驱逐、共享tile最后引用才卸缓存可借鉴。但其按缓存项数量控制及原位data覆盖不等价平台不可变证据/字节预算；析构捕获异常不证明外部GPU释放成功。
3. 回归真实断言覆盖插件抛出、转换失败后继续绘制且无未处理异常；释放抛错不破坏记录计数、null资源不调用析构；异步纹理替换期间旧纹理可用，替换后旧资源被free。测试使用定制drawer/常量tile及sleep，不证明真实显卡、内存长稳、工业权限或坐标精度。
4. 根许可为BSD-3-Clause，已阅读保留版权/条件、二进制附带声明和不得代言条款。package无运行dependencies字段，devDependencies包括Grunt/QUnit/Puppeteer/TypeScript等；未审完整构建/插件传递许可，不宣称整套无依赖。它是HTML/JavaScript查看器，不直接替代.NET/WPF已存在的ROI能力；当前仅借鉴设计与故障断言，未引入生产代码。

落点：[049](../shared-modules/packages/PKG-049_Viewport.md#viewport-display-protocol)、[DEV-UI-042](<../shared-modules/guidance/05-ui/DEV-UI-042_视觉/3D工作区与ROI交互开发指导.md#viewer-execution>)和[UI013](../shared-modules/guidance/14-page-contracts/UI-PCS-013_Evidence_Viewer.md#viewer-specific-operations)。既有Koh Young/Viscom原件上轮已直接读取/渲染，本轮复用其任务布局结论，未重复转换、没有新竞品性能证据。完整性/独立算例检查与产品测试分开。

<a id="library-programming-research"></a>
## 参考库、元件身份与AOI快速编程研究 — 2026-09-28

本轮复用现有AOI原指导/竞品PDF并直接读原页；新增固定OpenPnP源码与KiCad官方正文。设计落在[034公共库](../shared-modules/packages/PKG-034_ReferenceLibrary.md#reference-library-resolution)、[057A工艺生成](<../process-guides/guidance/06-domains/DEV-DOM-057A_AOI CAD PnP与Target自动生成开发指导.md#aoi-target-synthesis>)、DEV-AI-062和UI012/020。没有引入Java/KiCad或复制GPL代码，没有AsunImage/DevExpress依赖核验。

### 固定源码、真实测试与采纳限制

OpenPnP固定commit `5bd404cfc70f34103a3ca0fbb6b50c2b465f407c`，与此前研究版本一致。[上游仓库](https://github.com/openpnp/openpnp/tree/5bd404cfc70f34103a3ca0fbb6b50c2b465f407c)。归档10份原字节逐份SHA-256/Git blob核验；具体来源/抓取状态在本轮`.work/library-design-20260928/research-sources.json`。

| 固定原文件 | 实际读取范围与用途 | SHA-256 |
|---|---|---|
| [src/main/java/org/openpnp/model/Package.java](<open-source/openpnp_openpnp/5bd404cfc70f34103a3ca0fbb6b50c2b465f407c/src/main/java/org/openpnp/model/Package.java>) | 全文1–198；Package→Footprint与可变属性 | `98c923db1bf5abc6616b459182acd34121338c023d1621146fe7cfe398fae1b3` |
| [src/main/java/org/openpnp/model/Placement.java](<open-source/openpnp_openpnp/5bd404cfc70f34103a3ca0fbb6b50c2b465f407c/src/main/java/org/openpnp/model/Placement.java>) | 定向38–119；身份、面别、Part及enabled等属性，不是全文 | `1e63fd5364c275ec450f3195a6fa12b409e8154a0b51b1bf2c9c3bc5b61a90c5` |
| [src/main/java/org/openpnp/model/Part.java](<open-source/openpnp_openpnp/5bd404cfc70f34103a3ca0fbb6b50c2b465f407c/src/main/java/org/openpnp/model/Part.java>) | 全文1–215；Part→Package及按Configuration重新解析 | `90f380be24c635f6077b2982faacb9a5e7f3d428b632e9768169ce4a7a16a43c` |
| [src/main/java/org/openpnp/model/Footprint.java](<open-source/openpnp_openpnp/5bd404cfc70f34103a3ca0fbb6b50c2b465f407c/src/main/java/org/openpnp/model/Footprint.java>) | 定向35–75、270–371；局部shape/corners变换顺序，不是全文 | `63863d2202596959c8244f9215c70e480e8ea181afbfa23962024bee4da15e7b` |
| [src/main/java/org/openpnp/machine/reference/vision/AbstractPartSettingsHolder.java](<open-source/openpnp_openpnp/5bd404cfc70f34103a3ca0fbb6b50c2b465f407c/src/main/java/org/openpnp/machine/reference/vision/AbstractPartSettingsHolder.java>) | 全文1–168；generalize清本地与删除未用配置，未追父层解析实现 | `db6d105bd5250cde6c0470e0ed2ddb2f937218025af2bf9f7586dfb1b3bd3d58` |
| [src/main/java/org/openpnp/gui/importer/KicadPosImporter.java](<open-source/openpnp_openpnp/5bd404cfc70f34103a3ca0fbb6b50c2b465f407c/src/main/java/org/openpnp/gui/importer/KicadPosImporter.java>) | 全文1–163；身份构造、单位与bottom转换 | `5a2824e1ef2269a393aaaf1d99f8b6f75c252de6a38e68fae3936a39d5c8adea` |
| [src/test/java/Utils2DTest.java](<open-source/openpnp_openpnp/5bd404cfc70f34103a3ca0fbb6b50c2b465f407c/src/test/java/Utils2DTest.java>) | 全文1–167；注释随机测试与活跃断言分别核读 | `944e5b81d5780ffa651c7fc357137618004a40434d83cec9b33879ff51462b82` |
| [src/main/java/org/openpnp/util/Utils2D.java](<open-source/openpnp_openpnp/5bd404cfc70f34103a3ca0fbb6b50c2b465f407c/src/main/java/org/openpnp/util/Utils2D.java>) | 定向225–324；显式单位与逆变换异常处理，不是全工具库 | `cc24c958c9d2217e2376b0db2e17d6524a2de8869a773a0b1cb452af88be1ac5` |
| [LICENSE.txt](<open-source/openpnp_openpnp/5bd404cfc70f34103a3ca0fbb6b50c2b465f407c/LICENSE.txt>) | 1–17、150–171、192–234许可条款定向；非完整法律/传递许可审查 | `8ceb4b9ee5adedde47b31e975c1d90c73ad27b6b165a1dcd80c7c545eb65b903` |
| [pom.xml](<open-source/openpnp_openpnp/5bd404cfc70f34103a3ca0fbb6b50c2b465f407c/pom.xml>) | 1–191依赖/版本字段定向定位；非完整依赖/漏洞/部署审查 | `fa26494b5fc5ff65da091e665c4c37572fa6810f44d6a5584c8e0299c0239456` |

可借鉴Part→Package→Footprint分层、局部几何/放置分离、单位显式转换与实际算例。限制如下：

- Part/Package依赖全局`Configuration.get()`和可变对象，按ID重新取当前对象不能满足本平台精确不可变闭包；不迁入静态库或Java对象。
- `AbstractPartSettingsHolder.generalize`可清局部设置、删除无使用设置。平台“恢复继承”只移除当前覆盖，不删历史引用；本轮没有沿父类/全配置追完真正继承算法，不能宣称上游完整继承机制已审。
- KiCad导入器以value或package-value构造partId，缺项可自动创建Part/Package，默认毫米并对bottom反X/`180-angle`。这些是该导入器约定，不能当所有制造资料身份和底面语义；官方导出选项明确可变。
- Footprint定向方法分别涉及先局部旋转再平移、已含位置的corner再绕原点旋转，两种旋转基点不能混为一套平台坐标公式；独立算例用于防止误借鉴，未运行上游代码，不据此声称已确认其产品缺陷。
- Utils2D逆变换捕获求逆异常后继续使用原tx，平台必须拒绝奇异/非有限变换，不能把正变换冒充逆；统一单位后计算再转回值得借鉴。
- Utils2DTest的10万随机段被注释；活跃测试包含固定坐标/角度断言及角度循环。helper的上下界比较不能拒绝NaN（两个比较均false），不能将这些测试当非有限输入保障。已读真实断言，未构建或运行JUnit。

根LICENSE为GPLv3、源码头为GPLv3-or-later；本轮仅设计研究，不批准直接复制/链接/分发。pom定向列有Swing、OpenCV、JNA、simple-xml、JUnit等Java生态依赖；完整传递许可/供应链/部署未评估，不能因代码短就称可直接用于工业产品。后续如实际选用须另按复用范围完成审查。

初次从旧研究文本复用LICENSE/pom时Git blob不匹配，已补取上游原字节并保留失败记录；旧文本与新文件按UTF-8文本读回相同，不能把旧换行规范化文本当Git原字节。旧资料保留，本次只保存不同字节版本，不重复拷贝已存在PDF。

### KiCad官方来源约束

[KiCad 9.0 PCB Editor官方](<https://docs.kicad.org/9.0/en/pcbnew/pcbnew.html>)；[本地正文](<official/kicad/20260928/pcbnew-9.0.txt>)，SHA-256 `01f49ba6707f7a93a1de9799ca766c066d07c3c58fb235ed164e616fe0fbf749`。读取1605–1676、5548–5598、6424–6472行；其余章节仅归档，不声称全书审阅。


- 板内嵌封装副本，库更新不自动更新板；用户显式选择更新哪些封装/属性，可控制缺失和空值处理。平台借鉴显式更新/逐项差异，程序引用保持精确版本及人工覆盖。
- 位置导出可选单位、drill/place或页面原点、底面X负号、仅SMD、排除带通孔、排除DNP及分别输出板面。PnP不是必然完整AOI对象集，缺行不得当不装。
- Exclude from BOM、Exclude from position files、DNP及Not in schematic含义不同，平台在来源对账分别保留；官方事实不授权推断客户装配变体政策。

### PARMI原件直接阅读

[Programming Manual Component Library，Rev1.0，2017-03-15](<competitors/02_PCBA-AOI研究快照/research/operation_manuals/PARMI/English/ProgrammingManual_2017/Chapter18_ENG_Programming Manual_Component Library_20170315.pdf>)，21页，SHA-256 `c6e068c20b1fa093b32f8fac52bd12d20da77171a4897056ec3dedd55ad05d49`。文本读第3、4、5、6、16、17、18、19、20、21页；第5、16、20页已渲染并看图，图片在本轮`.work`中供审查，不另造PDF。


第3–6页描述component code共享、缺code的package-name第二库、Model/DB Library及Pad/Base ROI来源选择、单/多版本和检测中同步；第16–17页描述生产/测试版及最多20生产版的清理规则；第18–19页提供良/不良样本试验；第20–21页提供选择应用、差异与图像对照。可借鉴逐项来源、版本比较和样本试检任务；不照搬latest、检测中静默更新、按N版删除历史引用或按封装名称推料号唯一。UI截图只证明任务/布局表达，不证明其内部算法、节拍或当前最新版能力。

### 平台新增推演与验证边界

本平台补充同值不同覆盖意图、硬约束三值/检索完整性、独立必检全集、单程序原子与跨程序逐回执、语义耦合组/派生ROI、取消不回滚等闭环；这些是设计推演，不冒称来源已实现。AOI来源实际阅读和未迁入内容见[REF-008](REF-008_PCBA-AOI指导副本与平台采纳映射.md#library-adoption)。源码/hash/链接和独立反例核对只证明研究/文档一致，不代替本平台、OpenPnP、HALCON、WPF或工业样本性能测试。

<a id="coverage-planning-research"></a>
## 覆盖代数、FOV与资源路径规划研究 — 2026-09-28

设计落在[覆盖/采样实施](../shared-modules/guidance/04-metrology/DEV-MET-034_Coverage与Sampling开发指导.md#coverage-sampling-implementation)、[019规划细节](../shared-modules/packages/PKG-019_ScanPlanning.md#scan-candidates-constraints)、FS019、UI006/012和采集交接。公共18/19包独立，工艺提供义务，未启动产品实现或厂商SDK。

### HALCON官方语义

| 官方算子 | 本地正文 | SHA-256 |
|---|---|---|
| [difference](https://www.mvtec.com/doc/halcon/2511/en/difference.html) | [正文](<official/halcon/20260928/difference.txt>) | `12489ebf0ffe96df9afe03497c38ae9e97ac4044fb06b549b63a58ba199c8d6b` |
| [intersection](https://www.mvtec.com/doc/halcon/2511/en/intersection.html) | [正文](<official/halcon/20260928/intersection.txt>) | `3726232cfea049a0ef758a972eb7fc3fc8ee27e65836f47f1c0f6b80e73c7ef6` |
| [union1](https://www.mvtec.com/doc/halcon/2511/en/union1.html) | [正文](<official/halcon/20260928/union1.txt>) | `cdda115628dbeccd03953303abaa0ef0823bd67167e9887d375adfb0a1593042` |
| [erosion1](https://www.mvtec.com/doc/halcon/2511/en/erosion1.html) | [正文](<official/halcon/20260928/erosion1.txt>) | `e1227351cda2f70559f8fdf475941013133cfa2a8bd5d5301336039a9ef8fc10` |

实际读取intersection/difference Description、Attention和结果/空域条款，union1的Description、结果及示例定位，erosion1第22–58及空结果条款；其余列表/算子仅定位，未宣称完整数学公式（HTML提取公式有缺字）或全部相关算子已核读。记录来源页版本仅用于证据复核，不把底层版本写成平台依赖基线；平台继续AsunImage公开接口。

- intersection先合并Region2，再逐个与Region1相交；difference先合并Sub。不能把两个数组当zip配对，更不能混模态/面/义务后批量相交。
- union1只返回并集，目标/来源贡献需平台保留。空Region、空对象、未提供不等同，输出空域行为受系统设置影响；适配器不依赖数组下标保持目标身份，也不并发临时修改全局配置。
- erosion1的结构元素相对重心并有镜像定义，可分裂连通域；空结构元素产生最大Region。平台禁用空margin元素，明确锚点/物理误差，不能直接等同任意机械配置空间。

没有运行HALCON算子或检查AsunImage内部；连续几何/保守栅格/点线测度仍需对应实现与实际边界验证，Region结果不证明计量或工艺质量。

### OR-Tools固定源码与真实测试

固定tag `v9.14`、commit `0d60e8afe450ec817f510aae965ab8898310cb41`，[上游](https://github.com/google/or-tools/tree/0d60e8afe450ec817f510aae965ab8898310cb41)。9条原字节来源含2份官方仓库文档，LICENSE与已有OpenCV归档完全同字节已复用，没有再存一份。

| 固定来源 | 阅读范围 | SHA-256 |
|---|---|---|
| [CMakeLists.txt](<open-source/google_or-tools/0d60e8afe450ec817f510aae965ab8898310cb41/CMakeLists.txt>) | 159–192依赖段；另定向查BUILD_DOTNET/可选后端与目标框架选项；非全依赖审查 | `0ff6e11c170197f4c539b69062b523efade8b5b4f374dd836ecaca8e3336cd31` |
| [ortools/sat/cp_model_checker.cc](<open-source/google_or-tools/0d60e8afe450ec817f510aae965ab8898310cb41/ortools/sat/cp_model_checker.cc>) | 1483–1585、1928–1956实际NoOverlap/Cumulative/解校验；非全部约束实现 | `910c43768cfcec6c24d0ca5c2d0ff334444db372d0add9baf23bffa92d3426e0` |
| [LICENSE](<open-source/opencv_opencv/a0cda081f8d769f40ab2f4904738b4787b44d07c/LICENSE>) | 1–15、67–90定向；Apache-2.0，复用已有相同原字节 | `cfc7749b96f63bd31c3c42b5c471bf756814053e847c10f3eb003417bc523d30` |
| [ortools/sat/cp_model_checker_test.cc](<open-source/google_or-tools/0d60e8afe450ec817f510aae965ab8898310cb41/ortools/sat/cp_model_checker_test.cc>) | 254–280、291–338变量范围/目标溢出真实断言；其余测试仅定位 | `4205ecaf403a59b6738492d01c2e90512bf68f0c906a9706be91497b60833c84` |
| [ortools/sat/csharp/CpSolver.cs](<open-source/google_or-tools/0d60e8afe450ec817f510aae965ab8898310cb41/ortools/sat/csharp/CpSolver.cs>) | 全文1–254；Solve/StopSearch/回调/Dispose/可变实例 | `2d0623f25272503793dce6a060e0b20a993d1c9ee9d3decddfbaae14ff5ad8ba` |
| [ortools/sat/csharp/SatSolverTests.cs](<open-source/google_or-tools/0d60e8afe450ec817f510aae965ab8898310cb41/ortools/sat/csharp/SatSolverTests.cs>) | 222–286、766–797实际数值求解/Interval表达式/Hint断言；非整个测试集 | `244e3363610d754f278b0bfd714674494b066c5cc6b6bff74155307ebdece0f8` |
| [ortools/sat/cp_model.proto](<open-source/google_or-tools/0d60e8afe450ec817f510aae965ab8898310cb41/ortools/sat/cp_model.proto>) | 710–772、794–813状态/目标/界/assumption core注释；其它仅定位 | `6f4081e16c00f2ae48affdbca6448e74115a117d8fa70d5cbd968fb81b38f756` |
| [ortools/sat/docs/solver.md](<open-source/google_or-tools/0d60e8afe450ec817f510aae965ab8898310cb41/ortools/sat/docs/solver.md>) | 151–190、1147–1210 C#时间限制及回调停止示例；章节标题定向检索 | `07e368d559ec7995420bdffdbc4870cea2c9b57bfa52a34d419d4f7b18536a82` |
| [ortools/sat/docs/integer_arithmetic.md](<open-source/google_or-tools/0d60e8afe450ec817f510aae965ab8898310cb41/ortools/sat/docs/integer_arithmetic.md>) | 1–115整数域/线性表达式限制；非全书，示例API不直接作为平台签名 | `93172d43dfebd5bd7b9fa1e2a6a2d230acfe3ac33c41fac14331625070188f76` |

`cp_model.proto`明确FEASIBLE未必最优、OPTIMAL也可为纯可行任务或达到gap limit；无solution的objective不代表实际方案；min/max的bound方向不同；assumption core不保证最小。平台保存证明范围、终止/Gap政策、实际方案及可验证界，不只读状态字符串。

checker按全部变量域和constraint检查；NoOverlap按排序区间前末端拒绝重叠，Cumulative在同一时刻先处理负变化且忽略零duration/demand。两者对零长度并非同一语义，平台要定义资源实际占用/释放，而非把触发事件等同整段相机使用。模型遗漏了哪个生产义务，checker自身不会替调用者发现，需从原库存反向独立核验。

已读C++真实变量域/目标溢出断言和C#真实最优化、Interval与Hint断言。`TestInterval`只检查表达式字符串，`TestHint`只检查模型Hint内容，不能冒称已覆盖调度碰撞或硬件时序。未构建、运行C++/xUnit/native或性能测试。

CpSolver封装为可变一次求解上下文，StopSearch是异步请求、wrapper为空时不执行；响应和回调/Dispose生命周期需由平台Owner管理。源码中的锁不证明并发Solve/Dispose安全，平台不共享同实例并行求解。固定seed和版本不能单独证明wall-clock/并行搜索返回同一hash；平台保存原解，重开不重新求解。

根Apache-2.0只支持本次研究/候选判断；CMake有Abseil、Protobuf、压缩库、Eigen/re2及可选求解后端，并非纯C#无native部署。各后端/传递依赖/实际包许可、SBOM、平台部署及性能未全量审核；没有新增NuGet或安装求解器。两个developers.google.com页面连接超时，未作为已读证据；后续改读同一固定官方仓库中的solver与integer_arithmetic正文，失败记录保留在本轮来源清单。

### 竞品原件与平台取舍

[ScanSpection AOI Operator Manual原PDF](<competitors/02_PCBA-AOI研究快照/research/operation_manuals/Reference_AOI/ScanSpection_AOI_Operator_Manual.pdf>)共134页，SHA-256 `2b19ea19c2ce1ec93f9515217f1a51ae1b103057337e3d7b9f9efbec9d191187`。直接提取读取PDF第19、74、75、76页，第75页已渲染看图；原件未重拷或转换。页19描述地图/位号与Point-And-Shoot导航，页74描述切图偏移补偿，页75说明单FOV/搜索余量、ROI小于视场75%及错误后的后续未检风险，页76给坐标交换例。


借鉴地图/对象联动、边界不足的明确诊断；不把75%作为平台统一参数，不继承双击图像发机械运动、模板读取失败就删除模板的行为。已知后续未检必须保留原分母与原因，不能因首个错误将后续从任务集消失。PDF年代/产品能力仅限该原件，不用它证明当前国际最高水平或内部算法。

平台推演补有限候选无解范围、保守整数/几何量化、不可拆分/多观察支持、撤销交叠贡献、抽样失败、逐来源水位、资源与真实排空、单程序采用/运行修订。AOI原指导实际读取范围见[REF-008](REF-008_PCBA-AOI指导副本与平台采纳映射.md#coverage-planning-adoption)。独立算例与结构核对仅证明文档定义一致，不代表产品、上游求解器、WPF或工业节拍通过。

<a id="acquisition-quality-research"></a>
## 采集序列与成像质量研究 — 2026-09-28

实施落点：[012序列](../shared-modules/guidance/02-platform/DEV-PLT-015_设备、相机、光源、运动与采集开发指导.md#acquisition-sequence-implementation)、[IM-020质量指标](../independent-modules/image-quality/DEVELOPMENT-GUIDE.md#image-quality-implementation)及[UI014](../shared-modules/guidance/14-page-contracts/UI-PCS-014_Engineering_Diagnostics.md#acquisition-quality-ui)。本轮只研究公开来源和既有只读AOI归档，不实现SDK，不扫描AsunImage内部或验证其/DevExpress依赖。

### 固定Aravis源码和实际阅读

官方release返回0.8.36（2026-04-26），解引用tag固定commit `97ff5e330919d7a44b871df4eda669feeafdf342`，[上游](https://github.com/AravisProject/aravis/tree/97ff5e330919d7a44b871df4eda669feeafdf342)。原始raw下载9次连接失败，随后使用GitHub Git blobs API取同一tree的原字节，逐文件Git blob及SHA-256核验；失败记录保留，不称第一次成功。

| 原文件 | 实际读取范围 | SHA-256 |
|---|---|---|
| [COPYING](<open-source/AravisProject_aravis/97ff5e330919d7a44b871df4eda669feeafdf342/COPYING>) | 1–16及253–314（LGPL2.1与链接/再分发条款），非法律意见 | `dc626520dcd53a22f727af3ee42c770e56c97a64fe3adb063799d8ab032fe551` |
| [meson.build](<open-source/AravisProject_aravis/97ff5e330919d7a44b871df4eda669feeafdf342/meson.build>) | 1–95，依赖/编译平台选项；其余未全审 | `0a12a7c718c3b6f17cd85faf5c95178b4155486cd9378b66f4b9a20bfa6f1a38` |
| [src/arvbuffer.c](<open-source/AravisProject_aravis/97ff5e330919d7a44b871df4eda669feeafdf342/src/arvbuffer.c>) | 59–102、379–495，内存/时钟/frame ID；其它为定位 | `da71ee9385378164b366538fd2afb2c9d090793fc8686e331b861fa2f09de3ac` |
| [src/arvbuffer.h](<open-source/AravisProject_aravis/97ff5e330919d7a44b871df4eda669feeafdf342/src/arvbuffer.h>) | 1–77，许可/状态/payload枚举；其它未全审 | `0cf34dba30d170b4c2008fac77bcdb1c1c34dd1ee481163487634ef4fcb9490f` |
| [src/arvfakecamera.c](<open-source/AravisProject_aravis/97ff5e330919d7a44b871df4eda669feeafdf342/src/arvfakecamera.c>) | 240–268、750–811；计数初值1101仅定位 | `eb63937a0bfadec027516c4585eea70b774dd6bf578a644ba68e8229cc4c31bb` |
| [src/arvfakestream.c](<open-source/AravisProject_aravis/97ff5e330919d7a44b871df4eda669feeafdf342/src/arvfakestream.c>) | 1–190，实际接收循环、underrun和停止join | `d7e0543bbc4fb47ef1aef8669070943a9a68d83c1cd55a2eb4a6c2175dcc004e` |
| [src/arvstream.c](<open-source/AravisProject_aravis/97ff5e330919d7a44b871df4eda669feeafdf342/src/arvstream.c>) | 85–181、285–334、737–781、793–808；其它为定位 | `ab5d1a8326b4ba8b84bcfb8a79520c6b84ded0b40141494b22a7ac041c2b7396` |
| [tests/buffer.c](<open-source/AravisProject_aravis/97ff5e330919d7a44b871df4eda669feeafdf342/tests/buffer.c>) | 1–110，构造/预分配释放回调和时间戳断言；不是完整测试集 | `99ab3f6adc8a470c4df0fbb7978dd760b77a52143bed30de6826726fa4bafdd5` |
| [tests/fake.c](<open-source/AravisProject_aravis/97ff5e330919d7a44b871df4eda669feeafdf342/tests/fake.c>) | 270–438，未知feature错误及单帧模拟/统计真实断言；未运行 | `3ebedb5d335905615346e068808d8bc681d4e0b981d5a6eea2fb5ec7099bb97a` |

可借鉴：push向stream转所有权、pop虽有buffer仍可能无效；输入/输出队列及接收线程signal、stop后join、池耗尽underrun；元数据区分camera timestamp与主机接收时间。测试真实核构造/释放回调/未知feature错误与单次模拟采集计数，不覆盖所有并发/超时/重连。

不能照搬：fake camera直接把墙钟写入device/system两个timestamp，16位frame ID回卷并跳0；这不是实际曝光时钟同步或所有设备计数合同。等待下一帧使用sleep，cancel在循环观察且stop调用join，不证明硬取消时限。队列使用GAsyncQueue不自动提供平台字节预算/背压。公共层还须处理完整曝光关联、计数代、partial settings/unknown动作、外部借出buffer寿命和原子组推进。

库源头文件标LGPL-2.1-or-later，COPYING为LGPL2.1；所读tests/buffer.c标Unlicense，不能将测试许可扩展到库。Meson依赖GLib/GObject/GIO、libxml2、zlib及可选libusb，Windows还涉及系统网络库，不是纯C#组件。当前只借鉴边界/反例，未复制库到产品、未安装/构建或运行上游；若以后选为真实适配依赖，应单独审实际再分发/链接方式及完整传递闭包，不由本次研究自动批准。

### 官方行为核对

| 官方页与本地正文 | SHA-256 |
|---|---|
| [data-chunks](https://docs.baslerweb.com/data-chunks) · [正文](<official/basler/20260928/data-chunks.txt>) | `f66b43d4c3cc8d150e79ad2936980d164d2409894c1e71d4d9de944f4a384769` |
| [timestamp](https://docs.baslerweb.com/timestamp) · [正文](<official/basler/20260928/timestamp.txt>) | `d88e3db86647c48507f3c050f095206ebb56a43ed68cf09a748bbe68cdf934e3` |
| [deviation_image](https://www.mvtec.com/doc/halcon/2511/en/deviation_image.html) · [正文](<official/halcon/20260928/deviation_image.txt>) | `071237ae8c72a9a8c1cc896f42da83e1b7568bed3b9a06b24407fd5ddcdb6922` |
| [estimate_noise](https://www.mvtec.com/doc/halcon/2511/en/estimate_noise.html) · [正文](<official/halcon/20260928/estimate_noise.txt>) | `551f1a11b6d0c0608a29dd9dbb8941f3054b8ff63d60c1ecdd80229ad8f9b840` |
| [gray_histo](https://www.mvtec.com/doc/halcon/2511/en/gray_histo.html) · [正文](<official/halcon/20260928/gray_histo.txt>) | `cafdba359e313e61942ed13fad843060f870585a2748a9997be32b05a3dc3398` |
| [gray_histo_abs](https://www.mvtec.com/doc/halcon/2511/en/gray_histo_abs.html) · [正文](<official/halcon/20260928/gray_histo_abs.txt>) | `ececfcb8d4f8208d7e3e97e9c9673468e915b3187faebf063bf5af79c5ea8498` |
| [gray_histo_range](https://www.mvtec.com/doc/halcon/2511/en/gray_histo_range.html) · [正文](<official/halcon/20260928/gray_histo_range.txt>) | `27d43761d9541813efdfa745dbcf7d48e8e636346ee38e6cf48f2ae5be76af3d` |
| [intensity](https://www.mvtec.com/doc/halcon/2511/en/intensity.html) · [正文](<official/halcon/20260928/intensity.txt>) | `1c0792c3d8148152dd72270e0c0505c02cda3413fba529f77610e41a524e1883` |
| [laplace_of_gauss](https://www.mvtec.com/doc/halcon/2511/en/laplace_of_gauss.html) · [正文](<official/halcon/20260928/laplace_of_gauss.txt>) | `6387ece9ee58a490b7f00afd15f1070f1643653b233319b2af98c653186dabb6` |
| [sobel_amp](https://www.mvtec.com/doc/halcon/2511/en/sobel_amp.html) · [正文](<official/halcon/20260928/sobel_amp.txt>) | `c7598646c6ea4a38c4491f2fd8c156009e9df74c0e0d521962209f098a064de7` |

HALCON实际阅读8页Description/Attention；intensity/gray_histo另读参数/空域/类型段，gray_histo_abs/range补读参数与类型、边界归属段。HTML抽取的部分数学公式是SVG，未作为完整公式抄录；强制采用的统计定义在013明确，后续算子适配仍须原API/样例核对。URL版本只定位所读官方证据，不恢复平台固定HALCON版本。

- intensity及三种histogram都忽略Image已有domain，必须传显式有效Region。gray_histo把高位深/real按图范围缩到256级，不能据末bin判断sensor截断；gray_histo_abs仅支持byte/cyclic/direction/int1/int2/uint2，不能对int4/int8/real照搬。gray_histo_range支持后者，但非real范围向下取整、边界归较小bin、离散非整数bin可能产生峰/空洞，直方图形状不自动说明噪声；量化bin中心也不能冒充精确原灰度矩。
- deviation_image响应乘2、偶数窗增为下一奇数、边界镜像且OpenCL数值可异。Sobel尺度平滑/幅值倍率和signed输出必须保留；邻域滤波不能用压平mask替代二维域。
- estimate_noise不同方法假设与Percent适用性、foerstner假0和3175明确；局部灰度标准差不是噪声Sigma，二者差值不是统计不确定度。方向纹理也不是运动模糊证明。这些后两项是平台设计推演，不冒称厂商给出生产分类器。
- Basler Timestamp正文1023–1042：启动/重置、机型tick频率、PTP近似、Latch可变延迟。Data Chunks读1053–1080、1110–1123、1147–1181；image metadata机型例外、CRC/Exposure、Frame/Trigger counter、sequencer和rolling shutter时间语义。长机型支持表及API示例未全审，不宣称所有型号支持；Aravis接口0无效与某Basler Frame ID从0起的区别说明计数约定必须留在适配合同。

### 竞品原件和采纳限制

复用[ScanSpection原PDF](<competitors/02_PCBA-AOI研究快照/research/operation_manuals/Reference_AOI/ScanSpection_AOI_Operator_Manual.pdf>), SHA-256 `2b19ea19c2ce1ec93f9515217f1a51ae1b103057337e3d7b9f9efbec9d191187`；直接读PDF第48/50页，渲染并看第50页。48页提供失败重测选项并称可降低振动误报；50页有Settle Delay和No Feed重复测试。原文证明操作需求，不证明实际算法/同步、最优参数或生产表现。平台补冻结用途/次数/总期限、保留全部失败attempt、结构/质量/停止分开；不迁入默认0延时、No Feed生产授权或忽略下游选项。

AOI来源范围见[REF-008](REF-008_PCBA-AOI指导副本与平台采纳映射.md#acquisition-quality-adoption)。源码/官方/原件与算术核对不等于Aravis/HALCON/WPF/设备或工业效果测试；目前无这些运行证据。

<a id="imaging-optimization-research"></a>
## 曝光、增益与照明优化研究 — 2026-09-28

设计落点为[独立061](../shared-modules/packages/PKG-061_ImagingOptimization.md)、[快编接入](../shared-modules/guidance/07-ai/DEV-AI-062_自动编程与ProgramSynthesis开发指导.md#10-采集质量反馈与自动参数候选的边界)及UI012。数量由60增为61的理由是快编/独立试验台的真实复用与独立试验生命周期，不因资料中存在一个类就另建DLL。

Optuna官方latest release返回v5.0.0（2026-09-07），tag固定commit `01ddd17ab9f36c3d2817aed9afe376e1cb047d35`；OpenPnP沿用固定commit `5bd404cfc70f34103a3ca0fbb6b50c2b465f407c`。12条源码/测试/工程/许可来源通过GitHub blobs API读取并与各固定tree核Git blob，OpenPnP LICENSE/pom复用旧原字节，无重复拷贝。实际读取范围如下，不把定位或截断输出当全文审计。

| 来源 | 实际阅读 | SHA-256 |
|---|---|---|
| [optuna/optuna: LICENSE_THIRD_PARTY](<open-source/optuna_optuna/01ddd17ab9f36c3d2817aed9afe376e1cb047d35/LICENSE_THIRD_PARTY>) | 全文SciPy/ fdlibm通知 | `dbff6df3cb59b7fb11de7e234630e139318ee8cada55e2f14a24d184c48954a8` |
| [optuna/optuna: LICENSE](<open-source/optuna_optuna/01ddd17ab9f36c3d2817aed9afe376e1cb047d35/LICENSE>) | 全文MIT条款 | `c3df8e8523cf46be4b366ee7dd11578454b10ea5ec5159e57df849513aafe059` |
| [optuna/optuna: optuna/samplers/_base.py](<open-source/optuna_optuna/01ddd17ab9f36c3d2817aed9afe376e1cb047d35/optuna/samplers/_base.py>) | 149–232：before/after/reseed生命周期；后续约束实现未全审 | `ae2f952556b530d1ff9644e4f1c6fe93679e1c8bd71c8dea02d75d3571cb4d97` |
| [optuna/optuna: optuna/samplers/_grid.py](<open-source/optuna_optuna/01ddd17ab9f36c3d2817aed9afe376e1cb047d35/optuna/samplers/_grid.py>) | 1–208及190至末：网格展开/量化/重复/终结/穷尽 | `24647d3003918ab431828850b5143c62b3a541f743919ad1ecaed663f01f8a5c` |
| [optuna/optuna: pyproject.toml](<open-source/optuna_optuna/01ddd17ab9f36c3d2817aed9afe376e1cb047d35/pyproject.toml>) | 1–65：运行/构建及部分可选依赖 | `24fabd28399652bbc9798f9a69846dfcdee97a0277d124c11f9b388329604b39` |
| [optuna/optuna: tests/study_tests/test_multi_objective.py](<open-source/optuna_optuna/01ddd17ab9f36c3d2817aed9afe376e1cb047d35/tests/study_tests/test_multi_objective.py>) | 1–39、87至末：方向/相等、未完成/多维/重复/数值反例；中间部分未全读 | `18ee5d69eb609a6eb26440aca173574aa1ed3d57a7ac4597f1c8be0189fc027e` |
| [optuna/optuna: tests/samplers_tests/test_grid.py](<open-source/optuna_optuna/01ddd17ab9f36c3d2817aed9afe376e1cb047d35/tests/samplers_tests/test_grid.py>) | 1–109、224至末：越界警告/失败剪枝/重跑/seed/NaN/穷尽断言 | `a2965939b87c49b9b6d3d6de05020831e458e80b08af86998eac34a85e13b3b2` |
| [optuna/optuna: optuna/study/_multi_objective.py](<open-source/optuna_optuna/01ddd17ab9f36c3d2817aed9afe376e1cb047d35/optuna/study/_multi_objective.py>) | 1–124、206–248（末行）：完整/可行筛选、rank与dominates；中间加速实现未全审 | `bb23e88a3fd8bef2063cb18fdd0382c1026f09d567b5d0f4019ceaa59402b191` |
| [openpnp/openpnp: pom.xml](<open-source/openpnp_openpnp/5bd404cfc70f34103a3ca0fbb6b50c2b465f407c/pom.xml>) | 复用原件，重读54–87、177–189：Java依赖节选 | `fa26494b5fc5ff65da091e665c4c37572fa6810f44d6a5584c8e0299c0239456` |
| [openpnp/openpnp: LICENSE.txt](<open-source/openpnp_openpnp/5bd404cfc70f34103a3ca0fbb6b50c2b465f407c/LICENSE.txt>) | 复用原GPL3文件，重读1–18；不重新声称全许可审查 | `8ceb4b9ee5adedde47b31e975c1d90c73ad27b6b165a1dcd80c7c545eb65b903` |
| [openpnp/openpnp: src/main/java/org/openpnp/machine/reference/camera/OpenPnpCaptureCamera.java](<open-source/openpnp_openpnp/5bd404cfc70f34103a3ca0fbb6b50c2b465f407c/src/main/java/org/openpnp/machine/reference/camera/OpenPnpCaptureCamera.java>) | 510–535：auto读写/异常；其余仅定位 | `0de04561324a5d7baf0badff9421dac55549b7d503dd08ce6e5fbdf15d6e39c1` |
| [openpnp/openpnp: src/main/java/org/openpnp/machine/reference/camera/AbstractSettlingCamera.java](<open-source/openpnp_openpnp/5bd404cfc70f34103a3ca0fbb6b50c2b465f407c/src/main/java/org/openpnp/machine/reference/camera/AbstractSettlingCamera.java>) | 266–289、383–459、646–680；其余仅定位，未核全部差分方法 | `a5e137c4cce79494d76362fbc2ade2189f032b4c9913165ba759e5be2cb46ae9` |

Optuna可借鉴明确搜索空间、试验生命周期、可行集/非支配、失败与重复测试。不能直接采纳其设备行为：GridSampler完整展开积空间；suggest步进不约束grid值；越界警告后仍返回；并发/穷尽重跑可重复配置；failed/pruned计入已访问。BaseSampler并行reseed也不能给固定seed物理复现保证。多目标内部实现允许inf及把None归inf，本平台缺测需先独立分类，不能用它们替代有效指标或硬门。所读pytest有真实断言，但未执行，不扩称TPE/NSGA源码已审或工业效果更好。

Optuna主MIT，另有SciPy及fdlibm通知；Python运行依赖包含NumPy、SQLAlchemy、Alembic、PyYAML、packaging、colorlog、tqdm，未全审传递依赖。当前不引入Python运行时/数据库，先实现可核对的有限集合基线；如采用优化后端需按具体范围做部署/依赖与效果比较，不能因许可证宽松就把存储/动作权威交给库。

OpenPnP的稳定采样有单调时基、相邻帧差分/去抖、finally释放可借鉴；其超时或阈值达成均return image，使用非零图差推断非重复，fixed sleep异常被忽略，auto属性异常返回false或无声吞掉，不能迁为平台已稳定/已关闭/已设置事实。平台需原曝光身份、明确终止原因与Actual恢复。源码为GPL体系，项目含Java/OpenCV/openpnp-capture等依赖；不直接复制产品代码，所选稳定/auto路径没有本轮已核对应上游测试，不能将Optuna测试覆盖搬给它。

### 官方行为与原PDF

| 官方页 | SHA-256 |
|---|---|
| [set_framegrabber_param](https://www.mvtec.com/doc/halcon/2511/en/set_framegrabber_param.html) · [正文](<official/halcon/20260928/set_framegrabber_param.txt>) | `7a0e9d00953678050d9fa041d90addc981b2a2b5cdb4b24ed84c84774b7c70c3` |
| [exposure-auto](https://docs.baslerweb.com/exposure-auto) · [正文](<official/basler/20260928/exposure-auto.txt>) | `aba72763eef09f0536491390f0963ec88c6f72fbd9ba8d566855d022cf4b3702` |
| [auto-function-profile](https://docs.baslerweb.com/auto-function-profile) · [正文](<official/basler/20260928/auto-function-profile.txt>) | `41723ca06c185e223362f2b4b6fb309fcaf53b9f736884147fed9bd96ef1941b` |
| [gain-auto](https://docs.baslerweb.com/gain-auto) · [正文](<official/basler/20260928/gain-auto.txt>) | `d7e9748006c51c416cc71994732a48279d036262d1df48641dc69ec8621fba63` |

Basler读取三页Feature正文：Exposure/Gain Auto的Once/Continuous/Off、目标ROI/灰度、范围/初始帧延迟/Gamma及line-scan例外；Auto Function Profile的Minimize Gain/Exposure/Smart/抗闪烁说明。未全读长机型表或SDK示例。Once可能30次上限后结束；Off保留最后值，亮度达标不等于本平台逐任务质量达标；不同profile会在噪声/帧率间折衷，不能作为跨机型默认参数。官方示例中扩大限值不是平台授权。

HALCON只核`set_framegrabber_param` Description/Attention/Execution：具体参数依采集接口，修改同handle须同步；它不能证明一个通用“自动曝光优化器”已由该算子提供。013的质量算子研究沿上一节复用，经AsunImage公共接口，未扫描其内部或做依赖核验。

- [Viscom_vAI_ProVision_EN_2025.pdf](<competitors/02_PCBA-AOI研究快照/research/competitor_docs/Viscom/Viscom_vAI_ProVision_EN_2025.pdf>), SHA-256 `193b9d0b923d5928f1e7950d2e7c4f26df87489a939ce9ba5cec9539f10c4184`；读PDF页[1, 2]，渲染查看页[2]。
- [Viscom_vVision_Operation_Workflow_EN.pdf](<competitors/02_PCBA-AOI研究快照/research/operation_manuals/Viscom/Viscom_vVision_Operation_Workflow_EN.pdf>), SHA-256 `2e29fa19440fd6727d7756bf21667e5b888b73313400a7fed85782a6040cef73`；读PDF页[2, 3]，渲染查看页无（文字核读）。

vAI ProVision原页支持E-CAD/template结合AI建程及“minutes”等厂商主张，vVision第2页明确基于自动采集verification images优化和归档，第3页有新手/专家与核验站操作需求；它们不公开曝光搜索算法，也不证明本平台可达到宣传性能。复用原PDF，不转换或重拷；初次vVision第3页输出遇GBK错误，改UTF-8重读成功。源AOI差异见[REF-008](REF-008_PCBA-AOI指导副本与平台采纳映射.md#imaging-optimization-adoption)。本轮没有上游/平台/native/WPF/实机测试，研究与独立算术仅支持文档设计。

<a id="mosaic-research"></a>
## 多FOV全局几何、显示拼接与瓦片的实读依据 — 2026-09-28

落点为[017/029 §8–15](../shared-modules/guidance/03-vision/DEV-VIS-029_多FOV拼接与全局坐标开发指导.md#mosaic-implementation)、UI002和钢网/AOI工艺增量。沿用OpenCV固定commit `a0cda081f8d769f40ab2f4904738b4787b44d07c`，不是查询latest；下载按该tree blob核原字节。已有LICENSE/Stitcher/测试复用，无新生产依赖。以下精确范围是实际阅读，不把下载文件或文本截断处称全文审查。

| 固定来源 | 实际读取范围 | SHA-256 |
|---|---|---|
| [LICENSE](<open-source/opencv_opencv/a0cda081f8d769f40ab2f4904738b4787b44d07c/LICENSE>) | 标题/第4节再分发条件/附录，非本轮逐条法律审查 | `cfc7749b96f63bd31c3c42b5c471bf756814053e847c10f3eb003417bc523d30` |
| [modules/stitching/CMakeLists.txt](<open-source/opencv_opencv/a0cda081f8d769f40ab2f4904738b4787b44d07c/modules/stitching/CMakeLists.txt>) | 全文17行，模块与可选CUDA/contrib依赖 | `ea6b15516e3cded65e8fdf2c6e9ed0886d0723f94d6526925e4e766468d7ed7f` |
| [modules/stitching/src/blenders.cpp](<open-source/opencv_opencv/a0cda081f8d769f40ab2f4904738b4787b44d07c/modules/stitching/src/blenders.cpp>) | 80–94、136–184、233–299、328–357、366–398、720–750、778–785；其余/GPU内核未全审 | `d48e1f8b0752208c0b318d99735d6660ed2448751da8107dc34355eebd4b5e52` |
| [modules/stitching/src/matchers.cpp](<open-source/opencv_opencv/a0cda081f8d769f40ab2f4904738b4787b44d07c/modules/stitching/src/matchers.cpp>) | 397–448、483–564；其它匹配实现未全读 | `96d1d2ba869ff30cae9e9301f02a4e271643b4291cfa6177afb1a4ea2f572d6f` |
| [modules/stitching/src/motion_estimators.cpp](<open-source/opencv_opencv/a0cda081f8d769f40ab2f4904738b4787b44d07c/modules/stitching/src/motion_estimators.cpp>) | 222–315；各具体误差/Jacobian类未全审 | `a8cdb4d59050de0fc4f9f6a67b13b07b2f2907f271d8d4c8f0fd27cf686ee903` |
| [modules/stitching/src/stitcher.cpp](<open-source/opencv_opencv/a0cda081f8d769f40ab2f4904738b4787b44d07c/modules/stitching/src/stitcher.cpp>) | 50–92、459–512；其余沿既有研究或仅定位 | `84962ab2aa0efb5795a9821d995519dc9787029d127a99525703aed54b62c64a` |
| [modules/stitching/test/test_blenders.cpp](<open-source/opencv_opencv/a0cda081f8d769f40ab2f4904738b4787b44d07c/modules/stitching/test/test_blenders.cpp>) | 全文79行；两图mask融合与参考图PSNR | `39fc74ef608ece7e623ff62c52efb38f53938394b8051b71a9d0c1fd848c2452` |
| [modules/stitching/test/test_matchers.cpp](<open-source/opencv_opencv/a0cda081f8d769f40ab2f4904738b4787b44d07c/modules/stitching/test/test_matchers.cpp>) | 测试主体45–143；ROI/ORB描述子及范围匹配，头部许可；无全链PCB计量测试 | `6efb27309604316e630ba398dcb1c22a0fe2682041638cb9de4d36fc7f553f31` |
| [modules/stitching/test/test_stitcher.cpp](<open-source/opencv_opencv/a0cda081f8d769f40ab2f4904738b4787b44d07c/modules/stitching/test/test_stitcher.cpp>) | 全文28行；setTransform再合成一致性 | `b6b15cebea5627803953a53fdaf95386bdd8ec3e69447b9d53c72a9dc8fa5938` |

可借鉴：Stitcher分开配准/合成和工作分辨率；SCANS选择affine估计/partial bundle/平面warp且关闭wave correction及曝光补偿，PANORAMA默认球面warp/波形校正/块增益不适用PCB平面计量。受限候选图、明确源mask、融合halo/金字塔相位有工程价值。

不能直接采纳：`leaveBiggestComponent`丢弃其它分量后继续，本平台须保留缺项；RangeMatcher只计算索引邻近对却仍分配N×N结果容器，不能作稀疏资源保证；homography分支先减半宽高，而affine分支直接用像素坐标，不能互换矩阵；匹配confidence是内点经验公式，某分支过高还置零，不是概率/计量置信；BundleAdjusterBase调用优化后显式检查NaN并返回true不等于本平台物理残差/独立验证通过。未全审其求解器内核，不据此断言所有数值保障缺失。

Blender::prepare为完整输出ROI分配；MultiBand还分配整个输出金字塔，feed中的局部halo不使它自动成为超大图流式渲染。CPU/GPU和signed短整型累积/WEIGHT_EPS等不能直接迁入高位深计量语义。feather用距离权重可作显示候选；主来源不足以证明融合完整lineage，多带重构也不是简单同点非负混合。

测试实际断言包括ROI内提点、ORB描述子批量/单张一致、索引范围外confidence为零、双图融合PSNR和重新setTransform后的像素一致。它们未证明最小PCB缺陷保持、全板完整性、多FOV计量、超大tile、取消或资源上限；本轮未构建/运行上游测试。文件名ParallelFeaturesFinder内部注释明确该调用不使用parallel_for_，不能靠测试名宣称已验并行。

许可/依赖：根LICENSE是Apache-2.0，所读部分旧源码/测试还保留Intel/OpenCV许可与通知；潜在再分发需保留适用通知及修改标识。模块CMake直接列imgproc/features/geometry/flann及可选CUDA/xfeatures2d，未全审传递依赖/当前.NET绑定；本轮仅借鉴架构和反例，不引入OpenCV二进制或拷代码进产品。高阶后端须先证明HALCON适用能力缺口及同集收益。

### 官方HALCON能力

| 官方页与本地正文 | SHA-256 |
|---|---|
| [adjust_mosaic_images](https://www.mvtec.com/doc/halcon/2511/en/adjust_mosaic_images.html) · [正文](<official/halcon/20260928/adjust_mosaic_images.txt>) | `df8219ba7972208188ef3ccc0d8aba03efff0143544d5a38f4e40db88794ceef` |
| [affine_trans_image_size](https://www.mvtec.com/doc/halcon/2511/en/affine_trans_image_size.html) · [正文](<official/halcon/20260928/affine_trans_image_size.txt>) | `fb12529db861c9fa41e44a3d12379a66e836447f617248eba016c3c1ec78b1c8` |
| [bundle_adjust_mosaic](https://www.mvtec.com/doc/halcon/2511/en/bundle_adjust_mosaic.html) · [正文](<official/halcon/20260928/bundle_adjust_mosaic.txt>) | `111640da8e4e79d9660421b1b65aa7ac5aebabc10a9ac5f7a103716bb0f6adea` |
| [gen_bundle_adjusted_mosaic](https://www.mvtec.com/doc/halcon/2511/en/gen_bundle_adjusted_mosaic.html) · [正文](<official/halcon/20260928/gen_bundle_adjusted_mosaic.txt>) | `665b12fd1e695d1e2d06d839ea59badc28d35d7e186fa18e7a0756726b7298f9` |
| [gen_projective_mosaic](https://www.mvtec.com/doc/halcon/2511/en/gen_projective_mosaic.html) · [复用正文](official/halcon/20260927/gen_projective_mosaic.txt) | `551ebff6bafb0a2b90507d11768145e19a8bfd88bd4092a51fc32e961ee6dc4e` |

实际核四页Description/Attention（若有）/Execution及类型/参数，补读gen_bundle与adjust的完整Description；复用旧gen_projective_mosaic说明。bundle支持四种受限模型，参考图identity，输出平均Error；没有任意权重/soft anchor/covariance公开参数。本平台先外层有界筛选/重算，再独立验证，不冒称内置稳健损失。gen_bundle只合成已给每图矩阵，自动画布返回平移；stacking不是seam/feather。TransformDomain=false以及affine_trans_image_size忽略domain必须单独处理；后者row-column/角点约定、缩小bilinear不抗混叠与int_zooming精度/域差异已纳入适配反例。

adjust仅byte，输出校正图而无估计系数；add/mult/response/vignetting有组合约束，不能修复饱和或一般非均匀照明，响应/渐晕估计要可观测。部分网页公式为图像，文本未完整还原，本轮不抄缺失公式。官方版本只用于来源定位，不冻结平台底层HALCON版本；未扫描AsunImage内部、未核依赖/授权，也未运行算子。

### 竞品原PDF与工程采纳

- [WEB-0019__ScanINSPECT_Rev19082720.pdf](<competitors/06_WEB公开资料/ScanCAD/原始资料/WEB-0019__ScanINSPECT_Rev19082720.pdf>)，SHA-256 `96ece8fb4162caaca9652b28a09b935025524a8414c2e6041b6b3a2052f908ab`；直接读第1/2页，ScanSTENCIL另渲染查看第1页。
- [WEB-0020__ScanSTENCIL_Rev19082720.pdf](<competitors/06_WEB公开资料/ScanCAD/原始资料/WEB-0020__ScanSTENCIL_Rev19082720.pdf>)，SHA-256 `1ea0ba354658f360291794b5f9bc65bc93269e7c362c3cd1166806792180dc16`；直接读第1/2页，ScanSTENCIL另渲染查看第1页。

两PDF第2页明确Large Part Capability with Multiple Scans、多层/多级缩放和源数据/图像输出；ScanSTENCIL第1页Verification有LMA，图中也是局部对位选项。平台采纳全网/原图联动和局部搜索与全局位置分开；宣传的0.001英寸、43%改善、Unlimited Work Area不成为平台能力或预算证据。没有公开其拼接/计量算法，不能据图推断内部实现。原PDF未重拷/转换；AOI原指导定向采纳见[REF-008](REF-008_PCBA-AOI指导副本与平台采纳映射.md#mosaic-adoption)。

来源清单/Git blob/原件hash/备份和文档检查保留`.work/mosaic-design-20260928/`。独立矩阵/集合/资源算例只核指导期望；未运行产品、OpenCV、HALCON、WPF、设备或工业对标。

<a id="matching-research"></a>
## 二维定位、模板候选与多Mark对应的实读依据 — 2026-09-28

落点是[022/023 §7–14](../shared-modules/guidance/03-vision/DEV-VIS-023_定位、注册与Alignment开发指导.md#matching-implementation)、UI002/012、钢网及AOI接入。固定OpenPnP commit `5bd404cfc70f34103a3ca0fbb6b50c2b465f407c`和OpenCV commit `a0cda081f8d769f40ab2f4904738b4787b44d07c`。共9条Git来源，7条复用已有原字节、2条新增；只读取实际源码/测试，不据README或星数判断质量。完整来源tree/blob/hash及抓取记录保留`.work/matching-design-20260928/research-sources.json`。

| 固定本地来源 | 本轮实际阅读范围 | SHA-256 |
|---|---|---|
| [opencv/opencv / LICENSE](<open-source/opencv_opencv/a0cda081f8d769f40ab2f4904738b4787b44d07c/LICENSE>) | 标题及已有研究的通知要求；本轮非逐条审查 | `cfc7749b96f63bd31c3c42b5c471bf756814053e847c10f3eb003417bc523d30` |
| [opencv/opencv / modules/imgproc/src/templmatch.cpp](<open-source/opencv_opencv/a0cda081f8d769f40ab2f4904738b4787b44d07c/modules/imgproc/src/templmatch.cpp>) | 870–910、957–987，CPU归一化退化/数值分支；非所有后端 | `b40906775633dfa25bb4c363d389f42ceb31add2fab369bfc5cff9e72737677b` |
| [opencv/opencv / modules/imgproc/test/test_templmatch.cpp](<open-source/opencv_opencv/a0cda081f8d769f40ab2f4904738b4787b44d07c/modules/imgproc/test/test_templmatch.cpp>) | 1–40、127–257、258–360；大数组80–126输出截断不计全文审查 | `d730ee2122a65616f74c5865522616dc000b91aca532bb464dc8b9fbc919d171` |
| [openpnp/openpnp / LICENSE.txt](<open-source/openpnp_openpnp/5bd404cfc70f34103a3ca0fbb6b50c2b465f407c/LICENSE.txt>) | 标题/许可版本GPLv3；本轮非逐条法律审查 | `8ceb4b9ee5adedde47b31e975c1d90c73ad27b6b165a1dcd80c7c545eb65b903` |
| [openpnp/openpnp / pom.xml](<open-source/openpnp_openpnp/5bd404cfc70f34103a3ca0fbb6b50c2b465f407c/pom.xml>) | 1–60及依赖节点定向定位；不是全传递依赖审核 | `fa26494b5fc5ff65da091e665c4c37572fa6810f44d6a5584c8e0299c0239456` |
| [openpnp/openpnp / src/main/java/org/openpnp/machine/reference/vision/ReferenceFiducialLocator.java](<open-source/openpnp_openpnp/5bd404cfc70f34103a3ca0fbb6b50c2b465f407c/src/main/java/org/openpnp/machine/reference/vision/ReferenceFiducialLocator.java>) | 1–64、220–254、284–321、368–436、551–658；其它设备/UI/参数未全审 | `613d88e194dc1dc45963ccb64d574151c4aab240871f450f5d56e7a8488124d6` |
| [openpnp/openpnp / src/main/java/org/openpnp/util/Utils2D.java](<open-source/openpnp_openpnp/5bd404cfc70f34103a3ca0fbb6b50c2b465f407c/src/main/java/org/openpnp/util/Utils2D.java>) | 572–739，双点与多点变换分支；其余复用前轮，不称全文本轮重审 | `cc24c958c9d2217e2376b0db2e17d6524a2de8869a773a0b1cb452af88be1ac5` |
| [openpnp/openpnp / src/test/java/ReferenceFiducialLocatorTest.java](<open-source/openpnp_openpnp/5bd404cfc70f34103a3ca0fbb6b50c2b465f407c/src/test/java/ReferenceFiducialLocatorTest.java>) | 全文，主要断言输出数量/共线退两点；Math.random点 | `bfb48aeffacbf1c9436f79f2f5a13c633c52216c1a4227d90b0b7af0c36bde20` |
| [openpnp/openpnp / src/test/java/Utils2DTest.java](<open-source/openpnp_openpnp/5bd404cfc70f34103a3ca0fbb6b50c2b465f407c/src/test/java/Utils2DTest.java>) | 1–20、80–167完整读取；被注释随机测试不计有效覆盖，20–79本轮不称完整审查 | `944e5b81d5780ffa651c7fc357137618004a40434d83cec9b33879ff51462b82` |

OpenPnP可借鉴：把板定位作为独立步骤；Mark布局看基线/分布、相似/仿射参数及位移限值、保存原变换失败恢复。不能直接搬入平台：getBestFiducials先凸包再`Sets.powerSet`枚举所有子集筛3点，有指数枚举风险；按坐标map去重可能丢独立身份；最多面积不证明质量。findFiducial取距名义最近候选，多次相机移动/收敛均值也不证明绝对正确；平台先纯候选/几何验证，不先修改实体transform再回滚。双点Utils2D会带距离比尺度，多点入口按较短列表截断，均不适合作为固定尺度/稳定对应默认。

其FiducialLocator测试主要断言1/2/3数量及共线退2，不能证明定位精度、正确身份或最佳三角；Utils2DTest有效部分核board placement及角度，旧100k随机测试被注释。平台拟验收增加对称、周期阵列、候选截断、完整关联/最差点、独立目标质量等，未把这些拟测称上游已覆盖。

OpenCV CPU常量模板TM_CCOEFF_NORMED分支返回全1；参考测试函数也同样处理，因此与参考一致不能证明工业目标可观察。归一化有小分母/饱和分支，随机精度测试是8U/32F、1/3通道六种mode与参考相对1e-3比较，bug_21786核常亮大和下SQDIFF零差。可借鉴反例/数值核对，不把相关峰或PASS测试变为计量置信，不推断HALCON有同样退化输出，也未验证OpenCL/GPU等全部后端。

许可/依赖：OpenPnP根GPLv3，Java桌面/全局Configuration、相机动作、Swing、OpenCV、Guava、JNA等依赖可见，不能当独立.NET DLL直接拼入；本轮没有复制其产品代码。OpenCV根Apache-2.0，所读旧测试保留Intel/OpenCV通知，再分发须处理适用通知/修改及具体依赖。此轮只研究，不引入两者产品依赖，不做AsunImage/DevExpress授权核验。

### 官方HALCON资料与已核限制

| 官方页 / 本地正文 | SHA-256 |
|---|---|
| [create_generic_shape_model](https://www.mvtec.com/doc/halcon/2511/en/create_generic_shape_model.html) · [正文](<official/halcon/20260928/create_generic_shape_model.txt>) | `25100348a54c61a3ceac41558ec4ef4eb7217562ae51148c09bcfe02f98207e0` |
| [find_ncc_model](https://www.mvtec.com/doc/halcon/2511/en/find_ncc_model.html) · [正文](<official/halcon/20260928/find_ncc_model.txt>) | `744a0023d904b7c49737bc0bda3bebc86c7a94a34d456fe2eea65384d968bd45` |
| [get_generic_shape_model_result](https://www.mvtec.com/doc/halcon/2511/en/get_generic_shape_model_result.html) · [正文](<official/halcon/20260928/get_generic_shape_model_result.txt>) | `5f8af7866d6a12ba662e9db00074e69cdad9a7260816363a31b0396116925091` |
| [set_generic_shape_model_param](https://www.mvtec.com/doc/halcon/2511/en/set_generic_shape_model_param.html) · [正文](<official/halcon/20260928/set_generic_shape_model_param.txt>) | `67e8adc2cefe7cc4f7ceb0ca6d705a4efb387b5af21a8f5c1d2c3100037a54a7` |
| [train_generic_shape_model](https://www.mvtec.com/doc/halcon/2511/en/train_generic_shape_model.html) · [正文](<official/halcon/20260928/train_generic_shape_model.txt>) | `fce8e320d6e64ab31aac63bf74172e567b74a749dec8a113d3a266963babe9cd` |
| [vector_to_rigid](https://www.mvtec.com/doc/halcon/2511/en/vector_to_rigid.html) · [正文](<official/halcon/20260928/vector_to_rigid.txt>) | `bab284d967453ff48f812df9360d888ab57889f19c1f7a55291bef82c75f025e` |
| [find_generic_shape_model](https://www.mvtec.com/doc/halcon/2511/en/find_generic_shape_model.html) · [复用正文](official/halcon/20260927/find_generic_shape_model.txt) | `af5406b029c966d8aebfd097f821312acc963cb6b51d63d4709d7b9ab45e12b3` |

create/train、vector_to_rigid的Description/Attention/Execution已定向读；get result 27–136；set param 112–140、343–399、493–576、682–715、858–878、930–973、1046–1059；NCC的Description/域/参数/类型/Execution及Example326–337已核，部分公式图片未完整读，不抄作已验证公式；旧find_generic本轮385–485重读并沿前轮已核搜索domain/边界。set完整参数表未逐项审，未读内容不称完备API封装。

已落实：create不等于训练；image域重心和XLD轴对齐bbox中心不同；training samples域处理/替换/成功训练后释放；num_matches中间筛除使top1不必是all中最佳，strict在数量截断后过滤，overlap基于旋转包围矩形。提高greediness/最低金字塔层可能漏检/失准，all不证明数学穷尽。get result为edge-centered位置、0基索引及模型原点到图像矩阵；NCC域仍看原模板域重心，输出位置按官方Example经矩阵和affine_trans_pixel求真实原点，不能通用再加.5。

generic set/train/find均提示ModelID状态修改需跨线程同步，reentrant不授同handle并发。NCC timeout9400无结果、内部线程内存增长、OpenCL仅部分搜索且可能更慢均纳入预算/失败。vector_to_rigid至少两点、无尺度，iconic矩阵row→x/column→y及角点约定需007适配；原网页P/Q方向描述及set的origin_row文字存在易误读处，不能据此猜.NET签名，具体适配必须不对称Golden。官方版本仅锁资料来源，不冻结平台底层版本，未扫描AsunImage内部或运行算子。

### 竞品原件与实际操作要求

复用[PARMI Chapter11 Fiducial/Badmark/Barcode 2017](<competitors/02_PCBA-AOI研究快照/research/operation_manuals/PARMI/English/ProgrammingManual_2017/Chapter11_ENG_Programming Manual_Fiducial Marker_Badmark_Barcode_20170315.pdf>)，SHA-256 `1085d5025b6cf0314ac43cf029dec14fd51180592154b2efd6454d29d44206ab`。直接读第1–8页，渲染查看第3页（全手册39页，非全文审查）。

第3页分示教准备、Main Viewer/2D Live/Fiducial Manager；第4/5页区分Global/Layer/Module/Component但属厂商语义；第6页扫描图复用与停拍图独立照明存在节拍/成像权衡；第7/8页有设计资料带入位置和框选示教，**标记位置不等于注册参考模型**。平台据此补作用域、图像角色/资格、模型步骤和快编联动，不照搬二Mark数量、互斥层级、点击列表自动移动或节拍结论。未公开其内部匹配算法，不声称平台已达到它的检出/精度。

原PDF不重复拷贝/转换，AOI原指导定向采纳见[REF-008](REF-008_PCBA-AOI指导副本与平台采纳映射.md#matching-adoption)。未构建/运行OpenPnP/OpenCV上游测试、HALCON、平台、WPF或设备；本轮检查仅文档、来源完整性与独立算术，不是工业对标。

<a id="model-assets-research"></a>
## 技术模型资产、精确引用与完整依赖的实读依据 — 2026-09-28

落点为[033 §7–14](../shared-modules/packages/PKG-033_ModelAssets.md#model-assets-implementation)，并同步模型生产者、OCR/AI、UI002及开发计划014§27。固定MLflow v3.3.2 commit `9e9abf26f8aa7b546610652fa2556e09f2a83cd2`、ONNX v1.19.0 commit `57b9c6a4f6eebb09ae1b34cfb632078518f72832`，tree不截断且每文件核Git blob原字节。初次按LICENSE查MLflow无此路径，随后按固定tree读取LICENSE.txt，错误及更正保留，不修改原研究记录为零失败。

| 固定来源 | 实读范围/限制 | SHA-256 |
|---|---|---|
| [mlflow/mlflow / LICENSE.txt](<open-source/mlflow_mlflow/9e9abf26f8aa7b546610652fa2556e09f2a83cd2/LICENSE.txt>) | Apache-2.0标题/通知；非本轮逐条法律审查 | `6395355de6f391afff35996a30fb41b189b4991a4cb54993ace35ab69a0bfa28` |
| [mlflow/mlflow / mlflow/store/artifact/models_artifact_repo.py](<open-source/mlflow_mlflow/9e9abf26f8aa7b546610652fa2556e09f2a83cd2/mlflow/store/artifact/models_artifact_repo.py>) | 44–76、113–137、193–243；其它仓库/后端未全审 | `d43b45ffce4f05ad03bd2211805291c471dbcbdc136fcfe10fdeec3145469b68` |
| [mlflow/mlflow / mlflow/store/model_registry/sqlalchemy_store.py](<open-source/mlflow_mlflow/9e9abf26f8aa7b546610652fa2556e09f2a83cd2/mlflow/store/model_registry/sqlalchemy_store.py>) | 755–823、969–1032、1227–1247、1268–1297；其余未全审 | `b65e5e1bed75480dcb6113a4cf996000860843f14d17968cce76490c2f596524` |
| [mlflow/mlflow / pyproject.toml](<open-source/mlflow_mlflow/9e9abf26f8aa7b546610652fa2556e09f2a83cd2/pyproject.toml>) | 1–19及依赖/构建节点定位；开发文件不能冒称发布全依赖 | `c6680d1a2156c34df654554846c143c8463644ef799334a676ead7b92f7471c6` |
| [mlflow/mlflow / tests/store/artifact/test_models_artifact_repo.py](<open-source/mlflow_mlflow/9e9abf26f8aa7b546610652fa2556e09f2a83cd2/tests/store/artifact/test_models_artifact_repo.py>) | 1–75、235–284；mock委托/metadata/URI测试，非完整存储验收 | `ea36eb2febd49f058913dbc02f0c86db3affb789323c3800cfc208b9622d4ca8` |
| [mlflow/mlflow / tests/store/model_registry/test_sqlalchemy_store.py](<open-source/mlflow_mlflow/9e9abf26f8aa7b546610652fa2556e09f2a83cd2/tests/store/model_registry/test_sqlalchemy_store.py>) | 710–754、1666–1709；其它输出/未读测试不计全审 | `8a71a53aa0f69512ecf88740567fde5e37b3f9992034994ef83b997535187d1f` |
| [onnx/onnx / LICENSE](<open-source/opencv_opencv/a0cda081f8d769f40ab2f4904738b4787b44d07c/LICENSE>) | 复用同字节Apache-2.0原文件，未重复拷贝 | `cfc7749b96f63bd31c3c42b5c471bf756814053e847c10f3eb003417bc523d30` |
| [onnx/onnx / onnx/checker.cc](<open-source/onnx_onnx/57b9c6a4f6eebb09ae1b34cfb632078518f72832/onnx/checker.cc>) | 972–1034，external location检查；非完整checker审核 | `17650e255432815f7ea158e2481faf94cef75ad55f343745db0e25cf9da3ee5f` |
| [onnx/onnx / onnx/external_data_helper.py](<open-source/onnx_onnx/57b9c6a4f6eebb09ae1b34cfb632078518f72832/onnx/external_data_helper.py>) | 24–110、186–279；其它转换/保存分支仅定位未全审 | `e47c22bb38f80085325a39d772976bb3c8549a3ba3c09ef0b14e7f10c77682e0` |
| [onnx/onnx / onnx/test/test_external_data.py](<open-source/onnx_onnx/57b9c6a4f6eebb09ae1b34cfb632078518f72832/onnx/test/test_external_data.py>) | 223–253、748–806；路径挑战主体，其余不称全读 | `45cbd3795c5916c3297a8e2e1ef77242e8a69bcdf9f1f10e15b281069176744d` |
| [onnx/onnx / pyproject.toml](<open-source/onnx_onnx/57b9c6a4f6eebb09ae1b34cfb632078518f72832/pyproject.toml>) | 1–38及依赖/构建定位；requirements传递集合未全审 | `ebf8788ede7bd7c99fd3718320fd61d07bbc031bd542e9c0c91ce13155c8da67` |

MLflow可借鉴模型ID/版本/来源、别名独立映射、存储后端委托、错误及查询；但所读SqlAlchemy create保存source/storage_location，下载URI返回该位置，注册整数版本不承诺字节不变。set_alias用merge修改指向，别名解析含latest分支；平台工程选择须冻结精确ref，不能每次生产follow alias。delete将source/run等涂改并删alias，是其业务语义，不直接迁成平台历史资产保留规则。制品下载可返回本地目录，条件满足还写registered_model_meta，消费者不能假定外部目录始终只读或全hash已验。

其下载URI测试明确保持source路径，alias测试核设置/查询/删除，artifact测试主要mock仓库与是否添metadata；这些不证明内容寻址、跨存储耐久、撤回/在途或产品级恢复。033不引入MLflow产品服务；如果将来作为外部工程追踪工具，须另定同步/部署/内容保持和授权边界。

ONNX可借鉴外部张量location/offset/length及递归子图/函数/属性依赖遍历。所读load路径先检查location，但未校验checksum、未在该函数证明读取长度恰好满足声明，0/缺失长度按真假分支；读入内存后external_data清除，不能再据内存对象反推原文件闭包。保存有按offset补零及写入分支，应先有界验证而非信任原输入。C++ location函数拒绝绝对路径、词法归一化后含“..”及非普通文件；注释写不允许symlink，代码未显式使用symlink_status检查各级链接，因此不能仅据注释声称已证明无重解析/竞态。平台在独占物化根核最终访问范围，未运行漏洞试验或推断所有后端受影响。

ONNX测试直接覆盖`../`、绝对路径和Windows反斜杠/盘符；所读范围不证明全部链接/TOCTOU/区间/资源安全。许可证根为Apache-2.0（ONNX原LICENSE与已有来源同字节复用），MLflow亦Apache-2.0及原版权通知；潜在复用要核适用通知和实际依赖。两者Python/原生生态非现成.NET平台组件：MLflow pyproject说明是开发文件、发布会替换；ONNX依赖动态来自requirements。本轮不声称完成传递依赖/商业分发审计、不引入这些生产依赖，AsunImage/DevExpress仍不核授权。

### HALCON公开读写能力

| 官方页与本地正文 | SHA-256 |
|---|---|
| [read_deep_ocr](https://www.mvtec.com/doc/halcon/2511/en/read_deep_ocr.html) · [正文](<official/halcon/20260928/read_deep_ocr.txt>) | `447810e8048e11778fe9b66fc0cf5b0639b710e21fbd05a797a183780e4d320e` |
| [read_dl_model](https://www.mvtec.com/doc/halcon/2511/en/read_dl_model.html) · [正文](<official/halcon/20260928/read_dl_model.txt>) | `dc326f7d3aae6d45a1235edd568548d9898d1602c005c6598f977e34cb36df94` |
| [read_ncc_model](https://www.mvtec.com/doc/halcon/2511/en/read_ncc_model.html) · [正文](<official/halcon/20260928/read_ncc_model.txt>) | `a668270b551f3cc0df4b79a279f93941097e5010cae141b07bade1e6f7b53ff4` |
| [read_shape_model](https://www.mvtec.com/doc/halcon/2511/en/read_shape_model.html) · [正文](<official/halcon/20260928/read_shape_model.txt>) | `4d5730e0938c52e9b54cb37372b9a846f2bc59c365cc9694fab004a5bddc5715` |
| [write_deep_ocr](https://www.mvtec.com/doc/halcon/2511/en/write_deep_ocr.html) · [正文](<official/halcon/20260928/write_deep_ocr.txt>) | `6fcf0ef4ba1c5a7c7f0e2848be044717043a03d13b27bf87983226c755bc194e` |
| [write_dl_model](https://www.mvtec.com/doc/halcon/2511/en/write_dl_model.html) · [正文](<official/halcon/20260928/write_dl_model.txt>) | `51f2494c753ce99216307dc593aefde933994c6fcfaeb0a1fca93f94596e5b1a` |
| [write_ncc_model](https://www.mvtec.com/doc/halcon/2511/en/write_ncc_model.html) · [正文](<official/halcon/20260928/write_ncc_model.txt>) | `64960b97c4a728b83afe8876d281a35ae07c7a03d367f7c3d30b8d07e9c637e5` |
| [write_shape_model](https://www.mvtec.com/doc/halcon/2511/en/write_shape_model.html) · [正文](<official/halcon/20260928/write_shape_model.txt>) | `5cc494caafa53bc7026ff11fde1c7f789b7dbf062cfb080e21d5710820c01cef` |

实际读shape/NCC/Deep OCR读写及write_dl的Description/Execution；read_dl读30–48、341–389，支持算子长表仅定位未逐项审。shape/ncc可写读真实文件，read返回可能可变handle；写文件不代表注册/耐久原子完成。Deep OCR/DL写文件不含gpu/runtime/runtime_init，读回默认；read_dl支持有约束ONNX且会变换网络（pooling/fusion/split等），不能靠加载成功推断后端等价。官方页的opset13/float32/四维输入等只属于所锁资料，不固定本平台底层版本；更高/其它形式不能自行猜可支持。具体公共适配仍要按生产者功能验证，不开展AsunImage内部/安装/兼容或授权核验。

### 竞品原PDF

复用[ScanSpection Operator Manual](<competitors/02_PCBA-AOI研究快照/research/operation_manuals/Reference_AOI/ScanSpection_AOI_Operator_Manual.pdf>)，SHA-256 `2b19ea19c2ce1ec93f9515217f1a51ae1b103057337e3d7b9f9efbec9d191187`。直接读第60/61/64/65/67/68页，渲染查看第65/67页。

第60/61页批量编辑/备用模板更新实例；64/65页说明主Board Setup文本与隐藏子目录内多份模板/库文件，支持“只拷主文件不完整”的约束；67/68页明确本地/中心库传播风险、稳定器件编号/方向协议、模板串错检查和主程序无法启动时外部恢复工具。平台采纳精确依赖闭包、受控升级与独立恢复；不照搬五级每日备份、最新备份必然最好、直接批量更新或厂商目录/编号规则。竞品没有公开模型注册内部事务/哈希实现，不能据UI证明平台精度或稳定性。

源AOI模板模型注册指导的冲突与采纳见[REF-008](REF-008_PCBA-AOI指导副本与平台采纳映射.md#model-assets-adoption)。原PDF未重拷/转换；11条Git来源中1条同字节复用，8份新官方正文。源tree/blob/hash、备份及定向检查保留`.work/model-assets-20260928/`，未运行MLflow/ONNX/HALCON/产品/WPF、上游测试或设备/工业对标。

<a id="inference-source-research"></a>
## 受控推理：预处理、批次、资源与恢复研究（2026-09-28）

消费者为[052 §7–16](../shared-modules/packages/PKG-052_Inference.md#inference-execution)、060、AOI可见焊接外观、PG-021涂覆与UI014。保持HALCON优先，未引入ORT/Triton产品依赖、远端服务或默认独立worker。本轮只定向阅读下列源码/真实测试断言与官方正文，未运行上游测试/库/平台产品。

- ONNX Runtime v1.22.1固定commit `89746dc19a0a1ae59ebf4b16df9acab8f99f3925`；MIT保留版权/许可，无担保。C#工程含System.Memory 4.5.5、SourceLink 8.0.0、适用target的System.Numerics.Tensors 9.0.0，另需实际native runtime/provider部署；所读target不证明本平台运行资格。若未来直接复用还须按真实选中二进制/EP依赖闭包处理第三方事项，本轮没有审查AsunImage/DevExpress授权。
- Triton core r25.08固定commit `70b908ca74b27407ae7c33b26ef26401d50aa871`；BSD三条款性质许可，保留通知、二进制文档义务且不得借NVIDIA/贡献者背书。根CMake默认headers/stub，完整server依赖common、Boost/Protobuf/Threads/re2，GPU/metrics/cloud等按选项增加CUDA/Prometheus/云SDK；并非可直接塞入WPF的无依赖DLL。这里只借鉴调度约束，未移植服务或其协议。

### 直接阅读范围及可借鉴限制

ORT的RunOptions.Terminate作用于共用对象的所有Run，不能为独立操作共用取消开关；RunAsync把原生回调接成Task，调用方等待结束不代表native已经停止。OrtValue可借外部buffer或pin托管内存，生命周期不等于输入不可变/可返池；GetTensorDataAsSpan所指存储可能在设备上，不可凭Span类型直接CPU解引用。shape/buffer校验不能替代平台checked长度/维度预算。异步测试有实际数值与线程配置错误断言，但未覆盖本平台批次取消/全部释放路径，不能把测试示例当完整所有权规范。

Triton按shape/optional输入组合、preferred/max batch与最老等待/最近deadline决策；可借鉴有限等待/明确短批。其超时政策包括DELAY与REJECT、队列0可无限，平台不能不经产品政策照搬。request_cancellation_test检查标记及再次请求恢复，且有“响应与release状态”FIXME和2秒sleep；不能把它称为真实GPU取消已排空证明或照抄sleep为同步。平台038保留统一资源权，052只在预算内组批。

| 固定原件 | SHA-256 | 本轮实际读取范围 |
|---|---|---|
| [microsoft/onnxruntime: LICENSE](<open-source/microsoft_onnxruntime/89746dc19a0a1ae59ebf4b16df9acab8f99f3925/LICENSE>) · [固定网页](https://github.com/microsoft/onnxruntime/blob/89746dc19a0a1ae59ebf4b16df9acab8f99f3925/LICENSE) | `2f07c72751aed99790b8a4869cf2311df85a860b22ded05fa22803587a48922c` | 完整许可正文 |
| [microsoft/onnxruntime: csharp/src/Microsoft.ML.OnnxRuntime/InferenceSession.shared.cs](<open-source/microsoft_onnxruntime/89746dc19a0a1ae59ebf4b16df9acab8f99f3925/csharp/src/Microsoft.ML.OnnxRuntime/InferenceSession.shared.cs>) · [固定网页](https://github.com/microsoft/onnxruntime/blob/89746dc19a0a1ae59ebf4b16df9acab8f99f3925/csharp/src/Microsoft.ML.OnnxRuntime/InferenceSession.shared.cs) | `f9f26441405bba72e6ffbdf88873940e8c314db356873f3aba574537500afcb3` | 1105–1172、1522–1590：原生回调Task与释放；不是C#取消证明 |
| [microsoft/onnxruntime: csharp/src/Microsoft.ML.OnnxRuntime/Microsoft.ML.OnnxRuntime.csproj](<open-source/microsoft_onnxruntime/89746dc19a0a1ae59ebf4b16df9acab8f99f3925/csharp/src/Microsoft.ML.OnnxRuntime/Microsoft.ML.OnnxRuntime.csproj>) · [固定网页](https://github.com/microsoft/onnxruntime/blob/89746dc19a0a1ae59ebf4b16df9acab8f99f3925/csharp/src/Microsoft.ML.OnnxRuntime/Microsoft.ML.OnnxRuntime.csproj) | `b65c5987bde28f73cf4dce52d442d6461c38bae227edbee8c27e9cb5b1b5015b` | 7–31、183–194：netstandard2.0/net8.0及包引用 |
| [microsoft/onnxruntime: csharp/src/Microsoft.ML.OnnxRuntime/OrtValue.shared.cs](<open-source/microsoft_onnxruntime/89746dc19a0a1ae59ebf4b16df9acab8f99f3925/csharp/src/Microsoft.ML.OnnxRuntime/OrtValue.shared.cs>) · [固定网页](https://github.com/microsoft/onnxruntime/blob/89746dc19a0a1ae59ebf4b16df9acab8f99f3925/csharp/src/Microsoft.ML.OnnxRuntime/OrtValue.shared.cs) | `eee8d65d87d777e2fe0a73c4d1cae8035b2eda50426f4ec4ee1de3ff8ec2e62d` | 195–214、559–668、1420–1458：device Span、外部buffer所有权、pin/shape及Dispose |
| [microsoft/onnxruntime: csharp/src/Microsoft.ML.OnnxRuntime/OrtValueTensor.shared.cs](<open-source/microsoft_onnxruntime/89746dc19a0a1ae59ebf4b16df9acab8f99f3925/csharp/src/Microsoft.ML.OnnxRuntime/OrtValueTensor.shared.cs>) · [固定网页](https://github.com/microsoft/onnxruntime/blob/89746dc19a0a1ae59ebf4b16df9acab8f99f3925/csharp/src/Microsoft.ML.OnnxRuntime/OrtValueTensor.shared.cs) | `bb787435f7031ad8d282f39207e918eea584db1a315ec64e2e461b7dff25aa6f` | 85–130、145–203：借用/转移、无Pin引用计数及释放 |
| [microsoft/onnxruntime: csharp/src/Microsoft.ML.OnnxRuntime/RunOptions.shared.cs](<open-source/microsoft_onnxruntime/89746dc19a0a1ae59ebf4b16df9acab8f99f3925/csharp/src/Microsoft.ML.OnnxRuntime/RunOptions.shared.cs>) · [固定网页](https://github.com/microsoft/onnxruntime/blob/89746dc19a0a1ae59ebf4b16df9acab8f99f3925/csharp/src/Microsoft.ML.OnnxRuntime/RunOptions.shared.cs) | `6a97577e8eb532408f6e2a44cd6baf5af0ffb3399d28a196ada500ced73e4b7e` | 93–117、144–159：Terminate是共享RunOptions取消域；释放方式 |
| [microsoft/onnxruntime: csharp/test/Microsoft.ML.OnnxRuntime.Tests.Common/InferenceTest.cs](<open-source/microsoft_onnxruntime/89746dc19a0a1ae59ebf4b16df9acab8f99f3925/csharp/test/Microsoft.ML.OnnxRuntime.Tests.Common/InferenceTest.cs>) · [固定网页](https://github.com/microsoft/onnxruntime/blob/89746dc19a0a1ae59ebf4b16df9acab8f99f3925/csharp/test/Microsoft.ML.OnnxRuntime.Tests.Common/InferenceTest.cs) | `3def62502ba5e67d481061d331dd842d2d66e1f6b8e42d31278b15a521d94459` | 2059–2130：FP16异步输出断言和单线程配置失败断言 |
| [microsoft/onnxruntime: csharp/test/Microsoft.ML.OnnxRuntime.Tests.Common/OrtValueTests.cs](<open-source/microsoft_onnxruntime/89746dc19a0a1ae59ebf4b16df9acab8f99f3925/csharp/test/Microsoft.ML.OnnxRuntime.Tests.Common/OrtValueTests.cs>) · [固定网页](https://github.com/microsoft/onnxruntime/blob/89746dc19a0a1ae59ebf4b16df9acab8f99f3925/csharp/test/Microsoft.ML.OnnxRuntime.Tests.Common/OrtValueTests.cs) | `2f5d417dc0d2bc96123f2a8d3db1be48c47cae559e29bdab7bcad65bf15d9740` | 121–214：CPU内存/shape/数值及托管/非托管构造断言 |
| [triton-inference-server/core: CMakeLists.txt](<open-source/triton-inference-server_core/70b908ca74b27407ae7c33b26ef26401d50aa871/CMakeLists.txt>) · [固定网页](https://github.com/triton-inference-server/core/blob/70b908ca74b27407ae7c33b26ef26401d50aa871/CMakeLists.txt) | `dbc88fa200c73825a029f6448236af528f74bae7636edf4f42eb30c9136ea127` | 根28–155：默认stub/C++17；src35–110：common及条件依赖（Threads/re2为定位读取） |
| [triton-inference-server/core: LICENSE](<open-source/triton-inference-server_core/70b908ca74b27407ae7c33b26ef26401d50aa871/LICENSE>) · [固定网页](https://github.com/triton-inference-server/core/blob/70b908ca74b27407ae7c33b26ef26401d50aa871/LICENSE) | `1b8a007445bc1a495a20f18da3b437454afe9af706e2120c0a54260452f9f273` | 完整许可正文 |
| [triton-inference-server/core: src/CMakeLists.txt](<open-source/triton-inference-server_core/70b908ca74b27407ae7c33b26ef26401d50aa871/src/CMakeLists.txt>) · [固定网页](https://github.com/triton-inference-server/core/blob/70b908ca74b27407ae7c33b26ef26401d50aa871/src/CMakeLists.txt) | `b39126ab1f0d0efbad510c2017bfea29dfbc606561f6a69c6bb66d84570be1a9` | 35–110：common/Boost/Protobuf及条件GPU/metrics/cloud依赖；Threads/re2定位 |
| [triton-inference-server/core: src/dynamic_batch_scheduler.cc](<open-source/triton-inference-server_core/70b908ca74b27407ae7c33b26ef26401d50aa871/src/dynamic_batch_scheduler.cc>) · [固定网页](https://github.com/triton-inference-server/core/blob/70b908ca74b27407ae7c33b26ef26401d50aa871/src/dynamic_batch_scheduler.cc) | `4114689beca045bf9a2e3ff854827ca9cc5ab85f6fa2e4abbf1eb2fe005b32eb` | 488–665：shape/optional输入、批次/最老等待/最近超时 |
| [triton-inference-server/core: src/scheduler_utils.cc](<open-source/triton-inference-server_core/70b908ca74b27407ae7c33b26ef26401d50aa871/src/scheduler_utils.cc>) · [固定网页](https://github.com/triton-inference-server/core/blob/70b908ca74b27407ae7c33b26ef26401d50aa871/src/scheduler_utils.cc) | `09d7d995353001cc5e8696f67a479658d33042808b9b00ca4165a4327118c3e3` | 76–145、161–195、219–259：形状/输入、队列上限、取消与DELAY/REJECT |
| [triton-inference-server/core: src/test/request_cancellation_test.cc](<open-source/triton-inference-server_core/70b908ca74b27407ae7c33b26ef26401d50aa871/src/test/request_cancellation_test.cc>) · [固定网页](https://github.com/triton-inference-server/core/blob/70b908ca74b27407ae7c33b26ef26401d50aa871/src/test/request_cancellation_test.cc) | `fc4f5e09a3a2a0889b46b8cd74fdd095c2286da2dfb199ea75d500d5711c253d` | 182–248：取消状态、重复请求恢复与FIXME/sleep局限 |

### HALCON官方行为与平台约束

复用此前[apply_dl_model正文](official/halcon/20260927/halconapply.txt)，重读21–69及69–176任务输出/执行说明。每输入DLSample对应DLResult，大tuple内部多批；短批仍补齐、按完整batch用内存/时间；Outputs空tuple返回该模型可用输出；模型类型/输出语义不同，3D pose/counting等不能在该算子下泛化。gen_dl_samples_from_images/preprocess_dl_dataset为procedure，不能猜成公开算子。官方支持timeout/interrupt不授予未知AsunImage取消签名。

新正文来自MVTec官方固定URL，下列版本号只标记研究来源，不冻结平台底层版本。set/get参数说明揭示改变batch/尺寸可重初始化、改变通道可能改变权重或拒绝，运行不能靠修改通道数适配输入。runtime_init对CPU、AI²或此前device设置等条件无效，调用成功不证明预热。设备查询可能为同一物理设备返回多个后端handle，id只在接口内有定义，查询能力不等剩余显存/执行准入。get_dl_model_param所读CPU线程说明2161与2165–2167存在对tsp_thread_num的前后冲突，本轮明确保留未决，不生成肯定的线程调参调用。

| 官方正文 | SHA-256 | 读取范围 |
|---|---|---|
| [get_dl_device_param](<official/halcon/20260928/get_dl_device_param.txt>) · [官方](https://www.mvtec.com/doc/halcon/2511/en/get_dl_device_param.html) | `acbf2562b4693156bd68729a223c6bf1a7d4138cbb166160516b8cf20b975011` | 26–130：id/ai2/precisions及参数范围 |
| [get_dl_model_param](<official/halcon/20260928/get_dl_model_param.txt>) · [官方](https://www.mvtec.com/doc/halcon/2511/en/get_dl_model_param.html) | `acf18124eee3038505d958714fa4c32ff5e6ac3df78046ece44802ba62d1cfcc` | 1422–1450、1622–1653、1786–1836、2127–2170：batch/device/channel/range/output/precision/runtime |
| [query_available_dl_devices](<official/halcon/20260928/query_available_dl_devices.txt>) · [官方](https://www.mvtec.com/doc/halcon/2511/en/query_available_dl_devices.html) | `b68af9e995cf553e85a7bb497ca0c53efdcecf9130c9bbff40f079157765ae12` | 28–78：过滤、同设备多个后端、执行说明 |
| [set_dl_model_param](<official/halcon/20260928/set_dl_model_param.txt>) · [官方](https://www.mvtec.com/doc/halcon/2511/en/set_dl_model_param.html) | `370dc507c16224d4b22354b73a5237b2bf4b13002b24b8e18ff0477ea654fe1f` | 75–101、179–237：批次/通道/初始化及执行说明 |

### 竞品原件直接核对

复用既有[Viscom vConnect PDF](<competitors/02_PCBA-AOI研究快照/research/operation_manuals/Viscom/Viscom_vConnect_EN.pdf>)，SHA-256 `29a4e1f24d5df649d1370800180ac581c3055ea7ea0b84ee1a9e26d87d9306a2`；本轮直接读取PDF第2/3页并实际渲染查看第3页，未重复转换。原件列出vAI Hub在线试验、既有/自建模型、培训、设备总览和可定制仪表板。可借鉴工程试验与来源/诊断联动，不能据此推断内部模型、生产自动放行、每设备离线推理、精度、P99或GPU取消可靠性；原图仪表盘仅证明呈现方式。

原AOI DEV-AI-001采纳/不迁入范围见[REF-008](REF-008_PCBA-AOI指导副本与平台采纳映射.md#inference-adoption)。Git tree/blob、来源下载元信息、阅读原件hash及定向检查脚本保留于`.work/inference-design-20260928/`，不生成第二研究清单供开发者维护。14份Git源、4份新官方正文；apply复用已有文件，所有新增来源按字节去重复核。没有运行HALCON/ORT/Triton、上游测试/WPF/真实模型/工业对标。

<a id="dataset-evaluation-research"></a>
## 数据集、真值与评估补充研究边界（2026-09-28）

本轮固定并读取 scikit-learn 1.7.2（commit `25dee604bae18205b01548348388baf7a1cdfe0e`）与 SciPy v1.16.2（commit `b1296b9b4393e251511fe8fdd3e58c22a1124899`）的源码、测试、构建声明和许可证。原件、Git blob、URL与SHA-256保存在`.work/dataset-design-20260928/research-sources.json`及对应目录；未引入Python运行时或外部统计DLL，未运行上游测试。

| 来源与实际读取 | 可借鉴结论 | 不能直接迁移 |
|---|---|---|
| scikit-learn `_split.py` 532–665、1040–1099、1102–1313；`test_split.py` 598–746、1010–1047 | GroupKFold/StratifiedGroupKFold的整组约束、分层近似与TimeSeriesSplit的未来顺序；测试明确检查组不交叉和覆盖 | shuffle只打乱组、不保证样本数平衡；TimeSeriesSplit明确忽略groups；分层可能隐藏依赖；不能替代板/批次物理谱系 |
| scikit-learn `_ranking.py` 900–1056、1069–1180 | PR/ROC按排序阈值聚合，ties与无正例情况必须显式 | 未读取的前段输入校验/排序细节不作完整审计；首尾曲线点/无正例处理是绘图语义，不能当生产召回或阈值资格；实现仅二分类 |
| SciPy `_binomtest.py` 129–375；`test_morestats.py` 944–1090 | exact二项双侧/单侧边界、Wilson及k=0/k=n算例和参数校验 | 只适用于满足假设的二项estimand；不证明聚类对象率或本平台门禁默认 |
| SciPy `_resampling.py` 130–365、610–658；`test_resampling.py` 80–121、459–471 | paired共享索引、batch内存界限、BCa/percentile/basic接口及常量数据退化测试 | batch仍保存统计量；常量样本BCa可NaN、percentile/basic可退化；逐FOV抽样不能替代物理组bootstrap |

许可证为BSD-3-Clause；pyproject显示Python/NumPy/SciPy等依赖和构建要求。平台只吸收分组、区间适用条件、配对/聚类重采样和退化处理的边界，具体estimand、置信水平、多重比较和Profile仍由平台Contract/Owner批准。NIST `pmc16.txt`仅作过程统计/假设边界参考，不能证明AI召回的二项或bootstrap门禁。与既有CVAT一致性研究、原项目指导和竞品PDF不重复转换或复制。

<a id="task-model-selection-research-20260928"></a>
## 逐任务模型选择补充研究 — 2026-09-28

本轮为 DEV-AI-064 的逐任务路线提供两类直接证据：HALCON 官方的语义分割、目标检测/实例分割、分类和异常检测章节，以及固定源码点的 `pytorch/vision`。资料只支持方法边界和测试设计，不证明 AsunImage 公共签名、目标设备资源或工业效果；平台仍按 AsunImage 接口使用，未引入 PyTorch 运行时。

### 官方能力的可迁移边界

|任务证据|设计结论|禁止推断|
|---|---|---|
|语义分割章节：像素分配到类别，训练与推理分开；本地正文见 [task-selection/toc_deeplearning_semanticsegmentation.txt](<official/halcon/20260928/task-selection/toc_deeplearning_semanticsegmentation.txt>)，SHA-256 `4b4fe7f6fc096c2dfd4a890c838869855cce49945f960e3ce3fa0fe5ed54eca7`|适合有稳定类别和像素/区域真值的破损、污染、异物、涂覆异常候选；必须保存有效域、坐标映射和类别/背景定义|像素类别不是尺寸计量、膜厚或板级处置；未标区域不能当正常背景|
|目标检测/实例分割章节：寻找实例并分配类别，允许部分重叠；[正文](<official/halcon/20260928/task-selection/toc_deeplearning_objectdetection.txt>)，SHA-256 `bec28f6e95f5707c373bdb1e721e5705ea4bd8664bf6e84f8fa5802d8f315bd2`|适合开放外观对象或缺陷实例候选；保留目标ID、关联、重叠/未匹配和候选截断记录|检测框/实例不自动拥有 CAD 目标身份、完整性或公差；top-k/NMS不证明未检出对象不存在|
|分类章节：给整图/裁剪分配类别，含训练与预处理说明；[正文](<official/halcon/20260928/task-selection/toc_deeplearning_classification.txt>)，SHA-256 `9e8aa0c7eebc98098b80e7b40561e37a2cee0d93a0e423b25a72d77cb74031a5`|适合已定义的表面样态/方向/可见性类别；输入裁剪、类别平衡、OOD和拒识必须单列|分类分数不是校准概率，不能从一张裁剪图推断隐藏连接、内部焊接或膜厚|
|异常检测章节：用正常图像共同特征推断输入偏离，输出灰度异常结果；[正文](<official/halcon/20260928/task-selection/toc_deeplearning_anomalydetection.txt>)，SHA-256 `21e7e25d1c41defe9f9558ed172aa361cbae0ceb9d4e7c204b18cd1d33223967`|适合缺陷类别开放、良品库可严格核准的表面候选；评估必须额外加入有真值异常，局部与全局/关系异常分开|异常分数不是缺陷概率、尺寸或放行结论；正常库污染、缩放裁剪和板边缺失会直接改变漏检风险|

这些正文只是方法章节，调用方式和参数仍须经适用官方资料与实际 AsunImage 公共 API 核对。不能把 procedure、HDevelop 示例或网页名称改写为未经核实的 C# 方法。

### torchvision 固定源码的可借鉴点

固定源码：[pytorch/vision v0.22.1](https://github.com/pytorch/vision/tree/59a3e1f9f78cfe44cb989877cc6f4ea77c8a75ca)，commit `59a3e1f9f78cfe44cb989877cc6f4ea77c8a75ca`；固定摘取位于 [`open-source/pytorch_vision/59a3e1f9f78cfe44cb989877cc6f4ea77c8a75ca/`](<open-source/pytorch_vision/59a3e1f9f78cfe44cb989877cc6f4ea77c8a75ca/>)。许可证为 BSD-3-Clause，未安装或运行上游代码。

| 实际源码/测试 | 观察 | 平台吸收与限制 |
|---|---|---|
| `torchvision/models/detection/transform.py` 的 `GeneralizedRCNNTransform` | 明确要求浮点输入；归一化、resize、padding、target box/keypoint 同步变换；推理后把 box/mask/keypoint映回原图 | 吸收“预处理与反坐标必须成对冻结”的测试要求；不复制 Python/Torch 实现，AsunImage/平台适配必须记录像素中心、裁剪、有效域和回变换 |
| `torchvision/models/detection/roi_heads.py` 的 `postprocess_detections` | 分数阈值、去小框、按类别 NMS、每图 top-k；类别间不做 NMS | 只借鉴候选过滤分层和边界测试；不能把截断后的候选清单当完整检测，也不能用 top-k 替代工艺目标全集 |
| `torchvision/ops/boxes.py` 的 `nms`/`batched_nms` | 分数相等时 CPU/GPU 可能选择不同索引；大候选量在两种实现间切换 | 生产需要明确 tie-break、CPU/GPU一致性和候选上限；候选数量/资源超限要返回未完成范围而非静默删项 |
| `torchvision/models/segmentation/_utils.py` | 分割结果按输入尺寸插值回原图，输出键区分主/辅助结果 | 只借鉴输出域和坐标回映；插值不扩大真实有效域，边缘/缺测/无效掩码必须保留 |
| `test/test_models_detection_utils.py` 与 `test/test_ops.py` | 测试覆盖非浮点输入、target不被原地改写、box形状、NMS参考实现、CPU/GPU tie行为、空输入和量化 | 吸收为 Replay/契约挑战用例；上游通过不证明 PCB 材料、缺陷召回、工业资源或现场资格 |

固定文件的 SHA-256：LICENSE `6502f676851cfe25f8af75531dfb32375b7325b73c37e7b43741fa422893e71d`；transform.py `31ad020ef2c23259373314b76ac5dc0f1ad2a2c44b69c68ba62f93df82d79b50`；roi_heads.py `521f7de74c5950499e8f00f6a514612afa8d5746d8fc6d8e9bcc860b611d0c38`；boxes.py `a36041ab58a365bc821ea6390734a23c84b1f61ba4a256c21562e47cffdb5eac`；segmentation/_utils.py `41fcaa0ad1ff3099c890a5b99bef7c1990f6323b4f60bb4f4c38bbf697081a1b`；test_models_detection_utils.py `e19e7019f3faeb76ebe90817a869ee8480c7b6ee0364b0b73140d762539deb4b`。

**选型结论：** 语义分割、实例检测、分类和异常检测在 DEV-AI-064 中按任务分开评估；不建立“万能 AI”模块。HALCON 经典量测/定位优先，学习路线只能在相同输入和 GroupId 数据上证明收益后进入 Replay/Shadow/Advice。torchvision 仅作为预处理、反坐标、候选截断和测试边界的源码借鉴，当前不作为产品依赖，也不取代 AsunImage。


<a id="reporting-source-research"></a>
## 报表运行、文档缓存与独立预览研究（2026-09-28）

消费者为[PKG-046 §6–11](../shared-modules/packages/PKG-046_Reporting.md#reporting-implementation)及[UI-PCS-021报告工作流](../shared-modules/guidance/14-page-contracts/UI-PCS-021_Quality_Control_Workbench.md#reporting-workflow)。固定数据、统计、模板与输出职责仍由原包拥有；本节只登记来源，不复制实施规范。

官方GitHub示例`DevExpress-Examples/reporting-wpf-mvvm-show-report-document-preview`的`24.2.1+`分支本次解析为commit `4eadceb21b2df58cf9497288870ad046c72e4f14`（提交时间2026-05-14）。通过GitHub API列出该commit的树，再按固定commit原始字节只读下表8份文本并归档；没有获取示例SQLite数据文件、产品程序集或图片，没有构建/运行源项目。其仓库树未发现产品测试，所读工作流只运行README措辞检查，不能作功能测试依据。

| 本地固定来源 | SHA-256 |
|---|---|
| [LICENSE](<open-source/devexpress_examples/reporting-wpf-mvvm-show-report-document-preview/4eadceb21b2df58cf9497288870ad046c72e4f14/LICENSE>) | `62e0c53cfd653505c69dadf93e6cc73428aaf593f4d9bf21ebd1aec2e883c3ac` |
| [CS/Models/DocumentPreviewDialogViewModel.cs](<open-source/devexpress_examples/reporting-wpf-mvvm-show-report-document-preview/4eadceb21b2df58cf9497288870ad046c72e4f14/CS/Models/DocumentPreviewDialogViewModel.cs>) | `d5c73e719f19c6d32f02bd2a9e5eb4067c57c98095f364d09428a8220bfb781a` |
| [CS/Models/ReportCatalogViewModel.cs](<open-source/devexpress_examples/reporting-wpf-mvvm-show-report-document-preview/4eadceb21b2df58cf9497288870ad046c72e4f14/CS/Models/ReportCatalogViewModel.cs>) | `af913701f49f021ae9640f78dfdc23c497ad9792d71f4bfc1119c291a552f21f` |
| [CS/MainWindow.xaml](<open-source/devexpress_examples/reporting-wpf-mvvm-show-report-document-preview/4eadceb21b2df58cf9497288870ad046c72e4f14/CS/MainWindow.xaml>) | `c0adf10e2d50bda7b0be5ef1ef932a00ca5120ca1afcba33c05b6e48be685620` |
| [CS/Data/ReportCatalogDbContext.cs](<open-source/devexpress_examples/reporting-wpf-mvvm-show-report-document-preview/4eadceb21b2df58cf9497288870ad046c72e4f14/CS/Data/ReportCatalogDbContext.cs>) | `30758df89e0f888ec621a4bdcaff3157164b094a415f722d6ebb1cc789afcb14` |
| [CS/ShowReportPreview_MVVM.csproj](<open-source/devexpress_examples/reporting-wpf-mvvm-show-report-document-preview/4eadceb21b2df58cf9497288870ad046c72e4f14/CS/ShowReportPreview_MVVM.csproj>) | `020e1a70ed4931f524bcc53c1f7dfefdd94b2550bd4eed2e9dd931d570bb0b3c` |
| [CS/packages.config](<open-source/devexpress_examples/reporting-wpf-mvvm-show-report-document-preview/4eadceb21b2df58cf9497288870ad046c72e4f14/CS/packages.config>) | `17b7eeeba3d0c5d05197edae4cb5ec8ef3f25be0e4db0530f82bda3e5d2c27c8` |
| [.github/workflows/vale.yml](<open-source/devexpress_examples/reporting-wpf-mvvm-show-report-document-preview/4eadceb21b2df58cf9497288870ad046c72e4f14/.github/workflows/vale.yml>) | `4f9aa0fa48066b6af658b693bef72eea9bafaed934ae707dea8a82636c33493b` |

实际读取范围：两个VM、XAML、DbContext、packages.config、LICENSE及workflow全文；csproj核目标/依赖/导入。可借鉴VM与独立预览、模板选择的结构；不能照搬其同步DbContext加载、对布局字节直接FromStream、全局当前Report和仅UI禁用。源项目为.NET Framework 4.7.2/DevExpress 24.2/EF6与SQLite，不能作为本平台.NET 10/25.2.3工程模板。LICENSE仅为示例免责声明及产品条款指向，未把该代码标为MIT开源；本次仅研究结构，未核验用户已定DevExpress依赖的授权。

本次官方API/行为核对入口：

- [25.2 PDF流/token异步重载](https://docs.devexpress.com/XtraReports/DevExpress.XtraReports.UI.XtraReport.ExportToPdfAsync%28System.IO.Stream-DevExpress.XtraPrinting.PdfExportOptions-System.Threading.CancellationToken%29?v=25.2)：确认相应公开重载；取消是否已结束与资源责任仍须实际适配测试。
- [25.2 PdfStreamingExporter](https://docs.devexpress.com/XtraReports/DevExpress.XtraReports.UI.PdfStreamingExporter?v=25.2)及[CachedReportSource](https://docs.devexpress.com/CoreLibraries/DevExpress.XtraPrinting.Caching.CachedReportSource?v=25.2)：区分PDF流式输出与文档页缓存，不推导数据源流式、不宣称无限规模或本平台性能达标。
- [25.2 ReportUnit](https://docs.devexpress.com/XtraReports/DevExpress.XtraReports.UI.XtraReport.ReportUnit?v=25.2)：报表尺寸采用声明单位，不把所有WidthF当屏幕像素。

安装技能`devexpress-reports-core`及export/bands/table/data-binding参考的元数据为26.1，已完整读取相应正文；只作为职责/反模式辅助，API以本平台目标版本官方资料为准。其NuGet/安装建议不适用于用户已明确的本机程序集方式。模板安全加载、脚本策略、表达式及WPF预览具体API尚需实施切片继续绑定；没有以本轮文档研究替代真实渲染、三语字体、输出完整性、取消恢复或生产资格。


<a id="spc-statistics-halcon-research-20260928"></a>
## SPC统计与HALCON算子边界研究 — 2026-09-28

本轮消费方为[PKG-045 §7](../shared-modules/packages/PKG-045_Statistics.md#statistics-implementation)、[058A统计实施](<../shared-modules/guidance/06-domains/DEV-DOM-058A_QualityControl SPC与分母定义开发指导.md#spc-core>)、FS-064与UI008。复用既有NIST能力页，不重复转换竞品/Office材料；下面18份原字节按官方/固定仓库分类存放。9份Git来源已分别核对该固定commit树的Git blob及SHA-256，未发现与本项目既有资料的完全重复内容；原版本仅标识研究来源，不冻结平台HALCON版本。

**官方实读。** NIST pmc31控制图概念、pmc32变量图/常数与组合规则、pmc321 Xbar-R/S、pmc322 I-MR、pmc331缺陷计数、pmc332不合格比例正文，URL分别为`https://www.itl.nist.gov/div898/handbook/pmc/section3/<文件名>.htm`。实际公式、常数、适用条件及读取范围在058A §12；本轮未以NIST经验数值冻结客户样本量。HALCON [tuple_mean](https://www.mvtec.com/doc/halcon/2511/en/tuple_mean.html)、[tuple_deviation](https://www.mvtec.com/doc/halcon/2511/en/tuple_deviation.html)、[tuple_sum](https://www.mvtec.com/doc/halcon/2511/en/tuple_sum.html)读取Description、参数、空输入及Execution Information：mean/deviation空tuple抛异常，sum空tuple返回空tuple；sum还接受纯字符串并做拼接，不能直接用于未核类型的计数。三页均说明无内部并行。所读deviation正文未明确样本方差分母，不能据此断言它符合058A的n−1定义。未带版本段的三个网页返回404，随后使用上述明确来源链接；没有把失败请求记为成功。

**Math.NET。** Numerics v5.0.0固定commit `4435308e1b0efcb40dc483140059a4e3a2204044`；实读RunningStatistics、真实测试全文及核心/测试工程、MIT许可。借鉴稳定中心矩、样本/总体分母分开、组合与退化数据测试。Combine空输入直接返回另一可变对象，源码部分巨大计数乘积可能溢出，DataContract明确不保证持久版本兼容；平台不直接照搬。测试依赖NUnit/TestData及内部随机分布，本轮未运行或读取全部测试数据。核心目标包含net6/net5/net461/net48/netstandard2.0，不能据此宣称本平台集成或性能已通过。

**qcc。** CRAN镜像2.7固定commit `11b6ecef027c315ed547e4749949ee3a7eed502c`；定向实读qcc.R的xbar/R/S、I-MR、p/np/c/u函数，utilities.R的c4及常数、zzz.R的常数装配，DESCRIPTION的R/MASS/utils/graphics/grDevices依赖和GPL>=2声明。树中未列单独LICENSE/COPYING文件，许可依据为DESCRIPTION与源头声明，未将其当MIT。只交叉核公式/常数，不复制GPL实现或引入R；其通用NA处理不能替代平台的缺测/覆盖政策。未运行或声称全读其上游测试。

**路线选择。** 有界tuple聚合优先核实际AsunImage公开能力；顺序流式/可合并中心矩、实体/子组、固定分母及控制限资格由045承担。本次源码方案是设计候选，尚无目标环境对比，不能以“不是视觉任务”直接跳过HALCON基础数值能力，也不能为复用tuple操作一次物化无限数据。公共签名/运算定义及目标负载对照在实现切片完成，不涉及AsunImage/DevExpress依赖授权核验。

| 分类后的固定来源 | SHA-256 |
|---|---|
| [mathnet_numerics/LICENSE.md](<open-source/mathnet_numerics/4435308e1b0efcb40dc483140059a4e3a2204044/LICENSE.md>) | `3f87fb0bec6467d87760555e3cb246646a51912b0e97f432c159ba6baf5738f2` |
| [mathnet_numerics/src/Numerics/Numerics.csproj](<open-source/mathnet_numerics/4435308e1b0efcb40dc483140059a4e3a2204044/src/Numerics/Numerics.csproj>) | `2d80ad19c4f8371f39e21e03f8bf339e7b1abf00ccb7daf87be195cd9436e596` |
| [mathnet_numerics/src/Numerics/Statistics/RunningStatistics.cs](<open-source/mathnet_numerics/4435308e1b0efcb40dc483140059a4e3a2204044/src/Numerics/Statistics/RunningStatistics.cs>) | `01465c61b69661ba029b040c03df642085757431361b845236e93d9f0c7cb03c` |
| [mathnet_numerics/src/Numerics.Tests/Numerics.Tests.csproj](<open-source/mathnet_numerics/4435308e1b0efcb40dc483140059a4e3a2204044/src/Numerics.Tests/Numerics.Tests.csproj>) | `528414487433286a41288c24265982f775065dea59632c952bf73149f9c4ac40` |
| [mathnet_numerics/src/Numerics.Tests/StatisticsTests/RunningStatisticsTests.cs](<open-source/mathnet_numerics/4435308e1b0efcb40dc483140059a4e3a2204044/src/Numerics.Tests/StatisticsTests/RunningStatisticsTests.cs>) | `980d923bc4e4ccd99057c8e12471b1396c84dcc9c5353cc8d5953beb5743cabd` |
| [cran_qcc/DESCRIPTION](<open-source/cran_qcc/11b6ecef027c315ed547e4749949ee3a7eed502c/DESCRIPTION>) | `10637ab1115f2806e5e6294953bb4356ac624646f07604103586fb2cedab7a0b` |
| [cran_qcc/R/qcc.R](<open-source/cran_qcc/11b6ecef027c315ed547e4749949ee3a7eed502c/R/qcc.R>) | `4144f3f953ab572949fb6480e14bb391b939ace88fb9bf39b43ffb05199650b6` |
| [cran_qcc/R/utilities.R](<open-source/cran_qcc/11b6ecef027c315ed547e4749949ee3a7eed502c/R/utilities.R>) | `e4807f7fc5fd4a169d4dfc040b4791565be583c27ed925dfc98b6dec95643842` |
| [cran_qcc/R/zzz.R](<open-source/cran_qcc/11b6ecef027c315ed547e4749949ee3a7eed502c/R/zzz.R>) | `0822a09f5f6ae6519b924730ddc09b786cf972783f30e21a1e73dff84b54ae7f` |
| [nist/pmc31.html](<official/nist/20260928-spc/pmc31.html>) | `63e4e39a79264eb7d29fb04e1aa0d52e4910504c51aa8c9a7333f395ef712eb4` |
| [nist/pmc32.html](<official/nist/20260928-spc/pmc32.html>) | `7a4a3e727010c6f20bb4288c8f715ba5a4575cc6a8627731c1a62870a463c4d8` |
| [nist/pmc321.html](<official/nist/20260928-spc/pmc321.html>) | `305fd47b6aff00753e8acb3c8e22eed419ecafd2b2e0cf2ede8d725e47f12917` |
| [nist/pmc322.html](<official/nist/20260928-spc/pmc322.html>) | `22b9832747168ce189c08031b91ff3a26fac92936465b2dccdc828daa21a3058` |
| [nist/pmc331.html](<official/nist/20260928-spc/pmc331.html>) | `16c46089591747732348164c01bab62ce4fbf2ba6e07c6301a3a05ac305bef87` |
| [nist/pmc332.html](<official/nist/20260928-spc/pmc332.html>) | `ab39223fda13f45d52dd01dd797aab0afd8f2efc1ed44c17feb0d16b94bb566c` |
| [halcon/tuple_deviation.html](<official/halcon/20260928-spc/tuple_deviation.html>) | `15af18aaa08f4395874341b523451496a3aaaeeaf954715272fd83ffb4b349af` |
| [halcon/tuple_mean.html](<official/halcon/20260928-spc/tuple_mean.html>) | `eb70fd9aee01f060ebb07e6de48fc192f92c571a287991bb88efb0b009b75f55` |
| [halcon/tuple_sum.html](<official/halcon/20260928-spc/tuple_sum.html>) | `402f5454cedaca2b38c6eaaaeaf5181364defc99ab60db0d1e715910fd112f24` |

所有原字节只作研究，未安装新产品依赖。正文公式/合成向量验证与产品算法、HALCON/AsunImage、Math.NET/qcc上游测试、数据库、真实WPF/DevExpress、工业计量/性能分别记录；未运行的项目不能宣称通过。研究暂存与验算脚本保留在`.work/spc-detail-20260928/`，唯一活动指导为058A，原始源码不直接作为平台开发文件。


<a id="drill-matching-source-review-20260928"></a>
## 钻孔身份关联、几何与缺孔解释的源码复核 — 2026-09-28

消费方为[PG-002 §13](../process-guides/processes/PG-002_drill.md#drill-method-implementation)、FS-023/024及第一条离线钻孔链。原HALCON圆拟合/轮廓交点/距离正文、固定scikit-image CircleModel源码/测试与ScanINSPECT两页PDF直接复用；具体读取行号/页码及可借鉴限制在PG-002 §13.10，不重复拷贝PDF或转换。孔口观察、缺孔原因、拟合质量、产品超差和全目标覆盖分别保留，不能从营销资料推导内部算法或客户阈值。

新增直接阅读SciPy v1.16.2、固定commit `b1296b9b4393e251511fe8fdd3e58c22a1124899` 的 `rectangular_lsap.cpp` 与 `test_linear_assignment.py` 全文；根LICENSE和pyproject与此前统计数据集研究同字节，复用已有原件。本次只新增两份源码/测试原字节，已用此前固定commit完整Git树核对四个文件的blob与SHA-256。所读测试所引入的其它测试数据文件没有因此算已读，上游测试未执行。

最短增广路及空矩阵/NaN/不可行/常量cost/稠密稀疏交叉断言可用于对照。常量cost测试要求返回单位映射，只证明特定数值返回行为，不能证明工业目标身份唯一；源码仅返回一个解，未定义平台的先最大匹配数再最小费用和歧义见证。实际接入必须保持禁边与零cost差别、完整候选/分量、二次歧义检查、有限资源及取消；小规模参考枚举用于可判定对照，不默认它能承担整板大规模节拍。

许可为BSD-3-Clause，局部C++文件依赖标准库及相邻header；完整SciPy有Python/NumPy/Meson等依赖。此轮没有引入运行时、复制产品代码或宣称它优于HALCON。HALCON可提供的视觉/几何仍优先经AsunImage公共接口调用；跨目标关联方法及数值门保持待采纳设计，不把外部库内部符号当平台API。

| 分类原件（同一commit） | SHA-256 | Git blob |
|---|---|---|
| [scipy/optimize/rectangular_lsap/rectangular_lsap.cpp](<open-source/scipy_scipy/b1296b9b4393e251511fe8fdd3e58c22a1124899/scipy/optimize/rectangular_lsap/rectangular_lsap.cpp>) | `73d78155990732311a116bc04f7f64d874c0f3793172e9aab12a476cb3d15c2c` | `8b9157e328158465346c10d5e8db7892ae1fc8b7` |
| [scipy/optimize/tests/test_linear_assignment.py](<open-source/scipy_scipy/b1296b9b4393e251511fe8fdd3e58c22a1124899/scipy/optimize/tests/test_linear_assignment.py>) | `f8819b88189d2cd58080ca372c1b1ad5a93cbff207f8c4fa9e7e383214cf7d4b` | `c3927056f28c80be7345feee3d434f6780fc580f` |
| [LICENSE.txt](<open-source/scipy_scipy/b1296b9b4393e251511fe8fdd3e58c22a1124899/LICENSE.txt>) | `221e59f5e910fd7f94e44f0dac77436a11338c285c6346232e4a850a50da0e94` | `1032aece8a8109d67f238de6865d8b08e750a8c0` |
| [pyproject.toml](<open-source/scipy_scipy/b1296b9b4393e251511fe8fdd3e58c22a1124899/pyproject.toml>) | `3f9c882e10cb29a2b4fbb59f7106fc1b7a749e6cf8c08ccd637231604dc7df7f` | `7c804541cc16b9b0ff527eeb5ebb32e954dcbb0d` |


<a id="assignment-source-review-20260928"></a>
## 固定图分配独立能力的HALCON路径与开源复核 — 2026-09-28

消费者为[PKG-062](../shared-modules/packages/PKG-062_Assignment.md#assignment-implementation)及PG-002/003。通过HALCON官方算子名称索引查找assign/bipartite/cost/flow/match相关入口，再直接读取assign、exhaustive_match、proj_match_points_ransac的Description；后二者同时核Execution Information，未运行算子、未验证AsunImage公共签名。官方出处使用归档URL的原版本，不把资料版本重新写为平台技术版本。

- `assign`是表达式/变量赋值，不是目标分配。
- `exhaustive_match`在ROI内滑动图像模板，输出相关/差异图，不是稀疏图最大基数/最小费用。
- `proj_match_points_ransac`由灰度邻域对应和RANSAC估计投影变换，最终会移除不满足一致性的点对；可支持原定位研究，不能直接充当固定独立基准后的完整孔关联或替代解证明。
- 本次没有找到与062合同同义的直接入口，不据有限检索断言HALCON全部产品/扩展不存在相应能力。视觉/几何仍优先HALCON；后续发现适用能力时以同一图合同/反例核对。

直接复读上述SciPy固定commit的rectangular_lsap.cpp与test_linear_assignment.py全文、LICENSE全文及pyproject前108行。源码的矩形最短增广、NaN/负无穷检查、常量费用tie-break和稀疏测试用于方法比较；测试导入的其他fixture未因此计为已读，未运行上游测试。纯图两工艺共享需求导致独立062；其单位容量最小费用流、禁每条主解边检查替代解、精确费用参考为平台待采纳设计，并非宣称SciPy已经提供这些完整保证。没有引入Python/NumPy、复制产品代码或完成第三方库生产选型。

本次新增4份官方HTML原字节；抓取时按SHA-256核docs/references同尺寸原件并未发现重复。URL均为`https://www.mvtec.com/doc/halcon/2511/en/<原文件名>`，原件保留版本。文本提取只用于定位，无截图/UI视觉验收；原网页数学公式图片不作为本轮公式依据。读取内容、哈希及独立图算例保留`.work/association-design-20260928/`，不把这些检查称产品或工业性能通过。

| 官方归档原件 | SHA-256 |
|---|---|
| [index_by_name.html](official/halcon/20260928-association/index_by_name.html) | `a9d428ec1d9370bf07cf8f5fd56fd5cd8be6322b8f099a75fad54a26ead259ed` |
| [assign.html](official/halcon/20260928-association/assign.html) | `c13131fd839703712a2a23e6bfce21bb1ef47ddc0b7f8121266a574b60a96b35` |
| [exhaustive_match.html](official/halcon/20260928-association/exhaustive_match.html) | `a7638d264fbe90f39e61f3065d7c0a59d68f661ab05b32d426a3c017995a6bf6` |
| [proj_match_points_ransac.html](official/halcon/20260928-association/proj_match_points_ransac.html) | `681b7a2fd99029daa17b5db58d34f2a157614170fc0a21505bdc6b6bd59a271a` |

<a id="assignment-performance-research"></a>
## 图分配加速、开源后端与数值证明复核 — 2026-09-28

消费方为[062 §3.5–4.1](../shared-modules/packages/PKG-062_Assignment.md#assignment-scalable-proof)、PG-002和PG-003。同轮复读上述SciPy固定commit的`rectangular_lsap.cpp`与`test_linear_assignment.py`全文，不重复拷贝；其双精度矩形最短增广支持结构研究，不能直接继承为稀疏最大部分匹配或近等价证明。

新增官方OR-Tools仓库tag v9.14、commit `0d60e8afe450ec817f510aae965ab8898310cb41`的三份原字节，复用既有完整Git树核blob与SHA-256；下载前同尺寸/hash去重，未重复归档。上游固定目录：[ortools/graph](https://github.com/google/or-tools/tree/0d60e8afe450ec817f510aae965ab8898310cb41/ortools/graph)。

| 原件 | 实际阅读范围（行） | SHA-256 / Git blob |
|---|---|---|
| [min_cost_flow.h](<open-source/google_or-tools/0d60e8afe450ec817f510aae965ab8898310cb41/ortools/graph/min_cost_flow.h>) | 14–123、188–245、251–367：算法/约化费用、状态、整数范围、公开供需与费用政策；其余仅定位，非全文审核 | `389ac554cb58f790d287da16d5feae7cd22cada73cab69f025b12541a7a16b01` / `9bca8ed86b9cff83223da9a3f7ae2520b63c8595` |
| [min_cost_flow.cc](<open-source/google_or-tools/0d60e8afe450ec817f510aae965ab8898310cb41/ortools/graph/min_cost_flow.cc>) | 229–261、413–443、445–553、1056–1185：原检查/势/费用缩放与饱和、max-flow后min-cost实际路径；其余仅定位，非全文审核 | `55562d99612f0ae15959a6de6641b7a7cbca3100134948057465ec8cdf8f0188` / `c41f42ccc0c10c0050c93bc58c633797c5715cb3` |
| [min_cost_flow_test.cc](<open-source/google_or-tools/0d60e8afe450ec817f510aae965ab8898310cb41/ortools/graph/min_cost_flow_test.cc>) | 287–341、412–469：总费用饱和、输入溢出、供需不足与最小费用最大流真实断言；其余仅定位，非全文审核 | `663010cd390a7be667fd54098d1dba49aec0095e930dc32effd6419fb0821b1b` / `3440faabb8f14a2533170ed69fc06fbb2c046509` |

复读已归档CMakeLists 159–192的wrapper/BUILD_DEPS及ZLIB/BZip2/Abseil/Protobuf/Eigen/re2依赖选项；实际最小交付闭包未据这些选项自动确认。LICENSE继续复用[同字节Apache-2.0原件](open-source/opencv_opencv/a0cda081f8d769f40ab2f4904738b4787b44d07c/LICENSE)，读取1–15及67–90，完整来源在前述OR-Tools研究。当前没有引入OR-Tools、复制产品实现、安装NuGet或批准部署；未来直接依赖须按实际代码/NOTICE/传递依赖完成相应接收，AsunImage/DevExpress不在该核验范围。

实际发现与设计影响：

- `SolveMaxFlowWithMinCost`的C++实现先求最大流，再以该量求最小费用，具备本目标函数的候选能力；不能把严格`Solve()`供需不可行当成本图K=0，更不能据C++头推断未经核对的C#签名/取消接口。
- 上游以int64存费用；缩放、势和总费用有不同溢出行为，total cost可饱和为int64最大值而状态仍OPTIMAL。其测试明确覆盖该行为。平台必须取原映射精确重算费用、校验原问题证明，不能把饱和值用于δ，不能把超int64的binary64精确尺度直接装进此后端。
- `SetPriceScaling(false)`允许扰动问题的1-optimal，上游的double先缩放舍入建议不等于062输入费用的精确最优。平台不以减小精度或改δ绕过BAD_COST_RANGE；若数学输入变化必须明确新方法，而非优化实现悄悄改变。
- 头文件的势/约化费用及源码的实际输入/结果检查提供比较依据；平台选择精确势函数Dijkstra和固定主解残量环作为待采纳候选，其循环证明来自062正文推导，不宣称上游已经实现本消歧合同。Simple接口未承诺warm start；读过CP-SAT的StopSearch不表示最小费用流有同等取消能力。

独立只读复核指出“仅更新已出队顶点的势”会制造负约化费用、不同禁边子问题独立缩放会让不同原值拥有同整数系数、主解完成后的取消应保留已完成证明，以及冷重解完整成本远高于单次主解；已写回062。复核保留在`.work/assignment-audit-20260928/`：244小图/269选边与穷举相符，包括非完美/零费用和1200位数值。这是设计实验，不是产品或上游测试。

主任务另以独立穷举→精确势函数主解→逐边冷重解→固定残量环交叉验证4341图、8327选边子问题；同时核完整Dijkstra与汇点提前出队两条路线的全图势不变量。包含需要s/t的非完美匹配、0cost、次正规/大数费用和三角不等式反例。脚本/原件hash位于`.work/assignment-refine-20260928/`；Python仅本地数学实验，未进入平台运行时。

未运行OR-Tools/SciPy产品库或上游测试、.NET平台、真实取消/并发/内存池、HALCON/WPF、设备或工业节拍。算法操作数下降不是工业时延成绩，4341图也不证明所有实现无错。后续按062正式合同及两PG真实图分布实现、测试与性能测量；当前DesignReview保持。


<a id="mask-segmentation-avi-research"></a>
## 阻焊方法、公共分割与终检汇合/翘曲复核 — 2026-09-28

本节供[PG-006 §16](../process-guides/processes/PG-006_soldermask-legend.md#mask-method-implementation)、[025](../shared-modules/packages/PKG-025_Segmentation.md)和[PG-011](../process-guides/processes/PG-011_final-avi.md#avi-exact-side-join)消费，保持62公共包与原Owner。文档/合成数学实验不证明真实HALCON、WPF、材料/设备或国际竞品水平；平台依赖继续AsunImage，不从来源页版本推平台HALCON基线。

### 阻焊边界、数字连通与有符号量

复读既有[distance_contours_xld](official/halcon/20260927/distance_contours_xld.txt)全文103行、[intersection_line_contour_xld](official/halcon/20260927/intersection_line_contour_xld.txt)的Signature、Description及Execution Information：前者是每个From点到To的无符号最短距离，点到段O(mn)；后者的直线不自动受两点截成有限线段，轮廓与线重合时返回段端点和IsOverlapping。PG必须限定有限搜索、真实边对应、支持与符号；既有公共能力优先，不据OpenCV存在相似函数引入第二套视觉后端。

新增OpenCV固定commit `a0cda081f8d769f40ab2f4904738b4787b44d07c`的3份原字节，复用既有完整Git树及同字节LICENSE。该快照已将相关函数放在`modules/geometry/`，不能根据旧版本路径声称读过imgproc源码。实际读取范围与消费：

| 文件/范围 | 直接观察及设计限制 |
|---|---|
| geometry.cpp 1–211：版权头与完整pointPolygonTest | 轮廓仅接受int32/float32点、查询点Point2f；以最后一点连首点形成闭环，空轮廓距离返回-DBL_MAX，符号通过奇偶内外判断。双精度返回不等于全程double输入；空值哨兵不能当物理负余量，开轮廓不能据此补闭；多环/孔洞与原生有效域须另有明确合同 |
| test_convhull.cpp 434–457、601–613 | 前段用到矩形内部距离作辅助检查；regression_10222只核大坐标点在多边形内。未覆盖本平台有限法向、未知域、多环、物理单位、桥宽或完整工业精度；未运行上游测试 |
| modules/geometry/CMakeLists.txt全文 | 模块依赖opencv_flann，wrapper列表为Java/ObjC/Python/JS，链接LAPACK并有Eigen提示；不是已证明可直接调用的独立C#库，也非完整依赖闭包 |
| 根LICENSE标题；geometry.cpp文件头及211行起的相邻代码说明 | 根为Apache-2.0，当前函数文件还保留Intel来源许可；后续相邻代码另有Joseph O'Rourke通知。未来复用具体范围须保留适用通知，根许可证不能覆盖掉文件内来源条件；本轮只读研究，未复制到产品实现 |

- [modules/geometry/src/geometry.cpp](open-source/opencv_opencv/a0cda081f8d769f40ab2f4904738b4787b44d07c/modules/geometry/src/geometry.cpp) · [固定来源](https://github.com/opencv/opencv/blob/a0cda081f8d769f40ab2f4904738b4787b44d07c/modules/geometry/src/geometry.cpp)：SHA-256 `250a4dc2618f979253ce4b5b279847b68c1738cfc63bc9f40877844420600466`；Git blob `5747e1c5ebf13106a22139f11c6111a94d9cf0de`。
- [modules/geometry/test/test_convhull.cpp](open-source/opencv_opencv/a0cda081f8d769f40ab2f4904738b4787b44d07c/modules/geometry/test/test_convhull.cpp) · [固定来源](https://github.com/opencv/opencv/blob/a0cda081f8d769f40ab2f4904738b4787b44d07c/modules/geometry/test/test_convhull.cpp)：SHA-256 `526763142413487383b8bb659ca921d9df3bfe9befe14ea3427e372e6ce48380`；Git blob `a2333b8a784ad3bfcb9b010097ea4932fedccc94`。
- [modules/geometry/CMakeLists.txt](open-source/opencv_opencv/a0cda081f8d769f40ab2f4904738b4787b44d07c/modules/geometry/CMakeLists.txt) · [固定来源](https://github.com/opencv/opencv/blob/a0cda081f8d769f40ab2f4904738b4787b44d07c/modules/geometry/CMakeLists.txt)：SHA-256 `5ea13db05eb604ed5aa575d4bcc0ef7d0f652b1e67db2028d1ab8ec687e0fe85`；Git blob `d92de297a4a98137992cb51b042c964dfc70bd2f`。
- [LICENSE](open-source/opencv_opencv/a0cda081f8d769f40ab2f4904738b4787b44d07c/LICENSE) · [固定来源](https://github.com/opencv/opencv/blob/a0cda081f8d769f40ab2f4904738b4787b44d07c/LICENSE)：SHA-256 `cfc7749b96f63bd31c3c42b5c471bf756814053e847c10f3eb003417bc523d30`；Git blob `d645695673349e3947e8e5ae42332d0ac3164cd7`。


据此补入PG006：处理支撑W先于名义输出域裁剪；M/N/Q三态及面积界；合法合并窗与一对一关联分离；法向余量m/窗口偏移δ/纯平移拟合Δ分名且保留原缺陷；桥的低/高材料域可证通/断/未决与有限采样宽度分离；跨tile、交点重合/孔洞、取消和提交Unknown链路。没有批准图纸量时不把拓扑、距离或PV改称行业标准指标。

独立设计算例`.work/mask-method-20260928/verify_math.py`枚举3×3三态域在4/8邻接下39366种输入、524288种未知补全，并与独立union-find核1024个二值域；连通上下界与每种补全一致。另核面积、矩形符号/平移秩、孔洞截线与160MiB/6144MiB显式缓冲算术。这是有限集合/公式复核，没有测试HALCON、OpenCV或平台实现；不能用其证明真实分类准确性、亚像素资格或节拍。


### 公共分割的真实支撑、形态与组件

独立并行Owner逐来源阅读和主任务接收落实到[DEV026 §7–15](../shared-modules/guidance/03-vision/DEV-VIS-026_2D分割、Blob与缺陷候选开发指导.md#segmentation-support-components)。该节逐项记录原件/行号及限制，原始取得和派生文本在`.work/segmentation-method-20260928/source-records.json`，主任务已核全部原hash并将下列10份新原件去重归档；scikit-image三份源码/测试对既有完整Git树验证Git blob。派生文本缺公式时直接查看HTML内嵌公式，代理与主任务均查看公式渲染，未凭文本空白猜比较边界。

实质约束：整数threshold的小数端点会被截断；dyn_threshold的light/dark含等号而not_equal严格；局部均值需要真实复合halo而非tile镜像；严格形态支持在W递推、最后才投影D；处理后区域不能覆盖原证据；默认8邻接/组件上限和tsp作用域须适配，不临时改全局；跨四tile角点合并后才能过滤全局组件。固定scikit-image的布尔/整数连通路径、整图拷贝/forest与bbox/spacing行为只作参考，不默认引入Python/Cython/SciPy或复制产品实现。

- [threshold.html](official/halcon/20260928-segmentation/threshold.html) · [来源](https://www.mvtec.com/doc/halcon/2511/en/threshold.html)：SHA-256 `308e0169864d793f0764fb6099b443bbe4746ce53249deb4c1a14b56694c3690`。
- [dyn_threshold.html](official/halcon/20260928-segmentation/dyn_threshold.html) · [来源](https://www.mvtec.com/doc/halcon/2511/en/dyn_threshold.html)：SHA-256 `63b9f2c2a105b93b0bfc9803984743a8084aa5aa5e7f4943419d7247f61e24bf`。
- [mean_image.html](official/halcon/20260928-segmentation/mean_image.html) · [来源](https://www.mvtec.com/doc/halcon/2511/en/mean_image.html)：SHA-256 `dcaa33e2952d6d2e1e0ba99435a005908b9706c9e6242ac64d0a9a4489309588`。
- [opening.html](official/halcon/20260928-segmentation/opening.html) · [来源](https://www.mvtec.com/doc/halcon/2511/en/opening.html)：SHA-256 `899fd3040bef4144663ecfc67eeb05c8c78b2951f5ca732b518e644e2ed0f753`。
- [closing.html](official/halcon/20260928-segmentation/closing.html) · [来源](https://www.mvtec.com/doc/halcon/2511/en/closing.html)：SHA-256 `54f119723da9938947219c4b8312fbcd7a1362a5f7ac147ffd5b09b890a071e0`。
- [dilation1.html](official/halcon/20260928-segmentation/dilation1.html) · [来源](https://www.mvtec.com/doc/halcon/2511/en/dilation1.html)：SHA-256 `05adafb191749d914969795e14742a59c7d35af9e55f2ae707f0997224d45038`。
- [src/_skimage2/measure/_label.py](open-source/scikit-image_scikit-image/533b7694d2004ae84e49e2cfd0bcfc5f8e562f22/src/_skimage2/measure/_label.py) · [来源](https://raw.githubusercontent.com/scikit-image/scikit-image/533b7694d2004ae84e49e2cfd0bcfc5f8e562f22/src/_skimage2/measure/_label.py)：SHA-256 `5a84738defe564b6e5074052a46b1be2b1e27d683d64ef6ed7d16e76afc798f5`；Git blob `786b99a24f130c2c06d3533dfcb497602d980441`。
- [src/_skimage2/measure/_ccomp.pyx](open-source/scikit-image_scikit-image/533b7694d2004ae84e49e2cfd0bcfc5f8e562f22/src/_skimage2/measure/_ccomp.pyx) · [来源](https://raw.githubusercontent.com/scikit-image/scikit-image/533b7694d2004ae84e49e2cfd0bcfc5f8e562f22/src/_skimage2/measure/_ccomp.pyx)：SHA-256 `a6081f8e142e39f8d323265338151dfbf3b1a06873a186f650cc856a1684b43b`；Git blob `27eba35b68d010acef5631cf74714a521db45afc`。
- [tests/skimage2/measure/test_ccomp.py](open-source/scikit-image_scikit-image/533b7694d2004ae84e49e2cfd0bcfc5f8e562f22/tests/skimage2/measure/test_ccomp.py) · [来源](https://raw.githubusercontent.com/scikit-image/scikit-image/533b7694d2004ae84e49e2cfd0bcfc5f8e562f22/tests/skimage2/measure/test_ccomp.py)：SHA-256 `5638bea3e7f989ce5a562f7c046f80f44866e0d494f02adf259d72f38adc3cb8`；Git blob `bbf8eaee194a2bee7f05d072044763447d88a79d`。
- [set_system.html](official/halcon/20260928-segmentation/set_system.html) · [来源](https://www.mvtec.com/doc/halcon/2511/en/set_system.html)：SHA-256 `0bbde4d336984eefaf27be3ae6bc348b719fba7ab923d4be2a9198aedf002942`。


代理独立设计脚本比较10240组二值、5832组三态的整域/分块组件集合，二值另核可加原矩，S26-01～11/16集合/算术向量通过；S26-12～15真实运行/并发/恢复并未执行。保留025两个消费者（PG006阻焊、PG021涂覆），不把局部高通响应的背景当已证明无材料。FS010/011同步唯一方法入口与特征缺值/复判建议边界，原公共端口/项目保持。

### 终检分面与翘曲

PG011 §12.4–12.6、14.1–14.5记录精确输入闭包/封口/撤销接受边界、AND/OR观察路线及独立分母、多视角关系非传递、法向/指定轴距、全局样本PV/三点支撑间隙。独立Open3D源码/测试/许可的实际阅读与限制在[该页§14.5](../process-guides/processes/PG-011_final-avi.md#avi-numeric-challenges)后续表，原件复用；源hash、15个离线数学/集合结果及链接核对在`.work/final-avi-detail-20260928/validation.json`。未重复下载或转换。

复核发现：TLS平面的样本PV不是最小区域目标；示例TLS-PV=0.119489641mm，另一可行方向宽度0.099503719mm即足以反证。Open3D当前cofactor构造不等于直接特征分解TLS，零内点RMSE可为0，不能当平台资格证明。缺极值点/逐tile去平面、不同支撑或法向混用均会虚假改善翘曲；双面采集/提交完整与每功能有效完成分列。FS028删除算法生成ReviewClaim的语义，保留原Owner提交与044受控领取边界，相关注册表描述同步。

只读交叉审核还发现并修正PG006的未处理D_f漏入未知、曲线法向交点误套线性平移与空/重叠桥锚区，以及旧HTML证据弹窗随新试检重标尝试的问题。已打开证据现在固定原上下文；新增面积界/桥/单法向δ与无二维Δ的三语投影，未实现全部P0–P7、e1/e2或翘曲交互。核验边界与欠账见[UI015 §17](../process-guides/guidance/14-page-contracts/UI-PCS-015_PCB_Inspection_Workbench.md#mask-avi-method-projection)。

<a id="mask-circle-model-research"></a>
### 圆形开窗的模型量与原边界 — 2026-09-28

本次补足[PG006圆形方法](../process-guides/processes/PG-006_soldermask-legend.md#mask-circle-opening)未能使用直边平移式的常见形状；复用已归档原件，不新增下载。实际复读HALCON [fit_circle_contour_xld](official/halcon/20260928/fit_circle_contour_xld.txt)409–682行：不自动分割轮廓、代数/几何目标差异、Huber/Tukey权重与剔除、geometric族忽略Iterations、MaxNumPoints采样与端点/闭合行为及最低3点。物理圆拟合仍经AsunImage的公共021能力，未扫描封装内部或把这次查阅当依赖核验。

固定scikit-image commit `533b7694d2004ae84e49e2cfd0bcfc5f8e562f22`复读[fit.py](open-source/scikit-image_scikit-image/533b7694d2004ae84e49e2cfd0bcfc5f8e562f22/src/_skimage2/measure/fit.py)569–667、[test_fit.py](open-source/scikit-image_scikit-image/533b7694d2004ae84e49e2cfd0bcfc5f8e562f22/tests/skimage2/measure/test_fit.py)198–307、[pyproject.toml](open-source/scikit-image_scikit-image/533b7694d2004ae84e49e2cfd0bcfc5f8e562f22/pyproject.toml)1–62及[LICENSE.txt](open-source/scikit-image_scikit-image/533b7694d2004ae84e49e2cfd0bcfc5f8e562f22/LICENSE.txt)1–25与108–132：

- 中心来自归一化后的代数线性最小二乘和秩检查，半径由到中心距离平方均值得到；文档写total least squares不能作为其等价于HALCON geometric的证据。整数先转浮点、中心化/缩放和退化检查可借鉴；具体精度仍取决于输入dtype，float32损失不能靠返回double恢复。
- `residuals`实现返回`r−distance`，与PG定义的`distance−r`诊断符号相反；已读测试多对残差取abs，不能证明外扩/内侵符号符合平台定义。工业几何必须按原被测量映射并加符号反例。
- 已读测试涵盖带噪估计、整数偏置、点数/共线/相同点等；未运行其测试，也不能据这些覆盖证明短弧或材料缺口资格。该包需Python、NumPy、SciPy等；根默认BSD-3-Clause并包含按文件列举的其它许可，未来实际复用须保留相应通知。本轮只读研究，未引入运行时或复制产品代码。

方法分别给中心偏移、半径变化、模型圆盘包含余量及原边残差；理想模型包含不证明原边界无内侵或未知，单圆不提供可辨旋转角。源hash、实际读取范围和独立几何挑战保存在`.work/mask-circle-design-20260928/`。模型量须独立通过方法资格后接039/040，不能自动取得规则接受或生产权限；真实拟合/传感器/工业精度仍待验证。


<a id="stencil-method-research"></a>
## 钢网方法与清洗比较的复读依据 — 2026-09-28

本轮落点为[PG-013](../process-guides/processes/PG-013_stencil.md)、FS-039～043及UI017；没有复制第二份竞品PDF或再做Office转换。复用[ScanSTENCIL Rev19082720原PDF](competitors/06_WEB公开资料/ScanCAD/原始资料/WEB-0020__ScanSTENCIL_Rev19082720.pdf)，SHA-256 `1ea0ba354658f360291794b5f9bc65bc93269e7c362c3cd1166806792180dc16`；本轮直接读第1/2页，并渲染查看第2页。制造/来料/清洗后检查、Gerber/Golden/PCB比较、LMA、多扫描和多层编辑可作为操作需求来源；宣传能力和0.001英寸/43%/无限工作区不能证明当前竞品性能、内部算法或本平台精度。该2019资料不能代替最新工业对标。

维护/前后比较[FS-043 §28](../process-guides/guidance/12-function-specs/FS-043_Maintenance_advice.md#stencil-maintenance-comparison)复读SciPy v1.16.2 commit `b1296b9b4393e251511fe8fdd3e58c22a1124899`，沿既有原件/hash，不重复下载：

|来源|本轮实读行|SHA-256|
|---|---|---|
|[_resampling.py](open-source/scipy_scipy/b1296b9b4393e251511fe8fdd3e58c22a1124899/scipy/stats/_resampling.py)|201-277,345-379|`ad8335279281c69d4a3bbf4449100e3ac5e1f5bc7af360963133973ed2a64d7e`|
|[test_resampling.py](open-source/scipy_scipy/b1296b9b4393e251511fe8fdd3e58c22a1124899/scipy/stats/tests/test_resampling.py)|80-123,451-475|`012dc7f62df460b78bff70aee95add3a77d0323644d8fbadcdf4926865fe9bff`|
|[LICENSE.txt](open-source/scipy_scipy/b1296b9b4393e251511fe8fdd3e58c22a1124899/LICENSE.txt)|1-31|`221e59f5e910fd7f94e44f0dac77436a11338c285c6346232e4a850a50da0e94`|
|[pyproject.toml](open-source/scipy_scipy/b1296b9b4393e251511fe8fdd3e58c22a1124899/pyproject.toml)|1-75|`3f9c882e10cb29a2b4fbb59f7106fc1b7a749e6cf8c08ccd637231604dc7df7f`|

paired实现要求数组轴长度相等并共同重采样索引；测试比对手工索引方案，batch测试核同结果；常量样本BCa返回NaN、其他方法可退化为点。可借鉴配对/退化挑战，不能用行顺序代替身份，不能把逐孔配对当独立钢网或对未知界中点套bootstrap。BSD三条款需保留通知且不背书；pyproject显示Python>=3.11、NumPy及Meson/Cython等构建依赖，不是现成.NET类库。本轮不引入运行时/生产代码、不运行上游测试。采用045既有统计能力，未知集合界采用确定性集合定义，并非SciPy产出的置信区间。

主任务独立穷举三个等面积单元的729组前后三态组合及其全部未知实现，核实整孔差量上下界与共同已知域四分割；另核已知比例下降却不能证明改善的反例。证据在`.work/stencil-review-20260928/`；这些是设计数学验证，不是光学算法、真实量测、WPF、业务协议或清洗效果资格。

### 开口/厚度/壁面方法的已有原件复用

独占方法Owner的实读范围见下表；对应结论唯一落在[PG013 §17.3](../process-guides/processes/PG-013_stencil.md#stencil-method-implementation)及FS039～042。父任务另抽查Open3D最终内点/refit顺序、HALCON intersection第二数组并集及distance属性/截断正文；全部原hash复核，未再拷贝、下载或执行上游。源码/测试/依赖/许可的范围与限制不扩大为全仓审计。

|复用来源|Owner实读行|SHA-256|
|---|---|---|
|[fit_line_contour_xld.txt](official/halcon/20260927/fit_line_contour_xld.txt)|406–639|`9758b3c659d889563464e3a32a1fa6a5a2b7d05e0ab963af595be5e9b2acbd7d`|
|[fit_primitives_object_model_3d.txt](official/halcon/20260927/fit_primitives_object_model_3d.txt)|147–352|`5272227a3e3ce5e984ad0a1825cb3775c6b249087d95aee39c14575944e3bfa1`|
|[distance_object_model_3d.txt](official/halcon/20260928/distance_object_model_3d.txt)|216–365|`ab23c92fb9b75a761c497fbd699363f6c42bf90d5e14b681e7821729461b6d88`|
|[intersection.txt](official/halcon/20260928/intersection.txt)|20–62|`3726232cfea049a0ef758a972eb7fc3fc8ee27e65836f47f1c0f6b80e73c7ef6`|
|[PointCloudSegmentation.cpp](open-source/isl-org_Open3D/b6c5e196384ad71e75b6e6f9c5da22d046221f1d/cpp/open3d/geometry/PointCloudSegmentation.cpp)|1–30、79–282|`44487a05b6f3b70a4da2a856220638b60e4c483350572d098fc1ea4c073d7751`|
|[PointCloud.cpp](open-source/isl-org_Open3D/b6c5e196384ad71e75b6e6f9c5da22d046221f1d/cpp/tests/geometry/PointCloud.cpp)|1358–1439|`b8041cb7d6f5ad0a60e2ef136d580c1a8c21704cea7aeced1b3398fdbc7241b1`|
|[LICENSE](open-source/isl-org_Open3D/b6c5e196384ad71e75b6e6f9c5da22d046221f1d/LICENSE)|1–23|`e2105d24aa1dae0fb5450f5b974dbf369b44d3c91a100d1b134922edb0647175`|
|[CMakeLists.txt](open-source/isl-org_Open3D/b6c5e196384ad71e75b6e6f9c5da22d046221f1d/CMakeLists.txt)|1–95|`59991d103ea11ef959c48a2da6f7e4e21ecbe89425a4efc9de213868bee0af06`|
|[_regionprops.py](open-source/scikit-image_scikit-image/533b7694d2004ae84e49e2cfd0bcfc5f8e562f22/src/_skimage2/measure/_regionprops.py)|349–372、449–503|`0aa4712757cf898917162044af61ac5264156d4357431c9b4cf37d17441e89f7`|
|[test_regionprops.py](open-source/scikit-image_scikit-image/533b7694d2004ae84e49e2cfd0bcfc5f8e562f22/tests/skimage2/measure/test_regionprops.py)|257–306|`c0ee9a2eacbf958424e163c3c3e9ace8b1b3dfe948106040111f25247d641c5f`|
|[LICENSE.txt](open-source/scikit-image_scikit-image/533b7694d2004ae84e49e2cfd0bcfc5f8e562f22/LICENSE.txt)|1–65|`611d3207504dcb4a808df209d2e7c9b4f2e89fe690f84735c0d548160966b527`|
|[pyproject.toml](open-source/scikit-image_scikit-image/533b7694d2004ae84e49e2cfd0bcfc5f8e562f22/pyproject.toml)|1–75|`374eb358f7255c091fb8dd61c2553c5e8e1c998c774b1b90c6a9000b83c19d4f`|

HALCON直线拟合不替输入分段，稳健剔点不消除原缺陷；3D primitive及最近距离的目标类型、原对象属性和截断值须按原适配边界处理。Open3D所读实现先定内点再refit，必须重新检查最终模型残差，不能照搬日志为资格；scikit-image像素spacing面积不授予光学或曲面资格。两固定开源点用于设计与反例，未新增钢网私有拟合、Python/C++生产依赖或重复模块。


<a id="supported-integral-research"></a>
## 点胶/涂覆支持域、连通与积分研究 — 2026-09-28

消费方为[DEV-MET-031 §9](../shared-modules/guidance/04-metrology/DEV-MET-031_通用计量引擎开发指导.md#supported-numerical-integral)、[PG016 §16](../process-guides/processes/PG-016_dispense.md#dispense-method-implementation)、[PG021 §17](../process-guides/processes/PG-021_coating.md#coating-method-implementation)和UI022/023。新增仅两份固定SciPy源码/测试原文件，其余15份来源直接复用；没有重新复制/转换竞品Office/PDF，没有引入Python/C++生产依赖。

### 官方/竞品的实际阅读与约束

- HALCON归档`get_grayval_interpolated`沿既有§5支撑约束复用；重新读`triangulate_object_model_3d` 214–270、336–435行：xyz_mapping依赖原2D映射，孔洞阈值默认10，设0才不补这类洞；仍不能自动证明跨跳变/原边缘资格。
- 重新读`volume_object_model_3d_relative_to_plane` 193–347行：逐面投影棱柱、Mode和面向影响贡献，但返回值是累计量的绝对值，`signed`不能映为保留正负的物理积分。PG胶量与030据此限制适配；不是在平台固定原件所标HALCON版本。
- `junctions_skeleton`及`gen_contours_skeleton_xld`的Description至filter/generalize1直接复读：单像素骨架、8邻接、结点分段及按点数过滤。骨架不含制造图/边方向/允许关系，不能自动生成确定的工艺拓扑。
- H222-0036既有PDF第18–22页直接提取，复用第22页渲染查看：分别定位胶与LED，胶顶/外围/边缘掉点分别展示。顶部可测不证明完整胶底或总体积；原例中的尺寸/公差不采纳为平台默认。
- WEB-0009/0010的True 3D、L.I.F.T低相干/NIR、多层材料、向导与翻板段复读；WEB-0016 Viscom CCI原PDF两页提取、复用第2页图像查看，并核该图原PDF与归档逐字节一致。其技术表单列层厚能力/传感配置，未公开本平台可复制的层模型/校准方法。营销分辨率、节拍和“AI免调试”均不是实施/工业证据。

### 固定源码、测试与取舍

SciPy v1.16.2 commit `b1296b9b4393e251511fe8fdd3e58c22a1124899`，新增文件用GitHub固定contents取得原字节并核Git blob：

|本地/上游|实际读取范围|SHA-256 / Git blob|
|---|---|---|
|[_quadrature.py](open-source/scipy_scipy/b1296b9b4393e251511fe8fdd3e58c22a1124899/scipy/integrate/_quadrature.py) · [上游](https://github.com/scipy/scipy/blob/b1296b9b4393e251511fe8fdd3e58c22a1124899/scipy/integrate/_quadrature.py)|1–175、240–377、402–491；梯形、累积梯形、非等距Simpson与限制|`9af70005ed11ed37df7b53488035c9b054b473186bd9c6b6a0c632bfd878d1aa` / `86d70feed7a40f6ebb2a75e9da43c5d7bc2b10d8`|
|[test_quadrature.py](open-source/scipy_scipy/b1296b9b4393e251511fe8fdd3e58c22a1124899/scipy/integrate/tests/test_quadrature.py) · [上游](https://github.com/scipy/scipy/blob/b1296b9b4393e251511fe8fdd3e58c22a1124899/scipy/integrate/tests/test_quadrature.py)|183–372；累积、axis/shape/dx、空输入、广播和masked真实断言|`1468d63910ef0f03c968dd00268b29a0e0101c817f9bae988aab3d2f240542c2` / `3cd2238b76edd7784a300cde13ee712c1e249eaf`|

可借鉴真实坐标差、轴维度检查与明确累积结果；源码不自动排序x，逆序会反转符号。masked样例`x=0..4,y=x²,x=2未知`的实际断言为13，对应仅[0,1]和[3,4]两段贡献，不是整域积分或带完整性结果；不能照注释猜成补0或删除样点跨洞。Simpson关于等/不等间隔多项式精确度的说明不授予真实缺陷检出性。源码/测试未运行；平台用独立有理数例核公式，不把它称SciPy上游通过。

复读根LICENSE全文为BSD-3-Clause及pyproject前100行：Python>=3.11、NumPy约束和Meson/Cython/pybind11/Pythran构建依赖。只作方法/测试思路参考，未审全部传递依赖，未复制生产实现或引入运行时。

另复用scikit-image commit `533b7694d2004ae84e49e2cfd0bcfc5f8e562f22`的`_skeletonize.py`1–102及`test_skeletonize.py`1–126、LICENSE前38行、pyproject前86行。入口先转bool；不同强度相邻物合并；全前景样例Zhang/Lee结果不同。实际空/维度/单点/细线断言已读，但底层Cython算法本轮未全读、未运行上游测试。依赖为Python/NumPy/SciPy等，许可证延续原条目，不因本轮借鉴就批准新依赖。

17份来源的本地精确路径、hash和新增Git blob保存在`.work/dispense-coating-method-20260928/sources.json`，活动来源原字节未改。独立核算覆盖线性裁切、正负量、部分域、未知分类/连通的全部补全及融合顺序；自审发现并补充“冲突U再和M归约会丢反证据”和“裁掉未知洞不自动恢复原单元支撑”。数学与HTML均不是HALCON、WPF、真实材料、设备或国际竞品资格。


<a id="spi-feedback-cfx-research"></a>
## SPI印刷反馈：固定CFX官方源码与运行边界

设计消费者为[055D](<../process-guides/guidance/06-domains/DEV-DOM-055D_SPI Rule SPC与Printer Feedback开发指导.md#spi-feedback-implementation>)及[FS055](../process-guides/guidance/12-function-specs/FS-055_Printer_feedback.md)。官方仓库[IPCConnectedFactoryExchange/CFX](https://github.com/IPCConnectedFactoryExchange/CFX/tree/880255d2f7380f340f56b243a51d99f2136bdae3)固定commit `880255d2f7380f340f56b243a51d99f2136bdae3`；其工程声明SDK `2.1.1`，不把它当平台已选依赖或设备已兼容版本。15份原文件的URL、Git blob、SHA-256及实际读取范围在[来源记录](../../.work/spi-feedback-design-20260929/sources.json)，固定原件位于[本地源码](open-source/IPCConnectedFactoryExchange_CFX/880255d2f7380f340f56b243a51d99f2136bdae3/CFX/CFX.csproj)。首次整库递归tree传输IncompleteRead，改读同commit根和CFX/测试有限子树，未用不完整数据证明文件完整。

| 真正读取的材料 | 可转用的设计依据 | 限制与不可照搬 |
|---|---|---|
| ModifyStationParametersRequest/Response、StationParametersModified、RequestResult、GenericParameter | 请求/业务响应/变更广播分开；官方请求注释要求成功后另外发布变更消息 | GenericParameter只有Name/Value字符串；不自动给单位、旧值版本条件、耦合原子性或作用板边界。变更广播也可来自操作员，不能仅凭同值归为本命令应用 |
| UpdateRecipeRequest/Response、ActivateRecipeResponse、RecipeActivated、SolderPastePrintingRecipe | 配方接收与激活是不同消息；激活含配方/可选修订、Lane、Stage、面等上下文 | Overwrite按同名覆盖并非本平台期待版本CAS。印刷Recipe提供行程/间隙/分离/清洗字段；该类未提供经本轮核准的XY补偿映射，不能发明参数名/单位/正负号。样例值不是工艺建议 |
| AmqpRequestProcessor.cs 330–413行 | 请求回调结果被补Source/Target/RequestID；无回调结果返回NotSupported | 当前读取路径不是设备幂等/效果证明；消息处理捕获异常后仍执行messageContext.Complete()，不能把传输完成当业务持久提交成功。其它端点、序列化及所有异常路径未完整审计 |
| DirectConnectTests.cs 1–215行 | 确有同步/异步AreYouThere响应非空、类型与Source/Target断言 | 已读断言不核Command执行一次、作用板/配方版本或效果；消息等待由回调设事件，不能证明特定消息语义。测试设置ValidateCertificates=false，仅为其测试行为，不迁入生产方案；未运行上游测试 |
| CFX.csproj、CFXUnitTests.csproj、LICENSE.txt | Apache-2.0；阅读授权/再分发保留、修改声明与免责声明条款 | 当前源码多目标含netstandard1.6/net8.0/netcoreapp3.1/net462；测试net48。依赖AMQPNetLite 2.5.1、Newtonsoft.Json 13.0.4等；未审完传递依赖，不宣称.NET10接入/安全/互操作资格 |

采用建议：可以优先研究官方消息定义/序列化与AMQP适配，以避免自造CFX协议；业务身份、权限、版本/执行守卫、原出站意图、回查和效果关联仍由平台原Owner处理。引入前以确定设备协议版本核实际消息、类型白名单/长度和反序列化边界、幂等/能力差异、故障与部署；不是借用`TypeNameHandling.Auto`属性就获得任意类型加载权限。本轮只归档读取源码/测试，不安装NuGet、运行SDK、修改客户项目或实现厂商控制。

未因同一SDK支持某消息就宣称竞品算法、闭环稳定性或生产效果已验证；竞品资料仍保持原件与既有索引。本轮把无ACK误写拒绝、配方接收等同生效、图像ROI性能模板和反馈输出InspectionFact模板改为具体交付/应用/后效语义，来源不足的设备能力保留为精确外部条件。

<a id="metrology-numerical-certificate-research"></a>
## 计量数值后端与参考证书解析研究

数值消费者为[045 §7.6](../shared-modules/packages/PKG-045_Statistics.md#qualification-numerical-backend)，证书消费者为[033 §15](<../shared-modules/guidance/04-metrology/DEV-MET-033_MSA、GR&R与计量资格开发指导.md#reference-certificate-adoption>)及030/055。源说明与实际代码/测试正文分开读取，未安装新依赖或批准运行时。

- Math.NET Numerics 5.0.0固定commit `4435308e1b0efcb40dc483140059a4e3a2204044`。[源码/hash/阅读范围](../../.work/metrology-qualification-method-20260929/numerical-backend-research/sources.json)、[逐操作取舍](../../.work/metrology-qualification-method-20260929/numerical-backend-research/recommendation.md)保留Simple/MultipleRegression、公共/内部QR、SVD、EVD、t/F、Beta/Brent、provider、实际测试和工程声明。重点是公共Thin默认、固定绝对秩阈值/尺度、t/F搜索域、Beta耗尽仍返回、PSD奇异性、全局provider与不可中断资源；不照README选择后端。MIT通知已读；native发行物不在本轮依赖验证范围。
- dotnet/runtime v10.0.0固定commit `60629d14374c56f1cb51819049ad1fa529307f8d`。[来源字节与hash](../../.work/metrology-certificate-adoption-20260929/sources.json)包括JsonSerializerOptions、JsonDocumentOptions、Serialization/OptionsTests中的重复键真实断言及Common/UnmappedMemberHandlingTests的Skip/Disallow与元数据优先级；最初Serialization目录的同名文件只是wrapper，未将它冒充测试正文。MIT原许可已读；本轮借鉴框架调用与测试边界，不复制产品实现。
- JSON Schema [Draft 2020-12 validation §7](https://json-schema.org/draft/2020-12/json-schema-validation.html)及[string参考](https://json-schema.org/understanding-json-schema/reference/string)实际正文：format默认注解与可选assertion、pattern非数值语义。微软[AllowDuplicateProperties](https://learn.microsoft.com/en-us/dotnet/api/system.text.json.jsonserializeroptions.allowduplicateproperties?view=net-10.0)、[未映射成员](https://learn.microsoft.com/en-us/dotnet/standard/serialization/system-text-json/missing-members)、[Decimal.TryParse](https://learn.microsoft.com/en-us/dotnet/api/system.decimal.tryparse?view=net-10.0)说明落实到严格解析、结构/语义分离和超精度禁止静默舍入。

AOI证书Schema和原指导仅定向采纳，见[REF-008](REF-008_PCBA-AOI指导副本与平台采纳映射.md#reference-certificate-source-adoption)。源文件的decimal正则实际解析可接受1.25及−0.25，未认定多转义缺陷；源Schema已有语义校验comment，不把未写成Schema断言的单位/信任等要求误报源项目缺陷。原件与已有PDF保持原位，不重复转换。

数值独立反例和接收只验证设计/来源，不代表运行Math.NET/.NET解析器、完整Schema校验、签名链、实物计量或工业性能。首次raw GitHub下载新测试正文超时，改用同commit官方contents取得原字节；没有以失败响应生成伪来源。真实后端支持域、合同和最终数值Profile仍需完成。

<a id="aoi-component-solder-method-research"></a>
## AOI本体/引脚/焊点方法的固定源码与原手册研究

方法消费者为[057B](<../process-guides/guidance/06-domains/DEV-DOM-057B_AOI Component Pin Lead Polarity OCR开发指导.md#aoi-component-method>)、[057C](<../process-guides/guidance/06-domains/DEV-DOM-057C_AOI Solder Joint与Pre_Post Reflow开发指导.md#aoi-solder-method-implementation>)及公共[031 §12](../shared-modules/guidance/04-metrology/DEV-MET-031_通用计量引擎开发指导.md#plane-height-offset-relations)。原PDF与固定源码均复用已归档字节，没有重复拷贝或转换；逐文件hash、URL和实际阅读范围在[元件来源](../../.work/aoi-component-method-20260929/sources.json)、[焊点来源](../../.work/aoi-solder-method-20260929/sources.json)。

| 实际来源/范围 | 已提取约束 | 复用取舍与限制 |
|---|---|---|
| ScanSpection Operator Manual PDF物理页85–101 | Lead/Solder分开、Pitch/宽度/端部pad、Anchor搜索/覆盖域与库更新 | 可见功能事实，不继承典型百分比/精度声明；不推内部算法 |
| PARMI Solder Joint PDF9–16、19–22页，11/19实际渲染；Lead PDF6–8页 | Comp/Pad参考、排除与ROI跟随、AND/OR、Height Ratio排序分位、Slope亮度特征、扩大搜索串邻脚 | 固定D/W及未知，像素排序不换最大高度，2D亮度不换3D坡角/润湿角；默认值不移植 |
| 已归档HALCON find_ncc_model、generic shape、measure_pairs、affine_trans_pixel | 候选抑制/边界/原点、像素坐标、边对支持及measure_pairs忽略domain | 优先原公共能力，不猜ImageLibDotNet签名；候选数值唯一不授物理唯一 |
| HALCON fit_surface_first_order及fit_primitives_object_model_3d指定段 | 高度回归与正交面目标不同；前者忽略image domain；后者默认cylinder、plane算法选项结果相同 | 不凭Tukey字样授稳健性；提取缺Alpha/Beta公式图未猜坐标映射 |
| SciPy `b1296b9b4393e251511fe8fdd3e58c22a1124899` rectangular_lsap及测试 | 等费用tie-break、无穷/NaN/不可行断言 | full assignment不替代原062最大部分匹配与消歧；BSD-3-Clause，Python/NumPy/pytest未接入 |
| OpenCV `a0cda081f8d769f40ab2f4904738b4787b44d07c` templmatch及测试 | 常量模板TM_CCOEFF_NORMED填1且测试重复约定 | 相关score非身份；不推HALCON同样行为。Apache-2.0及文件内历史许可分别保留，未移植core/imgproc/OpenCL路径 |
| Open3D `b6c5e196384ad71e75b6e6f9c5da22d046221f1d` PointCloudSegmentation.cpp及PointCloud测试指定段 | GetPlaneFromPoints最大主子式余子式法不普遍等于正交TLS；最终inliers由refit前平面选取 | 公共029仍最终重算原/内点残差；MIT，实际源码涉及Eigen/TBB，未审全依赖或引入运行时 |

Open3D散布矩阵反例以有理数独立核算：源方向Rayleigh商1/2，另一个方向10/21更小，足以否定“总是TLS最优”，未运行库或宣称所有版本有相同行为。其余局部集合/小图/几何反例也仅验证指导定义，不是实际HALCON、WPF、上游库或工业板通过。平台新增数学关系由公共030单Owner承接；产品仅定义本体、引脚、焊料的物理解释和接受，不复制内核。

<a id="metrology-tail-distribution-research"></a>
## 条件t/F的尾方向与公开Beta候选

唯一活动方法接收在[045 §7.7](../shared-modules/packages/PKG-045_Statistics.md#qualification-tail-distribution-method)，033/055保留实验/自由度与用途权威。研究固定Boost.Math `boost-1.88.0 / 529f3a759d83aa9437613666ea6293c9336d4069`，20份原文件的URL/hash/Git blob及真实读段在[来源清单](../../.work/metrology-distribution-method-20260929/sources.json)，包括实际t/F入口、逆Beta/策略/根、测试与高精表生成器，原件保留研究目录，不再复制。

[研究稿](../../.work/metrology-distribution-method-20260929/recommendation.md)与[独立审核](../../.work/metrology-distribution-independent-20260929/review.md)确认：活动t快速路径不等于被禁用的直接Beta示例；F(2,2)补分位的1−q发生在提高内部精度前，小尾丢失后无从恢复；inverse Beta直接互补对近中位t必要，x=1并不意味着其y=0；可用尾数/指数恢复最终比值，但救不了已下溢的内核变量。F(2,4)、f=2^600还证明中间y>0而最终尾概率仍下溢，范围诊断须覆盖最终输出。

独立审核以有理数Beta多项式积分和根括界核整数形状F、精确double近中位t、解析极端范围及作者参考恒等式；没有运行Boost/SciPy/Math.NET或通用反Beta，也没有把同源高精表与回代当独立oracle。源Math.NET原研究复用固定commit；SciPy仅定向消费sf/fdtrc说明尾方向，未审其特殊函数数值核。

Boost Software License 1.0原文及INTERFACE/standalone构建声明已读；源码再分发按许可保留，完整头文件/CRT/平台构建闭包仍须按实际采用范围核实。候选不授权C++产品DLL、有限C#移植或硬实时保证，不将研究许可等同生产部署决定。

随后[活动方法独立接收](../../.work/metrology-tail-adoption-independent-20260929/review.md)核`045 0.5.0-prep`的尾数/指数恢复、负奇数、极端乘积、小/大尾和范围反例，限定范围未发现确定退修问题；没有运行通用Beta或产品库。[固定运行研究](../../.work/metrology-distribution-runtime-study-20260929/recommendation.md)则实际使用现有VS2026/MSVC x64 C++17 `/O2 /fp:strict /MD`、standalone及显式Policy构建隔离exe，83份头文件进入编译。固定归档、精确include、实际读段、构建/输入输出hash在[来源](../../.work/metrology-distribution-runtime-study-20260929/sources.json)和[运行验证](../../.work/metrology-distribution-runtime-study-20260929/validation-results.json)，不把“用于编译”记成“全文语义已审”。

此次源码定位证实：Beta/Gamma连分式和Temme初值使用无显式计数重载，默认uintmax最大值；Gamma小a分支的series−10和0计数do/while不能用于全域低预算取消；df6的活动初值循环与禁用df8/10分开。实际运行复现F22原补尾丢失/交换改善、近中位t直接互补、最终尾下溢在throw策略下也无异常，以及选定root/series失败。14个解析点用实际binary64输入独立110位Decimal解析参考核验；其容差只用于这批点。主任务已将操作限制写入[045 §7.7.6](../shared-modules/packages/PKG-045_Statistics.md#qualification-tail-runtime-evidence)和Q1，研究probe不等完整受检恢复实现，单次纳秒不充当性能/硬期限。未安装生产依赖、运行上游全套或取得通用数值/ABI/工业资格。

[独立运行审核](../../.work/metrology-runtime-independent-20260929/review.md)随后核83份头文件/归档/include闭包及固定输入，重跑保留exe的30行数值/状态一致；用不同π构造的解析参考复核14点，新增t₆多项式独立反演。限定范围没有确定退修项，不将100/150位参考稳定性或15点约1.08e−16的最大相对差当连续域证明。原始TSV、作者核验与独立核验分别保持，不重编或宣称可重复构建。

<a id="quality-correlation-source-research"></a>
## 跨工序质量消费的CFX检测与返修来源

消费者为[058B](<../shared-modules/guidance/06-domains/DEV-DOM-058B_Cross-Process Correlation与Disposition闭环开发指导.md#quality-correlation-consumption>)、FS065及047候选接收边界。继续使用官方CFX同一commit `880255d2f7380f340f56b243a51d99f2136bdae3`，通过固定contents目录定位后取得原文件，不以名称猜测接口。[来源/文件hash与实际读段](../../.work/quality-correlation-adoption-20260929/sources.json)记录7份新增源码和3份复用许可/工程/测试；原PDF未重拷或转换。

实际读UnitsInspected的1–25与720–807类体及尾部样例，未全读其所有样例；UnitsRepaired、InspectedUnit、Inspection、RepairedUnit、Repair、UnitPosition全文。关键约束是UnitIdentifier可指实物/拼板/载具、站内TransactionId与检查发生ID/目标RefNo分开、RecipeRevision可选、Inspections允许只报失败而TotalInspectionCount含全部检查。InspectedUnit默认Passed、UnitsInspected默认Human、RepairedUnit默认RepairSuccessful及Repair构造自动Guid，说明平台不能把构造后值当原消息显式证据；本轮未运行SDK或具体反序列化器，不据此报告上游漏洞/运行失败。

Repair的原缺陷/症状引用与重新分类可借鉴，但平台原复判/返修Owner仍负责采纳，成功修复消息不替代实体复检或最终放行。可借鉴官方类型定义/适配角色，不能把其可变DTO、类型处理属性或默认值直接迁为048正式合同、通用事实/安全边界。完整字段存在性、允许类型与来源/幂等资格要在实际适配设计中冻结。

复用DirectConnectTests的1–215行：实际断言仍是AreYouThere响应非空/类型/Source/Target及事件等待，不证明逐目标完整、重复返修或跨工序关系；其ValidateCertificates=false测试设置不迁入生产。CFX.csproj全文声明SDK2.1.1及AMQPNetLite2.5.1、Newtonsoft.Json13.0.4等；Apache-2.0原文全文复读，保留版权/许可/修改通知。未审全部传递依赖、安装包、执行上游测试或批准.NET10运行时。本轮固定源码用于设计取舍，不宣称协议/设备互操作或工业资格。

<a id="process-correlation-source-research"></a>
## 跨工序关系核心的固定区间关联源码

消费者为[048 §6–13](../shared-modules/packages/PKG-048_ProcessCorrelation.md#process-correlation-method)、上述058B以及SPI反馈/AOI前后/返修新尝试。研究Apache Flink `release-1.20.0`，固定commit `b1fe7b4099497f02b4658df7c3de8e45b62b7e21`；[来源清单](../../.work/process-correlation-method-20260929/sources.json)保留实际下载URL、字节和hash，[作者读段与自审](../../.work/process-correlation-method-20260929/review.md)区分源码观察、平台要求及合成检查。复用同一份原文件，不引入Flink/JVM或复制第二份活动方法。

`IntervalJoinOperator.java`的双侧状态、时间桶遍历、可选迟到旁路、事件时间清理与结果时间=max(left,right)提供明确实现参照。主任务另实读L200–346及`NOTICE`全文，并核`IntervalJoinOperatorTest.java`的快照恢复段L304–388。原测试在恢复后期望(3,4)/(4,3)/(4,4)，是单算子恢复断言，不证明平台跨来源/数据库恰好一次；本轮未执行Flink测试。作者还读了开闭端点/负界、清理和迟到断言及官方仓库watermark/idle/interval inner join文档，范围见其报告，未把定位列表中其它文件记为已审。

可借鉴有界双侧状态、恢复时保留候选和显式迟到通路；不照搬纯时间命中作为物理关系，也不照搬未注册旁路时的迟到无输出。原算子遍历另一侧时间桶，不构成本平台范围索引的性能证据。watermark、idle及清理只表达流处理进度，不证明预期实物齐全；inner join不保留未配对成员，平台必须先保留总体义务。双时间/原修订、缺序号源切面、更正旧新键及原来无边成员重算仍按042/048设计，Flink没有提供这些生产语义。

根`LICENSE`为Apache-2.0，根`NOTICE`还声明文档资源MIT/BSD/OFL及ISC/AWS复用；算子依赖Flink runtime/state/serializer/timer和SLF4J，测试依赖其harness/JUnit/AssertJ，根pom管理Java目标1.8及shaded Jackson/SLF4J版本。这是作者固定源的定向观察，不是完整依赖审计或生产版本建议。当前仅借鉴方法；若实际移植/分发，再按采用范围保留许可、NOTICE及依赖声明。

[独立方法审核](../../.work/process-correlation-independent-20260929/review.md)核同一固定源/实际测试读段，并以有理端点、消息/事实去重、多对多、双时间、源缺口、旧新键及无边成员更正反例复核。发现旧§3把旧SPI与返修后AOI一概禁止关联，会误伤有权威链的履历追踪；主任务在048 `0.2.1-prep`收窄为不可冒充同轮可比输入，保留合法跨轮履历、另验数值与复检覆盖。同时澄清原子发布与业务缺项、清洗重印例与实物身份；[原受审字节](../../.work/quality-correlation-adoption-20260929/before/PKG-048_ProcessCorrelation.md)保持`0.2.0-prep`，独立报告不改写成已审新版本。定向差异接收另核仅这三处和版本变化，没有重跑旧套件冒充新的产品测试。

<a id="factory-input-source-research"></a>
## CFX信封、序列化与原接纳身份

本轮来源服务于[PLT013 §8](<../shared-modules/guidance/02-platform/DEV-PLT-013_跨模块事件与外部互联开发指导.md#factory-input-adoption>)和[047入站边界](../shared-modules/packages/PKG-047_FactoryIntegration.md#factory-input-boundary)，不复制质量058B或关联048方法。仍为CFX commit `880255d2f7380f340f56b243a51d99f2136bdae3`；通过固定tree/contents定位后取得CFXEnvelope、CFXMessage、Utilities/JsonConvert、AmqpReceiverLink及OtherTests。[来源清单](../../.work/factory-input-method-20260929/sources.json)保留固定URL、实际contents API、原字节/SHA-256/Git blob及全文实读范围。raw端点首次超时后改同commit contents API，未安装SDK或接broker。

信封构造器会生成UniqueID、DateTime.Now与Version=2.1，协议版本常量与SDK工程版本2.1.1分开；FromJson兼容分支依据messageName选择Type，CFXMessage也有按字符串创建类型的入口。序列化工具共享可变静态JsonSettings，并在调用中改变TypeNameHandling。平台据此选择在构造DTO前保留原字段存在性/类型/原值，固定允许消息映射及实例隔离，不从SDK默认ID/当前时间/成功值恢复生产声明。未审全部宿主初始化、防护和真实运行，不将上述观察写成已复现安全漏洞或竞态。

AmqpReceiverLink的linkCredit=300和callback不证明业务持久接收/确认点；平台使用自己的容量、幂等/回查和应用采纳协议。OtherTests全文含外部broker、固定本地文件、重写事件时间/Source的Replay例及无Assert的Malformed/Dummy/Upgrade，不提供严格JSON、字段存在性、业务幂等或崩溃恢复证据，本轮没有执行这些测试。原Apache-2.0和工程依赖沿上方CFX研究保留，新增读段未把原DirectConnect传输断言提升为入站资格。

[独立入站审核](../../.work/factory-input-independent-20260929/review.md)绑定PLT013 `1.2.0-prep`及047 `0.2.0-prep`、复核五份源字节与实际行为，限定范围无确定退修项。检查了信封/业务两级身份、两个worker与旧租约、原应用已提交而应答丢失、重启/映射升级/批量部分结果及UI关闭的逻辑交错；这是文档推演，不是运行SDK/数据库/真实取消。采用边界是可控解析与原应用接纳桥的方法，不批准CFX运行库、协议部署或恰好一次副作用。

<a id="cross-process-statistics-source-research"></a>
## 具名相关、配对差与分类一致性的固定源

唯一实施正文在[045 §8](../shared-modules/packages/PKG-045_Statistics.md#cross-process-statistics-method)，058B只组合问题/总体/质量解释，048只提供关系/缺口。[研究](../../.work/cross-process-statistics-study-20260929/recommendation.md)与[来源清单](../../.work/cross-process-statistics-study-20260929/sources.json)保留实际读取范围、固定URL及字节hash；已存在的SciPy正文/测试直接复用，未重复复制或安装依赖。

| 固定源及实际读取 | 可复用与不照搬的内容 |
|---|---|
| Math.NET `4435308e1b0efcb40dc483140059a4e3a2204044`，Correlation.cs L160–359及CorrelationTests L124–229 | 差分在线累计、平均秩和等长检查；最终sqrt(varA*varB)及delta乘积存在范围问题。WeightedPearson零/负权保护和矩阵默认单位对角不能当平台资格；无请求取消 |
| SciPy `b1296b9b4393e251511fe8fdd3e58c22a1124899`，_stats_py的Pearson/Spearman/paired t/Fisher段及test_stats相应段 | 借范数归一化、并列平均秩、t方向及解析/高精测试设计；普通mean/clip、近常数阈值、n2 p1、缺失删除和默认Spearman近似p不直接采纳。paired t的a−b须映射平台post−pre |
| sklearn 1.6.1 `f159b78dc59f250cdde8fe391a21f0bc871960ad`，_classification.py L340–415/676–770、test_classification L767–796 | 借表/边际和κ定义；labels删观察、int64 outer溢出、nan_to_num、类别距离权重都不解决平台缺口/退化/单位政策 |
| HALCON 25.05固定官方索引及tuple_mean/deviation/sort_index/correlation_fft正文 | 已先查适用能力；基础算子没有本研究所需完整配对/推断契约，图像FFT相关不等样本Pearson。所读索引未定位四种完整方法，不推断所有版本不存在，不改平台底层版本或扫描AsunImage内部 |

Math.NET MIT及SciPy/sklearn BSD-3-Clause原文已读，保留版权/许可/免责及BSD不得背书要求；项目声明的NumPy/SciPy/joblib/threadpoolctl、编译/pytest或NUnit依赖只按实际读范围记录，未审全部发行闭包。当前借方法，不选择生产运行库或把上游测试读取写成执行。

[独立审核](../../.work/cross-process-statistics-independent-20260929/review.md)对照16项源记录和活动消费者，未发现需退修确定P1/P2。其Fraction原点矩Gram/Decimal100与作者逐对差oracle独立，625小2×2表、360尺度/排列点及条件t解析夹具属于有限数学证据。另发现严格非共线r舍入为1和数学r=1却浮点越界两个反例，活动045明确不无条件clip或输出p0；近单类10^18表用精确整数避免po/pe相消。原脚本/结果不重跑冒充产品验收；Pearson CI、Spearman/κ推断、聚类/权重/重采样等保持未支持，条件t仍依原后端支持域与抽样假设。

<a id="roi-topology-source-research"></a>
## ROI拓扑、Region/XLD和固定矢量源码

研究服务于[024 §5–11](<../shared-modules/guidance/03-vision/DEV-VIS-024_ROI与Inspection Target Selection开发指导.md#roi-topology-raster-method>)、020以及PG002/013两消费者。[阅读记录](../../.work/roi-geometry-study-20260929/review.md)逐项区分公开控件说明、实际源码和独立解析反例；既有Asun-ROI快照按REF008复用，没有读取实现或重拷客户项目。只引用公开协议不代表已验证控件二进制，也不迁入源底层版本或授权门。

8份[HALCON固定官方原件](../../.work/roi-geometry-study-20260929/sources.json)核出亚像素顶点舍入、XLD自动闭合/Bresenham、center/border/border_holes、Region及XLD变换的corner约定、difference先合并Sub、run与空语义。单像素border往返成四像素是官方明确例子，本轮未执行native；由此要求具名转换和同grid集合校验，不将所有Region转换称Exact。官网研究URL版本只标识来源，不固定平台AsunImage底层版本；系统参数线程作用域仍待实际接入核明。

Clipper2 `Clipper2_1.5.4`固定commit `ef88ee97c0e759792e43a2b2d8072def6c9244e8`。raw首次失败原样保留，后按固定tree通过[Git blob API原件](../../.work/roi-geometry-study-20260929/blob-sources.json)取得Core/Engine/Clipper选段、两个测试全文、工程及许可证，并核Git blob/hash。PolyTree/FillRule、低层bool可借鉴；AwayFromZero、部分double谓词/交点、便利包装丢bool和上游宽松面积/输出路径数容差不直接迁入。固定Core `TriSign(1)=0`造成具名乘积比较反例，仅为源表达式分析，不声称整库或原控件已运行失败。

所读库csproj为netstandard2.0且无PackageReference；测试为net6.0/MSTest及FileIO项目依赖。Boost Software License 1.0原文已读，当前只作方法比较；未来源码复用按采用范围保留版权/许可，未引入Clipper或Python生产后端。[有限解析结果](../../.work/roi-geometry-study-20260929/geometry-results.json)验证正面积无中心、网格丢洞、近共线消失、剪切类型/圆弦界、corner及D/V，不冒充一般拓扑实现/工业精度。

本节形成时多带与匹配研究尚在审核；后续方法采纳、原P2修正及精确范围见下两节。原研究/失败记录保持只读，研究候选不成为第二份活动规范，也不因被此索引引用而授予新的原生API、产品资格或依赖引入权。

[ROI独立审核](../../.work/roi-geometry-independent-20260929/review.md)未发现P1/P2。以有理数/整数集合、非对称变换和格间折叠反例核方法，并复核8份官方原件及8份Git blob。P3指出原研究记录将`Paths64.Count`写成“组件数”：一个外环带洞是2条路径、1个材料组件；原研究保持受审字节，活动024与此索引已修正为输出路径数。原审核输入024为1.3.0，最终1.3.1仅此澄清和接收说明，未重复旧算例冒称新版本原生验证。


<a id="mosaic-multiband-source-research"></a>
## 复杂重叠与具名多带方法的来源和退修接收 — 2026-09-29

方法唯一在[029 §11.3–11.8](../shared-modules/guidance/03-vision/DEV-VIS-029_多FOV拼接与全局坐标开发指导.md#mosaic-multiband-method)，017只保留边界导航，钢网PG013与AOI057A消费同一方法。[原研究](../../.work/mosaic-multiband-study-20260929/recommendation.md)、[实读范围](../../.work/mosaic-multiband-study-20260929/source-notes.md)及[来源清单](../../.work/mosaic-multiband-study-20260929/sources.json)保存固定原件、请求失败、Git blob/SHA和实际读段，不重复拷贝已有PDF或源码。

| 固定来源/实际研究范围 | 采纳与限制 |
|---|---|
| OpenCV `a0cda081f8d769f40ab2f4904738b4787b44d07c`，blenders.cpp的prepare/CPU feed/归一重建、seam_finders逐对GraphCut、pyramids的D/U边界及两份实际测试 | 借鉴分带/相位/测试反例。整幅分配、图像反射与权重零边界、signed累加和逐对有限罚项不能当平台支持归一/任意拓扑/全局最优保证 |
| 固定HALCON `convol_image`、`gen_gauss_pyramid`、`binomial_filter`、`zoom_image_size`的Description/Attention及适用执行信息 | 优先组合可证明等价的公开能力；相同尺寸不证明核/相位/边界一致，reduced domain不代独立支持通道。`gen_laplace_pyramid`尝试URL的404不证明HALCON无其它路线 |
| OpenCV LICENSE和stitching CMakeLists | 研究保留Apache-2.0及旧文件通知；实际依赖含imgproc/features/geometry/flann及可选后端，未采纳OpenCV/Python运行时，不把文件头或源码阅读当部署资格 |

[首次独立审核](../../.work/mosaic-multiband-independent-20260929/review.md)以不同的格点依赖、直接gather及有理数系数检查有限核/相位/H、保护直取、分量隔离及负权来源；发现P2：按一个K·A遗漏各隔离分量的金字塔总工作。[活动采纳](../../.work/mosaic-multiband-adoption-20260929/review.md)在原029修为逐tile/分量/源/层累计，分开工作/I/O与同时存活内存；原推荐中的旧公式只作历史来源，不继续当方法权威。

[固定字节复核](../../.work/mosaic-multiband-adoption-independent-20260929/review.md)关闭该P2，限定接收029 `1.3.0-prep`及017 `0.3.0`，未发现新增确定P1/P2。独立区间支持计数复核8²/16²/32²碎片域，明确16²例来源层位置27200、重建13600；这些不是FLOP、native调用、真实I/O或节拍。72A与149.96MiB仍只是指定缓冲下界。029 `1.3.1-prep`仅补版本和接收记录，受审字节保留。

本批没有重跑旧金字塔数学当新运行验证，也未执行HALCON/OpenCV、真实取消/存储、WPF或工业样本。方法保持合法标签/有限ICM，非全局最优；多带仅派生显示，真实保真/公共适配/资源资格、alpha过渡及其它方法仍分别未完成。原几何、曝光、feather、保存/Unknown和工艺结果权威不变。

<a id="matching-variants-source-research"></a>
## scaled/aniso/planar/local匹配变体的固定研究 — 2026-09-29

落点为[023的同一Matching方法](../shared-modules/guidance/03-vision/DEV-VIS-023_定位、注册与Alignment开发指导.md#matching-variants-method)、022边界及钢网/AOI/FPC消费者。[研究正文](../../.work/matching-variants-study-20260929/recommendation.md#10-来源定位与实读范围)列H1–H15具体页及读取用途，[来源清单](../../.work/matching-variants-study-20260929/sources.json)保存HTML/文本/源码路径与hash；已有未全读来源明确不算研究覆盖。官方URL的版本只标研究原件，不固定平台AsunImage底层版本。

| 实际来源及方法对照 | 可借鉴与不可直接迁入 |
|---|---|
| HALCON create/find_scaled、aniso、planar_uncalib/local及origin/contour/scale/projective/map/param/clear相关官方正文 | 模型族与输出分开，aniso先模板轴尺度后旋转；planar部分创建range参数不使用；local返回绝对取样场。不能造统一全局矩阵或从函数名升级模型能力 |
| scikit-image `v0.25.2` / `e8a42ba85aaf5fd9322ef9ca51bc21063b22fcae`，[Projective/Affine/Piecewise实现](../../.work/matching-variants-study-20260929/github/skimage/transform/_geometric.py)及[test_geometric](../../.work/matching-variants-study-20260929/github/skimage/transform/tests/test_geometric.py)相关段 | 借鉴归一/SVD/失败输入、仿射与相似区别。零分母改epsilon不符合本平台用途门；分别重三角化正逆的控制点通过不保证片内严格互逆 |
| 同提交[TPS实现](../../.work/matching-variants-study-20260929/github/skimage/transform/_thin_plate_splines.py)与[对应测试](../../.work/matching-variants-study-20260929/github/skimage/transform/tests/test_thin_plate_splines.py)全文 | 借鉴输入形状/退化与对应点插值；float32矩阵、未实现inverse及缺拓扑约束不能给FPC生产资格。HALCON已有相关能力，不据此另引TPS后端 |
| 同提交[LICENSE](../../.work/matching-variants-study-20260929/github/LICENSE.txt)与[pyproject](../../.work/matching-variants-study-20260929/github/pyproject.toml) | 所读transform为BSD-3-Clause且TPS另有版权通知；Python/NumPy/SciPy及其它运行依赖不能忽略。仅研究，不引入依赖、不把全仓文件概括成一种许可 |

首次raw下载4项失败后用固定commit的contents API补齐，失败保留。[独立研究审核](../../.work/matching-variants-independent-20260929/review.md)对照官方相关段、原007/020/033及工艺链，并自行核坐标、域内无穷远、取样方向/插值支持和几何反例，限定采纳且未发现确定P1/P2；没有运行作者脚本或上游库。新增分片反例中控制点均通过而片内往返差2/3；正Jacobian环域仍可多对一，足以反驳“平滑/低残差即无折叠可逆”。

作者数学与独立推导不证明真实HALCON模型读回、local非零原点/扩边索引、native互斥/取消、真实钢网尺寸、AOI极性或FPC夹持资格。匹配变体活动字节接收及消费者差异另由本批接收记录绑定；精确公共成员/真实Golden仍按对应切片完成。没有扫描AsunImage内部或重新核依赖授权。

[活动字节复核](../../.work/matching-variants-adoption-independent-20260929/review.md)随后限定接收023 `1.3.0-prep` / 022 `0.3.0-prep`，未发现确定P1/P2；原多Mark/备用/保存/资源段保留，并以不同有理坐标例复核桥和crop。023 `1.3.1-prep`只加版本/接收记录。消费者的[独立差异审核](../../.work/mosaic-matching-consumer-independent-20260929/review.md)另核原C/计划/钢网/AOI/FPC；P3指出钢网“缓存复用”应为“工作区复用”，已单句修正，原受审字节与结果保持。


<a id="local-field-topology-source-research"></a>
## 局部取样场的声明连续扩展、全域检查与同拓扑逆 — 2026-09-29

落点是[023唯一方法](../shared-modules/guidance/03-vision/DEV-VIS-023_定位、注册与Alignment开发指导.md#matching-local-topology-method)，007/020边界与FPC/钢网消费；没有增加生产几何库。[研究建议](../../.work/local-field-topology-study-20260929/recommendation.md)、[逐来源实读记录](../../.work/local-field-topology-study-20260929/source.md)和[原件hash](../../.work/local-field-topology-study-20260929/sources/downloads.json)保留全部范围及失败获取更正。

复用原HALCON local/map、scikit-image v0.25.2固定来源，新增官方vector_field_to_real与intersection_segments。HALCON样本、源灰度插值和另声明的LF-PL-AC-1分开；重合段端点返回不等任意数值范围下的精确几何证书。新NTS v2.6.0固定commit `97d26b92586448b52d5a4f0c060217f94f882c75`实读定向/求交/STRtree与对应测试、工程/许可：DD与端点保留分支可借鉴，最近端点回退、PrecisionModel舍入不能用于严格集合相等；visitor未证明节点级硬取消。netstandard2.0/2.1、2.0条件System.Memory依赖与BSD及第三方通知均保留，未引入运行库或执行上游测试。

[root独立方法审核](../../.work/local-field-topology-independent-20260929/review.md)检查充分条件、逆和消费者边界，并以不同闭半平面裁切方法核有限片交集；六项定向反例包含连通矩形正J仍重叠及只映ROI端点丢失1/4px折线差。该差仅属合成例。作者16项及独立结果分开，不冒称原生算法、严格数值后端、空间索引/取消、WPF或计量通过。公开严格接入、原grid适配、真实材料/模型误差及生产数值/性能仍需按原切片完成。


<a id="model-canonical-readback-source-research"></a>
## 模型资产规范化、摘要与同内容读回 — 2026-09-29

落点为[IM-014唯一技术方法](../independent-modules/model-assets/DEVELOPMENT-GUIDE.md#9-新资产-jcs旧资产原规则与版本迁移)和Matching/OCR/052/053消费；[033](../shared-modules/packages/PKG-033_ModelAssets.md#model-assets-canonical-method)只作应用映射，原C及014 §27.1承接平台边界。固定[研究](../../.work/model-asset-canonical-study-20260929/recommendation.md)、[原文来源](../../.work/model-asset-canonical-study-20260929/sources.json)、[源码blob](../../.work/model-asset-canonical-study-20260929/blob-sources.json)及[本地原协议实读](../../.work/model-asset-canonical-study-20260929/local-sources.json)是有限来源证据，不替代当前模块合同或真实运行资格。

研究实读RFC8785 §3/5/所用位模式、.NET官方字符转义/顺序/时间/重复字段，固定dotnet/runtime v10.0.0 `60629d14374c56f1cb51819049ad1fa529307f8d`的Options源码与MIT；作者在隔离目录观察本机runtime10.0.9，未声称源码等同本机全部实现。默认STJ和UnsafeRelaxed输出不是JCS，双精度先解析会丢大整数，时间与Unicode不能靠隐藏归一使旧hash漂移。

固定Trail of Bits rfc8785.py `655cbe02b8761208e3f4cc49e879ab1e328a7dca`（源码版本0.1.4），实读实现/测试/向量/pyproject/Apache-2.0及归属，运行依赖为空，测试依赖另记；只作研究对照，不引入Python生产后端。实现能规范化已解析对象，不能发现字典形成前丢失的重复字段；safe-int子集、递归/排序/缓冲与无预算/取消均保留，100M语料缺失的skip不算通过。

[独立审核](../../.work/model-asset-canonical-independent-20260929/review.md)限定接收研究，无确定P1/P2。独立Node按UTF16递归直接输出对象成员，避免“先建JS对象再Serialize”把整数形键10/2重排；RFC26个位模式、六组固定向量和179字节核心`dd51591c19fbcc143f7b740c0ee23115fea7072758ca03d2fdc20f764fad0d48`由独立路线核对，Python另核严格解析/路径词法。两套观察器并非生产完整管道；原工具失败/命名修正和UTF8读取修正均保留，未运行作者旧脚本冒新验证。

真实HALCON模型fresh读回、041事务/安全打开、完整跨语言canonical实现、资源/取消/WPF/工艺资格均未通过本研究验证。原AOI Manifest/安全投影/Proto各守旧协议，JCS为可评审新规则路线；未知旧算法不由新算法重算判坏。研究的.NET首次运行曾提示开发证书，未执行信任或删除，相关副作用按原报告保留。


<a id="local-field-exact-numerics-source-research"></a>
## 固定片精确数值路线的来源与采纳 — 2026-09-29

[研究正文](../../.work/local-field-exact-numerics-study-20260929/recommendation.md)、[固定来源/读段](../../.work/local-field-exact-numerics-study-20260929/source.md)、[原观察](../../.work/local-field-exact-numerics-study-20260929/results.json)与[独立审核](../../.work/local-field-exact-numerics-independent-20260929/review.md)接入[024唯一方法](../shared-modules/guidance/03-vision/DEV-VIS-024_ROI与Inspection%20Target%20Selection开发指导.md#roi-local-exact-numerics)、020/023及L2顺序。HALCON仍提供原场，平台只补声明PL资格所需的受限算术，不另造视觉主干。

固定dotnet/runtime v10.0.0 commit `60629d14374c56f1cb51819049ad1fa529307f8d`，实读BigInteger/BitConverter/NumericsHelpers、乘除实现/工程及GetBitLength/构造/移位/DivRem测试，MIT范围与具体读段见source。调用现有.NET公开能力，不复制runtime内核、不增加运行依赖。NTS固定v2.6.0仅复用其原分类/近似回退研究，不能代本严格证书。

作者实际隔离.NET10.0.9 x64观察278有限比较，与固定v10.0.0源码分开；独立审核未执行作者探针，以新闭半平面裁切/有理距离浮点oracle核反例和位长。2098/4199/6299/8400/10499界只针对原dyadic片及一次构造，558→640乘法仅具名调度；GC/池/内存峰值、任意递归ROI布尔、完整索引、真实场/物理误差及生产性能未证。原404/下载/编译提示与有限结果保留，不重跑旧套件冒采纳资格。

root接收时发现独审文字把`(0,0)→(3,3)`与`(5,0)→(0,2)`误标为W负分支；实际W=21。第二段倒向才得到W=-21，规范后同为H=(30,30,21)。[直接整数核对](../../.work/vision-methods-integration-20260929/negative-w-example-correction.json)固定两种方向，本次活动例按此纠正；原研究/独审记录保持，不将其方向误标当正确证据，通用公式及交点结论不变。

<a id="ocr-decoding-association-source-research"></a>
## OCR模式、CTC原读与目标关联的来源深化 — 2026-09-29

[root研究](../../.work/ocr-decoding-association-study-20260929/recommendation.md)及[独立审核](../../.work/ocr-decoding-association-independent-20260929/review.md)采入[021A唯一方法](../shared-modules/guidance/03-vision/DEV-VIS-021A_OCR与DeepOCR独立能力开发指导.md#ocr-decoding-association-method)，024/PG006/057B消费，原C与O0–O5承接。复用原HALCON apply/get归档和PaddleOCR `b03f46425e8ff4442b268ce449e3eef758146cd4`，没有重下、安装权重或运行OCR环境。

定向实读Python `rec_postprocess.py`前245行、C++ `processors.cc`前271行、`pipeline.cc`关联/过滤段及实际分词测试，许可/依赖沿原条目。HALCON三模式字典/输出域与Paddle CTC折叠/Blank/分数、空图压缩/排序回填分开；模型alphabet_mapping不等普遍字符串替换。C++先访问StatusOr.value、空时序/索引混用均只记静态风险，没有冒称真实推理复现。

独立小状态递推确认两步greedy为空而最大概率串为A；Blank分隔重复、保留位置均分、显式batch置换、Unicode单位及mapping不可逆有有限反例。它们不证明OCR模型准确率、PaddleX全链、内部坐标、native或WPF。路径含arabic的后处理与多码点token的word-box限制继续明确，CTC方法不能套全部网络或推断HALCON内部实现。研究源清单的失败记录无path引发一次读取KeyError，修为只取真实归档；原记录不删，未改来源或旧结果。


<a id="training-export-source-research"></a>
## 训练恢复与导出交接的实际来源 — 2026-09-29

[060唯一方法](../shared-modules/guidance/07-ai/DEV-AI-060_AI运行治理开发指导.md#ai-training-export-method)及053消费的原字节/差异见[作者交付](../../.work/ai-training-export-method-20260929/report.md)，[source](../../.work/ai-training-export-method-20260929/source.md)/[固定清单](../../.work/ai-training-export-method-20260929/sources.json)给实际URL/hash/读段与限制。HALCON官方OCR数据/分组件工作流、batch/整集异常训练及AI²优化优先；本次读的是.hdev流程说明，没有取得/执行全部示例源码，不猜ImageLibDotNet绑定。

PaddleOCR `b03f46425e8ff4442b268ce449e3eef758146cd4`保存/加载/训练/导出源证实pdopt缺失容错、epoch接续与状态传递不足，不能据模型文件可读证明完整scaler/RNG/sampler/optimizer恢复。anomalib `030c2df604175e07172873f4fca2dba2888ef569`的PatchCore无optimizer建bank、ExportMixin的PTQ/accuracy-control数据流及有限integration测试，支持按真实路线区分训练/转换，不把test_dataloader名称当最终测试。两项目代码许可/传递依赖沿固定来源，只研究不引入运行库或权重。

checkpoint同安全边界、完整保持、best与最后模型、导出前后语义翻转和用途采用分别写入060。有限momentum/类别/阈值例不是实际训练/恢复或导出测试；真实后端与物理样本资格未由源码读取关闭。

<a id="ocr-text-evaluation-source-research"></a>
## 原串Unicode、编辑距离与OCR评价来源 — 2026-09-29

[063唯一方法](../shared-modules/guidance/07-ai/DEV-AI-063_数据集、GroundTruth与统计验证开发指导.md#ocr-text-evaluation-method)的[source](../../.work/ocr-text-metrics-study-20260929/source.md)固定Paddle RecMetric、JiWER、RapidFuzz以及.NET Rune/严格解码官方页。Paddle默认去空格、可选ASCII/lower与逐串norm_edit_dis不等平台原串/CER；JiWER v4.0.0 commit `19e88eae1815e7ca40db9b45b14af5f1f9d8b6ce`实读process/transforms和CER/空参考/error-count测试，默认Strip和空参考约定不直接采用。Apache-2.0；Python/click/rapidfuzz依赖未引入。

RapidFuzz v3.9.7 commit `cb960f940f90e55c84f5f2b30eea8bc9132f6515`实读Levenshtein_py一般DP/bit-vector/normalized分母、Unicode/editops测试、MIT许可和构建声明；只可作固定离线对照及优化参考，不代表原Paddle实际依赖版本或.NET接入已获资格。分数cutoff、未冻结tie和库默认归一化不能进入精确CER。HALCON算子索引未确认可直接承接完整单位/状态口径的接口；这不是全版本不存在此功能的断言，视觉识别仍优先HALCON。

.NET EnumerateRunes替换非法序列，严格入口需逐项检查DecodeFromUtf16状态；有效scalar不等字素或字形位置。[有限设计核验](../../.work/ocr-text-metrics-study-20260929/method-checks.json)比较961个短串对的DP与显式编辑图，另核方向/tie、跨对象/空真值/Unicode等具名反例；未执行上游库、C#/OCR、模型或工业数据。两轮raw下载失败原记录保持，后从同一固定commit的GitHub官方API取得字节，未重标失败或下载模型。


<a id="ocr-geometry-tiling-source-research"></a>
## OCR外部几何、有效支持与分块研究 — 2026-09-29

[021A §16](../shared-modules/guidance/03-vision/DEV-VIS-021A_OCR与DeepOCR独立能力开发指导.md#ocr-external-geometry-tiling-method)的方法、实际来源/读段及未验边界保存在[研究](../../.work/ocr-geometry-tiling-study-20260929/recommendation.md)、[source](../../.work/ocr-geometry-tiling-study-20260929/source.md)和[固定清单](../../.work/ocr-geometry-tiling-study-20260929/sources.json)，[独立研究审核](../../.work/ocr-geometry-tiling-independent-20260929/review.md)支持有限方法采纳。活动采纳/版本/差异另见[作者交付](../../.work/ocr-geometry-tiling-adoption-20260929/report.md)，不把研究独审当活动字节或生产接入已审。

复用HALCON官方Deep OCR模式/域与内置tiling、affine忽略domain及像素桥；新增官方crop_rectangle1越界domain、projective_trans_image插值/TransformDomain和±0.5例。官方URL版本只定位来源，平台依赖仍为AsunImage。输出domain、最近邻Mask和四角有效不能证明全插值足迹；未知alignment逆不按宽高或文本长度猜测。

PaddleOCR固定commit `b03f46425e8ff4442b268ce449e3eef758146cd4` 的common/processors.cc（Git blob `01164553863d0c6c74e58fce34d73f5392a61f9b`）实际quad→minAreaRect、浮点角/整数extent、cubic+BORDER_REPLICATE及竖词旋转；poly分支仍返回minRect，不能据注释称通用曲线展平。复读pipeline的方向/排序/过滤、有限test_ocr.py、CMake/pyproject及Apache-2.0许可；Paddle/OpenCV/Abseil/Clipper等依赖和PaddleX未固定全链不因单文件可读消失。只借鉴来源链/边界限制，不引入该裁图或IoU代码替代HALCON/020。

完整采样支持递推、严格Δ>4ε的有资格单词子集、core负责范围、完整冲突组件与一次恢复外围关系均有有限数学/反例；完整目标图复用062。作者和独审算例不证明网络定位界、真实间距、halo或费用δ，也未运行HALCON/Paddle模型、上游测试、WPF或产品代码。原raw下载失败后使用固定GitHub tree/blob API取同commit字节；失败保留，不算成功来源。精确公开绑定、后端Golden及物理同样本资格继续按对应方法完成。


<a id="code-reading-evidence-source-research"></a>
## 条码原返回、质量与有限尝试的来源 — 2026-09-29

[021B唯一方法](../shared-modules/guidance/03-vision/DEV-VIS-021B_条码解码与印制质量独立能力开发指导.md#code-reading-evidence-method)采纳[CodeRead-Evidence-1研究](../../.work/code-reading-method-study-20260929/recommendation.md)，实际出处/读段在[source](../../.work/code-reading-method-study-20260929/source.md)、[sources](../../.work/code-reading-method-study-20260929/sources.json)及[固定交回](../../.work/code-reading-method-study-20260929/delivery.json)。HALCON官方资料支持码制/查询边界、成功/候选基数、raw层次/ECI、超时正常返回部分、模型结果寿命及按族的质量/特殊值；官方URL版本只定位原文，不重新固定平台底层版本。

固定ZXing-C++ v3.1.1 commit `287c85df6f961c8efbfb5ffd736cd9457b8b890e`实读Barcode/Content/ECI/StructuredAppend、Code128 FNC1、ReadBarcode集合行为及Content/ECI/Code128测试。bytes、bytesECI、HRI、猜测编码/空显示分别处理；内部去重/错误过滤不是全候选证明，合并便利函数的索引覆盖与shared_ptr别名风险不直接带入原证据。Apache-2.0，C++20/Threads及可选写码Zint/测试gtest等依赖按来源保留，未引入运行库或复制解码代码。

研究有限byte/tuple/状态/序列挑战不代表实际HALCON/ZXing/标准件执行。质量软件返回、原图及完整成像/标准资格分开；没有取得ISO/GS1/SEMI标准全文，不能编完整DPM流程或宣称认证。增强/重试不得择最高级，重新成像只沿原采集尝试/来源，生产身份和检测尝试仍由原Owner决定。实际公共封送、模型读回、真实码图、资源/WPF/工业对标均另验。

<a id="gs1-content-source-research"></a>
## GS1字段语法、词典与内容解释来源 — 2026-09-29

[037方法](../shared-modules/packages/PKG-037_Identity.md#gs1-content-parsing-method)来源为[固定研究](../../.work/gs1-content-method-study-20260929/recommendation.md)、[实读范围](../../.work/gs1-content-method-study-20260929/source.md)和[逐件来源](../../.work/gs1-content-method-study-20260929/sources.json)，[研究独审](../../.work/gs1-content-method-independent-20260929/review.md)限定通过。Engine commit `70c1b162812ef8964cf8d4f28507a1b699cb934f`与Dictionary commit `c63d8a12210dd0cfaceac4aae45ccf57b48eb15b`分别固定；Engine配套词典2026-01-27与独立UNSET词典内容/规则不同，不能混成同一发布版。

实际源码/测试支持有限AIM/GS表示、定长与需分隔区别、重复/req、校验位/日期精度、DL分组件一次解码、true普通串、错误/旧输出及额外内嵌fallback。优先研究直接复用官方C语法引擎及包装，避免另写GS1 parser；HALCON继续负责视觉读码，内容语法不代身份可信和质量。公开HRI输出没有逐AI原byte位置合同，未知映射只引用整观察。

两仓库Apache-2.0，固定包装为net8.0/Version1.4.1、本地native且csproj无PackageReference；静态构建信息不证明.NET10可直接投产。实际引入/分发需保留适用许可/归属/NOTICE及修改说明，完整依赖/ABI/原生加载与部署仍待具体采纳；不把软件许可解释成号码分配或商标授权。当前未引入运行库、未编译或执行上游native/.NET测试、真实扫码、WPF或标准认证；有限算术/字符串反例与源码核对仅支持研究边界。


<a id="variation-inspection-source-research"></a>
## 良品变化模型的统计、支持与资产来源 — 2026-09-29

[026方法](../shared-modules/guidance/03-vision/DEV-VIS-026_2D分割、Blob与缺陷候选开发指导.md#variation-inspection-method)来源于[固定研究](../../.work/variation-inspection-method-study-20260929/recommendation.md)、[实读范围](../../.work/variation-inspection-method-study-20260929/source.md)及[来源字节](../../.work/variation-inspection-method-study-20260929/sources.json)。[研究独审](../../.work/variation-inspection-method-independent-20260929/review.md)限定接收并要求澄清应用编排与D/I/R；[活动采纳独审](../../.work/variation-inspection-adoption-independent-20260929/review.md)另核实际指导，二者不冒原生验证。

HALCON官方create/train/prepare/direct/compare/ext/get/threshold/clear/read/write共12页及实际SVG公式支持模式差异、max(A,Bv)、严格上下界、亮暗顺序和模型生命周期。资料URL版本仅为出处，平台仍使用AsunImage。standard的ddof、MAD精确缩放/偶数median、内部量化与任意缺失域未由所读页证明；采用官方算子和完整R基线，不自写默认NumPy统计冒原生等价。

固定SciPy v1.16.2 commit `b1296b9b4393e251511fe8fdd3e58c22a1124899`实读median_abs_deviation和实际测试、LICENSE/pyproject；固定NumPy v2.3.3 commit `f2a77a76e08719556527e0819182073fe9b5f1c3`实读_var/_std、TestStats、LICENSE/pyproject。两者BSD-3-Clause，只借鉴统计定义/退化及批合并陷阱，不引入Python运行依赖。SciPy按已存tree绑定，NumPy只绑定四个contents/blob，未取得完整tree；test_ddof内_var循环无直接断言的限制保留，不用测试名夸大证明力。

作者与独审的有限算术/支持/分块反例分别保留，未执行HALCON、真实模型、SciPy/NumPy上游套件、WPF或工业对标。原NumPy全tree下载失败记录不改写；官方公式渲染仅为阅读原件。固定印刷与OCR/身份/位置、模型文件与用途资格分开，后续公开适配、真实样本和同内容fresh读取仍须实际验证。


<a id="edges2d-association-source-research"></a>
## 有向边对、轮廓与Metrology来源 — 2026-09-29

[025 §7方法](../shared-modules/guidance/03-vision/DEV-VIS-025_2D边缘、轮廓与几何特征开发指导.md#edges2d-association-method)基于[固定研究](../../.work/edges2d-association-method-study-20260929/recommendation.md)、[实读范围](../../.work/edges2d-association-method-study-20260929/source.md)和[原件hash](../../.work/edges2d-association-method-study-20260929/sources.json)。[原研究独审](../../.work/edges2d-association-method-independent-20260929/review.md)发现P2：measure_pairs不返回未配对单边；[活动采纳独审](../../.work/edges2d-association-adoption-independent-20260929/review.md)另审修正字节，不能把原研究重标为无问题通过。

HALCON官方measure_pos/pairs、projection、分段/拟合、轮廓属性及Metrology的说明/参数与三处实际公式支持有向幅值、pair选择、类型/基数、原采样与模型的差别。info_edges的5%宽度不证明真实有限支撑；完整profile及端点误差资格分开。measure_pairs all只返回完整对；Metrology找边点无法对应测区，实例顺序任意且数量上限不证明穷尽，模型轮廓仍是image坐标。官方URL版本只定位出处，不改变AsunImage平台基线。

复用固定scikit-image commit `533b7694d2004ae84e49e2cfd0bcfc5f8e562f22`，本轮增读LineModelND/RANSAC及实际测试，CircleModel只定向复核。借鉴正交残差、归一化、有效性回调、有限随机搜索与退化挑战；其两点重合、最终全内点重估后未更新mask及invalid仅warn的边界不能直接复制为成功规则。测试中数值索引的`outlier not in inliers`只检布尔容器成员，不能证明索引处False；其它测试仍按实际断言范围使用，不否定整套实现。

已读对应源码/测试的BSD-3许可与pyproject依赖片段；本任务不引入Python/NumPy/SciPy生产依赖，不以RANSAC同名推与HALCON等价，也不重写现有视觉库。有限列表/几何/语言反例只用于方法审核，未执行native、上游套件、真实图像/world读回、WPF或工业精度/性能。公开签名、端点/采样映射、实际坐标语义与资源仍需后续真实验证。


<a id="localization-scope-source-research"></a>
## 独立语言上下文、资源来源与编辑保持 — 2026-09-29

完整方法唯一见[040 §13](<../shared-modules/guidance/05-ui/DEV-UI-040_WPF+DevExpress Design System开发指导.md#localization-scope-method>)，来源为[固定研究](../../.work/localization-method-study-20260929/recommendation.md)、[实读范围](../../.work/localization-method-study-20260929/source.md)及[原件指纹](../../.work/localization-method-study-20260929/sources.json)。[原研究独审](../../.work/localization-method-independent-20260929/review.md)的P2是同Dispatcher同步回调卡住时无法保证B呈现继续；[活动采纳独审](../../.work/localization-method-adoption-independent-20260929/review.md)另核修正字节，原研究和发现保持原结论。

.NET/runtime v10.0.0 commit `60629d14374c56f1cb51819049ad1fa529307f8d`固定ResourceManager/ResourceFallbackManager、CultureInfo、CompositeFormat及相关实际测试；WPF v10.0.0 commit `72ca82c7a0f57eb8d0168246468b9cc1a6c14a5a`固定Language与BindingExpression相关源码。父链缓存别名说明tryParents=false不足以证明精确语言，MinimumArgumentCount不证明必需占位齐全，异步传播文化不等宿主隔离，UsesLanguage更新不证明编辑缓冲保持。复用.NET已有资源/格式能力，补明确来源与受限调用，不复制运行库或新建平行格式引擎。

DevExpress来源为既定25.2随附公开XML与官方示例commit `970e87163f05239023b1e786d862d98eee694338`；示例实际net8/24.2只作单窗口/静态入口反例，不迁其依赖。RuntimeLocalizationStrings、LocalizationDescriptor与MaskCulture只证明各自有限公开能力，不证明完整每宿主弹窗及编辑行为。没有以Active/Culture/ContainerType猜宿主ID；没有扫描内部或核安装/授权。

原报告记录官方资料、实际源码/测试和许可/依赖范围；只据其固定已读内容使用，不把所有上游测试当执行过。后续具体公开入口见下段。D1–D5未自动批准；未执行资源包/平台.NET实现、WPF/字体/UIA/编辑/报告渲染或性能，研究URL/commit不决定平台补丁版本。

<a id="localization-public-surface-source"></a>
### Grid实例、SuperTip与编辑缓冲的公开入口补充

[040正式正文](<../shared-modules/guidance/05-ui/DEV-UI-040_WPF+DevExpress Design System开发指导.md#localization-public-surface-method>)吸收[来源与实读范围](../../.work/localization-public-surface-study-20260929/source.md)及[固定来源](../../.work/localization-public-surface-study-20260929/sources.json)。研究方法SHA为`eb47855f3a75d6f6a798b52c594d734b07cb26485313f4bd8f5b96d354dfccb8`。既定25.2.3公开XML与仅导出元数据确认集合/元素构造、属性读写权限、编辑事件及SuperTipControl；没有执行控件、读取方法体或查询内部成员，也未做依赖准入核验。官网403不解释为不支持。

官方Grid示例commit `b0ee49c5c8c9bb9ad01520ecdbebcb83bb96f62e`实际代码是创建新集合再赋给view，项目为net8/24.2；官方SuperTip历史commit `0c534a44e832d2e3af6bbf9defb82ab23e28e7b4`以SuperTipControl承载到标准控件ToolTip，项目为net6/22.2。两例源码/XAML、项目及许可文本已读，按目标公开签名另核；只借公开用法，不导入示例依赖，不把as-is/EULA指向误记MIT，也不把旧例冒充目标运行测试。固定tree未见相应行为测试。微软TextCompositionManager/TextInput/AddHandler资料仅支持有限事件观察，不证明所有IME取消/失焦的完整终止协议。

限定采入的是每视图登记集合、自有实例内容及独立字符串草稿步骤；后续供应商模板raw方法见下段，实际槽位角色/文化、完整原生弹窗、Grid原位编辑与IME变体继续明确未决。主区赋值不证明子弹窗热更新，三语示意不代真实WPF/UIA/DPI。独立只读审核未发现确定P1/P2，审核身份和活动接收记录在项目进度，不为本轮新增审计脚本或重复报告。

[040原模板方法](<../shared-modules/guidance/05-ui/DEV-UI-040_WPF+DevExpress Design System开发指导.md#localization-native-template-method>)补快照/用途/raw校验及逐区域回执。补充只保存完整公开member的两份XML：[SummaryItemBase重载](../../.work/localization-public-surface-study-20260929/followup-sources/DevExpress.Xpf.Grid.v25.2.Core.xml.followup-excerpt.xml) SHA `30cbfd7b505e3d095cd35dce8e1c031e180a91385d6100e124f00500b0a5e4ec`，完整源SHA `9ca164e53a54e5bc0eb6432a709e95c9295e60db3b0eac4fabf6dd32604b8eba`；[七项菜单名称](../../.work/localization-public-surface-study-20260929/followup-sources/DevExpress.Xpf.Grid.v25.2.xml.followup-excerpt.xml) SHA `ea9db4630e8a0b9521fedcdd7948be1503cfa7a9c42416009e1b86b190d4fa0b`，完整源SHA `7537e3db16162155eda70058baccf40a6731f6dc9851ad31d382332c39c3d6bd`。源为既定25.2公开XML；原摘录已有的模板ID没有重复复制。两个InSameColumn族槽位不同，Get*DisplayText显式provider不证明Grid实际文化/参数映射，setter异常不证明回滚；这些限制直接写入指导。未读取内部实现、执行WPF或核依赖准入。

<a id="reference-surface-method-source"></a>
## 正交参考平面、轴向回归与有限二阶曲面 — 2026-09-29

[028方法](../shared-modules/guidance/03-vision/DEV-VIS-028_3D对象模型、配准与表面分析开发指导.md#reference-surface-method)及[031有限signed积分](../shared-modules/guidance/04-metrology/DEV-MET-031_通用计量引擎开发指导.md#quadratic-reference-signed-integral)使用[实读范围](../../.work/reference-surface-method-study-20260929/source.md)和[固定来源](../../.work/reference-surface-method-study-20260929/sources.json)。原研究SHA `4f91a8f8474c4aa5f5e276522b771234923dfa6b38b14e73626f9b0540aa2d7c`；独审指出消费者§9高度方向与面积元未成对的P2，活动指导修正不回写原研究为无问题。

直接读取HALCON primitive、surface一/二阶拟合与生成、matrix创建/SVD/求解/释放原文及实际SVG公式。plane不同拟合算法同结果不证明Tukey已剔点；灰度回归忽略图像domain、Region中心和row/column次序、plane常数符号及SVD截断各按真实语义。文档版本只为出处，平台仍通过AsunImage公共能力；未核到的ImageLibDotNet签名不编造，没有native执行。

固定Open3D `b6c5e196384ad71e75b6e6f9c5da22d046221f1d`实读PointCloudSegmentation.cpp及PointCloud.cpp真实测试、MIT和CMake：候选/原索引分离可借鉴，但最大余子式不普遍等于正交TLS、旧面内点后的refit必须重核。固定NumPy `0532af47d6a815298b7841de00bdbc547104b237`实读polyutils._fit、polynomial.polyfit及真实恢复/权重/RankWarning测试、BSD-3-Clause与构建声明：列范数缩放/秩诊断可借鉴，不提供二维物理板弯或孔洞资格。仅研究用法与数学，不引入上述生产运行时；真实复用仍保留各许可/归属要求。

作者15项合成检查与独立29/300有理反算仅验证有限数学，不代表固定上游套件、HALCON、两宿主、WPF、标准件或工业性能通过。原研究P2的倾斜例在正式消费者明确为n_z=.8、Z差.2、法向域2时体积.32；Q仍需用途和完整下游方法采纳。没有为登记本批新增检查或写入脚本。

[031二阶有界归约](../shared-modules/guidance/04-metrology/DEV-MET-031_通用计量引擎开发指导.md#quadratic-reference-bounded-reduction)补六系数/上下仿射界/确定细分、正负积分、CDF/左逆和端点、精确算术与全域预算。固定[dhermes/bezier源码](../../.work/reference-surface-method-study-20260929/extension-sources/bezier/src/python/bezier/hazmat/triangle_helpers.py) commit `cf18953a491e8568e4a4344327ed441d3e8956da`、SHA `11b45dbc287ffedd6960a8fcca93ddb22ccb5cd3f05e48868ef1aad5421bd378`；[真实测试](../../.work/reference-surface-method-study-20260929/extension-sources/bezier/tests/unit/hazmat/test_triangle_helpers.py) SHA `9e95fca7434f76a7336548f6c210e24e33367f8bb8729a6a55ede6a837137484`。实读矩阵49–104、polynomial_sign705–777、de Casteljau约895–958、subdivide_nodes1105–1182及相关测试；凸组合/四分可借鉴，float符号与文档重复lambda2不得照抄。Apache-2.0、Python/NumPy/setuptools及可选扩展声明已读，未引入产品运行时或执行上游测试。

四份[HALCON原件](../../.work/reference-surface-method-study-20260929/extension-sources/halcon/)核平面体积、一维积分、灰度直方图和阈值的输入/输出范围；不以名字推二阶连续域严格包络。作者与独审仅在终端作有限有理反算，支持5/192、CDF(0)=3/4、混合曲率四分缩率等；算法全式和异常已回正式031，不要求程序员读脚本补需求。数值证书限存储模型，材料/光学/真实资源/位长性能、WPF及工艺资格仍须验证。
