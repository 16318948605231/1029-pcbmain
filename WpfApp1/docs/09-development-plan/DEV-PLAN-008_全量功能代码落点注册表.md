> 2026-09-27适用性：本页保留既有实现规划/注册信息。当前文档阶段以[平台设计基线](../00-baseline/PLATFORM-DESIGN-BASELINE.md)和SM/PG目录为准；本页历史状态、69项覆盖或波次不构成自动开工授权，逐切片核对Contract/Owner/验收。

# 全量功能代码落点注册表
- 文档 ID：`DEV-PLAN-008`
- 版本：`2.0.0`
- 状态：`Normative`

本表是 69 个功能规格到代码/测试/UI/性能工作的唯一任务入口。实际仓库如存在同义实现，必须用 ADR 绑定，不允许并行建立第二套能力。

| FS | Domain | Capability | Guide | Project | Canonical Port | Page | Algorithm baseline | Performance | WorkPackage |
|---|---|---|---|---|---|---|---|---|---|
| FS-001 | Platform | Identity Resolution | DEV-PLT-010 | Asun.Platform.Core | IIdentityResolver | UI-PCS-001 | policy + conflict resolution | < configurable; no polling loops  | WP-03 |
| FS-002 | Platform | Effective Runtime Manifest | DEV-PLT-010 | Asun.Platform.Core | IEffectiveRuntimeManifestBuilder | UI-PCS-009 | graph closure + hash | manifest build time benchmark  | WP-04 |
| FS-003 | Platform | Pipeline execution | DEV-PLT-011 | Asun.Platform.Core | IPipelineExecutor | UI-PCS-014 | DAG orchestrator | P95/P99 per node  | WP-06 |
| FS-004 | Platform | Evidence commit | DEV-PLT-012 | Asun.Platform.Core | IEvidenceCommitService | UI-PCS-013 | CAS + idempotent commit | commit latency/IO  | WP-05 |
| FS-005 | Platform | Cross-module event | DEV-PLT-013 | Asun.Platform.Core | ICrossModuleEventService | UI-PCS-014 | at-least-once + idempotency | queue latency/backpressure  | WP-02 |
| FS-006 | Platform | Board flow | DEV-PLT-014 | Asun.Platform.Core | IBoardFlowCoordinator | UI-PCS-001 | state/lease model | multi-track throughput  | WP-03 |
| FS-007 | Vision | Shape localization | DEV-VIS-021 | Asun.Vision.Halcon | IShapeLocalizer | UI-PCS-002 | find_shape_model | ROI + pyramid benchmark  | WP-09 |
| FS-008 | Vision | Subpixel edge extraction | DEV-VIS-025 | Asun.Vision.Halcon | ISubpixelEdgeExtractor | UI-PCS-002 | edges_sub_pix | ROI size/threshold sweep  | WP-09 |
| FS-009 | Vision | Ellipse/circle fit | DEV-VIS-025 | Asun.Vision.Halcon | IEllipseCircleFitter | UI-PCS-006 | fit_ellipse_contour_xld or alternative fit | fit time vs contour points  | WP-09 |
| FS-010 | Vision | Local segmentation | DEV-VIS-026 | Asun.Vision.Halcon | ILocalSegmenter | UI-PCS-002 | dyn_threshold / local candidate | ROI + scale sweep  | WP-09 |
| FS-011 | Vision | 2D candidate scoring | DEV-VIS-026 | Asun.Vision.Halcon | ICandidateScoring | UI-PCS-002 | rule + feature score | feature budget  | WP-09 |
| FS-012 | Vision | 3D HeightField build | DEV-VIS-027 | Asun.Vision.Halcon | IHeightFieldBuilder | UI-PCS-002 | sensor-specific reconstruction + xyz_to_object_model_3d as needed | ROI reconstruction P95  | WP-09 |
| FS-013 | Vision | Stereo surface reconstruction | DEV-VIS-027 | Asun.Vision.Halcon | IStereoSurfaceReconstructor | UI-PCS-002 | reconstruct_surface_stereo | bounding box impact  | WP-10 |
| FS-014 | Vision | 3D registration | DEV-VIS-028 | Asun.Vision.Halcon | IObjectModel3dRegistrar | UI-PCS-002 | register_object_model_3d_global/pair | N model scaling  | WP-10 |
| FS-015 | Vision | Multi-FOV stitch | DEV-VIS-029 | Asun.Vision.Halcon | IMultiFovStitch | UI-PCS-002 | position graph + image/geometry fusion | tile/LOD and graph solve  | WP-07 |
| FS-016 | Metrology | Calibration | DEV-MET-030 | Asun.Metrology.Core | ICalibrationService | UI-PCS-007 | target solve + validation | calibration compute + load  | WP-08 |
| FS-017 | Metrology | Feature measurement | DEV-MET-031 | Asun.Metrology.Core | IFeatureMeasurementService | UI-PCS-006 | edge/fit/distance/relationship | P95 per measurement  | WP-08 |
| FS-018 | Metrology | Uncertainty budget | DEV-MET-033 | Asun.Metrology.Core | IUncertaintyBudgetEvaluator | UI-PCS-006 | component budget + statistical tests | analysis batch time  | WP-08 |
| FS-019 | Metrology | Coverage calculation | DEV-MET-034 | Asun.Metrology.Core | ICoverageCalculator | UI-PCS-006 | feature + intra-feature + sampling | coverage compute  | WP-08 |
| FS-020 | PCB | Pattern width/space | DEV-DOM-050A | Asun.Domain.Pcb | IPatternWidthSpace | UI-PCS-015 | design ROI + edge measurement | ROI-first P95  | WP-15 |
| FS-021 | PCB | Pad geometry | DEV-DOM-050A | Asun.Domain.Pcb | IPadGeometry | UI-PCS-015 | contour/fit + reference | ROI-first P95  | WP-15 |
| FS-022 | PCB | Surface defect candidate | DEV-DOM-050A | Asun.Domain.Pcb | ISurfaceDefectCandidate | UI-PCS-015 | local segmentation + feature scoring | ROI-first P95  | WP-15 |
| FS-023 | PCB | Drill diameter | DEV-DOM-050B | Asun.Domain.Pcb | IDrillDiameter | UI-PCS-015 | edge/ellipse/circle fit | ROI-first P95  | WP-15 |
| FS-024 | PCB | Drill position | DEV-DOM-050B | Asun.Domain.Pcb | IDrillPosition | UI-PCS-015 | registration + coordinate transform | ROI-first P95  | WP-15 |
| FS-025 | PCB | Laser via opening | DEV-DOM-050C | Asun.Domain.Pcb | ILaserViaOpening | UI-PCS-015 | local contour fit | ROI-first P95  | WP-15 |
| FS-026 | PCB | Layer registration | DEV-DOM-050D | Asun.Domain.Pcb | ILayerRegistration | UI-PCS-015 | multi-reference transform + residual | ROI-first P95  | WP-15 |
| FS-027 | PCB | Solder mask defect | DEV-DOM-050D | Asun.Domain.Pcb | ISolderMaskDefect | UI-PCS-015 | surface segmentation + template/reference | ROI-first P95  | WP-15 |
| FS-028 | PCB | Final AVI | DEV-DOM-050D | Asun.Domain.Pcb | IFinalAvi | UI-PCS-015 | candidate detection + read-only review recommendation | ROI-first P95  | WP-15 |
| FS-029 | HDI | Layer stack validation | DEV-DOM-051A | Asun.Domain.Hdi | ILayerStackValidation | UI-PCS-016 | reference graph + version/hash | local ROI + P95  | WP-16 |
| FS-030 | HDI | Build-up layer target | DEV-DOM-051A | Asun.Domain.Hdi | IBuildUpLayerTarget | UI-PCS-016 | layer revision + geometry | local ROI + P95  | WP-16 |
| FS-031 | HDI | Laser via metrology | DEV-DOM-051B | Asun.Domain.Hdi | ILaserViaMetrology | UI-PCS-016 | local contour + fit | local ROI + P95  | WP-16 |
| FS-032 | HDI | Fine line/space | DEV-DOM-051B | Asun.Domain.Hdi | IFineLineSpace | UI-PCS-016 | subpixel edge + design reference | local ROI + P95  | WP-16 |
| FS-033 | HDI | HDI metrology | DEV-DOM-051B | Asun.Domain.Hdi | IHDIMetrology | UI-PCS-006 | relationship measurement + uncertainty | local ROI + P95  | WP-16 |
| FS-034 | FPC | R2R coordinate | DEV-DOM-052A | Asun.Domain.Fpc | IR2RCoordinate | UI-PCS-016 | WebCoordinateReference + fitted correction | segment/ROI P95  | WP-16 |
| FS-035 | FPC | NonRigid local transform | DEV-DOM-052A | Asun.Domain.Fpc | INonRigidTransform | UI-PCS-016 | local deformation model + residual | segment/ROI P95  | WP-16 |
| FS-036 | FPC | Coverlay inspection | DEV-DOM-052B | Asun.Domain.Fpc | ICoverlayInspection | UI-PCS-016 | design ROI + segmentation | segment/ROI P95  | WP-16 |
| FS-037 | FPC | Stiffener inspection | DEV-DOM-052B | Asun.Domain.Fpc | IStiffenerInspection | UI-PCS-016 | geometry + surface candidate | segment/ROI P95  | WP-16 |
| FS-038 | FPC | Bend region | DEV-DOM-052B | Asun.Domain.Fpc | IBendRegion | UI-PCS-016 | local frame + admissibility | segment/ROI P95  | WP-16 |
| FS-039 | Stencil | Aperture geometry | DEV-DOM-054A | Asun.Domain.Stencil | IApertureGeometry | UI-PCS-017 | 2D contour + 3D surface | ROI/P95  | WP-17 |
| FS-040 | Stencil | Stencil thickness | DEV-DOM-054A | Asun.Domain.Stencil | IStencilThickness | UI-PCS-017 | 3D metrology + calibration | ROI/P95  | WP-17 |
| FS-041 | Stencil | Wall condition | DEV-DOM-054A | Asun.Domain.Stencil | IWallCondition | UI-PCS-017 | 3D profile + residual | ROI/P95  | WP-17 |
| FS-042 | Stencil | Blocked aperture | DEV-DOM-054B | Asun.Domain.Stencil | IBlockedAperture | UI-PCS-017 | height/surface/region candidate | ROI/P95  | WP-17 |
| FS-043 | Stencil | Maintenance advice | DEV-DOM-054B | Asun.Domain.Stencil | IMaintenanceAdvice | UI-PCS-017 | trend + rule-based evidence | ROI/P95  | WP-17 |
| FS-044 | SPI | 3D acquisition quality | DEV-DOM-055A | Asun.Domain.Spi | I3DAcquisitionQuality | UI-PCS-018 | sensor validity + ValidMask | ROI-first + P95/P99  | WP-18 |
| FS-045 | SPI | Reference plane | DEV-DOM-055B | Asun.Domain.Spi | IReferencePlane | UI-PCS-018 | local plane fit + residual | ROI-first + P95/P99  | WP-18 |
| FS-046 | SPI | Pad target generation | DEV-DOM-055B | Asun.Domain.Spi | IPadTargetGeneration | UI-PCS-019 | ManufacturingGeometry/PAD + local frame | ROI-first + P95/P99  | WP-18 |
| FS-047 | SPI | Paste segmentation | DEV-DOM-055C | Asun.Domain.Spi | IPasteSegmentation | UI-PCS-018 | local/global segmentation candidates | ROI-first + P95/P99  | WP-18 |
| FS-048 | SPI | Paste volume | DEV-DOM-055C | Asun.Domain.Spi | IPasteVolume | UI-PCS-018 | integral over valid surface | ROI-first + P95/P99  | WP-18 |
| FS-049 | SPI | Paste area | DEV-DOM-055C | Asun.Domain.Spi | IPasteArea | UI-PCS-018 | projected region measurement | ROI-first + P95/P99  | WP-18 |
| FS-050 | SPI | Paste height | DEV-DOM-055C | Asun.Domain.Spi | IPasteHeight | UI-PCS-018 | max/percentile/robust height metrics | ROI-first + P95/P99  | WP-18 |
| FS-051 | SPI | Paste offset | DEV-DOM-055C | Asun.Domain.Spi | IPasteOffset | UI-PCS-018 | centroid/reference relation | ROI-first + P95/P99  | WP-18 |
| FS-052 | SPI | Paste shape | DEV-DOM-055C | Asun.Domain.Spi | IPasteShape | UI-PCS-018 | contour descriptors | ROI-first + P95/P99  | WP-18 |
| FS-053 | SPI | SPI rule evaluation | DEV-DOM-055D | Asun.Domain.Spi | ISPIRuleEvaluation | UI-PCS-018 | measurement thresholds + quality gating | ROI-first + P95/P99  | WP-18 |
| FS-054 | SPI | SPC | DEV-DOM-055D | Asun.Domain.Spi | ISPC | UI-PCS-008 | subgroup + denominator + watermark | ROI-first + P95/P99  | WP-18 |
| FS-055 | SPI | Printer feedback | DEV-DOM-055D | Asun.Domain.Spi | IPrinterFeedback | UI-PCS-018 | proposal → command → applied → effect | ROI-first + P95/P99  | WP-18 |
| FS-056 | AOI | CAD/PnP target generation | DEV-DOM-057A | Asun.Domain.Aoi | ICADPnPTargetGeneration | UI-PCS-012 | reference binding + target synthesis | batch candidate + P95  | WP-19 |
| FS-057 | AOI | Component presence | DEV-DOM-057B | Asun.Domain.Aoi | IComponentPresence | UI-PCS-020 | ROI + region/candidate score | batch candidate + P95  | WP-19 |
| FS-058 | AOI | Component identity | DEV-DOM-057B | Asun.Domain.Aoi | IComponentIdentity | UI-PCS-020 | PackageLibrary + visual features | batch candidate + P95  | WP-19 |
| FS-059 | AOI | Polarity/orientation | DEV-DOM-057B | Asun.Domain.Aoi | IPolarityOrientation | UI-PCS-020 | mark/feature alignment | batch candidate + P95  | WP-19 |
| FS-060 | AOI | Pin/lead inspection | DEV-DOM-057B | Asun.Domain.Aoi | IPinLeadInspection | UI-PCS-020 | edge/region + geometry | batch candidate + P95  | WP-19 |
| FS-061 | AOI | OCR/marking | DEV-DOM-057B | Asun.Domain.Aoi | IOCRMarking | UI-PCS-020 | OCR candidate + confidence/review | batch candidate + P95  | WP-19 |
| FS-062 | AOI | Solder joint post-reflow | DEV-DOM-057C | Asun.Domain.Aoi | ISolderJointPostReflow | UI-PCS-020 | geometry/surface candidate + review | batch candidate + P95  | WP-19 |
| FS-063 | AOI | Review/rework | DEV-DOM-057D | Asun.Domain.Aoi | IReviewRework | UI-PCS-005 | evidence-first UI + state machine | batch candidate + P95  | WP-19 |
| FS-064 | Quality/AI | SPC chart | DEV-DOM-058A | Asun.Domain.Quality | ISPCChart | UI-PCS-008 | MetricDefinition + subgroup rules | batch latency  | WP-20 |
| FS-065 | Quality/AI | Cross-process correlation | DEV-DOM-058B | Asun.Domain.Quality | ICrossProcessCorrelation | UI-PCS-021 | identity/time/window join + statistics | batch latency  | WP-20 |
| FS-066 | Quality/AI | Disposition projection | DEV-AI-063 | Asun.Domain.Quality | IDispositionProjection | UI-PCS-021 | committed facts + quality plan | batch latency  | WP-20 |
| FS-067 | Quality/AI | AI assisted review | DEV-AI-061 | Asun.Domain.Quality | IAIAssistedReview | UI-PCS-005 | embedding/retrieval/ranking with evidence | batch latency  | WP-21 |
| FS-068 | Quality/AI | Program synthesis | DEV-AI-062 | Asun.Platform.Core | IProgramSynthesis | UI-PCS-012 | geometry + library + rules → draft | batch latency  | WP-21 |
| FS-069 | Quality/AI | AI validation | DEV-AI-063 | Asun.Platform.Core | IAIValidation | UI-PCS-014 | held-out dataset + confidence intervals | batch latency  | WP-21 |

## 1. 通用代码任务顺序

`Contract/Port → Validation → Core/Algorithm → Quality Gate → Evidence/Provenance → Application integration → UI projection → Golden/Replay → Benchmark → Fault recovery → Audit/Manifest`。

## 2. Parallelism

不同 FS 在 Contract 边界明确且没有共享写入冲突时可并行；任何涉及同一 Schema/Owner/AuthoritySource 的任务必须串行完成 Contract 变更后再并行消费者。

## 3. No-drift rule

任务执行者不得自行添加通用模型、第二 Store、隐藏参数、未经验证 HALCON/DevExpress API 或新的生产 Decision Producer。
