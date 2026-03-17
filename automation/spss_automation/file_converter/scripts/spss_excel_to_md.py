"""
SPSS 통계분석 엑셀(XLS/CSV) → 마크다운 변환 스크립트
=======================================================
SPSS에서 출력한 교차표 엑셀을 구조화된 마크다운으로 자동 변환합니다.

Usage:
    python spss_excel_to_md.py --input "파일.xls"
    python spss_excel_to_md.py --input "파일.csv" --output-dir "경로" --exclude A2-1
"""

import os
import sys
import io
import csv
import argparse
import time

# UTF-8 래퍼 (Windows cmd.exe 호환)
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
from datetime import datetime
from pathlib import Path

# ---------------------------------------------------------------------------
# 블록 유형 판별 헬퍼
# ---------------------------------------------------------------------------

def _has_mean_pattern(label_row):
    """라벨행에 '평균'이 포함되어 있으면 평균표."""
    return any("평균" in str(c) for c in label_row)


def _has_binary_categories(category_row):
    """카테고리행이 참여/미참여, 희망/비희망 등 이진 패턴이면 교차표."""
    cats = [str(c).strip() for c in category_row if str(c).strip() and str(c).strip() not in ("구 분", "")]
    non_label_cats = [c for c in cats if c not in ("빈도", "비율")]
    if not non_label_cats:
        return False
    binary_keywords = [
        ("참여", "미참여"), ("참여 희망", "희망하지 않음"),
        ("만족", "불만족"), ("예", "아니오"),
    ]
    for pos, neg in binary_keywords:
        if any(pos == c for c in non_label_cats) and any(neg == c for c in non_label_cats):
            return True
    # 카테고리가 2~3개이면 교차표로 추정
    if len(non_label_cats) <= 3:
        return True
    return False


def _has_frequency_pattern(label_row):
    """라벨행에 '빈도'가 존재하면 빈도표 (기본 fallback)."""
    return any("빈도" in str(c) for c in label_row)


# ---------------------------------------------------------------------------
# 블록 유형 레지스트리 (확장 가능)
# ---------------------------------------------------------------------------

BLOCK_TYPE_REGISTRY = [
    {"type": "mean_table",      "detect_label": _has_mean_pattern,      "detect_cat": None},
    {"type": "cross_table",     "detect_label": None,                   "detect_cat": _has_binary_categories},
    {"type": "frequency_table", "detect_label": _has_frequency_pattern, "detect_cat": None},
]


# ---------------------------------------------------------------------------
# XLS 셀 서식 백분율 감지 헬퍼
# ---------------------------------------------------------------------------

def _is_pct_format(fmt_text):
    """셀 서식 문자열에 '%'가 포함되어 있으면 백분율."""
    return "%" in fmt_text


def _get_pct_decimals(fmt_text):
    """셀 서식에서 소수점 자리수 추출. 예: '0.0%' → 1, '0.00%' → 2, '0%' → 0."""
    import re
    m = re.search(r'\.(\d*0)%', fmt_text)
    if m:
        return len(m.group(1))
    # '0%' 형태 (소수점 없음)
    if re.search(r'\d%', fmt_text):
        return 0
    return 1  # 기본 소수점 1자리


# ---------------------------------------------------------------------------
# 데이터 로드
# ---------------------------------------------------------------------------

def load_data(filepath):
    """XLS 또는 CSV 파일을 2D 리스트로 로드."""
    ext = Path(filepath).suffix.lower()
    rows = []

    if ext == ".xls":
        try:
            import xlrd
            wb = xlrd.open_workbook(filepath, formatting_info=True)
            ws = wb.sheet_by_index(0)
            for r in range(ws.nrows):
                row = []
                for c in range(ws.ncols):
                    cell = ws.cell(r, c)
                    if cell.ctype == xlrd.XL_CELL_NUMBER:
                        val = cell.value
                        # 셀 서식 확인하여 백분율 감지
                        xf_idx = ws.cell_xf_index(r, c)
                        xf = wb.xf_list[xf_idx]
                        fmt_key = xf.format_key
                        fmt_str = wb.format_map.get(fmt_key, None)
                        fmt_text = fmt_str.format_str if fmt_str else ""

                        if _is_pct_format(fmt_text):
                            # 소수점 자리수 추출 후 백분율 변환
                            decimals = _get_pct_decimals(fmt_text)
                            pct_val = val * 100
                            row.append(f"{pct_val:.{decimals}f}%")
                        elif val == int(val):
                            row.append(str(int(val)))
                        else:
                            row.append(str(val))
                    else:
                        row.append(str(cell.value).strip())
                rows.append(row)
        except ImportError:
            print("[ERROR] xlrd 패키지가 필요합니다: pip install xlrd")
            sys.exit(1)
    elif ext in (".csv", ".tsv"):
        encoding_list = ["utf-8-sig", "utf-8", "cp949", "euc-kr"]
        for enc in encoding_list:
            try:
                with open(filepath, "r", encoding=enc) as f:
                    reader = csv.reader(f)
                    rows = [list(r) for r in reader]
                break
            except (UnicodeDecodeError, UnicodeError):
                continue
        if not rows:
            print(f"[ERROR] 파일 인코딩을 판독할 수 없습니다: {filepath}")
            sys.exit(1)
    else:
        print(f"[ERROR] 지원하지 않는 파일 형식: {ext}")
        sys.exit(1)

    return rows


# ---------------------------------------------------------------------------
# 블록 분리
# ---------------------------------------------------------------------------

def split_blocks(rows):
    """빈 행 기준으로 블록 분리. 각 블록은 행 리스트."""
    blocks = []
    current = []
    for row in rows:
        # 모든 셀이 비어있으면 블록 구분
        if all(str(c).strip() == "" for c in row):
            if current:
                blocks.append(current)
                current = []
        else:
            current.append(row)
    if current:
        blocks.append(current)
    return blocks


# ---------------------------------------------------------------------------
# 블록 분류
# ---------------------------------------------------------------------------

def classify_block(block):
    """블록의 유형을 판별하여 반환."""
    if len(block) < 4:
        return "unknown"

    # 라벨행 (보통 3~4번째 행)
    label_row = block[3] if len(block) > 3 else block[-1]
    # 카테고리행 (보통 2~3번째 행)
    cat_row = block[2] if len(block) > 2 else block[-1]

    for entry in BLOCK_TYPE_REGISTRY:
        if entry["detect_label"] and entry["detect_label"](label_row):
            return entry["type"]
        if entry["detect_cat"] and entry["detect_cat"](cat_row):
            return entry["type"]

    return "frequency_table"  # 기본 fallback


# ---------------------------------------------------------------------------
# 블록 파싱
# ---------------------------------------------------------------------------

def _get_title(block):
    """블록에서 문항 제목 추출."""
    first_row = block[0]
    title = str(first_row[0]).strip()
    if not title and len(first_row) > 1:
        title = str(first_row[1]).strip()
    return title


def _get_total_n(block):
    """'전 체' 행에서 N 추출."""
    for row in block:
        cell0 = str(row[0]).strip()
        if cell0 == "전 체" or cell0 == "전체":
            for c in row[1:]:
                v = str(c).strip().replace(",", "")
                if v and v.replace(".", "").replace("%", "").isdigit() and "%" not in v:
                    try:
                        n = int(float(v))
                        if n > 0:
                            return n
                    except:
                        pass
    return None


def _find_label_row_index(block):
    """'빈도'/'비율' 또는 '업체수'/'평균'이 있는 라벨행 인덱스 찾기."""
    for i, row in enumerate(block):
        row_str = " ".join(str(c) for c in row)
        if "빈도" in row_str and "비율" in row_str:
            return i
        if "업체수" in row_str and "평균" in row_str:
            return i
    return 3  # 기본 fallback


def parse_frequency_block(block):
    """빈도표 블록 파싱 → dict."""
    title = _get_title(block)
    total_n = _get_total_n(block)
    label_idx = _find_label_row_index(block)

    # 카테고리행: label_idx - 1
    cat_idx = label_idx - 1
    cat_row = block[cat_idx] if cat_idx >= 0 else []

    # 카테고리 추출 (col 3부터 2칸 간격)
    categories = []
    for i in range(3, len(cat_row), 2):
        cat = str(cat_row[i]).strip()
        if cat:
            categories.append(cat)

    # "전 체" 행 찾기
    total_row = None
    all_data_rows = []
    for row in block[label_idx + 1:]:
        cell0 = str(row[0]).strip()
        if cell0 in ("전 체", "전체"):
            total_row = row
        else:
            all_data_rows.append(row)

    # 전체 행에서 빈도/비율 추출 (col 3부터 2칸 간격)
    items = []
    if total_row and categories:
        for ci, cat in enumerate(categories):
            freq_col = 3 + ci * 2
            pct_col = freq_col + 1
            freq = str(total_row[freq_col]).strip() if freq_col < len(total_row) else ""
            pct = str(total_row[pct_col]).strip() if pct_col < len(total_row) else ""
            if freq or pct:
                items.append({"category": cat, "frequency": freq, "percentage": pct})

    # 교차표용: 하위집단 데이터
    subgroups = _parse_subgroup_rows(all_data_rows, categories)

    return {
        "type": "frequency_table",
        "title": title,
        "total_n": total_n,
        "items": items,
        "subgroups": subgroups,
    }


def parse_cross_block(block):
    """교차표 블록 파싱 → dict, 빈도표와 동일한 구조."""
    return parse_frequency_block(block)


def parse_mean_block(block):
    """평균표 블록 파싱 → dict."""
    title = _get_title(block)
    total_n = _get_total_n(block)

    # 헤더행에서 프로그램명 추출
    if len(block) < 3:
        return {"type": "mean_table", "title": title, "total_n": total_n, "items": [], "subgroups": []}

    program_row = block[1]
    label_row = block[2]

    # 프로그램명 추출 (col 2부터 2칸 간격)
    programs = []
    for i in range(2, len(program_row), 2):
        name = str(program_row[i]).strip()
        if name:
            # [만족도점수] 접두사 제거
            name = name.replace("[만족도점수] ", "").replace("[만족도점수]", "")
            programs.append({"col_idx": i, "name": name})

    # "전 체" 행에서 업체수/평균 추출
    total_row = None
    all_data_rows = []
    for row in block[3:]:
        cell0 = str(row[0]).strip()
        if cell0 in ("전 체", "전체"):
            total_row = row
        else:
            all_data_rows.append(row)

    items = []
    if total_row and programs:
        for prog in programs:
            ci = prog["col_idx"]
            count = str(total_row[ci]).strip() if ci < len(total_row) else ""
            mean = str(total_row[ci + 1]).strip() if ci + 1 < len(total_row) else ""
            items.append({
                "program": prog["name"],
                "count": count,
                "mean": mean,
            })

    return {
        "type": "mean_table",
        "title": title,
        "total_n": total_n,
        "items": items,
        "subgroups": [],
    }


def _parse_subgroup_rows(data_rows, categories):
    """하위집단(연관 산업 분야별 등) 데이터 파싱."""
    subgroups = []
    current_group_name = None

    for row in data_rows:
        cell0 = str(row[0]).strip()
        cell1 = str(row[1]).strip() if len(row) > 1 else ""
        cell2 = str(row[2]).strip() if len(row) > 2 else ""

        if cell0 in ("전 체", "전체"):
            continue

        # 그룹명 (col 0에 텍스트가 있으면 새 그룹)
        if cell0:
            current_group_name = cell0

        sub_name = cell1 if cell1 else cell0
        sub_n = cell2

        # 빈도/비율 추출
        values = []
        for ci in range(len(categories)):
            freq_col = 3 + ci * 2
            pct_col = freq_col + 1
            freq = str(row[freq_col]).strip() if freq_col < len(row) else ""
            pct = str(row[pct_col]).strip() if pct_col < len(row) else ""
            values.append({"frequency": freq, "percentage": pct})

        subgroups.append({
            "group": current_group_name or "",
            "name": sub_name,
            "n": sub_n,
            "values": values,
        })

    return subgroups


# ---------------------------------------------------------------------------
# 마크다운 포맷터
# ---------------------------------------------------------------------------

def format_frequency_table(data, include_subgroups=False):
    """빈도표 dict → 마크다운 문자열."""
    lines = []
    n_str = f" (N={data['total_n']})" if data["total_n"] else ""
    lines.append(f"### {data['title']}{n_str}")
    lines.append("")

    if not data["items"]:
        lines.append("> 데이터 없음")
        lines.append("")
        return "\n".join(lines)

    if include_subgroups and data.get("subgroups"):
        # 통합 1개 테이블: 전체행 + 하위집단행
        lines.extend(_format_unified_table(data))
    else:
        # 요약 모드: 항목/빈도/비율 3열 테이블
        max_cat = max(len(item["category"]) for item in data["items"])
        max_cat = max(max_cat, 4)

        lines.append(f"| {'항목':<{max_cat}} | 빈도  | 비율  |")
        lines.append(f"| :{'-' * max_cat} | :---: | :---: |")

        for item in data["items"]:
            freq = item["frequency"] if item["frequency"] else "-"
            pct = item["percentage"] if item["percentage"] else "-"
            lines.append(f"| {item['category']:<{max_cat}} | {freq:>5} | {pct:>5} |")

        lines.append("")

    lines.append("---")
    lines.append("")
    return "\n".join(lines)


def format_cross_table(data, include_subgroups=False):
    """교차표도 빈도표와 동일 포맷 사용."""
    return format_frequency_table(data, include_subgroups)


def format_mean_table(data, include_subgroups=False):
    """평균표 dict → 마크다운 문자열."""
    lines = []
    n_str = f" (N={data['total_n']})" if data["total_n"] else ""
    lines.append(f"### {data['title']}{n_str}")
    lines.append("")

    if not data["items"]:
        lines.append("> 데이터 없음")
        lines.append("")
        return "\n".join(lines)

    lines.append("| 프로그램 | 업체수 | 평균(5점) |")
    lines.append("| :------- | :----: | :-------: |")

    for item in data["items"]:
        count = item["count"] if item["count"] else "-"
        mean = item["mean"] if item["mean"] else "-"
        lines.append(f"| {item['program']} | {count:>6} | {mean:>9} |")

    lines.append("")
    lines.append("---")
    lines.append("")
    return "\n".join(lines)


def _format_unified_table(data):
    """전체행 + 하위집단을 통합 1개 테이블로 포맷."""
    lines = []
    categories = [item["category"] for item in data["items"]]

    # 헤더 구성
    header = "| 구분 | 하위집단 | N |"
    sep = "| :--- | :------- | :---: |"
    for cat in categories:
        header += f" {cat}(빈도) | {cat}(비율) |"
        sep += " :---: | :---: |"

    lines.append(header)
    lines.append(sep)

    # 전체 행 (볼드체 강조)
    total_n = data.get("total_n", "")
    total_row = f"| **전체** | | **{total_n}** |"
    for item in data["items"]:
        freq = item["frequency"] if item["frequency"] else "-"
        pct = item["percentage"] if item["percentage"] else "-"
        total_row += f" **{freq}** | **{pct}** |"
    lines.append(total_row)

    # 하위집단 행
    for sg in data["subgroups"]:
        row = f"| {sg['group']} | {sg['name']} | {sg['n']} |"
        for v in sg["values"]:
            freq = v["frequency"] if v["frequency"] else "-"
            pct = v["percentage"] if v["percentage"] else "-"
            row += f" {freq} | {pct} |"
        lines.append(row)

    lines.append("")
    return lines


# ---------------------------------------------------------------------------
# 보고서 빌드
# ---------------------------------------------------------------------------

FORMATTERS = {
    "frequency_table": format_frequency_table,
    "cross_table": format_cross_table,
    "mean_table": format_mean_table,
}

PARSERS = {
    "frequency_table": parse_frequency_block,
    "cross_table": parse_cross_block,
    "mean_table": parse_mean_block,
}


def build_report(blocks_data, mode="summary"):
    """파싱된 블록 데이터 → 완성된 마크다운 문자열."""
    lines = []
    include_sub = (mode == "cross")

    for bd in blocks_data:
        btype = bd["type"]
        formatter = FORMATTERS.get(btype, format_frequency_table)
        lines.append(formatter(bd, include_subgroups=include_sub))

    return "\n".join(lines)


def build_header(config, mode="summary"):
    """보고서 헤더 생성."""
    mode_label = "요약 보고서" if mode == "summary" else "교차표 상세 보고서"
    lines = [
        f"# {config.get('project_name', 'SPSS 분석 결과')} — {mode_label}",
        "",
        f"> **조사 대상**: {config.get('survey_target', 'N/A')}  ",
        f"> **생성일시**: {config.get('timestamp', '')}",
        "",
        "---",
        "",
    ]
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# 실행 기록 로그
# ---------------------------------------------------------------------------

def log_execution(log_dir, timestamp, input_file, total, success, failed, elapsed):
    """execution_history.csv에 실행 기록 추가."""
    os.makedirs(log_dir, exist_ok=True)
    log_path = os.path.join(log_dir, "execution_history.csv")
    write_header = not os.path.exists(log_path)

    with open(log_path, "a", encoding="utf-8-sig", newline="") as f:
        writer = csv.writer(f)
        if write_header:
            writer.writerow(["timestamp", "input_file", "blocks_total", "blocks_success", "blocks_failed", "elapsed_sec"])
        writer.writerow([timestamp, os.path.basename(input_file), total, success, failed, f"{elapsed:.1f}"])


def log_error(log_dir, timestamp, input_file, block_title, error_msg):
    """error_report.md에 에러 기록 추가."""
    os.makedirs(log_dir, exist_ok=True)
    err_path = os.path.join(log_dir, "error_report.md")
    with open(err_path, "a", encoding="utf-8") as f:
        f.write(f"\n## [{timestamp}] {os.path.basename(input_file)}\n")
        f.write(f"- **블록**: {block_title}\n")
        f.write(f"- **에러**: {error_msg}\n\n")


# ---------------------------------------------------------------------------
# 메인
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="SPSS 엑셀/CSV → 마크다운 변환")
    parser.add_argument("--input", "-i", required=True, help="입력 파일 경로 (XLS/CSV)")
    parser.add_argument("--output-dir", "-o", default=None, help="출력 디렉토리 (기본: 입력파일 디렉토리/output/)")
    parser.add_argument("--exclude", "-e", nargs="*", default=[], help="제외할 문항번호 (예: A2-1)")
    parser.add_argument("--prefix", default="", help="출력 파일 접두사 (미지정 시 원본 파일명에서 자동 생성)")
    parser.add_argument("--project-name", default="SPSS 분석 결과", help="프로젝트명")
    parser.add_argument("--survey-target", default="", help="조사 대상 설명")
    args = parser.parse_args()

    input_path = os.path.abspath(args.input)
    if not os.path.exists(input_path):
        print(f"[ERROR] 파일을 찾을 수 없습니다: {input_path}")
        sys.exit(1)

    # 출력 디렉토리: 기본값은 입력파일 디렉토리/output/
    if args.output_dir:
        output_dir = os.path.abspath(args.output_dir)
    else:
        output_dir = os.path.join(os.path.dirname(input_path), "output")
    os.makedirs(output_dir, exist_ok=True)

    # 로그 디렉토리
    script_dir = os.path.dirname(os.path.abspath(__file__))
    log_dir = os.path.join(os.path.dirname(script_dir), "logs")

    # 타임스탬프 (YYMMDD_HHMM)
    now = datetime.now()
    timestamp = now.strftime("%y%m%d_%H%M")

    # 설정
    config = {
        "project_name": args.project_name,
        "survey_target": args.survey_target,
        "timestamp": timestamp,
    }

    # config.py가 같은 디렉토리에 있으면 로드
    config_path = os.path.join(script_dir, "config.py")
    if os.path.exists(config_path):
        import importlib.util
        spec = importlib.util.spec_from_file_location("config", config_path)
        cfg_mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cfg_mod)
        if hasattr(cfg_mod, "CONFIG"):
            # config.py 값을 기본값으로, CLI 인자를 우선
            for k, v in cfg_mod.CONFIG.items():
                if k not in config or not config[k]:
                    config[k] = v
            # exclude_items 병합
            if "exclude_items" in cfg_mod.CONFIG:
                args.exclude = list(set(args.exclude + cfg_mod.CONFIG["exclude_items"]))

    # prefix가 미지정이면 원본 파일명에서 자동 생성
    if not args.prefix:
        stem = Path(input_path).stem
        # (output) 또는 (OUTPUT) 접두사 제거
        import re as _re
        stem = _re.sub(r'^\((?:output|OUTPUT)\)\s*', '', stem)
        # 공백/특수문자 → 언더스코어, snake_case화
        stem = _re.sub(r'[\s\-\.]+', '_', stem)
        args.prefix = f"report_{stem}"

    print(f"[INPUT]  {input_path}")
    print(f"[OUTPUT] {output_dir}")
    print(f"[TIME]   {timestamp}")
    if args.exclude:
        print(f"[SKIP]   {', '.join(args.exclude)}")
    print()

    # 1. 데이터 로드
    start_time = time.time()
    print("[INFO] 데이터 로딩...")
    rows = load_data(input_path)
    print(f"   {len(rows)}행 로드 완료")

    # 2. 블록 분리
    print("[INFO] 블록 분리 중...")
    raw_blocks = split_blocks(rows)
    print(f"   {len(raw_blocks)}개 블록 감지")

    # 3. 블록 분류 및 파싱
    print("[INFO] 블록 분류 및 파싱 중...")
    blocks_data = []
    success_count = 0
    fail_count = 0

    for block in raw_blocks:
        title = _get_title(block)

        # 제외 항목 체크
        skip = False
        for ex in args.exclude:
            if title.startswith(ex):
                print(f"   [SKIP] {title}")
                skip = True
                break
        if skip:
            continue

        btype = classify_block(block)

        try:
            parse_fn = PARSERS.get(btype, parse_frequency_block)
            data = parse_fn(block)
            data["type"] = btype
            blocks_data.append(data)
            success_count += 1
            print(f"   [OK]   [{btype}] {title}")
        except Exception as e:
            fail_count += 1
            print(f"   [FAIL] [{btype}] {title} -- {e}")
            log_error(log_dir, timestamp, input_path, title, str(e))

    print(f"\n[RESULT] {success_count}개 성공, {fail_count}개 실패\n")

    # 4. 보고서 생성 (2파일)
    # 요약 보고서
    summary_content = build_header(config, "summary") + build_report(blocks_data, "summary")
    summary_file = os.path.join(output_dir, f"{args.prefix}_{timestamp}.md")
    with open(summary_file, "w", encoding="utf-8") as f:
        f.write(summary_content)
    print(f"[SAVED] 요약 보고서: {summary_file}")

    # 교차표 보고서
    cross_content = build_header(config, "cross") + build_report(blocks_data, "cross")
    cross_file = os.path.join(output_dir, f"{args.prefix}_{timestamp}_cross.md")
    with open(cross_file, "w", encoding="utf-8") as f:
        f.write(cross_content)
    print(f"[SAVED] 교차표 보고서: {cross_file}")

    # 5. 실행 기록
    elapsed = time.time() - start_time
    log_execution(log_dir, timestamp, input_path, len(raw_blocks), success_count, fail_count, elapsed)

    print(f"\n[DONE] 완료! ({elapsed:.1f}초)")


if __name__ == "__main__":
    main()
