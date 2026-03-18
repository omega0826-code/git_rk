# -*- coding: utf-8 -*-
"""
extract_style.py — HWPX 스타일 프로필 추출기

HWPX 파일에서 charPr/paraPr/fontfaces를 추출하여
스타일 프로필(JSON + header.xml)을 생성합니다.

사용법:
    python extract_style.py --input 원본.hwpx --profile-name bix
    python extract_style.py --list
    python extract_style.py --info bix
"""
import sys, io, os, json, zipfile, argparse, shutil
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
    'hc':  'http://www.hancom.co.kr/hwpml/2011/core',
}


# ══════════════════════════════════════════════
#  폰트 추출
# ══════════════════════════════════════════════
def extract_fonts(header_tree):
    """fontfaces → {id: face_name} 매핑 (한글 기준)"""
    fonts = {}
    for ff in header_tree.findall('.//hh:fontface', NS):
        lang = ff.get('lang', '')
        if lang.upper() != 'HANGUL':
            continue
        for font in ff.findall('hh:font', NS):
            fid = font.get('id', '')
            fname = font.get('face', '')
            fonts[fid] = fname
    # 한글 fontfaces가 없으면 전체에서 추출
    if not fonts:
        for ff in header_tree.findall('.//hh:fontface', NS):
            for font in ff.findall('hh:font', NS):
                fid = font.get('id', '')
                fname = font.get('face', '')
                if fid not in fonts:
                    fonts[fid] = fname
    return fonts


# ══════════════════════════════════════════════
#  charPr 추출
# ══════════════════════════════════════════════
def extract_char_styles(header_tree, fonts):
    """charPr 목록 추출 → dict"""
    char_props = header_tree.find('.//hh:charProperties', NS)
    if char_props is None:
        return {}
    result = {}
    for cp in char_props.findall('hh:charPr', NS):
        cp_id = cp.get('id', '')
        height = int(cp.get('height', '1000'))
        font_ref = cp.find('hh:fontRef', NS)
        hangul_ref = font_ref.get('hangul', '0') if font_ref is not None else '0'
        font_name = fonts.get(hangul_ref, f'font_{hangul_ref}')
        bold_elem = cp.find('hh:bold', NS)
        has_bold = bold_elem is not None
        result[cp_id] = {
            'height': height,
            'height_pt': height / 100,
            'font_ref': hangul_ref,
            'font_name': font_name,
            'text_color': cp.get('textColor', '#000000'),
            'bold': has_bold,
            'italic': cp.find('hh:italic', NS) is not None,
            'spacing': cp.get('spacing', '0'),
            'ratio': cp.get('ratio', '100'),
        }
    return result


# ══════════════════════════════════════════════
#  paraPr 추출
# ══════════════════════════════════════════════
def extract_para_styles(header_tree):
    """paraPr 목록 추출 → dict"""
    para_props = header_tree.find('.//hh:paraProperties', NS)
    if para_props is None:
        return {}
    result = {}
    for pp in para_props.findall('hh:paraPr', NS):
        pp_id = pp.get('id', '')
        align_elem = pp.find('.//hh:align', NS)
        align = align_elem.get('horizontal', 'JUSTIFY') if align_elem is not None else 'JUSTIFY'
        margin_elem = pp.find('.//hh:margin', NS)
        left = margin_elem.get('left', '0') if margin_elem is not None else '0'
        indent = margin_elem.get('indent', '0') if margin_elem is not None else '0'
        ls_elem = pp.find('.//hh:lineSpacing', NS)
        ls_val = ls_elem.get('value', '160') if ls_elem is not None else '160'
        ls_type = ls_elem.get('type', 'PERCENT') if ls_elem is not None else 'PERCENT'
        result[pp_id] = {
            'align': align,
            'left_margin': left,
            'indent': indent,
            'line_spacing': ls_val,
            'line_spacing_type': ls_type,
        }
    return result


# ══════════════════════════════════════════════
#  secPr (페이지 설정) 추출
# ══════════════════════════════════════════════
def extract_page_setup(hwpx_path):
    """section의 secPr에서 페이지 설정 추출"""
    with zipfile.ZipFile(hwpx_path, 'r') as z:
        sections = sorted([n for n in z.namelist()
                           if n.startswith('Contents/section') and n.endswith('.xml')])
        if not sections:
            return {}
        sec_bytes = z.read(sections[0])
    sec_tree = etree.fromstring(sec_bytes)
    secpr = sec_tree.find('.//hp:secPr', NS)
    if secpr is None:
        return {}
    pg_sz = secpr.find('hp:pageSz', NS)
    pg_margin = secpr.find('hp:pageMargin', NS)
    setup = {}
    if pg_sz is not None:
        setup['width'] = int(pg_sz.get('width', '59528'))
        setup['height'] = int(pg_sz.get('height', '84186'))
    if pg_margin is not None:
        setup['margins'] = {
            'left': int(pg_margin.get('left', '8504')),
            'right': int(pg_margin.get('right', '8504')),
            'top': int(pg_margin.get('top', '5668')),
            'bottom': int(pg_margin.get('bottom', '4252')),
            'header': int(pg_margin.get('header', '4252')),
            'footer': int(pg_margin.get('footer', '4252')),
        }
    return setup


# ══════════════════════════════════════════════
#  역할 자동 추정
# ══════════════════════════════════════════════
def estimate_role_mapping(char_styles, para_styles):
    """charPr/paraPr 조합으로 마크다운 → HWPX 역할 매핑 자동 추정"""
    # 후보 분류
    candidates = {'h1': [], 'h2': [], 'h3': [], 'body': [], 'body_center': [],
                  'caption': [], 'small': []}

    for cid, cs in char_styles.items():
        h = cs['height']
        bold = cs['bold']
        if h >= 2000 and bold:
            candidates['h1'].append((cid, cs))
        elif 1200 <= h < 2000 and bold:
            candidates['h2'].append((cid, cs))
        elif h >= 1200 and not bold:
            candidates['h2'].append((cid, cs))  # 볼드 아닌 대형 글자도 h2 후보
        elif 1000 < h < 1200 and bold:
            candidates['h3'].append((cid, cs))
        elif h == 1000 and not bold:
            candidates['body'].append((cid, cs))
        elif h < 1000:
            candidates['small'].append((cid, cs))

    # 매핑 결정
    mapping = {}

    # h1: 가장 큰 bold charPr + CENTER paraPr
    if candidates['h1']:
        best = max(candidates['h1'], key=lambda x: x[1]['height'])
        center_para = _find_para_by_align(para_styles, 'CENTER', line_spacing_min=150)
        mapping['h1'] = {'charPrIDRef': best[0],
                         'paraPrIDRef': center_para or '0'}
    else:
        # h2 중 가장 큰 것을 h1으로
        if candidates['h2']:
            best = max(candidates['h2'], key=lambda x: x[1]['height'])
            center_para = _find_para_by_align(para_styles, 'CENTER', line_spacing_min=150)
            mapping['h1'] = {'charPrIDRef': best[0],
                             'paraPrIDRef': center_para or '0'}

    # h2: bold + 중간 크기
    h2_pool = [c for c in candidates['h2'] if c[0] != mapping.get('h1', {}).get('charPrIDRef')]
    if h2_pool:
        best = max(h2_pool, key=lambda x: x[1]['height'])
        left_para = _find_para_by_align(para_styles, 'LEFT', line_spacing_min=150)
        mapping['h2'] = {'charPrIDRef': best[0],
                         'paraPrIDRef': left_para or '0'}

    # h3: bold + 소형 또는 body 크기 bold
    if candidates['h3']:
        best = max(candidates['h3'], key=lambda x: x[1]['height'])
        mapping['h3'] = {'charPrIDRef': best[0],
                         'paraPrIDRef': mapping.get('h2', {}).get('paraPrIDRef', '0')}
    else:
        # body 크기 bold가 있으면 h3로
        body_bold = [(cid, cs) for cid, cs in char_styles.items()
                     if cs['height'] == 1000 and cs['bold']]
        if body_bold:
            mapping['h3'] = {'charPrIDRef': body_bold[0][0],
                             'paraPrIDRef': mapping.get('h2', {}).get('paraPrIDRef', '0')}

    # body: 10pt 일반
    if candidates['body']:
        # JUSTIFY paraPr 선호
        justify_para = _find_para_by_align(para_styles, 'JUSTIFY', line_spacing_min=150)
        mapping['body'] = {'charPrIDRef': candidates['body'][0][0],
                           'paraPrIDRef': justify_para or '0'}

    # bullet: body와 같되 들여쓰기 paraPr
    indent_para = _find_para_with_indent(para_styles)
    body_char = mapping.get('body', {}).get('charPrIDRef', '0')
    mapping['bullet'] = {'charPrIDRef': body_char,
                         'paraPrIDRef': indent_para or mapping.get('body', {}).get('paraPrIDRef', '0')}

    # caption: 소형 텍스트
    if candidates['small']:
        best = max(candidates['small'], key=lambda x: x[1]['height'])
        mapping['caption'] = {'charPrIDRef': best[0],
                              'paraPrIDRef': mapping.get('body', {}).get('paraPrIDRef', '0')}

    # blockquote: caption과 동일
    mapping['blockquote'] = mapping.get('caption', mapping.get('body', {}))

    return mapping


def _find_para_by_align(para_styles, align, line_spacing_min=0):
    """특정 정렬의 paraPr 중 줄간격이 min 이상인 첫 번째 id"""
    for pid, ps in para_styles.items():
        if ps['align'] == align and int(ps['line_spacing']) >= line_spacing_min:
            return pid
    return None


def _find_para_with_indent(para_styles):
    """들여쓰기가 있는 paraPr 중 첫 번째 id"""
    for pid, ps in para_styles.items():
        if int(ps['left_margin']) > 0 or int(ps['indent']) > 0:
            return pid
    return None


# ══════════════════════════════════════════════
#  프로필 저장/관리
# ══════════════════════════════════════════════
def load_index():
    """_index.json 로드 (없으면 빈 구조 반환)"""
    if INDEX_FILE.exists():
        with open(INDEX_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"profiles": {}, "default": None}


def save_index(index_data):
    """_index.json 저장"""
    PROFILES_DIR.mkdir(parents=True, exist_ok=True)
    with open(INDEX_FILE, 'w', encoding='utf-8') as f:
        json.dump(index_data, f, ensure_ascii=False, indent=2)


def save_profile(profile_name, hwpx_path, description=""):
    """HWPX에서 스타일을 추출하고 프로필로 저장"""
    profile_dir = PROFILES_DIR / profile_name
    profile_dir.mkdir(parents=True, exist_ok=True)

    # header.xml 추출 + 저장
    with zipfile.ZipFile(hwpx_path, 'r') as z:
        header_bytes = z.read('Contents/header.xml')
        with open(profile_dir / 'header.xml', 'wb') as f:
            f.write(header_bytes)

    header_tree = etree.fromstring(header_bytes)

    # 스타일 추출
    fonts = extract_fonts(header_tree)
    char_styles = extract_char_styles(header_tree, fonts)
    para_styles = extract_para_styles(header_tree)
    page_setup = extract_page_setup(hwpx_path)
    role_mapping = estimate_role_mapping(char_styles, para_styles)

    style_guide = {
        'profile_name': profile_name,
        'source': str(hwpx_path),
        'created': datetime.now().strftime('%Y-%m-%d %H:%M'),
        'description': description,
        'fonts': fonts,
        'char_styles': char_styles,
        'para_styles': para_styles,
        'role_mapping': role_mapping,
        'page_setup': page_setup,
    }

    with open(profile_dir / 'style_guide.json', 'w', encoding='utf-8') as f:
        json.dump(style_guide, f, ensure_ascii=False, indent=2)

    # _index.json 업데이트
    index = load_index()
    index['profiles'][profile_name] = {
        'name': description or profile_name,
        'source': str(hwpx_path),
        'created': style_guide['created'],
        'description': description,
    }
    if index['default'] is None:
        index['default'] = profile_name
    save_index(index)

    return style_guide


def list_profiles():
    """등록된 프로필 목록 출력"""
    index = load_index()
    if not index['profiles']:
        print("등록된 프로필이 없습니다.")
        return
    print(f"{'이름':<15s} {'설명':<30s} {'생성일':<12s} {'기본':>4s}")
    print("-" * 65)
    for name, info in index['profiles'].items():
        is_default = " ★" if name == index.get('default') else ""
        desc = info.get('description', '') or info.get('name', '')
        created = info.get('created', '')[:10]
        print(f"{name:<15s} {desc:<30s} {created:<12s}{is_default}")


def show_profile_info(profile_name):
    """프로필 상세 정보 출력"""
    profile_dir = PROFILES_DIR / profile_name
    sg_path = profile_dir / 'style_guide.json'
    if not sg_path.exists():
        print(f"프로필 '{profile_name}'을 찾을 수 없습니다.")
        return
    with open(sg_path, 'r', encoding='utf-8') as f:
        sg = json.load(f)

    print(f"=== 프로필: {profile_name} ===")
    print(f"  출처: {sg.get('source', '?')}")
    print(f"  생성: {sg.get('created', '?')}")
    print(f"  설명: {sg.get('description', '')}")
    print(f"\n  폰트 수: {len(sg.get('fonts', {}))}")
    print(f"  charPr 수: {len(sg.get('char_styles', {}))}")
    print(f"  paraPr 수: {len(sg.get('para_styles', {}))}")
    print(f"\n  역할 매핑:")
    for role, ids in sg.get('role_mapping', {}).items():
        char_id = ids.get('charPrIDRef', '?')
        para_id = ids.get('paraPrIDRef', '?')
        cs = sg.get('char_styles', {}).get(char_id, {})
        ps = sg.get('para_styles', {}).get(para_id, {})
        print(f"    {role:>12s} → charPr={char_id} ({cs.get('height_pt','')}pt "
              f"{cs.get('font_name','')}"
              f"{' Bold' if cs.get('bold') else ''})"
              f"  paraPr={para_id} ({ps.get('align','')} {ps.get('line_spacing','')}%)")


# ══════════════════════════════════════════════
#  CLI
# ══════════════════════════════════════════════
def main():
    parser = argparse.ArgumentParser(description='HWPX 스타일 프로필 추출기')
    parser.add_argument('--input', help='원본 HWPX 파일 경로')
    parser.add_argument('--profile-name', help='프로필 이름 (snake_case)')
    parser.add_argument('--description', default='', help='프로필 설명')
    parser.add_argument('--list', action='store_true', help='프로필 목록 출력')
    parser.add_argument('--info', help='프로필 상세 정보 출력')

    args = parser.parse_args()

    if args.list:
        list_profiles()
    elif args.info:
        show_profile_info(args.info)
    elif args.input and args.profile_name:
        print(f"[1/3] HWPX 분석: {args.input}")
        sg = save_profile(args.profile_name, args.input, args.description)
        print(f"[2/3] 프로필 저장: profiles/{args.profile_name}/")
        print(f"  charPr: {len(sg['char_styles'])}개")
        print(f"  paraPr: {len(sg['para_styles'])}개")
        print(f"  fonts: {len(sg['fonts'])}개")
        print(f"[3/3] 역할 매핑:")
        for role, ids in sg['role_mapping'].items():
            cs = sg['char_styles'].get(ids['charPrIDRef'], {})
            print(f"  {role:>12s} → charPr={ids['charPrIDRef']} "
                  f"({cs.get('height_pt','')}pt {cs.get('font_name','')})"
                  f"  paraPr={ids['paraPrIDRef']}")
        print(f"\n[OK] 프로필 '{args.profile_name}' 생성 완료")
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
