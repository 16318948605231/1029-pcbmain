# ARCH-REVIEW-004 实施基线与 P1 收口绑定
- 文档 ID：`ARCH-REVIEW-004`
- 版本：`1.0.0`
- 状态：`NormativeImplementationBinding`
- 基线：`ARCH-PCBA-VISION-001 v0.5.3`
- 目的：消除 v0.5.3 对 BoardModel / ManufacturingGeometrySnapshot 的实施歧义，同时明确本文件不等于正式架构批准。

## 1. 实施绑定结论

从本开发标准开始，涉及制造几何的代码实施必须采用以下唯一语义：

```text
SourceSetManifest
  → BoardDataAdapter
  → BoardModelVersion / BoardModelSnapshot
  → SourceValidation + ConflictResolution
  → ApprovalBinding
  → ManufacturingGeometrySnapshot
  → Domain Target / Program / Measurement Reference
```

`BoardModel` 是标准化、版本化、验证化的导入/中间模型；`ManufacturingGeometrySnapshot` 是生产语义层的批准绑定，不复制第二套几何实体主数据。

## 2. 实施约束

- `BoardModelRef` 必须通过精确 `id + version + sha256` 绑定。
- 生产运行不得读取 `latest`、目录最新文件或未批准缓存。
- Snapshot 不复制第二套 Geometry Entity Store。
- Snapshot 不代表视觉观测、MeasurementSet、InspectionFact、InspectionDecision。
- 缺输入、冲突、单位/层/side 不一致或批准状态无效时必须阻断。
- NPI、PCB、SPI、AOI 等实现必须引用本绑定，不得自行重新定义制造几何主模型。

## 3. AI 禁止误读

`ARCH-REVIEW-002` 是候选修订片段，不能直接作为实施依据；`ARCH-REVIEW-001` 是实施前审查记录；本文件与 `ARCH-REVIEW-003` 共同作为当前实施绑定。若未来正式批准的架构版本变化，必须执行 `DEV-GOV-013` 影响分析后重新生成绑定。

## 4. 与正式架构批准的关系

本文件**关闭的是实施语义歧义，不授予架构批准、生产资格或 Qualification**。正式架构批准仍由架构治理流程记录。代码开发可以基于本绑定冻结当前语义，但不得把本文件的状态投影成 `ArchitectureApproved` 或 `ProductionAccepted`。
