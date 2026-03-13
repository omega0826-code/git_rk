# -*- coding: utf-8 -*-
"""
parser.py - HWPX 파싱/분석 모듈

원본 HWPX 파일에서 header.xml과 section XML을 추출하여
문서의 구조(charPr, paraPr, 본문 텍스트, 표 데이터)를 분석합니다.

사용법 (단독 실행):
    python -m modules.parser --input 원본.hwpx --output parsed_output.md

사용법 (모듈 import):
    from modules.parser import parse_hwpx
    result = parse_hwpx("원본.hwpx")
"""
import sys, io, zipfile, argparse
from lxml import etree

sys.path.insert(0, '..')
from config.namespaces import NS


def extract_xml_from_hwpx(hwpx_path, entry_name):
    """HWPX(ZIP)에서 특정 XML 엔트리를 바이트로 추출"""
    with zipfile.ZipFile(hwpx_path, 'r') as z:
        return z.read(entry_name)


def list_sections(hwpx_path):
    """HWPX 내 section 파일 목록 반환 (예: ['Contents/section0.xml', ...])"""
    with zipfile.ZipFile(hwpx_path, 'r') as z:
        return sorted([n for n in z.namelist() if n.startswith('Contents/section') and n.endswith('.xml')])


def parse_char_properties(header_bytes):
    """header.xml에서 charPr 목록을 파싱하여 dict로 반환

    Returns:
        dict: {id(str): {height, textColor, bold, italic, fontRef, spacing, ratio, ...}}
    """
    tree = etree.fromstring(header_bytes)
    char_props = tree.find('.//hh:charProperties', NS)
    if char_props is None:
        return {}

    result = {}
    for cp in char_props.findall('hh:charPr', NS):
        cp_id = cp.get('id', '')
        info = {
            'height': cp.get('height', ''),
            'textColor': cp.get('textColor', ''),
            'bold': cp.get('bold', '0'),
            'italic': cp.get('italic', '0'),
            'spacing': cp.get('spacing', ''),
            'ratio': cp.get('ratio', ''),
        }
        # fontRef 추출
        font_ref = cp.find('hh:fontRef', NS)
        if font_ref is not None:
            info['fontRef_hangul'] = font_ref.get('hangul', '')
        result[cp_id] = info
    return result


def parse_para_properties(header_bytes):
    """header.xml에서 paraPr 목록을 파싱하여 dict로 반환

    Returns:
        dict: {id(str): {align, leftMargin, indent, lineSpacing, ...}}
    """
    tree = etree.fromstring(header_bytes)
    para_props = tree.find('.//hh:paraProperties', NS)
    if para_props is None:
        return {}

    result = {}
    for pp in para_props.findall('hh:paraPr', NS):
        pp_id = pp.get('id', '')
        info = {'align': '', 'leftMargin': '', 'indent': '', 'lineSpacing': ''}
        align_elem = pp.find('hh:align', NS)
        if align_elem is not None:
            info['align'] = align_elem.get('horizontal', '')
        margin_elem = pp.find('hh:margin', NS)
        if margin_elem is not None:
            info['leftMargin'] = margin_elem.get('left', '')
            info['indent'] = margin_elem.get('indent', '')
        spacing_elem = pp.find('hh:lineSpacing', NS)
        if spacing_elem is not None:
            info['lineSpacing'] = spacing_elem.get('value', '')
        result[pp_id] = info
    return result


def get_para_text(p_elem):
    """문단 요소에서 전체 텍스트 추출"""
    texts = []
    for run in p_elem.findall('.//hp:run', NS):
        for t in run.findall('hp:t', NS):
            if t.text:
                texts.append(t.text)
    return ''.join(texts).strip()


def get_para_style_info(p_elem):
    """문단의 paraPrIDRef, charPrIDRef(run 기반) 추출"""
    para_pr = p_elem.get('paraPrIDRef', '')
    char_prs = set()
    for run in p_elem.findall('.//hp:run', NS):
        char_prs.add(run.get('charPrIDRef', ''))
    return para_pr, char_prs


def parse_section(section_bytes, char_info=None, para_info=None):
    """section XML에서 본문 문단과 표를 구조적으로 파싱

    Args:
        section_bytes: section XML 바이트
        char_info: parse_char_properties()의 반환값 (계층 판단용)
        para_info: parse_para_properties()의 반환값 (계층 판단용)

    Returns:
        list[dict]: 각 요소가 {type: 'para'|'table', text, paraPr, charPrs, ...}
    """
    tree = etree.fromstring(section_bytes)
    elements = []

    for child in tree:
        tag = etree.QName(child.tag).localname if isinstance(child.tag, str) else ''

        if tag == 'p':
            text = get_para_text(child)
            para_pr, char_prs = get_para_style_info(child)
            elements.append({
                'type': 'para',
                'text': text,
                'paraPrIDRef': para_pr,
                'charPrIDRefs': char_prs,
                'element': child,  # 수정 단계에서 직접 활용
            })

        elif tag == 'tbl':
            # 표 데이터 추출 (행/열/셀 텍스트)
            rows = child.findall('.//hp:tr', NS)
            table_data = []
            for row in rows:
                cells = row.findall('hp:tc', NS)
                row_data = []
                for cell in cells:
                    cell_texts = []
                    for p in cell.findall('.//hp:p', NS):
                        cell_texts.append(get_para_text(p))
                    row_data.append(' '.join(cell_texts))
                table_data.append(row_data)
            elements.append({
                'type': 'table',
                'rows': table_data,
                'element': child,
            })

    return elements


def parse_hwpx(hwpx_path):
    """HWPX 파일 전체를 분석하여 구조화된 결과를 반환

    Returns:
        dict: {
            'header_bytes': bytes,
            'sections': {name: bytes},
            'char_properties': dict,
            'para_properties': dict,
            'parsed_sections': {name: list},
            'file_list': list,
        }
    """
    with zipfile.ZipFile(hwpx_path, 'r') as z:
        file_list = z.namelist()
        header_bytes = z.read('Contents/header.xml')
        sections = {}
        for name in sorted(file_list):
            if name.startswith('Contents/section') and name.endswith('.xml'):
                sections[name] = z.read(name)

    char_info = parse_char_properties(header_bytes)
    para_info = parse_para_properties(header_bytes)

    parsed_sections = {}
    for sec_name, sec_bytes in sections.items():
        parsed_sections[sec_name] = parse_section(sec_bytes, char_info, para_info)

    return {
        'header_bytes': header_bytes,
        'sections': sections,
        'char_properties': char_info,
        'para_properties': para_info,
        'parsed_sections': parsed_sections,
        'file_list': file_list,
    }


def export_to_markdown(parsed_result, output_path):
    """파싱 결과를 마크다운 파일로 내보내기"""
    with open(output_path, 'w', encoding='utf-8') as f:
        for sec_name, elements in parsed_result['parsed_sections'].items():
            f.write(f"# {sec_name}\n\n")
            for elem in elements:
                if elem['type'] == 'para':
                    if elem['text']:
                        f.write(f"{elem['text']}\n\n")
                elif elem['type'] == 'table':
                    for row in elem['rows']:
                        f.write('| ' + ' | '.join(row) + ' |\n')
                    f.write('\n')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='HWPX 파싱/분석 모듈')
    parser.add_argument('--input', required=True, help='원본 HWPX 파일 경로')
    parser.add_argument('--output', default='parsed_output.md', help='마크다운 출력 경로')
    args = parser.parse_args()

    if sys.stdout.encoding != 'utf-8':
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

    result = parse_hwpx(args.input)
    export_to_markdown(result, args.output)

    print(f"[OK] 파싱 완료: {args.output}")
    print(f"  charPr 수: {len(result['char_properties'])}")
    print(f"  paraPr 수: {len(result['para_properties'])}")
    print(f"  섹션 수: {len(result['sections'])}")
