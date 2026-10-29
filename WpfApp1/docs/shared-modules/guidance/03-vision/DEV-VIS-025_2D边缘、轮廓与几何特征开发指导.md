# 2D边缘、轮廓与几何特征开发指导

- 文档 ID：`DEV-VIS-025`；版本：`1.4.0-map`；状态：`DesignReview`；日期：2026-10-10。
- 本页维护孔/开口等应用消费约束和原方法导航。完全独立模块的算法、参数、公开API、资源、UI、工程与逐切片准入唯一在[IM-025 features-2d](../../../independent-modules/features-2d/DEVELOPMENT-GUIDE.md)。
- Metrology对象/实例能力独立归[IM-036 metrology](../../../independent-modules/metrology/DEVELOPMENT-GUIDE.md)；具名量值与测量资格由该唯一指导维护，高级方法设计见IM-036 §19。DEV-MET-031仅作研究与应用导航；本页不将这些能力并入features-2d，不创建第二契约。
- 平台范围见[平台设计基线](../../../00-baseline/PLATFORM-DESIGN-BASELINE.md)。本页映射、文档接收和原研究不是实现或现场资格。

## 统一实施规则

先按对应独立模块唯一指导冻结输入/输出、方法、Owner和范围，再实施。领域身份、工艺公差、完整候选图、质量接受与事实提交归原应用；模块结果、UI及诊断不能获得隐含放行权。HALCON 26.05经项目AsunImage的ImageLibDotNet.cv2直接调用，算子语义查[项目内手册](../../../../halcon算子手册/operators/)，不核算子存在、库兼容性或授权。

## 1. 通用算法选择流程

具体方法派发与参数建议按[IM-025 §2](../../../independent-modules/features-2d/DEVELOPMENT-GUIDE.md#2-依赖权威与方法选择)，应用提供明确观察角色、原分辨率输入、有效支撑、坐标/单位和资格Profile。参数建议是离线候选，显式采用为新草稿；不得失败后换极性、选更接近名义值的边或隐式训练直到通过。

## 2. HALCON 使用规则

模块Core不泄漏原生句柄；真实适配按[IM-025 §7/附录A.3](../../../independent-modules/features-2d/DEVELOPMENT-GUIDE.md#7-端口装配与版本)。C#参数类型/重载/封送歧义只影响对应适配绑定，不重开薄封装能力审核。旧版25.11原件仅为研究来源，实施语义以26.05及唯一模块指导为准。

## 3. 鲁棒性要求

完整支撑、缺slot、原索引、退化和稳定性唯一按[IM-025 §3/6](../../../independent-modules/features-2d/DEVELOPMENT-GUIDE.md#3-请求坐标参数与输出)。空响应、合法无候选、歧义、截断、无效来源和未执行分别消费；原残差不替代缺陷证据或计量不确定度。

## 4. 性能要求

方法预算/峰值/阶段、冷暖与失败样本的方法唯一见[IM-025 §12](../../../independent-modules/features-2d/DEVELOPMENT-GUIDE.md#12-benchmark方法与可观测性)。应用绑定实际帧、局部窗口、负载和目标来源；没有实测不声称最快或达标。取消通知不证明原调用或帧租约已经归还。

## 实施级关联功能

[FS-008](../12-function-specs/FS-008_Subpixel_edge_extraction.md)和[FS-009](../12-function-specs/FS-009_Ellipse_circle_fit.md)保留平台功能绑定；它们消费唯一模块方法，不另外选择算子或API。Metrology功能单独接IM-035。

<a id="edge-fit-pipeline"></a>
## 5. 亚像素边缘到有类型特征的实施链

### 5.1 按证据选择固定方法

[IM-025 §2.2](../../../independent-modules/features-2d/DEVELOPMENT-GUIDE.md#22-halcon2605固定派发)已冻结E1/E2、灰度/颜色XLD和单primitive路线。宿主先选观察能力与输入计划；Metrology多对象/实例调用单独依IM-035，不把其随机搜索结果当显式卡尺全集。

### 5.2 卡尺方向和参数映射

方向、半长、实际中心与参数域唯一见[IM-025 §3.2–3.3](../../../independent-modules/features-2d/DEVELOPMENT-GUIDE.md#32-几何支撑和方向)。应用的全长规划须先换成该契约的半长，观察角色/材料内外关系由应用定义，不从拟合法向符号推导。

### 5.3 正常执行与候选关联

按[IM-025 §6.1–6.2](../../../independent-modules/features-2d/DEVELOPMENT-GUIDE.md#61-提取与分段)消费完整原观察与显式拟合支撑。局部唯一关联不替代产品全局分配；全局图由应用形成并调用[IM-037 assignment](../../../independent-modules/assignment/DEVELOPMENT-GUIDE.md)。目标不得因模块无候选而从必检集合消失。

## 6. 圆、椭圆和多实例拟合

### 6.1 拟合前与拟合后

[IM-025 §6.2–6.3](../../../independent-modules/features-2d/DEVELOPMENT-GUIDE.md#62-显式拟合支撑)唯一规定点/秩/跨度、单一支撑、固定拟合与稳定性证据。数学最低点数和低残差不授工业资格。近圆椭圆轴角不作可靠装配方位；鲁棒处理不消除应用需检查的毛刺/缺口。

### 6.2 Metrology结果不是置信概率

该能力按[IM-035唯一指导](../../../independent-modules/metrology/DEVELOPMENT-GUIDE.md)逐切片接收。应用把score、残差、支撑资格和工艺接受分开，不把原生score称合格概率；原找边、实际使用点和模型轮廓是不同证据。未建立逐slot映射时不能推导缺slot分布。具体对象/实例API及算法不在本页定义。

### 6.3 可判定的挑战集与性能

模块断言唯一见[IM-025 §10–11](../../../independent-modules/features-2d/DEVELOPMENT-GUIDE.md#10-具体样例与预期)：方向、基数、有效支撑、原索引、短弧/近圆、映射、取消/迟到和真实归还。应用另验目标身份、被测量与完整必检义务；不能用Core模拟结果代替真实视觉或标准件资格。

<a id="edges2d-association-method"></a>
## 7. 有向边缘、边对、轮廓关联与拟合输入的完整方法

本节保留原制程消费导航，模块处理步骤唯一按[IM-025](../../../independent-modules/features-2d/DEVELOPMENT-GUIDE.md)。旧研究、算例与审核原件保留§7.10–7.11，不构成新的实施权威。

### 7.1. 方法入口与输出责任

PG002孔口、PG013钢网开口冻结输入、物理观察角色、必检对象、定位和质量规则；模块输出原观察/候选及诊断。具名量值和全局分配分别归IM-035与IM-037/宿主，不通过按钮或方法Profile向模块暗加工艺责任。

### 7.2. 有向边和边对：选择路线而非试到通过

#### 7.2.1 三种固定入口

单边/边对与预登记独立诊断按[IM-025 §2.2/6.1](../../../independent-modules/features-2d/DEVELOPMENT-GUIDE.md#22-halcon2605固定派发)。完整pair空结果不区分物理无边/单侧边；只有显式单边入口实际返回才消费其位置/幅值。不得无响应后换阈值或补名义第二侧。

#### 7.2.2 一次显式卡尺处理

[IM-025 §3/6与附录A](../../../independent-modules/features-2d/DEVELOPMENT-GUIDE.md#3-请求坐标参数与输出)维护方向/基数/搜索次序、两端身份及显式PairFirst/PairSecond/PairCenter选择。中心是明确派生点，应用不能将其冒充独立实采边。

### 7.3. 完整profile与提边支撑

[IM-025 §3.2/A.3](../../../independent-modules/features-2d/DEVELOPMENT-GUIDE.md#32-几何支撑和方向)定义参与包络与方法资格。应用供给实际处理输入的完整有效域及预处理来源；点本身在mask中不证明整个投影/插值支撑有效。缺口不填0或补洞再称观察到。

### 7.4. 非等距/已标定坐标中的点、方向与法向

物理用途由应用冻结坐标与映射资格，逐点映射支撑后再核目标空间primitive并拟合，见[IM-025 §3.2/6.3](../../../independent-modules/features-2d/DEVELOPMENT-GUIDE.md#32-几何支撑和方向)。不只映射端点或圆心/半径；非线性变形后原像素primitive不自动保持。材料法向仍由产品观察语义确定。

### 7.5. 有序XLD到单primitive及原采样身份

#### 7.5.1 先分域，再分段，再局部关联

分段/原索引/重复坐标与边界内区按[IM-025 §6.1–6.2](../../../independent-modules/features-2d/DEVELOPMENT-GUIDE.md#61-提取与分段)。应用消费明确Exact/Unknown，不用最近点强配补原身份；跨parent、跨窗或断点不拼成完整轮廓。

#### 7.5.2 拟合输入与采样权重

完整InputPoints、原来源及有限候选按[IM-025附录A.2](../../../independent-modules/features-2d/DEVELOPMENT-GUIDE.md#a2-原证据候选事件与结果)。应用保留原缺陷支撑，不能将抽样、内点或显示LOD称为全部实采点。

### 7.6. 拟合残差、支撑覆盖与稳定性分开

唯一数值定义见[IM-025 §6.3](../../../independent-modules/features-2d/DEVELOPMENT-GUIDE.md#63-输出模型残差和稳定性)。残差、覆盖、参数敏感性与计量不确定度分别报告；显示拟合轮廓不是新增实采覆盖。失去资格时原观察留存，应用决定补证或人工复核。

### 7.7. Metrology对象、实例、原边及world结果

Metrology的算法、公开API和实际坐标语义由[IM-035](../../../independent-modules/metrology/DEVELOPMENT-GUIDE.md)唯一接收；本节保留其应用消费约束，不能由本页启动features-2d内的Metrology实现。

#### 7.7.1 公共返回的明确限制

按原对象/实例分别消费原边和实际使用点，返回顺序不代表质量或跨帧身份。无逐slot来源时只保对象/实例级支持，不推逐slot缺测或连续缺弧。依赖这种来源的用途改用已冻结的显式采样能力，而不是补造索引。

#### 7.7.2 解析步骤

宿主保持请求对象ID与模块对象/实例结果关联，零结果、上限、未完成和随机搜索完整性分别处理。参数、score、原找边和模型轮廓不得拍平混成一套点集；ReachedLimit不能被应用用于证明没有更多候选。实际字段与类型从IM-035取得，不照旧研究临时造API。

#### 7.7.3 坐标和输出类型

应用核图像/world/plane/scale、单位和资格引用；不能因模型参数已为mm便认为原找边、显示轮廓或所有阈值也为mm。原研究中distance_threshold及used_edges在world/scale下未证部分仍需IM-035接收目标版本依据/实际读回，不能猜倍率或把显示点当物理残差。二维平面不覆盖任意孔壁高度。

### 7.8. 两个无UI消费者闭环

#### 7.8.1 PG002钻孔孔口

应用固定原观察角色、独立板定位、必检孔口及完整性→调用IM-025冻结方法→消费原支撑/歧义与目标空间候选→形成全局关联图交IM-037→IM-035/宿主绑定既有被测量→产品接受与提交。不得重新定位到名义中心消除钻偏，拟合失败不删除目标；两圈反射和缺一侧保留未决原因，不补标准圆。补拍/方法换版由原应用发起，模块不发设备命令。

#### 7.8.2 PG013钢网开口

应用冻结钢网身份、面、清洁状态及开口意图→调用IM-025保留连续侧边/倒圆角原支撑→逐点目标映射与primitive资格→全局关联→已定义量值→三态通/遮/未知及清洗用途。使用后可见透光边不能自动称制造外边；局部宽度不证明全长或完整面积。污染双边不得挑更接近名义宽的侧；前后清洗是不同证据，原维护Owner控制清洗/复测。两应用不读取对方VM或私表。

### 7.9. 参数来源、预算及错误恢复

应用冻结观察角色、必检范围、坐标资格和消费者Profile；模块字段/域/来源与恢复唯一见[IM-025 §3–5](../../../independent-modules/features-2d/DEVELOPMENT-GUIDE.md#3-请求坐标参数与输出)。来源失效不换latest；取消/超时/释放失败保留原Owner。参数建议不按工艺公差选择最容易合格的候选。完整性未知不当PASS，实际归还未知不当性能通过。

### 7.10. 验证计划与当前证据

当前模块测试与六项规格定位见[IM-025 §11/17](../../../independent-modules/features-2d/DEVELOPMENT-GUIDE.md#17-逐切片六项定位自审与当前状态)；Metrology单独依IM-035。原E25-V1～6仅保留来源导航：有向边的信息边界、完整支撑/边界、原索引/拟合、Metrology坐标、双应用隔离及钢网目标空间拟合；其真实质量门仍须对应切片实测。

既有研究原件：[recommendation](../../../../.work/edges2d-association-method-study-20260929/recommendation.md)、[source](../../../../.work/edges2d-association-method-study-20260929/source.md)、[sources.json](../../../../.work/edges2d-association-method-study-20260929/sources.json)、[公式原图](../../../../.work/edges2d-association-method-study-20260929/official/measure_pos-formula-1.png)、[数学辅助脚本](../../../../.work/edges2d-association-method-study-20260929/minimal_checks.py)、[原检查](../../../../.work/edges2d-association-method-study-20260929/checks.json)、[原独审](../../../../.work/edges2d-association-method-independent-20260929/review.md)。保留原字节/hash/结果；P2单边信息边界已在当前唯一IM-025定义，原研究记录不改写为无问题通过。数学脚本不执行HALCON、产品或机台，不作生产依赖。

### 7.11. 开源对照与采纳顺序

来源和迁移边界唯一见[IM-025 §15.2](../../../independent-modules/features-2d/DEVELOPMENT-GUIDE.md#152-本次已保留研究与实际落点2026-10-0910-10复用)及[REF-002](../../../references/REF-002_GitHub_DevExpress与OpenSource研究基线.md#measurement-source-research)。原scikit-image固定commit `533b7694d2004ae84e49e2cfd0bcfc5f8e562f22`的正交残差/数值处理/有限搜索测试供参考；两点退化、重估后仅warn及旧inlier mask等限制不被README或文件存在代替。生产仍用HALCON 26.05/AsunImage，不引入Python拟合运行依赖。

先接收IM-025对应切片，独立实现及测试，再接应用合同与真实资格；不以本页导航或历史研究直接派全量生产代码。
