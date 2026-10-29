# 03D-SPI-F008 — Bridging Risk

## Purpose
Identify geometry/configuration evidence that may indicate a solder-paste bridging condition between adjacent intended deposits.

## Contract
- **Input:** qualified 3D paste surface data plus authoritative pad/land adjacency/topology context.
- **ROI / Region:** the pair/group of related pad regions and the authorized inter-pad search region.
- **Coordinate system:** calibrated board coordinate frame with topology traceability.
- **Pre-processing:** validate acquisition, registration, calibration and adjacency context.
- **Algorithm:** evaluate the authorized geometric/connectivity evidence for a potential bridge. The concrete rule/algorithm is device/recipe authority.
- **Output:** finding and supporting geometry/evidence; a production verdict is owned by Quality.

## Decision semantics
“Risk” is intentionally distinct from a confirmed manufacturing defect. The platform must preserve whether the output is an observation, finding, review-required condition or authoritative quality decision.

## Parameters
Adjacency source, search region, connectivity/geometry rule, confidence policy and acceptance rule require explicit IDs/revisions and authority sources.

## Boundary and failure cases
Missing topology, ambiguous adjacency, incomplete surface, invalid calibration, multiple candidate connections, algorithm non-evaluable and device fault require explicit states.

## Quality / Evidence / Replay
Evidence must retain the involved feature IDs, topology context, algorithm revision and input identity. Replay requires deterministic surface and topology evidence.

## UI / Program / Recipe
The UI should highlight the involved regions and expose the finding/evidence relationship without implying a final Release decision. Recipe changes are authorized and audited.

## Authority gates
Bridge definition, detection criteria, sensitivity/specificity, confidence semantics, tolerance and production acceptance: **Authoritative source required**.
