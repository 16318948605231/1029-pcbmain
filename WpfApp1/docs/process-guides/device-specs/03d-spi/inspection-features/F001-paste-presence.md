# 03D-SPI-F001 — Paste Presence

## Purpose
Determine whether a solder-paste deposit is present for the inspection object represented by the active pad/land definition.

## Contract
- **Input:** qualified 3D paste surface data plus the pad/land inspection geometry and registration context.
- **ROI / Region:** the feature-owned pad/land region. The exact geometry source is recipe/program authority.
- **Coordinate system:** the active calibrated board/pad coordinate frame. Raw sensor coordinates must not be treated as production coordinates without an authoritative calibration transform.
- **Pre-processing:** acquisition integrity, registration, calibration-validity and region-validity checks. Device/model-specific filtering remains an external authority.
- **Algorithm:** evaluate deposit evidence inside the feature region and produce an explicit evaluability state. The algorithm revision is part of the feature provenance.
- **Output:** presence outcome plus optional supporting measurement/finding data when the authoritative feature contract defines them.

## Decision semantics
PASS/FAIL/REVIEW/INCONCLUSIVE/NOT_EVALUATED are distinct states when supported by the authoritative Result contract. A missing or invalid surface is not interpreted as zero paste.

## Parameters
Feature parameters must identify:
- parameter ID and revision;
- value and unit/type;
- authoritative source;
- allowed range or enumerated values;
- dependency on calibration, recipe or inspection mode.

No production threshold or default numeric value is invented here.

## Boundary and failure cases
Handle target missing, empty ROI, ROI outside valid acquisition, invalid calibration, incomplete acquisition, corrupted data, algorithm non-evaluable, multiple candidate deposits, and device fault as explicit states.

## Quality / Evidence / Replay
The result contributes to Quality only through an authoritative Quality rule. Evidence must bind the feature revision, input identity, recipe revision, algorithm revision and relevant calibration/provenance. Replay requires deterministic captured inputs; a live hardware call is not a replay substitute.

## UI / Program / Recipe
The feature is selectable and teachable only inside an authorized Program/Recipe context. UI edits must identify the feature and preserve coordinate context. Parameter changes are versioned/audited according to platform policy.

## Authority gates
Accuracy, detection sensitivity, minimum deposit criteria, tolerance values and production acceptance rules: **Authoritative source required**.
