# -*- coding: utf-8 -*-
"""
HWPX 범용 오타 검사 스크립트
============================
HWPX 파일을 파싱하고, 텍스트/표 검증을 수행하여 Markdown 리포트를 생성한다.

사용법:
    python run_typo_check.py <hwpx_파일_경로> [--output-dir DIR]

단계:
    Step 1: HWPX 파싱 (텍스트, 표, 제목, 이미지 추출)
    Step 2: 텍스트 오타 검사 (A단계)
    Step 3: 표 데이터 검증 (B단계)
    Step 4: Markdown 리포트 생성 (C단계)
"""

import os
import re
import sys
import csv
import json
import argparse
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple

# ── hwpx_parser를 임포트하기 위해 경로 추가 ──
SCRIPT_DIR = Path(__file__).parent
PARSER_DIR = SCRIPT_DIR.parent / "Typo checker" / "01_hwpx_parser"
if str(PARSER_DIR) not in sys.path:
    sys.path.insert(0, str(PARSER_DIR))

from hwpx_parser import parse_hwpx  # noqa: E402


# ══════════════════════════════════════════════
#  PageMapper — pyhwpx COM 자동화 기반 페이지 매핑
# ══════════════════════════════════════════════
class PageMapper:
    """pyhwpx를 사용하여 HWPX 문서의 문단별 페이지 번호를 추출한다."""

    def __init__(self, hwpx_path: str):
        self.hwpx_path = Path(hwpx_path)
        self.hwp = None
        self._page_map: Dict[int, int] = {}  # {문단인덱스: 페이지번호}
        self.total_pages = 0

    def extract_page_info(self) -> Dict[int, int]:
        """
        한글을 백그라운드로 열어 goto_page()로 각 페이지의 시작 문단 위치를 수집하고,
        이를 기반으로 문단(줄) → 페이지 매핑을 구축한다.
        Returns: {문단_인덱스(1-based): 페이지_번호}
        """
        try:
            import pyhwpx
        except ImportError:
            print("  [WARNING] pyhwpx가 설치되어 있지 않습니다. 페이지 매핑을 건너뜁니다.")
            return {}

        try:
            self.hwp = pyhwpx.Hwp(visible=False)
            self.hwp.open(str(self.hwpx_path.resolve()))

            # 전체 페이지 수 확인
            self.total_pages = self.hwp.PageCount
            print(f"  -> 전체 페이지 수: {self.total_pages}")
            sys.stdout.flush()

            # 각 페이지의 시작 문단 인덱스 수집 (역방향 매핑)
            # GetPos() returns (list_id, para_id, char_pos)
            # para_id는 0-based 문단 인덱스
            page_start_paras = []  # [(page_num, para_id_0based), ...]

            for page in range(1, self.total_pages + 1):
                try:
                    self.hwp.goto_page(page)
                    pos = self.hwp.GetPos()
                    page_start_paras.append((page, pos[1]))
                except Exception:
                    pass

            # 문단 인덱스(0-based) → 페이지 번호 매핑 구축
            # page_start_paras는 오름차순 정렬되어야 함
            page_start_paras.sort(key=lambda x: x[1])

            # 전체 문단 수 확인 (문서 끝으로 이동)
            self.hwp.MovePos(3)  # movePosEnd
            end_pos = self.hwp.GetPos()
            total_paras = end_pos[1] + 1  # 0-based → 총 개수

            # 범위 기반 매핑: 각 페이지의 시작~다음 페이지 시작 전까지
            for i in range(len(page_start_paras)):
                page_num, start_para = page_start_paras[i]
                if i + 1 < len(page_start_paras):
                    end_para = page_start_paras[i + 1][1]
                else:
                    end_para = total_paras

                for para_0 in range(start_para, end_para):
                    self._page_map[para_0 + 1] = page_num  # 1-based

            print(f"  -> 매핑된 문단: {len(self._page_map)}개 ({self.total_pages}페이지)")
            sys.stdout.flush()

        except Exception as e:
            print(f"  [WARNING] pyhwpx 페이지 매핑 실패: {e}")
            print(f"  XML pageBreak 방식으로 폴백합니다.")
            sys.stdout.flush()
            self._page_map = self._fallback_xml_page_map()
        finally:
            if self.hwp:
                try:
                    self.hwp.quit()
                except Exception:
                    pass
                self.hwp = None

        return self._page_map

    def _fallback_xml_page_map(self) -> Dict[int, int]:
        """pyhwpx 실패 시 XML pageBreak 기반 폴백"""
        import zipfile
        from lxml import etree

        NS_HP = 'http://www.hancom.co.kr/hwpml/2011/paragraph'
        tag_p = f'{{{NS_HP}}}p'
        tag_t = f'{{{NS_HP}}}t'
        tag_tbl = f'{{{NS_HP}}}tbl'

        page_map = {}
        current_page = 1
        para_idx = 0

        def is_in_table_or_header(elem):
            parent = elem.getparent()
            while parent is not None:
                t = parent.tag
                if t == tag_tbl or 'header' in t.lower() or 'footer' in t.lower():
                    return True
                parent = parent.getparent()
            return False

        with zipfile.ZipFile(str(self.hwpx_path), 'r') as z:
            import re as _re
            section_files = sorted(f for f in z.namelist()
                                   if _re.match(r'Contents/section\d+\.xml', f))
            for sec_file in section_files:
                root = etree.fromstring(z.read(sec_file))
                for p in root.iter(tag_p):
                    if is_in_table_or_header(p):
                        continue
                    if p.get('pageBreak', '0') == '1':
                        current_page += 1
                    texts = []
                    for t in p.iter(tag_t):
                        if t.text:
                            texts.append(t.text)
                    text = ''.join(texts).strip()
                    if text:
                        para_idx += 1
                        page_map[para_idx] = current_page

        return page_map

    def get_page_for_line(self, line_num: int) -> Optional[int]:
        """문단(줄) 번호로 페이지 번호를 반환한다."""
        if line_num in self._page_map:
            return self._page_map[line_num]
        # 가장 가까운 이전 줄의 페이지를 반환
        for i in range(line_num, 0, -1):
            if i in self._page_map:
                return self._page_map[i]
        return None

    def get_page_str(self, line_num: int) -> str:
        """페이지 번호를 문자열로 반환 (없으면 '?')"""
        page = self.get_page_for_line(line_num)
        return str(page) if page else '?'


# ══════════════════════════════════════════════
#  데이터클래스
# ══════════════════════════════════════════════
@dataclass
class Issue:
    """검사에서 발견된 하나의 이슈"""
    category: str       # 'text' | 'table' | 'cross'
    severity: str       # '오타' | '의심' | '정보'
    location: str       # 줄 번호 or 표 번호
    original: str       # 원문 발췌
    description: str    # 설명
    suggestion: str = ""  # 수정 제안
    page: str = ""       # 페이지 번호


# ══════════════════════════════════════════════
#  A단계: TextChecker — 범용 텍스트 오타 검사
# ══════════════════════════════════════════════
class TextChecker:
    """규칙 기반 텍스트 오타 검사 (범용)"""

    # ── 일반적인 한국어 오타 패턴 ──
    KNOWN_TYPOS = [
        # (정규식, 설명, 수정 제안)
        (r'([가-힣])\1{2,}', '동일 글자 3회 이상 연속 반복', '반복 제거'),
        (r'의\s*\d+검토', '편집 잔류 숫자', '불필요 숫자 제거'),
        (r'부가가가치', '"가" 중복 오타', '부가가치'),
        (r'등을을', '"을" 중복', '등을'),
        (r'에에', '"에" 중복', '에'),
        (r'을을', '"을" 중복', '을'),
        (r'를를', '"를" 중복', '를'),
        (r'이이', '"이" 중복', '이'),
        (r'은은', '"은" 중복', '은'),
        (r'는는', '"는" 중복', '는'),
        (r'로로\s', '"로" 중복', '로'),
        (r'하하다', '"하" 중복', '하다'),
        (r'된된', '"된" 중복', '된'),
    ]

    # ── 미완성 문장 패턴 ──
    INCOMPLETE_ENDINGS = [
        r'사업비는\s*$',
        r'분석용\s*사업비는\s*$',
        r'으로\s*$',
        r'에서\s*$',
        r'에는\s*$',
        r'하여\s*$',
    ]

    # ── 율/률 혼용 검사 ──
    YUL_PATTERN = re.compile(r'([가-힣])(율|률)')

    def __init__(self, lines: List[str]):
        self.lines = lines
        self.issues: List[Issue] = []

    def check_all(self) -> List[Issue]:
        self._check_known_typos()
        self._check_duplicate_chars()
        self._check_incomplete_sentences()
        self._check_yul_ryul()
        self._check_bracket_pairs()
        self._check_duplicate_phrases()
        self._check_number_inconsistency()
        return self.issues

    def _check_known_typos(self):
        for idx, line in enumerate(self.lines, 1):
            for pattern, desc, suggestion in self.KNOWN_TYPOS:
                for m in re.finditer(pattern, line):
                    context = line[max(0, m.start()-15):m.end()+15]
                    self.issues.append(Issue(
                        category='text', severity='오타',
                        location=f'줄 {idx}',
                        original=f'...{context}...',
                        description=desc,
                        suggestion=suggestion
                    ))

    def _check_duplicate_chars(self):
        """연속 어절 중복 검사 — '사업 사업', '분석 분석' 등"""
        for idx, line in enumerate(self.lines, 1):
            words = line.strip().split()
            for i in range(len(words) - 1):
                if len(words[i]) >= 2 and words[i] == words[i + 1]:
                    context = ' '.join(words[max(0, i-1):i+3])
                    self.issues.append(Issue(
                        category='text', severity='의심',
                        location=f'줄 {idx}',
                        original=f'...{context}...',
                        description=f'연속 어절 중복: "{words[i]}"',
                        suggestion=f'"{words[i]}" (1회만 사용)'
                    ))

    def _check_incomplete_sentences(self):
        for idx, line in enumerate(self.lines, 1):
            stripped = line.strip()
            if not stripped:
                continue
            for pattern in self.INCOMPLETE_ENDINGS:
                if re.search(pattern, stripped):
                    tail = stripped[-60:] if len(stripped) > 60 else stripped
                    self.issues.append(Issue(
                        category='text', severity='의심',
                        location=f'줄 {idx}',
                        original=tail,
                        description='문장이 미완결 상태로 끝남',
                        suggestion='뒤에 구체적 내용 보충 필요'
                    ))

    def _check_yul_ryul(self):
        """율/률 혼용 검사"""
        for idx, line in enumerate(self.lines, 1):
            for m in self.YUL_PATTERN.finditer(line):
                prev_char = m.group(1)
                suffix = m.group(2)
                code = ord(prev_char) - 0xAC00
                if code < 0 or code > 11171:
                    continue
                jongseong = code % 28
                if jongseong == 0 and suffix == '률':
                    context = line[max(0, m.start()-10):m.end()+10]
                    self.issues.append(Issue(
                        category='text', severity='의심',
                        location=f'줄 {idx}',
                        original=f'...{context}...',
                        description=f'"{prev_char}률" → 받침 없으므로 "{prev_char}율"이 표준',
                        suggestion=f'{prev_char}율'
                    ))
                elif jongseong != 0 and jongseong != 8 and suffix == '율':
                    context = line[max(0, m.start()-10):m.end()+10]
                    self.issues.append(Issue(
                        category='text', severity='의심',
                        location=f'줄 {idx}',
                        original=f'...{context}...',
                        description=f'"{prev_char}율" → 받침 있으므로 "{prev_char}률"이 표준',
                        suggestion=f'{prev_char}률'
                    ))

    def _check_bracket_pairs(self):
        """괄호 짝 검사 — 스택 기반 전체 문서 매칭"""
        pairs = [('(', ')'), ('「', '」'), ('[', ']'), ('{', '}'), ('【', '】')]
        # 표 데이터처럼 보이는 줄은 건너뛰기 (숫자·쉼표·공백 위주)
        def is_table_data_line(line: str) -> bool:
            stripped = line.strip()
            if not stripped:
                return True
            non_num = re.sub(r'[0-9,.%\s\-]+', '', stripped)
            return len(non_num) < len(stripped) * 0.3

        for open_b, close_b in pairs:
            stack = []  # [(줄번호, 문자위치)]
            unmatched_close = []  # [(줄번호,)]

            for idx, line in enumerate(self.lines, 1):
                if is_table_data_line(line):
                    continue
                for ch in line:
                    if ch == open_b:
                        stack.append(idx)
                    elif ch == close_b:
                        if stack:
                            stack.pop()
                        else:
                            unmatched_close.append(idx)

            # 매칭 안 된 여는 괄호
            reported_lines = set()
            for line_num in stack:
                if line_num not in reported_lines:
                    reported_lines.add(line_num)
                    context = self.lines[line_num - 1].strip()[:80]
                    self.issues.append(Issue(
                        category='text', severity='정보',
                        location=f'줄 {line_num}',
                        original=f'{open_b} 닫히지 않음',
                        description=f'괄호 {open_b}{close_b} 짝 불일치 — 닫는 괄호 없음',
                    ))
            # 매칭 안 된 닫는 괄호
            for line_num in unmatched_close:
                if line_num not in reported_lines:
                    reported_lines.add(line_num)
                    self.issues.append(Issue(
                        category='text', severity='정보',
                        location=f'줄 {line_num}',
                        original=f'{close_b} 여는 괄호 없음',
                        description=f'괄호 {open_b}{close_b} 짝 불일치 — 여는 괄호 없음',
                    ))

    def _check_duplicate_phrases(self):
        """문장 내 주요 구절 반복 검사"""
        for idx, line in enumerate(self.lines, 1):
            stripped = line.strip()
            if len(stripped) < 20:
                continue
            clauses = re.split(r'[,，]\s*', stripped)
            seen = {}
            for c in clauses:
                c_clean = c.strip()
                if len(c_clean) > 10:
                    if c_clean in seen:
                        self.issues.append(Issue(
                            category='text', severity='의심',
                            location=f'줄 {idx}',
                            original=f'...{c_clean}...',
                            description='동일 절 반복',
                            suggestion='중복 절 제거 검토'
                        ))
                    seen[c_clean] = True

    def _check_number_inconsistency(self):
        """문서 내 핵심 숫자 불일치 검사 — 고도화 버전

        필터링 기준:
        - 정수부 3자리 이상 (100 이상)만 대상
        - 연도 범위(1900~2099) 제외
        - 반올림 차이(±0.5) 자동 제외
        - 같은 줄 또는 인접 줄(±5) 내에서 반복되는 숫자만 비교
        - 출현 빈도 3회 이상
        """
        # 소수점 숫자 수집 (정수부 3자리 이상)
        number_map = {}  # {정수부: [(줄번호, 전체숫자문자열, float값)]}
        year_range = set(str(y) for y in range(1900, 2100))

        for idx, line in enumerate(self.lines, 1):
            for m in re.finditer(r'(\d{3,})\.\d', line):
                int_part = m.group(1)
                full = m.group(0)

                # 연도 제외
                if int_part in year_range:
                    continue

                try:
                    val = float(full)
                except ValueError:
                    continue

                if int_part not in number_map:
                    number_map[int_part] = []
                number_map[int_part].append((idx, full, val))

        for int_part, occurrences in number_map.items():
            if len(occurrences) < 3:
                continue

            unique_vals = set(v for _, v, _ in occurrences)
            if len(unique_vals) <= 1:
                continue

            # 반올림 차이 필터: 모든 값 간 최대 차이가 0.5 이하면 제외
            float_vals = [fv for _, _, fv in occurrences]
            max_diff = max(float_vals) - min(float_vals)
            if max_diff <= 0.5:
                continue

            # 인접 줄 클러스터 검사: 같은 줄이나 가까운 줄(±5)에서 다른 값이 있는지
            # → 멀리 떨어진 줄끼리의 차이는 서로 다른 통계일 가능성 높음
            has_nearby_conflict = False
            sorted_occ = sorted(occurrences, key=lambda x: x[0])
            for i in range(len(sorted_occ)):
                for j in range(i + 1, len(sorted_occ)):
                    line_i, val_str_i, fv_i = sorted_occ[i]
                    line_j, val_str_j, fv_j = sorted_occ[j]
                    if abs(line_i - line_j) <= 5 and val_str_i != val_str_j and abs(fv_i - fv_j) > 0.5:
                        has_nearby_conflict = True
                        break
                if has_nearby_conflict:
                    break

            if not has_nearby_conflict:
                continue

            sample = list(occurrences)[:5]
            locs = ', '.join(f'줄{i}:{v}' for i, v, _ in sample)
            self.issues.append(Issue(
                category='text', severity='의심',
                location='복수 위치',
                original=locs,
                description=f'숫자 값 불일치: {unique_vals}',
                suggestion='정확한 값 확인 필요 (인접 위치에서 다른 값 사용)'
            ))


# ══════════════════════════════════════════════
#  B단계: TableChecker — 범용 표 데이터 검증
# ══════════════════════════════════════════════
class TableChecker:
    """표 데이터 숫자 검증 (범용)"""

    def __init__(self, tables_dir: Path, text_lines: List[str]):
        self.tables_dir = tables_dir
        self.text_lines = text_lines
        self.issues: List[Issue] = []
        self.tables: Dict[int, List[List[str]]] = {}
        self._load_tables()

    def _load_tables(self):
        """CSV 파일들 로드"""
        if not self.tables_dir.exists():
            return
        for csv_file in sorted(self.tables_dir.glob('table_*.csv')):
            try:
                num = int(re.search(r'table_(\d+)', csv_file.name).group(1))
                with open(csv_file, 'r', encoding='utf-8-sig') as f:
                    reader = csv.reader(f)
                    self.tables[num] = [row for row in reader]
            except Exception:
                pass

    def check_all(self) -> List[Issue]:
        self._check_sum_consistency()
        self._check_empty_cells()
        return self.issues

    def _parse_number(self, s: str) -> Optional[float]:
        """문자열을 숫자로 변환 시도"""
        s = s.strip().replace(',', '').replace(' ', '')
        if not s or s == '-' or s == '':
            return None
        s = s.rstrip('%')
        try:
            return float(s)
        except ValueError:
            return None

    def _check_sum_consistency(self):
        """합계 행/열의 일치 여부 검사"""
        for tbl_num, rows in self.tables.items():
            if len(rows) < 3:
                continue

            # 합계 행 찾기
            sum_row_idx = None
            for i, row in enumerate(rows):
                if row and re.search(r'합\s*계|소\s*계|총\s*계|계\s*$', row[0]):
                    sum_row_idx = i
                    break

            if sum_row_idx is None:
                continue

            sum_row = rows[sum_row_idx]

            # 합계 행 아래의 데이터 행들 합산 검증
            for col_idx in range(1, len(sum_row)):
                expected = self._parse_number(sum_row[col_idx])
                if expected is None or expected == 0:
                    continue

                actual_sum = 0
                data_count = 0
                for i in range(sum_row_idx + 1, len(rows)):
                    if col_idx < len(rows[i]):
                        val = self._parse_number(rows[i][col_idx])
                        if val is not None:
                            actual_sum += val
                            data_count += 1

                if data_count >= 2 and abs(expected) > 0:
                    diff = abs(actual_sum - expected)
                    rel_diff = diff / abs(expected) * 100
                    if rel_diff > 1.0 and diff > 1:
                        self.issues.append(Issue(
                            category='table', severity='의심',
                            location=f'표 {tbl_num}, 열 {col_idx+1}',
                            original=f'합계행={expected:,.1f}, 실제합={actual_sum:,.1f}',
                            description=f'합계 불일치 (차이: {diff:,.1f}, {rel_diff:.1f}%)',
                            suggestion='합산 로직 또는 원본 데이터 재확인'
                        ))

    def _check_empty_cells(self):
        """표 내 비정상 빈 셀 탐지 (데이터 행에 빈 셀이 많은 경우)"""
        for tbl_num, rows in self.tables.items():
            if len(rows) < 2:
                continue
            col_count = max(len(r) for r in rows)
            for i, row in enumerate(rows[1:], 2):  # 헤더 제외
                empty_count = sum(1 for c in row if not c.strip())
                if col_count > 2 and empty_count > col_count * 0.6 and empty_count < col_count:
                    non_empty = [c.strip() for c in row if c.strip()]
                    preview = ', '.join(non_empty[:3])
                    self.issues.append(Issue(
                        category='table', severity='정보',
                        location=f'표 {tbl_num}, 행 {i}',
                        original=f'빈 셀 {empty_count}/{col_count}개, 내용: {preview}',
                        description='빈 셀 비율이 높은 행 (셀 병합 또는 데이터 누락 가능)',
                    ))


# ══════════════════════════════════════════════
#  C단계: ReportWriter — Markdown 리포트 생성
# ══════════════════════════════════════════════
class ReportWriter:
    """검사 결과를 Markdown 리포트로 출력"""

    def __init__(self, output_path: Path, hwpx_filename: str, parse_info: dict):
        self.output_path = output_path
        self.hwpx_filename = hwpx_filename
        self.parse_info = parse_info

    def write(self, text_issues: List[Issue], table_issues: List[Issue]) -> Path:
        all_issues = text_issues + table_issues
        errors = [i for i in all_issues if i.severity == '오타']
        warnings = [i for i in all_issues if i.severity == '의심']
        infos = [i for i in all_issues if i.severity == '정보']

        has_page = any(i.page for i in all_issues)
        lines = []

        # 제목
        lines.append(f'# 오타 검사 결과 리포트\n')
        lines.append(f'> **대상 파일**: `{self.hwpx_filename}`  ')
        lines.append(f'> **검사일**: {datetime.now().strftime("%Y-%m-%d %H:%M")}  ')
        total_pages_str = f', 총 {self.parse_info.get("total_pages", "?")}페이지' if self.parse_info.get('total_pages') else ''
        lines.append(f'> **파싱 결과**: 문단 {self.parse_info.get("paragraphs", 0)}개, '
                      f'표 {self.parse_info.get("tables", 0)}개, '
                      f'제목 {self.parse_info.get("headings", 0)}개, '
                      f'이미지 {self.parse_info.get("images", 0)}개'
                      f'{total_pages_str}\n')
        lines.append('---\n')

        # 요약
        lines.append('## 검사 결과 요약\n')
        lines.append('| 심각도 | 건수 |')
        lines.append('| --- | --- |')
        lines.append(f'| 🔴 오타 (확정) | **{len(errors)}건** |')
        lines.append(f'| 🟡 의심 (확인 필요) | **{len(warnings)}건** |')
        lines.append(f'| 🔵 정보 (참고) | **{len(infos)}건** |')
        lines.append(f'| **합계** | **{len(all_issues)}건** |')
        lines.append('')

        # 오타 (확정)
        if errors:
            lines.append('---\n')
            lines.append('## 🔴 오타 (확정)\n')
            if has_page:
                lines.append('| # | 페이지 | 위치 | 원문 | 설명 | 수정 제안 |')
                lines.append('| --- | --- | --- | --- | --- | --- |')
                for i, issue in enumerate(errors, 1):
                    orig = issue.original.replace('|', '\\|')
                    lines.append(f'| {i} | {issue.page} | {issue.location} | {orig} | {issue.description} | {issue.suggestion} |')
            else:
                lines.append('| # | 위치 | 원문 | 설명 | 수정 제안 |')
                lines.append('| --- | --- | --- | --- | --- |')
                for i, issue in enumerate(errors, 1):
                    orig = issue.original.replace('|', '\\|')
                    lines.append(f'| {i} | {issue.location} | {orig} | {issue.description} | {issue.suggestion} |')
            lines.append('')

        # 의심 (확인 필요)
        if warnings:
            lines.append('---\n')
            lines.append('## 🟡 의심 (확인 필요)\n')
            if has_page:
                lines.append('| # | 페이지 | 위치 | 원문 | 설명 | 수정 제안 |')
                lines.append('| --- | --- | --- | --- | --- | --- |')
                for i, issue in enumerate(warnings, 1):
                    orig = issue.original.replace('|', '\\|')
                    lines.append(f'| {i} | {issue.page} | {issue.location} | {orig} | {issue.description} | {issue.suggestion} |')
            else:
                lines.append('| # | 위치 | 원문 | 설명 | 수정 제안 |')
                lines.append('| --- | --- | --- | --- | --- |')
                for i, issue in enumerate(warnings, 1):
                    orig = issue.original.replace('|', '\\|')
                    lines.append(f'| {i} | {issue.location} | {orig} | {issue.description} | {issue.suggestion} |')
            lines.append('')

        # 정보 (참고)
        if infos:
            lines.append('---\n')
            lines.append('## 🔵 정보 (참고)\n')
            if has_page:
                lines.append('| # | 페이지 | 위치 | 내용 | 설명 |')
                lines.append('| --- | --- | --- | --- | --- |')
                for i, issue in enumerate(infos, 1):
                    orig = issue.original.replace('|', '\\|')
                    lines.append(f'| {i} | {issue.page} | {issue.location} | {orig} | {issue.description} |')
            else:
                lines.append('| # | 위치 | 내용 | 설명 |')
                lines.append('| --- | --- | --- | --- |')
                for i, issue in enumerate(infos, 1):
                    orig = issue.original.replace('|', '\\|')
                    lines.append(f'| {i} | {issue.location} | {orig} | {issue.description} |')
            lines.append('')

        # 검사 항목별 통계
        lines.append('---\n')
        lines.append('## 검사 항목별 통계\n')
        cats = {}
        for issue in all_issues:
            cats[issue.category] = cats.get(issue.category, 0) + 1
        cat_names = {'text': '텍스트 검사 (A단계)', 'table': '표 검증 (B단계)', 'cross': '교차 검증'}
        lines.append('| 검사 항목 | 건수 |')
        lines.append('| --- | --- |')
        for cat, name in cat_names.items():
            if cats.get(cat, 0) > 0:
                lines.append(f'| {name} | {cats[cat]}건 |')
        lines.append('')

        # 파싱 상세 정보
        lines.append('---\n')
        lines.append('## 파싱 상세 정보\n')
        lines.append(f'- 입력 파일: `{self.hwpx_filename}`')
        lines.append(f'- 문단 수: {self.parse_info.get("paragraphs", 0)}')
        lines.append(f'- 표 수: {self.parse_info.get("tables", 0)}')
        lines.append(f'- 제목 수: {self.parse_info.get("headings", 0)}')
        lines.append(f'- 이미지 수: {self.parse_info.get("images", 0)}')
        if self.parse_info.get('total_pages'):
            lines.append(f'- 전체 페이지: {self.parse_info["total_pages"]}페이지')
        lines.append(f'- 파싱 소요: {self.parse_info.get("elapsed", 0):.1f}초')
        if self.parse_info.get("errors"):
            lines.append(f'\n### 파싱 오류')
            for e in self.parse_info["errors"]:
                lines.append(f'- {e}')
        lines.append('')

        with open(self.output_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))

        return self.output_path


# ══════════════════════════════════════════════
#  CSV 출력
# ══════════════════════════════════════════════
def write_issues_csv(csv_path: Path, issues: List[Issue]):
    """오타 검사 상세 내용을 CSV로 저장한다."""
    with open(csv_path, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['번호', '페이지', '심각도', '카테고리', '위치', '원문', '설명', '수정제안'])
        for i, issue in enumerate(issues, 1):
            writer.writerow([
                i,
                issue.page,
                issue.severity,
                issue.category,
                issue.location,
                issue.original,
                issue.description,
                issue.suggestion,
            ])
    return csv_path


# ══════════════════════════════════════════════
#  메인
# ══════════════════════════════════════════════
def main():
    parser = argparse.ArgumentParser(
        description='HWPX 범용 오타 검사 스크립트',
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument('hwpx_file', help='HWPX 파일 경로')
    parser.add_argument('--output-dir', metavar='DIR',
                        help='산출물 저장 디렉토리 (기본: 같은 폴더/output)')
    parser.add_argument('--no-page-map', action='store_true',
                        help='페이지 매핑 건너뛰기')
    args = parser.parse_args()

    hwpx_path = Path(args.hwpx_file)
    if not hwpx_path.exists():
        print(f"[ERROR] 파일을 찾을 수 없습니다: {hwpx_path}")
        sys.exit(1)

    # 산출물 저장 디렉토리
    if args.output_dir:
        output_dir = Path(args.output_dir)
    else:
        output_dir = hwpx_path.parent / "output"
    output_dir.mkdir(parents=True, exist_ok=True)

    parsed_dir = output_dir / "parsed"

    print("=" * 60)
    print(f"HWPX 오타 검사 -- {hwpx_path.name}")
    print("=" * 60)

    # ── Step 1: HWPX 파싱 ──
    print("\n[Step 1] HWPX 파싱...")
    sys.stdout.flush()
    try:
        result = parse_hwpx(str(hwpx_path), output_base=str(parsed_dir))
        print(f"  -> 문단: {len(result['paragraphs'])}개")
        print(f"  -> 표:   {len(result['tables'])}개")
        print(f"  -> 제목: {len(result['headings'])}개")
        print(f"  -> 이미지: {len(result['image_refs'])}개")
        print(f"  -> 출력: {result['output_dir']}")
        sys.stdout.flush()
    except Exception as e:
        print(f"[ERROR] 파싱 실패: {e}")
        sys.exit(1)

    parse_info = {
        'paragraphs': len(result['paragraphs']),
        'tables': len(result['tables']),
        'headings': len(result['headings']),
        'images': len(result['image_refs']),
        'elapsed': result.get('elapsed_seconds', 0),
        'errors': result.get('errors', []),
    }

    # ── Step 1.5: 페이지 매핑 ──
    page_mapper = None
    if not args.no_page_map:
        print("\n[Step 1.5] 페이지 매핑 (pyhwpx)...")
        sys.stdout.flush()
        page_mapper = PageMapper(str(hwpx_path))
        page_map = page_mapper.extract_page_info()
        if page_mapper.total_pages:
            parse_info['total_pages'] = page_mapper.total_pages
        print(f"  -> 매핑 결과: {len(page_map)}개 문단")
        sys.stdout.flush()

    # ── Step 2: 텍스트 오타 검사 (A단계) ──
    print("\n[Step 2] 텍스트 오타 검사 (A단계)...")
    sys.stdout.flush()
    text_checker = TextChecker(result['paragraphs'])
    text_issues = text_checker.check_all()

    # 페이지 번호 매핑
    if page_mapper:
        for issue in text_issues:
            # location에서 줄 번호 추출
            m = re.match(r'줄\s*(\d+)', issue.location)
            if m:
                line_num = int(m.group(1))
                issue.page = page_mapper.get_page_str(line_num)

    err_cnt = sum(1 for i in text_issues if i.severity == '오타')
    warn_cnt = sum(1 for i in text_issues if i.severity == '의심')
    info_cnt = sum(1 for i in text_issues if i.severity == '정보')
    print(f"  -> 텍스트 이슈: {len(text_issues)}건 (오타: {err_cnt}, 의심: {warn_cnt}, 정보: {info_cnt})")
    sys.stdout.flush()

    # ── Step 3: 표 데이터 검증 (B단계) ──
    print("\n[Step 3] 표 데이터 검증 (B단계)...")
    sys.stdout.flush()
    tables_dir = Path(result['output_dir']) / 'tables'
    table_checker = TableChecker(tables_dir, result['paragraphs'])
    table_issues = table_checker.check_all()
    print(f"  -> 표 이슈: {len(table_issues)}건")
    sys.stdout.flush()

    # ── Step 4: 리포트 생성 (C단계) ──
    print("\n[Step 4] 리포트 생성 (C단계)...")
    sys.stdout.flush()
    report_path = output_dir / "typo_check_report.md"
    writer = ReportWriter(report_path, hwpx_path.name, parse_info)
    writer.write(text_issues, table_issues)
    print(f"  -> 리포트: {report_path}")

    # ── Step 5: CSV 저장 ──
    print("\n[Step 5] CSV 저장...")
    sys.stdout.flush()
    all_issues = text_issues + table_issues
    csv_path = output_dir / "typo_check_detail.csv"
    write_issues_csv(csv_path, all_issues)
    print(f"  -> CSV: {csv_path} ({len(all_issues)}건)")

    total = len(all_issues)
    print(f"\n{'=' * 60}")
    print(f"검사 완료: 총 {total}건 발견")
    print(f"산출물 위치: {output_dir}")
    print(f"  - typo_check_report.md  (Markdown 리포트)")
    print(f"  - typo_check_detail.csv (상세 CSV)")
    print(f"  - parsed/              (파싱 결과)")
    print(f"{'=' * 60}")
    sys.stdout.flush()


if __name__ == '__main__':
    main()
