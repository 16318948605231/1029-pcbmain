# 03D-SPI-F003 — Paste Height

## Purpose
Measure solder-paste deposit height relative to the authoritative reference surface/plane for the inspection feature.

## Contract
- **Input:** qualified height/depth surface data plus pad/land reference geometry.
- **ROI / Region:** feature-owned deposit region and authoritative reference region.
- **Coordinate system:** calibrated board/pad height frame; the reference plane and transformation source must be explicit.
- **Pre-processing:** validate calibration, reference availability, surface completeness and registration.
- **Algorithm:** determine the deposit/reference relationship using the qualified algorithm revision.
- **Measurement:** height quantity with unit, reference frame, validity, precision policy and provenance.

## Reference semantics
“Height” is not a universal raw-sensor value. The specification must identify the reference plane/geometry and calibration source before a production result can be authoritative.

## Decision semantics
The measurement is not a production verdict by itself. PASS/FAIL/REVIEW/INCONCLUSIVE/NOT_EVALUATED semantics are supplied by the authoritative Result/Quality contract. An invalid measurement must remain non-evaluable rather than becoming a passing numeric value.

## Parameters
Reference selection, surface filtering, segmentation and acceptance parameters are externalized by ID/revision. Numeric limits are not defined without authority.

## Boundary and failure cases
Missing reference, invalid calibration, sparse/invalid surface, ROI mismatch, multiple candidate regions, algorithm non-convergence and device fault must remain explicit.

## Quality / Evidence / Replay
Quality gating is determined by the platform Quality contract. Evidence binds reference identity as well as feature/input/recipe/algorithm identity. Replay must preserve the deterministic inputs needed to reconstruct the reference and measurement.

## UI / Program / Recipe
The UI must display unit and reference semantics with the measurement. Any reference/ROI teaching operation is authorized, versioned and feature-scoped.

## Authority gates
Height accuracy, repeatability, reference-plane definition, resolution, tolerance and production acceptance: **Authoritative source required**.
