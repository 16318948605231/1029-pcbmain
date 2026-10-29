# Calibration与标定资格：平台接入指导

- 文档 ID：`DEV-MET-030`；版本：`1.3.0-prep`；状态：`DesignReview`。
- 本页维护产品标定引用、资格和激活的接入映射。相机/FOV标定方法、靶标、公开API、工程/测试与逐切片准入唯一见[IM-013 calibration-assets](../../../independent-modules/calibration-assets/DEVELOPMENT-GUIDE.md)；大图拼接标定唯一见[IM-023 mosaic](../../../independent-modules/mosaic/DEVELOPMENT-GUIDE.md)。两者为不同独立模块。

## 统一实施规则

按[DEV-GOV-010](../../../01-governance/DEV-GOV-010_实施级规格唯一标准.md)与各唯一模块指导划分规格准备、实现运行及产品资格。产品Schema、资格决定、激活与设备行为由各原Owner采纳；本页不冻结第二套Core契约或默认板型。

## 1. 核心数据链

应用提供参考靶/证书、设备配置、坐标/单位、拟合与独立检查计划和方法Profile→IM-013采样观测/求解/验证→不可变资产和适用性证据→原资格Owner决定→原激活Owner提交受控绑定→应用固定运行闭包并处理失效。求解不写产品量测或质量放行。

## 2. 异常点处理

应用保留原图、观测ID、失败/剔除原因及预先批准策略；模块按唯一方法处理。调整拟合或用过检查集必须形成新修订和独立验证，不能删掉难点获得通过。

## 3. 不确定度

物理资格需要实际参考、允差、温度与使用域证据。像素残差、物理误差、不确定度与拟合诊断分开；资格分析消费[IM-049 qualification](../../../independent-modules/qualification/DEVELOPMENT-GUIDE.md)，产品认可条件见[DEV-MET-033](DEV-MET-033_MSA、GR&R与计量资格开发指导.md)。缺客户数值不能编为全平台常量，也不阻已冻结Core规格。

## 4. 多 FOV

各FOV引用IM-013的合格相机资产；IM-023负责机台范围的位置/时钟/FOV映射与运动补偿。吸盘整板圆点靶、分层/移动参考、均匀无编码网格和编码靶的适用条件沿IM-023，不能用相机板求解替代整机验证。0.5px等历史例值仅为来源实例，不能作为准入指标。

## 实施级关联功能

[FS-016](../12-function-specs/FS-016_Calibration.md)与产品PageContract只映射具体用途；模块开工状态由唯一指导逐切片矩阵和主控接收确定，不继承旧活动文档的Ready声明。

<a id="distortion-module"></a>
## 5. 畸变矫正的独立核心与参数UI

校正执行独立由[IM-022 image-rectification](../../../independent-modules/image-rectification/DEVELOPMENT-GUIDE.md)负责，消费已解相机/映射资产并输出校正帧、坐标关系、有效域与来源。应用不得将它与板姿态、平场、拼接或资格批准共写为一个开关。映射安全、插值/支持、缓存键与Owner按IM-022；实际WPF与物理资格分别验收。

<a id="calibration-lifecycle"></a>
## 6. 标定种类、参数与求解闭环

[IM-013 §7](../../../independent-modules/calibration-assets/DEVELOPMENT-GUIDE.md#7-标定方法及-halconasunimage-选择)冻结相机/FOV靶型、面阵/线扫模型、观测识别与拒绝条件、相机—投影器方法；IM-023冻结拼接方法。棋盘格、无定位框均匀圆点板与HALCON标准板不能互相冒替，应用必须传明确方法/靶标/几何/参考绑定，不能按本页另设默认。

### 6.1 输入与参数的语义清单

原设备/采集配置、证书及实测点ID、单位/坐标、源图hash与租约、方法/模型/初值、拟合/检查分配、预算/截止和资格条件由应用固定；公开字段与有效域只读各模块唯一契约。解析证书不等于批准用途，实际证书采纳见[DEV-MET-033](DEV-MET-033_MSA、GR&R与计量资格开发指导.md#reference-certificate-adoption)。

### 6.2 相机与工作平面的逐步实现

具体观测/求解/残差/平面变换及资源路线按IM-013，应用只装配公开端口、绑定源身份、保留原操作和接受对应输出。HALCON 26.05算子经ImageLibDotNet.cv2，版本资料沿项目手册；本页不再并行定义采样、角点提取或另一套模型。

### 6.3 激活、失效、取消与恢复

不可变资产与可变资格/绑定分开。应用激活携候选hash、scope、原绑定修订和原操作身份；提交Owner重核资格/依赖/权限并CAS。运行固定闭包，新版本不替换在途；原资格撤销或配置/环境越域由执行/质量Owner按批准策略隔离受影响用途。求解服务不隐含急停权。提交未知只查原操作；回滚只能使用当前仍合格闭包，不能复活撤销资格。

## 7. 验收、性能与代码切片

相机、拼接、校正和资格分析分别验证本模块的软件/算法/Owner/性能，再由产品验证两消费者、真实参考和现场用途。低fit残差但独立边缘超限、fit/check泄漏、ROI变更、离面目标、子资产撤销、激活冲突和回执未知均不得默认为通过。当前状态以各唯一指导为准；本页不授整模块或生产Ready。

原固定研究与来源/hash保留在[REF-002](../../../references/REF-002_GitHub_DevExpress与OpenSource研究基线.md#foundation-source-research)、[REF-008](../../../references/REF-008_PCBA-AOI指导副本与平台采纳映射.md#foundation-adoption)，不是另一套当前实施权威。
