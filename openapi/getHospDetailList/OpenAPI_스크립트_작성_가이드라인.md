# OpenAPI 스크립트 작성 가이드라인

## 📋 목차
1. [개요](#개요)
2. [표준 스크립트 구조](#표준-스크립트-구조)
3. [핵심 구현 패턴](#핵심-구현-패턴)
4. [코드 주석 작성 가이드](#코드-주석-작성-가이드)
5. [테스트 및 검증](#테스트-및-검증)
6. [문서화 표준](#문서화-표준)

---

## 개요

이 문서는 공공데이터포털의 OpenAPI를 활용한 Python 스크립트 개발 시 참고할 수 있는 범용 가이드라인입니다. 검증된 패턴과 베스트 프랙티스를 제공하여 일관성 있고 안정적인 스크립트 개발을 지원합니다.

### 적용 대상
- 공공데이터포털 OpenAPI를 활용한 데이터 수집 스크립트
- REST API 기반 대량 데이터 다운로드 스크립트
- Excel 입출력을 포함한 데이터 처리 스크립트

---

## 표준 스크립트 구조

### 파일 구조

```python
"""
스크립트 제목
================================================================================
작성일: YYYY-MM-DD
목적: 스크립트의 목적 간략히 설명
입력: 입력 데이터 설명
출력: 출력 데이터 설명
================================================================================
"""

# ============================================================================
# 1. 임포트 섹션
# ============================================================================
import requests
import json
from typing import Dict, List, Optional
import pandas as pd
from datetime import datetime
import time
import os
from pathlib import Path

# ============================================================================
# 2. 설정 섹션 (Configuration)
# ============================================================================
# API 기본 정보
API_BASE_URL = "http://apis.data.go.kr/..."
SERVICE_KEY = "발급받은_인증키"
USE_ENCODED_KEY = True

# 재시도 설정
MAX_RETRIES = 3
RETRY_DELAY = 1

# 타임아웃 설정
CONNECT_TIMEOUT = 10
READ_TIMEOUT = 60

# 체크포인트 설정
ENABLE_CHECKPOINT = True
CHECKPOINT_INTERVAL = 5

# ============================================================================
# 3. API 호출 함수
# ============================================================================
def api_call_function(...):
    """API 호출 함수 (재시도 로직 포함)"""
    pass

# ============================================================================
# 4. 데이터 처리 함수
# ============================================================================
def save_checkpoint(...):
    """체크포인트 저장"""
    pass

def load_checkpoint(...):
    """체크포인트 로드"""
    pass

def save_to_excel(...):
    """Excel 저장"""
    pass

# ============================================================================
# 5. 메인 실행 코드
# ============================================================================
def main():
    """메인 실행 함수"""
    pass

if __name__ == "__main__":
    main()
```

---

## 핵심 구현 패턴

### 1. 재시도 로직 (Retry with Exponential Backoff)

**목적**: 일시적인 네트워크 오류나 API 서버 과부하 시 자동으로 재시도

**구현 패턴**:
```python
def api_call_with_retry(url, params, max_retries=3, retry_delay=1):
    """재시도 로직이 포함된 API 호출"""
    last_exception = None
    
    for attempt in range(max_retries + 1):
        try:
            if attempt > 0:
                # 지수 백오프: 1초, 2초, 4초, ...
                wait_time = retry_delay * (2 ** (attempt - 1))
                print(f"[재시도 {attempt}/{max_retries}] {wait_time}초 대기 중...")
                time.sleep(wait_time)
            
            # API 호출
            response = requests.get(url, params=params, timeout=(10, 60))
            response.raise_for_status()
            
            data = response.json()
            
            # API 응답 코드 확인
            if data['response']['header']['resultCode'] != '00':
                raise Exception(f"API Error: {data['response']['header']['resultMsg']}")
            
            return data
            
        except requests.exceptions.Timeout:
            last_exception = Exception("API 호출 시간 초과")
            if attempt < max_retries:
                print(f"[경고] {last_exception}")
                continue
        except requests.exceptions.ConnectionError:
            last_exception = Exception("네트워크 연결 오류")
            if attempt < max_retries:
                print(f"[경고] {last_exception}")
                continue
        except requests.exceptions.HTTPError as e:
            # HTTP 에러는 재시도하지 않음
            last_exception = Exception(f"HTTP Error: {e}")
            break
        except Exception as e:
            last_exception = e
            if attempt < max_retries:
                print(f"[경고] {last_exception}")
                continue
    
    # 모든 재시도 실패
    raise last_exception
```

**핵심 포인트**:
- 지수 백오프로 대기 시간 증가 (1초 → 2초 → 4초)
- HTTP 에러(인증 오류 등)는 재시도하지 않음
- 네트워크 오류와 타임아웃만 재시도

---

### 2. 체크포인트 기능 (Checkpoint & Resume)

**목적**: 중단된 작업을 이어서 진행할 수 있도록 진행상황 저장

**구현 패턴**:

#### 체크포인트 저장
```python
def save_checkpoint(data: Dict, checkpoint_file: str):
    """진행상황을 JSON 파일로 저장"""
    try:
        with open(checkpoint_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"[체크포인트 저장] {checkpoint_file}")
    except Exception as e:
        print(f"[경고] 체크포인트 저장 실패: {e}")
```

#### 체크포인트 로드
```python
def load_checkpoint(checkpoint_file: str) -> Optional[Dict]:
    """저장된 진행상황 로드"""
    if not os.path.exists(checkpoint_file):
        return None
    
    try:
        with open(checkpoint_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        print(f"[체크포인트 로드] {checkpoint_file}")
        print(f"  - 이전 진행: {data.get('processed_count', 0)}건 처리 완료")
        return data
    except Exception as e:
        print(f"[경고] 체크포인트 로드 실패: {e}")
        return None
```

#### 메인 로직에서 사용
```python
def process_all_items(items, checkpoint_file="checkpoint.json"):
    """체크포인트를 활용한 전체 항목 처리"""
    
    # 이전 진행상황 로드
    checkpoint = load_checkpoint(checkpoint_file)
    processed_indices = set(checkpoint.get('processed_indices', [])) if checkpoint else set()
    results = checkpoint.get('results', []) if checkpoint else []
    
    try:
        for idx, item in enumerate(items):
            # 이미 처리된 항목은 건너뛰기
            if idx in processed_indices:
                continue
            
            # 항목 처리
            result = process_item(item)
            results.append(result)
            processed_indices.add(idx)
            
            # 일정 간격마다 체크포인트 저장
            if len(processed_indices) % 5 == 0:
                checkpoint_data = {
                    'processed_count': len(processed_indices),
                    'processed_indices': list(processed_indices),
                    'results': results,
                    'timestamp': datetime.now().isoformat()
                }
                save_checkpoint(checkpoint_data, checkpoint_file)
        
        # 완료 후 체크포인트 파일 삭제
        if os.path.exists(checkpoint_file):
            os.remove(checkpoint_file)
        
        return results
        
    except Exception as e:
        # 오류 발생 시 현재까지 진행상황 저장
        checkpoint_data = {
            'processed_count': len(processed_indices),
            'processed_indices': list(processed_indices),
            'results': results,
            'timestamp': datetime.now().isoformat(),
            'error': str(e)
        }
        save_checkpoint(checkpoint_data, checkpoint_file)
        print(f"\n[오류] 진행상황이 저장되었습니다. 다시 실행하면 이어서 진행됩니다.")
        raise
```

**핵심 포인트**:
- 처리된 인덱스를 set으로 관리하여 중복 처리 방지
- 일정 간격(예: 5건)마다 자동 저장
- 오류 발생 시에도 진행상황 저장
- 완료 후 체크포인트 파일 자동 삭제

---

### 3. 진행률 표시 (Progress Tracking)

**목적**: 사용자에게 현재 진행 상황과 예상 완료 시간 제공

**구현 패턴**:
```python
def process_with_progress(items, total_count):
    """진행률 표시가 포함된 처리"""
    start_time = time.time()
    processed_count = 0
    
    for idx, item in enumerate(items):
        # 항목 처리
        process_item(item)
        processed_count += 1
        
        # 진행률 계산
        progress_pct = (processed_count / total_count * 100) if total_count > 0 else 0
        elapsed_time = time.time() - start_time
        
        # 예상 남은 시간 계산
        if processed_count > 0 and elapsed_time > 0:
            items_per_sec = processed_count / elapsed_time
            remaining_items = total_count - processed_count
            eta_seconds = remaining_items / items_per_sec if items_per_sec > 0 else 0
            eta_str = f", 예상 남은 시간: {int(eta_seconds)}초"
        else:
            eta_str = ""
        
        # 진행률 출력
        print(f"[진행] {processed_count}/{total_count}건 ({progress_pct:.1f}%){eta_str}")
```

**핵심 포인트**:
- 처리 속도 기반으로 예상 남은 시간 계산
- 백분율과 절대 건수 모두 표시
- 초 단위로 간단하게 표시

---

### 4. Excel 입출력 처리

**목적**: Excel 파일을 안정적으로 읽고 쓰기

**구현 패턴**:

#### Excel 읽기
```python
def load_excel_with_validation(filename: str, required_columns: List[str] = None) -> pd.DataFrame:
    """유효성 검증이 포함된 Excel 읽기"""
    print(f"[Excel 읽기] {filename}")
    
    if not os.path.exists(filename):
        raise FileNotFoundError(f"파일을 찾을 수 없습니다: {filename}")
    
    df = pd.read_excel(filename)
    print(f"  - 총 {len(df)}건")
    print(f"  - 컬럼: {', '.join(df.columns.tolist())}")
    
    # 필수 컬럼 확인
    if required_columns:
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            raise ValueError(f"필수 컬럼이 없습니다: {missing_columns}")
    
    return df
```

#### Excel 저장
```python
def save_to_excel_safe(data: List[Dict], filename: str, column_order: List[str] = None):
    """안전한 Excel 저장"""
    if not data:
        print("[경고] 저장할 데이터가 없습니다.")
        return
    
    # 데이터프레임 생성
    df = pd.DataFrame(data)
    
    # 컬럼 순서 정리
    if column_order:
        existing_columns = [col for col in column_order if col in df.columns]
        other_columns = [col for col in df.columns if col not in column_order]
        df = df[existing_columns + other_columns]
    
    # 디렉토리 생성
    output_dir = Path(filename).parent
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Excel 저장
    df.to_excel(filename, index=False, engine='openpyxl')
    print(f"[저장 완료] {filename} ({len(df)}건, {len(df.columns)}개 컬럼)")
```

---

## 코드 주석 작성 가이드

### 1. 파일 헤더 주석

```python
"""
스크립트 제목
================================================================================
작성일: 2026-01-15
목적: 이 스크립트의 목적을 명확하게 설명
입력: 입력 데이터 형식 및 위치
출력: 출력 데이터 형식 및 위치
참고: 관련 문서나 API 링크
================================================================================
"""
```

### 2. 함수 Docstring

```python
def function_name(param1: str, param2: int = 10) -> Dict:
    """
    함수의 목적을 한 줄로 요약
    
    더 자세한 설명이 필요한 경우 여기에 작성합니다.
    여러 줄로 작성 가능합니다.
    
    Parameters:
    -----------
    param1 : str
        파라미터 설명
    param2 : int, optional
        파라미터 설명 (기본값: 10)
    
    Returns:
    --------
    dict
        반환값 설명
    
    Raises:
    -------
    ValueError
        발생 가능한 예외 설명
    
    Examples:
    ---------
    >>> result = function_name("test", 20)
    >>> print(result)
    """
    pass
```

### 3. 섹션 구분 주석

```python
# ============================================================================
# 섹션 제목 (예: API 호출 함수)
# ============================================================================
```

### 4. 인라인 주석

```python
# 복잡한 로직에 대한 설명
result = complex_calculation()

# TODO: 향후 개선 사항
# FIXME: 알려진 버그
# NOTE: 중요한 참고사항
```

---

## 테스트 및 검증

### 1. 단계별 테스트

#### 1단계: API 연결 테스트
```python
def test_api_connection():
    """API 연결 가능 여부 테스트"""
    try:
        response = requests.get(API_BASE_URL, timeout=10)
        print(f"✓ API 연결 성공 (상태 코드: {response.status_code})")
        return True
    except Exception as e:
        print(f"✗ API 연결 실패: {e}")
        return False
```

#### 2단계: 소량 데이터 테스트
```python
def test_with_sample_data(max_items=3):
    """소량 데이터로 전체 플로우 테스트"""
    print(f"[테스트] 최대 {max_items}건으로 테스트 실행")
    # 실제 로직 실행
```

#### 3단계: 체크포인트 기능 테스트
- 중간에 강제 중단 (Ctrl+C)
- 재실행하여 이어서 진행 확인

### 2. 에러 시나리오 테스트

```python
def test_error_scenarios():
    """다양한 에러 시나리오 테스트"""
    
    # 1. 잘못된 인증키
    test_with_invalid_key()
    
    # 2. 존재하지 않는 데이터
    test_with_nonexistent_data()
    
    # 3. 네트워크 오류 시뮬레이션
    test_network_error()
```

---

## 문서화 표준

### 1. README.md 구조

```markdown
# 프로젝트명

## 개요
프로젝트 설명

## 요구사항
- Python 3.8+
- 필요한 라이브러리

## 설치
```bash
pip install -r requirements.txt
```

## 사용법
```bash
python script.py
```

## 설정
- API 키 설정 방법
- 입력 파일 형식

## 출력
- 출력 파일 형식
- 저장 위치

## 문제 해결
- 자주 발생하는 오류와 해결 방법
```

### 2. 개발 과정 문서 (REPORT 폴더)

```markdown
# 개발 과정 상세 문서

## 요구사항 분석
- 분석 내용

## 기술적 의사결정
- 선택한 기술과 이유

## 구현 세부사항
- 주요 구현 내용

## 테스트 결과
- 테스트 시나리오와 결과

## 알려진 이슈
- 현재 알려진 문제점

## 향후 개선 사항
- 개선 계획
```

---

## 부록: 체크리스트

### 스크립트 개발 완료 체크리스트

- [ ] 파일 헤더 주석 작성
- [ ] 모든 함수에 Docstring 작성
- [ ] 재시도 로직 구현
- [ ] 체크포인트 기능 구현
- [ ] 진행률 표시 구현
- [ ] 에러 처리 구현
- [ ] 소량 데이터로 테스트
- [ ] 전체 데이터로 테스트
- [ ] 체크포인트 기능 테스트
- [ ] README.md 작성
- [ ] 개발 과정 문서 작성
- [ ] 코드 정리 및 리팩토링

---

## 버전 정보
- **문서 버전**: 1.0
- **최종 수정일**: 2026-01-15
- **작성자**: OpenAPI 스크립트 개발팀
