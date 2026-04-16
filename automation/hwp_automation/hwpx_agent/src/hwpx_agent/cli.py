from __future__ import annotations

import argparse
import json

from .assetizer import HwpxAssetizer


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="HWPX 문서를 자산 구조로 분해합니다.")
    parser.add_argument("--input", required=True, help="입력 HWPX 파일 경로")
    parser.add_argument("--output-root", help="실행 결과 루트 폴더")
    parser.add_argument("--run-name", help="실행 이름. 비우면 파일명 기반으로 생성")
    parser.add_argument("--no-copy-source", action="store_true", help="source 폴더에 원본 HWPX를 복사하지 않음")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    assetizer = HwpxAssetizer(
        hwpx_path=args.input,
        output_root=args.output_root,
        run_name=args.run_name,
        copy_source=not args.no_copy_source
    )
    result = assetizer.run()

    summary = {
        "run_name": result["run_name"],
        "run_dir": result["run_dir"],
        "counts": result["document"]["counts"],
        "package": result["document"]["package"],
        "page_summary": result["document"]["page_summary"]
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0
