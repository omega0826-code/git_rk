# -*- coding: utf-8 -*-
"""
PDF에서 수식 영역을 이미지로 추출하고, 편집 가능한 PPT로 저장하는 스크립트.
1단계: PDF 페이지를 고해상도로 렌더링
2단계: 수식 영역의 좌표를 특정하여 크롭 → 이미지 저장
3단계: 추출된 수식 이미지를 PPT에 삽입
"""

import sys
import os
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

import fitz  # PyMuPDF
from PIL import Image
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN

# ── 경로 설정 ──
PDF_PATH = r"d:\git_rk\image\test\울산 일자리 미스매치 모델_PPT test.pdf"
OUTPUT_DIR = r"d:\git_rk\image\test\formula_images"
PPT_PATH = r"d:\git_rk\image\test\울산_미스매치_수식_PPT.pptx"

os.makedirs(OUTPUT_DIR, exist_ok=True)

# ── 1단계: PDF 페이지 렌더링 및 수식 영역 탐지 ──
print("=" * 60)
print(" PDF 수식 이미지 추출 및 PPT 생성")
print("=" * 60)

doc = fitz.open(PDF_PATH)
DPI = 300  # 고해상도
ZOOM = DPI / 72  # PDF default DPI is 72

# 수식 키워드 - 수식의 시작 부분을 식별하기 위한 패턴
# PDF 에서 수식을 찾기 위해 각 수식의 주변 텍스트를 기준으로 영역을 잡음
FORMULA_MARKERS = [
    {
        "search_text": "Gtarget",  # G_target 수식
        "alt_search": ["전체 취업자", "창업자", "기타(잠재"],
        "title": "연간 취업 대상 자원 (G_target)",
        "section": "2.1. [공급] 연간 취업 대상 자원 확정",
    },
    {
        "search_text": "Sk(ind)",
        "alt_search": ["ulsan,h", "β", "산업별 공급"],
        "title": "산업별 공급 인력 (S^(ind)_k)", 
        "section": "2.2. [공급] 산업별 유효 공급 인력",
    },
    {
        "search_text": "Sj(occ)",
        "alt_search": ["γ", "직무별 공급"],
        "title": "직무별 공급 인력 (S^(occ)_j)",
        "section": "2.2. [공급] 직무별 유효 공급 인력",
    },
    {
        "search_text": "Mk,quant(ind)",
        "alt_search": ["Sk(ind)", "Dk(ind)", "산업"],
        "title": "정량적 미스매치 - 산업",
        "section": "3.1. 정량적 미스매치 (수급차)",
    },
    {
        "search_text": "Mj,quant(occ)",
        "alt_search": ["Sj(occ)", "Dj(occ)", "직무"],
        "title": "정량적 미스매치 - 직무",
        "section": "3.1. 정량적 미스매치 (수급차)",
    },
    {
        "search_text": "수급차율",
        "alt_search": ["Sk−Dk", "×100"],
        "title": "수급차율 보조 지표",
        "section": "3.1. 정량적 미스매치 보조 지표",
    },
    {
        "search_text": "Mk,qual(ind)",
        "alt_search": ["∑S(ind)", "∑D(ind)"],
        "title": "정성적 미스매치 - 산업",
        "section": "3.2. 정성적 미스매치 (구조적 불일치)",
    },
    {
        "search_text": "Mj,qual(occ)",
        "alt_search": ["∑S(occ)", "∑D(occ)"],
        "title": "정성적 미스매치 - 직무",
        "section": "3.2. 정성적 미스매치 (구조적 불일치)",
    },
]


def render_page_to_image(page, dpi=300):
    """PDF 페이지를 고해상도 이미지로 렌더링"""
    zoom = dpi / 72
    mat = fitz.Matrix(zoom, zoom)
    pix = page.get_pixmap(matrix=mat, alpha=False)
    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
    return img


def find_formula_regions_by_page_analysis(doc):
    """
    각 페이지를 분석하여 수식 영역의 좌표를 찾습니다.
    전략: 페이지의 텍스트 블록을 분석하고,
    수식 섹션 헤더를 기준으로 수식 영역을 추출합니다.
    """
    print("\n[1단계] 페이지별 텍스트 분석으로 수식 영역 탐지...")
    
    all_regions = []
    
    for page_idx in range(doc.page_count):
        page = doc[page_idx]
        page_rect = page.rect
        
        # 텍스트 블록 추출 (x0, y0, x1, y1, text, block_no, block_type)
        blocks = page.get_text("dict", flags=fitz.TEXT_PRESERVE_WHITESPACE)
        
        # 텍스트 줄 단위로 분석
        text_lines = []
        for block in blocks["blocks"]:
            if "lines" in block:
                for line in block["lines"]:
                    line_text = ""
                    y0 = line["bbox"][1]
                    y1 = line["bbox"][3]
                    x0 = line["bbox"][0]
                    x1 = line["bbox"][2]
                    for span in line["spans"]:
                        line_text += span["text"]
                    text_lines.append({
                        "text": line_text.strip(),
                        "y0": y0, "y1": y1,
                        "x0": x0, "x1": x1,
                        "page": page_idx
                    })
        
        # 상세 출력
        print(f"\n  페이지 {page_idx + 1}: {len(text_lines)}줄 텍스트 발견")
        for tl in text_lines:
            if len(tl["text"]) > 0:
                print(f"    y={tl['y0']:.0f}-{tl['y1']:.0f}: {tl['text'][:80]}")
    
    return text_lines


# ── 전체 페이지 이미지 렌더링 ──
print("\n[전체 페이지 렌더링]")
page_images = []
for i in range(doc.page_count):
    page = doc[i]
    img = render_page_to_image(page, DPI)
    img_path = os.path.join(OUTPUT_DIR, f"page_{i+1}_full.png")
    img.save(img_path, "PNG")
    page_images.append(img)
    print(f"  페이지 {i+1}: {img.width}x{img.height}px -> {img_path}")

# ── 텍스트 분석으로 수식 영역 파악 ──
text_data = find_formula_regions_by_page_analysis(doc)

doc.close()

print("\n\n전체 페이지 이미지가 저장되었습니다.")
print("다음 단계에서 수식 영역을 크롭합니다.")
