# Bare-Board PCB Inspection Capabilities

## Normalized inputs
registered board images/layers; CAD/net reference when authorized; calibrated geometry

## Capability rules

A capability is advertised only when the concrete device instance can supply the required input modality, calibration/context, and qualified output. Capability IDs are stable platform concepts; vendor names are not capability identities.

## Feature capability catalog
PCB-BARE-BOARD-F001 TraceOpen
PCB-BARE-BOARD-F002 TraceShort
PCB-BARE-BOARD-F003 PadDefect
PCB-BARE-BOARD-F004 HolePresence
PCB-BARE-BOARD-F005 HolePosition
PCB-BARE-BOARD-F006 AnnularRing
PCB-BARE-BOARD-F007 CopperPattern
PCB-BARE-BOARD-F008 SolderMask
PCB-BARE-BOARD-F009 Silkscreen
PCB-BARE-BOARD-F010 BoardOutline
PCB-BARE-BOARD-F011 ForeignMaterial

## Capability states

- Available: supported and qualified for the configured device instance.
- Configurable: supported but dependent on recipe/context/qualification.
- Unavailable: not supported or required authority is missing.
- SimulationOnly: deterministic integration data exists without hardware qualification.

Unknown capability state must not be treated as Available.