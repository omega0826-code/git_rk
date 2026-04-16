# 폴더 구조 설명

## 기본 구조

`hwpx_agent` 아래는 크게 4개로 이해하면 됩니다.

- `src/`
- `schemas/`
- `docs/`
- `runs/`

## 각 폴더 역할

### `src/hwpx_agent/`

실제 코드가 들어 있습니다.

- `assetizer.py`: HWPX를 자산으로 분해
- `proofread.py`: 자산 기반 교정 이슈 생성
- `issue_bridge.py`: 검토 파일을 rebuild plan으로 변환
- `rebuild.py`: plan을 기반으로 HWPX 복원

### `schemas/`

JSON 파일 구조 기준입니다.

- `block_asset.schema.json`
- `proofread_issue.schema.json`

이 폴더는 "결과 JSON이 어떤 모양이어야 하는지" 보는 기준입니다.

### `docs/`

사람이 읽는 설명 문서입니다.

- 개요
- 초보자용 사용 문서
- 폴더 설명서
- 추후 개발 고려사항

### `runs/`

실제 실행 결과가 문서별로 저장되는 폴더입니다.

예:

```text
runs\
  2023_mei_tableflow_demo_20260416_144505\
```

이 안이 가장 중요합니다.

## `runs/<run_name>/` 안쪽 구조

### `source/`

원본 HWPX 복사본이 들어 있습니다.

용도:

- 어떤 원본으로 실행했는지 보존
- 나중에 rebuild 기준으로 사용

### `package/`

HWPX 내부 XML과 주요 패키지 파일을 풀어둔 폴더입니다.

예:

- `Contents/section0.xml`
- `Contents/header.xml`
- `Contents/masterpage0.xml`
- `content_manifest.json`
- `package_manifest.json`

용도:

- 원본 XML 확인
- 디버깅
- 복원 전후 비교

### `assets/`

AI가 읽기 쉬운 자산 결과가 들어 있습니다.

이 폴더가 핵심입니다.

#### `assets/document.json`

문서 전체 요약 파일입니다.

예:

- 문단 수
- 표 수
- 표 셀 수
- 이미지 수
- 페이지 정보

#### `assets/blocks/`

문단 관련 자산입니다.

- `paragraphs.json`: 문단 전체 목록
- `paragraph_summary.json`: 문단 분류 요약

#### `assets/tables/`

표 관련 자산입니다.

- `tables.json`: 표 전체 목록
- `cells.json`: 표 셀 전체 목록

`cells.json`은 표 셀 단위 수정과 추적에 직접 사용됩니다.

#### `assets/images/`

이미지 관련 자산입니다.

- `binaries.json`: 이미지 바이너리 목록
- `occurrences.json`: 문서 안 배치 위치 정보
- `raw/`: 실제 이미지 파일

#### `assets/pages/`

페이지 관련 정보입니다.

- `page_summary.json`: 페이지 계산 요약
- `paragraph_page_map.json`: 문단별 페이지 정보
- `root_body_page_map.json`: 루트 본문 문단 기준 페이지 정보

#### `assets/proofreading/`

교정과 검토 관련 파일입니다.

- `issues.json`: 교정 이슈
- `summary.json`: 교정 요약
- `line_map.json`: line 번호와 자산 매핑
- `issue_review.sample.json`: 사람이 수정 선택하는 파일

#### `assets/rebuild/`

복원용 계획 파일입니다.

- `rebuild_plan.from_issue_review.json`
- `issue_review_conversion_summary.json`
- `issue_review_conversion_log.json`

### `rebuild/`

실제로 다시 만든 HWPX와 복원 로그가 들어 있습니다.

- `<document>_rebuilt.hwpx`
- `rebuild_summary.json`
- `rebuild_log.json`

### `logs/`

자산화 로그가 들어 있습니다.

- `assetize_log.json`

## 초보자 기준으로 어디만 보면 되나

처음에는 아래 파일만 보면 충분합니다.

- `assets/document.json`
- `assets/pages/page_summary.json`
- `assets/proofreading/issues.json`
- `assets/proofreading/issue_review.sample.json`
- `rebuild/rebuild_summary.json`

이 5개가 현재 상태를 가장 빨리 보여줍니다.
