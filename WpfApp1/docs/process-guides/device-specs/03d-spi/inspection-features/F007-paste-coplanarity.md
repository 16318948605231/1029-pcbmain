# 03D-SPI-F007 — Paste Coplanarity

## Purpose
Characterize the relative height relationship of the accepted paste deposit against the authoritative reference geometry or plane.

## Contract
- **Input:** qualified 3D surface data and reference geometry.
- **ROI / Region:** feature-owned region plus any authoritative reference samples.
- **Coordinate system:** calibrated height frame with explicit reference identity.
- **Pre-processing:** validate calibration, reference geometry, surface completeness and registration.
- **Algorithm:** derive the authorized coplanarity descriptor from the measured surface/reference relationship.
- **Measurement:** descriptor value(s) with unit, reference frame, validity and provenance.

## Semantic boundary
Coplanarity must not be conflated with PasteHeight. The former describes a relative height relationship across a region/reference; the latter is a deposit height measurement under its own reference semantics.

## Decision semantics
The measurement is not a production verdict by itself. PASS/FAIL/REVIEW/INCONCLUSIVE/NOT_EVALUATED semantics are supplied by the authoritative Result/Quality contract. An invalid measurement must remain non-evaluable rather than becoming a passing numeric value.

## Parameters
Reference selection, sampling, filtering and decision parameters require explicit authority and revision. Numeric acceptance values are not invented.

## Boundary and failure cases
Insufficient reference samples, invalid calibration, sparse surface, out-of-region geometry, multiple candidate references and algorithm failure are non-evaluable conditions.

## Quality / Evidence / Replay
Quality contribution follows the authoritative rule. Evidence retains reference identity, sampling/algorithm revision and feature provenance. Replay requires deterministic surface and reference evidence.

## UI / Program / Recipe
The UI displays the reference and descriptor semantics; recipe edits remain feature-scoped and audited.

## Authority gates
Coplanarity definition, calculation method, uncertainty, repeatability, tolerance and acceptance: **Authoritative source required**.
