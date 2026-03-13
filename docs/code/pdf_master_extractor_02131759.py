"""
PDF 통합 추출 및 CSV 최적화 저장 마스터 시스템 (Windows 최적화)
- Excel 라이브러리 완전 배제, CSV(utf-8-sig) 중심의 데이터 파이프라인
- pdfplumber -> tabula-py 결함 허용(Fault-tolerant) 이중 폴백 추출
- 매니페스트(JSON) 및 코드 스냅샷 자동 백업을 통한 100% 데이터 추적성 보장
"""

import os
import sys
import re
import json
import shutil
import hashlib
import datetime
import subprocess
import argparse
import tkinter as tk
from tkinter import filedialog
from pathlib import Path

try:
    import fitz  # PyMuPDF
    import pdfplumber
    import pandas as pd
    import tabula
except ImportError:
    print("❌ 필수 라이브러리가 설치되지 않았습니다. 터미널에서 아래 명령어를 실행해주세요:")
    print("pip install PyMuPDF pdfplumber tabula-py pandas")
    sys.exit(1)

class PDFDocumentProcessor:
    def __init__(self, pdf_path, args):
        self.pdf_path = Path(pdf_path).resolve()
        self.args = args
        self.ts = datetime.datetime.now().strftime("%m%d%H%M")
        
        # Windows 파일명 제약 회피용 Slugify 처리 (최대 80자, 금지문자 제거)
        raw_name = self.pdf_path.stem
        slug = re.sub(r'[\\/*?:"<>|]', "", raw_name)
        slug = re.sub(r'\s+', "_", slug).strip("_")[:70]
        
        # 파일명 충돌 방지를 위한 해시 접미사
        short_hash = hashlib.md5(self.pdf_path.name.encode()).hexdigest()[:4]
        self.slugified_name = f"{slug}_{short_hash}"
        self.doc_id = self.slugified_name
        
        # 📁 출력 디렉토리 트리 구조 설계 (Exports 하위)
        self.base_dir = Path.cwd() / "Exports" / self.slugified_name
        self.dirs = {
            "Text": self.base_dir / "Text",
            "Tables_Index": self.base_dir / "Tables",
            "Tables_CSV": self.base_dir / "Tables" / "individual_csv",
            "Images_Embedded": self.base_dir / "Images" / "embedded",
            "Images_Rendered": self.base_dir / "Images" / "rendered",
            "Manifest": self.base_dir / "Manifest",
            "Backup": Path.cwd() / "GEMINI" / "code"
        }
        
        self.java_available = self._check_java()
        self.metadata_log = []
        self.tables_index = []
        self.page_count = 0
        self.scanned_suspect = False
        
        # 렌더링 검사 키워드
        self.render_keywords = ["그림", "그래프", "차트", "도표", "Figure", "Chart"]

    def _check_java(self):
        """Tabula-py 사용을 위한 Java 구동 환경 백그라운드 확인"""
        try:
            subprocess.run(["java", "-version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            return True
        except FileNotFoundError:
            print("⚠️ [시스템 알림] Java 환경이 감지되지 않아 tabula-py 폴백이 비활성화됩니다.")
            return False

    def _setup_directories_and_backup(self):
        """디렉토리 생성 및 실행 시점 코드 스냅샷 백업"""
        for d in self.dirs.values():
            d.mkdir(parents=True, exist_ok=True)
            
        try:
            if '__file__' in globals():
                current_file = Path(__file__).resolve()
                backup_name = f"{current_file.stem}_{self.ts}{current_file.suffix}"
                shutil.copy2(current_file, self.dirs["Backup"] / backup_name)
        except Exception as e:
            print(f"  [Warning] 코드 백업 중 예외 발생: {e}")

    def _parse_render_pages(self, pages_str):
        """--render-pages '1,2,5-8' 형태 파싱"""
        pages = set()
        if not pages_str:
            return pages
        for part in pages_str.split(','):
            part = part.strip()
            if '-' in part:
                try:
                    s, e = map(int, part.split('-'))
                    pages.update(range(s, e + 1))
                except ValueError:
                    pass
            elif part.isdigit():
                pages.add(int(part))
        return pages

    def _is_valid_table(self, table):
        """데이터 무결성 검증: 최소 2x2, 데이터 채움 밀도 20% 이상 확인"""
        if not table or len(table) < 2:
            return False
            
        max_cols = max((len(r) for r in table if r), default=0)
        if max_cols < 2:
            return False
            
        total_cells = len(table) * max_cols
        filled_cells = sum(1 for r in table if r for c in r if c is not None and str(c).strip() != "")
        
        return (filled_cells / total_cells) >= 0.2

    def _normalize_table(self, table):
        """불규칙한(가변 길이) 표 행 정규화 알고리즘"""
        if not table: return []
        max_cols = max(len(r) for r in table if r)
        normalized = []
        for r in table:
            row = [str(c) if c is not None else "" for c in (r or [])]
            row += [""] * (max_cols - len(row))
            normalized.append(row)
        return normalized

    def _save_table(self, table_data, page_num, t_idx, method):
        """DataFrame 변환 및 CSV(utf-8-sig) 저장"""
        table_data = self._normalize_table(table_data)
        if len(table_data) < 2: return
        
        # 중복 없는 컬럼명 생성 처리
        raw_cols = table_data[0]
        df_cols = []
        seen = set()
        for i, col in enumerate(raw_cols):
            base_col = str(col).strip().replace('\n', ' ') if col else f"Col_{i}"
            base_col = base_col if base_col else f"Col_{i}"
            
            final_col = base_col
            count = 1
            while final_col in seen:
                final_col = f"{base_col}_{count}"
                count += 1
            df_cols.append(final_col)
            seen.add(final_col)

        df = pd.DataFrame(table_data[1:], columns=df_cols)
        
        csv_name = f"table_p{page_num}_t{t_idx}_{method}_{self.ts}.csv"
        csv_path = self.dirs["Tables_CSV"] / csv_name
        
        # Windows Excel 호환성을 보장하는 utf-8-sig (BOM) 인코딩 강제
        df.to_csv(csv_path, index=False, encoding=self.args.csv_encoding)
        
        self.tables_index.append({
            "doc_id": self.doc_id, "ts": self.ts, "page": page_num,
            "table_idx": t_idx, "method": method,
            "csv_path": str(csv_path.relative_to(self.base_dir)),
            "rows": df.shape[0], "cols": df.shape[1]
        })
        
        self.metadata_log.append({
            "doc_id": self.doc_id, "ts": self.ts, "element_type": "table",
            "page": page_num, "method": method, "output_path": str(csv_path.relative_to(self.base_dir)),
            "bbox_unit(pt)": [], "coord_origin(top-left)": True
        })

    def run_pipeline(self):
        print(f"\n🚀 분석 및 추출 파이프라인 시작: {self.pdf_path.name}")
        self._setup_directories_and_backup()
        
        full_text_lines = []
        total_text_length = 0
        render_pages_set = self._parse_render_pages(self.args.render_pages)
        
        # 1. 텍스트 추출, 이미지 임베딩, 고해상도 렌더링 (PyMuPDF)
        with fitz.open(self.pdf_path) as doc:
            self.page_count = len(doc)
            for page_num in range(self.page_count):
                page = doc[page_num]
                page_height = page.rect.height
                
                # [텍스트 추출 및 정제]
                blocks = page.get_text("dict", sort=True)["blocks"]
                page_text_builder = []
                
                for b in blocks:
                    if b['type'] == 0:  # Text Block
                        y0, y1 = b["bbox"][1], b["bbox"][3]
                        block_text = "".join(s["text"] for l in b["lines"] for s in l["spans"])
                        
                        # 머리말/꼬리말(Noise) 스마트 필터링 로직 (상하단 5% 및 길이 50자 이하)
                        if (y0 < page_height * 0.05 or y1 > page_height * 0.95) and len(block_text) < 50:
                            continue
                            
                        block_text = re.sub(r'-\s*\n\s*', '', block_text).strip()  # 하이픈 줄바꿈 결합
                        
                        if block_text:
                            page_text_builder.append(block_text)
                            self.metadata_log.append({
                                "doc_id": self.doc_id, "ts": self.ts, "element_type": "text_block",
                                "page": page_num + 1, "method": "PyMuPDF", 
                                "output_path": f"Text/full_text_{self.ts}.txt",
                                "bbox_unit(pt)": [round(c, 2) for c in b["bbox"]], "coord_origin(top-left)": True
                            })
                            
                clean_page_text = "\n".join(page_text_builder)
                if clean_page_text:
                    full_text_lines.append(f"--- Page {page_num + 1} ---\n{clean_page_text}")
                    total_text_length += len(clean_page_text)

                # [순수 이미지 객체 추출]
                for img_idx, img in enumerate(page.get_images(full=True)):
                    base_image = doc.extract_image(img[0])
                    img_path = self.dirs["Images_Embedded"] / f"img_p{page_num+1}_{img_idx+1}_{self.ts}.{base_image['ext']}"
                    with open(img_path, "wb") as f_img:
                        f_img.write(base_image["image"])

                # [키워드 감지 기반 스마트 렌더링]
                has_keywords = any(kw in clean_page_text for kw in self.render_keywords)
                vectors = page.get_drawings()
                
                if self.args.render_all or ((page_num + 1) in render_pages_set) or has_keywords or len(vectors) >= 50:
                    pix = page.get_pixmap(dpi=300)
                    render_path = self.dirs["Images_Rendered"] / f"render_p{page_num+1}_{self.ts}.png"
                    pix.save(render_path)

        # 스캔본 판별 (평균 50자 미만)
        if self.page_count > 0 and (total_text_length / self.page_count) < 50:
            self.scanned_suspect = True
            print("⚠️ [경고] 텍스트가 현저히 적습니다. 스캔 이미지 기반 PDF(scanned_suspect)로 의심됩니다.")

        # 통합 텍스트 파일 생성
        with open(self.dirs["Text"] / f"full_text_{self.ts}.txt", "w", encoding="utf-8") as f:
            f.write("\n\n".join(full_text_lines))

        # 2. 표(Table) 추출 (pdfplumber + tabula-py 결함 허용 구조)
        print("📊 표 데이터 구조화 및 이중 폴백 처리 중...")
        with pdfplumber.open(self.pdf_path) as pdf:
            for page_num, page in enumerate(pdf.pages, start=1):
                tables = page.extract_tables()
                valid_tables_found = 0
                
                if tables:
                    for t_idx, table in enumerate(tables, start=1):
                        if self._is_valid_table(table):
                            self._save_table(table, page_num, valid_tables_found + 1, "pdfplumber")
                            valid_tables_found += 1
                            
                # 폴백 시스템 (pdfplumber가 실패하거나 품질이 미달일 때 Tabula 개입)
                if valid_tables_found == 0 and self.java_available:
                    try:
                        dfs = tabula.read_pdf(
                            self.pdf_path, pages=page_num, multiple_tables=True, 
                            guess=True, mode=self.args.tabula_mode,
                            pandas_options={'header': None, 'dtype': str} # 첫 행 데이터 소실 방어
                        )
                        for t_idx, df in enumerate(dfs):
                            df.fillna("", inplace=True)
                            table_list = df.values.tolist()
                            if self._is_valid_table(table_list):
                                self._save_table(table_list, page_num, valid_tables_found + 1, "tabula")
                                valid_tables_found += 1
                    except Exception:
                        pass
        
        self._generate_manifest()
        print(f"\n✅ 파이프라인 구동 완료! 결과물이 다음 경로에 저장되었습니다.\n📂 {self.base_dir.resolve()}")


    def _generate_manifest(self):
        """실행 이력, 파라미터 상태를 100% 보존하는 매니페스트 발급"""
        # CSV 전체 인덱스 저장
        if self.tables_index:
            df_index = pd.DataFrame(self.tables_index)
            df_index.to_csv(self.dirs["Tables_Index"] / f"tables_index_{self.ts}.csv", index=False, encoding=self.args.csv_encoding)
            
        # 개별 좌표 메타데이터 JSONL
        with open(self.dirs["Manifest"] / "metadata.jsonl", "w", encoding="utf-8") as f:
            for log in self.metadata_log:
                f.write(json.dumps(log, ensure_ascii=False) + "\n")
                
        # 실행 통합 매니페스트 JSON
        run_manifest = {
            "doc_id": self.doc_id,
            "ts": self.ts,
            "source_pdf_path": str(self.pdf_path),
            "slugified_name": self.slugified_name,
            "page_count": self.page_count,
            "python_version": sys.version,
            "library_versions": {
                "PyMuPDF": fitz.VersionBind,
                "pdfplumber": pdfplumber.__version__,
                "pandas": pd.__version__,
                "tabula-py": tabula.__version__ if self.java_available else "Not Installed"
            },
            "args": vars(self.args),
            "render_policy": "selective_auto(keywords,vectors) or manual",
            "java_available": self.java_available,
            "scanned_suspect": self.scanned_suspect
        }
        with open(self.dirs["Manifest"] / "run_manifest.json", "w", encoding="utf-8") as f:
            json.dump(run_manifest, f, indent=4, ensure_ascii=False)


def select_file_gui():
    """Tkinter를 이용한 직관적인 시스템 파일 선택기"""
    root = tk.Tk()
    root.withdraw()
    root.attributes('-topmost', True)
    
    file_path = filedialog.askopenfilename(
        title="데이터를 추출할 PDF를 선택하세요",
        filetypes=[("PDF 파일", "*.pdf"), ("모든 파일", "*.*")]
    )
    return file_path


def main():
    parser = argparse.ArgumentParser(description="PDF 데이터 무손실 구조화 시스템")
    parser.add_argument("--pdf", type=str, default="", help="처리할 PDF 파일 경로 (미지정 시 탐색기 창 열림)")
    parser.add_argument("--layout", type=str, choices=["simple", "auto"], default="simple", help="텍스트 다단 레이아웃 모드")
    parser.add_argument("--tabula-mode", type=str, choices=["stream", "lattice"], default="stream", help="Tabula 폴백 모드")
    parser.add_argument("--render-all", action="store_true", help="모든 페이지 강제 렌더링")
    parser.add_argument("--render-pages", type=str, default="", help="특정 페이지 범위 지정 렌더링 (예: 1,3,5-8)")
    parser.add_argument("--csv-encoding", type=str, choices=["utf-8-sig", "utf-8"], default="utf-8-sig", help="CSV 저장 인코딩 형식")
    
    args = parser.parse_args()
    
    print("=" * 65)
    print(" 📑 로컬 PDF 비정형 데이터 정밀 추출 파이프라인 (Windows) ")
    print("=" * 65)
    
    pdf_path = args.pdf
    if not pdf_path:
        print("💡 분석할 PDF를 시스템 파일 탐색기에서 선택해 주세요...")
        pdf_path = select_file_gui()
        
    if not pdf_path or not os.path.exists(pdf_path):
        print("❌ 유효한 PDF가 선택되지 않아 프로그램을 종료합니다.")
        sys.exit(0)
        
    processor = PDFDocumentProcessor(pdf_path, args)
    processor.run_pipeline()


if __name__ == "__main__":
    main()