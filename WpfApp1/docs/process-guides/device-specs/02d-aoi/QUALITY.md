# 2D AOI Quality and Evidence Specification

## Authority chain

Device inspection produces evidence-backed Result inputs. Platform authority remains:

Inspection → Result → Quality → Replay → Release → History

## Evidence minimum

Capture device instance/configuration, feature ID/revision, program/recipe revision, acquisition identity, input-data identity, algorithm/version, measurement/finding identity, and relevant calibration/provenance.

## Quality contribution

Each feature must declare whether it is informational, review-required, quality-gating, or release-relevant according to an authoritative domain rule. This document does not invent those rules.

## Replay

Replay is authoritative only when all required deterministic inputs and provenance are present. A live hardware call is not a substitute for captured replay evidence.

## Release

A device cannot directly mark a product Released. Release consumes the platform Quality and Replay authority state.

## Audit

Changes to feature parameters, algorithm revisions, calibration references, or acceptance rules must remain attributable and versioned where the platform audit contract requires it.