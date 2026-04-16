# -*- coding: utf-8 -*-
"""
오타 검사 CSV를 A4 인쇄용 체크리스트 PDF로 변환한다.

사용법:
    python export_printable_checklist.py typo_check_detail.csv [--output out.pdf]

기본 동작:
    - 페이지 번호 기준 그룹핑
    - 심각도 '오타', '의심'만 포함
    - A4 세로 레이아웃 PDF 출력
"""

import csv
import argparse
from collections import defaultdict
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


FONT_REGULAR = r"C:\Windows\Fonts\malgun.ttf"
FONT_BOLD = r"C:\Windows\Fonts\malgunbd.ttf"
INCLUDE_SEVERITIES = {"오타", "의심"}


def register_fonts():
    pdfmetrics.registerFont(TTFont("Malgun", FONT_REGULAR))
    pdfmetrics.registerFont(TTFont("Malgun-Bold", FONT_BOLD))


def make_styles():
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(
        name="TitleKo", fontName="Malgun-Bold", fontSize=15, leading=20,
        alignment=TA_CENTER, spaceAfter=6
    ))
    styles.add(ParagraphStyle(
        name="MetaKo", fontName="Malgun", fontSize=8.5, leading=11,
        alignment=TA_CENTER, textColor=colors.HexColor("#555555"), spaceAfter=10
    ))
    styles.add(ParagraphStyle(
        name="SectionKo", fontName="Malgun-Bold", fontSize=10.5, leading=13,
        spaceBefore=6, spaceAfter=5
    ))
    styles.add(ParagraphStyle(
        name="CellKo", fontName="Malgun", fontSize=7.4, leading=9.2, wordWrap="CJK"
    ))
    styles.add(ParagraphStyle(
        name="CellKoBold", fontName="Malgun-Bold", fontSize=7.6, leading=9.2, wordWrap="CJK"
    ))
    return styles


def para(text: str, style):
    safe = (text or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    return Paragraph(safe, style)


def normalize_page(page: str):
    try:
        return int(page)
    except (TypeError, ValueError):
        return 99999


def load_rows(csv_path: Path):
    groups = defaultdict(list)
    with open(csv_path, "r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get("심각도") not in INCLUDE_SEVERITIES:
                continue
            page = row.get("페이지") or "?"
            groups[page].append(row)
    return groups


def build_pdf(csv_path: Path, output_path: Path):
    register_fonts()
    styles = make_styles()
    groups = load_rows(csv_path)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    doc = SimpleDocTemplate(
        str(output_path),
        pagesize=A4,
        leftMargin=12 * mm,
        rightMargin=12 * mm,
        topMargin=12 * mm,
        bottomMargin=12 * mm,
    )

    story = [
        para("HWPX 수정 체크리스트", styles["TitleKo"]),
        para(
            f"원본 CSV: {csv_path.name} / 페이지 기준 위치와 수정 제안만 정리",
            styles["MetaKo"],
        ),
    ]

    header = [
        para("구분", styles["CellKoBold"]),
        para("위치", styles["CellKoBold"]),
        para("원문", styles["CellKoBold"]),
        para("수정", styles["CellKoBold"]),
    ]

    sorted_pages = sorted(groups.keys(), key=normalize_page)
    for page in sorted_pages:
        label = f"{page}페이지" if page != "?" else "?페이지"
        story.append(para(label, styles["SectionKo"]))
        rows = [header]

        page_rows = groups[page]
        page_rows.sort(key=lambda r: (
            0 if (r.get("페이지내위치") or "").startswith("줄") else 1,
            r.get("페이지내위치") or r.get("위치") or "",
        ))

        for row in page_rows:
            kind = "표" if (row.get("카테고리") == "table" or (row.get("위치") or "").startswith("표")) else "본문"
            loc = row.get("페이지내위치") or row.get("위치") or ""
            rows.append([
                para(kind, styles["CellKo"]),
                para(loc, styles["CellKo"]),
                para(row.get("원문") or "", styles["CellKo"]),
                para(row.get("수정제안") or row.get("설명") or "", styles["CellKo"]),
            ])

        table = Table(rows, colWidths=[18 * mm, 28 * mm, 68 * mm, 59 * mm], repeatRows=1)
        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#dbe7f3")),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#7f8c99")),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("LEFTPADDING", (0, 0), (-1, -1), 4),
            ("RIGHTPADDING", (0, 0), (-1, -1), 4),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fbfd")]),
        ]))
        story.append(table)
        story.append(Spacer(1, 4 * mm))

    doc.build(story)


def main():
    parser = argparse.ArgumentParser(description="오타 검사 CSV를 A4 체크리스트 PDF로 변환")
    parser.add_argument("csv_file", help="typo_check_detail.csv 경로")
    parser.add_argument("--output", help="출력 PDF 경로 (기본: 같은 폴더/printable_checklist.pdf)")
    args = parser.parse_args()

    csv_path = Path(args.csv_file)
    if not csv_path.exists():
        raise FileNotFoundError(f"CSV 파일을 찾을 수 없습니다: {csv_path}")

    if args.output:
        output_path = Path(args.output)
    else:
        output_path = csv_path.with_name("printable_checklist.pdf")

    build_pdf(csv_path, output_path)
    print(f"[OK] PDF 생성: {output_path}")


if __name__ == "__main__":
    main()
