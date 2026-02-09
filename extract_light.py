import csv
import sys

def extract():
    source = r'd:\git_rk\data\seoul hospital\HIRA_강남언니_결합_최종.csv'
    output = r'd:\git_rk\data\seoul hospital\seoul_extraction.csv'
    
    allowed_types = {"의원", "병원", "종합병원", "상급종합", "상급종합병원"}
    
    # Try encodings
    enc = 'cp949'
    try:
        with open(source, 'r', encoding=enc) as f:
            f.readline()
    except:
        enc = 'utf-8'
        
    print(f"Reading with {enc}...")
    
    count = 0
    extracted = 0
    try:
        with open(source, 'r', encoding=enc, errors='replace') as fin:
            reader = csv.reader(fin)
            header = next(reader)
            
            # Find column indices
            type_idx = -1
            if '종별코드명' in header:
                type_idx = header.index('종별코드명')
            
            with open(output, 'w', encoding='utf-8-sig', newline='') as fout:
                writer = csv.writer(fout)
                writer.writerow(header)
                
                for row in reader:
                    count += 1
                    # Check type
                    type_match = False
                    if type_idx != -1 and len(row) > type_idx:
                        if row[type_idx] in allowed_types:
                            type_match = True
                    
                    # Check "피부" in any field
                    content_match = any('피부' in field for field in row)
                    
                    if type_match and content_match:
                        writer.writerow(row)
                        extracted += 1
                    
                    if count % 5000 == 0:
                        print(f"Progress: {count} rows processed, {extracted} extracted...")
                        
    except Exception as e:
        print(f"Error: {str(e)}")
        return

    print(f"Total: {count}, Extracted: {extracted}")
    print(f"Finished. Saved to {output}")

if __name__ == "__main__":
    extract()
