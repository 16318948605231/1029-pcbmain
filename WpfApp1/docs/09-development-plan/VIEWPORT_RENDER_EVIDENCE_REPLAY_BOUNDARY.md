# Viewport Render Runtime — Evidence / Replay Boundary

## Purpose

The viewport rendering path now has a vendor-neutral evidence boundary that can be consumed by engineering diagnostics, replay tooling, and future UI/render hosts.

The boundary is intentionally below WPF/DevExpress and above HALCON/hardware adapters.

```text
Input Events
    ↓
Composite / ROI / Tile Visibility
    ↓
Render WorkPlan
    ↓
Render Batch
    ↓
Render CommandStream
    ↓
Presentation Queue
    ↓
Presentation Execution
    ↓
IViewportRenderSink<TTile>
    ↓
Surface / Backbuffer Commit
    ↓
Evidence Manifest + Audit Trace
```

## Evidence layers

`ViewportRenderEvidenceRuntime` produces deterministic SHA-256 identities for logical render artifacts:

- Batch
- CommandStream
- Pipeline Frame
- Replay operation sequence
- Arbitrary deterministic diagnostic text

These hashes are logical evidence identifiers. They are not pixel hashes and do not replace future production image-golden verification.

`ViewportRenderEvidenceManifest` combines generation, submission sequence, dirty flags, batch metrics, frame metrics, and the logical artifact hashes into one stable diagnostic object.

`ViewportRenderEvidenceStore` retains a bounded monotonic history of manifests.

## Replay layers

`ViewportInputReplayRuntime` records framework-neutral input events and can replay them through `ViewportCompositeInputRuntime<TTile>`.

`ViewportReplaySessionRuntime` combines:

- input trace;
- render evidence manifests;
- presentation audit events.

It can export a compact JSON evidence bundle without introducing vendor-specific rendering dependencies.

## Continuous runtime integration

`ViewportContinuousFrameRuntime<TTile>` now exposes:

- `EvidenceHistory`
- `AuditTrace`

After every executed presentation result, the continuous runtime records the corresponding manifest and an ordered audit-stage event. The retained histories are bounded and reset with the presentation runtime.

## Vendor boundary

No Skia, WPF, DevExpress, HALCON, camera SDK, motion SDK, or PLC type is allowed into these evidence contracts.

A future Skia/WPF backend implements the existing `IViewportRenderSink<TTile>` contract and can consume the same command/evidence stream without changing the core viewport model.

## Verification

The repository smoke path includes:

- deterministic evidence hashing;
- replay-session determinism;
- bounded evidence history;
- bounded audit history;
- 300 numbered deterministic verification rounds;
- continuous presentation evidence integration.

Authoritative C# build/test execution remains an external verification step whenever the repository runner/toolchain is available.
