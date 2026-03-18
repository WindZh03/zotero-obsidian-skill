#!/usr/bin/env python3
from __future__ import annotations
import argparse
import json
import re
from pathlib import Path

import fitz  # PyMuPDF

POSITIVE_KEYWORDS = [
    'pipeline', 'framework', 'overall framework', 'overview', 'architecture',
    'method overview', 'approach overview', 'system overview', 'model overview',
    'proposed method', 'our method', 'workflow', 'methodology', 'design overview'
]
NEGATIVE_KEYWORDS = [
    'result', 'results', 'ablation', 'dataset', 'statistics', 'accuracy', 'table',
    'appendix', 'supplementary', 'qualitative', 'quantitative', 'user study',
    'comparison', 'benchmark', 'error analysis'
]
CAPTION_RE = re.compile(r'^(figure|fig\.?|overview|architecture|pipeline)\b', re.I)
METHOD_TEXT_RE = re.compile(
    r'(pipeline|framework|architecture|workflow|overall|overview|method|approach|model)',
    re.I,
)


def first_page_title_author_clip(page: fitz.Page) -> fitz.Rect:
    w, h = page.rect.width, page.rect.height
    return fitz.Rect(0, 0, w, max(160, h * 0.28))


def save_clip(page: fitz.Page, rect: fitz.Rect, out_path: Path, zoom: float = 2.2):
    out_path.parent.mkdir(parents=True, exist_ok=True)
    pix = page.get_pixmap(matrix=fitz.Matrix(zoom, zoom), clip=rect, alpha=False)
    pix.save(str(out_path))


def normalize_text(text: str) -> str:
    return ' '.join(text.split())


def block_text(block: dict) -> str:
    parts: list[str] = []
    for line in block.get('lines', []):
        for span in line.get('spans', []):
            t = span.get('text', '')
            if t:
                parts.append(t)
    return normalize_text(' '.join(parts))


def nearby_text_score(text: str) -> float:
    t = text.lower()
    score = 0.0
    for kw in POSITIVE_KEYWORDS:
        if kw in t:
            score += 2.0 if kw != 'method' else 0.6
    for kw in NEGATIVE_KEYWORDS:
        if kw in t:
            score -= 1.5
    if CAPTION_RE.search(text):
        score += 1.5
    return score


def text_blocks(raw: dict):
    out = []
    for block in raw.get('blocks', []):
        if block.get('type') == 0:
            text = block_text(block)
            if text:
                out.append((fitz.Rect(block['bbox']), text))
    return out


def image_blocks(raw: dict, page_rect: fitz.Rect):
    imgs = []
    page_area = page_rect.get_area() or 1
    for block in raw.get('blocks', []):
        if block.get('type') != 1:
            continue
        bbox = fitz.Rect(block['bbox'])
        area_ratio = bbox.get_area() / page_area
        if area_ratio < 0.035:
            continue
        imgs.append((bbox, area_ratio))
    return imgs


def nearby_texts(img_bbox: fitz.Rect, texts: list[tuple[fitz.Rect, str]]):
    nearby = []
    expanded = fitz.Rect(
        max(0, img_bbox.x0 - 40),
        max(0, img_bbox.y0 - 120),
        img_bbox.x1 + 40,
        img_bbox.y1 + 140,
    )
    for rect, text in texts:
        if expanded.intersects(rect):
            nearby.append(text)
    return nearby


def page_level_score(page_text: str, page_number: int) -> float:
    t = page_text.lower()
    score = 0.0
    for kw in POSITIVE_KEYWORDS:
        if kw in t:
            score += 0.8 if kw != 'method' else 0.3
    for kw in NEGATIVE_KEYWORDS:
        if kw in t:
            score -= 0.6
    # Favor the early-middle pages where method figures often appear.
    if 2 <= page_number <= 6:
        score += 1.2
    elif 7 <= page_number <= 10:
        score += 0.5
    elif page_number == 1:
        score -= 0.8
    return score


def candidate_framework_regions(page: fitz.Page, page_number: int):
    raw = page.get_text('dict')
    texts = text_blocks(raw)
    images = image_blocks(raw, page.rect)
    page_text = normalize_text(page.get_text())
    page_bias = page_level_score(page_text, page_number)
    candidates = []

    for bbox, area_ratio in images:
        score = area_ratio * 10.0 + page_bias
        score -= abs(0.32 - bbox.y0 / max(page.rect.height, 1)) * 0.8
        local_texts = nearby_texts(bbox, texts)
        local_blob = ' '.join(local_texts)
        score += nearby_text_score(local_blob)

        # Prefer figures with caption-like text near them.
        if any(CAPTION_RE.search(t) for t in local_texts):
            score += 1.0

        # Penalize very top-of-first-page hero images/logos.
        if page_number == 1 and bbox.y1 < page.rect.height * 0.45:
            score -= 3.0

        # Penalize things that look like full-page teaser figures or posters.
        if area_ratio > 0.55 and page_number == 1:
            score -= 2.5

        candidates.append({
            'score': score,
            'bbox': bbox,
            'page_number': page_number,
            'area_ratio': area_ratio,
            'context': local_blob[:500],
        })

    # Fallback: when there are no image blocks, look for text-indicated method pages.
    if not candidates and METHOD_TEXT_RE.search(page_text):
        h = page.rect.height
        w = page.rect.width
        clip = fitz.Rect(w * 0.05, h * 0.18, w * 0.95, h * 0.78)
        candidates.append({
            'score': page_bias,
            'bbox': clip,
            'page_number': page_number,
            'area_ratio': clip.get_area() / (page.rect.get_area() or 1),
            'context': page_text[:500],
        })

    candidates.sort(key=lambda x: x['score'], reverse=True)
    return candidates


def choose_framework_region(doc: fitz.Document, max_pages: int):
    upper = min(max_pages, len(doc))
    all_candidates = []
    for idx in range(upper):
        page = doc[idx]
        all_candidates.extend(candidate_framework_regions(page, idx + 1))

    if not all_candidates:
        return None

    best = all_candidates[0]
    # Require a minimum quality bar so we do not save unrelated images.
    if best['score'] < 1.8:
        return None
    return best


def extract_assets(pdf_path: Path, out_dir: Path, base_name: str, max_pages: int = 12):
    doc = fitz.open(pdf_path)
    assets = {
        'pdf_path': str(pdf_path),
        'page_count': len(doc),
        'title_author_image': '',
        'framework_image': '',
        'framework_page': None,
        'framework_score': None,
        'asset_base_name': base_name,
    }
    try:
        page0 = doc[0]
        title_rect = first_page_title_author_clip(page0)
        title_out = out_dir / f'{base_name}__title.png'
        save_clip(page0, title_rect, title_out)
        assets['title_author_image'] = str(title_out)

        best = choose_framework_region(doc, max_pages=max_pages)
        if best is not None:
            page = doc[best['page_number'] - 1]
            bbox = best['bbox']
            pad = 8
            clip = fitz.Rect(
                max(0, bbox.x0 - pad),
                max(0, bbox.y0 - pad),
                min(page.rect.width, bbox.x1 + pad),
                min(page.rect.height, bbox.y1 + pad),
            )
            framework_out = out_dir / f'{base_name}__framework.png'
            save_clip(page, clip, framework_out, zoom=2.0)
            assets['framework_image'] = str(framework_out)
            assets['framework_page'] = best['page_number']
            assets['framework_score'] = round(best['score'], 3)
        return assets
    finally:
        doc.close()


def main():
    ap = argparse.ArgumentParser(description='Extract title/author and framework images from a PDF.')
    ap.add_argument('pdf_path')
    ap.add_argument('assets_root')
    ap.add_argument('--base-name', required=True, help='ASCII-safe base filename such as cat_01_paper_001')
    ap.add_argument('--json', action='store_true')
    ap.add_argument('--max-pages', type=int, default=12)
    args = ap.parse_args()

    pdf_path = Path(args.pdf_path).expanduser().resolve()
    assets_root = Path(args.assets_root).expanduser().resolve()
    assets_root.mkdir(parents=True, exist_ok=True)
    result = extract_assets(pdf_path, assets_root, base_name=args.base_name, max_pages=args.max_pages)
    text = json.dumps(result, ensure_ascii=False, indent=2)
    print(text)


if __name__ == '__main__':
    main()
