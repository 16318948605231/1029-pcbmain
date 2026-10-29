# 2D X-Ray Feature Catalog

| Feature ID | Feature | Required input | Output class |
|---|---|---|---|
| 02D-XRAY-F001 | InternalPresence | Device-native qualified input | Result/Finding/Measurement |
| 02D-XRAY-F002 | Void | Device-native qualified input | Result/Finding/Measurement |
| 02D-XRAY-F003 | SolderJointAppearance | Device-native qualified input | Result/Finding/Measurement |
| 02D-XRAY-F004 | BGA_QFN_Inspection | Device-native qualified input | Result/Finding/Measurement |
| 02D-XRAY-F005 | ForeignMaterial | Device-native qualified input | Result/Finding/Measurement |
| 02D-XRAY-F006 | BridgeOrShortAppearance | Device-native qualified input | Result/Finding/Measurement |
| 02D-XRAY-F007 | ComponentOrientationInternal | Device-native qualified input | Result/Finding/Measurement |

## Feature execution contract

Each feature binds an inspection object, ROI or geometry, coordinate frame, algorithm revision, parameters, threshold source, outcome semantics, evidence references, replay inputs, and Quality contribution.

## Decision semantics

PASS, FAIL, REVIEW, INCONCLUSIVE and NOT_EVALUATED are distinct concepts where the authoritative result contract supports them. A missing measurement is not a zero value. An unavailable feature is not a passing feature.

## Parameter authority

Parameters affecting production decisions require an identified authoritative source and revision. Device defaults may be displayed as descriptive defaults but cannot silently become production acceptance limits.