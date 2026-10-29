# 03D-SPI-F004 — Paste Volume

## Purpose
Measure the volume of the accepted solder-paste deposit associated with the inspection object.

## Contract
- **Input:** qualified 3D surface data, pad/land geometry and an authoritative reference surface/plane.
- **ROI / Region:** feature-owned deposit region with recipe-defined exclusions where applicable.
- **Coordinate system:** calibrated board coordinate frame plus a defined height reference; physical volume conversion requires authoritative calibration.
- **Pre-processing:** validate acquisition integrity, registration, calibration and reference availability.
- **Algorithm:** segment the deposit and integrate the accepted height field over the authoritative region using a versioned algorithm.
- **Measurement:** volume quantity with unit, validity, reference frame, algorithm revision and provenance.

## Measurement semantics
Volume is invalid when its surface, reference or calibration is invalid. A missing surface cannot be converted into a zero-volume pass.

## Decision semantics
The measurement is not a production verdict by itself. PASS/FAIL/REVIEW/INCONCLUSIVE/NOT_EVALUATED semantics are supplied by the authoritative Result/Quality contract. An invalid measurement must remain non-evaluable rather than becoming a passing numeric value.

## Parameters
Segmentation, reference, filtering, integration and acceptance parameters are identified by ID/revision and authority source. No production numeric thresholds are assumed.

## Boundary and failure cases
Missing/invalid reference, incomplete height data, empty region, disconnected deposits, merged deposits, unsupported geometry, algorithm failure and device fault require explicit non-evaluable outcomes.

## Quality / Evidence / Replay
Quality uses the platform rule chain. Evidence captures feature, input, reference/calibration, recipe, algorithm and measurement identity. Replay requires the deterministic captured surface/reference evidence.

## UI / Program / Recipe
The client exposes volume and its validity/provenance; feature teaching is isolated to the active recipe feature.

## Authority gates
Volume accuracy, repeatability, uncertainty, resolution, integration policy, tolerance and production acceptance: **Authoritative source required**.
