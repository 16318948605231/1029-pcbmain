# ICT Vendor Adapter Specification

## Responsibility

The adapter isolates vendor transport, SDK types, acquisition sequencing, proprietary formats, hardware status, and device-specific configuration from the platform contract.

## Platform-facing operations

- Connect / disconnect / readiness.
- Capability discovery.
- Acquisition or import of qualified device data.
- Device configuration identity and revision.
- Error normalization.
- Provenance/evidence capture.

## Non-responsibilities

The adapter does not own platform Quality, Replay, Release, History, or final product authority.

## External gates

Undocumented SDK APIs, safety behavior, exact hardware timing, performance limits, calibration procedures, and vendor-specific acceptance semantics remain external authority gates.

## Simulation

Simulation is permitted for deterministic integration and smoke coverage. Simulation success must never be represented as hardware qualification.