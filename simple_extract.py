import os

source = r'd:\git_rk\data\seoul hospital\HIRA_강남언니_결합_최종.csv'
target = r'd:\git_rk\seoul_extraction.csv'
types = ["의원", "병원", "종합병원", "상급종합병원"]

def extract():
    print(f"Reading from {source}")
    if not os.path.exists(source):
        print("Source not found")
        return

    try:
        f = open(source, 'r', encoding='utf-8-sig')
        header = f.readline()
    except:
        f = open(source, 'r', encoding='cp949')
        header = f.readline()
    
    count = 0
    with open(target, 'w', encoding='utf-8-sig') as tf:
        tf.write(header)
        for line in f:
            # Quick check for hospital types and "피부"
            if any(h_type in line for h_type in types):
                if "피부" in line:
                    tf.write(line)
                    count += 1
    f.close()
    print(f"Extraction complete. Found {count} lines.")
    print(f"Output saved to {target}")

if __name__ == "__main__":
    extract()
