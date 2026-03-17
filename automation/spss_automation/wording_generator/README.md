# 교차표 → 워딩 자동 생성 (wording_generator)

`file_converter`가 생성한 교차표 MD(`_cross.md`)를 파싱하여 보고서용 워딩을 자동 생성합니다.

## 빠른 시작

```cmd
cd d:\git_rk\automation\spss_automation\wording_generator\scripts
python generate_wording.py --input "report_*_cross.md"
```

산출물은 입력 파일 디렉토리의 `wording/` 하위폴더에 생성됩니다.

## CLI 옵션

| 인자 | 필수 | 기본값 | 설명 |
|------|------|--------|------|
| `--input`, `-i` | ✅ | — | 입력 `_cross.md` 파일 경로 |
| `--output-dir`, `-o` | — | 입력 디렉토리/wording/ | 출력 디렉토리 |
| `--exclude`, `-e` | — | config.py 참조 | 제외할 문항번호 |
| `--threshold`, `-t` | — | 10.0 | 특성별 감지 임계값(%p) |

## 워딩 규칙

`prompts/survey_wording_prompt.md` 참조. 핵심:

- **전체**: 1~3순위 기술, 합산 조합 (해당 시)
- **특성별**: 전체 대비 차이 큰 독립변수만 기술
- **문체**: 명사형 종결 (~이었음, ~높았음), 강조 서식 금지
- **비율**: 원본 수치 그대로 사용 (재계산 없음)

## 로그 관리

`logs/` 디렉토리:
- `changelog.md` — 업데이트 이력
- `execution_history.csv` — 실행 기록 (자동)
