# SPSS 공통 매크로 변경 이력

## [1.0.0] - 2026-02-26

### 추가
- 초기 매크로 43개 등록
  - 빈도분석: 7개 (`freg`, `freq`, `freqt`, `freqm2t`, `freq2`, `freq2t`, `m1t`)
  - 평균분석: 10개 (`m1`, `m1t`, `m1pt`, `m2`, `m2t`, `ms1`, `ms1t`, `ms2r`, `ms2t` 등)
  - 복합분석: 18개 (`co`, `cot`, `sot`, `cst`, `cm1`, `cm1t`, `cm2`, `cms1`, `cmmmt` 등)
  - 복수응답: 8개 (`PR`, `PRT`, `PR2`, `PR2T`, `PRG`, `PR3T`, `PR4`, `PR4T`)
- `common_macros.sps` (방식A: 복사 붙여넣기용) 생성
- `common_macros_template.sps` (방식B: 자동 생성 템플릿) 생성
- `generate_macros.py` (자동 생성 스크립트) 생성
