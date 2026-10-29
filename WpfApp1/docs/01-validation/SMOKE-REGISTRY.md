# Smoke Registry

| Smoke | Owner | Scope | Execution evidence |
|---|---|---|---|
| ProductionSessionProgressAcceptanceSmoke.Run100Stages | Asun.Platform.ClientIntegration | Ready → Running progress → Completed; Cancelled; Failed; Reset; target count; sequence; frame metadata; adapter routing | Source registered; execution not claimed |
| ClientProductionProgressPresentationSmoke.Run100Stages | Asun.Platform.ClientIntegration | Client-visible Production status/session/frame progress projection | Source registered; execution not claimed |
| ClientInspectionExecutionPresentationSmoke.Run100Stages | Asun.Platform.ClientIntegration | Program/status/progress/ROI/Acquisition/result presentation boundary | Source registered; execution not claimed |
| ClientInspectionExecutionSurfaceSmoke.Run100Stages | Asun.Platform.ClientIntegration | Unified Inspection execution surface; result/ROI/Acquisition availability projection | Source registered; execution not claimed |
| ClientInspectionExecutionCommandSmoke.Run100Stages | Asun.Platform.ClientIntegration | Inspection preview/run/cancel/reset/ROI command facade over existing workspace authority | Source registered; execution not claimed |
| ClientAcquisitionPreviewFaultSmoke.Run100Stages | Asun.Platform.ClientIntegration | Acquisition preview lifecycle, stale-preview invalidation, fault/recovery, metadata/fingerprint | Source registered; execution not claimed |
| ClientInspectionAcquisitionBindingEventSmoke.Run100Stages | Asun.Platform.ClientIntegration | Direct Acquisition binding event propagation and authority isolation | Source registered; execution not claimed |
| ClientInspectionAcquisitionPreviewSurfaceSmoke.Run100Stages | Asun.Platform.ClientIntegration | Inspection Surface raw Acquisition preview payload/metadata projection and stale-preview protection | Source registered; execution not claimed |
| ClientInspectionWorkspaceChangedSmoke.Run100Stages | Asun.Platform.ClientIntegration | Full Inspection snapshot change stream across Acquisition/Quality/History/Session boundaries | Source registered; execution not claimed |
| ClientResultsCommandSmoke.Run100Stages | Asun.Platform.ClientIntegration | Results workspace history-selection command facade over existing bounded Run History authority | Source registered; execution not claimed |
| ClientResultsSurfaceSmoke.Run100Stages | Asun.Platform.ClientIntegration | Unified current-result/history-selection surface over existing Result/Replay/Release/Run History projections | Source registered; execution not claimed |
| ClientReleaseReplaySurfaceSmoke.Run100Stages | Asun.Platform.ClientIntegration | Unified Replay identity/frame/release-readiness/artifact projection over existing Replay and Release authority | Source registered; execution not claimed |
| ClientWorkspaceContentSurfaceSmoke.Run100Stages | Asun.Platform.ClientIntegration | Unified Home/Program/Inspection/Quality/Results content projection over existing client authorities and routing | Source registered; execution not claimed |
| ClientWorkspaceClientSnapshotSmoke.Run100Stages | Asun.Platform.ClientIntegration | Single client snapshot entry point combining workspace selection, command routing, and content surfaces | Source registered; execution not claimed |
| ClientWorkspaceClientProjectionSmoke.Run100Stages | Asun.Platform.ClientIntegration | Subscribed client projection reacting to workspace navigation and Inspection state changes with lifecycle-safe snapshots | Source registered; execution not claimed |
| ClientWorkspaceClientSnapshotFenceSmoke.Run100Stages | Asun.Platform.ClientIntegration | Latest-wins client snapshot fence rejecting stale/equal projection sequences | Source registered; execution not claimed |
| ClientInspectionRoiPulseSmoke.Run100Stages | Asun.Platform.ClientIntegration | Dedicated high-frequency ROI pulse stream, lifecycle safety, and unified client projection bridge | Source registered; execution not claimed |
| ClientProgramSurfaceSmoke.Run100Stages | Asun.Platform.ClientIntegration | Unified Program snapshot/step/selection presentation over canonical Program presentation authority | Source registered; execution not claimed |
| ClientInspectionWorkspaceProgramItemsSmoke.Run100Stages | Asun.Platform.ClientIntegration | ProgramItems integration through Inspection Capture, including Invalid/Ready Program behavior | Source registered; execution not claimed |
| ClientProgramCommandSmoke.Run100Stages | Asun.Platform.ClientIntegration | Program step selection command facade and authoritative Selection/Surface event propagation | Source registered; execution not claimed |
| ClientInspectionWorkflowIntegritySmoke.Run100Stages | Asun.Platform.ClientIntegration | Cross-module client-state integrity: Program/Acquisition/Production/ROI/Quality/Results/Replay/Release coherence | Source registered; execution not claimed |
| ClientInspectionSnapshotValidationSmoke.Run100Stages | Asun.Platform.ClientIntegration | Validated full Inspection snapshot boundary across Program/Acquisition/Preview/Selection/Reset states | Source registered; execution not claimed |
| ClientQualityCommandSmoke.Run100Stages | Asun.Platform.ClientIntegration | Quality finding selection/clear command facade over existing Quality workspace authority | Source registered; execution not claimed |
| ClientQualitySurfaceSmoke.Run100Stages | Asun.Platform.ClientIntegration | Unified Quality result/finding/selection projection over existing validated Quality authority | Source registered; execution not claimed |

## Structural contract

- 10 loop groups
- 100 rounds per group
- explicit round==100
- 10 actual Check(...) call sites
- non-tautological assertions
- no TODO
- no NotImplementedException

| ClientInspectionAcquisitionCommandSmoke.Run100Stages | Asun.Platform.ClientIntegration | Inspection Acquisition command boundary: workspace routing, source binding, Ready-state publication, unified projection visibility | Source registered; execution not claimed |
