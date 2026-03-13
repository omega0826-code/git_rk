# PPT Automation

PPT 자동 생성 파이프라인 — 설문조사 데이터(XLS/마크다운)를 편집 가능한 PPT 차트로 자동 변환

## 빠른 시작
```bash
pip install -r requirements.txt
python run_ppt.py --module chart --input "data.xls" --sort both
```

## 폴더 구조
```
ppt_automation/
├── run_ppt.py          # 통합 파이프라인
├── chart/              # 차트 자동화
│   ├── run_chart.py    # 개별 파이프라인
│   ├── chart_builder.py
│   ├── chart_rules/    # 차트 유형 판별 (플러그인)
│   └── themes/         # 테마 JSON
├── table/              # 표 자동화 (향후)
├── wording/            # 워딩 자동화 (향후)
├── docs/               # 가이드 문서
├── logs/               # 실행 로그
├── examples/           # 프로젝트별 설정 예시
└── CHANGELOG.md        # 변경 이력
```

## 지원 입력 형식
| 형식 | 파서 | 설명 |
|---|---|---|
| `.xls`, `.xlsx` | parser_xls | SPSS 교차분석표 |
| `.md` | parser_md | 마크다운 테이블 |

## 차트 유형
| 유형 | 차트 | 판별 기준 |
|---|---|---|
| pie | 파이/도넛 | 항목 6개 이하 + 합 ~100% |
| radar | 레이더 | 평균 점수, 인식 수준 |
| stacked | 누적막대 | 대학교별 비교 |
| hbar | 수평막대 | 기본 (폴백) |

## 상세 문서
- [quick_start.md](docs/quick_start.md) — 3분 가이드
- [pipeline_guide.md](docs/pipeline_guide.md) — 파이프라인 상세
- [theme_guide.md](docs/theme_guide.md) — 테마 커스터마이징
- [chart_rules_guide.md](docs/chart_rules_guide.md) — 차트 규칙 추가
- [troubleshooting.md](docs/troubleshooting.md) — 트러블슈팅

## 의존성
```
python-pptx>=0.6.21
openpyxl>=3.0.0
pandas>=2.0.0
xlrd>=2.0.1
```
