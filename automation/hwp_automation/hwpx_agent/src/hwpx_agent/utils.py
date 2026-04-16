from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any

from .namespaces import local_name


SCHEMA_VERSION = "1.0.0"


def ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def write_json(path: Path, data: Any) -> Path:
    ensure_dir(path.parent)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(data, handle, ensure_ascii=False, indent=2)
    return path


def write_text(path: Path, text: str) -> Path:
    ensure_dir(path.parent)
    path.write_text(text, encoding="utf-8")
    return path


def sanitize_name(name: str, max_len: int = 80) -> str:
    value = re.sub(r"[^\w\-\.]+", "_", name, flags=re.UNICODE)
    value = re.sub(r"_+", "_", value).strip("._")
    if not value:
        value = "document"
    return value[:max_len]


def sha1_file(path: Path) -> str:
    digest = hashlib.sha1()
    with path.open("rb") as handle:
        while True:
            chunk = handle.read(1024 * 1024)
            if not chunk:
                break
            digest.update(chunk)
    return digest.hexdigest()


def compact_text(value: str | None) -> str:
    if not value:
        return ""
    return re.sub(r"\s+", " ", value).strip()


def element_children_summary(element) -> dict[str, list[dict[str, Any]]]:
    summary: dict[str, list[dict[str, Any]]] = {}
    for child in element:
        name = local_name(child.tag)
        payload: dict[str, Any] = {"attributes": dict(child.attrib)}
        text = compact_text(child.text)
        if text:
            payload["text"] = text
        grandchildren = [local_name(grandchild.tag) for grandchild in child]
        if grandchildren:
            payload["child_tags"] = grandchildren
        summary.setdefault(name, []).append(payload)
    return summary
