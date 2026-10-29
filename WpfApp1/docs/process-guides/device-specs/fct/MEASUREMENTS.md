# FCT Measurement Specification

## Measurement families

Measurements are defined per feature. The platform records quantity, unit, coordinate/reference frame, validity, precision/rounding policy, source feature, algorithm revision, and provenance.

## Qualification

Accuracy, repeatability, uncertainty, resolution, sampling density, calibration validity, and tolerance limits are not inferred from the device family name. They require model-specific qualification evidence.

## Invalid / indeterminate

Invalid calibration, incomplete input, acquisition corruption, algorithm non-convergence, unsupported geometry, or device fault must yield an explicit invalid/indeterminate state. It must not be serialized as a plausible numeric result.

## Result linkage

Every authoritative measurement links back to the inspection feature, acquisition/session identity, recipe revision, and evidence required for replay.