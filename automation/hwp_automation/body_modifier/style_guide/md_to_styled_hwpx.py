# -*- coding: utf-8 -*-
"""
md_to_styled_hwpx.py — 마크다운 → 스타일가이드 기반 HWPX 변환기

스타일 프로필(JSON + header.xml)을 기반으로
마크다운 파일을 HWPX로 변환합니다. (XML-first, pyhwpx 불필요)

사용법:
    python md_to_styled_hwpx.py --input wording.md --profile bix --output result.hwpx
    python md_to_styled_hwpx.py --input wording.md --output result.hwpx  # 기본 프로필 사용
"""
import sys, io, os, json, re, zipfile, argparse
from pathlib import Path
from datetime import datetime
from lxml import etree

# UTF-8 출력 보장
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

SCRIPT_DIR = Path(__file__).parent
PROFILES_DIR = SCRIPT_DIR / "profiles"
INDEX_FILE = PROFILES_DIR / "_index.json"

NS = {
    'hp':  'http://www.hancom.co.kr/hwpml/2011/paragraph',
    'hh':  'http://www.hancom.co.kr/hwpml/2011/head',
    'hs':  'http://www.hancom.co.kr/hwpml/2011/section',
}

NS_MAP = {
    'hp':  'http://www.hancom.co.kr/hwpml/2011/paragraph',
    'hs':  'http://www.hancom.co.kr/hwpml/2011/section',
}


# ══════════════════════════════════════════════
#  마크다운 파서 (md_to_hwpx.py MarkdownParser 기반)
# ══════════════════════════════════════════════
class MdElement:
    pass

class MdHeading(MdElement):
    def __init__(self, level, text):
        self.level = level
        self.text = text

class MdParagraph(MdElement):
    def __init__(self, text):
        self.text = text

class MdBullet(MdElement):
    def __init__(self, text):
        self.text = text

class MdBlockquote(MdElement):
    def __init__(self, text):
        self.text = text

class MdHorizontalRule(MdElement):
    pass


def parse_markdown(filepath):
    """마크다운 파일을 MdElement 리스트로 파싱"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    lines = content.split('\n')
    elements = []
    i = 0

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        if not stripped:
            i += 1
            continue

        # 수평선
        if re.match(r'^[-*_]{3,}\s*$', stripped):
            elements.append(MdHorizontalRule())
            i += 1
            continue

        # 제목
        heading_match = re.match(r'^(#{1,6})\s+(.+)$', stripped)
        if heading_match:
            level = len(heading_match.group(1))
            text = heading_match.group(2).strip()
            elements.append(MdHeading(level, text))
            i += 1
            continue

        # 인용문
        if stripped.startswith('>'):
            bq_lines = []
            while i < len(lines) and lines[i].strip().startswith('>'):
                bq_text = re.sub(r'^>\s*', '', lines[i].strip())
                bq_text = re.sub(r'^\[!(NOTE|TIP|IMPORTANT|WARNING|CAUTION)\]\s*', '', bq_text)
                # 마크다운 서식 제거
                bq_text = re.sub(r'\*\*(.+?)\*\*', r'\1', bq_text)
                bq_text = re.sub(r'\*(.+?)\*', r'\1', bq_text)
                if bq_text:
                    bq_lines.append(bq_text)
                i += 1
            if bq_lines:
                elements.append(MdBlockquote(' '.join(bq_lines)))
            continue

        # 불릿 포인트
        if re.match(r'^[*\-+]\s+', stripped):
            text = re.sub(r'^[*\-+]\s+', '', stripped)
            # 마크다운 서식 제거
            text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)
            text = re.sub(r'\*(.+?)\*', r'\1', text)
            elements.append(MdBullet(text))
            i += 1
            continue

        # 일반 문단
        para_lines = []
        while i < len(lines):
            cur = lines[i].strip()
            if not cur or cur.startswith('#') or cur.startswith('>') or \
               re.match(r'^[-*_]{3,}\s*$', cur) or re.match(r'^[*\-+]\s+', cur):
                break
            para_lines.append(cur)
            i += 1
        if para_lines:
            elements.append(MdParagraph(' '.join(para_lines)))

    return elements


# ══════════════════════════════════════════════
#  프로필 로드
# ══════════════════════════════════════════════
def load_profile(profile_name=None):
    """프로필 로드 (이름 지정 또는 기본 프로필)"""
    index = {}
    if INDEX_FILE.exists():
        with open(INDEX_FILE, 'r', encoding='utf-8') as f:
            index = json.load(f)

    if profile_name is None:
        profile_name = index.get('default')
        if profile_name is None:
            raise ValueError("기본 프로필이 설정되어 있지 않습니다. --profile 옵션을 지정하세요.")

    profile_dir = PROFILES_DIR / profile_name
    sg_path = profile_dir / 'style_guide.json'
    header_path = profile_dir / 'header.xml'

    if not sg_path.exists():
        raise FileNotFoundError(f"프로필 '{profile_name}'을 찾을 수 없습니다: {sg_path}")

    with open(sg_path, 'r', encoding='utf-8') as f:
        style_guide = json.load(f)

    header_bytes = None
    if header_path.exists():
        with open(header_path, 'rb') as f:
            header_bytes = f.read()

    return style_guide, header_bytes, profile_name


# ══════════════════════════════════════════════
#  section0.xml 생성
# ══════════════════════════════════════════════
def get_role_style(style_guide, role):
    """역할에 해당하는 (charPrIDRef, paraPrIDRef) 반환"""
    rm = style_guide.get('role_mapping', {})
    if role in rm:
        return rm[role]['charPrIDRef'], rm[role]['paraPrIDRef']
    # 폴백: body
    body = rm.get('body', {'charPrIDRef': '0', 'paraPrIDRef': '0'})
    return body['charPrIDRef'], body['paraPrIDRef']


def element_to_role(element):
    """MdElement → 역할 이름"""
    if isinstance(element, MdHeading):
        return f'h{element.level}' if element.level <= 3 else 'h3'
    elif isinstance(element, MdBullet):
        return 'bullet'
    elif isinstance(element, MdBlockquote):
        return 'blockquote'
    elif isinstance(element, MdParagraph):
        return 'body'
    elif isinstance(element, MdHorizontalRule):
        return 'separator'
    return 'body'


def build_section_xml(elements, style_guide, template_hwpx_path=None):
    """MdElement 리스트를 section0.xml로 변환"""
    HP = 'http://www.hancom.co.kr/hwpml/2011/paragraph'

    # secPr/colPr 요소만 템플릿에서 추출 (원본 텍스트는 제거)
    secpr_elem = None
    ctrl_elem = None
    if template_hwpx_path and os.path.exists(template_hwpx_path):
        with zipfile.ZipFile(template_hwpx_path, 'r') as z:
            sections = sorted([n for n in z.namelist()
                               if n.startswith('Contents/section') and n.endswith('.xml')])
            if sections:
                sec_bytes = z.read(sections[0])
                sec_tree = etree.fromstring(sec_bytes)
                # 첫 문단에서 secPr과 ctrl(colPr) 요소만 추출
                for child in sec_tree:
                    if etree.QName(child.tag).localname == 'p':
                        for run in child.findall(f'{{{HP}}}run', NS):
                            sp = run.find(f'{{{HP}}}secPr', NS)
                            if sp is not None:
                                secpr_elem = sp
                            ct = run.find(f'{{{HP}}}ctrl', NS)
                            if ct is not None:
                                ctrl_elem = ct
                        break

    # section 루트 생성
    sec = etree.Element('{http://www.hancom.co.kr/hwpml/2011/section}sec', nsmap=NS_MAP)

    para_id = 1000000001

    # secPr 포함 빈 첫 문단 (원본 텍스트 없이 secPr만)
    first_p = etree.Element(f'{{{HP}}}p')
    first_p.set('id', str(para_id))
    first_p.set('paraPrIDRef', '0')
    first_p.set('styleIDRef', '0')
    first_p.set('pageBreak', '0')
    first_p.set('columnBreak', '0')
    first_p.set('merged', '0')
    first_run = etree.SubElement(first_p, f'{{{HP}}}run')
    first_run.set('charPrIDRef', '0')
    if secpr_elem is not None:
        first_run.append(secpr_elem)
    if ctrl_elem is not None:
        first_run.append(ctrl_elem)
    empty_t = etree.SubElement(first_run, f'{{{HP}}}t')
    sec.append(first_p)
    para_id += 1

    # 본문 요소 변환
    for elem in elements:
        role = element_to_role(elem)

        # ── 불필요 요소 필터링 ──
        # h1 타이틀 (예: "통계 분석 결과 워딩 보고서") 제거
        if isinstance(elem, MdHeading) and elem.level == 1:
            continue
        # blockquote 메타데이터 (예: "생성일시: ...") 제거
        if isinstance(elem, MdBlockquote) and ('생성일시' in elem.text or '생성 일시' in elem.text):
            continue

        if isinstance(elem, MdHorizontalRule):
            # 빈 문단 (구분선) — 생략하여 불필요한 빈 줄 제거
            continue

        char_id, para_id_ref = get_role_style(style_guide, role)
        text = ''
        if isinstance(elem, (MdHeading, MdParagraph, MdBullet, MdBlockquote)):
            text = elem.text

            # ── h2 소제목 텍스트 정리 ──
            # "A1. 제목 (N=140, 단수 응답)" → "A1. 제목"
            # 문항 번호(A1.)는 유지, (N=xxx) 접미사만 제거
            if isinstance(elem, MdHeading) and elem.level == 2:
                text = re.sub(r'\s*\(N=\d+[^)]*\)\s*$', '', text)  # (N=xxx, ...) 접미사 제거

        p = _make_para(para_id, para_id_ref, char_id, text)
        sec.append(p)
        para_id += 1

    return sec


def _make_para(para_id, para_pr_ref, char_pr_ref, text):
    """단일 문단 XML 요소 생성"""
    HP = 'http://www.hancom.co.kr/hwpml/2011/paragraph'
    p = etree.Element(f'{{{HP}}}p')
    p.set('id', str(para_id))
    p.set('paraPrIDRef', str(para_pr_ref))
    p.set('styleIDRef', '0')
    p.set('pageBreak', '0')
    p.set('columnBreak', '0')
    p.set('merged', '0')

    run = etree.SubElement(p, f'{{{HP}}}run')
    run.set('charPrIDRef', str(char_pr_ref))

    t = etree.SubElement(run, f'{{{HP}}}t')
    if text:
        t.text = text

    return p


# ══════════════════════════════════════════════
#  HWPX 빌드
# ══════════════════════════════════════════════
def build_hwpx(template_hwpx_path, header_bytes, section_xml, output_path):
    """템플릿 HWPX를 기반으로 header.xml과 section0.xml을 교체하여 빌드"""
    section_bytes = etree.tostring(section_xml, xml_declaration=True,
                                   encoding='UTF-8', standalone=True)

    with zipfile.ZipFile(template_hwpx_path, 'r') as zin:
        file_list = zin.namelist()
        file_data = {}
        for name in file_list:
            file_data[name] = zin.read(name)

    # header.xml 교체
    if header_bytes:
        file_data['Contents/header.xml'] = header_bytes

    # section0.xml 교체 (첫 번째 section)
    sections = sorted([n for n in file_list
                       if n.startswith('Contents/section') and n.endswith('.xml')])
    if sections:
        file_data[sections[0]] = section_bytes

    # HWPX 저장
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zout:
        for name in file_list:
            if name == 'mimetype':
                zout.writestr(name, file_data[name], compress_type=zipfile.ZIP_STORED)
            else:
                zout.writestr(name, file_data[name])


# ══════════════════════════════════════════════
#  CLI
# ══════════════════════════════════════════════
def main():
    parser = argparse.ArgumentParser(description='마크다운 → 스타일가이드 기반 HWPX 변환기')
    parser.add_argument('--input', required=True, help='입력 마크다운 파일 경로')
    parser.add_argument('--profile', default=None, help='스타일 프로필 이름 (기본: _index.json의 default)')
    parser.add_argument('--template', default=None, help='템플릿 HWPX 경로 (기본: 프로필의 source)')
    parser.add_argument('--output', default=None, help='출력 HWPX 경로 (기본: 자동 생성)')
    args = parser.parse_args()

    # 프로필 로드
    print(f"[1/4] 프로필 로드...")
    style_guide, header_bytes, profile_name = load_profile(args.profile)
    print(f"  프로필: {profile_name}")
    print(f"  역할 매핑: {list(style_guide.get('role_mapping', {}).keys())}")

    # 템플릿 경로 결정
    template_path = args.template or style_guide.get('source', '')
    if not os.path.exists(template_path):
        print(f"  [WARNING] 템플릿 파일 없음: {template_path}")
        print(f"  secPr 없이 기본 구조로 생성합니다.")
        template_path = None

    # 마크다운 파싱
    print(f"[2/4] 마크다운 파싱: {args.input}")
    elements = parse_markdown(args.input)
    print(f"  요소 수: {len(elements)}개")
    for elem in elements[:5]:
        role = element_to_role(elem)
        text = getattr(elem, 'text', '')[:40]
        print(f"    {role:>12s}: {text}...")

    # section0.xml 생성
    print(f"[3/4] section0.xml 생성...")
    section_xml = build_section_xml(elements, style_guide, template_path)
    para_count = len(section_xml.findall(f'{{{NS_MAP["hp"]}}}p'))
    print(f"  문단 수: {para_count}개")

    # HWPX 빌드
    if template_path:
        output_path = args.output
        if output_path is None:
            input_dir = os.path.dirname(os.path.abspath(args.input))
            basename = os.path.splitext(os.path.basename(args.input))[0]
            timestamp = datetime.now().strftime('%y%m%d_%H%M')
            output_path = os.path.join(input_dir, f'{basename}_{timestamp}.hwpx')

        print(f"[4/4] HWPX 빌드: {output_path}")
        build_hwpx(template_path, header_bytes, section_xml, output_path)
        print(f"\n[OK] 변환 완료: {output_path}")
    else:
        # 템플릿 없이 section XML만 출력
        output_xml = args.output or 'section0.xml'
        with open(output_xml, 'wb') as f:
            f.write(etree.tostring(section_xml, xml_declaration=True,
                                   encoding='UTF-8', standalone=True, pretty_print=True))
        print(f"\n[OK] section XML 저장: {output_xml}")


if __name__ == '__main__':
    main()
