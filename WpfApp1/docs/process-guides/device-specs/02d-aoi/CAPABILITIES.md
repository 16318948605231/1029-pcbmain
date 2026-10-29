# 2D AOI Capabilities

## Normalized inputs
image/camera acquisition; calibrated image coordinates; component/library/board context

## Capability rules

A capability is advertised only when the concrete device instance can supply the required input modality, calibration/context, and qualified output. Capability IDs are stable platform concepts; vendor names are not capability identities.

## Feature capability catalog
02D-AOI-F001 PresenceAbsence
02D-AOI-F002 PositionOffset
02D-AOI-F003 RotationOrientation
02D-AOI-F004 Polarity
02D-AOI-F005 MarkingPresence
02D-AOI-F006 SurfaceAppearance
02D-AOI-F007 VisibleSolderJoint
02D-AOI-F008 TracePattern
02D-AOI-F009 ForeignMaterial

## Capability states

- Available: supported and qualified for the configured device instance.
- Configurable: supported but dependent on recipe/context/qualification.
- Unavailable: not supported or required authority is missing.
- SimulationOnly: deterministic integration data exists without hardware qualification.

Unknown capability state must not be treated as Available.