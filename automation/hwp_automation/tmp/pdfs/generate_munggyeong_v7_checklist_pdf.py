from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


OUTPUT = Path("output/pdf/문경_영순_v7_수정체크리스트_A4_20260407.pdf")
FONT_REGULAR = r"C:\Windows\Fonts\malgun.ttf"
FONT_BOLD = r"C:\Windows\Fonts\malgunbd.ttf"


DATA = [
    {
        "page": "p.1",
        "rows": [
            ("본문", "3줄", "CONTENTS         (페이지 번호 추후에 수정)", "CONTENTS"),
        ],
    },
    {
        "page": "p.4",
        "rows": [
            (
                "본문",
                "14줄",
                "워딩을 수정합니다.연차별 자금투입계획은 사업의 본격적 추진은 2026년~2031년까지로 설정함",
                "연차별 자금투입계획은 사업의 본격적 추진 시기를 고려하여 2026년부터 2031년까지로 설정함.",
            ),
            ("본문", "15줄", "워딩을 수정합니다.", "삭제"),
        ],
    },
    {
        "page": "p.5",
        "rows": [
            (
                "본문",
                "8줄",
                "워딩을 수정하였습니다.한편, 경제적 타당성을 평가하는 분석기법은 방법마다 장단점을 가지고 있어 다양한 기법을 활용하여 사업성을 검토한 후에 최종적인 경제적 타당성을 분석함",
                "한편, 경제적 타당성을 평가하는 분석기법은 방법마다 장단점이 있으므로 다양한 기법을 활용하여 사업성을 검토한 후 최종적인 경제적 타당성을 분석함.",
            ),
            ("본문", "9줄", "워딩을 수정하였습니다.", "삭제"),
        ],
    },
    {
        "page": "p.9",
        "rows": [
            (
                "본문",
                "15줄",
                "워딩을 수정합니다.당해 사업시행 필요 총사업비는으로 추정되고, 경제성 분석용 사업비는 70,445백만 원으로 산정함",
                "당해 사업시행 필요 총사업비는 76,510백만 원으로 추정되고, 경제성 분석용 사업비는 70,445백만 원으로 산정함.",
            ),
            (
                "표",
                "< 자금투입계획 연차별 금액 >",
                "전체 합계를 다시 맞추었습니다.연도별, 항목별로 구분하여 수치를 통일하였습니다.",
                "삭제",
            ),
        ],
    },
    {
        "page": "p.10",
        "rows": [
            ("본문", "1줄", "워딩을 수정합니다.", "삭제"),
            (
                "표",
                "< 경제성 분석용 사업비 >",
                "전체 합계를 다시 맞추었습니다.연도별, 항목별로 구분하여 수치를 통일하였습니다.",
                "삭제",
            ),
            (
                "표",
                "< 자금투입계획 연차별 경제성 분석용 금액 >",
                "전체 합계를 다시 맞추었습니다.연도별, 항목별로 구분하여 수치를 통일하였습니다.",
                "삭제",
            ),
        ],
    },
    {
        "page": "p.11",
        "rows": [
            (
                "본문",
                "5줄",
                "상부시설 건축비는 연차별 투입은 토지 분양의 일정을 감안하여 설정한 것으로 이는 기본 건축비를 비롯한 설계비, 감리비 및 전기 전기기본설비비가 포함된 것임",
                "상부시설 건축비의 연차별 투입은 토지 분양 일정을 감안하여 설정한 것으로, 기본 건축비를 비롯한 설계비, 감리비 및 전기기본설비비가 포함된 것임.",
            ),
            (
                "표",
                "< 연차별 상부시설 건축비 추정 >",
                "연차별 투입금액임으로 관련 내용을 수정하였습니다.",
                "삭제",
            ),
        ],
    },
    {
        "page": "p.12",
        "rows": [
            (
                "본문",
                "2줄",
                "전체 합계를 다시 맞추었습니다.연도별, 항목별로 구분하여 수치를 통일하였습니다.4) 연차별 사업비 추정 결과",
                "4) 연차별 사업비 추정 결과",
            ),
            ("본문", "3줄", "전체 합계를 다시 맞추었습니다.", "삭제"),
        ],
    },
    {
        "page": "p.17",
        "rows": [
            (
                "본문",
                "2줄",
                "< 주요 업종 내역 >워딩을 수정합니다.주요업종(7가지)...",
                "< 주요 업종 내역 >주요업종(7가지)...",
            ),
            (
                "본문",
                "6줄",
                "2021~2023년으로 테이블 수정 완료하였습니다.경상북도에 입지한 업종별 평균매출액(2021~2023년 평균)을 추정하고 이를 업종별 기업수로 나눠서 업종별 기업 평균 매출액을 계산함",
                "경상북도에 입지한 업종별 평균매출액(2021~2023년 평균)을 추정하고, 이를 업종별 기업수로 나누어 업종별 기업 평균매출액을 계산함.",
            ),
            ("본문", "7줄", "2021~2023년으로 테이블 수정 완료하였습니다.", "삭제"),
            (
                "본문",
                "10줄",
                "워딩을 명확하게 수정합니다.업종별 평균매출액과 평균부가가치율을 곱하여 평균부가가치액을 계산하고, 이를 평균 부지면적으로 나눠서 부지면적당 부가가치액을 계산함",
                "업종별 평균매출액과 평균부가가치율을 곱하여 평균부가가치액을 계산하고, 이를 평균 부지면적으로 나누어 부지면적당 부가가치액을 계산함.",
            ),
            ("본문", "11줄", "워딩을 명확하게 수정합니다.", "삭제"),
            (
                "본문",
                "21줄",
                "신규투자율 산정을 다시 실시하여, 해당업종(7종)을 기준으로 재산정하였습니다.신규투자율은 입주의향기업의 예상수요면적 261,690㎡(해당되는 업종 중에서 신규투자 및 이전수요의 합) 중에서 103,689㎡(해당업종 산규투자 분)의 비율로 39.6%로 계산",
                "신규투자율은 입주의향기업의 예상수요면적 261,690㎡(해당 업종의 신규투자 및 이전수요의 합) 중 103,689㎡(해당 업종 신규투자분)의 비율인 39.6%로 계산함.",
            ),
            ("본문", "22줄", "신규투자율 산정을 다시 실시하여, 해당업종(7종)을 기준으로 재산정하였습니다.", "삭제"),
        ],
    },
    {
        "page": "p.18",
        "rows": [
            (
                "표",
                "< 산업시설 편익(최종) >",
                "43.2% 194,396 27,884.8",
                "39.6% 194,396 27,884.8",
            ),
            (
                "표",
                "< 산업시설 편익(최종) > 하단",
                "☞ 산업시설  급면적 143,443㎡",
                "☞ 생산가능면적: 산업시설공급면적 143,443㎡",
            ),
        ],
    },
    {
        "page": "p.21",
        "rows": [
            (
                "본문",
                "1줄",
                "공실률을 감안한 상업시설(지원시설)의 명목편익은 21,084 백만 원이고 이를 4.5%로 할인한 할인편익은 8,313 백만 원으로 분석됨",
                "공실률을 감안한 상업시설(지원시설)의 명목편익은 21,801백만 원이고 이를 4.5%로 할인한 할인편익은 8,453백만 원으로 분석됨",
            ),
            (
                "표",
                "< 지원시설용지 임대료 수입 > 합계행",
                "합 계 / 8,434 / 12.30 / - / 20.7 / 249",
                "합 계 / 8,434 / 12.30 / - / 131.4 / 1,577",
            ),
            (
                "표",
                "< 상업시설편익 연차별 산정 결과 > 합계행",
                "합 계 21,084 / 21,084 / 8,313",
                "합 계 21,801 / 21,801 / 8,453",
            ),
        ],
    },
    {
        "page": "p.23",
        "rows": [
            (
                "본문",
                "2줄",
                "워딩수정히였습니다.항목별편익(B/C)은 0.882, 순현재가치(NPV)가 –35,774 백만 원, 내부수익률(IRR) 3.37%로 나타남",
                "항목별 편익(B/C)은 0.882, 순현재가치(NPV)는 -35,774백만 원, 내부수익률(IRR)은 3.37%로 나타남.",
            ),
            (
                "표",
                "< 경제성분석 결과 > 합계행",
                "지원시설 21,087 / 소계 696,270 / 순현재 267,153 / NPV -35,775 / 순명목 222,181",
                "p.21 지원시설 편익 최종값에 맞춰 연동 수정 필요",
            ),
        ],
    },
    {
        "page": "p.27",
        "rows": [
            (
                "본문",
                "4줄",
                "경제성 및 재무성분석 모두 4.5%로 동일하게 적용합니다.할인율(이자율)은 KDI 예비타당성조사 할인율 4.5%를 적용하도록 함",
                "할인율(이자율)은 KDI 예비타당성조사 기준에 따라 4.5%를 적용함.",
            ),
            ("본문", "5줄", "경제성 및 재무성분석 모두 4.5%로 동일하게 적용합니다.", "삭제"),
            (
                "본문",
                "8줄",
                "당해 사업시행 필요한 재무성 분석용 사업비는",
                "당해 사업시행에 필요한 재무성 분석용 사업비는 65,743백만 원으로 추정함.",
            ),
        ],
    },
    {
        "page": "p.28",
        "rows": [
            (
                "본문",
                "3줄",
                "산업시설용지는 2028년과 2029년에 각각 50%씩, 지원시설용지는 2028년 100%. 주차장은 2029년에 100%를 분양하는 것으로 가정함",
                "산업시설용지는 2028년과 2029년에 각각 50%씩, 지원시설용지는 2028년에 100%, 주차장은 2029년에 100%를 분양하는 것으로 가정함.",
            ),
        ],
    },
]


def register_fonts():
    pdfmetrics.registerFont(TTFont("Malgun", FONT_REGULAR))
    pdfmetrics.registerFont(TTFont("Malgun-Bold", FONT_BOLD))


def make_styles():
    styles = getSampleStyleSheet()
    styles.add(
        ParagraphStyle(
            name="TitleKo",
            fontName="Malgun-Bold",
            fontSize=15,
            leading=20,
            alignment=TA_CENTER,
            spaceAfter=6,
        )
    )
    styles.add(
        ParagraphStyle(
            name="MetaKo",
            fontName="Malgun",
            fontSize=8.5,
            leading=11,
            textColor=colors.HexColor("#555555"),
            alignment=TA_CENTER,
            spaceAfter=12,
        )
    )
    styles.add(
        ParagraphStyle(
            name="SectionKo",
            fontName="Malgun-Bold",
            fontSize=10.5,
            leading=13,
            textColor=colors.HexColor("#1f1f1f"),
            spaceBefore=6,
            spaceAfter=5,
        )
    )
    styles.add(
        ParagraphStyle(
            name="CellKo",
            fontName="Malgun",
            fontSize=7.4,
            leading=9.2,
            wordWrap="CJK",
        )
    )
    styles.add(
        ParagraphStyle(
            name="CellKoBold",
            fontName="Malgun-Bold",
            fontSize=7.6,
            leading=9.2,
            wordWrap="CJK",
        )
    )
    return styles


def para(text, style):
    return Paragraph(text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"), style)


def build_pdf():
    register_fonts()
    styles = make_styles()

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    doc = SimpleDocTemplate(
        str(OUTPUT),
        pagesize=A4,
        leftMargin=12 * mm,
        rightMargin=12 * mm,
        topMargin=12 * mm,
        bottomMargin=12 * mm,
    )

    story = [
        para("문경 영순 타당성 보고서 v7 수정 체크리스트", styles["TitleKo"]),
        para(
            "A4 인쇄용 / 페이지 시작 기준 줄번호 사용 / 본문과 표 수정 대상만 정리",
            styles["MetaKo"],
        ),
    ]

    header = [
        para("구분", styles["CellKoBold"]),
        para("위치", styles["CellKoBold"]),
        para("원본", styles["CellKoBold"]),
        para("수정", styles["CellKoBold"]),
    ]

    for section in DATA:
        story.append(para(section["page"], styles["SectionKo"]))
        rows = [header]
        for kind, loc, src, fix in section["rows"]:
            rows.append(
                [
                    para(kind, styles["CellKo"]),
                    para(loc, styles["CellKo"]),
                    para(src, styles["CellKo"]),
                    para(fix, styles["CellKo"]),
                ]
            )

        table = Table(
            rows,
            colWidths=[18 * mm, 35 * mm, 60 * mm, 62 * mm],
            repeatRows=1,
        )
        table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#dbe7f3")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.black),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#7f8c99")),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 4),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 4),
                    ("TOPPADDING", (0, 0), (-1, -1), 4),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fbfd")]),
                ]
            )
        )
        story.append(table)
        story.append(Spacer(1, 4 * mm))

    doc.build(story)


if __name__ == "__main__":
    build_pdf()
