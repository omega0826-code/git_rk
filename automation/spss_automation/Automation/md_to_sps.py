# -*- coding: utf-8 -*-
"""
md_to_sps.py - Markdown → SPSS Syntax 역변환 도구

마크다운(.md) 파일 내 ```sps 코드 블록에서 SPSS 구문을 추출하여
SPS 파일(.sps)로 저장합니다.
- 코드 블록 자동 추출
- 메타 정보에서 원본 인코딩 참조
- 배치 모드: 디렉토리 내 모든 .md 파일 일괄 변환

사용법:
    python md_to_sps.py input.md [-o output.sps] [--encoding cp949]
    python md_to_sps.py input_dir/ --batch [-o output_dir/]

Version: 1.0.0
Created: 2026-02-26
"""

import argparse
import os
import re
import sys
from pathlib import Path
from typing import List, Optional, Tuple


# ═══════════════════════════════════════════════════════════════
# 상수
# ═══════════════════════════════════════════════════════════════

VERSION = "1.0.0"
DEFAULT_ENCODING = "cp949"

# CP949 호환 불가 유니코드 → ASCII 대체 맵
CP949_REPLACE_MAP = {
    "\u2550": "=",   # ═ (이중선)
    "\u2551": "|",   # ║
    "\u00b7": ".",   # · (가운뎃점)
    "\u2013": "-",   # – (en dash)
    "\u2014": "-",   # — (em dash)
    "\u2018": "'",   # ' (왼쪽 작은따옴표)
    "\u2019": "'",   # ' (오른쪽 작은따옴표)
    "\u201c": '"',   # " (왼쪽 큰따옴표)
    "\u201d": '"',   # " (오른쪽 큰따옴표)
}

# 마크다운 코드 블록 패턴 (```sps ... ```)
# sps_to_md.py의 f"```sps\n{text}\n```" 구조에 맞춰
# 시작과 끝의 구분자 \n을 모두 소비하여 원본 텍스트만 캡처
CODE_BLOCK_PATTERN = re.compile(
    r"```sps\n(.*?)\n```",
    re.DOTALL,
)

# 메타 정보에서 원본 인코딩 추출 패턴
META_ENCODING_PATTERN = re.compile(
    r">\s*\*\*원본 인코딩\*\*:\s*`([^`]+)`"
)

# 메타 정보에서 원본 파일명 추출 패턴
META_FILENAME_PATTERN = re.compile(
    r">\s*\*\*원본 파일\*\*:\s*`([^`]+)`"
)

# 메타 정보에서 줄바꿈 패턴 추출
META_LINE_ENDING_PATTERN = re.compile(
    r">\s*\*\*줄바꿈\*\*:\s*`([^`]+)`"
)


# ═══════════════════════════════════════════════════════════════
# 마크다운 파싱
# ═══════════════════════════════════════════════════════════════


def extract_meta_info(md_text: str) -> dict:
    """마크다운 텍스트에서 메타 정보를 추출.

    Args:
        md_text: 마크다운 텍스트

    Returns:
        메타 정보 딕셔너리 {'encoding': str|None, 'filename': str|None, 'line_ending': str|None}
    """
    meta = {"encoding": None, "filename": None, "line_ending": None}

    header = md_text[:800]

    enc_match = META_ENCODING_PATTERN.search(header)
    if enc_match:
        meta["encoding"] = enc_match.group(1).strip()

    fn_match = META_FILENAME_PATTERN.search(header)
    if fn_match:
        meta["filename"] = fn_match.group(1).strip()

    le_match = META_LINE_ENDING_PATTERN.search(header)
    if le_match:
        meta["line_ending"] = le_match.group(1).strip()

    return meta


def extract_sps_content(md_text: str) -> str:
    """마크다운 텍스트에서 SPS 코드 블록 내용을 추출.

    여러 코드 블록이 있을 경우 순서대로 합침.

    Args:
        md_text: 마크다운 텍스트

    Returns:
        추출된 SPSS 구문 텍스트

    Raises:
        ValueError: SPS 코드 블록을 찾을 수 없는 경우
    """
    blocks = CODE_BLOCK_PATTERN.findall(md_text)

    if not blocks:
        raise ValueError("마크다운 파일에서 ```sps 코드 블록을 찾을 수 없습니다.")

    # 여러 블록이 있으면 줄바꿈 2개로 구분하여 합침
    # 정규식의 ```sps\s*\n 패턴이 코드 블록 구분자의 \n까지 소비하므로
    # 캡처된 내용은 원본 텍스트 그대로임 (별도 strip 불필요)
    combined = "\n\n".join(blocks)

    return combined


# ═══════════════════════════════════════════════════════════════
# 변환 핵심 로직
# ═══════════════════════════════════════════════════════════════


def determine_output_encoding(
    md_text: str, user_encoding: Optional[str] = None
) -> str:
    """출력 인코딩을 결정.

    우선순위:
        1. 사용자 지정 인코딩
        2. 마크다운 메타 정보의 원본 인코딩
        3. 기본값 (CP949)

    Args:
        md_text: 마크다운 텍스트
        user_encoding: 사용자가 CLI로 지정한 인코딩

    Returns:
        출력 인코딩 문자열
    """
    if user_encoding:
        return user_encoding

    meta = extract_meta_info(md_text)
    if meta["encoding"]:
        return meta["encoding"]

    return DEFAULT_ENCODING


def _replace_cp949_incompatible(text: str) -> str:
    """CP949 인코딩에서 지원하지 않는 유니코드 문자를 ASCII로 대체.

    Args:
        text: 원본 텍스트

    Returns:
        CP949 호환 텍스트
    """
    for unicode_char, ascii_char in CP949_REPLACE_MAP.items():
        text = text.replace(unicode_char, ascii_char)
    return text


def _strip_define_blank_lines(text: str) -> str:
    """DEFINE...!ENDDEFINE 블록 내부의 빈 줄을 제거.

    SPSS는 DEFINE 블록 안의 빈 줄을 명령 끝으로 해석하여
    매크로 정의 오류가 발생합니다.

    Args:
        text: SPS 텍스트

    Returns:
        빈 줄이 제거된 텍스트
    """
    lines = text.splitlines()
    result = []
    in_define = False
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("DEFINE "):
            in_define = True
            result.append(line)
        elif "!ENDDEFINE" in stripped:
            in_define = False
            result.append(line)
        elif in_define and stripped == "":
            continue
        else:
            result.append(line)
    return "\n".join(result)


def md_to_sps(
    md_text: str,
    encoding: Optional[str] = None,
    strip_define_blanks: bool = False,
) -> Tuple[str, str, str]:
    """마크다운 텍스트를 SPS 구문, 인코딩, 줄바꿈 패턴으로 변환.

    Args:
        md_text: 마크다운 텍스트
        encoding: 출력 인코딩 지정 (None이면 자동 결정)
        strip_define_blanks: True이면 DEFINE 내 빈 줄을 제거

    Returns:
        (SPS 구문 텍스트, 사용된 인코딩, 줄바꿈 패턴)
    """
    sps_content = extract_sps_content(md_text)
    out_encoding = determine_output_encoding(md_text, encoding)

    # CP949 출력 시 호환 불가 유니코드 자동 대체
    if out_encoding.lower().replace("-", "") in ("cp949", "euckr"):
        sps_content = _replace_cp949_incompatible(sps_content)

    # DEFINE 내 빈 줄 제거 (SPSS 매크로 오류 방지)
    if strip_define_blanks:
        sps_content = _strip_define_blank_lines(sps_content)

    meta = extract_meta_info(md_text)
    line_ending = meta.get("line_ending", "CRLF") or "CRLF"

    # 줄바꿈 복원
    if line_ending == "CRLF":
        # LF → CRLF 복원 (이미 CRLF인 것은 건드리지 않음)
        sps_content = sps_content.replace("\r\n", "\n").replace("\n", "\r\n")

    return sps_content, out_encoding, line_ending


def convert_file(
    input_path: str,
    output_path: Optional[str] = None,
    encoding: Optional[str] = None,
    strip_define_blanks: bool = False,
) -> str:
    """MD 파일을 SPS 파일로 변환 후 저장.

    Args:
        input_path: 입력 MD 파일 경로
        output_path: 출력 SPS 파일 경로 (None이면 자동 결정)
        encoding: 출력 인코딩 지정 (None이면 자동 결정)
        strip_define_blanks: True이면 DEFINE 내 빈 줄 제거

    Returns:
        생성된 SPS 파일 경로
    """
    with open(input_path, "r", encoding="utf-8") as f:
        md_text = f.read()

    sps_content, out_encoding, line_ending = md_to_sps(
        md_text, encoding, strip_define_blanks=strip_define_blanks
    )

    # 출력 파일 경로 결정
    if output_path is None:
        meta = extract_meta_info(md_text)
        if meta["filename"]:
            output_path = str(
                Path(input_path).parent / meta["filename"]
            )
        else:
            output_path = str(Path(input_path).with_suffix(".sps"))

    # 출력 디렉토리 생성
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)

    # 바이너리 모드로 쓰기 (줄바꿈 보존)
    with open(output_path, "wb") as f:
        f.write(sps_content.encode(out_encoding))

    return output_path


def convert_batch(
    input_dir: str,
    output_dir: Optional[str] = None,
    encoding: Optional[str] = None,
) -> List[str]:
    """디렉토리 내 모든 MD 파일을 SPS로 일괄 변환.

    Args:
        input_dir: 입력 디렉토리 경로
        output_dir: 출력 디렉토리 경로 (None이면 입력 디렉토리와 동일)
        encoding: 출력 인코딩 지정 (None이면 파일별 자동 결정)

    Returns:
        변환된 파일 경로 리스트
    """
    if output_dir is None:
        output_dir = input_dir

    os.makedirs(output_dir, exist_ok=True)

    results = []
    md_files = sorted(Path(input_dir).glob("*.md"))

    if not md_files:
        print(f"[WARNING] .md 파일이 없습니다: {input_dir}")
        return results

    for md_file in md_files:
        try:
            # MD 파일 읽기
            with open(md_file, "r", encoding="utf-8") as f:
                md_text = f.read()

            # SPS 코드 블록이 있는지 확인
            blocks = CODE_BLOCK_PATTERN.findall(md_text)
            if not blocks:
                print(f"  [SKIP] {md_file.name}: SPS 코드 블록 없음")
                continue

            # 출력 파일명 결정
            meta = extract_meta_info(md_text)
            if meta["filename"]:
                out_name = meta["filename"]
            else:
                out_name = md_file.stem + ".sps"
            out_path = os.path.join(output_dir, out_name)

            result = convert_file(str(md_file), out_path, encoding=encoding)
            results.append(result)
            print(f"  [OK] {md_file.name} → {Path(result).name}")

        except Exception as e:
            print(f"  [ERROR] {md_file.name}: {e}")

    return results


# ═══════════════════════════════════════════════════════════════
# CLI
# ═══════════════════════════════════════════════════════════════


def build_parser() -> argparse.ArgumentParser:
    """CLI 인자 파서를 생성."""
    parser = argparse.ArgumentParser(
        description="Markdown (.md) → SPSS Syntax (.sps) 역변환 도구",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""\
사용 예시:
  # 단일 파일 변환
  python md_to_sps.py input.md -o output.sps

  # 원본 인코딩으로 자동 복원
  python md_to_sps.py input.md

  # UTF-8로 출력
  python md_to_sps.py input.md --encoding utf-8

  # 배치 모드 (디렉토리 내 모든 .md)
  python md_to_sps.py ./md_dir/ --batch -o ./sps_output/
""",
    )
    parser.add_argument(
        "input",
        help="입력 MD 파일 또는 디렉토리 경로",
    )
    parser.add_argument(
        "-o", "--output",
        default=None,
        help="출력 SPS 파일 또는 디렉토리 경로 (기본: 원본 파일명 참조 또는 .sps 확장자)",
    )
    parser.add_argument(
        "--encoding",
        default=None,
        help="출력 인코딩 지정 (기본: 메타 정보 참조 또는 cp949)",
    )
    parser.add_argument(
        "--batch",
        action="store_true",
        help="배치 모드: 디렉토리 내 모든 .md 파일 변환",
    )
    parser.add_argument(
        "--strip-define-blanks",
        action="store_true",
        help="DEFINE 블록 내 빈 줄 제거 (SPSS 매크로 오류 방지)",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"md_to_sps v{VERSION}",
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
            input_path, output_path,
            encoding=args.encoding,
            strip_define_blanks=args.strip_define_blanks,
        )
        print(f"[OK] 변환 완료: {result}")


if __name__ == "__main__":
    main()
