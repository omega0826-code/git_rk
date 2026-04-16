from __future__ import annotations

import json
import re
import zipfile
from datetime import datetime
from pathlib import Path
from typing import Any

from lxml import etree

from .namespaces import NS, tag
from .utils import SCHEMA_VERSION, compact_text, ensure_dir, write_json


class HwpxRebuilder:
    def __init__(self, run_dir: str | Path):
        self.run_dir = Path(run_dir)
        if not self.run_dir.exists():
            raise FileNotFoundError(f"실행 폴더를 찾을 수 없습니다: {self.run_dir}")

        self.assets_dir = self.run_dir / "assets"
        self.rebuild_dir = self.run_dir / "rebuild"
        self.plan_dir = self.assets_dir / "rebuild"
        self.paragraphs_path = self.assets_dir / "blocks" / "paragraphs.json"
        self.tables_path = self.assets_dir / "tables" / "tables.json"
        self.table_cells_path = self.assets_dir / "tables" / "cells.json"
        self.document_path = self.assets_dir / "document.json"

        self.paragraphs = self._load_json(self.paragraphs_path)
        self.tables = self._load_json(self.tables_path) if self.tables_path.exists() else []
        self.table_cells = self._load_json(self.table_cells_path) if self.table_cells_path.exists() else []
        self.document = self._load_json(self.document_path)
        self.paragraph_by_id = {paragraph["asset_id"]: paragraph for paragraph in self.paragraphs}
        self.table_by_id = {table["asset_id"]: table for table in self.tables}
        self.table_cell_by_id = {cell["asset_id"]: cell for cell in self.table_cells}

    def init_sample_plans(self) -> dict[str, str]:
        ensure_dir(self.plan_dir)

        safe_paragraph = next(
            (
                paragraph
                for paragraph in self.paragraphs
                if self._is_safe_paragraph_asset(paragraph)
            ),
            None
        )
        if safe_paragraph is None:
            raise RuntimeError("복원 테스트에 사용할 안전한 문단을 찾지 못했습니다.")

        sample_plan = {
            "schema_version": SCHEMA_VERSION,
            "run_dir": str(self.run_dir),
            "notes": [
                "enabled=true인 update만 적용됩니다.",
                "expected_current_text가 실제 문단 텍스트와 다르면 기본적으로 건너뜁니다."
            ],
            "updates": [
                {
                    "update_id": "upd00001",
                    "enabled": False,
                    "origin_id": safe_paragraph["asset_id"],
                    "expected_current_text": safe_paragraph["text"],
                    "new_text": f"{safe_paragraph['text']} [수정문구 입력]",
                    "reason": "수동 수정 예시"
                }
            ]
        }

        demo_plan = {
            "schema_version": SCHEMA_VERSION,
            "run_dir": str(self.run_dir),
            "notes": [
                "데모 실행용 계획입니다. 결과 HWPX가 새로 생성됩니다."
            ],
            "updates": [
                {
                    "update_id": "upd_demo_0001",
                    "enabled": True,
                    "origin_id": safe_paragraph["asset_id"],
                    "expected_current_text": safe_paragraph["text"],
                    "new_text": f"{safe_paragraph['text']} (복원 테스트)",
                    "reason": "최소 복원 경로 데모"
                }
            ]
        }

        sample_path = write_json(self.plan_dir / "rebuild_plan.sample.json", sample_plan)
        demo_path = write_json(self.plan_dir / "rebuild_plan.demo.json", demo_plan)
        return {"sample_plan": str(sample_path), "demo_plan": str(demo_path)}

    def rebuild_from_plan(self, plan_path: str | Path, output_path: str | Path | None = None) -> dict[str, Any]:
        plan = self._load_json(Path(plan_path))
        ensure_dir(self.rebuild_dir)

        source_hwpx = self._find_source_hwpx()
        output_hwpx = Path(output_path) if output_path else self.rebuild_dir / f"{self.document['document_id']}_rebuilt.hwpx"

        section_map = self._load_section_roots(source_hwpx)
        modified_entries: dict[str, bytes] = {}

        logs: list[dict[str, Any]] = []
        applied_count = 0
        skipped_count = 0

        for update in plan.get("updates", []):
            if not update.get("enabled", False):
                skipped_count += 1
                logs.append({"update_id": update.get("update_id"), "status": "skipped_disabled"})
                continue

            origin_id = update.get("origin_id")
            paragraph_asset = self.paragraph_by_id.get(origin_id)
            table_cell_asset = self.table_cell_by_id.get(origin_id)
            if paragraph_asset is None and table_cell_asset is None:
                skipped_count += 1
                logs.append({"update_id": update.get("update_id"), "status": "error_missing_origin", "origin_id": origin_id})
                continue

            if paragraph_asset is not None:
                apply_result = self._apply_paragraph_update(update, paragraph_asset, section_map)
            else:
                apply_result = self._apply_table_cell_update(update, table_cell_asset, section_map)

            if apply_result["status"] != "applied":
                skipped_count += 1
                logs.append(apply_result)
                continue

            entry_name = apply_result["package_entry"]
            modified_entries[entry_name] = etree.tostring(section_map[entry_name], xml_declaration=True, encoding="UTF-8", standalone=True)
            applied_count += 1
            logs.append(apply_result)

        self._build_hwpx(source_hwpx, output_hwpx, modified_entries)

        summary = {
            "schema_version": SCHEMA_VERSION,
            "run_dir": str(self.run_dir),
            "plan_path": str(Path(plan_path)),
            "output_hwpx": str(output_hwpx),
            "applied_count": applied_count,
            "skipped_count": skipped_count,
            "modified_entry_count": len(modified_entries),
            "created_at": datetime.now().isoformat(timespec="seconds")
        }

        write_json(self.rebuild_dir / "rebuild_summary.json", summary)
        write_json(self.rebuild_dir / "rebuild_log.json", logs)

        return {"summary": summary, "logs": logs}

    def _apply_paragraph_update(self, update: dict[str, Any], paragraph_asset: dict[str, Any], section_map: dict[str, Any]) -> dict[str, Any]:
        origin_id = paragraph_asset["asset_id"]
        if not self._is_safe_paragraph_asset(paragraph_asset):
            return {
                "update_id": update.get("update_id"),
                "status": "skipped_unsafe_paragraph",
                "origin_id": origin_id,
                "control_tags": paragraph_asset.get("control_tags", []),
                "embedded_object_refs": paragraph_asset.get("embedded_object_refs", [])
            }

        entry_name = paragraph_asset["source_ref"]["package_entry"]
        section_root = section_map.get(entry_name)
        if section_root is None:
            return {"update_id": update.get("update_id"), "status": "error_missing_section", "package_entry": entry_name}

        paragraph_index = paragraph_asset.get("section_paragraph_index")
        paragraph_element = self._get_body_paragraph_by_index(section_root, paragraph_index)
        if paragraph_element is None:
            return {"update_id": update.get("update_id"), "status": "error_missing_paragraph", "origin_id": origin_id}

        current_text = self._extract_safe_paragraph_text(paragraph_element)
        expected_text = update.get("expected_current_text", "")
        if expected_text and current_text != expected_text and not update.get("allow_mismatch", False):
            return {
                "update_id": update.get("update_id"),
                "status": "skipped_text_mismatch",
                "origin_id": origin_id,
                "expected_current_text": expected_text,
                "actual_current_text": current_text
            }

        new_text = update.get("new_text", "")
        self._apply_text_update(paragraph_element, new_text)
        return {
            "update_id": update.get("update_id"),
            "status": "applied",
            "origin_id": origin_id,
            "origin_type": "paragraph",
            "package_entry": entry_name,
            "old_text": current_text,
            "new_text": new_text
        }

    def _apply_table_cell_update(self, update: dict[str, Any], cell_asset: dict[str, Any], section_map: dict[str, Any]) -> dict[str, Any]:
        origin_id = cell_asset["asset_id"]
        if not self._is_safe_table_cell_asset(cell_asset):
            return {
                "update_id": update.get("update_id"),
                "status": "skipped_unsafe_table_cell",
                "origin_id": origin_id,
                "classification": cell_asset.get("classification", {})
            }

        entry_name = cell_asset["source_ref"]["package_entry"]
        section_root = section_map.get(entry_name)
        if section_root is None:
            return {"update_id": update.get("update_id"), "status": "error_missing_section", "package_entry": entry_name}

        table_id = cell_asset.get("table_id")
        table_asset = self.table_by_id.get(table_id)
        if table_asset is None:
            return {"update_id": update.get("update_id"), "status": "error_missing_table_asset", "origin_id": origin_id, "table_id": table_id}

        paragraph_index = table_asset.get("paragraph_index")
        table_position = table_asset.get("table_position")
        cell_index = cell_asset.get("cell_index")
        table_element = self._get_table_by_index(section_root, paragraph_index, table_position)
        if table_element is None:
            return {"update_id": update.get("update_id"), "status": "error_missing_table_element", "origin_id": origin_id, "table_id": table_id}

        cell_element = self._get_table_cell_by_index(table_element, cell_index)
        if cell_element is None:
            return {"update_id": update.get("update_id"), "status": "error_missing_table_cell", "origin_id": origin_id}

        current_text = self._extract_table_cell_text(cell_element)
        expected_text = update.get("expected_current_text", "")
        if expected_text and current_text != expected_text and not update.get("allow_mismatch", False):
            return {
                "update_id": update.get("update_id"),
                "status": "skipped_text_mismatch",
                "origin_id": origin_id,
                "expected_current_text": expected_text,
                "actual_current_text": current_text
            }

        new_text = update.get("new_text", "")
        self._apply_cell_text_update(cell_element, new_text)
        return {
            "update_id": update.get("update_id"),
            "status": "applied",
            "origin_id": origin_id,
            "origin_type": "table_cell",
            "package_entry": entry_name,
            "old_text": current_text,
            "new_text": new_text,
            "table_id": table_id,
            "cell_index": cell_index
        }

    def _load_json(self, path: Path):
        return json.loads(path.read_text(encoding="utf-8"))

    def _find_source_hwpx(self) -> Path:
        source_dir = self.run_dir / "source"
        candidates = sorted(source_dir.glob("*.hwpx"))
        if not candidates:
            raise FileNotFoundError(f"source 폴더 안에 원본 HWPX가 없습니다: {source_dir}")
        return candidates[0]

    def _load_section_roots(self, source_hwpx: Path) -> dict[str, Any]:
        result = {}
        with zipfile.ZipFile(source_hwpx, "r") as archive:
            for name in archive.namelist():
                if name.startswith("Contents/section") and name.endswith(".xml"):
                    result[name] = etree.fromstring(archive.read(name))
        return result

    def _is_safe_paragraph_asset(self, paragraph: dict[str, Any]) -> bool:
        classification = paragraph.get("classification", {})
        if "rebuild_safe_text_only" in classification:
            return bool(classification.get("rebuild_safe_text_only"))
        if paragraph.get("embedded_object_refs"):
            return False
        if paragraph.get("control_tags"):
            return False
        if not (paragraph.get("text") or "").strip():
            return False
        runs = paragraph.get("runs", [])
        if not runs:
            return False
        if any(run.get("child_tags") for run in runs):
            return False
        return True

    def _is_safe_table_cell_asset(self, cell: dict[str, Any]) -> bool:
        classification = cell.get("classification", {})
        if "rebuild_safe_text_only" in classification:
            return bool(classification.get("rebuild_safe_text_only"))
        return bool((cell.get("text") or "").strip())

    def _get_body_paragraph_by_index(self, section_root, target_index: int):
        current_index = 0
        for paragraph in section_root.iter(tag("hp", "p")):
            if self._is_in_table(paragraph) or self._is_in_header_footer(paragraph):
                continue
            current_index += 1
            if current_index == target_index:
                return paragraph
        return None

    def _get_table_by_index(self, section_root, paragraph_index: int, table_position: int):
        paragraph = self._get_body_paragraph_by_index(section_root, paragraph_index)
        if paragraph is None:
            return None
        tables = list(paragraph.iter(tag("hp", "tbl")))
        if 1 <= table_position <= len(tables):
            return tables[table_position - 1]
        return None

    def _get_table_cell_by_index(self, table_element, cell_index: int):
        cells = list(table_element.iter(tag("hp", "tc")))
        if 1 <= cell_index <= len(cells):
            return cells[cell_index - 1]
        return None

    def _is_in_table(self, element) -> bool:
        parent = element.getparent()
        while parent is not None:
            if parent.tag == tag("hp", "tbl"):
                return True
            parent = parent.getparent()
        return False

    def _is_in_header_footer(self, element) -> bool:
        parent = element.getparent()
        while parent is not None:
            if parent.tag in (tag("hp", "header"), tag("hp", "footer")):
                return True
            parent = parent.getparent()
        return False

    def _extract_safe_paragraph_text(self, paragraph) -> str:
        texts = []
        for run in paragraph.findall(".//hp:run", NS):
            for text_node in run.findall("hp:t", NS):
                if text_node.text:
                    texts.append(text_node.text)
        return compact_text(" ".join(texts))

    def _extract_table_cell_text(self, cell) -> str:
        texts = []
        for text_node in cell.iter(tag("hp", "t")):
            if text_node.text:
                texts.append(text_node.text)
        return compact_text(" ".join(texts))

    def _apply_text_update(self, paragraph, new_text: str) -> None:
        text_nodes = []
        for run in paragraph.findall(".//hp:run", NS):
            for text_node in run.findall("hp:t", NS):
                text_nodes.append(text_node)

        if text_nodes:
            text_nodes[0].text = new_text
            for text_node in text_nodes[1:]:
                text_node.text = ""
            return

        first_run = paragraph.find(".//hp:run", NS)
        if first_run is None:
            first_run = etree.SubElement(paragraph, tag("hp", "run"))
        new_text_node = etree.SubElement(first_run, tag("hp", "t"))
        new_text_node.text = new_text

    def _apply_cell_text_update(self, cell, new_text: str) -> None:
        text_nodes = list(cell.iter(tag("hp", "t")))
        if text_nodes:
            text_nodes[0].text = new_text
            for text_node in text_nodes[1:]:
                text_node.text = ""
            return

        first_para = cell.find(".//hp:p", NS)
        if first_para is None:
            sublist = cell.find("hp:subList", NS)
            if sublist is None:
                sublist = etree.SubElement(cell, tag("hp", "subList"))
            first_para = etree.SubElement(sublist, tag("hp", "p"))
        first_run = first_para.find(".//hp:run", NS)
        if first_run is None:
            first_run = etree.SubElement(first_para, tag("hp", "run"))
        text_node = etree.SubElement(first_run, tag("hp", "t"))
        text_node.text = new_text

    def _build_hwpx(self, input_path: Path, output_path: Path, modified_files: dict[str, bytes]) -> None:
        with zipfile.ZipFile(input_path, "r") as zin:
            file_list = zin.namelist()
            file_data = {name: zin.read(name) for name in file_list}

        for name, data in modified_files.items():
            if name in file_data:
                file_data[name] = data

        with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as zout:
            for name in file_list:
                if name == "mimetype":
                    zout.writestr(name, file_data[name], compress_type=zipfile.ZIP_STORED)
                else:
                    zout.writestr(name, file_data[name])
