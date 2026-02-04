# -*- coding: utf-8 -*-
"""
의원급 피부과 입지 분석 - 환경 진단 스크립트
작성일: 2026-02-03
버전: 1.0
설명: 실행 전 필수 환경을 검증하여 무한 로딩 및 오류를 사전에 방지합니다.
"""

import sys
import os
from datetime import datetime
from pathlib import Path

print("=" * 80)
print("🔍 환경 진단 스크립트 실행 중...")
print("=" * 80)
print(f"진단 시작 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

# 진단 결과 저장
results = []
errors = []
warnings = []

# ============================================================================
# 1. Python 버전 확인
# ============================================================================
print("[1/5] Python 버전 확인...", end=' ', flush=True)
python_version = sys.version_info
if python_version.major >= 3 and python_version.minor >= 8:
    print(f"✓ Python {python_version.major}.{python_version.minor}.{python_version.micro}")
    results.append(f"✓ Python 버전: {python_version.major}.{python_version.minor}.{python_version.micro}")
else:
    print(f"✗ Python {python_version.major}.{python_version.minor}.{python_version.micro} (3.8 이상 필요)")
    errors.append(f"✗ Python 버전 부족: {python_version.major}.{python_version.minor}.{python_version.micro} (3.8 이상 필요)")

# ============================================================================
# 2. 필수 라이브러리 확인
# ============================================================================
print("[2/5] 필수 라이브러리 확인...", flush=True)

required_libraries = {
    'pandas': 'pandas',
    'numpy': 'numpy',
    'matplotlib': 'matplotlib',
    'seaborn': 'seaborn',
}

optional_libraries = {
    'koreanize_matplotlib': 'koreanize_matplotlib',
    'psutil': 'psutil',
}

missing_required = []
missing_optional = []

for name, import_name in required_libraries.items():
    try:
        __import__(import_name)
        print(f"  ✓ {name:25s} 설치됨", flush=True)
        results.append(f"  ✓ {name} 설치됨")
    except ImportError:
        print(f"  ✗ {name:25s} 미설치", flush=True)
        missing_required.append(name)
        errors.append(f"  ✗ {name} 미설치 (필수)")

for name, import_name in optional_libraries.items():
    try:
        __import__(import_name)
        print(f"  ✓ {name:25s} 설치됨 (선택)", flush=True)
        results.append(f"  ✓ {name} 설치됨 (선택)")
    except ImportError:
        print(f"  ⚠ {name:25s} 미설치 (선택)", flush=True)
        missing_optional.append(name)
        warnings.append(f"  ⚠ {name} 미설치 (선택사항)")

# ============================================================================
# 3. 메모리 확인
# ============================================================================
print("\n[3/5] 시스템 메모리 확인...", end=' ', flush=True)
try:
    import psutil
    memory = psutil.virtual_memory()
    available_gb = memory.available / (1024 ** 3)
    total_gb = memory.total / (1024 ** 3)
    
    if available_gb >= 4.0:
        print(f"✓ 사용 가능: {available_gb:.1f}GB / {total_gb:.1f}GB")
        results.append(f"✓ 메모리: {available_gb:.1f}GB 사용 가능")
    elif available_gb >= 2.0:
        print(f"⚠ 사용 가능: {available_gb:.1f}GB / {total_gb:.1f}GB (4GB 이상 권장)")
        warnings.append(f"⚠ 메모리: {available_gb:.1f}GB (4GB 이상 권장)")
    else:
        print(f"✗ 사용 가능: {available_gb:.1f}GB / {total_gb:.1f}GB (부족)")
        errors.append(f"✗ 메모리 부족: {available_gb:.1f}GB (최소 2GB 필요)")
except ImportError:
    print("⚠ psutil 미설치로 확인 불가 (선택사항)")
    warnings.append("⚠ 메모리 확인 불가 (psutil 미설치)")

# ============================================================================
# 4. 데이터 파일 확인
# ============================================================================
print("\n[4/5] 데이터 파일 확인...", flush=True)

data_path = Path('d:/git_rk/data/서울시 주요 82장소 영역/Gangnam_CSV_20260203_094620/')

if not data_path.exists():
    print(f"  ✗ 데이터 디렉토리 없음: {data_path}")
    errors.append(f"  ✗ 데이터 디렉토리 없음: {data_path}")
else:
    required_files = [
        'gangnam_서울시 상권분석서비스(영역-상권).csv',
        'gangnam_서울시 상권분석서비스(점포-상권)_2022년 1분기~2024년 4분기.csv',
        'gangnam_서울시 상권분석서비스(추정매출-상권)__2022년 1분기~2024년 4분기.csv',
        'gangnam_서울시 상권분석서비스(상주인구-상권).csv',
        'gangnam_서울시 상권분석서비스(직장인구-상권).csv',
        'gangnam_서울시 상권분석서비스(소득소비-상권).csv',
        'gangnam_서울시 상권분석서비스(집객시설-상권).csv',
        'gangnam_서울시 상권분석서비스(길단위인구-상권).csv'
    ]
    
    total_size = 0
    missing_files = []
    
    for filename in required_files:
        file_path = data_path / filename
        if file_path.exists():
            size_mb = file_path.stat().st_size / (1024 ** 2)
            total_size += size_mb
            print(f"  ✓ {filename[:30]:30s}... ({size_mb:.1f}MB)", flush=True)
            results.append(f"  ✓ {filename} ({size_mb:.1f}MB)")
        else:
            print(f"  ✗ {filename[:30]:30s}... (없음)", flush=True)
            missing_files.append(filename)
            errors.append(f"  ✗ 파일 없음: {filename}")
    
    if not missing_files:
        print(f"\n  총 데이터 크기: {total_size:.1f}MB")
        results.append(f"  총 데이터 크기: {total_size:.1f}MB")

# ============================================================================
# 5. 디스크 공간 확인
# ============================================================================
print("\n[5/5] 디스크 공간 확인...", end=' ', flush=True)
try:
    import psutil
    output_path = Path('d:/git_rk/data/서울시 주요 82장소 영역/REPORT/')
    disk_usage = psutil.disk_usage(str(output_path))
    free_gb = disk_usage.free / (1024 ** 3)
    
    if free_gb >= 1.0:
        print(f"✓ 여유 공간: {free_gb:.1f}GB")
        results.append(f"✓ 디스크 여유 공간: {free_gb:.1f}GB")
    else:
        print(f"⚠ 여유 공간: {free_gb:.1f}GB (1GB 이상 권장)")
        warnings.append(f"⚠ 디스크 공간: {free_gb:.1f}GB (1GB 이상 권장)")
except ImportError:
    print("⚠ psutil 미설치로 확인 불가")
    warnings.append("⚠ 디스크 공간 확인 불가 (psutil 미설치)")

# ============================================================================
# 진단 결과 요약
# ============================================================================
print("\n" + "=" * 80)
print("📋 진단 결과 요약")
print("=" * 80)

if not errors:
    print("✅ 모든 필수 항목 통과! 스크립트 실행 가능합니다.\n")
else:
    print(f"❌ {len(errors)}개의 오류 발견! 아래 문제를 해결해야 합니다.\n")
    for error in errors:
        print(error)

if warnings:
    print(f"\n⚠️  {len(warnings)}개의 경고 사항:\n")
    for warning in warnings:
        print(warning)

# ============================================================================
# 해결 방법 안내
# ============================================================================
if missing_required:
    print("\n" + "=" * 80)
    print("💡 필수 라이브러리 설치 방법")
    print("=" * 80)
    print("다음 명령어를 실행하세요:\n")
    print(f"pip install {' '.join(missing_required)}")

if missing_optional:
    print("\n" + "=" * 80)
    print("💡 선택 라이브러리 설치 방법 (권장)")
    print("=" * 80)
    print("다음 명령어를 실행하세요:\n")
    print(f"pip install {' '.join(missing_optional)}")

# ============================================================================
# 결과 파일 저장
# ============================================================================
output_file = Path('d:/git_rk/data/서울시 주요 82장소 영역/REPORT/환경진단_결과.txt')
with open(output_file, 'w', encoding='utf-8') as f:
    f.write("=" * 80 + "\n")
    f.write("환경 진단 결과\n")
    f.write("=" * 80 + "\n")
    f.write(f"진단 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
    
    f.write("✅ 통과 항목:\n")
    for result in results:
        f.write(result + "\n")
    
    if warnings:
        f.write("\n⚠️  경고 항목:\n")
        for warning in warnings:
            f.write(warning + "\n")
    
    if errors:
        f.write("\n❌ 오류 항목:\n")
        for error in errors:
            f.write(error + "\n")
    
    if missing_required:
        f.write("\n필수 라이브러리 설치 명령:\n")
        f.write(f"pip install {' '.join(missing_required)}\n")
    
    if missing_optional:
        f.write("\n선택 라이브러리 설치 명령:\n")
        f.write(f"pip install {' '.join(missing_optional)}\n")

print(f"\n📄 진단 결과가 저장되었습니다: {output_file}")
print("=" * 80)

# 종료 코드 반환
sys.exit(0 if not errors else 1)
