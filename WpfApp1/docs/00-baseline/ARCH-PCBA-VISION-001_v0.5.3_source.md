> 2026-09-27：本文件为保留的历史架构源（候选/DocMapped），原内容和跨仓库引用不自动成为本平台批准事实。当前平台边界按[PLATFORM-DESIGN-001](PLATFORM-DESIGN-BASELINE.md)，权威缺口见[GATE-001](REQUIRED-REPOSITORY-AUTHORITIES.md)。源内旧相对路径仅用于追溯，不作为当前导航或生产准入。

# PCB→PCBA 多产品视觉检测与质量管控平台总体架构
- 文档 ID：`ARCH-PCBA-VISION-001`
- 状态：`SourceBaseline`
- 关联标识：`ARCH-PCBA-VISION-001-SOURCE`

- 版本：`0.5.3`
- 日期：2026-09-18
- 平台基线措辞修订：2026-09-27，仅同步用户确认的 AsunImage 与依赖前提；不改变下述架构批准状态。原跨仓关联链接尚有本地缺失，见 PROJECT_PROGRESS.md 的本轮记录，不作为契约已绑定证据。
- 架构批准状态：待批准（评审修订稿；以第 14.13 节的精确版本批准记录为准）
- 实施成熟度：`DocMapped`（本文新增/扩展架构范围；既有模块按各自交付证据记录，不因本文状态退级）
- 基线性质：总体架构候选基线；文档修订与审核通过不自动授予批准或生产资格
- 适用范围：硬板、软板/FPC、刚柔结合板、HDI 及其组合产品的 PCB/PCBA 检测；钢网检测、3D SPI、SMT 炉前 AOI、SMT 炉后 AOI，以及跨工序质量管控平台
- 关联文档：[SPI 开发需求框架](spi开发需求框架.md)、[SPI 模块开发总则与接口约定](SPI模块开发总则与接口约定.md)、[SPI 实现级算法鲁棒性与 UI 窗体设计规范](SPI实现级算法鲁棒性与UI窗体设计规范.md)、[SPI UI Design Skill](../skills/spi-ui-design/SKILL.md)、仓库级 [Asun Vision Platform 架构](../../docs/40-development/00-standards/AsunVisionPlatform架构与模块目录.md)、[可复用模块独立性与 UI 分离标准](../../docs/40-development/00-standards/可复用模块独立性与UI分离标准.md)、[权威状态与判定所有权规范](../../docs/40-development/00-standards/权威状态角色消息与判定所有权规范.md)
- 文档消费者：产品负责人、平台架构师、视觉/计量工程师、软件开发、UI、AI、设备、工艺、质量、测试和交付负责人

> 本文定义产品族和平台架构，不代表任何一个产品已经实现、通过计量、通过 HIL/FAT/SAT 或取得生产资格。GitHub 项目只作为公开代码架构证据和设计方法输入；不得把其示例、许可证、算法、性能或领域模型直接复制为本项目事实。

> 本文尚未落入权威契约的对象名、能力名和流程名**只是架构语义**。需扩展的语义必须按第 14.6 节登记 `ContractCandidate` 并绑定既有权威资产；已存在的契约直接引用，不重复登记，不得在 `spi/`、产品目录或任何新建服务中创建第二套 Schema、状态机、事实存储或 Owner。引用的外部标准、法规和方法只说明可采用的依据来源，**不构成本项目已符合、已认证或已具备资格的声明**。

## 1. 架构结论

### 1.1 平台与产品族结论

本项目不应继续按“开发一个越来越庞大的 AOI 软件，再把 SPI、钢网和其它检测功能逐项塞进去”的方式扩展。推荐建设一套 **PCB/PCBA 多产品视觉检测平台**，由共享平台、共享视觉能力、领域能力、专业产品和跨工序质量管控组成。

```text
统一平台底座
├── PCB Inspection Product Family
│   ├── Rigid PCB
│   ├── HDI
│   ├── FPC
│   └── Rigid-Flex
├── 钢网检测产品
├── 3D SPI 产品
├── AOI 产品（炉前/炉后工作区）
└── PCB/PCBA 全流程质量管控产品
```

“一套平台”解决重复开发、统一升级和跨工序数据积累；“多个专业产品”保证每种设备和工序拥有自己的对象、算法、工作流、界面和验收标准。技术上可以在同一个仓库和解决方案中开发，交付时使用不同产品入口、配置、授权、模块装配和安装包。

平台只共享稳定的技术能力和治理能力，不把所有工序压成一个万能检测对象、万能配方页面或万能结果状态。共享控件不等于共享专业页面，共享计算引擎不等于共享业务定义，共享数据底座不等于混合领域事实。

平台技术基线（用户决定，2026-09-27）为 **Visual Studio 2026 + C# / .NET 10 + WPF + DevExpress 25.2.3 + AsunImage**。不在平台规则中固定底层 HALCON 版本。DevExpress 使用本机已有程序集，不从 NuGet 下载；AsunImage 通过 `ImageLibDotNet` 公共接口使用。两项依赖不验证、不做兼容/授权/许可证审查，不作为前置门禁。资源与后端边界见第 3.12.6 节。其它旧项目或 .NET 8 控件不自动迁移，接入范围另行确定；本项目业务实现仍需适用的构建与功能验收。

### 1.2 系统上下文与外部接口

外部接口按下表登记适用产品、部署范围、Owner 与契约。清单是能力分类，不代表所有接口均已实现；新增外部交互先完成契约登记与兼容验证，不得由适配器临时引入。

```text
                    ┌──────────────────────────────────────────┐
   设计/制造数据 ───▶│                                          │
   (CAD/CAM/BOM/PnP) │                                          │◀─── 企业 MES / ERP / QMS / PLM
                     │   PCB→PCBA 视觉检测与质量管控平台         │
   上游设备 ────────▶│                                          │───▶ 下游设备
   (印刷机/贴片机/    │   ├─ 边缘检测站（Edge Station）           │     (贴片/回流/AXI/ICT/FCT)
    炉/搬送/上下板)   │   ├─ 产线质量中心（Line/Site Hub）        │
                     │   └─ 企业侧数据/报表接入                  │───▶ 客户报告 / 审计 / 归档
   外部测试系统 ────▶│                                          │
   (AXI/CT/ICT/FCT)   │                                          │◀──▶ 远程服务与更新通道（受控）
                     └──────────────────────────────────────────┘
                        ▲              ▲              ▲
                        │              │              │
                   设备与传感        人员角色       环境与设施
             (相机/光源/运动/3D/PLC)  (操作/编程/复判/  (温湿度/电源/气源/
                                       计量/质量/维护)   网络/时钟源)
```

| 外部参与者/系统 | 交互方向 | 承载契约与落点 | 架构边界 |
|---|---|---|---|
| 设计与制造数据源（Gerber、ODB++、IPC-2581、Excellon、BOM、PnP、钢网/Coverlay CAD、层叠定义） | 入 | 唯一经 `BoardDataAdapter` → `ManufacturingGeometrySnapshot`（第 2.8 节） | 解析通过不等于几何可用，更不等于检测资格 |
| 上游/下游 SMT 设备与搬送（印刷机、贴片机、炉、上下板机、缓存、翻板） | 双向 | 板流握手与设备命令（第 3.14 节、第 14.7.2 节） | 传输握手不是质量事实；ACK 不是 Applied |
| 外部测试与分析设备（AXI/CT、ICT、FCT、切片、厚度/成分仪器） | 入 | `ExternalTestCapability/Attempt/Fact`（第 2.10 节） | 外部事实不得被解释为视觉量测，也不得被视觉结果替代 |
| 企业 MES/ERP/QMS/PLM | 双向 | 工厂互联与跨站事件（第 3.3、8.4 节） | 企业系统拥有主数据与企业质量流程，不拥有设备权威判定 |
| 产线质量中心 | 双向 | 质量事件、Hold、跨站评价（第 3.10、8.3、8.4 节） | 中心不得签发设备授权，不得成为第二个 `Decisioning` |
| 客户与审核方（报告、证书、审计导出、数据留存） | 出 | 报告、证书与归档（第 3.19.4 节） | 导出是投影；导出格式变化不得改变事实与 hash |
| 远程服务与软件更新通道 | 双向 | 远程服务与受控更新（第 3.16.5、9 章） | 默认只读与会话审计；断链后回到本地权威，不降级放行 |
| 人员角色（操作、编程、复判、计量、质量、维护、管理员） | 双向 | 角色工作区与权限（第 3.10、8 章） | UI 只能发起经权限检查的命令，不直接改事实 |
| 设备与传感硬件（相机、光源、运动、3D 传感、PLC、GPU） | 双向 | 能力探针与设备适配（第 3.8、3.13 节） | 能力被发现不等于已标定、已授权或具备资格 |
| 设施与环境（供电、气源、温湿度、振动、网络、时钟源） | 入 | 环境与工况监测（第 3.18 节）、时间域（第 8.4 节） | 环境越界必须能阻断，不允许静默继续生产判定 |

具有外部副作用的接口遵守第 14.7 节的副作用规则；只读查询和文件读取按风险定义完整性、资源与失败边界。任何一侧的“连接成功”“文件已生成”“消息已发送”都不能推断业务成功。跨越上表边界的新交互必须先登记 `ContractCandidate`，并明确 Owner、消费者、权限、失败与恢复路径。

### 1.3 架构驱动因素、量级假设与非目标

架构的形状由少数几个驱动因素决定。它们必须显式写出来，否则在实现期会被当作“后续优化”而丢失。以下为**架构级假设**，具体数值由产品线在 `PerformanceProfile`、`ProductProfile` 与部署策略中冻结，本文一律保持 `PendingProfile`。

| 驱动因素 | 对架构的强制影响 | 若忽略会产生的后果 |
|---|---|---|
| 多品种小批量（High-Mix） | 配方规模、检索、批量操作、换型与首件必须是一等能力；编程效率与配方可移植性直接决定可售性 | 编程与换型成为产能瓶颈，现场靠手调参数，质量不可复现 |
| 节拍与并发 | 多轨/多工位并行、有界队列与背压、资源租约按实际运行和资源范围建模；板级使用 BoardRun，卷料/离线使用获批对应上下文（第 3.14.2 节） | 并发靠全局锁或隐式串行，产能上不去且故障恢复不可控 |
| 计量可信度 | 量测必须携带有效性、不确定度与资格；模态限制进入适用域（第 2.11、3.13 节） | 数值缺少可信依据，不能证明满足相应客户的验收要求 |
| 跨机一致性 | 机台间偏差与配方移植必须可验证（第 3.17 节） | 每台机器成为孤岛，多机客户维护成本失控 |
| 追溯与合规 | 事实不可变、证据可回放、合规映射可引用（第 2.12、3.19 节） | 无法证明满足适用的客户体系或市场准入要求 |
| 长时间无人运行与恢复 | 断电、断网、卡板、重启后的实体与事实状态必须可确定（第 9.3、14.7 节） | 恢复靠人工猜测，产生重复或丢失的生产事实 |
| 国际交付 | 语言、法规、时区、单位、键盘与服务响应必须可配置（第 2.12、8.6 节） | 每个国家一个分支，升级不可控 |

容量验证场景（用于建立压力测试边界，不是已批准容量或首版必须实现的统一规模；由真实产品和客户负载选择后冻结）：

| 维度 | 候选压力场景 | 冻结位置 |
|---|---|---|
| 单站配方/产品版本数量 | 万级配方与多年份历史版本共存，检索与批量操作不退化 | `ProductProfile` / 数据平台 Profile |
| 单板检测目标数量 | 从数百到十万级目标（细间距、密集 Pad、卷料段） | `InspectionCoverageSpec` / `PerformanceProfile` |
| 单板证据数据量 | 单板 2D/3D 原始与派生证据可达 GB 级 | 第 3.19.1 节容量模型 |
| 站点在线设备数 | 单站点数十台设备并发上报与接收质量事件 | 第 8.4 节跨站契约 |
| 保留期 | 事实与必需证据按客户/法规保留数年，原始数据按分级策略淘汰 | `EvidencePolicy` / 合规基线 |
| 语言与区域 | 至少覆盖交付区域语言集，且新增语言不改代码（第 8.6 节） | `ProductProfile.SupportedLocaleSet` |

明确的**非目标**（本平台不承担，防止范围蔓延和责任错位）：

- 不做通用 MES/ERP/QMS，不承担工单排产、物料齐套、财务与人力流程；
- 不做安全控制器。急停、门禁、STO、光幕与运动安全由独立安全体系承担（第 3.12.8、2.12.2 节）；
- 不做通用图像处理框架或算法库对外发行；视觉后端边界按第 3.12.6 节冻结；
- 不替代电气测试、X 射线、切片、材料与可靠性试验，不由外观推断内部质量（第 2.6 节）；
- 不以 AI 替代计量与判定权威（第 7 章）；
- 不为单一客户做产品分支；定制只能落在第 4.4 节定义的层级内；
- 不追求“单一万能页面/万能对象/万能状态”，即使短期看起来减少工作量（第 13 章）。

## 2. 产品族范围与工艺位置

### 2.1 产品族

| 产品 | 主要工序/对象 | 主要输出 | 首版定位 |
|---|---|---|---|
| PCB 检测产品族 | 硬板、软板/FPC、刚柔结合板、HDI 的内层/积层/外层、孔/微孔、阻焊字符、外形和成品外观 | 缺陷候选、几何量测、覆盖报告、板级结果和证据 | PCB 领域产品族；现场入口由 ProductProfile 装配 |
| 钢网检测 | 钢网开口、孔壁、堵孔、变形、污染、厚度和版本 | 钢网质量事实、开口差异、维护建议 | 独立钢网领域产品 |
| 3D SPI | 钢网开口、焊盘、锡膏沉积、参考面和印刷尝试 | 体积、面积、高度、偏移、形状、规则评价和过程数据 | 当前优先建设产品 |
| 炉前 AOI | 贴装完成、回流前的元件、位置、方向、极性、缺件、错件 | 贴装后、回流前缺陷、元件证据和复判任务 | AOI 装配领域产品 |
| 炉后 AOI | 焊点、焊接形貌、连焊、少锡、虚焊、元件和板面 | 焊后缺陷、机判、复判、处置和追溯 | AOI 装配领域产品 |
| 全流程质量管控 | 产品、批次、板、Panel、印刷尝试、贴装/回流事件及检测事实 | 质量时间线、SPC、异常关联、处置闭环和过程改进 | 跨领域控制台，不能改写设备事实 |

名称分为两层，禁止混用：

- **领域能力标识**：`PCBInspection`、`FlexInspection`、`RigidFlexInspection`、`HDIInspection`、`StencilInspection`、`SPI`、`AssemblyAOI`、`QualityControl`。它们定义对象、算法、规则和事实的业务边界；
- **现场产品标识**：`PCBInspectionProduct`、`StencilProduct`、`SPIProduct`、`AOIProduct`、`QualityControlProduct`。它们定义入口、工作区、权限、安装包、授权和验收矩阵。

一个现场产品可以装配多个领域能力，但必须在 `ProductProfile` 和 `EffectiveRuntimeManifest` 中固定装配关系、版本和 `InspectionDomain`。领域能力标识不自动代表独立 EXE 或程序集；是否拆分代码项目仍须满足真实消费者、契约、生命周期、测试和发布边界。

典型流程示意为：

```text
PCB制造/来料
  → PCB光板检测
  → 钢网检验与版本确认
  → 锡膏印刷
  → 3D SPI
  → 贴片
  → 炉前 AOI（可选）
  → 回流焊
  → 炉后 AOI
  → AXI / ICT / FCT（按路线）
  → 最终质量评估
```

上述流程只是常见顺序示意，不是所有产品的默认生产路线，也不替代版本化的 `ProcessRouteRevision`。具体路线必须根据产品板型、工艺、检测方法、覆盖要求和外部测试条件装配。

流程管控产品可以汇聚事实、计算统计、展示因果线索和生成受控建议；不能用后段结果回写或覆盖前段原始量测，不能把跨工序相关性直接当成缺陷因果或质量放行依据。

### 2.2 明确不混用的专业语义

| 领域 | 权威对象示例 | 禁止直接迁移的对象 |
|---|---|---|
| PCB 光板 | `Trace`、`Pad`、`Hole`、`SolderMask`、`BoardSurface` | AOI `Component`、SPI `Deposit` |
| 钢网 | `StencilRevision`、`StencilOpening`、`WallCondition` | PCB `Pad` 的默认量测语义 |
| SPI | `DepositTarget`、`PrintAttempt`、`HeightField`、`MeasurementDefinition` | AOI `SolderJoint`、`Component`、焊后缺陷 |
| 炉前 AOI | `Component`、`Placement`、`Polarity`、`AssemblyPreReflowFinding` | SPI 体积/印刷尝试 |
| 炉后 AOI | `SolderJoint`、`AssemblyFinding`、`ReworkDisposition` | SPI 参考面和沉积域 |
| 跨工序 | 带域、版本、水位和来源的关联事件 | 把关联事件直接变成另一工序的质量事实 |

公共层可以提供稳定的 `EntityId`、坐标、单位量值、证据引用、版本、审计和结果封装；领域层负责定义对象的含义、生命周期、有效性和消费者。

### 2.3 板型、互连技术与生产形态

板型不能建模为一个互斥枚举。硬板/软板描述机械与材料形态，FPC 通常属于软板，HDI 描述高密度互连工艺；同一产品可能同时是刚柔结合板、HDI、多层板和拼板。产品装配必须把板型、互连技术、材料、层叠、生产形态和检测能力作为可组合属性，并在运行清单中固定，不得由 UI 标题或单个模式开关推断。

| 维度 | 典型值 | 对检测系统的实际影响 |
|---|---|---|
| 机械形态 | 硬板、软板/FPC、刚柔结合板 | 装夹、真空支撑、平面度、局部伸缩、定位重复性和允许变形不同 |
| 互连结构 | 单/双面、多层、HDI、任意层互连、微孔/盲孔/埋孔 | 层号、层叠版本、孔类型、设计基准、可见性和检测方法不同 |
| 材料/表面 | FR-4、聚酰亚胺、金属基等；沉金、沉银、OSP 等 | 反射、透射、纹理、颜色、污染表现和成像参数不同 |
| 生产形态 | 单板、拼板、载具、片料、卷料/卷对卷 | 输送、编码器同步、PanelUnit 映射、缺陷坐标和断点续传不同 |

产品 Profile 必须允许上述属性组合，并声明适用的 `InspectionDomain`、检测方法、夹具/载具、坐标模型、层/面范围、不可检区域、质量门槛和资格证据。HDI 不是另一个 AOI 或 SPI 结果状态；FPC 也不能直接套用硬板的刚体定位、平面假设和固定输送流程。

### 2.4 PCB 制造阶段的视觉检测机台

下表是平台需要承接的 PCB 制造检测机台范围。`架构已覆盖` 表示已有公共领域边界和数据链；`需要专项指导` 表示可以复用平台，但还不能直接进入开发；`外部方法/设备接入` 表示光学平台不能替代该检测手段。

| 工位/机台 | 主要检测对象和缺陷 | 推荐检测方式 | 本架构覆盖级别 |
|---|---|---|---|
| 基材、铜箔、膜材来料检验 | 划伤、折痕、异物、污染、针孔、厚度外观 | 面阵/线扫 2D，适用时 3D/厚度仪 | 需要专项指导 |
| 内层线路 AOI | 断线、缺口、短路、残铜、线宽线距、焊盘缺陷 | 图形对比、设计数据叠加、线扫/面阵 | 需要专项指导；PCB 领域可承接 |
| 机械钻孔检测 | 漏孔、孔位、孔径、孔口毛刺、孔型异常 | 2D 孔检测，适用时孔径/深度测量 | 需要专项指导 |
| 激光微孔/HDI 检测 | 微孔位置、孔口形状、残胶/残铜等可见异常 | 高倍率 2D/3D 或专用激光检测 | 需要专项指导；内部孔壁质量不能由外观推断 |
| 内层/积层对位 | 可见层间靶标、偏移、旋转、缩放和局部变形 | Mark/靶标定位、层间坐标配准 | 需要专项指导；隐藏层需适用的其他方法 |
| 外层线路 AOI | 外层线路、焊盘、残铜、桥连、线宽线距 | 2D AOI 与设计数据对比 | 需要专项指导；PCB 领域可承接 |
| 塞孔/填孔/整平 | 表面凹陷、凸起、污染、漏填等可见缺陷 | 2D/3D 表面检测 | 需要专项指导 |
| 阻焊与字符 | 开窗偏移、露铜、漏印、字符缺陷和可读性 | 2D 颜色/几何/OCR；适用时 3D | 需要专项指导 |
| FPC 覆盖膜、补强和胶层 | 开窗、贴合、皱褶、气泡、异物、位置和轮廓 | 2D/背光/适用时 3D | 需要专项指导；不能由外观证明内部粘接强度 |
| 表面处理及金手指外观 | 划伤、污染、露底、色差和外观异常 | 2D 外观；厚度/成分需专用仪器 | 需要专项指导；专用仪器结果接入 |
| 外形、冲切、铣边、V-Cut | 外形、槽孔、毛刺、缺口、残厚和损伤 | 2D/3D 尺寸与轮廓测量 | 需要专项指导 |
| 成品 AVI、尺寸和翘曲 | 双面外观、尺寸、平整度、板弯、标识 | 双面 2D/3D、尺寸测量、读码 | 架构已覆盖；需 PCB 专项指导 |
| 卷对卷线路/表面检测 | 连续线路、覆盖膜、缺陷位置、卷段缺陷分布 | 线扫、编码器同步、卷段 Map | 需要专项指导；需新增卷料运行契约 |

### 2.5 PCBA 装配及后处理阶段的检测机台

| 工位/机台 | 主要检测对象和缺陷 | 推荐检测方式 | 本架构覆盖级别 |
|---|---|---|---|
| 来料/首件/上料核验 | 板号、料号、方向、器件和可见来料异常 | 读码、2D 识别、首件比对 | 需要专项指导 |
| 钢网检测 | 开口、堵孔、孔壁、变形、污染和厚度 | 2D/3D、设计与实物版本比对 | 架构已覆盖；已有钢网领域边界 |
| 印刷后 3D SPI | 锡膏高度、面积、体积、偏移、桥连、形状 | 3D 高度图与 2D 辅助 | 架构已覆盖；当前优先产品 |
| 点胶/胶路检测 | 胶点、胶路位置、连续性、宽度、高度和覆盖 | 2D/3D，依工艺配置 | 需要专项指导；不能直接当 SPI 沉积语义 |
| 炉前 AOI | 缺件、错件、偏移、方向、极性、立碑等 | 2D/3D AOI | 架构已覆盖；需明确炉前缺陷集 |
| 炉后 AOI | 可见焊点、连焊、少锡、元件和装配外观 | 2D/3D AOI | 架构已覆盖；不能覆盖所有隐藏焊点缺陷 |
| 插件/压接检测 | 插件有无、位置、针脚、压接高度和方向 | 2D/3D、读码、装配比对 | 需要专项指导 |
| 波峰焊/选择焊后检测 | 通孔焊点、桥连、引脚和可见焊接异常 | 专用 AOI/3D | 需要专项指导；不能由“炉后 AOI”名称自动覆盖 |
| AXI/CT | 隐藏焊点、BGA、通孔内部和适用的空洞 | X 射线/CT | 外部方法/设备接入 |
| 三防漆/涂覆检测 | 漏涂、禁涂区侵入、边界、可见覆盖异常 | 2D/UV；厚度需专用测量 | 需要专项指导；不能未经标定声称厚度合格 |
| 灌封/底部填充 | 可见胶边、溢胶、覆盖和外形 | 2D/3D；内部质量需专用方法 | 需要专项指导 |
| 分板后与最终外观 | 毛刺、边缘损伤、连接器、标签、螺钉和装配完整性 | 2D/3D、读码、装配清单 | 需要专项指导 |
| 返修/复检工作站 | 原缺陷定位、返修记录、复检、放行 | 证据联动、复判、重新检测 | 架构已覆盖；需返修闭环指导 |
| ICT/FCT 等测试结果接入 | 通断、绝缘、功能和程序测试事实 | 外部测试系统接口 | 外部方法/设备接入 |

### 2.6 检测方法边界与不可推断规则

平台必须按检测方法记录“可观察范围”和“未覆盖范围”，并把检测能力与质量结论分开：

- 光学检测可以判断可见表面和可见几何，不能证明埋孔内部、孔壁镀层、压合内部或隐藏焊点没有缺陷；
- 线路图像检测不能替代通断、绝缘、阻抗和功能测试；
- 表面颜色、反射率或外观不能直接证明镀层厚度、成分、附着力和内部粘接强度；
- FPC 覆盖膜、补强、胶层和涂覆的外观合格，不能直接推导剥离强度、内部空洞或完整厚度合格；
- AOI 外观结果不能直接替代 AXI、ICT、FCT 或工艺专项测试；SPI 结果不能直接替代 AOI 焊点结果；
- `NotObserved`、`NotCovered`、`NotApplicable`、`Invalid`、`Unknown` 和 `NotQualified` 必须保留原因，不能折算为 `PASS`。

质量管控平台可以汇聚不同检测方法的事实并展示覆盖缺口，但不得因为一个工位 PASS 就生成“整板全检合格”。放行策略必须声明所需工位、检测方法、覆盖范围、最小质量和证据完整性。

### 2.7 多板型与多工位覆盖契约

产品运行清单冻结覆盖计划及其适用条件：`BoardForm`、`InterconnectTechnology`、`MaterialStack`、`LayerScope`、`SideScope`、`ProductionForm`、`CarrierProfile`、`StationInstance`、`InspectionMethod`、`TargetSet`、`InspectionCoverageSpec`、`EvidenceRequirement` 和 `QualificationRefs`。计划规定应检范围及获批的不适用范围；实际 `ObservedScope`、`NotCoveredScope`、重复覆盖和不可达原因由本次执行生成 `CoverageResult`，绑定清单 hash 后提交，不能提前写成已观察事实或反向修改清单。`QualificationRefs` 引用适用的既有标定、设备及产品/生产资格记录，不新增通用 `QualificationProfile`；`PerformanceProfile` 的目标值本身不是资格通过证明。工位类型由 `StationDefinition` 提供，现场执行绑定 `StationInstance`，字段继续归属既有 Product/Program/Recipe/Manifest、能力和质量契约。

检测路线采用“产品版本 → 工艺路线版本 → 工位实例 → 检测尝试 → 覆盖/证据 → 量测 → 规则评价 → 领域机判提议 → 权威机判 → 事实提交”的链路。具体生产计算链固定为 `Pipeline → MeasurementSet → CoverageResult → InspectionFact → RuleEvaluation → InspectionDecision → Decisioning → MachineDecision → EvidenceCommit → ResultCommitReceipt`。HDI 的多次积层、FPC 的卷段、双面板翻面、返工和重检必须由工艺路线和尝试身份表达，不能通过修改同一条历史记录或按最近时间猜测关联。

每个工位都必须生成覆盖报告，至少区分已覆盖目标、重复覆盖目标、未覆盖目标、不可达目标、方法不适用目标、证据不足目标和因设备/材料/形变被阻断的目标。报告绑定产品、路线、设备能力、标定、配方、检测尝试和版本 hash，供质量管控、SPC、复判和放行策略消费。

`CoverageResult` 只报告实际观察及其与计划的差异，不拥有缺失容忍或放行豁免权。未覆盖、不可达和证据不足必须原样保留；是否满足本步骤规则由已批准的领域策略评价，是否满足路线证据要求由 `RouteAssessment` 按质量计划评价。任何允许排除的范围必须能回溯到批准的覆盖/质量政策及适用条件，不能由覆盖率百分比、重试成功或操作员勾选自动补成已覆盖。

### 2.8 设计制造参考模型与领域对象边界

设计文件不是各检测模块自行解释的输入字符串。统一由既有 `BoardDataAdapter` 防腐层完成安全摄入、格式解析、单位/面别/轴向确认、多源关联、语义验证和稳定 ID 生成，形成版本化的 `ManufacturingGeometrySnapshot`。它是唯一经过验证的设计/制造几何参考快照，不是新的万能业务对象，也不替代 PCB、HDI、FPC、SPI 或 AOI 领域对象。所有领域只能通过版本化引用和适配映射消费该快照，不能再次解析原始 CAD 形成第二个设计参考事实。

```text
DesignSource
  → Parser / Importer
  → SourceValidation
  → CanonicalManufacturingGeometry
  → ManufacturingGeometrySnapshot
  → InspectionTargetSet / Program
```

`ManufacturingGeometrySnapshot` 是设计/制造参考，领域对象是领域解释：例如 `Snapshot.Trace → PCBInspection.TraceTarget`、`Snapshot.MicroVia → HDIInspection.ViaTarget`、`Snapshot.Pad → SPI.DepositTarget`。映射必须保留来源 ID、领域作用域、转换版本和冲突状态；快照中的几何对象不得直接冒充 PCB 缺陷、HDI 量测、FPC 结果、SPI 沉积事实或 AOI 判定。

既有 `BoardModelVersion/BoardModelSnapshot` 是 BoardDataAdapter 对外提供并按版本持久化的标准化导入契约，不是解析器私有中间对象。本文的 `ManufacturingGeometrySnapshot` 表示其在制造参考用途下经过验证并被精确引用的架构语义，优先以既有 BoardModel、来源清单与批准绑定表达；若字段不足，由 C-02 按第 14.6 节扩展原权威契约，不另建几何主库或强制复制一套模型。导入 `Committed` 证明模型已保存，不等于获准用于生产；制造参考进入 `Ready`、冲突关闭后，还须取得产品/工序适用绑定并经 Program/Recipe 发布与运行清单冻结，才能用于该范围的生产。NPI 的合法草稿与预览继续消费明确版本的 BoardModel，不能以对象名、导入成功或直接读取 `latest` 绕过上述门禁。

`ProductRevision` 与 `ManufacturingGeometrySnapshot` 属于不同版本域。同一产品版本可因 CAM 修正、钻孔文件或钢网/覆盖膜参考修订产生多个几何快照候选；依赖制造几何的每次运行必须选择经批准的明确绑定：产品版本、几何快照 `id/version/hash`、适用路线/步骤/层面、批准记录和生效范围。绑定进入 C-02 的现有发布资产，不另建制造主数据服务；多候选不能靠“最后导入”自动生效。制造参考更新不得重写旧快照或强制重编号产品，是否需要新产品版本由既有产品变更流程决定；同一快照 ID/版本却出现不同 hash 必须拒绝。获批的无 CAD 教导模式按第 3.20 节固定真实参考图像/目标与能力范围，不虚构制造几何快照，也不把教导图像称为 CAD 参考。

硬件/协议 Adapter 负责协议/文件/厂商 SDK 映射、能力探针、传输、原始 DTO、资源生命周期、错误映射和回读。BoardDataAdapter 另按既有开发指导负责经验证的标准化导入模型、来源诊断和身份策略草稿；这些输入或草稿不拥有运行身份裁决、规则发布、`MachineDecision` 或质量事实的权威。统一依赖方向为：

```text
Vendor SDK / File / Protocol
  → Adapter
  → Capability / Transport / Raw DTO
  → Approved Contract
  → Domain Interpretation
```

`ManufacturingGeometrySnapshot` 是 `BoardDataAdapter` 的制造参考输出，不替代或删减其既有标准化 BoardModel、来源诊断、`BarcodeIdentityPolicy` Draft 与静态 `BarcodeAssignmentGraph` 职责（见第 3.15.1 节及既有 BoardDataAdapter 指导）。身份策略须经批准发布，运行身份仍由既有 Orchestrator 身份 Owner 裁决。线扫/编码器/印刷机/激光传感器/AXI/ICT/FCT Adapter 形成能力、传输和原始事实输入；任何 Adapter 均不得把 SDK 类型带入领域层，也不得直接生成 PCB、HDI、FPC、SPI 或 AOI 的判定结果。

快照至少能表达 `Layer`、`LayerType`、`Side`、`Trace`、`Pad`、`Hole`、`Via`、`MicroVia`、`BuriedVia`、`Fiducial`、`BoardOutline`、`KeepOut`、`SolderMaskOpening`、`Silkscreen`、`StencilReference` 和 `ComponentReference` 的来源、坐标、单位、层/面、稳定 ID、版本及 hash。Gerber、ODB++、IPC-2581、Excellon/NC Drill、BOM、PnP/Centroid、钢网 CAD、Coverlay CAD、Flex Stackup 和 HDI Build-up Definition 只能通过该入口形成参考快照。快照内部必须保留 `SourceSetManifest`：每个输入记录 `SourceType`、`SourceId`、`Required/Optional`、`Present/Missing`、校验结果和原因；存在的输入必须具有版本、hash 和可定位原件，缺失输入不得伪造 hash 或标记为已验证。只有必需输入齐全、所用输入通过校验且冲突已解决时，`ManufacturingGeometrySnapshot` 才能进入 `Ready`，否则进入 `NotReady`，不得由各领域静默猜测。

### 2.9 HDI、FPC 与刚柔结合板的专业对象

HDI 的层叠和微孔不能实现成 `Hole` 加若干特殊参数。HDI 领域至少需要在 C-02/C-03 任务中登记 `LayerStackRevision`、`LayerRevision`、`BuildUpRevision`、`ViaDefinition`、`LaserVia`、`ViaTarget` 和 `LayerRegistrationTarget`。`LaserVia` 的专业量测至少包括顶/底层、孔类型、名义/实际中心和直径、圆度、层间对位误差、表面状态和 `MeasurementQuality`；具体字段进入批准的 Schema 后才能实现。

HDI 制造参考采用版本化引用图：`LayerStackRevision` 引用有序 `LayerRevision[]`；`BuildUpRevision` 引用适用叠层、参与层及前序制造阶段，可跨多层；`ViaDefinition` 引用起止层、孔型和形成该孔的制造阶段。`LaserVia/ViaTarget` 引用对应定义和层/阶段，不复制整套层叠。校验器必须检查层属于所选叠层、孔跨层范围与孔型相容、工艺前序无环、被检查特征在本阶段已形成且对当前方法可观察；层存在不等于孔已制造或可见。

FPC、刚柔结合板的坐标模型必须区分 `RigidTransform`、`AffineTransform` 与 `NonRigid/LocalDeformationTransform`，并关联 `NominalGeometry`、`ObservedGeometry`、`CorrectionModel`、`CorrectedGeometry`、`Residual`、`ManufacturingDeviation`、载具约束和适用域。`ObservedGeometry` 是原始观测，`CorrectionModel` 只描述坐标/采集误差模型，`CorrectedGeometry` 是应用模型后的几何，`ManufacturingDeviation` 是观测相对名义值的制造偏差；四者必须能够并列回放。`CorrectionModelId`、定义/策略版本、hash 和 `QualificationRef` 必须进入或被 `EffectiveRuntimeManifest` 精确引用；本次观测拟合出的模型实例另作为不可变 Artifact 保存，并绑定该定义、父清单和输入证据。FPC 的载具、真空/支撑、张力、局部伸缩和边界区不能藏在定位算法内部；补偿模型必须有独立检查点和残差门限，不能把真实线路、开窗、孔位、边界或装配偏差校正掉。刚性区、柔性区和过渡区应分别声明观察条件和质量规则。

模型定义资格与本次拟合实例有效性是两个独立门禁。运行拟合 Artifact 必须固定尝试身份、模型定义引用、观测证据、拟合参数、独立检查点、残差统计、有效域和退化/外推标记。定义已获资格但本次残差超限、检查点不足或超出有效域时，受影响量测标记 `INVALID`，不能以模型资格通过代替实例校验；资格失效另标记 `NotQualified`，不得混成同一原因。保留原始观测和失败实例供恢复；只有清单已批准且仍具备资格的替代策略才能在新尝试中使用，禁止静默回退到刚性补偿或无补偿后输出 PASS。

连续卷料是独立的采集/坐标运行模式。除 `Roll`、`RollSegment` 和 `Carrier` 外，相关能力需要在现有采集/坐标契约中登记 `Web`、`EncoderPosition`、`WebCoordinate`、`LineScanFrame`、`Splice`、`TensionState`、`WebSpeed`、`LineRate`、`WebInspectionAttempt` 和 `RollDefectMap` 的语义。核心链路为：

```text
Encoder → WebCoordinate → LineScanFrame → InspectionTarget
        → InspectionFact
        → RuleEvaluation
        → InspectionDecision
        → Decisioning
        → MachineDecision
        → EvidenceCommit
        → ResultCommitReceipt
        → RollDefectMap 投影
```

`ProductionForm=Roll` 只能描述生产形态，不能替代编码器同步、连续帧质量、卷段断点、拼接标记和缺陷定位契约。连续运行应有独立 `ContinuousInspectionProfile`，并引用 `WebCoordinateReference`。后者至少冻结 `WebCoordinateReferenceId`、`WebCoordinateReferenceVersion`、`WebCoordinateReferenceHash`、`RollZero`、`WebZero`、`EncoderZero`、方向、比例、`ResetPolicy`、`SpliceOffset`、`SegmentOrigin`、溢出策略和重启恢复规则；预先固定的基准引用进入 `EffectiveRuntimeManifest`，运行中重置/接头换基准按第 3.6 节保存新 Artifact 并从新卷段边界生效。机器重启、编码器重新计数、卷段切换、接头和断点恢复后，`DefectCoordinate` 仍必须能够回放。不能用单板 CT 代替 `WebSpeed`、`LineRate`、`EncoderRate`、像素/长度比例、定位延迟、连续运行长度、缓冲深度和背压的验收。

每个 `RollSegment` 的不可变上下文必须绑定坐标基准 `id/version/hash`、所属 Roll、设备/编码器 epoch 和明确的起止位置规则；段内帧、尝试、缺陷及缺陷图投影均保留该绑定。接头或重置建立新段及新基准引用，旧段缺陷不能读取“当前基准”。跨接头/重置边界的帧按已批准策略分段或标记无效，不能套用一侧基准到整帧；坐标连续性无法证明时，未知长度和覆盖缺口必须保留，不能靠偏移估算伪装连续。跨段显示坐标只通过版本固定的映射投影，不修改原始缺陷坐标。

### 2.10 工位、路线、覆盖与放行的责任分层

工位名称统一分为两种对象：`StationDefinition` 表示工位类型及所需能力；`StationInstance` 表示现场实际设备实例、站点/产线位置、版本和能力快照。`InspectionStation` 不再作为第三种身份使用。已有设备/工厂契约若采用其他名称，必须在适配层声明投影关系，不能生成第二套主键。

```text
ProductProfile
  → 产品允许的板型、材料、生产形态和能力范围
ProcessRouteRevision
  → RouteStep[]：本产品实际经过的工位链
InspectionProgram
  → 当前工位检查哪些目标和项目
InspectionCoverageSpec
  → 目标、范围、方法、观察条件和覆盖要求
EffectiveRuntimeManifest
  → 本次运行实际冻结的路线、程序、覆盖、能力和资格
```

`RouteStep` 至少声明 `StepId`、顺序、`StationDefinition`、执行约束、`InspectionDomain`、`InspectionMethod`、输入实体范围、所需能力、所需资格、覆盖要求、证据要求、重试/复检策略和退出条件。执行约束固定为 `Required`、`Conditional`、`Optional`、`Forbidden`：`Required` 必须完成；`Conditional` 在条件满足时必须完成；`Optional` 可以执行但不进入基础放行要求；`Forbidden` 表示当前产品/路线禁止执行。`BoardRun` 是一次生产运行/板级生命周期上下文；`ProcessAttempt` 只表示具有明确开始、结束、结果和回执的工艺动作尝试；`InspectionAttempt` 是检测动作尝试。SPI 中 `BoardRun` 可以关联 `PrintAttempt`、`InspectionAttempt` 和 `ReinspectAttempt`；人工复核不建立 `ReviewAttempt`，而是由已提交事实进入 `ReviewClaim → ReviewDecision → FinalDisposition`。各尝试不得复制或混用彼此的身份字段；公共字段只通过既有身份 Envelope 复用，不建立万能 `Attempt` 对象。`InspectionAttempt` 作为检测尝试身份，附带领域、方法、层/面、生产形态、工位实例和路线步骤；不为内层 AOI、钻孔、微孔、FPC 覆盖膜等分别建立平行状态机。

`Attempt` 的公共身份字段由现有身份契约统一提供；`PrintAttempt`、`ProcessAttempt`、`InspectionAttempt` 和 `ReinspectAttempt` 是实际工艺/检测动作的具体身份，不通过继承或复制形成新的万能 Attempt Schema。`ReviewClaim` 是对已提交事实的授权复核，不是 Attempt。每个具体 Attempt 必须声明其父运行上下文、动作类型、实体范围、路线步骤、工位实例、来源和因果关系。

`Conditional` 的条件必须版本化，保存本次求值输入的精确引用、输入水位、条件版本、结果和原因。只允许消费已提交的事实、机判/工艺事件及清单固定的获批产品/路线配置；禁止读取当前 UI 值、原始图像、临时缓存、`latest` Recipe、未提交 AI 候选或外部测试结果。条件未知不能当作不满足而跳过，也不能依赖本步骤尚未执行才会产生的结果或本次尚未形成的处置而构成循环。条件真假和缺口进入第 3.10 节的路线评价输入快照，消费者不得各自重新取数决定路线。

`Optional` 不要求未执行项目补齐，执行与否也不能隐式修改 `RequiredEvidenceSet`。只有固定版本的质量计划明确引用该可选步骤的证据规则时，才按其条件纳入要求。已获得的 NG、冲突或失效事实必须提交并按批准政策处理，不能因“可选”丢弃，也不能仅凭出现一条 FAIL 临时把整个步骤改成 Required。例如，可选 AXI 的 FAIL 按政策触发 Hold 或受控质量处置，不能自动变为全批 AXI 必检；政策未定义该异常处理时，阻断受影响的正常质量放行并补齐批准策略。

事实按原因追加，不能以复检或复判为名覆盖历史：同一来源结果的明确纠错通过 `FactId + Revision`、前版引用、纠错原因、来源尝试和提交回执形成修订链，按预期前版/CAS 提交，拒绝修订分叉和同键异 hash；真实重检/返工产生新 Attempt 和新事实，并关联原尝试；迟到结果按真实来源追加，不自动取代先前事实。人工复判只产生独立 `ReviewDecision` 及回执，不改原量测、事实或机判。用于评价的有效事实集合由批准的选择/替代政策和不可变评价快照确定，不在 Fact 上维护可随意翻转的 `ActiveForAssessment`。

`ReinspectAttempt` 必须绑定 `OriginalInspectionAttempt`、原事实精确引用、`ReinspectionScope`、`ReplacementPolicy` 版本及 `CoverageDelta`；后者引用新旧覆盖事实，不能修改旧覆盖。替代范围限定到目标、层/面、路线步骤和可比的方法/观察条件，且仅在复检已提交、具备资格并达到替代政策时生效。原检目标 1～1000、复检 31～60 时，1～30 和 61～1000 仍保留原事实，31～60 只采用满足替代条件的新事实；新尝试未覆盖或无效的部分仍保留缺口/原不合格。UI 和质量查询必须能显示每段范围的来源尝试、替代原因及未解决项，不能将局部 PASS 投影成整板 PASS。

`MeasurementSet` 是量测集合；`CoverageResult` 是检测覆盖事实；`InspectionFact` 是对外提交的领域事实封装，可引用量测、覆盖结果、质量/有效性和证据，但不是万能 `Result`。唯一生产计算链为 `Pipeline → MeasurementSet → CoverageResult → InspectionFact → RuleEvaluation → InspectionDecision → Decisioning → MachineDecision → EvidenceCommit → ResultCommitReceipt`；覆盖事实在链中参与评价，同时保持独立身份和可追溯内容。`InspectionFact` 必须同时表达 `ObservedScope`、`CoverageStatus`、`DetectionMethod`、`VisibilityCondition`、`QualificationStatus` 和 `EvidenceCompleteness`。`InspectionDecision` 是检测域输出的机判提议/领域投影，不是第二个生产判定 Owner；既有 `Decisioning` 负责生成权威 `MachineDecision`。`Decision=PASS` 只表示该判定所依据的事实满足其规则，不能隐含整板或整条路线已完整观察。

全文的量测与事实术语统一为 `MeasurementSet / CoverageResult / InspectionFact`；结果集合由既有 Result Commit 协议提交，`ResultCommitReceipt` 证明该集合已提交，不是另一份量测或机判。本文不另定义 `MeasurementFact` 或 `ResultFact` 通用类型；模块内部既有模型映射到批准的公共契约时必须保留原身份、单位、有效性和来源，不能因术语相近再复制事实存储。版本间关系见第 14.7.1 节。

放行继续分层：`InspectionDecision` 是领域级机判提议/投影；既有 `MachineDecision` 是生产运行权威机判；`RouteAssessment` 只根据已提交事实评估工艺路线要求；既有 `RouteAuthorization` 表示是否允许继续流转或放行。不得把单次 `InspectionDecision=PASS` 直接转换为路线完成或 `RouteAuthorization`，也不得让质量中心重新运行领域规则形成第二个 `MachineDecision`。

本机处置链为：`MachineDecision → EvidenceCommit → ResultCommitReceipt →（需要时 ReviewClaim → ReviewDecision 及其提交回执）→ RouteAssessment → Orchestrator FinalDisposition / DecisionActivationProof → DataService DispositionCommitReceipt / RouteAuthorization → MotionGateway → BoardExitAck`。可在复判前预评估缺口，但用于本次处置的 `RouteAssessment` 必须绑定精确结果 revision、已提交复判、路线/质量计划版本和输入水位，不依赖尚未生成的本次 `FinalDisposition`。无需人工复判也必须完成最终处置与处置提交。DataService 在同一处置事务中校验证明、持久化处置及回执并签发授权；MotionGateway 验证并一次性兑换授权，传感器回执确认实体交接。`RouteAuthorization` 表示获准执行特定路由动作，不能单独证明质量合格；隔离、返工和人工移除采用各自已批准的处置策略，不能为移动不合格板伪造合格事实。

`QualityPlanRevision` 应引用 `ProcessRouteRevision`、`InspectionCoverageSpec`、`RequiredEvidenceSet`、`AcceptanceProfile` 和既有 `MetricDefinition`，不复制它们。职责固定为：`MeasurementSpec` 定义如何测量；`RuleSet/RuleDefinition` 定义单次检测如何判定；`AcceptanceProfile` 沿用现有客户质量验收 Schema，包含客户/产品/机型适用范围、缺陷验收规则、阈值、guard band、不确定度策略、证据和审批要求，不拥有原始量测或运行时状态；`MetricDefinition` 定义 SPC、Cpk、FPY、DPMO 等统计指标如何计算；`RequiredEvidenceSet` 只定义放行前必须取得的已提交事实、覆盖报告、资格状态和外部测试结果。源于客户验收要求的 `RuleSet/RuleDefinition` 必须保留 `AcceptanceProfile` 及规则的精确引用或经验证的执行投影；采集质量、算法有效性等技术规则仍归属各自批准的策略，不强行塞入客户验收 Schema。`RequiredEvidenceSet` 不承载容差、缺陷阈值、Cpk 限值或召回率。正常质量放行必须满足路线所需证据、质量策略和权限；所有本机路由授权均由 DataService 按 `DEV-ARC-005` 校验 `ResultCommitReceipt`、`FinalDisposition` 与 `DecisionActivationProof`，原子持久化 `DispositionCommitReceipt` 后签发，Orchestrator 不持有路由签发权。AXI/CT、ICT/FCT 等外部方法只通过 `ExternalTestCapability`、`ExternalTestAttempt`、`ExternalTestFact` 和既有提交边界接入，质量平台消费其事实，不把它解释为视觉量测。

`ExternalTestFact` 必须携带 `SourceSystem`、`EquipmentId`、`EquipmentEpoch`、`TestProgramId`、`TestProgramVersion`、`TestAttemptId`、`SourceResultId`、`ResultHash`、`OccurredAt` 和 `ReceivedAt`，并能区分首次测试、返修测试、重测、复测和重新上传；不得按时间戳或文件名猜测关联。 来源身份必须可验证并绑定实体、路线步骤、方法与能力映射；源系统无法提供稳定尝试或重启身份时，登记接入能力缺口，不伪造来源字段。相同来源结果键且 hash 相同返回原回执；同键不同 hash 进入冲突，纠正结果保留明确修订/替代关系。重新上传不产生新测试尝试，真实重测才建立新尝试。

资格引用与验收规则不得混用：资格引用表达运行所需的资格条件，引用标定、测量系统、设备、产品和生产资格状态；`AcceptanceProfile` 表达验收指标和质量规则。仓库已有的 `AcceptanceProfile`、`HardwareQualificationProfile`、`CalibrationProfile`、`PerformanceProfile` 等权威资产继续分别承担对应职责；本架构不新增同名平行 Schema。资格层级必须保持独立：`AlgorithmQualification → MeasurementQualification → MachineQualification → ProductQualification → ProductionQualification`，前一级通过不能推导后一级通过。

`QualificationRefs` 进入 Manifest 时必须同时固定资格版本、有效期快照、适用域和撤销状态。Manifest 冻结不等于资格永久有效；每次生产准入和具有生产副作用的执行边界都必须检查快照仍有效、当前未撤销且未过期。标定、测量系统、设备、产品或生产资格任一失效时，运行必须进入 `Blocked`、`NotQualified` 或 `Unknown`，不得继续完成正常生产判定。

本文若使用“资格 Profile”作为概念统称，均指上述已批准资格资产的组合引用，不代表新增统一 Schema。正式字段必须使用已有 Schema 的明确引用，或先登记 ContractCandidate 后再进入实现。

### 2.11 PCB 专用几何与尺寸计量（PCBMetrology）

`PCBMetrology` 是本架构已列入 `PCBInspection` 的专业领域能力，负责把制造参考、客户/采购要求、实物几何、基准、测量方法、不确定度和验收评价连接起来。它与以断线、短路、缺口、残铜等为目标的 `PatternInspection` 保持不同的 InspectionIntent，能够共享图像、几何和计算能力，并相互引用同一来源的观察事实；一个局部缩颈既可构成缺陷也可形成尺寸测量，但不能因此重复制造两个原始量测权威。

专业计量按“参考/要求 → 基准与观测 → 量测和质量 → 验收评价 → 已提交事实的质量应用”组织，不按工具菜单堆叠功能。以下是生产用途通过准入后的逻辑依赖；执行一个 MeasurementSpec 本身不授予进入生产链的权限：

```text
ManufacturingGeometrySnapshot + 已批准的制造/验收要求
  → NominalFeature / DatumReference / MeasurementSpec
  → ObservedGeometry + Calibration/Registration Artifact
  → MeasurementSet（实际量值、偏差、质量、不确定度）+ CoverageResult
  → InspectionFact（PCB 计量领域载荷）
  → RuleEvaluation（含容差评价）→ InspectionDecision
  → 已登记 Decisioning → MachineDecision → EvidenceCommit / ResultCommitReceipt
  → Quality / SPC / RouteAssessment / 既有处置链
```

`NominalFeature`、测量方法和容差评价在本节是领域语义；正式结构映射到既有制造参考、MeasurementRequest/MeasurementResult、MeasurementSet、RuleEvaluation 和 InspectionFact 契约。不得另建 `PCBMetrologyFact` 事实库、客户验收 Profile、SPC 引擎或第二个 MachineDecision Owner。C-03 承接计量定义与算法边界，C-02/C-04/C-05/C-08 分别承接参考发布、规则/提交、专业界面和质量/路线接入；不新增顶层产品或 C-09，也不因存在九类测量就拆出九个 DLL。

测量用途必须在既有应用请求/执行上下文中冻结并参与授权、输入摘要、证据命名空间及提交校验。`MeasurementUsage` 表达以下用途语义，正式字段映射到现有契约，不因本表创建平行结果 Schema 或万能 MeasurementAttempt：

| 用途 | 允许的输出与消费者 | 生产边界 |
|---|---|---|
| Production | 获准的 InspectionAttempt 下产生量测集合、覆盖及领域事实，由既有生产链提交 | 用途为生产仍须通过能力/资格/配置/权限准入；无效项按生产失败规则记录，不能因失败隐藏事实 |
| Engineering | NPI、样板分析、算法调试产生 MeasurementResult/集合、预览和候选证据 | 不产生权威机判、生产事实或生产 SPC 样本 |
| Qualification | 既有 StudyPlan/StudyRun 消费量测、标准件与证据，形成批准流程的研究输入 | 研究数据不作为产品生产检测；量测引擎不自签资格或改生产限值 |
| Diagnostic | 维护诊断和人工辅助检查保存测量证据与诊断结论 | 不改变历史生产结果；设备动作仍受维护权限、资源和安全门禁约束 |
| Replay | 固定历史输入/版本的隔离重算与差异报告 | 不等于真实重检，不生成新的生产尝试、出板授权或生产 SPC 分母 |
| Review | 已授权复判中查看量测，必要时追加有来源的辅助测量证据 | 人工决定仍走 ReviewClaim/ReviewDecision；辅助测量不覆盖原量值，真实重拍/重检另建获准尝试 |

MeasurementResult/MeasurementSet 的结构可以复用，用途、运行身份和数据权威不能混用；不得将已完成的工程结果改一个标志后重新提交为生产事实。工程候选进入生产需先发布相应配置、通过资格与消费者门禁，再由新的获准生产执行产生事实；批准引用的辅助证据不改变其原用途。用途来自可信应用入口和批准任务，不能由页面随意指定；异步回调沿原 operation/用途路由，切换工作区不能使迟到结果进入生产提交。既有通用计量指导中的 `EngineeringGeometry` 路径及其 `ProductionEligible` 拒绝边界继续有效，数学计算通过不代表已交付生产图像计量。

#### 2.11.1 测量目录与可观察边界

以下目录是必须能够描述和按能力装配的范围，不表示现有设备均能完成。每项需固定对象/层面/工艺阶段、被测量定义、方法、支持域、资格和验收依据；缺少条件时标为未覆盖或未具备资格。

| 测量族 | 对象和量值 | 必须明确的边界 |
|---|---|---|
| 板外形与加工边界 | 长、宽、对角线、角半径、外形轮廓、槽/切口/缺口尺寸、孔到边/槽到边/切口到边 | 长宽沿指定基准轴或指定拟合模型定义；包围盒尺寸不自动等于图纸尺寸，边缘毛刺、倒角和圆角的纳入规则需固定 |
| 线路与铜图形 | 线宽、线距、中心线/长度/角度/转角半径、局部缩颈、铜间净距、铜到板边、铜图形相对名义轮廓的涨缩 | 声明成品铜边、观测表面和截面；投影线宽不代表导体底部宽度/铜厚，中心线长度不证明电气连续性或阻抗 |
| Pad/Land、金手指与测试点 | 宽、长、直径、面积、长宽比、形状、Pitch、边到边净距、位置与旋转 | Pad/Land 别名归一到稳定特征身份；矩形中心、面积质心、拟合中心和设计锚点分别定义，面积明确 mm²/µm² 等量纲 |
| 孔、Via 与铜环 | 可见孔口中心/直径/形状、孔间/孔到铜/孔到边距离、PTH/NPTH/Via/MicroVia 位置、最小/方向性铜环 | 区分钻孔径与成品孔径、顶/底孔口、镀前/镀后及孔型；光学孔口不代表孔壁、孔底、埋孔或内部铜环 |
| 位置与几何关系 | 特征到特征/基准/轴的距离、指定支持域内的最小/最大距离、ΔX/ΔY、中心距、角度、偏移、平行/垂直关系、对称、包含/重叠、轮廓偏差 | 每项声明操作数、方向、有限范围、基准及算子定义；最近边距、中心距、轴向投影距离不能混用 |
| 层间与图形对位 | 层对层、钻孔对铜、Pad 对 Via、阻焊/字符对铜的平移、旋转、尺度、局部残差场 | 仅比较具有共同可溯源参考且本工艺阶段可观察的特征；压合后不可见内层需适用外部方法，跨工序观测不能冒充同时可见的内层实测 |
| 阻焊及表面几何 | 阻焊开窗尺寸/位置/面积/形状、阻焊桥宽、开窗到 Pad 净距、对铜偏移 | 保存铜边与阻焊边的各自证据和对齐质量；二维几何不推导膜厚、成分、附着力或内部粘接 |
| FPC/刚柔与局部变形 | 刚性区/柔性区/过渡区位置、伸缩、非等比尺度、局部变形、覆盖膜/补强与目标的几何关系 | 固定自由态/载具约束、支撑/真空、张力、温度和观测阶段；沿用第 2.9 节的模型资格与实例有效性双门禁 |
| 厚度、平面度、弓曲与扭曲 | 适用面的厚度、平面度、Bow、Twist 和其空间分布 | 厚度须有两个表面或等效获批测量链，单面高度不等于板厚；平面度、弓曲、扭曲各有基准/支撑/归一化方法，不能用同一峰谷差替代 |

受控特征分类覆盖 Board/BoardEdge、Slot/Cutout、Trace/CopperRegion、Pad/Land、Finger/TestPoint、Hole/Via/MicroVia/BuriedVia、Fiducial、SolderMaskOpening 和 SilkscreenFeature；PTH/NPTH、孔加工阶段等使用孔定义的属性，不把工艺属性混成相互冲突的几何类型。量值分类覆盖 Length/Width/Thickness/Diameter/Radius/Area、Distance/Spacing/Pitch/Position/Angle、形状/轮廓/净距/对位和板形。它们映射到现有特征/计量定义目录，别名、单位、适用组合和版本由目录控制，UI 自由文字不能创建新类型。

孔距、线宽、线距等几何值可以作为工艺分析输入，不能产生阻抗、阻值、通断、绝缘、电流电压或信号完整性验收结论。电测、镀层/材料及不可见结构通过适用方法与 `ExternalTestFact` 汇合到质量计划；视觉计量不能替代它们。

#### 2.11.2 名义几何、制造要求与基准

名义几何是制造快照中某一特征对测量任务的只读投影：固定来源特征 ID、快照版本/hash、层面、工艺阶段及投影规则；一个快照可服务多个测量定义，不能复制后由计量模块私改。设计 CAD 值、CAM 工艺补偿值与成品验收值分别标识。客户仅规定最小成品线距时，无需伪造名义中心值或对称公差；绝对量值有效但名义值缺失时，偏差为带原因的 NotApplicable/Unknown，不能填零。

要求引用必须定位到批准的图纸/采购规范/客户条款及修订、适用产品/层面/阶段、量值、单位、上下限或单边限、边界包含规则、判定规则和批准记录，并由既有 AcceptanceProfile/RuleDefinition 管理执行引用。CAD 不是默认公差来源；IPC 设计类规范不能直接替代成品验收要求，未取得客户采用的标准版本、条款和适用类别时不填“IPC 默认阈值”。输入优先级按批准的来源/条款及适用范围解决，不按 IPC-2581、ODB++、Gerber 等格式名排序。Drill/Stackup、制造图纸、工艺注释、IPC-356/网表和客户要求是否必需由 SourceSetManifest 声明；格式支持某种信息不表示本次文件已提供。原始文件仍只经 BoardDataAdapter 输入，计量域只解析规范化引用。

基准定义必须固定基准特征身份/优先关系、原点、轴向/手性、板面、单位、参考框架、允许消除的自由度、获取方法和质量门限；运行实例保存实际基准观测及 Registration Artifact。沿用现有 `LocalMetrologyFrameDefinition` 和 CoordinateGraph，单 Mark 不能无依据确定方向，两点不能证明一般仿射/非刚性；基准缺失或退化时，受影响位置/对位评价无效，不沿用上次变换或“最近 Mark”。仅测局部形状或内在距离、不依赖外部 Datum 的项目可以声明带理由的 NotApplicable，但物理尺度、测量坐标和标定仍必需。

装夹/相机姿态配准、制造偏差量测和允许的工艺补偿分开保存。测量尺寸、尺度误差或局部形变时，不能先用含这些自由度的最佳拟合将偏差吸收，再报告零误差；被测特征不得未经批准兼作消除自身偏差的定位点。报告保留 Nominal、Observed、配准/补偿模型、Residual、CorrectedGeometry 和 ManufacturingDeviation，明确偏差正方向及有效范围；FPC 张力或仿射缩放变化不能静默改变成品要求。

二维 `RadialOffset = sqrt(ΔX² + ΔY²)` 是中心偏移量，不自动等于图纸“位置度”；只有批准定义指定二维直径容差带等条件时，才计算相应派生量并保留该定义。角差/平行偏差不能冒充带基准和长度容差带的平行度/垂直度，`4πA/P²` 圆形度指标不能冒充几何公差圆度。形位公差必须绑定采用的规范版本、基准体系、提取/拟合/评价方法及适用修饰条件；条件不足时只输出定义明确的几何量，不套标准名称。

能力声明明确区分基本几何量测与规范化形位公差评价，两类各自登记成熟度，不把“有位置/角度/轮廓工具”升级为完整 GD&T 支持。基本几何量按已定义的长度、偏移、夹角或轮廓差输出；某项标准形位公差只有在规范版本/条款、适用修饰条件、特征提取、关联/拟合、容差带和评价算法已 Contracted，并通过对应范围的计量资格后才能对外声明支持。基准按该公差项目的规则处理：位置/方向类需要适用的基准体系，圆度、平面度等无基准形状评价不能强加外部 Datum。未支持的修饰条件或标准组合须明确拒绝，不能静默降级到中心偏移或最小二乘残差后仍显示标准公差名称。

Pad 位置固定 `ReferencePointDefinition` 及其版本、名义参考点、实测参考点的构造规则和来源。设计锚点、面积质心、拟合中心和制造参考点可以不同；比较前必须按同一已批准定义或显式映射形成对应点。非对称/异形/Slot/Thermal Pad 的铜形变化不能通过自动换质心假装位置变化，反之也不能通过最佳拟合消除真正位移。实测无法重建所要求参考点时位置量测无效，可保留独立定义的形状结果；不以另一种“中心”替代。

PCB 新登记的有符号尺寸/位置偏差统一定义为 `Observed − Nominal`，在同一获批 MeasurementFrame 内计算；ΔX/ΔY 沿该 frame 正轴，线宽/线距偏差为实际尺寸减名义尺寸。无名义值不生成偏差；径向偏移、最小净距等无符号量不套该符号规则。旋转偏差采用同 frame 内的实际角减名义角、右手正向和已批准最短圆周差/边界约定；轮廓法向、对象对方向及无向轴的等价周期由 MeasurementDefinition 明示。CoordinateFrame、AxisConvention、手性、Top/Bottom 映射及其版本沿用 [坐标权威规范](../../docs/40-development/00-standards/坐标系统与数值黄金样例开发指导.md)，先完成显式坐标转换再比较，不能按 UI 朝向翻转符号；既有方法的冻结约定经显式投影接入，不改写历史 bytes。

#### 2.11.3 测量方法、采样与异常点

每项 MeasurementSpec 固定被测量、MeasurementMethod、目标/支持域、边缘定义、坐标、采样/拟合策略、标定/配准引用、数值预算、不确定度模型和证据策略。方法可复用 EdgeToEdge、CenterToCenter、Circle/Ellipse/Profile Fit、CrossSectionSampling、ContourComparison、MinimumClearance、NominalToObservedDeviation 和 Registration/LocalDeformation Fit 等能力；名称相同而数学定义不同的结果不得混用。算法优先复用既有通用计量及 AsunImage/HALCON 已批准公共能力；方法 ID 不等于某个猜测的 API，更不授予扫描 AsunImage 内部的权限。

单特征量测以稳定特征为操作数，关系量测以具有角色的操作数和批准的关系定义为输入，不另建关系事实库。对象对至少固定 OperandA/OperandB 的特征 ID、层面/阶段、几何版本/hash、RelationshipType、PairingRule、ReferenceFrame、Direction、有限支持域或无限几何、方法与配对证据；多对象关系复用有界且角色明确的操作数集合，不以两个槽位限制所有组合。设计指定的 Trace 对与观测铜集合中的最近净距是不同任务：前者缺失指定对象时不能替换为最近邻，后者须保存搜索范围、候选/胜出对象及并列选择规则。错层、身份重复、配对不唯一或共同坐标不可验证时拒绝或报告缺口；邻近残铜不能因不在设计对象对内而被另一项净距/缺陷检查遗漏。

MeasurementSpec 定义量值及方法，MeasurementSamplingPolicy 定义特征内部采样；本次 MeasurementPlan 是既有 InspectionProgram/TargetSet、InspectionCoverageSpec 和 Inspection Plan 对计量任务的执行投影，不新增第二套计划或 CoverageResult。计划固定目标特征/关系、测量定义、层面/阶段、预期采样与运行绑定，每个计划项有稳定身份；缺项、重试及多 FOV 重复观察均回到该项，不能按完成回调数计数。获批自适应采样固定算法/边界/停止规则及适用 seed，并保存实际选择轨迹；超出批准目标或方法的调整生成新计划版本/尝试，不以改计划消除已发生缺口。

覆盖分三个独立维度：特征选择（全体、关键特征、抽取的非关键特征）、特征内点/剖面覆盖、板/Panel/批次抽检；工程抽样另由用途限定，不把这些概念混成互斥的 CoverageMode。允许“全部关键特征 + 抽样非关键特征”的组合，但各自固定总体/目标集版本、选取规则、数量/纳入依据和未检范围。是否随机或系统抽样、重复观察与排除如何计入由批准计划决定；百分比不能代替目标清单。按计划完成抽样不等于观察了整板全部特征，批次接受也不能把未检对象标成已测 PASS。

实际执行继续用 CoverageResult 关联计划项，分别显示 Planned、Executed、Valid、Invalid、NotExecuted/Missing 及原因；执行中另列 Pending，不能提前当失败或已完成。在计划冻结、无未决且每项恰归一类的例子中，应测 1000 项、实际完成 997 项，其中 994 有效、3 无效、3 未执行，满足 `Executed = Valid + Invalid`、`Planned = Executed + NotExecuted`；不是 997 项全有效，更不是整板合格。事先批准的不适用项、执行期排除点和重试次数另列，不能既减少分母又计入成功；覆盖完整性及质量放行仍由既有批准规则评价。

| 关键方法 | 实现必须冻结的语义 |
|---|---|
| 线宽/缩颈剖面 | 按批准中心线/参考路径确定采样位置和局部法向，固定截线长度、两侧边配对、极性、光照通道、边缘阈值/插值、过滤尺度；弯折/分叉/端点/焊盘连接区单独定义适用性，多重交点不能任取一对 |
| 线距/铜净距 | 声明有限轮廓的最短物理距离、指定方向截距或设计配对距离；边界接触或区域相交不能仅用无符号零距离区分，须同时保留接触/重叠等观察事实；电气短路仍需适用验证。配对目标选择、相邻范围和残铜处理需版本固定，不能仅搜索设计中“应存在”的铜边而漏掉实际侵入物 |
| 孔/Pad 拟合 | 固定最小二乘、几何正交、最大内接/最小外接或其它批准定义、采样弧段和可见率；拟合直径、等效面积直径和最小开口不互换，孔边遮挡或拟合退化不能输出上一成功值 |
| 铜环 | 用同层/面/阶段下实际 Land 边界与实际孔口边界计算最小、方向性及适用平均环宽，保存最差位置与原轮廓；理想嵌套圆才可用 `Rpad − Rhole − centerOffset` 表示最小环宽，不能普遍用半径差替代；破环/缺铜、非圆与部分可见分别处理，拟合圆不能填补真实缺口 |
| 轮廓/位置/关系 | 固定对象对与方向、中心/轴定义、有限线段或无限线、最近点/指定对应点、带符号法向及轮廓重采样规则；输出几何证据和偏差场，不能只输出 PASS |

MeasurementSamplingPolicy 至少冻结采样模式、数量/间距/步长、区域选择、关键位置、最大未采样间隙、最小有效样本、拟合/统计聚合、分位数算法及上/下尾、最差值政策和资源上限。规则来自产品/能力资格，不填通用默认像素数。每个样本保留稳定 ID、位置/局部方向、原始边点/几何、结果、质量、来源 FOV/证据、被排除原因；报告计划/实际/有效/排除样本数及覆盖缺口。

Min/Max/Mean/StdDev/Percentile 和最差位置分别记录；最小值只代表已验证采样范围内的最小，有限采样不自动证明连续整条线路无更窄位置。Mean 合格不能覆盖局部缩颈，P95 也不能代替下限控制的最小线宽/线距；上尾/下尾或全范围规则由 AcceptanceProfile 冻结。观测覆盖、抽样覆盖与板/批抽检是不同范围，按 InspectionCoverageSpec 与质量计划分别解释，不将所有剖面样本当作独立板样本。

TraceWidth/Spacing 是量测族，不固定为一个 `Width` 标量。特征结果按批准定义包含逐样本剖面、适用名义值、Mean/Min/Max/StdDev、指定分位数、有效/排除样本数、最差位置/FOV/区域及支持范围；缺少样本时相应统计值标为不可用，不能用零占位。Mean 按点数或路径长度加权、StdDev 的统计口径及分位数插值方法均随策略固定，不均匀采样时不能混算。生产评价精确引用被验收的分量及聚合政策，而不是由 UI 临时选择最有利的汇总；板级最差值还须保留特征/测量项和原样本身份。

异常点处理保留 Raw/Filtered 样本与策略版本、方法、样本 ID、排除原因、数量/比例/空间间隙及重算关系。拟合残差可提示错误边点，但不能仅因测值超规格就剔除，也不能把缺口/缩颈/破环作为噪声删去。排除规则、上限、最少有效支持及是否允许补采必须预先批准；超限或连片缺失使该量测 Invalid/Insufficient，不能无限放宽阈值或以均值填补。人工修改排除项只形成可审计的工程候选/复核，不修改已提交事实；真实补采/复检建立新 Attempt 并沿第 2.10 节限定替代范围。

图像测量的证据必须沿 `原始图像/有效掩膜 → 预处理观察 → 提取边点/轮廓 → 拟合与排除 → 最终几何 → 量值` 回溯。保留原始和处理后观察引用、实际滤波/边缘参数、点集身份、拟合模型/实现版本、inlier/被拒点及原因、残差/退化指标、最终几何和坐标链；不能只存拟合后的线/圆。完整点集可按既有证据策略分块压缩，摘要必须绑定可重算的不可变源；显示抽稀不改变点集。边缘定位的系统偏差、滤波尺度与拟合/筛选共同影响不确定度估计，增加拟合点数或减小残差不能直接消除偏差。解析几何输入不伪造图像/边点阶段，而需声明输入几何和参考来源；缺少必需中间证据时降低可回放能力并按生产证据门禁处理。

#### 2.11.4 量测质量、不确定度与容差评价

MeasurementQuality 使用现有有效性及原因体系表达标定失效、配准失败、边缘/表面质量不足、覆盖不足、异常点超限、域外和不确定度不满足要求。原因可组合、按量值表达，不新建一个混合 Valid/NG/资格/设备状态的枚举；无效测量不能变成数值零、PASS 或普通产品 NG。有效但超限的量值、尚不能判定的量值和不具资格的执行必须可分别查询。

原始值、规范量值和显示值是三种表达。RawValue 保留算法原生数值/单位及来源；CanonicalMeasurementValue 是经批准单位转换与补偿、按契约数值精度保存的量值，连同变换版本、有效性和不确定度提交；DisplayValue 只是本地化格式化投影，不是可回写字段，也不因名称含 canonical 就改变第 3.12.11 节的序列化规则。例如规范量值 `101.237184 µm` 显示 `101.2 µm` 时，评价仍消费规范量值及批准的比较/舍入规则，不能重新解析屏幕文字参与计算。显示位数不代表物理准确度；显示单位或小数位变化不得改变结果 hash、偏差、评价和 SPC 输入，数值型导出与面向阅读的报告须明确各自单位/精度。

不确定度预算针对实际被测量，包含适用的标准件/标定、像素尺度/畸变、边缘提取、焦点/光照/表面、配准、运动/编码器、多 FOV、温度、装夹/张力及拟合/重采样贡献。`u_c` 与扩展不确定度 `U = k·u_c` 分开记录，携带覆盖因子/覆盖概率依据、分布/自由度假设、计算方法、单位、适用域和预算版本；AI/匹配 score、拟合残差或重复性单项均不等于完整不确定度。误差传播使用测量模型和相关项，同一标定/配准带来的相关误差不能当独立项重复求和；样本均值方差缩小不能证明单点最差值更准确。非线性最小距离/极值等项目需验证传播或数值方法适用性，不能机械套用线性近似。

ToleranceEvaluation 是既有 RuleEvaluation 对批准 AcceptanceProfile/RuleDefinition 的执行投影，负责公差、guard band 与不确定度政策；通用计量层不更改限值或自产客户 Pass/Fail。固定单/双边限、开闭边界、量纲、比较顺序及数值/显示舍入隔离；预算失效与有效量测落入不确定判定区分别保留原因。不确定度接近公差时按批准规则转 Review/Hold 或其它既有结果，不能假定所有客户采用同一种 guard band。

仅用于解释判定规则的示例：成品线宽要求 `[98,102] µm`，测值 `101.2 µm`；若已批准规则要求 `[y−U,y+U]` 完全落在闭规格带内，`U=0.8 µm` 时上界恰为 102，按含边界规则满足；`U=3.0 µm` 时不能据此证明符合。示例不是默认阈值，也不能与该 Profile 已计入的 guard band 再扣一次不确定度。无规则或不确定度依据时保留 Unknown/Review/Hold，不能按显示四舍五入后的值决定。

复用现有 [AcceptanceProfile Schema](../../contracts/v1/schema/acceptance-profile.schema.json) 的权威和审批机制，但其当前 AOI `componentScopes`、缺陷规则及单位集合不自动覆盖 PCB 的层面/区域、面积或全部形位要求。例如 v1 尚无 mm²/µm² 单位，必须在现有权威下完成版本化扩展、语义验证和消费者回归后才能启用面积验收；不能将面积写成 mm、伪装 percent，或另建 PCB 专属平行验收 Schema。是否可运行某项测量与是否可据此生产验收分别检查。

MetrologyCapability 复用现有计量能力分类，按特征×方法×尺度范围×光学配置/FOV×材料/表面×环境/装夹条件声明资格；同时引用分辨率、重复性、再现性、不确定度、局部/全局坐标能力、标准件及资格记录。像元尺寸、显示位数、亚像素拟合或工具按钮存在不能证明准确度；超出已验证范围不得插值成资格。光源/镜头/倍率、算法/策略、标定、载具或表面条件变更时按影响范围重验，软件测试和物理资格分别推进。

适用域必须能机器校验到特征/几何范围、尺寸/倍率、对比度及边缘条件、材料/表面、温度、装夹/张力、FOV/坐标区域、标定及方法版本。各限制来自批准的能力/Qualification 记录并给出单位、开闭边界、证据与有效期；不适用维度附理由，缺失不能视为无限制。约束按实际验证过的组合表达，不能把“高倍率/中心区域”和“低倍率/边缘区域”的各自合格范围拼成未经验证的笛卡尔积。TraceWidth 具备某段资格不等于 20 µm 线路也在范围内；几何数值预算可容纳一个数值也不证明光学系统能测准它。准入检查计划要求，执行时再以实际图像/环境/位置验证适用性，域外或未知状态不得输出可用于生产验收的有效量值。

测量要求准入同时校验特征/方法/尺度/测量范围、环境/位置及所要求的不确定度或测量能力指标；运行结果还要按本次有效预算和 Decision Rule 评价。能力存在、重复性好或测值落在规格内均不能代替匹配。例如规格为名义值 ±2 µm、当前扩展不确定度 U 为 5 µm，按不确定度区间完全落入规格带的规则无法证明符合；其他规则仍须明确覆盖因子/概率及批准的决策风险。能力不满足获批用途或没有判定依据时，阻断该生产验收，量值只按其真实有效性和用途保留，不能直接给出合格或把生产记录重标为工程记录。不在平台硬编码统一 4:1 比例、U/公差阈值或默认 guard band；能力不足不放宽客户限值，规则调整也不自动提高仪器资格。

每项生产量值须经精确引用回溯实际方法/能力、Qualification 及研究、CalibrationArtifact、对应 ReferenceStandard 的实物编号、证书中该量值的参考值/单位/不确定度和溯源链。复用 [标准件证书 Schema](../../contracts/v1/schema/metrology-reference-certificate.schema.json) 及标定/计量权威；这是一张可含多个参考和研究的依赖图，不强制每项都使用同一个串行证书链。Nominal CAD、Golden Sample、重复性或证书文件存在不自动构成可溯源参考。校验在标定/研究发生时的有效性及当前运行资格；证书后来到期不直接改写历史结果，撤销、漂移或标准件异常由计量 Owner 评估影响区间并形成受控处置，禁止用当前证书替换历史证书。

测量资格上下文通过现有 Manifest、实际运行绑定和 Qualification 记录组合解析，固定 MeasurementSpec、边缘/采样/拟合/补偿方法及参数、算法/后端版本、CalibrationArtifact、CoordinateGraph、ReferenceGeometry、能力域和不确定度预算；验收采用的 AcceptanceProfile/Decision Rule 作为适用用途引用。不新增同名 QualificationContext 存储。任一依赖变化都触发影响校验：边缘提取/光学/标定等变化需证明仍被已有资格覆盖或完成相应重验，不能继承旧 GR&R 标记；只改显示不触发物理重验，只改客户限值也须重验能力和规则匹配，但不无依据重做全部标定。形成可审计的复用/补充验证/暂停结论，在新配置准入前固定证据，旧研究及历史量值保持不可变。

计量工程师、运行准入、复核与报告通过同一只读解析视图 `MeasurementQualificationContext` 展开上述依赖；名称表示组合语义，不是新事实、独立资格或第二套存储。视图至少分组展示方法/参数、坐标/基准、标准件/研究/资格、实际模态/环境、量值有效性/不确定度、验收用途/决策规则，并显示每项的精确引用、适用范围和缺口。方法资格有效与本次实例有效分别展示；工程测量可有有效量值但尚不具客户验收资格。

解析使用该次运行冻结的引用和实际观测，不查询 `latest` 补齐历史。UI 可从单项量值直接定位方法、资格和原始证据；缺失、撤销或不可解析项显示影响范围及重验/恢复入口，不能用一个绿色“已标定”遮蔽。摘要复用现有 Manifest/Artifact 的批准 canonical 规则；需要缓存时固定其输入版本和失效条件，不把缓存当权威，不为每个量值另造 ContextHash/Schema。验收覆盖引用缺失、过期缓存、方法已获资格但本次域外、仅显示单位变化和资格撤销的历史影响。

#### 2.11.5 多 FOV 与最差位置

单 FOV 局部量测、跨 FOV 全局几何与全板汇总是三个不同层级。跨 FOV 的孔距、外形、对位等必须固定 Local→Global 变换链、标定/运动/编码器来源、方向/尺度、协方差、拼接残差和有效域；局部线宽在 FOV 内有效，不因另一 FOV 的无关失败自动作废，但受影响的全局关系及全板覆盖不能通过。

优先从原始局部观测几何经批准变换进入全局计量；融合显示图的插值、羽化和接缝修补可能改变边缘，不能直接拿显示拼接图测尺寸。确需重采样图计量时，重采样核、尺度、遮罩和不确定度贡献必须随方法获批。重叠区同一特征建立稳定匹配和重复测量策略，不能选对验收更有利的值，也不能把重复图像算成独立合格样本。

跨 FOV 一致性研究覆盖同一可溯源特征在不同 FOV、中心/边缘/角点、重叠/接缝、平台位置/运动方向、不同装夹及适用层面下的重复测量；分别报告差值、位置偏差、局部到全局残差和全局尺度。与同一系统多次测得接近只能证明一致性，准确度仍需独立参考及完整不确定度。每板/Panel/层面报告最差特征、FOV、区域、偏差、不确定度和质量原因；不得用全板平均掩盖边缘系统偏差，只有批准覆盖范围内才能声称全板计量合格。

#### 2.11.6 契约、提交与统计接入

PCB 计量候选契约复用 [通用计量引擎](../../docs/40-development/41-vision-platform/01-foundation/通用计量引擎开发指导.md) 的 MeasurementRequest/MeasurementResult，按用途保留量测结果/集合，生产用途通过 PCB 领域解释接入 InspectionFact。以下给出层级和最小必需信息，不要求把所有字段复制到一个巨型 DTO。

量测数据按下列层级关联；名称表示契约中的身份、集合或投影职责，不要求新增同名类型/服务或独立事实存储：

```text
MeasurementSample（特征内位置/方向/重复观测；仅适用方法）
  → FeatureMeasurement（单特征或已定义对象关系的结果/结果族）
  → MeasurementSet（同一获准执行上下文的量测集合）
      ├→ Board/Panel Measurement Summary（已提交集合的派生视图）
      └→ Statistical Dataset（按 MetricDefinition/SubgroupPolicy 选取原量值或获批汇总）
```

样本保留来源观察、SampleId、位置/重复序号和所属测量项；特征/关系结果保留方法、操作数、样本/拟合证据、聚合与质量。直接解析几何或无离散采样的方法可以不生成样本层，并注明理由，不能伪造采样点满足图示。MeasurementSet 在生产中绑定既有 InspectionAttempt/运行，在工程和资格研究中绑定其既有 operation/StudyRun 及用途，不另造 MeasurementAttempt。集合、层/面、特征、量值分量、样本和重复观测各有可追溯身份，不能以同一 MeasurementId 覆盖不同结果。

板/Panel 汇总与批次数据集是对版本固定、满足用途及有效性条件的集合派生的投影，绑定输入回执/水位、选择政策、缺口和聚合定义；统计域可按定义直接消费逐特征或适用样本，不强制先压缩为板级平均/最差值。卷段按其真实实体范围投影，不伪装成板。10 个剖面点不是 10 块 PCB，100 个 Pad 也不是 100 块板；一板内及同特征重复观察保留聚类关系，只有批准研究/统计计划定义了统计单位及相关性处理后，才进入对应分母。工程/Study 数据可以进入各自研究数据集，但不进入生产 SPC；UI 不提供把某个层级的“数量”直接当作另一级样本量的快捷操作。

| 字段组 | 直接字段或精确引用必须能够还原 |
|---|---|
| 身份与适用范围 | 用途、MeasurementId、特征/对象关系/结果分量/样本层级、ProductRevision、层/面/工艺阶段、InspectionDomain/DimensionalMetrology、StationInstance；生产绑定 InspectionAttempt，工程/研究绑定既有 operation/StudyRun，均保留真实实体范围 |
| 参考与要求 | 制造快照/NominalFeature 投影、设计/成品要求、AcceptanceProfile/RuleDefinition、Datum/MeasurementFrame、ReferencePointDefinition、偏差/方向约定、坐标与配准 Artifact 的 ID/版本/hash |
| 方法与执行 | MeasurementDefinition/Spec、配对/搜索规则及实际操作数、方法与算法/后端版本、ROI、采样/边缘/拟合/排除策略、资格上下文、计划项与运行实际条件 |
| 数值与覆盖 | Raw/规范量值、适用名义值与偏差、量纲、逐样本质量、计划/实际/有效/无效/未执行数量及独立覆盖维度、聚合/最差位置；缺失原因与显示值隔离 |
| 质量与证据 | 不确定度类型/预算/适用性、能力匹配与资格原因、参考证书/标准件追溯、原图/处理/轮廓/拟合/排除/样本 Artifact、实际参数、时间/来源和 canonical hash；失败也保留可用证据 |
| 评价与提交 | 生产 RuleEvaluation 从固定量测和要求派生，结果提交清单关联评价、机判和回执；非生产结果走原用途的证据/研究边界，不反向依赖评价 hash 或伪造生产回执 |

量值类型、合法特征组合、方法/单位/基准兼容、范围、最低支持和拒绝原因必须由现有 Schema/目录与 Validator 管理。C-03 的纯计量输出不拥有缺陷字典、机判或数据库；C-04 仅在生产用途通过准入后串联领域载荷、RuleEvaluation 和既有结果提交，资格及批准记录仍由对应计量/质量 Owner 签发。执行与提交入口均校验用途/命名空间/批准范围，UI 隐藏按钮不能代替服务端校验。取消或部分批次完成时，结果标明实际完成目标与缺口，不能将完成的一部分当作全部；样本/轮廓/证据量设置有依据的容量、流式/分块与背压预算，显示抽稀不改变生产样本。

SPC/过程能力继续由 [既有统计域](../../docs/40-development/60-data/SPC与过程控制开发指导.md) 的 MetricDefinition/SubgroupPolicy 负责。PCB 计量只提供已提交、可解释的量值及质量/覆盖；特征内剖面样本、单特征汇总、板级最差值和批次分母不能混算，极值或相关数据不能无验证套用正态 Cp/Cpk。样本不足、无效 MSA、工艺不稳定、规格/方法/标定/表面或采样机制变化按既有政策处理；重检不重复进入原始统计，规则限与控制限保持独立。统计接入不产生第二套工艺资格或覆盖原机判。

#### 2.11.7 专业工作区与操作流程

PCB 计量使用 WPF + 已安装 DevExpress 的编程、结果复核和计量诊断工作区。布局以中心图像/几何视口为主，左侧为层面/特征与测量任务，右侧为所选项的要求、方法与质量详情，下部为可收起的剖面曲线/逐样本表；窄分辨率通过停靠/切换保留主任务，不堆满工具栏。顶部常驻产品/工艺阶段、层面、基准、单位、方法版本、能力状态及“生产/工程/资格研究/诊断/回放/复判”用途；用途来自当前任务，不能作为更改历史结果性质的开关。图像叠加清楚标识两个操作数/配对方向、名义与实测参考点、坐标正轴及有限支持域，选择结果族分量时同步显示其最差样本和聚合方法。

- 编程路径：选已验证制造参考和批准要求 → 选单特征或对象对 → 确认基准/方法 → 查看采样线/边点/无效区 → Preview 与名义/实际/偏差/不确定度对照 → 验证覆盖/资格 → 进入既有审批发布。要求未提供、基准退化、单位不兼容或能力未具资格时显示具体阻断项，不用示例参数代替。批量套用前预览兼容特征、差异和跳过原因。
- 结果路径：选一行同步定位原图、CAD、基准、剖面与最差点；支持按层面、区域、FOV、无效原因和超限筛选。名义/实际/偏差、规格/guard band、U/k、方法、有效性和评价分列显示；使用文字/符号配合颜色，不能用一个绿灯代替全部状态。
- 复核路径：常用命令保留“上一项、下一项、定位最差点、查看基准、查看排除点”；键盘切换保持缩放、焦点和筛选上下文，图表点击与列表稳定特征 ID 联动。进入原始证据或原因应从当前选中项一步到达；容差/Datum/排除策略变更只生成新草稿，不能在历史结果页直接改值。
- 诊断/恢复路径：并排显示原始与处理后轮廓、拟合残差、排除原因、变换来源和能力有效域。提示使用“基准不足”“孔边未拍全”“面积单位不支持”等短语，并给出重拍、重检、重新标定或补充要求的实际入口；操作员不能以手动勾选恢复资格。

结果页将“计划项/已执行/有效/无效/未执行”和“特征/样本/板数”分别显示，筛选不能改变全局分母；点击缺口定位未完成计划项及原因。能力详情可从当前量值查看适用域、实际条件、资格与标准件证书链，域外直接提示“线宽超出已验证范围”等原因。基本几何量与已获资格的形位公差按真实支持范围命名；精确数值/单位转换在详情中可查，显示格式调整只改变视图。工程调试进入配置审批路径，生产重新采集进入获准重检路径，两者使用不同应用命令和权限。

PageContract 必须验收选中项联动、批量兼容预览、键盘焦点、取消/部分完成、Stale 与权限拒绝、历史版本复现及安全恢复；关键步骤数、数据规模和刷新预算按目标场景冻结，并覆盖既有八态、100/125/150% DPI、最小分辨率、UIA 和三语。三维夸张倍率、曲线平滑、显示单位与小数位仅影响显示，常驻标识且不回写量值或判定。

#### 2.11.8 验证与进入实施门禁

PCB 计量能力逐项进入 ContractCandidate/Contracted/ImplementationReady。必须有真实调用者、固定输入/输出、方法/采样/错误恢复、批准范围、资源预算、页面与以下定向验证，不能只凭类型枚举或目录名称宣布支持：

| 验证主题 | 必须能够区分的反例/预期 |
|---|---|
| 来源与尺寸语义 | CAD 值与成品要求不同、单边下限、缺名义值、错层/孔阶段、mm 与 mm² 混用；冲突必须阻断，缺失不能填零 |
| 基准与配准 | 板整体平移与局部 Pad 偏移、基准点不足/短基线、翻面/镜像/错方向、正负尺寸偏差、旋转跨零及角度边界、用缩放吸收制造涨缩；按指定 frame/符号验证，失效项不得输出伪零偏差 |
| 剖面与排除 | 弯线/分叉多交点、局部缩颈但平均合格、有限采样漏过短缺陷、排除真实坏点和超比例/连片缺样；局部坏值与缺口均可追溯 |
| 孔与铜环 | 偏心/非圆/部分遮挡、外形拟合合格但环边缺口、镀前/镀后直径混用；孔口值不能证明内层或孔壁 |
| 量值与判定 | 圆形度与圆度/位置偏移与位置度混用、边界相等、显示舍入、未知 U、相关误差和 guard band 重复扣减；按批准定义及实际精度解释 |
| 多 FOV/大板 | 同特征跨 FOV、中心到角点、接缝偏差、重复目标、局部有效但全局失效、不同运动方向/装夹；报告最差分层及影响范围 |
| 提交/UI/SPC | 部分批次、取消后迟到结果、重检替代范围、模型/Datum 改版后 Stale、历史不可改、剖面样本被误当独立板、越权改限；拒绝或恢复符合既有链 |
| 用途与权威 | Engineering/Qualification/Replay/Review 辅助测量尝试写生产结果/SPC、页面切换后迟到回调、工程结果重标 Production；提交边界拒绝，合法 Study 和辅助证据仍可追溯 |
| 对象关系与参考点 | 指定 Trace 缺失却存在更近邻边、相同距离候选、错层对象、非对称 Pad 质心与设计锚点不同；配对/参考点不确定时不能替换或输出伪位置合格 |
| 计划与层级 | 1000/997/994/3/3 的计划/执行/有效/无效/未执行例子、多 FOV 重复、关键全检加非关键抽检、不均匀采样；计数守恒且样本/特征/板/批次不混算 |
| 能力与资格依赖 | 20 µm 特征越出资格范围、有效范围拼接出未验证组合、U 不满足用途、边缘策略变更却沿用旧 GR&R、证书/实物编号错绑；生产准入阻断并给出补证/重验范围 |
| 形位与追溯 | 未支持修饰条件、无基准形状公差被强加 Datum、显示 101.2 覆盖规范值 101.237184、只有拟合轮廓没有必需边点证据；不误报标准支持，数值与证据门禁独立验证 |

数学黄金样例和合成图验证定义/数值/拒绝逻辑；量测准确度、Bias/Linearity/Stability、Repeatability/Reproducibility、MSA/GR&R、跨 FOV/跨机与环境/表面适用性必须由可溯源标准件、独立参考、挑战样板和 Qualification Study 证明。标准件证书、真值/参考不确定度、样本布局和研究方法属于计量 Owner 的批准输入，不预填 µm 级承诺。量产验收以逐量值、逐方法、逐尺度/位置和材料工况的资格为准，不以平均成绩替代最差位置或缺失证据。

不确定度方法参考已核对的 NIST 官方说明：[不确定度分量的合成](https://physics.nist.gov/cuu/Uncertainty/combination.html)（灵敏度系数、协方差及线性近似适用条件）与[扩展不确定度和覆盖因子](https://physics.nist.gov/cuu/Uncertainty/coverage.html)（U、u_c、k 及分布假设）；访问日期 2026-09-16，证据等级为官方公开方法说明，不证明本项目设备精度、客户阈值或生产资格。具体 PCB 验收及形位规则仍以获批客户规范、标准版本/条款和本项目计量研究为准。

### 2.12 标准、法规与合规基线

按销售区域、整机形态、软件用途与客户行业确定合规范围。本文规定软件需要提供的接口与证据，具体义务、版本、条款和适用日期由合规 Owner 依据官方来源确认，不以标准名称代替评定。

#### 2.12.1 合规域划分与责任边界

合规分三个互不替代的域，必须分别拥有责任主体、证据与失效处理：

| 合规域 | 含义 | 本平台的责任 | 明确不由本平台承担 |
|---|---|---|---|
| 产品合规 | 本设备/软件作为商品进入市场所需的符合性评定、适用认证与法定义务 | 提供软件侧证据：SBOM、签名、更新、漏洞处理、日志与配置可验证性 | 整机适用的 CE/UKCA 符合性评定与标志、NRTL 认证、机械与电气型式试验由整机与安全体系负责，按市场分别核定 |
| 过程合规 | 客户的质量体系要求本设备在其过程中承担的角色 | 提供事实、证据、权限、审计与报告；支持客户体系条款的引用 | 客户体系的裁决、放行与质量责任仍属客户 |
| 数据合规 | 数据的完整性、留存、跨境与隐私 | 提供分级、脱敏、保留、导出与审计机制（第 3.19 节） | 客户数据的法定处理目的与跨境授权由客户与合同确定 |

三个域的结论不得互相推导：通过产品认证不代表满足客户体系；满足客户体系不代表满足数据法规；任一域的证据缺失都必须显式暴露为缺口，而不是默认合规。

#### 2.12.2 适用标准与法规清单及其架构落点

下表是**需要评估适用性的依据来源**，不是本项目已符合的声明，也不提供任何默认阈值。用于产品质量验收的标准版本、类别（如 Class 1/2/3）与具体条款必须由客户合同或获批 `QualityPlanRevision` 采用后才能进入 `AcceptanceProfile` 或 `RuleDefinition`；未被采用的标准不得在生产判定或合规声明中作为依据，工程检索中须明确标为参考。法定适用义务按销售市场、产品用途和法律适用条件确定，不以客户是否自愿采用为生效条件。

| 域 | 依据来源（族） | 架构落点 | 不可推断的边界 |
|---|---|---|---|
| 装配验收 | IPC-A-610、J-STD-001、IPC/WHMA-A-620 | `AcceptanceProfile`、缺陷分类（第 2.13 节）、AOI 领域规则 | 标准类别必须由客户采用；标准中的判据不自动等于本机光学可检项，需逐项核对方法与覆盖 |
| 裸板验收与性能 | IPC-A-600、IPC-6012/6013、IPC-2221/2222、IPC-TM-650 试验方法 | PCB 领域规则、`PCBMetrology` 要求引用（第 2.11.2 节） | 设计类规范不等于成品验收要求；试验方法不等于光学可测 |
| 设计与制造数据 | IPC-2581（DPMX）、ODB++、Gerber X2/X3、Excellon、IPC-D-356/356A | `BoardDataAdapter` 与 `SourceSetManifest`（第 2.8 节） | 格式支持某信息不代表本次文件提供了该信息 |
| 印刷过程 | IPC-7527（锡膏印刷过程要求）、IPC-7525（钢网设计）、IPC-7095（BGA） | SPI 与钢网领域规则、印刷闭环（第 6.2 节） | 过程规范不产生本项目的阈值或资格 |
| 追溯 | IPC-1782（追溯等级与数据集） | 身份链（第 6.1 节）、数据平台（第 3.19 节） | 声明追溯等级前必须逐条核对数据项与保留期，不按“有数据库”自称等级 |
| 工厂互联 | IPC-2591 CFX、IPC-HERMES-9852、OPC UA、MQTT/AMQP | 板流握手与上报（第 3.14.3、3.14.5 节） | 协议实现不代表现场设备版本兼容；最小消息集须按机型确认 |
| 设备状态与绩效 | SEMI E10（设备状态分类）及适用的绩效方法；CFX 的设备状态与资源绩效消息 | 设备状态与 OEE（第 3.16.1、3.16.2 节） | 引用其分类不等于承诺 SEMI 认证；分类映射必须显式登记 |
| 测量不确定度与决策规则 | ISO/IEC Guide 98-3（GUM）、JCGM 106（不确定度在符合性评定中的作用）、ISO 14253-1（验证符合与不符合的判定规则） | 不确定度预算与 `ToleranceEvaluation`（第 2.11.4 节） | 平台不硬编码统一 guard band 或 4:1 比例；决策规则由客户与质量计划采用 |
| 光学/坐标测量系统验收 | VDI/VDE 2634（光学三维测量系统验收与复检）、ISO 10360 系列（坐标测量系统验收/复检思路）、ISO 25178（面结构表征）、ISO/IEC 17025（校准与检测能力管理） | 计量资格（第 2.11.4、3.12.3 节）、点检与期间核查（第 3.16.3 节） | 引用方法不等于已按该方法通过验收；标准件与证书仍须可溯源 |
| 测量系统分析 | 计量型 GR&R 与偏倚/线性/稳定性方法；属性一致性分析（Attribute Agreement/Kappa） | 第 3.12.3、7.8 节 | 计量型 GR&R 不能证明属性判定一致性，反之亦然 |
| 统计过程控制与抽样 | SPC 控制图方法族（含非正态与相关数据处理）、ISO 2859-1 / ANSI-ASQ Z1.4 类计数型抽样、ISO 3951 类计量型抽样 | `MetricDefinition`/`SubgroupPolicy`（第 8.3 节）、抽样检验（第 6.6 节） | 抽样方案是接收规则，不把未检单元标记为已测 PASS |
| 质量体系 | ISO 9001、IATF 16949（汽车）、ISO 13485（医疗）、AS9100（航空航天）、VDA 6.3 类过程审核 | 质量计划、证据集、审计导出（第 8.3、3.19.4 节） | 平台提供可引用证据，不代表客户体系已认证 |
| 电子记录与数据完整性 | FDA 21 CFR Part 11、EU GMP Annex 11、ALCOA+ 原则 | 数据完整性映射（第 3.19.3 节） | 电子签名功能存在不等于合规；须按客户验证（CSV/CSA）流程确认 |
| 工业信息安全 | IEC 62443 系列（尤其 -4-1 安全开发生命周期、-4-2 组件要求、-3-3 系统要求）、ISO/IEC 27001 | 安全边界（第 3.12.8 节）、更新与签名（第 9 章） | 过程符合不等于产品已认证；等级（SL）须按客户场景确定 |
| 产品网络安全法规 | EU Cyber Resilience Act（Regulation (EU) 2024/2847） | 第 2.12.4 节 | 义务按日期分阶段生效，须按实际上市时间与产品形态核定 |
| 机械与电气安全 | EU Machinery Regulation (EU) 2023/1230、ISO 12100（风险评估）、ISO 13849-1 / IEC 62061（安全功能性能等级）、IEC 60204-1（机械电气设备） | 与安全体系的接口（第 3.12.8 节） | 本平台的普通质量软件不得充当安全功能；安全等级由安全体系评定 |
| 光学辐射安全 | IEC 60825-1（激光产品安全）、IEC 62471（灯与灯系统光生物安全） | 传感模态能力声明（第 3.13 节）、设备防护与联锁 | 采用激光/强光模态必须声明等级与防护条件，软件不得解除联锁 |
| 电磁兼容与环境 | IEC 61000-6-2/-6-4 类工业 EMC、RoHS/REACH、WEEE | 整机与供应链 | 整机与供应链 Owner 负责适用性和评定；软件提供版本/BOM 及相关运行配置证据 |
| 人工智能治理 | EU AI Act（Regulation (EU) 2024/1689）、ISO/IEC 42001、ISO/IEC 23894、NIST AI RMF | AI 治理（第 7.5 节） | 用途分级与义务须按实际功能与市场核定，不按“我们只是工具”自我豁免 |
| 数据保护与跨境 | GDPR；中国《数据安全法》《个人信息保护法》；出口管制与客户保密条款 | 数据放置与主权（第 3.19.5 节） | 图像与工艺数据可能含客户商业秘密，按合同与法域分别处理 |

上表条目由合规 Owner 按交付范围维护；新增区域或行业先更新适用性记录和产品验收矩阵，新增依据来源时同步本表与附录 C。任何一条被采用后，必须能在 `QualityPlanRevision`、`AcceptanceProfile`、`SecurityControlCatalog` 或部署策略中找到具体引用位置；找不到引用位置的“合规声明”视为未实现。

#### 2.12.3 合规证据与不可推断规则

- 标准存在、条款被引用、功能已实现三者不可互推。只有**被采用的版本/类别/条款 + 可定位证据 + 有效期内的批准**共同成立，才构成合规证据；
- 合规证据与生产资格是不同门禁。取得认证不解除标定、计量、设备与产品资格要求；资格有效不代表合规文件仍在有效期内；
- 适用的强制义务或批准条件不满足时，按影响范围阻断发布、交付或受影响的生产能力。标准改版或支持期变化先核对采用版本、过渡安排与既有设备范围，不自动作废全部资格；已确认的生产风险不得静默放行；
- 报告与 UI 中出现的标准名称必须带版本与适用范围。未采用的标准不得以“行业惯例”形式出现在判定依据中；
- 合规缺口本身是可交付信息：缺什么、影响哪个市场/客户、由谁关闭、预计条件，必须可查询。

#### 2.12.4 产品网络安全义务与安全开发生命周期

面向欧盟或其他市场交付时，合规 Owner 必须核对产品是否落入相关法规范围、制造商/进口商/集成方责任、投放时间、实质性修改、过渡条款和事件报告要求。适用性记录必须包含官方来源、条款/版本、核对日期、适用产品、责任人及证据；不得把既有产品、软件组件与整机视为同一法定义务主体。

CRA 日期已按 [Regulation (EU) 2024/2847 正文](https://eur-lex.europa.eu/eli/reg/2024/2847/oj/eng) 第 69、71 条核对（2026-09-17）：一般适用日期为 2027-12-11，第 14 条报告义务自 2026-09-11 适用，第 IV 章自 2026-06-11 适用。第 69(2) 条规定此前投放市场产品的过渡安排，第 69(3) 条又明确第 14 条对范围内此前投放产品的例外适用；不能把“存量设备”当作所有义务的豁免。每个交付范围仍须评估产品适用性、责任主体及报告触发条件，日期本身不构成本平台或整机合规证明；后续修订与官方解释按第 2.12.5 节复核。

安全开发与交付按下列要求准备；具体能力仍按第 14.4 节验证，不能因本文列出即声称已实现或已合规：

| 要件 | 架构落点 | 验收要求 |
|---|---|---|
| SBOM 与依赖清单 | 第 3.12.8、9 章；交付 Manifest | 每个发布版本生成可机器读取的 SBOM，覆盖第三方与传递依赖，可按版本查询 |
| 漏洞管理与协调披露 | 安全 Owner 流程 + 发布通道 | 具备接收、评估、修复与通告路径；有可查询的处置记录与时限 |
| 事件与漏洞报告能力 | 可观测性与审计（第 8.5 节） | 能在规定时限内提供事件判定所需的版本、配置、日志与影响范围证据 |
| 安全更新与支持期 | 第 9 章升级隔离 | 声明产品支持期；更新可验证签名、可回退、可离线交付；过期版本明确提示 |
| 安全默认与最小权限 | 第 3.12.8 节 | 默认关闭非必需服务与端口；默认账户不得共享；权限最小化可审计 |
| 安全开发生命周期 | 研发流程（IEC 62443-4-1 思路） | 威胁建模、安全需求、代码与依赖扫描、渗透/滥用测试、发布评审留痕 |
| 组件与系统安全能力 | 第 3.12.8 节 + 部署拓扑 | 认证与会话、完整性保护、审计、备份恢复、加固基线可按客户 SL 要求映射 |

网络安全与功能安全保持分离：安全更新、密钥轮换与远程通道**不得**成为绕过安全联锁或修改安全状态的路径（第 3.12.8 节）。远程服务通道按第 3.16.5 节受控，默认只读、需客户授权、全程审计、断链即回到本地权威。

#### 2.12.5 适用性、采用与合规证据管理

在现有质量计划、安全目录、部署/交付资产中维护适用性与采用记录；`ComplianceAdoptionRecord` 仅为这组记录的架构语义，不增设合规数据库或审批 Owner。法定适用性、自愿/合同采用、实施验证和符合性评定分别表达，不能合成一个“已合规”勾选项。

| 记录部分 | 必须固定 | 主要消费者与门禁 |
|---|---|---|
| 依据与适用性 | 官方标题/定位、版次/条款、核对日期；法域、产品/软件用途、角色、上市时间及适用/不适用理由 | 合规 Owner、产品发布；范围未知保持待评估，不默认豁免 |
| 采用与要求映射 | 法定义务或合同/自愿采用依据、客户/行业/类别、批准角色；落入质量计划、验收、安全或部署资产的精确引用 | 配置发布、质量判定；避免只登记标准名称却没有执行规则 |
| 实施证据与评定路径 | 逐项证据、版本/范围、缺口、验证结论；适用的声明、内部/外部评定或证书及签发方、有效范围 | 发布/交付验收；并非每项均需第三方证书，不适用项附理由 |
| 生命周期 | 生效边界、过渡安排、复核日期与触发条件、撤销/替代关系、受影响产品和补救动作 | 升级、质量与服务；按影响范围阻断，不因标准发布新版自动作废全设备 |

实施证据缺失、依据未采用或适用性未明确时，UI/报告显示实际状态和关闭动作，不能声称认证或符合。工程资料可以展示未采用标准，但须标为参考，不能进入生产判定依据。更改采用版本、市场、用途或要求须先做影响分析，再更新相关配置与验证；历史报告保持原依据，已确认风险通过受控追溯和处置链通知消费者。验收至少包括强制义务未履行、合同版与最新版不同、证书范围不匹配、采用记录有名无引用和撤销后的受影响发布阻断。

### 2.13 缺陷分类学、缺陷代码映射与验收类别

缺陷分类与外部代码映射分别管理，保证领域事实、复判、统计和客户报告可追溯。既有分类 Schema 不能容纳的扩展先进入 C-04/C-08 契约评审，不由报表或适配器自行增加生产缺陷类型。

`DefectTaxonomy` 的唯一权威仍是既有 Schema，本节只固定其**结构与映射纪律**：

| 层级 | 内容 | 所有权 | 边界 |
|---|---|---|---|
| 领域缺陷定义 | 某 `InspectionDomain` 内可被检出的缺陷类型、判定依据、证据要求 | 对应领域 | 不同领域同名缺陷（如“偏移”）不得合并为一个类型 |
| 工艺阶段限定 | 该缺陷在哪些路线步骤/检测方法/可观察条件下有意义 | 领域 + `InspectionCoverageSpec` | 炉前“偏移”与炉后“偏移”不可互相替代 |
| 严重度与验收类别 | 与被采用标准类别（如 Class 1/2/3）及客户条款的对应关系 | `AcceptanceProfile` | 严重度不是固定属性，随采用的类别与客户条款变化 |
| 客户/外部代码映射 | 客户缺陷代码、MES 代码、CFX/报告代码与本平台类型的映射 | 质量数据域 | 映射是投影，不得反向改写领域缺陷身份 |
| 处置建议映射 | 与返修、报废、隔离、放行的默认关联（供参考，不自动执行） | 质量计划 | 建议不是处置；处置仍走第 2.10 节的链路 |

强制规则：

- 缺陷代码映射必须版本化并带生效范围。历史事实按其提交时的映射版本解释，不能因映射改版而改变历史报告；
- 映射按客户、领域、工序、接口/报告用途、验收类别和版本确定。默认单值映射须唯一；确需一对多时必须声明展开与计数规则。歧义或缺失阻断依赖该映射的上报/报告；仅在质量计划要求时阻断相应放行，不能把非必需外部代码缺失变成本机全局停机；
- 跨工序统计时，必须声明所用的是领域缺陷类型还是映射后的代码。两者不得在同一分子分母内混用；
- 缺陷类型不得携带阈值。阈值属于 `RuleDefinition`/`AcceptanceProfile`；
- AI 输出的类别只能落在**候选**命名空间，且必须能映射到已批准的领域缺陷类型；不能映射的类别按 `Unknown` 候选处理，不得新建生产缺陷类型（第 7 章）；
- 新缺陷类型的引入与旧类型的废止走配置生命周期（第 3.6 节），并在质量域完成分母影响分析后才能启用。

## 3. 总体分层

### 3.1 平台基础层

所有产品共用，但不包含具体检测对象：

- 产品启动、模块目录、能力注册和授权；
- 用户、角色、权限、审计和本地化；
- 配置、版本、签名、备份、迁移和回滚；
- 任务编排、取消、超时、幂等、Operation 查询和资源租约；
- 日志、诊断、健康状态、指标和故障关联；
- 文件、数据库、对象存储、缓存和数据保留策略；
- UI Shell、导航、主题、Design Token、基础控件和 UIA 约定；
- 发布、安装、卸载、产品包和并行版本管理。

平台基础层不得知道“锡膏体积”“焊点少锡”或“钢网堵孔”的业务含义。

### 3.2 视觉与计量能力层

以能力接口和强类型数据契约向多个领域提供服务：

- 相机、光源、运动、触发、传感器和采集同步；
- 2D 图像、3D 高度图、点云、有效掩膜和质量标识；
- 坐标变换、Mark 定位、拼板、FOV 和覆盖计划；
- 图像预处理、区域、轮廓、边缘、连通和几何 primitive；
- 标定、参考面、板弯、配准残差和不确定度传播；
- 通用测量执行器、单位量值、原始值/显示值和证据引用；
- 通用规则执行器、三值结果、解释、阈值版本和失败恢复；
- 原始证据、派生证据、回放、导出、哈希和完整性验证。

能力层必须保持领域中立。SPI 的沉积分割、钢网的开口缺陷、AOI 的焊点规则应作为领域策略接入，而不是写入同一个通用算法类的隐含分支。

### 3.3 制造与质量通用层

跨产品复用流程治理，但领域事实仍分开。身份还必须能够表达层/面、卷/卷段和载具，不能只保留单板身份：

- 产品、工单、批次、板、Panel、Unit 和站点身份；
- 配方 Draft、验证、审批、Release、应用和回读；
- 检测尝试、覆盖范围、采集尝试、量测集合和结果提交；
- 复判 Claim、ReviewDecision、FinalDisposition、DispositionCommitReceipt、RouteAuthorization；
- 质量事件、缺陷分类、SPC 数据集、控制图和异常分析；
- MES/ERP/印刷机/贴片机/回流/PLC/OPC UA 等工厂互联；
- 过程时间线、跨工序关联、批次追溯和质量报告。

该层提供治理和交接能力，不把不同工序的对象和判定规则合成一个无约束的 `Defect` 表或 `Result` 状态机。

### 3.4 领域能力包

每个领域包拥有自己的对象、算法策略、参数、规则、验证集、复判语义和专业工作区。下面的子能力是逻辑边界，不自动要求拆成独立 EXE 或程序集；最终程序集边界仍按真实消费者、契约、生命周期、测试和发布边界决定：

| 领域包 | 复用的平台能力 | 必须由领域拥有的内容 |
|---|---|---|
| PCBInspection | 图像、定位、几何、计量、证据、追溯 | PCB 对象模型、线路/孔/阻焊规则和板级缺陷解释 |
| StencilInspection | 图像、3D、标定、几何、版本和证据 | 钢网开口/孔壁/堵孔/变形模型与维护结论 |
| SPI | 采集、HeightField、参考、分割、计量、SPC | 锡膏沉积模型、印刷尝试、SPI 规则和工艺闭环 |
| AssemblyAOI | 图像、定位、库、规则、复判、追溯 | 元件/引脚/焊点模型、炉前/炉后规则和装配语义 |
| QualityControl | 查询、统计、关联、报告、权限 | 跨工序质量视图、分母定义、相关性和改进任务 |

PCB 制造领域内部至少分为：`FabricationInspection`、`PatternInspection`、`DrillInspection`、`LaserViaInspection`、`LayerRegistrationInspection`、`SolderMaskInspection`、`FinalAVI` 和 `PCBMetrology`。软板/FPC 相关能力至少分为：`FlexPanelInspection`、`R2RInspection`、`CoverlayInspection`、`StiffenerInspection`、`BendRegionInspection` 和 `FlexMetrology`。刚柔结合板由刚性区、柔性区和过渡区的组合策略组成；HDI 相关能力至少分为：`BuildUpLayerInspection`、`LaserViaInspection`、`FinePatternInspection` 和 `HDIMetrology`。这些边界共用平台能力，但不能把 HDI 微孔、FPC 覆盖膜或刚柔过渡区降格为普通 `Hole`、普通 `BoardSurface` 或普通 AOI 状态。

`PCBMetrology` 的参考/基准、测量族、方法/采样、不确定度、跨 FOV、UI 与验收闭环按第 2.11 节执行；它提供专业计量解释，通用引擎仍保持领域中立，统计定义仍归质量域。

领域包之间只通过批准的跨域事件和查询契约通信，不能直接访问对方内部 Store、ViewModel、算法缓存或设备线程。

### 3.5 产品应用层

应用层把平台能力和领域包装配成可交付产品。每个产品拥有独立入口、菜单、权限域、工作区集合、帮助内容、配方类型和验收矩阵。

```text
AOI ProductProfile       SPI ProductProfile
      ↓                        ↓
AOI Shell + AOI Workspaces    SPI Shell + SPI Workspaces
      ↓                        ↓
AOI Domain Pack                SPI Domain Pack
      └──── Shared Platform / Vision / Quality Services ────┘
```

配置只负责装配已经批准的模块和能力，不能靠改标题、隐藏菜单或替换颜色把 AOI 冒充 SPI。产品启动时必须校验 `InspectionDomain`、产品配置、模块版本、授权、设备能力、标定资格和数据消费者。

### 3.6 产品工程、Program 与运行时快照

平台必须把“产品工程定义”和“设备运行参数”分开管理。只保留 `Recipe` 会把检查对象、检查策略、设备能力和计量资格混在一起，难以支持 NPI、离线编程、跨设备部署和历史复现。

```text
Product
  → ProductRevision
  → CAD / Gerber / ODB++ / IPC-2581 / BOM / PickPlace
  → Board / Panel / Unit
  → InspectionProgram
  → Recipe
  → MachineProfile
  → CalibrationProfile
  → AlgorithmSet / AIModelSet / LibrarySnapshot
  → EffectiveRuntimeManifest
```

各对象职责必须固定：

| 对象 | 负责内容 | 不负责内容 |
|---|---|---|
| `Product/ProductRevision` | 产品身份、版本、客户/工艺来源、Panel/Unit 结构 | 设备实时参数 |
| `InspectionProgram` | 检查哪些对象、目标类型和检查项，并引用 `InspectionCoverageSpec` | 当前设备的曝光、覆盖要求内嵌副本、阈值实例和硬件句柄 |
| `Recipe` | 如何执行检查：参数、策略、容差、光源、分割和规则引用 | 产品主数据和设备能力声明 |
| `MachineProfile` | 相机、镜头、光源、运动、GPU、3D 传感器、PLC 和输送能力 | 当前板的质量判定 |
| `CalibrationProfile` | XY/Z/畸变/投影/运动/坐标变换等标定定义、Artifact 与适用域引用 | 设备控制和产品规则 |
| `LibrarySnapshot` | 元件、焊盘、钢网开口、缺陷、策略和 AI 模型的固定版本 | 未审批的工程草稿 |
| `EffectiveRuntimeManifest` | 版本固定的配置依赖闭包及本次运行解析绑定，引用能力、路线、覆盖、质量和资格依据 | 连续遥测、动态修改运行配置或把准入快照当作永久有效 |

`InspectionProgram` 解决“检查什么”，`Recipe` 解决“怎么检查”，`MachineProfile` 解决“设备能否执行”，`CalibrationProfile` 解决“使用哪些适用标定”，有效资格还须由计量研究及相应资格记录共同证明。生产运行只能使用已验证、已审批且不可变的 `EffectiveRuntimeManifest`；草稿、当前 UI 值、`latest` 查询结果和未签名模型不得直接进入生产流水线。

`EffectiveRuntimeManifest` 沿用既有配方发布和运行准入链。`Released` 生成签名发布清单，运行准入解析、校验并绑定精确版本；现有 BoardRun 在 `RecipeResolving` 固定引用，不在每次运行中改写发布清单。具体设备、运行身份及准入时资格检查结果属于运行绑定，不能反写已签名发布内容。C-01/C-02 扩展运行作用域与父子关联时，沿用现有身份/Manifest 入口；当前 [AOI 发布清单 Schema](../../contracts/v1/schema/recipe-manifest.schema.json) 尚未定义以下多产品字段，必须经 ContractCandidate 和兼容验证后使用。

`Recipe` 是工程配置对象；本文的 `RecipeSnapshot` 仅指清单解析后对已发布 Recipe 的不可变引用/投影，不新增第二套 Recipe 生命周期。它必须能还原 Recipe 的 ID/版本/hash、清单引用、解析回执及所用配置闭包；现有 [EffectiveRuntimeManifestRef](../../contracts/v1/proto/runtime.proto) 已携带 Recipe ArtifactRef、设备/boot、能力 hash、解析时刻和回执引用，应复用这些字段。闭包 hash 依对应契约引用，不为同一内容另造 `ResolvedDependencyHash`。`CalibrationProfile` 定义标定方法、适用范围及资产引用；`CalibrationArtifact` 是某次标定产生的不可变资产，实际使用时同时验证其 hash、适用域和当前资格，不能把 Profile 名称当作有效标定证据。

配置闭包与运行时输入集合分开解释：前者说明批准使用什么；后者说明本次在什么实际条件下执行。运行时输入集合复用上述解析绑定、既有执行/采集契约及证据引用，按适用性固定运行/尝试、设备 epoch、实际能力/后端、所用标定与资格检查、输入源，以及影响结果的温度、光源、张力、编码器和资源条件。每项观测保留来源、单位、时间/有效期、质量及 hash；未采集或过期不能用配置期望值补齐。无需为此建立与现有快照平行的 `RuntimeExecutionSnapshot` Schema。准入后发生的实际采集、设备回读和拟合结果进入不可变 Execution Artifact，并绑定对应执行边界；不能用准入时的一次读取代表全程实际条件。事实与回放必须同时定位配置引用、运行绑定和实际输入证据；条件越界按批准策略阻断或建立新尝试，不修改旧快照。

作用域按以下规则冻结，`ManifestScope` 是运行绑定语义，不是新的生产实体或配置服务：

- `ScopeType + ScopeId` 唯一标识 `BoardRun`、`PanelRun`、`RollRun` 或具体 `InspectionAttempt/ProcessAttempt` 上下文；`ParentScopeType + ParentScopeId` 引用直接父运行上下文，根运行无父项，`ScopeEntity` 引用既有实体身份及适用层/面/卷段范围。产品、路线、步骤和清单 `id/version/hash` 必须可追溯，不能用一个无类型的 `ParentRun` 字符串猜关联。
- 合法父子关系由 C-01/C-02 冻结：根运行或经批准关联的 `PanelRun → BoardRun`，适用生产运行 → 具体尝试；卷段作为 `RollRun` 及其尝试的实体范围，不能临时冒充新 Run 类型。校验父节点存在、同产品/实体谱系、范围包含、层级无环及路线步骤适用性。复检对原尝试采用因果引用，不把来源关系混成所有权父子关系。
- Product/Recipe Release 是配置来源，不是运行父节点。一个作用域只绑定一个有效配置闭包；多个运行或尝试可引用相同的不可变清单，无配置变化时不强制复制清单。子作用域沿用父配置，批准的变更必须形成新绑定并记录父引用、差异和生效边界，不能用继承覆盖绕过审批。

固定解析顺序为：解析精确引用及其递归依赖 → 身份与权限检查 → 路线/步骤/覆盖/质量计划/证据要求解析 → 设备/计算能力检查 → 适用标定与计量资格检查 → 兼容性检查 → 计算 canonical hash → 冻结绑定。按获批产品、用途、输入模式及实际启用能力固定全部必需依赖；依赖类别包括 `ProductRevision`、`ManufacturingGeometrySnapshot` 及其 `SourceSetManifest`、`ProcessRouteRevision/RouteStep`、`InspectionProgram/InspectionCoverageSpec`、`Recipe`、`MachineProfile/CalibrationProfile`、`LibrarySnapshot`、`AlgorithmSet/AIModelSet`、`QualityPlanRevision/RequiredEvidenceSet`。制造参考仅在模式依赖时必需；教导模式固定真实教导资产，AI 未启用按现有契约表达空集合或未启用，不创建占位模型。既有 Schema 的必填/可空规则仍须满足，所选模式尚无法表达时经权威扩展验证后再启用，不能由调用方删除必填字段。预先已知且本任务所需的 `WebCoordinateReference`、FPC `CorrectionModel` 定义/策略及资格引用也必须精确固定。作用域、绑定版本和清单 hash 必须进入证据、回执与回放，执行副作用前仍需复查撤销、权限、设备 epoch 和资格有效期。

配置闭包必须覆盖实际启用能力的所有直接和传递依赖。每个依赖节点固定 `id/version/hash`、Schema/兼容约束、适用域和批准来源，保留依赖边；可复用现有 ArtifactRef 和 Manifest 结构，不另建配置仓库。顶层引用 `Recipe v3` 而其库引用 `latest`，与顶层 `latest` 一样必须拒绝。缺引用、循环依赖、同 ID/版本不同 hash、不兼容的重复版本、适用域不匹配及解析超出批准的深度/节点/字节预算均阻断准入；未启用的可选能力明确记为未启用，不能在运行中隐式解析并启用。兼容范围用于选择候选，最终闭包必须锁定具体版本。

闭包校验在发布、部署/装载和运行准入共用同一语义验证器；按内容 hash 缓存只能省去不变内容的重复解析，不能跳过当前撤销、权限和资格检查。运行生成的 Fact、CoverageResult、拟合 Artifact 和回执进入结果/证据提交闭包，并引用父运行清单；它们不需要预先写入配置清单。配置清单不得反向包含尚未生成的事实或自己的 hash 形成自引用，配置 hash 与结果/证据 hash 各自按对应契约计算。

每个运行或尝试作用域必须能追溯到自身唯一的有效配置闭包及父绑定；合法重检或卷段换版建立新的尝试/子上下文并记录父清单引用与变更原因，禁止原地替换版本。运行中才产生的局部配准、形变拟合参数和编码器重置结果属于不可变执行 Artifact，绑定父清单、输入证据、实例 hash 与残差，不能为补写它们而修改清单。新基准从明确的卷段/尝试边界生效，旧证据保留原坐标基准。

产品工程数据必须遵循仓库权威状态规范中的配方生命周期：`Draft → Validating → AwaitingApproval → Approved → Released`，并支持 `Suspended`、`Retired`、`Archived` 等终态或管理状态。`Released` 是对外发布状态；不得在本架构中另建 `Publish/Deploy/Active` 平行状态机。发布前验证所选模式必需的制造/教导参考完整性、目标覆盖、ROI/几何有效性、已启用算法和模型兼容性、适用设备能力与标定有效期、库版本、容差范围及跨版本回读；不适用依据来自批准模式，不能用“不适用”豁免缺失的必需输入。部署和激活属于运行清单解析与设备装配操作，不改变配方历史状态。每次发布必须保留差异、审批身份、失效条件、撤销策略和在途板的适用边界；生产配方回退按 `DEV-ARC-005` 新建引用历史内容的版本，重新批准并 Released；工程草稿和部署指针的回退只在各自已批准的兼容策略内进行，不能修改历史事实。

### 3.7 Inspection Pipeline、Geometry 与计量质量

检测执行采用显式、可回放、可版本化的流水线。流水线是执行编排，不是新的领域状态机，也不能绕过各领域的判定所有权。

```text
Input
  → Preprocess
  → Registration
  → ROI / Target Selection
  → Segmentation / Recognition
  → Feature Extraction
  → MeasurementSet
  → CoverageResult
  → InspectionFact
  → RuleEvaluation
  → InspectionDecision
  → Decisioning
  → MachineDecision
  → EvidenceCommit
  → ResultCommitReceipt
```

每个 Stage 必须定义 `StageId`、`StageType`、`StageVersion`、输入输出类型、参数快照、执行模式、CPU/GPU 需求、超时/取消行为、资源所有权、失败策略和证据引用。Stage 的中间结果可以用于诊断、回放和性能分析，但只有领域量测和规则服务可以产生其领域事实。

SPI 的典型执行链为：

```text
Raw3D
  → Reconstruction
  → Calibration
  → BoardWarpCorrection
  → ReferenceSurface
  → PasteSegmentation
  → Height / Area / Volume / Offset
  → Bridge / Shape Rules
  → RuleEvaluation
  → InspectionDecision
  → Decisioning
  → MachineDecision
  → EvidenceCommit
  → ResultCommitReceipt
```

AOI 的典型执行链为：

```text
Image
  → IlluminationCorrection
  → Alignment
  → Component / Pin / Solder Target
  → Feature / Defect Candidate
  → Measurement
  → AOI RuleEvaluation
  → InspectionDecision
  → Decisioning
  → MachineDecision
  → EvidenceCommit
  → ResultCommitReceipt
```

不得使用一个 `UniversalInspectionObject`、万能 `Recipe` 或万能 `Defect` 承载所有领域。共享几何基础只提供 `Point2D`、`Point3D`、`Line`、`Circle`、`Polygon`、`Plane`、`Surface`、`Transform`、`CoordinateSystem` 和单位/容差类型；`Pad`、`Component`、`StencilOpening`、`Deposit`、`SolderJoint` 等业务对象由对应领域定义。

3D 数据必须保留完整生命周期和来源链：

```text
Raw3DData
  → Reconstructed3DData
  → CalibratedHeightField
  → CorrectedHeightField
  → ReferenceSurface
  → InspectionHeightField
  → MeasurementSet
```

每个阶段记录传感器、采集尝试、标定、坐标、算法版本、参数、时间、设备、有效掩膜、质量状态和父证据。`HeightField` 的显示结果不得直接当作生产量测；生产量测必须附带 `MeasurementQuality`，至少区分标定质量、配准残差、表面质量、分割质量、有效覆盖、不确定度/误差预算和可用性原因。`Confidence` 可以作为候选或辅助信息，不能替代计量有效性和质量判定。

### 3.8 Calibration、Coverage 与设备能力

标定和计量能力是平台能力，不是某个产品里的单一设置对话框。平台建立可追溯的坐标图。对于软板/FPC、刚柔结合板、卷料和 HDI，多出的变形、层号、卷段和局部基准必须进入适用的能力、路线和坐标契约，不能在定位算法中隐式处理：

```text
Machine
  → Stage
  → Camera / Image
  → Board
  → Panel / Unit
  → FOV / ROI
  → Measurement
```

标定 Artifact 必须有版本、有效期、适用设备/镜头/传感器、标准件或标定数据引用、残差、不确定度、创建/审核/失效记录和回读验证。硬板刚体/仿射、FPC 载具约束下的局部变形、卷料编码器同步和 HDI 层/面坐标必须声明适用模型及独立检查点。两枚 Mark 不能证明一般仿射或非刚性变换；补偿不能把真实线路、开窗、孔位或装配偏差校正掉。标定失效、坐标图不连通、残差超限或设备能力不匹配时，运行入口必须 `Blocked` 或 `NotQualified`，不能用默认变换继续生产。

Coverage Planning Engine 负责把目标、FOV、重叠率、边界、遮挡、运动限制和设备节拍转化为可验证的 Inspection Plan：

```text
Target Set → FOV Candidates → Coverage / Overlap → Motion Constraints
          → Ordered Path → Inspection Plan → Coverage Verification
```

计划必须报告未覆盖目标、重复覆盖、不可达位置、运动风险、预计节拍和降级原因。SPI、AOI、钢网可以复用规划算法，但目标定义、允许覆盖和缺陷风险由各领域拥有。

设备能力采用统一的能力描述和探针结果：`CapabilityId`、版本、状态、健康度、限制、资源需求、校验时间和证据。相机、光源、运动、GPU、PLC、3D 传感器、MES 和 AI 后端均必须通过能力检查进入产品装配；能力存在不等于已完成标定、协议应用或生产资格。

能力准入分别检查“已发现、当前可用、配置已应用并回读、所需标定有效、所需资格有效”，再按本次任务的权限、资源和安全前提派生生产就绪结论。这些是可独立失效的检查维度，不建立 `Discovered → Available → Configured → Calibrated → Qualified` 的万能状态机；软件能力无需标定时使用获批的 `NotApplicable` 理由，不能伪造标定通过。准入结果绑定能力版本、设备 epoch、检查时间/有效期、证据和阻断原因；任一必需检查未知、过期或失败，整体不能显示可生产。诊断页逐项显示缺少哪项、影响哪个任务及恢复动作；相机连接正常或 GPU 被发现不等于采集/AI 任务已就绪。

### 3.9 工程库、插件与离线工作区

平台建立版本化工程库，但库对象仍按领域分型：

- `ComponentLibrary`、`PadLibrary`、`PackageLibrary`；
- `StencilOpeningLibrary`、`DepositStrategyLibrary`；
- `DefectLibrary`、`InspectionStrategyLibrary`；
- `GoldenSample`、参考图像、参考 3D、SOP 和历史案例；
- `AIModelLibrary` 及其数据集、模型、后端和适用范围。

库对象必须支持草稿、审核、发布、废止、兼容性、来源、适用域和权限。历史检测使用运行时清单锁定的库快照，不能因为库中对象后来被修改而改变历史解释。

插件与平台模块必须区分：模块由产品装配固定，插件是具备独立版本和能力声明的可替换扩展。插件至少提供 `PluginManifest`、版本、能力、依赖、兼容范围、权限、资源预算、可选 WPF UI 贡献、迁移说明、签名/许可证和卸载后的 `NotReady` 行为。插件不得直接写入领域事实、绕过权限或持有未声明的设备资源；算法插件的输出必须回到批准的 Pipeline、Measurement、Rule 或 AI 候选契约。

离线工程能力至少规划为：离线编程、离线调试/回放、复判站和质量分析站。它们可以使用同一套 Contracts、Program、Recipe、Pipeline、Evidence 和 Review 契约，但不得复制生产状态机、另建结果事实或使用“离线保存即生产发布”的隐式路径。离线产物必须经过验证、审批和部署，生产设备只接受签名且能力匹配的运行时清单。

### 3.10 证据图、数据生命周期与角色工作区

证据关系应能沿以下链路回溯：

```text
Product / Board / Unit
  → Target / ROI
  → Image / Raw3D / HeightField
  → MeasurementSet / CoverageResult / InspectionFact
  → RuleEvaluation / InspectionDecision
  → Decisioning / MachineDecision
  → EvidenceCommit / ResultCommitReceipt
  → ReviewClaim / ReviewDecision / FinalDisposition
  → DispositionCommitReceipt / RouteAuthorization
```

对多层 PCB、HDI、FPC 和刚柔结合板，身份链还必须能够关联 `Panel`、`Layer/Side`、`RollSegment`、`Carrier`、`ProcessRouteRevision` 和 `StationInstance`；双面翻板、多次积层、卷段连续检测、分板、返工和重检通过明确实体与尝试身份表达。

这是一张证据关系图，不是新的事实存储或事件溯源要求。数据生命周期按用途分层：`Raw`、`Working`、`Evidence`、`Fact`、`Archive`。原始数据和派生证据按保留策略管理，生产事实不可覆盖，回放和候选必须使用隔离命名空间。所有层级都要保留来源、hash、版本、权限和删除/归档审计。

`RouteAssessment` 消费提交回执所绑定的 `MachineDecision`、`CoverageResult`、适用资格状态、`RequiredEvidenceSet`、`QualityPlanRevision`、已提交 `ExternalTestFact` 和必要的 `ReviewDecision`，并可引用上游工位/历史尝试的处置事实。本次尚未提交的 `FinalDisposition` 不是本次评价的前置输入，避免评价与处置互相等待。缺输入时明确报告缺口；复判或迟到事实到达后追加新的评价版本，不覆盖旧评价。路线评价不读取原始图像/HeightField/MeasurementSet 重新判缺陷，不使用 UI 当前值或 `latest` Recipe，也不重新运行领域 Rule。本机生产评价归属设备侧既有 Orchestrator 应用链，质量中心拥有其批准范围内的跨站质量评价及投影，DataService 负责提交/授权校验；三者均不得成为第二个 Decisioning。

评价的 `AuthorityScope` 必须区分用途、产品/领域、站点、实体类型/ID、路线/步骤及 revision 流。`LocalStation/BoardRun` 表示本机生产评价范围；`ProcessRoute/Panel/Lot/CrossSite` 表示按质量计划明确归属的路线或集合范围；`QualityInvestigation` 表示质量调查用途，不能与实体类型混成互斥的一个枚举。同一范围与评价流只有一个登记的语义 Producer 和提交 Owner；配置继承、重叠实体或改名不能制造第二个权威。C-04/C-08 在现有目录中登记本机评价组件、中心评价组件及其范围，禁止双方竞争更新同一个 Assessment。

质量中心的跨站/批次评价只能作为本机质量政策的版本固定输入，或形成既有 HoldRequest、NCR/CAPA、重评请求等质量事件，不能替换本机评价、机判、处置或签发设备授权。本机 PASS 与适用的有效质量 Hold 同时存在时，正常质量放行必须阻断；解除 Hold 必须由其所属批准流程提交并回读，设备侧不能用本机 PASS 清除。中心不可用时，按批准的离线政策使用仍有效的本机输入；若所需跨站证据、Hold 同步新鲜度或解除回执不足，则保持缺口/Hold，不临时升级本机为跨站权威，也不要求在线检测每步同步调用中心。UI 分开显示本机评价、跨站质量限制及其范围、版本和生效回执。

用于处置的评价必须绑定不可变 `RouteAssessmentContext`，由 C-04/C-08 在现有结果/路线契约中登记，作为评价输入快照，不建立第二套统计库或事实存储。快照至少固定：

| 输入组 | 必须固定的内容 |
|---|---|
| 评价与运行身份 | `AssessmentId/Revision`、上下文 hash、创建时间、AuthorityScope/评价用途/Producer、运行作用域及实体/路线步骤；现有 AOI 链使用精确 BoardRun 引用 |
| 规则依据 | 运行清单、产品/路线/步骤、QualityPlan、RequiredEvidenceSet、条件及事实选择/替代政策的精确版本/hash，评价器实现版本 |
| 已接纳事实集合 | 每项 Fact/Coverage/ExternalTest/Review 的 ID、revision、hash、来源尝试/工位和提交回执引用；MachineDecision ID/revision 及本次读取的 activationVersion |
| 一致性边界 | 消费者标识及按生产者/epoch/分区记录的已处理序列水位，已知序列缺口、迟到/冲突标记和未满足证据项；不得压成一个全局时间戳 |
| 资格与条件 | 评价时采用的资格记录/有效期/撤销状态证据、条件求值输入与结果、覆盖选择/替代明细及原因 |

评价先固定输入集合再计算；本地使用一致性读取，跨站使用已提交回执及其版本固定的输入集合，不声称存在跨设备全局事务或全局顺序。消费水位用于说明已处理到哪里，精确引用清单说明本次实际用了什么，两者不能互相替代。存在序列缺口时，不得以最大已见序列冒充连续完成水位；缺口是否影响本次要求必须由 RequiredEvidenceSet 的完成条件判定，无法证明齐备时阻断正常质量放行。

迟到事实、新复判或资格撤销只触发新的评价版本/质量事件，不修改旧上下文。回放旧评价使用当时的事实与资格快照，不读取当前资格覆盖历史解释；签发/执行新的生产动作仍须复查当前有效性。已形成处置门闩或已出站时，新评价不得回写已执行处置或驱动原授权再次执行，应沿既有 Hold/NCR/受控返工流程处理。UI 必须显示所见评价版本、证据缺口及迟到状态，不能在后台输入已变化时继续把旧 PASS 当作当前可放行结论。

UI 按角色组织任务工作区，而不是按内部 DLL 或算法模块暴露页面：操作员、编程员、视觉/计量工程师、复判员、质量人员、维护人员和管理员拥有不同的首屏信息、命令、权限和恢复路径。所有产品客户端统一采用 **WPF + DevExpress**。共享的是 WPF Design System、控件和交互约定，专业产品仍拥有自己的任务流、术语、对象和页面。

### 3.11 性能执行原则

采集到存储的热路径按以下方向设计，但是否采用 DMA、GPU、零拷贝或特定并行度必须由目标机实测决定：

```text
Camera / Sensor → BufferPool → Preprocess / GPU
                → Pipeline → Measurement → Evidence / Storage
```

必须明确帧/高度图/点云的所有权、租约、生命周期、队列上限、背压、取消和失败释放。减少不必要拷贝是优化目标，不得为了“零拷贝”破坏资源安全、可诊断性或跨进程边界。性能证据至少记录代表性板型、输入规模、冷/热状态、并发度、P50/P95/P99、内存/CPU/GPU/句柄、磁盘和长稳增长；没有目标 Profile 时标记 `PendingProfile`，不填宣传值。

### 3.12 V0.5 Contract 冻结前的架构要求

本节把进入 Contract 阶段前必须冻结的高风险边界转成可执行要求。它们属于架构门禁和契约准备；具体成熟度仍按第 14.4 节和对应模块指导判定。

#### 3.12.1 Program 与 Recipe 的字段边界

`InspectionProgram` 只描述产品要检查的目标和意图，至少包含 `Target`、`InspectionItem`、`InspectionIntent`、`InspectionCoverageSpecRef`、`MeasurementSpecRef` 和 `StrategyType`。`InspectionIntent` 至少区分 `ManufacturingPatternConformance`、`ProcessDefectDetection`、`FinalAppearanceAcceptance` 和 `DimensionalMetrology`；例如线路图形符合性、阻焊过程缺陷、成品外观和板外形尺寸不能共用一个结果语义。`Coverage` 不再作为与 `InspectionCoverageSpec` 并列的内嵌权威字段；覆盖目标、范围、方法、观察条件和覆盖要求统一由被引用的 `InspectionCoverageSpec` 管理。它不保存设备运行时参数、当前曝光值或硬件句柄。

`Recipe` 只描述执行方式，至少包含 `AlgorithmParameter`、`Lighting`、`Exposure`、`Threshold`、`ToleranceInstance` 和 `RuntimeParameter`。它不定义产品主数据、对象身份或跨产品的领域语义。

二者都必须引用版本化的产品、库、算法、设备能力和标定快照。参数归属存在争议时，先在 Contract/Decision 中解决，不能由编程器或 UI 自行决定。

#### 3.12.2 Pipeline、Decision 与 Commit 的边界

检测结果的逻辑依赖和提交顺序如下。箭头不要求把所有计算串行执行，覆盖与量测可在批准的 DAG 中并行汇合；任何缺失/无效项均要进入事实和判定，不能要求成功量测后才能记录失败：

```text
Pipeline
  → MeasurementSet
  → CoverageResult
  → InspectionFact
  → RuleEvaluation
  → InspectionDecision
  → Decisioning
  → MachineDecision
  → EvidenceCommit
  → ResultCommitReceipt
```

Pipeline 重试只重新计算或回放计算；事实提交重试只处理幂等提交和回执查询。必须分别定义 `CalculationIdentity` 和 `CommitIdentity`：前者由输入快照、参数、算法/模型版本、后端和确定性等级组成，后者由待提交事实及其版本组成。`operationId` 是一次操作的追踪身份，不得当作 `FactId` 或提交身份。GPU/并行计算只有在后端、精度、确定性等级和容差均冻结时才能声称可复现，不能仅凭相同输入宣称字节一致。断电恢复、Replay、Shadow 和离线候选不得重复创建生产事实，也不得把“文件已生成”当成提交成功。

当前 AOI 链的机判权威沿用 `DEV-ARC-005`：`Aoi.Decisioning` 在 Orchestrator 进程内创建 `decisionId/revision`；Orchestrator 的串行 BoardRun actor 拥有 active 指针和 activationVersion，并唯一发布机判事件。`Asun.Vision.Decisioning` 只提供无副作用评价能力，VisionHost 只产出领域事实与局部规则结果。`InspectionDecision` 是这些输出的提议/投影，不引入第二套 decisionId、active revision 或持久化权威。创建机判与激活机判是不同职责，禁止 UI、AI、Quality Hub、ReviewService、ExternalTest Adapter 或领域规则直接创建权威 revision、切换 active 指针或发布机判事件。

现有 [Aoi.Decision.Application 工程](../../src/Product/Aoi.Decision.Application/Aoi.Decision.Application.csproj) 引用 AOI 契约及领域工程，其 [DecisionInputSet](../../src/Product/Aoi.Decision.Domain/DecisionModels.cs) 仍绑定 BoardRun/Attempt，由 [AOI 结果提交与激活入口](../../src/Apps/Aoi.Orchestrator/AoiDataResultCommitPort.cs) 消费。因此，多产品可复用的是已定义的评价能力和职责分工，不能仅凭名称或通用纯引擎存在就宣称生产机判应用已支持 SPI、PCB、HDI 或卷料。C-04 接入新产品前必须核对身份、领域输入/策略、缺陷词典、持久化、active 状态、提交和真实调用者；由权威标准明确复用/上提后的语义 Owner 和产品隔离方式，再同步契约与消费者回归。该产品的机判接入契约从 ContractCandidate 起按第 14.6 节逐级验证，未通过准入不得启用生产链，不强套 AOI BoardRun 字段或另建平行机判权威。

非 AOI 产品的机判接入契约进入 `Contracted` 前，须在 `DEV-ARC-005` 的既有变更流程中批准其 `AuthorityScope`、Producer 与 Activation Owner 的复用或扩展分工；`Aoi.Decisioning` 不因现有实现存在而自动成为该产品的 Producer。批准及生产准入未关闭时，可在获批开发范围内推进 Engineering、Replay 和 Qualification 研究链，保持用途隔离；工程链运行或研究结果不授予生产机判创建、active 激活或设备授权能力，真实设备研究仍遵守其适用权限与安全门禁。

首次机判只能由权威 Decisioning 创建，后续 revision 仅能由其在合法重检或显式 `ReevaluateDecision` 路径中追加；同一计算/提交身份重试不得重复创建。结果提交后，Orchestrator 按预期 BoardRun 状态版本、activationVersion、尝试身份和处置锁校验，再切换 active 指针；旧机判始终不可变。人工复判独立提交 `ReviewDecision`，供 Orchestrator 形成处置，不要求为每次复判重造机判；确需重新机判时必须走批准的显式重评流程。迟到 AI/外部事实只能按政策请求重评或形成影子/质量事件，不能绕过锁。架构门禁检查创建/激活/发布的调用边界，状态测试覆盖旧版激活、错 Attempt、重复请求、处置锁定和出站后迟到结果。

共享 `MachineDecision` 语义不授予生产创建权限。每个产品的接入登记必须把 `InspectionDomain + ProductProfile + 站点/运行或决策流范围` 解析到唯一的 `AuthoritySource`、`Producer`、`StateOwner`、`CommitOwner`，并引用拥有 active 聚合的 Activation Owner；这些角色沿用现有字段和状态规范，不新建一套 DecisionOwner 字段别名。AOI 当前 Producer 仍为 `Aoi.Decisioning`。新增产品只有通过 `DEV-ARC-005` 的权威变更/扩展及消费者验证才可接入，公共 DTO 或配置选择器不能隐式授权。一个运行汇合多个领域提议时，仍只有一个负责最终机判的决策流；不得按领域拆出相互竞争的 active 机判。权威作用域缺失、重叠或 Producer 不匹配时阻断该产品准入，未来平台化也必须在权威源显式完成。

多产品绑定复用第 14.6 节 `AuthorityScope`；`DecisionFlowScope` 只表示其决策用途投影，不增设并行 Scope 字段或 Owner 注册表。解析由服务端按获批装配、用途和精确版本完成，拒绝零/多匹配、父子重叠和跨产品调用；UI 不能指定一个 Producer 绕过准入。多个领域结果参与同一最终机判时，必须冻结融合政策、必需输入、冲突/缺失/无效处理与版本，不以“最新结果”或未经批准的投票代替质量规则。

公共 Envelope 和机判生命周期可以复用，PCB、SPI、AOI 的强类型领域载荷、规则及专业对象仍保持独立；不要求所有领域共用一套含大量可选字段的 CLR 结果类型。领域结果不能因此获得第二个权威机判身份。平台职责也不意味着全厂单进程单例；允许按获批、不重叠的作用域独立部署。现有 BoardRun 经语义和消费者验证后可复用，新运行形态不适配时走现有权威契约扩展，不能仅因产品名不同就重建运行系统。新增产品准入失败只阻断该产品及确认受影响的共享消费者，不把现有 AOI 自动降为候选状态。

处置政策由既有产品/质量批准流程拥有；Orchestrator 依据该政策、权威机判、已提交复判和路线评价形成 `FinalDisposition`；DataService 验证并持久化处置、签发 `RouteAuthorization`；MotionGateway 兑换授权执行物理动作并返回传感器 ACK。政策审批、处置形成、提交签发和物理执行分别登记运行责任主体，不能用一个“处置执行 Owner”同时代指 Orchestrator 和 MotionGateway。

`EvidenceCommit` 表示现有 DataService 结果提交协议的边界，不新增提交服务。证据对象可以提前 staging，但须完成 durable CAS publish，随后由结果事务原子写入证据清单、机判引用、结果索引、回执和 Outbox，才对外可见。提交恢复按冻结 session/幂等键和 hash 继续；失败残留由既有保留/租约策略处理，不能把已落盘文件当成已提交事实。

#### 3.12.3 计量、MSA 与 GR&R

计量 Contract 需要从“数值 + PASS/FAIL”扩展为：

```text
MeasurementDefinition
  → MeasurementSpec
  → CalibrationArtifact
  → UncertaintyBudget
  → Repeatability / Reproducibility
  → Bias / Linearity / Stability
  → MSA / GR&R
  → Qualification
```

SPI 至少覆盖高度、面积、体积、偏移和适用时的共面性；每项量测必须声明单位、参考面、有效域、边界条件、质量标识、容差来源和失效原因。标准件、样板、测量系统分析、GR&R 和计量资格是后续生产门禁，不能用普通单元测试、合成数据或截图代替。

PCB 专业计量按第 2.11 节将量值、方法、Datum、抽样/排除策略和不确定度模型绑定为可资格化组合；通用 MeasurementResult 的数值正确不能自动授予线宽、铜环或全板位置精度资格。标定、计量研究、客户规则和 SPC 分别拥有各自批准依据，不合并为新的 PCB 专属资格/验收 Schema。

#### 3.12.4 坐标图与多 FOV/拼接边界

坐标关系必须以可版本化的 `CoordinateGraph` 表达，而不是隐含在多个转换字段中。每条边固定 source/target、变换类型/方向、版本/hash、单位、有效域和来源；依来源引用批准的坐标定义/约定、`CalibrationArtifact` 或实际运行拟合 Artifact，并保留适用的设备/实体/boot、残差与不确定度。标定来源必须有真实标定引用，运行配准须固定实际实例及其标定依赖；PixelCorner→PixelCenter 等定义性转换引用版本化约定与黄金样例，不伪造物理标定或拟合残差。按坐标权威规范验证所需路径的连通性、方向/域和版本、重复边/冲突路径及环路闭合；超限或不可解析时阻断该路径使用，不能以单位阵或另一设备的标定兜底。

`CoveragePlanning` 和 `MultiFovRegistration/Stitching` 是两个独立能力：

```text
CoveragePlanning：拍哪里、怎么走、是否覆盖
Registration/Stitching：不同 FOV 如何进入同一全局计量坐标
```

多 FOV 能力还需定义 `GlobalCoordinateMapping`、`RegistrationResidual`、`SeamQuality` 和 `GlobalScaleConsistency`。拼接图只能在注册质量满足门禁时进入全局计量；显示拼接成功不代表计量资格成立。

PCB 跨 FOV 计量还须按第 2.11.5 节验证同特征一致性、边角/接缝偏差和局部到全局误差传播；全局拼接质量失败应标明受影响量值与覆盖，不能用单个 FOV 的重复性推定整板准确度。

#### 3.12.5 状态分类与结果语义

不同状态机必须分开定义：`ProductState`、`ProgramState`、`RecipeState`、`CalibrationState`、`MachineState`、`InspectionState`、`MeasurementState`、`DecisionState`、`ReviewState`、`DeploymentState` 和 `AIState`。`Blocked` 必须带领域前缀或原因码，例如 `CalibrationBlocked`、`ProgramBlocked`、`InspectionBlocked`，不能用一个无上下文的字符串覆盖所有阻断。

量测有效性、规则评价、机判和控制状态必须分开，序列化值以既有权威契约为准：

| 维度 | 语义与权威 |
|---|---|
| 量测 | 数值、单位、有效性、未测原因和 `MeasurementQuality`；数值有效不等于产品合格，超限由规则评价 |
| 规则 | 保存满足/不满足、未执行或不适用的结果、依据和原因；缺输入不等于满足 |
| 机判 | 沿用 `DEV-ARC-005` 的 `MachineDecisionStatus`：`Pending, Pass, Ng, ReviewRequired, ReacquireRequired, Invalid` |
| 控制与处置 | Hold、恢复、位置未知和最终处置使用 BoardRun 对应正交状态，不能添加到机判枚举中替代既有值 |

相机异常、标定失效、数据缺失或规则未执行时，保存原因和无效事实，由批准的判定/处置策略映射为重新采集、复判、隔离或停止；不强制算法成功才能提交异常证据。本文的 `Unknown/Blocked/NotQualified` 是带所属对象的语义描述，不新增同名机判状态；无法确定的结果不得转换成 Pass，也不得丢失原因为普通缺陷 Ng。

#### 3.12.6 AsunImage、HALCON 与视觉后端边界

视觉后端使用 AsunImage；不设置 AsunImage/DevExpress 依赖核验或授权门禁。调用边界为：

```text
Domain
  → Inspection Pipeline
  → Vision Contract
  → ImageLibDotNet / AsunImage 公共能力
  → HALCON 算子与适配边界
```

HALCON 是视觉算法后端，AsunImage 是批准的薄封装；二者都不是产品应用框架。领域、流程、配方、计量资格、权限、证据和 UI 不得反向依赖 HALCON 内部对象。未经明确授权不得扫描或修改 AsunImage 内部实现，不得猜测未确认的公共 API。未来接入其它算法后端时，只能通过批准的 `Vision Contract` 和能力声明，不得改变领域契约。

#### 3.12.7 WPF 渲染契约

产品 UI 技术路线已经冻结为 WPF + DevExpress。为避免 WPF 页面直接绑定视觉后端，平台需要在 WPF UI 层定义可测试的渲染契约，例如 `IImageViewport`、`IRoiOverlay`、`IMeasurementOverlay`、`ICoordinateOverlay` 和 `I3DViewport`。

契约必须明确缩放、平移、坐标变换、ROI 交互、命中测试、叠加层、选择状态、空数据/失效数据表现和渲染性能。Viewport 只消费不可变帧、证据和 Overlay DTO，不持有 HALCON/AsunImage 原生对象，也不拥有生产判定。真实 WPF、UIA、键盘、DPI、最小分辨率和三语验证仍由产品页面承担。

#### 3.12.8 安全与安全功能边界

安全架构需要统一覆盖 RBAC/ABAC、密钥和凭证、代码签名、插件签名、模型签名、安全更新、证书、审计完整性、SBOM、依赖漏洞和外部工程文件校验。Recipe、Calibration、AI Model、Plugin 和工程库对象进入生产前必须验证来源、hash、签名、适用域、版本和撤销状态。

质量控制与功能安全必须分开：急停、门禁、STO、安全回路和运动安全由设备安全体系和安全控制器负责；AI、MES、Quality Hub 或普通 UI 只能提出受控请求，不能直接充当安全功能。质量 Hold 可以触发受控 RunControl 请求，但不能绕过安全边界或直接写安全状态。产品网络安全的法定义务、SBOM、漏洞披露、支持期与安全开发生命周期要求见第 2.12.4 节；远程服务与诊断通道的受控条件见第 3.16.5 节。

#### 3.12.9 能力分类与架构门禁

Capability Resolver 至少区分：

| 能力类别 | 示例 |
|---|---|
| `DeviceCapability` | Camera、Light、Motion、PLC、3D Sensor |
| `ComputeCapability` | CPU、GPU、CUDA、ONNX Backend、显存预算 |
| `MetrologyCapability` | Calibration、Measurement、MSA/GR&R、资格有效期 |
| `IntegrationCapability` | MES、OPC UA、IPC-CFX、离线缓存和回执 |
| `ProductCapability` | 当前产品允许的领域功能和工作区 |

能力必须同时有版本、状态、健康度、限制、检查时间和证据。发现能力不等于能力已标定、已授权或具备生产资格。

#### 3.12.10 架构 CI、资格矩阵与术语

架构约束必须逐步转为自动门禁：依赖方向和循环检查、公共 API 兼容性、Schema 兼容性、插件 Manifest 校验、SBOM、许可证和依赖漏洞扫描。文档中的禁止路径不能只依赖人工记忆；违规应在合并前阻止或明确登记例外。

测试/资格矩阵至少包含 Golden Board、Golden/Silver Sample、Reference Image、Reference 3D、缺陷注入、误报、漏报、重复性、GR&R、长稳、断电恢复、相机/光源/运动/PLC/GPU 故障、磁盘满和网络中断。软件测试、视觉测试、计量测试、系统测试、HIL、FAT、SAT 和 ProductionAccepted 必须分层记录，Mock、Simulator、截图和单元测试不能替代真实设备资格。

建立统一工业视觉术语表，至少为 `Attempt`、`Fact`、`Candidate`、`Decision`、`ReviewClaim`、`Evidence`、`Snapshot`、`Manifest`、`Measurement`、`RuleEvaluation`、`Disposition` 和 `RouteAuthorization` 记录定义、Owner、生命周期、权威来源、持久化方式和消费者。术语表是 Contract 的输入，不新增第二套状态或数据模型。

#### 3.12.11 Canonical bytes、内容摘要与签名边界

生产配置、事实提交、回执、安全授权和跨站完整性证明必须引用其权威契约批准的 Canonical Profile。入口沿用 `DEV-ARC-005` 第 10 节及对象所属 Schema；统一的是 Profile 登记、共享实现和测试门禁，不强迫所有对象改成一种 JSON。现有安全令牌使用固定投影 `ASUN Canonical Security JSON v1`，一般 Proto 对象、Decision Graph、ChannelMix 等保留各自已批准规则；不得改变既有内容 hash 或签名域来“统一格式”。

| Profile 必须固定的项目 | 可执行要求 |
|---|---|
| 字节和字段投影 | 编码/BOM、长度前缀、字段白名单及顺序、大小写/Unicode、缺失/null/default、未知字段处理；明确排除签名自身、摘要自身或其它派生字段，禁止 hash 自引用 |
| 集合与数值 | 字典排序与重复键拒绝；数组逐字段声明保序或按业务键排序；数值类型/精度/舍入、NaN/Infinity/负零、单位规范化和时间格式，不受本机区域设置影响 |
| 身份与算法 | 对象类型、Schema major、Profile ID/版本、hash 算法和域分离；签名算法/编码、key 用途及签名输入究竟是 payload 还是其摘要，禁止隐式二次 hash 或自动算法协商 |
| 验证与演进 | 重算而非相信调用方 hash；验证签名、用途、批准来源和撤销；Profile 改版产生新版本及兼容策略，历史内容仍按原规则解释 |

相同语义是否对应相同字节，由该 Profile 的等价规则定义。例如数值字段 `0.1/0.100` 可按批准的数值表示归一，但字符串或原始文件不能因此改写；有序步骤/图像通道交换位置必须改变摘要，只有声明无序的集合才排序。单位转换发生在明确的领域规范化步骤并保留来源，签名器不能擅自换算。原始图像/文件的字节摘要、配置内容摘要、传输块摘要和审计链摘要各有用途，不能互代。

安全执行令牌继续遵守 `DEV-ARC-005` 的严格字段集、P-256/P1363 和 `SHA-256(canonicalPayloadBytes)` 签名输入；普通协议的未知字段保留规则不得套到拒绝未知字段的安全投影。不同 Profile 对负零、null 或字段顺序已有明确规则时分别执行，不能在公共工具中静默覆盖。固定 Protobuf 实现的 deterministic 输出也须经黄金向量证明，不能单凭开关推定跨语言/版本字节稳定。

C-02/C-04/C-06 共用权威 Profile 引用和黄金向量。至少验证受支持的序列化实现/版本在相同输入下 bytes/hash 一致且签名互验，覆盖区域设置、NFC、缺失与默认、字典乱序、数组换序、边界数值、未知字段、重复键及错误 domain/key/schema；未支持的组合阻断。ECDSA 签名可能因随机数不同而产生不同字节，跨实现验收要求互验成功，不要求每次签名字节相等。黄金向量不能代替密钥治理或目标机安全资格。

### 3.13 传感与成像模态能力层

成像原理的量程、遮挡、反射响应、重建条件和误差结构必须进入能力与适用域声明，供量测有效性、跨机移植和资格校验消费。模态目录列出可扩展方向，不要求每个产品实现全部模态。

模态是能力层的属性，不是领域对象。`SensingModality` 与 `IlluminationConfiguration` 在既有 `DeviceCapability`/`MetrologyCapability` 中登记，不新建能力注册表。

#### 3.13.1 模态目录与必须声明的属性

| 模态族 | 典型实现 | 主要适用 | 固有限制（必须显式声明，不得靠算法掩盖） |
|---|---|---|---|
| 2D 明场/同轴 | 同轴照明、环形白光 | 图形、字符、表面 | 高反表面过曝、低对比材料边缘定位偏差 |
| 2D 多角度/多方位彩色 | 分区 RGB 侧光、低角度 | 焊点形貌、共面线索、极性 | 角度依赖的阴影与互遮挡；颜色响应随表面处理变化 |
| 2D 背光/透射 | 背光板 | 外形、孔、覆盖膜、透明材料 | 只反映投影轮廓，不反映表面与厚度 |
| 2D 特殊波段 | UV、红外/SWIR、偏振 | 三防漆、污染、特定材料对比 | 波段可用性依赖材料；不得由波段响应推断厚度或成分 |
| 3D 条纹相移轮廓术 | 多频/多相位数字条纹投影 | 锡膏、焊点、共面性 | 相位解缠模糊、阴影区无数据、镜面与多重反射造成伪高度；频率组合决定量程与分辨率 |
| 3D 激光三角 | 线激光/点激光三角测量 | 高度剖面、钢网、胶路 | 遮挡与阴影方向性、镜面反射丢点、激光散斑；扫描方向影响结果 |
| 3D 共焦 | 色散共焦、扫描共焦 | 经验证的高度/厚度与局部结构 | 量程、数值孔径、表面倾角、透明多界面和扫描速度限制随设备配置确定 |
| 3D 干涉 | 白光干涉等 | 经验证的表面形貌与微小结构 | 振动、相干/多界面信号、倾角、扫描范围和表面条件须单独验证 |
| 3D 几何立体/多视角 | 双目/多目 | 经验证的形貌与几何 | 对应关系、纹理、遮挡和相机几何影响重建；弱纹理区需明确处理 |
| 光度立体 | 多光照方向下的反射观测 | 表面法向、形貌候选或经资格验证的量测 | 依赖照明与反射模型，受镜面、阴影和积分漂移影响；不能套用几何立体的纹理匹配假设 |
| 形貌推断类 | Shape-from-Shading 等 | 辅助线索 | 不具备计量语义，除非单独取得资格，否则只能作为候选/辅助 |
| 读码 | 一维码、DataMatrix、DPM | 板与单元身份 | 见第 3.15 节；读码质量不是图像质量 |

每个模态实例必须在能力声明中固定：量程与景深、横向与纵向分辨率、采样密度、测高/测距的重复性与已验证不确定度贡献、可接受的表面/材料域、倾角与曲率限制、遮挡与阴影几何、镜面与多重反射的处理策略及其失效标记、相位/对应关系的模糊解算方式与失败表现、温漂与预热要求、与运动/编码器的同步要求、以及数据有效掩膜的生成规则。这些字段进入 `MetrologyCapability` 的适用域（第 2.11.4 节），缺失维度必须附理由，不得视为无限制。

#### 3.13.2 模态相关的数据链与有效性

既有 3D 生命周期保持不变，只是每个阶段必须携带模态与其有效性证据：

```text
ModalityConfiguration（模态、光源、波段、频率组合、投影/扫描几何、同步）
  → RawSensorData（原始帧/相位图/剖面，含模态原生单位与坏点标记）
  → Reconstructed3DData（含解缠状态、置信/有效掩膜、伪高度候选标记）
  → CalibratedHeightField → CorrectedHeightField → ReferenceSurface
  → InspectionHeightField → MeasurementSet
```

- **无数据不等于零高度**。阴影、遮挡、丢点、解缠失败区必须保留为无效掩膜并带原因，不得插值后按普通数值参与量测；允许的插值必须由批准方法声明并进入不确定度；
- **伪高度风险必须验证**。声明镜面、多重反射等失效的检测方法、挑战样本和已知盲区；已识别异常标为可疑或无效，不能靠阈值截断当作真实形貌。无法可靠区分的条件限制适用域或引入获批补充方法，不承诺所有伪高度都能自动识别；
- **模态融合是受控合成**。2D 与 3D、多角度与单角度、多模态融合的结果必须记录各来源的有效性；必需来源失效且无获批替代方案时，该目标的融合结果无效；经批准并验证的冗余/降级策略可采用剩余有效来源，但必须重评可观察范围、量测质量、不确定度与资格，并保留缺失来源和降级原因。不得以有效来源掩盖缺失或伪造完整覆盖；
- **模态切换即新条件**。更换模态、光源配置、频率组合、扫描方向或倍率属于影响量测的配置变化，按第 2.11.4 节触发适用域与资格的影响校验；
- **飞拍与运动同步**。运动中采集必须固定触发源、触发抖动、曝光与运动的时序关系、像素拖影预算与编码器/位置对应关系；同步失败必须使受影响帧无效，不能按“图像看起来清楚”继续；
- **预热与稳定**。需要预热的模态必须有明确的就绪条件与验证方式，未达条件按 `Blocked` 处理（与第 3.16.3 节点检配合）。

#### 3.13.3 模态与领域、资格的关系

- 模态属于能力层，领域只声明**所需能力与可观察条件**，不指定具体厂商实现；
- 同一被测量由不同模态获得时，是不同的测量方法，必须分别取得资格，未经等效性验证和批准映射，结果不可互相替代；是否汇总由 `MetricDefinition/SubgroupPolicy` 明确方法分层、适用域及不确定度要求（第 2.11.4、8.3 节）；
- 模态限制必须能被 `CoverageResult` 表达：应检目标因遮挡/阴影/材料不可观察时记为 `NotCovered` 或对应无效原因；`NotApplicable` 仅用于计划已批准的不适用范围，不能事后豁免漏检，不得折算为 PASS（第 2.6 节）；
- 新模态接入按第 3.12.6 节只通过批准的 `Vision Contract` 进入，不得改变领域契约；模态适配器不得把 SDK 类型或厂商语义带入领域层（第 2.8 节）。

能力准入按实际要求匹配“特征/被测量、方法、尺度范围、材料/表面、光学/照明、运动/同步、有效掩膜、标定/资格与适用点检”的已验证组合，再检查本次观测和环境。各维度按用途声明，不适用项有理由；不能机械要求所有设备安装全部传感器。拥有某种模态、输出高度图或达到某个像素尺寸，都不能单独证明计量能力；组合声明也必须有研究证据支撑，不能以配置匹配替代物理资格。

### 3.14 板流、轨道、搬送与产线握手

在线设备必须声明板流实体、轨道资源、上下游交接、并发和位置恢复。既有权威分工保持不变：质量路由授权由 DataService 签发，物理动作由 MotionGateway 执行；协议握手不拥有质量放行权。

#### 3.14.1 板流实体与身份

以下身份在 `C-01` 既有身份契约中登记，属于实体与位置语义，不承载质量判定：

| 对象 | 含义 | 边界 |
|---|---|---|
| `Lane` / `Track` | 设备内的独立输送与检测通道（单轨、双轨、多轨） | 轨道是资源与并发单位，不是产品或领域 |
| `ConveyorSegment` | 入口、检测位、出口、缓存等可占用的位置段 | 位置是物理事实，不得由软件状态推断 |
| `BoardPosition` | 板在设备内的当前位置及其证据（传感器、编码器、夹紧状态） | 无传感器证据时为 `Unknown`，不得默认在位或已离开 |
| `FixtureCarrier` / `CarrierSlot` | 载具及其槽位（FPC、片料、异形板） | 载具身份与板身份分离，一个载具可承载多个单元 |
| `HandoffSession` | 与上游/下游设备的一次交接会话 | 交接会话成功不等于质量放行 |

轨道与工位的关系：`StationInstance` 仍是设备实例身份（第 2.10 节），`Lane` 是其内部并发通道。一个 `StationInstance` 可拥有多个 `Lane`；在线输送场景的 `BoardRun` 必须绑定具体 `Lane`；离线、手动装夹和卷料使用已批准的工位/载具/卷运行关系，不虚构轨道，`EffectiveRuntimeManifest` 必须能区分轨道相关的能力、标定与配方差异（例如各轨独立的坐标与标定 Artifact）。

身份与位置复用 [runtime.proto](../../contracts/v1/proto/runtime.proto) 的 `PhysicalBoardLocation`、`track_id`、`station_id`、`slot_id`、位置版本与 PLC 序列，以及既有 Carrier 身份。`Lane` 是轨道能力语义，不能为同一物理通道再生成竞争的 `laneId`；`BoardPosition` 不建立第二个位置 Store。Orchestrator 仍是实体板流语义 Owner，MotionGateway 提供物理执行与传感器证据，协议适配器只提供外部观测和握手。新增拓扑、交接会话或能力差异经 C-01/C-06 契约扩展及消费者验证，不能把本文对象名直接当成已有字段。

#### 3.14.2 并发运行模型

```text
StationInstance
  ├─ Lane A ─ BoardRun(A,n) ─ InspectionAttempt … ─ Decision/Commit ─ Exit
  └─ Lane B ─ BoardRun(B,m) ─ InspectionAttempt … ─ Decision/Commit ─ Exit
        共享：计算资源、GPU、存储、AI 后端、数据库连接、日志
        独立：板身份、配方绑定、判定流、处置门闩、出板授权
```

- 每条轨道的判定与处置流**相互独立**。单轨局部异常不得串写另一轨道的事实或授权。共用运动/安全回路、存储、资源或质量 Hold 的影响必须按批准范围传播，必要时协调停机并重新核验相关授权，不能为了独立性忽略共因故障；
- 共享资源必须有租约、配额与背压（第 3.11 节）。资源不足时按批准策略降级为排队或阻断，**不得**降级为跳过检测、降低覆盖或使用过期标定；
- 轨道间不得共享可变全局状态。相同配方在不同轨道运行时，各自绑定自己的标定、坐标与能力快照（第 3.17 节）；
- 并发度、队列上限与每轨节拍分别登记性能预算；需求负载按轨道合计，供给能力须按共享相机/龙门/GPU/存储瓶颈、仲裁公平性和同时峰值实测，不能把单轨吞吐相加当作多轨产能；
- 多轨机型的复判与处置排队必须能区分轨道，UI 不得把两条轨道的板混在同一个待处理列表而不标明来源。

一个轨道可在不同获准位置段承载多个运行；占用冲突按真实位置段、共享运动空间和采集资源仲裁，不能把“一轨一个全局运行变量”当成并发模型。租约绑定运行、资源、设备 epoch 和有效期，采用固定获取顺序或等价的无死锁策略；取消、故障与重启按物理证据恢复，超时不自动证明资源已释放。出板前再次校验授权中的轨道、位置版本和 PLC 序列，防止跨轨或旧位置授权被兑换。

#### 3.14.3 上下游握手与传输协议

接口按现场连接选择 SMEMA 类电气握手或 IPC-HERMES-9852 信息握手，也可使用获批的转换网关。二者不是每条连接必须叠加的两层；同一连接只能有一个输送控制主路径，避免双重启动。协议适配层独立维护按版本验证的收发状态；以下仅为职责顺序，不是协议报文时序：

```text
上游供板条件 + 本机接收条件
  → 按选定协议协商搬送 → MotionGateway 执行 → 传感器确认在位/交接
  → 身份与配方防错 → 检测/判定/提交/处置
  → DataService 路由授权 + 下游接收条件
  → MotionGateway 兑换授权并执行 → BoardExitAck
```

具体消息方向、撤销、重连和超时以采用的协议版本及互操作测试冻结，不能从本图推断报文顺序。入板、定位、检修运动沿用各自既有 RunControl/Motion 契约；不得强套要求检测结果回执的出板授权而形成循环依赖。

已核对的 Hermes 1.6 示例：第 2.3.3 节及第 3.10～3.12 节规定 `StartTransport` 由下游发往上游，`TransportFinished` 由上游发出，`StopTransport` 由下游发出；不能将三者反向或省去撤销/异常分支后当成完整实现。此定位用于协议适配器契约验证，不把 1.6 自动设为所有现场设备的最低版本；官方来源与核对范围见附录 C。

强制约束：

- Hermes 消息中的板信息（板 ID、面别、工单、上游结论、已知坏板标记）是**外部来源事实**，必须按第 2.10 节的外部事实规则携带来源身份并经校验，不得直接当作本机质量事实或身份权威；
- 协议完成是对端报告，需结合本机传感器、会话身份与位置证据确认实体交接；握手本身不能证明实体已到位、检测完成或质量合格；
- 上游给出的板 ID 与本机读码结果冲突时进入 `Conflict/Hold`，按批准策略处理，不得按“上游优先”或“最新覆盖”自动选择；
- 协议版本与能力必须在 `IntegrationCapability` 中声明并探针确认。协议支持某字段不代表现场上下游设备提供该字段；
- 下游未就绪、缓存满、超时、传输失败必须有明确状态、超时边界与恢复入口；板位置无法确认时保持 `Unknown` 并要求人工核实，不得凭超时推断已离开（第 14.7 节）。

#### 3.14.4 拼板、坏板标记与单元有效性

拼板中的单元并非都需要检测或判定，这一点必须建模，否则分母、良率与放行全部失真。

| 单元状态（语义） | 来源 | 对判定与统计的影响 |
|---|---|---|
| `Valid` | 经批准的单元计划与存在性/标记检查 | 按计划检测；统计归属由指标定义决定，不能将未核实默认成有效 |
| `BadMarkUpstream` | 上游 Hermes/MES 传入的坏板标记 | 保留上游坏板标记与来源；按批准计划检测或跳过，指标纳入/排除由 `MetricDefinition/SubgroupPolicy` 决定，不把标记冒充本机实测缺陷 |
| `BadMarkDetected` | 本机识别的坏板标记（墨点、X-out 标记、缺件标识） | 同上；识别结果本身是事实，须保留证据 |
| `Depaneled/Absent` | 单元已分板或缺失 | 计划已分板按实体谱系移交；意外缺失属于覆盖缺口，不能自动排除；由覆盖计划和指标定义分别处理 |
| `NotInspectedByPlan` | 抽样或计划排除 | 计入未检范围，不得标为 PASS（第 2.7、6.6 节） |
| `Unknown` | 标记不可判读、冲突 | 阻断该单元的正常放行，进入受控处置 |

上述是单元处理语义，不是一个互斥状态枚举。存在性、坏板标记、计划覆盖、实际观察、机判与处置分别归属既有契约，可以组合出现；统计分子/分母、纳入和排除规则统一由已批准的 `MetricDefinition/SubgroupPolicy` 决定。跳过检测必须保留原因与证据，并在 `CoverageResult` 与质量统计中可见；板级结论必须能够说明由哪些单元构成、哪些被排除、依据哪条批准策略；不得把“跳过”折算为合格，也不得因一个单元不良而隐式改变其余单元的事实。

#### 3.14.5 CFX 垂直上报与最小消息集

设备侧向上的信息上报（工单、单元流转、检测结果摘要、设备状态、故障、维护、能耗、资源绩效）通过 IPC-2591 CFX 类通道进行时：

- 上报是**投影**，不是权威事实。上报失败不得修改已提交事实；是否暂停后续生产/放行取决于质量计划的必需回执、离线时限和缓存预算。非必需上报可排队补发，必需确认缺失不能默认继续；投影重放绑定原事件与幂等键；
- 最小消息集按机型确认并登记在 `IntegrationCapability`。声称支持某消息集前必须有真实消费者验证，不能按 SDK 支持推断；
- 设备状态上报使用第 3.16.1 节的状态模型并保留映射表；检测结果上报的粒度、字段与去标识策略按客户合同确定（第 3.19.5 节）；
- 上报通道的排队、离线缓冲、重发与幂等沿用第 8.4 节规则，不新建第二套 Outbox。

#### 3.14.6 板流异常与恢复

必须建模并各自具备状态、证据与恢复入口的异常：卡板、超时未到位、位置未知、掉板、双板进入、方向/面别错误、夹紧失败、载具未识别、上下游不就绪、急停后残留板、断电后在途板。

统一规则：异常首先确定**实体在哪里**，再确定事实状态，最后才决定动作。在原运行中恢复提交或查询动作结果使用原身份，不新建检测尝试；实际重新采集/检测时建立新尝试并保留来源，不能用“重新开始”掩盖未决动作；不得在实体位置未知时签发或重复兑换出板授权（第 9.3、14.7 节）。

### 3.15 板身份、读码、防错与首件/换型门禁

身份获取、防重与程序—板型防错必须在运行准入中校验。读码、上游身份与人工确认保留各自来源，不按最后写入覆盖实体身份。

#### 3.15.1 读码能力与读码事实

`CodeReadingCapability` 在既有能力目录中登记，至少声明支持的码制（一维码、DataMatrix、QR）及标记工艺（如 DPM 直接零件标记）、可读尺寸与模块大小范围、位置与数量、允许的表面与对比条件、解码质量评级方法与门限。

读码结果是事实，必须携带：读取位置与 ROI、原始图像证据、解码内容、码制、解码质量、重试次数、以及失败原因。解码成功、解码器置信度与标准化码质量评级分别记录；仅具备解码功能时，质量评级标为未提供，不能伪造等级。若声明符合码质量标准，还须验证评级方法、光学条件及专用校验资格。质量趋势可供退化预警使用（第 3.16.4 节）。

身份链分为原始观察、解析/裁决和运行绑定三个阶段。CodeReader、Hermes/MES 适配器与人工入口只提供来源观察，不争夺实体身份权威；原始码、规范化规则、来源实例/会话、时间/顺序、图像或报文引用、质量及失败原因均须可回溯。人工更正同样追加观察与依据，不能修改原读码事实。

```text
CodeReader / Hermes / MES / 人工观察
  → Orchestrator：BarcodeAssignmentGraph + 获批 BarcodeIdentityPolicy
  → 解析/冲突处置 + IdentityResolutionReceipt
  → BoardIdentity 的受控绑定 → 清单与配方防错 → 生产准入
```

沿用 [板级编排状态机开发指导](../../docs/40-development/30-runtime/板级编排状态机开发指导.md) 中的 Orchestrator 身份 Owner、`BarcodeAssignmentGraph`、身份冻结和 `IdentityResolutionReceipt`；静态策略输入仍由 BoardDataAdapter 生成 Draft。契约与实现继续使用既有 `BarcodeIdentityPolicy` 表达裁决策略，以来源观察作为输入、`IdentityResolutionReceipt` 记录裁决、`BoardIdentity` 承载受控绑定。本文的 `IdentityResolutionPolicy` 只描述该策略的解析规则；`ResolvedBoardIdentity` 仅为经回执确认的 UI/查询投影，二者不新增正式业务对象、平行 Schema、主键或服务，也不要求重命名既有类型。

尚不能创建正式 BoardRun 时，以已有入板会话、ingress/设备 epoch、位置及事件身份保存观察和冲突证据；已有运行则关联对应 BoardRun/Attempt。身份未决不妨碍取证、板件保管和受控恢复，不允许以“没有裁决身份”为由丢弃记录。只有满足身份策略的绑定才可供后续生产准入使用；临时身份和真实码必须区分，未决冲突不得正常放行。

#### 3.15.2 身份分配与冲突

| 情形 | 处理 | 禁止 |
|---|---|---|
| 读码成功且唯一 | 绑定实体身份，进入后续链路 | — |
| 不可读或无码 | 按**已批准**策略分配 `ProvisionalBoardId`，标记来源为“非读码”，并保留证据 | 不得静默生成顺序号冒充真实板号；不得在不允许无码运行的产品上继续 |
| 同一码重复出现 | 同一读取会话的重复消息幂等合并；获准返修/再检关联同一实体的新尝试；无法区分的重号、不同实体同时占用才进入 `Conflict` | 不得覆盖历史实体，也不得把合法重检或消息重发直接判为身份冲突 |
| 与上游 Hermes/MES 提供的身份不一致 | 进入 `Conflict/Hold`，按批准策略核实 | 不得按固定优先级自动取舍 |
| 拼板单元级码 | 单元身份与板身份分别保留并建立从属关系 | 不得用板号代替单元号做单元级追溯 |

表中“唯一”由权威解析在本产品身份策略规定的工单/批次、实体层级、设备/产线范围内校验，不是查询到全库一次即证明唯一；原始文本相同也可能是不同编码体系，不能未经规则直接合并。

`ProvisionalBoardId` 在后续被确认为真实身份时，通过既有事实修订链建立关联（第 2.10 节），保留原尝试与原标识，不得原地改写历史。迟到来源改变解析依据时，由 Orchestrator 追加解析修订和回执，并评估防错、追溯与未执行授权的影响；不原地换板号、不自动解除已提交 Hold，已出站对象通过质量异常与追溯链处理。

解析提交须绑定预期身份/聚合版本、观察集合、策略精确引用、裁决原因和权限，采用既有 CAS、幂等键与回执。相同操作同载荷返回原回执，不同载荷复用同键拒绝；并发处置、旧会话结果、错轨道/位置、同码不同实体和身份冻结后更正均要校验，不能按最后写入获胜。重试不增运行尝试，获批返修/再检才关联新的尝试。

身份处理 UI 在同一工作区并列展示本机、上游、MES 和人工来源、差异位置及证据，首屏固定板件位置、工单、真实/临时/冲突状态和阻断原因。主动作按状态为重新读取、核实来源或申请有权限的裁决；高级规则默认折叠。提交前显示绑定对象和影响范围，后台再次验证权限与版本；版本冲突保留输入并要求刷新，不自动重试另一份裁决。历史身份和原始观察只读，界面不能自行选定权威来源。验收覆盖无码留证、临时身份显式显示、合法重检、双轨重号、并发裁决、超时回执查询、断电恢复和迟到身份更正。

#### 3.15.3 程序—板型防错（RecipeMatchVerification）

运行前必须回答“当前装载的配方是否适用于眼前这块板”。该检查与设备能力、标定和资格检查正交：

```text
BoardIdentity（已按身份策略解析的绑定 + IdentityResolutionReceipt）
  + ProductRevision / ProcessRouteRevision 适用性
  + EffectiveRuntimeManifest 的产品与路线绑定
  + 可选：自动板型识别（几何/Mark/特征比对）
  → RecipeMatchVerification：Matched / Mismatched / Unverified
```

- `Mismatched` 必须阻断生产检测，不得降级为警告后继续；
- `Unverified`（无法充分确认配方适用性）按产品策略处理：允许的产品需明确记录未验证项，并在事实、报告与放行证据中可见；不允许的产品直接阻断。获批临时身份不等于未决冲突，身份绑定成功也不自动证明配方匹配；没有合法绑定或存在未决冲突时不能给出 `Matched`，不得借此例外继续正常生产/放行；
- 自动板型识别的结论是**辅助证据**，其可靠性必须单独验证并声明适用域；不得作为唯一身份来源用于高风险产品；
- 操作员的人工确认是一种受权限与审计约束的证据，不能凭勾选消除 `Mismatched`；
- 防错策略引用进入发布配置，实际检查结果进入既有运行绑定/执行证据并引用 `EffectiveRuntimeManifest`，不得反写已签名配置；结果可在复判与审计中回放。

#### 3.15.4 首件与换型门禁

首件检验（FAI）与换型（Changeover）按产品质量计划确定触发条件、适用范围和批准角色；凡要求执行的场景，必须形成可阻断门禁，不能仅保留界面勾选。

| 门禁 | 触发条件 | 必须完成 | 通过前的状态 |
|---|---|---|---|
| `ChangeoverGate` | 产品/配方/轨道配置/钢网/载具变更，或按批准策略的班次/时间触发 | 配方绑定、防错验证、适用能力/标定/点检及上下游配置一致性 | 受影响运行作用域保持 `Blocked`，不产生正常生产放行 |
| `FirstArticleGate` | 换型后首块/首 N 块板，或批准的首件/卷段样本范围 | 按质量计划完成首件检查项、覆盖确认、必要的人工确认与记录 | 首件未关闭前，后续实体/卷段按批准策略排队、隔离或标记待判 |

- 首件结论是独立事实，绑定实际板/载具单元/卷段样本身份、配方版本、清单 hash 与执行人；不得用普通生产判定代替；
- 首件失败必须能追溯到具体不符项，并阻断该配方在受影响作用域的正常放行，直至按批准流程关闭；
- 首件记录精确绑定设备、实际运行作用域、配方、适用标定及质量计划；在线输送绑定轨道，离线/手动装夹/卷料使用第 3.14.1 节获批的工位/载具/卷运行关系，不虚构 Lane。禁止按名称或版本接近自动继承。依赖变化后先阻断旧记录自动沿用，按批准的影响规则决定重做范围；只有具备等效性证据并重新批准的适用绑定可复用证据，不修改原记录；
- 门禁状态必须在生产首屏可见并说明下一动作（第 10.5 节）。

首件门禁未关闭时，可按批准的首件流程执行必要检查并将板保持待处置，不能因禁止正常放行而禁止取得首件证据，也不能将首件模式当成质量豁免。门禁解除由既有运行/质量权限与状态校验完成；重复提交返回原记录，过期配置、轨道变更或旧页面提交必须被拒绝并提示重新核对。

### 3.16 设备状态、OEE、点检、维护与远程服务

#### 3.16.1 设备状态模型

设备活动和停机原因作为带时间的事实记录。参考 SEMI E10 状态分类建立本项目映射，采用版本、区间归属和对外 CFX 映射另行验证，不宣称与其六类状态完全等价或已经符合标准；不新建与既有状态规范竞争的枚举，也不混用 `MachineDecision` 和 `BoardRun` 状态。

| 状态类 | 含义 | 典型原因码 |
|---|---|---|
| 生产中 | 正在执行批准的生产任务 | 正常检测、首件、复判等待中的在线处理 |
| 待机 | 具备生产条件但无任务 | 无板、上游缺料、等待下游、换型准备完成待开工 |
| 工程 | 设备被用于工程/研究用途 | 离线编程验证、算法调试、资格研究（第 2.11 节用途语义） |
| 计划停机 | 事先安排的不可生产时间 | 保养、点检、标定、升级、培训、计划换型 |
| 非计划停机 | 故障或异常导致不可生产 | 卡板、传感器/光源/运动故障、软件异常、断网、磁盘满 |
| 非排产 | 不属于排产时间 | 停线、节假日、无排班 |

设备/轨道和共享资源分别保留状态区间，记录来源时钟、起止、未知缺口与更正引用；重叠和时钟异常不得默认补成正常运行。统计时按获批映射和优先规则聚合，不能把多轨时长相加当作整机时长。状态转换必须带原因码与来源（自动检测或人工登记），并可回放。原因码目录由设备/维护 Owner 维护并与 MES 对齐；**不得**由 UI 自由文本创建新原因。

#### 3.16.2 OEE 与绩效事实

平台只提供构成 OEE 的**事实与定义**，不提供“一个 OEE 数字”作为权威结论：

- 可用率相关：计划时间、各状态时长、停机次数与原因分布；
- 性能相关：实际处理板/Panel/单元数、理论节拍、阻塞与饥饿时长、排队等待；
- 质量相关：必须显式声明分母与口径，并与第 8.3 节的 `MetricDefinition` 一致。**不得**把机判 PASS 比例直接当作质量率，也不得把复判后的结果与首次结果混入同一比率；
- 所有绩效事实绑定 `StationInstance`、适用轨道/工位/卷运行作用域、班次/时间窗与软件/配置版本；无轨道设备不虚构 Lane，卷料计数按批准长度/面积/单元口径，不伪装板数；
- 跨设备与跨站点汇总由质量/制造数据域按批准定义完成，设备侧不自行发布全厂 OEE。

SEMI E10 的设备状态/可靠性口径不等于 OEE 公式；SEMI E58 是自动化 RAM（可靠性、可用性、可维护性）概念、行为与服务规范，也不能当作 OEE 定义。采用 SEMI E79 设备生产率或其它绩效方法时，仍需在 `MetricDefinition` 中固定版本、计划时间、理想节拍、计数对象、质量分母及聚合方法（官方目录定位见附录 C），不能由状态名称直接推导产线绩效。

#### 3.16.3 点检与期间核查

标定有效期内并不代表今天的设备状态正常。点检（日常验证）与期间核查（有效期内的中间核查）是独立门禁：

```text
CheckDefinition（项目、标准件/样件、条件、判据、频次、责任人）
  → CheckExecution（实际执行、原始观测、证据）
  → CheckResult（Pass / Fail / Inconclusive + 原因）
  → 影响：正常生产放行是否允许；是否触发重新标定或维修
```

- 点检项目与判据由计量/设备 Owner 批准，绑定标准件或验证样件的实物编号与证书（第 2.11.4 节）；
- `Fail` 与 `Inconclusive` 必须阻断受影响能力的正常生产使用，并给出恢复路径（复测、重新标定、维修、降范围使用）；
- **操作员不能以勾选恢复能力**。恢复必须由具备权限的角色按批准流程完成并留痕；
- 点检失败前已产生的生产事实不自动作废，但必须进入影响分析（追溯上次成功点检以来的范围），由质量 Owner 形成受控处置（第 14.7.1 节）；
- 点检结果、趋势与到期提醒在诊断工作区可见；到期未执行按批准策略阻断或降级，不允许无限期顺延。

#### 3.16.4 维护、耗材与预测性维护

| 对象 | 内容 | 边界 |
|---|---|---|
| `MaintenancePlan/Task` | 保养项目、周期（时间/计数/里程）、步骤、SOP、备件 | 维护完成不自动恢复资格；受影响能力需按影响范围重验（第 2.11.4 节） |
| `ConsumableState` | 光源累计点亮与衰减、风扇/滤网、标准件磨损、载具寿命、传感器污染 | 消耗品状态是事实与提示，不得自动放宽质量限值 |
| `HealthIndicator` | 温度、风扇转速、驱动/电流、磁盘、内存、GPU、通信误码、重试率、解码质量趋势 | 健康度不是判定；健康良好不代表已标定或具备资格 |
| 预测性维护 | 基于健康与绩效趋势的剩余寿命/异常预警（可用 AI，遵第 7 章边界） | 预警只能生成维护建议与质量事件，不得改变判定、阈值或自动执行设备动作 |

#### 3.16.5 远程服务与诊断通道

国际客户的服务响应能力依赖远程通道，但它同时是最高风险的攻击面与责任面：

- 通道默认**只读**：日志、状态、健康、诊断导出与脱敏证据。写操作（配置变更、升级、参数调整、设备命令）必须单独授权、分级审批、限时有效并全程审计；
- 每次远程会话形成可查询记录：发起人、客户授权凭据、时间窗、访问范围、执行的操作与产生的变更；
- 远程通道不得绕过本地权限、资格与安全边界，也不得成为绕过安全联锁的路径（第 2.12.4、3.12.8 节）；
- 客户可随时撤回授权并断链；断链后系统回到本地权威并保持既有状态，不得因失去远程连接而降级放行或解除阻断；
- 导出数据按第 3.19.5 节进行脱敏、最小化与法域检查；客户合同禁止外发的内容不得通过诊断包离开现场。

### 3.17 跨机一致性与配方可移植性

跨机移植须验证检查意图、执行参数、目标机能力、标定与资格的相容性，并保留设备差异；共享配方不是免验证运行的承诺。

```text
InspectionProgram（检查意图）+ Recipe（执行参数与适用设备上下文）
  + MachineProfile（本机能力）
  + CalibrationArtifact（本机标定）
  + MachineMatchingArtifact（本机相对参考条件的偏差修正与其资格）
  = 本机可执行的运行绑定
```

要求：

- `InspectionProgram` 不保存设备运行参数；`Recipe` 可以包含曝光、光源、分割等设备相关参数，但须绑定 `MachineProfile`、能力、标定和适用域，不能脱离上下文解释或跨机直接套用。跨机派生参数经验证、批准、发布形成新绑定，标定修正仍由标定/匹配 Artifact 拥有（第 3.6、3.12.1 节）；
- 配方移植必须执行适用域校验：目标机的模态、量程、分辨率、FOV、光源配置、运动能力与资格范围必须覆盖配方要求。任一维度不覆盖则该配方在目标机上标记为不可用或部分可用，并列出受影响目标；
- `MachineMatching` 是受控能力：参考条件（可为标准件、参考样板或指定参照机）、匹配方法、残差门限、有效期与资格必须批准；匹配结果是 Artifact，不是可随时手调的偏置；
- 移植后必须完成 `TransferVerification`：在目标机上以约定样件/标准件验证关键量测与判定的一致性，保留差异报告。未通过前不得用于生产；
- **禁止**以现场手动微调阈值来掩盖机台差异。阈值变更走配置生命周期，核对所有引用设备的影响，按批准部署范围与生效边界逐机应用，不能热改全部在途运行（第 3.6、9 章）；
- 机台间差异、匹配残差与漂移趋势应可查询，作为维护与资格复验的输入（第 3.16.4 节）。

### 3.18 环境与工况监测

按具体成像、材料、装夹与设备条件识别影响质量的环境因素。所需监测项、采样方式、校准与质量标记由设备/计量 Owner 批准；不强制每台机安装全部传感器，获批不适用项须有依据。

| 监测项 | 典型影响 | 架构要求 |
|---|---|---|
| 环境温度与温变速率 | 机械热漂、标定失效、材料尺寸变化 | 采样、记录、门限、越界告警与阻断；进入运行输入集合（第 3.6 节） |
| 湿度 | 材料吸湿、静电、表面状态 | 同上；与材料/产品策略关联 |
| 振动与冲击 | 图像模糊、定位重复性下降、3D 噪声 | 事件化记录并关联受影响的采集尝试 |
| 气源/真空压力 | 吸附与夹持不稳、FPC 平面度 | 状态与门限；异常时相关量测有效性下降 |
| 光源状态 | 亮度衰减、色温漂移、老化 | 与消耗品状态、点检联动 |
| 电源与 UPS | 断电与瞬态 | 与恢复策略、RPO 承诺关联（第 9.3 节） |

规则：环境样本是带时间、位置与质量的事实；门限来自批准策略（可按产品与量测族不同）；越界必须能阻断受影响能力的生产使用，或使受影响量测标记为无效/不确定度不满足，而不是仅在日志中留一行。环境记录必须能与具体运行、尝试和量测对齐，供事后影响分析使用；缺少环境证据时不得声称环境条件满足。

### 3.19 数据分级、容量、完整性、归档与报告

#### 3.19.1 数据分级与容量核算

沿用既有生命周期分层 `Raw / Working / Evidence / Fact / Archive`（第 3.10 节）。以下板级公式以在线输送为例；无轨道板机以实际工位/处理通道的板率代替轨道求和，同一实体/采集证据不得跨通道重复计费：

```text
单站日板数 = Σ轨道 ∫日运行窗口 λ_lane(t) dt；λ 的单位为板/秒，时间单位为秒
单板证据字节 = Σ实际保留采集组/FOV (帧数 × 单帧编码后字节 × 保留比例) + 派生证据 + 事实/索引
单站日增量 = Σ产品 (日板数 × 对应证据字节) + 遥测/日志/元数据日增量
在线需求 = Σ各级 (日增量 × 在线天数 × 副本系数) + 在途/staging/WAL/重试积压 + 增长余量
归档需求 = Σ各级 (日增量 × 归档天数 × 副本系数) + 归档索引/校验开销
写入带宽 ≥ 同时峰值板流率 × 单板落盘字节 + 提交/复制放大；读取另覆盖复判/回放/导出并发

```

连续卷料按采集流核算：各级日增量为 `Σ流 ∫运行窗口 实际编码后保留字节率(t) dt`，再加未计入该流的派生证据、事实/索引与遥测；采用原始字节率时必须另计经过批准的编码与保留系数，不得对已保留数据再次乘保留比例。按 LineRate、每行像素/通道/字节、多相/多曝光帧组和实际并发验证输入带宽，落盘取编码后同时峰值；停止走料但继续采集的诊断/标定窗口按其用途另计。板流与卷料混合站点分别核算后汇总，在线/归档容量同样包含副本、staging、WAL、重试积压、回放/导出读取及增长余量，不能因没有“板/秒”漏计持续数据。

每个产品/站点必须冻结各级的保留期、淘汰策略与触发阈值，并声明容量不足时的行为：优先阻断新生产还是优先按策略淘汰可丢弃数据。**必需证据不得按可丢弃缓存处理**（第 9.3 节）。未冻结前保持 `PendingProfile`，不得用宣传值。

#### 3.19.2 证据压缩与保真

- 每类证据必须声明压缩方式（无损/有损/不压缩）与其**批准用途**：可用于显示、可用于复判、可用于再测量，三者分别授权；
- 有损压缩的证据**默认不可用于再测量**。若需用于再测量，压缩参数必须进入不确定度评估并取得相应资格，且在结果中可识别；
- 复判所依据的证据必须满足复判所需的可判读性，其判据由质量 Owner 批准，不由存储成本决定；
- 显示抽稀、降采样与缩略图只是视图，不改变原证据与 hash（第 2.11.4、3.12.11 节）；
- 淘汰与压缩动作必须审计留痕，并使受影响事实的“可回放能力”下降这一状态对查询可见，而不是静默失败。

#### 3.19.3 数据完整性与证据映射

下表是数据完整性要求到架构机制的映射。是否实现、验证并符合客户适用条款，仍须按版本逐项取证，不能以文档映射宣称已经满足法规。

| 数据完整性原则 | 本架构中的实现位置 |
|---|---|
| 可归属（谁做的） | 身份与权限快照、审计、复判 Claim/Decision、处置与授权签发记录 |
| 清晰可读 | Canonical 内容与显示投影分离（第 2.11.4、3.12.11 节）；导出可回读验证 |
| 同步记录 | 事实在其产生边界提交，`OccurredAt/ReceivedAt` 分离（第 8.4 节） |
| 原始性 | 原始观测与派生结果分层保存，原始证据不可被派生结果替代 |
| 准确 | 计量有效性、不确定度、覆盖与资格（第 2.11 节） |
| 完整 | 事实只追加、修订形成链、缺口显式保留（第 2.10 节） |
| 一致 | 版本、水位、评价快照与回执绑定（第 3.10、14.7.1 节） |
| 持久 | 提交、备份、恢复演练与保留策略（第 9.3 节） |
| 可获得 | 查询、回放、导出与归档（第 3.19.4 节） |

电子签名若被客户要求，必须区分“审批签名”（配置、处置、复判）与“内容完整性签名”（hash/签名域），分别满足其法规要求；不得用一种代替另一种。是否满足具体法规仍需客户的计算机化系统验证流程确认，本平台只提供可验证证据与机制。

#### 3.19.4 报告、证书与归档

| 输出类型 | 内容与边界 |
|---|---|
| 生产报告/班报 | 按批准 `MetricDefinition` 与分母口径生成；必须标明数据水位、迟到数据与版本 |
| 批次/工单质量报告 | 绑定质量计划版本、覆盖与证据完整性；缺口必须显示，不得省略 |
| 客户交付证明（如出货检验记录/合格证明类文档） | 只能陈述**已提交事实与已采用标准/类别**，不得宣称超出覆盖范围的结论 |
| 审计导出 | 面向体系审核，含身份、权限、审批、版本与证据引用；须脱敏与最小化 |
| 长期归档 | 按保留期归档事实、必需证据与解释所需的版本信息；归档须包含可独立读取的内容、Schema/格式说明、单位/坐标、版本和校验信息；专有原始格式须保留合法可用的解释器或获批迁移副本与原始摘要。可读导出不等于能重新运行专有算法；须分别验证读取、解释与回放能力 |

报告模板是受控资产，具有版本、审批与适用范围；模板变更不得改变历史报告内容。报告是投影：**不得**在报告生成过程中重新计算判定、重新选择更有利的数据集或改变分母。

#### 3.19.5 数据放置、主权与最小化

- 默认数据落在产生它的站点；跨站与跨境传输必须按合同与法域授权，并可按客户要求限制内容（例如只传结论与统计，不传图像）；
- 每类数据声明：是否含客户商业秘密、是否可离厂、是否需脱敏、保留期与销毁方式；
- 多租户/多站点隔离在身份、存储、查询与导出各层分别生效，不依赖 UI 过滤；
- 诊断包、训练数据与远程会话导出走同一套最小化与脱敏规则（第 3.16.5、7.6 节）。

### 3.20 自动编程、参数整定与配方优化

自动编程以缩短 NPI 和换型时间为目标，输出限定为可核对的草稿、参数建议和差异预览，不能直接成为生产配置或质量事实。SPI 使用焊盘、钢网开口与沉积策略，AOI 使用元件/引脚/焊点策略，不因复用生成流程而混用领域对象。

```text
ManufacturingGeometrySnapshot（已验证）
  + 本任务适用的 BOM / PnP / 领域库 / 历史配方与结果证据
  → ProgramSynthesis（目标生成、分组、方法选择、覆盖规划候选）
  → ParameterProposal（阈值/策略/光源/采样候选 + 依据与影响范围）
  → Draft InspectionProgram / Recipe
  → 既有验证、审批、Release 流程（第 3.6 节）
```

| 能力 | 输入 | 输出 | 硬边界 |
|---|---|---|---|
| 目标自动生成 | 当前输入模式要求的制造几何、BOM/PnP、库或获批教导参考 | 目标集与检查项草稿 | 所依赖快照未 `Ready` 时不生成依赖它的目标；允许保存不完整 Draft，显式列出未解决项，不能生产 Release |
| 库驱动装配 | `PackageLibrary`/`PadLibrary`/`StencilOpeningLibrary` | 按封装/焊盘族的策略草稿 | 库版本固定并进入清单；库缺项必须显式列出，不得用相似项静默替代 |
| 参数建议 | 金板/验证集/历史已提交事实 | 参数候选 + 影响对象数 + 预览差异 | 只写 Draft；必须可预览、可比较、可拒绝（第 7.1、7.3 节） |
| 裕度分析 | 已提交量测分布与规格 | 每个检查项与规格的裕度/风险排序 | 是分析输出，不自动改阈值；分布不足时标为不可用 |
| 批量套用 | 已批准草稿 + 兼容目标集合 | 批量修改草稿 | 必须预览兼容性、差异与跳过原因（第 2.11.7 节） |
| 首件学习 | 首件运行的观测 | 候选修正 | 不得在生产中自调；必须经审批发布后才生效 |

编程输入按“领域 × 任务 × 输入模式”冻结，不把一个领域的常见资料全部设为所有任务的必需输入。模式必须声明目标、必需/可选来源、单位/层面/版本、缺失处理、生成能力和后续验证；没有 BOM、CAD 或钢网资料是否阻断，由该模式的实际依赖决定，不能静默猜测。

| 领域/典型任务 | 常见输入与可批准的模式 | 缺失及输出边界 |
|---|---|---|
| PCB 图形/尺寸检查 | 制造几何/成品要求驱动；或适用的参考板/图像教导模式 | 无名义几何时不能声称完成 CAD 比对或名义偏差验收；教导模式仍需固定参考能力、目标与覆盖 |
| PCBA AOI | BOM/PnP/封装库驱动；或适用的图像教导、人工定义目标 | 无 BOM 不必一律禁止编程，但不能推断料号、替代料或装配完整性；未建立目标的范围明确保留缺口 |
| 3D SPI | 焊盘/CAD、钢网开口与厚度、库，或经验证的焊盘教导模式 | 按采用的面积/高度/体积基准确定必需项；没有钢网资料不能虚构开口、厚度或理论体积，不能自动改用另一分母 |
| 钢网检查 | 钢网设计/实物基准、开口/厚度要求、张力等任务相关输入 | 开口几何、厚度、张力分别需要对应参考和测量能力；光学图像不能补成未测的张力事实 |

格式解析复用 BoardDataAdapter，领域库、历史事实和外部工艺数据通过各自已有版本化、授权接口取得；不在各 ProductProfile 复制解析器，也不要求所有证据走 CAD 适配器。界面按当前任务展示“已取得、必需缺失、可选未提供、冲突”及影响目标，保留导入映射和未完成 Draft；补齐资料后只重算受影响部分，发布时对整个依赖闭包、覆盖与未决项重新校验。验收覆盖无 BOM 的合法教导、SPI 基准缺失、单位/版本冲突、库升级后旧草稿重验及批量生成的局部失败。

本节参数整定指检测配置候选；第 6.2 节经批准的印刷工艺反馈可在其受控范围内调整印刷参数，二者作用对象、授权、限幅和生效边界不同。工艺反馈不得夹带检测阈值变更，也不能以禁止自动改检测阈值为由否定已批准的印刷闭环。

强制禁止：

- **不得**用生产结果自动回调生产阈值。任何阈值变化走第 3.6 节配置生命周期，并保留差异与审批；
- **不得**以“通过率”作为参数优化目标。以通过率为目标的自动整定会系统性放宽检出能力，必须以已验证的召回/误报与裕度为目标，并由第 7.8 节方法验证；
- **不得**把工程用途的整定结果改标志后提交为生产事实（第 2.11 节用途语义）；
- 自动生成/整定的每一项必须可解释其依据（来源、样本、规则），不可解释的建议不得进入批量套用；
- 编程效率指标（编程耗时、人工干预次数、首次通过的目标比例）可作为产品验收维度（附录 B），但不得以牺牲覆盖或裕度换取速度。

## 4. 模块复用与独立性规则

### 4.1 共享模块的准入条件

一个模块只有在下列条件成立时才进入共享平台：

1. 职责边界稳定，至少存在两个真实消费者，或已有明确的产品族复用计划；
2. 输入输出、单位、版本、错误、取消、超时、资源和权限契约明确；
3. 不依赖某个领域的特殊对象、阈值、页面或默认值；
4. 有独立测试、性能预算、Owner、版本和升级策略；
5. 共享失败不会静默改变任何产品的质量事实或设备副作用；
6. 许可证、第三方依赖、部署架构和客户交付边界已核对。

只有一个产品使用、仍频繁变化或包含大量工艺假设的代码，先留在领域包中。待第二个真实消费者出现后，通过契约提取，不做猜测性通用化。

### 4.2 独立性判定必须沿用仓库标准

本文件不另建一套模块拆分标准。仓库级 `DEV-PLT-002` 已冻结五个边界：逻辑能力、程序集/包、流程、开发切片和跨模块集成；并使用八维评分决定保留模块、程序集或真正的消费者能力包。下表是本产品族的四项检查维度，服务于五边界判定，不能替代该标准。

“模块独立”必须同时检查四个维度：

| 维度 | 要求 |
|---|---|
| 代码独立 | 对应逻辑能力有稳定依赖方向、无跨域内部引用；是否拆项目按 `DEV-PLT-002` 评分决定 |
| 契约独立 | 版本化输入输出、兼容策略、禁止隐式字段和字符串绕过 |
| 运行独立 | 明确生命周期、线程安全/线程亲和性、资源租约、取消和故障恢复；使用调用方提供的 Scheduler/ResourceBudget，不为“独立”而自行新增线程或调度器 |
| 发布独立 | 独立产品装配、版本验证、安装包、迁移策略和验收矩阵；不要求所有能力都成为单独进程 |

只拆成 DLL 但共享静态全局状态、数据库表、缓存键、配置文件或隐式 UI 事件，不算真正独立。

### 4.3 复用矩阵基线

| 能力 | 共享平台处理 | 产品/领域扩展 | 禁止方式 |
|---|---|---|---|
| 采集 | 相机/触发/资源/取消/回读 | SPI、钢网、AOI 各自采集计划 | 各产品复制设备线程 |
| 定位 | 坐标、Mark、变换和残差 | 各领域目标和允许误差 | 用最近对象静默替代 |
| 3D | HeightField 容器、有效性、标定引用 | 沉积、钢网、焊点量测定义 | 显示网格直接当生产数值 |
| 量测 | Quantity、单位、有效性、证据 | 体积、开口、焊点等定义 | 共用一个含隐含分支的万能量测 |
| 规则 | 执行器、三值语义、解释框架 | 各领域 RuleSet | 把 AOI 规则改名为 SPI 规则 |
| 复判 | Claim、权限、审计、证据查看 | 各产品缺陷类型和处置流程 | AI 或 UI 直接生成人工 Claim |
| 追溯 | 时间线、快照、hash、回放 | 各领域事实和跨域关联 | 用 latest 覆盖历史依赖 |
| SPC | 分组、分母、统计引擎、报告 | SPI 印刷指标、AOI 缺陷指标 | 混合不同 MeasurementSpec |
| 设备互联 | Envelope、Outbox、回执和安全边界 | 目标设备协议和映射 | 用连接绿灯代替 Applied/Effect |

### 4.4 客户定制、扩展点与产品线隔离

客户定制按下表选择最低必要层级，禁止以长期客户专版分支承载产品差异。常规开发分支、隔离 worktree 与有兼容/回补期限的维护发布分支不属此禁令。所有定制保持原有判定权威和事实语义。

| 层级 | 承载方式 | 可改变的内容 | 审批与升级责任 | 边界 |
|---|---|---|---|---|
| L1 配置 | `ProductProfile`、部署配置、语言与单位、报表模板选择 | 装配范围、显示、阈值实例（经审批） | 现场/产品配置流程 | 不改代码、不改契约 |
| L2 策略资产 | `RuleSet`、`AcceptanceProfile`、`DefectTaxonomy` 映射、`MetricDefinition`、报告模板 | 质量规则、验收、统计口径、报告 | 质量/产品 Owner 审批，版本化 | 不改领域对象与权威 |
| L3 插件 | `PluginManifest` 声明的扩展（算法、适配器、报表、导出、外部系统映射） | 新增能力与集成 | 插件签名、能力与资源预算、兼容范围（第 3.9 节） | 不得直接写领域事实、绕权限或持有未声明资源 |
| L4 定制模块 | 产品内的可选模块，纳入主干代码与主干测试 | 特定客户/行业的工作区或流程 | 产品线 Owner；进入主干发布矩阵 | 必须可被装配关闭；不得破坏其他产品的回归 |
| L5 客户产品分叉 | **禁止作为定制承载** | — | — | 客户专版逻辑须回到 L1～L4；不禁止正常开发和受控维护分支 |

规则：

- 定制必须声明其层级与生命周期。临时用 L3/L4 解决的需求要登记回归计划，避免长期挂账；
- 同一需求出现第二个客户时，评估上提为标准能力（第 4.1 节共享准入条件），而不是复制第二份定制；
- 定制不得改变：事实的语义与不可变性、判定所有权、提交与授权链、审计与安全边界、统计口径的定义方式；
- 定制资产参与版本兼容与升级验证（第 9 章）。客户定制未通过兼容验证时，该客户保持旧版本或 `Blocked`，不得为兼容而降级平台约束；
- 交付物清单必须能列出某客户实际启用的 L1～L4 资产及其版本，供升级影响分析与审计使用。

## 5. 代码、解决方案和目录建议

以下是逻辑架构示意，不是当前仓库的搬迁授权：

未来代码可按稳定边界组织，具体项目数仍须现有治理批准：

```text
src/
  Platform/                  启动、权限、配置、日志、审计、资源、发布
  Vision/                    采集、坐标、定位、3D、标定、图像、计量基础
  Manufacturing/             配方、BoardRun、追溯、复判、SPC、工厂互联
  Ui/                        WPF Shell、Design System、共享控件和服务
  Domains/
    PcbInspection/           PCB 光板领域
    FlexInspection/          软板/FPC 逻辑领域；是否独立程序集按真实边界决定
    RigidFlexInspection/     刚柔结合板组合策略
    HDIInspection/           HDI 层叠、微孔和精细线路逻辑领域
    StencilInspection/       钢网领域
    Spi/                     SPI 领域；SPI 专属实现继续归属 spi/
    AssemblyAoi/             炉前/炉后 AOI 领域
    QualityControl/          跨工序质量视图和分析
  Apps/
    PcbInspection/
    StencilInspection/
    Spi/
    AssemblyAoi/
    QualityControl/
```

本仓库中的 SPI 专属交付目录单独表示为：

```text
spi/
├── docs/                    SPI 需求、架构、模块指导和证据
├── src/                     SPI 专属实现
├── contracts/               经现有契约目录登记的 SPI 专属契约，不复制共享契约
└── tests/                   SPI 专属测试
```

第一幅图的根级 `src/` 是逻辑分层示意，不授权当前新建、移动或重命名根目录项目。现有 AOI 公共模块、根解决方案、共享契约和 Owner 仍由仓库治理接管。第二幅图对应仓库内的 `spi/` 专属目录，SPI 文档、契约、代码和测试继续位于其中；只有经过 `DEV-PLT-002` 独立性评分、真实消费者证明和治理批准，才可把能力提升到既有 Asun 平台的公共路径。平台已有目录和模块注册表是权威来源，不能在 `spi/` 建立平行注册表。

产品入口可以是多个 EXE，也可以是一个带产品装配参数的宿主。优先选择薄入口，按 `ProductProfile` 生成 `PCBInspectionProduct`、`SPIProduct`、`StencilProduct`、`AOIProduct` 和 `QualityControlProduct` 产品包，以减少现场误用；共享平台 DLL 的版本必须可追踪，必要时支持并行安装。逻辑领域边界不等于程序集边界，是否拆分程序集仍由真实消费者、契约、生命周期、测试和发布边界决定。

## 6. 跨工序数据与质量事实

### 6.1 公共身份链

```text
Product / WorkOrder
  → Board / Panel / PanelUnit
  → Station / InspectionDomain
  → RecipeSnapshot + MachineProfile + CalibrationArtifact
  → InspectionAttempt / PrintAttempt
  → AcquisitionSet / HeightField / Evidence
  → MeasurementSet / CoverageResult / InspectionFact
  → RuleEvaluation / InspectionDecision
  → Decisioning / MachineDecision
  → EvidenceCommit / ResultCommitReceipt
  → ReviewClaim / ReviewDecision 及其回执（需要时）
  → RouteAssessment
  → FinalDisposition / DecisionActivationProof
  → DispositionCommitReceipt / RouteAuthorization
  → BoardExitAck
```

所有产品都可以复用身份、版本、证据、回执和审计机制，但每个事实必须携带 `InspectionDomain`、对象类型、来源、版本、hash、时间、水位和有效性。`StationInstance` 是 C-01 负责的实际设备身份；`StationDefinition` 与 `ProductProfile/RouteStep` 的能力和路线装配由 C-08 负责，C-01 不拥有产品装配、路线兼容或能力矩阵。跨工序关联是独立的关联事件，不能修改已提交的原始事实。

### 6.2 SPI 印刷过程控制闭环

SPI 的检测事实必须保留印刷过程上下文，不能只保存某个焊盘的测量值。`PrintProcessContext` 关联产品版本、钢网版本、印刷机实例、印刷配方、锡膏批次、印刷面、板/Panel/Unit、环境与适用的工艺参数快照；`PrintAttempt` 表示一次真实印刷尝试，并与统一的 `InspectionAttempt`、设备实例和路线步骤关联。一次重印、返工或复检必须生成新的尝试身份，历史尝试不可覆盖。

SPI 过程闭环按以下顺序运行：

```text
PrintProcessContext
  → PrintAttempt
  → PrintMeasurement / PrintDefect
  → InspectionDecision / Decisioning / MachineDecision
  → ResultCommitReceipt
  → ProcessFeedbackProposal
  → 授权后的 FeedbackCommand
  → FeedbackReceipt
  → EffectObservation
```

`PrintMeasurement` 只承载有来源、有计量质量和有效性标识的高度、面积、体积、偏移等测量；`PrintDefect` 承载基于领域规则的缺陷事实，不能由 AI 候选直接充当。`ProcessFeedbackProposal` 是对已提交事实的建议，必须包含依据、`FeedbackScope`、预期效果、有效期、回退目标和风险。`FeedbackScope` 至少区分 `CurrentBoard`、`CurrentPanel`、`NextBoard`、`RemainingLot`、`PrinterRecipe` 和 `MachineDefault`；只有经过权限、版本、能力和工艺策略检查后，才能形成设备可执行的 `FeedbackCommand`。`FeedbackCommand` 必须明确 `ParameterScope`（Printer、Recipe、Board、Panel、PrintAttempt 或 Station）、`ChangeScope`、持续时间、失效时间、回退目标和审批范围，防止单板偏移建议被错误应用为整机永久配方修改。设备适配器负责协议执行及原始 ACK/参数回读；反馈应用服务核对命令身份、版本、作用范围和回读结果，再通过既有提交边界形成 `FeedbackReceipt`，质量与过程分析负责比较前后事实并形成 `EffectObservation`。反馈发送成功不等于设备已应用，也不等于过程已经改善。

这条链由 `C-01` 管理尝试身份，`C-02` 管理印刷机/钢网/锡膏配方和运行清单，`C-03` 管理参考、变形、量测、准确度、重复性、GR&R 和计量资格，`C-04` 管理测量到判定、提交及反馈回执，`C-06` 管理印刷机协议、CFX/Hermes 和设备安全，`C-07` 管理 SPI 节拍、资源、故障恢复和长稳，并消费 C-03 的计量资格，`C-08` 管理产品装配、路线及跨站交换。不得为 SPI 反馈建立第二套提交机制，也不得由质量中心、AI 或 UI 直接写设备参数。

### 6.3 事实、建议和视图分离

```text
设备/算法事实 → 权威提交 → 质量查询与统计
                         ↘ AI候选/解释/建议
                          ↘ 人工复判 Claim/Decision
                           ↘ 受控处置和设备反馈
```

- 视图只投影权威事实，不拥有事实写入权；
- AI 候选不能直接成为 `MachineDecision`、`ReviewClaim`、`RouteAuthorization` 或设备 Applied；
- 统计必须绑定快照、分母、排除原因和水位；
- 回放和候选使用隔离命名空间，不写生产 `MeasurementSet/InspectionFact`、SPC、Outbox 或出板回执；
- 历史事实不可被新配方、最新算法或当前标定静默覆盖。

### 6.4 返修、再检与处置闭环

返修必须关联来源缺陷、已提交处置、实际动作、物料谱系与再验证。返修动作完成、复判通过和新检测合格是不同事实，任何环节都不能把原 NG 原地改为 OK。

```text
已提交事实 + MachineDecision(+ ReviewDecision)
  → Orchestrator 形成 FinalDisposition（获批返修/重工语义，非新增枚举）
  → DataService 处置提交/授权 → MotionGateway 执行并确认（有搬送时）
  → ReworkOrder（范围、依据、目标缺陷项、优先级、授权）
  → RepairAction[]（实际动作、人员、工位、物料、时间、SOP 版本）
  → ReworkVerification（再检或复核：新的 InspectionAttempt 或受控人工验证）
  → 检测路径：新事实/权威机判/结果回执；人工路径：获批验证记录与提交回执
  → 路线重新评价 → 新操作边界内的处置提交/授权/实体确认（第 2.10 节）
```

| 对象 | 必须固定 | 禁止 |
|---|---|---|
| `ReworkOrder` | 来源事实与机判的精确引用、返修范围（板/单元/目标）、授权与优先级、有效期 | 不得凭口头或列表勾选建立；不得覆盖来源事实 |
| `RepairAction` | 动作类型（补焊、更换、清洗、重印、重贴等）、执行人、工位、SOP/程序版本、更换物料的批次与来源、开始与结束时间 | 不得省略物料追溯；更换元件必须能回答“换成了什么” |
| `ReworkVerification` | 验证方式（再检 `ReinspectAttempt` / 受控人工验证）、范围、结果、证据 | 未验证不得放行；人工验证不得改写原量测 |
| 处置结果 | 新的处置事实与回执；与原处置的因果关系 | 不得删除或改写原 NG 事实 |

返修同时维护缺陷修复链和物料更换链，通过同一个 `RepairAction` 精确关联，不把“缺陷已关闭”当成物料谱系完整的证明：

| 追溯链 | 必须可回放的关系 | 边界 |
|---|---|---|
| 缺陷修复 | 原板/单元/目标及缺陷事实 → 获批 ReworkOrder → 实际 RepairAction → 再检或人工验证 → 路线/处置回执 | 动作完成不等于验证通过；保留原 NG、未覆盖项和每次尝试 |
| 物料更换 | 所属实体/位置 → 拆除事件及旧物料 → 安装事件及新物料 → 批次/序列号/来源 → 对应验证 | RefDes/位置不是实物 ComponentInstance；有序列号用实例级，无序列号按批次与装卸事件追溯并显示粒度 |

实体关系复用现有谱系，Panel、PanelUnit 与分离后 Board 按真实制造/分板事件关联；不强制所有产品采用同一种父子链。补焊、清洗、重印等无元件更换的动作可对元件链声明有理由的 `NotApplicable`，但仍记录该动作实际消耗的适用物料。旧料批次未知时明确保留缺口及处理责任，不编造实例或批次；是否允许后续放行由质量计划决定，不能用必填占位值绕过。

返修 UI 以缺陷/目标为入口，联动来源图像、动作、旧/新物料与验证状态。更换操作扫描新料并核对适用料号/替代料和批次，提交前显示变更位置与影响范围；权限和版本在后台复核。按同一动作幂等提交，防止重复扫码或重试生成两次更换。完成动作后继续显示“待验证”，未闭合的缺陷和物料缺口保持可见；记录修订追加新版本，不删除旧更换关系。验收覆盖同位号多次更换、无序列号、旧料未知、无更换返修、部分再检及断电后续作。

统计与追溯规则：

- 返修后的合格结果**不进入首次通过率分子**（沿用第 8.3 节），同时必须能计算返修率、重工率与滚动合格率类指标，口径由 `MetricDefinition` 定义；
- 同一块板的多次返修形成序列，必须可区分第 1 次与第 N 次，并保留每次的缺陷项与动作；
- 更换元件后，原元件的追溯链不得丢失：被换下的元件、位置与批次关系要可查询（供召回与失效分析）；
- 返修工位若具备检测能力，其结果同样遵守完整的事实/判定/提交链，不允许“工位内自判自过”；
- 未被获准再检/验证范围覆盖的原缺陷项继续保留其约束（第 2.10 节）；整板重检只有逐项满足适用的覆盖、方法与替代规则才可形成当前评价，原 NG 历史始终保留。

### 6.5 跨工序归因与过程相关性的受控形式

本项目默认采用下列受控归因路径。其他经批准的研究方法也须保留配对规则、样本、混杂因素、统计方法、置信区间和适用范围；归因研究不拥有生产判定或设备命令权。

```text
已提交事实（多工位、多方法、带版本与水位）
  → PairingRule（按批准映射建立可比较的对象对）
  → CorrelationAnalysis（统计关联 + 混杂因素 + 样本量与置信区间）
  → AttributionHypothesis（假设：某类缺陷更可能来自某工序/某因素）
  → 质量事件 / 验证性试验 / 工艺改进提案（受控）
  → EffectObservation（第 6.2 节）→ 结论的确认或否定
```

强制约束：

- **配对必须按批准映射**。例如 SPI 的 `DepositTarget` 与炉后 `SolderJoint` 的对应关系必须来自制造参考与领域映射（第 2.8 节），不得仅按坐标就近自动配对；跨面、跨层或跨版本仅在存在获批制造谱系、坐标映射、版本等效范围及歧义检查时可进行，缺失映射必须拒绝，不能禁止本来就需要跨层研究的合法关系；
- 分析必须声明：数据来源与水位、时间窗与批次范围、纳入与排除规则、样本量、统计方法、置信区间与多重比较处理、已识别的混杂因素（钢网清洗周期、锡膏批次与寿命、贴片机吸嘴、炉温曲线、板材批次、环境、操作班次）；
- 输出**不得**是判定。归因结论不能改变任何已提交事实、机判、复判或放行，只能形成受控质量事件与改进提案（第 8.3 节）；
- 归因用于调整参数或规则时，必须走第 3.6 节配置生命周期与第 6.2 节反馈闭环，并以 `EffectObservation` 验证；
- AI 参与归因时遵守第 7 章边界，其输出为候选与解释，仍需质量人员批准（第 7.1 节）；
- 相关性分析的结论具有有效期与适用范围，条件变化（新产品、新工艺、新设备）后需重新验证，不得长期沿用。

### 6.6 抽样检验与批次接收

第 2.11.3 节已定义特征选择、特征内采样与板/批次抽检三个独立维度。本节补齐**批次接收规则**的依据与边界，避免把抽样结论误当全检结论。

- 抽样方案（计数型/计量型、检验水平、AQL 或等效判据、加严/放宽/暂停转移规则）属于 `QualityPlanRevision` 的内容，依据来源见第 2.12.2 节，必须由客户或质量计划采用；
- 抽样接收的结论作用于**批次**，不作用于未检单元。未检单元在事实与报告中保持“未检”，不得因批次接收而标为 PASS（第 2.6、2.7 节）；
- 抽样计划、实际抽取、抽取依据（随机/系统/分层）、替换与补抽规则必须可回放；样本不足或抽取失败时结论为不确定，不得降低样本量后重新宣布接收；
- 抽样与全检在同一产品不同阶段并存时，分母与口径分别定义，不得混算（第 8.3 节）；
- 抽样发现的不合格必须按批准策略触发扩大检验或遏制，不能只记录一条 NG 了事。

## 7. AI 与 AI 辅助复判架构

### 7.1 AI 的适用位置

AI 不是替代所有确定性算法的总开关，而是按输入域和风险使用：

| AI 能力 | 可服务的领域 | 权威结果仍由谁负责 |
|---|---|---|
| 图像质量评估 | PCB、钢网、SPI、AOI | 采集/质量门禁决定是否可用 |
| 缺陷候选检测/分割 | PCB、钢网、SPI、AOI | 领域算法、量测和规则 |
| 候选排序与相似案例检索 | 所有复判工作区 | 授权复判员和 Review 服务 |
| 量测异常/漂移提示 | SPI、钢网、AOI | 计量资格、SPC 和工艺 Owner |
| 参数建议 | 编程、参考、分割、规则 | Draft、验证和审批服务 |
| 跨工序关联分析 | QualityControl | 质量人员解释和批准的统计结论 |

对于 SPI，AI 可以提出锡膏分割候选、疑似桥连/偏移区域、异常印刷尝试或复判优先级；体积、面积、高度、偏移等生产量测仍必须由可解释的 `MeasurementDefinition` 和有资格的计量链产生。对于 AOI，AI 可以提出元件/焊点缺陷候选；不能把 AOI AI 输出直接当成 SPI 沉积量测。

### 7.2 AI 运行契约

每次推理必须记录：

- 模型 ID、模型版本、模型文件 hash、推理引擎和后端；
- 输入证据引用、输入 hash、裁剪/归一化/坐标变换版本；
- 训练数据集快照或数据来源、标签版本和适用领域；
- 输出类别、候选区域、数值、置信度、拒绝原因和解释证据；
- 推理耗时、资源、设备、温度/驱动等必要运行上下文；
- 模型漂移、低置信、多候选、超时、断线和确定性回退状态；
- 是否为生产事实、工程候选、影子结果或复判建议。

AI 服务离线、模型不兼容、输入无效或资源不足时，按产品策略进入确定性回退或 `Unknown/Blocked`。不能用零置信度、默认类别、最近候选或上一板结果伪造结果。

### 7.3 AI 辅助复判闭环

```text
已提交检测事实
  → 生成 ReviewCase
  → 按权限领取 ReviewClaim
  → AI 读取固定证据快照
  → 生成 CandidateReviewSuggestion
  → 显示原机判/量测/2D/3D/剖面/AI依据和差异
  → 复判员确认、修改或拒绝建议
  → ReviewDecision 及其提交回执
  → RouteAssessment
  → Orchestrator FinalDisposition / DecisionActivationProof
  → DataService DispositionCommitReceipt / RouteAuthorization
  → 保存 AI 与人工审计
```

AI 的“复判”在产品中应命名为 **AI 辅助复判**，避免让操作员误以为系统已经完成具有人工责任的复判。AI 可以先做候选筛选、相似案例推荐和证据定位；只有真实 `ResultCommitReceipt` 后，授权人员才能领取生产 `ReviewClaim`。人工意见不覆盖原机判，二者并存并可追溯。

AI 逐步上线采用：

```text
离线评估 → Replay候选 → Shadow影子运行 → Advice建议 → 受控Automatic
```

每一级都要有适用数据、误报/漏报、拒识率、延迟、资源、解释、回退和权限证据。`Automatic` 不能只凭模型准确率启用，还要经过计量/质量/安全/生产 Owner 批准以及目标设备和客户验收。

### 7.4 AI 训练和反馈边界

- 生产事实、人工复判、候选结果和训练样本必须分层存储并带来源；
- 人工确认的标签不能自动视为绝对真值，需记录标注来源、复核和冲突；
- 模型训练不能在生产 UI 线程或生产设备进程中运行；
- 训练、验证、发布、回滚和灰度必须有模型注册表及审批；
- 数据脱敏、保留期限、客户授权和许可证必须先于外部训练服务；
- 合成数据、单次演示、公开数据集和局部截图不能作为客户生产资格证据；
- 模型升级使适用性改变时，生成新版本和重新验证，不能重写历史预测或历史量测。

### 7.5 AI 治理、模型档案与法规义务

AI 模型的用途、数据权利、统计验证、风险和运行限制必须形成可审查档案；治理要求与第 7.1～7.4 节的生产权限边界共同生效。

`ModelRecord`（模型档案）是既有模型注册表的必填内容，不是新建资产。每个进入 Shadow 及以上阶段的模型必须具备：

| 档案项 | 内容 |
|---|---|
| 身份与版本 | 模型 ID、版本、文件 hash、训练代码/配置版本、推理引擎与后端版本 |
| 预期用途 | 适用领域、工序、板型、材料/表面、缺陷族、**明确的不适用范围** |
| 数据 | 训练/验证/测试数据集快照、来源与授权、标签规范与版本、类别分布与已知偏斜 |
| 性能 | 按第 7.8 节方法得到的召回/误报/拒识、分层最差结果、置信区间、评估集版本 |
| 限制与失效 | 已知失效模式、分布外表现、退化征兆、拒识策略 |
| 运行约束 | 输入预处理与坐标变换版本、资源与延迟预算、确定性回退 |
| 责任 | 模型 Owner、批准人、批准范围与有效期、撤销条件 |
| 变更 | 与上一版本的差异、回归结果、迁移与回滚方案 |

治理要求：

- **人类监督可执行**。AI 阶段越高，监督手段必须越具体：Advice 阶段有拒绝与理由记录，受控 Automatic 阶段有抽检率、停用开关、异常升级路径与责任人；
- **用途分级与法规义务**由合规 Owner 按市场核定（依据见第 2.12.2 节）。分级结论进入产品交付清单，不得以“这只是辅助工具”自我豁免；
- **可追溯性**：任何 AI 参与的输出在证据链中必须可识别其模型身份与阶段（候选/影子/建议/受控自动），供复判、审计与事后分析使用（第 7.2 节）；
- **风险管理**：模型引入、升级、数据源变更与适用范围扩展都要做风险评估并留痕；风险不可接受时保持在低阶段运行；
- **AI 管理体系对接**：若客户或市场要求 AI 管理体系认证，本平台提供的是可引用的档案、评估与监控证据，不代表已认证（第 2.12.3 节）；
- 模型撤销或到期后，受影响能力立即不可用于生产；历史预测保持不可变，不得重写（第 7.4 节）。

### 7.6 数据闭环、标注治理与再训练触发

数据闭环连接生产证据、标注、数据集、训练和独立评估。它服务于模型改进，不能把人工标签或反复调参后的成绩当作独立质量验证。

```text
生产证据（已提交事实 + 证据快照）
  → 采样策略（随机 + 难例 + 复判不一致 + 低置信 + 漂移触发）
  → 脱敏与授权检查（第 3.19.5 节）
  → 标注任务（规范、标注者、复核、仲裁）
  → DatasetSnapshot（版本、来源、分布、许可）
  → 训练/评估（隔离环境）
  → 回归基准集评估（第 7.8 节）
  → 模型档案更新 → 灰度阶段推进（第 7.3 节）
```

约束：

- **标签不是真值**。人工复判结论、金板标注与仲裁结论都必须保留来源、复核状态与冲突记录；标注规范本身有版本，标签随规范版本解释（第 7.4 节）；
- 采样必须能说明**代表性**：仅采难例会使评估乐观或悲观，必须与随机样本分层组合，并记录采样比例；
- 训练与生产隔离：训练不得在生产设备进程或生产 UI 线程中运行；训练数据出厂需客户授权与脱敏（第 3.19.5 节）；
- **回归基准集是受控资产**：已发布快照不可原地修改；纠错、去重、撤回授权和样本退出通过新版本、差异及必要的受控处置实现，不要求永久只增不减。按板/拼板/批次/产品谱系与时间分组隔离训练、调参和测试集，同一来源裁剪、增强、重复检测不得跨集合泄漏。最终验收集独立封存；已用于调参的集不能继续冒充独立验收集。换版按共同样本与新分层重评，确因授权限制无法重算须声明可比性限制；
- 再训练触发条件须预先定义（新产品/新封装、漂移指标越界、复判不一致率上升、逃逸案例、召回率下降），触发只启动流程，**不自动发布模型**；
- 客户数据的使用范围（仅本站/仅本客户/可聚合）由合同确定；跨客户聚合训练必须有明确授权，默认不允许。

### 7.7 冷启动、少样本与无监督异常检测

新产品首件可能缺少代表性的缺陷样本。NPI 应提供确定性规则、设计参考和经验证的计量路径，AI 候选方法按数据条件选择；SPI 的高度、面积、体积等计量不能由异常分数替代。

| 场景 | 可用方法（作为候选能力） | 边界 |
|---|---|---|
| 无缺陷样本的首件 | 基于设计参考/金板的确定性比对；无监督或单类异常检测提供候选 | 异常候选不是缺陷事实；必须经领域规则与人工确认 |
| 少样本新封装/新缺陷 | 库迁移、相似封装策略复用、少样本学习候选 | 相似不是等同；适用域必须显式，不得自动跨材料/表面复用 |
| 罕见缺陷 | 缺陷注入与合成数据用于**训练与压力测试** | 合成数据不能作为客户生产资格证据（第 7.4 节） |
| 冷启动期的阈值 | 基于确定性计量分布与规格裕度的保守初值 | 初值必须经审批发布；不得在生产中自调（第 3.20 节） |

无监督/单类方法的额外要求：正常样本集必须是受控资产（来源、数量、覆盖的变异范围）；异常分数、阈值与拒识策略需与人工工作量一起评估。新材料或表面分布变化可能引起系统性误报，也可能使真实缺陷未被识别；必须在适用域中声明已知限制并在换料时重新评估，不能把异常检测解释为必然能发现所有未见缺陷。

### 7.8 检测与 AI 性能的统计验证方法

属性判定与连续量测分别验证。召回、误报、拒识和逃逸必须明确机会单位、参考结论、采样方法与不确定性，不能用总体百分比代替分层能力证明。

#### 7.8.1 参考真值、仲裁与验证集

`GroundTruthRecord` 表示受控参考结论，复用现有标注、`DatasetSnapshot`、计量参考和质量验证资产，不另建会改写生产事实的“真值服务”。人工 Annotation、已提交 `ReviewDecision`、客户逃逸反馈是可能的来源，均不因名称、签字或进入数据库就自动成为参考真值。

| 要素 | 必须固定 | 不可推断 |
|---|---|---|
| 对象与问题 | 原始证据/样本精确引用、板/目标/位置、缺陷族或被测量、机会单位、工序/时间及有效范围 | 同一板的另一目标或后续工序结论不能直接替代本工位参考 |
| 参考方法与能力 | 方法/设备/标准件、标定/资格与观察条件、可观察范围；连续量的单位/不确定度，类别结论的可信依据 | CT/X-ray、显微或专家均非通用更高真值；只在已验证的目标缺陷/尺度范围使用 |
| 结论与分歧 | 参考类别/量值、未知项、原始标注、判定者、复核/仲裁依据与结果 | 多人一致不等于正确；不得强迫证据不足的样本归入 PASS/NG |
| 版本与许可 | 来源、采集与标注版本、批准人、使用授权/保留范围、修订/撤销及依赖数据集 | 新参考不能覆盖旧标注、改写原机判或追溯报告；受限客户数据不能自动进入训练集 |

参考建立先冻结问题和验证计划，再选具有对应观察能力的方法，必要时做独立复核或受控仲裁。用于正式评价的参考判定应按计划与被评算法输出隔离，记录盲法及其例外；若参考方法也有失误，须说明局限并采用不确定参考的分析/排除规则。无法确证的样本单独报告数量、特征和原因，不静默丢弃或当作阴性；过滤规则在评价前冻结，报告其对适用范围的影响。

金板可证明已验证的正常范围，不能单独证明所有缺陷的真值。植入缺陷、合成图像和仿真可用于受限工程验证与边界挑战，必须保留来源标识；其指标外推到现场真实缺陷前，须取得代表性和方法等效性证据。客户反馈只证明被发现的事件，尚需区分原工位漏检、下游新生缺陷与原因未明，不能把未投诉件全部作为真阴性。

验证集按产品/工艺、缺陷族、尺度、材料/表面和边界样本建立版本化分层；同一受控母集可以派生不同指标的明确子集，但训练、调参和最终独立测试按板/批次/来源谱系隔离，重复采集与增强样本不得跨分区泄漏。每个研究固定数据快照、纳入/排除规则、参考版本、算法/阈值、指标与独立单位。纠错、授权撤销或参考失效通过新修订/新快照及受影响研究重验处理，历史结果保留原依据并标示不再适用的范围；保留与删除仍服从第 3.19、7.6 节，不以冻结测试集为由拒绝合法纠错或撤权。

复核工作区并列呈现原始图像/量测、各来源结论、分歧及参考依据，按评估计划控制何时显示被评模型结果。只有具备权限的批准流程能发布参考修订；界面展示当前研究采用版本和影响研究列表，不允许一个“采纳 AI”按钮建立真值。验收包括复判改判、参考不确定、错误层面/目标、标准件失效、客户授权撤销、同板重复泄漏、零阳性样本、未知参考及修订后历史回放。

#### 7.8.2 属性型测量系统分析

- 对 PASS/NG 这类属性判定，必须做属性一致性分析：同一批带已知真值（或专家仲裁结论）的样本，由多名复判员/多次运行重复判定，计算判定者内一致性、判定者间一致性与相对参考结论的一致性；同时报告混淆矩阵、分类别一致率和参考不确定性。Kappa 可作补充，但受类别流行率与判定偏倚影响，不能单独作为准确率或召回证明；
- 样本集必须包含**边界样本**（接近判定边界的可接受与不可接受件），否则一致性会被系统性高估；
- 设备判定与人工判定分别评估：机器重复性（同板多次检测的判定一致性）与人机一致性是两个指标；
- 结论有适用范围：某产品族/某缺陷族的一致性不能外推到其他族。

#### 7.8.3 召回、误报与逃逸的估计

| 指标 | 定义要点 | 必须同时报告 |
|---|---|---|
| 召回（检出率） | 在**已知缺陷集合**上的检出比例 | 缺陷集合的来源、构成与代表性；分缺陷族与分尺度的最差值 |
| 误报 | 按获批指标分别记录 FP/(FP+TN)、报警中的误报占比 FP/(TP+FP)、每板误报数；三者不得混称 | 分母、机会单位、参考结论可靠性、统计期与抽样权重 |
| 逃逸 | 对本工位放行集合进行独立验证或下游追踪所得的不合格数量/比例 | 可追踪分母、验证覆盖、下游方法局限、迟到/删失、观察窗口；不完整反馈只能称已观察逃逸 |
| 拒识/不确定率 | 模型或规则主动放弃判定的比例 | 其对人工工作量与节拍的影响 |

要求：

- 用于能力推断/验收的比率必须报告置信水平、区间方法、样本量和独立单位；全量事实描述仍声明总体、口径和窗口，不强套抽样区间。无阳性参考样本时召回不可估计；有 n 个独立阳性样本且零漏检时，可报告观测召回 100%，但必须给出小于 100% 的置信下限。漏检/逃逸零事件时按明确试验分母给单侧上限，不能写零风险；
- 分层报告优先于总体平均：按缺陷族、尺寸、封装、材料/表面、位置（中心/边缘）分层，报告最差层（第 14.9 节）；
- 漏检研究须用独立参考验证并说明参考能力，不能用本机结果自证。客户投诉或下游发现不构成完整真值；须区分本工位原有未检出缺陷、下游新生缺陷与原因未知，验证覆盖不足时不外推总体逃逸率；
- 同板多目标、拼板单元、同批次和重复运行通常相关；统计计划须按板/批次聚类或使用适当的分层模型、区间方法及有效样本量，不能把数十万相关 Pad 当作独立试验。先冻结目标风险、样本设计和盲法参考，再评估独立集；
- 缺陷集合与挑战集是受控资产（第 7.6 节），其构成变化会改变指标含义，必须版本化并保持可比；
- 误报统计以复判结论为依据时，必须按第 7.8.1 节核实参考能力，并按第 7.8.2 节评估一致性；一致不等于正确，未验证的复判标签不能证明误报率；
- 上述指标进入产品验收维度（第 14.9 节），未取得前保持 `PendingProfile`，不得使用宣传值。

## 8. UI 产品化架构

### 8.1 共享 UI 与专业 UI

所有产品客户端统一采用 WPF + DevExpress。共享 Design System 和 WPF/DevExpress 控件：

- 主题、字体、间距、图标、颜色语义和状态视觉；
- Shell、导航、Ribbon/Bars、Dock、Grid、Layout、对话框和通知；
- 2D/3D 视口、证据面板、表格、曲线和导出控件；
- UIA AutomationId、键盘焦点、三语、DPI 和多分辨率行为。

专业产品分别拥有：

- 产品导航和菜单；
- 对象列表、参数分组、编程向导和检测流程；
- 缺陷、量测、复判、工艺和处置术语；
- 生产页面首屏字段、最短安全路径和下一动作；
- 专业帮助、异常恢复和权限提示。

不能把 SPI、钢网和 AOI 参数放入同一个“万能参数页”，也不能让一个“缺陷列表”同时解释线路缺口、锡膏体积和焊点少锡。

板型差异必须在专业页面中体现为任务上下文，而不是堆叠成一个万能页面：PCB/HDI 页面提供层号、设计对比和层间偏移；FPC 页面提供载具、张力、局部形变和卷段定位；SPI 页面提供焊盘、沉积和参考面；AOI 页面提供元件、引脚和焊点。共享的是视口、证据、表格、状态和恢复控件，页面的对象、参数、主命令和验收路径由产品领域决定。

### 8.2 产品页面边界

| 页面类型 | 共享框架 | 专业内容 |
|---|---|---|
| Shell | 导航、用户、全局状态、能力提示 | 产品名称、工作区和领域术语 |
| 生产工作区 | 状态、证据、命令、回执、八态 | 当前产品的对象、阶段、规则和下一动作 |
| 编程工作区 | 向导、差异、草稿、版本、审批 | PCB/钢网/SPI/AOI 各自模型和参数 |
| PCB 计量任务工作区 | 复用编程/结果复核/计量诊断、视口/表格/曲线联动 | 第 2.11.7 节的层面/基准/名义与成品要求、采样/最差点、U/质量/评价、原始与排除样本；保持角色与发布权限 |
| 复判工作区 | Claim、证据、意见、处置、审计 | 各领域缺陷与量测显示 |
| 分析工作区 | 快照、筛选、分母、趋势、钻取 | SPI 印刷过程、AOI 装配、PCB 缺陷与尺寸统计；PCB 计量样本层级按第 2.11.6 节区分 |
| 诊断工作区 | 能力、租约、标定、维护、SOP | 设备、光学、运动和产品专属资格 |
| 质量管控工作区 | 统一时间线、权限和报告 | 跨工序关联和质量改进任务 |

所有适用页面都必须覆盖 `Ready`、`Busy`、`Empty`、`Stale`、`Blocked`、`RecoverableError`、`PermissionDenied` 和 `Completed`，并说明状态、影响和下一安全动作。真实 WPF、UIA、100/125/150% DPI、最小分辨率和 `zh-CN/zh-TW/en-US` 必须在产品级分别验收。

板流、维护、移植和返修能力进入既有工作区，不为每个架构对象新建窗口。C-05 的 Page Contract 按以下任务映射冻结布局、命令与恢复；控件和具体尺寸仍由批准的 WPF 页面契约确定：

| 任务与主要角色 | 工作区与首屏布局 | 操作链与提交边界 | 失败与便利性要求 |
|---|---|---|---|
| 操作员：板流与身份防错 | 生产页顶部固定产品/配方/当前轨道；中央图像；轨道位置和门禁与板身份同时可见 | 接收观测 → 自动匹配 → 有冲突时核对来源证据 → 重新校验 → 进入获准运行 | 切轨不改变处理对象；待提交命令锁定原运行和版本；位置未知时只能进入获准恢复，不能点“继续”出板 |
| 工艺/质量：换型与首件 | 生产页门禁摘要，详情在换型任务面板；按未完成项排序 | 选择已发布配置 → 预检 → 首件执行 → 逐项核对 → 有权限者提交结论 | 自动带入版本与证据；只要求人工处理缺口；失败项一步定位，关窗或重开不等于门禁通过 |
| 编程/计量：自动编程与跨机移植 | 编程页左侧目标/设备，中央图像或差异，右侧分组参数与适用性 | 选择参考/目标机 → 生成 Draft → 预览差异/覆盖 → 验证 → 原审批发布链 | 标记跳过和不兼容项；批量操作预览影响范围；撤销只作用草稿，不热改生产配方 |
| 维护/计量：点检与环境恢复 | 诊断页按受影响能力分组；显示当前值、时效、门限、趋势及依据 | 打开失败检查项 → 按 SOP 执行 → 保存观测 → 权限校验后恢复适用范围 | 过期遥测显为 Stale；计划、执行和恢复分开，不能以确认报警代替重新核查 |
| 复判/返修人员：缺陷与物料闭环 | 队列、证据视口、动作记录分区；原缺陷/当前验证状态并列 | Claim → 判读/记录动作与物料 → 提交 → 再验证 → 路线处置 | 扫码和键盘可完成常用路径；Claim 过期或证据缺失禁止提交；返修动作与质量放行采用不同命令 |
| 质量工程师：关联、抽样与报告 | 分析页筛选及数据水位固定；关联视图与可钻取明细联动 | 选批准规则 → 核对样本/缺口 → 分析/预览 → 提交改进提案或受控导出 | 样本不足显示原因；重算与历史报告分开；报告不能隐藏缺口或重新选择更有利分母 |

以上页面共用八态、键盘/UIA、DPI 与语言验证；提交前复核权限、对象身份、期望版本和证据时效。每项任务测量关键步骤/按键数、完成时间、误操作恢复及并发切换表现，目标由相应 Profile 冻结，不以增加弹窗或装饰效果替代可用性。

### 8.3 全流程质量体系的业务边界

质量管控产品不是把各设备页面拼在一起，而是围绕“质量计划 → 检测事实 → 异常识别 → 遏制/处置 → 根因与改进 → 效果确认 → 放行”建立跨工序视图。它必须能够回答每个产品、工单、批次、Panel、Unit 和检测尝试的来源、状态、证据、责任人和下一安全动作。

| 能力 | 质量管控产品负责 | 设备产品负责 | 关键约束 |
|---|---|---|---|
| 质量计划 | CTQ、检测覆盖、抽检策略、分母和版本 | 执行本设备的已发布计划 | 计划发布前不可改变在途 BoardRun |
| 追溯与谱系 | Product→Lot→Panel→Unit→Attempt→Fact 的查询和关联 | 产生本工序真实 Attempt、Evidence、MeasurementSet/InspectionFact | 支持拆分、合并、返工、重印、重检和多次尝试；历史不可覆盖 |
| 异常与遏制 | 跨批次聚合、风险分级、Hold 建议、受控质量事件 | 本机安全暂停、复测和本地恢复 | 质量 Hold 与设备 RunControl 分开；中央系统不能绕过设备安全边界 |
| 不合格与 CAPA | NCR、Containment、Correction、RootCause、CAPA、Effectiveness | 提供事实和执行结果 | 每个结论绑定证据、责任人、时限和审批 |
| 工艺改进 | 关联分析、SPC、趋势、改进提案和效果评估 | 接收批准后的新配方/规则并生成新版本事实 | 相关性线索不能直接宣称因果或改写 PASS |
| 放行与交接 | 聚合已提交事实，提出质量视图 | 遵守本机判定、复判、处置和出板回执 | `RouteAuthorization` 和 `BoardExitAck` 仍按既有权威所有权执行 |

质量/SPC Contract 的唯一 Owner 是质量数据域。它拥有 `MetricDefinition`、总体/分母、抽样、排除、分组、窗口、迟到数据和告警策略；不拥有原始量测、机判、复判、处置、配方发布或设备控制。任何产品都不得在自己的页面、报表或数据库中建立第二套统计口径。至少固定以下规则：

- 统计总体、有效分母、分子、排除原因、抽样资格和重复数据去重由 `MetricDefinition`/`SubgroupPolicy` 统一定义；
- 重印、返工和重检必须区分原始尝试与最终结果，返修后的合格结果不能进入首次通过率的首次分子；
- FPY 由批准的 `MetricDefinition` 固定入口总体、机会单位、首次尝试与完成条件；首次合格分子不包含返修/重工后通过。不能仅因后续身份解析失败、隔离或结果未知而缩减已进入的总体，须单列未知、未闭合与有依据的排除数量及其影响；未知不等于 NG。仅报告身份有效或已完成子集时显式命名条件口径，不能冒充全部进板的完整流程 FPY；总体无法可靠重建时标明不可估计。DPMO 同样固定机会单位、有效分母与排除依据，可变机会数逐项求和；
- Cpk 只用于满足有效 MSA、稳定过程和合理子组条件的连续量过程能力，不能替代板级良率或机判；
- 迟到事件生成新的受控 assessment，不覆盖已发布报告；每个 assessment 绑定统计策略、输入范围、数据水位和证据版本。

既有 SPC 指导中“身份有效板”分母保留为其原版本的条件口径；不能因本架构补充了全流程口径就静默重算或改名历史指标。增加完整流程 FPY 时，由质量数据 Owner 同步修订既有 MetricDefinition、指导和消费者，冻结入口计数与未知项处理，验证后发布新版本；新旧报告须能区分口径并回放。

质量中心只能发布 `NCR`、`CAPA`、`HoldRequest` 等质量事件或受控请求。质量中心负责质量事件的创建、审批、关闭和效果确认；设备/产品 Owner 负责 `RunControl` 的接受、拒绝、应用、实际效果和回执。质量中心不得直接写设备状态，设备未回执前不得显示“已暂停”或“已生效”。

`PatternInspection` 与 `FinalAVI` 必须使用不同的 `InspectionIntent` 和事实类型：前者是制造过程中的设计图形/层对象检查，后者是成品外观验收。`PatternFinding` 不能直接转换为 `FinalAppearanceFinding`。二者可以复用图像、坐标、几何、证据、量测和复判能力，但必须保留不同的领域、阶段、规则和放行语义。点胶/胶路、三防漆、灌封、底部填充和胶粘剂属于后续 `ProcessMaterialInspection` 能力族，分别定义 `Dot`、`Bead`、`Coating`、`Encapsulation`、`Underfill`、`Adhesive` 对象，不能建立或复用万能 `UniversalDeposit`；当前保持专项指导范围。

### 8.4 站点、产线和企业边界

```text
设备边缘（Edge Station）
  采集/算法/机判/复判/处置/出板回执
        │ 已提交事实、事件、回执；可离线缓冲
        ▼
产线质量中心（Line/Site Quality Hub）
  谱系、跨站时间线、SPC、遏制、NCR/CAPA、权限审批
        │ 版本化查询、质量事件、受控建议；不替代实时设备控制
        ▼
企业 MES/QMS/数据平台
  工单主数据、企业质量流程、长期分析、审计和报表
```

设备功能安全由设备侧独立安全体系及安全控制器负责，边缘普通软件必须遵守其联锁，软件缓存和运行状态不能替代安全许可；本机结果提交由 DataService 负责，机判与板流继续按第 3.12.2 节分工。质量中心拥有获批范围的跨站质量事件与质量处置流程，不能接管设备 FinalDisposition 或运动授权；MES/QMS 拥有企业主数据和质量治理范围。跨站事件契约归入 `C-08`，事件身份字段和通用 Envelope 语义由 `C-01` 提供，不另建平行工作包。接口必须支持离线缓存、重启续传、重复事件幂等、乱序到达、迟到事件、租户/站点隔离和权限撤回。网络连通只表示传输条件，不表示业务接收、事实提交、处置生效或设备应用成功。

跨站事件至少携带 `eventId`、`schemaVersion`、`siteId`、`stationId`、`inspectionDomain`、`boardRunId`/实体键、`occurredAt`、`producerEpoch`、`sequence`、`causationId`、`payloadHash` 和来源权限快照。生产者的 `epoch + sequence` 用于识别重启、乱序和重复；消费者维护 durable inbox 和按分区的消费水位。水位只表示某消费者的处理进度/分区快照，不能当作全局事件顺序或生产者权威字段。重复事件返回原处理结果，冲突 hash 进入 `Conflict/Hold`，不能用“最后到达”覆盖先前事实。

跨进程、设备和站点不假设 Exactly-Once Delivery。持久业务消息采用至少一次投递、durable Inbox/Outbox、稳定 Commit Identity、幂等消费者及冲突检测；重发可更换 message ID，但不能变更业务幂等键或载荷。接收 ACK、业务提交回执和设备执行回执分别解释。重试须有退避、容量上限、可查询状态及人工恢复入口；去重记录/已执行标记的保留范围必须覆盖批准的离线和迟到窗口，恢复备份时一并恢复，超出窗口的旧消息不得作为新动作执行。原始帧流按采集契约记录丢帧/重采，不机械套用业务消息重发；外部设备不支持幂等或执行状态查询时，动作超时保持 Unknown，先核实实体与设备状态，不能靠重发保证所谓恰好一次物理执行。

时间与顺序使用以下独立语义，字段沿用 `DEV-ARC-005` 的 Envelope，不另建通用 Timestamp 别名：

| 依据 | 用途及边界 |
|---|---|
| UTC 墙钟及 OccurredAt/ReceivedAt | 业务时间、审计和跨站时间窗口；来源时间与接收时间分别保存，不因晚到改写发生时间，不单独证明先后或因果 |
| 单调时钟 | 同一可比较时钟域内的持续时间、deadline 和安全有效窗；按 clock kind、machine boot/timing epoch 校验，跨机/跨 boot 不直接相减 |
| 生产者 epoch + 分区 sequence | 事件顺序、重复、重启和缺口；epoch 内单调不等于全局顺序 |
| 消费水位 | 某消费者已连续处理的分区范围；与实际采用的精确事实集合共同定义评价快照 |
| Encoder/WebCoordinate | 卷料空间位置；绑定卷段基准和帧/触发关系，不能以墙钟或网络到达时刻替代 |

对帧/动作对齐、跨设备关联和 SPC 时间窗，采集/事件证据须按适用性引用时钟来源/域、同步状态、观测偏差或不确定度界、校验时刻/有效期以及 TimeQuality；缺少这些语义的契约由 C-01/C-03/C-08 按消费者登记扩展，不向所有 Envelope 强加同一组字段。配置中的最大允许偏差是门限，不是实测精度；无法验证则记录 Unknown，不能默认偏差为零或同步已完成。设备硬件 tick 映射到主机时间需保存转换/标定版本和有效域；优先用触发 ID、帧序号、设备序列和实体谱系关联，时间只在质量满足门限时辅助对齐。NTP 回拨、漂移超限、时钟失锁、跨 boot 或证据过期时，保留原始事实并标明受影响窗口；不得硬算精确跨机延迟或强行合并 SPC 子组。deadline 扣减和旧令牌拒绝继续执行权威规范第 7.2/10.2 节，不增加第二套时钟协议。

### 8.5 资源、性能和可观测性基线

所有性能目标在目标机、目标分辨率、代表性板型和已冻结 Profile 后测量；本文件不把厂商宣传值写成指标。每个模块必须分别登记计时起止、输入规模、P50/P95/P99 或 CT 口径、内存/CPU/GPU、线程/句柄、磁盘/缓存、队列深度和取消/超时后的释放结果。未有真实 Profile 时使用 `PendingProfile`，不填猜测值。

系统级容量必须能由下式核算并用实测参数替换：

```text
所需处理能力 ≥ 目标板流入率 × (1 + 峰值余量)
并行度 × 单实例有效处理率 ≥ 所需处理能力
稳态理想出板间隔下界 = max(各阶段每板平均服务时间 / 该阶段有效并行度)
单板端到端延迟 = 实际关键路径上的服务时间 + 排队 + 交接/同步等待
实际 CT 和吞吐还受共享资源争用、输送互锁、复判阻塞和突发输入约束，以目标机测量为准
```

必须可观测并可按 `boardRunId`、`attemptId`、`operationId`、`decisionRevision` 和 `traceId` 关联：采集完整性、参考面/计量质量、规则未执行原因、AI 推理和回退、提交回执、复判领取、外部 ACK、水位延迟、资源增长和恢复次数。日志不得记录客户敏感图像或凭证；诊断导出必须脱敏、哈希、清单化并可回读验证。

板/Panel 模式与连续卷料模式必须分别建模性能。板/Panel 使用板级 CT、FOV 数量、阶段 P50/P95/P99、队列等待和资源峰值；FPC 卷对卷使用 `ContinuousInspectionProfile`，至少测量 `WebSpeed`、`LineRate`、`EncoderRate`、像素/长度比例、缺陷定位延迟、最大连续运行长度、卷长、缓冲深度和 `WebBackpressure`。连续运行不能用单板 CT 代替，编码器丢脉冲、拼接段、张力异常和背压必须有可观测状态与恢复动作。

### 8.6 国际化、本地化与可达性

三语 `zh-CN/zh-TW/en-US` 是当前交付基线；语言与区域资源支持扩展，按产品配置和交付要求冻结验收集合。扩展语言不改变领域语义、规范单位或生产事实。

- 本文其余章节出现的“三语”指**当前最小基线** `zh-CN/zh-TW/en-US`。实际验收语言集由 `ProductProfile.SupportedLocaleSet` 决定，新增语言不得修改页面代码或重新编译业务逻辑；
- 本地化范围包括：界面文本、术语表、错误与原因码翻译、报告与导出模板、帮助与 SOP、日期/时间/数字/单位格式、排序与检索规则；
- **术语一致性**：领域术语（缺陷名、量测名、状态名）必须来自受控术语表（附录 A），不得由译者自由发挥；术语变更走版本化流程，历史记录按其提交时的术语版本解释；
- 缺译项在验证和诊断中必须可检出，运行按批准语言回退并保留可理解内容，不显示空白或资源键；关键生产提示缺译阻断该语言发布，不能把工程占位文本交给操作员；
- 区域差异不只是语言：单位制（mm/mil、µm/µin）、纸张与报告格式、时区与班次定义、键盘布局、法规文本要求都属于本地化范围；单位切换只影响显示，不改变规范量值与判定（第 2.11.4 节）；
- 可达性基线：不以颜色单独表达状态（已有条款）、可键盘完成主任务、对比度与最小字号可满足车间照明条件、适用触摸机型按手套操作验证目标尺寸、UIA 可自动化；
- 文本扩展（不同语言长度差异可达数倍）必须在布局验收中覆盖，避免截断与遮挡；
- 三语之外新增语言时，验收矩阵按 `SupportedLocaleSet` 自动扩展，而不是逐页重写测试用例。

### 8.7 复判与返修工位的效率、一致性与人因

复判与返修工作区按产品领域显示证据、操作和缺陷语义。效率、一致性与误操作恢复分别验收，复判不是质量放行或完整路线验证的替代。

| 维度 | 架构要求 |
|---|---|
| 效率 | 单件复判的关键路径可测量（定位、判读、决定、提交）；支持键盘流、连续处理、批量同类项处理与优先级排序 |
| 证据一步到达 | 从待判项一步到达原图、3D/剖面、量测值、规则依据、历史同位置记录与相似案例（第 10.5 节） |
| 一致性 | 复判结论可被抽检复核；按第 7.8.2 节定期评估判定者内/间一致性，结果用于培训与规则澄清，不用于惩罚性排名 |
| 二次确认 | 高风险处置（报废、批量放行、跳过）需二次确认或双人；权限与审计留痕 |
| 人因 | 避免默认选中高风险选项；危险动作与常用动作在空间上分离；连续作业的疲劳与节奏可观测 |
| 队列与协作 | 多工位并发复判时 Claim 互斥与超时释放；跨轨道/跨设备来源可区分（第 3.14.2 节） |
| 反馈闭环 | 复判结论进入 AI 数据闭环与误报分析（第 7.6 节），但不得反向修改原机判与量测（第 7.3 节） |

复判工作区的效率优化不得以减少证据展示为代价：允许折叠与渐进披露，但“接受建议”只能填充待确认内容，“提交人工决定”才触发权限与状态复核及提交；键盘快捷路径须保留明确提交边界和错误恢复，不以无关弹窗堆叠替代确认（第 10.5 节）。

## 9. 升级与变更隔离

### 9.1 变更影响分类

| 变更 | 典型影响 | 强制动作 |
|---|---|---|
| 单一领域算法/页面 | 该产品 | 领域测试、产品 UI 和性能回归 |
| 共享控件/主题 | 所有使用产品 | AOI、SPI、钢网和 PCB 关键页面回归 |
| 共享视觉能力 | 相关设备和产品 | 契约测试、真实消费者回归、性能/资源验证 |
| 公共数据契约 | 可能影响所有产品和历史数据 | Schema 版本、迁移、回读、兼容验证；只回退工程指针，不回退生产事实 |
| 设备/协议适配器 | 目标设备相关产品 | Adapter 测试、能力回读和 HIL |
| AI 推理后端 | 使用该后端的领域 | 模型/引擎兼容、基准、回退和资源验证 |
| 质量管控查询 | 分析和报表 | 快照、分母、历史还原和权限回归 |

### 9.2 必须具备的隔离手段

1. 共享平台 API 和数据契约版本化，新增可兼容；改变单位、坐标方向、时间语义、枚举含义、状态语义或默认值必须升版本；
2. 产品通过能力清单和模块装配启用功能，禁止运行时隐式降级到另一产品语义；
3. 领域包不能依赖其它领域包的内部代码，只能使用公共契约和批准的跨工序事件；
4. 共享 UI 控件、主题或布局修改必须检查所有产品的关键工作区；
5. 公共模块发布前执行所有真实消费者的构建、契约、关键任务和资源回归；
6. 产品安装包、配置、Schema、模型、标定和数据库迁移可独立治理；数据库采用 expand/contract、兼容窗口和回读验证。工程版本、部署指针和发布配置可以按兼容范围回退，但 `MeasurementSet/InspectionFact`、`MachineDecision`、`ResultCommitReceipt`、`BoardExitAck` 等生产事实只追加，不得用旧备份覆盖或回滚；
7. 产品版本必须声明共享平台的兼容范围，实际安装锁定精确的平台、契约、模型、标定和插件版本；需要时允许 AOI 和 SPI 并行使用不同的共享平台版本，不要求所有产品同步升级，也不允许任意替换共享 DLL；
8. 升级前生成并签名版本清单和备份，升级后回读配置、历史事实和关键能力；签名/撤销状态必须在安装、装载、运行准入和升级后复查，并防止检查与使用之间发生未授权替换；
9. 任一共享变更未通过影响分析或消费者验证，相关产品保持旧版本或 `Blocked`，不能强行发布。

一个仓库不等于一个发布版本，一个共享控件不等于一个业务页面，一个公共契约不等于所有领域拥有同一语义。

### 9.3 灾备目标与恢复验收

备份恢复复用 [维护健康备份升级指导](../../docs/40-development/70-operations/维护健康备份升级开发指导.md) 的 BackupCheckpoint/BackupReceipt/RestoreDrillReceipt 及 [多存储提交协议](../../docs/40-development/60-data/多存储RPO0提交协议开发指导.md)，不建立平行备份服务。每个产品/站点的批准部署与性能策略须声明故障范围、数据等级、RPO（允许丢失范围）、RTO（恢复目标）、恢复责任及演练频率；未冻结时保持 PendingProfile，不填统一宣传值。

| 数据/故障范围 | RPO 与恢复约束 |
|---|---|
| 已提交生产事实、必须证据、回执和审计 | 本机 RPO=0 仅在已批准介质、文件系统、驱动及断电保证范围内成立；本机介质毁损/整站灾难另按异地副本和已确认复制水位验收，异步 Outbox 不证明异地零丢失 |
| 在途运行、设备动作及 Inbox/Outbox | 恢复提交/兑换日志、去重标记和待处理消息，逐一核实设备 epoch、实体位置和未完成动作；数据库恢复不能代表实体状态已恢复或允许重新执行旧授权 |
| 原始图像/3D、派生缓存和工作数据 | 以 EvidencePolicy/保留与 LegalHold 规则分级；放行必需证据不得按可丢缓存处理，缺失必须降低回放能力并暴露缺口 |
| Released 配置、模型、库、标定及批准记录 | 备份精确版本及依赖闭包、签名/信任记录；恢复不把旧配置重新批准，也不使用旧备份覆盖后来已提交的事实 |

RTO 分别统计单服务、单设备/整机和站点恢复，起止点应覆盖发现故障、隔离、数据恢复、验证及获准恢复生产；“服务启动”不是生产恢复完成。演练必须从明确 checkpoint/WAL/CAS 闭包在隔离环境重建，独立回读逐对象 hash/长度，核对数据库/证据/回执/审计引用，执行权限与密钥可用性检查、领域查询和适用回放，再测量实际 RPO/RTO 并签发演练回执。引用缺失、介质损坏、WAL 不完整、版本不兼容、已撤销密钥、重复消息和动作未知均须覆盖，备份文件存在不能表示 Restorable。

密钥恢复沿用 CNG/TPM/KMS 的引用、key epoch、用途和审批规则：历史验证公钥及解密密钥的保留按证据保留期管理；不可导出私钥不得为备份私自导出，遗失后按批准流程换钥和重新建立信任。恢复不能撤销吊销决定、重用旧 boot 或让已执行授权恢复成未执行。UI 显示最近成功演练、覆盖 checkpoint、实际损失/耗时、证据缺口及待人工核实动作，切回生产仍须通过设备回读、当前权限/资格和受控批准。

## 10. GitHub 架构证据与迁移结论

以下资料于 2026-09-14 至 2026-09-16 通过 GitHub 公开 API、仓库 README、固定提交源码和目录结构核对。stars 仅作为项目活跃度线索，不能证明工业生产质量。许可证必须由项目法务和依赖 Owner 进一步确认。

| 来源 | 已观察架构 | 可迁移到本项目的内容 | 限制和不采用内容 |
|---|---|---|---|
| [Prism](https://github.com/PrismLibrary/Prism/tree/358118cd640d9a22ff8cf21c8ad197fa038b7990) | 在固定提交中可直接核对 [`ModuleCatalogBase`](https://github.com/PrismLibrary/Prism/blob/358118cd640d9a22ff8cf21c8ad197fa038b7990/src/Prism.Core/Modularity/ModuleCatalogBase.cs) 的依赖完整性校验和 [`ModuleDependencySolver`](https://github.com/PrismLibrary/Prism/blob/358118cd640d9a22ff8cf21c8ad197fa038b7990/src/Prism.Core/Modularity/ModuleDependencySolver.cs) 的循环依赖检测；WPF E2E 还有独立模块装配 | Shell、模块目录、区域导航、依赖注入、平台层与核心层分离、独立模块测试 | 当前 Prism 9 README 标注 Dual License；不直接引入，先核对版本和商业许可；Prism 不提供 SPI 领域架构 |
| [WPF UI](https://github.com/lepoco/wpfui) | WPF Fluent 控件、主题、Navigation、Dialog、Snackbar；仓库含 architecture、views、testing、theming 文档 | UI 基础控件、主题分层、导航和架构文档组织 | 其视觉语言不能直接决定工业操作流程；当前项目以 DevExpress 和现有 UI 规范为准 |
| [MaterialDesignInXAML Toolkit](https://github.com/MaterialDesignInXAML/MaterialDesignInXamlToolkit) | WPF 控件库和多个 Demo；包含 Dialog、Grid、主题以及 UI 线程/渲染性能文档 | 控件状态、主题资源、Demo 驱动的控件审查、WPF 性能关注 | Material 风格不是 SPI 必须的产品风格；不复制其主题或依赖作为质量标准 |
| [OpenPnP](https://github.com/openpnp/openpnp/tree/5bd404cfc70f34103a3ca0fbb6b50c2b465f407c) | 固定提交的 [`CvPipeline`](https://github.com/openpnp/openpnp/blob/5bd404cfc70f34103a3ca0fbb6b50c2b465f407c/src/main/java/org/openpnp/vision/pipeline/CvPipeline.java) 按顺序运行可序列化阶段；[`CvStage`](https://github.com/openpnp/openpnp/blob/5bd404cfc70f34103a3ca0fbb6b50c2b465f407c/src/main/java/org/openpnp/vision/pipeline/CvStage.java) 暴露独立处理和中间模型结果；仓库还分开 `model`、`machine`、`gui`、`wizards` 和测试 | 机器/设备、视觉 pipeline、模型、GUI、向导、测试的边界；设备驱动与上层流程分离 | GPL-3.0，Java，面向贴片机；`org.openpnp.spi` 是 Service Provider Interface，不是 SPI 检测；不能复制代码、许可证或把贴装对象迁移为 SPI/AOI 对象 |
| [Anomalib](https://github.com/open-edge-platform/anomalib/tree/7d2a8ead7e8abb2327de2143a15c415cbd011299) | 固定提交包含 `application/backend/src/services`、`workers`、`repositories` 和 Pydantic 模型，分别承载 pipeline 服务、后台推理/训练、数据集快照仓储和契约模型 | AI 训练与生产推理解耦、dataset snapshot、pipeline service、后台 worker、模型导出和回退边界 | Python/深度学习异常检测库；不能用其 benchmark 或示例数据证明 PCB/SPI 量测准确度，不能照搬 Web UI |
| [ONNX Runtime](https://github.com/microsoft/onnxruntime/tree/8d85527a010e294a26b274749f74294b2a32cec5) | 固定提交的 C# `InferenceSession`/`SessionOptions` 边界把会话配置、模型加载和执行后端隔离 | AI 推理后端适配、CPU/GPU/加速器能力探针、模型版本与资源预算 | 推理引擎不负责缺陷语义、权限、复判或生产放行；不能把推理成功当质量成功 |
| [OPC UA .NET Standard](https://github.com/OPCFoundation/UA-.NETStandard/tree/8e874d073b54915a610eea205a930ab5064e7ede) | 固定提交保留 Core/Client/Server/PubSub/Device Integration 分层，并提供 [`StateMachines`](https://github.com/OPCFoundation/UA-.NETStandard/blob/8e874d073b54915a610eea205a930ab5064e7ede/docs/StateMachines.md)、高可用和订阅文档；版本/分支和迁移需显式管理 | 工厂互联的设备模型、能力/版本、迁移、状态机、长稳测试和协议层隔离 | 具体协议、模型和客户设备仍需签署；不因仓库支持 OPC UA 就认为目标印刷机/产线已兼容 |
| [SharpSCADA](https://github.com/GavinYellow/SharpSCADA) | 网关、采集归档、报警、TagConfig、设计时/运行时 HMI、驱动 DLL 和客户端/服务端示例 | 设计时与运行时分离、驱动扩展、采集/报警/归档的模块边界 | LGPL-3.0、较旧 .NET Framework，README 自述安全性不足；只作工业工作流参考 |
| [Gerbonara](https://github.com/jaseg/gerbonara/tree/736107f7a4fa1f9858d4da93879ca00015893628) | 固定提交包含 [`rs274x.py`](https://github.com/jaseg/gerbonara/blob/736107f7a4fa1f9858d4da93879ca00015893628/src/gerbonara/rs274x.py)、[`excellon.py`](https://github.com/jaseg/gerbonara/blob/736107f7a4fa1f9858d4da93879ca00015893628/src/gerbonara/excellon.py)、[`ipc356.py`](https://github.com/jaseg/gerbonara/blob/736107f7a4fa1f9858d4da93879ca00015893628/src/gerbonara/ipc356.py) 及 [`tests/`](https://github.com/jaseg/gerbonara/tree/736107f7a4fa1f9858d4da93879ca00015893628/tests) 下的格式和黄金样例测试；输入解析与测试数据保持可定位关系 | `BoardDataAdapter` 的格式分派、单位/语义校验、格式回归夹具和输入快照设计 | Apache-2.0；只覆盖公开 Gerber/Excellon/IPC-356 方向，不能证明 ODB++/IPC-2581 兼容，也不能证明制造检测能力或测量精度 |
| [Aravis](https://github.com/AravisProject/aravis/tree/086b1a7829e1655fb2140658a262a9876581af4c) | 固定提交包含 [`arvbuffer`](https://github.com/AravisProject/aravis/blob/086b1a7829e1655fb2140658a262a9876581af4c/src/arvbuffer.c)、[`arvstream`](https://github.com/AravisProject/aravis/blob/086b1a7829e1655fb2140658a262a9876581af4c/src/arvstream.c)、相机、fake camera 和 [`acquisition tests`](https://github.com/AravisProject/aravis/blob/086b1a7829e1655fb2140658a262a9876581af4c/tests/arvacquisitiontest.c)，并提供 [`thread-safety`](https://github.com/AravisProject/aravis/blob/086b1a7829e1655fb2140658a262a9876581af4c/docs/reference/aravis/thread-safety.md) 说明；采集、缓冲和测试边界清晰 | 线扫/面阵采集适配器的 buffer 所有权、异步流、帧完整性、取消、假相机测试边界和资源回收设计 | LGPL-2.1；C/GObject 工业相机库，不能直接作为本项目 .NET/AsunImage 实现或目标相机 HIL 证据 |
| [Open3D](https://github.com/isl-org/Open3D/tree/d32b4fce639b3cde284184072796480ef9b528d1) | 固定提交包含独立的 [`pipelines/registration`](https://github.com/isl-org/Open3D/tree/d32b4fce639b3cde284184072796480ef9b528d1/cpp/open3d/pipelines/registration) 实现、[`registration benchmarks`](https://github.com/isl-org/Open3D/tree/d32b4fce639b3cde284184072796480ef9b528d1/cpp/benchmarks/t/pipelines/registration) ；配准算法、结果和性能评估分层 | 点云/高度场配准的算法边界、RegistrationResult、对应关系检查、基准和退化样例组织 | 仓库 API 元数据未声明可直接采用的许可证结论；C++/Python 参考实现，不能替代 HALCON/AsunImage、工业计量资格或目标机验证 |

### 10.1 GitHub 证据转为我方决策

- 采用 Prism/OpenPnP 类的“模块目录 + 设备/视觉/GUI 分层”思想，但按现有 .NET/WPF/DevExpress 和项目契约重新实现；
- 采用 Anomalib/ONNX Runtime 类的“训练、推理、后端、数据集和生产服务分离”，但 AI 结果遵守本项目事实/候选/复判边界；
- 采用 OPC UA 项目类的“版本分支、迁移、状态机、能力和长稳验证”方法，扩展到所有共享平台变更；
- 不直接复制任何仓库代码，不把 Web、SCADA、贴片机或异常检测项目的领域对象转成 PCB、SPI 或 AOI 领域对象；
- 许可证、第三方依赖、客户数据和商业交付必须在正式复用评审中单独关闭，不因公开仓库可见而默认可商用。

### 10.2 证据定位与等级

本节只把能够定位到固定提交的源码观察写入架构依据。`A` 表示固定提交的源码/仓库文件已核对；`B` 表示固定提交的目录或官方说明已核对；`C` 表示 README、营销页或未能确认实现细节的线索。任何等级都不能证明本项目的生产性能、计量能力或客户验收。

| 设计问题 | 固定证据 | 等级 | 我方落地断言 |
|---|---|---:|---|
| 模块依赖和循环检测 | Prism `ModuleCatalogBase.cs`、`ModuleDependencySolver.cs`，提交 `358118c` | A | 产品装配启动前验证模块存在性、依赖方向和循环；失败时显示可操作原因 |
| 可编辑视觉流水线 | OpenPnP `CvPipeline.java`、`CvStage.java`，提交 `5bd404c` | A | SPI 编程可采用显式有序阶段和中间证据，但每阶段必须有输入输出、版本、失败策略和领域类型 |
| AI 服务与训练隔离 | Anomalib `application/backend` 的 services/workers/repositories/pydantic_models，提交 `7d2a8ea` | B | 训练、数据集、推理和生产候选分离；生产边界仍由本项目 `EffectiveRuntimeManifest` 和 Decisioning 管理 |
| 推理后端隔离 | ONNX Runtime C# `InferenceSession`/`SessionOptions`，提交 `8d85527` | A | 后端能力探针、会话资源和模型 hash 绑定；推理成功不改变质量事实 |
| 工业互联状态/订阅 | OPC UA `.NETStandard` 的 StateMachines/Subscriptions 文档和分层目录，提交 `8e874d0` | B | 接口区分连接、业务确认、应用、回读和效果；协议支持不等于现场设备兼容 |
| 制造数据解析与回归 | Gerbonara `rs274x.py`、`excellon.py`、`ipc356.py` 与 `tests/`，提交 `736107f` | A | 输入格式分派、解析错误、单位和黄金样例回归必须属于 `BoardDataAdapter` 入口；不能把解析通过当作几何或检测资格 |
| 连续采集与帧资源 | Aravis `arvbuffer`、`arvstream`、`arvcamera`、acquisition tests 和 thread-safety 文档，提交 `086b1a7` | A | 采集适配器必须明确 buffer 所有权、帧完整性、线程边界、取消和释放；线扫还需另行验证编码器同步和连续运行 |
| 点云/高度场配准 | Open3D `pipelines/registration`、registration benchmarks，提交 `d32b4fc` | A | 配准结果、对应关系、退化/失败和基准应作为 C-03 的算法输入与测试组织；不能把开源 benchmark 当计量资格 |

GitHub 访问日期为 `2026-09-14` 至 `2026-09-16`。表 10.2 的落地证据使用固定提交 URL；未固定提交的仓库主页仅作研究线索；后续仓库变化只形成新的研究输入，不自动改变本项目金标准。Prism 的 Dual License、OpenPnP 的 GPL-3.0、Anomalib/ONNX Runtime/OPC UA 的许可证和版本必须在实际引入依赖前由工程与法务复核；Gerbonara、Aravis 和 Open3D 的许可证/组件边界也必须在实际引入依赖前复核；本项目当前决策是吸收边界思想并按现有 Asun/.NET/DevExpress 契约实现，不直接复制实现。

### 10.3 GitHub 研究得到的通用模块交付模式

GitHub 项目真正有价值的部分不是类名，而是边界是否能让第二个消费者安全接入。后续每一个候选共享模块都必须按以下交付单元设计：

```text
Contracts       强类型输入/输出、Schema、错误、版本和兼容规则
Core            无副作用规则/算法策略、状态和验证
Adapters        相机、文件、数据库、协议或厂商 SDK 的映射
Runtime         调度、取消、超时、资源租约、指标和健康状态
UI              可选的 WPF 编辑/预览/诊断，不拥有业务事实
Consumer Kit    API、最小真实消费者、契约测试、SBOM、迁移说明
```

这套模式必须落到仓库已经批准的 `.Contracts`、`.Core`、`.ImageLib`、`.Adapters.*`、`.Ui.Wpf` 和产品 Feature 边界，不新建平行平台。一个模块的“独立”至少要求：可以在没有产品页面的情况下完成 Headless 合同测试；可以由两个不同消费者以不同产品配置装配；能报告实际版本和资源；失败、取消、重启和升级不会改变另一个产品的权威事实；卸载或替换后仍能通过能力检查明确返回 `NotReady`。只有满足这些条件，才允许把它提升为共享能力包。

### 10.4 模块之间的链路闭环与禁止越级

每一条功能链都必须有唯一生产者、唯一权威状态和明确消费者。SPI 的最小闭环如下：

```text
M01 数据/坐标
  → M02 钢网/焊盘/沉积目标
  → M03 已发布配方与审批
  → M04 定位/采集/覆盖 Attempt
  → M05 参考面/分割
  → M06 三维 MeasurementSet
  → M07 RuleEvaluation
  → InspectionDecision
  → 既有 Decisioning MachineDecision
  → M09 EvidenceCommit / ResultCommitReceipt / 追溯
      ├→ M08 复判（需要时，提交 ReviewDecision）
      │   → RouteAssessment
      │   → 既有 Orchestrator FinalDisposition / DecisionActivationProof
      │   → DataService DispositionCommitReceipt / RouteAuthorization
      │   → BoardExitAck
      └→ M10 SPC 与 M11 受控反馈提案
```

SPC 与反馈提案从匹配的已提交结果开始消费，不以板件已经离站作为统一前提。复判、处置和出板回执按各自提交时点成为后续独立输入；只有依赖这些事实的指标或动作才等待相应回执。受控反馈命令仍须通过作用范围、权限、设备实际状态及执行门禁，不能由统计分支直接触发设备动作。

| 链路位置 | 唯一 Owner | 下游可以消费 | 禁止越级 |
|---|---|---|---|
| 坐标/配方 | M01–M03 对应领域服务 | 定位、覆盖、规则引用的固定快照 | M06 直接读取 UI 当前值或 `latest` 配方 |
| 采集/参考 | M04/M05 | 有效 HeightField、参考面、分割证据 | M07 用显示网格、旧帧或失败帧补造量测 |
| 计量/规则 | M06/M07 | MeasurementSet、InspectionFact、RuleEvaluation、InspectionDecision 提议和解释 | M06/M07 不得自建权威 MachineDecision；UI 修改生产结果 |
| 机判/提交 | 既有 Decisioning/DataService | ResultCommitReceipt、版本固定事实 | M08 在提交前领取生产 Claim；M10 读取未提交候选 |
| 复判/处置 | ReviewService/Orchestrator | ReviewDecision、FinalDisposition；DataService 持久化 `DispositionCommitReceipt` 并签发 `RouteAuthorization` | AI 代替人工 Claim；质量中心直接出板 |
| 统计/反馈 | M10/M11 | committed snapshot、质量事件、受控建议 | SPC 或建议直接覆盖历史事实、强写设备 |

所有过渡都必须定义成功条件、输入输出、可接受状态、禁止状态、重试边界、取消点、资源释放、审计身份和恢复入口。生产 AI 辅助复判、SPC、质量中心和生产结果导出消费稳定提交的事实。提交前的 AI 图像质量评估、分割与检测候选按批准 DAG 消费本次不可变、版本固定且来源可验证的输入，其输出经领域评价及既有结果链提交；不能反过来等待本次 ResultCommitReceipt，也不能把候选当作已提交事实。工程回放与候选导出保留隔离用途。任何路径都不能用 UI 完成、文件存在或网络连通推断上游业务成功。

### 10.5 UI 便利性与专业化验收模型

共享的是交互基础设施和视觉语义，专业产品负责任务流。每个生产任务在设计评审时建立如下可执行卡片：

| 项目 | 必须明确 |
|---|---|
| 任务角色 | 操作员、编程员、复判员、计量/设备、质量或管理员 |
| 首屏判断 | 当前板/尝试、产品/配方版本、状态、影响、唯一下一动作 |
| 最短路径 | 正常完成的点击/按键序列；常用动作支持键盘和连续处理 |
| 错误路径 | 错误原因、影响范围、可恢复动作、预计等待和升级入口 |
| 高级操作 | 默认隐藏、权限、风险、预览、差异、审批和撤销/回退 |
| 证据联动 | 板级→Unit→开口/元件→2D/3D/剖面→参数来源→历史尝试 |
| 可观测性 | 状态水位、后台 Operation、进度、取消和回执；切页不丢失任务 |
| 验收记录 | 任务完成时间、误操作、恢复成功率、DPI/三语/UIA/分辨率结果 |

SPI 生产首屏应优先显示：板号和配方快照、采集/计量/判定/提交/出板五段状态、异常数量与最严重原因、当前对象证据和下一安全动作。参数编程页应优先显示对象作用域、单位、有效范围、数据来源、影响对象数量、预览差异和发布状态。复判页应让原始机判、量测值、有效性、证据、AI 建议和人工决定并列可比，并将“接受建议”与“提交人工决定”分成两个明确动作。

禁止使用会降低扫描速度或制造歧义的装饰性卡片、自动轮播、无意义动画、隐藏式关键命令、颜色单独表达状态、把所有参数塞进一页或把 AOI/SPI/钢网术语混在同一列表。所谓炫技功能只有在减少操作、提前发现风险、提高证据理解或缩短恢复时间之一得到实测收益时才进入产品。

### 10.6 AI 的发展路线和产品化约束

AI 的发展方向是从单点缺陷模型扩展为“数据闭环 + 多模型编排 + 人机协作 + 过程质量分析”，但每一层仍受 SPI 计量和生产责任约束：

```text
确定性计量/规则基线
  → AI 图像质量与候选分割
  → AI 复判排序/相似案例/证据解释
  → 多模型编排与不确定性/拒识
  → 跨工序质量关联和漂移预警
  → 经批准的自动决策或参数建议
```

| AI 阶段 | 输入 | 输出 | 必须满足 |
|---|---|---|---|
| 候选 | 固定图像/HeightField/已提交量测 | 候选区域、类别、置信度、拒识 | 不改变生产量测和机判；可回放 |
| 辅助复判 | ResultCommitReceipt、证据快照、历史案例 | 排序、相似案例、解释建议 | 人工确认仍是 ReviewDecision；保留建议版本 |
| 过程分析 | 已提交时间序列、谱系和分母 | 漂移、异常关联、预警 | 相关性与因果分开；质量人员批准 |
| 参数建议 | Draft/候选模型、验证集和影响范围 | 可比较的候选参数/模型 | 只能写 Draft；必须预览、验证、审批、发布 |
| 自动化 | 固定模型、规则、权限和设备能力 | 受控新 decisionRevision 或动作建议 | 置信度、拒识、回退、审计、双人/质量批准和现场验收齐全 |

未来可使用视觉语言模型或检索增强模型帮助解释已批准事实、SOP 和历史案例，但模型不得直接写入 `MeasurementSet/InspectionFact`、`MachineDecision`、`ReviewDecision`、`RouteAuthorization` 或设备命令。自然语言解释必须引用证据和版本；证据不足时显示“不足以判断”。模型推理服务应独立于生产 UI，具有模型/提示/检索快照、超时、资源预算、脱敏和确定性回退。

## 11. 实施路线

### 阶段 A：平台和边界冻结

- 在第 14.6 节既有契约/模块目录和交付资产中登记产品族、共享能力、领域对象与装配关系，并生成所需检查视图，不另建同义注册表；
- 盘点现有 AOI 源码、项目引用、真实 caller/consumer 和 Owner；
- 识别能直接复用的采集、定位、Surface3D、计量、Recipe、Review、Data、SPC、工厂和 UI 能力；
- 为共享能力建立契约版本、兼容策略、禁止路径和消费者回归表；
- 不以估计代码比例代替复用结论。
- 建立“板型 × 工艺路线 × 工位 × 检测方法 × 可观察范围”的覆盖矩阵，登记硬板、软板/FPC、刚柔结合板、HDI、层/面、单板/拼板/卷料和载具约束；
- 为每个工位明确已覆盖、未覆盖、不可达、方法不适用、证据不足和外部测试接入边界。

### 阶段 B：共享能力最小纵向链

- 先完成真实输入身份、采集/证据、量测、规则评价、提交回执和追溯查询链；
- 共享层先处理取消、超时、错误、资源释放、版本失效和恢复；
- 通过 SPI 最小链验证共享能力，不把 SPI 专属语义反向硬编码到平台层；
- 共享层每次修改同时检查现有 AOI 消费者。

### 阶段 C：专业产品工作区

- SPI 先完成生产、编程、复判、追溯、SPC、诊断；
- AOI 保持现有生产与编程体验，抽取公共能力时不改变其专业语义；
- 再建设钢网和 PCB 光板产品；
- PCB 光板产品按内层/积层/外层/阻焊字符/外形/成品 AVI 和片料、卷料路线拆分专业工作区；FPC/HDI 优先补齐专用定位、层/面、卷段和不可检项指导；
- 炉前/炉后 AOI 采用同一 AOI 领域包的不同产品配置和工作区，只有真正共享的能力才上提平台。

### 阶段 D：AI 和全流程质量管控

- 先做离线数据集快照、Replay、基线规则和人工复判证据；
- 再上线图像质量、候选排序、分割/缺陷候选和过程漂移提示；
- 通过 Shadow/Advice 验证后再考虑 Automatic；
- 最后建设跨工序质量时间线、SPC、根因线索和受控反馈；
- 质量管控平台只消费和解释事实，设备控制仍由各自产品和工厂互联 Owner 管理。

### 11.1 领域扩展顺序

在 SPI 共享能力纵向链稳定后，领域扩展按以下顺序进入独立的 Contract、指导文档、真实消费者和验收 Profile：

```text
首条切片的平台边界/Contract/Schema 冻结
  → SPI 最小纵向链
  → PCB Fabrication
  → HDI Laser Via / Layer Inspection
  → FPC / R2R / Coverlay / Stiffener
  → Rigid-Flex
  → 跨工序 QualityControl
  → AI / Process Optimization / Closed Loop
```

这是一条实施优先级，不是把所有产品绑定成固定路线。每个产品仍由自己的 `ProcessRouteRevision` 选择适用工位和覆盖要求；PCB、HDI、FPC 和刚柔结合板先完成领域契约与边界定义，再按实际设备、样板和资格条件逐步实现。SPI 保持第一条共享能力验证主线，PCB/FPC/HDI 的新增范围不能抢占或改写 SPI 的生产事实语义。

### 11.2 能力分期与工作包归属

下列能力映射到既有 `C-01`～`C-08`，不新建工作包编号。按产品实际使用范围选择切片；最终任务、Owner、路径和状态登记在现有模块目录/交付 Manifest 中，本表不另建任务状态。跨包协作仍由对应权威入口串行集成。

| 能力 | 章节 | 归属工作包 | 建议阶段 | 与 SPI 首条主线的关系 |
|---|---|---|---|---|
| 系统上下文与外部接口清单 | 1.2 | 架构 Owner（文档级） | A | 前置：界定契约范围 |
| 架构驱动因素、量级假设与非目标 | 1.3 | 架构 Owner | A | 前置：性能与容量预算的输入 |
| 合规基线与标准采用机制 | 2.12 | C-08（质量/装配）+ 合规 Owner | A | 按法定适用性及批准的合同/质量要求关闭受影响门禁；自愿采用不能替代强制义务 |
| 缺陷分类与代码映射 | 2.13 | C-04 + 质量数据域 | B | 影响统计口径，需早于 SPC 接入 |
| 传感与成像模态能力 | 3.13 | C-03（能力/标定/计量）+ C-06（适配器） | B | **主线前置**：SPI 3D 模态属性直接影响量测资格 |
| 板流、轨道与产线握手 | 3.14 | C-01（身份/并发）+ C-06（协议）+ C-07（并发性能） | B | **主线前置**（至少单轨最小集）；多轨可后置 |
| 板身份、读码与防错、首件/换型门禁 | 3.15 | C-01 + C-02（清单绑定）+ C-05（门禁界面） | B | **主线前置**：观察→解析回执→绑定→防错；未决仍留证，但不能绕过生产准入 |
| 设备状态、OEE、点检、维护、远程服务 | 3.16 | C-07（运行可靠性）+ C-06（远程安全）+ C-03（点检判据） | C | 点检为主线前置；OEE/远程可后置 |
| 跨机一致性与配方可移植性 | 3.17 | C-02（配方/清单）+ C-03（匹配与资格） | C | 多机客户交付前必须关闭 |
| 环境与工况监测 | 3.18 | C-06（采集）+ C-03（对不确定度的影响） | B | 主线关闭实际量测方法所需的环境条件、观测与越界行为；非必需项说明依据 |
| 数据分级、容量、完整性、归档与报告 | 3.19 | C-06（部署/存储）+ C-08（报告与导出）+ 数据域 | C | 容量模型需早于现场部署 |
| 自动编程与参数整定 | 3.20 | C-02（Draft 与发布）+ C-05（编程工作区） | C | 不进入主线判定链，但决定 NPI 竞争力 |
| 定制层级与扩展点隔离 | 4.4 | C-06（插件）+ 产品线 Owner | A | 约束性条款，立即生效 |
| 返修与再检闭环 | 6.4 | C-04（事实与替代范围）+ C-08（处置与统计）+ C-05（返修操作） | C | 适用路线验收前关闭缺陷修复与物料更换双链、实际追溯粒度及再验证 |
| 跨工序归因的受控形式 | 6.5 | C-08 + 质量数据域 | D | 依赖多工位数据积累 |
| 抽样检验与批次接收 | 6.6 | C-08（质量计划） | C | 与覆盖契约配合 |
| AI 治理、数据闭环、冷启动、统计验证 | 7.5～7.8 | C-04（推理接入）+ C-08（质量统计）+ AI Owner | D | AI 按阶段推进；参考真值、统计验证和分母定义须早于任何传统算法或 AI 的性能声明 |
| 国际化与可达性 | 8.6 | C-05（页面）+ 产品线 | B | 影响所有页面验收，越早越省成本 |
| 复判效率与一致性 | 8.7 | C-05 + C-08 | C | 与复判工作区同步 |
| 风险登记册与 ADR | 14.12、14.13 | 架构 Owner | A | 立即建立，持续维护 |
| 能力链与验收索引 | 14.14 | 产品负责人 + 架构 Owner | A | 作为验收范围检查输入 |

排期原则：首条纵向链使用的身份、模态、准入、提交、UI、安全与恢复要求在对应交付门禁前闭合；不要求为软件主线先实现全量硬件、所有模态和所有协议。真实板流、设备环境、计量与 HIL 证据依赖硬件时明确保持外部门禁，继续不依赖硬件的软件工作。在线 SPI 的最小板流按已选设备/现场协议冻结，不能把单轨 SMEMA 或“仅测温”视为所有机型的充分条件。

## 12. 架构审核和进入实施门禁

在一个共享模块或产品的具体实施切片开始编码前，必须冻结下列适用要求、责任人及验收方法；真实代码、设备和现场证据在对应交付门禁取得，不能把“已规划验证”写成“验证已通过”，也不要求尚未编写的代码先通过验收：

1. 产品/领域归属、Owner、真实 caller/consumer 和允许/禁止路径；
2. 输入输出、单位、版本/hash、身份、水位、权限、审计和资源 Owner；
3. 共享或领域独有的判定，以及不抽取为共享模块的理由；
4. 正常、边界、缺失、低质量、取消、超时、迟到、崩溃、断线和恢复路径；
5. 产品 UI 的主任务、窗体分类、布局、键盘、UIA、三语、DPI 和八态；
6. 性能/资源目标与预算、共享消费者回归范围、真实 WPF 验证方案和适用外部门禁；
7. 对 AI 的模型、数据集、输入域、置信度、解释、拒识、回退、审计和复判边界；
8. 对设备的能力探针、SDK/协议版本、应用/回读/效果与 HIL 退出条件；缺少实机输入时明确尚不能关闭的资格；
9. GitHub/第三方资料的版本、许可证、来源定位、可迁移内容和限制；
10. 指导文档的 Round 1 清点、Round 2 独立复核，以及该切片后续 `git diff --check`、定向验证和成熟度更新的门禁。

本文新增/扩展范围当前达到 `DocMapped`，可作为后续模块指导修订的输入；架构批准另按第 14.13 节记录，不由该成熟度推导。缺少 SDK、目标设备或真实样板不妨碍不依赖这些输入的文档工作。进入某个具体模块的 `ImplementationReady`，仍需在该模块范围内冻结实名 Owner、批准契约、真实 caller/consumer、输入输出、状态/错误/恢复、UI 验收、定向测试和性能预算。之后的 `Implemented`、`Tested`、`HIL`、`FAT/SAT`、`ProductionAccepted` 仍须按实际依赖关闭适用的代码、设备、计量、AI 数据/模型责任、WPF/UIA/DPI 和客户现场门禁。架构文档不能代替这些门禁，也不重新定义已交付模块的成熟度。

## 13. 架构反模式

- 一个巨型 `InspectionObject` 通过大量可空字段承载 PCB、钢网、SPI 和 AOI；
- 一个通用 `Defect` 或 `Result` 状态覆盖所有工序且没有领域和定义引用；
- 共享平台直接引用 SPI/AOI 页面、ViewModel 或阈值；
- 用复制 DLL、复制数据库表或复制后台线程制造“独立模块”；
- 用产品配置隐藏菜单，但底层仍加载和暴露不适用的领域能力；
- 用 AI 置信度替代量测有效性、人工复判或质量放行；
- 用连接成功、文件生成、截图、Mock、Simulator 或单测冒充设备应用、真实计量或生产验收；
- 为了追求复用，把专业页面改成参数过多、术语混杂、操作员无法快速恢复的万能页面；
- 共享模块升级没有调用者分析、消费者回归、版本迁移和回滚路径。
- 把模态差异藏在算法内部，使遮挡、镜面、解缠失败无法进入有效性、适用域与不确定度；
- 多轨机型用全局运行变量或无范围的状态写入实现并发，串改另一轨事实或授权；共享运动/安全/质量故障仍须按第 3.14.2 节传播，必要的资源仲裁不属于此反模式；
- 用上游握手消息或 MES 传入的板号直接充当本机身份权威，冲突时按“最新覆盖”解决；
- 把拼板坏板标记、未检单元或抽样未覆盖单元在统计中折算为合格；
- 允许操作员以勾选恢复点检失败、资格失效或防错不匹配的能力；
- 以通过率为目标做参数自动整定，或用生产结果自动回调生产阈值；
- 在返修工位直接修改原始事实或机判，而不是建立新的尝试与替代范围；
- 以“相关性分析结论”直接改写判定、放行或质量结论；
- 以未做属性一致性分析的复判结论作为误报率、召回率的依据；
- 未经用途批准和相应不确定度/资格验证就用有损压缩证据再测量，或在规定保留期/保护范围内因存储成本淘汰放行必需证据；
- 为单一客户拉产品分支，而不是落在配置、策略资产、插件或可关闭模块中；
- 把语言集、单位制与报告模板硬编码进页面，使新增交付区域必须改代码；
- 声称符合某标准或某追溯等级，却无法给出被采用的版本、类别、条款与逐条证据；
- 以远程服务通道绕过本地权限、资格或安全边界。

## 14. 架构冻结与实施门槛

本架构的质量标准不是层数更多、项目更多或功能清单更长，而是关键行为都具备明确的语义、唯一的权威、可验证的契约、可恢复的运行路径和可追溯的证据。任何产品在缺少这些条件时，都不能仅凭页面完成或算法运行宣称成熟。

### 14.1 架构的八项硬标准

| 标准 | 必须达到的状态 |
|---|---|
| 领域完整性 | PCB、钢网、SPI、AOI、质量管控分别拥有清晰对象、规则、状态和专业工作区；跨域只通过批准契约和事件关联 |
| 契约确定性 | 输入、输出、单位、版本、错误、取消、超时、幂等、权限、资源和兼容窗口均可机器验证；禁止 `latest`、隐式默认和字符串绕过 |
| 计量可信度 | 每个生产量测都能回溯采集、坐标、适用的标定/基准或参考面、质量、不确定度与方法资格；MSA/GR&R 等研究按被测量和方法选用，不适用项有理由，不能给不需要参考面的 2D 测量虚构参考面 |
| 执行确定性 | Pipeline、Measurement、Rule、Decision、Commit、Review 和设备回执各自拥有边界；重试、断电、乱序、迟到和回放不会重复或覆盖生产事实 |
| 工业韧性 | 设备、网络、磁盘、GPU、光源、运动、数据库和外部系统异常都有失败安全状态、恢复入口、超时边界和审计记录 |
| 产品专业性 | 每个产品使用独立 WPF 工作区、对象术语、操作路径、权限和验收矩阵；共享控件不改变专业任务流 |
| 智能可控性 | AI 绑定数据、模型、输入、版本、置信度、拒识、解释、资源、回退和人工责任；AI 不覆盖量测、机判、复判或安全动作 |
| 持续演进性 | 共享能力可独立版本化、兼容验证、迁移、回滚和并行运行；模块升级有真实消费者影响分析和可回退发布方案 |

### 14.2 目标架构

```text
产品与工艺工程
  Product / NPI / CAD / Program / Library
        ↓ 已审批的版本化运行清单
专业检测产品
  PCBInspectionProduct
    ├─ Rigid PCB / Fabrication domain
    ├─ HDIInspection domain
    ├─ FlexInspection domain
    └─ RigidFlexInspection domain
  StencilProduct
  SPIProduct
  AOIProduct
        ↓ 领域 Pipeline
确定性视觉与计量
  Acquisition / Coordinate / Calibration / 3D / Measurement
        ↓ 固定证据与质量状态
判定与生产闭环
  Rule / Decision / Commit / Review / Disposition / Route
        ↓ 已提交事实与质量事件
跨工序质量体系
  QualityControlProduct：Traceability / SPC / Correlation / NCR-CAPA / Effectiveness
        ↘ 受控 AI：Replay → Shadow → Advice → Automatic

横向基础能力：
  WPF UI / Security / Audit / Observability / Storage / Runtime / Plugin / Deployment
```

横向基础设施不定义产品领域事实的业务语义，也不自行生成质量结论；DataService 仍按批准契约承担 CommitOwner，所属 ReviewService 仍承担既定复判事务，不能因其部署在公共进程就取消其明确的应用职责。QualityControlProduct 消费已提交事实及受控质量命令，不必经过设备采集/计量 Pipeline。任何产品领域都不得绕过权限、审计、资源、版本和提交边界。

### 14.3 必须冻结的核心不变量

后续 Contract、代码和测试必须保持以下不变量：

1. 一个业务事实只有一个权威生产者和一个权威状态来源；
2. 历史事实只追加，不被新配方、新算法、新模型或当前标定覆盖；
3. 未通过本任务必需的身份、版本、能力及适用计量资格检查的运行绑定不能进入生产；非计量任务不伪造资格，须按批准范围声明不适用；
4. `INVALID`、`NOT_EXECUTED`、`UNKNOWN` 和 `BLOCKED` 不能静默转换为 `PASS`；
5. AI 建议、影子结果和回放结果不能写入生产量测、机判、复判、SPC 或设备命令；
6. 取消、超时、崩溃和重启后，必须确认后台/原生调用终结或完成进程隔离，再归还其资源；未确认的设备动作与租约保持隔离并回读恢复，不得因调用方超时就释放正在使用的缓冲或重复发命令；
7. UI 只能发起经过权限检查的命令，不能直接修改领域事实、设备安全状态或数据库内部表；
8. 共享模块的升级必须可识别受影响消费者，并在兼容验证失败时保持旧版本或安全阻断；
9. 每个生产结果必须能沿产品、板、目标、证据、量测、规则、判定和处置链回放；
10. 任何无法证明的结果进入 `Unknown/Blocked/NotQualified`，不得用推测补齐；
11. 原始身份观察、解析回执与运行绑定可分别追溯；未知/冲突可留证，正常生产与放行不得绕过身份门禁；
12. 参考真值有方法、范围、版本和不确定性，复判、客户反馈与 AI 标签不能未经验证进入性能验收分母；
13. 法定适用义务、合同采用、实施证据与认证/评定结论分开登记，任何一项存在不自动证明其余项成立。

### 14.4 从 DocMapped 到可实施架构

架构批准回答“哪一版、哪个范围由谁批准成为实施约束”，实施成熟度回答“对应契约、代码与验证到了哪一步”。下表分别记录这些维度，不是一个对象共用的状态机，不能用一个“完成”字段互相推导：

| 状态维度 | 记录对象与判定边界 |
|---|---|
| 架构批准 | 文件头显示该精确版本的批准投影；当前待批准。批准状态取自第 14.13 节既有决策/批准记录，文档修订与审核结论不自动冻结基线 |
| 契约成熟度 | 按第 14.6 节登记 ContractCandidate、Schema/Validator/Consumer/Test 与 Contracted；通过不代表产品实现完成 |
| 模块开发成熟度 | ImplementationReady、Implemented、Tested 分别依赖开发准备、真实代码和验证证据；不替代目标设备或客户门禁 |
| 产品/生产资格 | 按对应资格资产记录设备/产品/站点/版本范围、批准、有效期及暂停/撤销；HIL、FAT/SAT 和 ProductionAccepted 分别保留依据 |

以上维度引用已有状态资产，不新增统一枚举。架构批准复用 `DOC-GOV-003` 的状态及证据规则；“待批准、已批准、已替代”只是文档显示，不新建 `ArchitectureApproved` 运行时状态机。架构获批后，其新增实施范围仍可处于 `DocMapped`，已完成的 AOI 模块也可以继续保留自身 Tested/Integrated 等证据；任何一个状态都不能代替另一个。资格撤销时历史 Tested 证据仍保留，但受影响生产能力立即不可用；契约改版时，旧版的生产资格也不能自动转移到新版。

| 阶段 | 必须完成 | 进入条件 |
|---|---|---|
| `DocMapped` | 产品族、领域边界、平台分层、核心流程和架构不变量 | 本文新增/扩展范围当前映射状态；不是架构批准状态或全部模块的总状态 |
| `Contracted` | 核心 Schema、状态机、错误码、权限、资源和兼容规则；生成器/校验器可读取 | Contract 评审通过 |
| `ImplementationReady` | 真实 caller/consumer、允许/禁止路径、UI 操作、性能预算、测试和外部门禁冻结 | 模块指导双轮审核通过 |
| `Implemented` | 真实产品代码、契约绑定、失败/恢复和资源释放完成 | 定向验证通过 |
| `Tested` | 契约、回放、并发、UI、性能、故障和安全测试有可复现证据 | 测试证据完整 |
| `HIL` | 目标设备、真实图像/3D、标定、通信和资源行为通过 | HIL 证据通过 |
| `Integrated` | 主线装配、真实消费者、版本清单与受影响集成门禁闭合 | 现有交付 Manifest 与集成证据可解析；不自动授予生产资格 |
| `ProductionAccepted` | 计量、MSA/GR&R、FAT/SAT、长稳、现场操作和质量签署完成 | 生产资格批准 |

成熟度只能按相应证据提升，不能通过补充说明、截图、Mock、Simulator 或单元测试跨级。软件集成与 HIL 可按冻结依赖并行推进；产品正式放行要求适用门禁全部通过，不把表格顺序强制成纯软件模块也必须先完成 HIL 才能集成。适用维度引用 [逐功能链路闭环审计与证据维护标准](../../docs/40-development/00-standards/逐功能链路闭环审计与证据维护标准.md) 的 SoftwareClosed、ProductClosed 与 ProductionQualified，明确真实 Consumer、外部依赖和有理由的 NotApplicable，不增设另一套交付状态。

架构批准时，尚未关闭的工程与生产门禁须按适用范围引用既有记录；风险登记只说明潜在问题，不能代替门禁关闭证据。以下为集中核对索引，不是新门禁目录或动态进度表。当前状态从既有决策、模块交付 Manifest 和资格资产读取；本文未核实某项证据时不得默认通过，也不得据此把既有已通过项改为 Pending。

| 适用门禁 | 权威落点与责任 | 关闭条件与未关闭影响 |
|---|---|---|
| 非 AOI 生产机判接入 | DEV-ARC-005；C-04/C-08 与既有权威 Owner | 产品作用域/Producer/Activation Owner 分工获批，契约及真实消费者回归通过；未关闭则禁用该范围生产机判 |
| PCBMetrology 资格 | 既有计量/质量资格资产；C-03 | 适用标准件、独立参考、Qualification Study 与签署齐备；未关闭则不授予相应量值、方法和适用域的生产资格 |
| SPI 3D 模态与计量资格 | 第 3.13、3.17 节及既有计量资格资产；C-03/C-06 | 目标模态、标定、适用域、不确定度及测量系统研究通过；不能由重建成功或模拟数据推导生产合格 |
| 目标机 HIL 与恢复 | 既有硬件/部署/交付证据；C-06/C-07 | 实际采集、触发、适用运动/安全联锁、IPC、故障与恢复验证签署；未关闭范围不按实机验收通过交付 |
| CFX/Hermes 互操作 | 第 3.14 节及既有工厂互联证据；C-06/C-08 | 对实际采用的设备、协议版本和消息集完成正常/异常/重连互操作；不适用产品有批准理由，不要求所有离线产品实现 |
| 产品生产验收 | 既有产品/客户资格与交付 Manifest；产品、质量和交付 Owner | 适用计量、性能、长稳、FAT/SAT 与现场签署通过；架构批准不解除其未关闭限制 |

每项未关闭记录须能定位范围、实名 Owner、所需关闭证据、下一动作和允许开发范围；第 14.13 节的架构批准记录引用这些既有门禁。无关软件工作可继续；受影响生产启用仍按原门禁执行，不能用总体架构批准一次性豁免。

### 14.5 第一条实施主线

后续实现必须先形成一个真实、可回放、可追溯的 SPI 纵向闭环：

```text
ProductRevision
  → InspectionProgram / Recipe
  → EffectiveRuntimeManifest
  → 定位与采集
  → 3D 重建与坐标/标定检查
  → 参考面与锡膏分割
  → 高度/面积/体积/偏移 MeasurementSet
  → CoverageResult / InspectionFact
  → RuleEvaluation / InspectionDecision
  → Decisioning / MachineDecision
  → EvidenceCommit / ResultCommitReceipt
      ├→ 必要复判 / RouteAssessment
      │   → FinalDisposition / DispositionCommitReceipt / RouteAuthorization
      │   → MotionGateway / BoardExitAck（在线实体搬送）
      └→ 追溯、SPC 和回放
```

这条主线的交付优先级高于 AI、跨工序关联和更多产品扩展；软件先关闭身份、版本、状态、错误、恢复、权限、资源、UI 和证据契约，生产启用前再关闭适用的实机、计量和现场门禁。外部证据缺失时保持受影响生产能力关闭，继续不依赖该证据的软件和文档工作。上图展示成功依赖，覆盖/量测失败仍须提交真实失败与缺口；结果提交后才能复判或评价。已提交结果可立即进入追溯、适用统计和回放，处置/交接相关指标才等待各自回执。涉及搬送的运行只有实际交接确认后才可显示完成，离线/人工路径遵守其批准的保管与结束条件。

对 PCB 制造和 PCBA 装配的完整平台，主线必须由产品的 `ProcessRouteRevision` 选择具体工位链，而不是假定所有产品都经过同一条路线。硬板、软板/FPC、刚柔结合板和 HDI 可以选择不同的内层、积层、微孔、覆盖膜、印刷、贴装、焊接、AXI/ICT/FCT 和最终检验工位；每个工位都必须对自己的目标、检测方法、可观察范围和证据要求负责。

### 14.6 现有工程资产与架构权威绑定

本架构必须由可执行资产承载。本文只定义系统级关系；字段、枚举、校验和实现入口必须绑定到以下现有权威，禁止在产品或 `spi/` 目录中复制第二套定义：

| 架构主题 | 唯一权威资产 | 必须形成的实现闭环 |
|---|---|---|
| 配方生命周期、BoardRun、机判、复判和处置 | `docs/40-development/00-standards/权威状态角色消息与判定所有权规范.md`（`DEV-ARC-005`） | 状态转换、Owner、CAS、Receipt、禁止组合和投影验证一致 |
| 公共身份与跨站事件 | `contracts/v1/schema/events-catalog.schema.json`、`contracts/v1/catalog/events.v1.json`、`contracts/v1/schema/cross-module-flow-registry.schema.json` | C-01 负责通用 Envelope、AuthorityScope、实体/事件身份及时间域；时钟与预算沿用 DEV-ARC-005；C-08 负责跨站载荷、兼容、去重、乱序、断点续传和回执；不建立第二套 Event Schema |
| Recipe/Runtime Manifest | `contracts/v1/schema/recipe-manifest.schema.json`、`docs/40-development/20-product/配方版本审批发布开发指导.md` | Schema、签名、设备组、模型/库/标定引用、发布和回滚均使用精确 `id + version + sha256`；运行输入集合复用 runtime.proto 的解析绑定与回执 |
| NPI/Program 与制造参考 | `contracts/v1/schema/npi-programming-bundle.schema.json`、`docs/40-development/20-product/NPI三分钟快速编程开发指导.md`、`docs/40-development/20-product/BoardDataAdapter开发指导.md` | Gerber/ODB++/IPC-2581/Excellon 等输入经 BoardDataAdapter 形成验证后的标准化模型与版本化制造几何快照；NPI 协调既有领域/规划能力，依据任务和设备能力生成目标集、覆盖及路线候选，不把规划职责下放到导入适配器。输入集、库快照、能力、标定、覆盖报告、首板验证和未决任务可回放 |
| Evidence/Result Commit | `contracts/v1/schema/evidence-manifest.schema.json`、`docs/40-development/60-data/数据服务与证据追溯开发指导.md` | CAS 对象、Evidence Manifest、MachineDecision、Commit Receipt、Outbox 和回读组成一个可验证闭环 |
| 坐标/拼接/多 FOV | `docs/40-development/00-standards/坐标系统与数值黄金样例开发指导.md`、`contracts/v1/schema/coordinate-golden.schema.json`、`position-transform-artifact.schema.json`、`stitch-*.schema.json` | 方向、版本、有效域、残差、标定来源、全局坐标和拼接质量可重算 |
| 计量与资格 | `docs/40-development/40-vision/标定与计量开发指导.md`、`docs/40-development/41-vision-platform/01-foundation/通用计量引擎开发指导.md`、`metrology-reference-certificate.schema.json` | 标准件、Bias/Linearity/Stability、Repeatability/Reproducibility、MSA/GR&R、跨机和有效期形成资格链；PCB 专业测量按第 2.11 节引用同一计量/坐标/验收权威，不复制量测与判定 |
| 流水线/性能/背压 | `docs/40-development/00-standards/性能预算与并发流水线开发指导.md`、`contracts/v1/schema/performance-profile.schema.json` | 板/Panel 与连续卷料分别使用适用 Profile；真实 Profile、DAG 关键路径、资源预留、有界队列、取消和五终结路径均有证据 |
| WPF 页面与渲染 | `docs/40-development/10-ui/全页面PageContract与高保真交互规格.md`、`contracts/v1/catalog/ui-pages.v1.json`、`ui-application-ports-catalog.schema.json` | Query/Command、权限、八态、AutomationId、键盘、DPI、三语、UIA 和真实 WPF 验收一致 |
| 部署与本机隔离 | `docs/40-development/70-operations/Supervisor部署拓扑与本机安全开发指导.md`、`deployment-manifest.schema.json`、`machine-config.schema.json` | 进程 Owner、服务账号、IPC、签名、启动顺序、升级、恢复和安全权限可验证；灾备沿用维护健康备份升级指导及 DEV-DAT-002，RPO/RTO、密钥和恢复演练按故障范围验收 |
| 插件与扩展 | `contracts/v1/schema/plugin-manifest.schema.json`、插件 SDK 指导 | 能力、依赖、权限、资源、兼容版本、签名和卸载后的 `NotReady` 行为可验证 |
| 质量、SPC 和安全 | `acceptance-profile.schema.json`、`defect-taxonomy.schema.json`、`spc-control-rule-catalog.schema.json`、`security-control-catalog.schema.json` | 质量规则、统计分母、权限、审计、脱敏和发布门禁不依赖页面判断；Canonical Profile 引用 DEV-ARC-005 第 10 节及对象 Schema，格式/算法演进与签名互验有黄金向量 |

产品路线、工位和覆盖的权威分工固定为：`ProductProfile` 负责产品允许的板型/材料/生产形态和能力范围；`ProcessRouteRevision` 负责路线及 `RouteStep[]`；`InspectionProgram` 负责每个步骤检查的对象和项目；`InspectionCoverageSpec` 负责目标、范围、检测方法、观察条件和覆盖要求；`EffectiveRuntimeManifest` 负责本次运行的精确冻结引用；`RequiredEvidenceSet` 负责放行所需的已提交事实和外部测试结果。上述名称在正式进入 Contract 前只是架构语义，不能在 `spi/` 或产品内重复创建平行 Schema；正式字段必须登记到现有契约目录并绑定 Owner、消费者、Validator 和测试集合。

在进入 `Contracted` 前，新增语义必须在现有契约目录中登记以下最小信息，不要求一次性创建所有 Schema 文件。优先复用已有字段、引用、解析视图和消费者；增加字段或持久化对象须对应一个已确认的问题、真实消费者与可验收行为，不能因为架构中出现一个英文名就新建契约：

每个 `ContractCandidate` 至少登记：`ContractId`、`SchemaId`、`SchemaMajor`、`Owner`、`BackupOwner`、`Producer`、`Validator`、`Consumer[]`、`AuthoritySource`、`AuthorityScope`、`Status`、`CompatibilityPolicy`、`TestSuite`、`StateOwner`、`CommitOwner`、`QualificationOwner`、`ManifestReference` 和适用时的 `AcceptanceProfile` 引用。登记状态按以下顺序推进：

`StateOwner` 是聚合状态转换的唯一写入权威，`CommitOwner` 是事实/回执的持久化权威，`QualificationOwner` 是资格批准/撤销权威，`ManifestReference` 指定运行或交付快照中的引用位置。它们与工作包研发 Owner 不同，不要求全由同一服务承担；无状态、不提交或不签发资格的对象使用带理由的 `NotApplicable`。基础数据契约可先通过格式/语义契约测试；真实消费者闭环在相应工作包关闭前验证，不把完整产品实现当成允许开始实现的前置条件。

运行责任字段必须解析到既有服务/组件及其权限边界，不能填写 `C-01/C-04/C-08` 等研发工作包编号。`Producer` 表示语义生产者，传输外部结果的 Adapter 不因此成为 `ExternalTestFact` 的领域权威；外部来源身份由事实保留，规范化、语义验证和提交分别绑定既有责任主体。机判创建、BoardRun active 状态、复判提交、处置形成、签发和物理执行按第 3.12.2 节及 `DEV-ARC-005` 分别登记。不签发资格的机判、路线评价和处置使用带理由的 `NotApplicable`，消费资格不能被写成拥有资格。

```text
ContractCandidate
  → SchemaRegistered
  → ValidatorRegistered
  → ConsumerRegistered
  → ContractTested
  → Contracted
```

这些字段应进入现有契约目录、模块交付 Manifest 或开发准备度资产的适用登记入口；不能在总体架构文档中另建第二套机器真相。进入 `ImplementationReady` 须有获批契约、Owner、可定位的 Validator/测试入口或本切片明确的实现任务，以及真实消费场景、调用边界和负责接入的 Consumer；名称预留或假想消费者不满足要求。新消费者与验证器可在获准切片内实现，基础格式/语义契约按 Contracted 门禁先验证；完整消费者运行及失败恢复证据在工作包交付时关闭，不造成“先实现才能获准开始实现”的循环。

| 对象/能力组 | 归属与主要消费者 | 必须登记的验证重点 | 初始成熟度 |
|---|---|---|---|
| `ManufacturingGeometrySnapshot`、`SourceSetManifest`、PCB/HDI/FPC 制造参考对象 | C-02/C-03；BoardDataAdapter、各 PCB/FPC/HDI 领域 | 产品与制造参考的独立版本及批准绑定；来源、单位、层/面、稳定 ID、hash、必需/可选输入、缺失/冲突 | `ContractCandidate` |
| 多产品运行作用域、清单绑定与配置依赖闭包 | C-01/C-02；RecipeResolver、各产品 Orchestrator、回放和提交消费者 | 有类型的父子关系、实体范围、精确引用、传递依赖、配置与运行证据闭包分离；现有 AOI Schema 兼容 | `ContractCandidate` |
| `LayerStackRevision`、`BuildUpRevision`、`LaserVia`、`WebCoordinateReference`、`CorrectionModel`、非刚性/卷料坐标 | C-02/C-03；HDI、FPC/R2R 领域 | 层叠/积层/孔的引用图、模型资格与拟合实例双门禁、卷段与基准绑定、可观察范围和重启恢复 | `ContractCandidate` |
| PCBMetrology 专业计量契约与能力适用域 | C-03 计量定义/引擎、C-02 参考/要求发布、C-04 领域规则/提交、C-05 工作区、C-08 质量/路线；消费者为 PCB 编程/运行/复核与既有 SPC | 用途/命名空间、测量层级、名义/成品要求与参考点、Datum/方向、关系配对、计划与实际覆盖、采样/拟合/排除、不确定度、能力匹配/证书/资格依赖、铜环/跨 FOV 最差位置、形位支持边界与 UI 恢复；MeasurementQualificationContext 由精确引用解析，验证缺口和缓存失效；按第 2.11 节映射既有契约 | `ContractCandidate` |
| `ProcessRouteRevision`、`RouteStep`、`InspectionCoverageSpec`、`StationInstance` | C-01/C-08；产品装配和运行清单 | 路线顺序、工位实例、能力、方法、覆盖、必选项、重试和退出条件 | `ContractCandidate` |
| `QualityPlanRevision`、`RequiredEvidenceSet`、`RouteAssessmentContext` 及处置证据绑定 | C-04/C-08；QualityControl、Orchestrator、DataService | 条件/可选步骤、局部复检与事实修订、精确输入及分区水位、迟到事实、回执关联及签名兼容 | `ContractCandidate` |
| `PrintProcessContext`、`PrintAttempt`、`PrintMeasurement`、`PrintDefect`、反馈回执 | C-01～C-04、C-06～C-08；SPI、印刷机适配器、质量中心 | 尝试身份、测量/缺陷来源、提议→命令→回执→效果的闭环 | `ContractCandidate` |
| `ExternalTestCapability`、`ExternalTestAttempt`、`ExternalTestFact` | C-04/C-06/C-08；AXI/CT、ICT、FCT 适配器和质量中心 | 外部能力声明、事实来源、提交回执、冲突和不可替代性 | `ContractCandidate` |
| `SensingModality`、`IlluminationConfiguration`、模态适用域与有效掩膜 | C-03/C-06；各 2D/3D 领域与计量 | 模态属性与限制、遮挡/镜面/解缠失效标记、融合有效性、同步与预热条件 | `ContractCandidate` |
| `Lane`、`ConveyorSegment`、`BoardPosition`、`HandoffSession`、单元有效性状态 | C-01/C-06/C-07；板流、上下游协议与并发运行 | 轨道并发隔离、握手与位置证据、坏板标记来源与分母影响、异常与恢复 | `ContractCandidate` |
| 读码事实、`ProvisionalBoardId`、`RecipeMatchVerification`、换型与首件门禁 | C-01/C-02/C-05；既有 Orchestrator 身份 Owner、清单绑定与门禁界面 | 观察与裁决分离，复用 BarcodeAssignmentGraph/BarcodeIdentityPolicy/IdentityResolutionReceipt；留证、解析 CAS、临时身份、重号/合法重检区分、防错阻断、门禁失效与禁止继承、证据与审计 | 新增多产品语义为 `ContractCandidate`；既有身份契约直接引用 |
| 设备状态与原因码、绩效事实、点检定义与结果、消耗品与健康度 | C-07/C-06/C-03；MES/CFX、维护与计量 | 状态映射、分母口径、点检判据与阻断、恢复权限、远程会话审计 | `ContractCandidate` |
| `MachineMatchingArtifact`、`TransferVerification`、环境样本与门限 | C-02/C-03/C-06；多机部署与计量资格 | 移植适用域校验、匹配残差与有效期、环境越界对量测有效性的影响 | `ContractCandidate` |
| `ReworkOrder`、`RepairAction`、`ReworkVerification`、返修物料追溯 | C-04/C-08/C-05；返修工位、质量与统计 | 替代范围、缺陷/物料双链、位置与实物区别、实例/批次追溯粒度及缺口、返修/重工口径、原事实不可变 | `ContractCandidate` |
| `ModelRecord`、`DatasetSnapshot`、标注治理与回归基准集、参考真值与属性一致性研究 | C-04/C-08 与 AI/质量 Owner；算法验证、AI 服务与质量统计 | 模型档案完整性、数据授权与脱敏、参考方法与不确定性、仲裁修订、训练/调参/测试谱系隔离、统计方法与置信区间、阶段化上线证据；GroundTruthRecord 映射既有资产 | `ContractCandidate` |

上述登记只是实施前的契约工作项，不代表对象已经实现或具备生产资格。登记完成后仍须由真实消费者、语义校验、失败/恢复测试和适用的 WPF、性能、HIL 及质量门禁逐级提升成熟度。

现有目录和 Manifest 还必须能够生成一张只读的 Contract Ownership Matrix，至少包含 `Object`、`AuthorityScope`、`Owner`、`Producer`、`StateOwner`、`Schema`、`Validator`、`Consumer`、`CommitOwner`、`QualificationOwner`、`UIOwner` 和 `ManifestReference`。它是由权威资产生成的检查视图，不是新的 Owner 注册表；门禁至少检查同一 AuthorityScope/对象或重叠范围内是否有两个竞争的 Owner/Producer、同一聚合状态是否存在两个未协调的写入 Owner、一个 Schema 是否有两个权威入口、一个 Fact 是否有两个 CommitOwner、同一资格是否存在两个互相冲突的签发权威；多角色会签仍归属同一批准流程。

`AuthorityScope` 通过已有 ProductProfile、InspectionDomain、站点/设备、实体和聚合/决策/评价流身份表达，并声明适用版本及用途；不是任意文本标签或可由客户端填写的权限。Owner 解析必须拒绝零匹配、多匹配、未经授权的跨租户/站点访问及父子范围重叠冲突，不能通过改名或换一个 Profile ID 绕过同一实体的写入边界。已批准的 CrossSite 质量评价可消费其范围内多站事实，但不因此获得各设备的写入/放行权。AuthoritySource 负责批准该映射；Scope 不授予新权限，也不将工作包 Owner 变成运行服务。Schema 的权威定义仍统一，产品可拥有不重叠的运行实例。

矩阵还须校验语义 Producer 与真实调用者一致、所有生产配置依赖均进入配置闭包、所有运行事实/Artifact/回执均进入结果或证据提交闭包并绑定父清单。`ManifestReference` 必须给出实际引用路径及其类型，不能只写一个勾选值；不得要求尚未产生的运行事实预先进入发布清单。单一权威指同一聚合/身份范围的写入责任，不禁止同一组件在不同设备或产品隔离范围部署多个实例。矩阵是生成的检查视图，其生成和校验通过前不能宣称 Owner 门禁已实现。

产品开发只能引用这些权威资产；缺失的 Schema 定义、Owner 或验证规则须先经 Contract 任务明确、批准并通过适用的基础契约检查，才能进入 `ImplementationReady`。验证器实现与真实消费者的交付边界按本节前述规则登记，不能把全部运行验证完成作为开始编码的前提。权威分工固定为：架构文档负责系统关系和边界；Schema 负责数据结构；状态/角色规范负责状态和 Owner；PageContract 负责 UI 行为；开发指导负责实施语义、边界和验收；生成器负责按已批准规范生成代码或资产；Validator 负责机器校验；Test 负责验证；Manifest 负责交付快照和门禁引用。生成器、Validator 和测试不能反向定义需求正确性。

发现不一致时，禁止调用方局部兼容或自行选择：先阻止发布，依据冲突主题指定唯一权威 Owner，修订权威源，重新生成/校验，再对真实消费者回归；若冲突跨越多个权威源，由架构 Owner 组织决策并在相关权威源中同步版本。哈希只能证明内容一致，不能赋予批准、授权或生产资格。

### 14.7 核心运行时契约

设备产品内新产生的视觉检测结果采用以下提交与实体交接链；质量查询、工程回放、外部测试接入和不涉及实体运动的操作只执行其适用边界，不虚构视觉量测或出板步骤。外部事实沿第 2.10 节经规范化和提交后进入路线评价：

```text
Request
  → Identity/Authorization/Capability/Calibration validation
  → Immutable Runtime Snapshot
  → Bounded Operation
  → Evidence and Measurement staging
  → CoverageResult
  → InspectionFact
  → RuleEvaluation
  → InspectionDecision
  → Decisioning
  → MachineDecision revision
  → EvidenceCommit
  → Durable ResultCommitReceipt
  → ReviewClaim / ReviewDecision 及其回执（需要时）
  → RouteAssessment
  → Orchestrator FinalDisposition / DecisionActivationProof
  → DataService DispositionCommitReceipt / RouteAuthorization
  → MotionGateway / BoardExitAck
```

结果提交回执与处置提交回执不可互换。[现有 data.proto](../../contracts/v1/proto/data.proto) 中，`ResultCommitReceipt` 绑定结果 revision、MachineDecision ID/revision、结果及证据清单 hash；`DispositionCommitReceipt` 绑定单个本机 `result_commit_receipt_id`、同一机判 revision、处置 ID/hash 和授权。此 v1 结构不是跨站结果回执数组，也未包含完整路线评价上下文；多产品扩展前不能将它宣称为已具备跨站处置追溯能力。

C-04/C-08 的处置证据绑定必须形成以下不可变关系：本机 ResultCommitReceipt → 精确 MachineDecision revision；RouteAssessmentContext → 所采用的本机/跨站结果、复判、覆盖、资格及 RequiredEvidenceSet；FinalDisposition → 精确评价上下文、处置政策及机判；DispositionCommitReceipt → 该处置与本机结果回执；RouteAuthorization → 该处置回执/hash及动作范围。跨站结果集合由评价上下文精确引用，不能用另一站的回执替换本机提交锚点，也不能只按实体号查询“最新评价”。

新增评价引用必须进入获批的处置内容及其受签名 hash 保护的投影，处置事务须校验评价已提交、依赖齐全、输入属于该实体/路线且与 active revision 一致。若当前 wire/安全投影不能表达，由同一工作包同步演进 Schema、Proto、canonical 投影、签名域/版本、验证器和消费者；严格字段集的 v1 不得直接追加字段或用未保护附件绕过绑定。旧协议继续按已批准 AOI 范围运行，新产品要求无法表达时阻断其准入；不以降级丢弃上下文换取兼容。

Orchestrator 在串行 BoardRun actor 内校验评价输入仍适用于 active 机判，锁定处置并签发绑定精确内容的一次性证明。DataService 验证证明中的状态/activationVersion、结果回执、处置 hash、评价引用与政策版本并原子兑换，不直接读写 Orchestrator 内部状态表；校验及持久化回执/Outbox/授权沿用既有本机事务，不引入跨站分布式出板事务。评价读取版本与处置门闩版本按已批准状态转换关联，不能要求两个阶段的版本数值机械相等。未授权版本变化、证明已兑换、撤销、回执冲突或依赖未提交均不得重新签发另一动作；同键同载荷已提交返回原回执，超时先查原提交结果。验收必须覆盖评价仍引用机判 revision 4 而本机结果回执绑定机判 revision 5、评价后迟到输入、同幂等键异载荷、签名投影篡改、旧消费者拒绝新安全版本及授权一次性执行。

有副作用、跨进程或持久化状态的 Operation 必须按既有 Envelope 携带 `operationId`、`correlationId`、`causationId`、`boardRunId`/实体身份、输入快照 hash、schema major、producer epoch、state version、权限快照、幂等键、deadline 和取消来源，并声明 `OperationKind` 与 `SideEffectClass`。这里使用概念名称，wire 字段沿用 `DEV-ARC-005`，不能另建字段别名；只读查询和纯内存操作仅携带适用的追踪、权限及预算，不强制空幂等键或伪造 state version。基础分类为：

| OperationKind / SideEffectClass | 典型操作 | 超时、取消或未知时的处理 |
|---|---|---|
| `ReadOnly` | 查询、能力读取 | 可安全重试或重新查询，不产生生产事实 |
| `ComputeOnly` | 回放、算法计算、候选生成 | 按 `CalculationIdentity` 重算或丢弃候选，不提交生产事实 |
| `EvidenceWrite` | 原始/派生证据落盘 | 按证据键查询写入结果，校验完整性后继续或补偿 |
| `FactCommit` | 量测、机判、结果回执提交 | 先按 `CommitIdentity` 查询；已提交返回原 Receipt，确定未提交则以同键同载荷恢复提交，冲突拒绝；不重新判定或量测 |
| `DeviceCommand` | 采集、暂停、放行、路由命令 | 必须回读设备状态和 epoch；未知时进入人工确认/安全恢复 |
| `QualityEvent` | NCR、CAPA、HoldRequest | 查询服务端回执和应用效果，不能仅凭发送成功显示生效 |

响应须区分请求受理、执行进度、服务端终态与调用方当前是否知道结果，沿用 [进程通信与错误模型开发指导](../../docs/40-development/00-standards/进程通信与错误模型开发指导.md)。长任务可先返回受理回执和 operation 身份，再经已有状态查询/事件流报告排队、运行与最终结果；受理不等于完成。`Completed`、`Failed`、`Cancelled`、`TimedOut`、`Unknown`、`Rejected` 在本文只是语义类别，须映射该操作的权威契约，不能据此创建新的通用枚举。调用方超时/断连只表示尚未取得结果，不能把服务端已完成状态回写成 TimedOut，也不能把 Unknown 当终结并释放仍占用的设备/原生资源。取消请求须取得服务端确认及副作用处置结果；响应丢失后按原操作身份查询，完成事实不因客户端重新连接或退出页面而改变。

所有外部副作用遵循：

```text
应用请求 → 入口认证/形状检查 → Operation 幂等查询或预留
  → 新操作的聚合/CAS及当前前置检查 → 资源租约 → 执行/回读
  → durable receipt → 投影
```

只有收到与实体、版本、序列和 hash 匹配的 receipt，才能把操作显示为完成或允许下游推进。对于设备命令，还必须满足设备回读和设备 epoch 检查；对于权限、撤销、资格或安全状态可能变化的副作用，快照固定后仍须在执行边界复查，防止 TOCTOU。UI、MES、AI、质量中心和导出任务均不能通过文件存在、网络连通、按钮返回或本地缓存推断生产操作成功。

幂等查询沿 DEV-ARC-003 先于可变聚合的当前 CAS 检查。同键同载荷已提交时，按当前读取权限返回原 Operation/回执，不因聚合版本前进而拒绝原结果查询，也不再检查旧动作是否仍可重新执行；重复请求遇到 Pending 只允许查询、等待或订阅，不能再发一个设备动作。新 reservation 才进入聚合快照和当前前置检查。已受理操作的执行或崩溃恢复由其唯一 Owner 沿原身份、日志与批准恢复协议推进，不因查询 Pending 另起执行；恢复前核实提交及副作用边界，未知设备动作不得重发。同键异载荷拒绝；业务请求摘要不包含新 messageId、重试发送时间或剩余预算。回执读取不恢复已撤销授权，事件重放也不授权重复动作。验收覆盖提交成功但响应丢失后聚合已前进、权限撤销后的受控查询、Pending 重复请求与 Owner 恢复、超时后的已完成结果及旧令牌被再次执行的拒绝。

#### 14.7.1 版本、修订与不可变引用关系

Fact、Result、MachineDecision、Assessment 的 revision 是各自身份范围内的版本，彼此不要求数值相等，也不能共用一个字段。关系是精确引用图，不是每个上游变更都自动推进全部下游；所有生产追加仍需权限、适用状态和对应提交协议。领域事实、机判引用和结果集合仍沿用既有 Result 事务提交，矩阵不要求每一行新增独立事务或持久化服务。

| 对象/版本域 | 谁可产生或推进 | 精确依赖与修订约束 |
|---|---|---|
| InspectionFact ID/revision | 其 AuthorityScope 内的领域事实 Producer 提议，由已登记 CommitOwner 校验提交 | 绑定来源 Attempt、MeasurementSet/CoverageResult 和证据；纠错追加前版关系，重检另建 Attempt/事实，人工复判不能改原事实 |
| MachineDecision ID/revision | 唯一 Decisioning Producer 创建；DataService 提交其不可变引用 | 固定输入集合、策略、运行绑定及领域提议；合法重检/显式重评才追加，Fact 变化不自动重写旧机判 |
| Result revision / ResultCommitReceipt | 经授权调用方按现有 Begin/Finalize 协议提出该运行的结果 revision，DataService 约束唯一性并签发回执 | 原子绑定结果/证据清单和具体机判；同键同 hash 重试返回原 session/receipt，查询/上传次数不增加 revision |
| BoardRun stateVersion / activationVersion | Orchestrator 串行聚合 | 是 active 指针及处置门闩的并发版本，不是内容 revision；引用已提交机判/结果，切换不修改旧内容 |
| ReviewDecision / 提交回执 | DataService 内 ReviewService 按 Claim/权限/预期版本提交 | 绑定被复核的精确事实/机判与范围；不修订量测或替代机判 revision，冲突仲裁走既有复判流程 |
| RouteAssessment ID/revision | 该评价 Scope 内唯一 Producer，经登记提交边界持久化 | 固定 Context、事实选择政策、RequiredEvidenceSet 和输入水位；新输入产生新评价或质量事件，旧评价仍可回放 |
| FinalDisposition ID/hash / DispositionCommitReceipt | Orchestrator 形成，DataService 验证证明后原子提交并签发回执 | 引用本机结果、机判、复判、评价及政策；现有 v1 使用 dispositionId/hash，不凭空添加 DispositionRevision。已提交内容不可覆盖，后续处置只能走批准的状态/新操作边界 |
| RouteAuthorization ID / 一次性兑换 | DataService 签发，MotionGateway 验证兑换并记录执行回执 | 绑定处置回执/hash、目标、位置/PLC版本、boot、有效期与 nonce；现有 v1 不含 AuthorizationRevision。重复请求返回原处理结果，不以刷新版本/TTL重新执行 |

`Supersedes` 只表示批准的事实纠错或指定范围替代关系，不授予删除旧记录、跨 Attempt 整板替代或回滚已执行动作的权力。机判 revision 5 可以被评价 revision 12 引用，校验的是输入绑定而非数字相等；评价仍引用机判 4 却用于机判 5 的处置才是错误。事实更正后，影响分析必须识别相关机判、评价、统计和在途处置：未锁定的运行走批准重评，已提交/出站的运行形成质量事件和可追踪修正投影，不能默默把历史报告变成新结果。

#### 14.7.2 设备接收、应用、回读与工艺效果

命令生命周期、设备实际状态、参数回读和工艺效果是不同事实维度，沿用既有 Operation/DeviceCommand/SPI Feedback 契约，不新建所有设备共用的长状态枚举。每类命令在批准策略中明确哪些证据必需、何时算命令完成、何时仍需等待效果及未知状态如何恢复。

| 证据阶段 | 能证明什么 | 不能推导什么 |
|---|---|---|
| Requested/Validated/Dispatched | 请求已登记、前置条件检查或传输已发起 | 设备已接收或动作已完成 |
| DeviceAccepted / 协议 ACK | 设备或协议栈按明确映射接受了命令 | Applied、实体交接或工艺改善；普通网络 ACK 甚至不能证明设备应用已接收 |
| Applied / 实际执行回执 | 经设备明确应用状态或与命令对应的回读/传感器证据确认实际应用 | 参数符合预期或质量效果已达标 |
| ReadBackVerified | 实际值/状态与目标及允许容差相符，证据绑定设备 epoch、命令和适用板/卷段边界 | 未来板的质量已经改善；单纯“当前值相同”不证明该命令刚执行 |
| EffectObservation | 在规定后续样本/时间窗内观察到效果，含指标、资格、样本范围和混杂条件 | 自动证明因果关系、修改原量测/机判或追加未经批准的设备动作 |

例如印刷机 ACK 后仍需确认实际参数及生效印刷尝试，后续样本按预先批准的观察窗口与纳入规则进入效果观察。有效事实包含 PASS 与 NG；未知、无效和排除项单列并说明影响，不能以产品合格作为纳入条件。输送动作必须以对应传感器/BoardExitAck 确认实体交接。无回读能力时须声明协议可证明的边界，不能虚构 ReadBackVerified；命令已应用但效果不足/未知应分别显示，不把已执行动作标为未执行并重发。超时、断连或重启后的恢复先查询原操作和实际状态，无法证明则 Unknown/受控恢复；UI 显示“已发送、设备已接收、已应用、回读不符、效果待评估”等所处事实及下一动作，底层错误码和翻译仍沿用权威目录。

### 14.8 产品间隔离与升级策略

AOI、SPI、钢网和 PCB 产品共享平台版本时，必须分别拥有 `ProductProfile`、能力清单、Schema 兼容范围、安装包、配置根、日志/数据策略和验收矩阵。产品入口可共享 WPF Shell 基础设施，但产品菜单、页面、权限、对象、运行状态和错误码必须由领域装配决定。

共享能力变更采用以下顺序：

```text
影响分析 → 契约兼容检查 → 真实消费者构建/测试
→ 迁移与回读验证 → 并行/灰度部署 → 现场回退演练 → 发布
```

数据库和持久化契约采用 expand/contract 与兼容窗口；旧版本只能读取经过验证的兼容数据，不能用旧备份覆盖已经产生的新生产事实。模型、标定、库、插件、Recipe 和软件均按精确版本/hash绑定，禁止通过 `latest`、Champion 别名或隐式降级切换运行语义。产品包声明共享平台兼容范围，部署实例锁定精确版本；配方、标定、模型、插件和工程库对象必须在安装、装载、运行准入及升级后验证签名、哈希、适用域、版本和撤销状态。

### 14.9 架构的量化验收维度

每个产品和共享能力按实际责任引用批准的资格/性能/验收 Profile；需要签名的发布资产按其权威规则签名，不为每个小型库新建一份万能 Profile。下列维度须分别给出可测目标、责任资产和证据，或经批准的 `NotApplicable` 理由：

| 维度 | 必须测量或证明 |
|---|---|
| 质量 | 缺陷召回、误报、漏检、逃逸、未知/无效比例、覆盖率、分层最差值；参考真值按第 7.8.1 节核验，明确分母与样本量，能力推断/验收附适用的置信区间（第 7.8.3 节） |
| 计量 | Bias、Linearity、Stability、Repeatability、Reproducibility、MSA/GR&R、不确定度及跨机偏差/一致性；高相关性不能证明两机测值一致 |
| 判定一致性 | 属性一致性分析（判定者内/间、人机一致性）、复判抽检与仲裁结果（第 7.8.2 节） |
| 性能 | 板级 CT、阶段 P50/P95/P99、队列等待、UI 响应、资源峰值、长稳斜率 |
| 可靠性 | 断电、重启、服务崩溃、设备断连、磁盘满、网络中断、恢复时间和数据完整性 |
| 可用性 | 首次任务时间、点击/按键数、误操作率、恢复成功率、键盘/UIA、DPI，以及按 `SupportedLocaleSet` 的语言/区域矩阵（第 8.6 节，三语为最小基线） |
| 安全 | 权限拒绝、重认证、签名/篡改、证书、插件/模型/Recipe替换、审计完整性 |
| 演进 | Schema兼容、迁移、回读、并行版本、消费者回归、回退和撤销 |

专业验收应按检测族分别定义指标集合：客户缺陷验收归入现有 AcceptanceProfile，计量、硬件和性能研究分别归入既有计量/硬件资格/PerformanceProfile，并由产品验收精确引用；不向一个 Schema 填入全部指标。以下是必须分配到上述权威资产的指标，具体数字由真实设备、样板、挑战集和 Qualification Study 确定，未冻结前保持 `PendingProfile`：

| 检测族 | 专项指标 |
|---|---|
| PCB Pattern | 缺陷召回、误报、最小特征尺寸、层间/图形对位、线宽量测、覆盖率 |
| PCBMetrology | 逐量值/方法/尺度的 Bias、Linearity、Stability、Repeatability/Reproducibility、U/k 与适用域；铜环/局部缩颈最差值、跨 FOV/边角/接缝一致性、全局尺度、用途/层级隔离、关系配对与参考点、计划/实际覆盖、能力匹配及资格依赖与验收边界；数值见批准 Profile |
| HDI Laser Via | 微孔位置、直径、圆度、层间对位、重复性、缺陷召回和量测有效性 |
| FPC/R2R | Web 位置、编码器同步、LineRate、卷料坐标、局部形变残差和缺陷定位准确度 |
| SPI | 体积、高度、面积、XY 偏移、重复性和 GR&R |
| PCBA AOI（炉前/炉后） | 按实际工序可观察的元件/引脚/焊点/字符缺陷族，分封装/尺度/表面的召回、误报、拒识和覆盖；3D 量测及共面性仅在方法具备资格时验收，炉前外观不能证明炉后焊接质量 |
| 钢网检查 | 开口尺寸/位置/堵塞/损伤的覆盖与检出、适用厚度/形貌量测的不确定度；张力等独立测量按对应能力验证，不由开口图像外推 |
| 跨工序质量管控 | 实体/尝试配对准确性、事实/回执完整性、更新水位与查询时效、缺口/迟到可见性、Hold交接、统计可重算、权限隔离和报告可回放；不虚构设备计量资格 |

所有指标必须绑定产品、设备、软件、Schema、Profile、数据集和证据 hash；总体平均值不能掩盖关键缺陷族、关键量测、关键角色或最差分层失败。没有真实数据、目标机或专业签署时，状态保持 `Pending`、`Blocked` 或 `NotQualified`。

### 14.10 文档完成标准

本文取得精确版本的架构批准前，应满足以下文档条件；每个条件都应能指向既有权威或有 Owner 的待落地切片，不能把未来实现尚未完成当作文档永远无法审定的理由。是否批准与 DocMapped 等实施成熟度分别记录：

1. 产品边界、领域对象、共享能力和唯一权威已经冻结；
2. 核心 Contract 有唯一权威入口、明确资产集合、Owner、消费者和兼容策略；
3. 每条生产链有状态、错误、恢复、权限、资源、证据和回执闭环；
4. 视觉/计量、WPF UI、部署、安全、AI 和质量均有下层指导文档承接；
5. 架构不变量已分配到 Schema、生成器、静态检查、契约测试或真实验证，具备明确断言和失败处理；机器验证是否通过按实现成熟度另行记录；
6. 任何未完成项都有明确成熟度和进入下一阶段的可执行条件。

文档审定后，按切片把已批准要求落到权威 Schema、指导文档、生成器、测试和真实消费者。批准文档从实施开始就是约束来源；自动门禁逐步证明实现遵守它，不能由生成器或当前代码反过来改写要求，也不能把文档审核通过等同实现或生产验收通过。

已批准版本按受控基线保存；后续可以继续修正，但不能原地改写该版本的批准内容。修订须产生新版本候选，保留原版本的可定位制品或提交及内容摘要，列明前版引用、影响章节、消费者与兼容/迁移范围；涉及 Contract、Schema、State、Authority、UI 或 Qualification 时核对对应权威资产、现有任务及回归门禁，重大决定关联第 14.13 节 ADR。纯文字勘误可记录无语义影响及理由，不触发无关模块全量审核。影响分析、适用批准和生效范围未明确前，新候选不自动替代已批准实施基线；新版本批准后才在相应范围登记替代关系并通知消费者。已交付产品仍绑定其精确基线，升级按第 9 章执行，不能借文档改版静默改变生产行为或历史事实。

### 14.11 V0.5 Contract 工作包与完成判定

V0.5 按已冻结的切片依赖 DAG 推进，下表编号表示职责分工，不是八个整包必须逐个全部完成的顺序。每个交付切片必须闭合 Schema/强类型契约、语义校验、至少一个真实消费者、失败用例和交付引用；只有 Markdown 变化不能关闭工作包。

| 工作包 | 范围 | 必须交付 | 完成判定 |
|---|---|---|---|
| `C-01` 权威身份与状态 | Product、ProductRevision、WorkOrder、Lot、Board、Panel、PanelUnit、Layer、Side、Roll、RollSegment、Carrier、StationInstance、ProcessAttempt、InspectionAttempt、BoardRun、状态正交性及运行作用域/父子/因果关系 | AuthorityScope/状态/Owner 映射、独立版本域与时间域、ScopeType/ScopeId/ParentScope/ScopeEntity 身份引用、状态组合校验、事件/Receipt 绑定、身份黄金样例 | 多层/双面/卷段/载具/返工/重检可追溯；错父节点、跨产品实体、非法循环/状态转换/组合与冲突载荷被拒绝；合法重复事件幂等返回原结果且不重复应用，乱序按批准策略有界等待、补齐或重取快照；错 epoch/时钟域、作用域重叠和 revision 混用被拒绝；现有 Orchestrator/DataService 消费通过 |
| `C-02` Program/Recipe/Manifest | ProductRevision、ManufacturingGeometrySnapshot、SourceSetManifest、LayerStackRevision、BuildUpRevision、InspectionProgram、Recipe、MachineProfile、Calibration、Library、路线/覆盖/质量计划/证据集引用、运行清单作用域绑定与依赖闭包 | Schema、批准的 Canonical Profile/黄金向量、hash/签名、RecipeSnapshot 与运行实际输入绑定、发布/撤销/工程指针回退与兼容规则；必需输入校验、产品与制造参考批准绑定、PCB 名义几何/成品要求/Datum 的精确引用、HDI 引用图、父子配置适用规则和递归依赖验证器；PCB 计量计划投影、参考点/配对/方法与要求的精确发布绑定 | 同一输入稳定 hash；二级 latest、缺引用/循环、同版本异 hash、错层/阶段/能力/标定、CAD 冒充成品公差、资格失效、几何冲突和篡改均阻断；配置/运行证据闭包分离，配置期望值不冒充实际观测，AOI 消费者兼容，不得回退生产事实 |
| `C-03` 坐标/3D/计量 | CoordinateGraph、FOV、Stitching、HeightField、Rigid/Affine/NonRigid、WebCoordinate/WebCoordinateReference/卷段绑定、FPC 模型定义/拟合 Artifact、LaserVia、MeasurementDefinition、Quality、PCBMetrology | 坐标黄金样例、变换 Artifact、3D 生命周期、HDI/FPC/R2R/PCB 计量及第 2.11 节 PCB 用途/测量层级、特征/关系配对、参考点/基准/符号、采样/拟合证据、量纲/显示隔离、不确定度、能力匹配及资格/证书依赖、Calibration、MSA/GR&R、Bias、Linearity、Stability 和 Qualification Study | 方向/单位/域外/退化/残差/Invalid、缩颈/铜环/形位混用、排除真实坏值、跨 FOV 最差位置和 U/guard band、域外能力/未支持形位、策略改版沿用旧资格反例可复现；模型合格但本次拟合失效不能通过，旧卷段缺陷不取新基准；既有计量 Owner 按批准流程签发并管理资格有效期，现有坐标/计量测试通过 |
| `C-04` Pipeline/Decision/Commit | Stage、MeasurementSet、CoverageResult、InspectionFact、RuleEvaluation、InspectionDecision、MachineDecision/DecisionRevision/激活、Evidence、ExternalTestFact、ResultCommitReceipt/DispositionCommitReceipt、ProcessFeedbackProposal/FeedbackCommand/FeedbackReceipt/EffectObservation | DAG、资源/取消/幂等、覆盖/证据集及事实修订/局部替代提交、SPI 反馈闭环、多产品 Decisioning 准入、创建/激活/处置 Owner 校验；与 C-08 冻结评价作用域/输入及回执/签名绑定，按版本关系矩阵和设备证据阶段交付；PCB 生产计量载荷与 RuleEvaluation 接入同一事实/回执链，工程/研究/诊断/Replay/Review 辅助测量按用途隔离 | 重算/重试不重复事实；同键同载荷已提交返回原 Receipt，未提交恢复原 session；复判不改原事实，PCB 部分采样/无效量值不冒充合格，用途篡改和跨命名空间迟到提交拒绝；错尝试/机判版本、处置锁后激活、回执混接、签名不兼容、ACK 冒充 Applied 和效果未知触发重发被拒绝；覆盖缺口/外部冲突/断电/超时/迟到可恢复，AOI 与新增真实消费者回归通过 |
| `C-05` WPF 产品工作区 | Shell、生产、编程、复判、质量、诊断和维护 | Page Contract、Application Port、Query/Command、AutomationId、三语/DPI/UIA矩阵；第 2.11.7 节 PCB 计量用途/配对/基准/参考点/样本/最差点联动、计划计数、资格链与批量预览 | 每页真实 WPF 运行；八态、权限、键盘、恢复、截图和资源释放通过；PCB 计量缺口/无效/用途和层级区分、历史只读与单位/显示隔离可验收 |
| `C-06` 部署/安全/插件/适配器 | 进程拓扑、IPC、服务身份、签名、证书、插件、模型和更新；线扫、编码器、打印机、激光传感器、CAD 解析器和外部测试 Adapter | Deployment/Plugin/Security Catalog、适配器能力/版本/权限/资源边界、启动/升级/回退/撤销流程；Canonical Profile 及密钥用途/轮换/恢复、协议接收与应用/回读的证据映射 | 未签名、篡改、能力错配、证书失效、协议版本不符、重复 Owner 和升级中断均安全阻断；适配器不把 SDK 类型带入领域层；Profile/domain/key 错配拒绝，恢复不复活旧授权 |
| `C-07` 性能/恢复/运行可靠性 | PerformanceProfile、ContinuousInspectionProfile、队列、背压、资源、HIL、长稳和故障恢复；消费 C-03 的计量资格 | 板/Panel、PCB Pattern、HDI 微孔、FPC/R2R、SPI 印刷等专项 Profile、DAG trace、故障矩阵、按数据等级/故障范围的 RPO/RTO、备份独立回读/恢复演练回执、资源/恢复证据和长期运行记录 | P50/P95/P99、LineRate、编码器同步、资源斜率、恢复时间、运行可靠性和关键质量分层达到签名门限；实测恢复目标与演练完整性通过，备份文件存在不能代替可恢复；不签发或管理 MSA/GR&R/计量资格 |
| `C-08` 产品装配、路线、覆盖、外部测试与跨站交换 | AOI、SPI、钢网、PCB、QualityControl 装配矩阵，路线/覆盖/质量政策、评价上下文及跨站事件 | 内部子契约 `ProductAssembly`、`ProcessRoute`、`InspectionCoverage`、`Station`、`CrossSiteEvent`、`ExternalTestRegistration`；ProductProfile、板型/互连/材料/生产形态组合、ProcessRouteRevision/RouteStep/InspectionCoverageSpec、QualityPlanRevision/RequiredEvidenceSet、RouteAssessment/RouteAssessmentContext、能力清单、依赖 DAG、安装包、版本/兼容范围、消费者回归矩阵、跨站 Event Schema/回执、评价 AuthorityScope 与本机/中心 Hold 交接；PCB 计量需求/能力/用途装配、特征/特征内/板批次覆盖组合及既有 MetricDefinition/SubgroupPolicy 映射 | 产品独立启动/升级/回退；硬板/FPC/刚柔结合板/HDI 的条件未知、可选 NG、覆盖缺口、局部复检和放行不越权；评价固定输入及分区水位、迟到不改旧版；至少一次投递/幂等消费、时钟失锁、中心断网和冲突 Hold 恢复通过；共享升级不改其他产品事实；PCB 计量样本/特征/板/批次分母不混算，工程/研究数据不进入生产 SPC；与 C-04 的处置证据绑定及跨站去重/乱序/续传/回执闭合 |

每个工作包必须在现有模块目录和交付 Manifest 中登记一个最终 Owner、备份 Owner、批准角色、唯一权威入口、真实消费者、允许/禁止路径和完成状态引用。这里的“唯一权威入口”可以引用多个已存在的 Schema、指导文档和测试集合，不要求把不同领域合并为一个巨型 Schema 或重复建立测试工程。

对应能力被该切片采用时，验收还须覆盖：C-01 的身份观察/解析回执与重号/重检区分（第 3.15 节）；C-02 的分任务编程输入和不完整 Draft 发布阻断（第 3.20 节）；C-03 的测量资格上下文解析及实际适用域（第 2.11.4、3.13.3 节）；C-04 的多产品机判创建/激活/提交绑定（第 3.12.2 节）；C-05 的身份裁决、参考复核和返修操作与后台权限一致；C-08 的合规要求映射、返修双链和参考真值/统计口径（第 2.12.5、6.4、7.8 节）。各项由现有工作包承接，只补实际欠缺的契约/消费者，不增加平行注册表或工作包。

工作包的共同验收顺序为：

```text
契约定义 → Schema/代码生成 → 语义校验
→ 真实消费者接入 → 失败/恢复测试
→ 影响分析 → 定向验证 → Manifest/状态更新
```

先冻结首条 SPI 链实际消费的 C-01 身份、C-02 配置、C-03 计量、C-04 提交及 C-08 产品/路线契约，再按各自实现依赖接入；C-05 页面、C-06 安全部署和 C-07 预算/恢复要求在设计时参与，适用实现门禁在交付前通过。设计依赖、代码构建依赖与生产资格依赖分别登记在现有模块/Flow 资产，禁止用相互等待“对方整包完成”掩盖循环。一个 SPI 切片不必等待 C-03 全量 HDI/FPC 功能或 C-08 全厂质量平台完成；已关闭切片也不等于其所属整包完成，最终状态从实际要求与消费者证据汇总。

`C-01` 至 `C-04` 以及 C-08 中被首条链消费的产品装配、路线、覆盖和证据契约是 SPI 最小纵向链的前置；C-05～C-07 和 C-08 其余跨站扩展可并行推进。目标链路所需的页面、性能和安全门禁在其交付前必须通过，但不能以 UI 完成或测试夹具通过替代计量、目标机和生产资格。C-08 内部可按 `ProductAssembly`、`ProcessRoute`、`InspectionCoverage`、`Station`、`CrossSiteEvent` 和 `ExternalTestRegistration` 划分子契约/子任务，但仍只有一个 C-08 Owner、一个权威入口和一套交付状态，不新增 C-09。事件身份字段由 C-01 提供，跨站载荷、兼容、去重、乱序和回执由 C-08 负责。C-03 承接的既有计量 Owner 签发的资格是 C-07 的输入；C-07 只能验证和消费，不得复制资格模型。工作包的具体 Owner、允许路径、禁止路径和任务 ID 必须登记到仓库现有模块目录和交付 Manifest，不在本架构文档中维护第二套任务状态。

### 14.12 架构风险登记册

下表用于架构评审检查触发条件与缓解措施，不宣称风险已发生或已关闭。具体风险等级、责任人、期限、残余风险和验收证据引用现有任务/交付资产，不另建进度台账；每次变更只复核受影响项。

| ID | 风险 | 触发征兆 | 影响 | 缓解措施与落点 | 负责角色 |
|---|---|---|---|---|---|
| R-01 | 契约面过大，`C-01`～`C-08` 同时展开导致长期无可运行闭环 | 工作包并行数上升、无真实消费者的端到端链 | 交付延迟与集成风险积累 | 严格执行 SPI 最小纵向链优先（第 14.5 节）与第 11.2 节最小可用集 | 架构 Owner |
| R-02 | 新增产品接入产生同一作用域内竞争的 Decisioning 或统计权威 | 配置选择器决定 Owner、创建/激活混权、作用域重叠 | 事实冲突、追溯失效 | 第 3.12.2、14.6 节的绑定与矩阵门禁；接入前 DEV-ARC-005 变更；按非重叠作用域部署不等于重复权威 | 架构 Owner + 质量数据域 |
| R-03 | 计量资格长期无法关闭（标准件、样板、研究条件不具备） | `PendingProfile` 长期不清零 | 不能证明满足相应计量验收要求 | 资格分级推进；先关闭方法与适用域声明，再关闭数值（第 2.11.4 节） | 计量 Owner |
| R-04 | 模态与硬件选型变化导致算法与资格返工 | 供应链变更、传感器换代 | 资格与性能重做 | 模态属性抽象与适用域（第 3.13 节）；重验范围按影响分析确定 | 设备 + 计量 Owner |
| R-05 | 性能目标在多轨/大板/高密度场景下不可达 | 单轨达标但多轨严重劣化 | 产能不足，竞争力缺失 | 并发模型与背压（第 3.14.2、3.11 节）；负载按轨合计，共享瓶颈与故障域实测 | C-07 Owner |
| R-06 | 存储与带宽成本失控 | 现场磁盘频繁告警、证据被迫删除 | 回放与复判能力下降 | 容量模型与分级淘汰（第 3.19.1 节）；必需证据优先 | 部署 + 数据域 |
| R-07 | 合规义务迟启动或把自愿采用当作法定适用条件 | 无 SBOM/漏洞流程/AI 档案，仅列标准名，证书范围不匹配 | 市场准入受阻或错误合规声明 | 按第 2.12.4、2.12.5、7.5 节关闭适用性、要求映射、评定与证据 | 合规 Owner |
| R-08 | AI 能力被过早宣传为自动判定 | 销售材料出现“自动放行” | 质量事故与信任损失 | 阶段化上线与命名约束（第 7.3 节）；对外材料需质量与合规会签 | 产品负责人 |
| R-09 | 客户定制上升为分支 | 出现“客户专版”仓库或长期未合并分支 | 升级与回归不可控 | 第 4.4 节层级约束与交付清单审查 | 产品线 Owner |
| R-10 | 复判成为产线瓶颈，现场以放宽阈值应对 | 复判队列积压、阈值频繁调整申请 | 漏检风险上升 | 复判效率与一致性（第 8.7 节）；阈值变更走配置生命周期与影响分析 | 质量 Owner |
| R-11 | 跨机差异使客户认为产品不稳定 | 同配方跨机结果偏差、现场手调增多 | 口碑与售后成本 | 跨机一致性与移植验证（第 3.17 节） | 设备 + 计量 Owner |
| R-12 | 第三方依赖许可证或安全问题在交付前暴露 | 依赖扫描告警、法务未结论 | 交付阻断 | SBOM、许可证复核与第 10 章结论；引入前评审 | 工程 + 法务 |
| R-13 | 时钟、乱序与迟到事实处理不当导致质量结论漂移 | 报告随时间变化、重复事件 | 审计不通过 | 第 8.4、14.7.1 节的水位与评价版本机制 | C-01/C-08 Owner |
| R-14 | 文档与实现脱节，架构约束退化为口号 | 门禁未自动化、例外无登记 | 架构侵蚀 | 架构 CI 与例外登记（第 3.12.10 节）；ADR 记录（第 14.13 节） | 架构 Owner |
| R-15 | 身份观察直接绑定或冲突恢复丢失谱系 | 同码覆盖、临时号冒充真码、未决记录无法留存 | 错配方、串板、追溯中断 | 第 3.15 节的既有 Orchestrator 裁决、回执/CAS、防错与异常留证 | 身份模块 + 质量 Owner |
| R-16 | 参考标签错误、同源泄漏或不确定样本被静默排除 | 复判即真值、测试集跨板批次重复、修订后指标仍无条件沿用 | 检测/AI 性能高估，现场漏检 | 第 7.8.1 节参考能力、仲裁修订与数据分区；按第 7.8.3 节独立验证和分层估计 | 质量 + 算法/AI Owner |

### 14.13 架构决策记录（ADR）

重大架构决策复用 [产品输入与架构决策登记簿](../../docs/00-governance/产品输入与架构决策登记簿.md)（`DOC-GOV-003`）及其既有决策 Catalog、签署 ADR/附件，不创建平行审批流程。仅在存在实际决策与消费者时记录，日常低风险编辑不新增过程文件。

- 每条重大决策形成一条 ADR，至少记录：ID、标题、状态（提议/已接受/已替代/已废止）、背景与约束、被考虑的方案与取舍、决定、影响范围（章节、契约、工作包、消费者）、验证方式、决策人与日期、替代关系；
- ADR 适用范围：权威归属、契约边界、状态语义、坐标与单位约定、技术选型（后端、协议、存储）、性能与资源策略、安全与合规取舍、以及任何与本文条款冲突的例外；
- ADR **不是**需求或规范。它记录“为什么这样定”，正式约束仍写入本文、Schema、状态规范或开发指导；
- 与本文冲突的 ADR 必须同步修订本文并升版本，不允许长期并存两种说法；
- 已被替代的 ADR 保留原文与替代指向，不删除；
- 架构评审与 CI 例外登记引用 ADR ID，使“例外”可追溯、可到期复核（第 3.12.10 节）。

单项 ADR 被接受不等于整份架构获批。基线批准须在上述既有记录/附件中明确：基线与文档身份、精确版本及内容摘要/制品定位、批准范围、生效边界、实际批准人及职责、批准日期、关联 ADR、前版与适用替代关系，以及第 14.4 节尚未关闭门禁的权威引用、责任人与允许开发范围。这些是批准证据的内容要求，不新增 `ArchitectureApprovalRecord` Schema、服务或数据库，也不在本文复制动态门禁状态。

批准记录只有在证据可解析、版本与范围匹配且按既有流程完成批准后，才可驱动文件头的批准投影；缺失时保持待批准，不填虚构批准人、时间或签署结果。批准固定的是架构约束，不是 C-01～C-08 的完成状态，也不授予计量、设备或生产资格。批准证据中的摘要绑定明确的文档制品，不要求文档把自身最终 hash 写进正文形成自引用。

### 14.14 能力链与验收索引

下表供本项目的开发与验收人员检查能力链的架构位置和关闭证据。成熟度按第 14.4 节逐项取证；涉及竞品的结论须绑定具体厂商/型号/版本、资料位置、观察条件和限制。

对标资料只在现有证据条目中登记功能、操作步骤、输入输出、参数作用、可证实行为/实现推断、UI 布局、异常恢复、我方要求及定位等级。未取得手册/视频内容不能记作已观察，营销资料不能证明内部算法或现场性能；有证据支持的优势转成上述要求的验收输入，已知缺点不照搬。表内关闭条件验证本产品能力，不以“与竞品相同”代替质量、安全和易用性标准。

| 能力维度 | 架构落点 | 关闭条件（证据） |
|---|---|---|
| 3D 计量可信度 | 2.11、3.12.3、3.17 | 标准件与研究关闭数值，取得计量资格；单项量值可展开方法、实际运行、不确定度和资格依赖 |
| 多产品机判权威 | 3.12.2、14.6 | 每个产品作用域唯一解析创建/激活/提交权威；拒绝重叠与越权，AOI 与新增消费者回归通过 |
| 身份与防错闭环 | 3.15 | 原始观察→裁决回执→绑定→防错可回放；冲突留证、临时身份、合法重检与并发恢复验证 |
| 多模态成像 | 3.13 | 模态属性与适用域进入能力声明并通过资格 |
| 高速与并发 | 3.14.2、3.11、3.13.2 | 目标机多轨实测与背压验证 |
| 自动编程/NPI | 3.20、3.15.4 | 按领域/任务/模式验证输入、未决项及发布门禁；编程耗时与首次通过目标比例的实测 |
| 跨机一致性/配方移植 | 3.17 | 移植验证报告与差异门限 |
| SPI→印刷闭环 | 6.2 | 印刷机适配与效果观察实测 |
| 跨工序关联（SPI/AOI/AXI） | 6.5 | 配对映射与统计方法验证 |
| 复判效率与一致性 | 8.7、7.8.2 | 复判效率、混淆矩阵、分类别一致率及适用的一致性统计 |
| 返修闭环与物料追溯 | 6.4 | 缺陷修复与物料更换双链；序列号/批次/位置粒度、缺口和再验证端到端验收 |
| 设备绩效与远程服务 | 3.16 | 与 MES/CFX 的真实对接与服务流程 |
| 工厂互联标准 | 3.14.3、3.14.5、2.12.2 | 与真实设备/主机的互操作验证 |
| 追溯与合规证据 | 2.12、3.19 | 按客户体系审核通过 |
| AI 能力与治理 | 7.1～7.8 | 模型档案、统计验证与阶段化上线证据 |
| 检测性能可证明性 | 7.8 | 参考真值方法/仲裁/修订与独立数据集可回放；挑战集与统计研究关闭数值 |
| 国际化与服务 | 8.6、3.16.5 | 目标区域语言与服务流程就绪 |
| 网络安全与法规 | 2.12.4、2.12.5 | 实际市场/产品适用性、采用与实施证据映射、适用评定路径及支持/报告流程关闭 |

## 15. 附录

### 附录 A 受控术语表（架构级）

本表满足第 3.12.10 节对统一术语表的要求。它是**描述性**索引：定义与生命周期的权威仍在对应 Schema、状态规范与开发指导中，本表不新增状态或数据模型。术语的多语言对照按第 8.6 节受控管理。

| 术语 | 含义（架构级） | 权威所在 | 常见误用 |
|---|---|---|---|
| `InspectionDomain` | 领域能力标识，定义对象、算法、规则与事实的业务边界 | 第 2.1 节 | 与现场产品标识混用 |
| `ProductProfile` | 现场产品的装配范围：板型、材料、生产形态、能力与工作区 | C-08 | 当作配方或权限表 |
| `ProcessRouteRevision` / `RouteStep` | 产品实际经过的工位链及每步的约束、方法、覆盖与证据要求 | C-08 | 当作默认生产流程 |
| `StationDefinition` / `StationInstance` | 工位类型与现场设备实例 | C-01/C-08 | 第三种工位身份 |
| `Lane` / `Track` | 设备内的独立输送与检测通道，是并发单位 | 第 3.14.1 节 | 当作工位或产品 |
| `BoardRun` | 一次生产运行/板级生命周期上下文 | `DEV-ARC-005` | 与尝试混用 |
| `ProcessAttempt` / `InspectionAttempt` / `PrintAttempt` / `ReinspectAttempt` | 具体工艺或检测动作的尝试身份 | C-01 | 合并为万能 `Attempt` |
| `ManufacturingGeometrySnapshot` | 唯一经验证的设计/制造几何参考快照 | 第 2.8 节 | 当作领域对象或缺陷来源 |
| `SourceSetManifest` | 快照的输入清单：必需/可选、存在/缺失、校验结果 | 第 2.8 节 | 缺失输入伪造 hash |
| `InspectionProgram` | 检查什么（目标与项目） | 第 3.6 节 | 内嵌设备参数 |
| `Recipe` | 怎么检查（参数、策略、容差实例） | 第 3.6 节 | 承载产品主数据 |
| `EffectiveRuntimeManifest` | 本次运行冻结的配置依赖闭包与解析绑定 | 第 3.6 节 | 当作永久有效的资格证明 |
| `MeasurementSet` | 同一获准执行上下文的量测集合 | 第 2.10 节 | 与事实或结果混用 |
| `CoverageResult` | 实际观察与计划的差异事实 | 第 2.7 节 | 拥有豁免或放行权 |
| `InspectionFact` | 对外提交的领域事实封装 | 第 2.10 节 | 当作万能 `Result` |
| `RuleEvaluation` | 单次检测的规则评价结果 | 第 2.10 节 | 与机判混用 |
| `InspectionDecision` | 领域机判提议/投影 | 第 2.10 节 | 当作生产判定权威 |
| `MachineDecision` | 生产运行权威机判 | `DEV-ARC-005` | 由 UI/AI/质量中心创建 |
| `CAS`（按上下文） | 聚合并发处表示 Compare-and-Swap；证据对象处表示 Content-Addressable Storage | DEV-ARC-003、数据服务/多存储提交规范 | 用证据 hash 的存在代替状态版本校验，或用状态 CAS 成功证明证据已 durable |
| `EvidenceCommit` / `ResultCommitReceipt` | 证据与结果的提交边界与回执 | 第 3.12.2 节 | 以文件已生成代替提交成功 |
| `ReviewClaim` / `ReviewDecision` | 对已提交事实的授权复核与人工决定 | `DEV-ARC-005` | 视为一种 Attempt；改写原事实 |
| `RouteAssessment` / `RouteAssessmentContext` | 路线要求评价及其不可变输入快照 | 第 3.10 节 | 重新运行领域规则 |
| `FinalDisposition` / `DispositionCommitReceipt` | 最终处置及其提交回执 | 第 2.10 节 | 与结果回执互换 |
| `RouteAuthorization` / `BoardExitAck` | 路由动作授权与实体交接确认 | 第 2.10 节 | 当作质量合格证明 |
| `MeasurementQuality` | 量测有效性与原因（标定、配准、表面、覆盖、不确定度等） | 第 2.11.4 节 | 用 `Confidence` 替代 |
| `UncertaintyBudget` / `U` / `k` | 不确定度预算、扩展不确定度与覆盖因子 | 第 2.11.4 节 | 用拟合残差或重复性代替 |
| `MetrologyCapability` 适用域 | 特征×方法×尺度×光学×材料×环境的已验证组合 | 第 2.11.4 节 | 拼成未验证的笛卡尔积 |
| `MeasurementQualificationContext` | 量值引用的配置、实际运行、方法/研究/资格及验收用途的解析视图 | 第 2.11.4 节；现有 Manifest/计量权威 | 新增独立资格 Store 或以摘要代替可解析证据 |
| `ComplianceAdoptionRecord` | 法定适用性、合同/自愿采用、证据与评定路径的既有记录组合 | 第 2.12.5 节；质量/安全/交付资产 | 客户未采用即豁免强制义务 |
| `DecisionFlowScope` | AuthorityScope 的决策用途投影 | 第 3.12.2、14.6 节 | 新 Owner 注册表或全厂单例 |
| `SensingModality` | 成像/传感原理及其固有限制 | 第 3.13 节 | 当作实现细节隐藏 |
| `CodeReadingCapability` / `ProvisionalBoardId` | 读码能力与临时身份 | 第 3.15 节 | 顺序号冒充真实板号 |
| `BarcodeIdentityPolicy` / `IdentityResolutionReceipt` / `BoardIdentity` | 既有裁决策略、裁决回执与身份绑定；IdentityResolutionPolicy 为策略说明，ResolvedBoardIdentity 仅为 UI/查询投影 | 第 3.15 节；Orchestrator 身份权威 | 再建策略/实体主键；把未决身份当作正常生产绑定；因身份未决而拒绝留证或丢弃观察 |
| `RecipeMatchVerification` | 程序—板型防错结论 | 第 3.15.3 节 | 降级为提示 |
| `FirstArticleGate` / `ChangeoverGate` | 首件与换型门禁 | 第 3.15.4 节 | 未经影响验证和批准跨配方/跨轨道沿用 |
| `CheckDefinition` / `CheckResult` | 点检与期间核查 | 第 3.16.3 节 | 由操作员勾选恢复 |
| `MachineMatchingArtifact` / `TransferVerification` | 机台匹配与移植验证 | 第 3.17 节 | 现场手调掩盖差异 |
| `ReworkOrder` / `RepairAction` / `ReworkVerification` | 返修闭环 | 第 6.4 节 | 直接修改原事实 |
| `DatasetSnapshot` / `ModelRecord` | 数据集快照与模型档案 | 第 7.5、7.6 节 | 标签当绝对真值 |
| `GroundTruthRecord` | 带参考方法、范围、不确定性、仲裁与版本的参考结论语义 | 第 7.8.1 节；既有标注/质量验证资产 | 复判、客户反馈或 AI 标签自动当真值 |
| `SupportedLocaleSet` | 产品支持的语言/区域集合 | 第 8.6 节 | 语言硬编码 |
| `PendingProfile` | 性能/容量/精度目标或适用条件尚未批准冻结；目标与后续实测资格分别验证 | 第 3.11、8.5 节 | 填入宣传值 |
| `ContractCandidate` → `Contracted` | 契约成熟度推进状态 | 第 14.6 节 | 以文档变更关闭 |

### 附录 B 非功能需求（NFR）汇总矩阵

以下矩阵汇总非功能验收输入；数值和判据由对应的计量/质量/安全/性能权威资产冻结，不把所有要求塞入 PerformanceProfile。每项须有适用范围、Owner、验证方法与关闭证据，本表不预填承诺值。

| NFR 类别 | 要求要点 | 正文落点 | 验收证据形式 |
|---|---|---|---|
| 性能-节拍 | 板级 CT、阶段 P50/P95/P99、队列等待、多轨并发下的有效吞吐 | 3.11、8.5、3.14.2 | 目标机实测 + `PerformanceProfile` |
| 性能-连续 | `WebSpeed`、`LineRate`、编码器同步、缺陷定位延迟、背压 | 2.9、8.5 | `ContinuousInspectionProfile` |
| 容量-存储 | 日增量、在线保留、归档、带宽、淘汰策略 | 3.19.1 | 容量核算 + 现场验证 |
| 计量-准确度 | 偏倚、线性、稳定性、重复性、再现性、MSA/GR&R、U/k、适用域 | 2.11.4、3.12.3 | 标准件与 Qualification Study |
| 检测-有效性 | 召回、误报、逃逸、拒识、分层最差值与置信区间 | 7.8、14.9 | 挑战集与统计研究 |
| 一致性-属性 | 判定者内/间一致性、人机一致性 | 7.8.2 | 属性一致性分析 |
| 一致性-跨机 | 机台间偏差、移植验证、匹配残差 | 3.17 | 移植验证报告 |
| 可靠性 | 断电、崩溃、断连、磁盘满、卡板、重启恢复、长稳 | 9.3、14.9、3.14.6 | 故障矩阵与恢复演练回执 |
| 可恢复性 | 按数据等级与故障范围的 RPO/RTO、恢复演练 | 9.3 | 独立回读与演练回执 |
| 可用性-人因 | 首次任务时间、按键数、误操作率、恢复成功率、八态 | 10.5、8.2、8.7 | 真实 WPF 场景验收 |
| 可达性与本地化 | 语言集、单位制、对比度、键盘、UIA、文本扩展 | 8.6 | 按 `SupportedLocaleSet` 的矩阵 |
| 安全-信息 | 认证、权限、签名、完整性、审计、SBOM、漏洞与更新 | 3.12.8、2.12.4 | 安全测试与流程证据 |
| 安全-功能 | 与安全体系的边界、不得越权写安全状态 | 3.12.8、2.12.2 | 接口评审与联锁测试 |
| 合规 | 法定适用性、采用版本/类别/条款、评定路径与逐条证据；数据完整性映射 | 2.12、3.19.3 | 审核可引用的证据包及适用性记录 |
| 可维护性 | 点检、保养、耗材、健康度、远程服务与诊断导出 | 3.16 | 维护流程与现场验证 |
| 可演进性 | Schema 兼容、迁移、回读、并行版本、消费者回归、回退 | 9.2、14.8 | 升级演练与回归矩阵 |
| 可观测性 | 按 `boardRunId/attemptId/operationId/decisionRevision/traceId` 关联 | 8.5 | 诊断导出与追踪验证 |
| 可交付性 | 定制层级、安装包、授权、并行版本、现场升级 | 4.4、5、9 | 交付清单与升级演练 |

### 附录 C 外部依据采用与核对要求

第 2.12 节列出的标准族和法规是待适用性评估的依据目录，不是已完成逐条验证或已合规清单。第 10.2 节 A/B/C 仅用于其 GitHub 证据。NIST 方法来源沿用第 2.11.8 节的定位与核对记录；本附录下表记录实际核对的有限范围，其余条目的采用版本、条款和核对日期须以实际官方来源核验为准。

| 依据类别 | 正式采用前必须核对 | 消费位置 |
|---|---|---|
| CFX、Hermes 与设备状态 | 官方版本、消息方向/状态、设备能力、映射和真实互操作；状态分类引用不等于协议认证 | 3.14、3.16 |
| IPC 装配/裸板/印刷/追溯 | 客户采用的标准版本/条款/类别、可观察范围、试验方法与报告用语；最新版不自动替代合同版 | 2.12、2.13、6 |
| GUM/JCGM、ISO 14253、光学/坐标/表面计量方法 | 适用被测量、系统类型、具体部分与版本、不确定度模型、验证条件；不能整族套用至 SPI/AOI | 2.11、3.12.3、3.16.3 |
| 质量体系、抽样与数据完整性 | 客户适用体系、样本设计/转移规则、电子记录/电子签名用途、保留和验证责任 | 6.6、3.19、8.3 |
| 网络安全、机械/光学安全、数据保护与 AI 治理 | 官方法律文本及修订、产品用途/上市区域/责任主体、例外与过渡安排、适用日期、所需评定与记录 | 2.12、3.13、3.19、7.5 |

采用记录至少包含来源标题与官方定位、版次/条款、核对人和日期、市场/客户/产品范围、采用资产引用、实施证据、批准及复核触发条件。官方摘要用于识别主题，不能代替需要逐条验证的规范正文；未取得使用权或正式条款时不得声称完成条款核对。记录复用质量计划、安全/部署目录和既有证据资产，不为本附录再建一套标准数据库。

以下来源于 2026-09-17 核对，仅支持所列结论，不表示已验证本项目实现或现场资格：

| 官方来源与定位 | 已核对范围 | 消费位置与限制 |
|---|---|---|
| [CRA：Regulation (EU) 2024/2847](https://eur-lex.europa.eu/eli/reg/2024/2847/oj/eng)，第 69、71 条 | 适用日期、存量产品过渡与第 14 条报告义务例外 | 第 2.12.4、2.12.5 节；仍须逐产品核定适用性与义务，不作统一合规声明 |
| [IPC-HERMES-9852 Version 1.6，July 2024](https://www.the-hermes-standard.info/wp-content/uploads/IPC-HERMES-9852-Version-1.6-HERMES-SITE.pdf)，第 2.3.3、3.10～3.12 节，PDF 第 14、38 页（正文第 6、30 页） | StartTransport/StopTransport/TransportFinished 的发送方及运输分支说明 | 第 3.14.3 节；只核对相关条款，具体设备仍冻结现场版本、完整状态机与互操作测试 |
| [CFX 官方版本说明](https://www.electronics.org/about-cfx-global-standard-smart-manufacturing-enablement)，Version Release Dates / 2.0 | 官方列示 2.0 发布于 March 2025 | 第 3.14.5 节；发布存在不证明设备 SDK、消息集或现场互操作兼容，不能自动升级当前适配器 |
| [SEMI E58 官方目录](https://store-us.semi.org/products/e05800-semi-e58-automated-reliability-availability-and-maintainability-standard-arams-concepts-behavior-and-services)、[SEMI E79 官方目录](https://store-us.semi.org/products/e07900-semi-e79-specification-for-definition-and-measurement-of-equipment-productivity) | E58 为自动化 RAM 的概念/行为/服务，目录标示 E58-0703 为 Inactive；E79 为设备生产率定义与测量，E79-0422 标示为 Current | 第 3.16.2 节；目录仅核对主题/状态，E58 不作为默认新项目基线；未声称取得付费规范或已按其条款实现 OEE |
