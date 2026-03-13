# 파이프라인 상세 가이드

## 아키텍처

```
입력 (.xls/.xlsx/.md)
    ↓
파서 자동 선택 (parser_xls / parser_md)
    ↓
테이블 탐지 & 데이터 추출 (labels, pcts, freqs, n)
    ↓
chart_rules 순회 → 차트 유형 자동 판별
    ↓
chart_builder → 테마 적용 + 차트 생성
    ↓
출력 (.pptx)
```

## 2단계 실행 구조

### 통합: `run_ppt.py`
```bash
python run_ppt.py --module chart --input data.xls
python run_ppt.py --module chart,table --input data.xls  # 향후
python run_ppt.py --module all --input data.xls          # 향후
```

### 개별: `chart/run_chart.py`
```bash
cd chart
python run_chart.py --input data.xls --theme white_clean --sort both
```

## CLI 옵션

| 옵션 | 설명 | 기본값 |
|---|---|---|
| `--input`, `-i` | 입력 파일 경로 | (필수) |
| `--output`, `-o` | 출력 파일명 | 자동 생성 |
| `--theme`, `-t` | 테마명 | white_clean |
| `--sort`, `-s` | 정렬 (desc/original/both) | desc |
| `--skip` | 스킵 키워드 (쉼표 구분) | 불만족 이유,프로그램별 만족도 |

## 파서 동작 원리

### XLS 파서 (parser_xls)
1. DataFrame 로드 (pandas + xlrd)
2. 첫 번째 열에서 SQ/A/B/C 등으로 시작하는 테이블 헤더 탐지
3. 헤더 기준 +2행=항목명, +4행=전체 데이터
4. 홀수 열=빈도, 짝수 열=비율 으로 추출

### MD 파서 (parser_md)
1. `## 번호. 제목` 패턴으로 섹션 분리
2. 마크다운 테이블 (\|로 구분) 파싱
3. 항목명/빈도/비율 추출

## 에러 처리
- 개별 테이블 오류 시 해당 테이블만 SKIP
- 에러 내용은 로그에 `[ERROR]` 태그로 기록
- 전체 실행은 중단되지 않음
