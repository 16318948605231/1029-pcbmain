# 3D SPI Capabilities

## Normalized inputs
3D paste surface data; pad/land registration; stencil/board context where authorized

## Capability rules

A capability is advertised only when the concrete device instance can supply the required input modality, calibration/context, and qualified output. Capability IDs are stable platform concepts; vendor names are not capability identities.

## Feature capability catalog
03D-SPI-F001 PastePresence
03D-SPI-F002 PasteArea
03D-SPI-F003 PasteHeight
03D-SPI-F004 PasteVolume
03D-SPI-F005 PasteOffset
03D-SPI-F006 PasteShape
03D-SPI-F007 PasteCoplanarity
03D-SPI-F008 BridgingRisk

## Capability states

- Available: supported and qualified for the configured device instance.
- Configurable: supported but dependent on recipe/context/qualification.
- Unavailable: not supported or required authority is missing.
- SimulationOnly: deterministic integration data exists without hardware qualification.

Unknown capability state must not be treated as Available.