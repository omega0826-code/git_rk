"""
병원정보 조회 API 호출 스크립트
================================================================================
작성일: 2026-01-13
목적: 건강보험심사평가원 병원정보서비스 API를 사용하여 병원 정보 조회
예시: 서울 강남구 피부과 정보 추출
================================================================================
"""

import requests
import json
from typing import Dict, List, Optional
import pandas as pd
from datetime import datetime

# ============================================================================
# 설정 (Configuration)
# ============================================================================

# API 기본 정보
API_BASE_URL = "http://apis.data.go.kr/B551182/hospInfoService1/getHospBasisList1"

# 인증키 설정 (여기에 발급받은 디코딩 인증키를 입력하세요)
# 주의: 인코딩 키가 아닌 디코딩(Decoding) 키를 사용해야 합니다!
SERVICE_KEY = "Bk8LikYxwbpxf1OKF0mYYonK9RNmYo/mmgtNsZ41rRNxMuIh5s7RgflEXp+Xwp3R0FDR2j01gx62Hc++Jzc2pw=="

# 지역 코드 (시도/시군구)
SIDO_CODES = {
    '서울': '110000',
    '부산': '260000',
    '대구': '270000',
    '인천': '280000',
    '광주': '290000',
    '대전': '300000',
    '울산': '310000',
    '세종': '360000',
    '경기': '410000',
    '강원': '430000',
    '충북': '440000',
    '충남': '450000',
    '전북': '460000',
    '전남': '470000',
    '경북': '480000',
    '경남': '490000',
    '제주': '500000'
}

# 서울 시군구 코드
SEOUL_SGGU_CODES = {
    '종로구': '110011',
    '중구': '110012',
    '용산구': '110013',
    '성동구': '110014',
    '광진구': '110015',
    '동대문구': '110016',
    '중랑구': '110017',
    '성북구': '110018',
    '강북구': '110019',
    '도봉구': '110020',
    '노원구': '110021',
    '은평구': '110022',
    '서대문구': '110023',
    '마포구': '110024',
    '양천구': '110025',
    '강서구': '110026',
    '구로구': '110027',
    '금천구': '110028',
    '영등포구': '110029',
    '동작구': '110030',
    '관악구': '110031',
    '서초구': '110032',
    '강남구': '110033',
    '송파구': '110034',
    '강동구': '110035'
}

# 진료과목 코드
DGSBJ_CODES = {
    '일반의': '00',
    '내과': '01',
    '신경과': '02',
    '정신건강의학과': '03',
    '외과': '04',
    '정형외과': '05',
    '신경외과': '06',
    '흉부외과': '07',
    '성형외과': '08',
    '마취통증의학과': '09',
    '산부인과': '10',
    '소아청소년과': '11',
    '안과': '12',
    '이비인후과': '13',
    '피부과': '14',
    '비뇨의학과': '15',
    '가정의학과': '23',
    '응급의학과': '24'
}

# 종별 코드
CL_CODES = {
    '상급종합병원': '01',
    '종합병원': '11',
    '병원': '21',
    '요양병원': '28',
    '정신병원': '29',
    '의원': '31',
    '치과병원': '41',
    '치과의원': '51',
    '조산원': '61',
    '보건소': '71',
    '보건지소': '72',
    '보건진료소': '73',
    '보건의료원': '75',
    '한방병원': '92',
    '한의원': '93'
}


# ============================================================================
# API 호출 함수
# ============================================================================

def get_hospital_list(
    service_key: str,
    sido_cd: Optional[str] = None,
    sggu_cd: Optional[str] = None,
    emdong_nm: Optional[str] = None,
    yadm_nm: Optional[str] = None,
    cl_cd: Optional[str] = None,
    dgsbj_cd: Optional[str] = None,
    page_no: int = 1,
    num_of_rows: int = 100
) -> Dict:
    """
    병원정보 API 호출 함수
    
    Parameters:
    -----------
    service_key : str
        공공데이터포털에서 발급받은 디코딩 인증키
    sido_cd : str, optional
        시도코드 (예: '110000' - 서울)
    sggu_cd : str, optional
        시군구코드 (예: '110033' - 강남구)
    emdong_nm : str, optional
        읍면동명 (예: '삼성동')
    yadm_nm : str, optional
        병원명 (예: '서울의료원')
    cl_cd : str, optional
        종별코드 (예: '31' - 의원)
    dgsbj_cd : str, optional
        진료과목코드 (예: '14' - 피부과)
    page_no : int
        페이지 번호 (기본값: 1)
    num_of_rows : int
        한 페이지 결과 수 (기본값: 100)
    
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
        'ServiceKey': service_key,
        'pageNo': page_no,
        'numOfRows': num_of_rows,
        '_type': 'json'  # JSON 형식으로 응답 받기
    }
    
    # 선택적 파라미터 추가 (값이 있을 때만)
    if sido_cd:
        params['sidoCd'] = sido_cd
    if sggu_cd:
        params['sgguCd'] = sggu_cd
    if emdong_nm:
        params['emdongNm'] = emdong_nm
    if yadm_nm:
        params['yadmNm'] = yadm_nm
    if cl_cd:
        params['clCd'] = cl_cd
    if dgsbj_cd:
        params['dgsbjtCd'] = dgsbj_cd
    
    try:
        # API 호출
        print(f"[API 호출] 페이지: {page_no}, 결과 수: {num_of_rows}")
        response = requests.get(API_BASE_URL, params=params, timeout=30)
        
        # HTTP 상태 코드 확인
        response.raise_for_status()
        
        # JSON 파싱
        data = response.json()
        
        # API 응답 헤더 확인
        header = data['response']['header']
        if header['resultCode'] != '00':
            raise Exception(f"API 오류 [{header['resultCode']}]: {header['resultMsg']}")
        
        return data
        
    except requests.exceptions.Timeout:
        raise Exception("API 호출 시간 초과. 잠시 후 다시 시도하세요.")
    except requests.exceptions.ConnectionError:
        raise Exception("네트워크 연결 오류. 인터넷 연결을 확인하세요.")
    except requests.exceptions.HTTPError as e:
        raise Exception(f"HTTP 오류: {e}")
    except KeyError as e:
        raise Exception(f"응답 데이터 형식 오류: {e}")
    except Exception as e:
        raise Exception(f"예상치 못한 오류: {e}")


def get_all_hospitals(
    service_key: str,
    sido_cd: Optional[str] = None,
    sggu_cd: Optional[str] = None,
    emdong_nm: Optional[str] = None,
    yadm_nm: Optional[str] = None,
    cl_cd: Optional[str] = None,
    dgsbj_cd: Optional[str] = None,
    max_results: Optional[int] = None
) -> List[Dict]:
    """
    모든 페이지의 병원 정보를 가져오는 함수
    
    Parameters:
    -----------
    service_key : str
        공공데이터포털에서 발급받은 디코딩 인증키
    sido_cd, sggu_cd, emdong_nm, yadm_nm, cl_cd, dgsbj_cd : str, optional
        검색 조건 (get_hospital_list 함수 참조)
    max_results : int, optional
        최대 결과 수 (None이면 전체 조회)
    
    Returns:
    --------
    list
        모든 병원 정보 리스트
    """
    
    all_items = []
    page_no = 1
    num_of_rows = 100  # 한 번에 가져올 최대 개수
    
    while True:
        # API 호출
        data = get_hospital_list(
            service_key=service_key,
            sido_cd=sido_cd,
            sggu_cd=sggu_cd,
            emdong_nm=emdong_nm,
            yadm_nm=yadm_nm,
            cl_cd=cl_cd,
            dgsbj_cd=dgsbj_cd,
            page_no=page_no,
            num_of_rows=num_of_rows
        )
        
        # 응답 바디 확인
        body = data['response']['body']
        total_count = body.get('totalCount', 0)
        
        print(f"[진행 상황] 전체 {total_count}건 중 {len(all_items)}건 조회 완료")
        
        # 아이템 추출
        items = body.get('items', {}).get('item', [])
        
        # 단일 결과인 경우 리스트로 변환
        if isinstance(items, dict):
            items = [items]
        
        # 결과가 없으면 종료
        if not items:
            break
        
        # 결과 추가
        all_items.extend(items)
        
        # 최대 결과 수 확인
        if max_results and len(all_items) >= max_results:
            all_items = all_items[:max_results]
            break
        
        # 모든 데이터를 가져왔는지 확인
        if len(all_items) >= total_count:
            break
        
        # 다음 페이지로
        page_no += 1
    
    print(f"[완료] 총 {len(all_items)}건 조회 완료")
    return all_items


# ============================================================================
# 데이터 처리 함수
# ============================================================================

def save_to_excel(items: List[Dict], filename: str):
    """
    병원 정보를 엑셀 파일로 저장
    
    Parameters:
    -----------
    items : list
        병원 정보 리스트
    filename : str
        저장할 파일명 (예: 'hospitals.xlsx')
    """
    
    if not items:
        print("[경고] 저장할 데이터가 없습니다.")
        return
    
    # 데이터프레임 생성
    df = pd.DataFrame(items)
    
    # 주요 컬럼만 선택 (필요에 따라 수정)
    columns = [
        'yadmNm',      # 병원명
        'clCdNm',      # 종별명
        'sidoCdNm',    # 시도명
        'sgguCdNm',    # 시군구명
        'emdongNm',    # 읍면동명
        'addr',        # 주소
        'postNo',      # 우편번호
        'telno',       # 전화번호
        'hospUrl',     # 홈페이지
        'estbDd',      # 개설일자
        'drTotCnt',    # 의사총수
        'mdeptSdrCnt', # 의과전문의
        'detySdrCnt',  # 치과전문의
        'cmdcSdrCnt',  # 한방전문의
        'XPos',        # 경도
        'YPos'         # 위도
    ]
    
    # 존재하는 컬럼만 선택
    available_columns = [col for col in columns if col in df.columns]
    df_selected = df[available_columns]
    
    # 컬럼명 한글화
    column_names = {
        'yadmNm': '병원명',
        'clCdNm': '종별',
        'sidoCdNm': '시도',
        'sgguCdNm': '시군구',
        'emdongNm': '읍면동',
        'addr': '주소',
        'postNo': '우편번호',
        'telno': '전화번호',
        'hospUrl': '홈페이지',
        'estbDd': '개설일자',
        'drTotCnt': '의사총수',
        'mdeptSdrCnt': '의과전문의',
        'detySdrCnt': '치과전문의',
        'cmdcSdrCnt': '한방전문의',
        'XPos': '경도',
        'YPos': '위도'
    }
    df_selected = df_selected.rename(columns=column_names)
    
    # 엑셀 저장
    df_selected.to_excel(filename, index=False, engine='openpyxl')
    print(f"[저장 완료] {filename} ({len(df_selected)}건)")


def print_hospital_info(items: List[Dict], max_display: int = 10):
    """
    병원 정보를 콘솔에 출력
    
    Parameters:
    -----------
    items : list
        병원 정보 리스트
    max_display : int
        최대 출력 개수 (기본값: 10)
    """
    
    if not items:
        print("[결과 없음] 검색 조건에 맞는 병원이 없습니다.")
        return
    
    print(f"\n{'='*80}")
    print(f"검색 결과: 총 {len(items)}건")
    print(f"{'='*80}\n")
    
    for i, item in enumerate(items[:max_display], 1):
        print(f"[{i}] {item.get('yadmNm', '-')}")
        print(f"    종별: {item.get('clCdNm', '-')}")
        print(f"    주소: {item.get('addr', '-')}")
        print(f"    전화: {item.get('telno', '-')}")
        print(f"    의사수: {item.get('drTotCnt', '0')}명")
        print()
    
    if len(items) > max_display:
        print(f"... 외 {len(items) - max_display}건")
        print()


# ============================================================================
# 메인 실행 코드
# ============================================================================

def main():
    """
    메인 실행 함수
    예시: 서울 강남구 피부과 정보 조회
    """
    
    print("="*80)
    print("병원정보 조회 프로그램")
    print("="*80)
    print()
    
    # ========================================
    # 1. 인증키 확인
    # ========================================
    if SERVICE_KEY == "여기에_발급받은_디코딩_인증키를_입력하세요":
        print("[오류] 인증키를 설정하지 않았습니다.")
        print("스크립트 상단의 SERVICE_KEY 변수에 발급받은 디코딩 인증키를 입력하세요.")
        print()
        print("인증키 발급 방법:")
        print("1. https://www.data.go.kr 접속")
        print("2. 병원정보서비스 API 활용신청")
        print("3. 마이페이지 > 인증키 발급현황에서 '디코딩 인증키' 복사")
        return
    
    # ========================================
    # 2. 검색 조건 설정
    # ========================================
    # 예시: 서울 강남구 피부과
    sido_cd = SIDO_CODES['서울']              # 시도: 서울
    sggu_cd = SEOUL_SGGU_CODES['강남구']      # 시군구: 강남구
    dgsbj_cd = DGSBJ_CODES['피부과']          # 진료과목: 피부과
    
    print(f"[검색 조건]")
    print(f"  - 지역: 서울 강남구")
    print(f"  - 진료과목: 피부과")
    print()
    
    # ========================================
    # 3. API 호출
    # ========================================
    try:
        # 모든 결과 조회
        hospitals = get_all_hospitals(
            service_key=SERVICE_KEY,
            sido_cd=sido_cd,
            sggu_cd=sggu_cd,
            dgsbj_cd=dgsbj_cd
        )
        
        # ========================================
        # 4. 결과 출력
        # ========================================
        print_hospital_info(hospitals, max_display=10)
        
        # ========================================
        # 5. 엑셀 저장
        # ========================================
        if hospitals:
            # 파일명 생성 (현재 날짜시간 포함)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"서울_강남구_피부과_{timestamp}.xlsx"
            
            save_to_excel(hospitals, filename)
        
    except Exception as e:
        print(f"[오류 발생] {e}")
        print()
        print("문제 해결 방법:")
        print("1. 인증키가 올바른지 확인 (디코딩 키 사용)")
        print("2. 인터넷 연결 확인")
        print("3. 인증키 발급 후 30분 이상 경과했는지 확인")


# ============================================================================
# 추가 예시 함수들
# ============================================================================

def example_search_by_name():
    """
    예시: 병원명으로 검색
    """
    hospitals = get_all_hospitals(
        service_key=SERVICE_KEY,
        yadm_nm="서울의료원"  # 병원명에 "서울의료원" 포함
    )
    print_hospital_info(hospitals)


def example_search_by_location():
    """
    예시: 특정 지역의 종합병원 검색
    """
    hospitals = get_all_hospitals(
        service_key=SERVICE_KEY,
        sido_cd=SIDO_CODES['서울'],
        sggu_cd=SEOUL_SGGU_CODES['강남구'],
        cl_cd=CL_CODES['종합병원']
    )
    print_hospital_info(hospitals)


def example_search_pediatrics():
    """
    예시: 소아청소년과 검색
    """
    hospitals = get_all_hospitals(
        service_key=SERVICE_KEY,
        sido_cd=SIDO_CODES['서울'],
        dgsbj_cd=DGSBJ_CODES['소아청소년과']
    )
    print_hospital_info(hospitals)


# ============================================================================
# 프로그램 실행
# ============================================================================

if __name__ == "__main__":
    # 메인 함수 실행
    main()
    
    # 다른 예시를 실행하려면 아래 주석을 해제하세요
    # example_search_by_name()
    # example_search_by_location()
    # example_search_pediatrics()
