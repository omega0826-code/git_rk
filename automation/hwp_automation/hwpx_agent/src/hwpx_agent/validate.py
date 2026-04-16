from __future__ import annotations

import json
import zipfile
from datetime import datetime
from pathlib import Path
from typing import Any

from .utils import SCHEMA_VERSION, ensure_dir, write_json


class RunValidator:
    def __init__(self, run_dir: str | Path):
        self.run_dir = Path(run_dir)
        if not self.run_dir.exists():
            raise FileNotFoundError(f"실행 결과 폴더를 찾을 수 없습니다: {self.run_dir}")

        self.assets_dir = self.run_dir / "assets"
        self.proofreading_dir = self.assets_dir / "proofreading"
        self.rebuild_dir = self.run_dir / "rebuild"
        self.validation_dir = self.run_dir / "validation"

        self.document_path = self.assets_dir / "document.json"
        self.page_summary_path = self.assets_dir / "pages" / "page_summary.json"
        self.paragraphs_path = self.assets_dir / "blocks" / "paragraphs.json"
        self.tables_path = self.assets_dir / "tables" / "tables.json"
        self.table_cells_path = self.assets_dir / "tables" / "cells.json"
        self.issues_path = self.proofreading_dir / "issues.json"
        self.proofread_summary_path = self.proofreading_dir / "summary.json"

    def run(
        self,
        expected_page_count: int | None = None,
        require_proofread: bool = False,
        require_rebuild: bool = False,
        require_table_cell_issues: bool = False,
        rebuild_hwpx: str | Path | None = None,
        expect_string: str | None = None
    ) -> dict[str, Any]:
        findings: list[dict[str, Any]] = []

        document = self._load_json_if_exists(self.document_path)
        page_summary = self._load_json_if_exists(self.page_summary_path)
        paragraphs = self._load_json_if_exists(self.paragraphs_path) or []
        tables = self._load_json_if_exists(self.tables_path) or []
        table_cells = self._load_json_if_exists(self.table_cells_path) or []
        issues = self._load_json_if_exists(self.issues_path) or []
        proofread_summary = self._load_json_if_exists(self.proofread_summary_path)

        self._check_exists(self.document_path, findings, label="document.json")
        self._check_exists(self.page_summary_path, findings, label="page_summary.json")
        self._check_exists(self.paragraphs_path, findings, label="paragraphs.json")
        self._check_exists(self.tables_path, findings, label="tables.json")
        self._check_exists(self.table_cells_path, findings, label="cells.json")

        if document:
            counts = document.get("counts", {})
            self._check_equal(counts.get("paragraphs"), len(paragraphs), findings, "document paragraph count")
            self._check_equal(counts.get("tables"), len(tables), findings, "document table count")
            self._check_equal(counts.get("table_cells"), len(table_cells), findings, "document table cell count")

        if page_summary:
            pyhwpx = page_summary.get("pyhwpx", {})
            assignment = page_summary.get("assignment", {})
            actual_page_count = pyhwpx.get("page_count")
            if actual_page_count is not None:
                self._add_findings(findings, "pass", "page count detected", {"page_count": actual_page_count})
            else:
                self._add_findings(findings, "warn", "page count missing", {})

            if expected_page_count is not None:
                self._check_equal(actual_page_count, expected_page_count, findings, "expected page count")

            method = assignment.get("method")
            if method:
                self._add_findings(findings, "pass", "page assignment method", {"method": method})

        if require_proofread:
            self._check_exists(self.issues_path, findings, label="proofreading/issues.json")
            self._check_exists(self.proofread_summary_path, findings, label="proofreading/summary.json")

            if proofread_summary:
                self._check_equal(proofread_summary.get("issue_count"), len(issues), findings, "proofread issue count")

            origin_types = self._count_by_field(issues, "origin_type")
            self._add_findings(findings, "pass", "proofread issue origin types", origin_types)

            if require_table_cell_issues:
                table_cell_issue_count = origin_types.get("table_cell", 0)
                level = "pass" if table_cell_issue_count > 0 else "fail"
                self._add_findings(
                    findings,
                    level,
                    "table cell issues present",
                    {"table_cell_issue_count": table_cell_issue_count}
                )

        rebuild_target = Path(rebuild_hwpx) if rebuild_hwpx else None
        if require_rebuild:
            if rebuild_target is None:
                rebuild_target = self._guess_rebuild_hwpx()
            if rebuild_target is None:
                self._add_findings(findings, "fail", "rebuilt hwpx not found", {})
            else:
                self._check_exists(rebuild_target, findings, label="rebuilt hwpx")
                if rebuild_target.exists():
                    self._validate_hwpx_zip(rebuild_target, findings, expect_string=expect_string)

        status = self._overall_status(findings)
        report = {
            "schema_version": SCHEMA_VERSION,
            "run_dir": str(self.run_dir),
            "status": status,
            "created_at": datetime.now().isoformat(timespec="seconds"),
            "findings": findings
        }

        ensure_dir(self.validation_dir)
        output_path = self.validation_dir / "validation_summary.json"
        write_json(output_path, report)
        report["output_path"] = str(output_path)
        return report

    def _load_json_if_exists(self, path: Path):
        if not path.exists():
            return None
        return json.loads(path.read_text(encoding="utf-8"))

    def _check_exists(self, path: Path, findings: list[dict[str, Any]], label: str) -> None:
        level = "pass" if path.exists() else "fail"
        self._add_findings(findings, level, f"{label} exists", {"path": str(path)})

    def _check_equal(self, actual: Any, expected: Any, findings: list[dict[str, Any]], label: str) -> None:
        level = "pass" if actual == expected else "fail"
        self._add_findings(findings, level, label, {"actual": actual, "expected": expected})

    def _validate_hwpx_zip(self, path: Path, findings: list[dict[str, Any]], expect_string: str | None) -> None:
        try:
            with zipfile.ZipFile(path, "r") as archive:
                names = set(archive.namelist())
                required = {"mimetype", "Contents/content.hpf"}
                missing = sorted(required - names)
                if missing:
                    self._add_findings(findings, "fail", "rebuilt hwpx missing required entries", {"missing": missing})
                else:
                    self._add_findings(findings, "pass", "rebuilt hwpx zip valid", {"path": str(path)})

                if expect_string:
                    found = False
                    found_entry = None
                    for name in names:
                        if not (name.startswith("Contents/section") and name.endswith(".xml")):
                            continue
                        content = archive.read(name).decode("utf-8", errors="ignore")
                        if expect_string in content:
                            found = True
                            found_entry = name
                            break
                    self._add_findings(
                        findings,
                        "pass" if found else "fail",
                        "expected rebuild marker string",
                        {"expect_string": expect_string, "found_entry": found_entry}
                    )
        except zipfile.BadZipFile:
            self._add_findings(findings, "fail", "rebuilt hwpx zip invalid", {"path": str(path)})

    def _guess_rebuild_hwpx(self) -> Path | None:
        candidates = sorted(self.rebuild_dir.glob("*.hwpx"))
        if not candidates:
            return None
        return candidates[-1]

    def _count_by_field(self, items: list[dict[str, Any]], field_name: str) -> dict[str, int]:
        result: dict[str, int] = {}
        for item in items:
            key = str(item.get(field_name) or "unknown")
            result[key] = result.get(key, 0) + 1
        return result

    def _add_findings(self, findings: list[dict[str, Any]], level: str, title: str, payload: dict[str, Any]) -> None:
        findings.append({"level": level, "title": title, "details": payload})

    def _overall_status(self, findings: list[dict[str, Any]]) -> str:
        if any(item["level"] == "fail" for item in findings):
            return "fail"
        if any(item["level"] == "warn" for item in findings):
            return "warn"
        return "pass"
