import pandas as pd
import chardet

file_path = r'd:\git_rk\project\25_124_interviiew\data\(CSV)interview_data_260121.csv'

# Detect encoding
with open(file_path, 'rb') as f:
    rawdata = f.read(10000)
    result = chardet.detect(rawdata)
    encoding = result['encoding']
    confidence = result['confidence']

print(f"Detected encoding: {encoding} with confidence {confidence}")

try:
    df = pd.read_csv(file_path, encoding=encoding)
    print("CSV loaded successfully.")
    print("\nColumns:")
    print(df.columns.tolist())
    print("\nFirst 3 rows:")
    print(df.head(3).to_string())
    print("\nShape:", df.shape)
except Exception as e:
    print(f"Error loading CSV with {encoding}: {e}")
    # Try common encodings
    for enc in ['utf-8-sig', 'cp949', 'euc-kr']:
        try:
            df = pd.read_csv(file_path, encoding=enc)
            print(f"CSV loaded successfully with {enc}.")
            break
        except:
            continue
