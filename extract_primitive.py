import os

def primitive_extract():
    source = r'd:\git_rk\data\seoul hospital\HIRA_강남언니_결합_최종.csv'
    output = r'd:\git_rk\data\seoul hospital\seoul_extraction.csv'
    
    # Simple subjects to look for
    keywords = ['피부', '피부과']
    # Hospital types
    types = ['의원', '병원', '종합병원', '상급종합']
    
    try:
        # Detect encoding
        encoding = 'cp949'
        with open(source, 'r', encoding=encoding, errors='ignore') as f:
            header = f.readline()
        
        with open(source, 'r', encoding=encoding, errors='ignore') as fin, \
             open(output, 'w', encoding='utf-8-sig', newline='') as fout:
            
            header = fin.readline()
            fout.write(header)
            
            count = 0
            for line in fin:
                # Basic line filter
                if any(k in line for k in keywords) and any(t in line for t in types):
                    fout.write(line)
                    count += 1
                
        print(f"Extracted {count} rows.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    primitive_extract()
