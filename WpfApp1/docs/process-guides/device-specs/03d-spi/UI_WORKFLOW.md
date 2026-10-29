# 3D SPI Client Workflow

## Execution workflow

Configure device → Select Program → Load Recipe → Validate readiness/calibration → Prepare → Acquire → Inspect features → Review findings/measurements → Commit Result → Quality → Evidence/Replay → Release → History.

Reset/Recovery sits across the execution lifecycle and must preserve the correct distinction between current execution state and finalized historical authority.

## Feature workspace

The active feature workspace should expose:
- Feature identity/revision.
- Inspection object and ROI/Region identity.
- Coordinate/reference context.
- Current algorithm/parameter revision.
- Measurement/finding result and evaluability state.
- Evidence/provenance links.
- Quality contribution status when authoritative.
- Replay availability/state.

## Teaching

ROI, nominal geometry, reference geometry and topology/adjacency edits are feature-scoped. The client must not silently modify shared geometry owned by another feature. Authorized recipe editing produces a new revision according to Program/Recipe policy.

## Result review

Review must distinguish:
- raw/derived measurement;
- Finding;
- Quality authority;
- Replay authority;
- Release authority.

A UI summary must not reconstruct these authorities from unrelated workspace fields when a unified projection is available.

## Unified projection

WPF presentation consumes the unified client projection. Device-specific workspace state is not read directly by the presentation shell. The projection must carry the authoritative Result/Quality/Evidence/Replay/Release state needed by the view.

## Recovery

Acquisition interruption, invalid calibration, device fault, algorithm failure and user cancellation must leave the run in an explicit recoverable/non-finalized state. Recovery/re-execution must preserve finalized History and create the correct new execution identity according to the platform runtime contract.

## Safety and authority

Controls requiring hardware/domain authority remain unavailable until prerequisite state is known and valid. The UI must not fabricate thresholds, calibration validity, hardware qualification or Release authority.

## Acceptance boundary

Client acceptance requires deterministic simulation/structural evidence for projection and lifecycle behavior. Hardware acceptance remains a separate qualification gate.