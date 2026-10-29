# 3D AXI / CT Feature Catalog

| Feature ID | Feature | Required input | Output class |
|---|---|---|---|
| 03D-AXI-CT-F001 | InternalPresence | Device-native qualified input | Result/Finding/Measurement |
| 03D-AXI-CT-F002 | VoidVolume | Device-native qualified input | Result/Finding/Measurement |
| 03D-AXI-CT-F003 | VoidDistribution | Device-native qualified input | Result/Finding/Measurement |
| 03D-AXI-CT-F004 | SolderJoint3DGeometry | Device-native qualified input | Result/Finding/Measurement |
| 03D-AXI-CT-F005 | BGAInspection | Device-native qualified input | Result/Finding/Measurement |
| 03D-AXI-CT-F006 | QFNInspection | Device-native qualified input | Result/Finding/Measurement |
| 03D-AXI-CT-F007 | ForeignMaterial | Device-native qualified input | Result/Finding/Measurement |
| 03D-AXI-CT-F008 | InternalStructuralDefect | Device-native qualified input | Result/Finding/Measurement |

## Feature execution contract

Each feature binds an inspection object, ROI or geometry, coordinate frame, algorithm revision, parameters, threshold source, outcome semantics, evidence references, replay inputs, and Quality contribution.

## Decision semantics

PASS, FAIL, REVIEW, INCONCLUSIVE and NOT_EVALUATED are distinct concepts where the authoritative result contract supports them. A missing measurement is not a zero value. An unavailable feature is not a passing feature.

## Parameter authority

Parameters affecting production decisions require an identified authoritative source and revision. Device defaults may be displayed as descriptive defaults but cannot silently become production acceptance limits.