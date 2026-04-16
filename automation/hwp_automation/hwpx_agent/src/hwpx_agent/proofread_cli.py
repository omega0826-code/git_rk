from __future__ import annotations

import argparse
import json

from .proofread import AssetProofreader


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="자산화 결과를 기준으로 교정 이슈를 연결합니다.")
    parser.add_argument("--run-dir", required=True, help="hwpx_agent runs 하위 실행 폴더")
    parser.add_argument("--with-spell", action="store_true", help="kiwipiepy가 설치된 경우 띄어쓰기/미등록어 검사도 수행")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    proofreader = AssetProofreader(args.run_dir)
    result = proofreader.run(include_spell=args.with_spell)

    print(json.dumps({
        "output_dir": result["output_dir"],
        "summary": result["summary"]
    }, ensure_ascii=False, indent=2))
    return 0
