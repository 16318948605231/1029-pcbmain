# -*- coding: utf-8 -*-
"""为 52 份模块指导和 26 份 UI-PCS 统一补图标可访问性验收要求。

在每个文档的适当位置(最后一个section之前或验收相关section末尾)插入
标准的图标可访问性subsection,引用 DEV-UI-047 §2.3。
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULES = ROOT / "docs" / "independent-modules"
UI_PCS_SHARED = ROOT / "docs" / "shared-modules" / "guidance" / "14-page-contracts"
UI_PCS_PROCESS = ROOT / "docs" / "process-guides" / "guidance" / "14-page-contracts"

ICON_ACCESSIBILITY_TEXT = """
### 图标可访问性验收

遵循 [DEV-UI-047 §2.3](../../../../shared-modules/guidance/05-ui/DEV-UI-047_视觉设计系统规格.md#23-图标可访问性补齐全库空缺)：

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
"""

ICON_ACCESSIBILITY_PCS = """
### 图标可访问性验收

遵循 [DEV-UI-047 §2.3](../../../shared-modules/guidance/05-ui/DEV-UI-047_视觉设计系统规格.md#23-图标可访问性补齐全库空缺)：

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
"""


def process_modules():
    """为 52 份模块指导添加图标可访问性验收"""
    modules = sorted(MODULES.glob("*/DEVELOPMENT-GUIDE.md"))
    processed = 0
    for path in modules:
        content = path.read_text(encoding="utf-8")
        if "图标可访问性验收" in content or "Icon Accessibility" in content:
            continue  # 已有,跳过

        # 在最后插入(文档末尾前)
        lines = content.splitlines(keepends=True)
        # 找最后一个 ## 开头的section
        last_section_idx = -1
        for i in range(len(lines) - 1, -1, -1):
            if lines[i].startswith("## "):
                last_section_idx = i
                break

        if last_section_idx >= 0:
            # 在最后section之前插入新section
            new_content = "".join(lines[:last_section_idx]) + ICON_ACCESSIBILITY_TEXT + "\n" + "".join(lines[last_section_idx:])
        else:
            # 直接追加到末尾
            new_content = content.rstrip() + "\n" + ICON_ACCESSIBILITY_TEXT + "\n"

        path.write_text(new_content, encoding="utf-8")
        processed += 1

    print(f"处理了 {processed}/{len(modules)} 个模块指导")


def process_ui_pcs():
    """为 26 份 UI-PCS 添加图标可访问性验收"""
    pcs_shared = sorted(UI_PCS_SHARED.glob("UI-PCS-*.md"))
    pcs_process = sorted(UI_PCS_PROCESS.glob("UI-PCS-*.md"))
    all_pcs = pcs_shared + pcs_process
    processed = 0

    for path in all_pcs:
        content = path.read_text(encoding="utf-8")
        if "图标可访问性验收" in content or "Icon Accessibility" in content:
            continue

        lines = content.splitlines(keepends=True)
        # 找最后一个 ## 开头的section
        last_section_idx = -1
        for i in range(len(lines) - 1, -1, -1):
            if lines[i].startswith("## "):
                last_section_idx = i
                break

        if last_section_idx >= 0:
            new_content = "".join(lines[:last_section_idx]) + ICON_ACCESSIBILITY_PCS + "\n" + "".join(lines[last_section_idx:])
        else:
            new_content = content.rstrip() + "\n" + ICON_ACCESSIBILITY_PCS + "\n"

        path.write_text(new_content, encoding="utf-8")
        processed += 1

    print(f"处理了 {processed}/{len(all_pcs)} 个 UI-PCS")


def main():
    process_modules()
    process_ui_pcs()
    print("\n全部完成:52 份模块指导 + 26 份 UI-PCS 均已补图标可访问性验收")


if __name__ == "__main__":
    main()
