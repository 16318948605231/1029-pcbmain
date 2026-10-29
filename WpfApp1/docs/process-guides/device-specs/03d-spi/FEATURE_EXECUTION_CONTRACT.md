# 3D SPI Feature Execution Contract

This contract binds each 3D SPI feature to the platform execution chain without inventing hardware-specific semantics.

## Execution chain

Device input → acquisition/session identity → feature context → ROI/region → coordinate/calibration validation → pre-processing → algorithm revision → measurement/finding → normalization → Result → Quality contribution → Evidence → Replay → Release.

## Required feature context

Every execution must carry, where defined by the authoritative platform contract:
- Device instance/configuration identity and revision.
- Program/Recipe identity and revision.
- Inspection Feature ID and revision.
- Acquisition/session identity and input-data identity.
- ROI/region identity and coordinate/reference frame.
- Calibration identity/version and validity state.
- Algorithm identity/version.
- Parameter set identity/version.
- Operator/automation identity.
- Evidence/provenance identity.

## Evaluation state

The runtime must preserve the distinction between:
- input unavailable;
- input invalid/corrupt;
- calibration invalid;
- feature not configured;
- feature not evaluable;
- algorithm failed;
- evaluated with a finding;
- evaluated without a finding;
- review required.

The exact serialized enum names remain owned by the authoritative Result contract.

## Measurement normalization

A measurement becomes platform-facing only after quantity, unit, reference frame, validity and provenance are explicit. A failed evaluation is not a numeric zero.

## Finding normalization

A Finding identifies the feature, object/region, observation/evidence, evaluation state and provenance. It does not silently become a Quality or Release decision.

## Quality boundary

A feature declares its candidate contribution. Quality owns the authoritative aggregation and decision semantics. Production thresholds require an identified authority source and revision.

## Evidence boundary

Evidence must be sufficient to establish what was evaluated, with which feature/algorithm/parameters and against which input/calibration context. Evidence identity must remain stable across Result, Quality and Replay references.

## Replay boundary

Replay must use deterministic captured inputs and immutable feature/algorithm/parameter provenance. Hardware re-acquisition is not a substitute for replay evidence.

## Recovery boundary

If acquisition or feature execution is interrupted, the current run must expose an explicit non-finalized state. Recovery/re-execution must create a fresh execution identity where required by the platform runtime and must not mutate finalized historical authority.

## Open authority gates

Hardware timing, scanner behavior, sensor calibration procedures, exact algorithm implementation, numeric tolerances, production acceptance and safety constraints remain external authority gates.
