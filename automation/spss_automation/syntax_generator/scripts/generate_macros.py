# -*- coding: utf-8 -*-
"""
generate_macros.py - SPSS 매크로 자동 생성 도구

템플릿 파일의 플레이스홀더를 JSON 설정으로 치환하여
프로젝트 맞춤형 매크로 파일을 생성합니다.

사용법:
    python generate_macros.py config.json -o output.sps
    python generate_macros.py config.json -o output.sps --encoding cp949

Version: 1.0.0
Created: 2026-02-26
"""

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Dict


VERSION = "1.0.0"
DEFAULT_TEMPLATE = os.path.join(
    os.path.dirname(__file__), "..", "Macro", "lib", "common_macros_template.sps"
)


def load_config(config_path: str) -> Dict[str, str]:
    """JSON 설정 파일을 로드.

    Args:
        config_path: JSON 파일 경로

    Returns:
        설정 딕셔너리
    """
    with open(config_path, "r", encoding="utf-8") as f:
        config = json.load(f)

    required = ["banner", "banner_list", "ptotal1", "ptotal2", "validn_label"]
    for key in required:
        if key not in config:
            raise ValueError(f"설정 파일에 '{key}' 키가 없습니다.")

    return config


def apply_config(template_text: str, config: Dict[str, str]) -> str:
    """템플릿의 플레이스홀더를 설정값으로 치환.

    Args:
        template_text: 템플릿 텍스트
        config: 설정 딕셔너리

    Returns:
        치환된 텍스트
    """
    mapping = {
        "{{BANNER}}": config["banner"],
        "{{BANNER_LIST}}": config["banner_list"],
        "{{BANNER_NO_T1}}": config.get("banner_no_t1", config["banner_list"].replace(" ", "+")),
        "{{PTOTAL1}}": config["ptotal1"],
        "{{PTOTAL2}}": config["ptotal2"],
        "{{VALIDN_LABEL}}": config["validn_label"],
    }

    result = template_text
    for placeholder, value in mapping.items():
        result = result.replace(placeholder, value)

    return result


def generate(
    config_path: str,
    output_path: str,
    template_path: str = None,
    encoding: str = "utf-8",
) -> str:
    """매크로 파일을 생성.

    Args:
        config_path: JSON 설정 파일 경로
        output_path: 출력 SPS 파일 경로
        template_path: 템플릿 파일 경로 (None이면 기본 경로)
        encoding: 출력 인코딩

    Returns:
        생성된 파일 경로
    """
    if template_path is None:
        template_path = DEFAULT_TEMPLATE

    config = load_config(config_path)

    with open(template_path, "r", encoding="utf-8") as f:
        template = f.read()

    # 헤더의 템플릿 안내를 프로젝트 정보로 교체
    project_name = config.get("project_name", "")
    result = apply_config(template, config)
    result = result.replace(
        "SPSS 공통 매크로 템플릿 (자동 생성용)",
        f"SPSS 공통 매크로 - {project_name}" if project_name else "SPSS 공통 매크로",
    )
    result = result.replace(
        "이 파일은 generate_macros.py에서 사용하는 템플릿입니다.\n* 직접 수정하지 말고 generate_macros.py를 통해 사용하세요.",
        f"프로젝트: {project_name}\n* generate_macros.py로 자동 생성됨",
    )

    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    with open(output_path, "w", encoding=encoding) as f:
        f.write(result)

    return output_path


def build_parser() -> argparse.ArgumentParser:
    """CLI 파서 생성."""
    parser = argparse.ArgumentParser(
        description="SPSS 매크로 자동 생성 도구",
        epilog="""\
사용 예시:
  python generate_macros.py config.json -o project_macros.sps
  python generate_macros.py config.json -o output.sps --encoding cp949
  python generate_macros.py config.json -o output.sps --template custom_template.sps
""",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("config", help="배너 설정 JSON 파일 경로")
    parser.add_argument("-o", "--output", required=True, help="출력 SPS 파일 경로")
    parser.add_argument("--template", default=None, help="템플릿 파일 경로 (기본: lib/common_macros_template.sps)")
    parser.add_argument("--encoding", default="utf-8", help="출력 인코딩 (기본: utf-8)")
    parser.add_argument("--version", action="version", version=f"generate_macros v{VERSION}")
    return parser


def main() -> None:
    """CLI 진입점."""
    parser = build_parser()
    args = parser.parse_args()

    try:
        result = generate(
            config_path=os.path.abspath(args.config),
            output_path=os.path.abspath(args.output),
            template_path=os.path.abspath(args.template) if args.template else None,
            encoding=args.encoding,
        )
        print(f"[OK] 매크로 생성 완료: {result}")
    except Exception as e:
        print(f"[ERROR] {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
