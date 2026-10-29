# 3D SPI — Golden Device Specification

Family: 03d-spi  
Modality: 3D solder-paste inspection  
Objects: solder-paste deposits before component placement

This directory is the current golden device-specification surface. It is intentionally deeper than the other device-family catalogs and is the template source for subsequent device-specific expansion.

## Specification surfaces

- [DEVICE_SPEC.md](<DEVICE_SPEC.md>) — device boundary, input, coordinate/calibration, lifecycle and authority.
- [CAPABILITIES.md](<CAPABILITIES.md>) — normalized capabilities and qualification states.
- [FEATURES.md](<FEATURES.md>) — feature catalog and implementation-readiness rule.
- [inspection-features/](inspection-features/) — one detailed specification per feature.
- [FEATURE_EXECUTION_CONTRACT.md](<FEATURE_EXECUTION_CONTRACT.md>) — normalized feature execution chain.
- [FEATURE_TRACEABILITY.md](<FEATURE_TRACEABILITY.md>) — end-to-end feature-to-client traceability.
- [MEASUREMENTS.md](<MEASUREMENTS.md>) — measurement semantics and provenance.
- [PARAMETER_AUTHORITY.md](<PARAMETER_AUTHORITY.md>) — parameter identity and authority rules.
- [QUALITY.md](<QUALITY.md>) — Quality/Evidence/Replay/Release boundary.
- [QUALIFICATION_GATES.md](<QUALIFICATION_GATES.md>) — external qualification gates.
- [UI_WORKFLOW.md](<UI_WORKFLOW.md>) — Program/Recipe/client execution and recovery.
- [VENDOR_ADAPTER.md](<VENDOR_ADAPTER.md>) — vendor isolation boundary.

## Golden-spec rule

This directory is a specification foundation, not a hardware qualification record. Unknown, model-specific or production-specific values remain explicitly gated rather than guessed.

## Completion status

The eight current feature entries have detailed non-numeric execution specifications. Remaining authoritative inputs include concrete device/model behavior, approved calibration/metrology evidence, production thresholds, safety constraints, and vendor SDK contracts.