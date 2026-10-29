# 特征量测的产品接入映射

- 文档 ID：`FS-017`
- 类型：`Function Implementation Specification`
- 版本：`2.0.0-map`
- 状态：`DocMapped`
- 对应开发指导：[IM-036 metrology](../../../independent-modules/metrology/DEVELOPMENT-GUIDE.md)
- 领域：`Metrology`

本页定义宿主如何消费独立计量模块并形成产品量测事实，不定义第二套计量算法、公共 DLL、DTO 或状态机。[DEV-MET-031](../04-metrology/DEV-MET-031_通用计量引擎开发指导.md)只保留应用导航及迁移锚点。旧实施模板、端口名和工程摘要不构成新模块契约；模块代码按 IM-036 的唯一工程/API/测试准入实施。

## 1. 功能目标与边界

宿主把目标/方法/几何及采集证据映射为 IM-036 请求，消费具名量值与有效性，按产品定义组合 MeasurementQuality、FeatureMeasurement 和 MeasurementSet。Raw、Canonical、Display 分开；Display 的舍入、语言、图表或缩放不参与计算和规则比较。

模块不拥有生产事实、Required、公差、guard band、最终处置或设备命令。宿主保持原 Producer/StateOwner/CommitOwner，事实提交只经原授权路径。缺字段或 Owner 的产品映射保持 PreparationIncomplete，不阻断已接收的独立 Core 规格。

## 2. 权威与契约

| 边界 | 唯一来源 / 接入要求 |
|---|---|
| 独立基础 API、输入/方法/量值 | [IM-036 §11–15](../../../independent-modules/metrology/DEVELOPMENT-GUIDE.md#11-目标-v02-公开契约asunmetrologycontracts) |
| 连续输入、支持域、结果与数值界 | [IM-036 §19.2–19.8](../../../independent-modules/metrology/DEVELOPMENT-GUIDE.md#192-强类型输入参数与结果asunmetrologycontracts全部字段) |
| 模块事件、重复/取消/关闭及资源 | IM-036 §14/16.3/19.3；原身份/原 Task/真实归还证据，不复制 Runtime |
| 产品持久/传输 Schema、质量及用途 | 受影响 C-01～C-08、原 State/Owner、PG 方法与批准 Profile |
| UI | [UI-PCS-006](../14-page-contracts/UI-PCS-006_Metrology_Workspace.md) 的产品投影；可复用工作台沿 [IM-065](../../../independent-modules/measurement-workbench/DEVELOPMENT-GUIDE.md) |

模块 AssetRef/OperationKey 不能自动当产品 FactId/CommitIdentity/BoardIdentity。宿主映射必须保留原关联及版本/hash、frame、单位、方法、scope、支持、误差与 Evidence；不靠列表行号或 latest 关联异步结果。物理量的目标、公差和资格从产品批准输入取得，不由模块默认或 AI 推断。

## 3. 输入前置检查

宿主先冻结板/面/目标/尝试、被测量定义、参考/方向/有限域、Operand/Pairing、方法/profile 版本、坐标与单位及预算，再取得不可变证据。各模块 reader 核各自公开回执/内容身份；宿主额外核产品用途、Required、材料与资格，不把调用者 bool 当证明。

错板/错面、错修订/hash/frame、无端部/材料/全单元支持、方法不适用、资格撤销或未给有限预算须显式拒绝或不可评价。非空模型、低残差、Applied、Measured 和拼接连续均不能自动通过产品质量门。

## 4. 正常执行流程

1. 产品按 PG/FeatureDefinition 选择具名量，冻结原目标/方法及预算，不临时换成更容易通过的定义。
2. 宿主取得 frame/ROI/坐标/表面/参考证据；图像或 3D 特征提取用其所属模块，计量器不重建产品识别流程。
3. 映射为 IM-036 基础或连续请求；未知版本拒绝，旧身份/hash 保持原规则。
4. 调用唯一公开入口；保存原 Task/identity/source，消费每项值、支持、误差、部分域、数值停止与错误。
5. 原产品规则 Owner 核用途/质量/Required/完整性/公差与 guard band；输出量测事实或明确未评价，不把未知改为 OK。
6. 用原 CommitIdentity 提交并对账；UI/报表/统计投影已提交或明确候选的结果，不再计算第二份量值。

## 5. 算法与参数映射

| 请求族 | 唯一实现定义 |
|---|---|
| 距离、角度、尺寸、离散面积与视觉桥 | [IM-036 §12–13](../../../independent-modules/metrology/DEVELOPMENT-GUIDE.md#12-逐量测定义支撑域与解析断言) |
| 截面、方向剖面、轴端/指定截面、有限层面 | [IM-036 §19.4](../../../independent-modules/metrology/DEVELOPMENT-GUIDE.md#194-连续截面沿程轴与有限层面计算c1) |
| D/F/B/Us/Uh、有效域积分、连续矩/中心 | [IM-036 §19.5](../../../independent-modules/metrology/DEVELOPMENT-GUIDE.md#195-dfbusuh共同分片线性积分和矩c2) |
| 连续面积 CDF/左逆及 Q 归约 | [IM-036 §19.6–19.8](../../../independent-modules/metrology/DEVELOPMENT-GUIDE.md#196-连续面积cdf原子与左逆c3) |

边缘/拟合/距离/关系是功能导航分类，不是可任意选择的算法。实际参数、单位、数值预算和禁止组合只沿选定版本 Contract/Profile。替代方法必须已明确同一被测量的等价条件与用途资格；禁止静默更换插值、分母、面积权、参考、符号或缺项规则。自动建议只生成带范围/来源/版本的候选，由原宿主批准后形成新 Profile。

HALCON 行为按项目 [26.05 算子手册](../../../../halcon算子手册/operators/) 经 `ImageLibDotNet.cv2` 使用 AsunImage；已确定依赖不重复作安装、兼容或授权审查。

## 6. 并发、取消与恢复

模块计算与产品提交分别恢复。模块取消请求不证明退出，先核原 Runtime/lease 回执再归还；未决 Close/Dispose/端口任务仍由进程根 Owner 持有。两个消费者注入独立实例/预算/取消源，不读静态当前窗口。晚到旧结果只归原身份，不能覆盖新参数/参考修订。

重新计算采用新计算身份；重试事实提交用原 CommitIdentity，先查原回执，不隐形重算或新建重复事实。重启依原快照/回执/版本恢复；不能从 latest 猜运行状态。UI 关闭只结束投影，不回滚已提交事实，也不停止无关共享执行。

## 7. 结果、误差与产品质量

模块的数值包络、拟合质量、计算有效性、物理不确定度、工艺接受、持久提交分别保留。存储模型精确归约/向外舍入不能冒充计量标准件、MSA 或置信区间；RMS 和重复点数也不能给未知材料/高度域证明。

每个 Required 目标有可关联值或明确缺项。有效子集极差、部分积分/中心/CDF 不自动替代全对象结果；公差比较只使用批准 Canonical 定义。DisplayValue、图表平滑及等效尺寸标签不改变事实。

## 8. 性能与资源

产品 Profile 为 `PF-FS-017`；模块负载/测点/预算沿 IM-036 §16.1/19.9 和 DEV-GOV-010 §3.1。产品接入另记录证据获取/映射、端到端计算、质量/完整性、提交及 UI 投影，不重复派一个 Task 给每个样点。

同样本统计 cold/warm P50/P95/P99、峰值 managed/native、队列/租约/来源数、失败/删失样本、取消至实际排空和长稳。无批准目标为 NotEvaluated；未排空或省略失败样本不能性能通过。模块 harness 的 10/120/180s 是测试保护，不是客户节拍。

## 9. UI 与操作

量值表/影像/参考/支持域联动由 UI-PCS-006 和 IM-065 规定。短自然三语显示目标、单位、质量及可执行恢复动作；高级参数渐进展开，关键停止常显。页面只发原 Host 命令/投影，禁止把显示纹理、行号、筛选后的分母或 LOD 输入量测。

真实 WPF 固定 1920×1080 验证，计入任务栏/边框；三语、DPI、键盘/UIA、迟到/关闭/错误与视觉品质分别验收。metrology 本身无 UI，不在其 Core 增页面或 DevExpress 依赖。

## 10. 注册绑定与代码边界

| Item | Binding |
|---|---|
| Function | `FS-017` / Feature measurement |
| Guide | `IM-036`（DEV-MET-031 为导航） |
| Project | `Asun.Metrology.Core` |
| Canonical port | `IFeatureMeasurementService` |
| UI PageContract | `UI-PCS-006` |
| Primary Work Package | `WP-08` |
| Performance gate | `P95 per measurement` |
| PerformanceProfile | `PF-FS-017` |

Project 保留注册表的计量核心定位，实际 Contracts/Core/Runtime/Halcon/测试工程以 IM-036 §10/16.1 为准。`IFeatureMeasurementService` 仅是历史产品门面候选名，未冻结产品合同前不得据此新建模块公开接口、放进 Asun.Metrology.Core 或复制 FeatureMeasurement DTO；独立服务用 IM-036 的 IMetrologyService/IContinuousMetrologyService。产品 facade 的实际落点及签名须在真实集成任务绑定，注册名不冒充已批准 API。

模块代码/测试只按 IM-036 所列路径及切片，产品映射只改明确批准的宿主范围。禁止更改其它模块内部、AsunImage、参考项目、私有制程判断或原事实 Owner。旧实现存在时先核消费者和测试，不以本映射自动迁移/解除引用。

## 11. 接入测试与可判定断言

独立算法与 Runtime 必需测试/完整编码 oracle 沿 IM-036 §16/19.3.1/19.9，不在本页复制测试实现。以下为产品接入额外断言：

| ID | 触发 | 必须断言 |
|---|---|---|
| T17-01 Contract/Schema | 错 frame/unit/hash/板面/修订、资格撤销 | 不调用不适用后端、不生成权威有效值，原目标/错误可读 |
| T17-02 正常/边界/缺项 | 同 3-4-5 几何分别在两消费者使用；Required 缺端部/支持 | 相同方法量值一致，工艺定义各自判断；缺项不默认为零/PASS |
| T17-03 Replay/版本 | 同证据/参数重放、新参考修订及旧迟到 | 可重现或有批准差异说明，旧值不覆盖新身份 |
| T17-04 故障/恢复 | 取消/超时/迟到/资源未知，提交回执丢失 | 原根/Task 持有，真实归还后才结束；提交按原 CommitIdentity 对账 |
| T17-05 性能 | 极限片/孔/来源/并发、cold/warm 与失败样本 | 预算限制与删失口径明确，全部目标实测后才 Qualified |
| T17-06 标准件 | 方法/基准/量程与代表件匹配 | 数值定义及物理误差分别核，不用合成解析向量替代 |
| T17-07 重复性/再现性 | 多设备/操作者/时段及相同输入 | 按批准设计采样/分析，物理资格不从 Core 测试推导 |
| T17-08 不确定度/用途 | 标定/温漂/边界/参考共同误差与部分域 | 按批准误差来源/用途资格，不以 RMS/sqrtN 隐去共同误差 |

必需断言失败/跳过/未完成/未知资源均不能报通过；真实 Golden/Replay、标准件、性能、HIL 和现场按受影响产品门执行。本轮只改文档，没有运行上述测试。

## 12. 点胶、涂覆与其它消费者

PG-016拥有点/路/结点/胶量及中心用途，PG-021拥有覆盖/膜厚/层对应，SPI拥有锡膏被测量与材料语义。共用截面/层关系沿 IM-036 §19.4，积分/矩沿 §19.5，连续面积分位/Q 沿 §19.6–19.8；各 PG 不复制公式/DTO，不把制程对象传入共享核心。

宿主通过公开 ROI/surface/reference/coordinate 端口映射真实支撑、域与版本，不把已接收托管规格当实际字段/资格已闭合。缺失的具体映射只阻断该接入；不撤销其它已接收 Core 切片。

## 13. 准入状态

按 [DEV-GOV-010](../../../01-governance/DEV-GOV-010_实施级规格唯一标准.md) 分别接收模块规格、产品合同/Owner 映射、实现、运行与生产资格。当前模块基础 M1/M2 和连续 C1–C4 已在 IM-036 的精确范围接收为 ModuleCoreImplementationReady，仅规格准备。本 FS 产品持久契约/用途/Owner、真实接入、WPF、Golden、性能及现场仍按实际证据关闭；本页不授 ImplementationSpecificationReady，不启动代码队列。

研究来源、算子/API 决定与固定原件/hash 复用 IM-036 §17/19.10 及 DEV-MET-031 来源导航；输入/版本/范围未变不重复全审。缺失或矛盾先在所属唯一指导修订，再继续受影响切片，不靠现场测试后临时改变被测量。
