# -*- coding: utf-8 -*-
"""
의원급 피부과 입지 분석 - 데이터 로딩 및 초기 설정
작성일: 2026-02-03
버전: 2.1 (UTF-8 인코딩 안정성 강화 - Go 클라이언트 호환)
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib import font_manager, rc
from math import pi
import os
import sys
import time
import threading
from datetime import datetime
from pathlib import Path

# ============================================================================
# 시스템 인코딩 설정 (Go 클라이언트 호환성)
# ============================================================================
# Windows 환경에서 UTF-8 출력 보장
if sys.platform == 'win32':
    try:
        # Python 3.7+ 에서 UTF-8 모드 활성화
        if hasattr(sys, 'set_int_max_str_digits'):
            import io
            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
            sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    except Exception as e:
        print(f"⚠ 인코딩 설정 경고: {e}", flush=True)


# ============================================================================
# 하트비트 파일 초기화
# ============================================================================
HEARTBEAT_FILE = Path('d:/git_rk/data/서울시 주요 82장소 영역/REPORT/heartbeat.txt')

def write_heartbeat(message):
    """하트비트 파일에 상태 기록 (UTF-8 인코딩)"""
    try:
        with open(HEARTBEAT_FILE, 'a', encoding='utf-8') as f:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            # 단순 문자열 기록 (이중 인코딩 제거)
            f.write(f"[{timestamp}] {message}\n")
            f.flush()
    except Exception as e:
        # 하트비트 실패는 전체 프로세스를 중단하지 않음
        pass  # 조용히 실패 (로그 폭증 방지)

# 하트비트 파일 초기화
try:
    with open(HEARTBEAT_FILE, 'w', encoding='utf-8') as f:
        f.write("=" * 80 + "\n")
        f.write("Data Loading Execution Log\n")
        f.write("=" * 80 + "\n")
        f.flush()
except Exception as e:
    pass  # 조용히 실패

write_heartbeat("START - 데이터 로딩 시작")

print("=" * 70)
print("의원급 피부과 입지 분석 - 데이터 로딩 시작")
print("=" * 70)

# ============================================================================
# 한글 폰트 설정 (타임아웃 적용)
# ============================================================================
print("\n[1/4] 한글 폰트 설정 중...", end=' ', flush=True)
write_heartbeat("STEP 1/4 - 한글 폰트 설정 시작")

try:
    plt.rcParams['font.family'] = 'Malgun Gothic'
    plt.rcParams['axes.unicode_minus'] = False
    print("✓ 완료 (Malgun Gothic 직접 설정)", flush=True)
    write_heartbeat("STEP 1/4 - 한글 폰트 설정 완료 (Malgun Gothic)")
except Exception as e:
    print(f"✗ 실패: {e}", flush=True)
    print("  → 기본 폰트 사용 (한글 깨짐 가능)", flush=True)
    write_heartbeat(f"STEP 1/4 - 한글 폰트 설정 실패: {e}")

# ============================================================================
# 재시도 로직 함수
# ============================================================================
def load_csv_with_retry(file_path, max_retries=3, encoding='utf-8'):
    """재시도 로직이 포함된 CSV 로딩 함수"""
    for attempt in range(1, max_retries + 1):
        try:
            df = pd.read_csv(file_path, encoding=encoding)
            return df
        except Exception as e:
            if attempt < max_retries:
                wait_time = 2 ** attempt  # 지수 백오프: 2초, 4초, 8초
                time.sleep(wait_time)  # 중간 출력 제거 (로그 폭증 방지)
            else:
                raise Exception(f"Max retry exceeded: {e}")

# ============================================================================
# 데이터 로딩 함수
# ============================================================================
def load_data():
    # 경로 설정
    data_path = Path('d:/git_rk/data/서울시 주요 82장소 영역/Gangnam_CSV_20260203_094620/')
    output_base = Path('d:/git_rk/data/서울시 주요 82장소 영역/REPORT/')

    # 산출물 디렉토리 생성
    print("\n[2/4] 산출물 디렉토리 생성 중...", end=' ', flush=True)
    write_heartbeat("STEP 2/4 - 산출물 디렉토리 생성 시작")
    
    dirs = [
        '01_경쟁환경분석', '02_고객분석', '03_인구유동분석', 
        '04_입지조건분석', '05_종합평가', '06_최종리포트'
    ]
    for dir_name in dirs:
        (output_base / dir_name).mkdir(parents=True, exist_ok=True)
    
    print("✓ 완료", flush=True)
    write_heartbeat("STEP 2/4 - 산출물 디렉토리 생성 완료")

    # 데이터 로딩 (강남구 필터링된 9개 파일)
    files_to_load = [
        ('영역-상권', 'gangnam_서울시 상권분석서비스(영역-상권).csv'),
        ('상권변화지표-상권', 'gangnam_서울시 상권분석서비스(상권변화지표-상권).csv'),
        ('점포-상권', 'gangnam_서울시 상권분석서비스(점포-상권)_2022년 1분기~2024년 4분기.csv'),
        ('추정매출-상권', 'gangnam_서울시 상권분석서비스(추정매출-상권)__2022년 1분기~2024년 4분기.csv'),
        ('상주인구-상권', 'gangnam_서울시 상권분석서비스(상주인구-상권).csv'),
        ('직장인구-상권', 'gangnam_서울시 상권분석서비스(직장인구-상권).csv'),
        ('소득소비-상권', 'gangnam_서울시 상권분석서비스(소득소비-상권).csv'),
        ('집객시설-상권', 'gangnam_서울시 상권분석서비스(집객시설-상권).csv'),
        ('길단위인구-상권', 'gangnam_서울시 상권분석서비스(길단위인구-상권).csv')
    ]

    print(f"\n[3/4] 데이터 로딩 중 (총 {len(files_to_load)}개 파일)...", flush=True)
    write_heartbeat(f"STEP 3/4 - 데이터 로딩 시작 (총 {len(files_to_load)}개 파일)")
    
    dataframes = {}
    total_start = time.time()
    
    for idx, (name, filename) in enumerate(files_to_load, 1):
        file_start = time.time()
        print(f"  [{idx}/{len(files_to_load)}] {name:15s} loading...", end=' ')
        write_heartbeat(f"  File {idx}/{len(files_to_load)} loading: {name}")
        
        file_path = data_path / filename
        
        try:
            # 재시도 로직으로 CSV 로딩
            df = load_csv_with_retry(file_path, max_retries=3)
            dataframes[name] = df
            
            file_elapsed = time.time() - file_start
            print(f"OK ({df.shape[0]:,} rows, {df.shape[1]} cols, {file_elapsed:.1f}s)")
            write_heartbeat(f"  File {idx}/{len(files_to_load)} loaded: {name} ({df.shape[0]:,} rows, {df.shape[1]} cols, {file_elapsed:.1f}s)")
            
        except Exception as e:
            print(f"FAIL: {e}")
            write_heartbeat(f"  File {idx}/{len(files_to_load)} failed: {name} - {e}")
            raise Exception(f"File loading failed: {filename} - {e}")
    
    total_elapsed = time.time() - total_start
    print(f"\n  All files loaded (elapsed: {total_elapsed:.1f}s)")
    write_heartbeat(f"STEP 3/4 - Data loading completed (total {total_elapsed:.1f}s)")

    # 전처리
    print("\n[4/4] Preprocessing (date conversion)...", end=' ')
    write_heartbeat("STEP 4/4 - Preprocessing started")
    
    preprocess_start = time.time()
    for df in dataframes.values():
        if '기준_년분기_코드' in df.columns:
            df['기준_년분기_코드'] = df['기준_년분기_코드'].astype(str)
            df['년도'] = df['기준_년분기_코드'].str[:4].astype(int)
            df['분기'] = df['기준_년분기_코드'].str[4:].astype(int)
    
    preprocess_elapsed = time.time() - preprocess_start
    print(f"OK ({preprocess_elapsed:.1f}s)")
    write_heartbeat(f"STEP 4/4 - Preprocessing completed ({preprocess_elapsed:.1f}s)")

    return dataframes, output_base

# ============================================================================
# 메인 실행
# ============================================================================
if __name__ == "__main__":
    try:
        print("\n" + "=" * 70, flush=True)
        dataframes, output_base = load_data()
        
        print("=" * 70, flush=True)
        print("✅ 데이터 로딩 완료!", flush=True)
        print("=" * 70, flush=True)
        print(f"\n📊 로딩된 데이터 요약:", flush=True)
        print(f"  - 상권 수: {len(dataframes['영역-상권'])}개", flush=True)
        print(f"  - 분석 기간: 2022년 1분기 ~ 2024년 4분기", flush=True)
        print(f"  - 산출물 경로: {output_base}", flush=True)
        print(f"  - 하트비트 파일: {HEARTBEAT_FILE}", flush=True)
        print("\n다음 단계: 02_경쟁환경분석.py 실행 또는 99_전체실행.py 사용\n", flush=True)
        
        write_heartbeat("SUCCESS - 데이터 로딩 전체 완료")
        
    except Exception as e:
        print(f"\n❌ 오류 발생: {e}", flush=True)
        write_heartbeat(f"ERROR - 데이터 로딩 실패: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
