from __future__ import annotations

import importlib.util
import re
from dataclasses import asdict, is_dataclass
from pathlib import Path
from typing import Any

from .utils import SCHEMA_VERSION, write_json


class AssetProofreader:
    def __init__(self, run_dir: str | Path):
        self.run_dir = Path(run_dir)
        self.assets_dir = self.run_dir / "assets"
        self.output_dir = self.assets_dir / "proofreading"

        if not self.run_dir.exists():
            raise FileNotFoundError(f"실행 결과 폴더를 찾을 수 없습니다: {self.run_dir}")

        self.paragraphs_path = self.assets_dir / "blocks" / "paragraphs.json"
        self.table_cells_path = self.assets_dir / "tables" / "cells.json"
        if not self.paragraphs_path.exists():
            raise FileNotFoundError(f"문단 자산 파일을 찾을 수 없습니다: {self.paragraphs_path}")

    def run(self, include_spell: bool = False) -> dict[str, Any]:
        self.output_dir.mkdir(parents=True, exist_ok=True)

        legacy = self._load_legacy_module()
        paragraph_assets = self._load_json(self.paragraphs_path)
        table_cell_assets = self._load_json(self.table_cells_path) if self.table_cells_path.exists() else []
        line_bundle = self._build_line_bundle(paragraph_assets, table_cell_assets)

        text_checker = legacy.TextChecker(line_bundle["lines"])
        text_issues = list(text_checker.check_all())

        spell_issues = []
        spell_available = bool(getattr(legacy, "_KIWI_AVAILABLE", False))
        if include_spell and spell_available:
            spell_checker = legacy.SpellChecker(line_bundle["lines"])
            spell_issues = list(spell_checker.check_all())

        linked_text_issues = self._link_issues(text_issues, line_bundle, issue_kind="text")
        linked_spell_issues = self._link_issues(spell_issues, line_bundle, issue_kind="spell")
        all_issues = linked_text_issues + linked_spell_issues

        summary = {
            "schema_version": SCHEMA_VERSION,
            "run_dir": str(self.run_dir),
            "issue_count": len(all_issues),
            "text_issue_count": len(linked_text_issues),
            "spell_issue_count": len(linked_spell_issues),
            "spell_available": spell_available,
            "spell_executed": include_spell and spell_available,
            "issue_counts_by_severity": self._count_by_field(all_issues, "severity"),
            "issue_counts_by_category": self._count_by_field(all_issues, "category"),
            "line_count": len(line_bundle["lines"]),
            "mapped_paragraph_count": sum(1 for item in line_bundle["line_mappings"] if item.get("asset_type") == "paragraph"),
            "mapped_table_cell_count": sum(1 for item in line_bundle["line_mappings"] if item.get("asset_type") == "table_cell"),
            "line_counts_by_asset_type": self._count_by_field(line_bundle["line_mappings"], "asset_type")
        }

        write_json(self.output_dir / "issues.json", all_issues)
        write_json(self.output_dir / "summary.json", summary)
        write_json(self.output_dir / "line_map.json", line_bundle["line_mappings"])

        return {
            "issues": all_issues,
            "summary": summary,
            "output_dir": str(self.output_dir)
        }

    def _load_legacy_module(self):
        legacy_path = self.run_dir.parent.parent / "proofreading" / "run_typo_check.py"
        if not legacy_path.exists():
            legacy_path = Path(__file__).resolve().parents[3] / "proofreading" / "run_typo_check.py"
        spec = importlib.util.spec_from_file_location("legacy_run_typo_check", legacy_path)
        if spec is None or spec.loader is None:
            raise RuntimeError(f"기존 교정 모듈을 불러올 수 없습니다: {legacy_path}")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    def _load_json(self, path: Path):
        import json
        return json.loads(path.read_text(encoding="utf-8"))

    def _build_line_bundle(
        self,
        paragraph_assets: list[dict[str, Any]],
        table_cell_assets: list[dict[str, Any]]
    ) -> dict[str, Any]:
        lines: list[str] = []
        line_mappings: list[dict[str, Any]] = []

        for paragraph in paragraph_assets:
            text = (paragraph.get("text") or "").strip()
            if not text:
                continue
            lines.append(text)
            line_mappings.append(
                {
                    "line_no": len(lines),
                    "asset_id": paragraph.get("asset_id"),
                    "asset_type": "paragraph",
                    "page_no": paragraph.get("page_no"),
                    "page_source": paragraph.get("page_source"),
                    "source_ref": paragraph.get("source_ref", {}),
                    "paragraph_text": text,
                    "context_type": paragraph.get("classification", {}).get("context_type"),
                    "content_type": paragraph.get("classification", {}).get("content_type"),
                    "rebuild_safe_text_only": paragraph.get("classification", {}).get("rebuild_safe_text_only", False)
                }
            )

        for cell in table_cell_assets:
            text = (cell.get("text") or "").strip()
            if not text:
                continue
            lines.append(text)
            line_mappings.append(
                {
                    "line_no": len(lines),
                    "asset_id": cell.get("asset_id"),
                    "asset_type": "table_cell",
                    "page_no": cell.get("page_no"),
                    "page_source": cell.get("page_source"),
                    "source_ref": cell.get("source_ref", {}),
                    "paragraph_text": text,
                    "table_id": cell.get("table_id"),
                    "row": cell.get("row"),
                    "col": cell.get("col"),
                    "content_type": cell.get("classification", {}).get("content_type"),
                    "rebuild_safe_text_only": cell.get("classification", {}).get("rebuild_safe_text_only", False)
                }
            )

        return {"lines": lines, "line_mappings": line_mappings}

    def _link_issues(self, issues: list[Any], line_bundle: dict[str, Any], issue_kind: str) -> list[dict[str, Any]]:
        linked = []
        line_mappings = line_bundle["line_mappings"]

        for index, issue in enumerate(issues, start=1):
            issue_dict = self._normalize_issue(issue)
            related_lines = self._extract_related_line_numbers(issue_dict)
            primary_line = related_lines[0] if related_lines else None
            mapping = line_mappings[primary_line - 1] if primary_line and primary_line <= len(line_mappings) else None

            related_origin_ids = []
            for line_no in related_lines:
                if 1 <= line_no <= len(line_mappings):
                    related_origin_ids.append(line_mappings[line_no - 1]["asset_id"])

            linked.append(
                {
                    "schema_version": SCHEMA_VERSION,
                    "issue_id": f"{issue_kind}_{index:05d}",
                    "page": mapping.get("page_no") if mapping else None,
                    "origin_id": mapping.get("asset_id") if mapping else "unmapped",
                    "origin_type": mapping.get("asset_type") if mapping else None,
                    "related_origin_ids": related_origin_ids,
                    "source_location": self._build_source_location(mapping),
                    "original_text": issue_dict.get("original", ""),
                    "suggested_fix": issue_dict.get("suggestion", ""),
                    "reason": issue_dict.get("description", ""),
                    "memo": f"category={issue_dict.get('category','')} severity={issue_dict.get('severity','')} location={issue_dict.get('location','')}",
                    "category": issue_dict.get("category"),
                    "severity": issue_dict.get("severity"),
                    "line_no": primary_line
                }
            )

        return linked

    def _normalize_issue(self, issue: Any) -> dict[str, Any]:
        if is_dataclass(issue):
            return asdict(issue)
        if isinstance(issue, dict):
            return issue
        return {
            "category": getattr(issue, "category", ""),
            "severity": getattr(issue, "severity", ""),
            "location": getattr(issue, "location", ""),
            "original": getattr(issue, "original", ""),
            "description": getattr(issue, "description", ""),
            "suggestion": getattr(issue, "suggestion", ""),
            "page": getattr(issue, "page", "")
        }

    def _extract_related_line_numbers(self, issue_dict: dict[str, Any]) -> list[int]:
        values = []
        location = issue_dict.get("location") or ""
        original = issue_dict.get("original") or ""

        values.extend(int(match) for match in re.findall(r"(\d+)", location))

        if not values:
            values.extend(int(match) for match in re.findall(r"(\d+)\s*:", original))

        unique_values = []
        seen = set()
        for value in values:
            if value not in seen:
                seen.add(value)
                unique_values.append(value)
        return unique_values

    def _build_source_location(self, mapping: dict[str, Any] | None) -> str:
        if not mapping:
            return "unmapped"
        source_ref = mapping.get("source_ref", {})
        package_entry = source_ref.get("package_entry", "")
        xml_path = source_ref.get("xml_path", "")
        return f"{package_entry} | {xml_path}"

    def _count_by_field(self, issues: list[dict[str, Any]], field_name: str) -> dict[str, int]:
        counts: dict[str, int] = {}
        for issue in issues:
            key = str(issue.get(field_name) or "unknown")
            counts[key] = counts.get(key, 0) + 1
        return counts
