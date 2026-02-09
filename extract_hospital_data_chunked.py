import pandas as pd
import os

def extract_hospital_data():
    source_path = r'd:\git_rk\data\seoul hospital\HIRA_강남언니_결합_최종.csv'
    output_path = r'd:\git_rk\data\seoul hospital\seoul_extraction.csv'
    
    allowed_types = ["의원", "병원", "종합병원", "상급종합병원"]
    
    # Use CP949 first as it's common for Korean public data, fallback to UTF-8
    encoding = 'cp949'
    try:
        pd.read_csv(source_path, nrows=1, encoding=encoding)
    except:
        encoding = 'utf-8'
    
    header = True
    total_extracted = 0
    total_processed = 0
    
    print(f"Starting extraction with encoding {encoding}...")
    
    for chunk in pd.read_csv(source_path, encoding=encoding, chunksize=5000):
        total_processed += len(chunk)
        # Filter by Hospital Type
        mask_type = chunk['종별코드명'].isin(allowed_types)
        
        # Filter by "피부" in any column (or specifically treatment_tags if present)
        # To be safe and broad as requested, search in all string columns
        mask_subject = chunk.astype(str).apply(lambda row: row.str.contains('피부').any(), axis=1)
        
        filtered_chunk = chunk[mask_type & mask_subject]
        
        if not filtered_chunk.empty:
            filtered_chunk.to_csv(output_path, mode='a' if not header else 'w', 
                                 index=False, header=header, encoding='utf-8-sig')
            header = False
            total_extracted += len(filtered_chunk)
        
        print(f"Processed {total_processed} rows, Found {total_extracted} so far...")

    print(f"Finished. Total extracted: {total_extracted} rows.")
    print(f"Saved to: {output_path}")

if __name__ == "__main__":
    extract_hospital_data()
