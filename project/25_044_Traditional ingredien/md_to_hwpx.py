# -*- coding: utf-8 -*-
"""
마크다운 → HWPX(한글) 범용 변환기
==================================
- pyhwpx(COM 자동화) 기반
- 모듈화: MarkdownParser + HwpxWriter
- CLI 지원: python md_to_hwpx.py <input.md>
- 출력: 입력 파일 하위 hwpx_output/ 폴더에 타임스탬프 파일명으로 저장
"""

import os
import re
import sys
from datetime import datetime
from typing import List, Tuple, Optional, Dict, Any


# ─────────────────────────────────────────────
#  1. 마크다운 요소 데이터 클래스
# ─────────────────────────────────────────────
class MdElement:
    """마크다운 파싱 결과를 담는 기본 클래스."""
    pass


class MdHeading(MdElement):
    def __init__(self, level: int, text: str):
        self.level = level  # 1~6
        self.text = text


class MdParagraph(MdElement):
    def __init__(self, text: str):
        self.text = text


class MdTable(MdElement):
    def __init__(self, headers: List[str], rows: List[List[str]], alignments: List[str] = None):
        self.headers = headers
        self.rows = rows
        self.alignments = alignments or []


class MdBlockquote(MdElement):
    def __init__(self, text: str):
        self.text = text


class MdHorizontalRule(MdElement):
    pass


# ─────────────────────────────────────────────
#  2. MarkdownParser
# ─────────────────────────────────────────────
class MarkdownParser:
    """마크다운 텍스트를 MdElement 리스트로 파싱한다."""

    def parse(self, filepath: str) -> List[MdElement]:
        """마크다운 파일을 읽어 요소 리스트로 변환."""
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
        return self._parse_content(content)

    def _parse_content(self, content: str) -> List[MdElement]:
        lines = content.split("\n")
        elements: List[MdElement] = []
        i = 0

        while i < len(lines):
            line = lines[i]
            stripped = line.strip()

            # 빈 줄 건너뛰기
            if not stripped:
                i += 1
                continue

            # 수평선 (---, ***, ___)
            if re.match(r"^[-*_]{3,}\s*$", stripped):
                elements.append(MdHorizontalRule())
                i += 1
                continue

            # 제목 (#, ##, ###, ...)
            heading_match = re.match(r"^(#{1,6})\s+(.+)$", stripped)
            if heading_match:
                level = len(heading_match.group(1))
                text = heading_match.group(2).strip()
                elements.append(MdHeading(level, text))
                i += 1
                continue

            # 표 (| ... | ... |)
            if stripped.startswith("|") and "|" in stripped[1:]:
                table, i = self._parse_table(lines, i)
                if table:
                    elements.append(table)
                continue

            # 인용문 (>)
            if stripped.startswith(">"):
                blockquote_lines = []
                while i < len(lines) and lines[i].strip().startswith(">"):
                    bq_text = re.sub(r"^>\s*", "", lines[i].strip())
                    # [!NOTE], [!TIP] 등 GitHub 알림 제거
                    bq_text = re.sub(r"^\[!(NOTE|TIP|IMPORTANT|WARNING|CAUTION)\]\s*", "", bq_text)
                    if bq_text:
                        blockquote_lines.append(bq_text)
                    i += 1
                if blockquote_lines:
                    elements.append(MdBlockquote(" ".join(blockquote_lines)))
                continue

            # 일반 문단
            para_lines = []
            while i < len(lines):
                cur = lines[i].strip()
                if not cur or cur.startswith("#") or cur.startswith("|") or cur.startswith(">") or re.match(
                        r"^[-*_]{3,}\s*$", cur):
                    break
                para_lines.append(cur)
                i += 1
            if para_lines:
                elements.append(MdParagraph(" ".join(para_lines)))

        return elements

    def _parse_table(self, lines: List[str], start: int) -> Tuple[Optional[MdTable], int]:
        """표를 파싱한다. (헤더, 구분선, 데이터 행)"""
        i = start

        # 헤더 행
        header_line = lines[i].strip()
        headers = self._parse_table_row(header_line)
        i += 1

        # 구분선 행 (|---|---|)
        if i >= len(lines):
            return None, i
        sep_line = lines[i].strip()
        if not re.match(r"^\|[\s:|-]+\|$", sep_line):
            # 구분선이 없으면 표가 아니므로 문단으로 처리
            return None, start + 1

        # 정렬 정보
        alignments = self._parse_alignments(sep_line)
        i += 1

        # 데이터 행
        rows = []
        while i < len(lines):
            row_line = lines[i].strip()
            if not row_line.startswith("|"):
                break
            row = self._parse_table_row(row_line)
            rows.append(row)
            i += 1

        return MdTable(headers, rows, alignments), i

    @staticmethod
    def _parse_table_row(line: str) -> List[str]:
        """표의 한 행을 셀 리스트로 변환."""
        # 양쪽 | 제거 후 분리
        line = line.strip()
        if line.startswith("|"):
            line = line[1:]
        if line.endswith("|"):
            line = line[:-1]
        cells = [cell.strip() for cell in line.split("|")]
        # 마크다운 서식 제거 (**bold**, *italic*)
        cleaned = []
        for cell in cells:
            cell = re.sub(r"\*\*(.+?)\*\*", r"\1", cell)
            cell = re.sub(r"\*(.+?)\*", r"\1", cell)
            cleaned.append(cell)
        return cleaned

    @staticmethod
    def _parse_alignments(sep_line: str) -> List[str]:
        """구분선에서 정렬 정보 추출."""
        sep_line = sep_line.strip().strip("|")
        parts = sep_line.split("|")
        alignments = []
        for part in parts:
            part = part.strip()
            if part.startswith(":") and part.endswith(":"):
                alignments.append("center")
            elif part.endswith(":"):
                alignments.append("right")
            else:
                alignments.append("left")
        return alignments


# ─────────────────────────────────────────────
#  3. HwpxWriter
# ─────────────────────────────────────────────
class HwpxWriter:
    """
    MdElement 리스트를 받아 HWPX 파일로 생성한다.
    pyhwpx(COM 자동화)를 사용하므로 한글이 설치되어 있어야 한다.
    """

    # 제목 레벨별 글꼴 크기 (pt)
    HEADING_SIZES = {1: 18, 2: 14, 3: 12, 4: 11, 5: 10.5, 6: 10}
    BODY_SIZE = 10
    BLOCKQUOTE_SIZE = 9.5

    def __init__(self, visible: bool = False):
        """
        Args:
            visible: 한글 앱을 화면에 표시할지 여부 (False: 백그라운드)
        """
        self.visible = visible
        self.hwp = None

    def _init_document(self):
        """한글 문서를 초기화한다."""
        from pyhwpx import Hwp
        self.hwp = Hwp(visible=self.visible)

    def write(self, elements: List[MdElement], output_path: str) -> str:
        """
        요소 리스트를 HWPX 파일로 작성한다.

        Args:
            elements: MdElement 리스트
            output_path: 저장할 파일 경로 (.hwpx)

        Returns:
            저장된 파일의 절대 경로
        """
        try:
            self._init_document()

            for idx, element in enumerate(elements):
                if isinstance(element, MdHeading):
                    self._write_heading(element)
                elif isinstance(element, MdTable):
                    self._write_table(element)
                elif isinstance(element, MdBlockquote):
                    self._write_blockquote(element)
                elif isinstance(element, MdHorizontalRule):
                    self._write_horizontal_rule()
                elif isinstance(element, MdParagraph):
                    self._write_paragraph(element)

                # 요소 사이 줄바꿈 (마지막 요소 제외)
                if idx < len(elements) - 1 and not isinstance(element, MdHorizontalRule):
                    self.hwp.BreakPara()

            # 저장
            return self._save(output_path)
        finally:
            if self.hwp:
                try:
                    self.hwp.hwp.Clear(isDirty=False)
                    self.hwp.hwp.Quit()
                except:
                    pass

    def _write_heading(self, heading: MdHeading):
        """제목을 삽입한다."""
        size = self.HEADING_SIZES.get(heading.level, self.BODY_SIZE)
        self.hwp.set_font(FaceName="맑은 고딕", Height=size, Bold=True)
        if heading.level <= 2:
            self.hwp.ParagraphShapeAlignCenter()
        self.hwp.insert_text(heading.text)
        # 폰트 복원
        self.hwp.BreakPara()
        self.hwp.set_font(FaceName="맑은 고딕", Height=self.BODY_SIZE, Bold=False)
        if heading.level <= 2:
            self.hwp.ParagraphShapeAlignLeft()

    def _write_table(self, table: MdTable):
        """표를 삽입한다."""
        num_rows = len(table.rows) + 1  # 헤더 포함
        num_cols = len(table.headers)

        if num_rows == 0 or num_cols == 0:
            return

        # 표 생성
        self.hwp.create_table(rows=num_rows, cols=num_cols, treat_as_char=True, header=True)

        # 헤더 행 입력
        for col_idx, header_text in enumerate(table.headers):
            self.hwp.set_font(FaceName="맑은 고딕", Height=self.BODY_SIZE, Bold=True)
            self.hwp.insert_text(header_text)

            # 정렬 적용
            if col_idx < len(table.alignments):
                self._apply_alignment(table.alignments[col_idx])

            if col_idx < num_cols - 1:
                self.hwp.TableRightCellAppend()

        # 데이터 행 입력
        for row in table.rows:
            self.hwp.TableRightCellAppend()
            for col_idx, cell_text in enumerate(row):
                self.hwp.set_font(FaceName="맑은 고딕", Height=self.BODY_SIZE, Bold=False)
                self.hwp.insert_text(cell_text)

                # 정렬 적용
                if col_idx < len(table.alignments):
                    self._apply_alignment(table.alignments[col_idx])

                if col_idx < len(row) - 1:
                    self.hwp.TableRightCell()

        # 표 밖으로 이동
        self.hwp.Cancel()
        self.hwp.hwp.HAction.Run("MoveDown")
        self.hwp.hwp.HAction.Run("MoveDown")

    def _apply_alignment(self, align: str):
        """셀 정렬을 적용한다."""
        if align == "center":
            self.hwp.ParagraphShapeAlignCenter()
        elif align == "right":
            self.hwp.ParagraphShapeAlignRight()
        else:
            self.hwp.ParagraphShapeAlignLeft()

    def _write_blockquote(self, bq: MdBlockquote):
        """인용문을 삽입한다."""
        self.hwp.set_font(FaceName="맑은 고딕", Height=self.BLOCKQUOTE_SIZE, Italic=True,
                          TextColor=0x555555)
        self.hwp.ParagraphShapeIndentPositive()
        self.hwp.insert_text(bq.text)
        self.hwp.BreakPara()
        self.hwp.ParagraphShapeIndentNegative()
        self.hwp.set_font(FaceName="맑은 고딕", Height=self.BODY_SIZE, Italic=False,
                          TextColor=0x000000)

    def _write_horizontal_rule(self):
        """수평선을 삽입한다 (빈 줄로 대체)."""
        self.hwp.BreakPara()

    def _write_paragraph(self, para: MdParagraph):
        """일반 문단을 삽입한다."""
        self.hwp.set_font(FaceName="맑은 고딕", Height=self.BODY_SIZE, Bold=False)
        self.hwp.insert_text(para.text)

    def _save(self, output_path: str) -> str:
        """문서를 HWPX 형식으로 저장한다."""
        output_path = os.path.abspath(output_path)
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        self.hwp.save_as(output_path, format="HWPX")
        return output_path


# ─────────────────────────────────────────────
#  4. convert() — 원스톱 변환 함수
# ─────────────────────────────────────────────
def generate_output_path(input_path: str) -> str:
    """
    입력 파일 경로로부터 출력 경로를 생성한다.
    형식: <입력파일 디렉토리>/hwpx_output/<파일명>_YYYYMMDDHHmm.hwpx
    """
    input_dir = os.path.dirname(os.path.abspath(input_path))
    basename = os.path.splitext(os.path.basename(input_path))[0]
    timestamp = datetime.now().strftime("%Y%m%d%H%M")
    output_dir = os.path.join(input_dir, "hwpx_output")
    output_filename = f"{basename}_{timestamp}.hwpx"
    return os.path.join(output_dir, output_filename)


def convert(input_path: str, output_path: str = None, visible: bool = False) -> str:
    """
    마크다운 파일을 HWPX 파일로 변환한다.

    Args:
        input_path: 입력 마크다운 파일 경로
        output_path: 출력 HWPX 파일 경로 (None이면 자동 생성)
        visible: 한글 앱을 화면에 표시할지 여부

    Returns:
        저장된 HWPX 파일의 절대 경로
    """
    if not os.path.isfile(input_path):
        raise FileNotFoundError(f"입력 파일을 찾을 수 없습니다: {input_path}")

    if output_path is None:
        output_path = generate_output_path(input_path)

    print(f"[1/3] 마크다운 파싱 중: {input_path}")
    parser = MarkdownParser()
    elements = parser.parse(input_path)
    print(f"      → {len(elements)}개 요소 파싱 완료")

    print(f"[2/3] HWPX 문서 생성 중... (한글 앱 실행)")
    writer = HwpxWriter(visible=visible)
    saved_path = writer.write(elements, output_path)

    print(f"[3/3] 저장 완료: {saved_path}")
    return saved_path


# ─────────────────────────────────────────────
#  5. CLI 인터페이스
# ─────────────────────────────────────────────
def main():
    """CLI 진입점."""
    import argparse

    parser = argparse.ArgumentParser(
        description="마크다운 → HWPX(한글) 변환기",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
사용 예:
  python md_to_hwpx.py 건의사항_종합표.md
  python md_to_hwpx.py input.md --output result.hwpx
  python md_to_hwpx.py input.md --visible
        """,
    )
    parser.add_argument("input", help="변환할 마크다운 파일 경로")
    parser.add_argument("-o", "--output", help="출력 HWPX 파일 경로 (기본: 자동 생성)", default=None)
    parser.add_argument("-v", "--visible", help="한글 앱을 화면에 표시", action="store_true")

    args = parser.parse_args()

    try:
        result = convert(args.input, args.output, args.visible)
        print(f"\n✅ 변환 완료: {result}")
    except FileNotFoundError as e:
        print(f"\n❌ 오류: {e}", file=sys.stderr)
        sys.exit(1)
    except ImportError:
        print(
            "\n❌ 오류: pyhwpx가 설치되어 있지 않습니다.\n"
            "   pip install pyhwpx 로 설치해 주세요.\n"
            "   (한글이 설치된 Windows 환경 필요)",
            file=sys.stderr,
        )
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 변환 중 오류 발생: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
