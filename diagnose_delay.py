"""
Python 실행 지연 진단 스크립트
각 단계의 소요 시간을 측정하여 병목 지점을 파악합니다.
"""
import time
import sys
import os

log_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'diagnosis_result.txt')

results = []

def log(msg):
    line = f"[{time.time():.3f}] {msg}"
    results.append(line)
    print(line, flush=True)

# === 1. 기본 환경 정보 ===
t0 = time.time()
log("=" * 60)
log("파이썬 실행 지연 진단 시작")
log(f"Python version: {sys.version}")
log(f"Executable: {sys.executable}")
log(f"CWD: {os.getcwd()}")
log(f"PATH entries: {len(os.environ.get('PATH','').split(os.pathsep))}")

# === 2. 기본 모듈 import 시간 ===
log("\n--- 기본 모듈 import 벤치마크 ---")

modules_to_test = [
    ('os', 'os'),
    ('sys', 'sys'),
    ('json', 'json'),
    ('csv', 'csv'),
    ('re', 're'),
    ('pathlib', 'pathlib'),
    ('datetime', 'datetime'),
    ('collections', 'collections'),
]

for name, mod in modules_to_test:
    t = time.time()
    __import__(mod)
    elapsed = time.time() - t
    log(f"  import {name}: {elapsed:.4f}s")

# === 3. 무거운 라이브러리 import 시간 ===
log("\n--- 무거운 라이브러리 import 벤치마크 ---")

heavy_modules = [
    ('numpy', 'numpy'),
    ('pandas', 'pandas'),
    ('matplotlib', 'matplotlib'),
    ('matplotlib.pyplot', 'matplotlib.pyplot'),
    ('openpyxl', 'openpyxl'),
    ('chardet', 'chardet'),
]

for name, mod in heavy_modules:
    t = time.time()
    try:
        __import__(mod)
        elapsed = time.time() - t
        log(f"  import {name}: {elapsed:.4f}s")
    except ImportError:
        elapsed = time.time() - t
        log(f"  import {name}: FAILED (not installed) ({elapsed:.4f}s)")

# === 4. 한글 matplotlib 관련 ===
log("\n--- koreanize_matplotlib 벤치마크 ---")
t = time.time()
try:
    import koreanize_matplotlib
    elapsed = time.time() - t
    log(f"  import koreanize_matplotlib: {elapsed:.4f}s")
except ImportError:
    elapsed = time.time() - t
    log(f"  import koreanize_matplotlib: FAILED ({elapsed:.4f}s)")
except Exception as e:
    elapsed = time.time() - t
    log(f"  import koreanize_matplotlib: ERROR - {e} ({elapsed:.4f}s)")

# === 5. 파일 I/O 벤치마크 ===
log("\n--- 파일 I/O 벤치마크 ---")
test_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'io_benchmark_temp.txt')
t = time.time()
with open(test_file, 'w', encoding='utf-8') as f:
    for i in range(10000):
        f.write(f"Line {i}: 테스트 데이터 한글 포함\n")
elapsed = time.time() - t
log(f"  Write 10000 lines: {elapsed:.4f}s")

t = time.time()
with open(test_file, 'r', encoding='utf-8') as f:
    data = f.readlines()
elapsed = time.time() - t
log(f"  Read 10000 lines: {elapsed:.4f}s")
os.remove(test_file)

# === 6. .venv 확인 ===
log("\n--- 가상환경 정보 ---")
venv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.venv')
if os.path.exists(venv_path):
    log(f"  .venv 존재: Yes")
    venv_python = os.path.join(venv_path, 'Scripts', 'python.exe')
    if os.path.exists(venv_python):
        log(f"  .venv python: {venv_python}")
    else:
        log(f"  .venv python: NOT FOUND in Scripts")
else:
    log(f"  .venv 존재: No")

is_venv = hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)
log(f"  현재 venv 사용 중: {is_venv}")

# === 7. 안티바이러스 영향 체크 (대리 측정) ===
log("\n--- 디스크 접근 지연 테스트 (다수 파일 생성/삭제) ---")
temp_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '_diag_temp')
os.makedirs(temp_dir, exist_ok=True)
t = time.time()
for i in range(100):
    fp = os.path.join(temp_dir, f'test_{i}.tmp')
    with open(fp, 'w') as f:
        f.write('test')
elapsed_create = time.time() - t

t = time.time()
for i in range(100):
    fp = os.path.join(temp_dir, f'test_{i}.tmp')
    os.remove(fp)
elapsed_delete = time.time() - t
os.rmdir(temp_dir)
log(f"  100 파일 생성: {elapsed_create:.4f}s")
log(f"  100 파일 삭제: {elapsed_delete:.4f}s")
if elapsed_create > 1.0 or elapsed_delete > 1.0:
    log(f"  ⚠ 파일 I/O 지연 감지 - 안티바이러스 또는 디스크 성능 문제 의심")

# === 8. sys.path 분석 ===
log("\n--- sys.path 항목 수 ---")
log(f"  sys.path 항목: {len(sys.path)}")
for p in sys.path[:10]:
    log(f"    {p}")
if len(sys.path) > 10:
    log(f"    ... 외 {len(sys.path)-10}개")

# === 9. pip 캐시/패키지 수 ===
log("\n--- 설치된 패키지 수 ---")
t = time.time()
try:
    import pkg_resources
    packages = list(pkg_resources.working_set)
    elapsed = time.time() - t
    log(f"  설치된 패키지: {len(packages)}개 (조회 시간: {elapsed:.4f}s)")
except Exception as e:
    log(f"  패키지 조회 실패: {e}")

# === 총 소요 시간 ===
total = time.time() - t0
log(f"\n총 진단 소요 시간: {total:.2f}초")
log("=" * 60)

# 파일로 저장
with open(log_file, 'w', encoding='utf-8') as f:
    f.write('\n'.join(results))
print(f"\n결과가 {log_file}에 저장되었습니다.", flush=True)
