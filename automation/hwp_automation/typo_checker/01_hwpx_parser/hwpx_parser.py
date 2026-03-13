"""
HWPX 파서 v1.0
- HWPX 파일(ZIP 기반 XML 패키지)에서 텍스트, 표, 이미지, 제목을 추출한다.
- 출력: Markdown, Plain Text, CSV, Excel, JSON, 이미지 파일

사용법:
    python hwpx_parser.py <hwpx_파일_경로> [옵션]

옵션:
    --text-only         텍스트만 추출
    --tables-only       표만 추출
    --count-tables      표 개수만 출력
    --extract-table N   N번째 표만 추출
    --output FILE       출력 파일 지정 (CSV/Excel)
    --all               전체 추출 (기본값)
"""

import os
import re
import sys
import json
import zipfile
import argparse
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Tuple, Any

# --- 의존성 체크 ---
try:
    from lxml import etree
except ImportError:
    print("[ERROR] lxml이 설치되어 있지 않습니다. pip install lxml 을 실행하세요.")
    sys.exit(1)

try:
    import pandas as pd
except ImportError:
    pd = None
    print("[WARNING] pandas가 없습니다. DataFrame/Excel 출력이 비활성화됩니다.")

try:
    import openpyxl
except ImportError:
    openpyxl = None
    if pd:
        print("[WARNING] openpyxl이 없습니다. Excel 출력이 비활성화됩니다.")


# ============================================================
# 네임스페이스 정의
# ============================================================
NS = {
    'hp': 'http://www.hancom.co.kr/hwpml/2011/paragraph',
    'hs': 'http://www.hancom.co.kr/hwpml/2011/section',
    'hc': 'http://www.hancom.co.kr/hwpml/2011/core',
    'hh': 'http://www.hancom.co.kr/hwpml/2011/head',
    'ha': 'http://www.hancom.co.kr/hwpml/2011/app',
}

# 네임스페이스 전체 URI 생성 헬퍼
def _tag(ns_prefix: str, local_name: str) -> str:
    """네임스페이스 접두사와 로컬 이름으로 전체 태그명을 생성한다."""
    return f'{{{NS[ns_prefix]}}}{local_name}'


# ============================================================
# 파일명 sanitize
# ============================================================
def sanitize_filename(name: str, max_len: int = 50) -> str:
    """파일명에 사용할 수 없는 특수문자를 _로 치환한다."""
    name = re.sub(r'[/\\:*?"<>|]', '_', name)
    name = name.replace(' ', '_')
    name = re.sub(r'_+', '_', name)  # 연속 _ 제거
    name = name.strip('_')
    if len(name) > max_len:
        name = name[:max_len]
    return name


# ============================================================
# 로깅 설정
# ============================================================
def setup_logger(log_file: Optional[str] = None) -> logging.Logger:
    """로깅을 설정한다."""
    logger = logging.getLogger('hwpx_parser')
    logger.setLevel(logging.DEBUG)
    
    formatter = logging.Formatter('[%(asctime)s] %(levelname)s: %(message)s',
                                  datefmt='%H:%M:%S')
    
    # 콘솔 핸들러
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.INFO)
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    
    # 파일 핸들러
    if log_file:
        fh = logging.FileHandler(log_file, encoding='utf-8')
        fh.setLevel(logging.DEBUG)
        fh.setFormatter(formatter)
        logger.addHandler(fh)
    
    return logger


# ============================================================
# HwpxReader: ZIP 해제 + XML 로드
# ============================================================
class HwpxReader:
    """HWPX 파일을 열고 내부 XML을 읽는다."""
    
    def __init__(self, hwpx_path: str):
        self.hwpx_path = Path(hwpx_path)
        if not self.hwpx_path.exists():
            raise FileNotFoundError(f"파일을 찾을 수 없습니다: {hwpx_path}")
        if not zipfile.is_zipfile(str(self.hwpx_path)):
            raise ValueError(f"유효한 HWPX(ZIP) 파일이 아닙니다: {hwpx_path}")
        
        self.zip_file = zipfile.ZipFile(str(self.hwpx_path), 'r')
        self._file_list = self.zip_file.namelist()
    
    def close(self):
        """ZIP 파일을 닫는다."""
        if self.zip_file:
            self.zip_file.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
    
    def get_file_list(self) -> List[str]:
        """HWPX 내부 파일 목록을 반환한다."""
        return self._file_list
    
    def read_xml(self, internal_path: str) -> Optional[etree._Element]:
        """내부 XML 파일을 파싱하여 Element를 반환한다."""
        if internal_path not in self._file_list:
            return None
        data = self.zip_file.read(internal_path)
        return etree.fromstring(data)
    
    def read_binary(self, internal_path: str) -> Optional[bytes]:
        """내부 바이너리 파일을 읽는다."""
        if internal_path not in self._file_list:
            return None
        return self.zip_file.read(internal_path)
    
    def get_section_roots(self) -> List[etree._Element]:
        """모든 section XML을 파싱하여 반환한다."""
        sections = []
        for name in sorted(self._file_list):
            if re.match(r'Contents/section\d+\.xml', name):
                root = self.read_xml(name)
                if root is not None:
                    sections.append(root)
        return sections
    
    def get_header(self) -> Optional[etree._Element]:
        """header.xml을 파싱하여 반환한다."""
        return self.read_xml('Contents/header.xml')
    
    def get_bin_data_list(self) -> List[str]:
        """BinData/ 폴더 내 파일 목록을 반환한다."""
        return [f for f in self._file_list if f.startswith('BinData/')]


# ============================================================
# TextExtractor: 텍스트 추출
# ============================================================
class TextExtractor:
    """section XML에서 텍스트를 추출한다."""
    
    @staticmethod
    def extract_paragraph_text(p_elem) -> str:
        """하나의 hp:p 요소에서 텍스트를 추출한다."""
        texts = []
        for t in p_elem.iter(_tag('hp', 't')):
            # titleMark 등 자식 요소의 tail은 무시
            if t.text:
                texts.append(t.text)
        return ''.join(texts).strip()
    
    @staticmethod
    def is_in_table(p_elem) -> bool:
        """문단이 표 내부에 있는지 확인한다."""
        parent = p_elem.getparent()
        while parent is not None:
            if parent.tag == _tag('hp', 'tbl'):
                return True
            parent = parent.getparent()
        return False
    
    @staticmethod
    def is_in_header_footer(p_elem) -> bool:
        """문단이 머리말/꼬리말 내부에 있는지 확인한다."""
        parent = p_elem.getparent()
        while parent is not None:
            tag = parent.tag
            if tag in (_tag('hp', 'header'), _tag('hp', 'footer')):
                return True
            parent = parent.getparent()
        return False
    
    def extract_all(self, root, include_tables: bool = False,
                    include_header_footer: bool = False) -> List[str]:
        """전체 텍스트를 추출한다."""
        paragraphs = []
        for p in root.iter(_tag('hp', 'p')):
            if not include_tables and self.is_in_table(p):
                continue
            if not include_header_footer and self.is_in_header_footer(p):
                continue
            text = self.extract_paragraph_text(p)
            if text:
                paragraphs.append(text)
        return paragraphs
    
    def extract_by_heading(self, root, headings: List[Dict]) -> Dict[str, List[str]]:
        """제목별로 섹션을 분리하여 텍스트를 추출한다."""
        sections = {}
        current_heading = "서두"
        current_texts = []
        
        heading_texts = {h['text'] for h in headings}
        
        for p in root.iter(_tag('hp', 'p')):
            if self.is_in_table(p) or self.is_in_header_footer(p):
                continue
            text = self.extract_paragraph_text(p)
            if not text:
                continue
            
            if text in heading_texts:
                sections[current_heading] = current_texts
                current_heading = text
                current_texts = []
            else:
                current_texts.append(text)
        
        sections[current_heading] = current_texts
        return sections


# ============================================================
# HeadingDetector: 제목 감지
# ============================================================
class HeadingDetector:
    """titleMark와 styleIDRef를 기반으로 제목을 감지한다."""
    
    # styleIDRef → Markdown 헤딩 레벨 매핑
    STYLE_LEVEL_MAP = {
        '1': 1,   # 개요 1
        '2': 2,   # 개요 2
        '3': 3,   # 개요 3
        '4': 4,   # 개요 4
        '5': 5,   # 개요 5
        '6': 6,   # 개요 6
    }
    
    @staticmethod
    def detect(root) -> List[Dict[str, Any]]:
        """titleMark가 있는 문단을 제목으로 식별한다."""
        headings = []
        for p in root.iter(_tag('hp', 'p')):
            has_title = p.find(f'.//{_tag("hp", "titleMark")}') is not None
            if has_title:
                style_id = p.get('styleIDRef', '0')
                texts = []
                for t in p.iter(_tag('hp', 't')):
                    if t.text:
                        texts.append(t.text)
                heading_text = ''.join(texts).strip()
                if heading_text:
                    level = HeadingDetector.STYLE_LEVEL_MAP.get(style_id, 
                            int(style_id) if style_id.isdigit() else 1)
                    headings.append({
                        'level': level,
                        'styleIDRef': style_id,
                        'text': heading_text
                    })
        return headings


# ============================================================
# TableExtractor: 표 추출 (셀 병합 처리 포함)
# ============================================================
class TableExtractor:
    """section XML에서 표를 추출한다."""
    
    @staticmethod
    def _is_body_table(tbl_elem) -> bool:
        """본문 표인지 확인한다 (머리말/꼬리말 내부 표 제외)."""
        parent = tbl_elem.getparent()
        while parent is not None:
            tag = parent.tag
            if tag in (_tag('hp', 'header'), _tag('hp', 'footer')):
                return False
            parent = parent.getparent()
        return True
    
    @staticmethod
    def _get_cell_text(tc_elem) -> str:
        """셀 내 텍스트를 추출한다."""
        texts = []
        for t in tc_elem.iter(_tag('hp', 't')):
            if t.text:
                texts.append(t.text)
        return ' '.join(texts).strip()
    
    @staticmethod
    def _guess_table_title(tbl_elem, text_extractor: TextExtractor) -> str:
        """표 바로 위 문단에서 표 제목을 추측한다."""
        prev = tbl_elem.getparent()
        if prev is None:
            return ""
        
        # 표를 포함하는 hp:p의 이전 형제 요소에서 텍스트를 찾음
        parent_p = tbl_elem.getparent()
        if parent_p is not None and parent_p.tag == _tag('hp', 'p'):
            prev_sibling = parent_p.getprevious()
            if prev_sibling is not None and prev_sibling.tag == _tag('hp', 'p'):
                text = text_extractor.extract_paragraph_text(prev_sibling)
                if text:
                    return text
        return ""
    
    def extract_all(self, root, body_only: bool = True) -> List[Dict[str, Any]]:
        """모든 표를 추출한다."""
        tables = []
        text_ext = TextExtractor()
        table_idx = 0
        
        for tbl in root.iter(_tag('hp', 'tbl')):
            if body_only and not self._is_body_table(tbl):
                continue
            
            row_cnt = int(tbl.get('rowCnt', 0))
            col_cnt = int(tbl.get('colCnt', 0))
            
            if row_cnt == 0 or col_cnt == 0:
                continue
            
            # 2D 그리드 초기화
            grid = [['' for _ in range(col_cnt)] for _ in range(row_cnt)]
            occupied = [[False] * col_cnt for _ in range(row_cnt)]
            
            for tc in tbl.iter(_tag('hp', 'tc')):
                addr = tc.find(_tag('hp', 'cellAddr'))
                span = tc.find(_tag('hp', 'cellSpan'))
                
                if addr is None or span is None:
                    continue
                
                col = int(addr.get('colAddr', 0))
                row = int(addr.get('rowAddr', 0))
                cs = int(span.get('colSpan', 1))
                rs = int(span.get('rowSpan', 1))
                
                cell_value = self._get_cell_text(tc)
                
                # 병합 영역에 값 배치
                for r in range(row, min(row + rs, row_cnt)):
                    for c in range(col, min(col + cs, col_cnt)):
                        if 0 <= r < row_cnt and 0 <= c < col_cnt:
                            if not occupied[r][c]:
                                grid[r][c] = cell_value if (r == row and c == col) else ''
                                occupied[r][c] = True
            
            # 표 제목 추측
            title = self._guess_table_title(tbl, text_ext)
            
            table_idx += 1
            tables.append({
                'index': table_idx,
                'title': title,
                'rows': row_cnt,
                'cols': col_cnt,
                'grid': grid,
            })
        
        return tables
    
    @staticmethod
    def to_dataframe(table_data: Dict) -> Any:
        """표 데이터를 pandas DataFrame으로 변환한다."""
        if pd is None:
            raise ImportError("pandas가 설치되어 있지 않습니다.")
        
        grid = table_data['grid']
        if len(grid) < 2:
            return pd.DataFrame(grid)
        
        # 첫 행을 헤더로 사용
        headers = grid[0]
        data = grid[1:]
        return pd.DataFrame(data, columns=headers)


# ============================================================
# ImageExtractor: 이미지 추출
# ============================================================
class ImageExtractor:
    """HWPX 내부 이미지를 추출한다."""
    
    @staticmethod
    def extract_image_refs(root) -> List[Dict[str, str]]:
        """section XML에서 이미지 참조 목록을 추출한다."""
        images = []
        idx = 0
        for pic in root.iter(_tag('hp', 'pic')):
            img = pic.find(f'.//{_tag("hc", "img")}')
            if img is not None:
                idx += 1
                ref = img.get('binaryItemIDRef', '')
                comment_elem = pic.find(_tag('hp', 'shapeComment'))
                comment = comment_elem.text if comment_elem is not None and comment_elem.text else ''
                images.append({
                    'index': idx,
                    'binaryItemIDRef': ref,
                    'comment': comment,
                })
        return images
    
    @staticmethod
    def extract_images(reader: HwpxReader, image_refs: List[Dict], 
                       output_dir: str) -> List[str]:
        """이미지 파일을 output_dir에 저장한다."""
        saved = []
        bin_data_list = reader.get_bin_data_list()
        
        # binaryItemIDRef → BinData/ 실제 경로 매핑
        ref_to_path = {}
        for bin_path in bin_data_list:
            # BinData/image1.bmp → image1
            basename = os.path.splitext(os.path.basename(bin_path))[0]
            ref_to_path[basename] = bin_path
        
        os.makedirs(output_dir, exist_ok=True)
        
        for img_info in image_refs:
            ref = img_info['binaryItemIDRef']
            if ref in ref_to_path:
                src_path = ref_to_path[ref]
                ext = os.path.splitext(src_path)[1]
                out_name = f"image_{img_info['index']:02d}{ext}"
                out_path = os.path.join(output_dir, out_name)
                
                data = reader.read_binary(src_path)
                if data:
                    with open(out_path, 'wb') as f:
                        f.write(data)
                    saved.append(out_name)
        
        return saved


# ============================================================
# OutputWriter: 결과물 저장
# ============================================================
class OutputWriter:
    """파싱 결과를 다양한 형식으로 저장한다."""
    
    def __init__(self, output_dir: str):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.tables_dir = self.output_dir / 'tables'
        self.tables_dir.mkdir(exist_ok=True)
        self.images_dir = self.output_dir / 'images'
        self.images_dir.mkdir(exist_ok=True)
    
    def write_full_text_md(self, paragraphs: List[str], 
                           headings: List[Dict],
                           tables: List[Dict]) -> str:
        """전체 텍스트를 Markdown으로 저장한다."""
        out_path = self.output_dir / 'full_text.md'
        heading_texts = {h['text']: h['level'] for h in headings}
        
        lines = []
        for para in paragraphs:
            if para in heading_texts:
                level = heading_texts[para]
                lines.append(f"\n{'#' * level} {para}\n")
            else:
                lines.append(para)
                lines.append('')
        
        with open(out_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))
        return str(out_path)
    
    def write_full_text_txt(self, paragraphs: List[str]) -> str:
        """전체 텍스트를 Plain Text로 저장한다."""
        out_path = self.output_dir / 'full_text.txt'
        with open(out_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(paragraphs))
        return str(out_path)
    
    def write_headings_json(self, headings: List[Dict]) -> str:
        """제목 구조를 JSON으로 저장한다."""
        out_path = self.output_dir / 'headings.json'
        with open(out_path, 'w', encoding='utf-8') as f:
            json.dump(headings, f, ensure_ascii=False, indent=2)
        return str(out_path)
    
    def write_table_csv(self, table: Dict, index: int) -> str:
        """표 하나를 CSV로 저장한다."""
        title = table.get('title', '')
        safe_title = sanitize_filename(title) if title else f'table_{index:02d}'
        filename = f"table_{index:02d}_{safe_title}.csv" if title else f"table_{index:02d}.csv"
        out_path = self.tables_dir / filename
        
        with open(out_path, 'w', encoding='utf-8-sig', newline='') as f:
            import csv
            writer = csv.writer(f)
            for row in table['grid']:
                writer.writerow(row)
        return str(out_path)
    
    def write_all_tables_csv(self, tables: List[Dict]) -> List[str]:
        """모든 표를 개별 CSV로 저장한다."""
        paths = []
        for table in tables:
            path = self.write_table_csv(table, table['index'])
            paths.append(path)
        return paths
    
    def write_all_tables_excel(self, tables: List[Dict]) -> Optional[str]:
        """모든 표를 하나의 Excel 파일(시트별)로 저장한다."""
        if pd is None or openpyxl is None:
            return None
        
        out_path = self.tables_dir / 'all_tables.xlsx'
        
        with pd.ExcelWriter(str(out_path), engine='openpyxl') as writer:
            for table in tables:
                title = table.get('title', '')
                safe_title = sanitize_filename(title, max_len=30) if title else ''
                sheet_name = f"표{table['index']}_{safe_title}" if safe_title else f"표{table['index']}"
                sheet_name = sheet_name[:31]  # Excel 시트명 31자 제한
                
                grid = table['grid']
                if len(grid) >= 2:
                    df = pd.DataFrame(grid[1:], columns=grid[0])
                else:
                    df = pd.DataFrame(grid)
                
                df.to_excel(writer, sheet_name=sheet_name, index=False)
        
        return str(out_path)
    
    def write_parse_log(self, log_data: Dict) -> str:
        """파싱 로그를 저장한다."""
        out_path = self.output_dir / 'parse_log.txt'
        with open(out_path, 'w', encoding='utf-8') as f:
            f.write(f"HWPX 파싱 로그\n")
            f.write(f"{'='*50}\n")
            f.write(f"입력 파일: {log_data.get('input_file', 'N/A')}\n")
            f.write(f"파싱 시작: {log_data.get('start_time', 'N/A')}\n")
            f.write(f"파싱 완료: {log_data.get('end_time', 'N/A')}\n")
            f.write(f"{'='*50}\n\n")
            f.write(f"[추출 요약]\n")
            f.write(f"  섹션 수: {log_data.get('section_count', 0)}\n")
            f.write(f"  문단 수: {log_data.get('paragraph_count', 0)}\n")
            f.write(f"  제목 수: {log_data.get('heading_count', 0)}\n")
            f.write(f"  표 수:   {log_data.get('table_count', 0)}\n")
            f.write(f"  이미지 수: {log_data.get('image_count', 0)}\n\n")
            
            if 'tables' in log_data:
                f.write(f"[표 상세]\n")
                for t in log_data['tables']:
                    f.write(f"  표 {t['index']}: {t['rows']}행 × {t['cols']}열")
                    if t.get('title'):
                        f.write(f" - \"{t['title'][:50]}\"")
                    f.write('\n')
            
            if 'images' in log_data:
                f.write(f"\n[이미지 상세]\n")
                for img in log_data['images']:
                    f.write(f"  {img['index']:02d}: {img['binaryItemIDRef']}")
                    if img.get('comment'):
                        f.write(f" ({img['comment'][:40]})")
                    f.write('\n')
            
            if 'errors' in log_data and log_data['errors']:
                f.write(f"\n[오류]\n")
                for err in log_data['errors']:
                    f.write(f"  - {err}\n")
        
        return str(out_path)


# ============================================================
# 메인 파싱 함수
# ============================================================
def parse_hwpx(hwpx_path: str, output_base: Optional[str] = None) -> Dict[str, Any]:
    """
    HWPX 파일을 파싱하여 결과를 저장한다.
    
    Returns:
        파싱 결과 딕셔너리 (paragraphs, headings, tables, images, output_dir 등)
    """
    start_time = datetime.now()
    errors = []
    
    hwpx_path = Path(hwpx_path)
    
    # 출력 디렉토리 생성
    if output_base is None:
        output_base = hwpx_path.parent / 'hwpx_parsed'
    else:
        output_base = Path(output_base)
    
    timestamp = start_time.strftime('%Y%m%d_%H%M')
    stem = hwpx_path.stem
    output_dir = output_base / f"{stem}_{timestamp}"
    
    # 로거 설정
    output_dir.mkdir(parents=True, exist_ok=True)
    logger = setup_logger(str(output_dir / 'parse_log.txt'))
    
    logger.info(f"파싱 시작: {hwpx_path}")
    
    result = {
        'input_file': str(hwpx_path),
        'output_dir': str(output_dir),
        'paragraphs': [],
        'headings': [],
        'tables': [],
        'image_refs': [],
        'saved_images': [],
    }
    
    with HwpxReader(str(hwpx_path)) as reader:
        # 섹션 로드
        sections = reader.get_section_roots()
        logger.info(f"섹션 수: {len(sections)}")
        
        text_ext = TextExtractor()
        heading_det = HeadingDetector()
        table_ext = TableExtractor()
        img_ext = ImageExtractor()
        
        all_paragraphs = []
        all_headings = []
        all_tables = []
        all_image_refs = []
        
        for sec_idx, root in enumerate(sections):
            logger.info(f"  section{sec_idx} 파싱 중...")
            
            try:
                # 1. 제목 감지
                headings = heading_det.detect(root)
                all_headings.extend(headings)
                logger.info(f"    제목: {len(headings)}개")
                
                # 2. 텍스트 추출
                paragraphs = text_ext.extract_all(root, 
                                                   include_tables=False,
                                                   include_header_footer=False)
                all_paragraphs.extend(paragraphs)
                logger.info(f"    문단: {len(paragraphs)}개")
                
                # 3. 표 추출
                tables = table_ext.extract_all(root, body_only=True)
                all_tables.extend(tables)
                logger.info(f"    표: {len(tables)}개")
                
                # 4. 이미지 참조 추출
                image_refs = img_ext.extract_image_refs(root)
                all_image_refs.extend(image_refs)
                logger.info(f"    이미지: {len(image_refs)}개")
                
            except Exception as e:
                err_msg = f"section{sec_idx} 파싱 오류: {str(e)}"
                logger.error(err_msg)
                errors.append(err_msg)
        
        # 5. 이미지 파일 추출
        writer = OutputWriter(str(output_dir))
        
        if all_image_refs:
            try:
                saved = img_ext.extract_images(reader, all_image_refs,
                                               str(writer.images_dir))
                result['saved_images'] = saved
                logger.info(f"이미지 저장: {len(saved)}개")
            except Exception as e:
                err_msg = f"이미지 추출 오류: {str(e)}"
                logger.error(err_msg)
                errors.append(err_msg)
    
    # 6. 결과 저장
    result['paragraphs'] = all_paragraphs
    result['headings'] = all_headings
    result['tables'] = all_tables
    result['image_refs'] = all_image_refs
    
    # Markdown 텍스트
    try:
        md_path = writer.write_full_text_md(all_paragraphs, all_headings, all_tables)
        logger.info(f"Markdown 저장: {md_path}")
    except Exception as e:
        errors.append(f"Markdown 저장 오류: {e}")
    
    # Plain Text
    try:
        txt_path = writer.write_full_text_txt(all_paragraphs)
        logger.info(f"Plain Text 저장: {txt_path}")
    except Exception as e:
        errors.append(f"Plain Text 저장 오류: {e}")
    
    # 제목 구조 JSON
    try:
        json_path = writer.write_headings_json(all_headings)
        logger.info(f"Headings JSON 저장: {json_path}")
    except Exception as e:
        errors.append(f"Headings JSON 저장 오류: {e}")
    
    # 표 CSV
    try:
        csv_paths = writer.write_all_tables_csv(all_tables)
        logger.info(f"표 CSV 저장: {len(csv_paths)}개")
    except Exception as e:
        errors.append(f"CSV 저장 오류: {e}")
    
    # 표 Excel
    try:
        xlsx_path = writer.write_all_tables_excel(all_tables)
        if xlsx_path:
            logger.info(f"표 Excel 저장: {xlsx_path}")
        else:
            logger.warning("Excel 출력 건너뜀 (pandas/openpyxl 미설치)")
    except Exception as e:
        errors.append(f"Excel 저장 오류: {e}")
    
    end_time = datetime.now()
    elapsed = (end_time - start_time).total_seconds()
    
    # 파싱 로그 저장
    log_data = {
        'input_file': str(hwpx_path),
        'start_time': start_time.strftime('%Y-%m-%d %H:%M:%S'),
        'end_time': end_time.strftime('%Y-%m-%d %H:%M:%S'),
        'section_count': len(sections),
        'paragraph_count': len(all_paragraphs),
        'heading_count': len(all_headings),
        'table_count': len(all_tables),
        'image_count': len(all_image_refs),
        'tables': [{'index': t['index'], 'rows': t['rows'], 
                     'cols': t['cols'], 'title': t['title']} for t in all_tables],
        'images': all_image_refs,
        'errors': errors,
    }
    writer.write_parse_log(log_data)
    
    logger.info(f"파싱 완료 ({elapsed:.1f}초)")
    logger.info(f"출력 디렉토리: {output_dir}")
    
    if errors:
        logger.warning(f"오류 {len(errors)}건 발생")
        for e in errors:
            logger.warning(f"  - {e}")
    
    result['errors'] = errors
    result['elapsed_seconds'] = elapsed
    
    return result


# ============================================================
# CLI 인터페이스
# ============================================================
def main():
    parser = argparse.ArgumentParser(
        description='HWPX 파서 - HWPX 파일에서 텍스트, 표, 이미지를 추출합니다.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
사용 예시:
  python hwpx_parser.py sample.hwpx                  # 전체 추출
  python hwpx_parser.py sample.hwpx --text-only       # 텍스트만 출력
  python hwpx_parser.py sample.hwpx --count-tables    # 표 개수 확인
  python hwpx_parser.py sample.hwpx --extract-table 1 # 1번 표 추출
        """
    )
    parser.add_argument('hwpx_file', help='HWPX 파일 경로')
    parser.add_argument('--text-only', action='store_true', help='텍스트만 추출하여 출력')
    parser.add_argument('--tables-only', action='store_true', help='표만 추출')
    parser.add_argument('--count-tables', action='store_true', help='표 개수만 출력')
    parser.add_argument('--extract-table', type=int, metavar='N', help='N번째 표만 추출 (1부터)')
    parser.add_argument('--output', metavar='FILE', help='출력 파일 경로 (CSV)')
    parser.add_argument('--output-dir', metavar='DIR', help='출력 디렉토리 (기본: hwpx_parsed/)')
    parser.add_argument('--all', action='store_true', default=True, help='전체 추출 (기본)')
    
    args = parser.parse_args()
    
    # 간단 모드: 표 개수만
    if args.count_tables:
        with HwpxReader(args.hwpx_file) as reader:
            sections = reader.get_section_roots()
            ext = TableExtractor()
            total = 0
            for root in sections:
                tables = ext.extract_all(root)
                total += len(tables)
            print(f"표 개수: {total}")
        return
    
    # 간단 모드: 텍스트만
    if args.text_only:
        with HwpxReader(args.hwpx_file) as reader:
            sections = reader.get_section_roots()
            ext = TextExtractor()
            for root in sections:
                paragraphs = ext.extract_all(root)
                for p in paragraphs:
                    print(p)
        return
    
    # 간단 모드: 특정 표 추출
    if args.extract_table is not None:
        with HwpxReader(args.hwpx_file) as reader:
            sections = reader.get_section_roots()
            ext = TableExtractor()
            all_tables = []
            for root in sections:
                all_tables.extend(ext.extract_all(root))
            
            idx = args.extract_table - 1
            if 0 <= idx < len(all_tables):
                table = all_tables[idx]
                if args.output:
                    import csv
                    with open(args.output, 'w', encoding='utf-8-sig', newline='') as f:
                        writer = csv.writer(f)
                        for row in table['grid']:
                            writer.writerow(row)
                    print(f"표 {args.extract_table} → {args.output}")
                else:
                    for row in table['grid']:
                        print('\t'.join(row))
            else:
                print(f"[ERROR] 표 번호 {args.extract_table}이 범위 밖입니다 (총 {len(all_tables)}개)")
        return
    
    # 전체 추출 모드
    result = parse_hwpx(args.hwpx_file, output_base=args.output_dir)
    
    print(f"\n{'='*50}")
    print(f"HWPX 파싱 완료")
    print(f"{'='*50}")
    print(f"입력: {result['input_file']}")
    print(f"출력: {result['output_dir']}")
    print(f"소요: {result['elapsed_seconds']:.1f}초")
    print(f"문단: {len(result['paragraphs'])}개")
    print(f"제목: {len(result['headings'])}개")
    print(f"표:   {len(result['tables'])}개")
    print(f"이미지: {len(result['image_refs'])}개")
    
    if result['errors']:
        print(f"\n[경고] 오류 {len(result['errors'])}건:")
        for e in result['errors']:
            print(f"  - {e}")


if __name__ == '__main__':
    main()
