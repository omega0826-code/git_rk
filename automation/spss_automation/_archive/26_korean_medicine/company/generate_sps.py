# -*- coding: utf-8 -*-
"""
company_guideline.csv를 읽어 SPSS 25.0 syntax (.sps) 파일을 생성하는 스크립트
- VARIABLE LABELS: 원본 문항 전문 라벨
- VALUE LABELS: 각 변수의 값 라벨
- 인코딩: CP949 (EUC-KR) - SPSS 25.0 한국어 Windows 호환
"""

import csv
import os
import re

INPUT_CSV = os.path.join(os.path.dirname(__file__), "company_guideline.csv")
OUTPUT_SPS = os.path.join(os.path.dirname(__file__), "company_label.sps")
OUTPUT_SHORT_SPS = os.path.join(os.path.dirname(__file__), "company_label_short.sps")


def clean_text(text: str) -> str:
    """SPSS 라벨용 텍스트 정리"""
    text = text.replace("&amp;", "&")
    text = text.replace("\\n", " ")
    text = text.replace("\n", " ")
    # CP949 호환: 반각/특수 중점 등을 일반 문자로 치환
    text = text.replace("\uff65", "\u00b7")  # ･ → ·
    text = text.replace("\u2027", "\u00b7")  # ‧ → ·
    # 유니코드 스마트 따옴표를 일반 따옴표로 변환
    text = text.replace("\u2018", "'")
    text = text.replace("\u2019", "'")
    text = text.replace("\u201C", '"')
    text = text.replace("\u201D", '"')
    # 작은따옴표 이스케이프 (SPSS에서 '' 사용)
    text = text.replace("'", "''")
    return text.strip()


def parse_guideline(csv_path: str):
    var_labels = []
    val_labels_dict = []
    current_var = None
    current_values = []

    with open(csv_path, "r", encoding="utf-8-sig") as f:
        reader = csv.reader(f)
        next(reader)  # 헤더 스킵

        for row in reader:
            if len(row) < 4:
                continue

            qtn_type = row[0].strip()
            var_code = row[1].strip()
            content = row[2].strip()

            if qtn_type and var_code:
                if current_var and current_values:
                    val_labels_dict.append((current_var, current_values))
                current_var = var_code
                current_values = []
                label_text = clean_text(content)
                if label_text:
                    var_labels.append((var_code, label_text))

            elif not qtn_type and var_code.isdigit() and content:
                val_num = var_code
                val_text = clean_text(content)
                current_values.append((val_num, val_text))

        if current_var and current_values:
            val_labels_dict.append((current_var, current_values))

    return var_labels, val_labels_dict


def generate_sps(var_labels, val_labels_dict, output_path, title_suffix=""):
    lines = []
    lines.append("* Encoding: EUC-KR.")
    lines.append("* ============================================================.")
    lines.append(f"* 대구한의대학교 RISE사업 기업 설문조사 - 변수 라벨 및 값 라벨{title_suffix}.")
    lines.append("* SPSS 25.0 Syntax.")
    lines.append("* ============================================================.")
    lines.append("")
    lines.append("* -- VARIABLE LABELS -----------------------------------------------.")
    lines.append("")
    lines.append("VARIABLE LABELS")

    for i, (var_name, label_text) in enumerate(var_labels):
        if " TO " in var_name:
            parts = var_name.split(" TO ")
            separator = "." if i == len(var_labels) - 1 else ""
            lines.append(f"   {parts[0]}  '{label_text}'{separator}")
        else:
            separator = "." if i == len(var_labels) - 1 else ""
            lines.append(f"   {var_name}  '{label_text}'{separator}")

    lines.append("EXECUTE.")
    lines.append("")
    lines.append("* -- VALUE LABELS -------------------------------------------------.")
    lines.append("")
    lines.append("VALUE LABELS")

    for idx, (var_name, values) in enumerate(val_labels_dict):
        lines.append(f"   /{var_name}")
        for val_num, val_text in values:
            lines.append(f"      {val_num}  '{val_text}'")

    lines.append(".")
    lines.append("EXECUTE.")
    lines.append("")

    with open(output_path, "w", encoding="cp949") as f:
        f.write("\n".join(lines))

    print(f"[완료] SPS 파일 생성: {output_path}")
    print(f"       - 변수 라벨 수: {len(var_labels)}")
    print(f"       - 값 라벨 변수 수: {len(val_labels_dict)}")


# ── 통계표용 간략 라벨 매핑 ─────────────────────────────────
SHORT_LABELS = {
    "DQ1": "기업명",
    "DQ2": "대표자명",
    "DQ3": "대표전화",
    "DQ4": "기업 형태",
    "DQ5": "주소",
    "DQ6": "매출액(2024년)",
    "DQ7": "종업원 수",
    "DQ8": "업종",
    "AG1": "응답자명",
    "AG2": "부서/직급",
    "AG3": "전화번호",
    "AG4": "E-mail",
    "SQ1": "연관 산업 분야",
    "A1": "RISE사업 인지 여부",
    "A1_1": "RISE사업 인지 경로",
    "A2": "RISE사업 참여 여부",
    "A2_1": "RISE사업 전반 만족도",
    "A2_2": "프로그램 불만족 이유",
    "A2_3": "미참여 이유",
    "A3": "개선점·건의사항",
    "A4L_1": "[참여] 산학공동기술개발과제(R&D)",
    "A4L_2": "[참여] 디자인개발·시제품제작 지원",
    "A4L_3": "[참여] Tech-Bridge 시제품제작",
    "A4L_4": "[참여] 산학연계형 시제품제작",
    "A4L_5": "[참여] 한의-면역 R&D",
    "A4L_6": "[참여] Western Blot 실무과정",
    "A4L_7": "[참여] 재직자 대상 교육",
    "A4L_8": "[참여] RIES 비교과프로그램",
    "A4L_9": "[참여] 레벨업 리더십 캠프",
    "A4L_10": "[참여] 창업동아리",
    "A4L_11": "[참여] DHU취업사관학교",
    "A4L_12": "[참여] 취업톡톡",
    "A4L_13": "[참여] APT-Nexus 성인학습자 교육",
    "A4L_14": "[참여] 평생·직업교육 확산 프로그램",
    "A4L_15": "[참여] SOS 지역사회 봉사",
    "A4L_16": "[참여] 소외계층 문화활동",
    "A4R_1": "[만족도] 산학공동기술개발과제(R&D)",
    "A4R_2": "[만족도] 디자인개발·시제품제작 지원",
    "A4R_3": "[만족도] Tech-Bridge 시제품제작",
    "A4R_4": "[만족도] 산학연계형 시제품제작",
    "A4R_5": "[만족도] 한의-면역 R&D",
    "A4R_6": "[만족도] Western Blot 실무과정",
    "A4R_7": "[만족도] 재직자 대상 교육",
    "A4R_8": "[만족도] RIES 비교과프로그램",
    "A4R_9": "[만족도] 레벨업 리더십 캠프",
    "A4R_10": "[만족도] 창업동아리",
    "A4R_11": "[만족도] DHU취업사관학교",
    "A4R_12": "[만족도] 취업톡톡",
    "A4R_13": "[만족도] APT-Nexus 성인학습자 교육",
    "A4R_14": "[만족도] 평생·직업교육 확산 프로그램",
    "A4R_15": "[만족도] SOS 지역사회 봉사",
    "A4R_16": "[만족도] 소외계층 문화활동",
    "A5_1 TO A5_6": "세부프로그램 만족 이유",
    "A6_1 TO A6_7": "세부프로그램 불만족 이유",
    "A7_1 TO A7_6": "프로그램 개선사항",
    "B1_1": "[참여희망] 산학공동기술개발과제(R&D)",
    "B1_2": "[참여희망] 디자인개발·시제품제작 지원",
    "B1_3": "[참여희망] Tech-Bridge 시제품제작",
    "B1_4": "[참여희망] 산학연계형 시제품제작",
    "B1_5": "[참여희망] 한의-면역 R&D",
    "B1_6": "[참여희망] Western Blot 실무과정",
    "B1_7": "[참여희망] 재직자 대상 교육",
    "B1_8": "[참여희망] RIES 비교과프로그램",
    "B1_9": "[참여희망] 레벨업 리더십 캠프",
    "B1_10": "[참여희망] 창업동아리",
    "B1_11": "[참여희망] DHU취업사관학교",
    "B1_12": "[참여희망] 취업톡톡",
    "B1_13": "[참여희망] APT-Nexus 성인학습자 교육",
    "B1_14": "[참여희망] 평생·직업교육 확산 프로그램",
    "B1_15": "[참여희망] SOS 지역사회 봉사",
    "B1_16": "[참여희망] 소외계층 문화활동",
    "B2_1 TO B2_6": "중점 추진 희망 사업",
    "B3": "참여 희망 사업(기타)",
    "B5": "희망 교육 프로그램 유형",
    "B6": "대학 전공교육 강화 분야",
    "B7_1 TO B7_10": "RISE사업 필요 역량",
    "B8": "기타 의견",
}


if __name__ == "__main__":
    var_labels, val_labels_dict = parse_guideline(INPUT_CSV)

    # 1) 원본 라벨 SPS 생성
    generate_sps(var_labels, val_labels_dict, OUTPUT_SPS)

    # 2) 통계표용 간략 라벨 SPS 생성
    short_var_labels = []
    for var_name, _ in var_labels:
        if var_name in SHORT_LABELS:
            short_var_labels.append((var_name, clean_text(SHORT_LABELS[var_name])))
        else:
            # 매핑에 없으면 원본 유지
            short_var_labels.append((var_name, _))

    generate_sps(short_var_labels, val_labels_dict, OUTPUT_SHORT_SPS,
                 title_suffix=" (통계표용 간략)")
