# -*- coding: utf-8 -*-
"""PDF 구조 탐색: 페이지 수, 텍스트, 이미지 정보 확인"""
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

import fitz  # PyMuPDF

pdf_path = r"d:\git_rk\image\test\울산 일자리 미스매치 모델_PPT test.pdf"
doc = fitz.open(pdf_path)

print(f"총 페이지 수: {doc.page_count}")
print(f"PDF 크기: {doc[0].rect.width:.0f} x {doc[0].rect.height:.0f}")
print()

for i, page in enumerate(doc):
    text = page.get_text("text").strip()
    images = page.get_images(full=True)
    print(f"--- 페이지 {i+1} ---")
    print(f"  이미지 수: {len(images)}")
    # 텍스트 미리보기 (처음 200자)
    preview = text[:200].replace('\n', ' | ')
    print(f"  텍스트: {preview}")
    print()

doc.close()
