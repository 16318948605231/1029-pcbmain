# 3D SPI Quality and Evidence Specification

## Authority chain

Device inspection produces evidence-backed Result inputs. Platform authority remains:

Inspection → Result → Quality → Evidence → Replay → Release → History.

The device does not own final Release authority.

## Feature contribution

Each feature must declare its contribution class through an authoritative Quality rule:
- informational;
- review-required;
- quality-gating;
- release-relevant.

This document does not assign those classes to the eight features without authority.

## Finding versus decision

A Finding describes an inspection observation. A Quality decision interprets one or more Findings/Measurements under an authoritative rule. A BridgingRisk finding is not automatically a failed product.

## Evidence minimum

Evidence should bind device instance/configuration, feature ID/revision, Program/Recipe revision, acquisition identity, input-data identity, algorithm/version, parameter-set identity, measurement/finding identity and relevant calibration/reference/provenance.

## Replay

Replay is authoritative only when all required deterministic inputs and provenance are present. A live hardware call is not a replay substitute. Replay must preserve enough context to reproduce the feature evaluation or to prove why reproduction is not possible.

## History

Finalized Quality/Replay/Release authority is historical evidence. Recovery or re-execution creates a new current execution boundary and must not mutate finalized historical entries.

## Release

Release consumes platform Quality and Replay authority. A 3D SPI adapter cannot directly mark a product Released.

## Audit

Changes to feature parameters, algorithm revisions, calibration references, nominal geometry, topology context or acceptance rules must remain attributable and versioned according to the platform audit contract.

## Qualification

No statement here constitutes machine qualification, algorithm validation, metrology qualification or production acceptance.