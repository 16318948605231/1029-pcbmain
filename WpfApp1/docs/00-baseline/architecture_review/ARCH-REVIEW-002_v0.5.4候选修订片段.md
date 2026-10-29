# ARCH v0.5.4 候选修订片段
- 文档 ID：`ARCH-REVIEW-002`
- 版本：`1.0.0-prep`
- 状态：`Reference`
- 架构基线：`ARCH-PCBA-VISION-001 v0.5.3`
- 适用范围：只针对 v0.5.3 已识别 P1 的最小改动
- 直接依赖：`ARCH-REVIEW-001`
- 主要输出：可直接合并到架构的候选措辞

>
本文均以 `ARCH-PCBA-VISION-001 v0.5.3` 为架构输入。该架构当前仍为候选基线/DocMapped，未因本开发准备包而自动获得架构批准或生产资格。若本包与未来获批架构、既有权威 Schema、状态/Owner 规范或实际仓库实现冲突，以获批权威资产为准，并必须登记冲突后再实现。


## 候选措辞

> `BoardModel` 是 `BoardDataAdapter` 用于多来源制造设计数据标准化的中间模型/契约，不作为生产批准后的制造参考主数据；`ManufacturingGeometrySnapshot` 是经过 SourceSet 验证、冲突解决和批准绑定的生产制造参考快照，必须引用对应 `BoardModel` 的精确 `id/version/hash` 以及来源、验证和批准证据。Snapshot 不复制第二套几何语义；需要读取标准化几何时通过绑定的 BoardModel 版本回放。

此片段为候选修订，不自动替换原架构文件。
## 3. 强制禁止直接实现

本文件仅为架构候选修订片段。AI/开发人员不得因为看到 v0.5.4 字样而直接把其内容当作当前架构；任何实现必须回到 `ARCH-PCBA-VISION-001 v0.5.3` 与当前 `ARCH-REVIEW-004` 实施绑定。

> **AI使用警告：** 本文不是正式架构批准凭证；实施语义以当前 `ARCH-REVIEW-004` 绑定与活动 Registry/Manifest 为准。
