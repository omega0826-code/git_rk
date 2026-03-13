# Git Push & Pull 상세 설명서

> **작성일**: 2026-03-03  
> **저장소**: https://github.com/omega0826-code/database  
> **브랜치**: master

---

## 목차

1. [Git 기본 개념](#1-git-기본-개념)
2. [Git Push — 원격 저장소에 업로드](#2-git-push--원격-저장소에-업로드)
3. [Git Pull — 원격 저장소에서 가져오기](#3-git-pull--원격-저장소에서-가져오기)
4. [Git Clone — 저장소 전체 복제](#4-git-clone--저장소-전체-복제)
5. [일상적인 작업 흐름](#5-일상적인-작업-흐름)
6. [자주 발생하는 오류와 해결 방법](#6-자주-발생하는-오류와-해결-방법)
7. [유용한 Git 명령어 모음](#7-유용한-git-명령어-모음)
8. [용어 정리](#8-용어-정리)

---

## 1. Git 기본 개념

### 1.1 Git이란?

Git은 **분산 버전 관리 시스템(DVCS)**으로, 파일의 변경 이력을 추적하고 여러 사람이 협업할 수 있도록 해주는 도구입니다.

### 1.2 로컬 저장소 vs 원격 저장소

| 구분 | 로컬 저장소 (Local) | 원격 저장소 (Remote) |
|------|---------------------|----------------------|
| **위치** | 내 컴퓨터 | GitHub, GitLab 등 서버 |
| **용도** | 작업 및 커밋 | 백업, 공유, 협업 |
| **접근** | 오프라인 가능 | 인터넷 필요 |

### 1.3 Git의 3가지 영역

```
┌─────────────────────────────────────────────────┐
│             작업 디렉토리 (Working Directory)      │
│             → 실제 파일을 편집하는 공간              │
└──────────────────────┬──────────────────────────┘
                       │ git add
                       ▼
┌─────────────────────────────────────────────────┐
│             스테이징 영역 (Staging Area)            │
│             → 커밋할 파일을 모아두는 공간             │
└──────────────────────┬──────────────────────────┘
                       │ git commit
                       ▼
┌─────────────────────────────────────────────────┐
│             로컬 저장소 (Local Repository)          │
│             → 커밋된 이력이 저장되는 공간             │
└──────────────────────┬──────────────────────────┘
                       │ git push / git pull
                       ▼
┌─────────────────────────────────────────────────┐
│             원격 저장소 (Remote Repository)         │
│             → GitHub 등 서버에 저장된 공간           │
└─────────────────────────────────────────────────┘
```

---

## 2. Git Push — 원격 저장소에 업로드

### 2.1 개요

`git push`는 **로컬 저장소의 커밋을 원격 저장소에 업로드**하는 명령어입니다.

### 2.2 기본 사용법

```bash
# 기본 push (upstream이 설정된 경우)
git push

# 특정 원격 저장소와 브랜치를 지정하여 push
git push origin master

# 처음 push할 때 upstream 설정과 함께 push
git push --set-upstream origin master
# 또는 줄여서
git push -u origin master
```

### 2.3 Push 전 필수 단계

Push를 하기 전에 반드시 **add → commit** 과정을 거쳐야 합니다.

```bash
# 1단계: 변경된 파일을 스테이징 영역에 추가
git add .                  # 모든 변경 파일 추가
git add 파일명.txt          # 특정 파일만 추가

# 2단계: 커밋 (변경 사항에 대한 설명 작성)
git commit -m "변경 내용에 대한 설명"

# 3단계: 원격 저장소에 업로드
git push
```

### 2.4 Push 옵션 상세

| 명령어 | 설명 |
|--------|------|
| `git push` | 기본 push (upstream 설정 필요) |
| `git push origin master` | origin 원격 저장소의 master 브랜치에 push |
| `git push -u origin master` | upstream 설정 + push (최초 1회) |
| `git push --force` | ⚠️ 강제 push (원격 이력 덮어쓰기, 주의 필요) |
| `git push --dry-run` | 실제 push 없이 결과만 미리 확인 |
| `git push --tags` | 태그를 원격 저장소에 push |

### 2.5 Push 예시 시나리오

```bash
# 파일 수정 후 push하는 전체 과정
echo "새로운 내용" >> README.md     # 파일 수정
git status                         # 변경 상태 확인
git add README.md                  # 스테이징에 추가
git commit -m "README 내용 추가"    # 커밋
git push                           # GitHub에 업로드
```

---

## 3. Git Pull — 원격 저장소에서 가져오기

### 3.1 개요

`git pull`은 **원격 저장소의 변경 사항을 로컬 저장소로 가져와서 병합(merge)**하는 명령어입니다.

### 3.2 기본 사용법

```bash
# 기본 pull (upstream이 설정된 경우)
git pull

# 특정 원격 저장소와 브랜치를 지정하여 pull
git pull origin master
```

### 3.3 Pull = Fetch + Merge

`git pull`은 실제로 두 가지 동작을 한 번에 수행합니다:

```bash
# git pull은 아래 두 명령어를 합친 것입니다:
git fetch    # 원격 저장소의 변경 사항을 가져옴 (병합하지 않음)
git merge    # 가져온 변경 사항을 현재 브랜치에 병합
```

| 명령어 | 동작 | 로컬 파일 변경 |
|--------|------|----------------|
| `git fetch` | 원격 변경 사항 다운로드만 | ❌ 변경 안 됨 |
| `git merge` | 다운로드한 변경 사항 병합 | ✅ 변경됨 |
| `git pull` | fetch + merge 동시 수행 | ✅ 변경됨 |

### 3.4 Pull 옵션 상세

| 명령어 | 설명 |
|--------|------|
| `git pull` | 기본 pull (fetch + merge) |
| `git pull origin master` | origin의 master 브랜치에서 pull |
| `git pull --rebase` | merge 대신 rebase 방식으로 가져오기 (이력이 깔끔해짐) |
| `git pull --no-commit` | 자동 커밋 없이 병합만 수행 |

### 3.5 Pull 사용 시기

- ✅ 작업 시작 전에 최신 상태로 업데이트할 때
- ✅ 다른 사람(또는 다른 컴퓨터)이 push한 변경 사항을 가져올 때
- ✅ GitHub 웹에서 직접 수정한 내용을 로컬에 반영할 때

---

## 4. Git Clone — 저장소 전체 복제

### 4.1 개요

`git clone`은 **원격 저장소를 통째로 복제**하여 로컬에 새 폴더를 만드는 명령어입니다.

### 4.2 사용법

```bash
# 기본 clone (저장소 이름으로 폴더 생성)
git clone https://github.com/omega0826-code/database.git

# 특정 폴더 이름으로 clone
git clone https://github.com/omega0826-code/database.git my-database

# 특정 브랜치만 clone
git clone -b master https://github.com/omega0826-code/database.git
```

### 4.3 Clone vs Pull 비교

| 구분 | `git clone` | `git pull` |
|------|-------------|------------|
| **사용 시기** | 처음 저장소를 가져올 때 | 이미 있는 저장소를 업데이트할 때 |
| **실행 횟수** | 프로젝트당 1회 | 필요할 때마다 반복 |
| **결과** | 새 폴더 생성 + 전체 이력 복제 | 변경된 부분만 업데이트 |

---

## 5. 일상적인 작업 흐름

### 5.1 기본 작업 흐름 (혼자 작업)

```
[작업 시작]
    │
    ├── git pull                      ← 최신 상태로 업데이트
    │
    ├── 파일 수정 / 추가 / 삭제         ← 실제 작업
    │
    ├── git status                    ← 변경 상태 확인
    │
    ├── git add .                     ← 변경 파일 스테이징
    │
    ├── git commit -m "작업 내용 설명"  ← 커밋
    │
    └── git push                      ← GitHub에 업로드
```

### 5.2 다른 컴퓨터에서 작업 시작할 때

```
[처음인 경우]
    git clone https://github.com/omega0826-code/database.git

[이미 clone한 경우]
    git pull
```

### 5.3 실전 예시

```bash
# 1. 작업 시작 전 - 최신 상태로 업데이트
git pull

# 2. 파일 작업 (편집기에서 파일 수정)
# ... 파일 수정 작업 ...

# 3. 변경 상태 확인
git status

# 4. 모든 변경 파일을 스테이징에 추가
git add .

# 5. 커밋
git commit -m "데이터 파일 업데이트 및 분석 스크립트 추가"

# 6. GitHub에 업로드
git push
```

---

## 6. 자주 발생하는 오류와 해결 방법

### 6.1 Push 관련 오류

#### ❌ "No configured push destination"
```
fatal: No configured push destination.
```
**원인**: 원격 저장소가 설정되지 않음  
**해결**:
```bash
git remote add origin https://github.com/omega0826-code/database.git
git push -u origin master
```

---

#### ❌ "The current branch has no upstream branch"
```
fatal: The current branch master has no upstream branch.
```
**원인**: 현재 브랜치와 원격 브랜치의 연결(upstream)이 설정되지 않음  
**해결**:
```bash
git push --set-upstream origin master
```

---

#### ❌ "remote origin already exists"
```
error: remote origin already exists.
```
**원인**: 이미 `origin`이라는 이름의 원격 저장소가 등록됨  
**해결**:
```bash
# URL만 변경할 경우
git remote set-url origin https://github.com/새URL.git

# 삭제 후 다시 추가할 경우
git remote remove origin
git remote add origin https://github.com/새URL.git
```

---

#### ❌ "rejected - non-fast-forward"
```
! [rejected]  master -> master (non-fast-forward)
```
**원인**: 원격 저장소에 로컬에 없는 커밋이 있음 (다른 곳에서 push된 변경 사항)  
**해결**:
```bash
# 먼저 pull로 원격 변경 사항을 가져온 후 push
git pull
git push
```

---

### 6.2 Pull 관련 오류

#### ❌ "Your local changes would be overwritten by merge"
```
error: Your local changes to the following files would be overwritten by merge
```
**원인**: 로컬에 커밋하지 않은 변경 사항이 있는 상태에서 pull 시도  
**해결**:
```bash
# 방법 1: 변경 사항을 커밋한 후 pull
git add .
git commit -m "로컬 작업 저장"
git pull

# 방법 2: 변경 사항을 임시 저장한 후 pull
git stash          # 변경 사항 임시 저장
git pull           # pull 실행
git stash pop      # 임시 저장한 변경 사항 복원
```

---

#### ❌ Merge 충돌 (Conflict)
```
CONFLICT (content): Merge conflict in 파일명.txt
```
**원인**: 같은 파일의 같은 부분이 로컬과 원격에서 각각 다르게 수정됨  
**해결**:
```bash
# 1. 충돌 파일을 열어서 수동으로 수정
#    <<<<<<< HEAD
#    로컬 변경 내용
#    =======
#    원격 변경 내용
#    >>>>>>> origin/master

# 2. 충돌 표시(<<<, ===, >>>)를 삭제하고 원하는 내용으로 수정

# 3. 수정 완료 후 커밋
git add 파일명.txt
git commit -m "Merge 충돌 해결"
git push
```

---

## 7. 유용한 Git 명령어 모음

### 7.1 상태 확인 명령어

| 명령어 | 설명 |
|--------|------|
| `git status` | 현재 변경 상태 확인 |
| `git log` | 커밋 이력 보기 |
| `git log --oneline -10` | 최근 10개 커밋을 한 줄씩 보기 |
| `git diff` | 변경 내용 상세 보기 |
| `git remote -v` | 원격 저장소 URL 확인 |
| `git branch` | 현재 브랜치 확인 |

### 7.2 파일 관리 명령어

| 명령어 | 설명 |
|--------|------|
| `git add .` | 모든 변경 파일 스테이징 |
| `git add 파일명` | 특정 파일만 스테이징 |
| `git reset HEAD 파일명` | 스테이징 취소 |
| `git checkout -- 파일명` | 파일 변경 사항 되돌리기 (⚠️ 주의) |

### 7.3 커밋 관련 명령어

| 명령어 | 설명 |
|--------|------|
| `git commit -m "메시지"` | 커밋 |
| `git commit -am "메시지"` | add + commit 동시 실행 (수정된 파일만) |
| `git commit --amend` | 마지막 커밋 메시지 수정 |

### 7.4 .gitignore 파일

`.gitignore` 파일에 등록된 파일/폴더는 Git 추적에서 제외됩니다.

```gitignore
# .gitignore 예시

# 특정 파일 제외
secret.txt
passwords.csv

# 특정 확장자 제외
*.log
*.tmp

# 특정 폴더 제외
data/raw/
node_modules/

# 특정 패턴 제외
*.bak
~$*
```

---

## 8. 용어 정리

| 용어 | 영문 | 설명 |
|------|------|------|
| 저장소 | Repository | Git이 관리하는 프로젝트 폴더 |
| 커밋 | Commit | 변경 사항을 로컬 저장소에 기록하는 것 |
| 푸시 | Push | 로컬 커밋을 원격 저장소에 업로드하는 것 |
| 풀 | Pull | 원격 저장소의 변경 사항을 가져와 병합하는 것 |
| 클론 | Clone | 원격 저장소를 통째로 복제하는 것 |
| 페치 | Fetch | 원격 변경 사항을 다운로드만 하는 것 (병합 안 함) |
| 브랜치 | Branch | 독립적인 작업 공간 (코드 분기) |
| 머지 | Merge | 브랜치를 합치는 것 |
| 스테이징 | Staging | 커밋할 파일을 준비하는 과정 |
| 업스트림 | Upstream | 로컬 브랜치와 연결된 원격 브랜치 |
| 오리진 | Origin | 원격 저장소의 기본 이름 |
| 충돌 | Conflict | 같은 부분이 서로 다르게 수정되어 자동 병합 불가 |
| 스태시 | Stash | 변경 사항을 임시로 저장해두는 기능 |

---

> 💡 **팁**: 작업할 때 항상 `git pull` → 작업 → `git add .` → `git commit -m "메시지"` → `git push` 순서를 기억하세요!
