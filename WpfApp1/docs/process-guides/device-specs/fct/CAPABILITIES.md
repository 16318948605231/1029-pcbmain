# FCT Capabilities

## Normalized inputs
authorized functional test sequence; DUT state; external instrument and protocol data

## Capability rules

A capability is advertised only when the concrete device instance can supply the required input modality, calibration/context, and qualified output. Capability IDs are stable platform concepts; vendor names are not capability identities.

## Feature capability catalog
FCT-F001 PowerOn
FCT-F002 Communication
FCT-F003 InterfaceResponse
FCT-F004 DigitalIO
FCT-F005 AnalogResponse
FCT-F006 ProtocolExchange
FCT-F007 FunctionalSequence
FCT-F008 SafetyInterlock

## Capability states

- Available: supported and qualified for the configured device instance.
- Configurable: supported but dependent on recipe/context/qualification.
- Unavailable: not supported or required authority is missing.
- SimulationOnly: deterministic integration data exists without hardware qualification.

Unknown capability state must not be treated as Available.