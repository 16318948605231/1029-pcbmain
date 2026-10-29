# 03D-SPI-F002 — Paste Area

## Purpose
Measure the projected area of an accepted solder-paste deposit within the feature's pad/land inspection region.

## Contract
- **Input:** qualified 3D surface data and feature-owned pad/land geometry.
- **ROI / Region:** pad/land region with any exclusion geometry defined by the recipe authority.
- **Coordinate system:** calibrated board coordinate frame; conversion from sensor samples to physical area requires an authoritative calibration model.
- **Pre-processing:** validate acquisition completeness, registration and calibration before segmentation.
- **Algorithm:** segment/evaluate the deposit and compute the accepted region area using the authoritative algorithm revision.
- **Measurement:** area quantity with explicit unit, validity, reference frame, algorithm revision and provenance.

## Measurement semantics
A numeric value is authoritative only when the input, calibration and algorithm are valid. Invalid/indeterminate measurements must not be serialized as plausible zero values.

## Decision semantics
The measurement is not a production verdict by itself. PASS/FAIL/REVIEW/INCONCLUSIVE/NOT_EVALUATED semantics are supplied by the authoritative Result/Quality contract. An invalid measurement must remain non-evaluable rather than becoming a passing numeric value.

## Parameters
Segmentation, inclusion/exclusion geometry and any filtering parameters are recipe/algorithm parameters. Each production-affecting value requires an identified source and revision. No numeric defaults or acceptance limits are invented.

## Boundary and failure cases
Empty ROI, invalid calibration, incomplete surface, non-convergent segmentation, multiple deposits, merged deposits, unsupported geometry and device faults require explicit non-evaluable semantics.

## Quality / Evidence / Replay
Quality contribution is rule-driven. Evidence binds measurement identity, feature revision, acquisition identity, calibration identity, algorithm revision and recipe revision. Replay requires the deterministic surface/input evidence used by the measurement.

## UI / Program / Recipe
The client exposes the measurement and its validity/provenance. Teaching changes are feature-scoped and must not silently alter another feature's geometry.

## Authority gates
Area accuracy, repeatability, resolution, segmentation policy, tolerance and production acceptance: **Authoritative source required**.
