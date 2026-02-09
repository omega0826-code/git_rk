import csv
import os
import sys

# Set paths
source = r'd:\git_rk\data\seoul hospital\HIRA_강남언니_결합_최종.csv'
target = r'd:\git_rk\data\seoul hospital\seoul_extraction.csv'
types = ["의원", "병원", "종합병원", "상급종합병원"]

def extract():
    print(f"Starting extraction from {source}")
    if not os.path.exists(source):
        print("Source not found.")
        return

    # Determine encoding and open
    f = None
    try:
        f = open(source, 'r', encoding='utf-8-sig')
        reader = csv.reader(f)
        header = next(reader)
        print("Opened with utf-8-sig")
    except Exception as e:
        if f: f.close()
        try:
            f = open(source, 'r', encoding='cp949')
            reader = csv.reader(f)
            header = next(reader)
            print("Opened with cp949")
        except Exception as e2:
            print(f"Failed to open: {e2}")
            return

    # Process and write
    try:
        with open(target, 'w', encoding='utf-8-sig', newline='') as tf:
            writer = csv.writer(tf)
            writer.writerow(header)
            
            count = 0
            total = 0
            for row in reader:
                total += 1
                if not row or len(row) < 4:
                    continue
                
                # Check criteria
                h_type = row[3].strip()
                if h_type in types:
                    # Check "피부" in any column
                    found = False
                    for cell in row:
                        if "피부" in cell:
                            found = True
                            break
                    
                    if found:
                        writer.writerow(row)
                        count += 1
                        if count % 20 == 0:
                            tf.flush()
                            print(f"Found {count} matches so far...")
            
            print(f"Finished. Total rows: {total}, Matches: {count}")
    except Exception as e:
        print(f"Error during extraction: {e}")
    finally:
        if f: f.close()

if __name__ == "__main__":
    extract()
