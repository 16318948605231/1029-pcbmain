# 3D SPI Feature Traceability

| Feature | Input | ROI/Region | Coordinate/Reference | Measurement/Finding | Quality | Evidence | Replay | UI/Recipe |
|---|---|---|---|---|---|---|---|---|
| 03D-SPI-F001 Presence | 3D paste surface | Pad/land | Calibrated board/pad frame | Presence outcome | Rule-driven | Feature/input/calibration provenance | Deterministic surface/context | Feature-scoped |
| 03D-SPI-F002 Area | 3D paste surface | Pad/land | Calibrated physical frame | Area | Rule-driven | Measurement provenance | Deterministic surface | Feature-scoped |
| 03D-SPI-F003 Height | 3D surface + reference | Deposit/reference | Calibrated height frame | Height | Rule-driven | Reference + calibration provenance | Surface + reference | Feature-scoped |
| 03D-SPI-F004 Volume | 3D surface + reference | Deposit region | Calibrated physical frame | Volume | Rule-driven | Measurement + reference provenance | Surface + reference | Feature-scoped |
| 03D-SPI-F005 Offset | Surface + nominal | Pad/land/search region | Calibrated board frame | Offset | Rule-driven | Nominal + calibration provenance | Surface + nominal | Feature-scoped |
| 03D-SPI-F006 Shape | 3D surface | Deposit region | Calibrated board/pad frame | Shape descriptors | Rule-driven | Descriptor/algorithm provenance | Deterministic geometry | Feature-scoped |
| 03D-SPI-F007 Coplanarity | 3D surface + reference | Region/reference | Calibrated height frame | Coplanarity descriptor | Rule-driven | Reference/sampling provenance | Surface + reference | Feature-scoped |
| 03D-SPI-F008 BridgingRisk | 3D surface + topology | Inter-pad search region | Calibrated board frame | Finding/observation | Rule-driven | Topology + feature evidence | Surface + topology | Feature-scoped |

## Completeness rule

A feature is not implementation-ready merely because a name appears in the catalog. Its execution contract, parameter authority, invalid semantics, evidence/replay inputs and client interaction must be defined before production implementation.

## Qualification rule

“Candidate” capability means the platform knows the normalized concept. It does not mean a particular machine/model has been qualified to provide it.
