# Obsidian summary template

Use one markdown file per first-level folder category.

Suggested structure:

```markdown
---
category: <folder-name>
source_root: <paper_root>
paper_count: <n>
generated_by: paper-folder-obsidian
---

# <Category Name>

## Overview
- Total papers: <n>
- Source folder: `<folder>`
- Asset folder: `assets/cat_<category_index>`

## Papers

### <Paper title>
- Authors: <authors>
- Year: <year>
- Venue: <journal_or_conference>
- GitHub: <url or 未找到>
- PDF: `<absolute path>`
- Zotero: 未提供

![Title and authors](assets/cat_<category_index>/cat_<category_index>_paper_<paper_index>__title.png)

![Method pipeline / overall framework](assets/cat_<category_index>/cat_<category_index>_paper_<paper_index>__framework.png)

#### 摘要式总结
<summary>

#### 核心贡献
- ...

#### 方法
- ...

#### 实验结论
- ...

#### 局限性
- ...

#### 我的启发
- ...
```

Only include the framework image block if an image was successfully extracted.

Never use the original paper title or original PDF filename in PNG filenames. Always use the manifest-driven safe names.
