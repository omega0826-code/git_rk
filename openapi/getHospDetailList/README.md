# 의료기관별상세정보 조회 스크립트

건강보험심사평가원의 **의료기관별상세정보서비스 API**를 활용하여 병원 상세정보를 다운로드하는 Python 스크립트입니다.

## 📋 개요

이 스크립트는 병원기본목록에서 다운로드한 Excel 파일에서 암호화된 요양기호를 읽어와 각 병원의 상세정보를 조회하고 Excel 파일로 저장합니다.

### 주요 기능
- ✅ Excel 파일에서 암호화된 요양기호 자동 읽기
- ✅ 재시도 로직 (지수 백오프)
- ✅ 체크포인트 기능 (중단 후 재개 가능)
- ✅ 진행률 표시 (예상 남은 시간 포함)
- ✅ 상세한 에러 처리
- ✅ Excel 파일로 결과 저장

## 🚀 빠른 시작

### 1. 요구사항
- Python 3.8 이상
- 필수 라이브러리:
  ```bash
  pip install requests pandas openpyxl
  ```

### 2. API 인증키 발급
1. [공공데이터포털](https://www.data.go.kr) 접속
2. "의료기관별상세정보서비스" 검색
3. 활용신청 버튼 클릭
4. 승인 후 **디코딩 인증키** 복사

### 3. 스크립트 설정
`의료기관상세정보_조회_v1.00_260115.py` 파일을 열고 다음 항목을 수정:

```python
# 인증키 설정
SERVICE_KEY = "여기에_발급받은_디코딩_인증키_입력"

# 입력 파일 경로
INPUT_EXCEL_FILE = "D:/git_rk/openapi/getHospBasisList/data/서울_강남구_피부과_20260113_205835.xlsx"

# 요양기호 컬럼명 (자동 탐지되지 않는 경우에만 수정)
YKIHO_COLUMN = "ykiho"  # 또는 "암호화요양기호"
```

### 4. 실행
```bash
python 의료기관상세정보_조회_v1.00_260115.py
```

## 📂 입력 파일 형식

병원기본목록 Excel 파일에 다음 컬럼이 포함되어야 합니다:
- **필수**: 암호화된 요양기호 컬럼 (`ykiho`, `암호화요양기호`, `요양기호` 등)
- **권장**: 병원명 (`yadmNm`), 주소 (`addr`) - 진행 상황 표시용

## 📤 출력 파일

### 저장 위치
`data/병원상세정보_YYYYMMDD_HHMMSS.xlsx`

### 출력 컬럼
- 원본 데이터 (병원명, 주소)
- 상세정보 (시설정보, 인력정보, 장비정보 등)

## 🔧 고급 설정

### 재시도 설정
```python
MAX_RETRIES = 3          # 최대 재시도 횟수
RETRY_DELAY = 1          # 초기 재시도 대기 시간 (초)
```

### 타임아웃 설정
```python
CONNECT_TIMEOUT = 10     # 연결 타임아웃 (초)
READ_TIMEOUT = 60        # 읽기 타임아웃 (초)
```

### 체크포인트 설정
```python
ENABLE_CHECKPOINT = True # 진행상황 저장 활성화
CHECKPOINT_INTERVAL = 5  # 체크포인트 저장 간격 (건수)
```

## 💡 사용 팁

### 체크포인트 기능 활용
스크립트 실행 중 중단되더라도 다시 실행하면 이어서 진행됩니다:
```bash
# 실행 중 Ctrl+C로 중단
python 의료기관상세정보_조회_v1.00_260115.py

# 다시 실행하면 자동으로 이어서 진행
python 의료기관상세정보_조회_v1.00_260115.py
```

### 소량 데이터 테스트
전체 실행 전 소량 데이터로 테스트:
```python
# main() 함수에서 max_results 파라미터 추가
details = get_all_hospital_details(
    service_key=SERVICE_KEY,
    use_encoded_key=USE_ENCODED_KEY,
    hospital_df=hospital_df,
    ykiho_column=YKIHO_COLUMN,
    max_results=3  # 3건만 테스트
)
```

## 🐛 문제 해결

### 인증키 오류
```
API 오류 [30]: SERVICE_KEY_IS_NOT_REGISTERED_ERROR
```
**해결**: 디코딩 인증키를 사용하고 있는지 확인

### 요양기호 컬럼 오류
```
컬럼 'ykiho'을(를) 찾을 수 없습니다.
```
**해결**: Excel 파일을 열어 요양기호 컬럼명 확인 후 `YKIHO_COLUMN` 수정

### 트래픽 제한 초과
```
API 오류 [22]: LIMITED_NUMBER_OF_SERVICE_REQUESTS_EXCEEDS_ERROR
```
**해결**: 개발 계정은 일 1,000건 제한. 다음 날 재시도 또는 운영 계정 신청

### API 엔드포인트 오류
```
HTTP 오류: 404
```
**해결**: 공공데이터포털에서 정확한 operation 이름 확인 후 `API_BASE_URL` 수정

## 📚 문서

- [API 가이드라인](getHospDetailList_api_guideline.md) - API 사용법 상세 설명
- [스크립트 작성 가이드라인](OpenAPI_스크립트_작성_가이드라인.md) - 범용 개발 가이드
- [개발 과정 문서](REPORT/개발과정_상세문서_20260115_184300.md) - 개발 과정 및 의사결정

## 🔍 관련 프로젝트

- [병원기본목록 조회 스크립트](../getHospBasisList/병원정보_조회_v1.00F_260113.py)
- [병원정보조회 웹앱](../getHospBasisList/병원정보조회_웹앱_V1.00.html)

## 📝 라이선스

이 스크립트는 공공데이터포털의 OpenAPI를 활용합니다. 데이터 사용 시 출처를 표시해야 합니다.

**데이터 출처**: 건강보험심사평가원_의료기관별상세정보서비스

## 👥 기여

버그 리포트나 개선 제안은 이슈로 등록해 주세요.

---

**버전**: 1.00  
**최종 수정**: 2026-01-15  
**작성자**: OpenAPI 스크립트 개발팀
