"""
단일 파일 테스트 - 가장 작은 파일로 테스트
"""
import os
from pathlib import Path

source_file = Path(r"d:\git_rk\data\서울시 상권\서울시 상권분석서비스(영역-상권).csv")
target_dir = Path(r"d:\git_rk\CSV")
target_dir.mkdir(exist_ok=True)
target_file = target_dir / source_file.name

print(f"소스 파일: {source_file}")
print(f"파일 존재: {source_file.exists()}")
print(f"파일 크기: {source_file.stat().st_size if source_file.exists() else 'N/A'} bytes")
print()

if source_file.exists():
    # 여러 인코딩 시도
    encodings = ['utf-8', 'cp949', 'euc-kr', 'utf-8-sig']
    
    for encoding in encodings:
        try:
            print(f"시도 중: {encoding}")
            with open(source_file, 'r', encoding=encoding) as f:
                content = f.read()
            print(f"  ✓ 읽기 성공! (길이: {len(content)} 문자)")
            
            # UTF-8로 저장
            with open(target_file, 'w', encoding='utf-8-sig', newline='') as f:
                f.write(content)
            
            print(f"  ✓ 저장 완료: {target_file}")
            print(f"  ✓ 저장 크기: {target_file.stat().st_size} bytes")
            break
        except UnicodeDecodeError as e:
            print(f"  ✗ 실패: {e}")
        except Exception as e:
            print(f"  ✗ 오류: {e}")

print("\n작업 완료!")
