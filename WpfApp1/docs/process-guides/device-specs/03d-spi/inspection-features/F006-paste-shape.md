# 03D-SPI-F006 — Paste Shape

## Purpose
Characterize the geometric form of an accepted solder-paste deposit against the feature's authorized nominal geometry or shape criteria.

## Contract
- **Input:** qualified 3D surface data and pad/land geometry.
- **ROI / Region:** feature-owned deposit region and authorized exclusion geometry.
- **Coordinate system:** calibrated board/pad frame with explicit reference semantics.
- **Pre-processing:** registration, surface validity, segmentation and calibration checks.
- **Algorithm:** derive shape descriptors from the accepted deposit geometry using a versioned algorithm. The concrete descriptor set is model/recipe authority.
- **Output:** shape measurement/finding set with explicit descriptor identity, validity and provenance.

## Decision semantics
Shape descriptors do not imply a production verdict by themselves. The Quality contract supplies the rule that interprets them.

## Parameters
Shape descriptor selection, filtering, segmentation and decision parameters require IDs, revisions and authoritative sources. No vendor-specific descriptor names are elevated to platform contracts without qualification.

## Boundary and failure cases
Irregular/multiple deposits, empty region, incomplete surface, invalid calibration, unsupported geometry and algorithm failure must be explicit.

## Quality / Evidence / Replay
Evidence records the descriptor/algorithm revision and input provenance. Replay requires the deterministic geometry/surface evidence needed to reproduce the descriptor set.

## UI / Program / Recipe
The UI should expose the selected shape descriptor(s), validity and provenance without hiding whether the value is measured, derived or rule-evaluated.

## Authority gates
Shape metric definition, repeatability, algorithm qualification, tolerance and production acceptance: **Authoritative source required**.
