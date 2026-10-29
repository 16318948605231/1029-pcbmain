# 配置参数与版本快照独立模块开发指导

> 状态标记：review=`DesignReview/Prep`｜module-ready=`PreparationIncomplete`｜core-ready=`C1, C2`

- 模块 ID：`IM-002`；来源：`PKG-002`、`SM-002`。
- 文档版本：`0.3.4-prep`；修订日期：2026-10-11；状态：`DesignReview / Prep`；0.3.2限定内容接收日：2026-10-11；0.3.3全部批准范围文档准备结论见§19.1；0.3.4仅对齐SD 0.3.1启动/epoch/关闭说明，原结论保持。
- 主控于2026-10-10接收C1/C2六项准备结论，两个切片为 `ModuleCoreImplementationReady`；A1-F及U1无矛盾范围接收保持，仍为 `PreparationIncomplete / NotReady`；0.3.2的A1-DB绑定与U1物理单位桥指导内容已由主控限定接收；0.3.3定向接线补充与全范围自审见§19.1；A1-F/A1-DB/U1真实资格仍为 `PreparationIncomplete / NotReady`。完整模块仍为 `PreparationIncomplete`，本文不声明实现、构建、性能、WPF或现场资格通过。
- 永久会话：`01a10306-e17f-7fd0-b6ff-efa191bb2fac`，已检索并核对 [模块索引](../MODULE-INDEX.md)；内容接收与切片准入分别按下表记录，实际实现范围由用户指定。
- 技术基线：C# / .NET 10；Core无WPF/产品Shell/设备SDK。可选WPF只用已安装DevExpress25.2.3。HALCON/AsunImage非本模块计算依赖。
- 规划消费者：独立设备参数工具、离线算法工具、生产宿主，具体契约接入见§17。
- 本文是唯一实施规格。纯内存Core、持久服务/端口、真实适配和可选UI分别准入；不以缩小首片取消完整模块能力。历史v0.1设计尚无本文可验证的实现；本轮修正设计采用v0.2，不冒称旧版本兼容。

## Core implementation binding

| 切片 | 唯一工程 / namespace | 唯一测试工程 | 允许 / 禁止及后续门 | 接收与准备状态（2026-10-11） |
|---|---|---|---|---|
| C1 纯内存 | `src/Modules/configuration/Asun.Modules.Configuration.Core/Asun.Modules.Configuration.Core.csproj`；`Asun.Modules.Configuration` | `tests/Modules/configuration/Asun.Modules.Configuration.Core.Tests/Asun.Modules.Configuration.Core.Tests.csproj` | Definition、Candidate、SealDefinitions/Validate/Normalize/Compare、codec/hash；禁止IO、后台线程、UI/设备/默认存储装配。 | 六门已接收；`ModuleCoreImplementationReady`，仅规格准备。 |
| C2 服务和端口模拟 | `src/Modules/configuration/Asun.Modules.Configuration.Service/Asun.Modules.Configuration.Service.csproj`；`Asun.Modules.Configuration.Service` | `tests/Modules/configuration/Asun.Modules.Configuration.Service.Tests/Asun.Modules.Configuration.Service.Tests.csproj` | Load/Save/历史/原操作查询/迁移/Watch/Close，公开端口与内存故障夹具；不声称真实耐久。 | 六门已接收；`ModuleCoreImplementationReady`，仅服务/端口模拟规格准备。 |
| A1 真实存储 | `src/Modules/configuration/Asun.Modules.Configuration.Adapters/Asun.Modules.Configuration.Adapters.csproj`；`Asun.Modules.Configuration.Adapters` | `tests/Modules/configuration/Asun.Modules.Configuration.Adapters.Tests/Asun.Modules.Configuration.Adapters.Tests.csproj` | 文件适配、宿主存储端口映射；数据库技术由storage-database公开能力组合，不另建数据库平台；真实崩溃/卷/数据库资格另门。 | A1-F内容接收保持，`PreparationIncomplete / NotReady`；A1-DB §8.4公开映射/Owner编码/分页/双Host指导内容已限定接收，真实PG/fence/崩溃及产品资格仍 `PreparationIncomplete / NotReady`。 |
| U1 可选投影 | `src/Modules/configuration/Asun.Modules.Configuration.Wpf/Asun.Modules.Configuration.Wpf.csproj`；`Asun.Modules.Configuration.Wpf` | `tests/Modules/configuration/Asun.Modules.Configuration.Wpf.Tests/Asun.Modules.Configuration.Wpf.Tests.csproj` | 版本/差异/提交恢复控件；编辑复用parameter-editor公开能力；真实25.2.3/WPF/三语/UIA/1920×1080另验。 | 已接收无矛盾范围保持；§10.3.1/§10.5物理桥指导内容已限定接收，仍为 `PreparationIncomplete / NotReady`。 |

这些是计划落点，不代表已创建；不机械建立空工程。每个获准实现任务只写所选行的工程及测试目录；不得修改其它模块、产品、共享合同、参考快照、AsunImage或tools。当前文档任务只写本指导。依赖：Wpf/Adapters→Service→Core，Core不反向引用。端口/服务DTO只在Service定义，纯值只在Core定义，不再复制Contracts同名类型。

### DEV-GOV-010 §3.1 六项准备结论

| 门 | C1 | C2 | A1 / U1 |
|---|---|---|---|
| 1 职责、非目标、第二消费者 | §1/§3/§17规格已接收 | 副作用Owner规格已接收 | 接入消费者规格已接收，真实接入未验 |
| 2 API、状态、Owner、版本 | §4～§7及四域Golden规格已接收 | §6.2/§7/§11.3根Owner规格已接收 | A1-F/U1无矛盾合同接收保持；A1-DB §8.4公开端口/Owner原件/完整分页及U1物理桥本轮指导内容已限定接收 |
| 3 无UI独立宿主 | §11.1/§13.1 BCL Exe规格已接收 | §11.3 Factory前根Owner/两个Host规格已接收 | §8.3.3文件Host接收保持；§8.4.5 DB双无UI Host、§10.5修正STA Host指导内容已限定接收，未运行 |
| 4 正常/边界/并发/取消/回退 | §12/§13及四域bytes/hash规格已接收 | 同左，Owner移交/业务cleanup分离断言规格已接收 | §8.4.5/8.4.6 DB反例/Owner Golden及§10.3.1物理桥反例指导内容已限定接收；真实crash/STA/UIA/语言未执行 |
| 5 Profile、测点、资源 | §14方法/资源规格已接收；目标TargetPending/NotEvaluated | 同左；预算显式 | 已接收范围保持；本轮DB §8.4.4及修正PE转换预算指导内容已限定接收，目标待消费者采纳，性能未验 |
| 6 唯一落点、禁止范围、调用 | 本表/§11规格已接收 | 同左 | 已接收范围保持；本轮DB/修正U1落点与§13.1命令指导内容已限定接收，真实资格后续 |

主控于2026-10-10确认C1纯内存、C2服务/端口模拟满足六项准备条件，两个切片为 `ModuleCoreImplementationReady`；这是规格准备状态而非实现验收，构建/测试/性能尚未执行，属于获准实现后的验证，不反向要求文档六门先写代码。A1-F及U1无矛盾范围接收保持，仍为 `PreparationIncomplete / NotReady`，保留真实卷/crash/PowerLoss、WPF25.2.3/1920×1080/UIA、性能及产品接线资格门；2026-10-11补充A1-DB的storage-database精确公开映射及Owner编码/完整快照分页，修正U1物理kind/单位无损桥，主控已限定接收两个修订范围的指导内容；真实PG/fence/崩溃/WPF/产品资格仍未关闭，接收不提升运行资格。完整模块仍为 `PreparationIncomplete`。唯一准入标准见 [DEV-GOV-010](../../01-governance/DEV-GOV-010_实施级规格唯一标准.md#31-独立模块核心代码开工门)。

## 1. 目的与职责

管理类型化参数候选、定义引用、确定性规范化与差异、显式迁移、不可变持久版本、CAS和原操作回执。参数业务意义/范围来自算法或设备领域Owner；配置服务拥有配置版本事实，注入Store负责原子IO。

完整能力为SealDefinitions、CreateCandidate、Validate、Normalize、Compare、Load最新/指定修订、Save、QueryOperation、ListRevisions、MigrateCandidateAsync、Watch、Close；全部无UI可调用。没有自动合并、静默删字段、自动发布/激活、默认写盘或多配置批量事务。

非目标：EffectiveRuntimeManifest、板/工单关联、质量判定/放行、设备命令/回读、权限最终裁决、凭证解密、视觉校验/训练。设备曝光”已保存”不等于相机已应用；算法参数Valid不等于真实图像检测合格。外部视觉回执由宿主依其Owner合同保存并关联内容摘要，不成为Core的隐含放行状态。

### 1A. 新架构适配要点

**架构门禁**：`Asun.Configuration.Core`、`Asun.Configuration.Service`、`Asun.Configuration.Adapters` 不得引用 `System.Windows.*`、`PresentationFramework`、`DevExpress.*`。只有 `Asun.Configuration.Wpf` 可引用，不反向引用。

**Blazor/Web 宿主注意事项**：配置服务的 `Watch`（参数变更通知）在 Blazor Server 宿主中通过 SignalR 推送给浏览器，用于实时刷新参数看板。具体约束：
- Web 端只读展示参数值，不直接提交参数写入（写入必须经 WPF 工站的人工确认）
- `Watch` 产出的事件通过 `integration-transport` 的 SignalR Hub 推送，不直接注入 Blazor 组件
- 参数变更的三态流程（建议→草稿→生效）在 `parameter-editor` 模块中实现，本模块只存储已批准的配置版本

**L1-L4 参数学习接口**：`ai-dataset-governance` 的 L1-L4 输出为 `ParameterSuggestion`，通过 `parameter-editor` 模块确认后写入本模块：
- 本模块不直接接受来自 L1-L4 的推荐，只接受经人工或 `parameter-editor` 确认的 `CreateCandidate` 请求
- 每次参数变更必须有来源标记（`Source: “L2-AutoSuggestion”` 或 `”Manual”`），存入 `CandidateMetadata`
- 来源标记不影响参数有效性验证，但在审计日志中必须可追溯

**HALCON 备选无关性**：本模块存储参数值，不执行视觉算法，不涉及 HALCON/OpenCV 双跑。

## 2. 设计原则与术语

| 术语 | 语义 |
|---|---|
| Candidate | 不可变但可无效的内存候选；完整Definition随候选携带，无隐藏注册表。 |
| NormalizedCandidate | 全量验证后的规范值和内容摘要；公开record仍须在入口重验。 |
| Snapshot | Store已提交版本，含ConfigKey、Revision、原操作、时间与规范内容。 |
| ConfigKey | (ConfigurationId, ScopeId)，同键CAS；不能直接当路径/表名。 |
| Revision | ulong，0表示从未存在，首次成功为1，仅新Save递增；禁止回绕。 |
| ContractMajor / SchemaVersion | 公共合同主版本 / 精确结构SemVer；同major不自动兼容。 |
| OperationId | 调用方提供的持久Save身份，重试沿用。纯计算不生成ID。 |
| RequestSha256 / ContentSha256 | 请求身份（含键、期望修订、来源）/规范内容身份；不能混用。 |
| UnknownOutcome / DrainUnknown | 提交知识未知 / 在途资源未归还；独立两轴。 |

相同内容不同新操作且CAS正确仍生成新revision；同操作同请求返回原回执；同操作不同请求拒绝。不以“摘要无明文”证明保密：低熵值摘要仍可被穷举。失败/冲突保留旧快照，Unknown不生成空配置、不换ID重试、不删除新事实。

## 3. 分层与端口

Host显式构造Core→Service注入Core/Store/可选MigrationProvider/Clock/limits→可选Wpf投影。Core全部局部纯计算，无Dispose/后台资源；Service负责接纳、在途任务和内部订阅。Store由宿主所有，Service排空后宿主才可Dispose它；多个服务共享端口时不得由某一服务关闭它。

所有输入在调用期间由Host保持不变，检查容量后深复制；Definition默认值/AllowedValues/约束、字典和Opaque字节也复制，输出ImmutableArray/ImmutableDictionary。无Stream借用、SDK句柄、JSON节点、产品DTO、私有表或全局可变注册表。不依赖UI初始化，程序集可单独引用、测试、发布、回退。

## 4. 输入与输出契约

### 4.1 标识、容量和单位

严格UTF-16/UTF-8：孤立surrogate拒绝，UTF-8编码不替换坏字符。键、配置/作用域/定义/操作ID均1..160 Unicode标量，ordinal区分大小写，不trim、不NFC；ConfigKey不含斜杠、反斜杠、NUL/控制字符。Source Type/Id/Version非空，Sha256是64小写hex。字符串值允许空串，空串与缺失不同。Values/UnknownFields不能交叉重键，RawUnknownField.Key必须等于dictionary键；已定义键不能落在UnknownFields，未定义键不能落在Values。dictionary自带comparer不能改变ordinal语义，重新按ordinal检查/复制，不能先用原comparer搜索定义。

CoreLimits为显式资源预算：定义/候选字段数、约束数、每定义枚举成员数、单文本Unicode标量、所有定义与输入UTF-8总字节、单Opaque字节上限，均正数。定义和Values+Unknown字段各不得超过MaxFields，AppliedDefaultKeys不得超过MaxFields，每个AllowedValues不得超过MaxEnumValues。所有累加checked long，复制前计数Key/Unit/AllowedValues/默认/来源/Opaque；超限CFG-002。防止后续模块分配无界，不声称追回Host已分配内存。字段数上限不能替代单字段容量；大量空枚举成员也不能绕过数量门。

### 4.2 类型、范围与规则

ParameterValue显式Kind/Unit/Text，Kind与定义匹配、Unit精确匹配规范单位。Unit非空且受文本预算限制，量纲为无单位时写None，不用空串；Duration/Length/Angle单位固定，其余数值单位由定义Owner明确给出。数字不接受前后空白、千分位、NaN/Infinity和溢出；整数仅带可选正负号的十进制整数，Decimal语法为可选正负号+至少一位整数+可选小数点和至少一位小数，无指数；Double同样要求数字，小数/指数按Invariant语法允许，拒首尾空白及千分位，所有解析InvariantCulture。

| ValueKind | Unit / 数值 | 固定行为 |
|---|---|---|
| Boolean | None；bool | 仅小写true/false。 |
| Int32/Int64 | None或明确单位 | 精确整数闭区间/整数步长；规范无前导+或零、负零为0。 |
| Decimal | 明确单位 | .NET decimal、Invariant固定小数；零统一0。 |
| Double | 明确单位 | 有限binary64，独立DoubleBounds；Invariant R，正负零统一0；不支持Step。 |
| Duration | ms；Int64 | 非负毫秒整数，不表示无限等待。 |
| Length/Angle | um/deg；decimal | 负值/跨圈由范围决定，不猜单位、不自动环绕。 |
| Ratio | None；decimal | 固有0..1再与定义闭区间取交，拒绝不夹紧。 |
| Enum | None；字符串 | ordinal AllowedValues成员，集合非空无重复，不用显示标签持久化。 |
| String | None；字符串 | 保留原Unicode/换行，容量受限，不trim/NFC。 |
| Uri | None；字符串 | UriKind.Absolute语法有效，保留原文本，不依赖AbsoluteUri重写；网络/路径授权由Host。 |
| SecretReference | None；引用ID | 非空稳定引用、Sensitive=true；无解密/有效凭证检查，不能填密钥明文。 |

DecimalBounds用于除Double外的数值；Min≤Max，Step>0且需Minimum作为步长起点，(value-Minimum)%Step=0。Int/Duration界限及Step必须整数；步长判定转为BigInteger系数统一scale，避免decimal差值溢出。DoubleBounds仅Double，Min/Max有限并有序；非数字带范围、非Enum带AllowedValues、非法默认、重复定义键/枚举或约束悬空均CFG-004。范围/默认来自领域Owner，本模块不给业务阈值。

Decimal/Length/Angle/Ratio先按上述语法取符号、十进制BigInteger系数和scale，去掉不改变值的尾零，确认scale≤28且系数≤2^96−1后才构造decimal；禁止仅用decimal.TryParse的成功结果，因为不可表示的多位小数可能被静默舍入。Int32/Int64/Duration各有固有范围，定义范围必须与固有域相交非空，Duration不能为负；Ratio范围同理不得与0..1相交为空。Double是显式binary64语义，十进制输入允许一次正确解析舍入，但非零输入下溢为0拒绝CFG-005，不以静默归零掩盖数值。步长/范围计算不改输入值。

跨字段首版只支持同Kind/Unit的两个非Double数值字段按Less/LessOrEqual/Equal/GreaterOrEqual/Greater原子关系，不执行脚本/任意表达式或用户回调。被关系引用的任一字段缺失，即使其Required=false，也报告CFG-005并列双方RelatedKeys；字段非法先报告字段错误，不伪造约束通过。关系不满足CFG-005且RelatedKeys含双方。CreateCandidate只填明示DefaultValue并记录AppliedDefaultKeys，Validate不再改值；Required无值无默认整候选Invalid。

### 4.3 Core Module API Contract v0.2

所有纯值只定义在Asun.Modules.Configuration。下列是公开签名规格，工厂方法体属于获准实现；不是已经可运行的库。

```csharp
using System;
using System.Collections.Generic;
using System.Collections.Immutable;
namespace Asun.Modules.Configuration;

public readonly record struct SemanticVersion(int Major, int Minor, int Patch);
public enum ValueKind { Boolean, Int32, Int64, Decimal, Double, Duration, Length, Angle, Ratio, Enum, String, Uri, SecretReference }
public enum SchemaPolicy { Reject, PreserveOpaque, DropWithExplicitMigration }
public enum Relation { Less, LessOrEqual, Equal, GreaterOrEqual, Greater }
public enum DiffKind { Added, Removed, Changed }
public sealed record DecimalBounds(decimal? Minimum, decimal? Maximum, decimal? Step);
public sealed record DoubleBounds(double? Minimum, double? Maximum);
public sealed record ParameterValue(ValueKind Kind, string Unit, string Text);
public sealed record ParameterDefinition(string Key, ValueKind Kind, string Unit,
    bool Required, ParameterValue? DefaultValue, DecimalBounds? DecimalBounds,
    DoubleBounds? DoubleBounds, ImmutableArray<string> AllowedValues, bool Sensitive);
public sealed record FieldConstraint(string Id, string LeftKey, Relation Relation, string RightKey);
public sealed record DefinitionSet(string Id, string Version, SemanticVersion SchemaVersion,
    SchemaPolicy UnknownPolicy, ImmutableArray<ParameterDefinition> Parameters,
    ImmutableArray<FieldConstraint> Constraints, string ContentSha256);
public sealed record RawUnknownField(string Key, ImmutableArray<byte> Utf8Value);
public sealed record SourceRef(string Type, string Id, string Version, string ContentSha256);
public sealed record RawConfiguration(string ConfigurationId, string ScopeId,
    IReadOnlyDictionary<string, ParameterValue> Values,
    IReadOnlyDictionary<string, RawUnknownField> UnknownFields, SourceRef Source);
public sealed record ConfigurationCandidate(string ConfigurationId, string ScopeId,
    ushort ContractMajor, DefinitionSet Definitions,
    ImmutableDictionary<string, ParameterValue> Values,
    ImmutableDictionary<string, RawUnknownField> UnknownFields,
    ImmutableArray<string> AppliedDefaultKeys, SourceRef Source);
public sealed record NormalizedCandidate(ConfigurationCandidate Candidate, string ContentSha256);
public sealed record ValidationDiagnostic(string Code, string MessageResourceKey,
    ImmutableArray<string> RelatedKeys);
public sealed record ValidationResult(bool IsValid, ImmutableArray<ValidationDiagnostic> Errors);
public sealed record DiffEntry(string Key, DiffKind Kind, string Unit, bool Sensitive,
    bool BaselinePresent, bool CandidatePresent,
    string? BaselineValueSha256, string? CandidateValueSha256);
public sealed record DiffResult(ImmutableArray<DiffEntry> Entries);
public sealed record CoreLimits(int MaxFields, int MaxConstraints, int MaxEnumValues, int MaxTextScalars,
    long MaxTotalUtf8Bytes, int MaxOpaqueBytes);
public sealed record ConfigurationCoreOptions(ushort ContractMajor,
    SemanticVersion SchemaVersion, CoreLimits Limits);
public sealed class ConfigurationCoreException : Exception
{
    public string Code { get; }
    public string MessageResourceKey { get; }
    public ImmutableArray<string> RelatedKeys { get; }
    public ConfigurationCoreException(string code, string resourceKey,
        ImmutableArray<string> relatedKeys) : base(resourceKey)
    { Code = code; MessageResourceKey = resourceKey; RelatedKeys = relatedKeys; }
}
public interface IConfigurationCore
{
    ConfigurationCoreOptions Options { get; }
    DefinitionSet SealDefinitions(DefinitionSet definitions);
    ConfigurationCandidate CreateCandidate(DefinitionSet definitions, RawConfiguration raw);
    ValidationResult Validate(ConfigurationCandidate candidate);
    NormalizedCandidate Normalize(ConfigurationCandidate candidate);
    DiffResult Compare(NormalizedCandidate? baseline, NormalizedCandidate candidate);
}
```

唯一公开static工厂类为 `Asun.Modules.Configuration.ConfigurationModuleFactory`，公开static方法签名为 `IConfigurationCore CreateCore(ConfigurationCoreOptions options)`。只支持ContractMajor=1、非负精确SchemaVersion和有效limits；候选Schema不自动minor/patch兼容。SealDefinitions接受空摘要请求计算，或非空正确摘要请求核验；输出深复制、规范排列及摘要，不注册产品事实、不IO。后续所有入口复核完整Definition与摘要，不能信任public record身份/对象引用。default ImmutableArray与null结构拒绝，不当空集合。

Core不需要OperationId provider/Clock：纯调用无副作用；持久Save调用方显式提供ID。null、Unicode、enum、版本、定义结构/容量错误用CoreException；逐字段Required/值/Unknown/约束错误用ValidationResult。Normalize重新Validate，不凭外部IsValid缓存。返回诊断只含资源键/相关字段，不含值或路径。


## 5. 校验、确定性 codec、差异与迁移

### 5.1 Core逐步处理与摘要

1. 先检查null/default集合、枚举、标识、版本、容量和ordinal重复；原始JSON/INI/XML适配必须在建dictionary前拒重复键，不能用最后覆盖。
2. 复核Definition结构，规范默认值/范围/AllowedValues与约束，按下面codec重新算定义摘要。SealDefinitions允许空摘要，其它入口不允许空或伪造摘要。
3. CreateCandidate深复制，按定义补显式默认；没有默认的可选字段保持缺失。Required缺失由Validate诊断。AppliedDefaultKeys必须唯一、已定义且当前存在；它表示创建时使用默认的来源标记，不是“当前仍等于默认”的证明。
4. Validate全量检查定义、标识/来源、类型/单位/范围/枚举、Unknown策略，然后执行可判定的跨字段关系，收集错误。Unknown不允许伪装为已定义键。Reject和DropWithExplicitMigration遇Unknown均CFG-006；PreserveOpaque保留有效UTF-8原字节，不解析内部JSON，不把其内容当参数。
5. 字段错误按RelatedKeys的ordinal字典序、Code排序并去完全重复；约束相关键也排序。无效输入不产生NormalizedCandidate。Normalize重新验证后规范数字文本、规范排列；其它文本/opaque不改。
6. Compare两侧重新验证、Normalize并核验声称摘要，CFG-017拒伪造；同ConfigKey、ContractMajor、SchemaVersion及Definition摘要才比较，否则CFG-003/004要求显式迁移。null baseline返回所有已存在值/opaque的Added；不存在的可选字段不输出。变化按键ordinal排序，DiffEntry的Kind是Added/Removed/Changed，不是ValueKind；Unit为已知定义单位，opaque固定None且Sensitive=true。敏感字段和所有opaque仅返回存在性/差异种类/单位，两个值摘要均null；普通字段值摘要仅在差异对象中提供，不作日志默认字段。比较以规范值或opaque原字节为准；只变Source/AppliedDefaultKeys不产生字段diff，但Save请求身份仍不同。

codec唯一名称为 `asun-config-binary-v2`。这是摘要字节规范，不是新增公共API或磁盘格式，也不是Canonical JSON。所有文本严格UTF-8，字符串/字节为uint32大端长度+字节；长度超uint32或CoreLimits拒绝。所有集合为uint32大端数量；bool/可空标记用单byte 0/1；ushort/uint32/ulong固定大端；SemVer为3个非负int32大端。可空值先写存在byte再写值；不存在不写正文。枚举用此§4.3声明顺序从0起的uint32编号，非法值拒绝。以下“数字文本”一律§4.2规范，不用BinaryWriter默认小端/文化格式；unit的None精确为字符串`None`。

| 摘要域（第一个长度前缀字符串） | 后续字段精确顺序 |
|---|---|
| `asun-config-binary-v2/definition` | Id、Version、SchemaVersion、UnknownPolicy；Parameters按Key排序：Key、Kind、Unit、Required、DefaultValue存在性及(Kind/Unit/规范Text)、DecimalBounds存在性及Min/Max/Step逐项存在性及规范decimal文本、DoubleBounds存在性及Min/Max存在性及规范double文本、AllowedValues ordinal排序、Sensitive；Constraints按Id排序：Id、LeftKey、Relation、RightKey。 |
| `asun-config-binary-v2/content` | ContractMajor、SchemaVersion、Definition内容摘要（64hex文本）；Values按Key排序：Key、Kind、Unit、规范Text；UnknownFields按Key排序：Key、原Utf8Value。 |
| `asun-config-binary-v2/value` | 类别byte（0=已知值），Kind、Unit、规范Text。opaque不公开值摘要。 |
| `asun-config-binary-v2/save` | ConfigKey两字符串、OperationId、ExpectedRevision、内容摘要、Source.Type/Id/Version/ContentSha256、AppliedDefaultKeys按ordinal排序的字符串集合。 |

各域SHA-256输出64小写hex。Definition.ContentSha256不参与自己的摘要；Content不含ConfigKey/Source/AppliedDefaultKeys/OperationId/Revision/时间，便于内容复用；Save身份保留来源及默认使用标记，避免同内容不同持久元数据被误认同请求。AppliedDefaultKeys是调用方可构造的来源标记，不是经过认证的审计事实。定义Version只要求§4.1非空有界文本，结构Schema必须精确SemVer；定义内容或Version变动会改变Definition摘要。AllowedValues排序不改变成员含义；约束Id必须唯一，同关系不同Id不去重。序列化字段之间不存在裸拼接，空串、缺失和空集合可区分。

规范化decimal用InvariantCulture格式`0.############################`（28个可选小数位，无指数/多余尾零），零单独写0；Double用R，±0写0；整数用Invariant无前导+。原文本`0020`与`20`在Int32同单位下同摘要，String下不同；URI大小写或转义字面变化仍不同。旧codec/v1历史摘要不重新计算覆盖；未知codec的载荷拒绝，不把读取成功当语义兼容。

### 5.1.1 固定四域Golden与边界反例

合成输入：Definition.Id=d、Version=1、Schema=1.0.0、UnknownPolicy=Reject，唯一参数x为Boolean/None、Required=true、Default/两种Bounds=null、AllowedValues=[]、Sensitive=true，Constraints=[]。Candidate为ConfigKey=(c,s)、ContractMajor=1、x=true、Unknown=[]、AppliedDefaultKeys=[]；Source=(T,I,V,SHA256空字节)，OperationId=o、ExpectedRevision=0。Source摘要为e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855。这些只是协议例，不是客户参数。

**Definition**：96 bytes；SHA-256=cb2edb50719b147c79263bbd80f8c407a4ca30850f72189d8f0f2f4a77ba7c85。

```text
000000206173756e2d636f6e6669672d62696e6172792d76322f646566696e6974696f6e000000016400000001310000000100000000000000000000000000000001000000017800000000000000044e6f6e6501000000000000000100000000
```

**Content**：148 bytes；SHA-256=119e5544ec5faab79c799ca4bf3f7bb6ff068b2071afb8dc1ced1891f9b4ffc0。

```text
0000001d6173756e2d636f6e6669672d62696e6172792d76322f636f6e74656e740001000000010000000000000000000000406362326564623530373139623134376337393236336262643830663863343037613463613330383530663732313839643866306632663461373762613763383500000001000000017800000000000000044e6f6e65000000047472756500000000
```

**Value**：52 bytes；SHA-256=9c9c3a9d09d5905b49a1a43f500b17d31a023a08a7dfc6113502bd40915dd3a0。

```text
0000001b6173756e2d636f6e6669672d62696e6172792d76322f76616c75650000000000000000044e6f6e650000000474727565
```

**Save**：208 bytes；SHA-256=cbbd2211219122ea42311f9a7fa31fefdcb4386d7f70a89d02c8ed60626faad8。

```text
0000001a6173756e2d636f6e6669672d62696e6172792d76322f7361766500000001630000000173000000016f00000000000000000000004031313965353534346563356661616237396337393963613462663366376262366666303638623230373161666238646331636564313839316639623466666330000000015400000001490000000156000000406533623063343432393866633163313439616662663463383939366662393234323761653431653436343962393334636134393539393162373835326238353500000000
```

以上字节按§5.1字段独立逐项拼接后SHA-256，本轮在内存中重建核对；并非调用未来产品codec生成Expected。Value域只定义普通值摘要编码：此例虽可核算法字节，Sensitive=true时Compare必须将两值摘要置null，不能因有Golden就向UI泄露。实现测试须同时核全文bytes、长度、hash和敏感输出屏蔽。

排序比较明确采用.NET StringComparer.Ordinal的UTF-16 code unit次序：U+10000（D800 DC00）排在U+E000之前，不能改用Unicode标量或UTF-8字节序。计长仍以严格UTF-8字节数为准；Unicode标量限额与排序不是同一规则。文本字节长度>uint32.MaxValue及checked总长溢出均CFG-002，必须在写uint32/分配前拒绝；当前.NET string/byte[]实际容器界限可能更低，先执行CoreLimits和BCL容器界限，绝不截断转uint32。Golden不要求分配4 GiB：测试长度计账分支使用受测内部有界计长单元和checked边界，并核正常多字节文本真实长度。

反例：Boolean TRUE拒绝；Int32 +0020规范20；Decimal -0.00、Double -0均规范0；decimal 1.00000000000000000000000000001不能精确表示，拒绝而非舍入1；孤立D800拒绝；x置Unknown或RawUnknownField.Key与字典键不一致拒绝；换Source只改变Save域，换Sensitive改变Definition及Content；换同等数值文本不改变规范Content；敏感Changed只给存在性/种类，无明文或值摘要。

### 5.2 显式迁移

迁移是C2无UI能力，Core不加载程序集/脚本。Host注入IMigrationProvider，按精确(SourceSchema, SourceDefinitionSha256, TargetSchema, TargetDefinitionSha256)检索；零条CFG-007，多条CFG-007歧义，不自动搜索路径。provider返回稳定PlanId/Version/ArtifactSha256，需与Host批准的PlanIdentity完全一致。多跳由Host逐段确认；没有默认回退/删除/单位转换。

Provider输入是已复核原NormalizedCandidate和已sealed目标Definition，输出RawConfiguration和逐项Change报告。允许Rename/Add/Remove/UnitConvert/ValueConvert/DropOpaque；每项列来源键/目标键、公式或规则ID、精度/rounding说明和Lossy。涉及实际单位系数、精度或不可逆丢失必须由参数Owner批准具体计划，不能开发者猜。未批准计划CFG-007，不执行。

Service检查原件、计划身份、容量、所有受影响字段和opaque是否在报告中；报告条数≤MaxMigrationChanges，计划/报告文本也受主Core的单文本与总UTF-8预算限制，复制前检查，不能只约束目标参数。对目标CreateCandidate/Normalize，失败不输出成功候选。自动补默认也须列Add；禁止provider同时替换ConfigKey/Source。报告不含敏感原值/目标值；输出完整候选、变更报告、原/目标内容摘要及计划身份。迁移不写Store，不分配OperationId、不递增Revision、不激活。Host审核后另发新Save。损坏源摘要CFG-017不能“修复后迁移”，保留原件交Owner恢复。

## 6. 无UI同步/异步入口

### 6.1 Core调用约定

§4.3为全部同步入口。Core共享实例可并发处理不同输入，无静态可变状态、注册/反注册、后台队列或Dispose。工厂参数非法拒构造，业务字段错误按§7；异常不带值/路径。Core不能捕获错误后返回空候选。调用方不得一边修改输入一边调用；接收完成后再改原dictionary不会改变输出。

### 6.2 Service Module API Contract v0.2

以下类型唯一位于 `Asun.Modules.Configuration.Service`，引用§4.3，不复制Candidate。公开record/struct须在入口复核，空配置身份、空ID、非法枚举、负/无限预算、越界分页、null端口拒绝。唯一公开static工厂类为 `ConfigurationServiceFactory`，公开static方法签名为 `IConfigurationService Create(ConfigurationServiceOptions options, IConfigurationCore core, IConfigurationStore store, IConfigurationClock clock, IMigrationProvider? migrations)`。无隐式默认存储、Clock、迁移或环境目录。

```csharp
using System;
using System.Collections.Generic;
using System.Collections.Immutable;
using System.Threading;
using System.Threading.Tasks;
using Asun.Modules.Configuration;
namespace Asun.Modules.Configuration.Service;

public readonly record struct ConfigKey(string ConfigurationId, string ScopeId);
public readonly record struct OperationKey(ConfigKey Key, string OperationId);
public enum SaveOutcome { Committed, Conflict, Rejected, NotCommitted, Unknown }
public enum ResourceState { Released, Draining, DrainUnknown }
public enum LookupOutcome { Found, NotFound, Unknown }
public enum LoadOutcome { Found, NotFound, Unavailable, Corrupt }
public enum WatchKind { Committed, GapDetected }
public sealed record OperationBudget(TimeSpan Queue, TimeSpan Execution,
    TimeSpan CommitWait, TimeSpan Drain);
public sealed record ServiceLimits(int MaxQueuedOperations, long MaxQueuedBytes,
    int MaxConcurrentOperations, int MaxSubscriptions, int MaxPageSize,
    int MaxWatchBuffer, int MaxMigrationChanges, int MaxReadVersions,
    int MaxUnresolvedOperations);
public sealed record ConfigurationServiceOptions(ServiceLimits Limits,
    TimeSpan PollingInterval, ImmutableArray<ConfigurationCoreOptions> SupportedReadVersions);
public interface IConfigurationClock
{
    DateTimeOffset UtcNow { get; }
    long GetTimestamp();
    TimeSpan Elapsed(long startTimestamp);
    Task DelayAsync(TimeSpan delay, CancellationToken token);
}
public sealed record ConfigurationSnapshot(ConfigKey Key, ulong Revision,
    string OperationId, DateTimeOffset CommittedAtUtc,
    NormalizedCandidate Content, SourceRef Source);
public sealed record SaveRequest(OperationKey Operation, ulong ExpectedRevision,
    NormalizedCandidate Content, OperationBudget Budget);
public sealed record SaveReceipt(OperationKey Operation, string RequestSha256,
    SaveOutcome Outcome, ulong ActualRevision, ConfigurationSnapshot? Snapshot,
    DateTimeOffset DecidedAtUtc);
public sealed record SaveResult(SaveOutcome Outcome, ResourceState Resource,
    SaveReceipt? Receipt, string? ErrorCode);
public sealed record OperationLookup(LookupOutcome Outcome,
    SaveReceipt? Receipt, ResourceState Resource, string? ErrorCode);
public sealed record LoadResult(LoadOutcome Outcome,
    ConfigurationSnapshot? Snapshot, ResourceState Resource, string? ErrorCode);
public sealed record RevisionPage(ImmutableArray<ConfigurationSnapshot> Items,
    ulong LastRevision, bool HasMore);
public sealed record WatchRequest(ConfigKey Key, ulong AfterRevision,
    int BufferCapacity, OperationBudget Budget);
public sealed record ConfigurationEvent(ConfigKey Key, WatchKind Kind,
    ulong Revision, ulong LastDeliveredRevision, string? OperationId);
public sealed record CloseResult(ResourceState Resource, string? ErrorCode);
public sealed class ConfigurationServiceException : Exception
{
    public string Code { get; }
    public string MessageResourceKey { get; }
    public ResourceState Resource { get; }
    public ConfigurationServiceException(string code, ResourceState resource)
        : base("Configuration.Errors." + code)
    { Code = code; MessageResourceKey = Message; Resource = resource; }
}
public sealed record MigrationIdentity(string PlanId, string Version, string ArtifactSha256);
public enum MigrationChangeKind { Rename, Add, Remove, UnitConvert, ValueConvert, DropOpaque }
public sealed record MigrationChange(MigrationChangeKind Kind,
    string? SourceKey, string? TargetKey, string RuleId,
    string PrecisionAndRounding, bool Lossy);
public sealed record MigrationPlan(MigrationIdentity Identity,
    SemanticVersion SourceSchema, string SourceDefinitionSha256,
    SemanticVersion TargetSchema, string TargetDefinitionSha256);
public sealed record MigrationInput(NormalizedCandidate Source,
    DefinitionSet TargetDefinitions, MigrationIdentity ApprovedPlan);
public sealed record MigrationOutput(RawConfiguration Target,
    ImmutableArray<MigrationChange> Changes);
public sealed record MigrationResult(NormalizedCandidate Candidate,
    MigrationPlan Plan, ImmutableArray<MigrationChange> Changes,
    string SourceContentSha256, string TargetContentSha256);
public interface IMigrationProvider
{
    Task<ImmutableArray<MigrationPlan>> FindPlansAsync(MigrationInput input, CancellationToken token);
    Task<MigrationOutput> ExecuteAsync(MigrationPlan plan, MigrationInput input, CancellationToken token);
}
public interface IConfigurationService
{
    Task<LoadResult> LoadAsync(ConfigKey key, ulong? revision,
        OperationBudget budget, CancellationToken cancellationToken);
    Task<SaveResult> SaveAsync(SaveRequest request, CancellationToken cancellationToken);
    Task<OperationLookup> QueryOperationAsync(OperationKey operation,
        OperationBudget budget, CancellationToken cancellationToken);
    Task<RevisionPage> ListRevisionsAsync(ConfigKey key, ulong afterRevision,
        int pageSize, OperationBudget budget, CancellationToken cancellationToken);
    Task<MigrationResult> MigrateCandidateAsync(MigrationInput input,
        OperationBudget budget, CancellationToken cancellationToken);
    IAsyncEnumerable<ConfigurationEvent> WatchAsync(WatchRequest request,
        CancellationToken cancellationToken);
    Task<CloseResult> CloseAsync(TimeSpan drainTimeout);
}
public sealed record StoreSaveRequest(SaveRequest Request, string RequestSha256,
    DateTimeOffset RequestedAtUtc);
public interface IConfigurationStore
{
    Task<LoadResult> LoadAsync(ConfigKey key, ulong? revision, CancellationToken token);
    Task<SaveResult> TrySaveAtomicAsync(StoreSaveRequest request, CancellationToken token);
    Task<OperationLookup> QueryOperationAsync(OperationKey operation, CancellationToken token);
    Task<RevisionPage> ListRevisionsAsync(ConfigKey key, ulong afterRevision,
        int pageSize, CancellationToken token);
}
```

唯一Store名称是IConfigurationStore，不能另引入IConfigStore/ConfigRepository第二事实源。Store返回的record同样重验：键/摘要/修订/回执互相一致，Load重验定义与内容；损坏Corrupt/CFG-017，不补默认产生新snapshot。load revision=null是最新；指定revision=0非法，NotFound只指确实无该修订。

端口Task是实际资源退出信号，不只是“响应已经发送”：Store.Load/TrySaveAtomic/List每个Task成功、失败或取消完成时，该次调用已不再使用输入/连接/文件/锁，返回对象的Resource必须Released；不能完成Task后仍持有这些资源，却返回Draining而不给等待句柄。Query自己的读取资源也必须在Task结束时归还，其OperationLookup.Resource可报告**原操作**尚在另一Owner手中的状态；原Task由原调用者保留或由权威fence隔离，不能只靠Query结束推定原写入退出。若返回记录违反约定，Service保留未决身份，报CFG-017/Unknown；该适配器不能通过资源验收。Service的Draining/DrainUnknown由其持有的尚未完成端口Task及在途投影生成，Host共享Store必须等待所有使用它的Owner退出才能Dispose。

SupportedReadVersions是Host显式批准的不可变读版本列表，数量1..MaxReadVersions，按(ContractMajor,SchemaVersion)唯一且必须包含主Core.Options完全相同的一项；Options只返回工厂深复制的只读配置。Service仅通过同一ConfigurationModuleFactory为这些条目构造验证Core，不自动扩展版本、不读取产品定义注册表。Load、历史、Query已提交回执和迁移源按载荷的精确版本选匹配读Core重验；未批准读版本CFG-003，不重算覆盖历史。写入/迁移目标只用主Core的精确版本；历史页出现不支持版本则明确拒绝整页，不能静默过滤丢水位。当前codec-v2只能按其已知语义读取，旧codec-v1仍需对应旧包显式读取，不靠新Core模拟兼容。

RevisionPage按revision严格升序，afterRevision排他，LastRevision为空页等于afterRevision否则最后一项；HasMore由同次权威读取决定。历史版本本设计不删，所以无正常缺口。分页/Watch数据损坏、版本不支持、端口不可用/预算失败用ConfigurationServiceException(CFG-017/003/009/012, Resource)，不以空页冒充成功。成功页对应本次读取资源已Released。Load/Lookup使用类型化Outcome表达不可用与未知，不缓存NotFound；Load Found含snapshot，其余snapshot=null，版本不支持为Unavailable/CFG-003。查询预算到期返回Unknown，不会关闭Store或取消原提交。Load.Resource表示本次读取；Lookup.Resource取原操作已知资源与本次查询资源两者较差状态，不用查询已结束推定原操作已排空；进程重启fence确认后原操作可Released，即使知识仍Unknown。

SaveReceipt只容许Committed/Conflict/NotCommitted。Committed含非null Snapshot、ActualRevision=Snapshot.Revision；Conflict含当前revision、Snapshot=null；NotCommitted含确认的当前revision、Snapshot=null。Rejected是当前请求未接纳的新尝试（输入/容量/关闭或原ID不同请求拒绝），Receipt=null；Unknown也Receipt=null。Outcome和Resource独立，Conflict/NotCommitted也可能资源Draining。Store持久快照时间由Store在提交锁/事务内取UTC，RequestedAtUtc仅请求观测，不是提交顺序；Revision才是顺序。

所有预算显式有限正值，Queue/Execution/CommitWait/Drain分别限制接纳队列等待、合作执行期限、结果等待、资源排空观察；不得通过TimeSpan.MaxValue或Timeout.Infinite关掉。CloseAsync的drainTimeout、ConfigurationServiceOptions.PollingInterval也必须是有限正值；Watch BufferCapacity为1..MaxWatchBuffer。时间比较只用Clock单调时间，UTC只记录事实。PollingInterval和limits在options仅定义一次。入队数量/字节超限CFG-002；并行总数受限，按ConfigKey维护有界队列，同键串行只降低本进程冲突，Store的跨进程CAS仍必需。同OperationKey已在本服务Queued/Executing时，同摘要调用只等待/查询原Task，不再入队；不同摘要CFG-018。Query必须先核本地已接纳请求索引，尚未到Store的排队操作返回Unknown/Draining，不能让Store暂时NotFound误导重试。

期限从阶段进入的单调timestamp计算，Queue从接纳排队开始，Execution从真正启动端口开始；执行期限/用户取消先发合作取消，再以CommitWait观察Save结果，仍无证据返回Unknown；Drain观察取消至资源退出，总观察期限有限且不在循环重置。查/读/迁移到Execution期限后仅观察Drain，不叠加Save的CommitWait。计时/轮询只用Clock.DelayAsync，支持0延迟立即完成但不允许无限delay；Clock必须及时响应token且同步成员不阻塞。ManualClock推进时同时唤醒已到期Delay，系统实现用Stopwatch/UTC和Task.Delay，取消timer任务本身也须退出。

MigrateCandidateAsync限量、无IO：源使用SupportedReadVersions的精确验证Core，目标使用主Core；二者limits分别执行，任一未批准版本CFG-003。两provider方法都在Service注册为在途Task并受同一次Execution/Drain期限、并行槽位和Close管理。provider只能执行已批准的有界纯转换，不读网络/设备/Store或持有native资源；其方法须立即返回Task而不能在返回前长时间阻塞，循环合作检查token。超时/取消不输出成功候选，以ConfigurationServiceException(CFG-012/011, Resource)表达资源状态并保留真实Task；无provider或计划错误CFG-007。provider不合作时资源DrainUnknown，不能以“纯计算”提前释放槽位。此合同不提供无限同步迁移入口。

## 7. 状态、错误、事件与资源Owner

### 7.1 稳定错误与恢复

| Code | 触发 / 下一步 |
|---|---|
| CFG-001 InvalidArgument | null/default结构、非法标识/Unicode/重复原始键；修正输入重建候选。 |
| CFG-002 CapacityExceeded | 字段/文本/opaque/队列/历史容量超限；拒绝本次，调整已批准Profile或减少输入。 |
| CFG-003 VersionMismatch | Contract/精确Schema不匹配或比较不同ConfigKey；选匹配版本或明确迁移。 |
| CFG-004 InvalidDefinition | 无效定义/单位/范围/默认/枚举/约束引用或定义摘要不符；由定义Owner修正。 |
| CFG-005 InvalidValue | 必填、值、类型/单位/范围/约束失败；修正完整候选。 |
| CFG-006 UnknownField | 当前策略不允许Unknown；升级定义或批准显式迁移。 |
| CFG-007 MigrationRejected | 无计划/歧义/身份未批准/报告不完整/转换失败；保留原件。 |
| CFG-008 RevisionConflict | CAS期望不匹配；读最新、显示差异，人决定新候选/新操作。 |
| CFG-009 StoreUnavailable | 读取失败、权限/磁盘/连接不可用；保留原身份，先查询，不猜未提交。 |
| CFG-010 AtomicCommitFailed | 已确认事务未提交；须带NotCommitted回执才允许当最终失败。 |
| CFG-011 Cancelled | 接纳前取消或已权威确认未提交；已接纳提交未知仍用CFG-013。 |
| CFG-012 DeadlineExceeded | 队列/执行/等待预算到期；提交未知仍用CFG-013，资源未退出按第二轴。 |
| CFG-013 UnknownOutcome | 无法确认原提交；冻结本键写入动作，使用原OperationKey查询。 |
| CFG-014 ServiceClosed | 服务停接纳；排空/查询职责转给宿主仍拥有的Store。 |
| CFG-015 RevisionExhausted | ulong.MaxValue不能新提交；只读和原操作查询仍可用。 |
| CFG-016 WatchGap | 缓冲溢出/水位不连续；从LastDeliveredRevision分页补读。 |
| CFG-017 IntegrityMismatch | 内容/载荷/回执hash、键、修订或磁盘manifest损坏；隔离，不生成默认替代。 |
| CFG-018 OperationIdentityMismatch | 同OperationKey不同RequestSha256；原回执保持，不执行新请求。 |
| CFG-019 AccessDenied | UI/Host当前授权拒绝或失效；保原工作项，只允许重新取得当前授权后执行合适恢复；Core不裁权限。 |

每码资源键为 `Configuration.Errors.CFG-xxx`；诊断RelatedKeys不带值/路径。Validate可同时返回多个CFG-005/006，结构错误则CoreException；Normalize无效时按同一稳定排序的首项抛CoreException，Host可先Validate取得全量诊断。Save接纳前非法输入用Rejected/Released，输入验证错误保留首个稳定错误码。Store抛异常一旦可能越过提交边界服务返回Unknown，绝不能默认转换CFG-010。Service异步迁移/分页/Watch使用ServiceException以表达资源状态；不扩散厂商异常或敏感消息。

### 7.2 Save与关闭状态

内存阶段：Received→Validated→Queued→Executing→WaitingResult，终端知识为Committed/Conflict/NotCommitted/Unknown。Rejected只能在当前请求的新尝试尚无持久意图/写入且确知未接纳时返回；只读查询到原ID不同请求也可Rejected/CFG-018，原事实不变。预算/取消在Validated/Queued移除成功可Rejected，Executing后必须查询权威。Committed不可因通知失败/取消变回NotCommitted。

资源轴：真实在途完成并不再访问输入/Store/回调才Released；合作退出中Draining；Drain期限到仍未完成DrainUnknown。保留原Task、CTS、限额槽位和输入租约，任务迟到时核验结果更新查询视图并只释放一次，不能将超时的Task丢弃。CFG-013不是独立新事实，原操作仍只有一个Owner。

仅保留正在排队/执行和未决恢复的内存索引，完成且确认终态的Task/键锁退出后移除，不无限缓存所有历史ConfigKey/回执。知识Unknown但资源Released时保留最小未决身份/摘要元数据（完整候选仍由Host原工作项保管），数量受MaxUnresolvedOperations限制；接纳时保留该槽位，达上限拒新尝试CFG-002，不丢旧未决记录。原查询确认终态且资源Released才归还；本键未决期间第二个新ID保存拒绝CFG-013，原ID只能查询/等待。

Close第一次调用停接纳新Save/Load/Watch/迁移，移除未执行队列，停新Watch生产并合作取消；等待所有正在执行端口/枚举退出。重复Close复用同一关闭任务，新的drainTimeout仅限制该次观察，不重做/Dispose。未退出返回DrainUnknown，宿主保留服务/Store资源和查询原Task的能力；Closed服务的公开Query返回CFG-014，宿主用仍拥有的Store.QueryOperationAsync恢复，不能先Dispose Store。全部退出才Released；Service不Dispose宿主Store/Clock/provider。

Watch枚举取消/Dispose只结束该订阅，不Close服务；UI解绑不Close共享服务。Service不在Dispatcher运行IO。消费者UI仅在自己的Dispatcher投影；回调/异步枚举不得阻塞Save，也不能获得质量或设备写入权限。


## 8. CAS、原操作恢复与真实持久化

### 8.1 接纳和事务步骤

1. Service重验请求、NormalizedCandidate完整内容与摘要，要求Operation.Key等于Candidate身份，Candidate.Source合法，Store生成Snapshot.Source必须与其完全相等；不让Host传RequestSha256。服务先深复制并Normalize，核原摘要后把规范副本交Store，不能只验证hash却持久原来的非规范文本。按§5.1计算请求身份，预算不进入请求身份，重试可换等待预算而不能换内容/来源/默认标记/ExpectedRevision。
2. 宿主在第一次Save前把OperationKey/ExpectedRevision/规范候选保存在自身可恢复工作项中；Service不生成ID。没有该能力的工具只能称单进程试用，不能承诺窗口/进程关闭后恢复。
3. Store取得配置键的权威串行锁/事务，先查原操作。已存在同摘要终态直接原样返回；不同摘要CFG-018。已有Pending不得启动第二次，返回Unknown/查询；在途先排空/被跨进程隔离后才能恢复Pending。同键还有其它Pending时先恢复/对账这些原身份，未解决不得接纳新ID；重启后也不靠新服务丢失内存索引来绕过此门。
4. 未见原操作时先为其检查容量、保留恢复槽位并耐久记录Pending意图（含完整请求身份及期望修订）；此时尚无新版本。查询NotFound只有权威检查确认无意图/回执/在途且已隔离旧写入者时允许。
5. 在同一配置写锁/事务中检验ExpectedRevision与实际最新。冲突原子记录原Conflict回执，不改snapshot；符合则检查revision未耗尽、完整候选hash，再提交新不可变snapshot、revision索引、原Committed回执及Pending终结。三者同事务，不能“先成功写文件，再另写操作日志”。
6. 确认提交才返回Committed。已确认未提交且能完成原NotCommitted终态记录才返回NotCommitted；单纯异常/超时/连接断开都Unknown。已经durable的Conflict/NotCommitted重试返回原回执，修ExpectedRevision或修候选必须新OperationId。
7. Watch从已提交历史投影；通知延迟/失败不更改Save回执。Service本地缓存只是查询辅助，Store在重启后必须同原OperationKey恢复。

Pending恢复不是猜提交：在权威锁下fence旧进程/事务，验证当前完整状态；有同操作Committed原回执便Committed；完整权威状态只有Pending且确认不可能迟到提交，写原NotCommitted终态后才可终结。无法fence、manifest损坏或存储响应不明保持Unknown。Query的Found只代表已决定回执；Pending为Unknown，不用“查不到快照”当NotFound。

同键两个ExpectedRevision=0新ID同时请求，至多一个Committed revision=1，另一个Conflict actual=1；不同Scope独立。相同内容的新ID正确CAS仍生成revision。ulong.MaxValue时CFG-015拒新提交，原回执/Load/历史仍可读取。历史snapshot和全部回执必须保留；无已批准保留/压缩协议时禁止GC，达到容量只拒新操作，原操作查询保留。

### 8.2 取消、期限与等待

| 位置 | 行为 / 可判定结果 |
|---|---|
| 未接纳或仍在队列，且确认移除 | Rejected/Released、CFG-011或012；无Store调用和持久意图。 |
| Store已开始但合作取消，尚未确认事务 | 发合作取消，保留原Task和限额；等待CommitWait，仍不确定Unknown。 |
| 事务已提交但响应/通知丢失 | Query原操作得Committed，取消不能撤回或改终态。 |
| 只确认业务终态，资源仍使用 | 结果Committed/Conflict/NotCommitted，Resource=Draining或DrainUnknown；不提前Dispose资源。 |
| 等待与真实Task同时结束 | 先观察已完成Task并核验回执；Commit证据优先于本地取消。 |
| drain超过预算 | Resource=DrainUnknown；保留Owner/Task，禁止第二次本键未决写入，宿主查询原操作。 |

CancellationToken只是合作停止请求，不是事务撤销证明。Service不将已接纳Save裸抛TaskCanceledException令调用方误认“没保存”；每条可观察返回都有SaveResult，错误输入除构造前argument验证外也按Rejected。Load/历史取消只停止本次读取，不能取消另一个Save；读取资源仍需真实Task退出后归还。Close超时和原操作未知两轴独立，不以“窗口已关闭”清理IO缓冲。


### 8.3 本地文件Store合同（A1-F）

此切片独立于数据库实现，namespace为Asun.Modules.Configuration.Adapters；只依赖Service/Core和net10 BCL。适用Windows同机本地固定卷，不支持UNC、映射网络驱动器、共享盘、跨主机。目标卷实际ProcessCrash/PowerLoss资格留后门，装配/wire/恢复算法由本节冻结。

~~~csharp
public sealed record FileStoreOptions(string RootDirectory, string MutexNamespace,
    TimeSpan LockTimeout, TimeSpan IoObservationTimeout, TimeSpan CloseTimeout,
    long MaxManifestBytes, long MaxSnapshotBytes, long MaxTotalBytesPerKey,
    int MaxRevisions, int MaxOperationRecords, int MaxJsonDepth,
    int MaxConcurrentIo, int MaxQueuedIo, long MaxQueuedBytes);
public interface IConfigurationFileStore : IConfigurationStore
{
    Task<CloseResult> CloseAsync(TimeSpan drainTimeout);
}
// 同namespace唯一public static class ConfigurationFileStoreFactory：
// public static IConfigurationFileStore Create(FileStoreOptions options,
//     IConfigurationCore writeCore,
//     ImmutableArray<ConfigurationCoreOptions> supportedReadVersions,
//     IConfigurationClock clock);
public enum FileOperationState { Pending, Committed, Conflict, NotCommitted }
public sealed record FileRevision(ulong Revision, string OperationId, string BlobSha256);
public sealed record FileOperation(string OperationId, string RequestSha256,
    ulong ExpectedRevision, string ContentSha256, SourceRef Source,
    ImmutableArray<string> AppliedDefaultKeys, FileOperationState State,
    SaveReceipt? Receipt);
public sealed record FileManifest(ConfigKey Key, ulong Generation, ulong LatestRevision,
    ImmutableArray<FileRevision> Revisions, ImmutableArray<FileOperation> Operations);
public sealed record FileEnvelope<T>(string Format, string Codec, T Body, string BodySha256);
~~~

这些公开wire DTO在Adapters，不复制核心值；FileEnvelope<FileManifest>与FileEnvelope<ConfigurationSnapshot>为唯二磁盘根。代码块是Asun.Modules.Configuration.Adapters的合同片段，using System、System.Collections.Immutable、System.Threading.Tasks、Asun.Modules.Configuration、Asun.Modules.Configuration.Service。Create只校options/深复制、核已存在root和路径安全、构造纯托管状态，不建文件/不启动后台IO；失败无在途借用。RootDirectory由Host预先创建，必须是绝对路径，Path.GetFullPath后仍在同一固定本地卷；拒相对、UNC、drive-relative、设备路径及root/既有祖先/子目录reparse point。Host管理root ACL，模块不自动提权；恶意本地管理员不属于hash防御能力。MutexNamespace为显式ASCII [a-zA-Z0-9_.-]{1,64}，同root各进程必须相同；Global命名mutex跨同机session，权限不足CFG-009，不悄悄退Local。

上限>0、预算有限正；MaxManifestBytes/MaxSnapshotBytes≤int.MaxValue，驻留缓冲≤Array.MaxLength，MaxTotalBytesPerKey≥两者之和（checked），还须容纳下一manifest/backup/blob及终态回执；MaxJsonDepth≥32。SupportedReadVersions按Service唯一规则含writeCore.Options。MaxRevisions/MaxOperationRecords满只拒新，不GC，原ID Query/重试保留。IoObservationTimeout用于worker执行观察并在到期发合作停止信号，不能截断原Task；Service/Host外层等待用其自己的明确预算，真实IO Task仍到退出才完成。CloseTimeout为Host默认关闭观察，CloseAsync可另传有限预算；root归Host，Close只关闭自己worker/文件/mutex/CTS，不删目录。

### 8.3.1 唯一JSON wire与完整性字节

键目录名=SHA256(域文本asun-config-file/key-v1、ConfigurationId、ScopeId，均按§5.1长度前缀UTF8)；完整Key再次核验防错误映射。目录内current.json、backup.json、blobs/<BlobSha256>.json、Guid.NewGuid的N小写格式tmp-*.json；创建/打开前核root范围与reparse点，固定同卷，不把Key当路径。

规范写出UTF8无BOM、无空白/尾换行；net10 Utf8JsonWriter，Indented=false、SkipValidation=false、Encoder=System.Text.Encodings.Web.JavaScriptEncoder.Default。字段总是写出，null写JSON null，集合写数组。字段顺序按表，不依赖反射/字典枚举。enum写声明名称，ushort/非负int写JSON整数；所有ulong/long写无前导零十进制JSON字符串，decimal/double Bounds写§5.1规范文本或null；bool写true/false。此JSON不是二进制codec，不混用hash。

| 对象 | JSON字段精确顺序与映射 |
|---|---|
| Envelope | format、codec、body、bodySha256；format分别asun-config-manifest-v1 / asun-config-snapshot-v1，codec固定asun-config-binary-v2。 |
| Manifest | key、generation、latestRevision、revisions、operations；revisions按revision数值升序、operations按OperationId UTF-16 ordinal。 |
| ConfigKey | configurationId、scopeId。 |
| FileRevision | revision、operationId、blobSha256。 |
| FileOperation | operationId、requestSha256、expectedRevision、contentSha256、source、appliedDefaultKeys、state、receipt；默认keys ordinal排序。 |
| SaveReceipt | operation、requestSha256、outcome、actualRevision、snapshot、decidedAtUtc。operation对象为key、operationId；Committed内联完整snapshot（与blob相同），其余snapshot=null，不以“可外部查”代替原回执。 |
| Snapshot | key、revision、operationId、committedAtUtc、content、source。 |
| NormalizedCandidate | candidate、contentSha256。 |
| Candidate | configurationId、scopeId、contractMajor、definitions、values、unknownFields、appliedDefaultKeys、source；values/unknownFields为按Key ordinal排序对象数组，不用动态属性字典。 |
| Known条目 / ParameterValue | key、value / kind、unit、text。 |
| RawUnknownField | key、utf8Value；标准base64带padding无空白，解码后严格UTF8，不重编码改变原字节。 |
| DefinitionSet | id、version、schemaVersion、unknownPolicy、parameters、constraints、contentSha256。 |
| SchemaVersion | major、minor、patch。 |
| ParameterDefinition | key、kind、unit、required、defaultValue、decimalBounds、doubleBounds、allowedValues、sensitive；parameters按Key，allowedValues按ordinal。 |
| DecimalBounds / DoubleBounds | minimum、maximum、step / minimum、maximum；可空数值为规范文本。 |
| FieldConstraint | id、leftKey、relation、rightKey；constraints按Id排序。 |
| SourceRef | type、id、version、contentSha256。 |
| 时间 | UTC DateTimeOffset以Invariant格式yyyy-MM-dd'T'HH:mm:ss.fffffff'Z'，offset=0、七位小数，不猜本地时区。 |

BodySha256=SHA256(规范body对象完整UTF8 bytes)小写hex，Envelope不进入BodyHash；BlobSha256=SHA256(整个规范snapshot Envelope bytes)。不同来源/修订/时间可同ContentHash但必须不同blob，不用ContentHash覆写元数据。manifest内联回执snapshot与blob按规范bytes相等；再复核§5.1定义/内容/Save请求hash。hash不是签名/权限或加密。

严格解析：有界读取Max*Bytes+1即超限拒绝，不能先ReadAllBytes无界；Utf8JsonReader MaxDepth=options、CommentHandling=Disallow、AllowTrailingCommas=false，拒BOM/重复或未知属性/漏字段/非法enum、非规范数字/时间/base64、坏UTF8、null集合、ordinal重复键、尾随token。每对象允许字段集固定，分配前核数量与字节，所有计数checked。按表重编码body核BodyHash，并要求完整输入等规范Envelope bytes（拒字段乱序/空白/不同escape字面）。损坏CFG-017，不自动修复/改hash写回。

不变量：generation≥1，每次替换+1不回绕；latest=0则revisions空，否则从1连续至latest；每revision唯一同操作Committed回执和同blob。OperationId唯一，Pending receipt=null，其余receipt非null且Outcome等state，request/content/source/default标记与意图一致；Conflict/NotCommitted不增revision。Committed时间/Source/Content一致，原DecidedAt重试不改。current引用blob必须存在且双层hash正确。孤立blob/tmp保留但不算提交。

### 8.3.2 锁、原子事务、fence与错误恢复

mutex名为Global命名空间下<MutexNamespace>.configuration.<keyHash>，同root有唯一稳定namespace。锁覆盖权威读、Pending替换、blob准备、最终manifest替换/回读；Load/Query/List同锁，不能无锁猜替换状态。named Mutex有线程所有权，固定worker线程同线程WaitOne/ReleaseMutex，锁内同步FileStream工作，不跨await释放。worker/排队/字节受options限制；有限轮询WaitHandle和取消事件，单调总LockTimeout不重置，禁止无限sleep。abandoned取得后先检查manifest。IoObservation超时合作取消，原IO Task到句柄/锁真实退出才完成；Close停接纳后排空worker。

1. 目录存在不是配置存在。持mutex，首次创建current前目录为空或仅确认未提交临时文件可NotFound；backup存在而current缺失Corrupt/Unknown。current完整为唯一权威，backup仅对账材料；backup损坏/较新/不同键保留并隔离写入，不按mtime选版本。
2. 查原ID：同RequestHash终态返回原receipt，不同hash Rejected CFG-018；Pending只恢复/查询。新ID遇其它Pending先fence对账。容量检查覆盖最坏最终manifest/backup/blob和终态回执预算；超限/锁未取得/revision耗尽等仅在Pending前且确认无该操作才Rejected。写Pending后不再声称未接纳。
3. Pending新manifest generation+1：tmp写完Flush(true)关闭→同卷替换，已有current用File.Replace(tmp,current,backup)，首次File.Move(tmp,current,overwrite:false)；读回核验。替换异常在持锁下读权威current，不以异常推未提交。
4. snapshot Envelope写tmp/Flush(true)/关闭、rename至blobs/hash.json；已有同名必须完整bytes相同。blob未引用不是提交。最终manifest generation+1原子加入revision、blob引用、原Committed回执并结束Pending；Flush/Replace/读回后Committed。CAS冲突只原子写Conflict。异常后已证Committed返回原Committed，无证据Unknown。
5. 完整current仅有Pending、无其Committed且revision一致，并已独占mutex且本进程原IO不存在/真实退出，旧写入者被fence，才生成原NotCommitted回执（Actual=latest、DecidedAt=clock.UtcNow），原子替换后Found NotCommitted。原worker仍执行时Query不能假装崩溃；查询排队获得锁后恢复。无blob不能单独证明未提交，必须完整manifest无commit引用。
6. current损坏/缺失但backup可能有事实、blob损坏/丢失、回执不一致、无法fence、replace后不能读，保持Corrupt/Unknown并禁新写。不自动选backup、重建、删证据/重编号；当前无会丢事实的Repair API。
7. CloseAsync首次停接纳、排空所有worker/句柄/mutex，重复只观察同关闭工作；根Owner强持迟到Task。Released仅指本Store退出，失败/取消也到真实退出才完成原Task。

无自动GC/清历史/用户配置。总目录容量含tmp/blob/backup（有界枚举，条目>2*MaxRevisions+2*MaxOperationRecords+8硬拒写并诊断，checked计算），临时增长不无限。满时拒新而保原Query；磁盘满使NotCommitted也无法持久则Unknown。IO错误屏蔽敏感路径，按知识/资源两轴映射。

### 8.3.3 两个文件Host和真实故障验收落点

Adapters.Tests为net10.0 BCL Exe，引用Adapters/Service/Core。Program支持--host device|algorithm --root <absolute> --phase normal|child --crash <point>及--suite file，非法参数非零。Device/Algorithm完整参数/链沿§11.3.1，只把ScriptedStore替为FileStoreFactory，注入SystemClock；根Owner在两个factory前预留，原Task登记/工作项/cleanup相同。root由Host建；合成options：namespace=ConfigurationHarness、Lock=2s、IO观察=5s、Close=5s、manifest=4MiB、snapshot=1MiB、total/key=32MiB、revisions=32、operations=64、depth=64、并发=2、排队=16、字节=4MiB。同root同namespace，不同ConfigKey各独立版本；同键CAS另测。原工作项为Host私有harness文件，不放Store manifest替代调用方Owner；父程保存原身份，新child据它Query。

生产公开API无FaultInjector；Adapters内部断点通过InternalsVisibleTo唯一Tests连接私有harness命名事件。父程等AfterPendingFlush/AfterPendingReplace/AfterBlobFlush/AfterBlobRename/BeforeFinalReplace/AfterFinalReplace/BeforeResponse后，实际kill本次child tree并确认退出，再新child同root Query/Load/List。每child≤20s、父场景≤60s、全套外层300s，超时/门事件未到/进程未退出非零。计划dotnet build唯一Adapters工程-c Release（外层120s），dotnet run --project唯一Adapters.Tests工程-c Release -- --suite file（外层300s），具体命令见§13.1。

断言：final replace前完整Pending经fence原NotCommitted、无新revision；final replace后原Committed/revision1；Pending replace前权威无意图才NotFound；两进程CAS一Committed一Conflict；篡改/重复JSON键/错bodyHash/换blob/不连续revision均CFG-017隔离；只丢响应不重交；abandoned先校验；其它进程持锁不得fence或NotFound；reparse/相对/UNC拒绝；容量拒新保原；Close到期根Owner不释放，worker退出只归还一次。实际kill门可能落在原子替换前/后，必须核manifest与回执证据判完整旧/新态，不能按事件时间猜提交。ProcessCrash与目标卷PowerLoss/控制器缓存/FAT/SAT分开，未执行不声称通过。

### 8.4 数据库存储组合（A1-DB）

本节消费 [storage-database §6～6.3、§7.1.1～7.2](../storage-database/DEVELOPMENT-GUIDE.md#6-公开集成契约module-api-contract-v03-的-io-部分) 已接收的注册事务/窄读取/原操作查询合同。namespace仍为 `Asun.Modules.Configuration.Adapters`；新增引用为 `Asun.Platform.StorageDatabase.Contracts` 和Runtime的公开 `StorageRequestHasher`，配置Adapter不创建Runtime、不直连Npgsql、不提供SQL/表名/任意predicate接口。A1-F能力不调用SD端口，C1/C2引用不变。配置Owner独占Key、完整定义/候选、revision、Pending及原业务回执；storage-database拥有技术ledger、单写/fence、连接/事务与IO生命周期。数据库仅存参数与配置元数据，不存图像/点云。本文绑定指导内容于2026-10-11获主控限定接收；上游C1及本节内容接收不等于真实PostgreSQL后端接收。

Adapters/Adapters.Tests的计划ProjectReference精确指向 `src/Modules/storage-database/Asun.Modules.StorageDatabase.Contracts/Asun.Modules.StorageDatabase.Contracts.csproj` 与 `src/Modules/storage-database/Asun.Modules.StorageDatabase.Runtime/Asun.Modules.StorageDatabase.Runtime.csproj`（相对各工程目录计算引用路径）；不引用SD.PostgreSql/Npgsql或另一Host私有测试工程。注册Owner映射/codec及本节关系实现仍写配置Adapters允许目录，真实技术backend由Host通过SD公开BackendFactory注入，不能借本任务写上游工程。暂无产品工程，不把上述计划引用当已编译证据。

#### 8.4.1 完整装配、注册形状与公开调用

以下是本Adapter公开DTO/Factory声明；真实PostgreSQL marshal实现另见§8.4.1.1，除此不新增接线API。using System、System.Collections.Immutable、System.Threading.Tasks及Core/Service；`SD`别名指 `Asun.Platform.StorageDatabase.Contracts`。公开record同样在入口深复制/重验。

~~~csharp
using SD = Asun.Platform.StorageDatabase.Contracts;
public sealed record ConfigurationDbBindings(
    SD.VersionRef Prepare, SD.VersionRef Decide, SD.VersionRef Read,
    SD.VersionRef MutationSchema, SD.VersionRef MutationCodec,
    SD.VersionRef ReadSchema, SD.VersionRef ReadCodec,
    SD.VersionRef ResultSchema, SD.VersionRef ResultCodec);
public sealed record ConfigurationDbOptions(ConfigurationDbBindings Bindings,
    ImmutableArray<SD.StorageBindingDescriptor> BindingDescriptors,
    SD.CallContext Production, SD.CallContext Query, SD.CallContext Recovery,
    SD.StorageInputLimits StorageLimits, TimeSpan PollInterval,
    TimeSpan CloseTimeout, long MaxSnapshotBytes, int ChunkBytes,
    int MaxPageSize, int MaxOperationRecordsPerKey, int MaxRevisionsPerKey,
    long MaxBytesPerKey, int MaxActiveCalls, int MaxQueuedCalls,
    long MaxRetainedBytes, int MaxJsonDepth);
public interface IConfigurationDatabaseStore : IConfigurationStore
{
    Task<CloseResult> CloseAsync(TimeSpan drainTimeout);
}
// public static class ConfigurationDatabaseStoreFactory：
// public static IConfigurationDatabaseStore Create(ConfigurationDbOptions options,
//     IConfigurationCore writeCore,
//     ImmutableArray<ConfigurationCoreOptions> supportedReadVersions,
//     IConfigurationClock clock, SD.IStorageDatabase runtime);
public sealed record ConfigurationDbMutation(SD.VersionRef Schema,
    StoreSaveRequest Save) : SD.IOwnerStoragePayload;
public enum ConfigurationDbReadKind { Latest, Revision, History, Mutation, SnapshotChunk }
public sealed record ConfigurationDbSnapshotRef(ConfigKey Key, ulong Revision,
    string OperationId, long Bytes, string Sha256);
public sealed record ConfigurationDbRead(SD.VersionRef Schema,
    ConfigurationDbReadKind Kind, ConfigKey Key, string? OperationId,
    ulong? Revision, ulong AfterRevision, int MaxEntries,
    ConfigurationDbSnapshotRef? Snapshot, long Offset, int Count)
    : SD.IOwnerStoragePayload;
public sealed record ConfigurationDbReceiptRef(OperationKey Operation,
    string RequestSha256, SaveOutcome Outcome, ulong ActualRevision,
    ConfigurationDbSnapshotRef? Snapshot, DateTimeOffset DecidedAtUtc);
public enum ConfigurationDbMutationState { Absent, Pending, Decided, Blocked }
public sealed record ConfigurationDbOriginalMutation(ConfigurationDbBindings Bindings,
    SD.VersionRef RuntimeProfile, SD.OperationIdentity Prepare,
    SD.OperationIdentity Decide, ImmutableArray<byte> Bytes);
public sealed record ConfigurationDbResult(ConfigurationDbReadKind? ReadKind,
    ConfigKey Key, ulong LatestRevision, bool HasMore,
    ConfigurationDbMutationState MutationState,
    string? RequestSha256, ConfigurationDbReceiptRef? Receipt,
    ConfigurationDbOriginalMutation? OriginalMutation,
    ImmutableArray<ConfigurationDbSnapshotRef> Snapshots,
    ConfigurationDbSnapshotRef? ChunkSnapshot, long Offset,
    ImmutableArray<byte> Chunk);
// 仅以下公开构造；只实现上游已有接口，不加注册/查询入口：
// ConfigurationDbMutationCodec : SD.IStoragePayloadCodec
// ConfigurationDbReadCodec : SD.IStoragePayloadCodec
// ConfigurationDbResultCodec : SD.IStorageResultCodec
// Version/Schema来自本节冻结的注册规格；Encode/GetReferences/Validate沿SD接口。
// ConfigurationDbMutationCodec(ConfigurationDbBindings bindings, IConfigurationCore writeCore,
//     ImmutableArray<ConfigurationCoreOptions> supportedReadVersions)
// ConfigurationDbReadCodec(ConfigurationDbBindings bindings)
// ConfigurationDbResultCodec(ConfigurationDbBindings bindings)
~~~

三个codec的精确Version/Schema来自Host传入的受信任注册包；类名及构造器为上述ConfigurationDb完整前缀，不提供默认注册目录。MutationCodec用注入Core/获准read版本重验完整候选，不扫描产品注册表。Mutation/Read的 `PayloadType` 分别是上述精确sealed CLR type；`GetReferences`先核完整载荷合法，再返回 `ImmutableArray<SD.ObjectRef>.Empty`，所有事务/读取References为空。本模块没有技术文件对象引用；不得把配置快照分片装成图像对象或假ObjectRef。ResultCodec.Version=Bindings.ResultCodec、Schema=Bindings.ResultSchema，Mutation/Read同理。ResultCodec.Validate先有界解析再按下述tagged形状核验，不只检查JSON语法。

空宿主装配顺序固定：进程根Owner预留slot/最大strong-root bytes → 构造writeCore、read-version列表、配置clock、本节options及注册codec → 注入 `SD.StorageRuntimeDependencies(resolver, backendFactory, storageClock, barrier)` 和 `SD.StorageFactoryOptions(resolutionBudget)` → `new Asun.Platform.StorageDatabase.Runtime.StorageRuntimeFactory(dependencies, factoryOptions)` → 保存 `factory.CreateAsync(runtimeConfiguration, authority, ct).AsTask()` 一次并观察 → 保存runtime → `ConfigurationDatabaseStoreFactory.Create(..., runtime)` → `ConfigurationServiceFactory.Create(serviceOptions, core, store, clock, migrations:null)`。resolver返回的Profile/Input、Store/Generation/Bindings目录、ReferenceCatalog及所有VersionRef/hash必须与options完全相同；启动前Host按每个Binding核其精确类型/codec，不能让Adapter从诊断日志猜目录。Factory仅有界校验/深复制，不OpenSession、不启动工作、不迁移库；失败由原Host槽清理它已拥有的runtime。Runtime若共享，由其独立总Owner创建/保留；两个消费者不得各自Stop同一借用runtime。

按SD 0.3.1 §6.3冻结启动图：configuration的Core/read版本/options及codec在需要登记它们的Runtime.Create前由Host构造，后续配置Store只消费同一组已冻结值，fake与真实PG均不得启动后再补注册codec。Prepare/Decide共享同一ConfigurationDbMutationCodec稳定实例（完整Version/Schema/PayloadType相同），三个Binding共享同一ResultCodec稳定实例；真实PG marshal仍每descriptor一个实例。CLR PayloadType只在Binding内核验，不当跨Binding唯一键。Runtime在BackendFactory之前有界深复制注册值，PG工厂消费这同一快照、不再Resolve；Host持有codec/resolver/validator原实例至所有借用退出，声明getter零IO且全生命周期不变。同版本异实例、声明变化、重复/缺失/异hash注册均封闭拒绝，不热替换、不改历史身份。构造/启动只核ReferenceResolver声明和Owner映射，不调用OpenAsync或枚举根；本版本空引用resolver不借用配置Store，无须提前Attach Store或另造slot API。

固定OwnerKey=`asun.configuration/v1`。每个注册绑定均由本模块受信任Owner包提供参数化语句目录及结果codec，编译期登记，禁止请求携带delegate/SQL。具体配置事实存于此Owner自己的head、mutation、snapshot关系；不写storage-database私有ledger，跨Scope隔离以完整SD.StorageScope+StoreId+Generation+ConfigKey为复合身份，不因ScopeId字面相同合并租户。三个绑定：

| Binding | 注册与原子语义 |
|---|---|
| Prepare | Transaction、Production、Serializable、MutationSchema/Codec→ResultSchema/Codec、权限`configuration.save`；锁定/创建唯一head，先回查原mutation；同ID异RequestHash返回身份冲突，不改旧事实；同原ID同请求返回原Pending/Decided；其它Pending存在返回Blocked，不插新mutation。容量先核，为当前请求耐久插入完整规范请求+ExpectedRevision+准备身份+决定身份的Pending；不生成revision。 |
| Decide | Transaction、Production、Serializable、同Mutation/Result；权限`configuration.save`。必须同原Pending身份/请求；先查原Decided重放。仅head上该Pending可执行：ExpectedRevision不符原子写Conflict回执并清Pending；符合则revision+1，写完整snapshot bytes/hash、唯一revision、原Committed回执并清Pending，与技术commit结果同一事务。条件更新期望行=1；0或>1回滚/Unknown，不伪造成功。 |
| Read | Read、Query、RepeatableRead、ReadSchema/Codec→ResultSchema/Codec、权限`configuration.read`；仅Latest/Revision/History/Mutation/SnapshotChunk五种，强制授权范围，不增revision、不清Pending、不触发恢复/GC。单页快照头与HasMore来自同一次权威读取。 |

StatementCatalog分别是注册包的精确VersionRef；Options.BindingDescriptors恰含Prepare/Decide/Read三条，与Runtime目录全字段匹配，Factory核上表语义及预算，不能只核VersionRef名称。事务 `MinAffectedRows=0`（幂等/冲突只读重放允许0）、`MaxAffectedRows=6`、`MaxCommands=12`、`MaxRetries=0`，Read为0/0/4/0；AllowEmptyBatch=false，RetryDelay、锁/语句超时均显式有限正且锁超时≤语句超时≤Context.ExecutionBudget。这些是本Owner映射预算，不把所有影响行数都要求1；**只有关键head CAS更新要求恰1**。Prepare新键最多插head+mutation并更新head.Pending，Decide最多snapshot+mutation+head，技术ledger由Runtime计，不混进Owner行数。snapshot的主键就是revision索引，不复制第二快照表；对应原Committed且不可变。每键容量与历史保留沿§8.1，满只拒新，不删旧。

注册包的关系形状固定在本Owner私有 `cfg_v1` schema：三个表共有复合键K=(tenant_id,site_id,line_id,station_id,device_id,store_id,store_generation,configuration_id,configuration_scope_id)。ID列为text COLLATE "C"、NOT NULL、按输入codec有界检查，generation为bigint>0。head主键K，含latest_revision numeric(20,0)、pending_operation_id可空text、revision_count/operation_count/retained_bytes非负bigint；revision域check 0..18446744073709551615。mutation主键(K,operation_id)，含expected_revision numeric(20,0)、request_sha256严格小写64hex、state（仅Pending/Decided）、original_mutation_json bytea（上述OriginalMutation对象严格wire，完整payload/注册身份都保留）、receipt_json可空bytea；Pending无receipt、Decided必须有receipt。snapshot主键(K,revision>0)、另唯一(K,operation_id)，含envelope_bytes bytea、bytes bigint>0、sha256严格hex；外键同K的head及mutation。参数文字/metadata bytea允许，工业图像等仍禁止。Owner注册语句参数都用固定位置参数；Schema/表/列在受信任StatementCatalog编译期固定，调用方没有传标识符/SQL入口。

事务顺序：固定K插空head（冲突保持既有）→SELECT该head FOR UPDATE→查原mutation→容量/原Pending检查→Prepare插原件并CAS设置pending/count/逻辑保留bytes，或Decide读取同原件/当前revision生成UTC原Receipt、插snapshot（仅Committed）、更新mutation+head+逻辑预算；每个关键更新核受影响行1，任何中途错误整Owner写与技术commit回执一起回滚。真实PG的原UTC由权威事务的transaction_timestamp()取一次，按UTC七位小数wire记录（PG微秒后补一位0），fake用注入SD.IStorageClock取一次；不能由纯marshal编造“已提交时间”，不能从重放时间重建。retained_bytes按完整原件/快照/回执/有界head元数据规范字节及§8.4.1.1在途预约累计，是逻辑载荷限额，不冒称数据库物理磁盘占用；真实PG磁盘余量由SD Profile测量。SD单写/fence与参数化事务负责技术生效路径，本Owner不另建连接池或lease。

Production/Query/Recovery三个Context仅Caller及预算可按当前授权替换，Scope/Store/Profile固定且相同；SessionRequest.OwnerKey固定。领域事务用Production Session，所有RegisteredRead（含原Owner Mutation/完整快照读取）用Query Session；技术原route/ledger/Task回查用Recovery Context，不通过领域Read绑定或新的Recovery Session执行。这个分工服从SD§6.3/§7.2的Read只能Query用途及§6.7源Recovery技术职责，禁止把领域读取标成恢复来占用保留池。调用路径仅为 `runtime.OpenSessionAsync(new SD.SessionRequest(context, ownerKey, purpose), ct)` → `session.ExecuteTransactionAsync(new SD.RegisteredTransactionRequest(context, identity, binding, mutation, ImmutableArray<SD.ObjectRef>.Empty), ct)` 或 `session.ReadAsync(new SD.RegisteredReadRequest(context, readBinding, read), ct)`；技术事实回查为 `runtime.QueryOperationAsync(new SD.OperationQuery(recoveryContext, originalIdentity), ct)`，Task观察为 `runtime.GetTaskStatusAsync(new SD.TaskQuery(recoveryContext, originalHandle), ct)`。Release使用该Session.Handle和唯一原Release identity，Dispose沿原resource一次启动；不发明BeginTransaction/Commit/QuerySql/FindMutation重载。

ReferenceCatalog仍显式注册该Owner的允许Scopes/Stores、ReferenceResolver与ReadValidation精确VersionRef，不能因为无ObjectRef跳过目录。Host提供实现SD.IStorageOwnerReferenceResolver的受信任实例，Version为注册ref；Open核原Owner/scope/store/catalog/barrier及MaxEntries/MaxBytes后返回有限快照，SnapshotId由原barrier.ResourceHandle及OwnerKey长度前缀SHA标识，ReferenceEpoch=barrier.ReferenceEpoch。该注册包保证所有业务引用集合为空，ReadAsync(nextSequence=0)唯一返回Entries=Empty、NextSequence=null、Complete=true、SnapshotId/Epoch原样；其它nextSequence非法，取消等自身读取/Dispose真实结束，失败Complete=false/Fault非null，不借此声称已有配置整体备份。Owner.ReadValidation的受信任后端目录只读核head/mutation/snapshot唯一关系与完整codec/hash，损坏阻隔离恢复，不修数据；不需要增加SD公共API。注册包若后来产生ObjectRef必须新版本Resolver完整列举，不能沿用空结果。

上述根Open/Read只在调用方已核原协调保护、catalog/authority及指定屏障epoch后执行，启动阶段不据“引用为空”预生成完整根快照。Host关闭时先停消费者/新维护及resolver新接纳，有限观察已有resolver任务与snapshot实际排空/Dispose，再由总Owner停Runtime并释放backend，最后结束Host注册依赖生命周期；resolver不Dispose借用Store。若任何原借用/cleanup未确认，保留同组实例/原Task，不提前解除注册强根或新建替代Runtime。配置Service/Adapter自己的Close及借用Runtime边界仍按§8.4.4。

##### 8.4.1.1 真实PostgreSQL注册marshal与固定语句消费

SD当前§6.7.1已冻结 `Asun.Platform.StorageDatabase.PostgreSql.IPostgreSqlBindingCodec`，必须明确消费，不能把本Owner的软件接线推为客户事实。配置Adapters中唯一公开实现类型为 `ConfigurationPostgreSqlBindingCodec`，公开构造器为 `ConfigurationPostgreSqlBindingCodec(SD.VersionRef version, SD.StorageBindingDescriptor descriptor, ConfigurationDbOptions options, IConfigurationCore writeCore, ImmutableArray<ConfigurationCoreOptions> supportedReadVersions)`；实现该接口原有 `Version/InputSchema/ResultSchema/GetParameters(int commandIndex, ImmutableArray<byte> canonicalInput, SD.StorageInputLimits limits)/EncodeResult(ImmutableArray<PostgreSqlCommandResult> commands, int maxResultBytes)`，不增加SQL入口、回调、连接/Reader参数或等待状态。每个Prepare/Decide/Read descriptor一个不可变codec实例，Version等该可信StatementCatalog文档的codec ref，InputSchema/ResultSchema等descriptor。使用本机/项目已冻结SD.PostgreSql工程公开签名，Adapters的该真实绑定计划ProjectReference增加 `src/Modules/storage-database/Asun.Modules.StorageDatabase.PostgreSql/Asun.Modules.StorageDatabase.PostgreSql.csproj`，不在配置包另建Npgsql数据源或猜驱动版本；Core/Service仍不引用它。

Host在创建SD Runtime前构造三个codec，并将 `ImmutableArray<IPostgreSqlBindingCodec>` 注入SD已冻结 `new StoragePostgreSqlBackendFactory(documents,credentials,codecs,pgOptions)`；其 `OpenAsync(configuration,physicalGuards,storageClock,startupContext,ct)` 返回的PG group按SD§6.7.2组合至既有StorageBackendSet。documents含三个本Owner StatementCatalog及Schema迁移工件，Version/hash来自完整受信任工件字节；Create不建表，缺工件只拒相应真实Adapter。纯DB fake Host仍只消费§8.4.1 SD.Contracts/Runtime，不把真实PG资格混入fake。

marshal是有界纯转换：GetParameters重验commandIndex范围、原codec字节/核心候选/所有hash、options与descriptor（Scope/Store/Profile精确固定），返回上游允许的BCL值/独立byte[]副本；没有当前时间/IO/跨调用缓存。EncodeResult只消费该次完整命令数组与返回行，索引严格从0连续、数量精确、无default，读命令AffectedRows=0，变更命令计数合法且符合下表。结果在技术commit前通过ConfigurationDbResultCodec.Validate，错误使整个事务回滚；不能在commit后另造回执或补写snapshot。

所有StatementCatalog针对一个固定SD.Scope/Store/Generation登记，五域Scope/Store/Profile变化生成新的可信StatementCatalog/Binding版本；SQL中这些谓词及FORCE RLS显式绑定该登记范围，codec.Options三Context必须相同。领域参数只携ConfigKey，不能由请求改tenant/设备/库。RLS按迁移工件冻结的登录角色current_user→该完整登记范围映射核行范围，未知角色拒绝；不依赖本codec无法设置的tenant会话变量。运行角色非Owner/非BYPASSRLS，不授切角色权限；技术Recovery不授领域读取，Query角色给该范围的最小SELECT，Production给固定Owner写入，不给DDL。创建cfg_v1/表/约束/授权及StatementCatalog工件属于本Owner迁移包，由有迁移权的部署宿主按SD.Migrate流程显式执行；运行Factory/codec不得迁移。隔离恢复的Owner.ReadValidation只读检查同一关系/完整原件与快照，无修复函数。

固定命令顺序如下，每个序号是一条独立参数化命令，在上游**同一**已注册事务内串行执行；禁止把多步塞进同一个data-modifying WITH并依赖修改顺序/同一行二次UPDATE。各Mutation用DML实际影响行数，Read用有限SELECT；没有动态SQL、存储函数副作用或请求选择命令。每条末尾检查有限行数，PG Reader真实退出后才下一条。

| 绑定 | 精确commands与分支 |
|---|---|
| Prepare | 0 Mutation：INSERT空head ON CONFLICT(K) DO NOTHING，0/1行；1 Read：SELECT head WHERE K FOR UPDATE（必须1行），LEFT JOIN原mutation并取下述前置投影；2 Mutation：仅无原mutation、head.pending为null且容量/revision合法时插Pending原件，0/1行；3 Mutation：仅本次新Pending且head.pending为null时设置pending、operation_count+1与retained_bytes，新增意图必须1行，否则回滚，重放/Blocked为0；4 Read：按K+原OperationId读最终Owner状态/原件/回执，最多1原件，缺原件但其它Pending存在只返回Blocked元数据。首次插入必须2、3都1，不允许半Pending。 |
| Decide | 0 Read：SELECT head WHERE K FOR UPDATE及原mutation，必须同原ID/hash，head匹配Pending或原Decided；1 Mutation：只对Pending且expected=latest插完整snapshot（revision=latest+1），0/1行，已Decided或revision冲突为0；2 Mutation：只将同Pending改Decided，写Committed或Conflict完整原回执，0/1行，新决定必须1；3 Mutation：只在本head原pending同ID且mutation已Decided时CAS清pending、更新latest/revision_count/retained_bytes，0/1行，新决定必须1；4 Read：返回该原Decided回执和实际latest，原Decided重放三条Mutation均0。任何计数/原hash/预期行不符回滚并报Integrity/Conflict，不能部分成功。 |
| Read | 唯一0 Read：WHERE完整K；Latest/Revision返回0或1 SnapshotRef；History以revision>after升序LIMIT(MaxEntries+1)确定HasMore，返回前截去**探测用**第MaxEntries+1项（不是丢事实）；Mutation返回0或1完整原件/回执；SnapshotChunk按revision/operation/总bytes/hash全匹配提取bytea指定段，长度必须Count。读取Kind只能是公开五种，统一有界SELECT，不运行领域Mutation。所有meta与refs来自同一读取视图，空结果仍给合法空集合与latest元数据。 |

SQL更新条件复核原RequestSha256、ExpectedRevision、原件字节和head.pending，不仅比较OperationId。Decide保持head锁至整个事务结束，所以snapshot/回执/latest同时提交；技术ledger由上游同事务生成。Concurrent Serializable出现40001/40P01按descriptor.MaxRetries=0不重发，沿原identity查询；连接断开/取消不能按影响行0猜rollback。

按SD 0.3.1 §6.7.3，以上Owner命令只在A1已锁reference_authority→原route/attempt→对象/引用技术行之后才取得配置head/领域锁，不在持这些锁时反向申请Operation保护。Prepare/Decide虽References=Empty，新执行的注册写事务仍由A1 checked分配同一提交epoch E并设置事务局部`app.im066_reference_epoch`；A1负责填入并在Owner命令后复核技术GUC，codec不获取连接或新增参数。A1自己的epoch/route/receipt写不计本Owner影响行；Created=false技术重放、普通Read/QueryOperation不分配E。当前配置不产生ObjectRef/root_history/owner_object_reference，故不新增epoch列或领域根历史；不得拿PublicationToken.ReferenceEpoch当新提交E，也不自增技术epoch。未来引用版本如需历史定界，固定Owner SQL必须读取`current_setting('app.im066_reference_epoch',true)`并严格核非空、正bigint，使用这个同事务E；本空引用版本不凭空增加消费epoch的领域写入。四项技术GUC由A1设置/复核，本目录不修改，也不把它们当权限/fence证明；提交未知沿原identity保留Unknown，不能第二事务补写epoch/回执。

Prepare.1/Decide.0前置Read各恰一行，固定列为`keyJson:Bytea, latestRevision:UInt64, pendingOperationId:Text?, revisionCount:Int64, operationCount:Int64, retainedBytes:Int64, mutationState:Int32, originalMutationJson:Bytea?, receiptJson:Bytea?, attemptedRequestSha256:Text, expectedRevision:UInt64, checkCode:Text`；LEFT JOIN不存在时state=Absent，其余原件/回执null，不丢head行，锁只作用于head（FOR UPDATE OF head）。各Mutation命令不带RETURNING，resultColumnTypes/Rows为空、maxRows=0；前置Read maxRows=1，最终Read列按下表，maxRows为1或History的MaxPageSize。状态ordinal严格等公开enum：Absent=0/Pending=1/Decided=2/Blocked=3；readKind ordinal等§8.4.2。

EncodeResult依据同次前置行核分支及影响行：Prepare原Absent、无其它pending、checkCode=None时命令2/3必须1/1且最终Pending同attempted hash；同原Pending/Decided重放或Blocked必须0/0。Decide原Pending且expected=latest时命令1/2/3必须1/1/1，冲突必须0/1/1；原Decided重放必须0/0/0，最终回执规范bytes等前置receipt。命令0新建空head只能在最终合法新Pending分支保留；容量/身份/耗尽错误使整事务回滚，不能留下失败请求的新head。任何非法分支/计数/半原件/最终元数据不符立即拒绝，使技术commit前回滚；上游串行执行完再统一核，不要求上游在命令之间调用本codec。

前置checkCode的优先级固定：原件存在先核完整身份/hash/Expected/规范bytes；异请求IdentityMismatch，同请求原Pending/Decided不受新意图容量/revision门影响。原件不存在且其它pending存在返回Blocked；仅无原件且无pending的新Prepare再核RevisionExhausted/CapacityExceeded。Decide缺原件、head不匹配或原件/回执损坏为IntegrityMismatch。所有非None分支后续DML条件必须不成立，最终checkCode保留该错误，不靠codec回滚掩盖语句本身写错范围。

容量预约固定为`R=octet_length(original_mutation_json)+MaxSnapshotBytes+ReceiptUpperBound`，ReceiptUpperBound由Factory按§8.4.4的ID/UTC/数字/ref/escape最坏界计长，并作为受信任目录常量冻结；head规范元数据额度也为目录常量。新Prepare先核operation_count+1、revision_count+1、retained_bytes+R及所有checked上限，再把R计入retained_bytes。唯一Pending占一个潜在revision槽，Conflict仍保守预约；没有其它并发新意图。Decide用同一R减去预约，再加原件、实际snapshot（Conflict为0）和实际receipt字节，必须≤预约及总限额；head锁/原件不变保证可复算，无新增预约表/当前缓存。重放不改计数，已决定原件/回执保留。此retained_bytes含在途预约，属于逻辑限额，不是磁盘占用证明。

参数marshal固定完整包，commands均用相同位置/类型（未用项仍校验，SQL只消费列出的项）：`$1 ConfigurationId:Text, $2 ScopeId:Text, $3 OperationId:Text?, $4 ExpectedRevision:UInt64?, $5 RequestSha256:Text?, $6 CanonicalMutation:Bytea?, $7 OriginalMutationJson:Bytea?, $8 SnapshotPartsJson:Bytea?, $9 ReceiptPartsJson:Bytea?, $10 ReadKind:Int32?, $11 Revision:UInt64?, $12 AfterRevision:UInt64, $13 MaxEntries:Int32, $14 SnapshotRefJson:Bytea?, $15 Offset:Int64, $16 Count:Int32, $17 MaxOperationRecords:Int32, $18 MaxRevisions:Int32, $19 MaxBytes:Int64, $20 MaxSnapshotBytes:Int64`。Mutation的$10～$16固定null/0；Read的$4～$9固定null，$3仅ReadKind.Mutation取原OperationId、其它Read为null；$10～$16精确取公开Read对应字段，其余按§8.4.2。Nullable值以null交接口、由上游按登记类型发送DBNull；所有UInt64→numeric保全域，禁止转long。Scalar参数和parts由已核canonicalInput与冻结options确定，CanonicalMutation必须等输入本身；OriginalMutationJson按原版本/descriptor和StorageRequestHasher重建两原identity。数据库不重新猜JSON默认、量纲或核心约束。

每条可信SQL开头用无副作用、显式PG类型cast的参数CTE声明完整$1～$20（Text→text、UInt64→numeric、Bytea→bytea、Int32→integer、Int64→bigint），避免未使用/空参数类型推断失败；这只是SELECT参数，不含修改CTE。非null载荷只用BCL对应类型，null以object? null交接口，由SD按目录类型发送DBNull，不向接口传DBNull.Value假冒允许BCL值。SQL实际消费的容量参数须等目录冻结options，不能让输入扩大限额。

SnapshotPartsJson/ReceiptPartsJson是**私有参数编码**，不是新公共DTO/wire：SnapshotParts固定字段`key,operationId,content,source`，各值为对应§8.3.1规范JSON片段的base64（content为完整NormalizedCandidate），ReceiptParts固定`operation,requestSha256`同样编码。严格ASCII JSON字段序/无空白，SQL只解base64取得已规范bytea，禁止jsonb::text重排/改escape后算hash。数据库以已登记固定ASCII标点拼接这些片段与自己的revision/UTC数字：snapshot body按§8.3.1 Snapshot字段序，body hash=`encode(sha256(bodyBytes),'hex')`；按固定Envelope顺序组完整bytes并再算SnapshotRef hash，长度用octet_length。UTC使用`transaction_timestamp() AT TIME ZONE 'UTC'`以yyyy-MM-dd'T'HH:mm:ss.ffffff加`0Z`，revision用numeric整数无前导零/指数的十进制ASCII；超.NET DateTimeOffset年份域、revision耗尽或完整byte长度超限拒绝。Committed回执内snapshot为精确SnapshotRef，Conflict为null，decidedAtUtc与本次已生成UTC一致；重放仅读原receipt_json不拼新时间。原件/回执/parts中的所有用户字符串均由marshal按现有Utf8JsonWriter规范转义，SQL不再转义它们，hash不依赖PG locale/jsonb字段序；所有parts字节与候选/operation在消费前后核相等。

最后Read命令返回供EncodeResult消费的统一列（仅内部行投影）：`readKind:Int32?, keyJson:Bytea, latestRevision:UInt64, hasMore:Boolean, mutationState:Int32, requestSha256:Text?, receiptJson:Bytea?, originalMutationJson:Bytea?, snapshotRevision:UInt64?, snapshotOperationId:Text?, snapshotBytes:Int64?, snapshotSha256:Text?, chunkSnapshotJson:Bytea?, offset:Int64, chunk:Bytea, checkCode:Text`。每条refs占一行；无refs仍1行meta+四snapshot列全null，禁止“无行=空成功”。Mutation最多1行、chunk只有精确原片；History至多MaxEntries行且共同meta一致，不能混latest。checkCode封闭为`None/IdentityMismatch/CapacityExceeded/RevisionExhausted/IntegrityMismatch`，非None在结果codec前使事务失败并保持原操作查询；不得编码一个假的配置NotCommitted。Decode receipt/original/meta按§8.4.2严格wire，把完整行投影成唯一ConfigurationDbResult再规范编码，不返回PgRow/Reader。前置锁Read行只用于核原状态/影响行，不作为外部最终结果。

新增断言：Query绑定误用Recovery必须在启动/Session读取前拒，普通Read不消费技术Recovery连接；三Context任一Scope/Store不同拒；marshal commandIndex/参数类型/行列数量/影响行被篡改即拒；Prepare新意图只有一半行回滚；同事务Decide后Query看见完整原件/快照/回执；服务端UTF8 body/envelope hash与BCL规范器逐byte相等（含引号、反斜线、中文、代理对与DateTimeOffset七位小数），不得仅JSON语义相等。既有§8.4.6六向量的Mutation、合成Prepare/Decide descriptor及Hasher算法不改，它们仅固定编码夹具；真实新目录必须按实际完整工件计算三个StatementCatalog/Binding refs，Read还必须修正用途，不能沿用合成或旧目录hash冒匹配。原持久操作按其原注册版本核验，不用新目录refs改写旧身份。

#### 8.4.2 Owner规范编码、身份与结果wire

以下编码独立版本化，不更改已接收§5.1四域。`S`为uint32 big-endian长度+严格UTF8，`B`为uint32长度+原bytes；uint32/int32/uint64/int64均big-endian，枚举采用本节固定ordinal；nullable一字节0/1，再内容，禁止default集合/非规范值。VersionRef=`S(Id),int32(Revision),S(Hash.Hex)`；Key=`S(ConfigurationId),S(ScopeId)`；SnapshotRef=`Key,uint64(Revision),S(OperationId),int64(Bytes),S(Sha256)`。所有字符串/集合/总bytes先按Core及StorageLimits/Options有界计长，checked后再分配；解码拒尾随bytes/非法presence/未定义enum，完整重编码必须相等。

| 域 | 精确字段顺序 |
|---|---|
| Mutation codec | `S(asun-config-db/mutation-v1),VersionRef(MutationSchema),B(§5.1完整Save规范bytes),B(§8.3.1 Candidate对象规范JSON bytes)`。Save完整bytes包括Key/原OperationId/ExpectedRevision/ContentHash/Source/defaults；Candidate完整Definition/values/opaque/source/defaults再次复核。RequestedAtUtc是观察时间，不进入编码/身份，后端提交时间由事务内UTC产生。不能只编码ContentHash或Value域。 |
| Read codec | `S(asun-config-db/read-v1),VersionRef(ReadSchema),int32(Kind),Key,nullable S(OperationId),nullable uint64(Revision),uint64(AfterRevision),int32(MaxEntries),nullable SnapshotRef(Snapshot),int64(Offset),int32(Count)`。Kind ordinal Latest=0、Revision=1、History=2、Mutation=3、SnapshotChunk=4。未用字段必须固定null/0，不能携隐含查询条件。 |
| 技术Mutation语义信封 | 唯一使用SD§6.3的`StorageRequestHasher.Compute(RegisteredTransactionRequest request, StorageBindingDescriptor binding, ImmutableArray<byte> canonicalPayload, StorageInputLimits limits)`，不自造asun-config-db技术信封。精确bytes为ASCII `IM066-REQUEST-1`+Kind(Transaction=1)+Context.Scope/Store+Identity.Scope/StoreId/Generation/Owner/OperationId/IdempotencyKey+Binding VersionRef+**完整**StorageBindingDescriptor+canonicalPayload byte array+References数组（本模块为空）；原语全部按SD§6.4小端、Sha256为32原byte。Identity.PayloadHash不编码，Caller/预算/观察时间不入身份。Owner Mutation/Read payload本身仍按本表big-endian。 |
| 技术操作ID | `token=SHA256(S(asun-config-db/operation-v1),完整五字段StorageScope,S(StoreId),int64(Generation),Key,S(配置OperationId))`；Prepare.OperationId/IdempotencyKey均为`cfg-prep-`+token，Decide均为`cfg-decide-`+token。固定prefix+64字符，MaxIdBytes至少75；两阶段不能复用同一技术ID，配置原ID不变。内容不入token，异内容重用原配置ID必须冲突，不变成新ID逃过幂等。 |

Mutation.Schema必须等Bindings.MutationSchema，Read.Schema等ReadSchema；编码器不信任StoreSaveRequest.RequestSha256/NormalizedCandidate摘要，按获准版本Core与规范JSON重算并核一致；深复制不可变请求，不用record引用相等替代字段比较。Mutation payload不含RequestedAtUtc的规范语义；其重放不得改变原回执时间。配方自定义单位不交给数据库codec解释，继续按Core规范字面保存。

技术identity构造：按operation token生成固定两个ID/幂等键 → PayloadHash先用合法SHA256(Empty)占位 → 构造RegisteredTransactionRequest → MutationCodec.Encode(mutation,StorageLimits.MaxPayloadBytes) → 从Options.BindingDescriptors按精确Binding取已冻结descriptor → 调用上游Compute → with替换Identity.PayloadHash并保存完整请求。Host与Runtime均用同一公开算法重算；只把完整请求以业务身份保存，不复制技术Hasher。原件OriginalMutation保存两阶段完整identity、原Bindings/RuntimeProfile和payload，冷查询核原注册版本后同法校验，不能只重算payload hash。上游Runtime引用是此公开Hasher的真实消费者，不能用本模块新helper冒同名端口。

Read字段组合：Latest只有Key；Revision仅Revision>0；History仅AfterRevision及MaxEntries=1..MaxPageSize；Mutation仅OperationId；SnapshotChunk仅Snapshot非null、Offset≥0、Count>0且≤ChunkBytes，checked Offset+Count≤Snapshot.Bytes且外层Key一致。Snapshot.Ref修订>0、Bytes>0且≤MaxSnapshotBytes、Sha256严格小写hex。存在零条历史用空数组，而非零长度假snapshot。其它字段非零/null不合法即CFG-001，不能忽略。

ResultBytes采用严格规范JSON，复用§8.3.1的Unicode、数字/UTC/base64/字段序及深度检查方法，**不是FileEnvelope新增磁盘根**。根字段固定顺序：`format,readKind,key,latestRevision,hasMore,mutationState,requestSha256,receipt,originalMutation,snapshots,chunkSnapshot,offset,chunk`；format=`asun-config-db-result-v1`，readKind为名称或null，mutationState为名称，latest/offset及嵌套revision/bytes为规范十进制字符串。receipt字段顺序`operation,requestSha256,outcome,actualRevision,snapshot,decidedAtUtc`，snapshot是SnapshotRef而非内联对象；SnapshotRef字段序`key,revision,operationId,bytes,sha256`；chunk是标准base64。originalMutation字段顺序`bindings,runtimeProfile,prepare,decide,bytes`；bindings按ConfigurationDbBindings声明顺序的camelCase字段，VersionRef为`id,revision,hash`（hash为hex），OperationIdentity按SD声明顺序`scope,storeId,storeGeneration,ownerKey,operationId,idempotencyKey,payloadHash`，scope为`tenantId,siteId,lineId,stationId,deviceId`；bytes为完整Mutation codec bytes的base64。没有自报body hash；SD.ResultSchema固定结果codec，SnapshotRef.Sha256核完整snapshot envelope，技术PayloadHash核完整输入，三者不混用。

Result tagged形状：Prepare/Decide的ReadKind=null；Prepare新接纳/原Pending为Pending+原RequestHash+Receipt=null，原Decided重放或Decide成功为Decided+同RequestHash+非nullReceipt；其它键Pending阻挡为Blocked，RequestHash/Receipt均null。仅Read.Mutation的Pending/Decided带非null完整OriginalMutation，权威无Owner记录为Absent+OriginalMutation=null；所有事务结果及其它读取OriginalMutation=null。Mutation的Snapshots/Chunk=Empty、ChunkSnapshot=null、Offset=0。Absent/Blocked不带回执；事务Decided的完整快照只通过Receipt.Snapshot定位，Snapshots=Empty。Latest/Revision/History为Absent（此处未查询mutation），RequestHash/Receipt=null、ChunkSnapshot=null/Offset=0/Chunk=Empty，只带严格升序Snapshots和同次LatestRevision/HasMore；Latest/Revision最多1项且HasMore=false，History最多MaxEntries。SnapshotChunk仅ChunkSnapshot精确回显、Offset及Count字节Chunk，Snapshots=Empty/Receipt=null/RequestHash=null/HasMore=false。所有非History结果HasMore=false。技术故障用上游Fault，不编码半成功页。ResultCodec核枚举、键/时间、数组、shape及byte上限，Adapter再核与原read/request匹配。

#### 8.4.3 提交、原Mutation查询与完整快照分页

Save逐步：重验/深复制并预约额度 → 打开Production及Query Session → 原Owner Mutation窄读取（Query）及技术原身份回查（Recovery Context） → 原Decided同摘要返回原回执，异摘要Rejected/CFG-018，未决先观察，不换ID → 首次Prepare注册事务耐久Pending → 核技术Completed/Committed及Pending结果 → 同原payload执行唯一Decide注册事务 → 核原技术回执/业务ReceiptRef → 按下列分片读完整snapshot并重验 → 释放本次Session/所有原Task后返回SaveResult(Resource=Released)。其它Pending阻挡Unknown/CFG-013，不能当本请求Conflict/NotCommitted。技术Committed可能仅表示Prepare成功或配置Conflict，不能直接投影配置Committed；技术RolledBack/Rejected/Failed或空失败ResultBytes没有配置最终回执，已接纳时仍Unknown，不编CFG-010回执。revision耗尽在耐久Prepare前拒CFG-015；重放已决定回执仍允许。候选/快照过限在接纳前拒CFG-002。

Pending恢复不隐藏在Query中：若Prepare响应丢失，仅查询原Prepare/Decide技术身份及Owner Mutation，不自动补发Decide；若Prepare已Committed而Decide未发/结果不明，保留Pending+Unknown及原工作项。仅Host显式恢复原请求才可再次调用TrySaveAtomic，且只能原两个注册identity的Runtime幂等观察/执行；已有route/Unknown不重跑，Runtime单写lease未证明旧writer退出/不可绕过fence时不得接纳新writer。旧route已存在但未最终对账时等原Runtime/授权后端对账证据；本Adapter没有Transaction Resume或强制接管API。Owner读的Absent、SD.NotFound、连接消失、WaitBudget到期均不能证明安全重试/NotCommitted。这个保守行为是已冻结的恢复语义，不让程序员猜一次查无即可写；服务不能靠新实例绕过Pending。

QueryOperationAsync的输入只有OperationKey，冷恢复不能自造ExpectedRevision/Content/hash：先用ReadKind.Mutation读取OriginalMutation（原Bindings/RuntimeProfile、两个完整技术identity及完整Mutation codec bytes），核保存的原注册版本、重建摘要再调用Runtime.QueryOperationAsync；或使用Adapter原在途索引中保留的完整StoreSaveRequest。仅回执元数据或已提交快照不足以重建原技术PayloadHash，因为仍缺原ExpectedRevision；不能以最新版本倒推。原件的格式与一次有界读取见下段，不新增SD端口。两个identity由本节信封独立重算逐字段核等，不信任响应自报PayloadHash；v1只读当前Bindings及Profile的精确匹配版本，未批准注册版本CFG-003，可换显式匹配旧包只读，不用新绑定refs重算覆盖旧身份。完整identity/codec核对后才查；超保留期/权限拒绝/未知路由/主库不可确定为Unknown，原件损坏CFG-017。Found只在配置最终回执已决定且技术对应Decide.Committed、Request/Outcome/快照全量一致时返回；Pending为Unknown，Absent仍Unknown，不能用Load最新代替原结果。

本切片原Mutation查询的原件读须以**与快照不同的标签**走同一窄Read：`Mutation`带OperationId返回完整OriginalMutation，而不是SnapshotChunk；若bytes超过单次MaxResultBytes则不能临时截断。冻结options要求 `MaxPayloadBytes` 和 `MaxResultBytes`都足以容纳本切片最大完整Mutation（含原注册元数据及结果JSON/base64开销），冷查询一次返回完整原件，Snapshot仍可分页；完整Candidate过此上限在首次Prepare前拒绝。Record内原始规范payload及注册身份永久保留；不要把Pending原件称快照或遗漏其字节，未来有真实消费者需要更大的Mutation原件再另批原件分片，而非现在猜通用游标接口。

完整snapshot分页：snapshot bytes完全复用§8.3.1 `FileEnvelope<ConfigurationSnapshot>` 的规范wire（仅字节格式复用，不调用FileStore或创建文件）；SnapshotRef.Bytes/Sha256为完整envelope长度/SHA。Read Latest/Revision或History首先得到固定SnapshotRef列表（History HasMore同读决定）；每个ref从Offset=0按Count=min(ChunkBytes,Bytes-offset)重复SnapshotChunk；每次独立Query Session或同一已借用Query Session串行Read，原Read Task实际完成才启动下一片。每片必须精确回显ref/Offset、字节数=Count，拒重叠/短片/越界/调换key/revision/hash；不是同page号最新查。全部片后核总长度/hash/规范envelope/定义/Content/Source/Operation，再交完整Snapshot或整页RevisionPage；任何片失败取消/预算到期返回Unavailable/Corrupt或抛分页异常，绝不返回半snapshot/半页。哈希错误CFG-017、不修复。HasMore不由客户端“本页满了”推断；空页LastRevision=after，非空为最后一项，严格按§6.2。

当前最新可在分片间前进，但已选ref不可变，结果仍是最初权威读选定版本；历史列表从1连续，原ReceiptRef指定快照永不换“最新”。只允许追加、不删历史/原件，分片无需跨调用活Reader/隐藏cursor。原件Read和snapshot Read都全量重验，只读权限及Caller在每次调用核；撤权使整个结果拒绝，不把已读半页交UI。

#### 8.4.4 预算、任务与资源Owner

Options所有计数/字节上限>0、≤BCL容器上限，MaxJsonDepth≥32、MaxIdBytes≥76；MaxSnapshotBytes、最大规范Mutation（Save+完整Candidate）、最大History refs和base64结果均在Factory前以Profile最坏计长验证。`ChunkBytes>0`、`4*((ChunkBytes+2)/3)+最大结果元数据JSON bytes≤StorageLimits.MaxResultBytes`（checked），最大Mutation原件同式；本节显式要求完整Mutation可单包，不能看snapshot可分页就放行无限Candidate。Core.Options.Limits.MaxTotalUtf8Bytes/MaxFields及SD.MaxIdBytes决定最坏编码容量，Factory用保守字符escape膨胀界（每UTF16 code unit最多6个ASCII JSON byte）及固定字段计算，逐请求再按真实bytes核验。MaxSnapshotBytes及完整规范Mutation必须≤int.MaxValue/Array.MaxLength及较小Profile限额；MaxPageSize同时≤Service.MaxPageSize，History完整返回resident预算至少PageSize×MaxSnapshotBytes加refs/片副本，容量不够整页CFG-002，不能只预约单片再无限累积所有Snapshots。每键MaxBytes含所有Pending原件、snapshot、回执及head；MaxRevisions/OperationRecords满保留旧记录并拒新。MaxRetainedBytes覆盖输入/输出/完整组装buffer/单片base64与bytes副本/读取Core/状态，预算先预约，不计只读hash几十字节代替完整候选。并行MaxActiveCalls/等待MaxQueuedCalls均有界，同键在途/未决禁止第二新ID；共享Runtime总限额与本地Adapter限额分别有效。

Context.ExecutionBudget/WaitBudget沿SD要求有限正、Wait≤Execution≤Runtime.Profile.MaxOperationTime；每配置端口调用只取一次单调deadline，不在每片/每Poll刷新Execution。各SD子调用预算取原剩余时间，deadline到不发下一片/下一阶段，已发Task只发合作取消并继续真实收尾；WaitBudget只是观察，不等于资源释放。PollInterval有限正、不忙轮询；Profile测点沿§14并新增Prepare/Decide/头读/完整组装bytes/片数/取消至Session.Release测点，目标待消费者采纳，不编造延迟达标值。

Adapter借用runtime/Core/clock，拥有自己每个调用的CTS、原Open/Read/Execute/Poll/Query Task、Session及组装buffer。ValueTask仅AsTask一次并先保存。Execute返回非Completed时保存原TaskHandle并串行GetTaskStatus；原SD调用已返回不代表技术任务资源归还。配置端口Task只有本次全部读/技术工作Completed且其Session实际释放/Dispose成功后才能完成（Query读取自身资源退出；它可用Resource报告本Adapter原Save仍Draining/DrainUnknown）。Close停新业务，登记每个原Session Release/Dispose Task与取消，有限观察未退返回DrainUnknown并保持原根；不Stop/Dispose借用runtime，不删Pending。句柄跨epoch/ResultExpired用Unknown，不能伪Released。

Release与Stop只用SD实例控制身份，不套durable Hasher：Release规范bytes=`S(asun-config-db/release-v1),S(InstanceEpoch),S(ResourceId)`，Stop规范bytes=`S(asun-config-db/stop-v1),S(InstanceEpoch)`；按本节S严格UTF8长度前缀，SHA256为控制PayloadHash，OperationId/幂等键分别`cfg-release-`或`cfg-stop-`+该hash；Release prefix+hash为76byte，所以实际MaxIdBytes≥76。Host在调用前保存固定identity（Scope/Store/Generation及授权Owner），同一资源重复观察复用原请求/原Task，不改ID再次Release。Session.Release返回Released后仅该原Dispose Task实际成功才清Session强根；Fault/DrainUnknown继续保留。错误映射：SD.InvalidInput→CFG-001、CapacityExceeded/ResourceBusy→CFG-002、UnsupportedVersion→CFG-003、PermissionDenied→CFG-019、IntegrityFailed→CFG-017、TimedOut/Cancelled在纯读为CFG-012/011、Unavailable/ResultExpired/InstanceMismatch纯读为CFG-009；凡Save已可能接纳/Unknown/DrainIncomplete用CFG-013并保留资源轴。SD.Conflict要先区分原identity异hash（CFG-018）与配置Receipt.Conflict（CFG-008），不能全映射业务revision冲突。

跨进程原操作的业务事实靠耐久查询，资源事实仅来自该进程根/原TaskHandle的Completed/实际Session释放或Host确认原进程已退出且旧写者被权威隔离；不能用Committed ledger证明另一活进程已排空。原Adapter仍活时不得新建实例逃过其强根/在途借用；同根恢复查询合并原resource轴。冷启动确认旧进程退出但fence未确认时保留Unknown知识，不越过单写门；新的查询Session实际归还仅说明新读资源退出。Host可关闭它自己独占Runtime并取Stop Completed，再一次Dispose确认释放；共享Runtime由总Owner处理。同步Open/codec抛错、调用fault、取消、预算、Release/Dispose fault均保留原业务错误与独立cleanup错误，不在finally覆盖结果，不在观察超时后清slot。

#### 8.4.5 两个空宿主与可判定反例

两Host均在binding的Adapters.Tests（net10.0/BCL Exe）内，分别 `--suite database --host device` / `--suite database --host algorithm`；只引用Adapters/Core/Service和SD.Contracts/Runtime，同一工程不同自足入口，不共享另一Host私有类型。Host固定resolver+authority+clock+barrier+backendFactory通过SD公开依赖注入真实StorageRuntimeFactory；受控fake数据库只实现SD.IStorageDatabaseBackend，按本节注册映射模拟Owner事实，绝不fake IConfigurationStore或Runtime来掩盖桥错误。无文件对象调用，未用File/Coordinator/Maintenance后端仍按SD.StorageBackendSet显式提供可控测试实例，非调用路径返回合法Unavailable，不猜默认。真实PostgreSQL按SD.A1独立后续资格使用同注册包。

| Host | 从空根到结果/收尾 |
|---|---|
| DbDeviceHost | 进程根预留2slot/64MiB→合成Scope=(tenant-a,site-a,line-a,station-a,device-a)、Store=(cfg-test,Generation1,Profile精确ref)、Owner注册上述三个绑定及codec→显式SD依赖/Factory.Create原Task→§11.3.1 Device完整Core/Service定义和候选20→本節Options→DatabaseStoreFactory.Create→ServiceFactory.Create→Load latest NotFound→Save原ID db-device-1 Expected0→Prepare Pending无revision→Decide原Committed revision1→分片回读20→Query原操作同完整SaveReceipt→历史页→独立关闭Service/Store，释放每个Session，若Runtime独占再Stop/Dispose。 |
| DbAlgorithmHost | 独立root/resolver/runtime/另Scope device-b/algorithm-example，Score=0.75与自己的Source/规范hash→同构造全链→Save db-algorithm-1 Expected0→revision1→以同原ID异Content0.8拒CFG-018→新ID Expected0 Conflict actual1→Query复得原Conflict而非技术Committed→历史After0/Page1 HasMore=false→关闭/真实排空。可单独运行不加载DbDeviceHost依赖。 |

DB Host合成CoreLimits明确为(8,8,16,256,8192,1024)，Contract/Schema沿§11.3.1；Definition/输入及Source全量必须满足此预算。合成options：Execution=5s/Wait=1s（Production/Query/Recovery），PollInterval=20ms/Close=5s、MaxSnapshotBytes=1MiB/ChunkBytes=4096/PageSize=16/每键Operation=128/Revision=128/Bytes=64MiB、Active=4/Queued=16/Retained=64MiB/JsonDepth=64；SD.Input为Id128/Payload4MiB/Result8MiB/References8/BatchRows16/BatchBytes8MiB/CatalogEntries64/CatalogBytes1MiB。Runtime其余Profile/ReferenceCatalog/BackendSet照SD§6.3/§7.1.0逐项自足构造并精确绑定，不把这些数值当客户Profile；初始注册refs必须真实按本注册包规范hash算，不填随机hash。Host authority明示control/create/stop与configuration.read/save范围，普通Caller不得自获控制权。每个公共result先核Fault/shape再读取值。

每个Host按§11.3进程根Owner模式在Factory前预留，把原Create及runtime/store/service、所有请求/操作身份/Session/查询/cleanup原Task强持到实际退出；初始Create同步抛错也记原失败Task。观察10s、独立cleanup5s、suite180s、外层300s，超时不作释放；迟到原Task仍归原slot，一次归还，交接拒绝不清根。借用Runtime关闭由其总Owner，Service不Dispose Store。最终所有fake闩锁打开，原Session和Runtime实际退出才测试结束；失败/未退/跳过必需例返回非零。

反例断言：两进程同键Expected0仅一revision1另一Conflict；不同Scope同字面Key隔离；Prepare回执丢失只Query不Decide；Decide committed响应丢失沿原identity查回原Receipt；同ID换Expected/Source/defaults/definition拒；其它Pending阻新ID；技术Committed+配置Conflict不误判；RolledBack空result不造NotCommitted；冷恢复读取完整原Mutation重建hash而非最新猜；原件超SD上限接纳前拒；完整snapshot跨多片且latest同时增长仍原ref；缺片/调换/重复/短片/hash/定义篡改拒整页；权限撤回不漏半页；等待取消/执行超时/同步抛错/迟到Commit/Release fault均保持原根；旧TaskHandle epoch不匹配Unknown；查无无fence不能重发；版本/codec回退不重编码旧回执。真实PG的事务隔离/RLS/关键CAS=1/单写fence/崩溃与实际资源资格另验，fake不替代。

#### 8.4.6 固定Owner Golden（完整字节，不是运行证据）

本节合成Mutation沿用§5.1.1完整输入（Definition d/1、Boolean x=true、ConfigKey c/s、Operation o、Expected0、Source T/I/V）；Candidate规范JSON为687 bytes。MutationSchema=(m,1,H)、ReadSchema=(r,1,H)，H=SHA256(Empty)，仅为结构夹具引用，不冒注册工件来源有效性。技术Scope=(t,a,l,n,d)、Store=(z,Generation1,Profile p/1/H)、OwnerKey=asun.configuration/v1；Prepare/Decide Binding分别b/e，InputSchema m、InputCodec i、ResultSchema o、ResultCodec j、StatementCatalog分别u/w，每个VersionRef Revision1/hash H。完整descriptor按SD声明序：Owner相同、Kind=Transaction(0)、PermissionKey=configuration.save、Purpose=Production(0)、Isolation=Serializable(2)、Min/MaxAffectedRows=0/6、MaxCommands12、MaxRetries0、RetryDelay1ms、ServerLockTimeout1s、ServerStatementTimeout4s、AllowEmptyBatch=false。当前Caller/Execution5s/Wait1s仅影响授权/观察，不入摘要；References=Empty。Owner payload为big-endian，技术信封为SD小端，不混用。

下列每项均为完整hex；OperationToken的SHA决定两个技术OperationId/IdempotencyKey，Prepare/Decide的PayloadHash分别取其完整IM066信封SHA。固定期望由字段独立拼接，不调用未来受测codec/Hasher生成Expected。

**DB-OperationToken**：84 bytes；SHA-256=7d772fe9dff53b6080af738d6fb8b84a1644f5bed4069a36e8d47f7f5c8e31b0。

```text
0000001b6173756e2d636f6e6669672d64622f6f7065726174696f6e2d763100000001740000000161000000016c000000016e0000000164000000017a000000000000000100000001630000000173000000016f
```

**DB-Mutation**：1010 bytes；SHA-256=6cf256179c7162712d98ef18008b58d5f5f2e2e25ebfc79668e542c2c7cbe261。

```text
0000001a6173756e2d636f6e6669672d64622f6d75746174696f6e2d7631000000016d000000010000004065336230633434323938666331633134396166626634633839393666623932343237616534316534363439623933346361343935393931623738353262383535000000d00000001a6173756e2d636f6e6669672d62696e6172792d76322f7361766500000001630000000173000000016f00000000000000000000004031313965353534346563356661616237396337393963613462663366376262366666303638623230373161666238646331636564313839316639623466666330000000015400000001490000000156000000406533623063343432393866633163313439616662663463383939366662393234323761653431653436343962393334636134393539393162373835326238353500000000000002af7b22636f6e66696775726174696f6e4964223a2263222c2273636f70654964223a2273222c22636f6e74726163744d616a6f72223a312c22646566696e6974696f6e73223a7b226964223a2264222c2276657273696f6e223a2231222c22736368656d6156657273696f6e223a7b226d616a6f72223a312c226d696e6f72223a302c227061746368223a307d2c22756e6b6e6f776e506f6c696379223a2252656a656374222c22706172616d6574657273223a5b7b226b6579223a2278222c226b696e64223a22426f6f6c65616e222c22756e6974223a224e6f6e65222c227265717569726564223a747275652c2264656661756c7456616c7565223a6e756c6c2c22646563696d616c426f756e6473223a6e756c6c2c22646f75626c65426f756e6473223a6e756c6c2c22616c6c6f77656456616c756573223a5b5d2c2273656e736974697665223a747275657d5d2c22636f6e73747261696e7473223a5b5d2c22636f6e74656e74536861323536223a2263623265646235303731396231343763373932363362626438306638633430376134636133303835306637323138396438663066326634613737626137633835227d2c2276616c756573223a5b7b226b6579223a2278222c2276616c7565223a7b226b696e64223a22426f6f6c65616e222c22756e6974223a224e6f6e65222c2274657874223a2274727565227d7d5d2c22756e6b6e6f776e4669656c6473223a5b5d2c226170706c69656444656661756c744b657973223a5b5d2c22736f75726365223a7b2274797065223a2254222c226964223a2249222c2276657273696f6e223a2256222c22636f6e74656e74536861323536223a2265336230633434323938666331633134396166626634633839393666623932343237616534316534363439623933346361343935393931623738353262383535227d7d
```

**DB-ReadLatest**：144 bytes；SHA-256=c62b16b0cd211607a835e2317a5800e28f42846ddb56a1e12e34b04c2f0ee949。

```text
000000166173756e2d636f6e6669672d64622f726561642d763100000001720000000100000040653362306334343239386663316331343961666266346338393936666239323432376165343165343634396239333463613439353939316237383532623835350000000000000001630000000173000000000000000000000000000000000000000000000000000000
```

**DB-PrepareIntent**：1720 bytes；SHA-256=eed296261f37db411cad4b9a187d7898bff1783d8396f585972de2c8032aad38。

```text
494d3036362d524551554553542d310100000001000000740100000061010000006c010000006e0100000064010000007a0100000000000000010000007001000000e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b85501000000740100000061010000006c010000006e0100000064010000007a0100000000000000150000006173756e2e636f6e66696775726174696f6e2f7631490000006366672d707265702d37643737326665396466663533623630383061663733386436666238623834613136343466356265643430363961333665386434376637663563386533316230490000006366672d707265702d37643737326665396466663533623630383061663733386436666238623834613136343466356265643430363961333665386434376637663563386533316230010000006201000000e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855010000006201000000e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855150000006173756e2e636f6e66696775726174696f6e2f763100000000010000006d01000000e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855010000006901000000e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855010000006f01000000e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855010000006a01000000e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855010000007501000000e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b85512000000636f6e66696775726174696f6e2e73617665000000000200000000000000060000000c0000000000000010270000000000008096980000000000005a62020000000000f20300000000001a6173756e2d636f6e6669672d64622f6d75746174696f6e2d7631000000016d000000010000004065336230633434323938666331633134396166626634633839393666623932343237616534316534363439623933346361343935393931623738353262383535000000d00000001a6173756e2d636f6e6669672d62696e6172792d76322f7361766500000001630000000173000000016f00000000000000000000004031313965353534346563356661616237396337393963613462663366376262366666303638623230373161666238646331636564313839316639623466666330000000015400000001490000000156000000406533623063343432393866633163313439616662663463383939366662393234323761653431653436343962393334636134393539393162373835326238353500000000000002af7b22636f6e66696775726174696f6e4964223a2263222c2273636f70654964223a2273222c22636f6e74726163744d616a6f72223a312c22646566696e6974696f6e73223a7b226964223a2264222c2276657273696f6e223a2231222c22736368656d6156657273696f6e223a7b226d616a6f72223a312c226d696e6f72223a302c227061746368223a307d2c22756e6b6e6f776e506f6c696379223a2252656a656374222c22706172616d6574657273223a5b7b226b6579223a2278222c226b696e64223a22426f6f6c65616e222c22756e6974223a224e6f6e65222c227265717569726564223a747275652c2264656661756c7456616c7565223a6e756c6c2c22646563696d616c426f756e6473223a6e756c6c2c22646f75626c65426f756e6473223a6e756c6c2c22616c6c6f77656456616c756573223a5b5d2c2273656e736974697665223a747275657d5d2c22636f6e73747261696e7473223a5b5d2c22636f6e74656e74536861323536223a2263623265646235303731396231343763373932363362626438306638633430376134636133303835306637323138396438663066326634613737626137633835227d2c2276616c756573223a5b7b226b6579223a2278222c2276616c7565223a7b226b696e64223a22426f6f6c65616e222c22756e6974223a224e6f6e65222c2274657874223a2274727565227d7d5d2c22756e6b6e6f776e4669656c6473223a5b5d2c226170706c69656444656661756c744b657973223a5b5d2c22736f75726365223a7b2274797065223a2254222c226964223a2249222c2276657273696f6e223a2256222c22636f6e74656e74536861323536223a2265336230633434323938666331633134396166626634633839393666623932343237616534316534363439623933346361343935393931623738353262383535227d7d00000000
```

**DB-DecideIntent**：1724 bytes；SHA-256=772dc2ca13bd82f6ab8848599370ddcd541516dafa5b2aa6dd2fc90d36eb7fa6。

```text
494d3036362d524551554553542d310100000001000000740100000061010000006c010000006e0100000064010000007a0100000000000000010000007001000000e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b85501000000740100000061010000006c010000006e0100000064010000007a0100000000000000150000006173756e2e636f6e66696775726174696f6e2f76314b0000006366672d6465636964652d376437373266653964666635336236303830616637333864366662386238346131363434663562656434303639613336653864343766376635633865333162304b0000006366672d6465636964652d37643737326665396466663533623630383061663733386436666238623834613136343466356265643430363961333665386434376637663563386533316230010000006501000000e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855010000006501000000e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855150000006173756e2e636f6e66696775726174696f6e2f763100000000010000006d01000000e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855010000006901000000e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855010000006f01000000e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855010000006a01000000e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855010000007701000000e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b85512000000636f6e66696775726174696f6e2e73617665000000000200000000000000060000000c0000000000000010270000000000008096980000000000005a62020000000000f20300000000001a6173756e2d636f6e6669672d64622f6d75746174696f6e2d7631000000016d000000010000004065336230633434323938666331633134396166626634633839393666623932343237616534316534363439623933346361343935393931623738353262383535000000d00000001a6173756e2d636f6e6669672d62696e6172792d76322f7361766500000001630000000173000000016f00000000000000000000004031313965353534346563356661616237396337393963613462663366376262366666303638623230373161666238646331636564313839316639623466666330000000015400000001490000000156000000406533623063343432393866633163313439616662663463383939366662393234323761653431653436343962393334636134393539393162373835326238353500000000000002af7b22636f6e66696775726174696f6e4964223a2263222c2273636f70654964223a2273222c22636f6e74726163744d616a6f72223a312c22646566696e6974696f6e73223a7b226964223a2264222c2276657273696f6e223a2231222c22736368656d6156657273696f6e223a7b226d616a6f72223a312c226d696e6f72223a302c227061746368223a307d2c22756e6b6e6f776e506f6c696379223a2252656a656374222c22706172616d6574657273223a5b7b226b6579223a2278222c226b696e64223a22426f6f6c65616e222c22756e6974223a224e6f6e65222c227265717569726564223a747275652c2264656661756c7456616c7565223a6e756c6c2c22646563696d616c426f756e6473223a6e756c6c2c22646f75626c65426f756e6473223a6e756c6c2c22616c6c6f77656456616c756573223a5b5d2c2273656e736974697665223a747275657d5d2c22636f6e73747261696e7473223a5b5d2c22636f6e74656e74536861323536223a2263623265646235303731396231343763373932363362626438306638633430376134636133303835306637323138396438663066326634613737626137633835227d2c2276616c756573223a5b7b226b6579223a2278222c2276616c7565223a7b226b696e64223a22426f6f6c65616e222c22756e6974223a224e6f6e65222c2274657874223a2274727565227d7d5d2c22756e6b6e6f776e4669656c6473223a5b5d2c226170706c69656444656661756c744b657973223a5b5d2c22736f75726365223a7b2274797065223a2254222c226964223a2249222c2276657273696f6e223a2256222c22636f6e74656e74536861323536223a2265336230633434323938666331633134396166626634633839393666623932343237616534316534363439623933346361343935393931623738353262383535227d7d00000000
```

**DB-ConflictResult**：602 UTF8 bytes；SHA-256=d43152f12df99aeed002280478166c8b934283acbd50477a4edfef1135a6f595。这是技术Decide.Committed但业务Conflict的完整result，不生成snapshot/revision；前述payload的Expected0与实际revision1冲突。

```json
{"format":"asun-config-db-result-v1","readKind":null,"key":{"configurationId":"c","scopeId":"s"},"latestRevision":"1","hasMore":false,"mutationState":"Decided","requestSha256":"cbbd2211219122ea42311f9a7fa31fefdcb4386d7f70a89d02c8ed60626faad8","receipt":{"operation":{"key":{"configurationId":"c","scopeId":"s"},"operationId":"o"},"requestSha256":"cbbd2211219122ea42311f9a7fa31fefdcb4386d7f70a89d02c8ed60626faad8","outcome":"Conflict","actualRevision":"1","snapshot":null,"decidedAtUtc":"1970-01-01T00:00:00.0000000Z"},"originalMutation":null,"snapshots":[],"chunkSnapshot":null,"offset":"0","chunk":""}
```

定向变体断言：换Caller/等待预算/RequestedAtUtc不改Mutation及技术hash；换Source/defaults/Expected/定义或Binding任一语义变更改技术hash；换Scope/Store/Generation改token且改hash；同OperationId异内容token保持、hash改变，Runtime拒幂等键冲突。Read从Latest变Revision1需Kind=1及Revision presence1，其它字段仍固定零；Chunk Offset/Count/ref都入Owner读取编码，任意更改不能冒同读取。ConflictResult改Outcome为Committed但snapshot=null必须拒；OriginalMutation省略bytes/错两个技术identity必须拒。上述只核编码/形状，不证明数据库、C#、耐久或性能。

## 9. 适配、Watch与安全边界

### 9.1 输入与领域映射

文件/INI/XML/JSON输入adapter先有界读取并拒重复、非法UTF-8、未知codec/schema/超深结构；再构造RawConfiguration/DefinitionSet，不能把产品对象、JSON节点或SDK句柄带入Core。把历史INI字符串转为强类型须有Owner映射，`auto`/空值不能猜数值。平台machine-config/recipe-manifest仅只读参考，正式字段映射属于消费者Integration门，不复制设备/审批/质量字段。

完整Definition由Host显式取得并sealed，Core不自动注册/热更新。Scope是隔离标识而非授权凭据；Host检查用户权限和路径/网络访问，所有核心能力在无UI仍受Host的调用权限控制。库不会读取当前用户或环境来暗设权限。

### 9.2 Watch协议

Service以PollingInterval从Store.ListRevisionsAsync按最后投影revision轮询，只对完整已提交snapshot生成Committed事件，事件不带参数值。每订阅按键有界缓冲，不共享消费者可变状态；AfterRevision排他，Committed.Revision递增、OperationId非空。LastDeliveredRevision是已交给消费者的最后连续revision。

枚举不承诺exactly-once；消费者按(ConfigKey,Revision,OperationId)去重且副作用另做幂等。慢订阅导致缓冲溢出或历史不连续，清停该订阅新增Committed队列，输出一个GapDetected：Revision为已观察最高revision，LastDeliveredRevision为可补读水位，OperationId=null。该事件后枚举结束，消费者List分页补读并重新Watch；没有无限积压或默默跳过。Store不可用CFG-009结束枚举，保留已交付水位，不假造Gap补读成功。

WatchRequest预算用于每次轮询/分页，不是订阅无限执行的豁免，也不限制整个可取消订阅只能活一次Execution；一次轮询未退出绝不叠加后续轮询。端口超时/取消未排空时终止投影并以ServiceException报告资源轴，Owner保留Task/槽位；Close按§7.2等待真实归还。取消/DisposeAsync只结束本订阅，不取消其他订阅/Save；DisposeAsync使用Budget.Drain限制本次排空观察，未退出抛资源状态异常并保留后台Owner，不能Dispose外部Store。FileSystemWatcher可作Host刷新提示，但不能直接产生Committed事实或覆盖缓存，重启仍靠Store历史补读。

### 9.3 秘密、完整性与算法界限

SecretReference只保留引用，实际凭证服务由Host所有；不得在敏感diff/诊断/SuperTip/日志输出原文或值摘要。Snapshot/Candidate业务API确实含敏感参数，Host按权限决定是否展示/导出；SHA-256不是加密/签名，不能替代访问控制或防篡改认证。日志内容摘要也可能泄露低熵输入，默认不记录，需要审计时由Host受控保存引用。

本模块无图像/点云输入；HALCON路线、训练、噪声/遮挡判定和设备回读不适用。不核验或修改AsunImage内部，不添加HOperatorSet/halcondotnet引用。外部算法校验回执由算法/宿主Owner关联本内容摘要，本API不验证签名/有效期/质量、不把缺失回执写成PASS。

## 10. 可选WPF投影与操作流程（U1）

### 10.1 角色与完整页面

操作者读取当前配置/版本/差异及保存状态；具编辑权限者通过parameter-editor修改；工程师查看迁移报告/恢复诊断。Host拥有权限、语言/主题、EditorSession、服务生命周期和产品激活入口。配置控件只拥有选中版本/分页/比较投影/原保存等待状态，不创建第二份草稿、撤销栈、Preview/Recommend/Apply会话或事实缓存。

固定1920×1080验证viewport，先扣OS任务栏、边框/标题/状态栏，再按有效内容区域18%版本导航、57%编辑/差异主体、25%详情/诊断布局。宿主DockLayoutManager的LayoutGroup/LayoutPanel提供可恢复布局；历史/差异GridControl+TableView按Service分页、稳定选中键、允许长行滚动。中区parameter-editor的Inspector只Attach借用Host既有session；无编辑能力时显示只读版本/差异。大图像属于Host工作台，控件不抢占其主要区域。

顶栏固定显示配置/Scope、已保存revision、当前选择revision和未决OperationId状态，关键“保存候选”“查询保存结果”“重新读取”可直接访问。高级迁移/导出/布局命令可逐步展开，不能藏关键恢复。差异状态同时用图标/短文，不只颜色；敏感值显示遮罩，不显示摘要；无数据明确“尚无保存版本”。保存≠激活，按钮不命名“应用到设备”。

### 10.2 无猜测的流程与恢复

1. Bind时Host传ConfigKey/Core/Service/现有EditorSession与资源，Load当前→核身份/代次→只读投影→Host决定是否为编辑器设baseline。不能控件自动重建EditorSession。
2. Host把编辑器完整候选映射为RawConfiguration，Core.Validate/Normalize后与当前baseline Compare；全量Invalid定位字段，不保存合法子集。确认时Host持久原SaveRequest，然后控件调用同一Service.SaveAsync。
3. Committed显示“已保存，版本N”，Host自行决定是否更新编辑baseline/激活；Conflict保留原草稿并显示Expected/Actual，读最新后通过parameter-editor公开Rebase/人工选择，再用新OperationId保存。控件不能默认选远端/本地或自动合并。
4. Unknown冻结本键第二次保存/切换写入，保留候选、原OperationKey/ExpectedRevision；“查询保存结果”重复查原身份。Found Committed显示原版本；Found Conflict/NotCommitted显示原终态；NotFound只有权威确认后由Host决定原ID重试，不换ID掩盖；Unknown继续保留。
5. Resource DrainUnknown单独显示“后台操作尚未结束”，禁止Host释放共享Store。可以离开读页面，但未决工作项归Host保存。Close窗体只Unbind/退订，不隐式Save/Activate/Close共享服务。
6. 历史选择/分页/差异/Load都有presentation generation和ConfigKey/Revision匹配；切键/Unbind后迟到结果只留受控历史或丢弃投影，不抢当前页面。Watch Gap先补读，不猜当前版本。
7. 迁移只展示原/目标版本、计划/逐项变更、Lossy警示和候选；“保存迁移候选”仍完整验证/CAS/新ID，不直接激活。


### 10.3 完整公开绑定、工作项与投影合同（U1）

Wpf为net10.0-windows/UseWPF，引用Service/Core及parameter-editor的Core/Wpf公开程序集、已安装25.2.3；无UI不引用Wpf。以下类型唯一定义于Asun.Modules.Configuration.Wpf。合同片段using System、System.Collections.Immutable、System.Threading、System.Threading.Tasks及Core/Service；PE/PEW分别是Asun.Modules.ParameterEditor / Asun.Modules.ParameterEditor.Wpf别名；所有预算有限、集合不可变且有界，资源/权限错误沿ServiceException，不带产品ViewModel或私有表。

~~~csharp
using PE = Asun.Modules.ParameterEditor;
using PEW = Asun.Modules.ParameterEditor.Wpf;
public enum ConfigurationUiAction { Read, Edit, Save, Query, Migrate }
public enum ConfigurationUiState { Loading, Ready, Invalid, Saving, SavedAwaitingBaseline, Conflict, Unknown, Draining, Closed }
public sealed record UiAccessDecision(bool Allowed, DateTimeOffset ValidUntilUtc,
    CancellationToken Invalidated, string? ErrorResourceKey);
public interface IConfigurationUiAccess
{
    UiAccessDecision Check(ConfigKey key, ConfigurationUiAction action);
}
public sealed record WorkItemIdentity(string WorkItemId, string OperationId);
public sealed record PreparedConfigurationSave(string WorkItemId, SaveRequest Request);
public interface IConfigurationWorkItems
{
    WorkItemIdentity CreateIdentity(ConfigKey key); // 纯身份分配，无IO/设备副作用。
    Task<PreparedConfigurationSave> PrepareAsync(PreparedConfigurationSave original, CancellationToken token);
    Task<ImmutableArray<PreparedConfigurationSave>> LoadPendingAsync(ConfigKey key,
        CancellationToken token);
    Task RecordReceiptAsync(string workItemId, SaveReceipt receipt, CancellationToken token);
}
public sealed record UiOperationContext(string BindingId, long Generation,
    ConfigKey Key, OperationKey? Operation, string Phase, long RetainedBytes);
public sealed record UiRootReservation(Guid Id, string BindingId);
public interface IConfigurationUiRootOwner
{
    UiRootReservation ReserveBinding(string bindingId, long maximumRetainedBytes);
    void AttachBinding(UiRootReservation reservation, ImmutableArray<object> strongRoots, long retainedBytes);
    Task<CloseResult> ReleaseBindingAsync(UiRootReservation reservation, TimeSpan timeout);
    // 实现必须先预留/登记context和strongRoots，再调用start，保存真实Task。
    Task<T> StartOwned<T>(UiOperationContext context,
        ImmutableArray<object> strongRoots, Func<Task<T>> start);
    Task<CloseResult> ObserveBindingDrainAsync(string bindingId, TimeSpan timeout);
}
public sealed record EditorFieldBinding(string ConfigurationKey, PE.ParameterKey EditorKey);
public sealed record ConfigurationEditorBinding(PE.IParameterEditorSession Session,
    ImmutableArray<EditorFieldBinding> Fields);
public sealed record ConfigurationVersionOptions(string BindingId, int PageSize,
    int MaxProjectionRows, int MaxPendingWorkItems, TimeSpan UiCallTimeout,
    TimeSpan CleanupTimeout, OperationBudget Budget);
public sealed record ConfigurationVersionBinding(ConfigKey Key, IConfigurationCore Core,
    IConfigurationService Service, IConfigurationClock Clock,
    IConfigurationWorkItems WorkItems, IConfigurationUiRootOwner RootOwner,
    IConfigurationUiAccess Access, ConfigurationVersionOptions Options,
    NormalizedCandidate InitialCandidate, ulong ExpectedRevision,
    ConfigurationEditorBinding? Editor);
public sealed record ConfigurationPresentation(string ResourceCulture, string FormatCulture,
    string ThemeName, bool ReducedMotion, long Revision);
public interface IConfigurationTextResources : PEW.IEditorTextResources { }
public sealed record ConfigurationProjection(long Generation, ConfigKey Key,
    ConfigurationUiState State, ulong ExpectedRevision, ulong? SelectedRevision,
    ImmutableArray<ConfigurationSnapshot> History, DiffResult? Diff,
    ImmutableArray<ValidationDiagnostic> Errors, OperationKey? PendingOperation,
    SaveOutcome? Outcome, ResourceState Resource, string? MessageResourceKey);
public sealed record ConfigurationControlBinding(string BindingId,
    IConfigurationUiRootOwner RootOwner, IConfigurationClock Clock,
    ConfigurationVersionOptions Options, ConfigurationEditorBinding? Editor);
public interface IConfigurationVersionSession
{
    ConfigurationControlBinding ControlBinding { get; }
    ConfigurationProjection ReadProjection();
    IDisposable Subscribe(Action<ConfigurationProjection> observer);
    Task<ConfigurationProjection> ReloadAsync(CancellationToken token);
    Task<ConfigurationProjection> LoadHistoryAsync(ulong afterRevision, CancellationToken token);
    Task<ConfigurationProjection> SelectRevisionAsync(ulong revision, CancellationToken token);
    Task<ValidationResult> ValidateEditorAsync(CancellationToken token);
    Task<SaveResult> SaveCandidateAsync(long expectedEditorGeneration, CancellationToken token);
    Task<OperationLookup> QuerySaveAsync(OperationKey original, CancellationToken token);
    Task<MigrationResult> MigrateAsync(MigrationInput input, CancellationToken token);
    Task<CloseResult> CloseAsync(TimeSpan cleanupTimeout);
}
// public static class ConfigurationVersionSessionFactory：
// public static IConfigurationVersionSession Create(ConfigurationVersionBinding binding);
// public sealed class ConfigurationVersionControl : System.Windows.Controls.UserControl，无参构造：
// public void Bind(IConfigurationVersionSession session, PEW.InspectorOptions inspectorOptions,
//     IConfigurationTextResources resources, ConfigurationPresentation presentation);
// public Task SetPresentationAsync(ConfigurationPresentation presentation, CancellationToken token);
// public Task<CloseResult> UnbindAsync(TimeSpan cleanupTimeout);
// public Task<ConfigurationProjection> RefreshAsync(CancellationToken token);
~~~

Session是本模块自己的版本/恢复投影会话，不复制PE编辑会话/撤销。Factory前Host调用RootOwner.ReserveBinding并AttachBinding强持全部依赖，factory成功立即Attach追加Session/Control；factory只做有界验证，不IO/不启动Watch，失败由Host释放预留；第一次Reload才通过StartOwned调用LoadPending/Load。MaxProjectionRows/PageSize/MaxPendingWorkItems>0并受Profile/Service页上限；BindingId有界唯一、generation非负不回绕；InitialCandidate身份/摘要/定义必须与Core一致，ExpectedRevision必须来自Host已读权威基线（未存在才0），不由UI猜latest。ReadProjection/Subscribe为当前授权只读投影，Read撤回后抛CFG-019并清History/Diff/Errors载荷，观察者仅收到无载荷拒绝状态（以投影元数据原Key/generation及消息，History=[]）；Observer异常隔离、不阻塞Save，通知每绑定有界仅保最新generation，不当提交日志。每个公开命令在Session短锁校当前generation后登记，锁外运行；尚无Editor时只允许Read/History/Query/Migrate，SaveCandidate/ValidateEditor拒CFG-001，不提供“只读画面顺便保存”入口。Generation耗尽CFG-015阻新命令，终态查询保留。

ReserveBinding必须在任意factory前校slot/bytes上限，Attach不得超reserved maximum，失败不启动端口。ReleaseBindingAsync只有所有原Task及子借用已退出且Host交还/关闭协议完成才返回Released并唯一清根；它不能自动Dispose外部Service/PE/Store。未退出返回DrainUnknown保持reservation，重复Release只观察同原释放工作；Host正常进程结束前保留此根并处理未决。RootOwner是真实Host提供的生命周期端口，**不是测试Fake或静态ServiceLocator**；按§11.3先登记再调用、同步抛错、独立cleanup、迟到Task唯一归还、移交接收确认实现。RetainedBytes计所有强持输入，按Host显式Profile计slot/bytes；容量满StartOwned在start前抛CFG-002。RootOwner返回的Task与start原Task完成语义一致，不以有限等待Task替换真实Task；Session对其作UiCallTimeout观察并保留RootOwner的根。ObserveBindingDrain只观察不会清未退出引用，Close/Unbind返回DrainUnknown后RootOwner仍在窗口外强持；root不能是窗口字段唯一引用。借用Service/Clock/WorkItems/PE session，不Close/Dispose它们。

WorkItems是Host业务工作项持久Owner的端口：CreateIdentity是纯身份分配且必须立即返回；Session在Prepare前用该身份构造完整原SaveRequest并登记RootOwner，Prepare在返回前持久此不可变原件，不能改变WorkItemId/OperationId。绑定Key/Expected/Content/来源/默认标记必须精确，失败/观察未知时不能调用Save或生成第二身份；原Prepare重试只能同原身份/同请求。每binding一次Prepare，原Task/输入由RootOwner保留；迟到Prepared后保留工作项并Query原ID，不能静默自动Save。LoadPending返回有界原记录，超MaxPendingWorkItems拒绝而非截断；RecordReceipt幂等核原身份/RequestHash，失败不撤销Store已提交事实也不换ID。冷恢复只LoadPending→QueryOperation，不能自动重发或把Load最新当原操作结果。工作项ACL/保留由Host，UI不自建另一持久库。

SaveCandidateAsync步骤：当前Edit/Save授权、无Pending/Unknown Prepare/Save且未Close→调用PE.Read核成功且Draft.Generation精确expected→PE.Validate(Full)成功→从映射字段合成**完整**配置候选（未映射字段/opaque保留InitialCandidate）→Core.Validate/Normalize/Compare→CreateIdentity并RootOwner登记原请求→StartOwned Prepare原件→核返回请求→重新核授权/原PE generation及候选摘要→StartOwned Service.Save。授权失效或编辑已变时保留已Prepare工作项但不派发，查询权威原ID；不得用“界面按钮禁用”替代实际提交前授权。保存中必须由Host的PE访问策略拒Edit/Apply（与其Core Check共享），防另一入口修改同session；不能模块擅改PE状态。Committed转SavedAwaitingBaseline并禁第二Save，显示“已保存。请接收新基线。”（zh-TW“已儲存。請接收新基準。”、en-US“Saved. Accept the new baseline.”），不直接AdoptAppliedBaseline（本SaveReceipt不是PE.ApplyReceipt）；Host审核后以PE公开PlanRebase/Rebase或新Create明确接收基线，版本Session真Close/控件真Unbind后用最新权威Candidate/Revision重新构造Binding并Bind；不修改原请求/Expected，也不伪造AppliedReceipt解除门。Conflict/Unknown保留原PE草稿，RecordReceipt仅写原回执；人工解决后新工作项/新ID，不能改原请求。

SelectRevision只读历史，不自动改InitialCandidate/Expected/PE基线；历史Definition/Schema不同不得直接Compare，显示版本不兼容资源键并仅显示允许的版本元数据，迁移另走显式批准计划；Reload若latest变了显示Conflict/差异而不替换草稿。QuerySave须命中本绑定已恢复工作项且Key相等，原Task去重；未找到Host工作项拒CFG-001，不按用户输入ID查询敏感他人事实。Migrate只产候选/报告不Save，目标审核后Host显式重绑或通过PE公开原子编辑；不偷偷换Editor schema。Closed会话禁止新命令，Read只保有界无敏感终态；重复Close观察同工作。Session.Close只取消自身Watch/订阅/读取并等待这些子Task退出，不Close借用Service/PE。保存/Query已返回但Resource=DrainUnknown时仍有Service内部原Task，RootOwner继续强持Service/输入/工作项直到原Query确认资源Released，或Host关闭本身拥有的Service并取得Released；Session.Close不能用“我自己的await已结束”代替此证明。共享服务由总Owner确认，不能关闭它来验证单窗口结束。

Control从Session.ControlBinding取得唯一BindingId/RootOwner/Options/Editor，不能依靠隐藏注册表。Control.Bind在自己的Dispatcher执行，借用已构造Session，不Create PE/Service或发Save；重复同session/presentation幂等，换session必须Unbind Released后再Bind。若Editor=null，中区只读候选/差异，不禁整个版本功能。内部只把现有PE session传给无参ParameterEditorControl.Attach(session, inspectorOptions, resources, new PEW.EditorPresentation(...))，检查PeResult.Succeeded；SetPresentationAsync调用其现有同名方法，Unbind先停新UI命令、递增generation使迟到失效、取消本控件读取、退订，再对实际DetachAsync(token).AsTask登记/有限观察，不关闭session/service。若Detach未退，Unbind返回DrainUnknown，RootOwner保留control/Inspector/Dispatcher依赖，禁止马上销毁Dispatcher；Host先移交根Owner并确认，最终实际退出后再销窗。Session.Close由Host另行调用关闭版本投影，Control.Unbind只结束自己投影。

SetPresentation仅修改局部资源/主题/格式/减少动效，Revision必须递增；未结束IME保原token和解析culture，整控件菜单/SuperTip随同revision更新；语言/布局不改变hash/操作ID/Deadline。Refresh走Session.Reload，不产生第二读取事实。所有control异步方法调用必须在其Dispatcher，IO在后台；UI发布使用Dispatcher.InvokeAsync取得实际Task，经RootOwner先登记，不能仅BeginInvoke后认回调已退；迟到回调检查BindingId/generation/Key/session并受限额，Unbind等待实际执行/取消退出。Session无Dispatcher业务依赖，公开处理可无UI调用。

### 10.3.1 parameter-editor精确桥与不支持域

只消费当前[parameter-editor指导](../parameter-editor/DEVELOPMENT-GUIDE.md)的PE.IParameterEditorSession.Read/Validate/SetValues/PlanRebase/Rebase、ParameterEditorFactory.Create/Restore及PEW.ParameterEditorControl.Attach/SetPresentationAsync/DetachAsync。不发明GetDraft/Bind/Apply重载。PE Schema/ContentRef用其ParameterCanonical生成真实hash，Configuration定义hash不能冒作PE schema hash。

绑定映射必须一对一、ConfigurationKey已定义、EditorKey已存在，字段Kind/Unit/Required/Default/范围/Step精确对应且PE Nullable=false；ASCII小写Key域不同，Host提供稳定映射（可用p000001顺序标识，但映射存入Host版本，不因语言/排序变），不能把ExposureMs直接塞进PE不合法键。Fields不覆盖的配置字段只在独立只读Grid显示并原样保留，不能用PE.Text替身编辑。PE编辑器只校自己的映射子集，Configuration Core始终全量校约束/Unknown；这不是复制校验器。

| 配置值 | PE真实值与单位 | 精确性/拒绝 |
|---|---|---|
| Boolean/None | ParameterValue.Bool / UnitCode.None | 直接。 |
| Int32/None或Count、Int64/None或Count | ParameterValue.Int64；ValueType=Int64，Unit/DisplayUnit=None或Count | 有效闭区间与原整数格点保持；Int32反向checked固有域。PE.Int64不接受Millisecond。 |
| Decimal/None | ParameterValue.Decimal；ValueType=Decimal，Unit/DisplayUnit=None | 精确decimal系数/scale；不让PE.Decimal接受长度/角度单位。 |
| Int32/ms、Int64/ms、Duration/ms（Owner确认时间语义） | ParameterValue.DurationMicroseconds；ValueType=Duration，Unit=Microsecond，DisplayUnit=Millisecond | 同步×1000转换值/范围/默认/Step/Origin；范围或格点溢出拒桥、原字段只读。逆转换必须整除1000，再核原Int32/Int64/Duration域，Duration≥0。 |
| Decimal/mm（Owner确认长度）、Decimal/um或Length/um | ParameterValue.LengthMillimetres；ValueType=Length，Unit=Millimetre；DisplayUnit分别Millimetre/Micrometre | mm直映；um精确÷1000，逆×1000。按下述系数/scale算法核每项及逆编辑，不调用可能舍入的decimal除法。 |
| Decimal/deg（Owner确认角度） | ParameterValue.AngleDegrees；ValueType=Angle，Unit/DisplayUnit=Degree | 精确直映值/界限/Step/Origin，无wrap/归一化。 |
| Angle/deg、Ratio/None | AngleDegrees/Degree、Ratio/None | 精确对应。 |
| Enum/None、String/None | Enum/None、Text/None | enum成员/retired=false精确；String仅PE Text规则与定义完全一致且换行/Unicode可无损时编辑，否则只读；不能trim。 |
| Double、Uri、SecretReference、未映射单位/类型 | 无无损公开对应 | 保留配置只读Grid，不转Text/Decimal编辑，不公开敏感明文/值hash。 |

映射的物理语义由Host在Fields中显式绑定已核定义Owner/Version的字段，ms/mm/um/deg按该Owner已确认的时间/长度/角度解释；没有确认的不加入Fields，原样只读。Factory对该绑定冻结转换plan（仅内部值对象），不扩大EditorFieldBinding或PE API，不把配置Int32/Decimal的原Kind改为物理Kind保存。反向重建仍写原Configuration ValueKind/Unit及Invariant规范Text，Config Content/Definition hash继续由Core计算，与PE hash不同。

转换先取配置**有效域**：显式DecimalBounds与Int32/Int64固有域相交，Duration与0..long.MaxValue相交，Ratio与0..1相交，Decimal/Length/Angle与±decimal.MaxValue相交；两端均闭。PE Numeric显式给这个有效域的换算界限，而非用缺失界限放宽原类型。配置Step存在时原格点Origin=配置原Minimum（即使有效Minimum被固有域截取也不改变Origin），Step及Origin同倍率转换；Step不存在的Int32/Int64/Duration毫秒使用固有整数格点：PE.Step=1000、PE.StepOrigin=0，这是单位量化而非新增工艺步长。None/Count整数可Step=null、Origin=0；无Step的decimal域同样Step=null、Origin=0。数值必须构造PE.NumericConstraint，Bound.Inclusive=true；非数值Numeric=null。显式源Origin/Step/界限转换不精确、超PE long/decimal域则整个字段不桥接，不静默缩窄可编辑业务范围。

Int32/ms转换用BigInteger或checked long×1000（所有Int32固有域可表示），PE.Duration取整数微秒；反向divrem1000余数必须0，商须在原整数域及Core范围/格点内。Int64/ms或Duration/ms的整个有效整数域×1000若超long（例如无上限Duration）只读，不能把最大值夹到long.MaxValue/1000；合法明确上限时才编辑。配置Duration非负已在有效域体现，Int32/ms是否可负按Owner原定义，不能增加隐含正数限制。

十进制换算不走double/浮点或有舍入的decimal.Parse/除法：按§4.2得到有符号BigInteger系数c和scale s，值=c×10^-s；um→mm将s+3，去可约尾零后要求scale≤28且abs(c)≤2^96−1；mm→um先将c×1000，再去尾零/调整scale，复核同条件；mm/deg直映同样核精确性。逐一转换现值、Default、有效Min/Max、Step和原Origin，任一不可表示则本次绑定只读。每次PE编辑还执行逆换算和正向复算逐字段相等，Core全量Validate通过才允许保存；语言显示舍入文本不作反向初值。后来Reload/迁移出现不可映射值时重新检查plan并只读保原件，不用上一次可映射的值替代。

配置初始缺失不映射PE.Null；Entries省略键，默认来源用PE.ValueOrigin.Default/Explicit，AppliedDefaultKeys只作来源标记。Default C# null保null，不先补0。反向保持未编辑来源，确实编辑字段按其Origin更新；新增显式值不伪造默认。opaque完全不进入PE。跨字段两端映射且目标PE kind/规范unit仍相同才能用其现有Compare Predicate展示同关系；不同倍率先核转换后的同量纲关系，不能把原数字literal原封不动塞进PE。涉及只读/未映射字段由完整Core校验并定位原Key，不发明PE AST扩展。

固定桥反例（合成参数，只证规格）：ExposureMs=Int32/ms、bounds(0,1000,1)、Origin0、无默认、现20 → PE.DurationMicroseconds(20000)、Numeric(0,1000000,1000,0)、DisplayUnit=Millisecond；编辑30000us回程30ms，30001us被格点拒且逆divrem仍拒，不能舍入30。无业务Step的Int32/ms仍以1000us量化；默认7ms→7000us。Int32[-2147483648,2147483647]ms两端→[-2147483648000,2147483647000]us并保持signed域；Int64/ms上限9223372036854776×1000溢出，整个字段只读。Decimal/mm值1.25/bounds(0,10,0.25)→PE.LengthMillimetres(1.25)/同界限步长，Decimal/deg -45/bounds(-180,180,0.5)→PE.AngleDegrees(-45)/同界限步长。Decimal/um值1250/bounds(0,2000,250)/default500→mm值1.25/bounds(0,2,0.25)/default0.5，PE1.5mm回1500um；um的1e-28转1e-31mm不可表示，现值或Step为此均只读。未知`msec`/未确认量纲只读，PE.Int64/Millisecond或PE.Decimal/Millimetre必须被现PE-1007拒而非扩展支持。

Host必须以当前PE公开Create(schema,baseline,options,access,TimeProvider,preview:null,recommendation:null,apply:null)创建本绑定专用编辑session，防另一Apply入口；PE与配置Save权限均由同Host策略裁决。若Host借用已有含Apply/未决operation的session，绑定只读并显示恢复要求，不能假装Disable按钮就是禁止Apply。保存后基线更新用PE公开PlanRebase/Rebase，或等原session真Close后新Create；ApplyReceipt必须来自PE Apply port真实Owner，不由配置控件伪造。

主控跨模块事项仅有未来扩展Double/Uri/SecretReference/超域单位的**可编辑**能力（可选需求），以及两模块访问策略共享事实映射；当前只读保留路线已闭合，不阻断U1整体绑定。对方Restore签名现已在其factory整合，旧“待整合”提示撤销，本模块不改对方文件。

### 10.4 三语、键盘和视觉验收

| 场景 | zh-CN / zh-TW / en-US正文资源 |
|---|---|
| 保存 | 保存候选 / 儲存候選 / Save candidate |
| 成功 | 已保存，版本{0} / 已儲存，版本{0} / Saved, revision {0} |
| 冲突 | 版本已变化。读取最新版本后比较。 / 版本已變更。讀取最新版本後比較。 / The revision changed. Reload and compare. |
| 未知 | 尚未确认保存结果。请查询原操作。 / 尚未確認儲存結果。請查詢原操作。 / Save result is unconfirmed. Query the original operation. |
| 排空未知 | 后台操作尚未结束。 / 背景操作尚未結束。 / The background operation is still running. |
| 缺口 | 版本通知中断。重新读取历史。 / 版本通知中斷。重新讀取歷史。 / Revision notifications stopped. Reload history. |

所有标题、参数名/单位、状态、权限拒绝、菜单、验证/诊断/恢复和SuperTip资源化，Owner提供参数资源键；新语言可扩展。核心异常仅资源键，不直接显示key/原始异常。缺译按en-US再中性短标签回退并诊断；语言切换保留编辑token/IME/选择/代次，显示格式与持久Invariant编码分离，无模块语言切换按钮。

键盘Tab按导航→编辑/差异→保存/查询→详情，Enter只确认当前编辑、不隐式Save；明确命令快捷键Ctrl+S须过同一验证/权限/未决门，Esc取消当前编辑/投影等待，不声称撤销提交。Grid焦点行和错误定位可见，长英文、125/150%宿主既定DPI、三语热切、UIA Name/HelpText在同一1920×1080基线验证；不改用户显示设置或加分辨率矩阵。SuperTip说明保存/生效区别、容量、冲突/未知恢复，BarItem.SuperTip与普通控件ToolTip使用相应25.2API；布局/字体/间距/图标/动画按DEV-UI-040，视觉品质和功能分别验收。



### 10.5 紧凑25.2.3控件、两个STA Host与验证

冻结控件内三列Grid（不嵌套第二个DockLayoutManager）：有效宽度18/57/25%，Host自己的DockLayoutManager容纳整个ConfigurationVersionControl，LayoutPanel标题由Host资源。顶栏44 DIP：配置/Scope、已保存版本和草稿状态；命令栏36 DIP固定保存/验证/查询；底栏28 DIP显示操作/资源轴/诊断码。容器margin=12 DIP、gap=8、卡片padding=12，标题16 semibold、正文14、次要12，历史/差异行28–32 DIP；行数/页来自Options，不提前宣称无限虚拟化。三列最小宽180/480/260 DIP，1920×1080有效区按实际边框/taskbar测；窄有效区优先折叠右详情为显式Flyout，不藏查询/Unknown状态，主控同一viewport验证。

左GridControl/TableView显示revision、UTC本地化显示时间、来源短标识，右详情显示Definition/Schema、原操作、资源状态、诊断和迁移报告；中间为“参数 / 差异”两个Tab，参数页可选PEW.ParameterEditorControl加未映射只读Grid，差异页GridControl+TableView显示字段资源名、差异图标/短文、单位、敏感遮罩。禁止把每个参数变成独立浮窗；选择行联动详情/错误RelatedKeys。对可编辑/只读/忙/冲突/未知/排空状态分别有图标和文字，柔和卡片边界和统一主题，错误常驻不只红色。局部主题与Host一致，ThemeManager只作用控件，不设全局ApplicationThemeName。动效仅短选择/展开提示，ReducedMotion关闭，不延迟安全命令。

已核公开组合：GridControl.View配置TableView，读取历史分页不自动加载全表；宿主DockLayoutManager/LayoutGroup/LayoutPanel；BarItem.SuperTip用于命令，普通控件ToolTip包装SuperTipControl；普通WPF Grid/TabControl为稳态布局，不猜未核控件属性。实际25.2.3编译/API行为在U1验收，不能把官网25.2.10当升级理由。关键Save/Query常驻；Flyout/DropDown只承载次要高级迁移详情，不装必要恢复。AutomationId=<BindingId>.<稳定command/key>，不使用翻译/可见行index；SuperTip讲错误影响/安全恢复而非AI口号。

U1.Tests为Microsoft.NET.Sdk、net10.0-windows、UseWPF=true、OutputType=Exe，无测试NuGet，引用Wpf/Core/Service、PE Core/Wpf及本机已装DevExpress25.2.3（引用路径沿本机固定程序集，不下载）。[STAThread] Main创建Application/Dispatcher，一次固定1920×1080验证viewport，不改显示设置。私有HarnessRootOwner在Application/Window/session/control工厂前预留；Window关闭事件先禁新命令，注册Unbind/Session.Close/PE.Close/Service.Close/Store.Close原Task，再独立5s观察/cleanup，未Released不Shutdown Dispatcher；转移未确认保留根Owner。UI测试例真实观察10s、套件180s、外层240s。主控可检源码/API准备，不冒称本轮已运行STA。

| Host | 完整构造/调用 | 断言 |
|---|---|---|
| DeviceVersionHost | ReserveBinding并Attach本节STA根→§11.3.1 Device参数/真实hash→ScriptedStore+SystemClock→Core/Service→PE schema含p000001(ValueType=Duration、Unit=Microsecond、DisplayUnit=Millisecond)、Numeric闭界(0,1000000,step1000,origin0)、ReadOnly=false、Nullable=false、Required=true、无默认、ApplyMode.OwnerDefined、无PE Apply/Preview/Recommend→PE.ParameterCanonical生成schema/snapshot真实摘要，初始Entry=DurationMicroseconds(20000)/Explicit，Owner为设备配置稳定ContentRef且Revision=0；PE预算由Host合成Profile显式传，operation/close=5s→new PE.ParameterEditorFactory().Create(schema,baseline,options,access,TimeProvider.System,preview:null,recommendation:null,apply:null)核PeResult.Succeeded→ConfigurationVersionBinding(InitialCandidate仍为Int32/ms规范20,Expected=0,Editor=现session映射)→ConfigurationVersionSessionFactory.Create→new ConfigurationVersionControl()/Bind→Reload/Validate→PE session.SetValue(new PE.ParameterKey("p000001"),new PE.ParameterValue.DurationMicroseconds(30000),当前Draft.Generation,PE.EditOrigin.User)核Succeeded→SaveCandidateAsync精确代次→Query原操作/History/选择只读→SetPresentation三语→独立Unbind/所有Owner关闭 | 30000us回Int32/ms30保存revision1；30001us先被PE Step拒，反向也拒，工作项不创建。x或Scope未映射不猜；PE草稿不隐式Adopt，权限Save失效不写；关闭一窗口不Close另一Service。 |
| AlgorithmVersionHost | 另一STA测试场景同类根，Score=Ratio/None和Double阈值（定义Owner给合成0..1，用示例0.5）并存；映射只有score→p000001(PE Ratio/None)，Double原样只读Grid；另一Scope/Source/PE Owner、同样PE Create但无Apply；Control Bind、PE.SetValues Atomic改score为0.8、验证完整Core含Double、保存/查询/选历史、迁移候选只展示、三语/键盘/解绑 | Double不转Text/Decimal编辑，反向完整候选保留其binary64/来源；与Device隔离，无设备SDK/图像/生产表；删DeviceHost引用仍能独立启动。 |

两个Host是同Tests Exe的--host device/algorithm独立入口，每次独立依赖/语言/Scope/Session，不是复制产品Shell。PE构造中的资源字符串来自各Host三语资源，Schema名称/hash不是配置摘要；数值/时间都是合成测试不是客户阈值。预算合成：ParameterResourceBudget(128,4096,1048576,1048576,512,16,128,32,1048576,4,16,16,1048576,32,16)，ParameterOperationPolicy(5s,5s)，TimeProvider.System；Baseline Snapshot Generation=0、Entries为精确值/Explicit并用ParameterCanonical算hash，Owner=ContentRef(device-config-owner或algorithm-config-owner,"1",SHA256相应严格UTF8字面)，Revision=0。Read/所有PeResult须核Succeeded，不用空Value继续。

两STA Host补充PE物理桥场景：Device同定义Owner新增三个合成键，OffsetMm=Decimal/mm bounds(0,10,0.25)、初始1.25→p000002 Length/Millimetre值1.25；YawDeg=Decimal/deg bounds(-180,180,0.5)、初始-45→p000003 Angle/Degree值-45；PitchUm=Decimal/um bounds(0,2000,250)/default500、初始1250→p000004 Length/Millimetre、DisplayUnit Micrometre、Numeric(0,2,0.25,0)/default0.5、现1.25。Definitions/InitialCandidate的真实Core摘要及PE Schema/Snapshot摘要都由各自完整规范编码生成，不沿用Exposure单字段hash；EditorFieldBinding四条一对一。Atomic EditBatch ExpectedGeneration来自Read，分别Set LengthMillimetres(1.5)/AngleDegrees(-44.5)/LengthMillimetres(1.5)，逆合成OffsetMm1.5/YawDeg-44.5/PitchUm1500、完整Core Validate再Save；History/Query回读原Decimal kind/unit。再独立重建带Step=1e-28um/超long毫秒上限/未知单位的绑定，拒该字段编辑并原样只读Grid展示；不能把失败字段改PE.Text。Algorithm Host追加Decimal/mm的独立算法偏移字段并同样精确回程，Double仍只读，两个Host各自编译/启动不靠另一私有转换函数。测试值不迁入客户Definition。

专项场景：Factory失败释放预留；WorkItems Prepare响应丢失根Owner/原ID保持；Save提交后UI掉响应只Query；Unbind/Detach迟到+Dispatcher保留；Root移交拒绝；跨Binding迟到无投影；Unknown只查询；Conflict保草稿；long/微秒转换溢出/decimal单位不精确只读；敏感列无明文/hash；View/Save权限撤回/三语切换IME/Tab/Enter/Ctrl+S/Esc/UIA/英文长度和卡片布局分别断言。上述UI命令路径与无UI内容hash/回执一致，截图只作视觉证据不冒称功能验收。计划build/run命令见§13.1，真实WPF/设备/产品接线尚未执行。

## 11. 无UI最小调用与故障夹具

### 11.1 C1完整构造示例

下面是针对§4.3合同的完整Program形状，Core工程获准实现后可引用运行；本轮未创建工程、未编译。ExposureMs=20、范围0..1000及资源预算都是**合成契约例**，不是客户曝光/节拍或已采纳性能目标；实际Definition/limits由消费者Profile提供。所有对象可由公开类型构造，Definition摘要由SealDefinitions真实计算。

```csharp
using System;
using System.Collections.Generic;
using System.Collections.Immutable;
using System.Security.Cryptography;
using System.Text;
using Asun.Modules.Configuration;

internal static class Program
{
    public static int Main()
    {
        var schema = new SemanticVersion(1, 0, 0);
        var core = ConfigurationModuleFactory.CreateCore(
            new ConfigurationCoreOptions(1, schema,
                new CoreLimits(128, 64, 128, 4096, 1024 * 1024, 64 * 1024)));
        var definitions = core.SealDefinitions(new DefinitionSet(
            "device-tool", "example-1", schema, SchemaPolicy.Reject,
            ImmutableArray.Create(new ParameterDefinition(
                "ExposureMs", ValueKind.Int32, "ms", true, null,
                new DecimalBounds(0m, 1000m, 1m), null,
                ImmutableArray<string>.Empty, false)),
            ImmutableArray<FieldConstraint>.Empty, ""));
        var sourceHash = Convert.ToHexString(
            SHA256.HashData(Encoding.UTF8.GetBytes("synthetic-example-1")))
            .ToLowerInvariant();
        var source = new SourceRef("Example", "device-tool", "1", sourceHash);
        var values = new Dictionary<string, ParameterValue>(StringComparer.Ordinal)
        { ["ExposureMs"] = new(ValueKind.Int32, "ms", "0020") };
        var raw = new RawConfiguration("camera-settings", "tool-A", values,
            new Dictionary<string, RawUnknownField>(StringComparer.Ordinal), source);
        var candidate = core.CreateCandidate(definitions, raw);
        values["ExposureMs"] = new(ValueKind.Int32, "ms", "30");
        if (!core.Validate(candidate).IsValid) return 1;
        var normalized = core.Normalize(candidate);
        if (normalized.Candidate.Values["ExposureMs"].Text != "20") return 2;
        if (core.Compare(null, normalized).Entries.Length != 1) return 3;
        if (!core.Compare(normalized, normalized).Entries.IsEmpty) return 4;
        Console.WriteLine(normalized.ContentSha256);
        return 0;
    }
}
```

期望：输入变成30不改变已接收候选20；null基线一项Added，自比较空；重复运行同Definition/Source/值得到同ContentSha256。不写硬编码假摘要，不生成OperationId/revision，不依赖UI/Store。第二Host以§17不同定义和Scope执行同顺序，不复制Core或换工厂。

### 11.2 C2无UI接入顺序及真实端口夹具

Service最小宿主的构造順序：用C1工厂→宿主显式提供实现IConfigurationStore的端口和IConfigurationClock→ConfigurationServiceFactory.Create(options, core, store, clock, migrations:null)→LoadAsync→Core.CreateCandidate/Normalize/Compare→宿主持久化SaveRequest原工作项→SaveAsync→必要QueryOperationAsync→ListRevisions/Watch→CloseAsync→只有Released后由Store Owner关闭端口。

示例options仍是合成值：ServiceLimits(32, 4*1024*1024, 4, 8, 64, 64, 128, 8, 32)，PollingInterval=250ms，SupportedReadVersions=ImmutableArray.Create(core.Options)；需要旧Schema时显式加入已批准的CoreOptions。预算Queue=2s/Execution=5s/CommitWait=2s/Drain=5s。OperationId由Host稳定创建并在调用前持久化；使用规范Candidate身份构造ConfigKey和OperationKey，ExpectedRevision来自Load的权威revision（不存在才0）。没有权限/Store时不得拿空端口补出成功。

C2.Tests在上述唯一目录内实现ScriptedStore及ManualClock，逐项实现§6.2全部公开方法，不给Core增加测试专用钩子。ScriptedStore拥有按ConfigKey的不可变历史、原请求/回执和显式Pending；暴露门控点BeforeIntent/AfterIntent/BeforeCommit/AfterCommitBeforeResponse/BeforeReturn。ManualClock仅推进单调期限/UTC，不依靠真实长sleep。每条测试结束核在途计数/资源归还；故意未退出时断言DrainUnknown并保留Task而不是让夹具虚假释放。

| 夹具脚本 / 调用 | 断言 |
|---|---|
| Save新ID expected=0→Load→原ID重试→Query→List | revision=1；重试原回执完全相同；只一条history。 |
| 同键两个新ID expected=0，并发越过BeforeCommit | 一个Committed一个Conflict；没有第二revision。跨Scope不串值。 |
| AfterCommitBeforeResponse丢响应/取消→Query | Save Unknown可暂现；Query返回原Committed；新ID禁止自动重试。 |
| AfterIntent冻结→期限/Close→稍后解除 | DrainUnknown保留输入和Task；未提前Dispose；任务完成仅一次Released。 |
| 非合作Store抛IO错误且无法查询 | Unknown，不是NotCommitted；不会默默替换Store。 |
| 已决定Conflict后同ID改expected/值 | CFG-018，原Conflict保持；新ID另按CAS。 |
| Watch每次分页，慢枚举溢出→补读 | 一个Gap及水位，保存不阻塞；补读后无静默缺版本。 |
| 迁移计划零/多/错hash/漏报告/跨单位 | CFG-007，无Save；原候选与历史不变。 |

这些是无UI软件契约验证，不能冒称文件/数据库真实恢复。A1在同一调用顺序下替换真实Store，故障位置必须实际触发OS/数据库行为；U1只消费已核验API，不成为C2初始化条件。


### 11.3 C2最小宿主：Factory前根Owner与有限观察

旧例中Factory位于try前、finally Close覆盖业务错误且方法离栈丢Owner，现由本节替换。以下RootOwner/Slot/RunReport是**harness私有类型**，不属于生产公开API、不要求产品引用测试库；生产Host必须实现相同所有权协议。唯一位置Service.Tests/Program.cs及其私有Harness目录，无新工程/全局产品服务。Program创建一个进程根Owner（强引用生存至进程退出），在Factory前预留slot；容量MaxSlots=8、MaxHeldBytes=8 MiB、每slot最大16个在途观察记录，均为合成测试限额。满时不调用Factory/端口，返回失败；不逐操作产生不可回收slot。

slot字段必须有：HostId、ConfigKey、原OperationKey/SaveRequest、已深冻结Definition/Candidate/Source、Service/Store/provider/clock引用、是否拥有各端口Dispose权限、CTS、原Task/登记阶段/调用序号、单调deadline、独立BusinessError和CleanupErrors、Close观察列表、终态知识与资源轴、转移待确认标记。slot登记锁短持，不能跨端口调用/await；Host还必须保留需要重启的原工作项，根Owner只解决本进程资源强持。

1. **Reserve→Attach→Construct**：先预留，再把Store/provider/clock及输入绑入slot，再登记Factory调用标记，最后在try中调用factory。factory同步抛错也记入BusinessError；规范factory不能启动后台IO/借用或把未返回实例藏在全局，构造失败无已接纳工作，回滚其纯托管状态。Host还需排空/释放自己已经创建的端口，不能以“无service”忽略它们；成功对象立即绑slot后才进行下一调用。
2. **RegisterBeforeInvoke**：在slot中先留Phase/Identity/Input/CTS条目，再调用委托取得原Task，再原子填写Task。同步抛错记录原业务错误与资源状态；已登记条目直到确认该委托没有启动异步工作或其公开资源协议排空才关闭。端口不得在同步抛错前启动不可追踪后台资源；违反则保留slot、验收失败。返回null Task拒绝。ValueTask端口仅一次AsTask，保存该Task，不重复消费。
3. **Observe**：Load/Save/Query/List/Migrate/Watch MoveNext/Dispose各自原Task保存在slot。方法观察截止用真实单调计时（harness每调用10s），Task.WaitAsync有限观察不改变原Task所有权。超时请求合作取消，保留slot/Task/输入并记录观察失败；每个Task完成continuation观察异常、核回执/资源、按调用序号发布迟到结果，不覆盖后继generation。Task.WhenAny/观察方法返回都不是Released。
4. **IndependentCleanup**：捕获BusinessError后执行独立cleanup，不能沿用已取消的业务token。首次登记CloseAsync之前创建Close调用记录；Close观察5s，保存原Close Task及结果。原Close Task尚未结束时再观察同一Task；它已经返回DrainUnknown时，后续CloseAsync是对Service内部同一关闭工作的**新有限观察Task**，也先登记，不能把已完成的DrainUnknown Task当排空终结。所有close异常只记CleanupErrors，不throw覆盖BusinessError。
5. **LateCompletion**：根Owner每slot只装一次原Task完成continuation；最终业务/查询知识和Task资源终态分开。所有任务真实结束、Service.Close确认Released、所有Watch/Inspector等子借用退出，且Host拥有的Store实际关闭完成，才通过Interlocked状态归还slot/清引用一次。Store共享时只归还该Host借用，不Dispose共享端口；总Owner等待所有Host。Close先完成但原调用仍在运行视为契约失败，不能清slot。
6. **Unresolved/Transfer**：任一未退出返回RunReport(Resource=DrainUnknown, SlotId, BusinessError, CleanupErrors)，根Owner继续强持而不是把对象仅留在RunReport。进程正常停机前继续有限观察；无法退出以非零结束harness，不报验收PASS。转交到另一个**进程内**根Owner须接收方先校容量、注册同一Task/资源强引用并返回接受token，源核token后原子交接，再去重唯一释放；未确认则源保持Owner。跨进程不能转Task，须保留工作项、等待旧进程退出/Store fence后冷Query，绝不能用“已发送移交消息”释放资源。

### 11.3.1 两个自足Host的调用卡

两者只通过§4.3/§6.2公开API；私有slot方法仅用于上述harness持有/观察协议。Program按以下完整调用卡构造对象，不能要求读者复用旧缺陷代码：

| 字段 | DeviceHost | AlgorithmHost |
|---|---|---|
| HostId/ConfigKey/原操作 | device-A / (camera-settings,tool-A) / example-device-1 | algorithm-B / (algorithm-settings,offline-tool-B) / example-algorithm-1 |
| 定义/规范值 | device-example/1，ExposureMs=Int32/ms、Required=true、bounds(0,1000,1)、无默认、非敏感；raw=0020→20 | algorithm-example/1，Score=Ratio/None、Required=true、bounds(0,1,null)、无默认、非敏感；raw=0.7500→0.75 |
| 来源 | (Example,device-A,1,SHA256严格UTF8 device-example) | (Example,algorithm-B,1,SHA256严格UTF8 algorithm-example) |
| 注入 | 新ScriptedStore、SystemClock（真实单调/Delay）；无MigrationProvider | 另一新ScriptedStore、另一SystemClock；无MigrationProvider |
| Core/service | 两者均new SemanticVersion(1,0,0)、ContractMajor=1、CoreLimits(128,64,128,4096,1048576,65536)，工厂Core；ServiceLimits(32,4194304,4,8,64,64,128,8,32)、Polling=250ms、SupportedReadVersions=[core.Options]；工厂Service | 同一API/预算，不引用DeviceHost内部对象 |
| Budget | new OperationBudget(2s,5s,2s,5s)，独立CTS；Host观察10s、cleanup5s | 同左，独立CTS |

每Host都：根Owner.Reserve并Attach注入项→try内Core factory/SealDefinitions（空摘要由Core算真hash）→Service factory并绑slot→Register Load最新，要求fresh Store NotFound/Released→CreateCandidate/Validate/Normalize→Compare(null)仅一Added→形成完整SaveRequest(key原操作,Expected=0,normalized,budget)，先存slot及工作项→Register Save→正常要求Committed、revision1；Unknown只Register原OperationKey Query，不新ID→Register相同原Save重试，原回执/时间/摘要相同且不增revision→Register Query Found原Committed→Register List(after=0,size=8)，一条revision1→Register Load(revision=1)及Compare自比较空→Register Watch(after=0,buffer=8)，MoveNext读revision1，取消并Register DisposeAsync→独立cleanup Close至Released→端口Owner关闭→slot唯一归还。每一步失败保留首个BusinessError、执行cleanup，不跳过Task登记。原Save NotCommitted/Conflict时该正常例失败而不是新ID偷偷修复。

另一个共享Store的测试由进程根Owner持有Store，两个Host仅借用；并行不同Scope各revision1，关闭A不影响B。再构造第三个同ConfigKey调用卡、不同OperationId/Expected=0，确认CAS只有一成功；同键本Service队列不允许用闩锁等“两个执行均开始”，跨Service两个Owner实际竞争Store锁。ManualClock只用于故障卡：Advance同时唤醒Delay，BeforeIntent/AfterIntent/AfterCommitBeforeResponse门保持原Task，在cleanup释放闩锁后再核唯一释放。Factory抛错、端口同步抛错、Close抛错+原业务抛错、观察到期后迟到、移交未确认、根Owner满均须专项断言。

## 12. 两个视角的全能力走查

### 12.1 普通程序员：每项能力的输入、路径与反例

| 能力 | 正常输入→预期 | 必须拒绝/恢复的反例 |
|---|---|---|
| SealDefinitions | 合法Definition、空hash→复制/规范排序/真实hash | 默认值越界、约束悬空、重复键、错误hash、非法enum→CFG-004；超限CFG-002。 |
| CreateCandidate / Validate | raw含明示合法默认缺项→补默认并标记；完整值→IsValid | Required无默认、跨字段关系失败、部分非法→整候选Invalid，不保存合法子集。空定义/空值合法但不等于允许生产激活。 |
| Normalize | Int32 +0020/20→20相同hash；decimal -0.00→0 | 孤立surrogate、NaN/Infinity、URI无absolute、非法单位→拒，不夹紧/trim。最小decimal规范后可再解析，不输出指数。 |
| Compare | 同定义同键相等→空；null→Added | 伪造hash CFG-017，定义/schema变化需迁移；敏感/opaque无值hash或明文。 |
| Load | 最新/指定已存在revision→完整不可变snapshot | 不存在NotFound，IO失败Unavailable，损坏Corrupt；不自动创建默认或清空旧缓存。 |
| Save / Query | 新ID正确CAS→revision+1及原回执；原ID重试不增版 | 同ID不同请求CFG-018；结果未知只查原身份；Found/NotFound/Unknown不得混写。 |
| History / Watch | 升序排他分页，已提交事件可补读 | 同键乱序/坏载荷CFG-017；慢订阅Gap后结束，不能无限缓存或以事件推定事务。 |
| MigrateCandidateAsync | 唯一精确批准计划→目标候选/完整报告 | 零/多计划、删除未报告、单位舍入未批准→CFG-007；超时取消保留provider Task并表达资源轴；不Save/激活。 |
| Close | 停接纳、已运行真实结束→Released | 超时但Store仍访问输入→DrainUnknown保留资源；重复Close不另起关闭工作。 |
| 发布/回退 | 保留精确旧codec/Schema读能力，另发新CAS保存旧值 | 二进制回退不删新历史/原回执；无法读新Schema即只读拒绝，而非重写。 |
| 可选UI | Host已有编辑会话，验证/差异/确认保存/查询 | 双草稿、未知时第二保存、窗口关闭隐式激活、迟到投影换当前、语言改hash均失败。 |

### 12.2 集成人/操作者：故障到安全下一步

| 情形 | 保留 / 安全动作 / 可判定验收 |
|---|---|
| 设备工具与算法工具均使用相同字段名 | 各自Definition和Scope；一方错输入/取消/关闭不影响另一方；移除第一Host仍可独立构建第二Host。 |
| 大文本/opaque、定义很多但值很少 | Core计定义+输入总字节及单项上限；接纳前拒绝，不复制无界；Service计队列字节，不只数请求。 |
| 两个进程同键CAS | Store权威锁/事务，唯一个成功；本进程队列不能替代跨进程保护。 |
| 保存已提交，界面未收到响应就重启 | Host恢复原工作项，Query原OperationKey→原revision；不以新ID重复提交。 |
| 进程在写blob后退出 | 未被current引用不是提交；原Pending需fence/恢复；不能按文件时间自动上版。 |
| current损坏，backup看似可读 | 隔离写入并保留两者；不静默退旧导致丢新事实；Unknown/Corrupt可见。 |
| 磁盘/回执容量耗尽 | 保留历史及原回执；拒新操作并报告CFG-002/009，不能先删回执腾空间。 |
| 输入JSON重复键、旧Schema未知字段 | adapter先拒重复；Unknown按明确策略保留/拒；无法迁移保留原件，不猜auto/单位。 |
| 相机未连接或缺真实图像 | 参数纯校验/保存仍可进行；设备应用/算法有效性由其Owner独立阻断，不伪造回读或视觉PASS。 |
| 保存冲突 | 保留草稿/原Conflict，读最新比较并人工解决；新ExpectedRevision必须新ID。 |
| 窗口关闭/共享服务多控件 | 只结束该控件投影/订阅，Host保存未决工作项，资源未退出不Dispose；其他控件读服务仍可用。 |
| 新Definition单位从um变mm | 必须批准转换计划并列规则/精度/Lossy，再验证目标；不能Compare直接掩盖变定义。 |
| 空合法配置 | 允许纯候选/Store保存，Host明确业务能否“清空”；不因此获得运行/激活许可。 |
| UI长英文、热切三语、IME数值中切语言 | 同一viewport无遮挡关键查询/状态；token/选择不丢，不重解析/改值；诊断可键盘定位。 |

## 13. 分片测试与验收断言

文档阶段只规定测试，不创建/执行产品测试。规格的首要消费者是实现工程师与对应测试工程；以下断言与真实代码改动一起落地，不为本轮审核造独立测试报告。

| 切片 | 必需测试 | 完成断言 |
|---|---|---|
| C1 | 所有ValueKind、最小/最大数值、decimal scale/溢出步长、double±0/非有限、严格Unicode、URI保留、范围/默认/关联规则、缺失/空串、Unknown三策略、default集合、容量边界、输入隔离 | 不抛不可解释溢出/文化异常；规范输出可重新Validate；全量Invalid不产生正常结果；同Core并发确定。 |
| C1 codec | 小型固定字节Golden覆盖长度前缀/大小端/存在位/排序/空集合/敏感字段/Source与defaults元数据 | Definition/Content/Value/Save四域固定字节和hash；Content忽略身份来源，Save包含来源/默认标记；伪造内容/定义hash拒绝。不能只调用被测codec生成期望。 |
| C1 Diff | 添加/删除/变更/null、自比较、交换两侧、变定义、敏感/opaque | 稳定顺序，无敏感摘要/文本；普通Changed存在双方hash；不同定义不比较。 |
| C2 | §11.2真实公开端口、原操作不同hash、CAS/修订耗尽、入队容量、取消每个门、迟到/抛错/未知查询、Close重复、fence恢复 | 原请求至多一次提交，已提交不被取消覆盖；Unknown不当NotFound；槽位/输入只真实结束后释放。 |
| C2迁移/Watch | 唯一精确计划/完整报告/损坏源，慢订阅/断线/重复事件/重连补读 | 原件保留且不Save；无损/有损按批准规则；Save不被订阅阻塞，Gap水位可补读。 |
| A1文件 | 实际磁盘满/权限拒绝/锁竞争、两进程CAS、写意图/写blob/flush/replace/回执响应各点杀进程、current/backup/blob篡改 | 完整旧或新已提交状态及同原操作恢复；不按mtime、不吞Corrupt；容量拒新而不删旧。ProcessCrash独立记录，未做PowerLoss不声称通过。 |
| A1数据库 | §8.4注册Prepare/Decide/Read/原Mutation查询、关键CAS行=1、原件及完整快照分页、冷恢复/技术Committed+业务Conflict、取消/预算/迟到及异常清理、Owner Golden | snapshot+revision+回执一致；重复原ID同回执、只读Query无变更；缺片/损坏不交半页；实际PG/RLS/fence/崩溃与资源资格不能用fake替代。 |
| U1 | §10.3.1/§10.5时间/长度/角度值+Default/界限/Step/Origin精确往返、溢出/微秒余数/scale、session借用/解绑、保存/冲突/未知、代次迟到、权限撤回、三语/键盘/UIA/IME/布局 | Configuration原Kind/Unit/hash保持；PE不扩API/单位域；不能精确映射只读；UI和无UI得到同hash/回执；Unbind不Close；真实25.2.3+1920×1080行为与视觉分别验收。 |
| 两消费者/回退 | §17不同定义/Scope/Host，独立build/发布/故障恢复；旧Schema/codec读/新写拒绝 | 不依赖第一Host私有类型；旧快照与回执保留；无法兼容时明确拒绝，不覆写历史。 |

按风险保留关键并发、完整性、资源、权限和恢复测试，不能删正式历史测试。合成Golden只证软件契约，不证工业参数正确/视觉准确/现场节拍。

### 13.1 net10/BCL Exe、验证命令与有限截止

C1/C2测试工程按DEV-GOV-010 §3.1冻结的BCL Exe约定：Microsoft.NET.Sdk、TargetFramework=net10.0、OutputType=Exe、Nullable/ImplicitUsings=enable；C1仅ProjectReference到binding表Core，C2到Service及Core。System.Collections.Immutable/BigInteger/Task使用net10 BCL，不新增PackageReference或待选测试框架。全部断言、两Host最小Program和端口夹具置于上述唯一Tests目录，不建临时Host/报告工程。Core/Service为net10.0类库，无WPF/产品/SDK引用。

入口按§13每行给稳定用例ID（CFG-C1-*、CFG-C2-*），执行全部断言；任一失败、未完成或必需项跳过打印ID并返回非零。每例真实单调截止10秒、套件120秒；ManualClock负责业务时间，异步闩锁由真实有限截止兜底。故意DrainUnknown场景先断言保留，再解除闩锁并Close到Released；未退出即失败，不能把Task.WhenAny超时当资源归还。C1同步死循环由外层进程截停，截停不计通过。编码期望由独立BCL字节拼接固定，不调用受测codec生成Expected；Culture测试在受控线程执行并finally恢复，不能污染后续用例。

实现获准后从仓库根目录执行以下**计划命令**；先核当前目录存在PROJECT_ENTRY.md，工程路径保持相对，迁机后不依赖固定盘符。本轮不执行。每个build外层120秒，每个run外层180秒，非零或被截停均失败。PowerShell 7包装只启动本次dotnet子进程并继承输出；超时仅终止该子进程树，不据此声称业务正常排空。

```powershell
function Invoke-ConfigurationCheck {
    param([string[]] $CheckArguments, [int] $TimeoutSeconds)
    if (-not (Test-Path -LiteralPath './PROJECT_ENTRY.md' -PathType Leaf)) {
        throw 'Run configuration verification from the repository root.'
    }
    $start = [System.Diagnostics.ProcessStartInfo]::new('dotnet')
    $start.WorkingDirectory = (Get-Location).ProviderPath
    $start.UseShellExecute = $false
    $start.CreateNoWindow = $true
    foreach ($argument in $CheckArguments) { $start.ArgumentList.Add($argument) }
    $process = [System.Diagnostics.Process]::Start($start)
    try {
        if (-not $process.WaitForExit($TimeoutSeconds * 1000)) {
            $process.Kill($true)
            if (-not $process.WaitForExit(10000)) { throw 'Verification process did not exit.' }
            throw 'Configuration verification exceeded its process deadline.'
        }
        if ($process.ExitCode -ne 0) { throw "Configuration verification failed: $($process.ExitCode)" }
    }
    finally { $process.Dispose() }
}
Invoke-ConfigurationCheck -CheckArguments @('build', 'src/Modules/configuration/Asun.Modules.Configuration.Core/Asun.Modules.Configuration.Core.csproj', '-c', 'Release') -TimeoutSeconds 120
Invoke-ConfigurationCheck -CheckArguments @('run', '--project', 'tests/Modules/configuration/Asun.Modules.Configuration.Core.Tests/Asun.Modules.Configuration.Core.Tests.csproj', '-c', 'Release') -TimeoutSeconds 180
Invoke-ConfigurationCheck -CheckArguments @('build', 'src/Modules/configuration/Asun.Modules.Configuration.Service/Asun.Modules.Configuration.Service.csproj', '-c', 'Release') -TimeoutSeconds 120
Invoke-ConfigurationCheck -CheckArguments @('run', '--project', 'tests/Modules/configuration/Asun.Modules.Configuration.Service.Tests/Asun.Modules.Configuration.Service.Tests.csproj', '-c', 'Release') -TimeoutSeconds 180
```

`dotnet test`不执行这些Exe，空执行不得记通过。A1-F与U1按已冻结§8.3/§10.3/10.5运行如下命令，仍是工程实现后才可执行；不以C1/C2成功替代进程故障/STA资格。性能目标未采纳时Benchmark只输出NotEvaluated；本节截止是防挂死边界，不是客户吞吐/时延指标。


```powershell
Invoke-ConfigurationCheck -CheckArguments @('build', 'src/Modules/configuration/Asun.Modules.Configuration.Adapters/Asun.Modules.Configuration.Adapters.csproj', '-c', 'Release') -TimeoutSeconds 120
Invoke-ConfigurationCheck -CheckArguments @('run', '--project', 'tests/Modules/configuration/Asun.Modules.Configuration.Adapters.Tests/Asun.Modules.Configuration.Adapters.Tests.csproj', '-c', 'Release', '--', '--suite', 'file') -TimeoutSeconds 300
Invoke-ConfigurationCheck -CheckArguments @('run', '--project', 'tests/Modules/configuration/Asun.Modules.Configuration.Adapters.Tests/Asun.Modules.Configuration.Adapters.Tests.csproj', '-c', 'Release', '--', '--suite', 'database', '--host', 'device') -TimeoutSeconds 300
Invoke-ConfigurationCheck -CheckArguments @('run', '--project', 'tests/Modules/configuration/Asun.Modules.Configuration.Adapters.Tests/Asun.Modules.Configuration.Adapters.Tests.csproj', '-c', 'Release', '--', '--suite', 'database', '--host', 'algorithm') -TimeoutSeconds 300
Invoke-ConfigurationCheck -CheckArguments @('build', 'src/Modules/configuration/Asun.Modules.Configuration.Wpf/Asun.Modules.Configuration.Wpf.csproj', '-c', 'Release') -TimeoutSeconds 120
Invoke-ConfigurationCheck -CheckArguments @('run', '--project', 'tests/Modules/configuration/Asun.Modules.Configuration.Wpf.Tests/Asun.Modules.Configuration.Wpf.Tests.csproj', '-c', 'Release', '--', '--suite', 'wpf') -TimeoutSeconds 240
```

## 14. BenchmarkProfile与资源预算

测量协议依[DEV-GOV-010 §3.1](../../01-governance/DEV-GOV-010_实施级规格唯一标准.md#31-独立模块核心代码开工门)，不另复制百分位算法。Profile必须有稳定Id/修订/hash、真实消费者/输入hash、构建/.NET/OS/CPU/内存、冷/热/预热和样本计划、并发/有限deadline、阈值来源及失败处理。未采纳目标为TargetPending，测量结果NotEvaluated；不把§11合成limits当客户指标。

| 范围 | 负载维度 | 测点/资源计数 |
|---|---|---|
| C1 | 字段/约束数量、单位/数值边界、文本/opaque字节、Invalid比例、并发Core | Seal/Create/Validate/Normalize/Compare单步及全链；托管分配/GC/工作集、结构与单项拒绝计数。无native/IO排空，返回即资源归还。 |
| C2 | 同键/跨键竞争、队列字节/数量、并行度、Store延迟/不合作、历史/订阅规模 | 接纳→排队→Store→知识结果→ResourcesReleased；取消至真实退出、排队字节/Task/CTS/槽位/订阅峰值和Unknown/DrainUnknown。 |
| A1 | blob/manifest/回执增长、进程数、实际卷/provider、锁/事务冲突、崩溃点 | intent/flush/replace/readback/query、文件/连接/临时/锁资源峰值，磁盘容量拒绝与恢复时间；PowerLoss单独资格。 |
| U1 | 历史/差异页大小、长文本、三语/IME/权限、订阅更新 | 首次可用/行虚拟化/Dispatcher占用/选择→投影、UI内存峰值；一次固定1920×1080有效区验证。 |

CoreLimits、ServiceLimits、预算、adapter有界读取/manifest/回执上限都由Profile显式传入。A1-F options的MaxManifestBytes/MaxSnapshotBytes/MaxTotalBytesPerKey/MaxRevisions/MaxOperationRecords/MaxJsonDepth/worker/锁预算见§8.3，U1行数/工作项/RootOwner槽位计账见§10.3；没有无界默认。未知/失败/删失及资源终态按公共口径记录，不挑成功样本算通过，不合并不同Profile。优化不得减验证/截诊断/改hash或提前宣布Released。

## 15. 可观测性与诊断

Core只返回结构化诊断，零日志后台。Service/adapter向Host已有诊断能力上报OperationKey（按Host标识保护策略）、阶段、Contract/Schema/Definition版本、Expected/Actual revision、字节/字段/队列数、分段单调耗时、SaveOutcome和ResourceState、稳定ErrorCode。正式日志端口映射是Integration门，不往Core塞静态logger或私有诊断数据库。

不得普通日志记录参数明文、SecretReference值、原JSON、凭证、绝对路径、敏感/opaque值hash或默认ContentSha256；支持人员使用Host受控原工作项/回执查询。统计计数包含Rejected/Conflict/Unknown、DrainUnknown、容量/迁移/完整性/WatchGap；平均耗时不能掩盖P95/P99/未排空样本。通知发布只记投影情况，不写新的提交终态。

## 16. 版本、独立发布与回退

Module API v0.2本轮只设计修订，ContractMajor=1/Schema=Host精确版本/codec=v2是三种独立身份，不互相推出兼容。新版本按行为/字段/错误/状态兼容矩阵发布；同Schema minor也不默认兼容。所有读取重验定义/codec/hash，不能重算新hash覆写旧证据。

Core、Service、Adapters、Wpf按实际被接收切片独立构建/测试/包版本和依赖声明；无UI消费者不引用Wpf/DevExpress，Core不引用存储/产品。发布包只包含真实实现所需程序集、唯一合同/codec版本、已批准定义/迁移身份、已执行资格与回退说明，不提前堆空交付包。外部源码引入按DEV-GOV-006 pin来源/许可/依赖；本轮研究未复制源码。

升级先停本键新写入、对账原操作和资源、保留旧只读snapshot/codec/定义/计划，再部署匹配读能力；迁移产候选，经Host审核用新ID/CAS保存。运行中任务继续绑定旧snapshot。回退代码不能删除新历史/回执；恢复旧参数是另一次显式CAS提交新revision，不能降低revision/擦掉原操作。不可读新Schema的旧二进制只读其支持版本并拒新写，恢复动作由Host明确决定。

## 17. 两个真实消费者的接入与实施步骤

| 消费者 | 接入内容 / 隔离 / 非目标 |
|---|---|
| 独立设备参数工具 | ConfigId=camera-settings、Scope=Host分配的工具/设备实例；领域Owner提供ExposureMs(Int32/ms)、Gain(Decimal/None)等真实定义/limits，C1示例不作设备阈值。读取→编辑器→Core校验/差异→原工作项→CAS保存/查询。设备应用/回读另走硬件Owner；缺相机不阻断纯参数工具的软件验证。 |
| 离线算法工具（不同Host） | ConfigId=algorithm-settings、另一Scope；领域Owner提供Score(Ratio/None)、LengthTolerance(Length/um)等实际定义，真实图像/模型仍归算法模块。相同Core/Service、不引用设备工具UI/SDK/表；保存不表示算法或质量通过。可无UI或复用编辑Inspector。 |

二者须是独立集成计划而非复制两个Program改ID。领域Owner须提供真实Definition/Scope来源/权限/输入规模/Profile、原工作项恢复和激活边界；当前尚未接入验收，不能称第二消费者通过。跨Scope取消/故障不串revision/回执/草稿；同键共享时遵循CAS。

实施顺序：主任务接收C1六门→实现Core及必要测试/Benchmark诊断→接收C2合同和夹具门并实现Service/迁移/Watch→A1先文件或已绑定storage-database路径逐项真实恢复→独立接入两个Host→接收parameter-editor桥接/U1 API再实现可选控件→产品集成/现场资格。不是用后续真实设备或UI缺口阻断无UICore，也不是先上UI再补事实Owner。

## 18. 来源、研究证据与适用限制

### 18.1 已有项目资料沿用

PKG-002/SM-002及INTERFACE-MAP的候选/保存/发布/激活分离边界沿用；不复制第二活动指导。本轮输入未变，复用已有定向结论/原件记录，不重审全部旧项目：

- [C_IniConfigManager.cs](../../references/project-snapshots/AsunControl/20261004/original/ClassLibrary/C_IniConfigManager.cs)：路径检查、Mutex、临时替换的思想可迁移；自动写默认、无CAS/Schema/原操作回执不能直接充当本合同。
- [C_XmlConfigManager.cs](../../references/project-snapshots/AsunControl/20261004/original/ClassLibrary/C_XmlConfigManager.cs)：加载/通知/防抖方向可借用；自动节点/保存及时间戳不能证明事务。
- [ShapeModelParameters.cs](../../references/project-snapshots/AsunControl/20261004/original/Vision_Aligment2D_ShapeModel/ShapeModelParameters.cs)：单位/范围/默认/跨字段需求；object/auto/Clone不能作为强类型公共契约。
- machine-config/recipe-manifest只读参考，产品字段不并入Core；HALCON算法不适用本事务模块。

### 18.2 已读上游源码和测试（2026-10-09）

| 固定来源 | 实际阅读、hash及许可/依赖 | 采纳 / 限制 |
|---|---|---|
| dotnet/runtime v10.0.0，commit `60629d14374c56f1cb51819049ad1fa529307f8d` | [FileConfigurationProvider.cs](https://github.com/dotnet/runtime/blob/60629d14374c56f1cb51819049ad1fa529307f8d/src/libraries/Microsoft.Extensions.Configuration.FileExtensions/src/FileConfigurationProvider.cs)，SHA256 `56131f86ab2702e7e60738dbefe6b058dc273c97491512b88da23c13f99266b0`；[JsonConfigurationTest.cs](https://github.com/dotnet/runtime/blob/60629d14374c56f1cb51819049ad1fa529307f8d/src/libraries/Microsoft.Extensions.Configuration.Json/tests/JsonConfigurationTest.cs)，SHA256 `017090616a926cce08f199202bff5fee57dd684b294dccc7b643e95b20d3d25d`。MIT LICENSE已读；依赖FileProviders/Primitives。 | 实读CanLoadValidJsonFromStreamProvider、LoadWithCulture、NonObjectRootIsInvalid、ThrowFormatExceptionWhenFileIsEmpty，借用类型/文化/坏输入测试思想。provider reload缺失/异常可能清Data，Watch/Thread.Sleep/ChangeToken并非CAS或保留旧snapshot保证；不引入Core、不将其当本Store。 |
| dotnet/efcore v10.0.0，commit `12b8d44bf691d2e6933a6d1003647cce4f13c3d3` | [AffectedCountModificationCommandBatch.cs](https://github.com/dotnet/efcore/blob/12b8d44bf691d2e6933a6d1003647cce4f13c3d3/src/EFCore.Relational/Update/AffectedCountModificationCommandBatch.cs)，SHA256 `60b246a58416838cdf6b81d123fcc160db147f5b77a576b502e969db47880cbc`；[OptimisticConcurrencyTestBase.cs](https://github.com/dotnet/efcore/blob/12b8d44bf691d2e6933a6d1003647cce4f13c3d3/test/EFCore.Specification.Tests/OptimisticConcurrencyTestBase.cs)，SHA256 `a083a80e8b3490e91df4223781e9ef7125fb78c34cb33d34900d60cd2cdcbc77`。MIT LICENSE.txt已读；Relational/provider依赖不带Core。 | 实读受影响行非1抛并发异常、Simple_concurrency_exception_can_be_resolved_with_store_values_using_Reload及重复更改/删除冲突；采纳条件写/读取冲突再人工决定的思想，不复制Entity/DbContext或声称原操作恢复已由EF提供。仅定向依赖阅读，不称完整依赖审计。 |

以上hash用于固定本次所读原始文件，不表示代码已移植/通过验收；源码/测试思想与本模块实施语义均已落在正文，无须到辅助脚本寻找合同。

### 18.3 官方API与实际边界

- [.NET 10 File.Replace](https://learn.microsoft.com/en-us/dotnet/api/system.io.file.replace?view=net-10.0)、[FileStream.Flush](https://learn.microsoft.com/en-us/dotnet/api/system.io.filestream.flush?view=net-10.0)：replace/backup、Flush(true)的API依据，目标卷崩溃/断电资格仍需真实验证。
- [EF Core事务](https://learn.microsoft.com/en-us/ef/core/saving/transactions)、[SQLite atomic commit](https://www.sqlite.org/atomiccommit.html)、[SQLite WAL](https://www.sqlite.org/wal.html)：事务原子性、journal/flush/锁、WAL同host且不适用于网络文件系统；只为存储边界依据，不安装或指定SQLite。
- [.NET Double.ToString](https://learn.microsoft.com/en-us/dotnet/api/system.double.tostring?view=net-10.0)：R/Invariant有限double往返，±0本模块明确规范；decimal改用固定小数避免G29指数与输入语法冲突。
- DevExpress WPF 25.2：[TableView](https://docs.devexpress.com/WPF/DevExpress.Xpf.Grid.TableView?v=25.2)、[DockLayoutManager](https://docs.devexpress.com/WPF/DevExpress.Xpf.Docking.DockLayoutManager?v=25.2)、[SuperTip](https://docs.devexpress.com/WPF/DevExpress.Xpf.Core.SuperTip?v=25.2)，实际读控件/程序集与相应用法。网页patch25.2.10不替换本项目25.2.3；无本机编译/行为证据，U1另验。
- PostgreSQL 18官方：[data-modifying WITH](https://www.postgresql.org/docs/18/queries-with.html)、[binary string](https://www.postgresql.org/docs/18/functions-binarystring.html)、[date/time](https://www.postgresql.org/docs/18/functions-datetime.html)。2026-10-11定向读取，§8.4.1.1据此采用独立串行DML核实际影响行、内建sha256(bytea)/从1计substring偏移（Offset+1）、transaction_timestamp()事务UTC。仅为命令顺序/编码设计依据，不证明目标PG运行资格，不改变SD冻结版本或依赖。
- [DEV-UI-040](../../shared-modules/guidance/05-ui/DEV-UI-040_WPF+DevExpress%20Design%20System开发指导.md)和[parameter-editor指导](../parameter-editor/DEVELOPMENT-GUIDE.md)负责公共样式/编辑器；配置UI只消费，类型/单位桥接缺口按§10.3关闭。


## 19. 分片内部规格与真正外部门

前轮版本0.3.2-prep定向补A1-DB公开注册事务/读取/原Mutation查询、Owner编码/完整分页/空宿主，修正U1现值/Default/范围/格点与物理kind的无损桥及STA Host；主控于2026-10-11限定接收本轮指导内容。C1/C2六项接收及A1-F/U1无矛盾范围接收保持，不重审已接收Core、不编写产品工程/脚本/报告。既有四域Golden不变，新增DB Owner/技术Hasher向量与反例是指导规格，不声明构建/测试/性能/crash/STA/现场通过。

| 切片 | 内部规格接收与准备状态（2026-10-11） | 后续运行、集成或现场资格门 |
|---|---|---|
| C1 | §4.3/§5.1/5.1.1纯API/codec/Golden/边界，§11.1/§13.1独立BCL Exe；主控六门已接收，`ModuleCoreImplementationReady`，仅纯内存规格准备 | 实现后编译/全部断言/两消费者/实际Profile测量；客户物理阈值不作为纯Core阻断。 |
| C2 | §6.2端口/状态、§11.3根Owner完整两Host及移交/迟到/清理；主控六门已接收，`ModuleCoreImplementationReady`，仅服务/端口模拟规格准备 | 端口夹具实际运行、Factory/同步抛错/cleanup/排空/Unknown/CAS/迁移/Watch测试及Profile。 |
| A1-F本地文件 | §8.3 wire/JSON字段顺序/双hash/factory/options/根路径/worker锁/fence/原子回执/两个Host及唯一Tests命令内容已接收；`PreparationIncomplete / NotReady` | 实际本地卷双进程/crash/损坏/容量/权限、性能及资源验收；PowerLoss/控制器缓存/FAT/SAT单独资格，未执行。 |
| A1-DB | §8.4.1公开Factory/Options/注册payload/codec/SD端口及关系，§8.4.2/8.4.6 Owner规范/上游Hasher Golden，§8.4.3原Mutation与完整快照分页，§8.4.4根/预算/资源，§8.4.5双Host/反例已具体化；本轮指导内容已限定接收，仍 `PreparationIncomplete / NotReady` | 上游SD.A1真实PG provider/角色/RLS/目录工件/事务隔离/关键CAS/fence及资源、崩溃与原提交对账；未决Pending没有可证明终态时只查询，不绕过保守恢复门。不阻断A1-F。 |
| U1 | §10.3 Session/Binding/WorkItems/RootOwner/Control及无矛盾范围接收保持；§10.3.1物理kind/值/默认/界限/格点/精确性和§10.5修正STA Host本轮指导内容已限定接收，仍 `PreparationIncomplete / NotReady` | 实际25.2.3/WPF构建、STA/UIA/三语/IME/键盘/1920×1080视觉/性能/关闭资源；产品权限/工作项具体持久Owner接线按Integration验收。 |
| 跨模块可选扩展 | PE编辑Double/Uri/SecretReference/超域单位尚无公开无损类型，仅未来可编辑扩展，由主控协调；当前只读保留闭合 | 不修改对方指导，不把此扩展当当前所有UI阻断。 |
| 产品集成 | 平台正式Schema/真实DefinitionOwner/Scope/权限/原工作项持久Owner/激活合同映射须按消费者接收，不能用harness代替 | 真实阈值、设备/图像回读、真实两消费者、正式Profile/Golden/HIL及现场资格未执行。 |

六项逐片：①职责/非目标/真实复用计划见§1/3/17，本轮DB消费者见§8.4.1/8.4.5；②公开类型/方法/单位/状态/Owner/版本见§4～10，DB见§8.4.1～8.4.3、修正PE桥见§10.3.1；③C1/C2/A1-F无UI装配及U1无隐藏窗口业务见§8.3.3/§11，DB双Host见§8.4.5、修正STA Host见§10.5；④正常/错误/并发/有限观察/排空/原ID恢复/回退见§11～13，DB反例/Golden见§8.4.5/8.4.6、物理桥反例见§10.3.1/10.5；⑤资源/有限截止及统计口径见§14，本轮DB测点/预算见§8.4.4，TargetPending不造达标值；⑥唯一工程/Tests/允许禁止路径及具体命令见binding/§13.1。C1/C2、A1-F及U1无矛盾范围接收保持，A1-DB与U1物理桥修订指导内容已由主控限定接收；接收记录与实现运行证据分开。

0.3.2修订完成两个有限自审视角：实现者走Prepare→Decide→完整快照/回执与失败/取消/未知恢复；外部消费者核空Host的Factory/codec/Context/权限/预算/Session/原Task及异常cleanup闭包、PE完整定义到原kind逆转换。定向检查本地链接/fragment、标题/围栏、公开类型唯一性、消费签名和Golden；既有四域固定bytes/hash保持，新增DB六个完整向量核长度/hash并独立解码两阶段SD信封字段，物理桥整数/scale/溢出反例核算一致。这里只是规格与文档检查，未编译或执行产品工程。主控已回读0.3.2-prep §8.4.1～6及§10.3.1/10.5，核对SD公开Hasher/端口和PE单位域，独立构造操作token/Mutation/Read/两阶段技术信封五域完整hex/hash，并核Conflict完整结构，六向量一致；本轮A1-DB及U1物理单位桥指导内容限定接收。真实PG/fence/崩溃/WPF/产品资格仍未关闭；真实注册工件/hash/Scope/角色/后端Profile及事务/fence/崩溃/资源资格由实际宿主接入绑定，不能以合成目录代替。已durable Pending而旧writer结论不能证明时保留Unknown，不提供未经SD批准的Transaction.Resume或NotCommitted最终化旁路；真实对账能力需按SD.A1范围接收，查询本身不写恢复事实。

完整模块保持 `PreparationIncomplete`；仅C1/C2为 `ModuleCoreImplementationReady`，仅表示各自规格准备完成。A1-F及U1无矛盾范围接收保持，仍 `PreparationIncomplete / NotReady`；本轮A1-DB映射和U1物理桥修订指导内容已限定接收；A1-F/A1-DB/U1真实PG/fence/崩溃/WPF及产品资格仍 `PreparationIncomplete / NotReady`，不提升运行资格。不声明完整模块 `ImplementationSpecificationReady` 或 `Production`。全仓校验由主控；本轮只做唯一指导定向检查，不变入口/进度/登记/其它模块/参考源/AsunImage。

### 19.1 当前全部批准范围的文档准备结论（0.3.3-prep）

本次范围是§1完整公开能力及C1/C2/A1-F/A1-DB/U1，不以首片代替整模块。沿用已接收的Core/Service、文件wire/恢复、DB六向量及PE桥研究/自审；只补当前上游公开契约揭示的领域Read必须用Query、第三Context、真实PG marshal/固定命令消费、事务UTC与容量预约。规格自审由configuration永久原会话完成，不等待主控另做内容复核；总控只接收状态。当前批准的软件范围内，没有仍需实现者自行选择的算法、架构、公共接口、装配或恢复方案欠账；外部事实、实现工件与运行资格分别如下，不据此提升完整模块准入状态。

| 批准能力/切片 | 唯一实施正文与本次结论 |
|---|---|
| Definition/候选/校验/规范化/差异（C1） | §4～5、§11.1/§12/§13；类型/单位/默认/跨字段规则/容量/确定性编码均明确。默认仅来自明示Definition，不猜业务默认/物理阈值；已接收四域向量沿用，不重复审算。 |
| Load/Save/原操作查询/历史/Watch/迁移/Close（C2） | §6～9、§11.2～11.3/§12～14；无UI端口、CAS、唯一原ID、两轴状态、工作项/根Owner、有限等待和真实清理均闭合。迁移规则由批准provider输入，缺具体领域计划不补猜公式，不阻断其它能力。 |
| 本地真实存储（A1-F） | §8.3～8.3.3；规范wire、锁/fence、原子事务、损坏/容量/崩溃路径及两个Host沿已接收规格；不重审未改范围。 |
| 数据库真实绑定（A1-DB） | §8.4.1～8.4.6；领域Query与技术Recovery分离；§8.4.1.1冻结当前公开marshal、20项参数、前置/最终行、分支影响行、预约/决定计数、纯codec与同事务PG命令。原技术Hasher/六向量不改，真实Binding/Catalog工件由实现按新规格生成。 |
| 编辑/历史/差异/迁移投影及保存恢复（U1） | §10.1～10.5；借用Host EditorSession、PE值/Default/范围/格点无损桥、WorkItems/Access/RootOwner与STA Host明确。Preview/Recommend/Apply端口为null，当前不自动推荐/应用；Double/Uri/SecretReference及不能无损表示的域保留只读，未来可编辑扩展不算当前欠账。 |
| 独立发布/两消费者/回退 | binding、§11～17；唯一工程/测试落点、有限Profile、设备工具与离线算法工具接入、版本拒绝及原件保留明确。没有产品Shell、私有表或隐藏窗口初始化依赖。 |

HALCON算子、图像坐标/标定、视觉候选路线比较、训练与检测节拍不适用于此参数事务模块（§9.3）；保存/Valid仍不给生产放行或设备控制权。

| 剩余条件 | 决定或验收Owner / 影响边界 |
|---|---|
| 真实字段Definition/业务默认/单位/阈值、迁移转换及损失计划、客户Scope | 参数领域/客户Owner批准输入；只影响相应消费者Integration及领域正确性，不阻断纯Core或其它已有Definition。 |
| 用户权限、可恢复工作项存储、根生命周期、语言/主题/日志、真实消费者Profile | 消费宿主Owner按公开端口装配；不能把本模块接口/默认流程选择推给客户。真实目标值未采纳时保持TargetPending/NotEvaluated。 |
| 可信StatementCatalog/Schema迁移工件/hash、实际Scope/角色/RLS、凭据/TLS/后端Profile | configuration实现Owner生成自己的固定注册包；部署宿主与SD Owner负责公开迁移流程、技术provider/fence/原提交对账。工件未生成属于实现阶段，不是文档设计欠账；无凭据/迁移权只阻断相应真实Adapter。 |
| 实际编译、契约/资源/并发/故障测试、真实卷/PG/崩溃、WPF/UIA/三语/1920×1080、性能及客户现场 | 各获准切片实现/验收Owner执行并提交真实结果；本轮未运行这些验收，fake/向量/文档检查不代替。旧writer未被证明退出/fence时Pending仍Unknown，不新增恢复旁路。 |

C1/C2保留`ModuleCoreImplementationReady`；A1-F/A1-DB/U1与完整模块保留既有`PreparationIncomplete / NotReady`及产品集成门，不声明完整`ImplementationSpecificationReady`、实现完成或生产通过。0.3.3的文档结论是批准软件设计范围已闭合；资格结论是尚未执行相应实现和运行验收，二者分别记录。本轮定向检查只验证本指导结构、引用、消费签名及新增命令闭包，已接收Golden复用，不重算为新的运行证据。


### 图标可访问性验收

遵循 [DEV-UI-047 §2.3](../../shared-modules/guidance/05-ui/DEV-UI-047_视觉设计系统规格.md#23-图标可访问性补齐全库空缺)：

| 项 | 验收要求 |
|---|---|
| 可访问名称 | 每个图标按钮/树节点/状态标记有非空可访问名称(`Name`/`HelpText`/SuperTip)，不能只有图形 |
| 装饰图标 | 纯装饰图标标记为装饰并从可访问树剔除 |
| 悬停提示 | 图标操作使用 DevExpress SuperTip(标题/作用/限制/快捷键/恢复步骤)，随语言切换 |
| 危险动作 | 图标 + 文字 + 颜色三重表达，不依赖单一图形 |
| 状态标记 | 状态色块同时有文字标签或图形形状差异 |
| 对比度 | 图标本身满足 §1.3 图形 3:1 门槛 |
| 高对比模式 | 不因系统高对比模式失效 |

**判据**：屏幕阅读器朗读时，每个可操作图标都有可理解的名称；任何"只有图标、看不出是什么"的位置是缺陷。

## 附录 A：Module API Contract v0.2定位

无重复DTO：Core§4.3、codec§5.1及四域Golden§5.1.1；Service/Store/迁移§6.2、状态§7～9；A1-F独立wire/factory/options/文件恢复§8.3，A1-DB公开组合/Owner规范/原Mutation/完整快照分页/双Host/Golden§8.4；U1 Session/工作项/根/控件§10.3、PE物理无损桥§10.3.1、STA Host§10.5；工程/禁止路径binding，Host根生命周期§11.3，测试命令§13.1、Profile§14、真实复用§17。文档版0.3.2-prep的DB绑定及PE桥指导内容已限定接收，0.3.3-prep的Query用途/真实marshal及全范围自审结论见§8.4.1.1/§19.1；API仍未实现，不另造第二合同或宣称运行兼容已验证。
