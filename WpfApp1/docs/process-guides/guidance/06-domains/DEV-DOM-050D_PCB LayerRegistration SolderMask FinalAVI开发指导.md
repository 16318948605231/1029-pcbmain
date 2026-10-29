# PCB LayerRegistration SolderMask FinalAVI开发指导

> 2026-09-27 平台归位：当前职责与范围按[平台设计基线](<../../../00-baseline/PLATFORM-DESIGN-BASELINE.md>)及[所属指导目录](<../../README.md>)绑定。本页保留原ID与细化内容；原状态 `ImplementationSpecificationReady` 仅作历史记录，精确契约/Owner/参数未获批前不作为生产实施准入。
- 文档 ID：`DEV-DOM-050D`
- 版本：`1.1.0-prep`
- 状态：`DesignReview`
- 架构基线：`ARCH-PCBA-VISION-001 v0.5.3`
- 适用范围：层间对准、阻焊与成品 AVI
- 直接依赖：`DEV-DOM-050`; `DEV-DOM-050A`; `DEV-VIS-023`
- 主要输出：层间偏差、阻焊缺陷、Final AVI 事实

> 本文以 `ARCH-PCBA-VISION-001 v0.5.3` 为架构输入。未提供给本任务的真实仓库 Contract/Schema、实际 DevExpress 版本、HALCON 安装、实机与资格证据不会被虚构。

## 实施规则

- 领域负责语义；平台负责稳定技术能力；UI 不成为事实权威。
- 算法必须提供默认路径、Fallback、拒识和质量评分。
- 所有生产相关参数都必须可版本化、可回放、可审计。
- 大图/3D 优先 ROI、Tile/Pyramid/LOD、分层计算；先低成本候选，再高成本精测。
- 任何“自动优化”必须输出 Draft/Proposal，不得静默修改生产权威。

## 验收最小集

正常样本、边界样本、难例/污染样本、拒识样本；P50/P95/P99；失败/恢复；回放一致性；UI Automation；证据闭环。
## Layer Registration

建立多参考点/区域的约束模型，输出刚体/必要时低自由度变换、残差分布和最差位置。不得只用单个 Mark 的偏差作为全板 registration 结论。

## Solder Mask / Final AVI

阻焊与成品外观要区分“几何违规”和“视觉外观候选”。Final AVI 支持按缺陷分类、严重度、证据和 Review 路由，而不是直接用图像相似度给最终处置。

## 测试与验收

- 正常、边界、难例/污染、拒识样本；
- Replay 前后结果差异可解释；
- 关键参数变更触发必要回归；
- 失败/取消/恢复路径有证据。

## 性能

必须记录典型耗时、P95/P99、峰值内存、并发条件和数据规模；大图/3D 必须标明 ROI、分辨率和中间结果生命周期。

## 禁止实现

不得将领域专有对象降格为通用对象；不得绕过 Contract/Owner；不得将拒识/不可观察状态静默转换为 OK；不得用 AI/经验值修改生产权威。


## 实施级关联功能

本指导的具体功能以以下实施规范为准：FS-026, FS-027, FS-028。每个 FS-xxx 都包含输入/输出、算法、鲁棒性、性能、UI、测试、验收和禁止实现。


## 当前唯一实施正文与调用边界

阻焊逐方法以[PG-006 §16](../../processes/PG-006_soldermask-legend.md#mask-method-implementation)为唯一细化：材料M/N/Q、处理支撑、开窗/桥对应、原法向余量和套位、截断/未知、跨tile与恢复；FS-027绑定其无副作用端口。终检以[PG-011](../../processes/PG-011_final-avi.md#avi-coverage-pairing)及FS-028定义必检全集、明确双面选择、板面/支撑与翘曲；终检消费原子结果，不重建相同阻焊、钻孔或原始蚀刻算法。层间注册仍由FS-026及PG-004的专属工艺定义。

公共区域/边缘/计量分别复用025、021和030；生产身份/程序/执行/评价/证据沿037→035→038→039→040，复判/放行不属于上述计算端口。本页是跨功能领域边界，方法和UI细节在其唯一PG/PageContract继续深化，不复制第二套数学正文或Schema。整体仍为DesignReview，历史模板不授予全量编码或工业资格。
