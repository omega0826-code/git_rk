# -*- coding: utf-8 -*-
"""
서울시 주요 82장소 영역에서 강남구 영역만 추출
"""

import geopandas as gpd
import os
from pathlib import Path

# 파일 경로 설정
input_shapefile = r'd:\git_rk\data\서울시 주요 82장소 영역\서울시 주요 82장소 영역.shp'
output_dir = r'd:\git_rk\data\강남구_영역'
output_shapefile = os.path.join(output_dir, '강남구_영역.shp')
output_csv = os.path.join(output_dir, '강남구_영역.csv')
output_excel = os.path.join(output_dir, '강남구_영역.xlsx')

# 출력 디렉토리 생성
Path(output_dir).mkdir(parents=True, exist_ok=True)

print("=" * 60)
print("서울시 주요 82장소 영역에서 강남구 영역 추출")
print("=" * 60)

# Shapefile 읽기
print(f"\n[1/5] Shapefile 읽기 중...")
gdf = gpd.read_file(input_shapefile, encoding='cp949')
print(f"   - 전체 영역 개수: {len(gdf)}")
print(f"   - 컬럼: {list(gdf.columns)}")

# 데이터 미리보기
print(f"\n[2/5] 데이터 구조 확인")
print(gdf.head())
print(f"\n데이터 타입:")
print(gdf.dtypes)

# 강남구 필터링 (가능한 컬럼명들을 확인)
print(f"\n[3/5] 강남구 영역 필터링 중...")

# 가능한 구 이름 컬럼 찾기
possible_columns = ['구', '구명', 'SGG_NM', 'SIG_KOR_NM', 'SIG_NM', 'district', 'gu']
gu_column = None

for col in gdf.columns:
    col_lower = str(col).lower()
    if any(keyword in col_lower for keyword in ['구', 'gu', 'district', 'sgg', 'sig']):
        gu_column = col
        print(f"   - 구 컬럼 발견: '{col}'")
        print(f"   - 고유값: {gdf[col].unique()[:10]}")  # 처음 10개만 표시
        break

if gu_column is None:
    print("\n⚠️ 경고: 구 이름을 포함하는 컬럼을 찾을 수 없습니다.")
    print("모든 컬럼의 고유값을 확인합니다:\n")
    for col in gdf.columns:
        if col != 'geometry':
            print(f"\n컬럼 '{col}'의 고유값:")
            print(gdf[col].unique())
    
    # 사용자가 수동으로 확인할 수 있도록 전체 데이터 저장
    print(f"\n전체 데이터를 CSV로 저장하여 확인할 수 있도록 합니다.")
    temp_csv = os.path.join(output_dir, '전체_데이터_확인.csv')
    gdf_no_geom = gdf.drop(columns=['geometry'])
    gdf_no_geom.to_csv(temp_csv, index=False, encoding='utf-8-sig')
    print(f"   - 저장 위치: {temp_csv}")
    
    gangnam_gdf = None
else:
    # 강남구 필터링
    gangnam_gdf = gdf[gdf[gu_column].str.contains('강남', na=False)]
    print(f"   - 강남구 영역 개수: {len(gangnam_gdf)}")
    
    if len(gangnam_gdf) == 0:
        print(f"\n⚠️ 경고: '{gu_column}' 컬럼에서 '강남'을 포함하는 데이터를 찾을 수 없습니다.")
        print(f"'{gu_column}' 컬럼의 모든 고유값:")
        print(gdf[gu_column].unique())

# 강남구 데이터가 있는 경우에만 저장
if gangnam_gdf is not None and len(gangnam_gdf) > 0:
    print(f"\n[4/5] 강남구 영역 저장 중...")
    
    # Shapefile로 저장
    gangnam_gdf.to_file(output_shapefile, encoding='cp949')
    print(f"   ✓ Shapefile 저장: {output_shapefile}")
    
    # CSV로 저장 (geometry 제외)
    gangnam_df = gangnam_gdf.drop(columns=['geometry'])
    gangnam_df.to_csv(output_csv, index=False, encoding='utf-8-sig')
    print(f"   ✓ CSV 저장: {output_csv}")
    
    # Excel로 저장
    gangnam_df.to_excel(output_excel, index=False, engine='openpyxl')
    print(f"   ✓ Excel 저장: {output_excel}")
    
    print(f"\n[5/5] 추출 완료!")
    print(f"\n강남구 영역 정보:")
    print(gangnam_df)
    
    print(f"\n" + "=" * 60)
    print(f"✅ 작업 완료!")
    print(f"   - 추출된 영역 개수: {len(gangnam_gdf)}")
    print(f"   - 저장 위치: {output_dir}")
    print("=" * 60)
else:
    print(f"\n" + "=" * 60)
    print(f"⚠️ 강남구 데이터를 추출하지 못했습니다.")
    print(f"   위의 전체 데이터를 확인하여 올바른 필터링 조건을 찾아주세요.")
    print("=" * 60)
