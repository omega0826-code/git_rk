#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
SPSS Syntax 자동 생성 도구 — 웹 UI
실행: python app.py / start.bat / launch_web_ui.hta
기본 접속: http://127.0.0.1:5000
Version: 1.0.1 | Updated: 2026-04-15
"""

import json
import os
import re
import socket
import subprocess
import sys
import threading
import time
import uuid
import webbrowser
from pathlib import Path

from flask import Flask, jsonify, request, send_file

BASE_DIR = Path(__file__).parent.resolve()
SCRIPTS_DIR = BASE_DIR / "scripts"
WEB_DIR = BASE_DIR / "web"
OUTPUT_DIR = BASE_DIR / "web_output"
EXAMPLES_DIR = BASE_DIR / "examples"
MACROS_DIR = BASE_DIR / "macros"
PYTHON = sys.executable
DEFAULT_PORT = 5000
MAX_UPLOAD_MB = 50
INVALID_FILENAME_CHARS = re.compile(r'[<>:"/\\|?*\x00-\x1F]')

SAMPLE_FILES = {
    "guideline_sample.csv": EXAMPLES_DIR / "guideline_sample.csv",
    "short_labels_sample.json": EXAMPLES_DIR / "short_labels_sample.json",
    "analysis_config_sample.json": EXAMPLES_DIR / "analysis_config_sample.json",
    "banner_config_sample.json": MACROS_DIR / "banner_config_sample.json",
}

OUTPUT_DIR.mkdir(exist_ok=True)

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = MAX_UPLOAD_MB * 1024 * 1024


def make_session():
    session_id = str(uuid.uuid4())
    session_dir = OUTPUT_DIR / session_id
    session_dir.mkdir()
    return session_id, session_dir


def normalize_filename(filename, fallback):
    raw_name = Path(str(filename or "")).name.strip() or fallback
    path_obj = Path(raw_name)
    suffix = path_obj.suffix or Path(fallback).suffix
    stem = path_obj.stem if path_obj.suffix else raw_name
    safe_stem = INVALID_FILENAME_CHARS.sub("_", stem).strip(" ._")
    safe_suffix = INVALID_FILENAME_CHARS.sub("", suffix).strip()
    final_name = f"{safe_stem or Path(fallback).stem}{safe_suffix or Path(fallback).suffix}"
    return final_name[:180]


def normalize_stem(value, fallback):
    raw_value = Path(str(value or "").strip()).stem
    safe_value = INVALID_FILENAME_CHARS.sub("_", raw_value).strip(" ._")
    return (safe_value or fallback)[:80]


def run_script(command):
    env = os.environ.copy()
    env["PYTHONUTF8"] = "1"
    env["PYTHONIOENCODING"] = "utf-8"

    result = subprocess.run(
        command,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        cwd=BASE_DIR,
        env=env,
    )
    combined = "\n".join(part for part in (result.stdout.strip(), result.stderr.strip()) if part).strip()
    return result.returncode, combined or "(출력 없음)"


def collect_files(directory, extensions, session_id, exclude=None):
    excluded_names = set(exclude or [])
    collected = []
    for path in sorted(directory.iterdir()):
        if path.is_file() and path.suffix.lower() in extensions and path.name not in excluded_names:
            collected.append({"name": path.name, "url": f"/download/{session_id}/{path.name}"})
    return collected


def resolve_label_sps(config, working_dir):
    raw_path = str(config.get("label_sps", "")).strip()
    if not raw_path:
        return None

    candidate = Path(raw_path)
    candidates = []
    if candidate.is_absolute():
        candidates.append(candidate)
    else:
        candidates.extend(
            [
                working_dir / candidate,
                working_dir / candidate.name,
                BASE_DIR / candidate,
                BASE_DIR / candidate.name,
            ]
        )

    for item in candidates:
        resolved = item.resolve()
        if resolved.exists():
            return resolved
    return None


def find_available_port(start_port):
    port = max(1024, int(start_port))
    while port < 65535:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            if sock.connect_ex(("127.0.0.1", port)) != 0:
                return port
        port += 1
    raise RuntimeError("사용 가능한 포트를 찾지 못했습니다.")


def open_browser_later(url):
    def _open():
        time.sleep(1.0)
        webbrowser.open(url, new=2)

    threading.Thread(target=_open, daemon=True).start()


@app.errorhandler(413)
def handle_request_entity_too_large(_error):
    return (
        jsonify(
            success=False,
            log=f"업로드 용량이 너무 큽니다. 파일 크기를 {MAX_UPLOAD_MB}MB 이하로 줄여주세요.",
            files=[],
        ),
        413,
    )


@app.get("/")
def index():
    return send_file(WEB_DIR / "index.html")


@app.get("/api/health")
def health():
    return jsonify(success=True, status="ok")


@app.get("/samples/<filename>")
def download_sample(filename):
    sample = SAMPLE_FILES.get(Path(filename).name)
    if not sample or not sample.exists():
        return jsonify(success=False, log="샘플 파일을 찾을 수 없습니다."), 404
    return send_file(sample, as_attachment=True, download_name=sample.name)


@app.post("/api/guideline-to-sps")
def api_guideline_to_sps():
    session_id, working_dir = make_session()
    csv_file = request.files.get("csv_file")
    if not csv_file or not csv_file.filename:
        return jsonify(success=False, log="CSV 파일이 없습니다.", files=[])

    csv_path = working_dir / "input.csv"
    csv_file.save(csv_path)

    encoding = request.form.get("encoding", "cp949")
    title = request.form.get("title", "").strip()
    output_stem = normalize_stem(request.form.get("output_name"), "label")
    output_sps = working_dir / f"{output_stem}.sps"

    command = [
        PYTHON,
        str(SCRIPTS_DIR / "guideline_to_sps.py"),
        str(csv_path),
        "-o",
        str(output_sps),
        "--encoding",
        encoding,
    ]
    if title:
        command.extend(["--title", title])

    excluded_names = {"input.csv"}
    short_file = request.files.get("short_labels")
    if short_file and short_file.filename:
        short_json_path = working_dir / "short_labels.json"
        short_file.save(short_json_path)
        short_output_stem = normalize_stem(request.form.get("short_output_name"), "label_short")
        short_output_sps = working_dir / f"{short_output_stem}.sps"
        command.extend(
            [
                "--short-labels",
                str(short_json_path),
                "--short-output",
                str(short_output_sps),
            ]
        )
        excluded_names.add("short_labels.json")

    return_code, log = run_script(command)
    files = collect_files(working_dir, {".sps"}, session_id, exclude=excluded_names)
    return jsonify(success=(return_code == 0), log=log, files=files)


@app.post("/api/generate-syntax")
def api_generate_syntax():
    session_id, working_dir = make_session()
    config_file = request.files.get("config_json")
    if not config_file or not config_file.filename:
        return jsonify(success=False, log="analysis_config.json 파일이 없습니다.", files=[])

    config_path = working_dir / "analysis_config.json"
    config_file.save(config_path)

    try:
        config = json.loads(config_path.read_text(encoding="utf-8"))
    except Exception as exc:
        return jsonify(success=False, log=f"analysis_config.json 파싱 실패: {exc}", files=[])

    excluded_names = {"analysis_config.json"}
    label_file = request.files.get("label_sps")
    if label_file and label_file.filename:
        label_filename = normalize_filename(label_file.filename, "label.sps")
        label_path = working_dir / label_filename
        label_file.save(label_path)
        config["label_sps"] = label_filename
        excluded_names.add(label_filename)
    else:
        resolved_label_path = resolve_label_sps(config, working_dir)
        if not resolved_label_path:
            return jsonify(
                success=False,
                log=(
                    "analysis_config.json 안의 label_sps 파일을 찾지 못했습니다.\n"
                    "웹 UI에서는 label.sps 또는 label_short.sps 파일을 함께 업로드하는 방식을 권장합니다."
                ),
                files=[],
            )
        config["label_sps"] = str(resolved_label_path)

    config_path.write_text(json.dumps(config, ensure_ascii=False, indent=2), encoding="utf-8")

    command = [
        PYTHON,
        str(SCRIPTS_DIR / "generate_syntax.py"),
        str(config_path),
        "--output-dir",
        str(working_dir),
    ]
    return_code, log = run_script(command)
    files = collect_files(working_dir, {".sps", ".md"}, session_id, exclude=excluded_names)
    return jsonify(success=(return_code == 0), log=log, files=files)


@app.post("/api/generate-macros")
def api_generate_macros():
    session_id, working_dir = make_session()
    config_file = request.files.get("config_json")
    if not config_file or not config_file.filename:
        return jsonify(success=False, log="banner_config.json 파일이 없습니다.", files=[])

    config_path = working_dir / "banner_config.json"
    config_file.save(config_path)

    encoding = request.form.get("encoding", "utf-8")
    output_stem = normalize_stem(request.form.get("output_name"), "macros")
    output_sps = working_dir / f"{output_stem}.sps"

    command = [
        PYTHON,
        str(SCRIPTS_DIR / "generate_macros.py"),
        str(config_path),
        "-o",
        str(output_sps),
        "--encoding",
        encoding,
    ]
    return_code, log = run_script(command)
    files = collect_files(working_dir, {".sps"}, session_id, exclude={"banner_config.json"})
    return jsonify(success=(return_code == 0), log=log, files=files)


@app.post("/api/sps-to-md")
def api_sps_to_md():
    session_id, working_dir = make_session()
    sps_file = request.files.get("sps_file")
    if not sps_file or not sps_file.filename:
        return jsonify(success=False, log="SPS 파일이 없습니다.", files=[])

    source_name = normalize_filename(sps_file.filename, "input.sps")
    input_path = working_dir / source_name
    output_path = working_dir / f"{Path(source_name).stem}.md"
    sps_file.save(input_path)

    command = [PYTHON, str(SCRIPTS_DIR / "sps_to_md.py"), str(input_path), "-o", str(output_path)]
    return_code, log = run_script(command)
    files = collect_files(working_dir, {".md"}, session_id)
    return jsonify(success=(return_code == 0), log=log, files=files)


@app.post("/api/md-to-sps")
def api_md_to_sps():
    session_id, working_dir = make_session()
    md_file = request.files.get("md_file")
    if not md_file or not md_file.filename:
        return jsonify(success=False, log="MD 파일이 없습니다.", files=[])

    source_name = normalize_filename(md_file.filename, "input.md")
    input_path = working_dir / source_name
    md_file.save(input_path)

    encoding = request.form.get("encoding", "").strip()
    strip_define_blanks = request.form.get("strip_define_blanks") == "true"

    command = [PYTHON, str(SCRIPTS_DIR / "md_to_sps.py"), str(input_path)]
    if encoding:
        command.extend(["--encoding", encoding])
    if strip_define_blanks:
        command.append("--strip-define-blanks")

    return_code, log = run_script(command)
    files = collect_files(working_dir, {".sps"}, session_id)
    return jsonify(success=(return_code == 0), log=log, files=files)


@app.get("/download/<session_id>/<filename>")
def download(session_id, filename):
    safe_name = Path(filename).name
    file_path = OUTPUT_DIR / session_id / safe_name
    if not file_path.exists():
        return "파일을 찾을 수 없습니다.", 404
    return send_file(file_path, as_attachment=True, download_name=safe_name)


if __name__ == "__main__":
    requested_port = os.environ.get("SPSS_UI_PORT", str(DEFAULT_PORT))
    try:
        requested_port_int = int(requested_port)
    except ValueError:
        requested_port_int = DEFAULT_PORT

    port = find_available_port(requested_port_int)
    url = f"http://127.0.0.1:{port}"
    open_browser_later(url)

    print("=" * 64)
    print("  SPSS Syntax 자동 생성 도구 - 웹 UI")
    if port != requested_port_int:
        print(f"  기본 포트 {requested_port_int} 사용 중 -> {port} 포트로 전환")
    print(f"  접속 주소: {url}")
    print("  종료: 이 창 닫기 또는 Ctrl+C")
    print("=" * 64)

    app.run(host="127.0.0.1", port=port, debug=False)
