# -*- coding: utf-8 -*-
"""대구한의대 XLS → PPT 차트 생성 예시 (DHU Cobalt 테마)

사용법:
    cd d:\git_rk\automation\ppt_automation\chart
    python -u ..\examples\dhu_cobalt_xls_config.py

생성 결과:
    - 입력 XLS 파일 위치에 _차트_정렬_YYMMDD_HHMM.pptx 생성
    - 입력 XLS 파일 위치에 _차트_원본순서_YYMMDD_HHMM.pptx 생성
"""
import sys, os, io

if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# 차트 모듈 경로 설정
CHART_DIR = os.path.join(os.path.dirname(__file__), '..', 'chart')
os.chdir(CHART_DIR)
sys.path.insert(0, CHART_DIR)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from run_chart import generate

# ── 설정 ──────────────────────────────────────────
# 입력 파일 경로 (수정하여 사용)
INPUT_CORP = r"d:\git_rk\project\26_Korean_Medicine\data\(output)기업체_대구한의대 rise_260310_송부.xls"
INPUT_STUDENT = r"d:\git_rk\project\26_Korean_Medicine\data\(output)재학생_대구한의대 rise_260310_송부.xls"

THEME = "dhu_cobalt"   # 테마: dhu_cobalt | white_clean | dark_premium
SORT = "both"          # 정렬: desc | original | both

if __name__ == "__main__":
    for label, path in [("기업체", INPUT_CORP), ("재학생", INPUT_STUDENT)]:
        if os.path.exists(path):
            print(f"\n{'='*50}")
            print(f"[{label}] {os.path.basename(path)}")
            print(f"{'='*50}")
            results = generate(path, None, THEME, SORT, None)
            print(f"[DONE] Generated: {results}")
        else:
            print(f"[SKIP] {label}: 파일 없음 - {path}")
