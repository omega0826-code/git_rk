"""
서울시 상권 CSV 파일을 UTF-8 인코딩으로 변환하여 CSV 폴더에 저장
간단한 버전 - 외부 라이브러리 최소화
"""
import os
import shutil
from pathlib import Path

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

def convert_to_utf8_simple(source_file, target_file):
    """CSV 파일을 UTF-8로 변환 (간단한 방식)"""
    try:
        print(f"처리 중: {source_file.name}")
        
        # 여러 인코딩 시도
        encodings = ['utf-8', 'cp949', 'euc-kr', 'utf-8-sig']
        content = None
        used_encoding = None
        
        for encoding in encodings:
            try:
                with open(source_file, 'r', encoding=encoding) as f:
                    content = f.read()
                used_encoding = encoding
                print(f"  - 읽기 성공: {encoding}")
                break
            except UnicodeDecodeError:
                continue
        
        if content is None:
            print(f"  - 오류: 지원되는 인코딩으로 읽을 수 없음")
            return False
        
        # UTF-8로 저장
        with open(target_file, 'w', encoding='utf-8-sig', newline='') as f:
            f.write(content)
        
        # 파일 크기 확인
        source_size = source_file.stat().st_size
        target_size = target_file.stat().st_size
        
        print(f"  - 저장 완료: {target_file.name}")
        print(f"  - 원본 크기: {source_size:,} bytes")
        print(f"  - 변환 크기: {target_size:,} bytes")
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

for i, filename in enumerate(files_to_convert, 1):
    print(f"[{i}/{len(files_to_convert)}]")
    source_file = source_dir / filename
    target_file = target_dir / filename
    
    if source_file.exists():
        if convert_to_utf8_simple(source_file, target_file):
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
