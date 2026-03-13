# -*- coding: utf-8 -*-
"""
modifier.py - 본문 수정 모듈

JSON 수정 사양(spec)을 기반으로 section XML의 DOM 트리를 수정합니다.

지원 수정 유형:
  A. insert_after  - 매칭 문단 뒤에 새 문단 삽입
  B. replace_text  - 매칭 문단의 텍스트 교체
  C. change_style  - 매칭 문단의 charPrIDRef 변경
  D. delete_para   - 매칭 문단 삭제

지원 매칭 전략:
  - startswith  : 문단 텍스트가 특정 문자열로 시작
  - contains    : 문단 텍스트에 특정 문자열 포함
  - regex       : 정규식 매칭

사용법 (모듈 import):
    from modules.modifier import apply_modifications
    modified_xml = apply_modifications(section_bytes, spec, new_charpr_id="66")
"""
import re, copy
from lxml import etree

import sys
sys.path.insert(0, '..')
from config.namespaces import NS


def get_para_text(p_elem):
    """문단 요소에서 전체 텍스트 추출"""
    texts = []
    for run in p_elem.findall('.//hp:run', NS):
        for t in run.findall('hp:t', NS):
            if t.text:
                texts.append(t.text)
    return ''.join(texts).strip()


def match_paragraph(text, rule):
    """매칭 규칙에 따라 텍스트가 해당하는지 판단

    Args:
        text: 문단 텍스트
        rule: {'strategy': 'startswith'|'contains'|'regex', 'pattern': str}

    Returns:
        bool
    """
    strategy = rule.get('strategy', 'startswith')
    pattern = rule.get('pattern', '')

    if strategy == 'startswith':
        return text.startswith(pattern)
    elif strategy == 'contains':
        return pattern in text
    elif strategy == 'regex':
        return bool(re.search(pattern, text))
    return False


def make_new_para(parent_para, text, charpr_id, ns_map):
    """기존 문단을 기반으로 새 문단 요소를 생성

    Args:
        parent_para: 참조할 기존 문단 요소 (paraPrIDRef, styleIDRef 복사)
        text: 삽입할 텍스트
        charpr_id: 적용할 charPr id (예: "66" 빨간색)
        ns_map: XML 네임스페이스 매핑

    Returns:
        새 lxml Element
    """
    new_p = etree.Element('{http://www.hancom.co.kr/hwpml/2011/paragraph}p', nsmap=ns_map)
    new_p.set('paraPrIDRef', parent_para.get('paraPrIDRef', '22'))
    new_p.set('styleIDRef', parent_para.get('styleIDRef', '0'))
    new_p.set('pageBreak', '0')
    new_p.set('columnBreak', '0')
    new_p.set('merged', '0')

    run = etree.SubElement(new_p, '{http://www.hancom.co.kr/hwpml/2011/paragraph}run')
    run.set('charPrIDRef', charpr_id)

    t = etree.SubElement(run, '{http://www.hancom.co.kr/hwpml/2011/paragraph}t')
    t.text = text

    return new_p


def apply_modifications(section_bytes, rules, new_charpr_id="66"):
    """수정 규칙을 section XML에 적용

    Args:
        section_bytes: section XML 바이트
        rules: 수정 규칙 리스트
            각 규칙: {
                'action': 'insert_after' | 'replace_text' | 'change_style' | 'delete_para',
                'strategy': 'startswith' | 'contains' | 'regex',
                'pattern': str,
                'text': str (insert_after/replace_text용),
                'charpr_id': str (change_style용, 생략 시 new_charpr_id 사용),
            }
        new_charpr_id: 기본 charPr id (삽입 시 적용)

    Returns:
        bytes: 수정된 section XML
    """
    tree = etree.fromstring(section_bytes)
    ns_map = tree.nsmap

    # 직접 자식 <hp:p>만 대상 (테이블 내부 제외)
    children = list(tree)
    insert_ops = []

    for i, child in enumerate(children):
        tag = etree.QName(child.tag).localname if isinstance(child.tag, str) else ''
        if tag != 'p':
            continue

        text = get_para_text(child)
        if not text:
            continue

        for rule in rules:
            if not match_paragraph(text, rule):
                continue

            action = rule.get('action', 'insert_after')

            if action == 'insert_after':
                insert_ops.append(('insert', child, rule.get('text', ''),
                                   rule.get('charpr_id', new_charpr_id)))

            elif action == 'replace_text':
                # run 내 <hp:t> 텍스트 교체
                for run in child.findall('.//hp:run', NS):
                    for t in run.findall('hp:t', NS):
                        t.text = rule.get('text', '')
                    break  # 첫 번째 run만 교체

            elif action == 'change_style':
                for run in child.findall('.//hp:run', NS):
                    run.set('charPrIDRef', rule.get('charpr_id', new_charpr_id))

            elif action == 'delete_para':
                tree.remove(child)

            break  # 한 문단에 하나의 규칙만 적용

    # 삽입은 역순 처리 (인덱스 밀림 방지)
    for action_type, para, ins_text, charpr_id in reversed(insert_ops):
        new_para = make_new_para(para, ins_text, charpr_id, ns_map)
        parent = para.getparent()
        para_idx = list(parent).index(para)
        parent.insert(para_idx + 1, new_para)

    return etree.tostring(tree, xml_declaration=True, encoding='UTF-8', standalone=True)
