# FCT Feature Catalog

| Feature ID | Feature | Required input | Output class |
|---|---|---|---|
| FCT-F001 | PowerOn | Device-native qualified input | Result/Finding/Measurement |
| FCT-F002 | Communication | Device-native qualified input | Result/Finding/Measurement |
| FCT-F003 | InterfaceResponse | Device-native qualified input | Result/Finding/Measurement |
| FCT-F004 | DigitalIO | Device-native qualified input | Result/Finding/Measurement |
| FCT-F005 | AnalogResponse | Device-native qualified input | Result/Finding/Measurement |
| FCT-F006 | ProtocolExchange | Device-native qualified input | Result/Finding/Measurement |
| FCT-F007 | FunctionalSequence | Device-native qualified input | Result/Finding/Measurement |
| FCT-F008 | SafetyInterlock | Device-native qualified input | Result/Finding/Measurement |

## Feature execution contract

Each feature binds an inspection object, ROI or geometry, coordinate frame, algorithm revision, parameters, threshold source, outcome semantics, evidence references, replay inputs, and Quality contribution.

## Decision semantics

PASS, FAIL, REVIEW, INCONCLUSIVE and NOT_EVALUATED are distinct concepts where the authoritative result contract supports them. A missing measurement is not a zero value. An unavailable feature is not a passing feature.

## Parameter authority

Parameters affecting production decisions require an identified authoritative source and revision. Device defaults may be displayed as descriptive defaults but cannot silently become production acceptance limits.