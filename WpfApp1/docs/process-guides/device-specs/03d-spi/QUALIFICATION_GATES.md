# 3D SPI Qualification Gates

The specification catalog is an engineering contract foundation. It is not a machine qualification record.

## Gate categories

| Gate | Required authority | Blocks production claim? |
|---|---|---|
| Device capability | Model/device capability evidence | Yes |
| Calibration | Approved calibration procedure and evidence | Yes |
| Measurement accuracy | Metrology qualification evidence | Yes |
| Repeatability | Qualification study | Yes |
| Algorithm performance | Approved algorithm/validation evidence | Yes |
| Defect sensitivity/specificity | Validated sample-set evidence | Yes |
| Parameter defaults | Approved recipe/engineering authority | Yes |
| Thresholds/tolerances | Production Quality authority | Yes |
| Safety/interlocks | Hardware/vendor/safety authority | Yes |
| Throughput/timing | Qualified device/production evidence | Yes |
| Replay determinism | Platform evidence contract + deterministic input evidence | Yes for authoritative replay |
| UI behavior | Client contract + acceptance evidence | Required before client acceptance |

## Required record

Each qualified gate should identify the device/model/revision, evidence artifact, owner/authority, effective revision and acceptance status.

## Unknown state

Unknown, missing or conflicting qualification evidence must not be promoted to production-qualified.

## Non-blocking development

Documentation, contract validation, deterministic simulation and adapter-boundary preparation may continue while external qualification evidence is pending.
