# ICT Capabilities

## Normalized inputs
test program; fixture mapping; electrical stimulus and measurement channels

## Capability rules

A capability is advertised only when the concrete device instance can supply the required input modality, calibration/context, and qualified output. Capability IDs are stable platform concepts; vendor names are not capability identities.

## Feature capability catalog
ICT-F001 OpenCircuit
ICT-F002 ShortCircuit
ICT-F003 Resistance
ICT-F004 Capacitance
ICT-F005 Inductance
ICT-F006 Diode
ICT-F007 ComponentValue
ICT-F008 Continuity
ICT-F009 Isolation

## Capability states

- Available: supported and qualified for the configured device instance.
- Configurable: supported but dependent on recipe/context/qualification.
- Unavailable: not supported or required authority is missing.
- SimulationOnly: deterministic integration data exists without hardware qualification.

Unknown capability state must not be treated as Available.