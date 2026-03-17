"""
의료기관별상세정보 조회 API 호출 스크립트
================================================================================
작성일: 2026-01-15
목적: 건강보험심사평가원 의료기관별상세정보서비스 API를 사용하여 병원 상세정보 조회
입력: 병원기본목록 Excel 파일 (암호화된 요양기호 포함)
출력: 병원 상세정보 Excel 파일
================================================================================
"""

import requests
import json
from typing import Dict, List, Optional
import pandas as pd
from datetime import datetime
import time
import os
from pathlib import Path

# ============================================================================
# 설정 (Configuration)
# ============================================================================

# API 기본 정보
# 참고: 공공데이터포털에서 API 상세 명세를 확인하여 정확한 operation 이름을 설정하세요
# 일반적인 패턴: /getDtlInfo, /getMadmDtlInfo 등
API_BASE_URL = "http://apis.data.go.kr/B551182/MadmDtlInfoService2.7/getDtlInfo"

# 인증키 설정 (여기에 발급받은 인증키를 입력하세요)
# 주의: 공공데이터포털에서 복사한 디코딩 키를 사용하세요
SERVICE_KEY = "Bk8LikYxwbpxf1OKF0mYYonK9RNmYo/mmgtNsZ41rRNxMuIh5s7RgflEXp+Xwp3R0FDR2j01gx62Hc++Jzc2pw=="

# API 키 타입 설정 (True: 인코딩 키, False: 디코딩 키)
USE_ENCODED_KEY = True

# 재시도 설정
MAX_RETRIES = 3          # 최대 재시도 횟수
RETRY_DELAY = 1          # 초기 재시도 대기 시간 (초)

# 타임아웃 설정
CONNECT_TIMEOUT = 10     # 연결 타임아웃 (초)
READ_TIMEOUT = 60        # 읽기 타임아웃 (초)

# 체크포인트 설정
ENABLE_CHECKPOINT = True # 진행상황 저장 활성화
CHECKPOINT_INTERVAL = 5  # 체크포인트 저장 간격 (건수 단위)

# 입력 파일 설정
INPUT_EXCEL_FILE = "D:/git_rk/openapi/getHospBasisList/data/서울_강남구_피부과_20260113_205835.xlsx"
YKIHO_COLUMN = "암호화요양기호"  # Excel 파일에서 요양기호가 저장된 컬럼명 (실제 컬럼명으로 수정 필요)

# ============================================================================
# API 호출 함수
# ============================================================================

def get_hospital_detail(
    service_key: str,
    use_encoded_key: bool = False,
    ykiho: str = None,
    max_retries: int = MAX_RETRIES,
    retry_delay: int = RETRY_DELAY
) -> Dict:
    """
    병원 상세정보 API 호출 함수 (재시도 로직 포함)
    
    Parameters:
    -----------
    service_key : str
        공공데이터포털에서 발급받은 인증키 (인코딩 또는 디코딩)
    use_encoded_key : bool
        True: 인코딩 키 사용 (URL에 직접 포함)
        False: 디코딩 키 사용 (params로 전달)
    ykiho : str
        암호화된 요양기호
    max_retries : int
        최대 재시도 횟수 (기본값: 3)
    retry_delay : int
        초기 재시도 대기 시간 (기본값: 1초)
    
    Returns:
    --------
    dict
        API 응답 데이터 (JSON 형식)
    
    Raises:
    -------
    Exception
        API 호출 실패 시 예외 발생
    """
    
    # 요청 파라미터 구성
    params = {
        'ykiho': ykiho,      # 암호화된 요양기호
        '_type': 'json'      # JSON 형식으로 응답 받기
    }
    
    # API 키 처리 방식 결정
    if use_encoded_key:
        # 인코딩 키: URL에 직접 포함
        api_url = f"{API_BASE_URL}?ServiceKey={service_key}"
    else:
        # 디코딩 키: params로 전달 (requests가 자동 인코딩)
        api_url = API_BASE_URL
        params['ServiceKey'] = service_key
    
    # 재시도 로직
    last_exception = None
    for attempt in range(max_retries + 1):
        try:
            if attempt > 0:
                wait_time = retry_delay * (2 ** (attempt - 1))  # 지수 백오프
                print(f"[재시도 {attempt}/{max_retries}] {wait_time}초 대기 중...")
                time.sleep(wait_time)
            
            # API 호출
            response = requests.get(
                api_url, 
                params=params, 
                timeout=(CONNECT_TIMEOUT, READ_TIMEOUT)
            )
            
            # HTTP 상태 코드 확인
            response.raise_for_status()
            
            # JSON 파싱
            data = response.json()
            
            # API 응답 헤더 확인
            header = data['response']['header']
            if header['resultCode'] != '00':
                raise Exception(f"API 오류 [{header['resultCode']}]: {header['resultMsg']}")
            
            return data
            
        except requests.exceptions.Timeout as e:
            last_exception = Exception(f"API 호출 시간 초과 (연결: {CONNECT_TIMEOUT}초, 읽기: {READ_TIMEOUT}초)")
            if attempt < max_retries:
                print(f"[경고] {last_exception}")
                continue
        except requests.exceptions.ConnectionError as e:
            last_exception = Exception("네트워크 연결 오류. 인터넷 연결을 확인하세요.")
            if attempt < max_retries:
                print(f"[경고] {last_exception}")
                continue
        except requests.exceptions.HTTPError as e:
            # HTTP 에러 발생 시 응답 내용 출력
            error_msg = f"HTTP 오류: {e}"
            try:
                error_response = e.response.text
                print(f"\n[API 응답 내용]\n{error_response}\n")
                error_msg += f"\n응답 내용: {error_response}"
            except:
                pass
            last_exception = Exception(error_msg)
            # HTTP 에러는 재시도하지 않음 (인증 오류 등)
            break
        except KeyError as e:
            last_exception = Exception(f"응답 데이터 형식 오류: {e}")
            break
        except Exception as e:
            last_exception = Exception(f"예상치 못한 오류: {e}")
            if attempt < max_retries:
                print(f"[경고] {last_exception}")
                continue
    
    # 모든 재시도 실패
    raise last_exception


def save_checkpoint(data: Dict, checkpoint_file: str):
    """
    체크포인트 저장
    
    Parameters:
    -----------
    data : dict
        저장할 데이터
    checkpoint_file : str
        체크포인트 파일 경로
    """
    try:
        with open(checkpoint_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"[체크포인트 저장] {checkpoint_file}")
    except Exception as e:
        print(f"[경고] 체크포인트 저장 실패: {e}")


def load_checkpoint(checkpoint_file: str) -> Optional[Dict]:
    """
    체크포인트 로드
    
    Parameters:
    -----------
    checkpoint_file : str
        체크포인트 파일 경로
    
    Returns:
    --------
    dict or None
        저장된 데이터 또는 None
    """
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


def load_hospital_list_from_excel(filename: str, ykiho_column: str = None) -> pd.DataFrame:
    """
    Excel 파일에서 병원 목록 읽기
    
    Parameters:
    -----------
    filename : str
        Excel 파일 경로
    ykiho_column : str, optional
        요양기호 컬럼명 (None이면 자동 탐지)
    
    Returns:
    --------
    pd.DataFrame
        병원 목록 데이터프레임
    """
    print(f"[Excel 읽기] {filename}")
    df = pd.read_excel(filename)
    
    print(f"  - 총 {len(df)}건")
    print(f"  - 컬럼: {', '.join(df.columns.tolist())}")
    
    # 요양기호 컬럼 자동 탐지
    if ykiho_column is None:
        possible_columns = ['ykiho', '암호화요양기호', '요양기호', 'YKIHO']
        for col in possible_columns:
            if col in df.columns:
                ykiho_column = col
                print(f"  - 요양기호 컬럼 자동 탐지: {ykiho_column}")
                break
        
        if ykiho_column is None:
            raise Exception(f"요양기호 컬럼을 찾을 수 없습니다. 가능한 컬럼: {df.columns.tolist()}")
    
    # 요양기호 컬럼 존재 확인
    if ykiho_column not in df.columns:
        raise Exception(f"컬럼 '{ykiho_column}'을(를) 찾을 수 없습니다. 사용 가능한 컬럼: {df.columns.tolist()}")
    
    return df


def get_all_hospital_details(
    service_key: str,
    use_encoded_key: bool = False,
    hospital_df: pd.DataFrame = None,
    ykiho_column: str = 'ykiho',
    max_results: Optional[int] = None,
    enable_checkpoint: bool = ENABLE_CHECKPOINT,
    checkpoint_file: Optional[str] = None
) -> List[Dict]:
    """
    모든 병원의 상세정보를 가져오는 함수 (체크포인트 지원)
    
    Parameters:
    -----------
    service_key : str
        공공데이터포털에서 발급받은 인증키
    use_encoded_key : bool
        True: 인코딩 키 사용, False: 디코딩 키 사용
    hospital_df : pd.DataFrame
        병원 목록 데이터프레임
    ykiho_column : str
        요양기호 컬럼명
    max_results : int, optional
        최대 결과 수 (None이면 전체 조회)
    enable_checkpoint : bool
        체크포인트 기능 활성화 여부
    checkpoint_file : str, optional
        체크포인트 파일 경로 (None이면 자동 생성)
    
    Returns:
    --------
    list
        모든 병원 상세정보 리스트
    """
    
    # 체크포인트 파일 설정
    if enable_checkpoint and checkpoint_file is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        checkpoint_file = f"checkpoint_detail_{timestamp}.json"
    
    # 이전 진행상황 로드
    all_items = []
    processed_indices = set()
    start_index = 0
    
    if enable_checkpoint and checkpoint_file:
        checkpoint_data = load_checkpoint(checkpoint_file)
        if checkpoint_data:
            all_items = checkpoint_data.get('items', [])
            processed_indices = set(checkpoint_data.get('processed_indices', []))
            start_index = checkpoint_data.get('last_index', 0) + 1
            print(f"[재개] 인덱스 {start_index}부터 계속 진행합니다.")
    
    total_count = len(hospital_df)
    if max_results:
        total_count = min(total_count, max_results)
    
    start_time = time.time()
    
    try:
        for idx in range(start_index, total_count):
            # 이미 처리된 인덱스는 건너뛰기
            if idx in processed_indices:
                continue
            
            row = hospital_df.iloc[idx]
            ykiho = row[ykiho_column]
            
            # 요양기호 유효성 확인
            if pd.isna(ykiho) or str(ykiho).strip() == '':
                print(f"[경고] 인덱스 {idx}: 요양기호가 비어있습니다. 건너뜁니다.")
                processed_indices.add(idx)
                continue
            
            # 진행률 계산
            processed_count = len(processed_indices)
            progress_pct = (processed_count / total_count * 100) if total_count > 0 else 0
            elapsed_time = time.time() - start_time
            
            if processed_count > 0 and elapsed_time > 0:
                items_per_sec = processed_count / elapsed_time
                remaining_items = total_count - processed_count
                eta_seconds = remaining_items / items_per_sec if items_per_sec > 0 else 0
                eta_str = f", 예상 남은 시간: {int(eta_seconds)}초"
            else:
                eta_str = ""
            
            print(f"[진행] {processed_count}/{total_count}건 ({progress_pct:.1f}%){eta_str}")
            print(f"  - 인덱스 {idx}: {row.get('yadmNm', '알 수 없음')} (요양기호: {ykiho[:20]}...)")
            
            # API 호출
            try:
                data = get_hospital_detail(
                    service_key=service_key,
                    use_encoded_key=use_encoded_key,
                    ykiho=ykiho
                )
                
                # 응답 바디 확인
                body = data['response']['body']
                items = body.get('items', {}).get('item', {})
                
                # 단일 결과인 경우 처리
                if isinstance(items, dict):
                    items = [items]
                
                if items:
                    # 원본 데이터와 병합
                    for item in items:
                        # 원본 행의 데이터 추가
                        item['원본_병원명'] = row.get('yadmNm', '')
                        item['원본_주소'] = row.get('addr', '')
                        all_items.append(item)
                else:
                    print(f"  - 상세정보 없음")
                
                processed_indices.add(idx)
                
            except Exception as e:
                print(f"  - 오류 발생: {e}")
                # 오류가 발생해도 다음 항목으로 계속 진행
                processed_indices.add(idx)
                continue
            
            # 체크포인트 저장 (일정 간격마다)
            if enable_checkpoint and checkpoint_file and len(processed_indices) % CHECKPOINT_INTERVAL == 0:
                checkpoint_data = {
                    'last_index': idx,
                    'processed_count': len(processed_indices),
                    'processed_indices': list(processed_indices),
                    'total_count': total_count,
                    'timestamp': datetime.now().isoformat(),
                    'items': all_items
                }
                save_checkpoint(checkpoint_data, checkpoint_file)
            
            # API 호출 간격 (초당 요청 제한 고려)
            time.sleep(0.1)
        
        print(f"[완료] 총 {len(all_items)}건 조회 완료")
        
        # 완료 후 체크포인트 파일 삭제
        if enable_checkpoint and checkpoint_file and os.path.exists(checkpoint_file):
            try:
                os.remove(checkpoint_file)
                print(f"[체크포인트 삭제] {checkpoint_file}")
            except:
                pass
        
        return all_items
        
    except Exception as e:
        # 오류 발생 시 현재까지의 데이터 체크포인트 저장
        if enable_checkpoint and checkpoint_file:
            checkpoint_data = {
                'last_index': idx if 'idx' in locals() else 0,
                'processed_count': len(processed_indices),
                'processed_indices': list(processed_indices),
                'total_count': total_count,
                'timestamp': datetime.now().isoformat(),
                'error': str(e),
                'items': all_items
            }
            save_checkpoint(checkpoint_data, checkpoint_file)
            print(f"\n[오류] 진행상황이 저장되었습니다. 다시 실행하면 이어서 진행됩니다.")
        raise


# ============================================================================
# 데이터 처리 함수
# ============================================================================

def save_to_excel(items: List[Dict], filename: str):
    """
    병원 상세정보를 엑셀 파일로 저장
    
    Parameters:
    -----------
    items : list
        병원 상세정보 리스트
    filename : str
        저장할 파일명 (예: 'hospital_details.xlsx')
    """
    
    if not items:
        print("[경고] 저장할 데이터가 없습니다.")
        return
    
    # 데이터프레임 생성
    df = pd.DataFrame(items)
    
    # 컬럼 순서 정리 (주요 컬럼 우선)
    priority_columns = [
        '원본_병원명', '원본_주소',
        'yadmNm', 'addr', 'telno', 'hospUrl',
        'clCdNm', 'sidoCdNm', 'sgguCdNm', 'emdongNm',
        'postNo', 'XPos', 'YPos'
    ]
    
    # 존재하는 우선 컬럼만 선택
    existing_priority = [col for col in priority_columns if col in df.columns]
    # 나머지 컬럼
    other_columns = [col for col in df.columns if col not in existing_priority]
    # 최종 컬럼 순서
    final_columns = existing_priority + other_columns
    df = df[final_columns]
    
    # 엑셀 저장
    df.to_excel(filename, index=False, engine='openpyxl')
    print(f"[저장 완료] {filename} ({len(df)}건)")
    print(f"  - 컬럼 수: {len(df.columns)}")


# ============================================================================
# 메인 실행 코드
# ============================================================================

def main():
    """
    메인 실행 함수
    """
    
    print("="*80)
    print("의료기관별상세정보 조회 프로그램")
    print("="*80)
    print()
    
    # ========================================
    # 1. 인증키 확인
    # ========================================
    if SERVICE_KEY == "여기에_발급받은_디코딩_인증키를_입력하세요":
        print("[오류] 인증키를 설정하지 않았습니다.")
        print("스크립트 상단의 SERVICE_KEY 변수에 발급받은 디코딩 인증키를 입력하세요.")
        return
    
    # ========================================
    # 2. 입력 파일 읽기
    # ========================================
    try:
        hospital_df = load_hospital_list_from_excel(
            INPUT_EXCEL_FILE,
            ykiho_column=YKIHO_COLUMN
        )
    except Exception as e:
        print(f"[오류] Excel 파일 읽기 실패: {e}")
        print()
        print("해결 방법:")
        print("1. INPUT_EXCEL_FILE 경로가 올바른지 확인")
        print("2. YKIHO_COLUMN 이름이 올바른지 확인")
        print("3. Excel 파일이 열려있지 않은지 확인")
        return
    
    # ========================================
    # 3. API 호출
    # ========================================
    try:
        # 모든 병원 상세정보 조회
        details = get_all_hospital_details(
            service_key=SERVICE_KEY,
            use_encoded_key=USE_ENCODED_KEY,
            hospital_df=hospital_df,
            ykiho_column=YKIHO_COLUMN if YKIHO_COLUMN in hospital_df.columns else None
        )
        
        # ========================================
        # 4. 엑셀 저장
        # ========================================
        if details:
            # 파일명 생성 (현재 날짜시간 포함)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_dir = Path("data")
            output_dir.mkdir(exist_ok=True)
            filename = output_dir / f"병원상세정보_{timestamp}.xlsx"
            
            save_to_excel(details, str(filename))
        
    except Exception as e:
        print(f"[오류 발생] {e}")
        print()
        print("문제 해결 방법:")
        print("1. 인증키가 올바른지 확인 (디코딩 키 사용)")
        print("2. 인터넷 연결 확인")
        print("3. API 엔드포인트가 올바른지 확인")
        print("4. 체크포인트 파일이 있다면 삭제 후 재시도")


# ============================================================================
# 프로그램 실행
# ============================================================================

if __name__ == "__main__":
    main()
