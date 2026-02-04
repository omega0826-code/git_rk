# [직종_raw data.csv] KECO2 코드 매핑 구현 계획 (복사본)

`직종_raw data.csv` 파일의 `KECO` 명칭을 기준으로 `KECO2` 코드를 새로 추가(Column 추가)하는 작업을 기술합니다.

## User Review Required

> [!IMPORTANT]
> 현재 제공된 참조 파일 `d:\git_rk\project\25_121_ulsan\CSV\KECO.CSV`가 **0바이트(비어 있음)**로 확인되었습니다. 
> 이로 인해 매핑 작업을 진행할 수 없는 상태입니다. 다음 사항에 대해 확인을 요청드립니다:
> 1. `KECO.CSV` 파일에 데이터가 정상적으로 저장되어 있는지 다시 한번 확인 부탁드립니다.
> 2. 혹시 KECO2 매핑 데이터가 별도의 텍스트나 다른 파일(예: PDF 부록 등)에 정의되어 있는지 확인 부탁드립니다.

## Proposed Changes

### [Data Processing]

#### [MODIFY] [직종_raw data.csv](file:///d:/git_rk/project/25_121_ulsan/CSV/직종_raw data.csv)
- `KECO2` 컬럼을 새로 추가합니다.
- `KECO.CSV`에서 읽어온 매핑 정보를 바탕으로 값을 채웁니다.
- 매핑되지 않는 항목은 '알수없음' 혹은 '미분류'로 처리합니다.

#### [NEW] [KECO_Mapping_Script.py] (임시 실행용)
- 두 CSV 파일을 읽어 매핑을 수행하고 결과를 저장하는 파이썬 스크립트입니다.

## Verification Plan

### Automated Tests
- `pandas`를 사용하여 `KECO2` 컬럼이 추가되었는지, NaN 값이 없는지 검증하는 스크립트 실행.
- 총 레코드 수와 업데이트된 레코드 수 비교.

### Manual Verification
- 생성된 `직종_raw data.csv` 파일을 열어 상위/하위 5개 레코드가 올바르게 매핑되었는지 확인.
- `REPORT` 폴더에 생성될 `KECO2_Mapping_Report_YYYYMMDD_HHMMSS.md` 파일 검토.
