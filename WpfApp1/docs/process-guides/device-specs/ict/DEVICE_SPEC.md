# ICT Device Specification

## Scope
ICT provides nets, components, electrical nodes and board test points through in-circuit electrical test. The platform consumes normalized acquisition and inspection contracts; proprietary transport and SDK details remain behind the adapter.

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
- ICT-F001 — OpenCircuit
- ICT-F002 — ShortCircuit
- ICT-F003 — Resistance
- ICT-F004 — Capacitance
- ICT-F005 — Inductance
- ICT-F006 — Diode
- ICT-F007 — ComponentValue
- ICT-F008 — Continuity
- ICT-F009 — Isolation

## Production qualification gate
Accuracy, repeatability, throughput, defect sensitivity/specificity, false-call behavior, calibration validity, and acceptance thresholds require qualified evidence before production use.