"""
서울시 상권 CSV 파일을 UTF-8 인코딩으로 변환하여 CSV 폴더에 저장
"""
import os
import pandas as pd
from pathlib import Path
import chardet

# 소스 디렉토리와 타겟 디렉토리 설정
source_dir = Path(r"d:\git_rk\data\서울시 상권")
target_dir = Path(r"d:\git_rk\CSV")

# 타겟 디렉토리 생성
target_dir.mkdir(exist_ok=True)

# 변환할 파일 목록
files_to_convert = [
    "서울시 상권분석서비스(길단위인구-상권).csv",
    "서울시 상권분석서비스(상권변화지표-상권).csv",
    "서울시 상권분석서비스(상주인구-상권).csv",
    "서울시 상권분석서비스(소득소비-상권).csv",
    "서울시 상권분석서비스(영역-상권).csv",
    "서울시 상권분석서비스(점포-상권)_2022년 1분기~2024년 4분기.csv",
    "서울시 상권분석서비스(직장인구-상권).csv",
    "서울시 상권분석서비스(직장인구-상권배후지).csv",
    "서울시 상권분석서비스(집객시설-상권).csv",
    "서울시 상권분석서비스(추정매출-상권)__2022년 1분기~2024년 4분기.csv"
]

def detect_encoding(file_path):
    """파일의 인코딩을 감지"""
    with open(file_path, 'rb') as f:
        result = chardet.detect(f.read(100000))  # 처음 100KB만 읽어서 감지
    return result['encoding']

def convert_to_utf8(source_file, target_file):
    """CSV 파일을 UTF-8로 변환"""
    try:
        # 인코딩 감지
        encoding = detect_encoding(source_file)
        print(f"처리 중: {source_file.name}")
        print(f"  - 감지된 인코딩: {encoding}")
        
        # CSV 파일 읽기
        df = pd.read_csv(source_file, encoding=encoding)
        
        # UTF-8로 저장
        df.to_csv(target_file, index=False, encoding='utf-8-sig')
        
        print(f"  - 저장 완료: {target_file.name}")
        print(f"  - 행 수: {len(df):,}, 열 수: {len(df.columns)}")
        print()
        
        return True
    except Exception as e:
        print(f"  - 오류 발생: {str(e)}")
        print()
        return False

# 메인 실행
print("=" * 60)
print("서울시 상권 CSV 파일 UTF-8 변환 작업 시작")
print("=" * 60)
print()

success_count = 0
fail_count = 0

for filename in files_to_convert:
    source_file = source_dir / filename
    target_file = target_dir / filename
    
    if source_file.exists():
        if convert_to_utf8(source_file, target_file):
            success_count += 1
        else:
            fail_count += 1
    else:
        print(f"파일을 찾을 수 없음: {filename}")
        fail_count += 1
        print()

print("=" * 60)
print("변환 작업 완료")
print("=" * 60)
print(f"성공: {success_count}개")
print(f"실패: {fail_count}개")
print(f"저장 위치: {target_dir}")
print()
