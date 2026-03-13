# -*- coding: utf-8 -*-
"""
run_chart.py — 차트 개별 파이프라인
chart/ 폴더에서 단독 실행 또는 run_ppt.py에서 import 호출 가능
"""
import sys, os, io, re, argparse, logging
from pathlib import Path
from datetime import datetime

# 인코딩 설정
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# automation 루트를 sys.path에 추가 (parser import용)
_AUTOMATION_ROOT = str(Path(__file__).resolve().parent.parent.parent)
if _AUTOMATION_ROOT not in sys.path:
    sys.path.insert(0, _AUTOMATION_ROOT)

import pandas as pd
from chart_builder import Builder
from chart_rules import detect_chart_type

from parser.parser_xls import find_tables, extract_bar_data, load_xls, get_table_ranges
from parser.parser_md import parse_md_sections, get_bar_data_md


# ── 로거 ─────────────────────────────────────────────
def setup_logger(module_name):
    log_dir = os.path.join(os.path.dirname(__file__), '..', 'logs')
    os.makedirs(log_dir, exist_ok=True)
    ts = datetime.now().strftime('%y%m%d_%H%M')
    log_path = os.path.join(log_dir, f"{ts}_{module_name}.log")

    logger = logging.getLogger(module_name)
    logger.setLevel(logging.INFO)
    fh = logging.FileHandler(log_path, encoding='utf-8')
    fh.setFormatter(logging.Formatter('[%(asctime)s] [%(levelname)-5s] %(message)s', datefmt='%Y-%m-%d %H:%M:%S'))
    logger.addHandler(fh)
    sh = logging.StreamHandler()
    sh.setFormatter(logging.Formatter('[%(levelname)-5s] %(message)s'))
    logger.addHandler(sh)
    return logger


# ── 스킵 패턴 ──────────────────────────────────────
DEFAULT_SKIP = ['불만족 이유', '프로그램별 만족도']


# ── XLS 처리 ─────────────────────────────────────────
def generate_from_xls(input_path, theme_path, sort_mode, skip_patterns, log):
    df = load_xls(input_path)
    log.info(f"데이터: {df.shape[0]}행 x {df.shape[1]}열")

    tables = find_tables(df)
    log.info(f"탐지된 테이블: {len(tables)}개")

    ranges = get_table_ranges(df, tables)

    # 스킵 필터
    filtered = []
    for row, title, next_row in ranges:
        if any(pat in title for pat in skip_patterns):
            log.info(f"  SKIP (패턴): {title}")
            continue
        filtered.append((row, title, next_row))

    log.info(f"차트 생성 대상: {len(filtered)}개")

    builder = Builder(theme_path=theme_path)
    total = len(filtered)
    ok = 0

    for row, title, next_row in filtered:
        pg = ok + 1
        clean_title = re.sub(r'^[■\s]+', '', title).strip()

        try:
            labels, pcts, freqs, n = extract_bar_data(df, row, next_row)
            flt = [(l, p, f) for l, p, f in zip(labels, pcts, freqs) if p > 0]

            if not flt:
                log.info(f"  SKIP 표 {pg} {clean_title[:40]} -> 데이터 없음")
                continue

            fl, fp, ff = zip(*flt)
            fl, fp, ff = list(fl), list(fp), list(ff)

            chart_type, method = detect_chart_type(clean_title, fl, fp, ff, n)
            getattr(builder, method)(fl, fp, ff, n, clean_title, pg, total, sort=sort_mode) if method == 'add_hbar' \
                else getattr(builder, method)(fl, fp, ff, n, clean_title, pg, total)

            log.info(f"  OK   표 {pg} {clean_title[:40]} -> {chart_type} ({len(fl)}항목)")
            ok += 1

        except Exception as e:
            log.error(f"  FAIL 표 {pg} {clean_title[:40]} -> {e}")

    return builder, ok, total


# ── MD 처리 ──────────────────────────────────────────
def generate_from_md(input_path, theme_path, sort_mode, skip_patterns, log):
    sections = parse_md_sections(input_path)
    log.info(f"탐지된 섹션: {len(sections)}개")

    builder = Builder(theme_path=theme_path)
    total = len(sections)
    ok = 0

    for idx in sorted(sections.keys()):
        sec = sections[idx]
        title = sec['title']
        pg = ok + 1

        if any(pat in title for pat in skip_patterns):
            log.info(f"  SKIP (패턴): {title}")
            continue

        try:
            labels, pcts, freqs, n = get_bar_data_md(sec)
            flt = [(l, p, f) for l, p, f in zip(labels, pcts, freqs) if p > 0]

            if not flt:
                log.info(f"  SKIP 섹션 {idx} {title[:40]} -> 데이터 없음")
                continue

            fl, fp, ff = zip(*flt)
            fl, fp, ff = list(fl), list(fp), list(ff)

            chart_type, method = detect_chart_type(title, fl, fp, ff, n)
            getattr(builder, method)(fl, fp, ff, n, title, pg, total, sort=sort_mode) if method == 'add_hbar' \
                else getattr(builder, method)(fl, fp, ff, n, title, pg, total)

            log.info(f"  OK   섹션 {idx} {title[:40]} -> {chart_type} ({len(fl)}항목)")
            ok += 1

        except Exception as e:
            log.error(f"  FAIL 섹션 {idx} {title[:40]} -> {e}")

    return builder, ok, total


# ── 공용 엔트리 ──────────────────────────────────────
def generate(input_path, output_path=None, theme="white_clean", sort="desc", skip=None):
    """run_ppt.py 에서 호출하는 인터페이스"""
    log = setup_logger("chart")
    start = datetime.now()

    theme_dir = os.path.join(os.path.dirname(__file__), 'themes')
    theme_path = os.path.join(theme_dir, f"{theme}.json")
    if not os.path.exists(theme_path):
        theme_path = os.path.join(theme_dir, "white_clean.json")

    skip_patterns = skip.split(',') if skip else DEFAULT_SKIP
    ext = Path(input_path).suffix.lower()

    sorts = [True, False] if sort == "both" else [sort != "original"]
    results = []

    for sort_mode in sorts:
        mode_str = "정렬" if sort_mode else "원본순서"
        log.info(f"실행 시작: chart [{mode_str}]")
        log.info(f"입력: {input_path}")
        log.info(f"테마: {theme}")

        if ext in ('.xls', '.xlsx'):
            builder, ok, total = generate_from_xls(input_path, theme_path, sort_mode, skip_patterns, log)
        elif ext == '.md':
            builder, ok, total = generate_from_md(input_path, theme_path, sort_mode, skip_patterns, log)
        else:
            log.error(f"지원하지 않는 파일 형식: {ext}")
            continue

        if output_path:
            out = output_path
        else:
            ts = datetime.now().strftime('%y%m%d_%H%M')
            base = Path(input_path).stem
            suffix = f"_{mode_str}"
            out = str(Path(input_path).parent / f"{base}_차트{suffix}_{ts}.pptx")

        builder.save(out)
        elapsed = (datetime.now() - start).total_seconds()
        log.info(f"생성 완료: {ok}장 -> {out}")
        log.info(f"소요시간: {elapsed:.1f}초")

        # 검증
        from pptx import Presentation
        try:
            t = Presentation(out)
            log.info(f"검증 통과: {len(t.slides)}장 로드 성공")
        except Exception as e:
            log.error(f"검증 실패: {e}")

        results.append(out)

    return results


# ── CLI ──────────────────────────────────────────────
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="차트 자동 생성 파이프라인")
    parser.add_argument("--input", "-i", required=True, help="입력 파일 (.xls/.xlsx/.md)")
    parser.add_argument("--output", "-o", help="출력 파일명 (미지정시 자동생성)")
    parser.add_argument("--theme", "-t", default="white_clean", help="테마명 (default: white_clean)")
    parser.add_argument("--sort", "-s", default="desc", choices=["desc", "original", "both"],
                        help="정렬 옵션: desc(내림차순), original(원본), both(2종)")
    parser.add_argument("--skip", help="스킵할 키워드 (쉼표 구분)")
    args = parser.parse_args()

    generate(args.input, args.output, args.theme, args.sort, args.skip)
