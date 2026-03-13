# SPSS 공통 매크로 레퍼런스

> **Version**: 1.0.0 | **매크로 수**: 43개 | **최종 수정**: 2026-02-26

---

## A. 빈도분석 (Frequency) — 7개

| 매크로       | 파라미터                | 통계량            | 제목 |
| ------------ | ----------------------- | ----------------- | ---- |
| `freg`       | `x`                     | COUNT             | ✕    |
| `freq`       | `x`                     | COUNT, CPCT       | ✕    |
| `freqt`      | `x`, `a`(제목)          | COUNT, CPCT       | ✔    |
| `freqm2t`    | `x`, `y`(평균변수), `a` | COUNT, MEAN, CPCT | ✔    |
| `freq2`      | `x`                     | COUNT             | ✕    |
| `freq2t`     | `x`, `a`                | COUNT             | ✔    |
| `m1t` (초기) | `x`(다변수), `a`        | MEAN(f8.1)        | ✔    |

### 사용 예시

```sps
* 단순 빈도
freq x=b1.

* 빈도 + 제목
freqt a='B1. 공동활용 연구장비를 활용하십니까?' / x=b1.

* 빈도 + 평균 + 제목
freqm2t a='C1-1. 연구장비 정보시스템에 대한 만족도' / x=c1a_1 y=c1a_1r.
```

---

## B. 평균분석 (Mean) — 10개

| 매크로 | 파라미터    | 통계량      | 소수점 | 제목 |
| ------ | ----------- | ----------- | ------ | ---- |
| `m1`   | `x`(다변수) | MEAN        | 1자리  | ✕    |
| `m1t`  | `x`, `a`    | MEAN        | 1자리  | ✔    |
| `m1pt` | `x`, `a`    | MEAN(100점) | 1자리  | ✔    |
| `m2`   | `x`         | MEAN        | 2자리  | ✕    |
| `m2t`  | `x`, `a`    | MEAN        | 2자리  | ✔    |
| `ms1`  | `x`         | MEAN, SUM   | 1자리  | ✕    |
| `ms1t` | `x`, `a`    | MEAN, SUM   | 1자리  | ✔    |
| `ms2r` | `x`         | MEAN, SUM   | 2자리  | ✕    |
| `ms2t` | `x`, `a`    | MEAN, SUM   | 2자리  | ✔    |

### 사용 예시

```sps
* 평균 (1자리)
m1t a='현황' / x=a6 a7.

* 평균 + 합계 (2자리, 제목)
ms2t a='예산 현황' / x=a6 a7.
```

---

## C. 복합분석 (Count + Mean/Sum) — 18개

| 매크로  | 파라미터 | 통계량                 | 제목 |
| ------- | -------- | ---------------------- | ---- |
| `co`    | `x`      | VALIDN                 | ✕    |
| `cot`   | `x`, `a` | VALIDN                 | ✔    |
| `sot`   | `x`, `a` | SUM                    | ✔    |
| `cst`   | `x`, `a` | VALIDN, SUM            | ✔    |
| `cm1`   | `x`      | VALIDN, MEAN(1)        | ✕    |
| `cm1t`  | `x`, `a` | VALIDN, MEAN(1)        | ✔    |
| `cm2`   | `x`      | VALIDN, MEAN(2)        | ✕    |
| `cm2t`  | `x`, `a` | VALIDN, MEAN(2)        | ✔    |
| `csm1t` | `x`, `a` | VALIDN, SUM, MEAN(1)   | ✔    |
| `cms1`  | `x`      | VALIDN, MEAN(1), SUM   | ✕    |
| `cms1t` | `x`, `a` | VALIDN, MEAN(1), SUM   | ✔    |
| `cms2`  | `x`      | VALIDN, MEAN(2), SUM   | ✕    |
| `cms2t` | `x`, `a` | VALIDN, MEAN(2), SUM   | ✔    |
| `cms2r` | `x`      | VALIDN, MEAN(2), SUM   | ✕    |
| `cms3`  | `x`      | CPCT, MEAN, SUM        | ✕    |
| `cs`    | `x`      | VALIDN, SUM            | ✕    |
| `sm1t`  | `x`, `a` | SUM, MEAN(1)           | ✔    |
| `sm2t`  | `x`, `a` | SUM, MEAN(2)           | ✔    |
| `cmmmt` | `x`, `a` | VALIDN, MEAN, MIN, MAX | ✔    |

### 사용 예시

```sps
* 업체수 + 평균(1자리) + 합계 + 제목
cms1t a='현황' / x=a6 a7.

* 업체수 + 평균 + 최소 + 최대
cmmmt a='장비 현황' / x=a6 a7.
```

---

## D. 복수응답 (Multiple Response) — 8개

| 매크로 | 파라미터                       | 통계량             | 제목 |
| ------ | ------------------------------ | ------------------ | ---- |
| `PR`   | `x`, `y`, `z`(그룹), `a`(라벨) | COUNT, CPCT        | ✕    |
| `PRT`  | `x`, `y`, `z`, `a`, `b`(제목)  | COUNT, CPCT        | ✔    |
| `PR2`  | `x`, `y`, `z`, `a`             | COUNT              | ✕    |
| `PR2T` | `x`, `y`, `z`, `a`, `b`        | COUNT              | ✔    |
| `PRG`  | `x`, `y`, `z`, `a`             | COUNT, CPCT (그룹) | ✕    |
| `PR3T` | `x`, `y`, `z`, `a`, `b`        | COUNT, CPCT        | ✔    |
| `PR4`  | `x`, `y`, `z`, `a`             | COUNT              | ✕    |
| `PR4T` | `x`, `y`, `z`, `a`, `b`        | COUNT              | ✔    |

### 사용 예시

```sps
* 복수응답 빈도·비율 + 제목
PRT b='B1-3. 연구장비를 이용하시는 목적은?' / x=B1a_3_1 y=B1a_3_2 z=aa a='연구장비 이용 목적(1순위+2순위)'.

* 복수응답 빈도만
PR2 x=D1_1 y=D1_6 z=aa a='연구장비 활용 애로사항(중복)'.
```

---

## 파라미터 규칙

| 파라미터 | 타입                               | 설명                              |
| -------- | ---------------------------------- | --------------------------------- |
| `x`      | `!TOKENS(1)` 또는 `!CMD`/`!CMDEND` | 분석 변수 (단일 또는 다변수)      |
| `y`      | `!TOKENS(1)`                       | 보조 변수 (평균용 역코딩 변수 등) |
| `z`      | `!TOKENS(1)`                       | 복수응답 그룹 변수명              |
| `a`      | `!CHAREND('/')`                    | 복수응답 라벨 또는 제목           |
| `b`      | `!CHAREND('/')`                    | 테이블 제목 (`/title=`)           |

### 매크로 이름 규칙

- `t` 접미사 = 제목(`title`) 포함 (예: `freq` → `freqt`)
- `숫자` = 소수점 자릿수 (예: `m1` = 1자리, `m2` = 2자리)
- `r` 접미사 = comma 형식 (예: `ms2r`)
- `PR` = 복수응답(Plural Response)
