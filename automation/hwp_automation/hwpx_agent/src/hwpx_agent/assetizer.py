from __future__ import annotations

import shutil
import zipfile
from datetime import datetime
from pathlib import Path
from typing import Any

from lxml import etree

from .namespaces import NS, local_name, tag
from .page_map import build_xml_page_map, try_build_pyhwpx_root_page_map
from .utils import SCHEMA_VERSION, compact_text, element_children_summary, ensure_dir, sanitize_name, sha1_file, write_json


KEY_PACKAGE_PREFIXES = ("Contents/", "META-INF/", "Preview/")
KEY_PACKAGE_FILES = {"mimetype", "version.xml", "settings.xml"}


class HwpxAssetizer:
    def __init__(self, hwpx_path: str, output_root: str | None = None, run_name: str | None = None, copy_source: bool = True):
        self.hwpx_path = Path(hwpx_path)
        if not self.hwpx_path.exists():
            raise FileNotFoundError(f"입력 파일을 찾을 수 없습니다: {self.hwpx_path}")

        self.project_root = Path(__file__).resolve().parents[3]
        self.output_root = Path(output_root) if output_root else self.project_root / "hwpx_agent" / "runs"
        self.copy_source = copy_source

        base_name = run_name or sanitize_name(self.hwpx_path.stem)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.run_name = f"{base_name}_{timestamp}"
        self.run_dir = self.output_root / self.run_name

        self.source_dir = self.run_dir / "source"
        self.package_dir = self.run_dir / "package"
        self.assets_dir = self.run_dir / "assets"
        self.logs_dir = self.run_dir / "logs"
        self.blocks_dir = self.assets_dir / "blocks"
        self.tables_dir = self.assets_dir / "tables"
        self.images_dir = self.assets_dir / "images"
        self.styles_dir = self.assets_dir / "styles"
        self.sections_dir = self.assets_dir / "sections"
        self.masterpages_dir = self.assets_dir / "masterpages"
        self.pages_dir = self.assets_dir / "pages"

    def run(self) -> dict[str, Any]:
        self._prepare_directories()

        if self.copy_source:
            shutil.copy2(self.hwpx_path, self.source_dir / self.hwpx_path.name)

        notes: list[str] = []

        with zipfile.ZipFile(self.hwpx_path, "r") as archive:
            package_manifest = self._build_package_manifest(archive)
            write_json(self.package_dir / "package_manifest.json", package_manifest)
            self._extract_key_package_files(archive)

            content_hpf_root = self._read_xml(archive, "Contents/content.hpf")
            header_root = self._read_xml(archive, "Contents/header.xml")

            section_entries = sorted(
                name for name in archive.namelist() if name.startswith("Contents/section") and name.endswith(".xml")
            )
            masterpage_entries = sorted(
                name for name in archive.namelist() if name.startswith("Contents/masterpage") and name.endswith(".xml")
            )

            section_roots = [(entry, self._read_xml(archive, entry)) for entry in section_entries]
            masterpage_roots = [(entry, self._read_xml(archive, entry)) for entry in masterpage_entries]

            content_manifest = self._parse_content_hpf(content_hpf_root)
            styles = self._parse_header_styles(header_root)
            write_json(self.styles_dir / "char_styles.json", styles["char_styles"])
            write_json(self.styles_dir / "para_styles.json", styles["para_styles"])
            write_json(self.styles_dir / "named_styles.json", styles["named_styles"])

            xml_page_summary = build_xml_page_map(section_roots)
            pyhwpx_summary = try_build_pyhwpx_root_page_map(self.hwpx_path)

            if pyhwpx_summary["page_count"] and pyhwpx_summary["page_count"] != xml_page_summary["estimated_total_pages"]:
                notes.append(
                    "pyhwpx 실측 페이지 수와 XML pageBreak 추정 페이지 수가 다릅니다. "
                    "문단별 page_no는 현재 XML 추정값만 기록했습니다."
                )

            page_summary = {
                "schema_version": SCHEMA_VERSION,
                "xml_page_map": {
                    "method": xml_page_summary["method"],
                    "estimated_total_pages": xml_page_summary["estimated_total_pages"],
                    "mapped_paragraphs": xml_page_summary["mapped_paragraphs"]
                },
                "pyhwpx": pyhwpx_summary,
                "notes": notes
            }
            write_json(self.pages_dir / "page_summary.json", page_summary)
            write_json(self.pages_dir / "paragraph_page_map.json", xml_page_summary["paragraph_to_page"])

            section_assets, paragraph_assets, table_assets, image_occurrences = self._parse_sections(
                section_roots,
                content_manifest["manifest_map"],
                xml_page_summary["paragraph_to_page"]
            )
            masterpage_assets, masterpage_occurrences = self._parse_masterpages(
                masterpage_roots,
                content_manifest["manifest_map"]
            )
            image_occurrences.extend(masterpage_occurrences)
            image_binaries = self._extract_binary_assets(archive, content_manifest["binary_items"])
            paragraph_summary = self._build_paragraph_summary(paragraph_assets)
            page_summary = self._apply_page_numbers(
                paragraph_assets=paragraph_assets,
                table_assets=table_assets,
                image_occurrences=image_occurrences,
                xml_page_summary=xml_page_summary,
                pyhwpx_summary=pyhwpx_summary,
                notes=notes
            )
            table_cell_assets = self._build_table_cell_assets(table_assets)

            asset_index = {
                "schema_version": SCHEMA_VERSION,
                "files": {
                    "document": "assets/document.json",
                    "paragraphs": "assets/blocks/paragraphs.json",
                    "paragraph_summary": "assets/blocks/paragraph_summary.json",
                    "tables": "assets/tables/tables.json",
                    "table_cells": "assets/tables/cells.json",
                    "image_binaries": "assets/images/binaries.json",
                    "image_occurrences": "assets/images/occurrences.json",
                    "sections": "assets/sections/sections.json",
                    "masterpages": "assets/masterpages/masterpages.json",
                    "page_summary": "assets/pages/page_summary.json",
                    "paragraph_page_map": "assets/pages/paragraph_page_map.json"
                }
            }

            write_json(self.blocks_dir / "paragraphs.json", paragraph_assets)
            write_json(self.blocks_dir / "paragraph_summary.json", paragraph_summary)
            write_json(self.tables_dir / "tables.json", table_assets)
            write_json(self.tables_dir / "cells.json", table_cell_assets)
            write_json(self.images_dir / "binaries.json", image_binaries)
            write_json(self.images_dir / "occurrences.json", image_occurrences)
            write_json(self.sections_dir / "sections.json", section_assets)
            write_json(self.masterpages_dir / "masterpages.json", masterpage_assets)
            write_json(self.pages_dir / "page_summary.json", page_summary)
            write_json(self.pages_dir / "paragraph_page_map.json", self._build_paragraph_page_map(paragraph_assets))
            if pyhwpx_summary["root_paragraph_to_page"]:
                write_json(self.pages_dir / "root_body_page_map.json", pyhwpx_summary["root_paragraph_to_page"])
            write_json(self.assets_dir / "asset_index.json", asset_index)

            document_asset = {
                "schema_version": SCHEMA_VERSION,
                "document_id": sanitize_name(self.hwpx_path.stem),
                "source_file_name": self.hwpx_path.name,
                "source_file_sha1": sha1_file(self.hwpx_path),
                "created_at": datetime.now().isoformat(timespec="seconds"),
                "package": {
                    "entry_count": package_manifest["entry_count"],
                    "section_count": len(section_entries),
                    "masterpage_count": len(masterpage_entries),
                    "bindata_count": package_manifest["bindata_count"]
                },
                "counts": {
                    "paragraphs": len(paragraph_assets),
                    "tables": len(table_assets),
                    "table_cells": len(table_cell_assets),
                    "image_binaries": len(image_binaries),
                    "image_occurrences": len(image_occurrences),
                    "sections": len(section_assets),
                    "masterpages": len(masterpage_assets),
                    "char_styles": len(styles["char_styles"]),
                    "para_styles": len(styles["para_styles"]),
                    "named_styles": len(styles["named_styles"])
                },
                "paragraph_breakdown": paragraph_summary,
                "page_summary": page_summary,
                "asset_files": asset_index["files"],
                "notes": notes
            }
            write_json(self.assets_dir / "document.json", document_asset)

            write_json(
                self.logs_dir / "assetize_log.json",
                {
                    "schema_version": SCHEMA_VERSION,
                    "run_name": self.run_name,
                    "created_at": datetime.now().isoformat(timespec="seconds"),
                    "notes": notes
                }
            )

            return {
                "run_name": self.run_name,
                "run_dir": str(self.run_dir),
                "document": document_asset
            }

    def _prepare_directories(self) -> None:
        for path in [
            self.source_dir,
            self.package_dir,
            self.assets_dir,
            self.logs_dir,
            self.blocks_dir,
            self.tables_dir,
            self.images_dir / "raw",
            self.styles_dir,
            self.sections_dir,
            self.masterpages_dir,
            self.pages_dir
        ]:
            ensure_dir(path)

    def _build_package_manifest(self, archive: zipfile.ZipFile) -> dict[str, Any]:
        entries = []
        bindata_count = 0
        for info in archive.infolist():
            if info.filename.startswith("BinData/"):
                bindata_count += 1
            entries.append(
                {
                    "name": info.filename,
                    "file_size": info.file_size,
                    "compress_size": info.compress_size,
                    "crc": info.CRC
                }
            )
        return {
            "schema_version": SCHEMA_VERSION,
            "entry_count": len(entries),
            "bindata_count": bindata_count,
            "entries": entries
        }

    def _extract_key_package_files(self, archive: zipfile.ZipFile) -> None:
        for entry in archive.namelist():
            if entry in KEY_PACKAGE_FILES or entry.startswith(KEY_PACKAGE_PREFIXES):
                target = self.package_dir / entry
                ensure_dir(target.parent)
                with target.open("wb") as handle:
                    handle.write(archive.read(entry))

    def _read_xml(self, archive: zipfile.ZipFile, entry_name: str):
        return etree.fromstring(archive.read(entry_name))

    def _parse_content_hpf(self, root) -> dict[str, Any]:
        manifest_items = []
        manifest_map = {}
        binary_items = []

        for item in root.findall(".//opf:item", NS):
            payload = {
                "id": item.get("id", ""),
                "href": item.get("href", ""),
                "media_type": item.get("media-type", ""),
                "is_embedded": item.get("isEmbeded", "")
            }
            manifest_items.append(payload)
            manifest_map[payload["id"]] = payload
            if payload["href"].startswith("BinData/"):
                binary_items.append(payload)

        spine = []
        for itemref in root.findall(".//opf:itemref", NS):
            spine.append({"idref": itemref.get("idref", ""), "linear": itemref.get("linear", "")})

        write_json(
            self.package_dir / "content_manifest.json",
            {"schema_version": SCHEMA_VERSION, "manifest_items": manifest_items, "spine": spine}
        )

        return {
            "manifest_items": manifest_items,
            "manifest_map": manifest_map,
            "binary_items": binary_items,
            "spine": spine
        }

    def _parse_header_styles(self, root) -> dict[str, list[dict[str, Any]]]:
        char_styles = []
        para_styles = []
        named_styles = []

        char_props = root.find(".//hh:charProperties", NS)
        if char_props is not None:
            for char_pr in char_props.findall("hh:charPr", NS):
                char_styles.append(
                    {
                        "style_id": char_pr.get("id", ""),
                        "attributes": dict(char_pr.attrib),
                        "children": element_children_summary(char_pr)
                    }
                )

        para_props = root.find(".//hh:paraProperties", NS)
        if para_props is not None:
            for para_pr in para_props.findall("hh:paraPr", NS):
                para_styles.append(
                    {
                        "style_id": para_pr.get("id", ""),
                        "attributes": dict(para_pr.attrib),
                        "children": element_children_summary(para_pr)
                    }
                )

        styles_root = root.find(".//hh:styles", NS)
        if styles_root is not None:
            for style in styles_root.findall("hh:style", NS):
                named_styles.append(
                    {
                        "style_id": style.get("id", ""),
                        "attributes": dict(style.attrib),
                        "children": element_children_summary(style)
                    }
                )

        return {"char_styles": char_styles, "para_styles": para_styles, "named_styles": named_styles}

    def _parse_sections(self, section_roots: list[tuple[str, Any]], manifest_map: dict[str, dict[str, Any]], paragraph_page_map: dict[int, int]):
        section_assets = []
        paragraph_assets = []
        table_assets = []
        image_occurrences = []

        paragraph_element_to_asset_id: dict[Any, str] = {}
        paragraph_element_to_root_index: dict[Any, int] = {}

        global_paragraph_index = 0
        global_root_paragraph_index = 0
        global_table_index = 0
        global_image_occurrence_index = 0

        for section_index, (entry_name, root) in enumerate(section_roots):
            section_id = f"sec{section_index:04d}"
            paragraph_ids = []
            table_ids = []
            image_occurrence_ids = []
            section_paragraph_index = 0
            section_table_index = 0
            last_non_empty_text = ""

            for paragraph in root.iter(tag("hp", "p")):
                if self._is_in_table(paragraph) or self._is_in_header_footer(paragraph):
                    continue

                global_paragraph_index += 1
                section_paragraph_index += 1
                paragraph_id = f"{section_id}.p{section_paragraph_index:05d}"
                paragraph_ids.append(paragraph_id)

                context = self._describe_paragraph_context(paragraph)
                root_flow_index = None
                if context["is_root_flow"]:
                    global_root_paragraph_index += 1
                    root_flow_index = global_root_paragraph_index

                host_body_element = context["host_body_paragraph_element"]
                host_body_paragraph_id = paragraph_id if context["is_root_flow"] else paragraph_element_to_asset_id.get(host_body_element)
                host_root_flow_index = root_flow_index if context["is_root_flow"] else paragraph_element_to_root_index.get(host_body_element)

                paragraph_text = self._extract_paragraph_text(paragraph)
                paragraph_page_no = paragraph_page_map.get(global_paragraph_index)

                embedded_refs = []
                runs = []
                char_pr_ids = []
                control_tags = set()

                for run in paragraph.findall(".//hp:run", NS):
                    if not self._is_owned_by_paragraph(run, paragraph):
                        continue
                    if self._has_ancestor(run, tag("hp", "tbl"), paragraph):
                        continue
                    run_text = self._extract_run_text(run)
                    child_tags = [local_name(child.tag) for child in run.iterchildren() if local_name(child.tag) != "t"]
                    control_tags.update(child_tags)
                    char_pr_id = run.get("charPrIDRef")
                    if char_pr_id:
                        char_pr_ids.append(char_pr_id)
                    runs.append(
                        {
                            "run_index": len(runs) + 1,
                            "text": run_text,
                            "char_pr_id_ref": char_pr_id,
                            "child_tags": child_tags
                        }
                    )

                paragraph_pictures = list(paragraph.iter(tag("hp", "pic")))

                for image_position, picture in enumerate(paragraph_pictures, start=1):
                    global_image_occurrence_index += 1
                    occurrence_id = f"imgocc{global_image_occurrence_index:05d}"
                    embedded_refs.append(occurrence_id)
                    image_occurrence_ids.append(occurrence_id)
                    image_occurrences.append(
                        self._build_image_occurrence(
                            occurrence_id=occurrence_id,
                            picture=picture,
                            owner_type="section",
                            owner_id=section_id,
                            parent_paragraph_id=paragraph_id,
                            entry_name=entry_name,
                            xml_path=f"{entry_name}#/body/p[{section_paragraph_index}]/pic[{image_position}]",
                            page_no=paragraph_page_no,
                            manifest_map=manifest_map
                        )
                    )

                paragraph_tables = list(paragraph.iter(tag("hp", "tbl")))

                for table_position, table in enumerate(paragraph_tables, start=1):
                    global_table_index += 1
                    section_table_index += 1
                    table_id = f"tbl{global_table_index:05d}"
                    table_ids.append(table_id)
                    embedded_refs.append(table_id)
                    table_assets.append(
                        self._build_table_asset(
                            table_id=table_id,
                            table=table,
                            section_id=section_id,
                            section_index=section_index,
                            section_table_index=section_table_index,
                            parent_paragraph_id=paragraph_id,
                            entry_name=entry_name,
                            paragraph_index=section_paragraph_index,
                            page_no=paragraph_page_no,
                            title_hint=last_non_empty_text,
                            table_position=table_position
                        )
                    )

                classification = self._build_paragraph_classification(
                    paragraph=paragraph,
                    paragraph_text=paragraph_text,
                    control_tags=sorted(control_tags),
                    table_count=len(paragraph_tables),
                    image_count=len(paragraph_pictures),
                    host_body_paragraph_id=host_body_paragraph_id,
                    root_flow_index=root_flow_index,
                    host_root_flow_index=host_root_flow_index
                )
                if paragraph_text and classification["context_type"] == "body":
                    last_non_empty_text = paragraph_text

                paragraph_assets.append(
                    {
                        "schema_version": SCHEMA_VERSION,
                        "asset_id": paragraph_id,
                        "asset_type": "paragraph",
                        "section_id": section_id,
                        "section_index": section_index,
                        "section_paragraph_index": section_paragraph_index,
                        "global_paragraph_index": global_paragraph_index,
                        "root_flow_paragraph_index": root_flow_index,
                        "source_ref": {
                            "package_entry": entry_name,
                            "xml_path": f"{entry_name}#/body/p[{section_paragraph_index}]",
                            "parent_asset_id": host_body_paragraph_id if not context["is_root_flow"] else None
                        },
                        "page_no": paragraph_page_no,
                        "page_source": "xml_pagebreak_estimate" if paragraph_page_no else None,
                        "text": paragraph_text,
                        "title_mark": paragraph.find(".//hp:titleMark", NS) is not None,
                        "style_refs": {
                            "style_id_ref": paragraph.get("styleIDRef"),
                            "para_pr_id_ref": paragraph.get("paraPrIDRef"),
                            "char_pr_id_refs": sorted(set(char_pr_ids))
                        },
                        "layout": {
                            "page_break": paragraph.get("pageBreak", "0") == "1",
                            "column_break": paragraph.get("columnBreak", "0") == "1",
                            "merged": paragraph.get("merged", "0") == "1"
                        },
                        "run_count": len(runs),
                        "runs": runs,
                        "embedded_object_refs": embedded_refs,
                        "control_tags": sorted(control_tags),
                        "classification": classification
                    }
                )

                paragraph_element_to_asset_id[paragraph] = paragraph_id
                if root_flow_index is not None:
                    paragraph_element_to_root_index[paragraph] = root_flow_index

            section_assets.append(
                {
                    "schema_version": SCHEMA_VERSION,
                    "section_id": section_id,
                    "section_index": section_index,
                    "package_entry": entry_name,
                    "paragraph_ids": paragraph_ids,
                    "table_ids": table_ids,
                    "image_occurrence_ids": image_occurrence_ids
                }
            )

        return section_assets, paragraph_assets, table_assets, image_occurrences

    def _parse_masterpages(self, masterpage_roots: list[tuple[str, Any]], manifest_map: dict[str, dict[str, Any]]):
        masterpage_assets = []
        image_occurrences = []
        global_occurrence_index = 0

        for masterpage_index, (entry_name, root) in enumerate(masterpage_roots):
            masterpage_id = root.get("id") or f"masterpage{masterpage_index}"
            picture_refs = []

            for picture_index, picture in enumerate(root.iter(tag("hp", "pic")), start=1):
                global_occurrence_index += 1
                occurrence_id = f"imgocc_mp{global_occurrence_index:05d}"
                picture_refs.append(occurrence_id)
                image_occurrences.append(
                    self._build_image_occurrence(
                        occurrence_id=occurrence_id,
                        picture=picture,
                        owner_type="masterpage",
                        owner_id=masterpage_id,
                        parent_paragraph_id=None,
                        entry_name=entry_name,
                        xml_path=f"{entry_name}#/masterPage/pic[{picture_index}]",
                        page_no=None,
                        manifest_map=manifest_map
                    )
                )

            masterpage_assets.append(
                {
                    "schema_version": SCHEMA_VERSION,
                    "asset_id": masterpage_id,
                    "asset_type": "masterpage",
                    "source_ref": {
                        "package_entry": entry_name,
                        "xml_path": f"{entry_name}#/masterPage",
                        "parent_asset_id": None
                    },
                    "masterpage_index": masterpage_index,
                    "attributes": dict(root.attrib),
                    "image_occurrence_ids": picture_refs
                }
            )

        return masterpage_assets, image_occurrences

    def _extract_binary_assets(self, archive: zipfile.ZipFile, binary_items: list[dict[str, Any]]):
        binaries = []
        for item in binary_items:
            href = item["href"]
            if href not in archive.namelist():
                continue
            file_name = Path(href).name
            target = self.images_dir / "raw" / file_name
            with target.open("wb") as handle:
                handle.write(archive.read(href))
            binaries.append(
                {
                    "schema_version": SCHEMA_VERSION,
                    "binary_id": item["id"],
                    "package_entry": href,
                    "file_name": file_name,
                    "media_type": item["media_type"],
                    "stored_path": str(target.relative_to(self.run_dir)).replace("\\", "/")
                }
            )
        return binaries

    def _build_table_asset(
        self,
        table_id: str,
        table,
        section_id: str,
        section_index: int,
        section_table_index: int,
        parent_paragraph_id: str,
        entry_name: str,
        paragraph_index: int,
        page_no: int | None,
        title_hint: str,
        table_position: int
    ) -> dict[str, Any]:
        row_count = int(table.get("rowCnt", 0))
        col_count = int(table.get("colCnt", 0))
        cells = []

        for cell_index, cell in enumerate(table.iter(tag("hp", "tc")), start=1):
            addr = cell.find(tag("hp", "cellAddr"))
            span = cell.find(tag("hp", "cellSpan"))
            cell_text = self._extract_table_cell_text(cell)
            cell_control_tags = self._extract_table_cell_control_tags(cell)
            cell_picture_count = len(list(cell.iter(tag("hp", "pic"))))
            cell_nested_table_count = len(list(cell.iter(tag("hp", "tbl"))))
            cell_classification = self._build_table_cell_classification(
                text=cell_text,
                control_tags=cell_control_tags,
                picture_count=cell_picture_count,
                nested_table_count=cell_nested_table_count
            )
            cells.append(
                {
                    "schema_version": SCHEMA_VERSION,
                    "asset_id": f"{table_id}.c{cell_index:05d}",
                    "asset_type": "table_cell",
                    "table_id": table_id,
                    "cell_index": cell_index,
                    "row": int(addr.get("rowAddr", 0)) if addr is not None else 0,
                    "col": int(addr.get("colAddr", 0)) if addr is not None else 0,
                    "row_span": int(span.get("rowSpan", 1)) if span is not None else 1,
                    "col_span": int(span.get("colSpan", 1)) if span is not None else 1,
                    "text": cell_text,
                    "page_no": page_no,
                    "page_source": "xml_pagebreak_estimate" if page_no else None,
                    "source_ref": {
                        "package_entry": entry_name,
                        "xml_path": f"{entry_name}#/body/p[{paragraph_index}]/tbl[{table_position}]/tc[{cell_index}]",
                        "parent_asset_id": table_id
                    },
                    "classification": cell_classification
                }
            )

        return {
            "schema_version": SCHEMA_VERSION,
            "asset_id": table_id,
            "asset_type": "table",
            "section_id": section_id,
            "section_index": section_index,
            "section_table_index": section_table_index,
            "paragraph_index": paragraph_index,
            "table_position": table_position,
            "source_ref": {
                "package_entry": entry_name,
                "xml_path": f"{entry_name}#/body/p[{paragraph_index}]/tbl[{table_position}]",
                "parent_asset_id": parent_paragraph_id
            },
            "page_no": page_no,
            "page_source": "xml_pagebreak_estimate" if page_no else None,
            "title": title_hint,
            "row_count": row_count,
            "col_count": col_count,
            "cells": cells
        }

    def _build_image_occurrence(
        self,
        occurrence_id: str,
        picture,
        owner_type: str,
        owner_id: str,
        parent_paragraph_id: str | None,
        entry_name: str,
        xml_path: str,
        page_no: int | None,
        manifest_map: dict[str, dict[str, Any]]
    ) -> dict[str, Any]:
        image_node = picture.find(f".//{tag('hc', 'img')}")
        binary_item_id_ref = image_node.get("binaryItemIDRef") if image_node is not None else None
        manifest_item = manifest_map.get(binary_item_id_ref or "", {})
        comment_node = picture.find(tag("hp", "shapeComment"))
        current_size = picture.find(tag("hp", "curSz"))
        original_size = picture.find(tag("hp", "orgSz"))

        return {
            "schema_version": SCHEMA_VERSION,
            "asset_id": occurrence_id,
            "asset_type": "image_occurrence",
            "section_id": owner_id if owner_type == "section" else None,
            "owner_type": owner_type,
            "owner_id": owner_id,
            "source_ref": {
                "package_entry": entry_name,
                "xml_path": xml_path,
                "parent_asset_id": parent_paragraph_id
            },
            "page_no": page_no,
            "page_source": "xml_pagebreak_estimate" if page_no else None,
            "binary_item_id_ref": binary_item_id_ref,
            "binary_package_entry": manifest_item.get("href"),
            "media_type": manifest_item.get("media_type"),
            "comment": compact_text(comment_node.text if comment_node is not None else ""),
            "current_size": dict(current_size.attrib) if current_size is not None else {},
            "original_size": dict(original_size.attrib) if original_size is not None else {}
        }

    def _build_table_cell_assets(self, table_assets: list[dict[str, Any]]) -> list[dict[str, Any]]:
        cells: list[dict[str, Any]] = []
        for table in table_assets:
            for cell in table.get("cells", []):
                cell_asset = dict(cell)
                cell_asset["table_id"] = table.get("asset_id")
                cell_asset["section_id"] = table.get("section_id")
                cell_asset["section_index"] = table.get("section_index")
                cell_asset["section_table_index"] = table.get("section_table_index")
                cell_asset["table_title"] = table.get("title")
                cells.append(cell_asset)
        return cells

    def _build_table_cell_classification(
        self,
        text: str,
        control_tags: list[str],
        picture_count: int,
        nested_table_count: int
    ) -> dict[str, Any]:
        has_text = bool(text.strip())
        if has_text and not control_tags and not picture_count and not nested_table_count:
            content_type = "text"
        elif not has_text and not control_tags and not picture_count and not nested_table_count:
            content_type = "empty"
        elif picture_count and not has_text and not control_tags and not nested_table_count:
            content_type = "image_only"
        elif picture_count and has_text and not control_tags and not nested_table_count:
            content_type = "image_with_text"
        elif nested_table_count and not has_text and not control_tags:
            content_type = "table_only"
        elif nested_table_count and has_text and not control_tags:
            content_type = "table_with_text"
        elif control_tags and has_text and not picture_count and not nested_table_count:
            content_type = "control_with_text"
        elif control_tags and not has_text and not picture_count and not nested_table_count:
            content_type = "control_only"
        else:
            content_type = "mixed"

        rebuild_safe_text_only = content_type == "text"
        return {
            "content_type": content_type,
            "has_text": has_text,
            "control_tags": control_tags,
            "picture_count": picture_count,
            "nested_table_count": nested_table_count,
            "rebuild_safe_text_only": rebuild_safe_text_only
        }

    def _build_paragraph_summary(self, paragraph_assets: list[dict[str, Any]]) -> dict[str, Any]:
        by_context: dict[str, int] = {}
        by_content: dict[str, int] = {}
        root_flow_count = 0
        rebuild_safe_count = 0

        for paragraph in paragraph_assets:
            classification = paragraph.get("classification", {})
            context_type = classification.get("context_type", "unknown")
            content_type = classification.get("content_type", "unknown")
            by_context[context_type] = by_context.get(context_type, 0) + 1
            by_content[content_type] = by_content.get(content_type, 0) + 1
            if classification.get("is_root_flow"):
                root_flow_count += 1
            if classification.get("rebuild_safe_text_only"):
                rebuild_safe_count += 1

        return {
            "schema_version": SCHEMA_VERSION,
            "total_paragraphs": len(paragraph_assets),
            "root_flow_paragraphs": root_flow_count,
            "nested_control_paragraphs": len(paragraph_assets) - root_flow_count,
            "rebuild_safe_text_only": rebuild_safe_count,
            "by_context": by_context,
            "by_content": by_content
        }

    def _build_paragraph_page_map(self, paragraph_assets: list[dict[str, Any]]) -> list[dict[str, Any]]:
        return [
            {
                "asset_id": paragraph.get("asset_id"),
                "global_paragraph_index": paragraph.get("global_paragraph_index"),
                "root_flow_paragraph_index": paragraph.get("root_flow_paragraph_index"),
                "page_no": paragraph.get("page_no"),
                "page_source": paragraph.get("page_source"),
                "context_type": paragraph.get("classification", {}).get("context_type"),
                "content_type": paragraph.get("classification", {}).get("content_type")
            }
            for paragraph in paragraph_assets
        ]

    def _apply_page_numbers(
        self,
        paragraph_assets: list[dict[str, Any]],
        table_assets: list[dict[str, Any]],
        image_occurrences: list[dict[str, Any]],
        xml_page_summary: dict[str, Any],
        pyhwpx_summary: dict[str, Any],
        notes: list[str]
    ) -> dict[str, Any]:
        paragraph_by_id = {paragraph["asset_id"]: paragraph for paragraph in paragraph_assets}
        root_flow_count = sum(1 for paragraph in paragraph_assets if paragraph.get("classification", {}).get("is_root_flow"))
        notes.clear()

        use_pyhwpx_exact = (
            pyhwpx_summary.get("available")
            and not pyhwpx_summary.get("error")
            and pyhwpx_summary.get("paragraph_count") == root_flow_count
            and pyhwpx_summary.get("mapped_root_paragraphs") == root_flow_count
        )

        inherited_page_count = 0
        if use_pyhwpx_exact:
            notes.append("루트 본문 문단은 pyhwpx 실측 페이지를 사용하고, 글상자/각주 하위 문단은 상위 본문 문단의 페이지를 상속했습니다.")
            root_page_map = pyhwpx_summary.get("root_paragraph_to_page", {})
            for paragraph in paragraph_assets:
                classification = paragraph.get("classification", {})
                if classification.get("is_root_flow"):
                    root_index = paragraph.get("root_flow_paragraph_index")
                    page_no = root_page_map.get(root_index)
                    paragraph["page_no"] = page_no
                    paragraph["page_source"] = "pyhwpx_root_paragraph" if page_no is not None else None
                    continue

                host_id = classification.get("host_body_paragraph_asset_id")
                host_paragraph = paragraph_by_id.get(host_id)
                if host_paragraph and host_paragraph.get("page_no") is not None:
                    paragraph["page_no"] = host_paragraph["page_no"]
                    paragraph["page_source"] = "parent_body_paragraph"
                    inherited_page_count += 1
        else:
            if pyhwpx_summary.get("available") and pyhwpx_summary.get("error"):
                notes.append(f"pyhwpx 본문 페이지 맵 생성 실패: {pyhwpx_summary['error']}")
            elif pyhwpx_summary.get("available"):
                notes.append(
                    "pyhwpx 본문 문단 수와 파서 루트 본문 문단 수가 달라 exact page 매핑을 적용하지 못했습니다. "
                    "page_no는 XML 추정값을 유지하고, 하위 컨트롤 문단은 상위 본문 문단 page를 우선 상속합니다."
                )

            for paragraph in paragraph_assets:
                classification = paragraph.get("classification", {})
                if classification.get("is_root_flow"):
                    continue
                host_id = classification.get("host_body_paragraph_asset_id")
                host_paragraph = paragraph_by_id.get(host_id)
                if host_paragraph and host_paragraph.get("page_no") is not None:
                    paragraph["page_no"] = host_paragraph["page_no"]
                    paragraph["page_source"] = "parent_body_paragraph_fallback"
                    inherited_page_count += 1

        for table in table_assets:
            parent_id = table.get("source_ref", {}).get("parent_asset_id")
            parent_paragraph = paragraph_by_id.get(parent_id)
            if parent_paragraph and parent_paragraph.get("page_no") is not None:
                table["page_no"] = parent_paragraph["page_no"]
                table["page_source"] = parent_paragraph.get("page_source")
                for cell in table.get("cells", []):
                    cell["page_no"] = table["page_no"]
                    cell["page_source"] = table.get("page_source")

        for occurrence in image_occurrences:
            parent_id = occurrence.get("source_ref", {}).get("parent_asset_id")
            parent_paragraph = paragraph_by_id.get(parent_id)
            if parent_paragraph and parent_paragraph.get("page_no") is not None:
                occurrence["page_no"] = parent_paragraph["page_no"]
                occurrence["page_source"] = parent_paragraph.get("page_source")

        return {
            "schema_version": SCHEMA_VERSION,
            "assignment": {
                "method": "pyhwpx_root_paragraph_exact" if use_pyhwpx_exact else "xml_pagebreak_estimate",
                "paragraphs_with_page": sum(1 for paragraph in paragraph_assets if paragraph.get("page_no") is not None),
                "paragraphs_without_page": sum(1 for paragraph in paragraph_assets if paragraph.get("page_no") is None),
                "root_flow_paragraphs": root_flow_count,
                "nested_paragraphs_inherited": inherited_page_count
            },
            "xml_page_map": {
                "method": xml_page_summary["method"],
                "estimated_total_pages": xml_page_summary["estimated_total_pages"],
                "mapped_paragraphs": xml_page_summary["mapped_paragraphs"]
            },
            "pyhwpx": {
                "available": pyhwpx_summary.get("available"),
                "page_count": pyhwpx_summary.get("page_count"),
                "paragraph_count": pyhwpx_summary.get("paragraph_count"),
                "mapped_root_paragraphs": pyhwpx_summary.get("mapped_root_paragraphs"),
                "used_for_assignment": use_pyhwpx_exact,
                "error": pyhwpx_summary.get("error")
            },
            "notes": notes
        }

    def _describe_paragraph_context(self, paragraph) -> dict[str, Any]:
        parent = paragraph.getparent()
        is_root_flow = parent is not None and local_name(parent.tag) == "sec"

        host_body_paragraph = paragraph if is_root_flow else None
        context_path: list[str] = []
        context_type = "body" if is_root_flow else "control_sublist"

        current = paragraph.getparent()
        while current is not None:
            name = local_name(current.tag)
            context_path.append(name)
            if current.tag == tag("hp", "p"):
                grandparent = current.getparent()
                if grandparent is not None and local_name(grandparent.tag) == "sec":
                    host_body_paragraph = current
            if name == "footNote":
                context_type = "footnote"
            elif name == "endNote":
                context_type = "endnote"
            elif name in {"container", "drawText"} and context_type == "control_sublist":
                context_type = "container"
            current = current.getparent()

        return {
            "is_root_flow": is_root_flow,
            "host_body_paragraph_element": host_body_paragraph,
            "context_type": context_type,
            "context_path": list(reversed(context_path))
        }

    def _build_paragraph_classification(
        self,
        paragraph,
        paragraph_text: str,
        control_tags: list[str],
        table_count: int,
        image_count: int,
        host_body_paragraph_id: str | None,
        root_flow_index: int | None,
        host_root_flow_index: int | None
    ) -> dict[str, Any]:
        context = self._describe_paragraph_context(paragraph)
        has_text = bool(paragraph_text.strip())
        control_only_tags = [name for name in control_tags if name not in {"tbl", "pic"}]

        if has_text and not table_count and not image_count and not control_only_tags:
            content_type = "text"
        elif not has_text and not table_count and not image_count and not control_only_tags:
            content_type = "empty"
        elif table_count and not has_text and not image_count and not control_only_tags:
            content_type = "table_only"
        elif table_count and has_text and not image_count and not control_only_tags:
            content_type = "table_with_text"
        elif image_count and not has_text and not table_count and not control_only_tags:
            content_type = "image_only"
        elif image_count and has_text and not table_count and not control_only_tags:
            content_type = "image_with_text"
        elif control_only_tags and not has_text and not table_count and not image_count:
            content_type = "control_only"
        elif control_only_tags and has_text and not table_count and not image_count:
            content_type = "control_with_text"
        else:
            content_type = "mixed"

        rebuild_safe_text_only = (
            context["context_type"] == "body"
            and bool(root_flow_index)
            and content_type == "text"
        )

        return {
            "context_type": context["context_type"],
            "context_path": context["context_path"],
            "is_root_flow": context["is_root_flow"],
            "root_flow_paragraph_index": root_flow_index,
            "host_body_paragraph_asset_id": host_body_paragraph_id,
            "host_root_flow_paragraph_index": host_root_flow_index,
            "content_type": content_type,
            "has_text": has_text,
            "table_count": table_count,
            "image_count": image_count,
            "control_tag_count": len(control_only_tags),
            "rebuild_safe_text_only": rebuild_safe_text_only
        }

    def _extract_run_text(self, run) -> str:
        texts = []
        for child in run.iterchildren():
            if local_name(child.tag) != "t":
                continue
            texts.append("".join(child.itertext()))
        return compact_text("".join(texts))

    def _extract_paragraph_text(self, paragraph) -> str:
        texts = []
        for run in paragraph.findall(".//hp:run", NS):
            if not self._is_owned_by_paragraph(run, paragraph):
                continue
            if self._has_ancestor(run, tag("hp", "tbl"), paragraph):
                continue
            run_text = self._extract_run_text(run)
            if run_text:
                texts.append(run_text)
        return compact_text(" ".join(texts))

    def _extract_table_cell_text(self, cell) -> str:
        texts = []
        for text_node in cell.iter(tag("hp", "t")):
            if text_node.text:
                texts.append(text_node.text)
        return compact_text(" ".join(texts))

    def _extract_table_cell_control_tags(self, cell) -> list[str]:
        tags_found: set[str] = set()
        for run in cell.iter(tag("hp", "run")):
            for child in run.iterchildren():
                child_name = local_name(child.tag)
                if child_name == "t":
                    continue
                tags_found.add(child_name)
        return sorted(tags_found)

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

    def _has_ancestor(self, element, ancestor_tag: str, stop_element) -> bool:
        parent = element.getparent()
        while parent is not None and parent is not stop_element:
            if parent.tag == ancestor_tag:
                return True
            parent = parent.getparent()
        return False

    def _is_owned_by_paragraph(self, element, paragraph) -> bool:
        parent = element.getparent()
        while parent is not None and parent is not paragraph:
            if parent.tag == tag("hp", "p"):
                return False
            parent = parent.getparent()
        return parent is paragraph
