# 3D AOI Device Specification

## Scope
3D AOI provides PCB/PCBA components and height-bearing structures through 3D optical imaging / height data. The platform consumes normalized acquisition and inspection contracts; proprietary transport and SDK details remain behind the adapter.

## Lifecycle
Configure → Prepare → Acquire → Inspect → Review → Commit → Quality → Replay → Release → History.

## Required context
Product/program identity, device identity/configuration revision, acquisition/session identity, calibration/coordinate context where applicable, feature/recipe revision, operator/automation identity, evidence provenance.

## Capability advertisement
The concrete adapter advertises only capabilities supported by the device instance and an authoritative qualification record. Unknown capabilities remain unavailable.

## Result boundary
Feature results are normalized into the platform Result model and linked to evidence/provenance. The device does not publish final Release authority.

## Failure semantics
Acquisition failure, device-not-ready, calibration-invalid, algorithm-not-evaluable, feature-failed, review-required, and successful evaluation must remain distinguishable. Exact production states come from authoritative domain contracts.

## Hardware authority
Safety interlocks, exposure rules, motion/fixture constraints, electrical limits, and vendor SDK semantics are external authority gates and are not invented here.

## Feature catalog
- 03D-AOI-F001 — PresenceAbsence
- 03D-AOI-F002 — PositionOffset
- 03D-AOI-F003 — RotationOrientation
- 03D-AOI-F004 — Height
- 03D-AOI-F005 — Area
- 03D-AOI-F006 — Volume
- 03D-AOI-F007 — Coplanarity
- 03D-AOI-F008 — VisibleSolderGeometry
- 03D-AOI-F009 — ComponentLift

## Production qualification gate
Accuracy, repeatability, throughput, defect sensitivity/specificity, false-call behavior, calibration validity, and acceptance thresholds require qualified evidence before production use.