from __future__ import annotations

import argparse
import json

from .rebuild import HwpxRebuilder


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="origin_id 기반 최소 복원 경로를 실행합니다.")
    parser.add_argument("--run-dir", required=True, help="hwpx_agent runs 하위 실행 폴더")
    parser.add_argument("--init-plan", action="store_true", help="sample/demo rebuild plan 파일을 생성")
    parser.add_argument("--plan", help="적용할 rebuild plan JSON 파일")
    parser.add_argument("--output", help="출력 HWPX 파일 경로")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    rebuilder = HwpxRebuilder(args.run_dir)

    if args.init_plan:
        result = rebuilder.init_sample_plans()
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0

    if not args.plan:
        parser.error("--plan 또는 --init-plan 중 하나는 필요합니다.")

    result = rebuilder.rebuild_from_plan(args.plan, output_path=args.output)
    print(json.dumps(result["summary"], ensure_ascii=False, indent=2))
    return 0
