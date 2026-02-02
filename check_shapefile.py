"""
Shapefile 데이터 구조 확인 스크립트
"""
import sys

try:
    import geopandas as gpd
    import pandas as pd
    from pathlib import Path
    
    # Shapefile 경로
    shp_path = Path(r"d:\git_rk\data\서울시 상권\서울시 주요 82장소 영역\서울시 주요 82장소 영역.shp")
    excel_path = Path(r"d:\git_rk\data\서울시 상권\서울시 주요 82장소 영역\서울시 주요 82장소 목록.xlsx")
    
    print("=" * 60)
    print("서울시 주요 82장소 영역 데이터 분석")
    print("=" * 60)
    print()
    
    # Shapefile 읽기
    print("[1] Shapefile 데이터 로드")
    gdf = gpd.read_file(shp_path, encoding='cp949')
    print(f"  ✓ 로드 완료: {len(gdf)}개 영역")
    print()
    
    # 좌표계 정보
    print("[2] 좌표계 정보")
    print(f"  - CRS: {gdf.crs}")
    print()
    
    # 데이터 구조
    print("[3] 데이터 구조")
    print(f"  - 컬럼: {list(gdf.columns)}")
    print(f"  - 형상 타입: {gdf.geometry.geom_type.unique()}")
    print()
    
    # 샘플 데이터
    print("[4] 샘플 데이터 (처음 3개)")
    print(gdf.head(3).to_string())
    print()
    
    # 공간 범위
    print("[5] 공간 범위")
    bounds = gdf.total_bounds
    print(f"  - X 범위: {bounds[0]:.6f} ~ {bounds[2]:.6f}")
    print(f"  - Y 범위: {bounds[1]:.6f} ~ {bounds[3]:.6f}")
    print()
    
    # 엑셀 파일 읽기
    if excel_path.exists():
        print("[6] 엑셀 파일 내용")
        df_excel = pd.read_excel(excel_path)
        print(f"  ✓ 로드 완료: {len(df_excel)}개 행")
        print(f"  - 컬럼: {list(df_excel.columns)}")
        print()
        print("  샘플 데이터:")
        print(df_excel.head(3).to_string())
        print()
    
    print("=" * 60)
    print("분석 완료!")
    print("=" * 60)
    
except ImportError as e:
    print(f"필요한 라이브러리가 설치되지 않았습니다: {e}")
    print("\n설치 필요:")
    print("  pip install geopandas pandas openpyxl")
except Exception as e:
    print(f"오류 발생: {e}")
    import traceback
    traceback.print_exc()
