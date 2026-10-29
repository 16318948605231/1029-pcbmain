# 3D AOI Capabilities

## Normalized inputs
2D image plus height/depth data; calibrated 3D coordinates; component/pad context

## Capability rules

A capability is advertised only when the concrete device instance can supply the required input modality, calibration/context, and qualified output. Capability IDs are stable platform concepts; vendor names are not capability identities.

## Feature capability catalog
03D-AOI-F001 PresenceAbsence
03D-AOI-F002 PositionOffset
03D-AOI-F003 RotationOrientation
03D-AOI-F004 Height
03D-AOI-F005 Area
03D-AOI-F006 Volume
03D-AOI-F007 Coplanarity
03D-AOI-F008 VisibleSolderGeometry
03D-AOI-F009 ComponentLift

## Capability states

- Available: supported and qualified for the configured device instance.
- Configurable: supported but dependent on recipe/context/qualification.
- Unavailable: not supported or required authority is missing.
- SimulationOnly: deterministic integration data exists without hardware qualification.

Unknown capability state must not be treated as Available.