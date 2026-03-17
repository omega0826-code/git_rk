# -*- coding: utf-8 -*-
"""
sps_to_md.py - SPSS Syntax → Markdown 변환 도구

SPSS 구문 파일(.sps)을 마크다운(.md) 형식으로 변환합니다.
- 인코딩 자동 감지 (CP949 / UTF-8)
- 메타 정보 (원본 파일명, 인코딩, 변환 시각) 포함
- 배치 모드: 디렉토리 내 모든 .sps 파일 일괄 변환

사용법:
    python sps_to_md.py input.sps [-o output.md]
    python sps_to_md.py input_dir/ --batch [-o output_dir/]

Version: 1.0.0
Created: 2026-02-26
"""

import argparse
import os
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional, Tuple


# ═══════════════════════════════════════════════════════════════
# 상수
# ═══════════════════════════════════════════════════════════════

VERSION = "1.0.0"
SUPPORTED_ENCODINGS = ["utf-8-sig", "utf-8", "cp949", "euc-kr", "latin-1"]
ENCODING_COMMENT_PATTERN = re.compile(
    r"^\*\s*Encoding:\s*(.+)\.\s*$", re.IGNORECASE
)


# ═══════════════════════════════════════════════════════════════
# 인코딩 감지
# ═══════════════════════════════════════════════════════════════


def detect_encoding(file_path: str) -> str:
    """SPS 파일의 인코딩을 자동 감지.

    감지 우선순위:
        1. UTF-8 BOM (0xEF 0xBB 0xBF)
        2. 파일 내 '* Encoding: ...' 주석 참조
        3. UTF-8 디코딩 시도
        4. CP949 fallback

    Args:
        file_path: SPS 파일 경로

    Returns:
        감지된 인코딩 문자열 (예: 'utf-8', 'cp949')
    """
    with open(file_path, "rb") as f:
        raw = f.read()

    # 1. BOM 확인
    if raw[:3] == b"\xef\xbb\xbf":
        return "utf-8-sig"

    # 2. 파일 내 Encoding 주석 확인 (ASCII 범위 내에서 검색)
    header = raw[:500]
    try:
        header_text = header.decode("ascii", errors="ignore")
        match = ENCODING_COMMENT_PATTERN.search(header_text)
        if match:
            declared = match.group(1).strip().lower()
            # SPSS에서 선언한 인코딩과 실제 인코딩이 다를 수 있음
            # UTF-8 선언인데 실제로 CP949인 경우 처리
            if "utf" in declared:
                try:
                    raw.decode("utf-8")
                    return "utf-8"
                except UnicodeDecodeError:
                    pass
            if "949" in declared or "euc" in declared or "korean" in declared:
                return "cp949"
    except Exception:
        pass

    # 3. UTF-8 시도
    try:
        raw.decode("utf-8")
        return "utf-8"
    except UnicodeDecodeError:
        pass

    # 4. CP949 fallback
    try:
        raw.decode("cp949")
        return "cp949"
    except UnicodeDecodeError:
        pass

    # 5. 최종 fallback
    return "latin-1"


# ═══════════════════════════════════════════════════════════════
# 변환 핵심 로직
# ═══════════════════════════════════════════════════════════════


def read_sps_file(
    file_path: str, encoding: Optional[str] = None
) -> Tuple[str, str, str]:
    """SPS 파일을 읽어 텍스트, 인코딩, 줄바꿈 패턴을 반환.

    바이너리 모드로 읽어 줄바꿈 패턴을 정확히 감지합니다.

    Args:
        file_path: SPS 파일 경로
        encoding: 인코딩 지정 (None이면 자동 감지)

    Returns:
        (파일 텍스트, 사용된 인코딩, 줄바꿈 패턴 'CRLF'|'LF')
    """
    if encoding is None:
        encoding = detect_encoding(file_path)

    with open(file_path, "rb") as f:
        raw = f.read()

    # 줄바꿈 패턴 감지
    crlf_count = raw.count(b"\r\n")
    lf_only_count = raw.count(b"\n") - crlf_count
    line_ending = "CRLF" if crlf_count >= lf_only_count else "LF"

    text = raw.decode(encoding)

    return text, encoding, line_ending


def generate_title(file_path: str) -> str:
    """파일명에서 마크다운 제목을 생성.

    Args:
        file_path: 파일 경로

    Returns:
        제목 문자열 (확장자 및 타임스탬프 제거)
    """
    stem = Path(file_path).stem
    # 파일명 끝의 _YYYYMMDD_HHMMSS 패턴 제거
    stem = re.sub(r"_\d{6}_\d{4}$", "", stem)
    return stem


def sps_to_markdown(
    file_path: str,
    encoding: Optional[str] = None,
    title: Optional[str] = None,
) -> str:
    """SPS 파일을 마크다운 문자열로 변환.

    Args:
        file_path: 입력 SPS 파일 경로
        encoding: 인코딩 지정 (None이면 자동 감지)
        title: 마크다운 제목 (None이면 파일명에서 생성)

    Returns:
        마크다운 형식의 문자열
    """
    text, used_encoding, line_ending = read_sps_file(file_path, encoding)

    # 텍스트를 LF로 정규화 (마크다운은 항상 LF)
    normalized_text = text.replace("\r\n", "\n")

    file_name = Path(file_path).name

    if title is None:
        title = generate_title(file_path)

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # 헤더 부분
    header_lines = [
        f"# {title}",
        "",
        f"> **원본 파일**: `{file_name}`  ",
        f"> **원본 인코딩**: `{used_encoding}`  ",
        f"> **줄바꿈**: `{line_ending}`  ",
        f"> **변환 시각**: {now}",
        "",
    ]
    header = "\n".join(header_lines) + "\n"

    # 코드 블록: 구분자 \n과 원본 텍스트의 \n이 혼합되지 않도록 직접 구성
    # ```sps\n 뒤에 원본 텍스트, 원본 텍스트 바로 뒤에 \n```
    code_block = f"```sps\n{normalized_text}\n```\n"

    return header + code_block


def convert_file(
    input_path: str,
    output_path: Optional[str] = None,
    encoding: Optional[str] = None,
    title: Optional[str] = None,
) -> str:
    """SPS 파일을 MD 파일로 변환 후 저장.

    Args:
        input_path: 입력 SPS 파일 경로
        output_path: 출력 MD 파일 경로 (None이면 같은 위치에 .md로 생성)
        encoding: 입력 인코딩 지정 (None이면 자동 감지)
        title: 마크다운 제목

    Returns:
        생성된 MD 파일 경로
    """
    if output_path is None:
        output_path = str(Path(input_path).with_suffix(".md"))

    md_content = sps_to_markdown(input_path, encoding=encoding, title=title)

    # 출력 디렉토리 생성
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(md_content)

    return output_path


def convert_batch(
    input_dir: str,
    output_dir: Optional[str] = None,
    encoding: Optional[str] = None,
) -> list:
    """디렉토리 내 모든 SPS 파일을 MD로 일괄 변환.

    Args:
        input_dir: 입력 디렉토리 경로
        output_dir: 출력 디렉토리 경로 (None이면 입력 디렉토리와 동일)
        encoding: 인코딩 지정 (None이면 파일별 자동 감지)

    Returns:
        변환된 파일 경로 리스트
    """
    if output_dir is None:
        output_dir = input_dir

    os.makedirs(output_dir, exist_ok=True)

    results = []
    sps_files = sorted(Path(input_dir).glob("*.sps"))

    if not sps_files:
        print(f"[WARNING] .sps 파일이 없습니다: {input_dir}")
        return results

    for sps_file in sps_files:
        out_path = os.path.join(output_dir, sps_file.stem + ".md")
        try:
            result = convert_file(str(sps_file), out_path, encoding=encoding)
            results.append(result)
            print(f"  [OK] {sps_file.name} → {Path(result).name}")
        except Exception as e:
            print(f"  [ERROR] {sps_file.name}: {e}")

    return results


# ═══════════════════════════════════════════════════════════════
# CLI
# ═══════════════════════════════════════════════════════════════


def build_parser() -> argparse.ArgumentParser:
    """CLI 인자 파서를 생성."""
    parser = argparse.ArgumentParser(
        description="SPSS Syntax (.sps) → Markdown (.md) 변환 도구",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""\
사용 예시:
  # 단일 파일 변환
  python sps_to_md.py input.sps -o output.md

  # 자동 파일명 (input.md)
  python sps_to_md.py input.sps

  # 인코딩 명시 지정
  python sps_to_md.py input.sps --encoding cp949

  # 배치 모드 (디렉토리 내 모든 .sps)
  python sps_to_md.py ./macro_dir/ --batch -o ./md_output/
""",
    )
    parser.add_argument(
        "input",
        help="입력 SPS 파일 또는 디렉토리 경로",
    )
    parser.add_argument(
        "-o", "--output",
        default=None,
        help="출력 MD 파일 또는 디렉토리 경로 (기본: 입력과 동일 위치)",
    )
    parser.add_argument(
        "--encoding",
        default=None,
        help="입력 파일 인코딩 지정 (기본: 자동 감지)",
    )
    parser.add_argument(
        "--title",
        default=None,
        help="마크다운 제목 (기본: 파일명에서 생성)",
    )
    parser.add_argument(
        "--batch",
        action="store_true",
        help="배치 모드: 디렉토리 내 모든 .sps 파일 변환",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"sps_to_md v{VERSION}",
    )
    return parser


def main() -> None:
    """CLI 진입점."""
    parser = build_parser()
    args = parser.parse_args()

    input_path = os.path.abspath(args.input)

    if args.batch or os.path.isdir(input_path):
        # 배치 모드
        output_dir = os.path.abspath(args.output) if args.output else None
        print(f"[BATCH] 디렉토리 변환: {input_path}")
        results = convert_batch(input_path, output_dir, encoding=args.encoding)
        print(f"\n완료: {len(results)}개 파일 변환됨")
    else:
        # 단일 파일 모드
        if not os.path.isfile(input_path):
            print(f"[ERROR] 파일을 찾을 수 없습니다: {input_path}")
            sys.exit(1)

        output_path = os.path.abspath(args.output) if args.output else None
        result = convert_file(
            input_path, output_path, encoding=args.encoding, title=args.title
        )
        print(f"[OK] 변환 완료: {result}")


if __name__ == "__main__":
    main()
