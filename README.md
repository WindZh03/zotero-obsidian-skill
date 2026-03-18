# zotero-obsidian-skill

一个用于**批量读取本地论文 PDF，并按分类生成 Obsidian 汇总 Markdown** 的 Skill。

当前版本以“**本地文件夹输入 → 论文解析与截图 → Obsidian 输出**”为核心工作流，适合已经按主题整理好论文目录的用户。
未来版本希望进一步打通 **Zotero** 和 **Obsidian**，形成从文献收集、阅读总结到笔记沉淀的一体化闭环。

---

## 项目简介

`zotero-obsidian-skill` 的目标，是将你本地整理好的论文文件夹自动转换为适合在 Obsidian 中阅读、检索和持续积累的分类总结笔记。

当前版本支持以下能力：

1. 读取你提供的本地论文总文件夹
2. 将总文件夹下的**一级子文件夹**视为分类
3. 递归扫描每个分类中的所有 PDF 文件
4. 对每篇论文提取并整理关键信息
5. 为每篇论文尝试生成两张配图：

   * 一张包含**论文标题与作者信息**的截图
   * 一张尽可能贴近**论文方法 / framework / pipeline / overall architecture** 的截图
6. 为每个分类生成一个 Obsidian Markdown 汇总文件
7. 将 Markdown 与配套图片统一写入指定的输出目录

---

## 未来规划

`zotero-obsidian-skill` 的长期目标，是进一步打通 **Zotero** 和 **Obsidian**，形成一条真正自动化的论文管理与知识沉淀流程：

* 直接从 Zotero 中读取指定分类或文献条目
* 自动获取对应 PDF 与元数据
* 完成论文内容总结、关键信息提取和方法图整理
* 按预设结构输出到 Obsidian 中

这样就不再需要先手动整理本地文件夹，而是可以把 **Zotero** 作为论文入口，把 **Obsidian** 作为知识输出与整理终点，实现从“文献收集”到“阅读总结”再到“笔记沉淀”的一体化闭环。

> 当前公开版本仍以“本地文件夹输入 + Obsidian 输出”为主，Zotero 直连能力仍在规划中。

---

## 在 Claude Code 中使用

```bash
# Create the skill directory
mkdir -p ~/.claude/skills/zotero-obsidian-skill

# Copy all files (or copy the unpacked skill folder directly)
cp -R /path/to/zotero-obsidian-skill/* ~/.claude/skills/zotero-obsidian-skill/
```

或者直接克隆仓库：

```bash
git clone https://github.com/WindZh03/zotero-obsidian-skill.git ~/.claude/skills/zotero-obsidian-skill
```

安装完成后，即可在 Claude Code 中调用对应 Skill。

---

## 使用示例

你可以像下面这样使用这个 Skill：

```text
请读取下面这个论文总文件夹，并为每个一级子文件夹生成一个 Obsidian markdown 汇总文件，同时输出论文标题/作者截图，以及尽可能贴近论文方法介绍的 framework 图。

paper_root: /Users/yourname/Documents/Papers-A
output_root: /Users/yourname/Obsidian/MyVault/Paper Summaries
```

---

## 输入目录说明

你需要提供一个**总文件夹 A 的绝对路径**作为输入。

这个总文件夹 `A` 下可以包含一个或多个**一级子文件夹**。
**一级子文件夹的数量 = 分类数量 = 最终生成的 Markdown 文件数量。**

对于 Zotero 用户，可以先在 Zotero 中选择一个目标分类，将该分类中的论文导出到本地文件夹，再将导出的文件夹作为本 Skill 的输入目录。

### 输入结构示例

```text
A/
├── CV/
│   ├── paper1.pdf
│   ├── paper2.pdf
│   └── more_papers/
│       └── paper3.pdf
├── NLP/
│   ├── a.pdf
│   └── b.pdf
└── Multimodal/
    ├── mm_1.pdf
    └── subfolder/
        ├── mm_2.pdf
        └── mm_3.pdf
```

在这个例子中：

* `CV` 是一个分类
* `NLP` 是一个分类
* `Multimodal` 是一个分类

因此最终会生成 **3 个 Markdown 文件**。

### 输入规则

* 总文件夹 `A` 本身不是分类
* **只有 A 下的一级子文件夹才会被视为分类**
* 每个分类文件夹内部可以继续包含任意层子文件夹
* Skill 会**递归扫描**这些子目录中的 PDF
* 非 PDF 文件会被忽略

---

## 输出目录说明

你还需要提供一个输出目录 `output_root`，通常建议将其设置为 Obsidian Vault 中的某个专用子目录，例如：

```text
/Users/yourname/Obsidian/MyVault/Paper Summaries
```

生成结果通常类似如下结构：

```text
Paper Summaries/
├── CV.md
├── NLP.md
├── Multimodal.md
└── assets/
    ├── cat_01/
    │   ├── cat_01_paper_001__title.png
    │   ├── cat_01_paper_001__framework.png
    │   ├── cat_01_paper_002__title.png
    │   └── ...
    ├── cat_02/
    │   └── ...
    └── cat_03/
        └── ...
```

### 输出规则

* 每个分类生成 **1 个 Markdown 文件**
* 所有截图资源统一放在 `assets/` 目录下
* Markdown 中通过**相对路径**引用图片
* 图片命名采用**安全命名规则**，不依赖原始 PDF 文件名或论文标题

---

## 提取字段说明

每篇论文默认会整理以下信息：

* 标题
* 作者
* 年份
* 发表期刊 / 会议
* GitHub 链接（如果有）
* 摘要式总结
* 核心贡献
* 方法
* 实验结论
* 局限性
* 你自己的启发
* Zotero 链接 / PDF 链接

---

## 截图逻辑说明

### 标题 / 作者截图

对于每篇论文，Skill 会尝试从论文首页截取一张图片，尽量覆盖以下内容：

* 论文标题
* 作者
* 作者单位（如果位置合适）
* 可能存在的副标题

这张图通常命名为：

```text
cat_01_paper_001__title.png
```

### Framework / 方法图

这张图不会简单地截取第一页的大图，而是尽量寻找**最贴近论文方法介绍**的那张图。

Skill 会优先寻找更像以下内容的图片：

* overall framework
* method overview
* pipeline
* architecture
* workflow
* proposed method
* model overview

同时会尽量避开以下不符合需求的图片：

* teaser figure
* 结果图
* 实验曲线图
* 消融实验图
* 数据集统计图
* appendix 图
* 纯示意性装饰图

### 当前提取策略

当前版本遵循以下原则：

* **优先准确**
* **宁可不截，也不要截错**

也就是说，如果没有足够把握找到一张真正贴近“方法框架图”的图片，Skill 会选择**不输出 framework 图**，而不是随意用第一页的大图替代。

---

## 如何提供输入路径

使用时，你只需要提供两个绝对路径：

```text
paper_root: /你的总文件夹A绝对路径
output_root: /你的Obsidian输出目录绝对路径
```

### macOS / Linux 示例

```text
paper_root: /Users/yourname/Documents/Papers-A
output_root: /Users/yourname/Obsidian/MyVault/Paper Summaries
```

### Windows 示例

```text
paper_root: C:\Users\yourname\Documents\Papers-A
output_root: C:\Users\yourname\Documents\ObsidianVault\Paper Summaries
```

---

## Markdown 输出示例

每个分类会生成一个 Markdown 文件，其中会按论文逐篇列出信息，并插入对应图片。

示意结构如下：

```markdown
# CV

## 1. Paper Title

- 作者：...
- 年份：...
- 期刊/会议：...
- GitHub：...
- Zotero 链接 / PDF 链接：...

### 标题与作者截图
![](assets/cat_01/cat_01_paper_001__title.png)

### 方法框架图
![](assets/cat_01/cat_01_paper_001__framework.png)

### 摘要式总结
...

### 核心贡献
...

### 方法
...

### 实验结论
...

### 局限性
...

### 我的启发
...
```

如果某篇论文没有成功提取到 framework 图，则对应部分可以省略，或注明“未提取”。

---

## 文件命名策略

为了避免 Markdown 链接因为中文、空格或特殊字符而失效，Skill 不会直接使用论文标题或原始 PDF 文件名来命名图片资源。

以下类型的文件名都可能带来潜在问题：

* 中文文件名
* 含空格的文件名
* 含括号、井号、百分号等特殊字符的文件名
* 多层复杂命名格式

因此当前版本采用稳定且安全的 ASCII 命名规则，例如：

* 分类目录：`cat_01`、`cat_02`
* 论文编号：`paper_001`、`paper_002`

对应图片文件名示例：

```text
cat_01_paper_001__title.png
cat_01_paper_001__framework.png
```

这种方式的优点包括：

* 避免中文路径导致的显示问题
* 避免空格与特殊字符导致的引用异常
* 输出命名稳定，便于排查和复用
* 与原始 PDF 文件名解耦，更适合自动化生成流程

---

## 使用限制与注意事项

### 1. 必须能够访问本地路径

这个 Skill 只有在当前运行环境**确实可以访问你提供的本地目录**时，才能完成以下操作：

* 扫描 PDF
* 提取截图
* 写入 Markdown
* 写入图片资源

如果运行环境无法访问你的本地文件系统，那么 Skill 应当：

* 明确说明无法直接访问该路径
* 不假装已经写入成功
* 退化为生成说明、模板或中间结果

### 2. PDF 质量会影响结果

以下情况可能影响提取效果：

* PDF 为扫描版
* 论文版式特殊
* 标题页不是标准论文格式
* 方法图被拆分为多个子图
* 图注位置不标准
* PDF 图片分辨率过低

### 3. 方法图不是每篇都能稳定找到

即使论文中确实存在方法图，也可能因为以下原因无法稳定提取：

* 图片位置特殊
* 图片尺寸过小
* 文字特征不明显
* 图中没有明显的 `framework / pipeline / overview` 等信号

因此本 Skill 的设计原则是：

**优先减少误截，而不是强行让每篇论文都输出 framework 图。**

---

## 适用场景

当前版本尤其适合以下场景：

* 你已经按主题整理好了本地论文目录
* 你希望将“文件夹分类”直接映射为 Obsidian 分类笔记
* 你希望保留 PDF 原文的同时，在 Obsidian 中形成结构化总结
* 你希望每篇论文附带关键截图，方便快速回顾

---

## 暂不适合的场景

当前版本暂不特别适合以下需求：

* 直接从 Zotero Collection 中自动读取论文
* 自动同步 Zotero 元数据
* 不按一级子文件夹组织论文
* 对每篇 PDF 单独生成完整独立笔记，而不是分类汇总笔记
* 要求 100% 精准提取所有论文的方法图

这些能力都可以在后续版本中继续增强。

---

## 推荐使用习惯

为了获得更稳定的结果，建议你：

1. 让总文件夹 `A` 下的一级子文件夹语义尽量清晰
   例如：`CV`、`NLP`、`Multimodal`、`3D Vision`

2. 保持每个分类内部的 PDF 结构相对整洁
   虽然支持递归扫描，但过深的目录层级会增加管理复杂度

3. 在 Obsidian 中使用专门的输出目录
   例如：`Paper Summaries`

4. 将 Skill 生成的结果视为“高质量初稿”
   后续可以继续在 Obsidian 中进行人工补充和精修

---

## 一句话总结

`zotero-obsidian-skill` 当前版本适合这样的工作流：

> 你提供一个按分类整理好的本地论文总文件夹 A，Skill 会将每个一级子文件夹视为一个分类，递归读取其中的 PDF，提取论文关键信息与关键截图，并在 Obsidian 中为每个分类生成一个汇总 Markdown 文件。
