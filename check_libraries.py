"""
라이브러리 설치 확인 스크립트
"""
import sys

print("=" * 60)
print("라이브러리 설치 확인")
print("=" * 60)
print()

# 필수 라이브러리 확인
libraries = {
    'geopandas': 'geopandas',
    'folium': 'folium',
    'pandas': 'pandas',
    'openpyxl': 'openpyxl'
}

missing = []
installed = []

for name, import_name in libraries.items():
    try:
        __import__(import_name)
        installed.append(name)
        print(f"✓ {name}: 설치됨")
    except ImportError:
        missing.append(name)
        print(f"✗ {name}: 설치 필요")

print()
print("=" * 60)

if missing:
    print(f"❌ {len(missing)}개 라이브러리 설치 필요")
    print()
    print("다음 명령어로 설치하세요:")
    print(f"  pip install {' '.join(missing)}")
    sys.exit(1)
else:
    print(f"✓ 모든 라이브러리 설치 완료 ({len(installed)}개)")
    sys.exit(0)
