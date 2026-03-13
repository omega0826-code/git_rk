# -*- coding: utf-8 -*-
"""문경 영순 타당성 보고서 HWPX 파싱 실행 스크립트"""
import sys, io
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
import os

# hwpx_parser.py 경로 추가
sys.path.insert(0, r"d:\git_rk\project\25_121_ulsan\HWPX")

from hwpx_parser import parse_hwpx

HWPX_FILE = os.path.join(
    r"d:\git_rk\project\25_n33_MunKyung\hwpx",
    "문경 영순_타당성 보고서(송부용)_20260217_v4.hwpx"
)
OUTPUT_DIR = r"d:\git_rk\project\25_n33_MunKyung\hwpx\hwpx_parsed"

print(f"[INFO] HWPX 파일: {HWPX_FILE}")
print(f"[INFO] 출력 디렉토리: {OUTPUT_DIR}")
print(f"[INFO] 파일 존재 여부: {os.path.exists(HWPX_FILE)}")
print()

result = parse_hwpx(HWPX_FILE, output_base=OUTPUT_DIR)

print(f"\n{'='*50}")
print(f"HWPX 파싱 완료")
print(f"{'='*50}")
print(f"입력: {result['input_file']}")
print(f"출력: {result['output_dir']}")
print(f"소요: {result['elapsed_seconds']:.1f}초")
print(f"문단: {len(result['paragraphs'])}개")
print(f"제목: {len(result['headings'])}개")
print(f"표:   {len(result['tables'])}개")
print(f"이미지: {len(result['image_refs'])}개")

if result['errors']:
    print(f"\n[경고] 오류 {len(result['errors'])}건:")
    for e in result['errors']:
        print(f"  - {e}")
