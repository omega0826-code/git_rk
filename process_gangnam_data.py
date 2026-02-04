
import pandas as pd
import os
import glob
from datetime import datetime

# 1. 설정
DATA_DIR = r'd:\git_rk\data\서울시 상권'
SHP_DIR = r'd:\git_rk\data\서울시 주요 82장소 영역'
TIMESTAMP = datetime.now().strftime('%Y%m%d_%H%M%S')
REPORT_DIR = os.path.join(r'd:\git_rk', 'REPORT', f'Gangnam_Data_{TIMESTAMP}')
CSV_OUT_DIR = os.path.join(REPORT_DIR, 'csv')
SHP_OUT_DIR = os.path.join(REPORT_DIR, 'shapefile')

os.makedirs(CSV_OUT_DIR, exist_ok=True)
os.makedirs(SHP_OUT_DIR, exist_ok=True)

print(f"작업 시작... 저장 경로: {REPORT_DIR}")

# 2. 강남구 상권 코드 추출
area_file = os.path.join(DATA_DIR, '서울시 상권분석서비스(영역-상권).csv')
try:
    area_df = pd.read_csv(area_file, encoding='cp949')
    gangnam_codes = area_df[area_df['자치구_코드_명'] == '강남구']['상권_코드'].unique().tolist()
    print(f"강남구 상권 코드 추출 완료: {len(gangnam_codes)}개")
except Exception as e:
    print(f"상권 코드 추출 실패: {e}")
    gangnam_codes = []

# 3. 10개 CSV 파일 필터링
csv_files = glob.glob(os.path.join(DATA_DIR, '*.csv'))
for f in csv_files:
    filename = os.path.basename(f)
    print(f"처리 중: {filename}...")
    try:
        # 파일 크기에 따라 chunksize 적용 고려 (현재는 약 100MB 이하이므로 한 번에 로드)
        df = pd.read_csv(f, encoding='cp949')
        if '상권_코드' in df.columns:
            filtered_df = df[df['상권_코드'].isin(gangnam_codes)]
            out_path = os.path.join(CSV_OUT_DIR, f'gangnam_{filename}')
            # UTF-8 with BOM으로 저장 (엑셀 오픈 시 한글 깨짐 방지)
            filtered_df.to_csv(out_path, index=False, encoding='utf-8-sig')
            print(f"  -> 저장됨: {len(filtered_df)}행")
        else:
            print(f"  -> '상권_코드' 컬럼이 없어 건너뜁니다.")
    except Exception as e:
        print(f"  -> 처리 실패: {e}")

# 4. Shapefile 필터링
try:
    import geopandas as gpd
    shp_file = os.path.join(SHP_DIR, '서울시 주요 82장소 영역.shp')
    if os.path.exists(shp_file):
        print(f"Shapefile 처리 중: {os.path.basename(shp_file)}...")
        gdf = gpd.read_file(shp_file)
        # 강남구 필터링 (컬럼명 확인 필요 - 시각화 탭에서 'AREA_NM' 등 확인했으나 'GU_NM' 또는 '자치구'일 가능성)
        # 서울시 데이터의 경우 보통 'NM' 또는 'AREA_NM'에 구 정보가 포함되기도 함.
        # 일단 자치구 관련 컬럼을 찾아봄
        gu_col = [col for col in gdf.columns if 'GU' in col.upper() or '구' in col]
        if gu_col:
             filtered_gdf = gdf[gdf[gu_col[0]].str.contains('강남구', na=False)]
        else:
             # 컬럼을 못 찾으면 시각화를 위해 모든 컬럼 출력 후 첫 5행 기반 추측
             print(f"구 컬럼을 찾을 수 없어 전체 컬럼 기준 필터링 시도: {gdf.columns.tolist()}")
             filtered_gdf = gdf[gdf.apply(lambda row: row.astype(str).str.contains('강남').any(), axis=1)]
        
        if not filtered_gdf.empty:
            out_shp = os.path.join(SHP_OUT_DIR, 'gangnam_major_82_locations.shp')
            filtered_gdf.to_file(out_shp, encoding='cp949') # SHP는 보통 cp949/euc-kr
            print(f"  -> Shapefile 저장됨: {len(filtered_gdf)}개 구역")
        else:
            print(f"  -> 필터링된 데이터가 없습니다.")
    else:
        print(f"Shapefile을 찾을 수 없습니다: {shp_file}")
except Exception as e:
    print(f"Shapefile 처리 실패: {e}")

print("모든 작업이 완료되었습니다.")
