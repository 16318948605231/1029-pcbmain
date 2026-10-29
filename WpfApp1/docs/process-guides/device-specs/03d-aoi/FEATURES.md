# 3D AOI Feature Catalog

| Feature ID | Feature | Required input | Output class |
|---|---|---|---|
| 03D-AOI-F001 | PresenceAbsence | Device-native qualified input | Result/Finding/Measurement |
| 03D-AOI-F002 | PositionOffset | Device-native qualified input | Result/Finding/Measurement |
| 03D-AOI-F003 | RotationOrientation | Device-native qualified input | Result/Finding/Measurement |
| 03D-AOI-F004 | Height | Device-native qualified input | Result/Finding/Measurement |
| 03D-AOI-F005 | Area | Device-native qualified input | Result/Finding/Measurement |
| 03D-AOI-F006 | Volume | Device-native qualified input | Result/Finding/Measurement |
| 03D-AOI-F007 | Coplanarity | Device-native qualified input | Result/Finding/Measurement |
| 03D-AOI-F008 | VisibleSolderGeometry | Device-native qualified input | Result/Finding/Measurement |
| 03D-AOI-F009 | ComponentLift | Device-native qualified input | Result/Finding/Measurement |

## Feature execution contract

Each feature binds an inspection object, ROI or geometry, coordinate frame, algorithm revision, parameters, threshold source, outcome semantics, evidence references, replay inputs, and Quality contribution.

## Decision semantics

PASS, FAIL, REVIEW, INCONCLUSIVE and NOT_EVALUATED are distinct concepts where the authoritative result contract supports them. A missing measurement is not a zero value. An unavailable feature is not a passing feature.

## Parameter authority

Parameters affecting production decisions require an identified authoritative source and revision. Device defaults may be displayed as descriptive defaults but cannot silently become production acceptance limits.