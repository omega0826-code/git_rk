# -*- coding: utf-8 -*-
"""
run_body_mod.py - HWPX 본문 수정 통합 파이프라인

3개 모듈(parser → modifier → builder)을 순차 호출하여
원본 HWPX에 수정 사양을 적용한 새 HWPX를 생성합니다.

사용법:
    python run_body_mod.py --input 원본.hwpx --spec config/sample_spec.json --output 결과.hwpx
    python run_body_mod.py --input 원본.hwpx --spec config/sample_spec.json --output 결과.hwpx --parsed parsed.md

옵션:
    --input   : 원본 HWPX 파일 경로 (필수)
    --spec    : 수정 사양 JSON 파일 경로 (필수)
    --output  : 출력 HWPX 파일 경로 (필수)
    --parsed  : 파싱 결과 마크다운 출력 경로 (선택, 기본값: 생성 안 함)
"""
import sys, io, os, json, argparse, logging
from datetime import datetime

# UTF-8 출력 보장
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# 모듈 경로 추가
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from modules.parser import parse_hwpx, export_to_markdown
from modules.modifier import apply_modifications
from modules.builder import add_charpr_style, build_hwpx


def setup_logging():
    """로그 디렉토리에 타임스탬프 파일로 로깅 설정"""
    log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs')
    os.makedirs(log_dir, exist_ok=True)
    timestamp = datetime.now().strftime('%y%m%d_%H%M')
    log_path = os.path.join(log_dir, f'run_{timestamp}.log')

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(message)s',
        handlers=[
            logging.FileHandler(log_path, encoding='utf-8'),
            logging.StreamHandler(sys.stdout),
        ]
    )
    return log_path


def main():
    arg_parser = argparse.ArgumentParser(description='HWPX 본문 수정 통합 파이프라인')
    arg_parser.add_argument('--input', required=True, help='원본 HWPX 파일 경로')
    arg_parser.add_argument('--spec', required=True, help='수정 사양 JSON 파일 경로')
    arg_parser.add_argument('--output', required=True, help='출력 HWPX 파일 경로')
    arg_parser.add_argument('--parsed', default=None, help='파싱 결과 마크다운 출력 경로 (선택)')
    args = arg_parser.parse_args()

    log_path = setup_logging()
    logger = logging.getLogger(__name__)

    logger.info("=" * 60)
    logger.info("HWPX 본문 수정 파이프라인 시작")
    logger.info("=" * 60)

    # ── ① 파싱/분석 ──
    logger.info(f"[1/3] 파싱: {args.input}")
    parsed = parse_hwpx(args.input)
    logger.info(f"  charPr: {len(parsed['char_properties'])}개")
    logger.info(f"  paraPr: {len(parsed['para_properties'])}개")
    logger.info(f"  섹션: {len(parsed['sections'])}개")

    if args.parsed:
        export_to_markdown(parsed, args.parsed)
        logger.info(f"  마크다운 출력: {args.parsed}")

    # ── 수정 사양 로드 ──
    with open(args.spec, 'r', encoding='utf-8') as f:
        spec = json.load(f)

    target_section = spec.get('target_section', 'Contents/section1.xml')
    rules = [r for r in spec.get('rules', []) if 'action' in r]  # _comment 항목 제외
    new_styles = spec.get('new_styles', [])

    logger.info(f"  수정 대상: {target_section}")
    logger.info(f"  규칙 수: {len(rules)}개")
    logger.info(f"  신규 스타일: {len(new_styles)}개")

    # ── ② 본문 수정 ──
    modified_files = {}
    header_bytes = parsed['header_bytes']
    new_charpr_id = None

    # 신규 스타일 추가
    for style_def in new_styles:
        if style_def.get('type') == 'charPr':
            header_bytes, new_charpr_id = add_charpr_style(
                header_bytes,
                style_def['base_id'],
                style_def['changes']
            )
            logger.info(f"[2/3] 스타일 추가: charPr id={new_charpr_id}")

    modified_files['Contents/header.xml'] = header_bytes

    # section 수정
    if target_section in parsed['sections']:
        section_bytes = parsed['sections'][target_section]
        modified_section = apply_modifications(
            section_bytes,
            rules,
            new_charpr_id=new_charpr_id or "0"
        )
        modified_files[target_section] = modified_section
        logger.info(f"  {target_section} 수정 완료")
    else:
        logger.error(f"  {target_section}을 찾을 수 없습니다!")
        sys.exit(1)

    # ── ③ HWPX 빌드 ──
    logger.info(f"[3/3] 빌드: {args.output}")
    build_hwpx(args.input, args.output, modified_files)
    logger.info("  빌드 완료!")

    logger.info("=" * 60)
    logger.info(f"[OK] 결과: {args.output}")
    logger.info(f"[LOG] {log_path}")
    logger.info("=" * 60)


if __name__ == '__main__':
    main()
