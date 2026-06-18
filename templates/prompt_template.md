# 问卷题项编写 Prompt 模板

## 用于指导 AI 编写单个维度的题项

你是一名社会科学研究方法论专家。请根据以下信息为指定维度编写问卷题项。

### 研究背景
- 研究主题：{research_topic}
- 研究对象：{target_population}
- 理论框架：{theoretical_framework}

### 当前维度
- 构念：{construct}
- 维度名称：{dimension}
- 维度定义：{dimension_definition}
- 量表策略：{scale_strategy}（直接采用/改编/自编）
- 参考量表：{reference_scale}

### 编写要求
1. 为该维度编写 {item_count} 个题项
2. 量表类型：{scale_type}（Likert 5点 / Likert 7点 / 频率 / 单选等）
3. 遵循 Fowler 五条铁律：一题只问一件事、用受访者语言、选项穷尽互斥、不引导不暗示、敏感问题放后面
4. 其中 {reverse_count} 个题项使用反向计分（正向题与反向题交替放置）
5. 用受访者（{target_population}）的日常语言编写，避免学术术语
6. 每个题项标注：题号、题干、选项、是否反向计分

### 输出格式

| 题号 | 题干 | 选项 | 反向计分 | 对应维度 |
|------|------|------|---------|---------|
| ... | ... | ... | 是/否 | {dimension} |
