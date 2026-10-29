# 独立模块目录索引

本文件是52个独立模块的快速导航，同时是各模块原专属会话的唯一登记处（取代原 SESSION-REGISTRY.md）。"原专属会话"列记录该模块在全项目研发周期内复用的专属会话 ID，"指导核实"列为该模块开发指导的核实状态。每个模块的详细开发指导位于对应子目录的 `DEVELOPMENT-GUIDE.md`，指导文件本身是实现的唯一权威。

## 平台基础能力（18项）

| ID | 目录 | 职责摘要 | 原专属会话 | 指导核实 |
|---|---|---|---|---|
| IM-002 | [configuration](configuration/) | 配置读写、版本化、迁移、Schema校验 | `01a10306-e17f-7fd0-b6ff-efa191bb2fac` | verified |
| IM-003 | [localization](localization/) | zh-CN/zh-TW/en-US 三语动态切换 | `01a10306-e279-7943-8a6f-4ddff247a5b5` | verified |
| IM-004 | [authorization](authorization/) | 角色、权限、操作审计日志 | `01a10306-e37a-70b0-9389-81b79aed8bf7` | verified |
| IM-005 | [diagnostics](diagnostics/) | 结构化日志、指标、健康检查 | `01a10306-e474-7132-a988-9d1c6e27770c` | verified |
| IM-068 | [alarms](alarms/) | 报警发生/确认/结束/抑制生命周期 | `01a12765-2d8e-7510-9dcb-e71cfadffa3b` | verified |
| IM-006 | [image-frame](image-frame/) | 图像帧租约、Tile懒加载、像素格式 | `01a10306-e5ca-7142-a49d-fe69436c08ff` | verified |
| IM-007 | [coordinate-geometry](coordinate-geometry/) | 坐标系变换、仿射、透视、多FOV链 | `01a10306-e6e9-7c61-b5c1-29109ed8f6c1` | verified |
| IM-008 | [camera-acquisition](camera-acquisition/) | 相机采集状态机、资源排空、租约 | `01a10306-e817-7a42-9f51-6be2c4494c67` | verified |
| IM-009 | [lighting-control](lighting-control/) | 光源通道控制、配方、诊断 | `01a10306-e930-7c21-8684-a996e3df4c56` | verified |
| IM-010 | [motion-control](motion-control/) | 运动控制抽象、扫描路径规划 | `01a10306-ea59-7200-843c-9a16fcce894f` | verified |
| IM-011 | [structured-light](structured-light/) | 结构光相机采集与原始点云生成 | `01a10306-eb75-7773-8a6f-aa96fac1afc3` | verified |
| IM-013 | [calibration-assets](calibration-assets/) | 标定资产、溯源链、版本化存储 | `01a10306-ec87-7d20-b5cc-337280b4113c` | verified |
| IM-014 | [model-assets](model-assets/) | 视觉/AI模型资产注册、版本、发布 | `01a10306-ede3-7de1-9ad7-93de6dd2be11` | verified |
| IM-015 | [inspection-evidence](inspection-evidence/) | 生产证据写入、提交、租约管理 | `01a10306-ef14-7191-a5d1-c5135eeae735` | verified |
| IM-016 | [replay](replay/) | 离线回放、回归测试、问题复现 | `01a10306-f040-7b30-87a6-211f2ccc6cbc` | verified |
| IM-045 | [query](query/) | 通用数据集查询、分页、聚合、导出 | `01a10307-0eef-74c2-9585-e13ae839ec9b` | verified |
| IM-066 | [storage-database](storage-database/) | 关系数据库、文件对象存储、迁移、备份 | `01a109b6-49e5-7380-95ca-cbe3ba32b2c8` | verified |
| IM-067 | [human-review](human-review/) | 人工复判、意见追加、仲裁工作流 | `01a109a0-9f66-7143-a835-7b5fe691bcf1` | verified |

## 视觉与计量能力（19项）

| ID | 目录 | 职责摘要 | 原专属会话 | 指导核实 |
|---|---|---|---|---|
| IM-020 | [image-quality](image-quality/) | 采集质量评估、模糊/噪声/曝光检测 | `01a10306-f171-79a1-9e16-755c1ee237d1` | verified |
| IM-021 | [image-preprocessing](image-preprocessing/) | 滤波、增强、归一化、通道转换 | `01a10306-f2a8-79e3-b466-b8fd194666ec` | verified |
| IM-022 | [image-rectification](image-rectification/) | 畸变校正、透视矫正、仿射变换 | `01a10306-f3f9-77d1-a526-f0f0b47656fe` | verified |
| IM-023 | [mosaic](mosaic/) | 多FOV图像拼接、全局坐标映射 | `01a10306-f537-7b90-b793-d9c49a4f2f99` | verified |
| IM-024 | [roi-geometry](roi-geometry/) | ROI定义、变换链、裁切、坐标绑定 | `01a10306-f66f-7ee0-9c35-f2eb7867909c` | verified |
| IM-025 | [features-2d](features-2d/) | 2D亚像素边缘、轮廓、几何拟合 | `01a10306-f7a0-7773-98d2-27034ea2312d` | verified |
| IM-026 | [alignment-2d](alignment-2d/) | 2D模板匹配、配准、Alignment | `01a10306-f8cf-78b0-be63-da785b62312a` | verified |
| IM-027 | [barcode](barcode/) | 条码/二维码读取与印制质量 | `01a10306-fa0c-72d3-8fb2-8fe6a044ed5f` | verified |
| IM-028 | [ocr](ocr/) | 字符识别、深度OCR、打印质量 | `01a10306-fb32-7792-8533-43e987529aa2` | verified |
| IM-029 | [segmentation](segmentation/) | 区域分割、Blob分析、连通域 | `01a10306-fc70-7c02-8e48-ec83a652d698` | verified |
| IM-030 | [variation-inspection](variation-inspection/) | 差异检测、变化分析、良品比对 | `01a10306-fda4-7dc0-a852-0949ddf4ede0` | verified |
| IM-031 | [surface-data](surface-data/) | 高度场数据管理、点云封装 | `01a10306-ff29-7463-a87d-5727c4691bbf` | verified |
| IM-032 | [reconstruction-3d](reconstruction-3d/) | 3D重建、深度估计、表面生成 | `01a10307-0075-78c1-aed2-c79de7d15cf7` | verified |
| IM-033 | [registration-3d](registration-3d/) | 3D点云配准、多视角对齐 | `01a10307-01b9-7032-a635-54bcde7589e0` | verified |
| IM-034 | [surface-features-3d](surface-features-3d/) | 3D表面特征提取、拓扑分析 | `01a10307-030b-79e2-9900-9d28e7e1919c` | verified |
| IM-035 | [reference-surface](reference-surface/) | 参考面拟合、翘曲、体积计量 | `01a10307-0454-7f33-befa-cb9ada86e3b4` | verified |
| IM-036 | [metrology](metrology/) | 2D/3D尺寸计量（含子程序集拆分）、GR&R | `01a10307-05b5-7102-9f3d-10287f213a79` | verified |
| IM-037 | [assignment](assignment/) | 候选-目标关联、孔位/焊点分配 | `01a10307-06f0-7012-a08f-51ed05953045` | verified |
| IM-065 | [measurement-workbench](measurement-workbench/) | 可嵌入测量工作台UI控件 | `01a10579-735b-7641-ab77-ea4fe9a42fb4` | verified |

## 设备、工程和服务能力（12项）

| ID | 目录 | 职责摘要 | 原专属会话 | 指导核实 |
|---|---|---|---|---|
| IM-040 | [profile-acquisition](profile-acquisition/) | 激光轮廓传感器采集 | `01a10307-0847-7d90-98c9-e32b45a7a714` | verified |
| IM-041 | [device-signals](device-signals/) | DI/DO/AI/AO、触发、编码器信号 | `01a10307-099b-7532-9471-d488c3d937d6` | verified |
| IM-063 | [deep-sight-control](deep-sight-control/) | 深视SR/SRI激光设备适配层 | `01a1053f-cec0-7ac0-a89e-7ddbd0398ba9` | verified |
| IM-064 | [googol-motion-adapter](googol-motion-adapter/) | 固高GTS运动控制卡适配层 | `01a1053f-d078-79e1-b675-d05126c8ea82` | verified |
| IM-042 | [imaging-optimization](imaging-optimization/) | 成像参数自动优化 | `01a10307-0ae0-77a2-9209-d871823f090a` | verified |
| IM-043 | [statistics](statistics/) | SPC、Cpk、质量统计分析 | `01a10307-0c3f-7703-874c-df1923b03760` | verified |
| IM-044 | [reporting](reporting/) | 生产报告、质量报告、客户输出 | `01a10307-0d8e-76d0-af97-f0bad40a61a1` | verified |
| IM-046 | [integration-transport](integration-transport/) | MES集成、OPC-UA Pub/Sub、MQTT Sparkplug B、gRPC | `01a10307-104f-7c90-b5e8-49af2eabc2a5` | verified |
| IM-047 | [ai-inference](ai-inference/) | 模型推理执行、三态仲裁、ONNX Runtime三路EP | `01a10307-11ba-7e50-8afb-d4cf9aaa6a11` | verified |
| IM-048 | [ai-dataset-governance](ai-dataset-governance/) | 训练治理、MLOps闭环、L1-L4参数学习 | `01a10307-1306-7981-ac71-918aa7c5007c` | verified |
| IM-049 | [qualification](qualification/) | 计量资格、Golden数据集、MSA | `01a10307-146c-7813-a748-cb880cffbd43` | verified |
| IM-050 | [delivery-migration](delivery-migration/) | 机台交付、升级恢复、数据迁移 | `01a10307-15c0-7911-8855-f36f29fc2293` | verified |

## 独立UI与工程控件（3项）

| ID | 目录 | 职责摘要 | 原专属会话 | 指导核实 |
|---|---|---|---|---|
| IM-060 | [viewport](viewport/) | 影像视口控件、ROI交互、叠加层渲染 | `01a10307-1727-7691-90fe-26ab71976b94` | verified |
| IM-061 | [design-system](design-system/) | WPF主题Token、色彩、字体、组件 | `01a10307-18d4-7101-bf1d-60336ad4be29` | verified |
| IM-062 | [parameter-editor](parameter-editor/) | 算法/设备/配方参数编辑器控件 | `01a10307-1a4c-7321-b090-8efade8e9ec5` | verified |

---

每个模块指导达到 DEV-GOV-010 §3.1 可执行标准后，算法工程师按指导写代码，不需要额外的架构决定。架构缺口直接在对应 `DEVELOPMENT-GUIDE.md` 中修订，不在聊天记录里口头确定。
