# 3D SPI Device Specification

## Scope
3D SPI provides solder-paste inspection before component placement through qualified 3D surface data. The platform consumes normalized acquisition and inspection contracts; proprietary transport and SDK details remain behind the adapter.

## Device boundary
The device family owns acquisition-specific data production and device configuration. The platform owns normalized inspection execution, Result, Quality, Evidence, Replay, Release and History authority. A concrete adapter is responsible for translating the vendor/device contract into the platform boundary.

## Lifecycle
Configure → Prepare → Acquire → Inspect → Review → Commit → Quality → Replay → Release → History.

Interrupted execution additionally follows the platform Reset/Recovery contract. Recovery must not mutate finalized historical authority.

## Required context
Product/program identity, device identity/configuration revision, acquisition/session identity, calibration/coordinate context, feature/recipe revision, operator/automation identity, evidence provenance, and parameter-set identity where applicable.

## Input model
The normalized 3D SPI input is a qualified surface representation plus the board/pad/land context required by the active feature. Exact sensor format, sampling topology, scan timing and vendor serialization remain device-specific.

## ROI and region model
ROI/Region is feature-owned. A feature must state whether its region is:
- nominal geometry;
- search region;
- deposit region;
- reference region;
- exclusion region;
- topology/adjacency region.

The concrete geometry source and edit authority belong to Program/Recipe semantics.

## Coordinate and calibration model
Every physical measurement identifies its coordinate/reference frame and calibration identity. Raw sensor coordinates are not production coordinates by implication. Calibration validity is an execution prerequisite for measurements that depend on physical conversion.

## Pre-processing boundary
Acquisition integrity, registration, calibration validity and region validity are prerequisite checks. Device/model-specific denoising, filtering, surface reconstruction and artifact removal require qualified algorithm authority and must be versioned when they affect production results.

## Algorithm boundary
Feature algorithms are identified by stable feature identity plus algorithm revision. Vendor algorithm names are not platform contracts unless explicitly mapped through an adapter/qualification record.

## Result boundary
Feature results normalize into the platform Result model and link to evidence/provenance. Findings and measurements remain distinguishable from Quality and Release authority.

## Failure semantics
Acquisition failure, device-not-ready, calibration-invalid, input-invalid, feature-not-configured, algorithm-not-evaluable, algorithm-failed, review-required and successful evaluation must remain distinguishable. Exact serialized states come from authoritative domain contracts.

## Quality / Evidence / Replay / Release
The device supplies inputs to the platform authority chain:
Inspection → Result → Quality → Evidence → Replay → Release → History.

The device cannot directly publish final Quality or Release authority.

## Program / Recipe
Program identifies the inspection workflow. Recipe revision identifies the concrete feature/parameter configuration used for an execution. Parameter changes that affect results must remain traceable to the resulting Result/Evidence/History records.

## Hardware authority
Safety interlocks, sensor behavior, scan/motion sequencing, hardware limits, vendor SDK semantics, calibration procedures and exact acquisition timing are external authority gates and are not invented here.

## Qualification
Accuracy, repeatability, throughput, defect sensitivity/specificity, false-call behavior, calibration validity and acceptance thresholds require qualified evidence. See QUALIFICATION_GATES.md.