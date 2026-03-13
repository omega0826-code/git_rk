# -*- coding: utf-8 -*-
"""
generate_syntax.py - SPSS 범용 분석 Syntax 자동 생성기

JSON 설정 파일을 기반으로 분석 syntax (.md + .sps)를 자동 생성합니다.

사용법:
    python generate_syntax.py analysis_config.json
    python generate_syntax.py config.json --output-dir d:\\path\\to\\output
    python generate_syntax.py config.json --encoding utf-8

Version: 1.0.0
Created: 2026-02-26
"""

import argparse
import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

VERSION = "1.0.0"

# CP949 호환 불가 유니코드 → ASCII 대체 맵
CP949_REPLACE_MAP: Dict[str, str] = {
    "\u2550": "=",
    "\u2551": "|",
    "\u00b7": ".",
    "\u2013": "-",
    "\u2014": "-",
    "\u2018": "'",
    "\u2019": "'",
    "\u201c": '"',
    "\u201d": '"',
}

# ═══════════════════════════════════════════════════════════════
# 설정 로드
# ═══════════════════════════════════════════════════════════════


def load_config(config_path: str) -> Dict[str, Any]:
    """JSON 설정 파일을 로드하고 기본값을 적용.

    Args:
        config_path: JSON 파일 경로

    Returns:
        검증된 설정 딕셔너리
    """
    with open(config_path, "r", encoding="utf-8") as f:
        config = json.load(f)

    # 필수 키 검증
    required = ["project_name", "banner", "label_sps", "sections"]
    for key in required:
        if key not in config:
            raise ValueError(f"설정 파일에 '{key}' 키가 없습니다.")

    if "variables" not in config["banner"]:
        raise ValueError("banner.variables가 필요합니다.")

    # 기본값 적용
    config.setdefault("version", "1.0.0")
    config.setdefault("encoding", "cp949")
    config["banner"].setdefault("validn_label", "응답수")

    return config


# ═══════════════════════════════════════════════════════════════
# 라벨 SPS 파싱
# ═══════════════════════════════════════════════════════════════


def parse_label_sps(sps_path: str) -> Dict[str, str]:
    """간략 라벨 SPS에서 VARIABLE LABELS를 파싱하여 {변수명: 라벨} 딕셔너리 반환.

    Args:
        sps_path: 라벨 SPS 파일 경로

    Returns:
        {변수명: 라벨텍스트} 딕셔너리
    """
    # 인코딩 자동 감지 (CP949 우선)
    for enc in ("cp949", "utf-8", "euc-kr"):
        try:
            with open(sps_path, "r", encoding=enc) as f:
                text = f.read()
            break
        except (UnicodeDecodeError, LookupError):
            continue
    else:
        raise ValueError(f"라벨 SPS 인코딩을 감지할 수 없습니다: {sps_path}")

    labels: Dict[str, str] = {}
    # VARIABLE LABELS 블록에서 변수명-라벨 추출
    pattern = re.compile(r"^\s+(\S+)\s+'([^']*(?:''[^']*)*)'", re.MULTILINE)
    for m in pattern.finditer(text):
        var_name = m.group(1)
        label_text = m.group(2).replace("''", "'")
        labels[var_name] = label_text

    return labels


# ═══════════════════════════════════════════════════════════════
# SPS 블록 빌더
# ═══════════════════════════════════════════════════════════════


def _escape_sps(text: str) -> str:
    """SPSS 문자열에서 작은따옴표를 이스케이프."""
    return text.replace("'", "''")


def build_header(config: Dict[str, Any]) -> str:
    """SPS 파일 헤더 생성."""
    now = datetime.now().strftime("%Y-%m-%d")
    banner_vars = " + ".join(config["banner"]["variables"])
    lines = [
        "* Encoding: EUC-KR.",
        f"* ===============================================================.",
        f"* {config['project_name']} 통계분석.",
        f"* Version: {config['version']}.",
        f"* Created: {now}.",
        f"* Banner: {banner_vars}.",
        f"* ===============================================================.",
    ]
    return "\n".join(lines)


def build_label_include(config: Dict[str, Any], config_dir: str) -> str:
    """라벨 SPS INCLUDE 또는 인라인 구문 생성.

    라벨 SPS를 읽어서 전체 내용을 인라인으로 삽입합니다.
    """
    label_path = os.path.join(config_dir, config["label_sps"])
    if not os.path.exists(label_path):
        # 절대 경로 시도
        label_path = config["label_sps"]

    for enc in ("cp949", "utf-8", "euc-kr"):
        try:
            with open(label_path, "r", encoding=enc) as f:
                text = f.read()
            break
        except (UnicodeDecodeError, LookupError):
            continue
    else:
        return f"* [WARNING] 라벨 파일을 읽을 수 없습니다: {config['label_sps']}."

    # 헤더 주석 제거 (Encoding, ===== 줄 등)
    lines = text.splitlines()
    content_lines = []
    skip_header = True
    for line in lines:
        stripped = line.strip()
        if skip_header and (stripped.startswith("* ") or stripped == "" or stripped.startswith("*")):
            if "VARIABLE LABELS" in stripped or "VALUE LABELS" in stripped:
                skip_header = False
                content_lines.append(line)
            continue
        skip_header = False
        content_lines.append(line)

    return "\n".join(content_lines)


def build_macro_block(config: Dict[str, Any]) -> str:
    """배너 설정에 맞는 매크로 DEFINE 블록 생성."""
    banner_vars = config["banner"]["variables"]
    banner_plus = "t1+" + "+".join(banner_vars)
    banner_list = " ".join(banner_vars)
    validn = config["banner"]["validn_label"]
    banner_comment = " + ".join(banner_vars)

    macros = f"""****배너: {banner_comment}


DEFINE freg (x=!TOKENS(1))
CTABLES
  /VLABELS VARIABLES=!x DISPLAY=LABEL
  /TABLE BY !x [C][COUNT F40.0]
  /CATEGORIES VARIABLES=!x ORDER=A KEY=VALUE EMPTY=INCLUDE.
!ENDDEFINE.


DEFINE freq (x=!TOKENS(1))
    TABLES
    /PTOTAL=t1'전 체' t2'구 분'
    /TABLE={banner_plus} BY t2+!x
    /STATISTICS=COUNT(t2'' !x'빈도') CPCT(!x'비율' : {banner_list} )
!ENDDEFINE.


DEFINE freqt (x=!CMDEND / a=!CHAREND("/"))
    TABLES
    /PTOTAL=t1'전 체' t2'구 분'
    /TABLE={banner_plus} BY t2+!x
    /STATISTICS=COUNT(t2'' !x'빈도') CPCT(!x'비율' : {banner_list} )
    /title=!a.
!ENDDEFINE.


DEFINE freqm2t (x=!TOKENS(1) / y=!TOKENS(1) / a=!CHAREND('/'))
    TABLES OBS = !y
    /PTOTAL=t1'전 체' t2'구 분'
    /TABLE={banner_plus} BY t2+ !y + !x
    /STATISTICS=COUNT(t2'' !x'빈도') mean( !y (f8.2)) CPCT(!x'비율' : {banner_list} )
    /title=!a.
!ENDDEFINE.


DEFINE m1t (x=!CMDEND / a=!CHAREND("/"))
    !LET !H=!HEAD(!x)
    !LET !T=!TAIL(!x)
    TABLES OBS=!x
    /PTOTAL=t1'전 체'
    /TABLE={banner_plus} BY !H !DO !var !IN (!T) !CONCAT('+',!var) !DOEND
    /STATISTICS=MEAN(!H !DO !var !IN (!T) !CONCAT('(f8.1)',!var) !DOEND (f8.1))
    /title=!a.
!ENDDEFINE.


DEFINE freq2 (x=!TOKENS(1))
    TABLES
    /PTOTAL=t1'전 체' t2'구 분'
    /TABLE={banner_plus} BY t2+!x
    /STATISTICS=COUNT(t2'' !x'빈도').
!ENDDEFINE.


DEFINE freq2t (x=!TOKENS(1) / a=!CHAREND('/'))
    TABLES
    /PTOTAL=t1'전 체' t2'구 분'
    /TABLE={banner_plus} BY t2+!x
    /STATISTICS=COUNT(t2'' !x'빈도')
    /title=!a.
!ENDDEFINE.


DEFINE PR (x=!TOKENS(1) / y=!TOKENS(1) / z=!TOKENS(1) / a=!CHAREND('/'))
    TABLES
    /PTOTAL=t1'전 체' t2'구 분'
    /MRGROUP=!z !a !x TO !y
    /TABLE={banner_plus} BY t2+!z
    /STATISTICS=COUNT(t2'' !z'빈도') CPCT(!z'비율': {banner_list}).
!ENDDEFINE.


DEFINE PRT (x=!TOKENS(1) / y=!TOKENS(1) / z=!TOKENS(1) / a=!CHAREND('/')  / b=!CHAREND('/'))
    TABLES
    /PTOTAL=t1'전 체' t2'구 분'
    /MRGROUP=!z !a !x TO !y
    /TABLE={banner_plus} BY t2+!z
    /STATISTICS=COUNT(t2''  !z'빈도') CPCT(!z'비율': {banner_list})
    /title=!b.
!ENDDEFINE.


DEFINE co (x=!CMD)
    !LET !H=!HEAD(!x)
    !LET !T=!TAIL(!x)
    TABLES OBS=!x
    /PTOTAL=t1'전 체'
    /TABLE={banner_plus} BY !H !DO !var !IN (!T) !CONCAT('+',!var) !DOEND
    /STATISTICS=VALIDN('{validn}')
!ENDDEFINE.


DEFINE cot (x=!CMDEND / a=!CHAREND("/"))
    !LET !H=!HEAD(!x)
    !LET !T=!TAIL(!x)
    TABLES OBS=!x
    /PTOTAL=t1'전 체'
    /TABLE={banner_plus} BY !H !DO !var !IN (!T) !CONCAT('+',!var) !DOEND
    /STATISTICS=VALIDN('{validn}')
    /title=!a.
!ENDDEFINE.


DEFINE cm1t (x=!CMDEND / a=!CHAREND("/"))
    !LET !H=!HEAD(!x)
    !LET !T=!TAIL(!x)
    TABLES OBS=!x
    /PTOTAL=t1'전 체'
    /TABLE={banner_plus} BY !H !DO !var !IN (!T) !CONCAT('+',!var) !DOEND
    /STATISTICS=VALIDN('{validn}') MEAN(!H !DO !var !IN (!T) !CONCAT('(f8.1)',!var) !DOEND (f8.1))
    /title=!a.
!ENDDEFINE."""

    return macros


def _build_filter(filt: Optional[Dict]) -> str:
    """필터 조건 → TEMPORARY + SELECT IF 구문."""
    if not filt:
        return ""
    var = filt["var"]
    op = filt.get("op", "=")
    val = filt["val"]
    return f"TEMPORARY.\nSELECT IF({var}{op}{val})."


def render_item(item: Dict, var_labels: Dict[str, str], group_counter: List[int]) -> str:
    """단일 item을 SPS 구문으로 렌더링.

    Args:
        item: 분석 항목 딕셔너리
        var_labels: 라벨 SPS에서 추출한 변수-라벨 맵
        group_counter: 복수응답 그룹 카운터 (mutable)

    Returns:
        SPS 구문 문자열
    """
    item_type = item.get("type", "freq")
    lines = []

    if item_type == "freq":
        var = item["var"]
        label = item.get("label") or var_labels.get(var, var)
        comment = item.get("comment", f"*{label}.")
        lines.append(comment)
        filt = _build_filter(item.get("filter"))
        if filt:
            lines.append(filt)
        lines.append(f"freqt a='{_escape_sps(label)}' / x={var}.")

    elif item_type == "freq_each":
        prefix = item["prefix"]
        frm = item["from"]
        to = item["to"]
        filt_conf = item.get("filter")
        for i in range(frm, to + 1):
            var = f"{prefix}_{i}"
            label = item.get("label_prefix", "")
            if item.get("auto_label", True):
                label = var_labels.get(var, var)
            filt = _build_filter(filt_conf)
            if filt:
                lines.append(filt)
            lines.append(f"freqt a='{_escape_sps(label)}' / x={var}.")

    elif item_type == "mean":
        var_list = item.get("vars", [])
        if not var_list and "prefix" in item:
            prefix = item["prefix"]
            frm = item["from"]
            to = item["to"]
            var_list = [f"{prefix}_{i}" for i in range(frm, to + 1)]
        label = item.get("label", "평균")
        comment = item.get("comment", f"*{label}.")
        lines.append(comment)
        filt = _build_filter(item.get("filter"))
        if filt:
            lines.append(filt)
        # 8개씩 줄바꿈
        chunks = []
        for j in range(0, len(var_list), 8):
            chunks.append(" ".join(var_list[j:j + 8]))
        var_str = "\n ".join(chunks)
        lines.append(f"cm1t a='{_escape_sps(label)}' /\n x={var_str}.")

    elif item_type == "multi":
        from_var = item["from"]
        to_var = item["to"]
        group = item.get("group", "")
        if not group:
            group_counter[0] += 1
            group = f"mg{group_counter[0]}"
        mr_label = item.get("mr_label", item.get("title", "복수응답"))
        title = item.get("title", mr_label)
        comment = item.get("comment", f"*{title}.")
        lines.append(comment)
        filt = _build_filter(item.get("filter"))
        if filt:
            lines.append(filt)
        lines.append(
            f"PRT b='{_escape_sps(title)}' / "
            f"x={from_var} y={to_var} z={group} a='{_escape_sps(mr_label)}'."
        )

    elif item_type == "scale":
        var = item["var"]
        scale_var = item["scale_var"]
        label = item.get("label") or var_labels.get(var, var)
        comment = item.get("comment", f"*{label}.")
        lines.append(comment)
        filt = _build_filter(item.get("filter"))
        if filt:
            lines.append(filt)
        lines.append(f"freqm2t a='{_escape_sps(label)}' / x={var} y={scale_var}.")

    elif item_type == "recode":
        source_vars = item["source"]
        target_vars = item["target"]
        mapping = item["mapping"]
        recode_pairs = " ".join(f"({k}={v})" for k, v in mapping.items())
        recode_pairs += "(ELSE=SYSMIS)"
        src_str = " TO ".join(source_vars) if len(source_vars) == 2 else " ".join(source_vars)
        tgt_str = " ".join(target_vars)
        lines.append(f"RECODE {src_str} {recode_pairs} INTO\n  {tgt_str}.")
        # 변수 라벨 추가
        if item.get("target_labels"):
            label_lines = ["VARIABLE LABELS"]
            for tvar, tlabel in item["target_labels"].items():
                label_lines.append(f"  {tvar}  '{_escape_sps(tlabel)}'")
            label_lines[-1] += "."
            lines.append("\n".join(label_lines))
        lines.append("EXECUTE.")

    return "\n".join(lines)


# ═══════════════════════════════════════════════════════════════
# 전체 조립
# ═══════════════════════════════════════════════════════════════


def generate(config_path: str, output_dir: Optional[str] = None) -> Tuple[str, str]:
    """분석 설정을 기반으로 MD + SPS 파일을 생성.

    Args:
        config_path: JSON 설정 파일 경로
        output_dir: 출력 디렉토리 (None이면 자동 결정)

    Returns:
        (MD 파일 경로, SPS 파일 경로)
    """
    config = load_config(config_path)
    config_dir = os.path.dirname(os.path.abspath(config_path))

    # 라벨 SPS 파싱
    label_path = os.path.join(config_dir, config["label_sps"])
    if not os.path.exists(label_path):
        label_path = config["label_sps"]
    var_labels = parse_label_sps(label_path)

    # 출력 디렉토리 결정
    if output_dir is None:
        output_dir = config_dir

    os.makedirs(output_dir, exist_ok=True)

    # 출력 파일명 결정
    base_name = config.get("output_name", "analysis")
    md_path = os.path.join(output_dir, f"{base_name}.md")
    sps_path = os.path.join(output_dir, f"{base_name}.sps")

    # ── SPS 내용 조립 ──
    sps_parts = []

    # 1. 헤더
    sps_parts.append(build_header(config))

    # 2. 라벨
    section_num = 1
    sps_parts.append(f"\n\n\n***** {section_num}. 라벨 적용(간략) *****\n\n")
    sps_parts.append(build_label_include(config, config_dir))
    section_num += 1

    # 3. 리코딩 블록 (있는 경우)
    recode_items = []
    for section in config["sections"]:
        for item in section.get("items", []):
            if item.get("type") == "recode":
                recode_items.append(item)

    if recode_items:
        sps_parts.append(f"\n\n\n***** {section_num}. 변수 생성(리코딩) *****\n\n")
        group_counter = [0]
        for item in recode_items:
            sps_parts.append(render_item(item, var_labels, group_counter))
            sps_parts.append("")
        section_num += 1

    # 4. 매크로 정의
    sps_parts.append(f"\n\n\n***** {section_num}. 공통 매크로 정의 *****\n\n")
    sps_parts.append(build_macro_block(config))
    section_num += 1

    # 5. 분석 섹션
    group_counter = [0]
    for section in config["sections"]:
        title = section.get("title", "분석")
        sps_parts.append(f"\n\n\n***** {section_num}. {title} *****\n\n")
        section_num += 1

        for item in section.get("items", []):
            if item.get("type") == "recode":
                continue  # 이미 처리됨
            rendered = render_item(item, var_labels, group_counter)
            sps_parts.append(rendered)
            sps_parts.append("")

    sps_content = "\n".join(sps_parts)

    # ── MD 파일 생성 ──
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    md_content = f"""# {config['project_name']} 분석 Syntax

> **원본 파일**: `{base_name}.sps`
> **원본 인코딩**: `{config['encoding']}`
> **줄바꿈**: `CRLF`
> **변환 시각**: {now}

```sps
{sps_content}
```
"""
    with open(md_path, "w", encoding="utf-8", newline="\n") as f:
        f.write(md_content)

    # ── SPS 파일 생성 (CP949) ──
    out_encoding = config.get("encoding", "cp949")

    # CP949 호환 불가 문자 대체
    if out_encoding.lower().replace("-", "") in ("cp949", "euckr"):
        for uc, ac in CP949_REPLACE_MAP.items():
            sps_content = sps_content.replace(uc, ac)

    # CRLF
    sps_content = sps_content.replace("\r\n", "\n").replace("\n", "\r\n")

    with open(sps_path, "wb") as f:
        f.write(sps_content.encode(out_encoding))

    return md_path, sps_path


# ═══════════════════════════════════════════════════════════════
# CLI
# ═══════════════════════════════════════════════════════════════


def build_parser() -> argparse.ArgumentParser:
    """CLI 파서 생성."""
    parser = argparse.ArgumentParser(
        description="SPSS 범용 분석 Syntax 자동 생성기",
        epilog="""\
사용 예시:
  python generate_syntax.py analysis_config.json
  python generate_syntax.py config.json --output-dir d:\\SPSS\\Syntax\\MyProject
  python generate_syntax.py config.json --encoding utf-8
""",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("config", help="분석 설정 JSON 파일 경로")
    parser.add_argument(
        "--output-dir", default=None,
        help="출력 디렉토리 (기본: 설정 파일과 같은 디렉토리)",
    )
    parser.add_argument("--version", action="version", version=f"generate_syntax v{VERSION}")
    return parser


def main() -> None:
    """CLI 진입점."""
    parser = build_parser()
    args = parser.parse_args()

    config_path = os.path.abspath(args.config)
    if not os.path.isfile(config_path):
        print(f"[ERROR] 설정 파일을 찾을 수 없습니다: {config_path}")
        sys.exit(1)

    output_dir = os.path.abspath(args.output_dir) if args.output_dir else None

    try:
        md_path, sps_path = generate(config_path, output_dir)
        print(f"[OK] MD  생성: {md_path}")
        print(f"[OK] SPS 생성: {sps_path}")
        print(f"     Size: {os.path.getsize(sps_path):,} bytes")
    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
