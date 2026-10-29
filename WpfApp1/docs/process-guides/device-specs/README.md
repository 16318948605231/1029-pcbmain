# Device Inspection Specifications

> 2026-09-27 用户范围确认：X-Ray/CT、ICT、FCT 暂缓，只保留入口作为当前规划范围，不新增详细开发文档或实现。目录内既有详细文件保留为历史资料，不作为当前开发队列。已完成的蚀刻后 PCB 光板检测项目等待用户后续提供。平台唯一入口为 [PROJECT_ENTRY.md](<../../../PROJECT_ENTRY.md>)。

This directory defines the device-oriented specification layer for the PCB/PCBA inspection platform.

设计关系：工艺目的 → 机型能力 → 功能/量测 → 工艺规则 → 结果/证据提交。质量处置、回放与投影分别成链，见[端到端链路](../END-TO-END-FLOWS.md)。

Every device family has its own subdirectory. Device documents specialize generic contracts in shared-modules/guidance/12-function-specs 与 process-guides/guidance/12-function-specs and never invent vendor SDK behavior, hardware timing, metrology tolerances, defect thresholds, or production acceptance criteria.

Initial families: 2D AOI, 3D AOI, 3D SPI, 2D X-Ray, 3D AXI/CT, Optical/Laser Metrology, ICT, FCT, Bare-Board PCB Inspection.

Capability documentation is not production qualification. Model-specific behavior, accuracy, repeatability, throughput, safety, algorithm performance, and acceptance thresholds require authoritative evidence.

Each device directory grows toward README.md, DEVICE_SPEC.md, CAPABILITIES.md, FEATURES.md, MEASUREMENTS.md, QUALITY.md, UI_WORKFLOW.md, VENDOR_ADAPTER.md, and qualification/evidence records.

## 制程与设备层的对应

本目录保留原机型/模态细项，受[制程目录](../README.md)约束，不能用2D/3D名称代替炉前/炉后等工艺定义。2D/3D AOI对应PG-017/018及适用装配工位；3D SPI对应PG-014；计量按PG-002/005/010/011等具体被测量组合；钢网对应PG-013。未来细化在对应PG内登记唯一Profile与契约链接，不复制第二份工艺判据。

X-Ray/CT、ICT、FCT和待交付蚀刻线路产品仅入口有效。其历史详细文件保持原内容，不作为本轮设计交付或工具的详细规格门槛。模板只用于已确定范围的机型，不能据模板自动扩展暂缓设备。
