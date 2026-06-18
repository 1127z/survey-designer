"""
survey-designer 辅助脚本
功能：将问卷数据生成问卷星可导入的文本格式

⚠️ 重要：本脚本仅生成基础文本草稿，不保证完全符合最新版问卷星导入格式。
问卷星格式可能更新，使用前请到 https://www.wjx.cn/help/help.aspx?helpid=138 确认最新格式。

问卷星"从文本创建问卷"的格式规则：
- 单选题：题目后分行列出选项，题目前加 [单选题]
- 多选题：同上，题目前加 [多选题]
- 量表题：题目前加 [量表题]，选项为Likert等级
- 填空题：题目前加 [填空题]，用____标记填空位
- 矩阵题：题目前加 [矩阵题]
- 段落说明：题目前加 [段落说明]

参考：https://www.wjx.cn/help/help.aspx?helpid=138
"""

import sys
from pathlib import Path


# Likert 量表选项预设——不同类型使用不同选项，不能统一用"非常不同意—非常同意"
LIKERT_PRESETS = {
    "同意度": ["非常不同意", "比较不同意", "一般", "比较同意", "非常同意"],
    "频率": ["从不", "很少", "有时", "经常", "总是"],
    "程度": ["完全没有", "比较轻微", "中等", "比较强烈", "非常强烈"],
    "满意度": ["非常不满意", "比较不满意", "一般", "比较满意", "非常满意"],
    "符合度": ["完全不符合", "比较不符合", "一般", "比较符合", "完全符合"],
}


def resolve_likert_options(likert_type: str, custom_options: list[str] = None) -> list[str]:
    """
    根据 Likert 类型解析选项

    Args:
        likert_type: Likert 类型，如 "Likert-同意度"、"Likert-频率" 等
        custom_options: 自定义选项列表，如有则优先使用
    """
    if custom_options:
        return custom_options

    # 尝试匹配预设类型
    for key, options in LIKERT_PRESETS.items():
        if key in likert_type:
            return options

    # 默认使用同意度选项
    return LIKERT_PRESETS["同意度"]


def generate_wenjuanxing_text(items: list[dict], output_path: str):
    """
    生成问卷星"从文本创建问卷"可导入的文本文件

    输入 items 格式：每个字典包含以下键
    - type: 题型（单选题/多选题/量表题/填空题/矩阵题/段落说明）
    - stem: 题干
    - options: 选项列表（字符串），量表题可为空（自动填充Likert选项）
    - required: 是否必答（默认True）
    - likert_type: 量表题的Likert类型（如 "同意度"、"频率" 等），默认"同意度"
    """

    lines = []

    for item in items:
        qtype = item.get("type", "单选题")
        stem = item.get("stem", "")
        options = item.get("options", [])
        required = item.get("required", True)
        likert_type = item.get("likert_type", "同意度")

        # 段落说明（过渡语）
        if qtype == "段落说明":
            lines.append("[段落说明]")
            lines.append(stem)
            lines.append("")
            continue

        # 题型标记
        type_tag = f"[{qtype}]"

        # 题干
        if required:
            lines.append(f"{type_tag} {stem}")
        else:
            lines.append(f"{type_tag} {stem}（选填）")

        # 选项
        if qtype == "量表题":
            # 根据 Likert 类型选择选项
            resolved_options = resolve_likert_options(likert_type, options if options else None)
            for opt in resolved_options:
                lines.append(opt)
        elif qtype == "填空题":
            # 填空题不需要选项
            pass
        else:
            # 单选/多选题
            for i, opt in enumerate(options):
                label = chr(65 + i)  # A, B, C, D...
                lines.append(f"{label}.{opt}")

        lines.append("")  # 题间空行

    result = "\n".join(lines)
    Path(output_path).write_text(result, encoding="utf-8")
    print(f"问卷星文本文件已生成: {output_path}")


def generate_wenjuanxing_text_from_simple_table(rows: list[dict], output_path: str):
    """
    从简化的题项表（SKILL.md 中的格式）生成问卷星文本

    输入 rows 格式：每个字典包含
    - 题号: 如 Q1, D1, AC1
    - 题干: 题目内容
    - 选项/量表: 如 "Likert-同意度 5点", "男/女/不愿透露"
    - 反向计分: 是/否/—
    - 对应维度: 维度名称
    """

    items = []

    for row in rows:
        qid = row.get("题号", "")
        stem = row.get("题干", "")
        qtype_str = row.get("选项/量表", "Likert-同意度 5点")
        dimension = row.get("对应维度", "")
        required = row.get("必答", True)

        # 判断题型
        if dimension == "注意力检测":
            item_type = "单选题"
        elif dimension == "人口学":
            item_type = "单选题"
        elif "Likert" in qtype_str or "量表" in qtype_str:
            item_type = "量表题"
        elif "多选" in qtype_str:
            item_type = "多选题"
        elif "开放" in qtype_str or "填空" in qtype_str:
            item_type = "填空题"
        else:
            item_type = "单选题"

        # 解析 Likert 类型
        likert_type = "同意度"  # 默认
        for key in LIKERT_PRESETS:
            if key in qtype_str:
                likert_type = key
                break

        # 解析选项
        options = []
        if item_type == "量表题":
            # 量表题使用 likert_type 自动填充选项
            options = []
        elif "/" in qtype_str:
            options = [opt.strip() for opt in qtype_str.split("/") if opt.strip()]
        elif "、" in qtype_str:
            options = [opt.strip() for opt in qtype_str.split("、") if opt.strip()]
        else:
            options = []

        # 题干加上题号
        full_stem = f"{qid}. {stem}"

        items.append({
            "type": item_type,
            "stem": full_stem,
            "options": options,
            "required": required,
            "likert_type": likert_type,
        })

    generate_wenjuanxing_text(items, output_path)


def main():
    """主函数：演示用法"""
    demo_items = [
        {
            "type": "段落说明",
            "stem": "以下问题关注您在日常生活中的情绪体验，请根据实际情况作答。",
            "options": [],
            "required": True,
        },
        {
            "type": "量表题",
            "stem": "1. 过去两周内，我经常感到心情愉快",
            "options": [],
            "required": True,
            "likert_type": "频率",
        },
        {
            "type": "量表题",
            "stem": "2. 购物能帮助我缓解压力",
            "options": [],
            "required": True,
            "likert_type": "同意度",
        },
        {
            "type": "量表题",
            "stem": "3. 我对目前的消费状况感到满意",
            "options": [],
            "required": True,
            "likert_type": "满意度",
        },
        {
            "type": "单选题",
            "stem": "4. 您的性别是？",
            "options": ["男", "女", "不愿透露"],
            "required": True,
        },
        {
            "type": "单选题",
            "stem": "5. 您的年级是？",
            "options": ["大一", "大二", "大三", "大四", "研究生及以上"],
            "required": True,
        },
    ]

    output_path = "demo_wenjuanxing.txt"
    generate_wenjuanxing_text(demo_items, output_path)


if __name__ == "__main__":
    main()
