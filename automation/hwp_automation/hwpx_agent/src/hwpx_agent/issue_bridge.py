from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from .utils import SCHEMA_VERSION, ensure_dir, write_json


class IssuePlanBridge:
    def __init__(self, run_dir: str | Path):
        self.run_dir = Path(run_dir)
        if not self.run_dir.exists():
            raise FileNotFoundError(f"실행 폴더를 찾을 수 없습니다: {self.run_dir}")

        self.assets_dir = self.run_dir / "assets"
        self.proofreading_dir = self.assets_dir / "proofreading"
        self.rebuild_dir = self.assets_dir / "rebuild"
        self.issues_path = self.proofreading_dir / "issues.json"
        self.paragraphs_path = self.assets_dir / "blocks" / "paragraphs.json"
        self.table_cells_path = self.assets_dir / "tables" / "cells.json"

        self.issues = self._load_json(self.issues_path)
        self.paragraphs = self._load_json(self.paragraphs_path)
        self.table_cells = self._load_json(self.table_cells_path) if self.table_cells_path.exists() else []
        self.paragraph_by_id = {paragraph["asset_id"]: paragraph for paragraph in self.paragraphs}
        self.table_cell_by_id = {cell["asset_id"]: cell for cell in self.table_cells}
        self.asset_by_id = {}
        self.asset_by_id.update(self.paragraph_by_id)
        self.asset_by_id.update(self.table_cell_by_id)

    def init_review_files(self) -> dict[str, str]:
        ensure_dir(self.proofreading_dir)

        review_entries = []
        demo_entries = []
        demo_created = False

        for issue in self.issues:
            asset = self.asset_by_id.get(issue.get("origin_id"))
            paragraph = asset
            eligibility = self._get_rebuild_eligibility(issue, asset)

            entry = {
                "issue_id": issue.get("issue_id"),
                "selected": False,
                "eligible_for_rebuild": eligibility["eligible"],
                "blocking_reason": eligibility["blocking_reason"],
                "origin_id": issue.get("origin_id"),
                "origin_type": issue.get("origin_type") or (asset.get("asset_type") if asset else None),
                "page": issue.get("page"),
                "source_location": issue.get("source_location"),
                "issue_reason": issue.get("reason"),
                "issue_original_text": issue.get("original_text"),
                "issue_suggested_fix": issue.get("suggested_fix"),
                "current_text": asset.get("text") if asset else "",
                "current_paragraph_text": asset.get("text") if asset else "",
                "approved_new_text": "",
                "approval_note": ""
            }
            review_entries.append(entry)

            demo_entry = dict(entry)
            if not demo_created and eligibility["eligible"] and asset:
                demo_entry["selected"] = True
                demo_entry["approved_new_text"] = f"{paragraph.get('text', '')} (선택 수정안 테스트)"
                demo_entry["approval_note"] = "데모용 자동 선택"
                demo_created = True
            demo_entries.append(demo_entry)

        review_payload = {
            "schema_version": SCHEMA_VERSION,
            "run_dir": str(self.run_dir),
            "created_at": datetime.now().isoformat(timespec="seconds"),
            "notes": [
                "selected=true인 항목만 plan으로 변환됩니다.",
                "approved_new_text에는 최종 문단 전체 문장을 넣어야 합니다.",
                "표/그림/컨트롤 포함 문단은 현재 자동 복원 대상이 아닙니다."
            ],
            "entries": review_entries
        }

        demo_payload = {
            "schema_version": SCHEMA_VERSION,
            "run_dir": str(self.run_dir),
            "created_at": datetime.now().isoformat(timespec="seconds"),
            "notes": [
                "데모용 리뷰 파일입니다. 첫 번째 안전한 문단 이슈 하나가 선택돼 있습니다."
            ],
            "entries": demo_entries
        }

        sample_path = write_json(self.proofreading_dir / "issue_review.sample.json", review_payload)
        demo_path = write_json(self.proofreading_dir / "issue_review.demo.json", demo_payload)
        return {"sample_review": str(sample_path), "demo_review": str(demo_path)}

    def review_to_rebuild_plan(self, review_path: str | Path, output_path: str | Path | None = None) -> dict[str, Any]:
        review = self._load_json(Path(review_path))
        ensure_dir(self.rebuild_dir)

        grouped_updates: dict[str, dict[str, Any]] = {}
        conversion_log: list[dict[str, Any]] = []
        selected_count = 0
        skipped_count = 0

        for entry in review.get("entries", []):
            if not entry.get("selected", False):
                continue

            selected_count += 1
            origin_id = entry.get("origin_id")
            asset = self.asset_by_id.get(origin_id)
            eligibility = self._get_rebuild_eligibility({"origin_id": origin_id}, asset)
            approved_new_text = (entry.get("approved_new_text") or "").strip()

            if not eligibility["eligible"]:
                skipped_count += 1
                conversion_log.append({
                    "issue_id": entry.get("issue_id"),
                    "origin_id": origin_id,
                    "status": "skipped_ineligible",
                    "blocking_reason": eligibility["blocking_reason"]
                })
                continue

            if not approved_new_text:
                skipped_count += 1
                conversion_log.append({
                    "issue_id": entry.get("issue_id"),
                    "origin_id": origin_id,
                    "status": "skipped_missing_approved_text"
                })
                continue

            existing = grouped_updates.get(origin_id)
            if existing and existing["new_text"] != approved_new_text:
                skipped_count += 1
                conversion_log.append({
                    "issue_id": entry.get("issue_id"),
                    "origin_id": origin_id,
                    "status": "skipped_conflict_same_origin",
                    "existing_new_text": existing["new_text"],
                    "requested_new_text": approved_new_text
                })
                continue

            reason_parts = [entry.get("issue_id", ""), entry.get("issue_reason", ""), entry.get("approval_note", "")]
            reason_text = " | ".join(part for part in reason_parts if part)

            grouped_updates[origin_id] = {
                "update_id": f"upd_from_{entry.get('issue_id')}",
                "enabled": True,
                "origin_id": origin_id,
                "origin_type": entry.get("origin_type") or (asset.get("asset_type") if asset else None),
                "expected_current_text": asset.get("text", "") if asset else "",
                "new_text": approved_new_text,
                "reason": reason_text
            }
            conversion_log.append({
                "issue_id": entry.get("issue_id"),
                "origin_id": origin_id,
                "status": "converted"
            })

        updates = list(grouped_updates.values())
        plan = {
            "schema_version": SCHEMA_VERSION,
            "run_dir": str(self.run_dir),
            "created_at": datetime.now().isoformat(timespec="seconds"),
            "notes": [
                "issue_review에서 selected=true로 선택된 항목만 변환했습니다.",
                "같은 origin_id에 서로 다른 approved_new_text가 있으면 충돌로 건너뜁니다."
            ],
            "updates": updates
        }

        plan_output = Path(output_path) if output_path else self.rebuild_dir / "rebuild_plan.from_issue_review.json"
        write_json(plan_output, plan)
        write_json(self.rebuild_dir / "issue_review_conversion_log.json", conversion_log)

        summary = {
            "schema_version": SCHEMA_VERSION,
            "review_path": str(Path(review_path)),
            "plan_output": str(plan_output),
            "selected_count": selected_count,
            "converted_update_count": len(updates),
            "skipped_count": skipped_count,
            "created_at": datetime.now().isoformat(timespec="seconds")
        }
        write_json(self.rebuild_dir / "issue_review_conversion_summary.json", summary)
        return {"summary": summary, "plan": plan}

    def _load_json(self, path: Path):
        return json.loads(path.read_text(encoding="utf-8"))

    def _get_rebuild_eligibility(self, issue: dict[str, Any], asset: dict[str, Any] | None) -> dict[str, Any]:
        if issue.get("origin_id") == "unmapped":
            return {"eligible": False, "blocking_reason": "unmapped_issue"}
        if asset is None:
            return {"eligible": False, "blocking_reason": "missing_origin_asset"}

        if asset.get("asset_type") == "table_cell":
            classification = asset.get("classification", {})
            if classification.get("rebuild_safe_text_only"):
                return {"eligible": True, "blocking_reason": None}
            content_type = classification.get("content_type", "unknown")
            return {
                "eligible": False,
                "blocking_reason": f"table_cell_not_rebuild_safe:{content_type}"
            }

        classification = asset.get("classification", {})
        if "rebuild_safe_text_only" in classification:
            if classification.get("rebuild_safe_text_only"):
                return {"eligible": True, "blocking_reason": None}
            content_type = classification.get("content_type", "unknown")
            context_type = classification.get("context_type", "unknown")
            return {
                "eligible": False,
                "blocking_reason": f"paragraph_not_rebuild_safe:{context_type}:{content_type}"
            }
        if asset.get("embedded_object_refs"):
            return {"eligible": False, "blocking_reason": "paragraph_has_embedded_objects"}
        if asset.get("control_tags"):
            return {"eligible": False, "blocking_reason": "paragraph_has_control_tags"}
        if not (asset.get("text") or "").strip():
            return {"eligible": False, "blocking_reason": "empty_paragraph_text"}
        runs = asset.get("runs", [])
        if not runs:
            return {"eligible": False, "blocking_reason": "missing_runs"}
        if any(run.get("child_tags") for run in runs):
            return {"eligible": False, "blocking_reason": "run_has_child_controls"}
        return {"eligible": True, "blocking_reason": None}
