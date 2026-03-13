# hwpxskill 스킬 반영 가이드

`body_modifier` 모듈의 기능을 기존 `hwpxskill`에 통합하기 위한 상세 절차입니다.

---

## 1. 현재 스킬 구조 파악

기존 `hwpxskill` (`d:\git_rk\.agent\skills\hwpxskill\`)은 다음 워크플로우를 제공합니다:

| 워크플로우 | 용도 | 핵심 도구 |
|-----------|------|----------|
| 기본 동작 모드 | 첨부 HWPX → 분석 → 복원 → 재작성 | `analyze_template.py` → `build_hwpx.py` |
| XML-first 생성 | 템플릿 선택 → section 작성 → 빌드 | `build_hwpx.py` |

**body_modifier**는 여기에 **"워크플로우 3: 규칙 기반 본문 수정"**을 추가합니다.

---

## 2. SKILL.md에 추가할 내용

`d:\git_rk\.agent\skills\hwpxskill\SKILL.md` 파일의 워크플로우 섹션(현재 `## 워크플로우 1` 이후) 뒤에 아래 내용을 추가합니다.

### 추가 위치

```
기존 구조:
  ## 워크플로우 1: XML-first 문서 생성  (약 112행~)
  ...
  → 여기 뒤에 추가 ↓

  ## 워크플로우 3: 규칙 기반 본문 수정 (body_modifier)   ← 신규
```

### 추가할 마크다운 내용

````markdown
---

## 워크플로우 3: 규칙 기반 본문 수정 (body_modifier)

기존 HWPX 문서의 본문을 **JSON 수정 사양(spec)**에 따라 일괄 수정하는 파이프라인.
문단 삽입, 텍스트 교체, 스타일 변경, 문단 삭제를 지원하며 새로운 글자 스타일(charPr)을 동적으로 추가할 수 있다.

**모듈 위치**: `d:\git_rk\automation\hwp_automation\body_modifier\`

### 사용 시점

- 원본 HWPX의 **구조(표, 페이지, 섹션)는 유지**하면서 특정 문단만 추가/수정/삭제하고 싶을 때
- 수정 내용에 **원본에 없는 새로운 스타일**(빨간색, 볼드 등)을 적용하고 싶을 때
- 여러 문단에 **동일한 규칙을 일괄 적용**하고 싶을 때

### 파이프라인 흐름

```
parser.py (분석) → modifier.py (수정) → builder.py (빌드)
```

### 실행 방법

```bash
cd d:\git_rk\automation\hwp_automation\body_modifier
python run_body_mod.py --input 원본.hwpx --spec config/sample_spec.json --output 결과.hwpx
```

### 수정 사양 (spec.json) 형식

```json
{
    "new_styles": [
        {
            "type": "charPr",
            "base_id": "22",
            "changes": {"textColor": "#FF0000"}
        }
    ],
    "target_section": "Contents/section1.xml",
    "rules": [
        {
            "action": "insert_after",
            "strategy": "startswith",
            "pattern": "교육 운영 선호",
            "text": "삽입할 텍스트"
        }
    ]
}
```

### 지원 액션 및 매칭 전략

| 액션 | 설명 |
|------|------|
| `insert_after` | 매칭 문단 뒤에 새 문단 삽입 |
| `replace_text` | 문단 텍스트 교체 |
| `change_style` | 문단의 charPrIDRef 변경 |
| `delete_para` | 문단 삭제 |

| 매칭 전략 | 설명 |
|---------|------|
| `startswith` | 문단 텍스트가 패턴으로 시작 |
| `contains` | 문단 텍스트에 패턴 포함 |
| `regex` | 정규식 매칭 |

### 핵심 기술 (기존 스킬 확장)

1. **charPr 동적 인젝션**: header.xml의 기존 charPr을 deepcopy하여 속성만 오버라이딩, itemCnt 자동 갱신
2. **mimetype ZIP_STORED 보장**: HWPX ZIP 패키징 시 mimetype만 비압축으로 분기 저장
3. **역순 삽입(Index Shift 방어)**: 문단 삽입 좌표를 수집 후 역순 처리하여 인덱스 밀림 방지

### 관련 문서

- `body_modifier/docs/process_overview.md` — 4단계 프로세스 설계
- `body_modifier/docs/style_reference.md` — charPr/paraPr 속성 레퍼런스
- `body_modifier/docs/troubleshooting.md` — 빌드 이슈 해결법
````

---

## 3. 디렉토리 구조 섹션 업데이트

SKILL.md의 `## 디렉토리 구조` 섹션(약 84~108행)에 automation 참조를 추가합니다:

```diff
 └── references/
     └── hwpx-format.md                    # OWPML XML 요소 레퍼런스
+
+# 연관 모듈 (automation)
+d:\git_rk\automation\hwp_automation\body_modifier\
+├── run_body_mod.py                       # 통합 파이프라인 CLI
+├── modules/                              # parser, modifier, builder
+├── config/                               # 수정 사양 JSON, 네임스페이스
+├── docs/                                 # 프로세스/스타일/트러블슈팅 문서
+├── examples/                             # 사용 예시
+└── logs/                                 # 실행 로그
```

---

## 4. scripts/ 연동 여부 판단

두 가지 방식이 가능합니다:

### 방식 A: SKILL.md에 경로 참조만 추가 (권장)

`body_modifier`를 독립 모듈로 유지하고 SKILL.md에서 경로만 안내합니다.

- **장점**: 모듈 독립성 유지, 중복 코드 없음
- **단점**: 스킬 디렉토리 안에 코드가 없어 다른 환경에서 스킬만 복사 시 누락

### 방식 B: scripts/에 심볼릭 링크 또는 래퍼 스크립트 추가

```bash
# 심볼릭 링크 (Windows)
mklink /D "d:\git_rk\.agent\skills\hwpxskill\scripts\body_modifier" "d:\git_rk\automation\hwp_automation\body_modifier\modules"
```

또는 래퍼 스크립트:
```python
# d:\git_rk\.agent\skills\hwpxskill\scripts\run_body_mod.py
"""body_modifier 파이프라인 래퍼"""
import subprocess, sys
BODY_MOD = r"d:\git_rk\automation\hwp_automation\body_modifier\run_body_mod.py"
sys.exit(subprocess.call([sys.executable, BODY_MOD] + sys.argv[1:]))
```

- **장점**: 스킬 디렉토리에서 직접 실행 가능
- **단점**: 유지보수 포인트 증가

---

## 5. 실행 체크리스트

1. [ ] SKILL.md에 워크플로우 3 섹션 추가
2. [ ] SKILL.md 디렉토리 구조에 body_modifier 참조 추가
3. [ ] scripts/ 연동 방식 결정 (A 또는 B)
4. [ ] 연동 방식 B 선택 시 심볼릭 링크 또는 래퍼 생성
5. [ ] SKILL.md의 `description` 프론트매터에 본문 수정 기능 언급 추가
      ```yaml
      description: "한글(HWPX) 문서 생성/읽기/편집/본문 수정 스킬..."
      ```
6. [ ] 테스트: 스킬 트리거 확인 (에이전트가 body_modifier 관련 요청 시 SKILL.md를 참조하는지)
