# 3D AXI / CT Device Specification

## Scope
3D AXI / CT provides internal PCBA structures and volumetric defects through 3D reconstructed X-ray / CT. The platform consumes normalized acquisition and inspection contracts; proprietary transport and SDK details remain behind the adapter.

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
- 03D-AXI-CT-F001 — InternalPresence
- 03D-AXI-CT-F002 — VoidVolume
- 03D-AXI-CT-F003 — VoidDistribution
- 03D-AXI-CT-F004 — SolderJoint3DGeometry
- 03D-AXI-CT-F005 — BGAInspection
- 03D-AXI-CT-F006 — QFNInspection
- 03D-AXI-CT-F007 — ForeignMaterial
- 03D-AXI-CT-F008 — InternalStructuralDefect

## Production qualification gate
Accuracy, repeatability, throughput, defect sensitivity/specificity, false-call behavior, calibration validity, and acceptance thresholds require qualified evidence before production use.