"""
서울시 주요 82장소 영역 Folium 인터랙티브 지도 생성
"""
import sys
from pathlib import Path

try:
    import geopandas as gpd
    import folium
    import pandas as pd
    from folium import plugins
    import json
    
    print("=" * 60)
    print("서울시 주요 82장소 영역 인터랙티브 지도 생성")
    print("=" * 60)
    print()
    
    # 경로 설정
    shp_path = Path(r"d:\git_rk\data\서울시 상권\서울시 주요 82장소 영역\서울시 주요 82장소 영역.shp")
    excel_path = Path(r"d:\git_rk\data\서울시 상권\서울시 주요 82장소 영역\서울시 주요 82장소 목록.xlsx")
    output_dir = Path(r"d:\git_rk\output")
    output_dir.mkdir(exist_ok=True)
    output_file = output_dir / "서울시_82장소_지도.html"
    
    # 1. Shapefile 로드
    print("[1] Shapefile 데이터 로드")
    # 여러 인코딩 시도
    encodings_to_try = ['utf-8', 'euc-kr', 'cp949']
    gdf = None
    used_encoding = None
    
    for encoding in encodings_to_try:
        try:
            gdf = gpd.read_file(shp_path, encoding=encoding)
            used_encoding = encoding
            print(f"  ✓ 로드 완료: {len(gdf)}개 영역 (인코딩: {encoding})")
            break
        except (UnicodeDecodeError, Exception) as e:
            print(f"  - {encoding} 시도 실패, 다음 인코딩 시도...")
            continue
    
    if gdf is None:
        print("  ✗ 모든 인코딩 시도 실패")
        sys.exit(1)
    
    print(f"  - 원본 좌표계: {gdf.crs}")
    print()
    
    # 2. 좌표계 변환 (WGS84로 변환)
    print("[2] 좌표계 변환")
    if gdf.crs != "EPSG:4326":
        gdf = gdf.to_crs("EPSG:4326")
        print(f"  ✓ WGS84(EPSG:4326)로 변환 완료")
    else:
        print(f"  - 이미 WGS84 좌표계입니다")
    print()
    
    # 3. 데이터 확인
    print("[3] 데이터 구조")
    print(f"  - 컬럼: {list(gdf.columns)}")
    print(f"  - 형상 타입: {gdf.geometry.geom_type.unique()}")
    print()
    
    # 4. 중심 좌표 계산
    print("[4] 지도 중심 좌표 계산")
    bounds = gdf.total_bounds
    center_lat = (bounds[1] + bounds[3]) / 2
    center_lon = (bounds[0] + bounds[2]) / 2
    print(f"  - 중심 좌표: ({center_lat:.6f}, {center_lon:.6f})")
    print()
    
    # 5. Folium 지도 생성
    print("[5] Folium 지도 생성")
    m = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=11,
        tiles='OpenStreetMap'
    )
    
    # 다양한 배경 지도 레이어 추가
    folium.TileLayer('CartoDB positron', name='CartoDB Positron').add_to(m)
    folium.TileLayer('CartoDB dark_matter', name='CartoDB Dark').add_to(m)
    
    print("  ✓ 기본 지도 생성 완료")
    print()
    
    # 6. 색상 팔레트 생성 (82개 장소를 구분하기 위한 색상)
    print("[6] 영역 폴리곤 추가")
    
    # 색상 리스트 (다양한 색상으로 구분)
    colors = [
        '#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A', '#98D8C8',
        '#F7DC6F', '#BB8FCE', '#85C1E2', '#F8B739', '#52B788',
        '#E63946', '#A8DADC', '#457B9D', '#F1FAEE', '#E76F51',
        '#264653', '#2A9D8F', '#E9C46A', '#F4A261', '#E76F51'
    ] * 5  # 20개 색상을 5번 반복하여 100개 확보
    
    # 각 영역을 지도에 추가
    for idx, row in gdf.iterrows():
        # 장소명 추출 (컬럼명은 실제 데이터에 따라 조정 필요)
        # 일반적인 컬럼명: 'NAME', 'name', '장소명', '상권명' 등
        place_name = None
        for col in ['NAME', 'name', '장소명', '상권명', 'PLACE_NAME']:
            if col in gdf.columns:
                place_name = row[col]
                break
        
        if place_name is None:
            place_name = f"장소 {idx + 1}"
        
        # 폴리곤 색상
        color = colors[idx % len(colors)]
        
        # 팝업 내용 생성
        popup_html = f"""
        <div style="font-family: 'Malgun Gothic', sans-serif; width: 250px;">
            <h4 style="margin: 0 0 10px 0; color: {color};">{place_name}</h4>
            <table style="width: 100%; font-size: 12px;">
        """
        
        # 모든 속성 정보 추가
        for col in gdf.columns:
            if col != 'geometry':
                value = row[col]
                if pd.notna(value):
                    popup_html += f"""
                    <tr>
                        <td style="padding: 3px; font-weight: bold;">{col}:</td>
                        <td style="padding: 3px;">{value}</td>
                    </tr>
                    """
        
        popup_html += """
            </table>
        </div>
        """
        
        # 폴리곤 추가
        folium.GeoJson(
            row['geometry'],
            style_function=lambda x, color=color: {
                'fillColor': color,
                'color': 'black',
                'weight': 2,
                'fillOpacity': 0.5
            },
            highlight_function=lambda x: {
                'weight': 4,
                'fillOpacity': 0.7
            },
            tooltip=place_name,
            popup=folium.Popup(popup_html, max_width=300)
        ).add_to(m)
    
    print(f"  ✓ {len(gdf)}개 영역 추가 완료")
    print()
    
    # 7. 레이어 컨트롤 추가
    folium.LayerControl().add_to(m)
    
    # 8. 전체 화면 버튼 추가
    plugins.Fullscreen(
        position='topright',
        title='전체 화면',
        title_cancel='전체 화면 종료',
        force_separate_button=True
    ).add_to(m)
    
    # 9. HTML 파일로 저장
    print("[7] HTML 파일 저장")
    m.save(str(output_file))
    print(f"  ✓ 저장 완료: {output_file}")
    print(f"  ✓ 파일 크기: {output_file.stat().st_size:,} bytes")
    print()
    
    print("=" * 60)
    print("지도 생성 완료!")
    print("=" * 60)
    print()
    print(f"브라우저에서 다음 파일을 열어보세요:")
    print(f"  {output_file}")
    print()
    
except ImportError as e:
    print(f"❌ 필요한 라이브러리가 설치되지 않았습니다: {e}")
    print()
    print("다음 명령어로 설치해주세요:")
    print("  pip install geopandas folium pandas openpyxl")
    sys.exit(1)
except Exception as e:
    print(f"❌ 오류 발생: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
