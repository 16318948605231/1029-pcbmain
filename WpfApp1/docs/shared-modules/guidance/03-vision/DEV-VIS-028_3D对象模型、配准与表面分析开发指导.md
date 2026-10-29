# 3D对象模型、配准与表面分析应用映射

- 文档 ID：`DEV-VIS-028`
- 版本：`1.4.0-map`
- 状态：`DocMapped`
- 本页保留历史文档 ID、应用导航和迁移锚点；契约、算法、参数、状态、工程与准入均由对应独立模块唯一维护。

## 唯一实施权威

| 能力 | 唯一模块指导 | 宿主组合边界 |
|---|---|---|
| 表面快照、有效性、源索引、派生版本 | [IM-031 surface-data](../../../independent-modules/surface-data/DEVELOPMENT-GUIDE.md) | 宿主提供不可变输入及版本/hash |
| 重建、结构光和多方向融合 | [IM-032 reconstruction-3d](../../../independent-modules/reconstruction-3d/DEVELOPMENT-GUIDE.md) | 宿主选择采集结果、用途和发布时机 |
| 双/多表面配准、位姿、图质量 | [IM-033 registration-3d](../../../independent-modules/registration-3d/DEVELOPMENT-GUIDE.md) | 宿主提供配准支撑和Profile |
| 单表面采样、法向、primitive、拓扑与距离 | [IM-034 surface-features-3d](../../../independent-modules/surface-features-3d/DEVELOPMENT-GUIDE.md) | 不隐含配准或计量 |
| 参考面、板弯补偿和适用域资格 | [IM-035 reference-surface](../../../independent-modules/reference-surface/DEVELOPMENT-GUIDE.md) | 宿主声明物理参考、独立检查域和下游用途 |
| 2D/3D 具名量值、关系与数值归约 | [IM-036 metrology](../../../independent-modules/metrology/DEVELOPMENT-GUIDE.md) | 质量放行仍归产品 Owner |

旧包映射：[PKG-027](../../packages/PKG-027_SurfaceData.md)、[PKG-028](../../packages/PKG-028_Reconstruction.md)、[PKG-029](../../packages/PKG-029_ReferenceSurface.md)、[PKG-030](../../packages/PKG-030_Metrology.md)、[PKG-031](../../packages/PKG-031_Features3D.md)、[PKG-060](../../packages/PKG-060_Registration3D.md)。包页只保留应用导航，不新增公共类型或第二算法。

## 宿主调用与产品责任

宿主冻结输入及用途 → 映射为模块公开快照与参数 → 调用所选独立模块 → 核对支持、版本和资源回执 → 交给下一模块或产品事实 Owner。业务调用顺序、工艺解释和提交由宿主实现。模块之间只经公开契约交换，不读对方内部，不共享可变 native 工作模型，不依赖产品页面、数据库表或静态当前实例。

定位采样、显示 LOD 与计量支撑分别绑定。参考拟合由 IM-035 完成，具名量值由 IM-036 完成；产品不能通过自由拟合被测对象、改变参考域或删去失败点，使应检偏差消失。真实输入/物理参考、可观测性、原点索引、孔洞及未知域按各模块指导检验；非空模型、低残差或平滑显示不能证明计量资格。

所有视觉算子经项目 `ImageLibDotNet.cv2` 使用 HALCON 26.05，语义以[本地算子手册](../../../../halcon算子手册/operators/)为准。历史 AOI、AsunMeasure、开源实现及旧版本手册只作来源，不定义当前 API 或生产参数。

## 迁移锚点

<a id="surface-processing-registration"></a>
### 表面处理与配准

数据使用 IM-031，单表面处理使用 IM-034，位姿估计使用 IM-033，参考资格使用 IM-035，计量使用 IM-036。详细输入、算法、Owner与测试分别读取上述唯一指导；本页不提供可直接编码的算法。

<a id="registration-observability"></a>
### 配准质量与可观测性

变换方向、支撑、覆盖、闭环、独立检查和图质量只见[IM-033 §7](../../../independent-modules/registration-3d/DEVELOPMENT-GUIDE.md#7-处理路线与质量门)。本锚点不解释 native score 或另设残差阈值。

<a id="reference-surface-method"></a>
### 参考面方法

P/H/Q 方法、支撑、适用域、板弯补偿与重开只见[IM-035 §6](../../../independent-modules/reference-surface/DEVELOPMENT-GUIDE.md#6-算法实施语义)。量值及积分消费见[IM-036 §12/19](../../../independent-modules/metrology/DEVELOPMENT-GUIDE.md#12-逐量测定义支撑域与解析断言)；DEV-MET-031仅导航，未绑定公开API的扩展不从本页获得实施准入。

## 准入与参考资料

按[DEV-GOV-010](../../../01-governance/DEV-GOV-010_实施级规格唯一标准.md)逐切片接收。Core、发布Simulator、HALCON适配、WPF、宿主集成和现场资格分别判断。文档映射不代表代码、性能、Golden、HIL或计量验收通过。

来源导航仍见[REF-002](../../../references/REF-002_GitHub_DevExpress与OpenSource研究基线.md#surface-source-research)及[REF-008](../../../references/REF-008_PCBA-AOI指导副本与平台采纳映射.md#surface-adoption)。保留原件/hash和真实研究范围；修改方案只在受影响模块唯一指导完成。
