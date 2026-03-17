"""
교차표 마크다운 → 보고서 워딩 자동 생성 스크립트
=================================================
file_converter가 생성한 _cross.md를 파싱하여
survey_wording_prompt.md 규칙에 따라 보고서용 워딩을 생성합니다.

Usage:
    python generate_wording.py --input "report_*_cross.md"
    python generate_wording.py --input "report_*_cross.md" --threshold 10
"""

import os
import sys
import io
import re
import argparse
import time
from datetime import datetime
from pathlib import Path

# UTF-8 래퍼 (Windows cmd.exe 호환)
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')


# ---------------------------------------------------------------------------
# MD 파싱
# ---------------------------------------------------------------------------

SKIP_CATEGORIES = {"기타", "99.00", "99", "무응답"}


def parse_cross_md(filepath):
    """교차표 MD 파일을 파싱하여 블록 리스트 반환."""
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    blocks = []
    # ### 제목 (N=숫자) 패턴으로 분리
    sections = re.split(r'(?=^### )', content, flags=re.MULTILINE)

    for section in sections:
        section = section.strip()
        if not section.startswith("###"):
            continue

        block = _parse_section(section)
        if block:
            blocks.append(block)

    return blocks


def _parse_section(section):
    """하나의 ### 섹션을 파싱."""
    lines = section.split("\n")
    title_line = lines[0].strip()

    # ### 제거
    title_line = re.sub(r'^###\s*', '', title_line)

    # ■ 제거 (섹션 구분자)
    title_clean = re.sub(r'^■\s*', '', title_line).strip()

    # N 추출
    n_match = re.search(r'\(N=(\d+)\)', title_clean)
    total_n = int(n_match.group(1)) if n_match else None

    # 제목에서 N 제거
    title_no_n = re.sub(r'\s*\(N=\d+\)', '', title_clean).strip()

    # 문항번호와 내용 분리
    id_match = re.match(r'^([A-Z]\d+[\-_]?\d*(?:_\d+)*)\.\s*(.+)', title_no_n)
    if id_match:
        item_id = id_match.group(1)
        item_title = id_match.group(2).strip()
    else:
        item_id = ""
        item_title = title_no_n

    # 응답 방식
    response_type = "복수 응답" if "중복응답" in title_line else "단수 응답"

    # 데이터 없음 체크
    if "> 데이터 없음" in section:
        return None

    # 테이블 파싱
    table_lines = [l for l in lines if l.strip().startswith("|")]
    if len(table_lines) < 3:
        return None

    # 헤더에서 카테고리 추출
    header = table_lines[0]
    categories = _extract_categories(header)
    if not categories:
        return None

    # 전체 행과 하위집단 파싱
    total_row = None
    groups = {}

    for tl in table_lines[2:]:  # 헤더, 구분선 제외
        cells = [c.strip() for c in tl.strip().strip("|").split("|")]
        if len(cells) < 3:
            continue

        # 볼드 제거
        cells_clean = [re.sub(r'\*\*(.+?)\*\*', r'\1', c) for c in cells]

        group_name = cells_clean[0].strip()
        sub_name = cells_clean[1].strip()
        n_val = cells_clean[2].strip()

        # 카테고리별 빈도/비율 추출
        values = {}
        for i, cat in enumerate(categories):
            freq_idx = 3 + i * 2
            pct_idx = 4 + i * 2
            freq = cells_clean[freq_idx].strip() if freq_idx < len(cells_clean) else "-"
            pct = cells_clean[pct_idx].strip() if pct_idx < len(cells_clean) else "-"
            values[cat] = {"freq": freq, "pct": pct}

        if group_name == "전체":
            total_row = {"n": n_val, "values": values}
        else:
            if group_name not in groups:
                groups[group_name] = []
            groups[group_name].append({
                "name": sub_name,
                "n": n_val,
                "values": values
            })

    if not total_row:
        return None

    return {
        "id": item_id,
        "title": item_title,
        "full_title": title_clean,
        "response_type": response_type,
        "total_n": total_n,
        "categories": categories,
        "total_row": total_row,
        "groups": groups
    }


def _extract_categories(header_line):
    """헤더에서 카테고리명 추출. '(빈도)' 패턴 기반."""
    cells = [c.strip() for c in header_line.strip().strip("|").split("|")]
    categories = []
    for c in cells[3:]:  # 구분, 하위집단, N 이후
        m = re.match(r'^(.+?)\(빈도\)$', c.strip())
        if m:
            categories.append(m.group(1).strip())
    return categories


# ---------------------------------------------------------------------------
# 한글 조사 헬퍼
# ---------------------------------------------------------------------------

def _has_batchim(char):
    """한글 문자에 받침(종성)이 있는지 판별. 비한글은 True 취급."""
    if '가' <= char <= '힣':
        return (ord(char) - 0xAC00) % 28 != 0
    # 숫자: 0,1,3,6,7,8 → 받침 있음
    if char.isdigit():
        return char in '01367'
    return True  # 영문 등은 받침 있는 것으로


def _josa(word, josa_pair):
    """단어 뒤에 올바른 조사를 붙여 반환.
    josa_pair: ('이', '가'), ('은', '는'), ('을', '를'), ('과', '와'), ('으로', '로')
    """
    if not word:
        return word + josa_pair[0]
    last = word.rstrip()[-1]
    has = _has_batchim(last)
    # 으로/로 특수: ㄹ받침이면 '로'
    if josa_pair == ('으로', '로'):
        if '가' <= last <= '힣' and (ord(last) - 0xAC00) % 28 == 8:  # ㄹ
            return word + '로'
        return word + (josa_pair[0] if has else josa_pair[1])
    return word + (josa_pair[0] if has else josa_pair[1])


# ---------------------------------------------------------------------------
# 워딩 생성
# ---------------------------------------------------------------------------

def _pct_to_float(pct_str):
    """비율 문자열 → float. '-' 또는 빈값 → 0."""
    if not pct_str or pct_str == "-":
        return 0.0
    return float(pct_str.replace("%", ""))


def generate_total_wording(block):
    """전체 섹션 워딩 생성."""
    total = block["total_row"]["values"]
    title_text = re.sub(r'\(중복응답\)', '', block["title"]).strip()

    # 카테고리를 비율 기준 내림차순 정렬 (SKIP_CATEGORIES 제외)
    ranked = []
    for cat in block["categories"]:
        if cat in SKIP_CATEGORIES:
            continue
        pct = _pct_to_float(total[cat]["pct"])
        if pct <= 0:
            continue
        ranked.append((cat, total[cat]["pct"], pct))

    ranked.sort(key=lambda x: x[2], reverse=True)

    if not ranked:
        return []

    lines = []

    # 조사 적용 헬퍼
    title_josa = _josa(title_text, ('으로', '로'))
    top1 = ranked[0][0]
    top1_josa_ig = _josa(top1, ('이', '가'))

    # 첫 bullet: 순위별 기술
    if len(ranked) == 1:
        sentence = f"{title_josa} {top1_josa_ig} {ranked[0][1]}로 나타남"
    elif len(ranked) <= 3:
        parts = [f"{top1_josa_ig} {ranked[0][1]}로 가장 높았으며"]
        for r in ranked[1:]:
            parts.append(f"{r[0]} {r[1]}")
        sentence = f"{title_josa} {', '.join(parts)} 순이었음"
    else:
        parts = [f"{top1_josa_ig} {ranked[0][1]}로 가장 높았으며"]
        for r in ranked[1:3]:
            parts.append(f"{r[0]} {r[1]}")
        sentence = f"{title_josa} {', '.join(parts)} 등의 순이었음"

    lines.append(f"* {sentence}")

    # 두 번째 bullet: 상위 2항목 합산 ≥ 50%
    if len(ranked) >= 2:
        top2_sum = ranked[0][2] + ranked[1][2]
        if top2_sum >= 50.0:
            t0_gwa = _josa(ranked[0][0], ('과', '와'))
            t1_eul = _josa(ranked[1][0], ('을', '를'))
            lines.append(
                f"* {t0_gwa} {t1_eul} 합산하면 "
                f"{top2_sum:.1f}%로, 응답의 절반 이상이 두 항목에 집중되었음"
            )

    return lines


def generate_group_wording(block, threshold=10):
    """특성별 섹션 워딩 생성."""
    total = block["total_row"]["values"]
    lines = []

    for group_name, subgroups in block["groups"].items():
        bullet = _analyze_group(group_name, subgroups, total, block["categories"], threshold)
        if bullet:
            lines.append(f"* {bullet}")

    return lines


def _analyze_group(group_name, subgroups, total_values, categories, threshold):
    """독립변수 하나 분석 → 워딩 문장 반환."""
    # 유효 카테고리만
    valid_cats = [c for c in categories if c not in SKIP_CATEGORIES]

    # 각 하위집단 × 카테고리에서 전체 대비 차이 계산
    diffs = []
    for sg in subgroups:
        for cat in valid_cats:
            total_pct = _pct_to_float(total_values[cat]["pct"])
            sg_pct = _pct_to_float(sg["values"].get(cat, {}).get("pct", "-"))
            diff = abs(sg_pct - total_pct)
            if diff >= threshold and sg_pct > 0:
                diffs.append({
                    "subgroup": sg["name"],
                    "category": cat,
                    "sg_pct": sg["values"][cat]["pct"],
                    "total_pct": total_values[cat]["pct"],
                    "diff": diff,
                    "direction": "높" if sg_pct > total_pct else "낮"
                })

    if not diffs:
        return None

    # 가장 큰 차이 기준으로 문장 생성
    diffs.sort(key=lambda x: x["diff"], reverse=True)
    top = diffs[0]

    # 하위집단이 2개인 경우 → 패턴 A (집단 간 비교)
    if len(subgroups) == 2:
        other = [d for d in diffs if d["subgroup"] != top["subgroup"] and d["category"] == top["category"]]
        if other:
            return (
                f"{group_name}별로는, {top['subgroup']}의 경우 "
                f"{top['category']} 비율이 {top['sg_pct']}인 반면, "
                f"{other[0]['subgroup']}의 경우 "
                f"{other[0]['sg_pct']}로 두 집단 간 차이가 있었음"
            )

    # 하위집단 3개 이상 → 패턴 B (특정 집단 강조)
    return (
        f"{group_name}별로는, {top['subgroup']}의 경우 "
        f"{top['category']} 비율이 {top['sg_pct']}로 "
        f"타 {group_name} 대비 상대적으로 {top['direction']}았음"
    )


# ---------------------------------------------------------------------------
# 보고서 조립
# ---------------------------------------------------------------------------

def build_wording_report(blocks, timestamp):
    """전체 워딩 보고서 생성."""
    lines = []
    lines.append("# 통계 분석 결과 워딩 보고서")
    lines.append("")
    lines.append(f"> **생성일시**: {timestamp}")
    lines.append("")
    lines.append("---")
    lines.append("")

    for block in blocks:
        n_str = f" (N={block['total_n']}, {block['response_type']})" if block["total_n"] else ""
        lines.append(f"## {block['id']}. {block['title']}{n_str}")
        lines.append("")

        # 전체
        total_lines = generate_total_wording(block)
        if total_lines:
            lines.append("### 전체")
            lines.extend(total_lines)
            lines.append("")

        # 특성별
        group_lines = generate_group_wording(block)
        if group_lines:
            lines.append("### 특성별")
            lines.extend(group_lines)
            lines.append("")

        lines.append("---")
        lines.append("")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# 로그
# ---------------------------------------------------------------------------

def log_execution(log_dir, timestamp, input_file, block_count, elapsed):
    """실행 기록."""
    os.makedirs(log_dir, exist_ok=True)
    csv_path = os.path.join(log_dir, "execution_history.csv")
    header_needed = not os.path.exists(csv_path)
    with open(csv_path, "a", encoding="utf-8") as f:
        if header_needed:
            f.write("timestamp,input_file,blocks,elapsed_sec\n")
        f.write(f"{timestamp},{os.path.basename(input_file)},{block_count},{elapsed:.1f}\n")


# ---------------------------------------------------------------------------
# 메인
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="교차표 MD → 보고서 워딩 자동 생성")
    parser.add_argument("--input", "-i", required=True, help="입력 _cross.md 파일 경로")
    parser.add_argument("--output-dir", "-o", default=None, help="출력 디렉토리 (기본: 입력 디렉토리/wording/)")
    parser.add_argument("--exclude", "-e", nargs="*", default=[], help="제외할 문항번호 (예: A2)")
    parser.add_argument("--threshold", "-t", type=float, default=10.0, help="특성별 감지 임계값(%%p, 기본: 10)")
    args = parser.parse_args()

    input_path = os.path.abspath(args.input)
    if not os.path.exists(input_path):
        print(f"[ERROR] 파일을 찾을 수 없습니다: {input_path}")
        sys.exit(1)

    # 출력 디렉토리
    if args.output_dir:
        output_dir = os.path.abspath(args.output_dir)
    else:
        output_dir = os.path.join(os.path.dirname(input_path), "wording")
    os.makedirs(output_dir, exist_ok=True)

    # config.py 로드
    script_dir = os.path.dirname(os.path.abspath(__file__))
    log_dir = os.path.join(os.path.dirname(script_dir), "logs")
    config_path = os.path.join(script_dir, "config.py")
    if os.path.exists(config_path):
        import importlib.util
        spec = importlib.util.spec_from_file_location("config", config_path)
        cfg_mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cfg_mod)
        if hasattr(cfg_mod, "CONFIG"):
            if "exclude_items" in cfg_mod.CONFIG:
                args.exclude = list(set(args.exclude + cfg_mod.CONFIG["exclude_items"]))
            if "threshold" in cfg_mod.CONFIG and args.threshold == 10.0:
                args.threshold = cfg_mod.CONFIG["threshold"]

    # 타임스탬프
    now = datetime.now()
    timestamp = now.strftime("%y%m%d_%H%M")

    # 출력 파일명: 입력 파일명에서 _cross 제거 → wording_ 접두사
    stem = Path(input_path).stem
    stem = re.sub(r'_cross$', '', stem)
    stem = re.sub(r'^report_', '', stem)
    out_name = f"wording_{stem}_{timestamp}.md"

    print(f"[INPUT]  {input_path}")
    print(f"[OUTPUT] {output_dir}")
    print(f"[TIME]   {timestamp}")
    print(f"[THRESHOLD] {args.threshold}%p")
    if args.exclude:
        print(f"[SKIP]   {', '.join(args.exclude)}")
    print()

    # 1. 파싱
    start_time = time.time()
    print("[INFO] 교차표 MD 파싱 중...")
    blocks = parse_cross_md(input_path)
    print(f"   {len(blocks)}개 블록 파싱 완료")

    # 2. 제외 항목 필터
    if args.exclude:
        filtered = []
        for b in blocks:
            skip = False
            for ex in args.exclude:
                if b["id"].startswith(ex):
                    print(f"   [SKIP] {b['id']}. {b['title']}")
                    skip = True
                    break
            if not skip:
                filtered.append(b)
        blocks = filtered

    print(f"   {len(blocks)}개 블록 워딩 대상")
    print()

    # 3. 워딩 생성
    print("[INFO] 워딩 생성 중...")
    report = build_wording_report(blocks, timestamp)

    # 4. 저장
    out_path = os.path.join(output_dir, out_name)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(report)
    print(f"[SAVED] {out_path}")

    # 5. 로그
    elapsed = time.time() - start_time
    log_execution(log_dir, timestamp, input_path, len(blocks), elapsed)

    print(f"\n[DONE] 완료! ({elapsed:.1f}초)")


if __name__ == "__main__":
    main()
