#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
AI agent-friendly runner for the SPSS syntax generator bundle.

This wrapper exposes the existing scripts through a stable CLI contract and
prints a single JSON manifest to stdout so an orchestration agent can parse
results without scraping human-readable logs.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List


BASE_DIR = Path(__file__).resolve().parent
SCRIPTS_DIR = BASE_DIR / "scripts"
RUNS_DIR = BASE_DIR / "runs"
PYTHON = sys.executable

RUNS_DIR.mkdir(exist_ok=True)


def safe_name(value: str, fallback: str) -> str:
    cleaned = "".join(ch if ch.isalnum() or ch in ("-", "_") else "_" for ch in (value or "").strip())
    cleaned = cleaned.strip("._-")
    return cleaned or fallback


def make_job_dir(job_id: str | None) -> Path:
    resolved_job_id = safe_name(job_id or datetime.now().strftime("%Y%m%d_%H%M%S"), "job")
    job_dir = RUNS_DIR / resolved_job_id
    job_dir.mkdir(parents=True, exist_ok=True)
    return job_dir


def write_manifest(payload: Dict) -> int:
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if payload.get("ok") else 1


def run_command(command: List[str], log_path: Path) -> subprocess.CompletedProcess:
    env = os.environ.copy()
    env["PYTHONUTF8"] = "1"
    env["PYTHONIOENCODING"] = "utf-8"
    result = subprocess.run(
        command,
        cwd=BASE_DIR,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        env=env,
    )
    combined = "\n".join(part for part in (result.stdout.strip(), result.stderr.strip()) if part).strip()
    log_path.write_text(combined or "(출력 없음)\n", encoding="utf-8")
    return result


def build_outputs(job_dir: Path, patterns: Dict[str, str]) -> List[Dict[str, str]]:
    outputs: List[Dict[str, str]] = []
    for kind, pattern in patterns.items():
        for path in sorted(job_dir.glob(pattern)):
            if path.is_file():
                outputs.append({"kind": kind, "path": str(path.resolve())})
    return outputs


def base_manifest(task: str, job_dir: Path, command: List[str], result: subprocess.CompletedProcess, outputs: List[Dict[str, str]]) -> Dict:
    return {
        "ok": result.returncode == 0,
        "task": task,
        "job_dir": str(job_dir.resolve()),
        "command": command,
        "exit_code": result.returncode,
        "log_path": str((job_dir / "run.log").resolve()),
        "outputs": outputs,
    }


def task_guideline_to_sps(args: argparse.Namespace) -> int:
    job_dir = make_job_dir(args.job_id)
    log_path = job_dir / "run.log"
    output_name = safe_name(args.output_name, "label")
    command = [
        PYTHON,
        str(SCRIPTS_DIR / "guideline_to_sps.py"),
        str(Path(args.csv).resolve()),
        "-o",
        str(job_dir / f"{output_name}.sps"),
        "--encoding",
        args.encoding,
    ]
    if args.title:
        command.extend(["--title", args.title])
    if args.short_labels:
        short_name = safe_name(args.short_output_name, "label_short")
        command.extend(
            [
                "--short-labels",
                str(Path(args.short_labels).resolve()),
                "--short-output",
                str(job_dir / f"{short_name}.sps"),
            ]
        )

    result = run_command(command, log_path)
    outputs = build_outputs(job_dir, {"sps": "*.sps"})
    return write_manifest(base_manifest("guideline-to-sps", job_dir, command, result, outputs))


def task_generate_syntax(args: argparse.Namespace) -> int:
    job_dir = make_job_dir(args.job_id)
    log_path = job_dir / "run.log"
    config_src = Path(args.config).resolve()
    config_dst = job_dir / config_src.name
    config = json.loads(config_src.read_text(encoding="utf-8"))

    if args.label_sps:
        label_src = Path(args.label_sps).resolve()
        label_dst = job_dir / label_src.name
        label_dst.write_bytes(label_src.read_bytes())
        config["label_sps"] = label_dst.name

    config_dst.write_text(json.dumps(config, ensure_ascii=False, indent=2), encoding="utf-8")
    command = [
        PYTHON,
        str(SCRIPTS_DIR / "generate_syntax.py"),
        str(config_dst),
        "--output-dir",
        str(job_dir),
    ]

    result = run_command(command, log_path)
    outputs = build_outputs(job_dir, {"md": "*.md", "sps": "*.sps"})
    return write_manifest(base_manifest("generate-syntax", job_dir, command, result, outputs))


def task_generate_macros(args: argparse.Namespace) -> int:
    job_dir = make_job_dir(args.job_id)
    log_path = job_dir / "run.log"
    output_name = safe_name(args.output_name, "macros")
    command = [
        PYTHON,
        str(SCRIPTS_DIR / "generate_macros.py"),
        str(Path(args.config).resolve()),
        "-o",
        str(job_dir / f"{output_name}.sps"),
        "--encoding",
        args.encoding,
    ]

    result = run_command(command, log_path)
    outputs = build_outputs(job_dir, {"sps": "*.sps"})
    return write_manifest(base_manifest("generate-macros", job_dir, command, result, outputs))


def task_sps_to_md(args: argparse.Namespace) -> int:
    job_dir = make_job_dir(args.job_id)
    log_path = job_dir / "run.log"
    input_path = Path(args.input_sps).resolve()
    output_path = job_dir / f"{input_path.stem}.md"
    command = [
        PYTHON,
        str(SCRIPTS_DIR / "sps_to_md.py"),
        str(input_path),
        "-o",
        str(output_path),
    ]
    if args.encoding:
        command.extend(["--encoding", args.encoding])
    if args.title:
        command.extend(["--title", args.title])

    result = run_command(command, log_path)
    outputs = build_outputs(job_dir, {"md": "*.md"})
    return write_manifest(base_manifest("sps-to-md", job_dir, command, result, outputs))


def task_md_to_sps(args: argparse.Namespace) -> int:
    job_dir = make_job_dir(args.job_id)
    log_path = job_dir / "run.log"
    input_path = Path(args.input_md).resolve()
    output_path = job_dir / f"{input_path.stem}.sps"
    command = [
        PYTHON,
        str(SCRIPTS_DIR / "md_to_sps.py"),
        str(input_path),
        "-o",
        str(output_path),
    ]
    if args.encoding:
        command.extend(["--encoding", args.encoding])
    if args.strip_define_blanks:
        command.append("--strip-define-blanks")

    result = run_command(command, log_path)
    outputs = build_outputs(job_dir, {"sps": "*.sps"})
    return write_manifest(base_manifest("md-to-sps", job_dir, command, result, outputs))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="AI agent runner for the SPSS syntax generator bundle")
    subparsers = parser.add_subparsers(dest="task", required=True)

    p1 = subparsers.add_parser("guideline-to-sps", help="Generate label SPS files from guideline CSV")
    p1.add_argument("--csv", required=True, help="Path to the input guideline CSV")
    p1.add_argument("--encoding", default="cp949", help="Output encoding for the main SPS file")
    p1.add_argument("--title", default="", help="Optional title for the SPS comment header")
    p1.add_argument("--output-name", default="label", help="Main SPS output stem")
    p1.add_argument("--short-labels", default=None, help="Optional short labels JSON path")
    p1.add_argument("--short-output-name", default="label_short", help="Short-label SPS output stem")
    p1.add_argument("--job-id", default=None, help="Optional job folder name under runs/")
    p1.set_defaults(func=task_guideline_to_sps)

    p2 = subparsers.add_parser("generate-syntax", help="Generate analysis syntax files from analysis_config.json")
    p2.add_argument("--config", required=True, help="Path to analysis_config.json")
    p2.add_argument("--label-sps", default=None, help="Optional label SPS path copied into the job folder")
    p2.add_argument("--job-id", default=None, help="Optional job folder name under runs/")
    p2.set_defaults(func=task_generate_syntax)

    p3 = subparsers.add_parser("generate-macros", help="Generate a macro SPS file from banner_config.json")
    p3.add_argument("--config", required=True, help="Path to banner_config.json")
    p3.add_argument("--encoding", default="utf-8", help="Output encoding")
    p3.add_argument("--output-name", default="macros", help="Macro SPS output stem")
    p3.add_argument("--job-id", default=None, help="Optional job folder name under runs/")
    p3.set_defaults(func=task_generate_macros)

    p4 = subparsers.add_parser("sps-to-md", help="Convert one SPS file to Markdown")
    p4.add_argument("--input-sps", required=True, help="Path to the source SPS file")
    p4.add_argument("--encoding", default=None, help="Optional input encoding override")
    p4.add_argument("--title", default=None, help="Optional Markdown title override")
    p4.add_argument("--job-id", default=None, help="Optional job folder name under runs/")
    p4.set_defaults(func=task_sps_to_md)

    p5 = subparsers.add_parser("md-to-sps", help="Convert one Markdown file back to SPS")
    p5.add_argument("--input-md", required=True, help="Path to the source Markdown file")
    p5.add_argument("--encoding", default=None, help="Optional output encoding")
    p5.add_argument("--strip-define-blanks", action="store_true", help="Remove blank lines inside DEFINE blocks")
    p5.add_argument("--job-id", default=None, help="Optional job folder name under runs/")
    p5.set_defaults(func=task_md_to_sps)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
