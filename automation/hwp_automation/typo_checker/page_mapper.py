# -*- coding: utf-8 -*-
"""
HWPX 원본에서 문단별 페이지 번호를 추출하여
오타 검사 결과의 줄 번호를 원본 페이지로 매핑한다.
"""
import sys, os, re, zipfile, json
from pathlib import Path
from lxml import etree

HWPX_FILE = Path(r"d:\git_rk\project\25_n33_MunKyung\hwpx\문경 영순_타당성 보고서(송부용)_20260217_v4.hwpx")
TEXT_FILE = Path(r"d:\git_rk\project\25_n33_MunKyung\hwpx\hwpx_parsed"
                 r"\문경 영순_타당성 보고서(송부용)_20260217_v4_20260219_1908\full_text.txt")

NS = {
    'hp': 'http://www.hancom.co.kr/hwpml/2011/paragraph',
    'hs': 'http://www.hancom.co.kr/hwpml/2011/section',
    'hc': 'http://www.hancom.co.kr/hwpml/2011/core',
}

def _tag(prefix, local):
    return f'{{{NS[prefix]}}}{local}'


def extract_paragraph_text(p_elem):
    """hp:p 요소에서 텍스트 추출 (표/머리말 내부 제외)"""
    texts = []
    for t in p_elem.iter(_tag('hp', 't')):
        if t.text:
            # titleMark 등 자식 요소의 tail도 포함
            texts.append(t.text)
    return ''.join(texts).strip()


def is_in_table(elem):
    """해당 요소가 표(hp:tbl) 안에 있는지 확인"""
    parent = elem.getparent()
    while parent is not None:
        if parent.tag == _tag('hp', 'tbl'):
            return True
        parent = parent.getparent()
    return False


def is_in_header_footer(elem):
    """머리말/꼬리말 안인지 확인"""
    parent = elem.getparent()
    while parent is not None:
        tag = parent.tag
        if 'header' in tag.lower() or 'footer' in tag.lower():
            return True
        parent = parent.getparent()
    return False


def get_page_mapping():
    """HWPX에서 문단별 페이지 번호를 추출"""
    with zipfile.ZipFile(str(HWPX_FILE), 'r') as z:
        # section 파일 찾기
        section_files = [f for f in z.namelist() if re.match(r'Contents/section\d+\.xml', f)]
        section_files.sort()

        para_page_map = []  # [(text, page_num), ...]
        current_page = 1

        for sec_file in section_files:
            xml_data = z.read(sec_file)
            root = etree.fromstring(xml_data)

            for p in root.iter(_tag('hp', 'p')):
                # 표/머리말 내부 문단은 건너뛰기 (full_text.txt와 동일 로직)
                if is_in_table(p) or is_in_header_footer(p):
                    continue

                # pageBreak 확인
                page_break = p.get('pageBreak', '0')
                if page_break == '1':
                    current_page += 1

                text = extract_paragraph_text(p)
                if text:
                    para_page_map.append({
                        'text': text,
                        'page': current_page,
                    })

    return para_page_map


def map_lines_to_pages(para_page_map):
    """full_text.txt의 줄 번호를 페이지에 매핑"""
    with open(TEXT_FILE, 'r', encoding='utf-8') as f:
        text_lines = [line.rstrip('\r\n') for line in f.readlines()]

    line_to_page = {}
    para_idx = 0

    for line_num, line_text in enumerate(text_lines, 1):
        if not line_text.strip():
            continue

        # 매칭 시도: para_page_map에서 같은 텍스트 찾기
        best_page = None

        # 정확 매칭
        if para_idx < len(para_page_map):
            para = para_page_map[para_idx]
            # 텍스트 시작 부분 비교 (표가 섞인 줄은 앞부분만 일치)
            if line_text.strip().startswith(para['text'][:30]) or \
               para['text'].startswith(line_text.strip()[:30]):
                best_page = para['page']
                para_idx += 1
            else:
                # 순차 탐색으로 시도
                for search_idx in range(para_idx, min(para_idx + 5, len(para_page_map))):
                    if line_text.strip().startswith(para_page_map[search_idx]['text'][:30]) or \
                       para_page_map[search_idx]['text'].startswith(line_text.strip()[:30]):
                        best_page = para_page_map[search_idx]['page']
                        para_idx = search_idx + 1
                        break

        if best_page is not None:
            line_to_page[line_num] = best_page
        else:
            # 이전 줄의 페이지를 상속
            if line_num > 1 and (line_num - 1) in line_to_page:
                line_to_page[line_num] = line_to_page[line_num - 1]

    return line_to_page


def main():
    print("=" * 50)
    print("페이지 번호 매핑 시작")
    print("=" * 50)

    # 1. HWPX에서 문단별 페이지 추출
    print("\n[1] HWPX 파싱 중...")
    para_page_map = get_page_mapping()
    print(f"  → 본문 문단: {len(para_page_map)}개")

    # 페이지 통계
    pages = set(p['page'] for p in para_page_map)
    print(f"  → 페이지 범위: {min(pages)}~{max(pages)}페이지")

    # 2. 줄 번호-페이지 매핑
    print("\n[2] 줄-페이지 매핑 중...")
    line_to_page = map_lines_to_pages(para_page_map)
    print(f"  → 매핑 완료: {len(line_to_page)}/{266}줄")

    # 3. 오타 위치별 페이지 표시
    typo_lines = {
        44: '입주주요조사',
        71: '사업의 7검토',
        111: '미완성 문장',
        125: '전기 전기기본설비비',
        152: '한국은행 중복',
        158: '부가가가치율',
        177: '유효가동율',
        236: '미완성 문장',
        251: '문장 반복',
        263: '교육연구시설용지',
        266: '현금유츌'
    }

    print("\n[3] 오타별 페이지 매핑:")
    print(f"{'줄':>4s}  {'페이지':>4s}  오류 내용")
    print("-" * 45)
    results = {}
    for line_num, desc in sorted(typo_lines.items()):
        page = line_to_page.get(line_num, '?')
        print(f"{line_num:4d}  {str(page):>4s}  {desc}")
        results[line_num] = page

    # 4. JSON 저장
    output_json = Path(r"d:\git_rk\project\25_n33_MunKyung\hwpx\page_mapping.json")
    with open(output_json, 'w', encoding='utf-8') as f:
        json.dump({
            'total_paragraphs': len(para_page_map),
            'page_range': [min(pages), max(pages)],
            'line_to_page': {str(k): v for k, v in line_to_page.items()},
            'typo_pages': {str(k): v for k, v in results.items()},
        }, f, ensure_ascii=False, indent=2)
    print(f"\n  → 매핑 저장: {output_json}")

    print(f"\n{'=' * 50}")
    print("완료")
    print(f"{'=' * 50}")


if __name__ == '__main__':
    main()
