# Bare-Board PCB Inspection Device Specification

## Scope
Bare-Board PCB Inspection provides bare PCB traces, pads, holes, solder mask, silkscreen and geometry through optical / dimensional / electrical PCB inspection. The platform consumes normalized acquisition and inspection contracts; proprietary transport and SDK details remain behind the adapter.

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
- PCB-BARE-BOARD-F001 — TraceOpen
- PCB-BARE-BOARD-F002 — TraceShort
- PCB-BARE-BOARD-F003 — PadDefect
- PCB-BARE-BOARD-F004 — HolePresence
- PCB-BARE-BOARD-F005 — HolePosition
- PCB-BARE-BOARD-F006 — AnnularRing
- PCB-BARE-BOARD-F007 — CopperPattern
- PCB-BARE-BOARD-F008 — SolderMask
- PCB-BARE-BOARD-F009 — Silkscreen
- PCB-BARE-BOARD-F010 — BoardOutline
- PCB-BARE-BOARD-F011 — ForeignMaterial

## Production qualification gate
Accuracy, repeatability, throughput, defect sensitivity/specificity, false-call behavior, calibration validity, and acceptance thresholds require qualified evidence before production use.