# AsunImage 算法使用与 Benchmark 开发指导

> 2026-09-27 平台归位：当前职责与范围按[平台设计基线](<../../../00-baseline/PLATFORM-DESIGN-BASELINE.md>)及[所属指导目录](<../../README.md>)绑定。本页保留原ID与细化内容；原状态 `Normative` 仅作历史记录，精确契约/Owner/参数未获批前不作为生产实施准入。
- 文档 ID：`DEV-VIS-022A`
- 版本：`2.1.0`
- 状态：`DocMapped`
- 视觉库基线：项目内 AsunImage / HALCON 26.05；算子核对入口为 [`halcon算子手册/operators`](../../../../halcon算子手册/operators/)

## 1. Mandatory rule

HALCON operator、参数和返回值按适用官方 Reference Manual 与 AsunImage 公共签名正确编写，不能凭记忆猜测。AsunImage/DevExpress 不做依赖验证、兼容或授权审查；本指导要求验证的是本项目算法结果、鲁棒性和性能。

## 2. 历史算子研究与本项目候选

| Task | Verified operator | Evidence rule |
|---|---|---|
| Shape-based 2D localization | `find_shape_model` / `find_shape_models` | 当前目标版本 Reference + Golden benchmark |
| Subpixel edge | `edges_sub_pix` | 当前目标版本 Reference + repeatability benchmark |
| Ellipse fitting | `fit_ellipse_contour_xld` | 当前目标版本 Reference + residual benchmark |
| Local thresholding | `dyn_threshold` | 当前目标版本 Reference + illumination sweep |
| Camera calibration | `calibrate_cameras` | calibration qualification + independent validation poses |
| Stereo surface | `reconstruct_surface_stereo` | calibrated stereo setup + coverage/height benchmark |
| 3D global registration | `register_object_model_3d_global` | overlap/residual benchmark |

以下说明来自保留原链接的历史资料，不宣称已在本项目重验。实现前必须以项目内 HALCON 26.05 算子手册和 `ImageLibDotNet` 公共签名重新核对。MVTec documentation confirms `calibrate_cameras` performs a simultaneous minimization over the calibration data model, `fit_ellipse_contour_xld` fits XLD contours to ellipses/elliptic arcs and exposes robust fitting options, and multi-view stereo reconstruction requires a calibrated stereo setup; `reconstruct_surface_stereo` returns an ObjectModel3D. 

## 3. Algorithm selection procedure

For each problem record: candidate A/B/C, applicability, input-quality assumptions, robustness, parameter sensitivity, CPU/memory cost, multithreading behavior, determinism, diagnostics, fallback and reject conditions.

## 4. HALCON 3D rule

3D object models are not equivalent to metrology qualification. Registration, reconstruction and visualization quality must be separated from calibrated measurement quality. HALCON provides object-model functions including `FindSurfaceModel`, `ReconstructSurfaceStereo`, `RegisterObjectModel3dGlobal`, etc.; selection depends on task and qualification data, not operator popularity. 

## 5. Benchmark record

Every benchmark record must bind: HALCON exact version, CPU/GPU, input dataset hash, operator parameters, thread settings, ROI/bounding box, P50/P95/P99, peak memory, output quality metrics, failure count and reproducibility.


## 6. Implementation requirements

1. HALCON adapter must expose only the approved Vision Contract surface.
2. Operator selection records are versioned artifacts; application code does not embed an undocumented alternative route.
3. Benchmark instrumentation must be part of the implementation path, not a post-hoc manual measurement.
4. Any unverified operator/parameter blocks production implementation of that route; a Mock/Interface skeleton may be implemented without asserting API details.

## 7. Test requirements

- 业务代码使用的算子/签名与 AsunImage 公共接口及适用官方资料一致，不单独进行 AsunImage 依赖准入验证;
- nominal/boundary/adversarial Golden samples;
- repeatability and deterministic-output checks where required;
- parameter sweep and sensitivity analysis;
- P50/P95/P99, peak memory, cancellation and concurrency measurements;
- benchmark result hash and environment capture.

## 8. Forbidden implementation

- Do not guess HALCON operator names or parameters from model memory;
- do not silently replace a qualified route with a different operator;
- do not call HALCON from Domain/UI code;
- do not declare an operator “best” without the required benchmark and qualification evidence.
