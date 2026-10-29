# 高保真PageContract与工作台开发指导

> 2026-09-27 平台归位：当前职责与范围按[平台设计基线](<../../../00-baseline/PLATFORM-DESIGN-BASELINE.md>)及[所属指导目录](<../../README.md>)绑定。本页保留原ID与细化内容；原状态 `原文元数据` 仅作历史记录，精确契约/Owner/参数未获批前不作为生产实施准入。
- 文档 ID：`DEV-UI-041`
- 版本：`1.3.0`
- 状态：`DocMapped`
- 架构基线：`ARCH-PCBA-VISION-001 v0.5.3`
- 适用范围：专业工作区、Docking、Document、Inspector、Timeline、Search
- 直接依赖：`DEV-UI-040`
- 主要输出：Query/Command、八态、权限、AutomationId、DPI、键盘

>
本文均以 `ARCH-PCBA-VISION-001 v0.5.3` 为架构输入。该架构当前仍为候选基线/DocMapped，未因本开发准备包而自动获得架构批准或生产资格。若本包与未来获批架构、既有权威 Schema、状态/Owner 规范或实际仓库实现冲突，以获批权威资产为准，并必须登记冲突后再实现。


## 统一实施规则

1. **单一权威**：架构文档负责关系与边界；Schema 负责数据结构；状态/角色规范负责状态与 Owner；PageContract 负责 UI 行为；本开发指导负责实施语义、禁止路径、算法选择、性能、测试与验收；Validator/Test/Manifest 分别负责机器校验、验证和交付快照。
2. **不得复制第二套事实**：不得在产品目录、`spi/`、ViewModel、数据库或临时 JSON 中建立与既有 Schema/状态机/Owner 平行的定义。
3. **事实与投影分离**：UI、报告、统计、质量中心、AI 解释均不得成为事实的第二写入权威。
4. **生产副作用后移**：能在离线/Replay/Shadow 完成的验证，不要先绑定真实设备。
5. **所有失败可见**：失败、拒识、覆盖不足、资格不足、配置失效都必须形成显式状态或事实，禁止默认降级为 Success/OK。
6. **性能有预算**：算法、UI、IO、缓存和并发必须在设计时给出预算；不得在最后阶段才测性能。
7. **可回放优先**：能进入 Replay 的输入、参数、模型、库快照、标定、环境和算法版本尽量冻结为可引用资产。
8. **AI 不获得隐含权威**：AI 只能在既定 Contract 和 AuthorityScope 内产生建议/候选或受控 revision。
9. **真实硬件证据单独计门**：没有 HIL/实机/Golden Sample 证据时，文档状态只能为“准备完成/软件可验证”，不能写“生产通过”。

## 1–6. 共同设计基线（唯一权威：DEV-UI-040）

本页原 §1–§6（设计目标、DevExpress 使用原则、页面八态、高保真工作台骨架、操作流程、UI 自动化）**与 [DEV-UI-040](<DEV-UI-040_WPF+DevExpress Design System开发指导.md>) §1–§6 逐字相同**，属于同一内容的重复副本。2026-10-28 审核归一：**该六节唯一维护于 DEV-UI-040**，本页不再复制，避免两处各自演化而产生同义第二套定义。

本页读者按 DEV-UI-040 §1–§6 执行，另加：

| 议题 | 唯一权威 |
|---|---|
| 设计目标"状态 → 对象 → 结果 → 下一动作" | DEV-UI-040 §1 |
| DevExpress 使用原则与官方 demo 基线 | DEV-UI-040 §2 |
| 页面八态语义 | DEV-UI-040 §3；状态**视觉**呈现见 [DEV-UI-047](DEV-UI-047_视觉设计系统规格.md) §6 |
| 高保真工作台骨架 | DEV-UI-040 §4 |
| 操作流程（自动带出 → 只处理异常、渐进披露、批量差异预览、Draft/Validate/Approve/Release） | DEV-UI-040 §5 |
| UI 自动化（稳定 AutomationId、键盘可达、DPI/最小分辨率/三语） | DEV-UI-040 §6 |
| 色板、图标、排版、动效、无障碍、组件状态矩阵 | [DEV-UI-047](DEV-UI-047_视觉设计系统规格.md) |
| Token 契约、校验算法、对比度公式 | [IM-061 design-system](../../../independent-modules/design-system/DEVELOPMENT-GUIDE.md) §3 |

## 7. 实现前的页面与操作链规划

先在既有架构/页面目录中明确系统有哪些工作区、主窗体/独立窗口/弹窗，各自服务谁、负责什么任务、从哪里进入、怎样返回和恢复。模块链、数据流与页面对应关系在同一批准体系中维护，不新增另一套页面/状态目录。

每个 PageContract 写明：主要角色、使用情境、入口条件、首屏信息、主任务/主命令、常用键盘或单击路径、参数来源、权限、状态转换、错误与恢复、资源释放、适用性能和可用性指标。状态不适用时说明原因；不得在所有页面生搬同一套无业务意义的状态。

生产主窗体优先展示影像、对象身份、状态、结果和下一安全动作。树、属性、日志、SPC 等按任务需要展开；上面的工作台骨架是职责示例，不要求全部面板同时出现。高级参数进入上下文面板或适当弹窗，不能压缩影像到无法判断；关键状态和安全命令不得随布局隐藏。

编码前以关键场景走查原型/流程：载入、编程、运行、异常、复判、恢复、离线测试，以及适用的权限与语言切换。原型仅用于确认流程；需要实现验收时再验证真实 WPF，不把原型冒充最终软件。最终页面数量、分辨率和点击指标在各产品指导冻结，本轮不推定。

控件、SuperTip、状态栏和语言服务统一引用 DEV-UI-040；离线载图引用 DEV-UI-042。共享控件不包含产品私有流程，领域页面不回流到通用 DLL。

## 8. 每页交付内容与页面组合

每个PageContract在原文件增加本页的视觉构图、联动、主任务路径、异常下一动作和具体验收断言；只引用DEV-UI-040的统一Token，避免每页重复建立视觉标准。UI工作区本身可复用，但机台专有动作、权限和质量语义放在制程页组合中。

页级指导必须连到具体PG功能卡或SM公共能力；缺少专页的工艺可以引用公共工作台加本PG的页面增量，不得误称其它制程已有PageContract完整覆盖。待实现时将增量落实为唯一PageContract/正式端口，不复制另一套状态/事件。

高保真设计需能演示正常、失败、恢复连续路径，并标注初始选择、焦点、刷新/取消条件、数值/单位、图例、缺图/无效值、主命令位置。开发者可以调整可逆的像素细节，但不能自行决定角色、业务状态、阈值、命令权限或事实写入。


## 9. 当前可评审交互样例

[UI-PCS-015 §12–14](../../../process-guides/guidance/14-page-contracts/UI-PCS-015_PCB_Inspection_Workbench.md#12-阻焊终检的可交互评审样例)提供阻焊/终检HTML样例、角色/命令/八态及已执行交互/渲染检查。它用于评审面别证据、OCR原读/建议、未评价、草稿修订、取消与提交恢复；其余工作区继续逐页补齐。HTML结果不能代替真实DevExpress/WPF控件行为、DPI/UIA、性能或生产验收。


点胶[UI-PCS-022](../../../process-guides/guidance/14-page-contracts/UI-PCS-022_Dispense_Workbench.md)和涂覆[UI-PCS-023](../../../process-guides/guidance/14-page-contracts/UI-PCS-023_Coating_Workbench.md)已有专属角色/区域、Query来源、Command/AutomationId、八态和操作验收设计。当前尚无这两页交互原型；与UI-PCS-015的已执行HTML检查明确区分。它们消费共享视口/曲线/证据控件，业务VM/工艺区域留在各制程。

插件[UI-PCS-024](../../../process-guides/guidance/14-page-contracts/UI-PCS-024_Insertion_Workbench.md)与THT[UI-PCS-025](../../../process-guides/guidance/14-page-contracts/UI-PCS-025_THT_Solder_Workbench.md)已有专属任务/命令/八态，以及[双模式HTML样例和检查范围](../../../process-guides/guidance/14-page-contracts/UI-PCS-024_Insertion_Workbench.md#prototype-evidence)。重点评审稳定针号、镜像、多目标关系、针端/锡峰、草稿修订与取消迟到；全部合成输入，尚无实际WPF/3D/算法及持久化验证。终装等未覆盖页面继续在原工作区逐项补齐。
