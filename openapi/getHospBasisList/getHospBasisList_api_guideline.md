# 건강보험심사평가원 병원정보서비스 API 가이드라인

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
- **서비스명**: 병원정보서비스 (HospInfoService1)
- **제공기관**: 건강보험심사평가원
- **서비스 설명**: 건강보험심사평가원에서 관리하는 병원 정보 조회 (저작권에 위배되지 않는 정보)
- **인터페이스 표준**: REST API
- **응답 형식**: XML (기본), JSON (옵션)

### 엔드포인트
- **Base URL**: `http://apis.data.go.kr/B551182/hospInfoService1`
- **Operation**: `/getHospBasisList1` (병원기본목록)

---

## API 인증키 발급

### 발급 절차
1. [공공데이터포털](http://data.go.kr) 접속
2. "병원정보서비스" 검색
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
http://apis.data.go.kr/B551182/hospInfoService1/getHospBasisList1?ServiceKey={인증키}&pageNo={페이지번호}&numOfRows={결과수}&_type={응답형식}
```

### 응답 형식 선택
- **XML (기본)**: `_type` 파라미터 생략
- **JSON**: `_type=json` 추가

#### 예시
```
# XML 응답
http://apis.data.go.kr/B551182/hospInfoService1/getHospBasisList1?pageNo=1&numOfRows=10&ServiceKey=발급받은인증키

# JSON 응답
http://apis.data.go.kr/B551182/hospInfoService1/getHospBasisList1?pageNo=1&numOfRows=10&_type=json&ServiceKey=발급받은인증키
```

---

## 요청 파라미터

### 필수 파라미터

| 파라미터명 | 타입 | 필수여부 | 설명 | 예시 |
|-----------|------|---------|------|------|
| `ServiceKey` | String(400) | 필수 | 공공데이터포털에서 발급받은 인증키 | - |

### 선택 파라미터 (검색 조건)

| 파라미터명 | 타입 | 필수여부 | 설명 | 예시 |
|-----------|------|---------|------|------|
| `pageNo` | Integer(5) | 선택 | 페이지 번호 | `1` |
| `numOfRows` | Integer(2) | 선택 | 한 페이지 결과 수 | `10` |
| `sidoCd` | String(6) | 선택 | 시도코드 | `110000` (서울) |
| `sgguCd` | String(6) | 선택 | 시군구코드 | `110019` (중랑구) |
| `emdongNm` | String(150) | 선택 | 읍면동명 (UTF-8 인코딩 필요) | `신내동` |
| `yadmNm` | String(150) | 선택 | 병원명 (UTF-8 인코딩 필요) | `서울의료원` |
| `zipCd` | String(4) | 선택 | 분류코드 | `2010` (종합병원) |
| `clCd` | String(2) | 선택 | 종별코드 | `11` (종합병원) |
| `dgsbjtCd` | String(2) | 선택 | 진료과목코드 | `01` (내과) |
| `xPos` | Decimal(18) | 선택 | x좌표 (경도, 소수점 15자리) | `127.09854004628151` |
| `yPos` | Decimal(18) | 선택 | y좌표 (위도, 소수점 15자리) | `37.6132113197367` |
| `radius` | Integer(10) | 선택 | 반경 (단위: 미터) | `3000` |

### 분류코드 (zipCd)
| 코드 | 설명 |
|------|------|
| `2010` | 종합병원 |
| `2030` | 병원 |
| `2040` | 요양병원 |
| `2050` | 치과 |
| `2060` | 한방 |
| `2070` | 의원 |
| `2080` | 보건기관 |
| `2090` | 조산원 |

### 종별코드 (clCd)
| 코드 | 설명 |
|------|------|
| `01` | 상급종합병원 |
| `11` | 종합병원 |
| `21` | 병원 |
| `28` | 요양병원 |
| `29` | 정신병원 |
| `31` | 의원 |
| `41` | 치과병원 |
| `51` | 치과의원 |
| `61` | 조산원 |
| `71` | 보건소 |
| `72` | 보건지소 |
| `73` | 보건진료소 |
| `75` | 보건의료원 |
| `92` | 한방병원 |
| `93` | 한의원 |

### 진료과목코드 (dgsbjtCd) - 주요 항목
| 코드 | 설명 | 코드 | 설명 |
|------|------|------|------|
| `00` | 일반의 | `01` | 내과 |
| `02` | 신경과 | `03` | 정신건강의학과 |
| `04` | 외과 | `05` | 정형외과 |
| `06` | 신경외과 | `07` | 흉부외과 |
| `08` | 성형외과 | `09` | 마취통증의학과 |
| `10` | 산부인과 | `11` | 소아청소년과 |
| `12` | 안과 | `13` | 이비인후과 |
| `14` | 피부과 | `15` | 비뇨의학과 |
| `23` | 가정의학과 | `24` | 응급의학과 |

> 📌 **전체 진료과목코드는 원본 가이드 문서 참조**

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
| `numOfRows` | Integer | 한 페이지 결과 수 | `10` |
| `pageNo` | Integer | 페이지 번호 | `1` |
| `totalCount` | Integer | 총 건수 | `2` |
| `items` | Object | 리스트 항목 | - |
| `items.item` | Array | 세부 항목 배열 | - |

### 병원 정보 항목 (Item)

#### 기본 정보
| 필드명 | 타입 | 설명 | 예시 |
|--------|------|------|------|
| `ykiho` | String(400) | 암호화된 요양기호 | (암호화된 값) |
| `yadmNm` | String(150) | 병원명 | `서울특별시서울의료원` |
| `clCd` | String(2) | 종별코드 | `11` |
| `clCdNm` | String(150) | 종별코드명 | `종합병원` |

#### 주소 정보
| 필드명 | 타입 | 설명 | 예시 |
|--------|------|------|------|
| `sidoCd` | String(6) | 시도코드 | `110000` |
| `sidoCdNm` | String(150) | 시도명 | `서울` |
| `sgguCd` | String(6) | 시군구코드 | `110019` |
| `sgguCdNm` | String(150) | 시군구명 | `중랑구` |
| `emdongNm` | String(150) | 읍면동명 | `신내동` |
| `postNo` | String(6) | 우편번호 | `02053` |
| `addr` | String(500) | 주소 | `서울특별시 중랑구 신내로 156 (신내동)` |

#### 연락처 정보
| 필드명 | 타입 | 설명 | 예시 |
|--------|------|------|------|
| `telno` | String(30) | 전화번호 | `02-2276-7000` |
| `hospUrl` | String(500) | 홈페이지 | `http://www.seoulmc.or.kr` |

#### 운영 정보
| 필드명 | 타입 | 설명 | 예시 |
|--------|------|------|------|
| `estbDd` | String(8) | 개설일자 (YYYYMMDD) | `20110309` |
| `drTotCnt` | Integer(14) | 의사총수 | `227` |

#### 의과 인력 정보
| 필드명 | 타입 | 설명 | 예시 |
|--------|------|------|------|
| `mdeptGdrCnt` | Integer(22) | 의과일반의 인원수 | `0` |
| `mdeptIntnCnt` | Integer(22) | 의과인턴 인원수 | `28` |
| `mdeptResdntCnt` | Integer(22) | 의과레지던트 인원수 | `64` |
| `mdeptSdrCnt` | Integer(22) | 의과전문의 인원수 | `131` |

#### 치과 인력 정보
| 필드명 | 타입 | 설명 | 예시 |
|--------|------|------|------|
| `detyGdrCnt` | Integer(22) | 치과일반의 인원수 | `1` |
| `detyIntnCnt` | Integer(22) | 치과인턴 인원수 | `0` |
| `detyResdntCnt` | Integer(22) | 치과레지던트 인원수 | `0` |
| `detySdrCnt` | Integer(22) | 치과전문의 인원수 | `2` |

#### 한방 인력 정보
| 필드명 | 타입 | 설명 | 예시 |
|--------|------|------|------|
| `cmdcGdrCnt` | Integer(22) | 한방일반의 인원수 | `1` |
| `cmdcIntnCnt` | Integer(22) | 한방인턴 인원수 | `0` |
| `cmdcResdntCnt` | Integer(22) | 한방레지던트 인원수 | `0` |
| `cmdcSdrCnt` | Integer(22) | 한방전문의 인원수 | `0` |

#### 위치 정보
| 필드명 | 타입 | 설명 | 예시 |
|--------|------|------|------|
| `XPos` | Decimal(18) | x좌표 (경도, 소수점 13자리) | `127.09854004628151` |
| `YPos` | Decimal(18) | y좌표 (위도, 소수점 13자리) | `37.6132113197367` |
| `distance` | Integer(10) | 거리 (단위: 미터) | `0` |

---

## 코드 구현 가이드

### 1. Python 구현 예제

#### 기본 요청 (XML 응답)
```python
import requests
from urllib.parse import quote

# API 설정
SERVICE_KEY = "발급받은_인증키"  # 인코딩하지 않은 원본 키
BASE_URL = "http://apis.data.go.kr/B551182/hospInfoService1/getHospBasisList1"

# 요청 파라미터
params = {
    'ServiceKey': SERVICE_KEY,  # requests 라이브러리가 자동으로 인코딩
    'pageNo': 1,
    'numOfRows': 10
}

# API 호출
response = requests.get(BASE_URL, params=params)

# 응답 확인
if response.status_code == 200:
    print(response.text)  # XML 응답
else:
    print(f"Error: {response.status_code}")
```

#### JSON 응답 요청
```python
import requests
import json

SERVICE_KEY = "발급받은_인증키"
BASE_URL = "http://apis.data.go.kr/B551182/hospInfoService1/getHospBasisList1"

params = {
    'ServiceKey': SERVICE_KEY,
    'pageNo': 1,
    'numOfRows': 10,
    '_type': 'json'  # JSON 응답 요청
}

response = requests.get(BASE_URL, params=params)

if response.status_code == 200:
    data = response.json()
    print(json.dumps(data, indent=2, ensure_ascii=False))
else:
    print(f"Error: {response.status_code}")
```

#### 한글 파라미터 사용 (병원명, 읍면동명 검색)
```python
import requests
from urllib.parse import quote

SERVICE_KEY = "발급받은_인증키"
BASE_URL = "http://apis.data.go.kr/B551182/hospInfoService1/getHospBasisList1"

# 한글 파라미터는 requests가 자동으로 인코딩
params = {
    'ServiceKey': SERVICE_KEY,
    'pageNo': 1,
    'numOfRows': 10,
    'yadmNm': '서울의료원',  # 병원명 (한글)
    'emdongNm': '신내동',    # 읍면동명 (한글)
    '_type': 'json'
}

response = requests.get(BASE_URL, params=params)

if response.status_code == 200:
    data = response.json()
    
    # 응답 헤더 확인
    header = data['response']['header']
    print(f"결과코드: {header['resultCode']}")
    print(f"결과메시지: {header['resultMsg']}")
    
    # 응답 바디 확인
    body = data['response']['body']
    print(f"총 건수: {body['totalCount']}")
    
    # 병원 목록 출력
    items = body.get('items', {}).get('item', [])
    if isinstance(items, dict):  # 결과가 1건인 경우
        items = [items]
    
    for item in items:
        print(f"\n병원명: {item.get('yadmNm')}")
        print(f"주소: {item.get('addr')}")
        print(f"전화번호: {item.get('telno')}")
else:
    print(f"Error: {response.status_code}")
```

#### 위치 기반 검색 (좌표 + 반경)
```python
import requests

SERVICE_KEY = "발급받은_인증키"
BASE_URL = "http://apis.data.go.kr/B551182/hospInfoService1/getHospBasisList1"

# 특정 좌표 주변 3km 이내 종합병원 검색
params = {
    'ServiceKey': SERVICE_KEY,
    'pageNo': 1,
    'numOfRows': 20,
    'xPos': 127.09854004628151,  # 경도
    'yPos': 37.6132113197367,    # 위도
    'radius': 3000,               # 3km (미터 단위)
    'clCd': '11',                 # 종합병원
    '_type': 'json'
}

response = requests.get(BASE_URL, params=params)

if response.status_code == 200:
    data = response.json()
    body = data['response']['body']
    
    items = body.get('items', {}).get('item', [])
    if isinstance(items, dict):
        items = [items]
    
    for item in items:
        print(f"\n병원명: {item.get('yadmNm')}")
        print(f"거리: {item.get('distance')}m")
        print(f"주소: {item.get('addr')}")
else:
    print(f"Error: {response.status_code}")
```

#### 페이징 처리
```python
import requests
import time

SERVICE_KEY = "발급받은_인증키"
BASE_URL = "http://apis.data.go.kr/B551182/hospInfoService1/getHospBasisList1"

def get_all_hospitals(sido_cd, sggu_cd):
    """특정 시군구의 모든 병원 정보 조회"""
    all_items = []
    page_no = 1
    num_of_rows = 100  # 한 번에 가져올 최대 개수
    
    while True:
        params = {
            'ServiceKey': SERVICE_KEY,
            'pageNo': page_no,
            'numOfRows': num_of_rows,
            'sidoCd': sido_cd,
            'sgguCd': sggu_cd,
            '_type': 'json'
        }
        
        response = requests.get(BASE_URL, params=params)
        
        if response.status_code != 200:
            print(f"Error: {response.status_code}")
            break
        
        data = response.json()
        header = data['response']['header']
        
        # 에러 체크
        if header['resultCode'] != '00':
            print(f"API Error: {header['resultMsg']}")
            break
        
        body = data['response']['body']
        total_count = body.get('totalCount', 0)
        
        items = body.get('items', {}).get('item', [])
        if isinstance(items, dict):
            items = [items]
        
        if not items:
            break
        
        all_items.extend(items)
        
        print(f"페이지 {page_no}: {len(items)}건 조회 (전체 {total_count}건 중 {len(all_items)}건)")
        
        # 모든 데이터를 가져왔는지 확인
        if len(all_items) >= total_count:
            break
        
        page_no += 1
        time.sleep(0.1)  # API 호출 간격 (초당 요청 제한 고려)
    
    return all_items

# 사용 예시: 서울시 중랑구의 모든 병원
hospitals = get_all_hospitals('110000', '110019')
print(f"\n총 {len(hospitals)}개 병원 조회 완료")
```

### 2. JavaScript (Node.js) 구현 예제

```javascript
const axios = require('axios');

const SERVICE_KEY = '발급받은_인증키';
const BASE_URL = 'http://apis.data.go.kr/B551182/hospInfoService1/getHospBasisList1';

async function getHospitalList(params = {}) {
    try {
        const response = await axios.get(BASE_URL, {
            params: {
                ServiceKey: SERVICE_KEY,
                pageNo: 1,
                numOfRows: 10,
                _type: 'json',
                ...params
            }
        });
        
        const { header, body } = response.data.response;
        
        if (header.resultCode !== '00') {
            throw new Error(`API Error: ${header.resultMsg}`);
        }
        
        return body;
    } catch (error) {
        console.error('Error:', error.message);
        throw error;
    }
}

// 사용 예시
(async () => {
    try {
        const result = await getHospitalList({
            yadmNm: '서울의료원',
            sidoCd: '110000'
        });
        
        console.log(`총 건수: ${result.totalCount}`);
        
        let items = result.items?.item || [];
        if (!Array.isArray(items)) {
            items = [items];
        }
        
        items.forEach(item => {
            console.log(`\n병원명: ${item.yadmNm}`);
            console.log(`주소: ${item.addr}`);
            console.log(`전화번호: ${item.telno}`);
        });
    } catch (error) {
        console.error('Failed to fetch hospital list');
    }
})();
```

### 3. Java 구현 예제

```java
import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.net.HttpURLConnection;
import java.net.URL;
import java.net.URLEncoder;

public class HospitalInfoAPI {
    private static final String SERVICE_KEY = "발급받은_인증키";
    private static final String BASE_URL = "http://apis.data.go.kr/B551182/hospInfoService1/getHospBasisList1";
    
    public static String getHospitalList(int pageNo, int numOfRows) throws Exception {
        // 인증키 인코딩
        String encodedServiceKey = URLEncoder.encode(SERVICE_KEY, "UTF-8");
        
        // URL 구성
        StringBuilder urlBuilder = new StringBuilder(BASE_URL);
        urlBuilder.append("?ServiceKey=").append(encodedServiceKey);
        urlBuilder.append("&pageNo=").append(pageNo);
        urlBuilder.append("&numOfRows=").append(numOfRows);
        urlBuilder.append("&_type=json");
        
        // HTTP 연결
        URL url = new URL(urlBuilder.toString());
        HttpURLConnection conn = (HttpURLConnection) url.openConnection();
        conn.setRequestMethod("GET");
        conn.setRequestProperty("Content-type", "application/json");
        
        // 응답 읽기
        BufferedReader rd;
        if (conn.getResponseCode() >= 200 && conn.getResponseCode() <= 300) {
            rd = new BufferedReader(new InputStreamReader(conn.getInputStream()));
        } else {
            rd = new BufferedReader(new InputStreamReader(conn.getErrorStream()));
        }
        
        StringBuilder sb = new StringBuilder();
        String line;
        while ((line = rd.readLine()) != null) {
            sb.append(line);
        }
        rd.close();
        conn.disconnect();
        
        return sb.toString();
    }
    
    public static void main(String[] args) {
        try {
            String result = getHospitalList(1, 10);
            System.out.println(result);
        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}
```

---

## 에러 처리

### 공공데이터포털 에러 코드

| 에러코드 | 에러메시지 | 설명 | 해결방법 |
|---------|-----------|------|---------|
| `0` | `NORMAL_CODE` | 정상 | - |
| `1` | `APPLICATION_ERROR` | 어플리케이션 에러 | 요청 파라미터 확인 |
| `2` | `DB_ERROR` | 데이터베이스 에러 | 잠시 후 재시도 |
| `3` | `NODATA_ERROR` | 데이터없음 에러 | 검색 조건 변경 |
| `4` | `HTTP_ERROR` | HTTP 에러 | 네트워크 연결 확인 |
| `5` | `SERVICETIMEOUT_ERROR` | 서비스 연결실패 에러 | 잠시 후 재시도 |
| `10` | `INVALID_REQUEST_PARAMETER_ERROR` | 잘못된 요청 파라메터 에러 | 파라미터 형식 확인 |
| `11` | `NO_MANDATORY_REQUEST_PARAMETERS_ERROR` | 필수요청 파라메터가 없음 | ServiceKey 확인 |
| `12` | `NO_OPENAPI_SERVICE_ERROR` | 해당 오픈API서비스가 없거나 폐기됨 | URL 확인 |
| `20` | `SERVICE_ACCESS_DENIED_ERROR` | 서비스 접근거부 | 인증키 권한 확인 |
| `21` | `TEMPORARILY_DISABLE_THE_SERVICEKEY_ERROR` | 일시적으로 사용할 수 없는 서비스 키 | 잠시 후 재시도 |
| `22` | `LIMITED_NUMBER_OF_SERVICE_REQUESTS_EXCEEDS_ERROR` | 서비스 요청제한횟수 초과에러 | 일일 트래픽 확인 (1,000건) |
| `30` | `SERVICE_KEY_IS_NOT_REGISTERED_ERROR` | 등록되지 않은 서비스키 | 인증키 재확인 |
| `31` | `DEADLINE_HAS_EXPIRED_ERROR` | 기한만료된 서비스키 | 인증키 재발급 |
| `32` | `UNREGISTERED_IP_ERROR` | 등록되지 않은 IP | IP 등록 확인 |
| `33` | `UNSIGNED_CALL_ERROR` | 서명되지 않은 호출 | 인증 방식 확인 |
| `99` | `UNKNOWN_ERROR` | 기타에러 | 관리자 문의 |

### Python 에러 처리 예제

```python
import requests
from typing import Optional, Dict, Any

class HospitalAPIError(Exception):
    """병원정보 API 에러"""
    pass

def get_hospital_list_safe(params: Dict[str, Any]) -> Optional[Dict]:
    """안전한 API 호출 (에러 처리 포함)"""
    SERVICE_KEY = "발급받은_인증키"
    BASE_URL = "http://apis.data.go.kr/B551182/hospInfoService1/getHospBasisList1"
    
    # 기본 파라미터 설정
    default_params = {
        'ServiceKey': SERVICE_KEY,
        'pageNo': 1,
        'numOfRows': 10,
        '_type': 'json'
    }
    default_params.update(params)
    
    try:
        # API 호출
        response = requests.get(BASE_URL, params=default_params, timeout=10)
        response.raise_for_status()  # HTTP 에러 체크
        
        data = response.json()
        header = data['response']['header']
        
        # API 결과 코드 체크
        if header['resultCode'] != '00':
            error_code = header['resultCode']
            error_msg = header['resultMsg']
            
            # 에러 코드별 처리
            if error_code == '3':
                print("검색 결과가 없습니다.")
                return None
            elif error_code == '22':
                raise HospitalAPIError("일일 트래픽 제한 초과 (1,000건)")
            elif error_code == '30':
                raise HospitalAPIError("등록되지 않은 서비스키입니다.")
            else:
                raise HospitalAPIError(f"API Error [{error_code}]: {error_msg}")
        
        return data['response']['body']
        
    except requests.exceptions.Timeout:
        print("API 호출 시간 초과. 잠시 후 다시 시도하세요.")
        return None
    except requests.exceptions.ConnectionError:
        print("네트워크 연결 오류. 인터넷 연결을 확인하세요.")
        return None
    except requests.exceptions.HTTPError as e:
        print(f"HTTP 에러: {e}")
        return None
    except KeyError as e:
        print(f"응답 데이터 형식 오류: {e}")
        return None
    except HospitalAPIError as e:
        print(f"API 에러: {e}")
        return None
    except Exception as e:
        print(f"예상치 못한 에러: {e}")
        return None

# 사용 예시
result = get_hospital_list_safe({
    'yadmNm': '서울의료원',
    'sidoCd': '110000'
})

if result:
    print(f"총 {result['totalCount']}건 조회 완료")
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
SERVICE_KEY = os.getenv('HOSPITAL_API_KEY')
```

### 2. 인코딩 처리
- **한글 파라미터** (`yadmNm`, `emdongNm`): UTF-8 인코딩 필요
- **인증키**: URL 인코딩 필요 (대부분의 HTTP 라이브러리가 자동 처리)
- `requests` 라이브러리 사용 시 자동 인코딩됨

### 3. 응답 데이터 처리
- **단일 결과**: `items.item`이 딕셔너리 형태
- **복수 결과**: `items.item`이 리스트 형태
- 반드시 타입 체크 후 처리

```python
items = body.get('items', {}).get('item', [])
if isinstance(items, dict):  # 결과가 1건인 경우
    items = [items]
```

### 4. 트래픽 제한
- **개발계정**: 일 1,000건
- 대량 데이터 수집 시 페이징 처리 및 적절한 딜레이 추가
- 운영계정 필요 시 별도 신청

### 5. 좌표계
- **좌표계**: WGS84 (GPS 좌표계)
- **경도 (xPos)**: 동경 124° ~ 132° (한반도 기준)
- **위도 (yPos)**: 북위 33° ~ 43° (한반도 기준)
- 소수점 13~15자리까지 지원

### 6. 데이터 갱신 주기
- 공공데이터포털과 건강보험심사평가원 간 동기화: 약 30분
- 실시간 데이터가 아닐 수 있음

### 7. 응답 형식
- 기본 응답: XML
- JSON 응답: `_type=json` 파라미터 추가
- XML 파싱이 필요한 경우 `xml.etree.ElementTree` 또는 `BeautifulSoup` 사용

---

## 참고 자료

- [공공데이터포털](http://data.go.kr)
- [건강보험심사평가원](https://www.hira.or.kr)
- 원본 가이드: `OpenAPI활용가이드_건강보험심사평가원(병원정보서비스)_210616.md`

---

## 버전 정보
- **가이드 버전**: 1.0
- **API 버전**: 1.2
- **최종 수정일**: 2026-01-13
- **작성 기준**: OpenAPI활용가이드 v1.2 (2021-06-16)
