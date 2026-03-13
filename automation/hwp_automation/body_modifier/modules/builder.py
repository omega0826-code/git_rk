# -*- coding: utf-8 -*-
"""
builder.py - HWPX 빌드 모듈

수정된 header.xml과 section XML을 원본 HWPX 리소스와 합성하여
새로운 HWPX 파일(ZIP)을 생성합니다.

핵심 기능:
  - charPr 동적 추가 (deepcopy + 속성 오버라이딩)
  - mimetype ZIP_STORED 보장
  - 원본 리소스 보존 (수정 대상만 교체)

사용법 (모듈 import):
    from modules.builder import build_hwpx
    build_hwpx(input_path, output_path, modified_files)
"""
import zipfile, copy
from lxml import etree

import sys
sys.path.insert(0, '..')
from config.namespaces import NS


def add_charpr_style(header_bytes, base_id, changes):
    """header.xml에 새 charPr을 추가

    기존 charPr(base_id)을 deepcopy한 뒤 changes 속성만 오버라이딩합니다.
    itemCnt를 자동 갱신합니다.

    Args:
        header_bytes: header.xml 바이트
        base_id: 복사할 기존 charPr id (str)
        changes: 변경할 속성 dict (예: {'textColor': '#FF0000'})

    Returns:
        tuple: (수정된 header_bytes, 새로운 charPr id(str))
    """
    tree = etree.fromstring(header_bytes)
    char_props = tree.find('.//hh:charProperties', NS)

    if char_props is None:
        raise ValueError("header.xml에 charProperties가 없습니다")

    current_cnt = int(char_props.get('itemCnt', '0'))
    new_id = str(current_cnt)

    # base charPr 찾기
    base_cp = None
    for cp in char_props.findall('hh:charPr', NS):
        if cp.get('id') == base_id:
            base_cp = cp
            break

    if base_cp is None:
        raise ValueError(f"charPr id={base_id}를 찾을 수 없습니다")

    # deepcopy 후 속성 변경
    new_cp = copy.deepcopy(base_cp)
    new_cp.set('id', new_id)
    for attr, value in changes.items():
        new_cp.set(attr, value)

    char_props.append(new_cp)
    char_props.set('itemCnt', str(current_cnt + 1))

    modified_bytes = etree.tostring(tree, xml_declaration=True, encoding='UTF-8', standalone=True)
    return modified_bytes, new_id


def build_hwpx(input_path, output_path, modified_files):
    """수정된 파일들로 새 HWPX를 빌드

    Args:
        input_path: 원본 HWPX 경로
        output_path: 출력 HWPX 경로
        modified_files: {entry_name: bytes} - 수정된 파일들만 전달
            예: {'Contents/header.xml': b'...', 'Contents/section1.xml': b'...'}
    """
    # 원본 모든 파일 로드
    with zipfile.ZipFile(input_path, 'r') as zin:
        file_list = zin.namelist()
        file_data = {}
        for name in file_list:
            file_data[name] = zin.read(name)

    # 수정된 파일 교체
    for name, data in modified_files.items():
        if name in file_data:
            file_data[name] = data

    # 새 HWPX 저장 (mimetype은 ZIP_STORED)
    with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zout:
        for name in file_list:
            if name == 'mimetype':
                zout.writestr(name, file_data[name], compress_type=zipfile.ZIP_STORED)
            else:
                zout.writestr(name, file_data[name])
