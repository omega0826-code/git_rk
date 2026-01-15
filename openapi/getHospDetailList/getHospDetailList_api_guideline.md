# 건강보험심사평가원 의료기관별상세정보서비스 API 가이드라인

## 📋 목차
1. [서비스 개요](#서비스-개요)
2. [API 인증키 발급](#api-인증키-발급)
3. [API 명세](#api-명세)
4. [요청 파라미터](#요청-파라미터)
5. [응답 데이터 구조](#응답-데이터-구조)
6. [코드 구현 가이드](#코드-구현-가이드)
7. [에러 처리](#에러-처리)
8. [주의사항](#주의사항)

---

## 서비스 개요

### 서비스 정보
- **서비스명**: 의료기관별상세정보서비스 (MadmDtlInfoService2.7)
- **제공기관**: 건강보험심사평가원
- **서비스 설명**: 건강보험심사평가원에서 수집·관리하는 의료기관의 상세정보를 제공하는 서비스
- **인터페이스 표준**: REST API
- **응답 형식**: XML (기본), JSON (옵션)

### 제공 정보
- 시설정보
- 세부정보
- 진료과목정보
- 교통정보
- 의료장비정보
- 식대가산정보
- 간호등급정보
- 특수진료정보 (진료가능분야조회)
- 전문병원지정분야
- 전문과목별전문의수
- 기타인력수 정보

### 엔드포인트
- **Base URL**: `http://apis.data.go.kr/B551182/MadmDtlInfoService2.7`
- **Operation**: `/getDtlInfo` (상세정보 조회)

> [!IMPORTANT]
> **암호화된 요양기호 사용**
> 
> 요양기호는 1:1로 매칭한 암호화된 요양기호로 제공되며, 별도의 복호화 방법 또는 요양기호는 제공하지 않습니다.
> 암호화된 요양기호는 건강보험심사평가원 '병원정보서비스' Open API > 병원기본목록에서 확인 가능합니다.

---

## API 인증키 발급

### 발급 절차
1. [공공데이터포털](http://data.go.kr) 접속
2. "의료기관별상세정보서비스" 검색
3. 활용신청 버튼 클릭
4. 신청 정보 입력 및 제출
5. 자동승인 (약 30분 후 사용 가능)

### 사용 제한
- **개발계정**: 일 1,000건 트래픽 제공
- **동기화 시간**: 공공데이터포털과 건강보험심사평가원 간 약 30분 소요

---

## API 명세

### 전체 URL 구조
```
http://apis.data.go.kr/B551182/MadmDtlInfoService2.7/getDtlInfo?ServiceKey={인증키}&ykiho={암호화된요양기호}&_type={응답형식}
```

### 응답 형식 선택
- **XML (기본)**: `_type` 파라미터 생략
- **JSON**: `_type=json` 추가

#### 예시
```
# XML 응답
http://apis.data.go.kr/B551182/MadmDtlInfoService2.7/getDtlInfo?ykiho=암호화된요양기호&ServiceKey=발급받은인증키

# JSON 응답
http://apis.data.go.kr/B551182/MadmDtlInfoService2.7/getDtlInfo?ykiho=암호화된요양기호&_type=json&ServiceKey=발급받은인증키
```

---

## 요청 파라미터

### 필수 파라미터

| 파라미터명 | 타입 | 필수여부 | 설명 | 예시 |
|-----------|------|---------|------|------|
| `ServiceKey` | String(400) | 필수 | 공공데이터포털에서 발급받은 인증키 | - |
| `ykiho` | String(400) | 필수 | 암호화된 요양기호 | - |

### 선택 파라미터

| 파라미터명 | 타입 | 필수여부 | 설명 | 예시 |
|-----------|------|---------|------|------|
| `_type` | String | 선택 | 응답 형식 (json 또는 xml) | `json` |

---

## 응답 데이터 구조

### 응답 헤더 (Header)
| 필드명 | 타입 | 설명 | 예시 |
|--------|------|------|------|
| `resultCode` | String(5) | 결과코드 | `00` (정상) |
| `resultMsg` | String(50) | 결과메시지 | `NORMAL SERVICE.` |

### 응답 바디 (Body)
| 필드명 | 타입 | 설명 | 예시 |
|--------|------|------|------|
| `items` | Object | 리스트 항목 | - |
| `items.item` | Object/Array | 세부 항목 | - |

### 병원 상세정보 항목 (Item)

상세정보 항목은 API 응답에 따라 다양하게 제공됩니다. 주요 항목은 다음과 같습니다:

#### 기본 정보
- `yadmNm`: 병원명
- `clCdNm`: 종별명
- `addr`: 주소
- `telno`: 전화번호
- `hospUrl`: 홈페이지

#### 위치 정보
- `sidoCdNm`: 시도명
- `sgguCdNm`: 시군구명
- `emdongNm`: 읍면동명
- `postNo`: 우편번호
- `XPos`: 경도
- `YPos`: 위도

---

## 코드 구현 가이드

### 1. Python 구현 예제

#### 기본 요청 (JSON 응답)
```python
import requests

# API 설정
SERVICE_KEY = "발급받은_인증키"  # 디코딩 키
BASE_URL = "http://apis.data.go.kr/B551182/MadmDtlInfoService2.7/getDtlInfo"
YKIHO = "암호화된_요양기호"  # 병원기본목록에서 획득

# 요청 파라미터
params = {
    'ServiceKey': SERVICE_KEY,
    'ykiho': YKIHO,
    '_type': 'json'
}

# API 호출
response = requests.get(BASE_URL, params=params)

if response.status_code == 200:
    data = response.json()
    
    # 응답 헤더 확인
    header = data['response']['header']
    if header['resultCode'] == '00':
        # 상세정보 추출
        body = data['response']['body']
        items = body.get('items', {}).get('item', {})
        
        print(f"병원명: {items.get('yadmNm')}")
        print(f"주소: {items.get('addr')}")
        print(f"전화번호: {items.get('telno')}")
    else:
        print(f"API 오류: {header['resultMsg']}")
else:
    print(f"HTTP 오류: {response.status_code}")
```

#### 여러 병원 상세정보 조회 (Excel 입력)
```python
import requests
import pandas as pd
from typing import List, Dict

def get_hospital_detail(service_key: str, ykiho: str) -> Dict:
    """단일 병원 상세정보 조회"""
    BASE_URL = "http://apis.data.go.kr/B551182/MadmDtlInfoService2.7/getDtlInfo"
    
    params = {
        'ServiceKey': service_key,
        'ykiho': ykiho,
        '_type': 'json'
    }
    
    response = requests.get(BASE_URL, params=params, timeout=30)
    response.raise_for_status()
    
    data = response.json()
    header = data['response']['header']
    
    if header['resultCode'] != '00':
        raise Exception(f"API Error: {header['resultMsg']}")
    
    return data['response']['body'].get('items', {}).get('item', {})

def main():
    SERVICE_KEY = "발급받은_인증키"
    
    # Excel 파일에서 병원 목록 읽기
    df = pd.read_excel('병원목록.xlsx')
    
    details = []
    for idx, row in df.iterrows():
        ykiho = row['ykiho']  # 암호화된 요양기호 컬럼
        
        try:
            detail = get_hospital_detail(SERVICE_KEY, ykiho)
            details.append(detail)
            print(f"[{idx+1}/{len(df)}] {detail.get('yadmNm')} 조회 완료")
        except Exception as e:
            print(f"[{idx+1}/{len(df)}] 오류: {e}")
        
        # API 호출 간격
        time.sleep(0.1)
    
    # 결과 저장
    result_df = pd.DataFrame(details)
    result_df.to_excel('병원상세정보.xlsx', index=False)
    print(f"총 {len(details)}건 저장 완료")

if __name__ == "__main__":
    main()
```

---

## 에러 처리

### 공공데이터포털 에러 코드

| 에러코드 | 에러메시지 | 설명 | 해결방법 |
|---------|-----------|------|---------|
| `0` | `NORMAL_CODE` | 정상 | - |
| `3` | `NODATA_ERROR` | 데이터없음 에러 | 요양기호 확인 |
| `22` | `LIMITED_NUMBER_OF_SERVICE_REQUESTS_EXCEEDS_ERROR` | 서비스 요청제한횟수 초과에러 | 일일 트래픽 확인 (1,000건) |
| `30` | `SERVICE_KEY_IS_NOT_REGISTERED_ERROR` | 등록되지 않은 서비스키 | 인증키 재확인 |
| `31` | `DEADLINE_HAS_EXPIRED_ERROR` | 기한만료된 서비스키 | 인증키 재발급 |

### Python 에러 처리 예제

```python
import requests
from typing import Optional, Dict

class HospitalDetailAPIError(Exception):
    """병원 상세정보 API 에러"""
    pass

def get_hospital_detail_safe(service_key: str, ykiho: str) -> Optional[Dict]:
    """안전한 API 호출 (에러 처리 포함)"""
    BASE_URL = "http://apis.data.go.kr/B551182/MadmDtlInfoService2.7/getDtlInfo"
    
    params = {
        'ServiceKey': service_key,
        'ykiho': ykiho,
        '_type': 'json'
    }
    
    try:
        response = requests.get(BASE_URL, params=params, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        header = data['response']['header']
        
        if header['resultCode'] != '00':
            error_code = header['resultCode']
            error_msg = header['resultMsg']
            
            if error_code == '3':
                print("해당 요양기호의 상세정보가 없습니다.")
                return None
            elif error_code == '22':
                raise HospitalDetailAPIError("일일 트래픽 제한 초과 (1,000건)")
            elif error_code == '30':
                raise HospitalDetailAPIError("등록되지 않은 서비스키입니다.")
            else:
                raise HospitalDetailAPIError(f"API Error [{error_code}]: {error_msg}")
        
        return data['response']['body'].get('items', {}).get('item', {})
        
    except requests.exceptions.Timeout:
        print("API 호출 시간 초과. 잠시 후 다시 시도하세요.")
        return None
    except requests.exceptions.ConnectionError:
        print("네트워크 연결 오류. 인터넷 연결을 확인하세요.")
        return None
    except HospitalDetailAPIError as e:
        print(f"API 에러: {e}")
        return None
    except Exception as e:
        print(f"예상치 못한 에러: {e}")
        return None
```

---

## 주의사항

### 1. 인증키 관리
- ⚠️ **인증키는 절대 공개 저장소에 업로드하지 마세요**
- 환경변수 또는 별도 설정 파일로 관리 권장
- `.gitignore`에 설정 파일 추가

```python
# 환경변수 사용 예시
import os
SERVICE_KEY = os.getenv('HOSPITAL_DETAIL_API_KEY')
```

### 2. 암호화된 요양기호 획득
- 병원기본목록 API를 먼저 호출하여 암호화된 요양기호 획득 필요
- 요양기호는 복호화할 수 없으며, API 간 1:1 매칭으로만 사용 가능

### 3. 응답 데이터 처리
- **단일 결과**: `items.item`이 딕셔너리 형태
- **복수 결과**: `items.item`이 리스트 형태 (드물지만 가능)
- 반드시 타입 체크 후 처리

```python
items = body.get('items', {}).get('item', {})
if isinstance(items, list):
    # 복수 결과 처리
    for item in items:
        process(item)
else:
    # 단일 결과 처리
    process(items)
```

### 4. 트래픽 제한
- **개발계정**: 일 1,000건
- 대량 데이터 수집 시 적절한 딜레이 추가 권장
- 운영계정 필요 시 별도 신청

### 5. 데이터 갱신 주기
- 공공데이터포털과 건강보험심사평가원 간 동기화: 약 30분
- 실시간 데이터가 아닐 수 있음

---

## 참고 자료

- [공공데이터포털](http://data.go.kr)
- [건강보험심사평가원](https://www.hira.or.kr)
- [의료기관별상세정보서비스 API 페이지](https://www.data.go.kr/data/15001699/openapi.do)

---

## 버전 정보
- **가이드 버전**: 1.0
- **최종 수정일**: 2026-01-15
- **작성 기준**: 공공데이터포털 API 명세
