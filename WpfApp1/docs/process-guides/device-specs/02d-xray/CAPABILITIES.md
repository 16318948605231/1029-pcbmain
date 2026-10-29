# 2D X-Ray Capabilities

## Normalized inputs
radiographic image; board/component identity; calibrated projection context where available

## Capability rules

A capability is advertised only when the concrete device instance can supply the required input modality, calibration/context, and qualified output. Capability IDs are stable platform concepts; vendor names are not capability identities.

## Feature capability catalog
02D-XRAY-F001 InternalPresence
02D-XRAY-F002 Void
02D-XRAY-F003 SolderJointAppearance
02D-XRAY-F004 BGA_QFN_Inspection
02D-XRAY-F005 ForeignMaterial
02D-XRAY-F006 BridgeOrShortAppearance
02D-XRAY-F007 ComponentOrientationInternal

## Capability states

- Available: supported and qualified for the configured device instance.
- Configurable: supported but dependent on recipe/context/qualification.
- Unavailable: not supported or required authority is missing.
- SimulationOnly: deterministic integration data exists without hardware qualification.

Unknown capability state must not be treated as Available.