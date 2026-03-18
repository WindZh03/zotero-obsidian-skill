---
name: paper-folder-obsidian
description: summarize papers from a local root folder that contains one or more first-level subfolders, treat each first-level subfolder as one category, read pdf files recursively inside those category folders, extract a title-authors image and a method pipeline or overall framework image when available, and write one obsidian markdown summary per category. use when the user provides local folder paths for papers and an obsidian output folder.
---

# Paper Folder Obsidian

Use this skill when the user wants an end-to-end paper reading workflow from a local paper folder into Obsidian.

## Required user input
Ask for or confirm exactly these paths before doing any work:

```text
paper_root: /absolute/path/to/A
output_root: /absolute/path/to/obsidian/subfolder
```

Interpret the input strictly:
- `paper_root` is the root folder `A`.
- Each **first-level subfolder** directly under `A` is one category.
- The number of first-level subfolders equals the number of output markdown files.
- Scan PDFs recursively inside each first-level subfolder.
- Ignore non-PDF files.
- If PDFs are placed directly under `A`, group them into a fallback category named `root`.

## Important environment rule
Only claim that files were written when the runtime truly has filesystem access to those local paths.
- If the environment can access the local paths, write the markdown files and extracted images directly.
- If the environment cannot access the user's local filesystem, do **not** pretend the write succeeded. Instead, explain the limitation clearly and either:
  1. ask the user to upload the folder contents, or
  2. generate the markdown content as a deliverable they can save themselves.

## Workflow
Follow this sequence.

1. Validate both absolute paths.
2. Run `scripts/scan_paper_root.py` to inventory PDFs and group them by first-level subfolder.
3. For each PDF in each category:
   - read the PDF;
   - extract bibliographic details from the first page and metadata when possible;
   - create a concise, faithful paper summary using the sections below;
   - run `scripts/extract_pdf_assets.py` to generate image assets:
     - `title_author_image`: crop from the first page containing the paper title and author block;
     - `framework_image`: search the early and mid paper pages for the figure that is most likely to describe the proposed method, pipeline, architecture, workflow, or overall framework. Do not default to the first-page figure. Score candidate figures using nearby captions/text such as `Figure`, `pipeline`, `framework`, `architecture`, `overview`, `workflow`, or `proposed method`, and prefer pages around the method section. If no figure passes the quality bar, omit it.
4. Write exactly one markdown file per category into `output_root`.
5. Store extracted images under a predictable sibling folder, for example:
   - `<output_root>/assets/cat_01/cat_01_paper_001__title.png`
   - `<output_root>/assets/cat_01/cat_01_paper_001__framework.png`
6. In the markdown, embed images with relative paths so Obsidian can render them.

## Safe naming rule for markdown image links
Do **not** use the paper title, original PDF filename, or any user-provided Unicode text when naming extracted PNG files.
- Some PDFs have Chinese filenames, spaces, punctuation, or other characters that can break markdown rendering in some environments.
- Always use the safe, manifest-driven naming scheme from `scan_paper_root.py`:
  - category asset directory: `cat_<category_index>`
  - per-paper base name: `cat_<category_index>_paper_<paper_index>`
- Example:
  - `assets/cat_02/cat_02_paper_003__title.png`
  - `assets/cat_02/cat_02_paper_003__framework.png`
- Keep the original paper title only inside the markdown content, never in the asset filename.
- When building markdown links, always use the generated relative path from this safe naming scheme.

## Required paper fields
For every paper section, include:
- 标题
- 作者
- 年份
- 发表的期刊/会议
- github链接（如果有的话）
- 摘要式总结
- 核心贡献
- 方法
- 实验结论
- 局限性
- 你自己的启发
- Zotero 链接 / PDF 链接

Use `未找到` when a field is genuinely unavailable. For `Zotero 链接`, use `未提供` unless the user supplied a Zotero mapping.
For `PDF 链接`, prefer the local absolute path or a vault-relative path if that is more useful.

## Image rules
- Always include the title-authors image if extraction succeeded.
- Include the method/framework image only if extraction succeeded and looks plausibly relevant to the paper's method.
- Do not fabricate or hallucinate an image.
- If a framework image is missing, simply omit that image block.
- Prefer one framework image per paper.
- When uncertain, prefer omitting the framework image over using a likely wrong teaser, result chart, or first-page illustration.

## Markdown format
Use the template in `references/markdown_template.md`.
Add YAML frontmatter with category, source_root, and paper_count.
Use clear section headings so the note is readable in Obsidian.

## Quality bar for summaries
- Base claims on the paper itself.
- Distinguish clearly between what the paper says and your own insight.
- Keep summaries concise but specific.
- Mention uncertainty when metadata or figure extraction is ambiguous.

## Script usage
Inventory the paper tree:

```bash
python scripts/scan_paper_root.py "/path/to/A" --output-root "/path/to/output" --manifest /tmp/paper_manifest.json
```

Extract images for one PDF using a safe ASCII base name from the manifest:

```bash
python scripts/extract_pdf_assets.py "/path/to/paper.pdf" "/path/to/output/assets/cat_01" --base-name "cat_01_paper_001"
```

## Example request
```text
请读取下面这个论文目录，并把每个一级子文件夹汇总成一个 Obsidian markdown 文件，写入指定目录。

paper_root: /Users/qiqi/Documents/A
output_root: /Users/qiqi/Obsidian/MyVault/Paper Summaries
```
