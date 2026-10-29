# Optical / Laser Metrology Device Specification

## Scope
Optical / Laser Metrology provides PCB/PCBA geometry, features, planes, edges, holes and datums through optical/laser geometric measurement. The platform consumes normalized acquisition and inspection contracts; proprietary transport and SDK details remain behind the adapter.

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
- METROLOGY-F001 — PointDistance
- METROLOGY-F002 — LineDistance
- METROLOGY-F003 — Angle
- METROLOGY-F004 — Diameter
- METROLOGY-F005 — Radius
- METROLOGY-F006 — Width
- METROLOGY-F007 — Height
- METROLOGY-F008 — Flatness
- METROLOGY-F009 — Parallelism
- METROLOGY-F010 — Perpendicularity
- METROLOGY-F011 — Position
- METROLOGY-F012 — Profile

## Production qualification gate
Accuracy, repeatability, throughput, defect sensitivity/specificity, false-call behavior, calibration validity, and acceptance thresholds require qualified evidence before production use.