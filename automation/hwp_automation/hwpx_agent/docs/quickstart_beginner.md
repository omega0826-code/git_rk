# 초보자용 사용 문서

## 이 문서는 누구를 위한 문서인가

이 문서는 Python이나 HWPX 구조를 잘 몰라도, 테스트 파일을 기준으로 결과를 만들고 확인할 수 있게 설명한 문서입니다.

## 준비물

- Windows 환경
- Python 실행 가능
- 현재 프로젝트 폴더
- 테스트 파일

테스트 파일 경로:

```text
D:\git_rk\automation\hwp_automation\test\2023_mei_workforce.hwpx
```

작업 폴더:

```text
D:\git_rk\automation\hwp_automation\hwpx_agent
```

## 전체 흐름

처음에는 아래 순서만 기억하면 됩니다.

0. 한 번에 실행하기
1. 문서를 자산으로 뽑기
2. 교정 이슈 만들기
3. 고를 수 있는 검토 파일 만들기
4. 검토 파일에서 원하는 수정만 선택하기
5. 새 HWPX 만들기
6. 결과 검증하기

## 가장 쉬운 방법: 한 번에 실행하기

아래 명령 하나로 자산화, 교정 이슈 생성, 리뷰 샘플 파일 생성, 기본 검증까지 한 번에 실행할 수 있습니다.

```powershell
cd D:\git_rk\automation\hwp_automation\hwpx_agent
python run_pipeline.py --input D:\git_rk\automation\hwp_automation\test\2023_mei_workforce.hwpx --expected-page-count 239 --require-table-cell-issues
```

이 명령을 실행하면 아래 파일들이 자동으로 만들어집니다.

- `assets/document.json`
- `assets/pages/page_summary.json`
- `assets/proofreading/issues.json`
- `assets/proofreading/issue_review.sample.json`
- `validation/validation_summary.json`

처음 테스트할 때는 이 방법을 먼저 권장합니다.

## 1단계: 자산화 실행

```powershell
cd D:\git_rk\automation\hwp_automation\hwpx_agent
python run_assetize.py --input D:\git_rk\automation\hwp_automation\test\2023_mei_workforce.hwpx
```

실행 후 `runs\` 아래에 새 폴더가 하나 생깁니다.

예:

```text
D:\git_rk\automation\hwp_automation\hwpx_agent\runs\2023_mei_tableflow_demo_20260416_144505
```

### 자산화가 잘됐는지 보는 방법

먼저 아래 파일을 엽니다.

- `assets/document.json`
- `assets/pages/page_summary.json`

아래 값이 보이면 정상에 가깝습니다.

- `page_count: 239`
- `paragraphs`
- `tables`
- `table_cells`
- `image_occurrences`

## 2단계: 교정 이슈 만들기

```powershell
python run_proofread.py --run-dir D:\git_rk\automation\hwp_automation\hwpx_agent\runs\<run_name>
```

결과 파일:

- `assets/proofreading/issues.json`
- `assets/proofreading/summary.json`

### 이 단계에서 볼 것

- `issues.json`에 `origin_id`가 있는지
- `origin_type`이 `paragraph` 또는 `table_cell`로 나오는지
- `source_location`이 들어있는지

## 3단계: 검토 파일 만들기

```powershell
python run_issue_bridge.py --run-dir D:\git_rk\automation\hwp_automation\hwpx_agent\runs\<run_name> --init-review
```

결과 파일:

- `assets/proofreading/issue_review.sample.json`
- `assets/proofreading/issue_review.demo.json`

### 이 파일에서 무엇을 수정하나

`issue_review.sample.json`을 열고 아래 2개만 주로 바꿉니다.

- `selected`
- `approved_new_text`

예:

```json
{
  "selected": true,
  "approved_new_text": "여기에 최종 문장을 직접 입력"
}
```

중요한 점:

- `selected=true`인 항목만 다음 단계로 넘어갑니다.
- `approved_new_text`에는 "최종 결과 문장 전체"를 넣어야 합니다.

## 4단계: rebuild plan 만들기

```powershell
python run_issue_bridge.py --run-dir D:\git_rk\automation\hwp_automation\hwpx_agent\runs\<run_name> --review D:\git_rk\automation\hwp_automation\hwpx_agent\runs\<run_name>\assets\proofreading\issue_review.sample.json
```

결과 파일:

- `assets/rebuild/rebuild_plan.from_issue_review.json`

이 파일은 "어떤 위치를 어떤 문장으로 바꿀지" 정리한 중간 파일입니다.

## 5단계: 새 HWPX 만들기

```powershell
python run_rebuild.py --run-dir D:\git_rk\automation\hwp_automation\hwpx_agent\runs\<run_name> --plan D:\git_rk\automation\hwp_automation\hwpx_agent\runs\<run_name>\assets\rebuild\rebuild_plan.from_issue_review.json
```

결과 파일:

- `rebuild\<문서명>_rebuilt.hwpx`
- `rebuild\rebuild_summary.json`
- `rebuild\rebuild_log.json`

## 6단계: 결과 검증하기

기본 검증:

```powershell
python run_validate.py --run-dir D:\git_rk\automation\hwp_automation\hwpx_agent\runs\<run_name>
```

현재 테스트 파일 기준으로 더 강하게 확인하려면:

```powershell
python run_validate.py --run-dir D:\git_rk\automation\hwp_automation\hwpx_agent\runs\<run_name> --expected-page-count 239 --require-proofread --require-rebuild --require-table-cell-issues
```

검증 결과는 아래 파일에 저장됩니다.

- `validation/validation_summary.json`

## 초보자 기준 확인 방법

### 꼭 확인할 4개

1. `page_summary.json`에서 페이지 수가 맞는지
2. `issues.json`에서 `origin_type=table_cell` 같은 항목이 보이는지
3. rebuilt `.hwpx`가 한글에서 열리는지
4. 내가 선택한 수정이 실제 문서에 들어갔는지

### 이렇게 보면 쉽다

- 원본 문서와 rebuilt 문서를 같이 연다.
- 내가 선택한 수정 항목 1개만 먼저 테스트한다.
- 실제로 문장이 바뀌었는지 본다.

## 지금 단계에서 되는 것

- 본문 텍스트 문단 수정
- 안전한 텍스트 표 셀 수정

## 지금 단계에서 안 되는 것

- 그림이 섞인 복잡한 문단 자동 수정
- 복잡한 컨트롤 셀 자동 수정
- 머리말, 꼬리말, 마스터페이지 수정 복원

## 문제가 생기면 먼저 볼 파일

- `assets/document.json`
- `assets/pages/page_summary.json`
- `assets/proofreading/summary.json`
- `rebuild/rebuild_summary.json`
- `rebuild/rebuild_log.json`

이 5개만 먼저 봐도 어디서 막혔는지 대부분 알 수 있습니다.
