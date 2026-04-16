from __future__ import annotations

from pathlib import Path
from typing import Any

from .assetizer import HwpxAssetizer
from .issue_bridge import IssuePlanBridge
from .proofread import AssetProofreader
from .validate import RunValidator


class HwpxPipelineRunner:
    def __init__(
        self,
        input_path: str | Path,
        output_root: str | Path | None = None,
        run_name: str | None = None,
        copy_source: bool = True,
    ):
        self.input_path = Path(input_path)
        self.output_root = Path(output_root) if output_root else None
        self.run_name = run_name
        self.copy_source = copy_source

    def run(
        self,
        include_spell: bool = False,
        expected_page_count: int | None = None,
        require_table_cell_issues: bool = False,
    ) -> dict[str, Any]:
        assetizer = HwpxAssetizer(
            hwpx_path=self.input_path,
            output_root=self.output_root,
            run_name=self.run_name,
            copy_source=self.copy_source,
        )
        assetize_result = assetizer.run()

        run_dir = Path(assetize_result["run_dir"])
        proofread_result = AssetProofreader(run_dir).run(include_spell=include_spell)
        review_result = IssuePlanBridge(run_dir).init_review_files()

        validator = RunValidator(run_dir)
        validation_summary = validator.run(
            expected_page_count=expected_page_count,
            require_proofread=True,
            require_rebuild=False,
            require_table_cell_issues=require_table_cell_issues,
        )

        return {
            "input_path": str(self.input_path),
            "run_name": assetize_result["run_name"],
            "run_dir": str(run_dir),
            "assetize": {
                "counts": assetize_result["document"]["counts"],
                "page_summary": assetize_result["document"]["page_summary"],
            },
            "proofread": proofread_result["summary"],
            "review_files": review_result,
            "validation": {
                "status": validation_summary["status"],
                "output_path": validation_summary["output_path"],
            },
        }
