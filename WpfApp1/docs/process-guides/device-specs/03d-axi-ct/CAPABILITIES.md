# 3D AXI / CT Capabilities

## Normalized inputs
reconstructed volume/slices; reconstruction metadata; calibrated 3D coordinate context

## Capability rules

A capability is advertised only when the concrete device instance can supply the required input modality, calibration/context, and qualified output. Capability IDs are stable platform concepts; vendor names are not capability identities.

## Feature capability catalog
03D-AXI-CT-F001 InternalPresence
03D-AXI-CT-F002 VoidVolume
03D-AXI-CT-F003 VoidDistribution
03D-AXI-CT-F004 SolderJoint3DGeometry
03D-AXI-CT-F005 BGAInspection
03D-AXI-CT-F006 QFNInspection
03D-AXI-CT-F007 ForeignMaterial
03D-AXI-CT-F008 InternalStructuralDefect

## Capability states

- Available: supported and qualified for the configured device instance.
- Configurable: supported but dependent on recipe/context/qualification.
- Unavailable: not supported or required authority is missing.
- SimulationOnly: deterministic integration data exists without hardware qualification.

Unknown capability state must not be treated as Available.