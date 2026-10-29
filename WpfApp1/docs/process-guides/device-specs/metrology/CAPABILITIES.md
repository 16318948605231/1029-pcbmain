# Optical / Laser Metrology Capabilities

## Normalized inputs
calibrated point/edge/surface data; datum/reference geometry; traceable calibration context

## Capability rules

A capability is advertised only when the concrete device instance can supply the required input modality, calibration/context, and qualified output. Capability IDs are stable platform concepts; vendor names are not capability identities.

## Feature capability catalog
METROLOGY-F001 PointDistance
METROLOGY-F002 LineDistance
METROLOGY-F003 Angle
METROLOGY-F004 Diameter
METROLOGY-F005 Radius
METROLOGY-F006 Width
METROLOGY-F007 Height
METROLOGY-F008 Flatness
METROLOGY-F009 Parallelism
METROLOGY-F010 Perpendicularity
METROLOGY-F011 Position
METROLOGY-F012 Profile

## Capability states

- Available: supported and qualified for the configured device instance.
- Configurable: supported but dependent on recipe/context/qualification.
- Unavailable: not supported or required authority is missing.
- SimulationOnly: deterministic integration data exists without hardware qualification.

Unknown capability state must not be treated as Available.