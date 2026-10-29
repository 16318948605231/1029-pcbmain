# BoardModel 与 ManufacturingGeometrySnapshot 权威收口
- 文档 ID：`ARCH-REVIEW-003`
- 版本：`2.0.0`
- 状态：`NormativeImplementationBinding`
- 基线：`ARCH-PCBA-VISION-001 v0.5.3`

## 1. 权威层级

`BoardModelVersion/BoardModelSnapshot` 是 `BoardDataAdapter` 对不同制造数据来源进行**标准化、版本化、验证化**的中间/导入契约。

`ManufacturingGeometrySnapshot` 是生产语义层对“已验证、冲突已关闭、适用域已确定、批准可用于生产参考”的**制造参考绑定**。它不是第二份几何主库，不复制 BoardModel 的实体集合。

```text
SourceSetManifest
  → BoardDataAdapter
  → BoardModelVersion / BoardModelSnapshot
  → SourceValidation + ConflictResolution
  → ApprovalBinding
  → ManufacturingGeometrySnapshot
  → Domain Target / Program / Measurement reference
```

## 2. 代码规则

- `BoardDataAdapter` 可以输出 `BoardModel*`，不得输出第二套 `ManufacturingGeometry*` 主模型。
- `ManufacturingGeometrySnapshot` 代码结构以 `BoardModelRef(id/version/hash)` + source/validation/approval/effective-scope evidence 为主。
- Product/Program/Recipe/Inspection Domain 不得读取 adapter 的 `latest`。
- Runtime 必须绑定明确的 `id + version + hash`。
- 缺输入、冲突、单位不一致、层/side 不一致、适用域不一致均不得自动 Ready。
- ManufacturingGeometrySnapshot 不代表视觉观测、MeasurementSet、InspectionFact、InspectionDecision。

## 3. 审核门

本条必须作为所有 NPI/Auto-Programming/PCB/SPI/AOI 导入流程的公共审计规则；任何代码若引入第二份 geometry 主模型，静态审计必须阻断。

> **AI使用警告：** 本文不是正式架构批准凭证；实施语义以当前 `ARCH-REVIEW-004` 绑定与活动 Registry/Manifest 为准。
