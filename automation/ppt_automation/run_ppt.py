# -*- coding: utf-8 -*-
"""
run_ppt.py — PPT 자동화 통합 파이프라인
모든 모듈(chart, table, wording)을 조합하여 실행
"""
import sys, io, os, argparse, importlib
from pathlib import Path
from datetime import datetime

if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# 모듈 레지스트리 ─ 새 모듈 추가 시 여기에 등록
MODULES = {
    "chart": "chart.run_chart",
    # "table":   "table.run_table",     # 향후 구현
    # "wording": "wording.run_wording", # 향후 구현
}

# automation 루트를 sys.path에 추가
_AUTOMATION_ROOT = str(Path(__file__).resolve().parent.parent)
if _AUTOMATION_ROOT not in sys.path:
    sys.path.insert(0, _AUTOMATION_ROOT)


def run_module(mod_name, input_path, output_path, theme, sort, skip):
    """개별 모듈 실행"""
    if mod_name not in MODULES:
        print(f"[ERROR] 알 수 없는 모듈: {mod_name}")
        print(f"  사용 가능: {', '.join(MODULES.keys())}")
        return []

    mod = importlib.import_module(MODULES[mod_name])
    return mod.generate(input_path, output_path, theme, sort, skip)


def main():
    parser = argparse.ArgumentParser(description="PPT 자동화 통합 파이프라인")
    parser.add_argument("--module", "-m", default="chart",
                        help="실행할 모듈 (chart,table,wording 또는 all)")
    parser.add_argument("--input", "-i", required=True, help="입력 파일")
    parser.add_argument("--output", "-o", help="출력 파일명")
    parser.add_argument("--theme", "-t", default="white_clean", help="테마명")
    parser.add_argument("--sort", "-s", default="desc",
                        choices=["desc", "original", "both"])
    parser.add_argument("--skip", help="스킵할 키워드 (쉼표 구분)")
    args = parser.parse_args()

    print("=" * 60)
    print("  PPT Automation — 통합 파이프라인")
    print("=" * 60)

    modules = list(MODULES.keys()) if args.module == "all" else args.module.split(",")
    all_results = []

    for mod_name in modules:
        mod_name = mod_name.strip()
        print(f"\n[MODULE] {mod_name}")
        results = run_module(mod_name, args.input, args.output, args.theme, args.sort, args.skip)
        all_results.extend(results)

    print(f"\n{'=' * 60}")
    print(f"  완료: {len(all_results)}개 파일 생성")
    for r in all_results:
        print(f"  -> {r}")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()
