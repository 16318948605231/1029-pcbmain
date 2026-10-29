# 3D SPI Feature Catalog

| Feature ID | Feature | Required input | Output class | Detailed specification |
|---|---|---|---|---|
| 03D-SPI-F001 | PastePresence | 3D paste surface + pad/land context | Result/Finding/Measurement | inspection-features/F001-paste-presence.md |
| 03D-SPI-F002 | PasteArea | 3D paste surface + pad/land context | Measurement/Finding | inspection-features/F002-paste-area.md |
| 03D-SPI-F003 | PasteHeight | 3D surface + reference | Measurement/Finding | inspection-features/F003-paste-height.md |
| 03D-SPI-F004 | PasteVolume | 3D surface + reference | Measurement/Finding | inspection-features/F004-paste-volume.md |
| 03D-SPI-F005 | PasteOffset | Surface + nominal geometry | Measurement/Finding | inspection-features/F005-paste-offset.md |
| 03D-SPI-F006 | PasteShape | 3D surface + pad/land context | Measurement/Finding | inspection-features/F006-paste-shape.md |
| 03D-SPI-F007 | PasteCoplanarity | 3D surface + reference | Measurement/Finding | inspection-features/F007-paste-coplanarity.md |
| 03D-SPI-F008 | BridgingRisk | 3D surface + topology context | Finding/Measurement | inspection-features/F008-bridging-risk.md |

## Feature execution contract

Each feature binds an inspection object, ROI/region, coordinate/reference frame, calibration identity, algorithm revision, parameters, threshold source, outcome semantics, evidence references, replay inputs and Quality contribution.

The detailed execution contract is defined in [FEATURE_EXECUTION_CONTRACT.md](<FEATURE_EXECUTION_CONTRACT.md>), with end-to-end traceability in [FEATURE_TRACEABILITY.md](<FEATURE_TRACEABILITY.md>).

## Decision semantics

PASS, FAIL, REVIEW, INCONCLUSIVE and NOT_EVALUATED are distinct concepts where the authoritative Result contract supports them. A missing measurement is not a zero value. An unavailable feature is not a passing feature.

## Feature implementation rule

A catalog entry is not implementation-ready until its detailed specification defines input, ROI/region, coordinate/reference semantics, pre-processing, algorithm boundary, measurement/finding output, parameter authority, invalid/failure semantics, Quality contribution, Evidence, Replay, UI and Program/Recipe interaction.

## Parameter authority

Parameters affecting production decisions require an identified authoritative source and revision. Device defaults may be displayed as descriptive defaults but cannot silently become production acceptance limits.

## Qualification status

All features remain Candidate until concrete device/model qualification evidence exists. The catalog does not assert that every 3D SPI machine supports every feature.