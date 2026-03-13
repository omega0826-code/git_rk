import pandas as pd

# Excel 파일 읽기
df = pd.read_excel('D:/git_rk/openapi/getHospBasisList/data/서울_강남구_피부과_20260113_205835.xlsx')

print(f'총 {len(df)}건\n')
print('컬럼 목록:')
for col in df.columns:
    print(f'  - {col}')

print(f'\n첫 번째 행 샘플:')
for key, value in df.iloc[0].to_dict().items():
    print(f'  {key}: {value}')
