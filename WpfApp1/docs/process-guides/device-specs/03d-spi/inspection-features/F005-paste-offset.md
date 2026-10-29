# 03D-SPI-F005 — Paste Offset

## Purpose
Determine the positional deviation of an accepted paste deposit relative to its authoritative nominal pad/land geometry.

## Contract
- **Input:** qualified paste surface/segmentation plus nominal pad/land geometry.
- **ROI / Region:** feature-owned pad/land region and any authoritative search/exclusion region.
- **Coordinate system:** calibrated board coordinate frame; nominal and measured geometry must share a traceable frame.
- **Pre-processing:** registration, calibration validation and target segmentation.
- **Algorithm:** derive the deposit reference location/geometry and calculate its deviation from nominal.
- **Measurement:** offset components/geometry with explicit units, frame, validity and provenance.

## Decision semantics
Offset is a measurement, not inherently a FAIL. Quality interpretation requires an authoritative rule and tolerance source.

## Parameters
Nominal geometry source, registration policy, segmentation and tolerance references are versioned. Numeric tolerances require production authority.

## Boundary and failure cases
Missing nominal, registration failure, empty ROI, multiple deposits, ambiguous centroid/geometry, invalid calibration, unsupported geometry and algorithm failure remain explicit.

## Quality / Evidence / Replay
Evidence binds nominal geometry identity and calibration as well as feature/recipe/input/algorithm identities. Replay must retain the deterministic nominal and measurement inputs.

## UI / Program / Recipe
The UI shows the reference/nominal source and measured offset. Teaching a nominal or ROI requires authorized recipe editing and audit/version capture.

## Authority gates
Offset accuracy, repeatability, coordinate transformation, nominal-source semantics, tolerance and acceptance: **Authoritative source required**.
