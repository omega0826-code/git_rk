# 샘플 설문조사 분석 Syntax

> **원본 파일**: `sample_analysis.sps`
> **원본 인코딩**: `cp949`
> **줄바꿈**: `CRLF`
> **변환 시각**: 2026-04-15 20:40:00

```sps
* Encoding: EUC-KR.
* ===============================================================.
* 샘플 설문조사 통계분석.
* Version: 1.0.0.
* Created: 2026-04-15.
* Banner: SQ1 + SQ2 + SQ3.
* ===============================================================.



***** 1. 라벨 적용(간략) *****


* -- VARIABLE LABELS -----------------------------------------------.

VARIABLE LABELS
   SQ1  '성별'
   SQ2  '학년'
   SQ3  '소속 대학'
   A1  'RISE사업 인지 여부'
   A2_1  'RISE사업 만족 이유'
   A2_2  'RISE사업 불만족 이유'
   A2_3  '서비스 비용에 대해 만족하십니까?'
   B1_1  '이용 채널: 온라인 웹사이트'
   B1_2  '이용 채널: 모바일 앱'
   B1_3  '이용 채널: 전화'
   B1_4  '이용 채널: 방문'
   B1_5  '이용 채널: SNS'
   C1  '종합 만족도는 어떻습니까?'.
EXECUTE.

* -- VALUE LABELS -------------------------------------------------.

VALUE LABELS
.
EXECUTE.



***** 2. 변수 생성(리코딩) *****


RECODE SQ2 (1=1) (2=1) (3=2) (4=2) (5=3)(ELSE=SYSMIS) INTO
  SQ2R.
VARIABLE LABELS
  SQ2R  '연령대(통합)'.
EXECUTE.




***** 3. 공통 매크로 정의 *****


****배너: SQ1 + SQ2 + SQ3


DEFINE freg (x=!TOKENS(1))
CTABLES
  /VLABELS VARIABLES=!x DISPLAY=LABEL
  /TABLE BY !x [C][COUNT F40.0]
  /CATEGORIES VARIABLES=!x ORDER=A KEY=VALUE EMPTY=INCLUDE.
!ENDDEFINE.


DEFINE freq (x=!TOKENS(1))
    TABLES
    /PTOTAL=t1'전 체' t2'구 분'
    /TABLE=t1+SQ1+SQ2+SQ3 BY t2+!x
    /STATISTICS=COUNT(t2'' !x'빈도') CPCT(!x'비율' : SQ1 SQ2 SQ3 )
!ENDDEFINE.


DEFINE freqt (x=!CMDEND / a=!CHAREND("/"))
    TABLES
    /PTOTAL=t1'전 체' t2'구 분'
    /TABLE=t1+SQ1+SQ2+SQ3 BY t2+!x
    /STATISTICS=COUNT(t2'' !x'빈도') CPCT(!x'비율' : SQ1 SQ2 SQ3 )
    /title=!a.
!ENDDEFINE.


DEFINE freqm2t (x=!TOKENS(1) / y=!TOKENS(1) / a=!CHAREND('/'))
    TABLES OBS = !y
    /PTOTAL=t1'전 체' t2'구 분'
    /TABLE=t1+SQ1+SQ2+SQ3 BY t2+ !y + !x
    /STATISTICS=COUNT(t2'' !x'빈도') mean( !y (f8.2)) CPCT(!x'비율' : SQ1 SQ2 SQ3 )
    /title=!a.
!ENDDEFINE.


DEFINE m1t (x=!CMDEND / a=!CHAREND("/"))
    !LET !H=!HEAD(!x)
    !LET !T=!TAIL(!x)
    TABLES OBS=!x
    /PTOTAL=t1'전 체'
    /TABLE=t1+SQ1+SQ2+SQ3 BY !H !DO !var !IN (!T) !CONCAT('+',!var) !DOEND
    /STATISTICS=MEAN(!H !DO !var !IN (!T) !CONCAT('(f8.1)',!var) !DOEND (f8.1))
    /title=!a.
!ENDDEFINE.


DEFINE freq2 (x=!TOKENS(1))
    TABLES
    /PTOTAL=t1'전 체' t2'구 분'
    /TABLE=t1+SQ1+SQ2+SQ3 BY t2+!x
    /STATISTICS=COUNT(t2'' !x'빈도').
!ENDDEFINE.


DEFINE freq2t (x=!TOKENS(1) / a=!CHAREND('/'))
    TABLES
    /PTOTAL=t1'전 체' t2'구 분'
    /TABLE=t1+SQ1+SQ2+SQ3 BY t2+!x
    /STATISTICS=COUNT(t2'' !x'빈도')
    /title=!a.
!ENDDEFINE.


DEFINE PR (x=!TOKENS(1) / y=!TOKENS(1) / z=!TOKENS(1) / a=!CHAREND('/'))
    TABLES
    /PTOTAL=t1'전 체' t2'구 분'
    /MRGROUP=!z !a !x TO !y
    /TABLE=t1+SQ1+SQ2+SQ3 BY t2+!z
    /STATISTICS=COUNT(t2'' !z'빈도') CPCT(!z'비율': SQ1 SQ2 SQ3).
!ENDDEFINE.


DEFINE PRT (x=!TOKENS(1) / y=!TOKENS(1) / z=!TOKENS(1) / a=!CHAREND('/')  / b=!CHAREND('/'))
    TABLES
    /PTOTAL=t1'전 체' t2'구 분'
    /MRGROUP=!z !a !x TO !y
    /TABLE=t1+SQ1+SQ2+SQ3 BY t2+!z
    /STATISTICS=COUNT(t2''  !z'빈도') CPCT(!z'비율': SQ1 SQ2 SQ3)
    /title=!b.
!ENDDEFINE.


DEFINE co (x=!CMD)
    !LET !H=!HEAD(!x)
    !LET !T=!TAIL(!x)
    TABLES OBS=!x
    /PTOTAL=t1'전 체'
    /TABLE=t1+SQ1+SQ2+SQ3 BY !H !DO !var !IN (!T) !CONCAT('+',!var) !DOEND
    /STATISTICS=VALIDN('응답수')
!ENDDEFINE.


DEFINE cot (x=!CMDEND / a=!CHAREND("/"))
    !LET !H=!HEAD(!x)
    !LET !T=!TAIL(!x)
    TABLES OBS=!x
    /PTOTAL=t1'전 체'
    /TABLE=t1+SQ1+SQ2+SQ3 BY !H !DO !var !IN (!T) !CONCAT('+',!var) !DOEND
    /STATISTICS=VALIDN('응답수')
    /title=!a.
!ENDDEFINE.


DEFINE cm1t (x=!CMDEND / a=!CHAREND("/"))
    !LET !H=!HEAD(!x)
    !LET !T=!TAIL(!x)
    TABLES OBS=!x
    /PTOTAL=t1'전 체'
    /TABLE=t1+SQ1+SQ2+SQ3 BY !H !DO !var !IN (!T) !CONCAT('+',!var) !DOEND
    /STATISTICS=VALIDN('응답수') MEAN(!H !DO !var !IN (!T) !CONCAT('(f8.1)',!var) !DOEND (f8.1))
    /title=!a.
!ENDDEFINE.



***** 4. 응답자 특성 *****


*성별.
freqt a='성별' / x=SQ1.

*연령대.
freqt a='연령대' / x=SQ2.

*거주지역.
freqt a='거주지역' / x=SQ3.




***** 5. 인지 및 이용 현황 *****


*서비스 인지 여부.
freqt a='RISE사업 인지 여부' / x=A1.

freqt a='RISE사업 만족 이유' / x=A2_1.
freqt a='RISE사업 불만족 이유' / x=A2_2.
freqt a='서비스 비용에 대해 만족하십니까?' / x=A2_3.
freqt a='A2_4' / x=A2_4.
freqt a='A2_5' / x=A2_5.




***** 6. 만족도 분석 *****


*부문별 만족도.
cm1t a='부문별 만족도' /
 x=B1_1 B1_2 B1_3 B1_4 B1_5.

*세부 항목 만족도.
cm1t a='세부 항목 만족도' /
 x=B2_1 B2_2 B2_3 B2_4 B2_5 B2_6 B2_7 B2_8.

*종합 만족도(척도).
freqm2t a='종합 만족도' / x=B3 y=B3S.




***** 7. 복수응답 분석 *****


*이용 채널(복수응답).
PRT b='이용 채널(복수응답)' / x=C1_1 y=C1_7 z=mg_c1 a='이용 채널'.

*불편 요인(복수응답).
PRT b='불편 요인(복수응답)' / x=C2_1 y=C2_5 z=mg_c2 a='불편 요인'.




***** 8. 변수 리코딩 *****





***** 9. 필터 적용 예시 *****


*서비스 개선 의향 - 남성 한정.
TEMPORARY.
SELECT IF(SQ1=1).
freqt a='서비스 개선 의향(남성)' / x=D1.

```
