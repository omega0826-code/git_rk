# hwpx_agent

`hwpx_agent`는 HWPX 문서를 AI가 다루기 쉬운 자산 구조로 분해하고, 검토 결과를 다시 HWPX로 반영하기 위한 통합 작업 폴더입니다.

현재 검증된 범위는 다음과 같습니다.

- HWPX 패키지 분해
- 본문 문단 자산화
- 표와 표 셀 자산화
- 이미지 바이너리와 이미지 배치 자산화
- 페이지 번호 정합화
- 교정 이슈와 원본 위치 연결
- 선택한 수정안을 rebuild plan으로 변환
- 안전한 텍스트 문단 복원
- 안전한 텍스트 표 셀 복원

이번 단계에서 실제 확인된 내용은 다음과 같습니다.

- 페이지 수가 `239`로 맞게 잡힘
- `origin_type=table_cell` 이슈가 실제 생성됨
- rebuilt `.hwpx`가 한글에서 정상 열림
- 선택한 표 셀 수정이 실제로 반영됨

## 문서 안내

- 프로젝트 개요: `docs/overview.md`
- 1차 완료 기준: `docs/phase1_completion.md`
- 초보자용 사용 문서: `docs/quickstart_beginner.md`
- 폴더 구조 설명: `docs/folder_guide.md`
- 테스트 체크리스트: `docs/test_checklist.md`
- 운영자 점검 문서: `docs/operator_checklist.md`
- 추후 개발 고려사항: `docs/future_considerations.md`

## 빠른 실행

테스트 파일:

```text
D:\git_rk\automation\hwp_automation\test\2023_mei_workforce.hwpx
```

가장 쉬운 실행:

```powershell
cd D:\git_rk\automation\hwp_automation\hwpx_agent
python run_pipeline.py --input D:\git_rk\automation\hwp_automation\test\2023_mei_workforce.hwpx --expected-page-count 239 --require-table-cell-issues
```

위 명령은 아래 순서를 한 번에 실행합니다.

- 자산화
- 교정 이슈 생성
- 리뷰 샘플 파일 생성
- 기본 검증 실행

자산화:

```powershell
cd D:\git_rk\automation\hwp_automation\hwpx_agent
python run_assetize.py --input D:\git_rk\automation\hwp_automation\test\2023_mei_workforce.hwpx
```

교정 이슈 생성:

```powershell
python run_proofread.py --run-dir D:\git_rk\automation\hwp_automation\hwpx_agent\runs\<run_name>
```

검토 파일 생성:

```powershell
python run_issue_bridge.py --run-dir D:\git_rk\automation\hwp_automation\hwpx_agent\runs\<run_name> --init-review
```

검토 파일을 수정한 뒤 rebuild plan 생성:

```powershell
python run_issue_bridge.py --run-dir D:\git_rk\automation\hwp_automation\hwpx_agent\runs\<run_name> --review D:\git_rk\automation\hwp_automation\hwpx_agent\runs\<run_name>\assets\proofreading\issue_review.sample.json
```

복원 실행:

```powershell
python run_rebuild.py --run-dir D:\git_rk\automation\hwp_automation\hwpx_agent\runs\<run_name> --plan D:\git_rk\automation\hwp_automation\hwpx_agent\runs\<run_name>\assets\rebuild\rebuild_plan.from_issue_review.json
```

## 현재 지원 범위

- 본문 텍스트 문단 수정
- 안전한 텍스트 표 셀 수정
- 페이지 번호 추적
- 원본 위치 추적

## 현재 제한 범위

- 그림, 복합 컨트롤, 혼합 셀 자동 수정
- 머리말, 꼬리말, 마스터페이지 수정 복원
- 100% 동일한 새 HWPX 재생성
- 맞춤법 엔진 고도화
