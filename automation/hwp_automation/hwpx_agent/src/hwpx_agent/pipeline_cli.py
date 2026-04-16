from __future__ import annotations

import argparse
import json

from .pipeline import HwpxPipelineRunner


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="HWPX 문서를 자산화하고, 교정 이슈와 리뷰 파일까지 한 번에 생성합니다."
    )
    parser.add_argument("--input", required=True, help="입력 HWPX 파일 경로")
    parser.add_argument("--output-root", help="실행 결과 루트 폴더")
    parser.add_argument("--run-name", help="실행 이름. 비우면 파일명 기반으로 생성")
    parser.add_argument("--no-copy-source", action="store_true", help="source 폴더에 원본 HWPX를 복사하지 않음")
    parser.add_argument("--include-spell", action="store_true", help="가능하면 맞춤법 검사도 함께 실행")
    parser.add_argument("--expected-page-count", type=int, help="기대 페이지 수를 함께 검증")
    parser.add_argument(
        "--require-table-cell-issues",
        action="store_true",
        help="table_cell 이슈가 최소 1건 이상 있는지 함께 검증",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    runner = HwpxPipelineRunner(
        input_path=args.input,
        output_root=args.output_root,
        run_name=args.run_name,
        copy_source=not args.no_copy_source,
    )
    result = runner.run(
        include_spell=args.include_spell,
        expected_page_count=args.expected_page_count,
        require_table_cell_issues=args.require_table_cell_issues,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0
