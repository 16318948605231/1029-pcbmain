# 3D SPI Measurement Specification

## Measurement record

Each authoritative measurement records, as applicable:
- Measurement ID and source Feature ID/revision.
- Quantity/value representation.
- Unit.
- Coordinate/reference frame.
- Calibration identity/revision and validity.
- Algorithm identity/revision.
- Parameter-set identity/revision.
- Validity/evaluability state.
- Precision/rounding policy.
- Provenance/evidence reference.

## Measurement families

The current 3D SPI feature catalog defines candidate measurement families for paste presence, area, height, volume, offset, shape and coplanarity. BridgingRisk is primarily a finding/observation contract and may include supporting measurements where authorized.

## Normalization

Sensor-native values become platform measurements only after their unit and reference semantics are explicit. Coordinate transformation and physical-unit conversion require an authoritative calibration contract.

## Invalid / indeterminate

Invalid calibration, incomplete input, acquisition corruption, missing reference geometry, unsupported geometry, algorithm non-convergence, ambiguous target identification or device fault must yield explicit invalid/indeterminate semantics. They must not be serialized as plausible numeric results.

## Reference integrity

Height, volume and coplanarity require an explicit reference definition. Offset requires traceable nominal geometry. Area and shape require an explicit accepted-region definition. The reference identity is part of provenance.

## Precision and qualification

Precision, accuracy, repeatability, uncertainty, resolution and tolerance limits are not inferred from the 3D SPI family name. They require model-specific qualification evidence.

## Rounding

Rounding/display precision must not silently change the authoritative stored measurement. The authoritative numeric representation and the presentation representation are separate concerns when the platform contract requires it.

## Result linkage

Every authoritative measurement links to Feature, acquisition/session, Recipe revision, calibration/reference context, algorithm revision and evidence required for Replay.

## Open authority

No numeric tolerance, default value, accuracy claim, repeatability claim or production threshold is defined here without an authoritative source.