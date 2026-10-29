# 3D AOI Client Workflow

## Workflow

Configure device → Select program/recipe → Prepare → Acquire → Inspect → Review findings/measurements → Commit Result → Quality → Replay → Release → History.

## Presentation

The client should expose readiness, active configuration, acquisition progress, current feature, result/finding list, evidence/review context, Quality authority, Replay/Release authority, and history/recovery state.

## Interaction

Teaching and parameter editing are scoped to the active feature and authorized recipe. ROI/geometry edits must identify the feature and preserve the applicable coordinate context.

## Unified projection

WPF presentation consumes the unified client projection. Device-specific workspace state is not read directly by the presentation shell.

## Safety and authority

Controls that require hardware/domain authority remain unavailable until their prerequisite state is known and valid. The UI must not fabricate thresholds or claim hardware qualification.