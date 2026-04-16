from __future__ import annotations

from pathlib import Path
from typing import Any

from .namespaces import tag


def _is_in_table(element) -> bool:
    parent = element.getparent()
    while parent is not None:
        if parent.tag == tag("hp", "tbl"):
            return True
        parent = parent.getparent()
    return False


def _is_in_header_footer(element) -> bool:
    parent = element.getparent()
    while parent is not None:
        if parent.tag in (tag("hp", "header"), tag("hp", "footer")):
            return True
        parent = parent.getparent()
    return False


def build_xml_page_map(section_roots: list[tuple[str, Any]]) -> dict[str, Any]:
    page_map: dict[int, int] = {}
    current_page = 1
    global_paragraph_index = 0

    for _, root in section_roots:
        for paragraph in root.iter(tag("hp", "p")):
            if _is_in_table(paragraph) or _is_in_header_footer(paragraph):
                continue
            global_paragraph_index += 1
            if global_paragraph_index > 1 and paragraph.get("pageBreak", "0") == "1":
                current_page += 1
            page_map[global_paragraph_index] = current_page

    return {
        "method": "xml_pagebreak_estimate",
        "paragraph_to_page": page_map,
        "estimated_total_pages": current_page if page_map else 0,
        "mapped_paragraphs": global_paragraph_index
    }


def try_get_pyhwpx_page_count(hwpx_path: Path) -> dict[str, Any]:
    try:
        import pyhwpx
    except ImportError:
        return {"available": False, "page_count": None, "error": "pyhwpx is not installed"}

    hwp = None
    try:
        hwp = pyhwpx.Hwp(visible=False)
        hwp.open(str(hwpx_path.resolve()))
        return {"available": True, "page_count": int(hwp.PageCount), "error": None}
    except Exception as exc:
        return {"available": True, "page_count": None, "error": str(exc)}
    finally:
        if hwp is not None:
            try:
                hwp.quit()
            except Exception:
                pass
