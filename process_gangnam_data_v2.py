
import pandas as pd
import os
import glob
from datetime import datetime

# 1. 설정
DATA_DIR = r'd:\git_rk\data\서울시 상권'
GANGNAM_LIST_FILE = r'd:\git_rk\data\서울시 주요 82장소 영역\서울시 주요 82장소 목록(강남구).csv'
TIMESTAMP = datetime.now().strftime('%Y%m%d_%H%M%S')
REPORT_DIR = os.path.join(r'd:\git_rk', 'REPORT', f'Gangnam_CSV_{TIMESTAMP}')

os.makedirs(REPORT_DIR, exist_ok=True)

print(f"작업 시작... 저장 경로: {REPORT_DIR}")

# 2. 강남구 목록에서 상권 코드 추출
try:
    # 사용자 제공 목록 읽기
    df_list = pd.read_csv(GANGNAM_LIST_FILE, encoding='utf-8')
    target_names = df_list['AREA_NM'].dropna().unique().tolist()
    print(f"필터링 기준 명칭 추출 완료: {len(target_names)}개")

    # 상권 영역 데이터에서 코드 매칭
    area_file = os.path.join(DATA_DIR, '서울시 상권분석서비스(영역-상권).csv')
    
    # 인코딩 자동 시도 로직
    try:
        df_area = pd.read_csv(area_file, encoding='utf-8-sig')
    except UnicodeDecodeError:
        df_area = pd.read_csv(area_file, encoding='cp949')
    
    # 명칭 매칭을 통한 코드 리스트 생성
    gangnam_codes = df_area[df_area['상권_코드_명'].isin(target_names)]['상권_코드'].unique().tolist()
    print(f"매칭된 상권 코드 개수: {len(gangnam_codes)}개")
    
    if not gangnam_codes:
        print("경고: 명칭 매칭 결과가 없습니다. '자치구_코드_명' 기준 강남구 데이터를 탐색합니다.")
        gangnam_codes = df_area[df_area['자치구_코드_명'] == '강남구']['상권_코드'].unique().tolist()
        print(f"행정구역 기준 추출된 강남구 상권 코드 개수: {len(gangnam_codes)}개")

except Exception as e:
    print(f"필터링 기준 확보 실패: {e}")
    gangnam_codes = []

# 3. 10개 CSV 파일 필터링
if gangnam_codes:
    csv_files = glob.glob(os.path.join(DATA_DIR, '*.csv'))
    for f in csv_files:
        filename = os.path.basename(f)
        print(f"처리 중: {filename}...")
        try:
            # 개별 파일도 인코딩 자동 시도
            try:
                df = pd.read_csv(f, encoding='utf-8-sig')
            except UnicodeDecodeError:
                df = pd.read_csv(f, encoding='cp949')
                
            if '상권_코드' in df.columns:
                filtered_df = df[df['상권_코드'].astype(str).isin([str(c) for c in gangnam_codes])]
                out_path = os.path.join(REPORT_DIR, f'gangnam_{filename}')
                filtered_df.to_csv(out_path, index=False, encoding='utf-8-sig')
                print(f"  -> 저장됨: {len(filtered_df)}행")
            else:
                print(f"  -> '상권_코드' 컬럼이 없어 건너뜁니다.")
        except Exception as e:
            print(f"  -> 처리 실패: {e}")
else:
    print("처리할 상권 코드가 없어 중단합니다.")

print("모든 작업이 완료되었습니다.")
