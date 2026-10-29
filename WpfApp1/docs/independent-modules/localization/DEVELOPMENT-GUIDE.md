# Localization 独立模块开发指导

> 状态标记：review=`DesignReview/Prep`｜module-ready=`PreparationIncomplete`｜core-ready=`L-Catalog, L-Runtime, L-Tests/Host`

- 模块：IM-003 / localization（语言资源与专业术语）。
- 版本：0.2.3-prep；日期：2026-10-11；状态：DesignReview/Prep（产品整体）。本次仅统一原会话审核结论与产品集成剩余门，不改既有合同/API。
- 切片准入：L-Catalog、L-Runtime、L-Tests/Host 为 ModuleCoreImplementationReady；2026-10-09 主控内容复核 §1–15 后明确接收六项文档规格。本状态只表示规格准备，不表示产品代码、构建/运行、WPF、性能或现场通过；本轮仍不实施产品代码。
- L-Wpf 有限适配设计：2026-10-09 主控复核 §7.2.1–3/§13 后已接收（规格准备）；2026-10-11 本原会话补齐并完成 PlainTextSurface、Dispatcher/实例归属、恢复及有限验证规格的内容审核。总控仅登记完成结论，不另设主控技术审核/接收门。它是可选 WPF 适配，不属于无 UI Core。NativeApply=false 封闭限制保持；真实 DevExpress 25.2.3 消费、三语/IME/UIA/呈现/有限关闭验证未执行。L-Integration未完整是具体宿主资源、产品接线、发行/存档政策和真实验证门未落实，不是本模块内部软件设计欠缺，逐项Owner/输入见§13.1。
- 永久会话：01a10306-e279-7943-8a6f-4ddff247a5b5；登记见 [模块索引](../MODULE-INDEX.md)。
- 当前架构见 [INDEPENDENT-MODULE-ARCHITECTURE](../INDEPENDENT-MODULE-ARCHITECTURE.md)。PKG-003/SM-003 只保留历史来源映射。
- 平台基线：C# / .NET 10 / WPF / DevExpress 25.2.3；Core 为纯 net10.0，不引用 WPF、DevExpress、AsunImage 或 HALCON。
- 本轮修正原 v0.1 契约缺口，冻结以下 Core v0.2 设计；没有证据表明 v0.1 已形成发布程序集，不承诺两者二进制兼容。所有示例是未来工程的合同示例，未编译或运行。

## Core implementation binding

| 切片 | 唯一工程 / namespace / 消费者 | 允许的实现路径与后续门 |
|---|---|---|
| L-Catalog | src/Modules/localization/Asun.Modules.Localization.Core/Asun.Modules.Localization.Core.csproj；Asun.Modules.Localization | 独立目录解析、合同验证、加载端口和不可变精确索引；不引用平台资源表或数据库 |
| L-Runtime | 同一 Core 工程，不另起核心；同一 namespace | scope、Resolve、强类型格式、快照租约、切换、订阅投影及真实排空；依 L-Catalog |
| L-Tests/Host | tests/Modules/localization/Asun.Modules.Localization.Core.Tests/Asun.Modules.Localization.Core.Tests.csproj；Asun.Modules.Localization.Tests；最小入口 LocalizationHostTests.cs | Microsoft.NET.Sdk / net10.0 / OutputType=Exe，仅 ProjectReference 至 Core 与 .NET BCL；两个无 UI 消费者、内存 loader、可控 scheduler、故障夹具和性能夹具；不得启动产品 Shell |
| L-Wpf | 后续计划 src/Modules/localization/Asun.Modules.Localization.Wpf/Asun.Modules.Localization.Wpf.csproj；Asun.Modules.Localization.Wpf | 实例资源绑定和 DevExpress 适配；唯一验证工程 tests/Modules/localization/Asun.Modules.Localization.Wpf.Tests/Asun.Modules.Localization.Wpf.Tests.csproj，namespace Asun.Modules.Localization.Wpf.Tests、入口 WpfHostTests.cs；§11.1冻结有限执行，必须另验真实 WPF/三语/IME/UIA/1920×1080 |
| L-Integration | 宿主组合根通过本页 API 引用 Core/Wpf | 平台 Schema 映射、语言选择入口、语言偏好持久化、外部签名信任、报告存档由宿主拥有；本轮不授权这些路径写入 |

当前任务只允许修改本文件。未来产品实现须由主会话逐切片授权上述路径；禁止其它模块、共享 Contract、产品页面/ViewModel/私表、客户项目、参考原件、AsunImage 内部及直接 halcondotnet.dll/HOperatorSet 引用。Core 工程无需 DevExpress/视觉库/产品 UI 才可引用、构建、测试、发布和回退。首版验证沿 DEV-GOV-010 §3.1 已定 BCL Exe 约定，不引 xUnit/NUnit/MSTest 或待选测试包、不升级共享构建；§8 的 Assert 是本测试工程私有确定性断言辅助类，不是第三方 API。

## 1. 职责、消费者和禁止边界

### 1.1 完整能力

模块拥有：独立资源包装载与校验；精确语言索引；专业术语和参数签名校验；有界 Resolve 和显式格式；宿主 scope 的语言/目录切换；不可变报告快照；中立供应商模板取得；可选区域通知和逐区域呈现回执；取消、超时、关闭、迟到和资源预算；诊断、版本引用和回退兼容验证。所有能力可以通过无 UI 接口调用；投影区域也可由无 UI 测试实现。

真实规划消费者：A 为通用视觉/测量工具宿主（实例控件和编辑草稿）；B 为离线报告生成器（并行报表、跨页固定语言）；C 为独立诊断工具（只读错误/状态显示）。A/B/C 可以同进程、不同 scope；B 不初始化窗口、Dispatcher 或 DevExpress。至少 A/B 使用同一发布包，Core 先用 B/C 无 UI 宿主验证，不能以两个空 scope 充作完整消费者。

### 1.2 禁止与 Owner

调用方拥有流程、目标关联、配方、工艺解释、质量放行、权限、设备副作用、业务输入解析、报告保存和偏好持久化。Core 只拥有资源/语言/投影事实，不修改任何量值、单位、坐标、业务枚举、错误码、ID、OCR/读码原串、操作者自由文本或持久化字节。不调用设备、数据库、翻译云服务，不授予权限、不停止生产。

不设全局可变语言，不修改 CurrentCulture/CurrentUICulture、DefaultThreadCurrentCulture 或 Application.Current.Resources，不从焦点/窗口标题判断 scope。不在模块控件中放语言选择入口或资源维护页面；宿主只有一个自己的选择入口。缺资源不能直接显示内部 key/异常栈，也不能改生产 PASS/FAIL。

非目标：ICU MessageFormat、自动复数/性别语法、任意富文本/XAML/脚本、自动翻译直发、译文驱动换算或精度修改、跨进程全局语言同步、扫描第三方视觉控件内部节点、无公开入口的原生弹窗全量热刷新。新增此类需求须先变更本模块合同；不通过“模板原串”绕过约束。

### 1A. 新架构适配要点

**架构门禁**：`Asun.Modules.Localization.Core`（资源键/值管理层）不得引用 `System.Windows.*`；只有 WPF 绑定切片可引用，Core 不得反向引用。§1 已明确"不设全局可变语言，不修改 CurrentCulture/CurrentUICulture"。

**Blazor/Web**：Web 端（Blazor Server）通过本模块的同一套三语资源（zh-CN/zh-TW/en-US）渲染 UI 文字；语言切换经服务端 API 推送；宿主唯一语言选择入口规则（§1）同样适用于 Web 宿主——Web 端不得另设独立语言切换按钮。

**AI/HALCON 不适用**：本模块是纯语言资源管理，不执行视觉算法；HALCON 备选 CI 不涉及本模块。

## 2. 主路线和依赖方向

冻结主路线为独立 UTF-8 JSON 字符串目录 → .NET 10 System.Text.Json 严格解析 → 已校验不可变的（ModuleId、Key、ExactLocale）索引 → 显式 fallback → 受限 CompositeFormat 与受控参数。理由是精确来源可证、没有 satellite ResourceManager 的隐式父文化缓存，且独立报告无需程序集加载。只用 .NET 随附能力，不引入第三方运行时。

已有 .resx 可经宿主构建/导入适配器转换为同一目录；禁止从 GetString 非 null 结果推断精确来源。ResourceManager.GetResourceSet 在先前 fallback 后可能命中缓存的父 ResourceSet，即使 tryParents=false。转换时须证明每语言来源和字串类型，不装载用户自定义资源对象、不运行任意程序集。来源无法证实则拒绝该导入，不切换到猜测路线。

核心依赖仅为 IResourceCatalogLoader（读取）、TimeProvider（单调期限，测试可注入）、ILocalizationSurfaceScheduler（可选调度）和 ILocalizationDiagnostics（非阻塞诊断）。所有端口注入 LocalizationService 构造器；不经服务定位器、Shell 或其它模块的业务流程。报告输出只持本模块快照和自己的原事实引用。

## 3. 独立资源包 Contract

### 3.1 核心格式 localization-catalog/1

顶层必需字段为 schemaId（固定 asun.localization.catalog/1）、catalogVersion（严格 SemVer）、supportedLocales（含 zh-CN/zh-TW/en-US 的有序无重复数组）、fallbacks（每语言后继候选数组，可空）、messages（非空数组）。未知字段、重复属性、重复条目或规范化后重复语言均拒绝；不取最后一个覆盖前者。

消息字段：

| 字段 | 类型、语义和范围 |
|---|---|
| moduleId / key | 非空 ASCII 标识；moduleId 匹配 `^[a-z][a-z0-9-]*$`；key 匹配 `^[a-z][A-Za-z0-9]*(\.[a-z][A-Za-z0-9]*)*$`；精确 Ordinal，不 Trim 或模糊匹配。各自长度由 MaxKeyChars 限定 |
| semanticRevision | 正整数；同 key 改义、类型、用途、单位标签含义或恢复动作必须产生新语义修订，不能仅改译文 |
| purpose | PlainText 或 NativeTemplate；同 key 不能暗中互换用途 |
| critical / allowEmpty | bool；critical=true 时 allowEmpty 必须 false。关键命令/警告/恢复文案禁止空白；可选说明只有 allowEmpty=true 才可为空 |
| parameters | 按位置排序的 ParameterSpec[]，可空数组；位置连续从 0 起；Name 唯一、Kind/Nullable/MaxDisplayChars/MinOccurrences/MaxOccurrences 固定 |
| texts | JSON object，属性名为 supportedLocales 中的精确语言；值为 `{ "text": string, "review": ReviewInfo }`。null 拒绝，缺项不等空字符串；至少一种文本；不得使用另一份平行审核映射 |
| ReviewInfo | JSON 字段 status=Draft/Reviewed/Approved、reviewer（非空 string）、reviewedAtUtc（ISO 8601、offset 为 Z）；运行加载只接受 Approved 文本；合法 JSON 不表示专业审校已通过 |
| terminology | termId、definition、usage、prohibitedMeanings、translationRevision；无术语绑定时显式 null。定义不含制程判据 |
| nativeContract | PlainText=null；NativeTemplate 必填 §3.5 的合同，不含任何 DevExpress 类型 |

JSON 字段大小写严格按本表及下面示例；所有字段必填，只有明确标为 null 的字段允许 null。枚举用区分大小写的名称 string，不接受整数；修订为 Int64 正整数，其余位置/次数/长度为 Int32 整数，不接受小数或字符串数字。parameters 的对象字段固定为 position、name、kind、nullable、maxDisplayChars、minOccurrences、maxOccurrences；name 按 key 单段语法且唯一，position 连续从 0 起，`0<=minOccurrences<=maxOccurrences`，maxDisplayChars 正且不超过 MaxArgumentChars，maxOccurrences 不超过 MaxTemplateChars。NativeTemplate 的 parameters 必须空，供应商槽位只在 nativeContract 定义，避免两套签名。

terminology 非 null 时固定 termId:string（key 语法）、definition:string、usage:string、prohibitedMeanings:string[]（可空、无重复）、translationRevision:long；全部文本长度受 MaxTemplateChars 限制，必需字符串非空白。fallbacks 必须为每个 supportedLocale 恰好给一个数组，数组元素也必须属于该集合。按声明顺序深度优先、首次访问去重，先自身再后继；禁止环，展开后总候选数不得超过 MaxFallbackDepth。因此分叉链的遍历顺序也唯一。

以下是单条消息的完整合成包，不代表客户词条已批准；审核者和时间只作测试输入。ExpectedHash 对这份实际 UTF-8 字节在请求外计算，包禁止 BOM；词条重复身份为 (moduleId,key)，不是文本内容。

~~~json
{
  "schemaId": "asun.localization.catalog/1",
  "catalogVersion": "1.0.0",
  "supportedLocales": ["zh-CN", "zh-TW", "en-US"],
  "fallbacks": {"zh-CN": [], "zh-TW": [], "en-US": []},
  "messages": [{
    "moduleId": "common", "key": "items.count", "semanticRevision": 1,
    "purpose": "PlainText", "critical": false, "allowEmpty": false,
    "parameters": [{"position": 0, "name": "count", "kind": "Count", "nullable": false,
      "maxDisplayChars": 32, "minOccurrences": 1, "maxOccurrences": 1}],
    "texts": {
      "zh-CN": {"text": "项数：{0}", "review": {"status": "Approved", "reviewer": "fixture-reviewer", "reviewedAtUtc": "2026-10-09T00:00:00Z"}},
      "zh-TW": {"text": "項數：{0}", "review": {"status": "Approved", "reviewer": "fixture-reviewer", "reviewedAtUtc": "2026-10-09T00:00:00Z"}},
      "en-US": {"text": "Items: {0}", "review": {"status": "Approved", "reviewer": "fixture-reviewer", "reviewedAtUtc": "2026-10-09T00:00:00Z"}}
    },
    "terminology": null, "nativeContract": null
  }]
}
~~~

CatalogRevision = (schemaId, catalogVersion, lowercase SHA-256 of exact payload bytes)。ExpectedHash 在 CatalogLoadRequest 中，不能嵌入待 hash 的包作为自引用字段；SourceRef 是诊断来源，不授权 Core 任意文件/URL访问。相同版本与不同 hash 同时登记视为 LOC-011；相同 hash/版本再次加载可复用已校验修订。回退旧资源仍须经过加载/兼容检查，不能覆盖同版本原字节。

BCP-47 标识在加载阶段以 CultureInfo(name, useUserOverride:false).Name 校验并要求目录使用标准形式；不从 CultureInfo 能构造就宣布语言支持。Core 不隐式追加 Parent/Invariant/脚本候选，不把 zh-TW 转为简体。fallback 仅使用包内显式有序后继，精确语言优先并去重；首版默认后继为空。允许的兼容政策举例为 CN→en-US、TW→en-US、en-US→[]，这是显式包配置，非自动默认。请求完全不支持的语言返回 LOC-001，绝不偷偷变为默认语言。

加载时检查 fallback 的缺引用、重复、循环和最大链长；同 key 在不同语言共享同一签名。ScopeCreateRequest.RequiredKeys 提供该宿主完整必需集合；critical key 默认要求请求语言精确存在，只有显式 AllowCriticalFallback=true 才允许按该目录链命中。非关键必需 key 可批准回退。坏语法、错误类型、用途或 hash 失败不能伪装成“缺词”继续 fallback。运行期损坏返回失败，保留之前已呈现文字，不默默拼句。

历史 AOI localization.v1 Schema 是只读输入合同，其 minLength、命名与审批状态保留在导入器；它不直接充当本模块新目录 Schema。不复制产品缺陷/放行词条进入 Core。旧包不能因字段名相似直接解析；导入器生成新目录并记录旧来源 hash/新 payload hash。

### 3.2 预算、单位和有效域

RuntimeOptions 包含必填 RuntimeBudget，四类期限上限也在该 Budget；没有隐式“无限”或客户节拍默认值。包/输出内容硬界限来自宿主已冻结 Profile；Core 对上限机制冻结，不编造性能达标值。

| 字段 | 类型/单位/有效域；来源和默认 |
|---|---|
| MaxCatalogBytes / MaxResidentPayloadBytes | long/byte，正值且 <= int.MaxValue；总原字节缓存预算不得小于单包预算；必须显式提供 |
| MaxMessages / MaxLocales / MaxCachedCatalogs | int/count，正值；MaxLocales>=3；实际缓存包括被租约固定的旧修订，满时只淘汰无人使用项 |
| MaxTemplateChars / MaxKeyChars / MaxArgumentChars / MaxOutputChars | int/UTF-16 code units，正值且受 int 分配范围约束；没有可截断关键文字的含义 |
| MaxArguments / MaxFallbackDepth | int/count；MaxArguments>=0；MaxFallbackDepth>=1；两者都必填，链含 requested 自身 |
| MaxScopes / MaxSurfacesPerScope / MaxSnapshotLeases / MaxInflightLoads / MaxOperationRecords | int/count；前四正值（MaxSurfacesPerScope 可为 0），MaxOperationRecords 正值；未释放记录占容量，满则不接纳；全部必填 |
| MaxPresentationRecords | int/count，正值且至少为 checked(2*MaxScopes)；包含未释放批和保留的完成批，全部必填；不为历史 batch ID 留无界墓碑 |
| MaxConcurrentReads | int/count，正值、必填；全 service 的 Validate/Resolve/GetRawTemplate（含批 Context）共用同步计算 slot，满时 LOC-013，不忙等或占锁等待 |
| MaxJsonDepth | int/count，正值；JSON 文本嵌套预算；不借默认 64 隐式放宽 |
| LoadDeadline / SwitchDeadline / PresentationDeadline / DrainObservationTimeout | TimeSpan/单调 elapsed，必须正、有限且可由 TimeProvider 换算；显式提供。关闭期限只限制观察，不中止真实排空 |
| ResolveRequest.MaxOutputChars | 正值且 <= RuntimeBudget.MaxOutputChars；必填，不替代 key/参数自身约束 |
| OwnerTag / Reason | 非空诊断字符串，长度受 MaxKeyChars 限制；调用方提供，不用作 scope ID/幂等键 |

默认语言是宿主显式选定的三语之一；默认 fallback 后继为空、AllowCriticalFallback=false；无参数列表为空数组，不以 null 代替空。所有长度是 UTF-16 code units，输入原字节是 byte，日期是 DateTimeOffset，计数 Int64，期限以单调时钟计算，日志时间以 UTC 记录。资源阈值与性能目标分别登记；例如 §8 的数值只是有明确消费者的合成测试夹具，不是工业推荐上限。

读取时先预留一个 MaxCatalogBytes 有界缓冲和并发 slot，再由 loader 写入。只准完整读取/验证后登记；overflow、超长或读未完均拒绝。登记原字节另复制为 ByteCount 长度的 Core-owned 数组，释放读取 buffer，ResidentPayloadBytes 按该数组实际长度计费；预留读取 buffer 按实际容量单独计费，两者短暂重叠计入实测内存。托管元数据也受 messages/locales/长度等维度约束；byte 预算只代表明确计费的原字节缓存，不宣称等于全部 CLR 堆内存。基准另测实际分配/GC/峰值内存。旧租约不能因 LRU 满而被淘汰；无空闲项时返回 LOC-013，由宿主释放/降低并发再重试。SourceRef/SourceVersion、Purpose、SurfaceId/ActualRegions 的各字符串受 MaxKeyChars，区域数不超 surface.RequiredKeys.Length；集合/计数边界均用 checked 算术验证。

### 3.3 强类型参数与四种表示

resource locale、display FormatProfile、活动编辑 ParseProfile 和持久化表示是四个独立值。Core 不解析用户输入，ParseProfile 属宿主编辑器/参数 Owner；不为它另造核心写入权威。

ParameterSpec.Kind 固定为 Text、Identifier、Count、Decimal、FiniteDouble、Timestamp、Duration。ArgumentValue 为封闭 tagged union，只有相应 string/long/decimal/double/DateTimeOffset/TimeSpan 工厂；不能派生执行自定义代码、不能传 object[] 或任意 IFormattable。非有限 double 拒绝；Count>=0；nullable 必须传显式 Null，并使用调用方指定的 NullDisplayText，不自动显示 0。Identifier 原值是 string，0012 不走数值解析。

FormatProfile 是不可变值合同：Id:string（key 语法）、Revision:long 正值、CultureName:string（非空标准 CultureInfo.Name）、Rules:immutable ParameterFormatRule[]、NullDisplayText:string。ParameterFormatRule 为 ResourceKey、Position:int、Format:string；按 (ModuleId,Key,Position) 精确匹配，每个 PlainText 参数恰好一条规则，无重复/未知参数。Text/Identifier 的 Format 为空字符串且原样；Count 仅 G；Decimal 仅 G 或 F0..F12；FiniteDouble 仅 G17 或 F0..F12；Timestamp 仅 O；Duration 仅 c。这里的逐参数规则覆盖整个已装载目录，不仅 RequiredKeys；Create/Switch 预检完整集合。NullDisplayText 可空、长度受 MaxArgumentChars，实际 null 显示也须通过该参数 MaxDisplayChars。NativeTemplate 不使用这些规则。

Core 构造并冻结内建 CultureInfo，useUserOverride=false，不接收任意 IFormatProvider/ICustomFormatter。同 (Id,Revision) 在当前活动/租约/操作引用中内容不同为 LOC-011；全向量等价比较全部规则/文化/null 文本，不只比较 Id。FormatProfile 的精度选择归领域 Owner，UI 语言切换不自动改它；日期 O 保留原 offset，不自动换时区/日历。其它格式需求先扩合同，不让译文插入 token。

单位只作为调用方确定的单位 ID 和单独标签资源引用；数值换算在调用方完成再传 Decimal/FiniteDouble，Core 没有 UnitValue 的乘法或范围判定。EnumLabel 由调用方把稳定枚举映射到普通 key；Core 不尝试识别业务状态。显示舍入值不能写回原量值/哈希/排序键；原 OCR、字节、板号和自由文本均不翻译或 Normalize。

### 3.4 PlainText 的有界处理

先验证 module/key/purpose/签名和参数数目，再检文本/参数长度；单次扫描只允许字面、{{、}}、{非负索引}，索引不允许符号、空格、前导零或越界；每个参数出现次数必须在 ParameterSpec 区间，必需参数不能漏。百分号可以是普通字面，不允许译文通过 :P 或 :F 改量值格式；对齐宽度、嵌套项与 token 全拒绝。

用 CompositeFormat.Parse 验证框架语法，复用它及 string.Format 的公开实现；不反射内部 segments。MinimumArgumentCount 仅为最大索引+1，不能作为占位集合/次数验收。先将受控值按 FormatProfile 转成 string，计算 literal code units + sum(occurrences*argument length)，checked 算术，超输出预算则在最终分配前 LOC-006。最后以 InvariantCulture 合成只含 string 的句子，原参数中的 {0} 或下划线只是数据，不再解析，也不作为助记符。

每个格式化参数（含 NullDisplayText）先检 MaxArgumentChars 和该 ParameterSpec.MaxDisplayChars，超任一为 LOC-006；所有声明文本都在加载时完成语法/签名验证，不把非请求语言的坏模板留到现场。allowEmpty=false 拒绝空或全空白文本，allowEmpty=true 只放行合法的非 critical 说明；空字符串仍须满足零必需占位次数。

ResolveResult.Success 携 Text、RequestedLocale、ResolvedLocale、CatalogRevision、FormatProfileId/Revision、ModuleId/Key、UsedFallback、SemanticRevision 和 DiagnosticId。缺 key 返回 MissingKey/LOC-003，不返回伪装成功的空字串；可选合法空串返回 Success，IsEmpty=true。Failed 不覆盖宿主旧显示；内置三语应急文字为 Core 审校文本“文本不可用 / 文字無法顯示 / Text unavailable”，不用失败的 Resolve 再解析一次。

### 3.5 NativeTemplate：原串用途隔离

GetRawTemplate 的公开 service 入口只接受固定报告快照租约、已登记 module/key 和 NativeContractId/Revision/hash；§4.1 批 Context 可按它自己的固定批 pin 取得同一 raw 结果。PlainText 错用或合同不匹配为 LOC-015。NativeContract 定义槽 index/role/kind、Min/MaxOccurrences、是否允许重排、每槽 FormatToken 白名单（默认空）、alignment 是否允许（默认不允许）、MaxTokenChars 和模板长度限制；实际供应商参数角色必须由目标版本公开资料/运行资格绑定，Core 不猜。

nativeContract 的 JSON 字段固定为 id:string（key 语法）、revision:long 正值、hash:string（64 lowercase hex、外部已批准中立合同原件的 SHA-256，不是当前包 hash）、allowReorder:bool、allowAlignment:bool、maxAlignment:int、maxTokenChars:int、maxTemplateChars:int、slots:array。每槽为 index:int（连续从 0 起）、role:string（非空 key 语法）、kind:ParameterKind、minOccurrences:int、maxOccurrences:int、formatTokens:string[]（无重复）。槽数不超过 MaxArguments；token/template 限制正且不超过 MaxTemplateChars；次数范围同 PlainText。allowAlignment=false 时 maxAlignment=0；true 时为正且不超过 RuntimeBudget.MaxOutputChars，只允许有符号十进制宽度且绝对值不超该值。allowReorder=false 时占位 index 按非递减顺序出现。formatTokens 不含冒号/花括号，空名单只允许 `{index}`；非空 token 必须逐字命中批准名单。Contract hash 是匹配标识，Core 不声称它能证明供应商实际槽位；适配器必须以自身批准映射核同 id/revision/hash 后调用。

单次受限扫描 + CompositeFormat.Parse 核语法、完整槽集合和格式白名单；损坏/用途不符不 fallback。结果 NativeTemplateResult 含原串和精确 provenance，不提前 string.Format，不二次插值，不转换数字/精度。Core 只校验中立合同；DevExpress ID/具体应用属性映射在 Wpf 层。供应商实际调用 provider、已开弹窗刷新和实际槽位未绑定的 ID 为 NotSupported，不以英文默认词条报“全译”。raw String 独立不可变复制；适配呈现仍持该批租约直到回调真实退出。

## 4. 唯一公开 API 与构造契约

命名空间唯一为 Asun.Modules.Localization；下面是 Module API Contract v0.2 的唯一方法表。代码是定义形状，尚未创建/编译程序集；不得另留第二份 API 附录。

~~~csharp
public interface ILocalizationService {
    CatalogValidationResult ValidateCatalog(CatalogBytes input, CatalogValidationOptions options);
    ValueTask<CatalogLoadResult> LoadCatalogAsync(CatalogLoadRequest request, CancellationToken ct);
    ScopeCreateResult CreateScope(ScopeCreateRequest request);
    ScopeStatusResult GetScopeStatus(LocalizationScopeHandle scope);
    ResolveResult Resolve(LocalizationScopeHandle scope, ResolveRequest request);
    ResolveResult Resolve(ReportSnapshotLease snapshot, ResolveRequest request);
    SnapshotAcquireResult AcquireSnapshot(LocalizationScopeHandle scope, SnapshotRequest request);
    NativeTemplateResult GetRawTemplate(ReportSnapshotLease snapshot, NativeTemplateRequest request);
    SubscribeResult Subscribe(LocalizationScopeHandle scope, ILocalizationSurface surface);
    void Detach(SubscriptionToken token);
    ValueTask<SwitchResult> RequestSwitchAsync(LocalizationScopeHandle scope, SwitchRequest request, CancellationToken ct);
    OperationQueryResult GetOperation(Guid operationId);
    PresentationQueryResult GetPresentation(Guid batchId);
    ValueTask<ScopeCloseResult> CloseScopeAsync(LocalizationScopeHandle scope, ScopeCloseRequest request, CancellationToken ct);
    ValueTask<ServiceStopResult> StopAsync(ServiceStopRequest request, CancellationToken ct);
    RuntimeStatus GetRuntimeStatus();
}
~~~

LocalizationService(RuntimeOptions options, IResourceCatalogLoader loader, TimeProvider timeProvider, ILocalizationSurfaceScheduler scheduler, ILocalizationDiagnostics diagnostics) 是唯一公开实现构造器；RuntimeOptions 为不可变值，不另造动态配置接口。构造只验证 budgets 并进入 Ready，零目录也可 Ready；无 UI 宿主使用 InlineSurfaceScheduler（没有登记 surface 时不执行 UI）和 NullLocalizationDiagnostics。不得从后台更改 options；变更资源预算需新 service 实例和新 ServiceInstanceId，原租约按原实例停止规则释放。

请求/结果精确字段：

| 类型 | 必需字段、返回值与 Owner |
|---|---|
| CatalogBytes | Payload:ReadOnlyMemory<byte>；调用期间借用，调用方不得并发改写；Validate 不保存调用方内存。Load 登记前复制/持有 Core-owned 缓冲，调用方之后改原数组不能改变目录 |
| RuntimeOptions / RuntimeBudget | RuntimeOptions(Budget:RuntimeBudget)；Budget 含 §3.2 全部命名字段（含四个期限上限）；方法请求期限必须正且 <= 对应 Budget 期限；没有省略请求期限的另一重载 |
| ResourceKey / CatalogRevision | ResourceKey(ModuleId:string,Key:string)；CatalogRevision(SchemaId:string,CatalogVersion:string,Hash:string)，语法见 §3；值相等用 Ordinal 字段比较 |
| ParameterSpec / ParameterKind | ParameterSpec(Position:int,Name:string,Kind:ParameterKind,Nullable:bool,MaxDisplayChars:int,MinOccurrences:int,MaxOccurrences:int)；ParameterKind 的七个成员见 §3.3 |
| ArgumentValue / FormatProfile | sealed ArgumentValue；静态工厂 Text(string)、Identifier(string)、Count(long)、Decimal(decimal)、FiniteDouble(double)、Timestamp(DateTimeOffset)、Duration(TimeSpan)、Null()；IsNull:bool、Kind:ParameterKind? 与对应类型值只读；Null 时 Kind=null/无值，其余 IsNull=false/Kind 与工厂一致；不提供 public object 构造器。FormatProfile 与 ParameterFormatRule 按 §3.3 精确字段及顺序构造 |
| CatalogValidationOptions | RuntimeBudget、RequireApproved=true；false 仅验证草稿，不允许 Load 注册运行目录 |
| CatalogLoadRequest | OperationId:Guid 非空；SourceRef:string；ExpectedHash:64 hex；LoadDeadline:TimeSpan；不再同时要求 bytes 和 loader 两种来源 |
| CatalogValidationResult / CatalogIssue | IsValid:bool、Issues:immutable CatalogIssue[]、ValidatedHash:string?；Issue 为 ModuleId?/Key?/Locale?:string、JsonPath:string、Code:string、ReasonId:string。路径明确到坏字段/数组位置；不含原值/异常栈。不登记目录；IsValid=true 时 Issues 为空、Hash 非 null |
| CatalogLoadResult | OperationId:Guid、Status:CatalogLoadStatus、CatalogRevision?、Error?、ResourcesReleased:bool；Loaded 与 true 同时成立才能创建 scope；DrainUnknown 为可查询的非终态观察 |
| ScopeCreateRequest | OwnerTag、InitialLocale、CatalogRevision、RequiredKeys:immutable ResourceKey[]、AllowCriticalFallback=false、FormatProfile；先验证所有必需 key，不返回半构造 scope |
| ScopeCreateResult | IsSuccess、Handle:LocalizationScopeHandle?、Error?；成功 handle 非 null；失败无 handle、无活动引用 |
| LocalizationScopeHandle | service 生成 Guid Id、Guid ServiceInstanceId、long CreationEpoch=1；sealed/internal 构造，无 Dispose。CurrentEpoch 在 service 状态内，不能以修改 immutable handle 实现关闭 |
| ScopeStatusResult | IsSuccess:bool、State:ScopeState?、CurrentEpoch/CurrentRequestOrdinal/ActivityRevision:long?、ActiveLocale:string?、ActiveCatalogRevision?、ActiveFormatProfile?、Error?；外来 handle 失败时事实全 null；Stopped 释放完整状态后只保 State/CurrentEpoch=2，其余为 null |
| ResolveRequest | ModuleId、Key、Arguments:immutable ArgumentValue[]、MaxOutputChars；不接收与快照不匹配的临时 culture |
| ResolveResult | Status:ResolveStatus、IsSuccess:bool（Status=Success）、Text:string?、IsEmpty:bool、RequestedLocale/ResolvedLocale:string?、CatalogRevision?、FormatProfileId:string?、FormatProfileRevision:long?、ModuleId/Key:string、UsedFallback:bool、SemanticRevision:long?、DiagnosticId:Guid、Error?；失败 Text=null/IsEmpty=false，不用应急串冒充成功 |
| SnapshotRequest | Purpose:string、ExpectedActivityRevision:long?（默认 null 表示当前）；冻结快照已含 FormatProfile，不能另传不同文化悄悄覆盖 |
| SnapshotAcquireResult | IsSuccess、Lease:ReportSnapshotLease?、Error? |
| ReportSnapshotLease | Id:Guid、ServiceInstanceId、ActivityRevision、CatalogRevision、Locale、FormatProfile、AllowCriticalFallback:bool；sealed/internal 构造、IDisposable，Dispose 幂等；不重新从 scope 取当前值 |
| NativeTemplateRequest | ModuleId、Key、NativeContractId、Revision、Hash；不包含运行供应商 object 参数 |
| NativeTemplateResult | IsSuccess:bool、Template:string?、RequestedLocale/ResolvedLocale:string?、CatalogRevision?、ModuleId/Key/NativeContractId:string、Revision:long、Hash:string、SemanticRevision:long?、UsedFallback:bool、DiagnosticId:Guid、Error?；成功 Template 非 null，失败为 null；不带供应商对象 |
| SwitchRequest | OperationId、TargetLocale、CatalogRevision、FormatProfile（必须显式给，即使沿用旧值）、SwitchDeadline、PresentationDeadline；scope 必需集合保持创建时版本，改变 RequiredKeys 需关闭后创建新 scope |
| SwitchResult | OperationId:Guid、RequestOrdinal:long?（接纳前拒绝为 null）、Status:SwitchStatus、ActivityRevision:long?、CatalogRevision?、Locale:string?、PresentationBatchId:Guid?、Error?、PresentationError:LocalizationError?、ResourcesReleased:bool；活动向量字段是结果时门内观察值，非声称失败目标已生效；外来 scope 拒绝时全 null。PresentationError 只表示未能安排呈现，核心成功 Error 仍 null；不表示 UI 排空 |
| SubscriptionToken / SubscribeResult | token 的字段 Id:Guid/ServiceInstanceId:Guid/ScopeId:Guid/SurfaceId:string，internal 构造；SubscribeResult 为 IsSuccess:bool/Token?/InitialPresentationBatchId:Guid?/Error?，成功时 Token 与 batch ID 非 null，不可转移；同 scope 重复 surface ID 或同 service 重复登记同一 surface 对象为 LOC-014，实例归属算法见 §5 |
| ScopeCloseRequest / ServiceStopRequest | Reason:string、DrainObservationTimeout:TimeSpan；不自动重开、不过期回滚 |
| ScopeCloseResult | Status:ScopeCloseStatus；FinalEpoch:long?、PendingRequestCount/ExecutingReadCount/RunningSurfaceCount/ScopeOwnedReferenceCount:long、Error?；拒绝时 Epoch=null、计数0；报告租约另计 |
| ServiceStopResult | Status:ServiceStopStatus；RemainingScopeCount/LoadCount/ExecutingReadCount/RunningSurfaceCount/ReportLeaseCount:long、Error?；未归还项明确列出 |
| OperationQueryResult | Lookup:QueryLookup、OperationId:Guid、Kind:OperationKind?、State:OperationState?、LoadResult:CatalogLoadResult?、SwitchResult:SwitchResult?、ResourcesReleased:bool?；Found 时 Kind/State 非 null，按 Kind 只填一个已有观察/终态结果，Pending 可两结果皆 null |
| PresentationQueryResult | Lookup:QueryLookup、BatchId:Guid、ScopeId:Guid?、ActivityRevision:long?、IsLogicalComplete/ResourcesReleased:bool?、Receipts:immutable PresentationReceipt[]；Found 时身份/布尔非 null；无记录时 Receipts 为空，其余 null |
| RuntimeStatus / RuntimeBudgetUsage | ServiceInstanceId:Guid、State:ServiceState、BudgetUsage:RuntimeBudgetUsage、ScopeCount/LoadCount/ExecutingReadCount/RunningSurfaceCount/ReportLeaseCount/OperationRecordCount/PresentationRecordCount/DroppedDiagnostics:long；Usage 为 ResidentPayloadBytes/ReservedLoadBufferBytes/CachedCatalogCount/SubscriptionCount/QueuedBatchCount:long；全为只读原子快照 |

上表省略后缀类型时统一规则为：ID/DiagnosticId=Guid 非空、文本=string、修订/代次=long、期限=TimeSpan、集合=ImmutableArray<T>（禁止 default，空集合使用 Empty），`?` 才可缺省。ScopeCreateRequest/ResolveRequest/NativeTemplateRequest/SwitchRequest 的构造参数顺序就是表列顺序，§8 示例沿用该顺序；ReadOnlyMemory 与全部集合必须按这里的所有权约束复制或借用，不能靠 readonly record 掩盖可变数组。Error? 为 LocalizationError?，其字段 Code/ReasonId:string、Retryable:bool、DiagnosticId:Guid、SafeDetails:immutable KeyValuePair<string,string>[]；键/值分别受 MaxKeyChars/MaxTemplateChars，条数不超过 MaxArguments+1，不含参数原值。所有成功结果 Error=null，所有失败/未排空结果 Error 非 null。

状态枚举成员唯一如下；没有未命名的 Status 类型：

~~~csharp
public enum CatalogLoadStatus { Loaded, Rejected, Failed, Cancelled, TimedOut, DrainUnknown }
public enum SwitchStatus { Applied, NoChange, Superseded, Cancelled, TimedOut, Rejected, Failed }
public enum ScopeCloseStatus { ScopeClosed, NotDrained, WaitCancelled, Rejected }
public enum ServiceStopStatus { ServiceStopped, NotDrained, WaitCancelled }
public enum ScopeState { Ready, Switching, Stopping, Stopped }
public enum ServiceState { Ready, Stopping, Stopped }
public enum ResolveStatus { Success, MissingKey, Failed }
public enum QueryLookup { Found, NotFound }
public enum OperationKind { LoadCatalog, Switch }
public enum OperationState { Pending, DrainUnknown, Completed }
public enum SurfaceStatus { Applied, Failed, Expired, NotSupported }
public enum PresentationStatus { Pending, Applied, Failed, Expired, Detached, Superseded, NotSupported }
~~~

正常领域错误均为 typed result.Error，不是异常或 null 值表达成功。null API 参数/构造器非法 budget 是 ArgumentException 系列编程错误，文档/单测必须覆盖；ArgumentValue 工厂只冻结类型和非 null 引用，有限性/非负数等领域校验在 Resolve 返回 LOC-005。不把 OOM/进程崩溃 catch 后伪报正常关闭。GetScopeStatus/Close 验 service identity 和 handle 私有 owner 身份；外来 handle 为 LOC-008。真正关闭后移除活动 scope 记录；同实例、合法已发出的 handle 可再查 Stopped 或 Close 得 ScopeClosed（计数0/epoch2），不为每个历史 scope 保存完整永久表。

handle 的公开身份值不可变；私有 lifetime cell 由 service 单写，关闭后只保留轻量 owner identity token/Stopped/epoch2，不引用整个 service、目录或 surface，随调用方最后 handle 引用回收。ScopeState.Switching 表示存在尚未终态的最新切换，Resolve 仍读活动快照；计数和整个运行状态在同门下读取，不拼接多个时刻的快照。无效观察期限、default 集合、非正 ExpectedActivityRevision 等结构输入为 ArgumentException；完全不支持语言、缺 key、签名与资源身份不兼容则为上表领域失败。AcquireSnapshot 在同门比较 ExpectedActivityRevision，不符为 LOC-011、无 lease/无 pin；相符时先计 lease slot 再取得 pin，Close 后不再创建租约。Close/Stop 在接纳前 ct 已取消时仅 WaitCancelled，不开始关闭；关闭开始后取消只撤该次观察。

OperationId 由调用方在 service 全局范围产生不重复 ID。Core 的幂等窗口是仍保留的操作记录：同 ID/同已验证请求内容复用原操作，绝不再发布/递增代次；同 ID/不同输入返回 LOC-014，接纳前拒绝不影响现存 pending。内容比较包含方法、scope identity、全部请求字段和 FormatProfile 值，不比较 ct；禁止用非抗碰撞 GetHashCode 代替内容一致性。终态且资源已释放的记录按完成顺序 FIFO 淘汰；load/switch 未真实释放的记录不可淘汰。容量满且无可淘汰项则接纳前 LOC-013。GetOperation/GetPresentation 淘汰或未知 ID 一律 NotFound，不用无限墓碑声称能区分两者；调用方遇到 NotFound 禁止以旧 ID 盲重放，需按当前 scope 状态重新决定一次新意图/新 ID。记录已淘汰后 Core 不保证检测旧 ID 或返回历史结果，也不作跨重启恰好一次保证。

原请求 ct 控制该操作的协作取消，scope close/service stop 亦可取消它；重复调用的 ct 只取消该次等待，抛 OperationCanceledException，不改变原操作/终态，调用方用 GetOperation 回查。首次 load 期限/取消可返回 DrainUnknown 观察；首次 switch 只有其 worker 引用真正归还才返回唯一终态。Close/Stop 的等待取消按其 typed WaitCancelled 返回，不采用此重复等待异常规则。所有期限从对应接纳（Close/Stop 每次观察开始）算单调 elapsed，重复等待不重置原执行期限。

报告租约 Resolve 与 scope Resolve 返回同一形状；前者不要求 scope/service 仍 Ready，仅要求自己的 lease 未释放且属于该 service。同步 Resolve 先取得内部读取引用再退出短锁。Dispose 在同门下标记 lease 不再接纳新 read，幂等立即返回；最后物理 pin 延迟至已接纳 read 的 finally 归还，不同步等待其它线程。Stop 将这些 read 和延迟 pin 继续计入排空；已 Dispose 不等 ResourcesReleased。Context 只读，不接受任意外部 provider。

### 4.1 注入端口、事件与区域

| 端口 | 唯一方法/字段与执行责任 |
|---|---|
| IResourceCatalogLoader | ValueTask<CatalogReadReceipt> ReadAsync(CatalogReadContext context, CancellationToken ct)；context 为 SourceRef:string、Buffer:Memory<byte>（Core 提供、长度 MaxCatalogBytes）、Deadline:TimeSpan（剩余期限）。receipt 为 ByteCount:int（0..Buffer.Length）、EndOfInputConfirmed:bool、SourceVersion:string?；必须确认完整输入，非完整返回 LOC-002。receipt 返回前必须实际结束写入/归还外部读取句柄；恰好填满且 EOF 可合法，不加哨兵字节 |
| ILocalizationSurface | string SurfaceId、immutable ResourceKey[] RequiredKeys；ValueTask<SurfaceReceipt> PresentAsync(PresentationContext context, CancellationToken ct)；仅短投影，不做资源 I/O 或业务提交 |
| ILocalizationSurfaceScheduler | ValueTask<SurfaceReceipt> ScheduleAsync(ILocalizationSurface surface, PresentationContext context, CancellationToken ct)；返回前 callback 必须真实退出，不得以“已入 Dispatcher 队列”完成 Task |
| PresentationContext | BatchId/ScopeId:Guid、CapturedEpoch/ActivityRevision:long、Snapshot:LocalizationSnapshot、ResolveResult Resolve(ResolveRequest)、NativeTemplateResult GetRawTemplate(NativeTemplateRequest)、bool IsCurrent()；无 Dispose/写权威 |
| LocalizationSnapshot | sealed/internal 构造的不可变元数据：CatalogRevision、Locale:string、FormatProfile、ActivityRevision:long、AllowCriticalFallback:bool。批/报告拥有的内部 pin 保持目录；不公开可变索引或绕过 service 的 Resolve；scope 创建时的 critical 政策进入所有快照，适用于全部查词 |
| SurfaceReceipt | SurfaceId:string、BatchId:Guid、ActivityRevision:long、Status:SurfaceStatus、Error?、ActualRegions:immutable string[]；Applied 只覆盖已实际更新的区域；身份/修订与 Context 不符为 Failed/LOC-009 |
| PresentationReceipt | SurfaceId:string、Status:PresentationStatus、ActualRegions:immutable string[]、Error?、CallbackExited:bool；Core 为每个登记 surface 维护 Pending→一个逻辑终态，callback 真退出独立更新 CallbackExited，不倒改逻辑终态 |
| ILocalizationDiagnostics | bool TryWrite(LocalizationEvent value)，必须短、非阻塞；调用发生在 Core 锁外，false/异常计 DroppedDiagnostics，不影响权威结果 |

PresentationContext 的 Resolve/raw 使用固定批快照；它在 scheduler 真正返回后失效，不能被控件保存并迟后调用。IsCurrent 比较 service 中 epoch/ActivityRevision、订阅 token 和呈现 deadline；callback 初进及每次可能重入的外部调用返回后都检查。不能抢占已开始的控件 setter，检查不承诺跨控件原子性；Close 不能因此保证零像素已写，UI 故障必须保留逐区域结果。

批 Context 也按同门接纳 read 并取得独立 pin；callback 退出立即阻止后来 read，已接纳 read 归还前不能发 PresentationResourcesReleased。callback 禁止 fire-and-forget 控件写入或保存 Context；违反规则的 read 仍须计费/排空，不通过 Dispose 提前释放。报告与批 Resolve/raw 均沿固定快照 critical 政策；批 Context.raw 是唯一受生命周期限制的租约入口例外，不另造可释放报告租约。

LocalizationEvent 是不可变投影：EventSequence:long（service 内递增）、Utc:DateTimeOffset（UTC）、ElapsedTimestamp:long（注入 TimeProvider.GetTimestamp）、Kind:LocalizationEventKind、ScopeId:Guid?/Epoch:long?/OperationId:Guid?/RequestOrdinal:long?/BatchId:Guid?/SurfaceId:string?、ActivityRevision:long?/Status:string?/ErrorCode:string?、ResourcesReleased:bool?。LocalizationEventKind 固定 CatalogLoadObserved、CatalogLoadCompleted、ScopeCreated、SwitchAccepted、CorePublished、SwitchCompleted、PresentationBatchCompleted、PresentationResourcesReleased、ScopeStopping、ScopeClosed、ServiceStopping、ServiceStopped、DiagnosticFailure；Status 为本页相关状态枚举名称，不能作业务状态。序号耗尽后停止输出事件、DroppedDiagnostics 饱和累计，不影响业务请求。诊断不是可靠事务总线：权威回查是 API 返回值及查询；Core 不调用未知 observer 同步订阅，不设无界事件队列。

## 5. 逐操作顺序、状态和错误

### 5.1 加载/查询/原模板

Load 接纳前校验 ID/摘要/状态/预算 → 预留并发读取 buffer → loader 完整读取 → exact hash → 严格 JSON/字段/重复/审核/模板/fallback → 不可变索引 → service 内登记 → 释放读取句柄/buffer 临时引用 → Loaded(ResourcesReleased=true)。登记成功只增加可用目录，不改变 scope。JSON 采用 JsonDocumentOptions：AllowDuplicateProperties=false、AllowTrailingCommas=false、CommentHandling=Disallow、MaxDepth=明确 budget；检查未配对 surrogate/无效 UTF-8、未知字段和重复 message。不自己编完整 JSON parser。

loader 在预留 slot 对应的有界 worker 中调用，不在公开方法返回 ValueTask 前同步调用未知 loader；独立期限观察可在它同步阻塞时仍返回 DrainUnknown。worker 真实返回前 slot/buffer 不可复用，也不创建替代 worker 重试同读取。ValidateCatalog 是有界同步纯计算、不调用 loader；其内容预算取调用方 options 和 service 对应上限的较小者，停止后或无计算 slot 时返回 IsValid=false、LOC-012/013 Issue，不设置 ValidatedHash。Load 必须再次按 service 的预算/RequireApproved=true 验证，不能拿外部 ValidatedHash 跳过运行校验。UTF-8 用严格解码失败模式验证；JSON 字符串以框架读取并检查 Unicode surrogate 成对，不接受替代字符静默修复。

取消/期限发生在 loader 正在使用 buffer 时记录 DrainUnknown；协作 token 传递，停止登记资格。ReadAsync 真正返回（成功/异常）且 finally 回收其句柄后才可释放 buffer/slot 和转换为 Cancelled/TimedOut/Failed。某 adapter 不合作返回前 service 保留引用，不能用 Task.WaitAsync 截止当资源退出证据。主路线是托管目录读取，无 HALCON/native 视觉句柄；“native 排空”仅适用于外部 loader/scheduler 确有该资源的后续实现。

Resolve：在短锁内验 handle/lease 并 pin 当前 snapshot → 锁外校验 key/参数/purpose → 精确查找和显式 fallback → 类型转 display string → 校验完整模板签名/输出上限 → 合成 → finally 归还 pin。零参数是合法空数组；空/未知 key 或无命中返回失败。GetRawTemplate 使用同一 snapshot/provenance，独立校验用途合同并返回原串。

### 5.2 创建、切换、订阅

CreateScope：service Ready + 已装载修订，门内取得临时 catalog pin/计入正在执行的创建 → 锁外必需 key/fallback/FormatProfile 完整预检 → service lock 下再次核 Ready/预算 → 分配 Guid scope ID、CurrentEpoch=CreationEpoch=1、RequestOrdinal=0、ActivityRevision=1 → 临时 pin 转初始 scope-owned pin → 成功返回 Handle。并发 Stop 在分配之前赢则失败，不产生 ScopeCreated；同 OwnerTag 多次创建也必须不同 ID。失败 finally 归还临时 pin/创建计数，不留下半初始化记录；GetRuntimeStatus().ExecutingReadCount/Stop 同样覆盖这类预检。

切换先做结构/版本/ID接纳前验证，合法新请求才分配 scope 单调 RequestOrdinal 并令旧 pending Superseded；同 OperationId 的重试不构成新请求。新请求即使 TargetLocale 等于活动语言，也必须使旧 pending 失效。锁外预检目标目录/必需 key/格式，最后在同一 scope gate 核 epoch/latest ordinal/token/deadline；原子交换的是 CatalogRevision+Locale+FormatProfile 全向量。仅全向量等价可 NoChange；译文版本/格式变了但语言相同必须 Applied。每次实际交换 ActivityRevision++；epoch 只在关闭递增。计数溢出接纳前 LOC-013，不回绕。

目标 catalog 在接纳时先取得临时 pin，锁外预检不被缓存淘汰；失败/取消/替代在 finally 归还。RequiredKeys 的既有 semanticRevision/purpose/参数签名/native 合同与订阅覆盖必须兼容，改义或破坏性修订为 LOC-011，需显式关闭/重建并由宿主重新绑定；纯译文/兼容新增 key 可 Switch。新 scope 的 RequiredKeys 可空（工具按需查词），条数 <= MaxMessages、无重复；不得据空集合宣布产品完整。

首次 Switch 的 ct 若在接纳前已取消，返回 Cancelled/LOC-016、RequestOrdinal=null、ResourcesReleased=true，不撤旧 pending，也不计新 operation；有效已接纳的新意图才有替代资格。Create/Subscribe 锁外预检也预留全 service MaxConcurrentReads slot，满则 typed LOC-013；不为预检另开无界计算队列。

CorePublished → SwitchCompleted(Applied) 不等待任何 surface；请求内部引用已归还才 ResourcesReleased=true，呈现批仍可能排空未知。NoChange 若有落后订阅须发新独立呈现批，否则 BatchId=null。提交后的取消只能影响调用方后续等待，不能改变 Applied；取消/关闭先于提交则不发布。回退是新 operation/ordinal/activity revision。

Subscribe 验 surface ID/必需 key 全部能在 scope 当前快照解析 → pin 快照与订阅 slot → 登记 token → 安排一次初始呈现批，使后建窗口直接显示当前语言。不可执行外部 callback 时持 Core 锁。批中的 surface 集合在排队时固定；后建区域用自己的初始批，不把未来窗口塞进旧批分母。关闭/Detach 后队列项标 Detached，不伪造此前 Applied。

同一 service 在最后登记门用对象 reference identity（不调用 surface.Equals/GetHashCode）核 surface 实例尚无登记；它与同 scope 的 SurfaceId 唯一性分别校验。已登记同一对象，即使换 SurfaceId 或换 scope，也拒绝 LOC-014/ReasonId=surfaceAlreadyOwned，不创建 token/pin/初始批。并发预检不能绕过此门。Detach 立即撤新接纳，但该实例仍有 queued/executing callback 时保留原归属及引用；确认所有相关队列未运行或 callback 真实退出后移除实例索引，再允许宿主重新登记。索引只覆盖仍占 MaxScopes/MaxSurfacesPerScope 容量的活动或待排空订阅，不留永久墓碑。跨 service 不能共享 surface 是宿主组合根约束，不引全局表；独立 service 无法核别的实例归属。此处细化既有“surface不能跨scope共享”，不将 WPF 类型引入 Core。

surface.SurfaceId/RequiredKeys 的外部 getter 只在锁外读取并复制一次，异常返回 SubscribeResult 失败/LOC-009；之后不在锁内重入 surface 或读取其可变属性。这些 getter 是短同步端口、不得阻塞/I/O；Core 无法抢占它们，不能把不合作 getter 包装成“超时已关闭”。取得当前向量的临时 read pin 后才锁外预检；最后登记门检查仍 Ready/epoch/当前向量等预检值，否则 LOC-008/011（宿主重新 Subscribe），不把旧预检结果用于新目录；finally 归还预检 pin/slot。Inline scheduler/diagnostics 即使无 UI 也不获锁内回调特权。

Subscribe 的 RequiredKeys 必须无重复且非空、条数 <= MaxMessages；service 复制它并冻结，批 Context 只允许解析该 surface 登记 key（外部 key 为 LOC-003）。若已有 waiting 批，先将它逐区域置 Superseded、归还尚未提交 scheduler 的 pin，再以当前向量/当前全部订阅构建新批；新订阅返回该新批 ID，因此不突破一执行/一等待上限，也不修改旧批分母。发布/订阅先预留呈现记录；若满且没有已释放可淘汰记录，则 Subscribe 拒绝而不登记，Switch 仍可核心 Applied/NoChange、PresentationBatchId=null、Error=null、PresentationError=LOC-013，由宿主显示区域未更新；不把呈现失败混入核心失败。Subscribe 的 slot/记录/必要 key 验证全部成功后才登记，失败不丢原 waiting 批。

每 scope 至多一份待执行刷新批 + 一份执行中批；后到 activity revision 替换等待批，旧批逐区域标 Superseded；执行中批不能取消资源引用，也不能宣称新批已呈现。多个 surface 在同一 dispatcher 可逐个短更新。某 callback 抛异常且返回只令该 surface Failed；同步阻塞不返回则同 Dispatcher 的 A/B 都可能停顿，独立状态/语言隔离不等 UI 阻塞隔离。

呈现 worker 与请求 worker 分开，只有上述有界批 slot 可启动调度；不能在 RequestSwitchAsync/Subscribe 的完成路径同步进入 scheduler。InlineSurfaceScheduler 仅在该 worker 上调用短无 UI callback，Wpf scheduler 明确转目标 Dispatcher；由 scheduler 包装 callback 的真实异常/退出为回执。调度失败且已退出才可释放 pin；未退出计 RunningSurfaceCount。MaxPresentationRecords 内逻辑完成且真实释放的批按完成顺序淘汰，其余不可淘汰；GetPresentation 不作永久历史档案。

PresentationBatchCompleted 只表示每个登记区域获得 Applied/Failed/Expired/Detached/Superseded/NotSupported 逻辑回执，不等资源释放；另发 PresentationResourcesReleased 只在所有 queued/executing scheduler 已确认不运行且 snapshot pin 归还后。期限记录 Expired 后不接收迟到 Applied 覆盖；真实返回仍更新资源释放，不倒改历史超时。队列满调度拒绝转 Failed/LOC-013，Core 已发布向量保留。

逐区域只有 Pending 能进入逻辑终态：新向量发布使旧执行批仍 Pending 的区域 Superseded；Detach/Close 使对应仍 Pending 区域 Detached；期限使仍 Pending 区域 Expired，实际回执使仍 Pending 区域 Applied/Failed/NotSupported。以上与真实回执在同门下按先到者冻结，已 Applied 区域不追改为失败。Superseded/Detached 触发协作取消但不释放仍运行 pin；迟到 callback 回执仅补真实退出和此前已写区域诊断，不覆盖冻结回执。

PresentationDeadline 从批建立开始，初始 Subscribe 批用 Budget.PresentationDeadline；计时不因入队或重试重置。未执行且期满的批直接 Expired/释放，执行中期满只标逻辑 Expired。RunningSurfaceCount 包含已交 scheduler 未真返回的调用；PendingRequestCount 包含已逻辑替代但 worker 未真退出的 scope 请求。ScopeCloseResult.ScopeClosed 与 ServiceStopResult.ServiceStopped 必须全部对应计数为 0，NotDrained 计数是观察时真实余额。

### 5.3 Close/Stop/租约归还

Close 第一次在 scope gate 置 Stopping、CurrentEpoch 从 1→2，禁止新 Resolve/Switch/Subscribe/Acquire（LOC-008）并取消 pending、撤订阅接纳/丢弃队列旧批。immutable handle.CreationEpoch 不变；旧 callback 的 CapturedEpoch 必须与内部 CurrentEpoch 比，不比较两个永远为 1 的 handle。发布与关闭由同门线性化：发布先赢保留已发布向量，关闭先赢无 CorePublished。

排空集合明确含：接纳的 scope Resolve/Acquire 操作、未完成切换 worker、所有执行中/已交给 scheduler 尚未确认取消的 surface callback、scope-owned snapshot pin。外部调用在 finally 真正退出后归还；Close 不能 Dispose callback 正在读的上下文。可控 callback 从重入/阻塞返回后复核 epoch，不再执行余下旧控件写入。

并发 Close 共享第一次关闭的 drain owner/Reason/epoch；每个调用的观察期限/取消只影响该次等待。返回 NotDrained/WaitCancelled 是观察结果，不缓存成永久终态；后续调用继续观察，实际归零后统一 ScopeClosed 终态。这样期限后继续观察可完成，不与“共享原 Task 结果永远 NotDrained”矛盾。Stopped scope 的 handle 只可关闭/查状态，不可重开；重开需新 CreateScope、新 ID。

ScopeClosed 不等待调用方合法报告租约；它们通过 Resolve(lease,...) 独立继续读原向量。Lease.Dispose 的非阻塞标记/延迟释放按 §4；ReportLeaseCount 包含已经 Dispose 但仍有 read pin 的租约，最后 read 退出才减。Detach 幂等立即撤接纳，已运行 callback 由 Core drain 计数承担；关闭后仍可 Detach，Core 在 callback 退出后清除引用 surface 的注册条目，不保留控件强引用。外来 token 不执行任何撤销；合法已移除 token 再 Detach 是 no-op，不建无限墓碑。

Stop 先全 service Stopping、拒绝新 Validate/Load/Create/Subscribe/Switch/Acquire，再依同一 Close 顺序关闭每个 scope，等待 loads/surfaces/reads（含已接纳 Validate）/报告租约归还；任何未归还项返回 NotDrained。报告已持租约可继续 Resolve 并自行释放；所有归零后清缓存、返回 ServiceStopped，不能提前清 cache 或强制释放。并发 Stop 与 Close 一样共享 drain owner、逐次观察期限，不缓存永久 NotDrained；ServiceStopped 后重复 Stop 返回同一成功终态。Service 没有额外 Dispose/OpenScope/CloseScope API；运行状态与资源计数由 GetRuntimeStatus 查。Core 不需要自动重连，loader 断连的重试是明确新 ID；未知旧读取未退不能在同 slot 并发重读。

### 5.4 错误与降级

| Code | 原因和允许恢复 |
|---|---|
| LOC-001 | 不支持语言；保留活动向量，选择目录已声明语言 |
| LOC-002 | 原字节/UTF-8/JSON/重复属性/hash/完整读取无效；整包拒绝，取有效原包，新 ID 重试 |
| LOC-003 | 未知 key、必需集合缺失或链耗尽；精确定位缺项，更新同义已审词条/目录后新请求 |
| LOC-004 | 模板/占位次数/签名非法；整候选拒绝，不丢参数、不改显示精度 |
| LOC-005 | 参数数目/种类/有限性/nullable非法；只本次解析失败，不修改业务值 |
| LOC-006 | 输入/输出超长或预算算术 overflow；拒绝，不静默截断 |
| LOC-007 | 参数数量超 MaxArguments；先调整正式合同/预算，不能 object[] 绕过 |
| LOC-008 | 外来/已关闭 handle、epoch过期或已释放 lease；禁止继续读写，使用新合法 scope |
| LOC-009 | surface抛异常/未支持入口；区域失败，核心向量不回滚，宿主显示明确局部错误 |
| LOC-010 | 观察/执行期限到达；区分发布未发生、呈现 Expired 和排空未完，允许同关闭任务再观察 |
| LOC-011 | schema/API/语义/FormatProfile/同版本hash不兼容；拒绝升级或恢复闭包 |
| LOC-012 | service Stopping/Stopped；拒绝新操作，既有 lease按寿命读取 |
| LOC-013 | 有界容量不足/ID计数耗尽/调度队列满；拒绝接纳，先释放无用租约或由宿主降低并发 |
| LOC-014 | 重复 OperationId 内容不同、重复 SurfaceId 或同 service 重复 surface 对象；明确冲突，不重放 |
| LOC-015 | PlainText/NativeTemplate 用途或合同不符；绑定正确用途再调用 |
| LOC-016 | 调用方取消操作或关闭观察等待；不改已发布事实，回查原操作或继续观察真实排空 |

Core load/switch 的 Unknown 不得等同业务“提交未知”：未完成观察返回明确 DrainUnknown/查询 Pending，生产枚举不动。纯同步解析无 native drain 状态；HIL/视觉资格不适用。日志失效最多 DroppedDiagnostics 增长，权威结果/错误不依赖诊断回调成功。

Cancelled/WaitCancelled 使用 LOC-016；TimedOut/NotDrained 使用 LOC-010；Superseded 使用 LOC-008、ReasonId=superseded。DrainUnknown 的 Error 保留导致观察结束的取消/期限/读取故障代码，不能先报 Cancelled/TimedOut 终态。首个取消与期限竞态原因在操作 gate 冻结；后续取消不会改初因。Load 在登记前同门再次检查 Ready/取消/期限，登记先赢则 Loaded，取消先赢则不登记；接纳前 ct 已取消返回 Cancelled、ResourcesReleased=true，不调用 loader。

## 6. 持久化、兼容、发布与回退

独立包发布内容为 Core DLL/API、完整目录原字节及版本/hash、格式/术语审核元数据、最小宿主和使用说明；Wpf DLL 可选，不能成为 Core 加载前提。旧 .NET8 WinForms 不是此次自动升级对象，需要它的消费目标与适配另立切片。

Core 不做磁盘写入/首选语言存储。宿主将目录原字节和 provenance 保存到受控不可变存储；先完整落盘/封口再发布引用，原子替换不等完整断电耐久，耐久和凭证/签名验收归宿主存储/安全策略。SHA-256 只证字节身份，不证发行者；需要签名时外部 loader/trust verifier 先验证固定 allow-list，Core 不编造证书策略。

报告闭包：CatalogRevision 原 payload、语义/模板合同修订、requested/resolved来源、固定 Locale+FormatProfile 全规则、报告自己的原事实引用。进程重启新 service/新 scope/new epoch，不能反序列化旧 handle、租约、Guid callback 或 OperationId task。宿主从完整 hash 原字节重新 Load/Create/Acquire 后生成新的语言显示；缺旧版本则 LOC-011/不可复现，不以最新资源冒称原报告恢复。

SemVer 的译文修订只改文本且保签名/语义；新增可选 key 是兼容增量；删除、改义、用途/参数kind/单位含义/fallback或审批策略变更是破坏性新契约。新目录加载不能自动迁移 scope 必需集合；宿主明确 Switch 或关闭/重建。回退已验证旧包允许目录版本下降，ActivityRevision/RequestOrdinal 永不下降，不复用旧请求/呈现 ID；原 catalog hash仍是旧字节。总缓存满而旧报告固定资源时拒新加载，不能靠删除报告版本换升级成功。

## 7. 可选 UI 适配 PageContract

### 7.1 任务流与边界

本模块没有独立页面、语言选择器、Dock 工作台、PropertyGrid 或图表。它提供宿主嵌入的文字投影/局部状态，不能为“炫技”新增资源编辑 UI。复杂信息、图像、工艺参数和权限留在宿主已有工作台。本节冻结语言适配的可见行为，宿主页面引用其规范，不复制 localizer。

宿主选择语言 → 立即显示短“更新文本 / 更新文字 / Updating text”状态 → 核心向量 Applied → 已登记区域按批更新 → 状态恢复原任务状态。局部失败采用宿主已有状态/错误区“部分文本未更新 / 部分文字尚未更新 / Some text is unchanged”，详细码和受影响区域放 DevExpress SuperTip；关键恢复动作始终有显式文字，不只靠悬停。语言切换不再提交业务、清筛选、重置目标、重建 VM、关闭编辑器或抢焦点。

### 7.2 25.2.3 实例接入

1. 每个 Grid view 独立 GridRuntimeStringCollection，元素为 RuntimeStringIdInfo(GridControlRuntimeStringId,string)，一次构造该 view 登记覆盖集合后给 DataViewBase.RuntimeLocalizationStrings。适用 NoRecords、NoRecordsFound、GridGroupPanelText 等已知普通字串；集合/元素不在 A/B 间共享，不设置 GridControlLocalizer.Active。
2. DataViewBase.LocalizationDescriptor 只读；不写只读属性，不猜 SetValue 字符串键/刷新路径。summary/标题等供应商占位模板经 §3.5 raw 合同取得，未知槽位 ID保持 NotSupported；主区属性赋成功不能报告原生过滤/汇总窗全译。
3. Bars 通过实际 BarItem.Content/SuperTip；DevExpress SuperTipItem.Content 独立绑定当前批快照。标准可承载元素用 SuperTipControl.SuperTip → element.ToolTip，保持 DevExpress SuperTip；不降为无解释的普通 tooltip，不依赖未知 PatchDataContext行为。
4. 宿主 Dock 已存在时仅更新实际 BaseLayoutItem.Caption/TabCaption 和自有 Content，不变更 Dock 分割、浮动布局/选中页。自有 popup/flyout 必须显式 owner/Source和生命周期订阅；不借 Popup 默认 DataContext/线程文化反推宿主。
5. Table/Grid 已开过滤器、日历、summary原生窗逐区域单独登记公开入口和 actual regions；尚无已验证入口就返回 NotSupported。设置模板可能重建输入节点，活动编辑期间不作模板替换，不能用重开弹窗偷换“动态更新”验收。

这些 API 依据为既有官方 XML和25.2.3公开元数据及固定示例 (§15)。没有 dxdocs 可调用；本轮官网403不作“不支持”结论。实际热切换/内部窗口覆盖保持 L-Wpf 运行门，禁止反编译供应商或扫描控件内部替补。

### 7.2.1 Wpf API v0.2：模块提供与宿主注入

以下是本模块计划实现的公开 API，namespace 为 Asun.Modules.Localization.Wpf，唯一工程沿 binding，net10.0-windows/UseWPF=true、引用 Core 和本机25.2.3程序集。它不是已经存在的 DevExpress API。模块提供 WpfSurfaceScheduler、GridLocalizationSurface、PlainTextSurface、NativeTextSurface、Dx2523TemplateRegistry、NativeTextRenderer；宿主提供实际 Dispatcher、view、已编译文字目标、scope、资源key映射和自己的业务值投影。没有语言页面/第二选择器，没有 Application.Resources、static Active 或线程文化修改。v0.2补齐普通文本和调度归属，不承诺尚未发布的v0.1二进制兼容。

~~~csharp
public interface IDispatcherLocalizationSurface : ILocalizationSurface {
    Dispatcher Dispatcher { get; }
}
public sealed class WpfSurfaceScheduler : ILocalizationSurfaceScheduler {
    public WpfSurfaceScheduler(Dispatcher dispatcher);
    public ValueTask<SurfaceReceipt> ScheduleAsync(ILocalizationSurface surface, PresentationContext context, CancellationToken ct);
}
public sealed class GridLocalizationSurface : IDispatcherLocalizationSurface {
    public GridLocalizationSurface(string surfaceId, DataViewBase view, ImmutableArray<GridTextBinding> bindings, RuntimeBudget budget);
    public Dispatcher Dispatcher { get; }
    public string SurfaceId { get; }
    public ImmutableArray<ResourceKey> RequiredKeys { get; }
    public ValueTask<SurfaceReceipt> PresentAsync(PresentationContext context, CancellationToken ct);
}
public sealed class PlainTextSurface : IDispatcherLocalizationSurface {
    public PlainTextSurface(string surfaceId, Dispatcher dispatcher, ImmutableArray<PlainTextBinding> bindings, RuntimeBudget budget, int maxOutputChars, IPlainTextHost host);
    public Dispatcher Dispatcher { get; }
    public string SurfaceId { get; }
    public ImmutableArray<ResourceKey> RequiredKeys { get; }
    public ValueTask<SurfaceReceipt> PresentAsync(PresentationContext context, CancellationToken ct);
}
public interface IPlainTextHost {
    PlainTextInput Capture(string targetId);
    NativeTextWriteReceipt TrySet(NativeTextWrite request);
}
public sealed class NativeTextSurface : IDispatcherLocalizationSurface {
    public NativeTextSurface(string surfaceId, Dispatcher dispatcher, ImmutableArray<NativeTextBinding> bindings, RuntimeBudget budget, int maxOutputChars, INativeTextHost host);
    public Dispatcher Dispatcher { get; }
    public string SurfaceId { get; }
    public ImmutableArray<ResourceKey> RequiredKeys { get; }
    public ValueTask<SurfaceReceipt> PresentAsync(PresentationContext context, CancellationToken ct);
}
public interface INativeTextHost {
    NativeTextInput Capture(string targetId);
    NativeTextWriteReceipt TrySet(NativeTextWrite request);
}
public static class Dx2523TemplateRegistry {
    public static DxTemplateCapability Get(GridControlRuntimeStringId id);
    public static ControlledContractResult GetControlledContract(string contractId);
}
public static class NativeTextRenderer {
    public static NativeRenderResult Render(NativeTemplateResult template, NativeTextContract contract, ImmutableArray<string> displayArguments, int maxOutputChars);
}
~~~

API 字段和有效域：

下表输入/结果类型均为本模块的公开不可变值对象，构造参数顺序按字段列出顺序；只有NativeTextContract/NativeTextSlot由Registry内部构造。集合沿§4的ImmutableArray/复制规则，字段未标?不得null；surface持host实例至真实Detach/Close退出，不转静态存储。IDispatcherLocalizationSurface.Dispatcher getter须短同步、稳定、非null，不执行UI/I/O；异常/不合法getter在scheduler锁外映射Failed/LOC-009/ReasonId=invalidDispatcher，不入队。WpfSurfaceScheduler构造器可在组合根任意线程调用，不要求在目标UI线程，必须显式提供合法dispatcher；surface的构造/投影仍仅所属UI线程。

| 类型 | 唯一字段/行为 |
|---|---|
| GridTextBinding | Id:GridControlRuntimeStringId、Key:ResourceKey；只收下面 PlainText allow-list，key 必须零参数；同Id或同Key重复在构造拒绝ArgumentException，保持回执区域与登记key一一对应 |
| PlainTextBinding | TargetId:string、Key:ResourceKey；目标ID与key分别唯一且非空，长度/条数受Core MaxKeyChars/MaxMessages；只消费purpose=PlainText，零参数和typed参数均可，不携带模板合同 |
| PlainTextInput | IsAvailable:bool、DataRevision:long正值、Arguments:ImmutableArray<ArgumentValue>；Capture短同步读取一致业务投影；零参数用Empty，可用时禁止default/null元素。参数类型/次数/长度及nullable全部沿Core.Resolve，不接受任意object或provider |
| NativeTextBinding | TargetId:string、Key:ResourceKey、Contract:NativeTextContract；ID/key唯一，长度/条数受 Core 的 MaxKeyChars/MaxMessages；不接受任意供应商 object[] |
| NativeTextContract | Id:string、Revision:long、Hash:string、Slots:ImmutableArray<NativeTextSlot>；只由Registry内部构造；与 §3.5 的原包 nativeContract 的身份/槽/用途一致；本适配首版限定 allowAlignment=false、formatTokens=[]、每槽恰好出现1次、允许重排。模块随DLL发布固定合同UTF-8原件及hash，不能运行时生成不同合同后复用原hash |
| NativeTextSlot | Index:int、Role:NativeTextRole（唯一enum为 CountDisplay/ValueDisplay/ColumnCaption/TitleSubject）、Kind:ParameterKind固定Text；输入已由宿主量值Owner使用明确 FormatProfile 转成string，模块不换算/舍入。原包用 Text 是这条受控适配合同，不能冒充原生供应商 numeric 槽合同 |
| NativeTextInput | IsAvailable:bool、DataRevision:long正值、DisplayArguments:ImmutableArray<string>、FormatProfileId:string、FormatProfileRevision:long、CultureName:string；Capture 在目标Dispatcher短同步读取一致业务投影；与 context.Snapshot.FormatProfile身份/文化不符拒绝 LOC-011 |
| NativeTextWrite | TargetId:string、BatchId:Guid、ActivityRevision:long、ExpectedDataRevision:long、Text:string；模块渲染后在 TrySet 前复核 context.IsCurrent。此DTO只代表文字目标写入，PlainTextHost与NativeTextHost共用，不携带native模板/供应商object，不引第二套写入协议 |
| NativeTextWriteReceipt | Status:NativeTextWriteStatus（唯一enum为 Applied/Stale/Unavailable/Failed）、Error:LocalizationError?；Applied时Error=null，其余需Error非null，异常映射Failed/LOC-009；TrySet 仅当目标仍存活且DataRevision相符时设置；Stale 不写，区域 Failed/LOC-011，宿主下一次业务刷新重新渲染；不循环重试 |
| NativeRenderResult | IsSuccess:bool、Text:string?、Error:LocalizationError?；Render 验 typed template成功/id/revision/hash/槽数/受限语法，按checked长度先验预算再以InvariantCulture和全部string一次合成。输入中的花括号只作数据，输出不再交供应商格式器 |
| DxTemplateCapability | Id:GridControlRuntimeStringId、NativeApply:bool、ControlledContractId:string?、ReasonId:string；不可变注册结果；枚举中的未知ID一律 false/null/unregistered，不推测槽位 |
| ControlledContractResult | IsSuccess:bool、Contract:NativeTextContract?、Error:LocalizationError?；只接受下面4个精确合同ID，未知为LOC-015；成功内部构造不可变合同，宿主不用自造hash/槽角色 |

所有 constructed surface 必须在所属Dispatcher构造，检查 view.Dispatcher/dispatcher 一致；错误线程为 InvalidOperationException 编程错误。bindings 冻结并复制，不读可变宿主字典。GridLocalizationSurface.PresentAsync 在 UI 线程先 Resolve 所有已登记零参数文本，构造新的独立 GridRuntimeStringCollection/RuntimeStringIdInfo；全部成功且 IsCurrent 后一次给 view.RuntimeLocalizationStrings。部分查词失败则保留原集合并回 Failed；setter已进入后抛异常不声称回滚。模块登记集合为该view资源的唯一写入Owner；宿主原自定义词条须显式加入bindings，不自动Merge或覆盖未知配置。

三个surface构造器显式注入RuntimeBudget，宿主传与service RuntimeOptions.Budget相同的不可变值；不从隐藏scope/全局配置取得预算。构造器按§3.2核合法budget，surfaceId/targetId/资源标识长度<=MaxKeyChars、bindings条数<=MaxMessages、native槽数<=MaxArguments、每合同合法长度边界，并检查显式maxOutputChars<=budget.MaxOutputChars。宿主不得把更宽的独立budget与更窄Core组合；Core的Subscribe/Resolve/回执仍独立核自身边界，不能以宿主注入代替Core验证。Grid ActualRegions用每个已成功登记Id的精确枚举名称（构造时也核其长度<=MaxKeyChars），Plain/Native用TargetId；各自无重复且数目不超过RequiredKeys.Length，批总回执还受Core预算核验。

三个surface的Dispatcher属性在构造冻结：Grid取view.Dispatcher，其余取显式dispatcher；不得按Application.Current或最后活动窗口求值。直接调用PresentAsync时先CheckAccess，错误线程为InvalidOperationException且零目标调用。WpfSurfaceScheduler在排队前要求surface实现IDispatcherLocalizationSurface，且其Dispatcher与构造注入的dispatcher为ReferenceEquals；不符分别回Failed/LOC-009（ReasonId=unsupportedSurfaceType/dispatcherMismatch），ActualRegions=Empty且不调用PresentAsync/Capture/setter。宿主路由器也使用此接口和预登记实例映射，不猜类型/控件树。Core只依ILocalizationSurface，不验证或引用Dispatcher。

PlainTextSurface的bindings冻结顺序即执行顺序，RequiredKeys按绑定生成并保持一一对应；首版同key多目标须拆surface或使用同义独立key，不能让ActualRegions超过RequiredKeys.Length。maxOutputChars显式正int，构造核注入budget上限；每次ResolveRequest还由Core核此界。每批在所属UI线程先核ct/IsCurrent，再逐绑定Capture(targetId) → 核资格/输入 → context.Resolve(new ResolveRequest(key.ModuleId,key.Key,input.Arguments,maxOutputChars)) → 核资格 → host.TrySet(new NativeTextWrite(targetId,context.BatchId,context.ActivityRevision,input.DataRevision,result.Text)) → 核资格；始终使用批Snapshot.FormatProfile，宿主不预格式化Count/Decimal等typed值。IsAvailable=false不读其余字段，回NotSupported/LOC-009；DataRevision/default集合等回执结构非法为Failed/LOC-009，合法参数集合的种类/次数/内容坏沿Core的LOC-005，Resolve用途/预算失败保留其LOC-015/006等typed码，均不调用该目标setter。首次失败/取消/过期停止剩余绑定，已确认Applied的目标保持实际回执，不假称跨目标原子性。

IPlainTextHost/INativeTextHost的TrySet均短同步：核目标存活、ExpectedDataRevision一致，然后只设置宿主已编译的文字属性；Unavailable不写、区域NotSupported/LOC-009，Stale不写、区域Failed/LOC-011，Failed沿宿主有效Error或LOC-009。禁止写编辑器Text/EditValue/Mask/Language/模板/业务值，也不触发业务命令。普通标题、命令、提示用PlainTextSurface；四份受控供应商显示合同用NativeTextSurface。映射可为BarItem.Content、SuperTipItem.Content、BaseLayoutItem.Caption/TabCaption或自有TextBlock.Text；映射Owner须确认该目标是显示而非编辑输入，并为实际AutomationPeer的Name/HelpText设置对应投影，UIA实测另验。setter重入或写后抛异常时当前目标结果未知，回Failed/LOC-009/ReasonId=setterOutcomeUnknown；ActualRegions只列此前确认Applied项，不承诺当前目标原值保留。正常回Applied后若资格已失效，也保留该已写目标诊断，但不继续下一目标；Core仍按冻结逻辑终态处理迟到回执。

普通文本最小接入：§3.1的items.count合成包Load/Create并登记ResourceKey("common","items.count") → 在dispatcher构造PlainTextBinding("statusCount",key)、PlainTextSurface("status",dispatcher,[binding],budget,maxOutputChars,host) → Subscribe；host.Capture返回(true,1,[ArgumentValue.Count(12)])，TrySet对同revision的自有状态TextBlock.Text赋值。CN初始批得到“项数：12”，新ID切TW得到“項數：12”；零参数标题/按钮改用parameters=[]的PlainText key和Arguments=Empty，不能挤进countDisplay等NativeTemplate合同。批Context不能保存供下一次业务刷新使用；已Applied区域的业务值变化由宿主在所属Dispatcher短同步Capture → service.Resolve(scope,typed request) → 核scope仍Ready且ActivityRevision等于解析前观察值、DataRevision/目标存活未变 → 给已编译显示属性赋值。此业务刷新无语言BatchId，不伪造NativeTextWrite或Core呈现回执；若版本/数据不符就不写，等宿主下一次明确刷新。NoChange只为语言落后订阅补批，不是业务刷新总线；语言模块不订阅业务总线。共享Dispatcher中语言交换与业务赋值仍可能相邻发生，宿主不得在检查与setter间await/泵消息，重入setter后的恢复仍按局部失败处理；不承诺跨线程交换和已开始setter原子性。

NativeTextSurface 的 maxOutputChars 为Profile显式正int上限，需不超过该scope Core RuntimeBudget.MaxOutputChars，构造无默认值；宿主组合根传同Profile边界，renderer每个display参数/总输出均不得超过这个值。bindings最多MaxMessages条，所有Slot数受MaxArguments；RequiredKeys由bindings按顺序生成，重复Key在构造拒绝而非去重。NativeTextInput不可用时其余值不读取，区域NotSupported；可用时DataRevision须正、参数数目/角色与Contract逐槽一致、不得default/null，入Render前每个display string再核budget.MaxArgumentChars（越界LOC-006），FormatProfile引用匹配批快照；值原意和舍入仍由宿主Owner负责。

NativeTextSurface 在 UI 线程按绑定 Capture→context.GetRawTemplate→Render→IsCurrent→TrySet，每一步返回后核当前资格；Capture/TrySet必须短、无I/O、无重入业务提交。模块不持有业务SDK/数据库句柄。宿主可把 TrySet 实现为实际 BarItem.Content、SuperTipItem.Content、BaseLayoutItem.Caption 或自己已编译 TextBlock.Text 的 setter；不得把完成Text给 RuntimeStringIdInfo 的 NativeTemplate 或 SummaryItemBase.DisplayFormat 再format。Grid内可用宿主创建的 TotalSummaryItemTemplate 中明确Source的文字投影，模板在编辑开始前固定，切语言只更新Text；不依赖未知供应商模板DataContext。业务值更新由宿主用同一已发布快照/本渲染器刷新文字，语言模块不订阅生产事实总线。

部分target Applied而另一target失败时，SurfaceReceipt.Status=Failed/NotSupported、ActualRegions只列已成功target，GetPresentation沿Core逐surface回执，不假称所有目标原子更新；binding含target全在构造冻结。host.DataRevision不匹配的Stale不增加ActualRegions，恢复为后续新批/业务刷新，最多一次尝试；与Close重入同样不继续写余下目标。

Plain/Native的Capture抛异常映射Failed/LOC-009/ReasonId=captureFailed且不调用当前setter；TrySet抛异常按setterOutcomeUnknown处理。每个adapter生成SurfaceReceipt的SurfaceId/BatchId/ActivityRevision直接取冻结身份/context；成功全部目标时Applied/Error=null，失败必须Error非null。ct已取消或IsCurrent=false时停止，返回Expired/LOC-016或LOC-008（ReasonId=presentationNotCurrent），已确认区域保持；Core已有Superseded/Detached/Expired逻辑终态优先冻结，adapter不猜关闭还是替代原因，不以其返回覆盖Core事实。Grid Resolve/建集合/赋值路径也逐外部返回核资格；setter异常同样Failed/LOC-009/ReasonId=setterOutcomeUnknown，不把已赋集合报未改动。

宿主端口返回的null输入、default参数集合/非法DataRevision、未定义NativeTextWriteStatus或Status/Error组合矛盾均为typed Failed/LOC-009/ReasonId=invalidHostReceipt（已明确的合法参数内容错误仍沿LOC-005/006）。TrySet已经进入时非法回执同样不能证明当前target未写，不加入确认ActualRegions；诊断可标结果未知，且不记录参数原文。合法Stale/Unavailable才保证当前目标不写；Failed可以已有部分文字副作用，不能推导事务回滚。全部目标写入后还应核资格，失效时保留全部确认区域并回Expired，不以“都写过”绕过最后资格核验。

按§4公共空值/错误约定，Wpf结果IsSuccess成功时有效内容非null/Error=null；失败内容null/Error非null。Binding集合不能default/空，surface.RequiredKeys必须非空；constructor非法标识/重复/不在allow-list/非正输出预算为ArgumentException并不给Core登记半对象。NativeTextRenderer.DisplayArguments不得default/null元素，内容/长度错误typed LOC-005/006，错误用途/合同为LOC-015。Core.GetPresentation仅证明adapter报实际setter完成；layout/可见字形/已开原生窗口的资格由真实Wpf验证单独证明。

### 7.2.2 25.2.3逐ID、槽位与文化矩阵

本表是封闭注册表；支持的是下面精确路径，不声称全控件自动本地化。PlainText允许列表为 NoRecords、NoRecordsFound、GridGroupPanelText、FilterEditorTitle、MenuFooterCount、MenuFooterSum、MenuFooterMin、MenuFooterMax、MenuFooterAverage、MenuFooterCustomize、MenuColumnGroupSummaryEditor、GroupSummaryEditorFormCaption、SummaryEditorFormItemsTabCaption、SummaryEditorFormOrderTabCaption、SummaryEditorFormOrderAndAlignmentTabCaption、SummaryEditorFormMoveItemUpCaption、SummaryEditorFormMoveItemDownCaption、SummaryEditorFormOrderLeftSide、SummaryEditorFormOrderRightSide。这些逐ID零槽/零token，由view.RuntimeLocalizationStrings消费；Dx2523TemplateRegistry.Get对此名单返回NativeApply=true、ControlledContractId=null、ReasonId=plainText，表示实例集合赋值路径可用，不表示已开窗口热更新已通过。下面受控模板ID返回NativeApply=false、对应精确合同ID、ReasonId=controlledDisplayOnly；slotRolesUnproven和未知项按表返回。标题/菜单/页签区域只有真实出现且文字实测正确才计呈现覆盖。原生已开窗口缓存不获Applied承诺。

| 精确供应商ID（前缀+列出后缀即完整ID） | 官方原串与可确认槽 | 冻结路径、合同和文化 |
|---|---|---|
| DefaultTotalSummaryFormatString_Count；DefaultTotalSummaryFormatStringInSameColumn_Count；DefaultGroupSummaryFormatString_Count；DefaultGroupColumnSummaryFormatString_Count；DefaultGroupColumnSummaryFormatStringInSameColumn_Count | Count={0}；Count summary值槽0，无format token | NativeApply=false（内部文化/已开刷新无完整合同）；ControlledContractId=dx2523.countDisplay.v1：槽0 CountDisplay/Text/1次；宿主按固定FormatProfile.Count G给display字符串，Render输出到自有文字目标 |
| DefaultTotalSummaryFormatString_Avg/Min/Max/Sum；DefaultTotalSummaryFormatStringInSameColumn_Avg/Min/Max/Sum；DefaultGroupSummaryFormatString_Avg/Min/Max/Sum；DefaultGroupColumnSummaryFormatString_Avg/Min/Max/Sum | 官方字符串分别含值0/列说明1；Avg/Sum族含0:#.##或0:0.##，Min/Max通常0；这不是允许译文修改精度的证据 | 各ID NativeApply=false；ControlledContractId=dx2523.valueAndCaption.v1：槽0 ValueDisplay/Text、槽1 ColumnCaption/Text、各1次、零token；宿主按明确参数格式规则给值与caption，module只拼句 |
| DefaultGroupColumnSummaryFormatStringInSameColumn_Avg/Min/Max/Sum | Avg/Sum含槽0:0.##，Min/Max为槽0；不带列说明槽 | 各ID NativeApply=false；ControlledContractId=dx2523.valueDisplay.v1：槽0 ValueDisplay/Text/1次/零token；文化由宿主固定FormatProfile；不能沿原numeric格式token运行 |
| TotalSummaryEditorFormCaption；TotalSummaryPanelEditorFormCaption | Totals for ‘{0}’；现有XML未把subject来源逐项充分绑定 | NativeApply=false；ControlledContractId=dx2523.titleSubject.v1，仅自有明确标题目标：槽0 TitleSubject/Text/1次；host明确提供标题subject，不猜原生控件参数；原生汇总窗口标题自动热切换不支持 |
| MenuColumnGroupSummarySortFormat | {1} by - ‘{0}’ - {2}；保存XML的Where未保留三槽含义 | NativeApply=false、ControlledContractId=null、ReasonId=slotRolesUnproven；不根据默认文本反猜顺序/排序事实。宿主自有排序命令用普通明确ResourceKey与业务参数合同，不能标为此供应商ID已支持 |
| 其余GridControlRuntimeStringId / 未列出的槽或format | 没有本页固定登记 | NativeApply=false/null/unregistered；注册阶段拒绝，不自动走global localizer或英文回退 |

上述受控合同是本模块定义的显示合同：例如 count三语“项数：{0} / 項數：{0} / Items: {0}”，valueAndCaption为“{1}：{0} / {1}：{0} / {1}: {0}”，titleSubject为“{0}的合计 / {0}的合計 / Totals for {0}”。Avg/Min/Max/Sum含义由宿主传入已批准caption/值身份，不让本模板重新执行统计；需要显式运算名时caption含批准运算标签。没有客户翻译时可先用这些合成包实现验证，生产词条仍由领域审校。Count输入12、en-US格式得“Items: 12”；value字符串1.25与caption长度得到“长度：1.25”；输入caption含{0}仍原样，绝不二次解析。

固定合同原件字节为下面各单行JSON的UTF-8（无BOM/无尾换行，字段顺序按原文，不重新serialize）；这些是外部中立槽语义原件，包nativeContract仍另含§3.5全部预算字段和每槽formatTokens=[]，预算只可收紧，不能改以下语义。Registry内嵌同样字节和SHA-256常量；目录的hash引用该原件，避免包自引用。用户无需批准生成规则或补供应商参数猜测。

~~~json
{"id":"dx2523.countDisplay.v1","revision":1,"slots":[{"index":0,"role":"countDisplay","kind":"Text","minOccurrences":1,"maxOccurrences":1}],"allowReorder":true,"allowAlignment":false,"formatTokens":[]}
~~~

hash：8c5b2c26f8eed68d70f9d4082f57dc21f695aced85ee3fadbebf94125efbe086。

~~~json
{"id":"dx2523.valueAndCaption.v1","revision":1,"slots":[{"index":0,"role":"valueDisplay","kind":"Text","minOccurrences":1,"maxOccurrences":1},{"index":1,"role":"columnCaption","kind":"Text","minOccurrences":1,"maxOccurrences":1}],"allowReorder":true,"allowAlignment":false,"formatTokens":[]}
~~~

hash：f5f05f40d51204a78aca2369bac9a6e8608fb0f93334790adb5125d3721bdfde。

~~~json
{"id":"dx2523.valueDisplay.v1","revision":1,"slots":[{"index":0,"role":"valueDisplay","kind":"Text","minOccurrences":1,"maxOccurrences":1}],"allowReorder":true,"allowAlignment":false,"formatTokens":[]}
~~~

hash：ec38a20cccb58f538e39547dce0d133984b2dff2cc2c0e86de7d618eef8519e6。

~~~json
{"id":"dx2523.titleSubject.v1","revision":1,"slots":[{"index":0,"role":"titleSubject","kind":"Text","minOccurrences":1,"maxOccurrences":1}],"allowReorder":true,"allowAlignment":false,"formatTokens":[]}
~~~

hash：f62cbd4e1ba27817e7ed0722a0cbafef77214715f18a029c16e87a532b60ed46。NativeTextSlot.Role的enum映射到原件lowerCamelCase字符串，Kind始终Text；不把CountDisplay enum拼成不合法的包role。

外部宿主最小接入顺序：`GetControlledContract("dx2523.countDisplay.v1")` 取得typed合同 → 资源包同key的purpose=NativeTemplate/parameters=[]/nativeContract.hash用上述值、slots.role=countDisplay/kind=Text/token名单空、完整预算字段按已采纳Profile → Load/Create(scope含该key) → 构造NativeTextBinding(targetId,key,contract)和NativeTextSurface(surfaceId,dispatcher,[binding],budget,maxOutputChars,host) → Subscribe。host.Capture返回使用scope相同FormatProfile得到的["12"]，host.TrySet在DataRevision仍一致时给所属TextBlock.Text；切TW经新批得到“項數：12”。这样不需要宿主造另一份原生DTO/语言服务；ID/Contract/hash/version错误在查词/Render明确失败，不把SDK未知变用户阻断。

确切依据：25.2.3官方随附Core XML的各 `F:DevExpress.Xpf.Grid.GridControlRuntimeStringId.<上表ID>` 给用途/默认串；本轮定向复读的 SummaryItemBase.DisplayFormat 官方XML只说明格式pattern，不能证明所有槽意义。随附 [GetFooterDisplayText/GetGroupDisplayText/GetGroupColumnDisplayText方法XML](../../../.work/localization-public-surface-study-20260929/followup-sources/DevExpress.Xpf.Grid.v25.2.Core.xml.followup-excerpt.xml) 公开签名为 `(IFormatProvider language,string columnCaption,object value,string columnDisplayFormat)`；它证明可显式传provider的计算入口，不能证明Grid内部调用文化，首版不借它绕过本模块封闭ArgumentValue。固定 [Grid XML](../../../.work/localization-public-surface-study-20260929/sources/DevExpress.Xpf.Grid.v25.2.Core.xml.excerpt.xml)、[SummaryItemBase公开签名](../../../.work/localization-public-surface-study-20260929/public-signatures-3.json) 与实例集合源码见§15；不用未读网页补断言。

### 7.2.3 生命周期、双Host与反证

宿主先Load/Create scope，再在其Dispatcher创建scheduler/surface，service.Subscribe拿token/初始batch；host拥有view/目标/INativeTextHost的实例生命周期，Core拥有订阅和批pin。同一service可用Composite宿主调度器按surface归属转各Dispatcher，但没有全局最后窗口；WpfSurfaceScheduler单实例只服务自己的Dispatcher，路由组合由宿主实现ILocalizationSurfaceScheduler并显式按surface身份登记，不扫visual tree。ScheduleAsync用Dispatcher.InvokeAsync执行短callback并await其实际异步完成；禁止同步Wait/Result。关闭Dispatcher或排队取消先于执行时不调用setter，返回Failed/Expired并确认队列操作未运行；执行已开始则协作检查资格并真实返回后释放。

Wpf API中的Dispatcher为System.Windows.Threading.Dispatcher，Grid相关类型为DevExpress.Xpf.Grid；用 `Dispatcher.InvokeAsync(Func<Task<SurfaceReceipt>>)` 时必须await其DispatcherOperation.Task后再await内层Task，不能在外层Task仅返回内层Task时释放Core pin。仅允许短surface投影，PlainTextSurface/NativeTextSurface自身无异步外部I/O；若同Dispatcher内已经执行也必须排入异步调度，避免Subscribe返回前执行外部setter。Surface实例不能跨scope共享，Core按§5的reference identity登记门核同service唯一归属，无需构造器猜scope；宿主不得跨service复用同实例。多个Host可以各自service+scheduler，或同service的显式路由scheduler，验收优先同service两个scope证明隔离。

窗口Closing先Detach所有token（撤资格），等待service.CloseScopeAsync时保持Dispatcher泵运行；NotDrained显示“关闭未完成”，不能Dispose/清空目标造成运行callback访问已释放对象。窗口真正关闭由宿主等ScopeClosed后执行；超时强关是宿主显式策略，不会被本模块伪报排空。已开始setter可能已改文字，Close只阻止后续写入；报表租约仍固定原语言，最终Stop等其释放。每个批Context、view集合、target/controller仅实例持有；Detach/真实退出后模块释放目标强引用，不建静态强引用表。

验收场景 WPF-HOST-001：同进程Host A中文、Host B英文，各view+独立集合+独立native host。A count=12/B count=7，A切TW仅A变“項數：12”，B保持“Items: 7”；系统CurrentCulture/CurrentUICulture、已有summary事实、选择/筛选和IME草稿不变。两个Host使用同一已编译模块、不同scope，不以两个空窗口替第二消费者。WPF-HOST-002：A setter可控重入/阻塞，B切语言；独立资格与原语言互不串，共Dispatcher阻塞仍可能影响时延。关闭A先赢时旧queued不得写，执行中返回后只能释放/补退出；旧callback不能改新scope/view；B保持可独立Close；报告旧lease在A关闭后仍可Resolve。另断言未登记ID/错hash/错profile/数据revision变化/重复target全部明确拒绝，零业务写入。

此前有限适配设计已由主控接收（规格准备）；本轮v0.2增量已在本页冻结并由本永久原会话完成内容审核，总控仅登记结论，不回标此前版本、不再等待主控技术接收。NativeApply=false是首版有限路径决定，不是客户待决或SDK/许可证门；以后扩大原生自动消费先补同版本公开证据/合同和运行验证。本轮没有实现或运行上述Wpf API。真实25.2.3消费、三语/1920×1080、IME/UIA/DPI、已开窗口文字、layout、有限关闭和两个Host失败恢复按§7.3–7.4及§11.1验收，均未执行。

### 7.2.4 局部失败、重试与原版本恢复

局部失败不回滚Core活动向量。宿主先GetPresentation(batchId)读取各surface逻辑终态、ActualRegions、CallbackExited/ResourcesReleased，显示§7.1局部错误和受影响区域；失败目标可能已经写过，不能据Failed断言所有旧文字保留。先修复缺词/目标存活/数据revision/调度问题，再从GetScopeStatus取得活动Locale/CatalogRevision/FormatProfile，以新OperationId提交完整相同向量RequestSwitchAsync；NoChange不递增ActivityRevision，但为落后订阅安排独立新批。已有Applied区域不强行回滚或冒充需重做；旧operation/batch不可重放复用。每次显式恢复只提交一次，不自动循环切换；仍Failed/Expired/PresentationError或NotFound时继续显示未更新，由操作者/宿主决定下一次新意图。尚在执行的旧callback必须真实退出才能让同surface的新批执行，超时只冻结逻辑回执，不跳过drain。

整套旧版本恢复按顺序：宿主取保留的原UTF-8字节与hash/旧FormatProfile → 新Load operation校验并Loaded+ResourcesReleased → 检查当前必需key的semanticRevision/purpose/参数/native合同兼容 → 新Switch operation发布旧CatalogRevision+明确Locale/FormatProfile → 查看新呈现批。成功恢复仍是新的RequestOrdinal/ActivityRevision，不倒退计数，也不覆写同version异hash；已有报告lease继续原快照。加载缺包或不兼容为LOC-011/003，不用最新版冒称恢复。破坏性语义/模板/RequiredKeys变化须先撤订阅、CloseScope并真实排空，再新Create/绑定；宿主按编辑Owner流程先采用或取消草稿，语言模块不自行关闭/重建活动输入节点。旧资源保留/存储路径和批准发行策略属宿主，模块只执行本页兼容和生命周期合同。

### 7.3 紧凑布局、长度和视觉层级

唯一验证画面为固定1920×1080，扣除 OS任务栏/窗口边框/标题/状态栏后取实际客户区；不改显示设置或另跑分辨率矩阵。记录当前OS实际DPI和有效DIP面积，不把1920个像素当1920 DIP；100/125/150%等历史DPI候选不授权修改用户缩放设置，未在实际环境验证的DPI不计覆盖，产品目标DPI由宿主验收Profile明确。

宿主文字遵循主题字体，正文12–14 DIP、主要动作14 DIP；8 DIP基础间距、同组4 DIP，区域外沿12 DIP。语言适配只提供 layout role 与短/全长 key，不能硬改宿主影像比例。共享状态块优先固定1–2行，简繁/en都用原有容器；按钮min height32 DIP、左右padding12 DIP、自然宽度按三语最长实测文本+padding，不依靠按钮固定窄宽截断。最多两行动作说明，超过时转入紧邻详情/错误块，关键动作文字、负号、单位和原 ID 不省略。

每个 ResourceKey 的紧凑 short key必须和完整 key共享 termId/语义；容器容不下时宿主改用经审校 short key或换行，不以自动Substring/语言判断删字。Grid列头可换行/按任务自适应宽；数值列不因英文标题拉宽到挤掉图像，详情与列选择由宿主已有公开功能处理。非关键摘要允许 ellipsis，但焦点/鼠标/读屏可取得完整文本；重要警告要留原作用范围和恢复动作。

动效沿宿主主题，文字更新不得重排整个数据源；同一dispatcher一批提交已登记区域，避免每 key一个订阅触发数千次layout。Grid保留行/列/选择/筛选对象，Dock保留位置；性能记录包括实际layout/呈现时延，与核心查词分开。无 UI Core不引入主题或动画配置。

### 7.4 编辑、键盘与可访问性

编辑开始由宿主冻结原文本/ParseProfile/约束修订；空串、-、1e、IME组合属于未采用草稿。语言刷新只更新外部label、帮助和错误译文，不写 Text/EditValue/MaskCulture/Language/模板/DataContext/Focus/Caret。保留原输入节点和native IME会话；selection/caret数值只能诊断，不证明可重建IME。Enter组合确认与业务“采用”不能同一次动作触发。

格式 culture 改变也通过独立 FormatProfile 显式 Switch；已有草稿继续原 ParseProfile，不轮流尝试culture。en-US+允许分组的1,234表示1234；de-DE小数输入1,234可为1.234，旧缓冲切语言后不重解析。Infinity/NaN或false-out=0的校验属于参数Owner，语言模块不自动修值。Spin/Date/Mask/Grid原位等变体分别验真实行为；standalone TextEdit成功不外推全部Editor。

AutomationId/命令ID/快捷键身份稳定；Name/HelpText、列头和错误摘要按实际区域更新。原串下划线不能自动解释成助记符。Tab/Shift-Tab/Enter/Esc的业务行为不变；语言切换不偷焦点，助记符冲突按当前菜单范围验。UIA实际事件以 AutomationPeer/读屏验证，不从绑定值变化推定完成。

## 8. 最小 Host 与两个消费者

未来最小无 UI测试入口在 LocalizationHostTests.cs；service由测试明确构造，不靠未定义 factory。下面使用 C#合同形状，未编译；所有 request/result/lease/method均在 §4 定义。fixture内存loader、零UI scheduler和材料文件在唯一测试工程，不是产品依赖。

### 8.1 BCL Exe 与有限验证入口

按 DEV-GOV-010 §3.1，唯一 Core.Tests 工程为 Microsoft.NET.Sdk、TargetFramework=net10.0、OutputType=Exe；只 ProjectReference 到本页 Core 工程和 .NET BCL，无第三方测试依赖。LocalizationHostTests.cs 的 `static async Task<int> Main(string[] args)` 按下面固定用例表执行全部必需断言，私有 Assert.True/Equal 失败抛含CaseId的异常；顶层记录失败/未完成项并返回非零，不能因catch继续后输出0。固定TimeProvider与异步闩锁由BCL实现，异步门使用RunContinuationsAsynchronously；故障观察后必须解除测试自己持有的门并等待真实finally释放。

~~~powershell
dotnet build src/Modules/localization/Asun.Modules.Localization.Core/Asun.Modules.Localization.Core.csproj -c Release
dotnet run --project tests/Modules/localization/Asun.Modules.Localization.Core.Tests/Asun.Modules.Localization.Core.Tests.csproj -c Release -- --case-timeout-seconds 30 --suite-timeout-seconds 180
~~~

这两个参数是测试监护截止点：正整数、上限分别30/180秒，允许调用方缩短；不是模块生产deadline或性能达标目标。Main 以 TimeProvider.System 单调计时设置整套180秒上限，每Case最多30秒；Case内部模块时间仍用可控TimeProvider与§3.2显式deadline。必需Case ID先输出START，完成全部断言且恢复排空后才输出PASS；未执行/跳过/卡住都输出对应ID/原因并非零。入口不接受只跑子集后宣称本合同通过；开发者局部调试可另做过滤，但该模式退出非零且注明Incomplete。

退出码：0=全部必需断言完成且最后Stop真实ServiceStopped；1=断言/异常/未完成/资源未归还；2=非法参数/夹具；3=Case/整套内层截止到期。外层调用进程的有限截止为240秒（包括dotnet run构建与启动）；dotnet build另有120秒外层截止。实施时执行器负责启动/等退出，超时只终止本次测试进程及其自建子进程并记录CASE当前ID/外层超时，判失败非零；不得结束用户其它进程，也不得将强杀当资源正常释放。卡在同步端口时内层可能无法响应，外层必须仍能判失败。`dotnet test` 无报错不能代替这个Exe执行。

| Case ID | 必须完整执行的断言范围 |
|---|---|
| LOC-CORE-001 | §9正常三语、Load/Create/Resolve、两消费者完整业务显示链 |
| LOC-CORE-002 | 空/合法空/畸形字节与JSON、重复字段/条目、审核/术语/大小写/fallback与critical政策 |
| LOC-CORE-003 | 强类型签名、次数、ID/花括号保留、文化/Null、输出N与N+1、Native用途/槽/合同错误 |
| LOC-CORE-004 | 并发switch、同语言换版本/格式、NoChange撤旧意图、ID冲突/窗口淘汰/容量和全向量 |
| LOC-CORE-005 | Load取消/超时/同步阻塞/断连、buffer未退不可复用、DrainUnknown→真实终态 |
| LOC-CORE-006 | 初始订阅/替换批、局部失败、迟到/Expired、Detach、逻辑完成与资源释放分离、getter异常 |
| LOC-CORE-007 | Close/Stop并发与再观察、epoch、未归还计数、Dispose并发read、报告跨关闭、最终全部排空 |
| LOC-CORE-008 | 版本/语义兼容及回退、报告原hash闭包、B/C隔离、长期缓存/订阅/记录归零、诊断故障 |
| LOC-CORE-009 | §3.2各容量正好满/超一及计数overflow、计算slot/预检/发布竞态；§12各测点可记录且无目标时NotEvaluated |

每组绑定§9相关整行及§11额外断言，不以一条Happy-path冒整组完成。性能数值/真正WPF属于另外验证，不因Core Exe返回0变成生产通过。

### 8.2 两消费者正常调用

~~~csharp
ILocalizationService service = new LocalizationService(
    options, memoryLoader, TimeProvider.System, inlineScheduler, nullDiagnostics);
var load = await service.LoadCatalogAsync(
    new CatalogLoadRequest(Guid.NewGuid(), "fixture/catalog-1", payloadSha256, loadDeadline),
    CancellationToken.None);
Assert.True(load.Status == CatalogLoadStatus.Loaded && load.ResourcesReleased);
var create = service.CreateScope(new ScopeCreateRequest(
    "report-worker-01", "en-US", load.CatalogRevision!,
    requiredKeys, false, reportFormatProfile));
Assert.True(create.IsSuccess);
var scope = create.Handle!;
var acquire = service.AcquireSnapshot(scope, new SnapshotRequest("report-01", null));
Assert.True(acquire.IsSuccess);
using (var lease = acquire.Lease!) {
    var page1 = service.Resolve(lease, new ResolveRequest(
        "common", "items.count", [ArgumentValue.Count(12)], maxOutputChars));
    Assert.True(page1.IsSuccess && page1.Text == "Items: 12");
    var change = await service.RequestSwitchAsync(scope,
        new SwitchRequest(Guid.NewGuid(), "zh-TW", load.CatalogRevision!,
            reportFormatProfile, switchDeadline, presentationDeadline),
        CancellationToken.None);
    Assert.True(change.Status == SwitchStatus.Applied);
    var closed = await service.CloseScopeAsync(scope,
        new ScopeCloseRequest("report-finished", drainObservationTimeout),
        CancellationToken.None);
    Assert.Equal(ScopeCloseStatus.ScopeClosed, closed.Status);
    var page2 = service.Resolve(lease, new ResolveRequest(
        "common", "items.count", [ArgumentValue.Count(12)], maxOutputChars));
    Assert.Equal(page1.Text, page2.Text); // scope已关闭，报告租约仍固定旧英文
} // 租约 Dispose 幂等；service此后可释放最后目录引用
var stopped = await service.StopAsync(
    new ServiceStopRequest("host-exit", drainObservationTimeout), CancellationToken.None);
Assert.Equal(ServiceStopStatus.ServiceStopped, stopped.Status);
~~~

参数材料由显式options提供，合成基准夹具例如：单包64KiB、驻留原字节256KiB、100 messages、3 locales、4 catalogs、16 scopes、每scope16 surfaces、64 leases、4 loads、128 operation records、64 presentation records、64 concurrent reads、16 fallback depth、JSON depth16、16 arguments、template/output4096 code units、key128、argument4096、各deadline5s。这里只是功能边界/故障夹具的负载输入，不是默认生产预算或达标数值；大包夹具按消费者Profile换新options/新service，不改现instance。

合成目录：common.items.count 三语为“项数：{0} / 項數：{0} / Items: {0}”，Count签名出现1次；common.text.unavailable为固定应急文案。定义module/key/locale/status/hash都在测试输入，不从平台资源硬编码生成。报告FormatProfile固定en-US Count的G，仅日期用O，无UI元素。

消费者B（报告）按上例跨两页固定租约，不随着scope切TW改变英文；C（诊断工具）另创建zh-CN scope，接收 stable error→key映射并Resolve，其每次显示是C当前snapshot。并发切B到TW时C原语义/语言/计数不变；关闭B不清C缓存引用。真实消费者A在宿主注入Wpf scheduler和已登记Grid/SuperTip/编辑草稿，再执行§7及三语长文本场景，不能以B/C测试证明WPF通过。

所有失败路径用 try/finally 释放租约、Detach tokens并观察Close/Stop；示例为正常断言路径，不表示异常安全代码已写完。Stop为NotDrained时读计数/完成释放再观察，不忙等或同步阻塞Dispatcher。

## 9. 双视角场景与可判定验收

视角一：外部实现者从原字节、精确语言、文本含义到显示输出，找“表面成功掩盖缺资源/错格式”。
视角二：并发宿主/资源所有者从接纳、提交、UI执行到关闭/恢复，找“逻辑回执掩盖仍在运行/混合版本”。
以下为合成例/拟测试，不是已完成运行证据。

| 场景 | 输入与参数来源 → 处理顺序 | 结果/错误、恢复、断言 |
|---|---|---|
| 正常配置/三语执行 | §8完整包/hash、scope.RequiredKeys和FormatProfile → load校验 → create → Count(12)Resolve → scope切TW | 输出项数：12/項數：12/Items: 12各自正确，原Count=12不变；render独立回执 |
| 空输入/空key/零参数/合法空说明 | 零bytes或messages=[]；key=""；无需参数的空数组；allowEmpty可选条目 | 零bytes LOC-002、空messages/未知key LOC-003；空参数合法；空说明Success/IsEmpty，critical空白拒包；不默返空关键按钮 |
| 多候选/部分成功 | 多模块同名Key；同module/key重复；TW缺可选说明有显式en后继；一个surface抛异常 | 不同module隔离；同module重复LOC-002；fallback带requested/resolved/hash；surface失败不回滚其它surface或core，不冒全覆盖 |
| 歧义与畸形包 | JSON同属性两次，"0"与Unicode转义同名；同一合法单段的大小写不同key；BOM/坏UTF-8/未配对surrogate；未知字段 | 严格解析拒重复/非法编码LOC-002；itemsCount 与 itemscount 作为不同合法 key，而 ItemsCount 首字母大写非法；保留旧向量，不自动改名，修包新ID |
| 模板签名与参数改变 | 参数0/1必现，译文仅{1}或{1}{1}；:F0/对齐；ID=0012；值含{0}；输出刚好N/N+1 | 集合/次数不符LOC-004，不以MinimumArgumentCount等于2放行；ID和花括号保留；长度N成功/N+1 LOC-006，先计算后分配 |
| 弱信号/退化/遮挡 | 缺词、低完整度Draft包、字形方框、控件被遮/文本截断、用户自由串控制字符 | 审核状态非法不得Load；缺词按approved链或未解析；字形/遮挡是UI失败，查词成功不关闭门；自由文本不修OCR/Normalize，显示层保原串并安全呈现 |
| 大规模/高并发/资源满 | Profile的messages/locales、并发loads/scopes/leases、callback堵塞；超过每项一单位 | 超输入长度LOC-006/007；slot或固定cache满LOC-013且不接纳；租约固定旧目录不可淘汰；实际队列/缓冲有界，CLR内存另测 |
| A→TW待提交→CN与同语言新版 | A当前CN R1等待gate；新R2为CN；R1迟到；同CN换catalog/FormatProfile | R1 Superseded不能晚发布；R2可NoChange但已撤R1资格；全向量变更Applied/activity++；新请求ID区别重试 |
| 并发重复/ID冲突 | 同OperationId同内容重复switch；同ID不同locale；同scope同SurfaceId重复登记；记录容量超一 | 保留窗口内同操作/终态不二次代次/投影；不同内容LOC-014；修改输入需新ID；淘汰与未知都 NotFound，不无界留ID、不承诺窗口外幂等；调用方不得盲重放 |
| 取消/超时/断连/未知 | loader仍写buffer时cancel/deadline/断连；switch gate前/后cancel；UI闩锁 | loader DrainUnknown不释放buffer或slot，真返回后Cancelled/TimedOut；gate前不发布/gate后Applied不倒改；断连无无限重连，新ID等待原操作结束 |
| 排队/迟到/关闭/回收 | queued批被替换；执行中callback过期；Detach/Close与发布竞态 | 旧队列Superseded；迟到Applied不倒改Expired；资源只真实退出归还；epoch=2拒CreationEpoch=1旧意图；CorePublished先赢保持向量 |
| 部分UI回执/阻塞隔离 | A/B同Dispatcher，A同步throw或闩锁不返回 | throw且退出只A失败，B可调度；不返回时B可能一起停顿。独立timer只能Expired，不能报B已呈现或A已释放；无多进程绕过双宿主要求 |
| Close重复与报告跨关闭 | 并发Close，观察5s到期；报告旧lease存活；后来解除callback闩锁 | epoch仅加1；NotDrained是观察结果可后来ScopeClosed；scopeClosed后lease Resolve仍有效，Stop需最后lease释放；不强清目录 |
| 参数文化与编辑 | en-US允许分组草稿1,234；UI切de-DE/TW；日期O offset；0012 ID | 旧ParseProfile读1234不改成1.234；语言刷新不动草稿/caret/IME；显示FormatProfile变化显式；ID/瞬间/偏移保持 |
| NativeTemplate误用/角色未知 | Plain Resolve用于summary raw key；槽含未批准format；供应商角色未知 | LOC-015/004，不扩大普通语法或二次format；无准确角色ID返回NotSupported，原模板/来源和呈现回执分开 |
| 版本修订/持久化/回退 | 同version异hash；增加可选key；删除requiredkey；V1报告+V2屏幕；重启缺V1包 | 冲突/缺依赖LOC-011/003；安全增量可装载但不自动切；回退新ordinal/activity保旧hash；缺闭包不可复现、不偷用V2 |
| 无UI/第二消费者/长期运行 | B报告+C诊断并发，A可选Grid；反复load/switch/close、log sink失败 | B/C无Shell正常完链；互不串语；Operation表、cache、订阅引用和租约计数最终回归；日志失效可查询权威；长期增长/死订阅为失败 |

## 10. 三语自然术语与长度合同

以下是本模块通用显示用词与对应含义；不是产品判定枚举的重新定义。用于资源验收，行业术语须母语/领域人员审校后标Approved；简繁不能字符机械转换。

| 中文简体 | 中文繁体 | English | 适用语义 |
|---|---|---|---|
| 文本不可用 | 文字無法顯示 | Text unavailable | lookup未取得有效文字 |
| 部分文本未更新 | 部分文字尚未更新 | Some text is unchanged | 核心已发布但部分区域未呈现 |
| 正在关闭 | 正在關閉 | Closing | 关闭已开始尚未排空 |
| 关闭未完成 | 尚未完成關閉 | Close incomplete | 观察期限到而真实排空未证 |
| 项数 | 項數 | Items | 确定非负count显示 |
| 未提交 | 尚未提交 | Not submitted | 无提交意图；不能与未知混用 |
| 结果未知 | 結果未知 | Result unknown | 原Owner未知事实的只读投影 |
| 已接收 | 已接收 | Received | 仅收悉，不等Applied或质量放行 |
| 未评价 | 尚未評估 | Not evaluated | 尚无评价；不等不合格 |
| 无法计算 | 無法計算 | Cannot calculate | 条件不足；不表示量值为零 |
| 取消 | 取消 | Cancel | 撤等待意图；不等底层已停止 |

术语审校输出termId/definition/usage/三语/短全形key/禁止混义/审核者/时间/semanticRevision/长度角色。CI校验合同和字符/长度，母语审校验证自然表达；自动翻译只是Draft候选，不直接Approved。UI文字只说发生了什么/影响区域/如何恢复，不用“智能、完美、一键无缝”等夸大标题。长度限制同时检字串预算和真实布局，不把汉字数当英文宽度，也不能仅用伪本地化证明三语审校。

## 11. 测试落点和恢复夹具

唯一Core.Tests计划按能力建立 CatalogContractTests、ResolveAndRawTemplateTests、ScopeLifecycleTests、ConcurrentSwitchTests、PresentationDrainTests、ReportLeaseTests、VersionRollbackTests、LocalizationHostTests；没有实施时不创建空测试项目或报告。可控loader/scheduler通过显式门闩注入“已接纳/正执行/未返回/迟到/异常/断连”，测试使用固定deadline和TimeProvider，不靠sleep/时序碰运气。

覆盖§9每行：正常、零/满/超一、畸形、重复、多候选、取消前后、未排空、回退和恢复；所有结果、事件序列、引用计数、作用域隔离和旧快照内容均可断言。目录材料immutable且有原字节/hash；同Profile复用既有断言，不因文档改名全跑无关模块。关键字形/IME/第三方popup只能Wpf.Tests在真实1920×1080基线验证，纯C#/模拟dispatcher/HTML不能冒充。

必须额外断言：Create返回typed失败而非不明确异常；creation epoch不随关闭变，CurrentEpoch真递增；同request新语言但旧R1晚到无法发布；NoChange比较全向量；订阅初始批和迟到batch终态闭合；NotDrained后同Close可转ScopeClosed；报告租约有真实Resolve入口并跨scope关闭；held catalog缓存满不淘汰；loader返回前buffer不能回收；diagnostics.TryWrite异常不导致业务写入或停主任务。

### 11.1 Wpf.Tests 有限验证入口

唯一Wpf.Tests工程沿binding，Microsoft.NET.Sdk / net10.0-windows / UseWPF=true / OutputType=Exe；ProjectReference到本页Core/Wpf工程，DevExpress25.2.3沿本机既有Reference，UIA用WindowsDesktop提供的公开Automation API，不下载测试/UI包。WpfHostTests.cs的[STAThread]同步Main创建测试自有Dispatcher和真实宿主控件并启动消息泵，后台协调器用InvokeAsync与显式闩锁投影；不把async Main续体当已保持STA，不在UI线程Wait/Result。双Dispatcher用两个显式STA线程、独立泵/控件，service只一个，组合scheduler按实例登记路由。测试关闭所有自有窗口/线程前解除闩锁、Detach、观察Close/Stop真实归还，最后才Shutdown其Dispatcher；未排空不能输出PASS。

~~~powershell
dotnet build tests/Modules/localization/Asun.Modules.Localization.Wpf.Tests/Asun.Modules.Localization.Wpf.Tests.csproj -c Release
dotnet run --project tests/Modules/localization/Asun.Modules.Localization.Wpf.Tests/Asun.Modules.Localization.Wpf.Tests.csproj -c Release -- --case-timeout-seconds 120 --suite-timeout-seconds 900
~~~

参数为正整数、上限120/900秒，允许缩短；仅限验证进程的观察界，不是客户节拍或生产deadline。外层build截止120秒，run截止1020秒（含构建启动），执行器只可终止本次自建进程，强杀判失败且不称排空。协调器用TimeProvider.System单调计时；每Case START、全部必需断言及资源归还后才PASS。退出码沿§8.1的0/1/2/3；局部过滤、手动项未完成、环境缺失、强杀或跳过均非零并输出CaseId/原因。真正IME/UIA输入需要操作者或公开系统输入工具在运行夹具中执行，不能用合成TextComposition/设置IsComposing标志替代；无人完成交互只能报Incomplete。当前仅定义工程和验证规格，不创建或运行它们。

| 必需CaseId | 操作与可判定断言 |
|---|---|
| WPF-TEXT-001 | 零参数命令/标题/SuperTip及typed Count(12)状态接PlainTextSurface，CN→TW→en输出精确；DataRevision/业务值不变；空参数合法，错种类/用途/超长typed失败且无该目标setter；参数含{0}不二次解释 |
| WPF-GRID-001 | 两view独立集合，逐allow-list ID的实例赋值与实际出现文字分别核；未出现或已开窗口未刷新只记录未证覆盖，不冒全译；Grid对象/行列/选择/筛选/summary事实保持 |
| WPF-NATIVE-001 | 四份合同id/revision/hash/槽/重排及零token；count=12、value=1.25/caption含花括号输出精确；错hash/profile/角色或未知ID拒绝，无原生二次format；四合同原件hash保持 |
| WPF-DISPATCH-001 | 错Dispatcher/未实现归属接口零callback，正确入口CheckAccess；同surface对象跨scope拒LOC-014，不同对象在不同scope可用同SurfaceId；Detach仍运行时拒复用，真实退出后可登记，旧scope迟到不写新scope |
| WPF-HOST-001 | §7.2.3同service双scope、两个完整host+Plain/Grid/Native投影；A切TW、B英文不变，ambient culture不改；独立Dispatcher与同Dispatcher显式路由均核归属，共Dispatcher阻塞时延不能冒隔离性能 |
| WPF-HOST-002 | §7.2.3关闭/重入/阻塞/迟到，双await真实退出与pin计数；旧queued取消先赢零setter，已开始setter可有部分写入；NotDrained不释放controller，解除夹具阻塞后Close/Stop真实完成；报告旧lease仍能解析 |
| WPF-RECOVERY-001 | 三目标第一Applied、第二Stale/Unavailable/写后抛分别注入；ActualRegions只含确认项，不写第三项；修复后新ID同向量NoChange发新批、无自动循环；失败surface按冻结bindings重新投影（已成功目标可重写同文本，不回滚），完整成功surface不冒业务刷新；原包Load+新Switch恢复，activity不倒退；不兼容拒绝/显式重建 |
| WPF-EDITOR-001 | 真实TextEdit/Spin/Date/Mask/Grid原位编辑分别留未采用草稿（含-、1e、0012、1,234）；切语言/显示格式不改输入节点、Text/EditValue/Mask/ParseProfile、focus/caret/selection；实际IME组合中切换后确认，Enter不同时采用业务值 |
| WPF-UIA-001 | Tab/Shift-Tab/Enter/Esc、实际助记符范围和AutomationPeer/读屏核Name/HelpText/错误/列头三语与实际事件；AutomationId/命令ID保持，语言切换不抢焦点；绑定值改变单独不计PASS |
| WPF-LAYOUT-001 | §7.3唯一1920×1080固定视口、三语最长文本/关键恢复文字/单位负号不截断，字体与layout role/short key正确；DPI按当前实际设置记录，不改用户显示设置，OS当前DPI之外的验证未执行就不计覆盖 |

仅软件故障Case可使用受控host setter/闩锁；真实控件显示、IME、UIA与字形不可由模拟替代。WPF-GRID-001对首版明确不承诺的原生热更新输出NotSupported范围，不作为支持项PASS；若产品PageContract将它列必需则对应L-Integration未完整，不能省去。呈现/布局/队列/排空性能仍按§12正式Profile采样，以上有限截止不表示性能达标。

## 12. BenchmarkProfile、预算与诊断

公共分位/失败样本口径唯一沿 [DEV-GOV-010 §3.1](../../01-governance/DEV-GOV-010_实施级规格唯一标准.md)，不另抄第二套nearest-rank算法。模块Profile冻结：ID/修订/hash、.NET/模块/适配器构建标识、目标CPU/RAM/OS/存储、完整输入hash与模板/参数分布、message/locale/fallback规模、冷热/预热/测量/最低有效n、load/resolve/switch调用混合、scopes/surfaces/租约/并发/到达模型、全部RuntimeBudget、deadline、失败注入、目标/来源或TargetPending。

独立阶段测点：有界读取与JSON/模板验证、精确索引热查找、fallback/格式/输出分配、scope gate排队与交换、发布到区域实际呈现、批逻辑终态到真实ResourcesReleased、租约持有及Close/Stop真实排空。单调时钟记录，冷样本新service和自有cache；OS文件缓存未清需实记，不称冷。失败/取消/超时/未排空样本单列，不能只挑成功快样本计算通过。WPF呈现指标与Core查词分开；未排空不得判性能通过。

记录真实CPU/私有字节/托管分配/GC、原字节缓存、load buffers、pin/lease/scopes/surface操作记录计数、队列当前/峰值、订阅强引用、句柄和取消到真实归还。没有消费者目标时NotEvaluated而非达标；无HIL/客户节拍输入不阻断Core方法测量。

诊断字段按§4 Event公开形状，SafeDetails只含path/模块/key引用与计数，不含完整argument/板号/原码/用户文本/凭证。按(module/key/cataloghash/requested/resolved/reason)聚合缺词，聚合本身也受MaxOperationRecords/预算并淘汰，不建无界key字典；DroppedDiagnostics是long饱和计数，溢出不影响请求。Scope/surface ID是身份，不能用翻译文字作日志比较键。

## 13. 六项准备结论与按切片后续门

采用[DEV-GOV-010](../../01-governance/DEV-GOV-010_实施级规格唯一标准.md) §3.1 六项，不由章节存在宣称Ready。2026-10-09主控已内容复核§1–15，接收L-Catalog/L-Runtime及配套L-Tests/Host六项文档规格，准入同步为ModuleCoreImplementationReady；下表保留实现与产品后续资格门。

| 条件 | L-Catalog / L-Runtime 文档准备 | 后续实施与产品确认 |
|---|---|---|
| 1 职责与第二消费者 | §1/2/8明确B报告/C诊断及A视觉宿主；无制程/放行/设备写入；主控已接收 | 真实A/B接入另验，不以规划消费者声称集成通过 |
| 2 精确契约/namespace/Owner | §3–5/本页唯一API列类型、参数/有效域、状态/错误、输入编码/hash、资源Owner和回退；主控已接收 | 平台Schema映射不作为Core外部门；实现必须沿采纳合同 |
| 3 最小无UI构建 | binding精确工程/namespace；§4构造器+端口、§8.1 BCL Exe/build+run/退出码+内外截止；无WPF/数据库/设备SDK；主控已接收 | 实施授权/真实构建执行仍单独进行；本轮不改共享构建或创建测试工程 |
| 4 正常/边界/异常/关闭 | §5/9/11有两视角反例及可判定计数/事件/错误 | 下一实现切片编写并实际执行Core契约/故障测试，不能以本轮自审代跑 |
| 5 性能计划 | §3.2/12冻结预算机制、输入负载/阶段/统计引用、资源与失败归还测点 | 真实消费者Profile数值TargetPending，允许Core诊断测量不判达标 |
| 6 唯一落点/允许禁止/后续门 | binding及§7/8完整最小调用和Wpf/Integration边界 | 产品工程/测试写入仍须逐切片实施授权；执行、审核与验证在本原会话，总控只调度/登记；Wpf真实行为/信任签名/产品数据映射独立门 |

Core三切片保持ModuleCoreImplementationReady（规格）；L-Wpf此前有限适配设计已由主控接收（规格准备），本轮v0.2增量已由本永久原会话完成内容审核，总控仅登记，不另等技术接收。它不属于无UI Core，未授产品ImplementationSpecificationReady。L-Wpf真实25.2.3消费、三语/IME/UIA/呈现/有限关闭验证仍未执行；L-Integration仍PreparationIncomplete，明确只表示§13.1具体宿主资源/产品接线、发行/存档政策及真实验证门未落实，本模块当前架构全部能力的软件设计已闭合。技术方案不再写“开发者以后任选”。本页现有资源format/raw/并发/恢复能力全部保留，不以缩小首片替代整模块完善。L-Wpf设计沿§7.2.1–4封闭公开实例、普通typed文字和受控模板路径，NativeApply=false是明确限制，不把未证原生popup更新和Editor变体冒充支持；L-Integration的各项剩余门仅阻相应用途，不阻无UICore。没有本轮代码、性能、WPF、真实HALCON、HIL或生产验收结论。

逐切片结论（Core既有规格接收保持，Wpf增量内容审核在本原会话完成；不是运行通过）：

| 切片 | 条件1/2/3 | 条件4/5/6 | 当前门及真正外部输入 |
|---|---|---|---|
| L-Catalog | 职责/消费者、独立 JSON/loader/typed 结果、无 UI 工程/构造入口已给出 | 严格包/hash/重复/取消/缓冲排空断言、load 测量计划、唯一落点已给出 | ModuleCoreImplementationReady；已接收规格，不依赖客户词条或平台Schema才可实现合成目录Core；实施授权/代码验证另行 |
| L-Runtime | 无 UI B/C 消费、scope/格式/租约/投影全部 API 与 Owner 已给出；沿同一 Core | 并发/ID窗口/关闭/回退/第二消费者断言、阶段/资源测量、工程边界已给出 | ModuleCoreImplementationReady；依L-Catalog；消费者实际Profile冻结前允许诊断测量，禁止判性能达标 |
| L-Tests/Host | 测试真实能力覆盖、端口形状、B/C 最小调用及测试工程已给出 | §8.1 BCL Exe用例/退出码/内外截止、故障闩锁/计数断言、合成预算/BenchmarkProfile、禁止Shell范围已给出 | ModuleCoreImplementationReady（配套验证规格）；无需待选测试包，build/run未执行 |
| L-Wpf | §7.2.1–4明确模块Wpf API、PlainText/受控槽、预算/Dispatcher注入与封闭拒绝、独立Wpf工程；可选Wpf适配不属于无UI Core | §7/9/11.1覆盖双Host、紧凑三语/编辑/IME/UIA/逐区域失败/恢复、STA有限入口及呈现性能 | 此前有限适配设计接收保持，本轮v0.2增量已在本原会话完成内容审核，总控仅登记。NativeApply=false不承诺原生自动模板/已开窗热更新；真实25.2.3消费、三语/IME/UIA/呈现/有限关闭验证均未执行，仍须实际验收 |
| L-Integration | 本模块对宿主的API、输入/Owner、报告闭包和恢复边界设计已闭合；平台DTO/存储/信任不进入Core | 具体A/B/C宿主提供资源、配置、页面/端口及存档/发行接线并完成真实验证；不由本模块猜产品事实 | PreparationIncomplete仅指产品集成资格：§13.1逐项列明资源审校、产品实例映射/接线、发行信任、报告保留输入、消费者Profile和运行验收；无本模块内部待补软件设计，不阻Core |

DevExpress/AsunImage 安装、兼容性或许可不列外部门；HALCON 非视觉事务不适用，Core 不新增视觉桥。真实样本/客户节拍缺失仅阻工业输出和性能资格，不阻合同/预算机制实现。

### 13.1 本轮完整范围核实与剩余Owner（2026-10-11）

本永久原会话按当前批准的§1.1完整能力走查，不只检查首个Core切片。新增普通PlainText零/typed参数投影、可执行Dispatcher归属、surface实例登记/真退出后复用、显式预算输入、局部写后异常、单次新批重试/原包恢复、有限STA验证入口，均已入唯一正文。按外部实现者接入和关闭/迟到两轮静态反证，本模块当前架构全部能力的软件设计已闭合，没有留给普通程序员补猜的算法、参数、错误或生命周期决定；内容审核在本永久原会话已完成，总控仅登记完成结论，无额外技术审核/接收门，不表示已有实现。L-Integration未完整没有本模块内部的软件设计欠账；以下是具体宿主和产品实例必须提供的输入、接线与资格，不能统称客户物理外部门：

| 剩余范围 | 唯一责任Owner、交付与准入影响 |
|---|---|
| 模块代码、发布及真实验证 | 本模块原会话在实施授权后沿binding实现Core/Wpf和§8.1/11.1验证；实现/正确性/呈现/资源/性能均待执行，不因本轮文档闭合判PASS |
| 宿主资源与领域审校输入 | A视觉/测量、B报告、C诊断各宿主的资源Owner/领域与母语审校Owner提供实际原包字节/hash、全量RequiredKeys、三语Approved词条/关键恢复文案及semanticRevision；参数Owner提供完整FormatProfile规则和数据revision投影。§3/4已定义格式/校验，缺的是产品资源和批准事实，不是模块算法；仅阻相应宿主完整文字覆盖与领域使用 |
| 产品实例配置、软件接线与接入设计 | A/B/C各宿主组合根Owner提供实际平台DTO到§3/4字段的映射、SourceRef到loader的受控来源、RuntimeBudget/初始locale、scope/Dispatcher/目标绑定与scheduler路由；A页面/编辑Owner绑定唯一语言入口、ParseProfile/草稿采用取消和恢复动作，宿主持久化Owner接语言偏好。模块步骤/端口已在§4/7/8确定，尚需完成的是具体产品实例的映射/页面/持久化接线设计与实现；不得当作本模块内部欠缺或客户物理门，也不据未指定产品字段扩Core合同。只阻相应产品集成 |
| 发行信任与来源授权输入 | 产品发行/安全Owner提供批准发行者策略、可信公钥/签名及来源授权材料，并在宿主loader前置适配中完成实际校验后才按§4.1返回完整读取回执。Core的内容hash不冒充发行者身份；策略/凭证/校验接线未落实仅阻相关生产发行，不阻合成目录的软件验证 |
| 报告存档与原版本恢复输入 | B报告/产品存档Owner确定保留期、存储位置/权限、原包hash与事实闭包关联及缺失处置，并接实际存档/读取端口；模块的固定lease、闭包内容、旧包Load/兼容检查/新Switch及缺版本失败已在§5/6/7.2.4确定。缺的是产品政策、存档接线与实际可取回原件，不是模块恢复软件设计；只阻相应报告耐久/重启恢复资格 |
| 消费者Profile与真实资格 | A/B/C实际消费者/客户验收Owner提供真实资源规模、负载/并发、机器/当前DPI和性能/节拍目标；本模块原会话在实施授权后执行§8.1/11.1/12，宿主Owner验实际产品接线和现场覆盖。当前编译/Core与Wpf运行、真实25.2.3呈现/IME/UIA/关闭、性能和现场均未执行；缺输入或未执行只阻对应运行/性能/现场资格，不把有限测试截止冒称客户目标 |

完整范围的软件设计核实与内容审核在本原会话已完成；产品整体仍DesignReview/Prep，L-Integration保持PreparationIncomplete（仅具体产品输入/接线与资格）。Core三切片和既有有限Wpf设计接收保持，Wpf增量无需主控技术接收。本轮不扩非目标，不把未证原生热更新转成自动支持，不新增依赖安装/许可证门；上述剩余门不阻无关Core。总控只串行登记状态与维护共享导航，本会话不写共享记录或其它模块。本次仅核本处及状态一致文本，既有合同hash、Core和已通过验证未重审或重跑。

## 14. 外部实现者自审与跨文件接收项

从零宿主按§8依次Load/Create/Acquire/Resolve/Switch/Close/lease.Dispose/Stop，任何domain失败都有typed结果；从关闭与租约持有反推资源不会提前释放；从相同语言不同版本反推全向量/activity revision不会混用；从缺词与原模板反推fallback不会掩格式/用途错误。以上是静态走查，实际断言到唯一测试工程实施。

本轮外部宿主视角关闭：Create 返回值与失败码不相容、报告没有真实 Resolve 重载、格式配置键不明确、JSON 文本与审校映射不闭合、示例状态类型无定义、原模板误用普通格式路径。并发/资源视角关闭：两个 immutable epoch 比较、NotDrained 永久缓存、Dispose 同步等 read、逻辑区域完成冒资源释放、迟到 Applied 覆盖超时、初始订阅突破待执行批上限、历史ID/控件墓碑无界保存、同步未知 loader/scheduler 阻塞公开返回。这里的“关闭”仅指指导语义缺陷已修正，须由未来测试验证实现。

本次接收后增量反证：外部宿主必须能从§7.2.1/2取得模块提供的固定合同，按相同hash构造包，再以实际Dispatcher/view/host接入；不能让宿主反猜numeric模板角色或修改ambient culture。对未知ID、错模板hash、错误profile/数据revision，保留旧文字并给typed失败；对实际setter局部失败，ActualRegions只包含已写区域，不能假原子回滚。并发关闭视角核Dispatcher外层Task已返回但内层callback未退的反例，只有双await和Core finally才能释放pin；关闭先赢/重入/迟到都不能继续余下旧setter；诊断/报告旧租约不污染另一个Host。首版NativeApply=false限制与模块受控显示路径均为明确设计，未把内部方案转外部门。

2026-10-11两轮静态自审：外部宿主从零接入PlainText零参数/typed Count、Grid与四份Native合同，输入→批快照→目标revision→实际回执→单次恢复顺序可落地；未通过解析不调用setter，写后抛异常结果未知而不冒保留原值。关闭视角核错Dispatcher零callback、同service双scope抢同实例拒绝、Detach未退出不能复用、真正排空才清引用、双STA显式路由、Close/重入/迟到冻结回执。修正了构造器缺预算输入、重复key“去重”与唯一约束矛盾、NoChange不能刷新已Applied业务值及DPI不能改用户设置的问题。全部是规格静态核对，没有运行未来测试；文档本地链接/表格、JSON原件hash和API示例一致性定向检查仅证明文档内部一致。

仅主会话可串行处理的跨文件项：旧PKG-003/SM-003/040和原C-05关于语言政策/包格式/正式承载引用应映射本页v0.2；旧资料“无统一包格式”“D1/D2待冻结”“scope StopAsync”“API v0.1”不能与本页作为并列活动权威。当前架构末尾若仍有“需确认AsunImage是否含算子”或要求非视觉适配器核HALCON的通用旧句，应由主会话按最新AGENTS修正；本模块不写这些文件，不把此冲突转Core依赖阻断。


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

## 15. 来源、版本、实际读取与采用范围

来源只作证据，本页已写齐实现步骤；程序员不需要进.work或会话补参数。已有资料版本/输入未变，复用其固定原件，不重复下载全仓。下表“本轮联网/新增研究”指2026-10-09既有研究；2026-10-11只复用这些证据和公开setter/输入事件签名，不重复联网或下载。下列测试是阅读源码，未运行。

| 依据 | 本轮实际读取/固定身份 | 可迁移强项、局限和正文落点 |
|---|---|---|
| .NET10 runtime | v10.0.0，commit 60629d14374c56f1cb51819049ad1fa529307f8d；本轮联网GitHub tag/commit核同identity；MIT | 复用随附System.Text.Json/CompositeFormat，不复制runtime内部算法或引新依赖；§2/3/5 |
| ResourceManager / CompositeFormat 源码与测试 | 复读固定[ResourceManager源码](../../../.work/localization-method-study-20260929/sources/runtime-resource-manager-api.source.cs) GetResourceSet缓存段，[资源测试](../../../.work/localization-method-study-20260929/sources/runtime-rm-tests-final.source.cs) EnglishResourceData/CultureResourceData；[CompositeFormat](../../../.work/localization-method-study-20260929/sources/runtime-composite-api.source.cs) 与 [测试](../../../.work/localization-method-study-20260929/sources/runtime-composite-tests-final.source.cs) MinimumArgumentCount | 缺key=null与空串分离、父缓存误判、最大index+1非签名；不读内部segments做公开API。依赖为.NET随附CoreLib；测试源码xUnit，不引资源序列化/图片依赖；§2/3.4 |
| 本轮新增JSON定向联网研究 | 同runtime固定commit的 [JsonDocumentOptions.cs](https://github.com/dotnet/runtime/blob/60629d14374c56f1cb51819049ad1fa529307f8d/src/libraries/System.Text.Json/src/System/Text/Json/Document/JsonDocumentOptions.cs)、[TryGetProperty源码](https://github.com/dotnet/runtime/blob/60629d14374c56f1cb51819049ad1fa529307f8d/src/libraries/System.Text.Json/src/System/Text/Json/Document/JsonDocument.TryGetProperty.cs)、[JsonDocumentTests.cs](https://github.com/dotnet/runtime/blob/60629d14374c56f1cb51819049ad1fa529307f8d/src/libraries/System.Text.Json/tests/System.Text.Json.Tests/JsonDocumentTests.cs) duplicate属性/deep nested/escaped与AssertDuplicateProperty实际段 | AllowDuplicateProperties默认true，false抛JsonException；测试含"0"/Unicode转义同名。直接用.NET10公开严格选项而非重写parser；未审整个JSON库、未运行上游测试；§3.1/5.1/9 |
| WPF源码/官方API | 固定v10.0.0 commit 72ca82c7a0f57eb8d0168246468b9cc1a6c14a5a，MIT；既有来源[固定说明](../../../.work/localization-method-study-20260929/source.md)和[source manifest](../../../.work/localization-method-study-20260929/sources.json)；FrameworkElement.Language/BindingExpression实际采纳段沿用 | Language继承/AffectsMeasure，ConverterCulture和编辑transfer不能等同宿主语言或IME安全；只Wpf适配依赖WindowsDesktop，Core不依赖；§7 |
| DevExpress25.2.3官方随附XML/公开签名 | 本轮复读[公开签名](../../../.work/localization-public-surface-study-20260929/public-signatures.json)、[SuperTip签名](../../../.work/localization-public-surface-study-20260929/public-signatures-8.json)和[来源说明](../../../.work/localization-public-surface-study-20260929/source.md)。元数据assembly25.2.3.0；SuperTip Core DLL证据hash 4ddb441ae3d22b584bad608c8f3e621fd6a182f43cb8134cf5067b21b23360b5 | 实例集合/公开setter、Bars/Dock/SuperTip可接；未知native popup/IME覆盖不可推。2026-10-09官方Grid/SuperTip网页403，无dxdocs/匹配25.2技能可调用；用官方随附资料，不查授权/内部；§7.2 |
| DevExpress GitHub实例资源例 | commit b0ee49c5c8c9bb9ad01520ecdbebcb83bb96f62e，[实例代码](../../../.work/localization-public-surface-study-20260929/sources/dx-runtime-code.cs)、XAML/csproj/license沿既有固定manifest | GridRuntimeStringCollection→RuntimeStringIdInfo→view属性；单窗口/一个词条，无已见功能测试；net8/24.2引用不搬入.NET10/25.2.3。as-is/EULA指向非MIT，不复制整个项目；§7.2 |
| 对照global localizer例/标准控件SuperTip例 | global例commit970e87163f05239023b1e786d862d98eee694338；SuperTip最后含源码commit0c534a44e832d2e3af6bbf9defb82ab23e28e7b4；[SuperTip代码](../../../.work/localization-public-surface-study-20260929/sources/dx-SuperTipFromCodeForStandardControls.xaml.cs) | global Active只单窗口不证同进程隔离，排除；SuperTip标准承载公开用法可借，旧net6/22.2/无行为测试不证25.2.3运行；原许可同as-is/EULA，不改变用户已批准依赖；§2/7 |
| 专业指导与只读参考 | [040](<../../shared-modules/guidance/05-ui/DEV-UI-040_WPF+DevExpress Design System开发指导.md>) §13，原catalog Schema和[AsunControl快照](../../references/project-snapshots/AsunControl/20261004/original)的InvariantCulture/ComponentResourceManager有限证据 | 复用scope/编辑/报告/模板/排空思想，明确升级到本页独立契约；旧WinForms/.NET8/产品文案不变成Core API |
| HALCON26.05 / AsunImage | 非视觉语言事务，明确不适用 | 没有图像输入、ROI、训练/拒识或HALCON资源，故本轮不查无关operators，不重复核cv2覆盖、不直接引用halcondotnet.dll、不扫描内部。过去笼统“已核字符/图像算子入口”不作为本轮实际核对证据 |

本轮研究是定向能力选择和代码/测试阅读，不以官方例的README/星数/营销或截图证明生产能力；未保存新的外部快照，新增JSON证据用固定commit链接可复核，既有证据/原件保持只读。
