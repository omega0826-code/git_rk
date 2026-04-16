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


def _find_max_root_paragraph_index(hwp, upper_bound: int = 100000) -> int:
    low = 0
    high = 1

    while high <= upper_bound and hwp.set_pos(0, high, 0):
        low = high
        high *= 2

    while low + 1 < high:
        mid = (low + high) // 2
        if hwp.set_pos(0, mid, 0):
            low = mid
        else:
            high = mid

    return low


def try_build_pyhwpx_root_page_map(hwpx_path: Path) -> dict[str, Any]:
    try:
        import pyhwpx
    except ImportError:
        return {
            "available": False,
            "page_count": None,
            "paragraph_count": None,
            "mapped_root_paragraphs": 0,
            "root_paragraph_to_page": {},
            "root_paragraph_to_printpage": {},
            "error": "pyhwpx is not installed"
        }

    hwp = None
    try:
        hwp = pyhwpx.Hwp(visible=False)
        hwp.open(str(hwpx_path.resolve()))

        max_paragraph_index = _find_max_root_paragraph_index(hwp)
        paragraph_count = max_paragraph_index + 1 if max_paragraph_index >= 0 else 0

        page_map: dict[int, int] = {}
        print_page_map: dict[int, int] = {}
        for para_index in range(paragraph_count):
            if not hwp.set_pos(0, para_index, 0):
                break
            page_map[para_index + 1] = int(hwp.current_page)
            print_page_map[para_index + 1] = int(hwp.current_printpage)

        return {
            "available": True,
            "page_count": int(hwp.PageCount),
            "paragraph_count": paragraph_count,
            "mapped_root_paragraphs": len(page_map),
            "root_paragraph_to_page": page_map,
            "root_paragraph_to_printpage": print_page_map,
            "error": None
        }
    except Exception as exc:
        return {
            "available": True,
            "page_count": None,
            "paragraph_count": None,
            "mapped_root_paragraphs": 0,
            "root_paragraph_to_page": {},
            "root_paragraph_to_printpage": {},
            "error": str(exc)
        }
    finally:
        if hwp is not None:
            try:
                hwp.quit()
            except Exception:
                pass


def try_get_pyhwpx_page_count(hwpx_path: Path) -> dict[str, Any]:
    summary = try_build_pyhwpx_root_page_map(hwpx_path)
    return {
        "available": summary["available"],
        "page_count": summary["page_count"],
        "error": summary["error"]
    }
