# 3D HeightField与重建开发指导

- 文档 ID：`DEV-VIS-027`；版本：`1.3.0-map`；状态：`DocMapped`
- 适用范围：高度场、结构光、立体、多方向输入的应用消费映射。
- 直接依赖：`DEV-GOV-006`、`DEV-GOV-008`。
- 唯一实施权威：[IM-031 surface-data](../../../independent-modules/surface-data/DEVELOPMENT-GUIDE.md) 与 [IM-032 reconstruction-3d](../../../independent-modules/reconstruction-3d/DEVELOPMENT-GUIDE.md)。本页保留原ID、功能索引和应用入口，不定义第三套算法或契约。

## 统一实施规则

应用先冻结用途、输入完整性、attempt/epoch、标定/图案/资格Profile、坐标及资源，再调用对应独立模块。IM-031负责描述、布局、有效性、来源、坐标交接和有界读取；IM-032负责重建、方向质量、一次变换、共同支持与融合；图案生成/投影归[IM-011](../../../independent-modules/structured-light/DEVELOPMENT-GUIDE.md)。产品Schema与State/Owner映射由对应Owner采纳，UI/报告/AI只投影或编排。

## 1. 通用算法选择流程

实现按各模块唯一指导的模式/输入确定路线，不由宿主运行时任选“默认算法”或fallback。新的算法候选先按DEV-GOV-006及既有决策规则研究/同样本比较，再修订唯一指导和Profile，不以新方案覆盖历史事实。

## 2. HALCON 使用规则

AsunImage / HALCON 26.05经`ImageLibDotNet.cv2`适配端口调用。算子顺序、参数、封送与资源Owner唯一在模块指导；产品领域不持native句柄，不重复核验封装算子存在性。手册入口：[HALCON 26.05 operators](../../../../halcon算子手册/operators/)。

## 3. 鲁棒性要求

缺帧、乱序、跨attempt、过期资产、不可观测表面、单位/坐标不一致与来源缺失显式拒绝或保留候选/未验证状态，不用零值、显示网格或AI填齐。真实材料与计量Profile按消费者用途验收；源有效域、插值/显示、冲突和不确定度分开。

## 4. 性能要求

资源计划、阶段测点、P50/P95/P99与有限测试期限唯一见IM-031 §11、IM-032 §14及DEV-GOV-010。模块已冻结全尺寸ROI/禁止自动tile的路线时，宿主不得套通用降采样/金字塔建议改变测量语义；Viewport显示LOD不回写算法输入。没有客户目标不编造节拍或性能达标值。

## 实施级关联功能

FS-012/FS-013保留应用功能索引；独立模块公共输入/参数/输出/错误、算法、生命周期与测试继续定位到IM-031/IM-032，产品提交及工艺判定留对应FunctionSpec/Contract/Owner。映射不授代码、集成或生产资格。

<a id="structured-light-closure"></a>
## 5. 结构光重建与高度输入的可实现边界

激光/设备已提供HeightField时通过IM-031接入；原始结构光或立体输入由IM-032处理；宿主组合采集、标定、投影与重建，不复制公共算法。SPI消费条件见[055A](../../../process-guides/guidance/06-domains/DEV-DOM-055A_SPI%203D%20Acquisition与HeightField质量开发指导.md#spi-acquisition-method)。

结构光non-specular前提、共同标定、曝光/图案稳定窗和实际材料可观测性须成立；多方向和AI不能自动解除这些条件。方向变换由registration-3d发布的不可变快照消费一次，融合只在共同支持/贡献门满足时发生，保留原始来源、冲突和无效域。缺可靠不确定度保持未知，不以零高度当空点。

宿主关闭、等待超时与取消不能提前归还在途输入/模型；未确认排空仍持原Owner。可选UI、迟到回执、有限预算、测试与切片准入按唯一模块指导。真实HALCON/WPF、Golden、计量、性能、HIL和现场验收未因本映射完成而通过；研究来源继续保留在既有REF-008清单。
