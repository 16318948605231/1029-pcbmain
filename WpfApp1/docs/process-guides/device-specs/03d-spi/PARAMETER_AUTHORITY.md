# 3D SPI Parameter Authority

## Parameter identity

Every parameter that can affect inspection behavior or production decisions requires:
- stable parameter ID;
- feature association;
- data type/unit;
- current value;
- revision;
- source/authority;
- effective scope;
- dependency list;
- audit/version metadata where required.

## Parameter classes

### Acquisition
Sensor/device settings supplied by the concrete adapter. Exact fields and limits are hardware/vendor authority.

### Geometry
ROI, pad/land reference, nominal geometry, topology and exclusion regions. Source and coordinate frame must be explicit.

### Algorithm
Algorithm revision and algorithm-specific parameters. Production behavior requires a qualified algorithm source.

### Measurement
Reference plane, filtering, sampling and normalization parameters. Numeric semantics require authoritative metrology definitions.

### Decision
Thresholds, review criteria and Quality contribution. These are production authority and cannot be inferred from generic 3D SPI knowledge.

## Default-value rule

A displayed device or software default is descriptive until an authoritative source makes it a production default. A missing default is preferable to a fabricated production value.

## Invalid-value rule

Out-of-range, incompatible or missing parameters must block or mark the feature non-evaluable according to the authoritative execution contract. They must not silently clamp into a production value unless that behavior is itself specified and qualified.

## Change propagation

Parameter changes must invalidate or version the affected Program/Recipe and downstream evidence according to platform policy. Historical results retain the parameter revision that produced them.

## Open authority

No numeric parameter ranges, tolerances, confidence limits or production thresholds are defined in this document.
