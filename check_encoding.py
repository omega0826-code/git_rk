
import chardet

def detect_encoding(file_path):
    with open(file_path, 'rb') as f:
        rawdata = f.read(10000)
    return chardet.detect(rawdata)

print(detect_encoding(r'd:\git_rk\data\gangnam_reviews_FINAL_ALL.csv'))
