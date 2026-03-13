# -*- coding: utf-8 -*-
"""
문경 영순 타당성 보고서 오타 검사 스크립트
- A단계: 텍스트 오타 검사 (full_text.txt)
- B단계: 표 데이터 검증 (CSV)
- C단계: 결과 종합 리포트 (typo_check_report.md)
"""
import sys, os, re, csv, json
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Optional

# ──────────────────────────────────────────────
# 설정
# ──────────────────────────────────────────────
PARSED_DIR = Path(r"d:\git_rk\project\25_n33_MunKyung\hwpx\hwpx_parsed"
                  r"\문경 영순_타당성 보고서(송부용)_20260217_v4_20260219_1908")
TEXT_FILE = PARSED_DIR / "full_text.txt"
TABLES_DIR = PARSED_DIR / "tables"
OUTPUT_REPORT = Path(r"d:\git_rk\project\25_n33_MunKyung\hwpx\typo_check_report.md")


@dataclass
class Issue:
    """검사에서 발견된 하나의 이슈"""
    category: str       # 'text' | 'table' | 'cross'
    severity: str       # '오타' | '의심' | '정보'
    location: str       # 줄 번호 or 표 번호
    original: str       # 원문 발췌
    description: str    # 설명
    suggestion: str = ""  # 수정 제안


# ══════════════════════════════════════════════
# A단계: TextChecker
# ══════════════════════════════════════════════
class TextChecker:
    """규칙 기반 텍스트 오타 검사"""

    # ── 사전 등록 오타 패턴 ──
    KNOWN_TYPOS = [
        # (정규식, 설명, 수정 제안)
        (r'입주주요조사', '입주수요조사 오타', '입주수요조사'),
        (r'의\s*7검토', '편집 잔류 숫자 "7"', '의 검토' ),
        (r'전기\s+전기기본설비비', '"전기" 중복', '전기기본설비비'),
        (r'한국은행\s*및\s*통계청의\s*한국은행에서', '"한국은행" 중복', '한국은행에서'),
        (r'부가가가치', '"가" 중복', '부가가치'),
        (r'현금유츌', '유출→유츌 오자', '현금유출'),
    ]

    # ── 미완성 문장 패턴 ──
    INCOMPLETE_ENDINGS = [
        r'사업비는\s*$',
        r'분석용\s*사업비는\s*$',
    ]

    # ── 율/률 혼용 검사 (앞 글자 받침 유무) ──
    # 받침 없는 글자 + 률 → 율, 받침 있는 글자 + 율 → 률
    YUL_PATTERN = re.compile(r'([가-힣])(율|률)')

    # ── 용어 불일치 후보 ──
    TERM_VARIANTS = {
        '지원시설용지': ['교육연구시설용지'],  # 동일 개념인데 다른 표기
    }

    def __init__(self, text_path: Path):
        with open(text_path, 'r', encoding='utf-8') as f:
            self.lines = [line.rstrip('\r\n') for line in f.readlines()]
        self.issues: List[Issue] = []

    def check_all(self) -> List[Issue]:
        self._check_known_typos()
        self._check_incomplete_sentences()
        self._check_yul_ryul()
        self._check_bracket_pairs()
        self._check_term_consistency()
        self._check_number_consistency()
        self._check_duplicate_phrases()
        return self.issues

    def _check_known_typos(self):
        for idx, line in enumerate(self.lines, 1):
            for pattern, desc, suggestion in self.KNOWN_TYPOS:
                m = re.search(pattern, line)
                if m:
                    context = line[max(0, m.start()-15):m.end()+15]
                    self.issues.append(Issue(
                        category='text', severity='오타',
                        location=f'줄 {idx}',
                        original=f'...{context}...',
                        description=desc,
                        suggestion=suggestion
                    ))

    def _check_incomplete_sentences(self):
        for idx, line in enumerate(self.lines, 1):
            stripped = line.strip()
            if not stripped:
                continue
            for pattern in self.INCOMPLETE_ENDINGS:
                if re.search(pattern, stripped):
                    self.issues.append(Issue(
                        category='text', severity='의심',
                        location=f'줄 {idx}',
                        original=stripped[-60:] if len(stripped) > 60 else stripped,
                        description='문장이 미완결 상태로 끝남',
                        suggestion='뒤에 구체적 금액/내용 보충 필요'
                    ))

    def _check_yul_ryul(self):
        """율/률 혼용 검사 — 실제 오류만 보고"""
        for idx, line in enumerate(self.lines, 1):
            for m in self.YUL_PATTERN.finditer(line):
                prev_char = m.group(1)
                suffix = m.group(2)
                # 받침 유무 판별 (유니코드 한글 분해)
                code = ord(prev_char) - 0xAC00
                jongseong = code % 28  # 0 = 받침 없음
                if jongseong == 0 and suffix == '률':
                    # 받침 없는데 '률' 사용 → '율'이 맞음
                    context = line[max(0, m.start()-10):m.end()+10]
                    self.issues.append(Issue(
                        category='text', severity='의심',
                        location=f'줄 {idx}',
                        original=f'...{context}...',
                        description=f'"{prev_char}률" → 받침 없으므로 "{prev_char}율"이 표준',
                        suggestion=f'{prev_char}율'
                    ))
                elif jongseong != 0 and suffix == '율':
                    # 받침 있는데 '율' 사용 → '률'이 맞음 (단, ㄹ받침 제외)
                    if jongseong != 8:  # ㄹ받침(8)은 '율' 사용
                        context = line[max(0, m.start()-10):m.end()+10]
                        self.issues.append(Issue(
                            category='text', severity='의심',
                            location=f'줄 {idx}',
                            original=f'...{context}...',
                            description=f'"{prev_char}율" → 받침 있으므로 "{prev_char}률"이 표준',
                            suggestion=f'{prev_char}률'
                        ))

    def _check_bracket_pairs(self):
        """괄호 짝 검사"""
        pairs = [('(', ')'), ('「', '」'), ('[', ']')]
        for idx, line in enumerate(self.lines, 1):
            for open_b, close_b in pairs:
                if line.count(open_b) != line.count(close_b):
                    self.issues.append(Issue(
                        category='text', severity='정보',
                        location=f'줄 {idx}',
                        original=f'{open_b}:{line.count(open_b)}개, {close_b}:{line.count(close_b)}개',
                        description=f'괄호 {open_b}{close_b} 짝 불일치',
                    ))

    def _check_term_consistency(self):
        """용어 불일치 검사"""
        for standard, variants in self.TERM_VARIANTS.items():
            for idx, line in enumerate(self.lines, 1):
                for variant in variants:
                    if variant in line:
                        context = line[max(0, line.index(variant)-15):line.index(variant)+len(variant)+15]
                        self.issues.append(Issue(
                            category='text', severity='의심',
                            location=f'줄 {idx}',
                            original=f'...{context}...',
                            description=f'"{variant}" — 다른 곳에서는 "{standard}"로 표기',
                            suggestion=standard
                        ))

    def _check_number_consistency(self):
        """핵심 숫자의 일관성 검사"""
        # 조성원가 510.8 vs 510.9 검사
        values_510 = []
        for idx, line in enumerate(self.lines, 1):
            for m in re.finditer(r'510\.\d', line):
                values_510.append((idx, m.group()))

        unique_vals = set(v for _, v in values_510)
        if len(unique_vals) > 1:
            locs = ', '.join(f'줄{i}:{v}' for i, v in values_510)
            self.issues.append(Issue(
                category='text', severity='의심',
                location='복수 위치',
                original=locs,
                description=f'조성원가 값 불일치: {unique_vals}',
                suggestion='정확한 값 확인 필요 (반올림 차이 가능)'
            ))

    def _check_duplicate_phrases(self):
        """문장 내 주요 구절 반복 검사"""
        for idx, line in enumerate(self.lines, 1):
            # 동일 절이 한 문장 내에서 반복되는 경우
            stripped = line.strip()
            if len(stripped) < 20:
                continue
            # 쉼표로 분리된 절이 동일한 경우
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


# ══════════════════════════════════════════════
# B단계: TableChecker
# ══════════════════════════════════════════════
class TableChecker:
    """표 데이터 숫자 검증"""

    def __init__(self, tables_dir: Path, text_lines: List[str]):
        self.tables_dir = tables_dir
        self.text_lines = text_lines
        self.issues: List[Issue] = []
        self.tables: Dict[int, List[List[str]]] = {}
        self._load_tables()

    def _load_tables(self):
        """CSV 파일들 로드"""
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
        self._check_cross_table()
        self._check_text_table_cross()
        return self.issues

    def _parse_number(self, s: str) -> Optional[float]:
        """문자열을 숫자로 변환 시도"""
        s = s.strip().replace(',', '').replace(' ', '')
        if not s or s == '-' or s == '':
            return None
        # 퍼센트 제거
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

            # 합계 행 찾기 (첫 번째 열에 '합계' 또는 '합 계' 포함)
            sum_row_idx = None
            for i, row in enumerate(rows):
                if row and re.search(r'합\s*계', row[0]):
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

                # 데이터 행들의 합
                actual_sum = 0
                data_count = 0
                for i in range(sum_row_idx + 1, len(rows)):
                    if i >= len(rows):
                        break
                    if col_idx < len(rows[i]):
                        val = self._parse_number(rows[i][col_idx])
                        if val is not None:
                            actual_sum += val
                            data_count += 1

                if data_count >= 2 and abs(expected) > 0:
                    diff = abs(actual_sum - expected)
                    rel_diff = diff / abs(expected) * 100
                    if rel_diff > 1.0 and diff > 1:  # 1% 이상 차이, 절대값 1 이상
                        self.issues.append(Issue(
                            category='table', severity='의심',
                            location=f'표 {tbl_num}, 열 {col_idx+1}',
                            original=f'합계행={expected:,.1f}, 실제합={actual_sum:,.1f}',
                            description=f'합계 불일치 (차이: {diff:,.1f}, {rel_diff:.1f}%)',
                            suggestion='합산 로직 또는 원본 데이터 재확인'
                        ))

    def _check_cross_table(self):
        """반복 표 간 교차 검증 — 총사업비 76,510 확인"""
        key_values = {
            '총사업비': 76510,
            '유상공급면적': 149769,
        }

        tables_with_values: Dict[str, List[Tuple[int, float]]] = {k: [] for k in key_values}

        for tbl_num, rows in self.tables.items():
            for row in rows:
                for cell in row:
                    for key, expected in key_values.items():
                        val = self._parse_number(cell)
                        if val is not None and abs(val - expected) < 1:
                            tables_with_values[key].append((tbl_num, val))

        # 보고 (정보성)
        for key, occurrences in tables_with_values.items():
            if occurrences:
                locs = ', '.join(f'표{t}' for t, v in occurrences)
                self.issues.append(Issue(
                    category='table', severity='정보',
                    location=locs,
                    original=f'{key}={key_values[key]:,}',
                    description=f'핵심 값 "{key}"이(가) {len(occurrences)}개 표에서 일치 확인',
                ))

    def _check_text_table_cross(self):
        """본문 핵심 숫자 ↔ 표 교차 검증"""
        # 본문에서 핵심 분석 결과 추출
        text_values = {}
        full_text = '\n'.join(self.text_lines)

        # 경제성 분석 결과
        bc_match = re.search(r'편익.*?B/C.*?(\d+\.\d+)', full_text)
        if bc_match:
            text_values['B/C'] = float(bc_match.group(1))

        npv_match = re.search(r'순현재가치.*?NPV.*?[–-]?\s*([\d,]+)', full_text)
        if npv_match:
            text_values['NPV'] = float(npv_match.group(1).replace(',', ''))

        irr_match = re.search(r'내부수익률.*?IRR.*?(\d+\.\d+)%', full_text)
        if irr_match:
            text_values['경제성IRR'] = float(irr_match.group(1))

        # 재무성 분석 결과
        pi_match = re.search(r'PI.*?(\d+\.\d+)', full_text)
        if pi_match:
            text_values['PI'] = float(pi_match.group(1))

        fnpv_match = re.search(r'FNPV.*?(\d[\d,]+)', full_text)
        if fnpv_match:
            text_values['FNPV'] = float(fnpv_match.group(1).replace(',', ''))

        if text_values:
            items = ', '.join(f'{k}={v}' for k, v in text_values.items())
            self.issues.append(Issue(
                category='cross', severity='정보',
                location='본문',
                original=items,
                description='본문에서 추출한 핵심 분석 결과값 (수동 대조 필요)',
            ))


# ══════════════════════════════════════════════
# C단계: ReportWriter
# ══════════════════════════════════════════════
class ReportWriter:
    """검사 결과를 Markdown 리포트로 출력"""

    def __init__(self, output_path: Path):
        self.output_path = output_path

    def write(self, text_issues: List[Issue], table_issues: List[Issue]):
        all_issues = text_issues + table_issues

        # 심각도별 분류
        errors = [i for i in all_issues if i.severity == '오타']
        warnings = [i for i in all_issues if i.severity == '의심']
        infos = [i for i in all_issues if i.severity == '정보']

        lines = []
        lines.append('# 문경 영순 타당성 보고서 — 오타 검사 결과 리포트\n')
        lines.append(f'> 검사일: 2026-02-19 | 대상: `full_text.txt` (266줄) + CSV 52개\n')
        lines.append('---\n')

        # 요약
        lines.append('## 검사 결과 요약\n')
        lines.append(f'| 심각도 | 건수 |')
        lines.append(f'| --- | --- |')
        lines.append(f'| 🔴 오타 (확정) | **{len(errors)}건** |')
        lines.append(f'| 🟡 의심 (확인 필요) | **{len(warnings)}건** |')
        lines.append(f'| 🔵 정보 (참고) | **{len(infos)}건** |')
        lines.append(f'| **합계** | **{len(all_issues)}건** |')
        lines.append('')

        # 오타 (확정)
        if errors:
            lines.append('---\n')
            lines.append('## 🔴 오타 (확정)\n')
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
            lines.append('| # | 위치 | 내용 | 설명 |')
            lines.append('| --- | --- | --- | --- |')
            for i, issue in enumerate(infos, 1):
                orig = issue.original.replace('|', '\\|')
                lines.append(f'| {i} | {issue.location} | {orig} | {issue.description} |')
            lines.append('')

        # 카테고리별 통계
        lines.append('---\n')
        lines.append('## 검사 항목별 통계\n')
        cats = {}
        for issue in all_issues:
            cats[issue.category] = cats.get(issue.category, 0) + 1
        cat_names = {'text': '텍스트 검사 (A단계)', 'table': '표 검증 (B단계)', 'cross': '교차 검증'}
        lines.append('| 검사 항목 | 건수 |')
        lines.append('| --- | --- |')
        for cat, name in cat_names.items():
            lines.append(f'| {name} | {cats.get(cat, 0)}건 |')
        lines.append('')

        with open(self.output_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))

        return self.output_path


# ══════════════════════════════════════════════
# 메인
# ══════════════════════════════════════════════
def main():
    print("=" * 50)
    print("오타 검사 시작")
    print("=" * 50)

    # A단계: 텍스트 검사
    print("\n[A단계] 텍스트 오타 검사...")
    text_checker = TextChecker(TEXT_FILE)
    text_issues = text_checker.check_all()
    print(f"  → 텍스트 이슈: {len(text_issues)}건")

    errors = sum(1 for i in text_issues if i.severity == '오타')
    warnings = sum(1 for i in text_issues if i.severity == '의심')
    infos = sum(1 for i in text_issues if i.severity == '정보')
    print(f"    오타: {errors}건, 의심: {warnings}건, 정보: {infos}건")

    # B단계: 표 검증
    print("\n[B단계] 표 데이터 검증...")
    table_checker = TableChecker(TABLES_DIR, text_checker.lines)
    table_issues = table_checker.check_all()
    print(f"  → 표 이슈: {len(table_issues)}건")

    # C단계: 리포트 생성
    print("\n[C단계] 리포트 생성...")
    writer = ReportWriter(OUTPUT_REPORT)
    report_path = writer.write(text_issues, table_issues)
    print(f"  → 리포트: {report_path}")

    total = len(text_issues) + len(table_issues)
    print(f"\n{'=' * 50}")
    print(f"검사 완료: 총 {total}건 발견")
    print(f"{'=' * 50}")


if __name__ == '__main__':
    main()
