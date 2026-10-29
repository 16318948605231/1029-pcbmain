> 使用范围：先绑定PG制程、SM复用能力及正式Contract/Owner，再补型号能力；不得用于本轮暂缓的X-Ray/CT、ICT、FCT。模板字段未填写不等于验收已完成。

# Device Specification Template

## Identity
Device Family ID / Display Name / Revision / Status / Scope / Inspection Domain.

## Boundary
Define physical-device responsibility versus platform responsibility.

## Inputs
Product/program identity, acquisition data, coordinate/calibration context, recipe and synchronization metadata.

## Outputs
Feature identity, measurement/finding, outcome, evidence, replay reference, quality inputs, provenance/version.

## Capability
Capability ID, modality, feature IDs, required context, output type, evidence requirements, constraints, authority status.

## Feature
Feature ID, object, input, ROI/geometry, coordinate system, algorithm/version, parameters, threshold source, decision semantics, evidence, replay, quality, UI, qualification.

## Measurement
Quantity, unit, reference frame, precision, accuracy/repeatability source, uncertainty, invalid semantics. Never guess unverified accuracy.

## Quality and release
Device results feed the platform Quality → Replay → Release authority chain; the device cannot publish final Release authority.

## Adapter
Vendor SDK, transport, proprietary data, hardware sequencing and safety details remain behind the adapter.

## Open authority gates
Record missing authoritative information explicitly.