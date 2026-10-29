# Integration Checkpoint — Stage 73,600

> **状态声明（2026-10-28 审核补注）**：本文件记录**已移除的旧代码阶段**产物。所述实现（Program/Acquisition/Production/ROI/Quality/Results/Replay 统一客户端投影等）随 `c4e10cf` 的脚手架清理**已不存在于当前仓库**。本文件保留仅供追溯，**不作当前状态、实现完成度或生产资格证据**。当前仓库为纯文档状态，见 [CODE-BASE-01](OPEN-GATES.md)；实现须严格按对应模块指导冻结的契约新建工程。当前文档准备与审查结论见 [T2-REVIEW-LEDGER.md](../../T2-REVIEW-LEDGER.md)。

Product chain:
Program → Program Presentation → Acquisition → Production Execution → ROI → Quality → Results → Replay/Release → Home/Program/Inspection/Quality/Results unified client projection.

## Closed client boundaries

- Program state now projects canonical ProgramItems and selected-step detail.
- Invalid Program loads clear dependent Production/Acquisition/Quality/Replay/Release context before the client snapshot is published.
- Acquisition Preview carries real frame metadata/payload/fingerprint into the Inspection surface; Faulted Acquisition invalidates stale preview and blocks Production source access.
- Production exposes a separate high-frequency state/pulse channel.
- ROI exposes a separate raw and sequenced high-frequency pulse channel.
- Quality provides command gates, canonical Outcome/Severity filtering, selected-finding visibility, finding detail, and provider evaluation gate.
- Results provides current result state, bounded history, selected historical-run detail, and structured Replay/Release projection.
- Home/Program/Inspection/Quality/Results are composed into one vendor-neutral client content surface.
- Workspace navigation + command routing + content projection are unified in one client snapshot stream.
- Unified client snapshots carry a monotonic ProjectionSequence; stale asynchronous snapshots are rejected by ClientWorkspaceClientSnapshotFence.

## Acceptance evidence

Registered client Smoke families include Program, Acquisition, Production progress, ROI, Quality, Results, Replay/Release, unified Workspace Content, unified Client Projection, Snapshot Fence, and event-pulse boundaries.

New/modified Smoke sources in the 73,501–73,600 interval were statically checked for:
- 10 loop groups
- 100 rounds per group
- explicit round==100
- 10 actual Check(...) invocation sites
- balanced braces
- no TODO
- no NotImplementedException

## Verification boundary

This checkpoint records repository implementation and static source-structure evidence only. It does not claim authoritative local Build/Test/CI execution, DevExpress environment success, HALCON runtime/operator verification, camera/lighting/motion SDK verification, HIL, installer, or final customer release.

Open external/contract gates remain governed by docs/00-baseline/OPEN-GATES.md.

## Post-checkpoint continuation — 73,618–73,619

The implementation after the 73,600 checkpoint continued into the real WPF client shell:

- Acquisition Bind now requires explicit `CanBindAcquisition` permission in addition to Inspection workspace routing.
- WPF Shell binding validation now enforces the command-facade-only mutation boundary and checks duplicate XAML names.
- The Unified Client Projection remains the state source for Full Snapshot, Execution Pulse, and ROI Pulse presentation.
- These are implementation/static-audit results only; they do not replace the open DevExpress/HALCON/hardware/build/test gates.
