# SPSS Syntax 자동 생성 도구

> **버전**: 1.0.0 | **최종 수정**: 2026-02-26

변수 가이드라인 CSV 파일을 SPSS 25.0 syntax (.sps) 파일로 자동 변환하는 도구입니다.

---

## 목차

1. [빠른 시작](#빠른-시작)
2. [CSV 입력 형식](#csv-입력-형식)
3. [CLI 옵션](#cli-옵션)
4. [간략 라벨 JSON 작성법](#간략-라벨-json-작성법)
5. [인코딩 가이드](#인코딩-가이드)
6. [트러블슈팅](#트러블슈팅)
7. [업데이트 이력](#업데이트-이력)

---

## 빠른 시작

```bash
# 기본 사용 (CP949 인코딩, SPSS 한국어 Windows 호환)
python guideline_to_sps.py input.csv --output label.sps

# 제목 지정
python guideline_to_sps.py input.csv -o label.sps --title "학생 설문조사"

# 간략 라벨 포함 생성
python guideline_to_sps.py input.csv -o label.sps ^
       --short-labels short.json --short-output label_short.sps

# UTF-8 인코딩으로 출력
python guideline_to_sps.py input.csv -o label.sps --encoding utf-8
```

---

## CSV 입력 형식

**4컬럼 구조**를 따라야 합니다:

| 컬럼 | 이름            | 설명                              |
| ---- | --------------- | --------------------------------- |
| 1    | `QtnType`       | 문항 유형 코드 (변수 행에만 존재) |
| 2    | `문항/보기번호` | 변수명 또는 보기번호(숫자)        |
| 3    | `내용`          | 문항 텍스트 또는 값 라벨 텍스트   |
| 4    | `VALUE LABELS`  | SPSS VALUE LABELS 원문 (참고용)   |

### 파싱 규칙

```
QtnType이 있고 + 문항/보기번호가 변수명  → 변수 행 (VARIABLE LABELS)
QtnType이 비어 있고 + 문항/보기번호가 숫자 → 값 라벨 행 (VALUE LABELS)
```

### CSV 예시

```csv
QtnType,문항/보기번호,내용,"VALUE LABELS"
11,SQ1,"귀하의 성별은?","   /SQ1"
,1,"남성","      1  '남성'"
,2,"여성","      2  '여성'"
```

---

## CLI 옵션

| 인자             | 필수 | 기본값     | 설명                               |
| ---------------- | ---- | ---------- | ---------------------------------- |
| `input_csv`      | ✅    | —          | 가이드라인 CSV 파일 경로           |
| `-o`, `--output` | ✅    | —          | 원본 라벨 SPS 출력 경로            |
| `--encoding`     | —    | `cp949`    | 출력 인코딩 (`cp949` 또는 `utf-8`) |
| `--title`        | —    | CSV 파일명 | SPS 파일 내 주석 제목              |
| `--short-labels` | —    | —          | 간략 라벨 JSON 파일 경로           |
| `--short-output` | —    | —          | 간략 라벨 SPS 출력 경로            |
| `--version`      | —    | —          | 버전 정보 표시                     |

---

## 간략 라벨 JSON 작성법

통계표 제목용 간략 라벨을 별도 JSON 파일로 관리합니다.

```json
{
  "SQ1": "성별",
  "SQ2": "학년",
  "A1": "RISE사업 인지 여부",
  "B1L_1": "[참여] 산학공동기술개발과제(R&D)"
}
```

- **키**: CSV의 변수명(문항/보기번호)과 정확히 일치
- **값**: 통계표에 표시할 간략 라벨
- JSON에 없는 변수는 **원본 라벨이 그대로** 유지됨

> 예시 파일: `examples/short_labels_sample.json`

---

## 인코딩 가이드

| 환경                     | 권장 인코딩        | 옵션                      |
| ------------------------ | ------------------ | ------------------------- |
| SPSS 25.0 한국어 Windows | **CP949 (EUC-KR)** | `--encoding cp949` (기본) |
| SPSS 28+ / Unicode 모드  | UTF-8              | `--encoding utf-8`        |

---

## 트러블슈팅

### 한글 깨짐 (SPSS에서)
- `--encoding cp949`로 생성했는지 확인
- SPSS에서 파일 열기 시 인코딩 설정 확인

### CP949 인코딩 에러
- `UnicodeEncodeError: 'cp949' codec can't encode character` 발생 시
- 원인: CSV에 CP949로 표현할 수 없는 특수문자 포함
- 해결: `clean_text()` 함수에 해당 문자 치환 규칙 추가
- 주요 사례: 반각 중점 `ﾥ` (U+FF65) → `·` (U+00B7)

### VS Code에서 CP949 파일 보기
1. 하단 상태바의 인코딩 영역 클릭
2. **Reopen with Encoding** → **Korean (EUC-KR)** 선택

---

## 업데이트 이력

전체 변경 이력은 [CHANGELOG.md](./CHANGELOG.md)를 참조하세요.

| 버전  | 날짜       | 주요 변경   |
| ----- | ---------- | ----------- |
| 1.0.0 | 2026-02-26 | 최초 릴리즈 |

---

## SPS ↔ MD 변환 도구

SPSS 구문 파일(`.sps`)과 마크다운(`.md`) 간 양방향 변환 도구입니다.

### 빠른 시작

```bash
# SPS → MD 변환
python sps_to_md.py input.sps -o output.md

# MD → SPS 역변환
python md_to_sps.py output.md -o restored.sps

# 배치 변환 (디렉토리 내 전체)
python sps_to_md.py ./Macro/ --batch -o ./Macro_MD/
python md_to_sps.py ./Macro_MD/ --batch -o ./Macro_SPS/
```

> 상세 가이드: [docs/sps_md_conversion_guide.md](./docs/sps_md_conversion_guide.md)
