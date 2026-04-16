from __future__ import annotations

import argparse
import json

from .issue_bridge import IssuePlanBridge


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="교정 이슈를 사람이 고른 수정안 기준으로 rebuild plan에 연결합니다.")
    parser.add_argument("--run-dir", required=True, help="hwpx_agent runs 하위 실행 폴더")
    parser.add_argument("--init-review", action="store_true", help="리뷰용 sample/demo 파일 생성")
    parser.add_argument("--review", help="변환할 issue review JSON 파일")
    parser.add_argument("--output", help="생성할 rebuild plan JSON 경로")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    bridge = IssuePlanBridge(args.run_dir)

    if args.init_review:
        result = bridge.init_review_files()
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0

    if not args.review:
        parser.error("--review 또는 --init-review 중 하나는 필요합니다.")

    result = bridge.review_to_rebuild_plan(args.review, output_path=args.output)
    print(json.dumps(result["summary"], ensure_ascii=False, indent=2))
    return 0
