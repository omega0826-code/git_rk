# 테스트 체크리스트

## 목적

이 문서는 `hwpx_agent` 결과물을 테스트할 때, 무엇을 합격 기준으로 볼지 빠르게 확인하기 위한 체크리스트입니다.

## 추천 테스트 순서

1. 자산화 결과 확인
2. 페이지 정합성 확인
3. 교정 이슈 확인
4. 검토 파일 확인
5. rebuild 결과 확인
6. 원본 문서와 rebuilt 문서 수동 비교

## 1. 자산화 결과 체크

- `assets/document.json`이 존재한다
- `assets/blocks/paragraphs.json`이 존재한다
- `assets/tables/tables.json`이 존재한다
- `assets/tables/cells.json`이 존재한다
- `assets/images/occurrences.json`이 존재한다

합격 기준:

- 문단 수, 표 수, 표 셀 수가 `document.json`과 실제 파일 길이에서 일치한다

## 2. 페이지 정합성 체크

- `assets/pages/page_summary.json`이 존재한다
- `pyhwpx.page_count`가 기대값과 맞는다
- `assignment.method`가 기대한 방식인지 확인한다

현재 테스트 파일 기준 기대값:

- `page_count = 239`
- `assignment.method = pyhwpx_root_paragraph_exact`

## 3. 교정 이슈 체크

- `assets/proofreading/issues.json`이 존재한다
- `assets/proofreading/summary.json`이 존재한다
- `origin_id`가 들어 있다
- `source_location`이 들어 있다

표 셀까지 검증할 때 추가 확인:

- `origin_type=table_cell` 이슈가 최소 1개 이상 존재한다

## 4. 검토 파일 체크

- `issue_review.sample.json`이 존재한다
- 사람이 선택할 수 있는 `selected` 필드가 있다
- 최종 문장을 적을 `approved_new_text` 필드가 있다
- `origin_type`이 `paragraph` 또는 `table_cell`로 보인다

## 5. rebuild 체크

- rebuilt `.hwpx` 파일이 생성된다
- `rebuild_summary.json`이 존재한다
- `rebuild_log.json`이 존재한다
- rebuilt `.hwpx`가 ZIP 구조로 유효하다
- `mimetype`, `Contents/content.hpf`가 존재한다

수동 확인:

- 한글에서 파일이 실제 열리는지 확인
- 내가 선택한 문장 또는 셀이 실제로 바뀌었는지 확인

## 6. 사람이 꼭 봐야 하는 위험 구간

- 그림이 섞인 문단
- 복합 컨트롤 문단
- 각주, 미주
- 컨테이너 텍스트
- 복잡한 표 셀

이 구간은 현재 자동 수정 대상에서 제외되거나 주의가 필요합니다.

## 자동 검증 명령

기본 검증:

```powershell
python run_validate.py --run-dir D:\git_rk\automation\hwp_automation\hwpx_agent\runs\<run_name>
```

페이지, proofread, rebuild까지 같이 보기:

```powershell
python run_validate.py --run-dir D:\git_rk\automation\hwp_automation\hwpx_agent\runs\<run_name> --expected-page-count 239 --require-proofread --require-rebuild --require-table-cell-issues
```

문자열 반영까지 같이 보기:

```powershell
python run_validate.py --run-dir D:\git_rk\automation\hwp_automation\hwpx_agent\runs\<run_name> --require-rebuild --rebuild-hwpx D:\git_rk\automation\hwp_automation\hwpx_agent\runs\<run_name>\rebuild\<file>.hwpx --expect-string "[CELL UPDATE TEST]"
```

## 최종 합격 기준

아래가 모두 만족되면 현재 단계 합격으로 볼 수 있습니다.

- 페이지 수가 기대값과 맞다
- `table_cell` 이슈가 실제로 나온다
- rebuilt 파일이 실제로 열린다
- 선택한 수정이 실제 문서에 들어간다
