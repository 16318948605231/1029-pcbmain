# ICT Feature Catalog

| Feature ID | Feature | Required input | Output class |
|---|---|---|---|
| ICT-F001 | OpenCircuit | Device-native qualified input | Result/Finding/Measurement |
| ICT-F002 | ShortCircuit | Device-native qualified input | Result/Finding/Measurement |
| ICT-F003 | Resistance | Device-native qualified input | Result/Finding/Measurement |
| ICT-F004 | Capacitance | Device-native qualified input | Result/Finding/Measurement |
| ICT-F005 | Inductance | Device-native qualified input | Result/Finding/Measurement |
| ICT-F006 | Diode | Device-native qualified input | Result/Finding/Measurement |
| ICT-F007 | ComponentValue | Device-native qualified input | Result/Finding/Measurement |
| ICT-F008 | Continuity | Device-native qualified input | Result/Finding/Measurement |
| ICT-F009 | Isolation | Device-native qualified input | Result/Finding/Measurement |

## Feature execution contract

Each feature binds an inspection object, ROI or geometry, coordinate frame, algorithm revision, parameters, threshold source, outcome semantics, evidence references, replay inputs, and Quality contribution.

## Decision semantics

PASS, FAIL, REVIEW, INCONCLUSIVE and NOT_EVALUATED are distinct concepts where the authoritative result contract supports them. A missing measurement is not a zero value. An unavailable feature is not a passing feature.

## Parameter authority

Parameters affecting production decisions require an identified authoritative source and revision. Device defaults may be displayed as descriptive defaults but cannot silently become production acceptance limits.