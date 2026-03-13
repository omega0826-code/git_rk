"""
202601 폴더 내 파일을 그룹별로 분류하여 최신 1개만 남기고 나머지를 archive/로 이동
파일명 패턴: {prefix}_{YYMMDD}_{HHMM}.csv  (예: company_cleaned_260307_1754F.csv)
"""
import sys, io, os, re, shutil
from pathlib import Path
from collections import defaultdict

if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

TARGET = Path(r"d:\git_rk\output\company_database\factory_on\202601")
ARCHIVE = TARGET / "archive"

# 날짜_시각 패턴: _YYMMDD_HHMM 또는 _YYMMDD_HHMM + suffix
DATE_PATTERN = re.compile(r'^(.+?)_(\d{6})_(\d{4}[A-Z]?)(.*)\.csv$')

# 파일 그룹화
groups = defaultdict(list)
standalone = []

for f in sorted(TARGET.iterdir()):
    if not f.is_file() or f.suffix.lower() != '.csv':
        continue
    m = DATE_PATTERN.match(f.name)
    if m:
        prefix = m.group(1)       # e.g. company_cleaned
        date_str = m.group(2)     # e.g. 260307
        time_str = m.group(3)     # e.g. 1754F
        suffix = m.group(4)       # e.g. _classified
        group_key = f"{prefix}{suffix}"
        # 정렬 키: 날짜+시각 (숫자 부분만)
        sort_key = date_str + re.sub(r'[^0-9]', '', time_str)
        groups[group_key].append((sort_key, f))
    else:
        standalone.append(f)

print("=" * 60)
print("파일 그룹 분석 결과")
print("=" * 60)

to_archive = []
to_keep = []

for key in sorted(groups.keys()):
    files = sorted(groups[key], key=lambda x: x[0])
    latest = files[-1][1]
    old = [f for _, f in files[:-1]]
    to_keep.append(latest)
    to_archive.extend(old)
    
    print(f"\n[{key}] ({len(files)}개)")
    for sort_key, f in files:
        marker = " << KEEP" if f == latest else " -> archive"
        size_mb = f.stat().st_size / (1024 * 1024)
        print(f"  {f.name} ({size_mb:.1f}MB){marker}")

if standalone:
    print(f"\n[standalone] ({len(standalone)}개) - 날짜 패턴 없음, 유지")
    for f in standalone:
        size_mb = f.stat().st_size / (1024 * 1024)
        print(f"  {f.name} ({size_mb:.1f}MB) << KEEP")
    to_keep.extend(standalone)

print(f"\n{'=' * 60}")
print(f"유지: {len(to_keep)}개 / archive 이동: {len(to_archive)}개")
print(f"{'=' * 60}")

if not to_archive:
    print("\n이동할 파일이 없습니다.")
else:
    ARCHIVE.mkdir(exist_ok=True)
    print(f"\n[실행] archive 폴더 생성: {ARCHIVE}")
    for f in to_archive:
        dst = ARCHIVE / f.name
        shutil.move(str(f), str(dst))
        print(f"  [OK] {f.name} -> archive/")
    print(f"\n[완료] {len(to_archive)}개 파일을 archive/로 이동했습니다.")
