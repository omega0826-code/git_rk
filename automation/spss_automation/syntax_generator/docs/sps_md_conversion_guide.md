# SPS ↔ MD 변환 도구 활용 가이드

> **버전**: 1.0.0 | **최종 수정**: 2026-02-26

SPSS 구문 파일(`.sps`)과 마크다운(`.md`) 파일 간 양방향 변환 도구입니다.

---

## 목차

1. [개요](#개요)
2. [사전 요건](#사전-요건)
3. [SPS → MD 변환](#sps--md-변환)
4. [MD → SPS 변환](#md--sps-변환)
5. [배치 변환](#배치-변환)
6. [마크다운 형식 규격](#마크다운-형식-규격)
7. [인코딩 가이드](#인코딩-가이드)
8. [활용 시나리오](#활용-시나리오)
9. [트러블슈팅](#트러블슈팅)

---

## 개요

| 도구             | 기능            | 파일           |
| ---------------- | --------------- | -------------- |
| **sps_to_md.py** | SPS → MD 변환   | `.sps` → `.md` |
| **md_to_sps.py** | MD → SPS 역변환 | `.md` → `.sps` |

**핵심 특징:**
- 인코딩 자동 감지 (UTF-8, CP949)
- 원본 내용 무변경 보장 (왕복 변환 Round-trip 지원)
- 메타 정보 자동 기록 (원본 파일명, 인코딩, 변환 시각)
- 단일 파일 / 배치(디렉토리) 모드 지원

---

## 사전 요건

- **Python 3.7+**
- 추가 패키지 불필요 (표준 라이브러리만 사용)

---

## SPS → MD 변환

### 기본 사용법

```bash
# 단일 파일 변환 (같은 위치에 .md 생성)
python sps_to_md.py input.sps

# 출력 경로 지정
python sps_to_md.py input.sps -o output.md

# 제목 지정
python sps_to_md.py input.sps --title "연구장비 기업 명령문"
```

### CLI 옵션

| 인자             | 필수 | 기본값                | 설명                             |
| ---------------- | ---- | --------------------- | -------------------------------- |
| `input`          | ✅    | —                     | 입력 SPS 파일 또는 디렉토리 경로 |
| `-o`, `--output` | —    | 입력 파일과 동일 위치 | 출력 경로                        |
| `--encoding`     | —    | 자동 감지             | 입력 파일 인코딩 지정            |
| `--title`        | —    | 파일명에서 생성       | 마크다운 제목                    |
| `--batch`        | —    | —                     | 배치 모드 활성화                 |
| `--version`      | —    | —                     | 버전 표시                        |

### 인코딩 자동 감지 순서

1. UTF-8 BOM 확인
2. 파일 내 `* Encoding: ...` SPSS 주석 참조
3. UTF-8 디코딩 시도
4. CP949 fallback

---

## MD → SPS 변환

### 기본 사용법

```bash
# 단일 파일 역변환 (메타 정보에서 원본 파일명/인코딩 참조)
python md_to_sps.py input.md

# 출력 경로 지정
python md_to_sps.py input.md -o output.sps

# UTF-8 인코딩으로 출력
python md_to_sps.py input.md --encoding utf-8
```

### CLI 옵션

| 인자             | 필수 | 기본값                       | 설명                            |
| ---------------- | ---- | ---------------------------- | ------------------------------- |
| `input`          | ✅    | —                            | 입력 MD 파일 또는 디렉토리 경로 |
| `-o`, `--output` | —    | 원본 파일명 참조 또는 `.sps` | 출력 경로                       |
| `--encoding`     | —    | 메타 정보 참조 또는 `cp949`  | 출력 인코딩                     |
| `--batch`        | —    | —                            | 배치 모드 활성화                |
| `--version`      | —    | —                            | 버전 표시                       |

### 출력 인코딩 결정 우선순위

1. `--encoding` CLI 인자
2. 마크다운 메타 정보의 `원본 인코딩` 값
3. 기본값: `cp949`

---

## 배치 변환

### SPS → MD (전체 디렉토리)

```bash
# 같은 디렉토리에 .md 파일 생성
python sps_to_md.py ./Macro/ --batch

# 별도 출력 디렉토리 지정
python sps_to_md.py ./Macro/ --batch -o ./Macro_MD/
```

### MD → SPS (전체 디렉토리)

```bash
# SPS 코드 블록이 있는 .md 파일만 변환 (없으면 SKIP)
python md_to_sps.py ./Macro_MD/ --batch -o ./Macro_SPS/
```

---

## 마크다운 형식 규격

`sps_to_md.py`가 생성하는 마크다운 파일의 구조:

```markdown
# [제목]

> **원본 파일**: `[파일명.sps]`  
> **원본 인코딩**: `[cp949|utf-8]`  
> **변환 시각**: YYYY-MM-DD HH:MM:SS

​```sps
[SPSS 구문 원본 내용 전체]
​```
```

> [!IMPORTANT]
> `md_to_sps.py`는 위 형식의 마크다운에서 ` ```sps ``` ` 코드 블록만 추출합니다.
> 코드 블록 외부의 내용(제목, 메타 정보)은 참조용이며 SPS 출력에 포함되지 않습니다.

---

## 인코딩 가이드

| 환경                     | 권장 인코딩 | 비고               |
| ------------------------ | ----------- | ------------------ |
| SPSS 25.0 한국어 Windows | **CP949**   | 기본값             |
| SPSS 28+ / Unicode 모드  | UTF-8       | `--encoding utf-8` |
| 마크다운 저장            | **UTF-8**   | 항상 UTF-8         |

### 왕복 변환 (Round-trip)

```
원본.sps (CP949) → sps_to_md → 파일.md (UTF-8) → md_to_sps → 복원.sps (CP949)
```

메타 정보에 원본 인코딩이 기록되므로, 역변환 시 별도 인코딩 지정 없이도 원본과 동일한 인코딩으로 복원됩니다.

---

## 활용 시나리오

### 1. 버전 관리 (Git)

CP949 인코딩인 SPS 파일은 Git에서 diff 확인이 어렵습니다.
UTF-8 마크다운으로 변환하면 변경 이력을 쉽게 추적할 수 있습니다.

```bash
# 작업 전: SPS → MD 변환
python sps_to_md.py macro.sps -o macro.md
git add macro.md && git commit -m "매크로 마크다운 백업"

# 수정 후: 변경 사항 확인
git diff macro.md
```

### 2. 문서화 및 리뷰

마크다운 형태로 변환하면 GitHub/GitLab에서 코드 리뷰가 가능합니다.

### 3. SPSS 매크로 아카이빙

```bash
# 전체 매크로 디렉토리를 마크다운으로 백업
python sps_to_md.py ./Macro/ --batch -o ./Macro_Archive/

# 필요 시 역변환하여 SPSS에서 사용
python md_to_sps.py ./Macro_Archive/target.md -o ./Macro/target.sps
```

---

## 트러블슈팅

### 한글 깨짐 (SPS → MD)

- 원인: 인코딩 자동 감지 실패
- 해결: `--encoding cp949` 또는 `--encoding utf-8`을 명시 지정

### `ValueError: SPS 코드 블록을 찾을 수 없습니다` (MD → SPS)

- 원인: 마크다운 파일에 ` ```sps ``` ` 코드 블록이 없음
- 해결: 코드 블록이 ` ```sps `로 시작하는지 확인 (` ```spss `, ` ``` ` 등은 불인식)

### CP949 인코딩 에러 (MD → SPS)

- 원인: 마크다운 편집 중 CP949 비호환 문자가 삽입됨
- 해결: `--encoding utf-8`로 출력하거나, 해당 문자를 수정

### 파일명에 한글이 있는 경우

- Windows 환경에서는 정상 동작합니다
- Linux/Mac에서는 터미널 인코딩에 따라 파일명이 깨질 수 있으므로 `-o` 옵션으로 출력 경로를 명시 지정하세요
