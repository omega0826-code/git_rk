import pandas as pd
import os

def process_industry_data():
    raw_data_path = r'd:\git_rk\project\25_121_ulsan\CSV\업종_raw data.csv'
    mid_mapping_path = r'd:\git_rk\project\25_121_ulsan\CSV\표준산업분류_중분류.csv'
    detail_mapping_path = r'd:\git_rk\project\25_121_ulsan\CSV\표준산업분류_세세분류.csv'

    print(f"Loading data...")
    df_raw = pd.read_csv(raw_data_path, encoding='utf-8')
    df_mid = pd.read_csv(mid_mapping_path, encoding='utf-8')
    df_detail = pd.read_csv(detail_mapping_path, encoding='utf-8')

    # 1. Delete empty rows
    df_raw = df_raw.dropna(how='all')

    # Text Normalization function
    def normalize_text(text):
        if pd.isna(text):
            return ""
        text = str(text).replace('；', ';').replace(';', ';')
        text = "".join(text.split())
        return text

    # Prepare mapping dictionaries
    df_mid['normalized_name'] = df_mid['중분류명'].apply(normalize_text)
    mid_dict = dict(zip(df_mid['normalized_name'], df_mid['코드']))

    df_detail['normalized_name'] = df_detail['항목명'].apply(normalize_text)
    # Detail code's first 2 digits represent the middle category
    df_detail['mid_code'] = df_detail['코드'].apply(lambda x: str(x).zfill(5)[:2])
    detail_dict = dict(zip(df_detail['normalized_name'], df_detail['mid_code']))

    # 3. Update s3 column with 3-step mapping
    def map_s3(s1_value):
        normalized_s1 = normalize_text(s1_value)
        if normalized_s1 == "9999":
            return "알수없음"
        
        # Step 1: Exact match in Middle Category
        code = mid_dict.get(normalized_s1)
        if code:
            return str(int(float(code))).zfill(2)
        
        # Step 2: Exact match in Detail Category
        code = detail_dict.get(normalized_s1)
        if code:
            return str(code)
            
        # Step 3: Keyword based mapping (for names that differ slightly)
        keyword_map = {
            '출판': '58',
            '소프트웨어': '58',
            '연구개발': '70',
            '시장조사': '71',
            '여론조사': '71',
            '법무': '71',
            '회계': '71',
            '세무': '71',
            '경영컨설팅': '71',
            '광고': '71',
            '전문서비스': '71'
        }
        for kw, target_code in keyword_map.items():
            if kw in normalized_s1:
                return target_code

        return "알수없음"

    df_raw['s3'] = df_raw['s1'].apply(map_s3)

    # 4. Save results (UTF-8)
    def clean_code(val):
        if pd.isna(val) or val == "":
            return ""
        try:
            return str(int(float(val)))
        except:
            return str(val)

    df_raw['s2'] = df_raw['s2'].apply(clean_code)
    df_raw['s3'] = df_raw['s3'].astype(str)
    
    print("Pre-save check (first 5 rows):")
    print(df_raw[['s1', 's3']].head())
    
    # Check specifically for "출판"
    test_rows = df_raw[df_raw['s1'].str.contains('출판', na=False)]
    print("\nCheck for '출판' keyword mapping:")
    print(test_rows[['s1', 's3']])

    df_raw.to_csv(raw_data_path, index=False, encoding='utf-8')
    print(f"\nSuccessfully updated {raw_data_path}")

if __name__ == "__main__":
    process_industry_data()
