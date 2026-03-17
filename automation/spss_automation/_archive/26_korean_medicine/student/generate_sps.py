# -*- coding: utf-8 -*-
"""
student_guideline.csv를 읽어 SPSS 25.0 syntax (.sps) 파일을 생성하는 스크립트
- VARIABLE LABELS: 변수명과 설문 내용을 라벨로 지정
- VALUE LABELS: 각 변수의 값 라벨을 지정
"""

import csv
import os
import re

INPUT_CSV = os.path.join(os.path.dirname(__file__),
                         "student_guideline.csv")
OUTPUT_SPS = os.path.join(os.path.dirname(__file__),
                          "student_label.sps")


def clean_text(text: str) -> str:
    """SPSS 라벨용 텍스트 정리: HTML entity 디코딩, 줄바꿈 제거 등"""
    text = text.replace("&amp;", "&")
    text = text.replace("\\n", " ")
    text = text.replace("\n", " ")
    # CP949 호환: 반각/특수 중점 등을 일반 문자로 치환
    text = text.replace("\uff65", "\u00b7")  # ･ → ·
    text = text.replace("\u2027", "\u00b7")  # ‧ → ·
    # 유니코드 스마트 따옴표를 일반 따옴표로 변환 후 이스케이프
    text = text.replace("\u2018", "'")  # '
    text = text.replace("\u2019", "'")  # '
    text = text.replace("\u201C", '"')  # "
    text = text.replace("\u201D", '"')  # "
    # 작은따옴표 이스케이프 (SPSS에서 '' 사용)
    text = text.replace("'", "''")
    return text.strip()


def parse_guideline(csv_path: str):
    """
    CSV를 파싱하여 두 가지 구조를 반환:
    1) var_labels: [(var_name, label_text), ...]
    2) val_labels: [(var_name_expr, [(val, label), ...]), ...]
    """
    var_labels = []      # 변수 라벨 목록
    val_labels_dict = [] # 값 라벨 목록 (변수명, [(값, 라벨)])

    current_var = None
    current_values = []

    with open(csv_path, "r", encoding="utf-8-sig") as f:
        reader = csv.reader(f)
        header = next(reader)  # 헤더 스킵

        for row in reader:
            if len(row) < 4:
                continue

            qtn_type = row[0].strip()
            var_code = row[1].strip()
            content = row[2].strip()
            val_label_raw = row[3].strip()

            if qtn_type and var_code:
                # 새 변수 시작 → 이전 변수의 값 라벨 저장
                if current_var and current_values:
                    val_labels_dict.append((current_var, current_values))

                current_var = var_code
                current_values = []

                # 변수 라벨 추가
                label_text = clean_text(content)
                if label_text:
                    var_labels.append((var_code, label_text))

            elif not qtn_type and var_code.isdigit() and content:
                # 값 라벨 행: QtnType이 비어 있고, 보기번호(숫자)가 있음
                val_num = var_code
                val_text = clean_text(content)
                current_values.append((val_num, val_text))

        # 마지막 변수 처리
        if current_var and current_values:
            val_labels_dict.append((current_var, current_values))

    return var_labels, val_labels_dict


def generate_sps(var_labels, val_labels_dict, output_path):
    """SPSS syntax (.sps) 파일 생성"""
    lines = []

    # 헤더 주석
    lines.append("* Encoding: EUC-KR.")
    lines.append("* ============================================================.")
    lines.append("* 대구한의대학교 RISE사업 학생 설문조사 - 변수 라벨 및 값 라벨.")
    lines.append("* SPSS 25.0 Syntax.")
    lines.append("* ============================================================.")
    lines.append("")

    # ── VARIABLE LABELS ─────────────────────────────────────
    lines.append("* ── VARIABLE LABELS ──────────────────────────────────────────.")
    lines.append("")
    lines.append("VARIABLE LABELS")

    for i, (var_name, label_text) in enumerate(var_labels):
        # TO 구문이 있는 경우 개별 변수로 분리해야 함
        if " TO " in var_name:
            # "B1_1_1_1 TO B1_1_1_7" 같은 경우 → 그대로 사용 불가
            # VARIABLE LABELS에서는 개별 변수만 가능하므로 첫 번째 변수만 사용
            # 하지만 범위의 모든 변수에 동일 라벨을 줄 수도 있음
            # 여기서는 범위 표기 그대로 라벨 부여 (개별 변수 확장 어려움)
            parts = var_name.split(" TO ")
            # 첫 번째 변수에만 라벨 부여
            separator = "." if i == len(var_labels) - 1 else ""
            lines.append(f"   {parts[0]}  '{label_text}'{separator}")
        else:
            separator = "." if i == len(var_labels) - 1 else ""
            lines.append(f"   {var_name}  '{label_text}'{separator}")

    lines.append("EXECUTE.")
    lines.append("")

    # ── VALUE LABELS ──────────────────────────────────────────
    lines.append("* ── VALUE LABELS ────────────────────────────────────────────.")
    lines.append("")
    lines.append("VALUE LABELS")

    for idx, (var_name, values) in enumerate(val_labels_dict):
        is_last = (idx == len(val_labels_dict) - 1)

        lines.append(f"   /{var_name}")
        for val_num, val_text in values:
            lines.append(f"      {val_num}  '{val_text}'")

        if is_last:
            # 마지막 변수 뒤에 마침표
            pass

    lines.append(".")
    lines.append("EXECUTE.")
    lines.append("")

    # 파일 쓰기 (SPSS 한국어 Windows: CP949/EUC-KR)
    with open(output_path, "w", encoding="cp949") as f:
        f.write("\n".join(lines))

    print(f"[완료] SPS 파일 생성: {output_path}")
    print(f"       - 변수 라벨 수: {len(var_labels)}")
    print(f"       - 값 라벨 변수 수: {len(val_labels_dict)}")


if __name__ == "__main__":
    var_labels, val_labels_dict = parse_guideline(INPUT_CSV)
    generate_sps(var_labels, val_labels_dict, OUTPUT_SPS)
