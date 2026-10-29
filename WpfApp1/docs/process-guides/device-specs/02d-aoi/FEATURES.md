# 2D AOI Feature Catalog

| Feature ID | Feature | Required input | Output class |
|---|---|---|---|
| 02D-AOI-F001 | PresenceAbsence | Device-native qualified input | Result/Finding/Measurement |
| 02D-AOI-F002 | PositionOffset | Device-native qualified input | Result/Finding/Measurement |
| 02D-AOI-F003 | RotationOrientation | Device-native qualified input | Result/Finding/Measurement |
| 02D-AOI-F004 | Polarity | Device-native qualified input | Result/Finding/Measurement |
| 02D-AOI-F005 | MarkingPresence | Device-native qualified input | Result/Finding/Measurement |
| 02D-AOI-F006 | SurfaceAppearance | Device-native qualified input | Result/Finding/Measurement |
| 02D-AOI-F007 | VisibleSolderJoint | Device-native qualified input | Result/Finding/Measurement |
| 02D-AOI-F008 | TracePattern | Device-native qualified input | Result/Finding/Measurement |
| 02D-AOI-F009 | ForeignMaterial | Device-native qualified input | Result/Finding/Measurement |

## Feature execution contract

Each feature binds an inspection object, ROI or geometry, coordinate frame, algorithm revision, parameters, threshold source, outcome semantics, evidence references, replay inputs, and Quality contribution.

## Decision semantics

PASS, FAIL, REVIEW, INCONCLUSIVE and NOT_EVALUATED are distinct concepts where the authoritative result contract supports them. A missing measurement is not a zero value. An unavailable feature is not a passing feature.

## Parameter authority

Parameters affecting production decisions require an identified authoritative source and revision. Device defaults may be displayed as descriptive defaults but cannot silently become production acceptance limits.