# HALCON 24.11 Operator Verification Baseline

> 历史研究来源。本文只记录当时阅读的 HALCON 24.11 官方资料。本项目使用项目内 AsunImage / HALCON 26.05；本页不构成版本要求、26.05 行为或调用依据，也不证明本项目算法已验证。具体实现优先核对本地 [`halcon算子手册/operators`](../../halcon算子手册/operators/) 的 26.05 页面与消费项目 `ImageLibDotNet` 公共签名。
- 文档 ID：`REF-003`
- 版本：`1.0.0`
- 状态：`Reference`
- 日期：2026-09-18
- 当时研究资料版本：HALCON 24.11 family

## 已验证的官方资料入口

- HALCON documentation：`https://www.mvtec.com/products/halcon/documentation`
- `find_shape_model`：`https://www.mvtec.com/doc/halcon/2411/en/find_shape_model.html`
- `fit_ellipse_contour_xld`：`https://www.mvtec.com/doc/halcon/2411/en/fit_ellipse_contour_xld.html`
- `dyn_threshold`：`https://www.mvtec.com/doc/halcon/2411/en/dyn_threshold.html`
- `xyz_to_object_model_3d`：`https://www.mvtec.com/doc/halcon/2411/en/xyz_to_object_model_3d.html`
- `reconstruct_surface_stereo`：`https://www.mvtec.com/doc/halcon/2411/en/reconstruct_surface_stereo.html`
- Multi-view stereo overview：`https://www.mvtec.com/doc/halcon/2411/en/toc_3dreconstruction_multiviewstereo.html`
- `register_object_model_3d_global`：`https://www.mvtec.com/doc/halcon/2411/en/register_object_model_3d_global.html`
- HALCON 24.11.3 release notes：`https://www.mvtec.com/de/produkte/halcon/dokumentation/release-notes-2411-3`

> **MVTec 官方资料核验说明：** 本文链接均指向 MVTec 官方 HALCON 文档/Release Notes；2026-09-18 复核。

## Engineering interpretation

- 官方参考用于证明 operator/API 的存在、签名、输入输出、参数与版本范围；
- Golden Dataset + Benchmark 用于决定本项目默认路线、Fallback、参数和性能；
- Release Notes 用于检查已知 bug/fix 对目标算法的影响；
- 未经目标环境实测，不把任何 operator 标记为“最优”。
