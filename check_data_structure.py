import geopandas as gpd
import pandas as pd
import os

dbf_path = r'd:\git_rk\data\서울시 주요 82장소 영역\서울시 주요 82장소 영역(강남구).dbf'
csv_sample_path = r'd:\git_rk\data\서울시 상권\서울시 상권분석서비스(영역-상권).csv'

print("--- DBF File Content ---")
try:
    gdf = gpd.read_file(dbf_path, encoding='cp949')
    print(gdf.drop(columns='geometry') if 'geometry' in gdf.columns else gdf)
    gangnam_areas = gdf['AREA_NM'].tolist() if 'AREA_NM' in gdf.columns else []
    if not gangnam_areas and '핫플레이스' in gdf.columns: # 예시 컬럼명
        gangnam_areas = gdf['핫플레이스'].tolist()
    print("\nExtracted Area Names:", gangnam_areas)
except Exception as e:
    print(f"Error reading DBF: {e}")

print("\n--- CSV Sample Header (영역-상권) ---")
try:
    df_sample = pd.read_csv(csv_sample_path, encoding='cp949', nrows=5)
    print(df_sample.columns.tolist())
    print(df_sample.head())
except Exception as e:
    try:
        df_sample = pd.read_csv(csv_sample_path, encoding='utf-8', nrows=5)
        print(df_sample.columns.tolist())
        print(df_sample.head())
    except Exception as e2:
        print(f"Error reading CSV: {e2}")
