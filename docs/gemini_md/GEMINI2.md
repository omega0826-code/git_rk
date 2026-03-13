# Global Rules — File Naming Convention

## 1. 기본 원칙

- 모든 파일명과 폴더명은 **snake_case**를 사용한다.
- 영문 소문자, 숫자, 언더스코어(`_`)만 허용한다.
- 파일명은 **해당 파일의 역할이나 내용을 즉시 파악**할 수 있도록 명확하게 짓는다.
- 약어는 팀 내 합의된 것만 사용하고, 그 외에는 풀네임을 쓴다.

## 2. 파일명 패턴

### 2.1 일반 소스 파일

```
<도메인>_<역할>.<확장자>

예시:
  user_service.py
  order_repository.java
  payment_controller.ts
  product_model.go
```

### 2.2 테스트 파일

```
test_<대상 파일명>.<확장자>   (단위 테스트)
e2e_<시나리오명>.<확장자>     (E2E 테스트)

예시:
  test_user_service.py
  test_order_repository.java
  e2e_checkout_flow.ts
```

### 2.3 설정·환경 파일

```
config_<환경 또는 대상>.<확장자>

예시:
  config_database.yaml
  config_production.env
  config_logging.json
```

### 2.4 유틸·헬퍼

```
util_<기능명>.<확장자>
helper_<기능명>.<확장자>

예시:
  util_date_format.py
  helper_string_sanitize.ts
```

### 2.5 타입·인터페이스·DTO

```
type_<도메인>.<확장자>
dto_<도메인>_<방향>.<확장자>

예시:
  type_user.ts
  dto_order_request.py
  dto_order_response.py
```

### 2.6 마이그레이션·스크립트

```
<YYYYMMDD>_<순번>_<설명>.<확장자>

예시:
  20260307_001_create_users_table.sql
  20260307_002_add_email_index.sql
```

### 2.7 문서·마크다운

```
<주제>.<확장자>

예시:
  architecture_overview.md
  api_design_guide.md
  deployment_runbook.md
```

## 3. 폴더명 패턴

- 폴더명도 snake_case를 따른다.
- 복수형을 기본으로 한다(단, 단일 목적 폴더는 단수 허용).
- 깊이는 최대 4단계까지로 제한한다.

```
예시:
  src/
  tests/
  configs/
  migrations/
  docs/
  scripts/
  utils/
```

## 4. 금지 패턴

아래 패턴은 절대 사용하지 않는다:

| 금지 항목 | 이유 | 위반 예시 |
|-----------|------|-----------|
| 한글·한자·일본어 등 비ASCII 문자 | OS 간 호환성, 인코딩 문제 | `사용자_서비스.py` |
| 공백(스페이스) | 셸 명령어 오류, 이스케이프 필요 | `user service.py` |
| 하이픈(`-`) | snake_case 통일 정책 | `user-service.py` |
| 대문자 | 대소문자 구분 없는 OS에서 충돌 | `UserService.py` |
| 특수문자(`!@#$%^&*()+=[]{}`) | 경로 파싱 오류, 보안 이슈 | `user@service.py` |
| 마침표(`.`) 확장자 외 사용 | 숨김 파일 오인, 파싱 혼란 | `user.service.v2.py` |
| 연속 언더스코어(`__`) | 가독성 저하, 언어별 예약 패턴 충돌 | `user__service.py` |
| 숫자로 시작 | 일부 언어에서 식별자 불가 | `2nd_migration.sql` |
| 의미 없는 이름 | 유지보수 불가 | `temp.py`, `a.js`, `test2.py` |

## 5. 디렉토리 구조 가이드

```
project_root/
├── src/                        # 소스 코드 루트
│   ├── modules/                # 도메인별 모듈
│   │   ├── users/
│   │   │   ├── user_service.py
│   │   │   ├── user_repository.py
│   │   │   ├── user_controller.py
│   │   │   └── type_user.py
│   │   └── orders/
│   │       ├── order_service.py
│   │       ├── order_repository.py
│   │       └── dto_order_request.py
│   ├── shared/                 # 공유 코드
│   │   ├── utils/
│   │   ├── constants/
│   │   └── middleware/
│   └── main.py                 # 엔트리포인트
├── tests/                      # 테스트 (src 구조 미러링)
│   ├── modules/
│   │   ├── users/
│   │   │   └── test_user_service.py
│   │   └── orders/
│   │       └── test_order_service.py
│   └── e2e/
│       └── e2e_checkout_flow.py
├── configs/                    # 설정 파일
│   ├── config_database.yaml
│   └── config_production.env
├── migrations/                 # DB 마이그레이션
│   └── 20260307_001_create_users_table.sql
├── scripts/                    # 빌드·배포·유틸 스크립트
│   └── setup_dev_environment.sh
├── docs/                       # 문서
│   └── architecture_overview.md
└── README.md
```

## 6. 적용 규칙 요약

- 새 파일 생성 시 반드시 위 패턴을 따를 것.
- 기존 파일이 규칙에 어긋나면 리팩토링 시점에 일괄 변경할 것.
- 에이전트가 코드를 생성할 때 이 규칙을 자동으로 적용할 것.
- 규칙에 없는 특수한 케이스는 가장 유사한 패턴을 따르되, 코드 리뷰에서 합의할 것.
