# Bare-Board PCB Inspection Feature Catalog

| Feature ID | Feature | Required input | Output class |
|---|---|---|---|
| PCB-BARE-BOARD-F001 | TraceOpen | Device-native qualified input | Result/Finding/Measurement |
| PCB-BARE-BOARD-F002 | TraceShort | Device-native qualified input | Result/Finding/Measurement |
| PCB-BARE-BOARD-F003 | PadDefect | Device-native qualified input | Result/Finding/Measurement |
| PCB-BARE-BOARD-F004 | HolePresence | Device-native qualified input | Result/Finding/Measurement |
| PCB-BARE-BOARD-F005 | HolePosition | Device-native qualified input | Result/Finding/Measurement |
| PCB-BARE-BOARD-F006 | AnnularRing | Device-native qualified input | Result/Finding/Measurement |
| PCB-BARE-BOARD-F007 | CopperPattern | Device-native qualified input | Result/Finding/Measurement |
| PCB-BARE-BOARD-F008 | SolderMask | Device-native qualified input | Result/Finding/Measurement |
| PCB-BARE-BOARD-F009 | Silkscreen | Device-native qualified input | Result/Finding/Measurement |
| PCB-BARE-BOARD-F010 | BoardOutline | Device-native qualified input | Result/Finding/Measurement |
| PCB-BARE-BOARD-F011 | ForeignMaterial | Device-native qualified input | Result/Finding/Measurement |

## Feature execution contract

Each feature binds an inspection object, ROI or geometry, coordinate frame, algorithm revision, parameters, threshold source, outcome semantics, evidence references, replay inputs, and Quality contribution.

## Decision semantics

PASS, FAIL, REVIEW, INCONCLUSIVE and NOT_EVALUATED are distinct concepts where the authoritative result contract supports them. A missing measurement is not a zero value. An unavailable feature is not a passing feature.

## Parameter authority

Parameters affecting production decisions require an identified authoritative source and revision. Device defaults may be displayed as descriptive defaults but cannot silently become production acceptance limits.