# HWPX 스타일가이드 모듈

HWPX 파일에서 스타일(폰트, 크기, 색상, 정렬 등)을 추출하여 프로필로 관리하고, 마크다운 파일을 해당 스타일로 HWPX 변환합니다.

## 구조

```
style_guide/
├── extract_style.py         ← 스타일 추출 스크립트
├── md_to_styled_hwpx.py     ← MD→HWPX 변환 스크립트
├── profiles/                ← 프로필 저장소
│   ├── _index.json              전체 프로필 목록·기본값
│   └── <프로필명>/
│       ├── style_guide.json     스타일 정의(charPr/paraPr/fontfaces/역할매핑)
│       └── header.xml           원본 header.xml (빌드용)
├── docs/                    ← 트러블슈팅 리포트
│   └── troubleshooting.md
└── README.md                ← 이 파일
```

### 등록된 프로필 목록

| 프로필명 | 출처 | 설명 | 기본 |
|----------|------|------|:----:|
| `bix` | `.test/bix_test.hwpx` | BIX 포승지구 보고서 스타일 | ★ |

## 사용법

### 1. 프로필 추출

```bash
python extract_style.py --input 원본.hwpx --profile-name bix --description "BIX 보고서"
```

### 2. 프로필 확인

```bash
python extract_style.py --list            # 프로필 목록
python extract_style.py --info bix        # 상세 정보
```

### 3. MD → HWPX 변환

```bash
# 프로필 지정
python md_to_styled_hwpx.py --input wording.md --profile bix --output result.hwpx

# 기본 프로필 사용 (--profile 생략)
python md_to_styled_hwpx.py --input wording.md --output result.hwpx
```

> **참고**: CMD에서 한글 파일명이 깨지는 경우 Python wrapper 스크립트에서 `subprocess.run()`으로 호출하세요.

## 스타일 매핑 (bix 프로필 기준)

| 마크다운 | 역할 | charPr | 폰트 | paraPr | 비고 |
|---------|------|--------|------|--------|------|
| `# 제목` | h1 | 37 | 18pt HY견고딕 | 62 (LEFT 160%) | 변환 시 **필터링** (출력 안 함) |
| `## 제목` | h2 | 39 | 14pt 한양견고딕 | 62 (LEFT 160%) | `(N=xxx)` 접미사 자동 제거 |
| `### 제목` | h3 | 20 | 10pt 맑은 고딕 Bold | 62 (LEFT 160%) | 글머리표 미사용 |
| `* 항목` | bullet | 54 | 12pt 휴먼명조 | 56 (JUSTIFY 160%) | paraPr 스타일 글머리표 |
| `> 인용` | blockquote | 1 | 9pt 휴먼고딕 | 83 (LEFT 140%) | `생성일시` 포함 시 필터링 |
| `---` | separator | — | — | — | 필터링 (출력 안 함) |
| 일반 텍스트 | body | 54 | 12pt 휴먼명조 | 56 (JUSTIFY 160%) | |

## 변환 시 자동 처리

- **h1 제목** (`# 통계 분석 결과 워딩 보고서`) → 삭제
- **메타데이터** (`> 생성일시: ...`) → 삭제
- **구분선** (`---`) → 삭제
- **h2 접미사** `(N=140, 단수 응답)` → 자동 제거
- **`**bold**` 서식** → 자동 제거

## role_mapping 수동 편집

`profiles/<이름>/style_guide.json`의 `role_mapping`을 직접 편집 가능:

```json
"role_mapping": {
  "h1": {"charPrIDRef": "37", "paraPrIDRef": "62"},
  "h2": {"charPrIDRef": "39", "paraPrIDRef": "62"},
  "body": {"charPrIDRef": "54", "paraPrIDRef": "56"}
}
```
