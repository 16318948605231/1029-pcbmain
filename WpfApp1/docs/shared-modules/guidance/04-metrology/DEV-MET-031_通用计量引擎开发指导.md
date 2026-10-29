# 通用计量应用映射

- 文档 ID：`DEV-MET-031`
- 版本：`2.0.0-map`
- 状态：`DocMapped`
- 本页保留应用交接、历史 ID、迁移锚点和研究来源；模块公开 API、算法、参数、资源、测试及实施准入只由 [IM-036 metrology](../../../independent-modules/metrology/DEVELOPMENT-GUIDE.md) 唯一维护。

## 唯一实施权威

| 能力 | 唯一实施章节 | 宿主责任 |
|---|---|---|
| 二维基线兼容 | [IM-036 附录 A](../../../independent-modules/metrology/DEVELOPMENT-GUIDE.md#a1-类型) | 旧消费者及项目引用迁移另行绑定，不能把旧接口当新契约 |
| 基础具名量测、拟合及视觉桥 | [IM-036 §11–16](../../../independent-modules/metrology/DEVELOPMENT-GUIDE.md#11-目标-v02-公开契约asunmetrologycontracts) | 映射原帧/ROI/坐标与方法，消费量值及有效性 |
| 连续截面、轴端、有限层面 | [IM-036 §19.4](../../../independent-modules/metrology/DEVELOPMENT-GUIDE.md#194-连续截面沿程轴与有限层面计算c1) | 冻结对象、方向、有限支持和用途，不能由拟合自动选择工艺基准 |
| 支持域积分、连续矩及中心 | [IM-036 §19.5](../../../independent-modules/metrology/DEVELOPMENT-GUIDE.md#195-dfbusuh共同分片线性积分和矩c2) | 提供原单元支撑、材料/未知域与已资格分解，不把未知补零 |
| 连续面积分布及左逆分位 | [IM-036 §19.6](../../../independent-modules/metrology/DEVELOPMENT-GUIDE.md#196-连续面积cdf原子与左逆c3) | 明确面积权、固定域、端点和工艺量定义，不能以节点排序替代 |
| 二阶参考有界归约 | [IM-036 §19.7–19.8](../../../independent-modules/metrology/DEVELOPMENT-GUIDE.md#197-仿射顶部减q严格正负与cdf分位包络c4) | 提供参考来源/适用域及用途资格，存储数值界不冒充物理误差 |

v0.1、v0.2、v0.3 各用原版本入口与编码规则；不得添加枚举后仍沿旧身份。模块不写 FeatureMeasurement/MeasurementSet、数据库、配方、质量放行或设备命令。产品按 [FS-017](../12-function-specs/FS-017_Feature_measurement.md) 组合模块结果、计量质量及规则；公差、Required、guard band、事实提交和最终判定归原产品 Owner。

## 宿主数据与操作链

冻结目标/方法/输入版本及预算 → 经公开 ROI、坐标、表面和参考端口取得不可变证据 → 映射到 IM-036 的具名请求 → 校验/执行 → 核对量值、支持、版本、有效性及真实资源回执 → 产品 Owner 解释并提交 → UI/报表/统计只读投影。业务顺序由宿主负责，不让独立模块读产品页面、VM、私表或静态当前对象。

DisplayValue、显示缩放、LOD、平滑和语言切换不参与计算。跨 FOV 必须引用各 FOV 的资格及变换证据；美缝连续不能证明计量一致。异常点及参考改变按方法保留证据/派生版本，不以删点、重拟合或换基底使应检偏差消失。未知、部分域、数值停止、取消请求与实际退出分别表达；真实排空前不得释放或伪报终态。

## 迁移锚点

<a id="profile-and-integral"></a>
### 5. 有效截面、方向高度与积分

截面/剖面/沿程见 [IM-036 §19.4](../../../independent-modules/metrology/DEVELOPMENT-GUIDE.md#194-连续截面沿程轴与有限层面计算c1)，域/面积元/部分积分见 [§19.5](../../../independent-modules/metrology/DEVELOPMENT-GUIDE.md#195-dfbusuh共同分片线性积分和矩c2)。PG-016、PG-021、SPI 和钢网按各自用途消费，公共模块不选择材料或替代工艺判断。

<a id="axis-datum-relations"></a>
### 6. 轴端、基准截面与关系

唯一公式、有限域、端部证据和拒绝分支见 [IM-036 §19.4](../../../independent-modules/metrology/DEVELOPMENT-GUIDE.md#194-连续截面沿程轴与有限层面计算c1)；视觉候选及拟合适配见 [§12–13](../../../independent-modules/metrology/DEVELOPMENT-GUIDE.md#12-逐量测定义支撑域与解析断言)。PG-019/020 保留针型、针号、端部识别和接受规则。

<a id="measurand-result-closure"></a>
### 7. 从候选到量值与产品判定

基础请求/量值/有效性见 [IM-036 §11–12](../../../independent-modules/metrology/DEVELOPMENT-GUIDE.md#11-目标-v02-公开契约asunmetrologycontracts)，连续结果见 [§19.2–19.3](../../../independent-modules/metrology/DEVELOPMENT-GUIDE.md#192-强类型输入参数与结果asunmetrologycontracts全部字段)。产品按 FS-017 映射质量、完整性、公差与事实；Applied、Measured 或模型非空均不自动获得生产 PASS。

<a id="surface-deviation-measurands"></a>
### 8. 基准、配准与表面偏差

具名偏差定义见 [IM-036 §12](../../../independent-modules/metrology/DEVELOPMENT-GUIDE.md#12-逐量测定义支撑域与解析断言)；位姿与参考分别由 [IM-033](../../../independent-modules/registration-3d/DEVELOPMENT-GUIDE.md) 和 [IM-035](../../../independent-modules/reference-surface/DEVELOPMENT-GUIDE.md) 拥有。宿主组合公开结果，不在计量器中重建配准或参考拟合。

<a id="supported-numerical-integral"></a>
### 9. 支持域积分、裁切与误差

唯一有限域/共同分片/符号/未知界定义见 [IM-036 §19.5](../../../independent-modules/metrology/DEVELOPMENT-GUIDE.md#195-dfbusuh共同分片线性积分和矩c2)，精确数值、预算和向外舍入见 [§19.8](../../../independent-modules/metrology/DEVELOPMENT-GUIDE.md#198-数值后端预算失败和真实验收门)。原单元跨洞不能靠裁小或细分恢复支撑，重复 FOV 不重复累计。

<a id="supported-moments-centers"></a>
### 10. 面积矩、主轴与体积中心

唯一矩、中心、正部体积、量纲及退化规则见 [IM-036 §19.5](../../../independent-modules/metrology/DEVELOPMENT-GUIDE.md#195-dfbusuh共同分片线性积分和矩c2)，面积独立路线见 [§19.2](../../../independent-modules/metrology/DEVELOPMENT-GUIDE.md#192-强类型输入参数与结果asunmetrologycontracts全部字段)。离散点质量、连续面积中心、同矩等效椭圆与真实拟合尺寸分别命名。

<a id="continuous-area-height-quantiles"></a>
### 11. 连续面积分位

唯一 CDF、常值原子、间隙左逆及条件包络见 [IM-036 §19.6](../../../independent-modules/metrology/DEVELOPMENT-GUIDE.md#196-连续面积cdf原子与左逆c3)，验收向量见 [§19.9](../../../independent-modules/metrology/DEVELOPMENT-GUIDE.md#199-无ui样例反例与唯一测试benchmark落点)。SPI/点胶选择具名方法，不将样本 percentile 或直方图改称连续面积分位。

<a id="plane-height-offset-relations"></a>
### 12. 有限平面、方向高度与层关系

唯一射线交点、定向高度、夹角、同射线/法向偏置及有限支持见 [IM-036 §19.4](../../../independent-modules/metrology/DEVELOPMENT-GUIDE.md#194-连续截面沿程轴与有限层面计算c1)。一般曲面、多交、光程转换不从有限平面模型获得支持；下层模型推导与实测分别表达。

<a id="quadratic-reference-signed-integral"></a>
### 13. 二阶参考有符号积分

原 Q 参考、物理尺度和仿射顶部下的唯一有符号归约见 [IM-036 §19.7](../../../independent-modules/metrology/DEVELOPMENT-GUIDE.md#197-仿射顶部减q严格正负与cdf分位包络c4)。参考资格归 IM-035；不得连接底部三顶点改成平面或以数值模型非负替代材料资格。

<a id="quadratic-reference-bounded-reduction"></a>
### 二阶正负、CDF 与有界分位

唯一全片 Bernstein 界、确定细分、原子/左逆、极值和父片保留见 [IM-036 §19.7–19.8](../../../independent-modules/metrology/DEVELOPMENT-GUIDE.md#197-仿射顶部减q严格正负与cdf分位包络c4)，完整强类型字段及 oracle 见 [§19.2–19.3.1](../../../independent-modules/metrology/DEVELOPMENT-GUIDE.md#1931-v03独立canonical向量规格oracle本轮内存复算)。预算耗尽保诊断界，不报测量有效。

## 准入与来源

2026-10-10 主控已按 DEV-GOV-010 §3.1 接收 IM-036 基础 M1/M2 和连续 C1–C4 的本模块托管规格；精确范围/剩余门以 IM-036 §18/19.10 为准。没有创建新工程、启动实现或执行产品构建/算法/WPF/性能/HIL/计量/现场验收；产品合同映射、native 资源包络和真实资格不随文档接收提升。

HALCON 路线只按 [26.05 本地算子手册](../../../../halcon算子手册/operators/) 经 `ImageLibDotNet.cv2` 使用 AsunImage。历史手册及公开来源不定义平台 API。原研究原件、hash、有限阅读范围和原数学核对保留，不能作为第二套活动指导：

- 矩研究：[scikit-image _regionprops.py](../../../references/open-source/scikit-image_scikit-image/533b7694d2004ae84e49e2cfd0bcfc5f8e562f22/src/_skimage2/measure/_regionprops.py)、[测试](../../../references/open-source/scikit-image_scikit-image/533b7694d2004ae84e49e2cfd0bcfc5f8e562f22/tests/skimage2/measure/test_regionprops.py)，commit `533b7694d2004ae84e49e2cfd0bcfc5f8e562f22`，BSD-3-Clause；[读集](../../../../.work/metrology-moments-20260929/inputs.json)、[数学记录](../../../../.work/metrology-moments-20260929/validation-results.json)。只借尺度/中心/方向及外层测试思想，不引入 Python/NumPy/SciPy。
- 分位研究：SciPy 1.16.2 commit `b1296b9b4393e251511fe8fdd3e58c22a1124899`，BSD-3-Clause；[来源/hash](../../../../.work/metrology-moments-20260929/quantile-research/sources.json)、[读集](../../../../.work/metrology-moments-20260929/quantile-research/readset.json)、[独立数学核对](../../../../.work/metrology-moments-20260929/quantile-research/verify_quantiles.py)、[结果](../../../../.work/metrology-moments-20260929/quantile-research/validation-results.json)、[接收输入](../../../../.work/metrology-moments-20260929/quantile-research/adoption-inputs.json)、[接收验证](../../../../.work/metrology-moments-20260929/quantile-research/adoption-validation.json)。样本排序仅为边界教训，不提供连续面积分布后端。
- 平面/层关系：[来源及固定 hash](../../../../.work/aoi-solder-method-20260929/sources.json)。二阶参考：[原研究](../../../../.work/reference-surface-method-study-20260929/source.md)及[历史官方原件](../../../../.work/reference-surface-method-study-20260929/extension-sources/halcon/)。历史版本仅作出处，当前算子语义按 26.05。
- 二阶细分：[dhermes/bezier 源码](../../../../.work/reference-surface-method-study-20260929/extension-sources/bezier/src/python/bezier/hazmat/triangle_helpers.py)，commit `cf18953a491e8568e4a4344327ed441d3e8956da`，SHA-256 `11b45dbc287ffedd6960a8fcca93ddb22ccb5cd3f05e48868ef1aad5421bd378`；[测试](../../../../.work/reference-surface-method-study-20260929/extension-sources/bezier/tests/unit/hazmat/test_triangle_helpers.py)，SHA-256 `9e95fca7434f76a7336548f6c210e24e33367f8bb8729a6a55ede6a837137484`，Apache-2.0。仅采凸组合/确定细分与预算异常思想，float 符号分类及上游测试不证明本模块严格积分/CDF。

| 原已核对 HALCON 26.05 原件 | 保留 SHA-256 |
|---|---|
| [area_center](../../../../halcon算子手册/operators/area_center.html) | `8f53f57263bf1bc1d11f20cd5c1ccce15d1417bcbeaaddf6cb8b1b54908ef4d7` |
| [moments_region_2nd](../../../../halcon算子手册/operators/moments_region_2nd.html) | `6639a8367e865d8ec656a04e13c1de46ecac4b0ce130bc57d9eb7b5cc13b9175` |
| [area_center_xld](../../../../halcon算子手册/operators/area_center_xld.html) | `f6139aa73d3988f99eb7c5c2259d3ba534eefe7f75df50f9d493c399e9dd3a50` |
| [moments_xld](../../../../halcon算子手册/operators/moments_xld.html) | `dbfba5f076de9f25cf63417d7da3ebe495191c38efaa72570d68697cbb63862c` |

上述历史数学验证仅覆盖原算例，不冒充当前 C#、预算、资源、物理材料或生产性能结果。模块研究及实现选择只在 IM-036 修订，本页不重新定义公式或接口。
