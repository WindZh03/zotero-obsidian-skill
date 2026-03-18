#!/usr/bin/env python3
from __future__ import annotations
import argparse
import json
from pathlib import Path


def iter_pdf_files(root: Path):
    for p in sorted(root.rglob('*')):
        if p.is_file() and p.suffix.lower() == '.pdf':
            yield p


def category_for(root: Path, pdf: Path) -> str:
    rel = pdf.relative_to(root)
    return rel.parts[0] if len(rel.parts) > 1 else 'root'


def main():
    ap = argparse.ArgumentParser(description='Scan a paper root and group PDFs by first-level folder.')
    ap.add_argument('paper_root')
    ap.add_argument('--output-root', default='')
    ap.add_argument('--manifest', default='')
    args = ap.parse_args()

    paper_root = Path(args.paper_root).expanduser().resolve()
    if not paper_root.exists() or not paper_root.is_dir():
        raise SystemExit(f'paper_root not found or not a directory: {paper_root}')

    grouped: dict[str, list[dict[str, str]]] = {}
    for pdf in iter_pdf_files(paper_root):
        cat = category_for(paper_root, pdf)
        grouped.setdefault(cat, []).append({
            'pdf_path': str(pdf),
            'relative_path': str(pdf.relative_to(paper_root)),
            'filename': pdf.name,
            'stem': pdf.stem,
            'category': cat,
        })

    output_root = Path(args.output_root).expanduser().resolve() if args.output_root else None
    categories = []
    for cat_idx, (cat, papers) in enumerate(sorted(grouped.items()), start=1):
        asset_dir_name = f'cat_{cat_idx:02d}'
        enriched_papers = []
        for paper_idx, p in enumerate(papers, start=1):
            asset_basename = f'cat_{cat_idx:02d}_paper_{paper_idx:03d}'
            enriched = dict(p)
            enriched.update({
                'paper_index': paper_idx,
                'asset_basename': asset_basename,
                'safe_title_image_name': f'{asset_basename}__title.png',
                'safe_framework_image_name': f'{asset_basename}__framework.png',
            })
            enriched_papers.append(enriched)
        categories.append({
            'category': cat,
            'category_index': cat_idx,
            'asset_dir_name': asset_dir_name,
            'pdf_count': len(enriched_papers),
            'output_markdown': str((output_root / f'{cat}.md')) if output_root else f'{cat}.md',
            'papers': enriched_papers,
        })

    data = {
        'paper_root': str(paper_root),
        'output_root': str(output_root) if output_root else '',
        'category_count': len(categories),
        'pdf_count': sum(len(v['papers']) for v in categories),
        'categories': categories,
    }

    text = json.dumps(data, ensure_ascii=False, indent=2)
    if args.manifest:
        manifest = Path(args.manifest)
        manifest.parent.mkdir(parents=True, exist_ok=True)
        manifest.write_text(text, encoding='utf-8')
        print(str(manifest))
    else:
        print(text)


if __name__ == '__main__':
    main()
