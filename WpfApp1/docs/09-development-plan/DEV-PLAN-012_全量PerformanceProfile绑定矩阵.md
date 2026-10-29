> 2026-09-27适用性：本页保留既有实现规划/注册信息。当前文档阶段以[平台设计基线](../00-baseline/PLATFORM-DESIGN-BASELINE.md)和SM/PG目录为准；本页历史状态、69项覆盖或波次不构成自动开工授权，逐切片核对Contract/Owner/验收。

# 全量 PerformanceProfile 绑定矩阵
- 文档 ID：`DEV-PLAN-012`
- 版本：`1.0.0`
- 状态：`Normative`
- 目的：防止 AI 以“高性能/低延迟”等模糊词自行选择性能目标。所有 69 个 FS 均绑定唯一 PerformanceProfile 标识。

> 本表只规定性能测试入口和字段完整性，不制造硬件相关数值。真实吞吐、P95/P99、内存、CPU/GPU、冷启动和恢复目标必须由目标机器/产品的批准 Profile 关闭。

| FS | PerformanceProfileId | 关注指标 | 必测维度 | 缺失时行为 |
|---|---|---|---|---|
| `FS-001` | `PF-FS-001` | < configurable; no polling loops | P50/P95/P99, peak memory, concurrency, queue/backpressure, cancellation, recovery | `Unverified/Blocker` for production optimization; scaffold/instrumentation only for implementation |
| `FS-002` | `PF-FS-002` | manifest build time benchmark | P50/P95/P99, peak memory, concurrency, queue/backpressure, cancellation, recovery | `Unverified/Blocker` for production optimization; scaffold/instrumentation only for implementation |
| `FS-003` | `PF-FS-003` | P95/P99 per node | P50/P95/P99, peak memory, concurrency, queue/backpressure, cancellation, recovery | `Unverified/Blocker` for production optimization; scaffold/instrumentation only for implementation |
| `FS-004` | `PF-FS-004` | commit latency/IO | P50/P95/P99, peak memory, concurrency, queue/backpressure, cancellation, recovery | `Unverified/Blocker` for production optimization; scaffold/instrumentation only for implementation |
| `FS-005` | `PF-FS-005` | queue latency/backpressure | P50/P95/P99, peak memory, concurrency, queue/backpressure, cancellation, recovery | `Unverified/Blocker` for production optimization; scaffold/instrumentation only for implementation |
| `FS-006` | `PF-FS-006` | multi-track throughput | P50/P95/P99, peak memory, concurrency, queue/backpressure, cancellation, recovery | `Unverified/Blocker` for production optimization; scaffold/instrumentation only for implementation |
| `FS-007` | `PF-FS-007` | ROI + pyramid benchmark | P50/P95/P99, peak memory, concurrency, queue/backpressure, cancellation, recovery | `Unverified/Blocker` for production optimization; scaffold/instrumentation only for implementation |
| `FS-008` | `PF-FS-008` | ROI size/threshold sweep | P50/P95/P99, peak memory, concurrency, queue/backpressure, cancellation, recovery | `Unverified/Blocker` for production optimization; scaffold/instrumentation only for implementation |
| `FS-009` | `PF-FS-009` | fit time vs contour points | P50/P95/P99, peak memory, concurrency, queue/backpressure, cancellation, recovery | `Unverified/Blocker` for production optimization; scaffold/instrumentation only for implementation |
| `FS-010` | `PF-FS-010` | ROI + scale sweep | P50/P95/P99, peak memory, concurrency, queue/backpressure, cancellation, recovery | `Unverified/Blocker` for production optimization; scaffold/instrumentation only for implementation |
| `FS-011` | `PF-FS-011` | feature budget | P50/P95/P99, peak memory, concurrency, queue/backpressure, cancellation, recovery | `Unverified/Blocker` for production optimization; scaffold/instrumentation only for implementation |
| `FS-012` | `PF-FS-012` | ROI reconstruction P95 | P50/P95/P99, peak memory, concurrency, queue/backpressure, cancellation, recovery | `Unverified/Blocker` for production optimization; scaffold/instrumentation only for implementation |
| `FS-013` | `PF-FS-013` | bounding box impact | P50/P95/P99, peak memory, concurrency, queue/backpressure, cancellation, recovery | `Unverified/Blocker` for production optimization; scaffold/instrumentation only for implementation |
| `FS-014` | `PF-FS-014` | N model scaling | P50/P95/P99, peak memory, concurrency, queue/backpressure, cancellation, recovery | `Unverified/Blocker` for production optimization; scaffold/instrumentation only for implementation |
| `FS-015` | `PF-FS-015` | tile/LOD and graph solve | P50/P95/P99, peak memory, concurrency, queue/backpressure, cancellation, recovery | `Unverified/Blocker` for production optimization; scaffold/instrumentation only for implementation |
| `FS-016` | `PF-FS-016` | calibration compute + load | P50/P95/P99, peak memory, concurrency, queue/backpressure, cancellation, recovery | `Unverified/Blocker` for production optimization; scaffold/instrumentation only for implementation |
| `FS-017` | `PF-FS-017` | P95 per measurement | P50/P95/P99, peak memory, concurrency, queue/backpressure, cancellation, recovery | `Unverified/Blocker` for production optimization; scaffold/instrumentation only for implementation |
| `FS-018` | `PF-FS-018` | analysis batch time | P50/P95/P99, peak memory, concurrency, queue/backpressure, cancellation, recovery | `Unverified/Blocker` for production optimization; scaffold/instrumentation only for implementation |
| `FS-019` | `PF-FS-019` | coverage compute | P50/P95/P99, peak memory, concurrency, queue/backpressure, cancellation, recovery | `Unverified/Blocker` for production optimization; scaffold/instrumentation only for implementation |
| `FS-020` | `PF-FS-020` | ROI-first P95 | P50/P95/P99, peak memory, concurrency, queue/backpressure, cancellation, recovery | `Unverified/Blocker` for production optimization; scaffold/instrumentation only for implementation |
| `FS-021` | `PF-FS-021` | ROI-first P95 | P50/P95/P99, peak memory, concurrency, queue/backpressure, cancellation, recovery | `Unverified/Blocker` for production optimization; scaffold/instrumentation only for implementation |
| `FS-022` | `PF-FS-022` | ROI-first P95 | P50/P95/P99, peak memory, concurrency, queue/backpressure, cancellation, recovery | `Unverified/Blocker` for production optimization; scaffold/instrumentation only for implementation |
| `FS-023` | `PF-FS-023` | ROI-first P95 | P50/P95/P99, peak memory, concurrency, queue/backpressure, cancellation, recovery | `Unverified/Blocker` for production optimization; scaffold/instrumentation only for implementation |
| `FS-024` | `PF-FS-024` | ROI-first P95 | P50/P95/P99, peak memory, concurrency, queue/backpressure, cancellation, recovery | `Unverified/Blocker` for production optimization; scaffold/instrumentation only for implementation |
| `FS-025` | `PF-FS-025` | ROI-first P95 | P50/P95/P99, peak memory, concurrency, queue/backpressure, cancellation, recovery | `Unverified/Blocker` for production optimization; scaffold/instrumentation only for implementation |
| `FS-026` | `PF-FS-026` | ROI-first P95 | P50/P95/P99, peak memory, concurrency, queue/backpressure, cancellation, recovery | `Unverified/Blocker` for production optimization; scaffold/instrumentation only for implementation |
| `FS-027` | `PF-FS-027` | ROI-first P95 | P50/P95/P99, peak memory, concurrency, queue/backpressure, cancellation, recovery | `Unverified/Blocker` for production optimization; scaffold/instrumentation only for implementation |
| `FS-028` | `PF-FS-028` | ROI-first P95 | P50/P95/P99, peak memory, concurrency, queue/backpressure, cancellation, recovery | `Unverified/Blocker` for production optimization; scaffold/instrumentation only for implementation |
| `FS-029` | `PF-FS-029` | local ROI + P95 | P50/P95/P99, peak memory, concurrency, queue/backpressure, cancellation, recovery | `Unverified/Blocker` for production optimization; scaffold/instrumentation only for implementation |
| `FS-030` | `PF-FS-030` | local ROI + P95 | P50/P95/P99, peak memory, concurrency, queue/backpressure, cancellation, recovery | `Unverified/Blocker` for production optimization; scaffold/instrumentation only for implementation |
| `FS-031` | `PF-FS-031` | local ROI + P95 | P50/P95/P99, peak memory, concurrency, queue/backpressure, cancellation, recovery | `Unverified/Blocker` for production optimization; scaffold/instrumentation only for implementation |
| `FS-032` | `PF-FS-032` | local ROI + P95 | P50/P95/P99, peak memory, concurrency, queue/backpressure, cancellation, recovery | `Unverified/Blocker` for production optimization; scaffold/instrumentation only for implementation |
| `FS-033` | `PF-FS-033` | local ROI + P95 | P50/P95/P99, peak memory, concurrency, queue/backpressure, cancellation, recovery | `Unverified/Blocker` for production optimization; scaffold/instrumentation only for implementation |
| `FS-034` | `PF-FS-034` | segment/ROI P95 | P50/P95/P99, peak memory, concurrency, queue/backpressure, cancellation, recovery | `Unverified/Blocker` for production optimization; scaffold/instrumentation only for implementation |
| `FS-035` | `PF-FS-035` | segment/ROI P95 | P50/P95/P99, peak memory, concurrency, queue/backpressure, cancellation, recovery | `Unverified/Blocker` for production optimization; scaffold/instrumentation only for implementation |
| `FS-036` | `PF-FS-036` | segment/ROI P95 | P50/P95/P99, peak memory, concurrency, queue/backpressure, cancellation, recovery | `Unverified/Blocker` for production optimization; scaffold/instrumentation only for implementation |
| `FS-037` | `PF-FS-037` | segment/ROI P95 | P50/P95/P99, peak memory, concurrency, queue/backpressure, cancellation, recovery | `Unverified/Blocker` for production optimization; scaffold/instrumentation only for implementation |
| `FS-038` | `PF-FS-038` | segment/ROI P95 | P50/P95/P99, peak memory, concurrency, queue/backpressure, cancellation, recovery | `Unverified/Blocker` for production optimization; scaffold/instrumentation only for implementation |
| `FS-039` | `PF-FS-039` | ROI/P95 | P50/P95/P99, peak memory, concurrency, queue/backpressure, cancellation, recovery | `Unverified/Blocker` for production optimization; scaffold/instrumentation only for implementation |
| `FS-040` | `PF-FS-040` | ROI/P95 | P50/P95/P99, peak memory, concurrency, queue/backpressure, cancellation, recovery | `Unverified/Blocker` for production optimization; scaffold/instrumentation only for implementation |
| `FS-041` | `PF-FS-041` | ROI/P95 | P50/P95/P99, peak memory, concurrency, queue/backpressure, cancellation, recovery | `Unverified/Blocker` for production optimization; scaffold/instrumentation only for implementation |
| `FS-042` | `PF-FS-042` | ROI/P95 | P50/P95/P99, peak memory, concurrency, queue/backpressure, cancellation, recovery | `Unverified/Blocker` for production optimization; scaffold/instrumentation only for implementation |
| `FS-043` | `PF-FS-043` | ROI/P95 | P50/P95/P99, peak memory, concurrency, queue/backpressure, cancellation, recovery | `Unverified/Blocker` for production optimization; scaffold/instrumentation only for implementation |
| `FS-044` | `PF-FS-044` | ROI-first + P95/P99 | P50/P95/P99, peak memory, concurrency, queue/backpressure, cancellation, recovery | `Unverified/Blocker` for production optimization; scaffold/instrumentation only for implementation |
| `FS-045` | `PF-FS-045` | ROI-first + P95/P99 | P50/P95/P99, peak memory, concurrency, queue/backpressure, cancellation, recovery | `Unverified/Blocker` for production optimization; scaffold/instrumentation only for implementation |
| `FS-046` | `PF-FS-046` | ROI-first + P95/P99 | P50/P95/P99, peak memory, concurrency, queue/backpressure, cancellation, recovery | `Unverified/Blocker` for production optimization; scaffold/instrumentation only for implementation |
| `FS-047` | `PF-FS-047` | ROI-first + P95/P99 | P50/P95/P99, peak memory, concurrency, queue/backpressure, cancellation, recovery | `Unverified/Blocker` for production optimization; scaffold/instrumentation only for implementation |
| `FS-048` | `PF-FS-048` | ROI-first + P95/P99 | P50/P95/P99, peak memory, concurrency, queue/backpressure, cancellation, recovery | `Unverified/Blocker` for production optimization; scaffold/instrumentation only for implementation |
| `FS-049` | `PF-FS-049` | ROI-first + P95/P99 | P50/P95/P99, peak memory, concurrency, queue/backpressure, cancellation, recovery | `Unverified/Blocker` for production optimization; scaffold/instrumentation only for implementation |
| `FS-050` | `PF-FS-050` | ROI-first + P95/P99 | P50/P95/P99, peak memory, concurrency, queue/backpressure, cancellation, recovery | `Unverified/Blocker` for production optimization; scaffold/instrumentation only for implementation |
| `FS-051` | `PF-FS-051` | ROI-first + P95/P99 | P50/P95/P99, peak memory, concurrency, queue/backpressure, cancellation, recovery | `Unverified/Blocker` for production optimization; scaffold/instrumentation only for implementation |
| `FS-052` | `PF-FS-052` | ROI-first + P95/P99 | P50/P95/P99, peak memory, concurrency, queue/backpressure, cancellation, recovery | `Unverified/Blocker` for production optimization; scaffold/instrumentation only for implementation |
| `FS-053` | `PF-FS-053` | ROI-first + P95/P99 | P50/P95/P99, peak memory, concurrency, queue/backpressure, cancellation, recovery | `Unverified/Blocker` for production optimization; scaffold/instrumentation only for implementation |
| `FS-054` | `PF-FS-054` | ROI-first + P95/P99 | P50/P95/P99, peak memory, concurrency, queue/backpressure, cancellation, recovery | `Unverified/Blocker` for production optimization; scaffold/instrumentation only for implementation |
| `FS-055` | `PF-FS-055` | ROI-first + P95/P99 | P50/P95/P99, peak memory, concurrency, queue/backpressure, cancellation, recovery | `Unverified/Blocker` for production optimization; scaffold/instrumentation only for implementation |
| `FS-056` | `PF-FS-056` | batch candidate + P95 | P50/P95/P99, peak memory, concurrency, queue/backpressure, cancellation, recovery | `Unverified/Blocker` for production optimization; scaffold/instrumentation only for implementation |
| `FS-057` | `PF-FS-057` | batch candidate + P95 | P50/P95/P99, peak memory, concurrency, queue/backpressure, cancellation, recovery | `Unverified/Blocker` for production optimization; scaffold/instrumentation only for implementation |
| `FS-058` | `PF-FS-058` | batch candidate + P95 | P50/P95/P99, peak memory, concurrency, queue/backpressure, cancellation, recovery | `Unverified/Blocker` for production optimization; scaffold/instrumentation only for implementation |
| `FS-059` | `PF-FS-059` | batch candidate + P95 | P50/P95/P99, peak memory, concurrency, queue/backpressure, cancellation, recovery | `Unverified/Blocker` for production optimization; scaffold/instrumentation only for implementation |
| `FS-060` | `PF-FS-060` | batch candidate + P95 | P50/P95/P99, peak memory, concurrency, queue/backpressure, cancellation, recovery | `Unverified/Blocker` for production optimization; scaffold/instrumentation only for implementation |
| `FS-061` | `PF-FS-061` | batch candidate + P95 | P50/P95/P99, peak memory, concurrency, queue/backpressure, cancellation, recovery | `Unverified/Blocker` for production optimization; scaffold/instrumentation only for implementation |
| `FS-062` | `PF-FS-062` | batch candidate + P95 | P50/P95/P99, peak memory, concurrency, queue/backpressure, cancellation, recovery | `Unverified/Blocker` for production optimization; scaffold/instrumentation only for implementation |
| `FS-063` | `PF-FS-063` | batch candidate + P95 | P50/P95/P99, peak memory, concurrency, queue/backpressure, cancellation, recovery | `Unverified/Blocker` for production optimization; scaffold/instrumentation only for implementation |
| `FS-064` | `PF-FS-064` | batch latency | P50/P95/P99, peak memory, concurrency, queue/backpressure, cancellation, recovery | `Unverified/Blocker` for production optimization; scaffold/instrumentation only for implementation |
| `FS-065` | `PF-FS-065` | batch latency | P50/P95/P99, peak memory, concurrency, queue/backpressure, cancellation, recovery | `Unverified/Blocker` for production optimization; scaffold/instrumentation only for implementation |
| `FS-066` | `PF-FS-066` | batch latency | P50/P95/P99, peak memory, concurrency, queue/backpressure, cancellation, recovery | `Unverified/Blocker` for production optimization; scaffold/instrumentation only for implementation |
| `FS-067` | `PF-FS-067` | batch latency | P50/P95/P99, peak memory, concurrency, queue/backpressure, cancellation, recovery | `Unverified/Blocker` for production optimization; scaffold/instrumentation only for implementation |
| `FS-068` | `PF-FS-068` | batch latency | P50/P95/P99, peak memory, concurrency, queue/backpressure, cancellation, recovery | `Unverified/Blocker` for production optimization; scaffold/instrumentation only for implementation |
| `FS-069` | `PF-FS-069` | batch latency | P50/P95/P99, peak memory, concurrency, queue/backpressure, cancellation, recovery | `Unverified/Blocker` for production optimization; scaffold/instrumentation only for implementation |

## 1. Profile 必须包含的字段

- ProfileId / Revision / ApplicableProduct / MachineClass / StationClass；
- workload definition、warm/cold condition、input size/ROI/FOV、batch/stream mode；
- throughput、latency P50/P95/P99、peak memory、CPU/GPU、queue depth、concurrency；
- timeout、cancel latency、restart/recovery budget；
- acceptance threshold、measurement method、sample count、confidence/reporting method；
- benchmark environment hash、software/driver/model/calibration versions。

## 2. AI 实施规则

1. 没有 Profile 数值时，AI 不得发明数值；可以先完成计时点、resource instrumentation、mock、contract 和测试 harness。
2. 不得以 UI 响应时间代替视觉/计量 pipeline latency。
3. 不得以单次最好值代替 P95/P99。
4. 不得通过降低覆盖、分母、采样或证据要求“优化”性能。
5. 性能优化后的语义结果必须回放一致或记录批准的非确定性来源。


## Blocker 与验收

- **Scope Freeze**：本计划只覆盖已登记的 FunctionSpec/PerformanceProfile；新增能力必须走变更控制。
- **Blocker**：缺 Contract/Schema、Owner/State、Profile、Golden/Replay、目标 API 或验收口径立即停止。
- **Test**：至少覆盖 Contract/Schema、正常、边界、失败/恢复、Replay/Golden、性能；适用时执行 HIL。
- **验收**：测试与性能证据必须与当前版本、配置、数据集和环境绑定；没有证据不得声明完成。

## Scope

覆盖 FS-001..FS-069 的 PerformanceProfile 绑定、度量字段、Benchmark harness、环境指纹和外部实测门禁；不伪造目标硬件性能数值。
