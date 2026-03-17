# SPSS 엑셀 → 마크다운 변환 (file_converter)

SPSS 통계분석 출력 엑셀(XLS/CSV)을 구조화된 마크다운으로 자동 변환합니다.

## 빠른 시작

```cmd
cd d:\git_rk\automation\spss_automation\file_converter\scripts
python spss_excel_to_md.py --input "입력파일.xls"
```

산출물은 입력 파일 디렉토리의 `output/` 하위폴더에 자동 생성됩니다.

## CLI 옵션

| 인자 | 필수 | 기본값 | 설명 |
|------|------|--------|------|
| `--input`, `-i` | ✅ | — | 입력 파일 경로 (XLS/CSV) |
| `--output-dir`, `-o` | — | 입력 디렉토리/output/ | 출력 디렉토리 |
| `--exclude`, `-e` | — | config.py 참조 | 제외할 문항번호 |
| `--prefix` | — | 원본 파일명에서 자동 생성 | 출력 파일 접두사 |
| `--project-name` | — | config.py 참조 | 프로젝트명 |
| `--survey-target` | — | config.py 참조 | 조사 대상 |

## 출력 파일

| 파일 | 내용 |
|------|------|
| `report_{원본파일명}_{YYMMDD_HHMM}.md` | 요약 보고서 (전체 행만, 항목/빈도/비율) |
| `report_{원본파일명}_{YYMMDD_HHMM}_cross.md` | 교차표 보고서 (전체+하위집단 통합 1개 테이블) |

- `(output)` 접두사 자동 제거, 공백 → 언더스코어 변환
- `--prefix` 수동 지정 시 해당 값 사용

## 블록 유형

| 유형 | 판별 조건 |
|------|-----------| 
| 빈도표 | 라벨행에 빈도/비율 쌍 + 고유 카테고리 |
| 교차표 | 이진 카테고리 (참여/미참여 등) |
| 평균표 | 업체수/평균 쌍 |

새 유형 추가: `BLOCK_TYPE_REGISTRY`에 detect 함수 등록

## XLS 비율 처리

XLS 파일의 백분율 셀은 `formatting_info=True`로 서식을 감지하여 원본 소수점 자리수 그대로 변환합니다 (예: `0.4545...` → `45.5%`).

## 로그 관리

`logs/` 디렉토리에서 관리:
- `changelog.md` — 업데이트 이력
- `error_report.md` — 에러 리포트
- `execution_history.csv` — 실행 기록 (자동)
