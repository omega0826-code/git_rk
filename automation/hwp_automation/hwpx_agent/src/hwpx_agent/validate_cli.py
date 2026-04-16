from __future__ import annotations

import argparse
import json

from .validate import RunValidator


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="run 결과물을 기준으로 기본 검증을 실행합니다.")
    parser.add_argument("--run-dir", required=True, help="hwpx_agent runs 하위 실행 폴더")
    parser.add_argument("--expected-page-count", type=int, help="기대 페이지 수")
    parser.add_argument("--require-proofread", action="store_true", help="proofreading 결과까지 검증")
    parser.add_argument("--require-rebuild", action="store_true", help="rebuilt hwpx까지 검증")
    parser.add_argument("--require-table-cell-issues", action="store_true", help="table_cell 이슈 존재 여부 검증")
    parser.add_argument("--rebuild-hwpx", help="검증할 rebuilt hwpx 경로")
    parser.add_argument("--expect-string", help="rebuilt xml 내부에 있어야 할 문자열")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    validator = RunValidator(args.run_dir)
    report = validator.run(
        expected_page_count=args.expected_page_count,
        require_proofread=args.require_proofread,
        require_rebuild=args.require_rebuild,
        require_table_cell_issues=args.require_table_cell_issues,
        rebuild_hwpx=args.rebuild_hwpx,
        expect_string=args.expect_string
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["status"] != "fail" else 1
