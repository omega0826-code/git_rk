import pandas as pd
import os
import sys

def extract():
    log_file = r'd:\git_rk\extraction_log.txt'
    with open(log_file, 'w', encoding='utf-8') as log:
        log.write("Starting extraction...\n")
        source_path = r'd:\git_rk\data\seoul hospital\HIRA_강남언니_결합_최종.csv'
        output_path = r'd:\git_rk\data\seoul hospital\seoul_extraction.csv'
        
        if not os.path.exists(source_path):
            log.write(f"ERROR: Source file not found: {source_path}\n")
            return
            
        log.write(f"Source file size: {os.path.getsize(source_path)} bytes\n")
        
        # Try different encodings
        encodings = ['utf-8-sig', 'cp949', 'utf-8']
        df = None
        for enc in encodings:
            try:
                df = pd.read_csv(source_path, encoding=enc, nrows=5000)
                log.write(f"Successfully read first 5000 rows with encoding {enc}\n")
                break
            except Exception as e:
                log.write(f"Failed to read with {enc}: {str(e)}\n")
        
        if df is None:
            log.write("ERROR: Could not read CSV with any encoding\n")
            return
            
        log.write(f"Columns: {df.columns.tolist()}\n")
        
        # Define filters
        allowed_types = ["의원", "병원", "종합병원", "상급종합병원"]
        # The user said "상급종합", which might be "상급종합병원"
        
        # Broad filter for "피부"
        mask_type = df['종별코드명'].astype(str).str.contains('|'.join(allowed_types))
        mask_subject = df.astype(str).apply(lambda row: row.str.contains('피부').any(), axis=1)
        
        filtered = df[mask_type & mask_subject]
        log.write(f"Filtered {len(filtered)} rows from first 5000\n")
        
        # Now process full file if first 5000 worked
        header = True
        total = 0
        for chunk in pd.read_csv(source_path, encoding=enc, chunksize=5000):
            m_type = chunk['종별코드명'].astype(str).str.contains('|'.join(allowed_types))
            m_subj = chunk.astype(str).apply(lambda r: r.str.contains('피부').any(), axis=1)
            f_chunk = chunk[m_type & m_subj]
            if not f_chunk.empty:
                f_chunk.to_csv(output_path, mode='a' if not header else 'w', 
                               index=False, header=header, encoding='utf-8-sig')
                header = False
                total += len(f_chunk)
        
        log.write(f"TOTAL EXTRACTED: {total}\n")
        log.write(f"Saved to {output_path}\n")

if __name__ == "__main__":
    try:
        extract()
    except Exception as e:
        with open(r'd:\git_rk\extraction_log.txt', 'a', encoding='utf-8') as log:
            log.write(f"CRITICAL ERROR: {str(e)}\n")
