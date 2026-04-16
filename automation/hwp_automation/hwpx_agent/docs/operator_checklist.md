# 운영자용 점검 문서

## 목적

이 문서는 실제 테스트나 운영 전에 작업자가 확인해야 할 항목을 단계별로 정리한 문서입니다.

## 시작 전 확인

- 작업할 원본 HWPX 경로가 맞는지 확인
- 이전 run 폴더와 새 run 폴더를 헷갈리지 않도록 이름 확인
- 이번 실행에서 무엇을 검증할지 정리

예:

- 페이지 정합성
- 문단 수정
- 표 셀 수정
- rebuild 파일 열림 여부

## 1. 자산화 직후 점검

확인 파일:

- `assets/document.json`
- `assets/pages/page_summary.json`
- `assets/blocks/paragraphs.json`
- `assets/tables/cells.json`

볼 것:

- 페이지 수
- 문단 수
- 표 수
- 표 셀 수
- `pyhwpx_root_paragraph_exact` 적용 여부

## 2. 교정 결과 점검

확인 파일:

- `assets/proofreading/issues.json`
- `assets/proofreading/summary.json`

볼 것:

- issue 수가 비정상적으로 너무 많지 않은지
- `origin_id`가 비어 있지 않은지
- `origin_type=table_cell`이 필요한 경우 실제로 나오는지

## 3. 검토 파일 작성 전 점검

확인 파일:

- `assets/proofreading/issue_review.sample.json`

볼 것:

- 수정할 항목의 `origin_type`
- `eligible_for_rebuild`
- `blocking_reason`

운영 원칙:

- 처음에는 1건만 선택해서 테스트
- 문단 1건, 표 셀 1건을 따로 테스트하면 가장 안전함

## 4. rebuild 전 점검

확인 파일:

- `assets/rebuild/rebuild_plan.from_issue_review.json`

볼 것:

- `origin_id`
- `origin_type`
- `expected_current_text`
- `new_text`

중요:

- `expected_current_text`가 너무 다르면 rebuild에서 건너뛸 수 있음
- 공백이 많은 셀은 rebuild 전에 한 번 더 확인하는 것이 좋음

## 5. rebuild 후 점검

확인 파일:

- `rebuild/rebuild_summary.json`
- `rebuild/rebuild_log.json`
- rebuilt `.hwpx`

볼 것:

- `applied_count`
- `skipped_count`
- `modified_entry_count`
- `skipped_text_mismatch` 같은 로그 유무

## 6. 수동 확인

한글에서 rebuilt 파일을 열고 아래를 본다.

- 파일이 정상 열리는지
- 페이지가 크게 깨지지 않았는지
- 내가 선택한 문장이 실제로 바뀌었는지
- 내가 선택한 표 셀이 실제로 바뀌었는지

## 7. 최종 판정 기준

현재 단계에서 합격으로 보기 위한 최소 조건:

- 페이지 수가 맞다
- `table_cell` 이슈가 생성된다
- rebuilt 파일이 열린다
- 선택한 문단 또는 표 셀 수정이 실제 반영된다

## 8. 실패 시 먼저 볼 곳

- `validation/validation_summary.json`
- `assets/pages/page_summary.json`
- `assets/proofreading/summary.json`
- `rebuild/rebuild_log.json`

## 자동 점검 명령

```powershell
python run_validate.py --run-dir D:\git_rk\automation\hwp_automation\hwpx_agent\runs\<run_name> --expected-page-count 239 --require-proofread --require-rebuild --require-table-cell-issues
```
