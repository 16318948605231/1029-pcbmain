# Optical / Laser Metrology Feature Catalog

| Feature ID | Feature | Required input | Output class |
|---|---|---|---|
| METROLOGY-F001 | PointDistance | Device-native qualified input | Result/Finding/Measurement |
| METROLOGY-F002 | LineDistance | Device-native qualified input | Result/Finding/Measurement |
| METROLOGY-F003 | Angle | Device-native qualified input | Result/Finding/Measurement |
| METROLOGY-F004 | Diameter | Device-native qualified input | Result/Finding/Measurement |
| METROLOGY-F005 | Radius | Device-native qualified input | Result/Finding/Measurement |
| METROLOGY-F006 | Width | Device-native qualified input | Result/Finding/Measurement |
| METROLOGY-F007 | Height | Device-native qualified input | Result/Finding/Measurement |
| METROLOGY-F008 | Flatness | Device-native qualified input | Result/Finding/Measurement |
| METROLOGY-F009 | Parallelism | Device-native qualified input | Result/Finding/Measurement |
| METROLOGY-F010 | Perpendicularity | Device-native qualified input | Result/Finding/Measurement |
| METROLOGY-F011 | Position | Device-native qualified input | Result/Finding/Measurement |
| METROLOGY-F012 | Profile | Device-native qualified input | Result/Finding/Measurement |

## Feature execution contract

Each feature binds an inspection object, ROI or geometry, coordinate frame, algorithm revision, parameters, threshold source, outcome semantics, evidence references, replay inputs, and Quality contribution.

## Decision semantics

PASS, FAIL, REVIEW, INCONCLUSIVE and NOT_EVALUATED are distinct concepts where the authoritative result contract supports them. A missing measurement is not a zero value. An unavailable feature is not a passing feature.

## Parameter authority

Parameters affecting production decisions require an identified authoritative source and revision. Device defaults may be displayed as descriptive defaults but cannot silently become production acceptance limits.