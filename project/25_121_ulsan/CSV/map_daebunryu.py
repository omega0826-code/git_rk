import pandas as pd
import os

os.chdir(r'd:\git_rk\project\25_121_ulsan\CSV')

# 1. 파일 읽기
raw = pd.read_csv('업종_raw data.csv', encoding='utf-8', dtype=str)
daebun = pd.read_csv('표준산업분류_대분류.csv', encoding='utf-8', dtype=str)

# 정리
for df in [raw, daebun]:
    df.columns = df.columns.str.strip()
    for c in df.columns:
        df[c] = df[c].str.strip().str.replace('\r', '', regex=False).str.replace('　', '', regex=False)

# 2. 중분류 코드 -> 대분류 코드 매핑 테이블
jung_to_dae = {}
code_ranges = {
    'A': ['01','02','03'],
    'B': ['05','06','07','08'],
    'C': [str(i).zfill(2) for i in range(10,34+1)],
    'D': ['35'],
    'E': ['36','37','38','39'],
    'F': ['41','42'],
    'G': ['45','46','47'],
    'H': ['49','50','51','52'],
    'I': ['55','56'],
    'J': ['58','59','60','61','62','63'],
    'K': ['64','65','66'],
    'L': ['68'],
    'M': ['70','71','72','73'],
    'N': ['74','75','76'],
    'O': ['84'],
    'P': ['85'],
    'Q': ['86','87'],
    'R': ['90','91'],
    'S': ['94','95','96'],
    'T': ['97','98'],
    'U': ['99']
}
for dae_code, jung_codes in code_ranges.items():
    for jc in jung_codes:
        jung_to_dae[jc] = dae_code

# 대분류 코드 -> 대분류명
dae_name_map = dict(zip(daebun['a1'], daebun['a3']))

# 대분류명 -> 대분류코드 (역방향)
name_to_dae = {}
for _, row in daebun.iterrows():
    name_to_dae[row['a3']] = row['a1']

# 3. 매핑 실행
s4_list = []
s4_name_list = []

for idx, row in raw.iterrows():
    s1 = str(row.get('s1', '')).strip() if pd.notna(row.get('s1')) else ''
    s3 = str(row.get('s3', '')).strip() if pd.notna(row.get('s3')) else ''
    
    s1 = s1.replace('\r', '').replace('　', '').strip()
    s3 = s3.replace('\r', '').strip()
    
    dae_code = ''
    dae_name = ''
    
    # Case 1: s3(중분류 코드)가 있는 경우
    if s3 and s3 != 'nan' and s3 != '':
        if s3 in jung_to_dae:
            dae_code = jung_to_dae[s3]
            dae_name = dae_name_map.get(dae_code, '')
        elif s3 == '알수없음':
            dae_code = '알수없음'
            dae_name = '알수없음'
    # Case 2: s1이 대분류명인 경우
    elif s1:
        # 직접 매칭
        matched = False
        for nm, cd in name_to_dae.items():
            if s1 == nm:
                dae_code = cd
                dae_name = nm
                matched = True
                break
        if not matched:
            # 부분 매칭
            for nm, cd in name_to_dae.items():
                if s1 in nm or nm in s1:
                    dae_code = cd
                    dae_name = nm
                    matched = True
                    break
        # 특수: 제조업 관련 세부 항목
        if not matched and '제조업' in s1:
            dae_code = 'C'
            dae_name = '제조업'
        # 특수: 9999/알수없음
        if not matched and (s1 == '9999' or s1 == '알수없음'):
            dae_code = '알수없음'
            dae_name = '알수없음'
    
    s4_list.append(dae_code)
    s4_name_list.append(dae_name)

raw['s4'] = s4_list
raw['s4_name'] = s4_name_list

# 4. 결과 확인
print('=== 매핑 결과 ===')
print(raw[['s1','s2','s3','s3_nm','s4','s4_name']].to_string())

unmapped = raw[(raw['s4'] == '') & (raw['s1'].notna()) & (raw['s1'].str.strip() != '')]
if len(unmapped) > 0:
    print(f'\n=== 매핑 실패 {len(unmapped)}건 ===')
    print(unmapped[['s1','s2','s3','s3_nm','s4','s4_name']].to_string())
else:
    print('\n모든 행이 정상적으로 매핑되었습니다.')

# 5. 저장
raw.to_csv('업종_raw data.csv', index=False, encoding='utf-8-sig')
print('\n파일이 저장되었습니다: 업종_raw data.csv')
