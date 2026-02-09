import pandas as pd
import os

def map_industry_middle_name():
    industry_path = r'd:\git_rk\project\25_121_ulsan\CSV\업종_raw data.csv'
    mid_mapping_path = r'd:\git_rk\project\25_121_ulsan\CSV\표준산업분류_중분류.csv'

    print("Loading data for middle category name mapping...")
    df_ind = pd.read_csv(industry_path, encoding='utf-8')
    df_mid = pd.read_csv(mid_mapping_path, encoding='utf-8')

    # Ensure s3 and 코드 are formatted correctly for merging
    def format_code(val):
        try:
            if pd.isna(val) or val == '알수없음': return '알수없음'
            # Convert to float then int then string with zfill to handle potential float-like strings
            return str(int(float(val))).zfill(2)
        except:
            return str(val)

    df_ind['s3_code_formatted'] = df_ind['s3'].apply(format_code)
    df_mid['코드_formatted'] = df_mid['코드'].apply(format_code)

    # Dictionary for mapping: code -> name
    name_map = dict(zip(df_mid['코드_formatted'], df_mid['중분류명']))

    # Add new column 's3_nm' (Middle category name)
    df_ind['s3_nm'] = df_ind['s3_code_formatted'].map(name_map).fillna('알수없음')

    # Remove temporary helper column
    df_ind = df_ind.drop(columns=['s3_code_formatted'])

    # Save back to CSV
    df_ind.to_csv(industry_path, index=False, encoding='utf-8')
    print(f"Successfully mapped and saved to {industry_path}")

    # Display some results
    print("\n[Mapping Results Sample]")
    print(df_ind[['s1', 's3', 's3_nm']].head(10))

if __name__ == "__main__":
    map_industry_middle_name()
