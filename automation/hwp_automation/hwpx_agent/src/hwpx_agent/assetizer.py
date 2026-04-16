from __future__ import annotations

import shutil
import zipfile
from datetime import datetime
from pathlib import Path
from typing import Any

from lxml import etree

from .namespaces import NS, local_name, tag
from .page_map import build_xml_page_map, try_get_pyhwpx_page_count
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
            pyhwpx_summary = try_get_pyhwpx_page_count(self.hwpx_path)

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

            asset_index = {
                "schema_version": SCHEMA_VERSION,
                "files": {
                    "document": "assets/document.json",
                    "paragraphs": "assets/blocks/paragraphs.json",
                    "tables": "assets/tables/tables.json",
                    "image_binaries": "assets/images/binaries.json",
                    "image_occurrences": "assets/images/occurrences.json",
                    "sections": "assets/sections/sections.json",
                    "masterpages": "assets/masterpages/masterpages.json",
                    "page_summary": "assets/pages/page_summary.json"
                }
            }

            write_json(self.blocks_dir / "paragraphs.json", paragraph_assets)
            write_json(self.tables_dir / "tables.json", table_assets)
            write_json(self.images_dir / "binaries.json", image_binaries)
            write_json(self.images_dir / "occurrences.json", image_occurrences)
            write_json(self.sections_dir / "sections.json", section_assets)
            write_json(self.masterpages_dir / "masterpages.json", masterpage_assets)
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
                    "image_binaries": len(image_binaries),
                    "image_occurrences": len(image_occurrences),
                    "sections": len(section_assets),
                    "masterpages": len(masterpage_assets),
                    "char_styles": len(styles["char_styles"]),
                    "para_styles": len(styles["para_styles"]),
                    "named_styles": len(styles["named_styles"])
                },
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

        global_paragraph_index = 0
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

                paragraph_text = self._extract_paragraph_text(paragraph)
                if paragraph_text:
                    last_non_empty_text = paragraph_text

                paragraph_page_no = paragraph_page_map.get(global_paragraph_index)
                embedded_refs = []
                runs = []
                char_pr_ids = []
                control_tags = set()

                for run_index, run in enumerate(paragraph.findall(".//hp:run", NS), start=1):
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
                            "run_index": run_index,
                            "text": run_text,
                            "char_pr_id_ref": char_pr_id,
                            "child_tags": child_tags
                        }
                    )

                for image_position, picture in enumerate(paragraph.iter(tag("hp", "pic")), start=1):
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

                for table_position, table in enumerate(paragraph.iter(tag("hp", "tbl")), start=1):
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

                paragraph_assets.append(
                    {
                        "schema_version": SCHEMA_VERSION,
                        "asset_id": paragraph_id,
                        "asset_type": "paragraph",
                        "section_id": section_id,
                        "section_index": section_index,
                        "section_paragraph_index": section_paragraph_index,
                        "global_paragraph_index": global_paragraph_index,
                        "source_ref": {
                            "package_entry": entry_name,
                            "xml_path": f"{entry_name}#/body/p[{section_paragraph_index}]",
                            "parent_asset_id": None
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
                        "control_tags": sorted(control_tags)
                    }
                )

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
            cells.append(
                {
                    "cell_index": cell_index,
                    "row": int(addr.get("rowAddr", 0)) if addr is not None else 0,
                    "col": int(addr.get("colAddr", 0)) if addr is not None else 0,
                    "row_span": int(span.get("rowSpan", 1)) if span is not None else 1,
                    "col_span": int(span.get("colSpan", 1)) if span is not None else 1,
                    "text": self._extract_table_cell_text(cell)
                }
            )

        return {
            "schema_version": SCHEMA_VERSION,
            "asset_id": table_id,
            "asset_type": "table",
            "section_id": section_id,
            "section_index": section_index,
            "section_table_index": section_table_index,
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

    def _extract_run_text(self, run) -> str:
        texts = []
        for text_node in run.iter(tag("hp", "t")):
            if text_node.text:
                texts.append(text_node.text)
        return compact_text("".join(texts))

    def _extract_paragraph_text(self, paragraph) -> str:
        texts = []
        for run in paragraph.findall(".//hp:run", NS):
            if self._has_ancestor(run, tag("hp", "tbl"), paragraph):
                continue
            for text_node in run.iter(tag("hp", "t")):
                if text_node.text:
                    texts.append(text_node.text)
        return compact_text("".join(texts))

    def _extract_table_cell_text(self, cell) -> str:
        texts = []
        for text_node in cell.iter(tag("hp", "t")):
            if text_node.text:
                texts.append(text_node.text)
        return compact_text(" ".join(texts))

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
