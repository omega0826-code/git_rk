# body_modifier — HWPX 본문 수정 자동화 모듈

HWPX 파일의 본문을 분석하고, 규칙 기반으로 수정한 뒤, 새로운 HWPX를 생성하는 파이프라인입니다.

## 빠른 시작

```bash
cd d:\git_rk\automation\hwp_automation\body_modifier
python run_body_mod.py --input 원본.hwpx --spec config/sample_spec.json --output 결과.hwpx
```

## 파이프라인 흐름

```
① parser.py (파싱/분석)  →  ② modifier.py (본문 수정)  →  ③ builder.py (HWPX 빌드)
```

| 모듈 | 역할 | 입력 | 출력 |
|------|------|------|------|
| `parser.py` | HWPX 구조 분석 | `.hwpx` | 메타데이터 dict + `parsed.md` |
| `modifier.py` | 규칙 기반 수정 | section XML + rules | 수정된 XML bytes |
| `builder.py` | HWPX ZIP 패키징 | 수정 파일 + 원본 | `.hwpx` |

## 디렉토리 구조

```
body_modifier/
├── run_body_mod.py         ← 통합 파이프라인 CLI
├── modules/                ← 개별 모듈 (parser, modifier, builder)
├── config/                 ← 수정 사양 JSON + 네임스페이스 상수
├── docs/                   ← 프로세스 문서, 스타일 레퍼런스
├── examples/               ← 사용 예시 (울산 프로젝트 등)
├── logs/                   ← 실행 로그 (자동 생성)
└── tests/                  ← 단위 테스트
```

## 수정 사양 (spec.json)

`config/sample_spec.json` 참조. 지원 액션:
- `insert_after`: 매칭 문단 뒤에 새 문단 삽입
- `replace_text`: 문단 텍스트 교체
- `change_style`: 문단의 charPrIDRef 변경
- `delete_para`: 문단 삭제

## 의존 패키지

```bash
pip install lxml
```
