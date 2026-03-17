* ═══════════════════════════════════════════════════════════════
* SPSS 공통 매크로 템플릿 (자동 생성용)
* Version: 1.0.0
* Updated: 2026-02-26
* ═══════════════════════════════════════════════════════════════
*
* 이 파일은 generate_macros.py에서 사용하는 템플릿입니다.
* 직접 수정하지 말고 generate_macros.py를 통해 사용하세요.
*
* 플레이스홀더:
*   {{BANNER}}        - TABLE 행 변수 (t1 포함)
*   {{BANNER_LIST}}   - 통계량 적용 변수 (공백 구분)
*   {{BANNER_NO_T1}}  - 행 변수 (t1 제외, + 구분)
*   {{PTOTAL1}}       - 전체 라벨
*   {{PTOTAL2}}       - 구분 라벨
*   {{VALIDN_LABEL}}  - 업체수/응답수 라벨
* ═══════════════════════════════════════════════════════════════

****************************공통 메크로





*그래프(빈도)





DEFINE freg (x=!TOKENS(1))
CTABLES 
  /VLABELS VARIABLES=!x DISPLAY=LABEL 
  /TABLE BY !x [C][COUNT F40.0] 
  /CATEGORIES VARIABLES=!x ORDER=A KEY=VALUE EMPTY=INCLUDE.
!ENDDEFINE.















*객관식(빈도, 비율)





DEFINE freq (x=!TOKENS(1))
    TABLES
    /PTOTAL=t1'{{PTOTAL1}}' t2'{{PTOTAL2}}'
    /TABLE={{BANNER}} BY t2+!x
    /STATISTICS=COUNT(t2'' !x'빈도') CPCT(!x'비율' : {{BANNER_LIST}} )
!ENDDEFINE.















DEFINE freqt (x=!CMDEND / a=!CHAREND("/"))
    TABLES
    /PTOTAL=t1'{{PTOTAL1}}' t2'{{PTOTAL2}}'
    /TABLE={{BANNER}} BY t2+!x
    /STATISTICS=COUNT(t2'' !x'빈도') CPCT(!x'비율' : {{BANNER_LIST}} )
    /title=!a.
!ENDDEFINE.











DEFINE freqm2t (x=!TOKENS(1) / y=!TOKENS(1) / a=!CHAREND('/'))
    TABLES OBS = !y
    /PTOTAL=t1'{{PTOTAL1}}' t2'{{PTOTAL2}}'
    /TABLE={{BANNER}} BY t2+ !y + !x
    /STATISTICS=COUNT(t2'' !x'빈도') mean( !y (f8.2)) CPCT(!x'비율' : {{BANNER_LIST}} )
    /title=!a.
!ENDDEFINE.











DEFINE m1t (x=!CMDEND / a=!CHAREND("/"))
    !LET !H=!HEAD(!x)
    !LET !T=!TAIL(!x)
    TABLES OBS=!x
    /PTOTAL=t1'{{PTOTAL1}}'
    /TABLE={{BANNER}} BY !H !DO !var !IN (!T) !CONCAT('+',!var) !DOEND
    /STATISTICS=MEAN(!H !DO !var !IN (!T) !CONCAT('(f8.1)',!var) !DOEND (f8.1))
    /title=!a.
!ENDDEFINE.















*객관식(빈도 제외)



DEFINE freq2 (x=!TOKENS(1))
    TABLES
    /PTOTAL=t1'{{PTOTAL1}}' t2'{{PTOTAL2}}'
    /TABLE={{BANNER}} BY t2+!x
    /STATISTICS=COUNT(t2'' ) CPCT(!x'' (Pct8.1) : {{BANNER_LIST}}).
!ENDDEFINE.









DEFINE freq2t (x=!TOKENS(1) / a=!CHAREND('/'))
    TABLES
    /PTOTAL=t1'{{PTOTAL1}}' t2'{{PTOTAL2}}'
    /TABLE={{BANNER}} BY t2+!x
    /STATISTICS=COUNT(t2'') CPCT(!x'%' (Pct8.1) : {{BANNER_LIST}} )
    /title=!a.
!ENDDEFINE.







*중복응답



DEFINE PR (x=!TOKENS(1) / y=!TOKENS(1) / z=!TOKENS(1) / a=!CHAREND('/'))
    TABLES
    /PTOTAL=t1'{{PTOTAL1}}' t2'{{PTOTAL2}}'
    /MRGROUP=!z !a !x TO !y
    /TABLE={{BANNER}} BY t2+!z
    /STATISTICS=COUNT(t2'' !z'빈도') CPCT(!z'비율': {{BANNER_LIST}}).
!ENDDEFINE.





*prt  b='하자보수 처리 시 불편사항' / x=b5_1 y=b5_5 z=aa a='eeeee'.

DEFINE PRT (x=!TOKENS(1) / y=!TOKENS(1) / z=!TOKENS(1) / a=!CHAREND('/')  / b=!CHAREND('/'))
    TABLES
    /PTOTAL=t1'{{PTOTAL1}}' t2'{{PTOTAL2}}'
    /MRGROUP=!z !a !x TO !y
    /TABLE={{BANNER}} BY t2+!z
    /STATISTICS=COUNT(t2''  !z'빈도') CPCT(!z'비율': {{BANNER_LIST}})
    /title=!b.
!ENDDEFINE.















DEFINE PR2 (x=!TOKENS(1) / y=!TOKENS(1) / z=!TOKENS(1) / a=!CHAREND('/'))
    TABLES
    /PTOTAL=t1'{{PTOTAL1}}' t2'{{PTOTAL2}}'
    /MRGROUP=!z !a !x TO !y
    /TABLE={{BANNER}} BY t2+!z
    /STATISTICS=COUNT(t2'' ) CPCT(!z'%' (Pct8.1): {{BANNER_LIST}}).
!ENDDEFINE.









DEFINE PR2T (x=!TOKENS(1) / y=!TOKENS(1) / z=!TOKENS(1) / a=!CHAREND('/')  / b=!CHAREND('/'))
    TABLES
    /PTOTAL=t1'{{PTOTAL1}}' t2'{{PTOTAL2}}'
    /MRGROUP=!z !a !x TO !y
    /TABLE={{BANNER}} BY t2+!z
    /STATISTICS=COUNT(t2'' (comma8.0) ) CPCT(!z'%'(Pct8.1): {{BANNER_LIST}})
    /title=!b.
!ENDDEFINE.













*중복응답(빈도 제외) 그래프



DEFINE PRG (x=!TOKENS(1) / y=!TOKENS(1) / z=!TOKENS(1) / a=!CHAREND('/'))
    TABLES
    /PTOTAL=t1'{{PTOTAL1}}' t2'{{PTOTAL2}}'
    /MRGROUP=!z !a !x TO !y
    /TABLE={{BANNER}} BY t2+!z
    /STATISTICS=COUNT(t2'' ) CPCT(!z'비율': {{BANNER_LIST}})
    /corner ='그래프(비율)' .
    TABLES
    /PTOTAL=t1'{{PTOTAL1}}' t2'{{PTOTAL2}}'
    /MRGROUP=!z !a !x TO !y
    /TABLE={{BANNER}} BY t2+!z
    /STATISTICS=COUNT(t2'' !z'빈도')
    /corner ='그래프(빈도)' .
!ENDDEFINE.









*우선순위(100%)



DEFINE PR3T (x=!TOKENS(1) / y=!TOKENS(1) / z=!TOKENS(1) / a=!CHAREND('/')  / b=!CHAREND('/'))
    TABLES
    /PTOTAL=t1'{{PTOTAL1}}' t2'{{PTOTAL2}}'
    /MRGROUP=!z !a !x TO !y
    /GBASE=RESPONSE
    /TABLE={{BANNER}} BY t2+!z
    /STATISTICS=COUNT(t2'' !z'빈도') CPCT(!z'비율': {{BANNER_LIST}})
    /title=!b.
!ENDDEFINE.





*우선순위(빈도 제외) 그래프(100%)



DEFINE PR4 (x=!TOKENS(1) / y=!TOKENS(1) / z=!TOKENS(1) / a=!CHAREND('/'))
    TABLES
    /PTOTAL=t1'{{PTOTAL1}}' t2'{{PTOTAL2}}'
    /MRGROUP=!z !a !x TO !y
    /GBASE=RESPONSE
    /TABLE={{BANNER}} BY t2+!z
    /STATISTICS=COUNT(t2'' ) CPCT(!z'비율': {{BANNER_LIST}}).
!ENDDEFINE.





DEFINE PR4T (x=!TOKENS(1) / y=!TOKENS(1) / z=!TOKENS(1) / a=!CHAREND('/')  / b=!CHAREND('/'))
    TABLES
    /PTOTAL=t1'{{PTOTAL1}}' t2'{{PTOTAL2}}'
    /MRGROUP=!z !a !x TO !y
    /GBASE=RESPONSE
    /TABLE={{BANNER}} BY t2+!z
    /STATISTICS=COUNT(t2''(comma8.1) ) CPCT(!z'%': {{BANNER_LIST}})
    /title=!b.
!ENDDEFINE.



















*평균









DEFINE m1 (x=!CMD)
    !LET !H=!HEAD(!x)
    !LET !T=!TAIL(!x)
    TABLES OBS=!x
    /PTOTAL=t1'{{PTOTAL1}}'
    /TABLE={{BANNER}} BY !H !DO !var !IN (!T) !CONCAT('+',!var) !DOEND
    /STATISTICS=MEAN('(100점)' (f8.1)).
!ENDDEFINE.









DEFINE m1t (x=!CMDEND / a=!CHAREND("/"))
    !LET !H=!HEAD(!x)
    !LET !T=!TAIL(!x)
    TABLES OBS=!x
    /PTOTAL=t1'{{PTOTAL1}}'
    /TABLE={{BANNER}} BY !H !DO !var !IN (!T) !CONCAT('+',!var) !DOEND
    /STATISTICS=MEAN(!H !DO !var !IN (!T) !CONCAT('(f8.1)',!var) !DOEND (f8.1))
    /title=!a.
!ENDDEFINE.









*참고 : PCT는 표시형식만 %추가 *100 필요



DEFINE m1pt (x=!CMDEND / a=!CHAREND("/"))
    !LET !H=!HEAD(!x)
    !LET !T=!TAIL(!x)
    TABLES OBS=!x
    /PTOTAL=t1'{{PTOTAL1}}'
    /TABLE={{BANNER}} BY !H !DO !var !IN (!T) !CONCAT('+',!var) !DOEND
    /STATISTICS=MEAN(!H !DO !var !IN (!T) !CONCAT('(PCT8.1)',!var) !DOEND (PCT8.1))
    /title=!a.
!ENDDEFINE.



















DEFINE m2 (x=!CMD)
    !LET !H=!HEAD(!x)
    !LET !T=!TAIL(!x)
    TABLES OBS=!x
    /PTOTAL=t1'{{PTOTAL1}}'
    /TABLE={{BANNER}} BY !H !DO !var !IN (!T) !CONCAT('+',!var) !DOEND
    /STATISTICS=MEAN((f8.2)).
!ENDDEFINE.







*예제 m2t  a = '부대별 차원 만족도' / x = TT a2h a4h a6h a8h.

DEFINE m2t (x=!CMDEND / a=!CHAREND("/"))
    !LET !H=!HEAD(!x)
    !LET !T=!TAIL(!x)
    TABLES OBS=!x
    /PTOTAL=t1'{{PTOTAL1}}'
    /TABLE={{BANNER}} BY !H !DO !var !IN (!T) !CONCAT('+',!var) !DOEND
    /STATISTICS=MEAN(!H !DO !var !IN (!T) !CONCAT('(f8.2)',!var) !DOEND (f8.2))
    /title=!a.
!ENDDEFINE.















DEFINE co (x=!CMD)
    !LET !H=!HEAD(!x)
    !LET !T=!TAIL(!x)
    TABLES OBS=!x
    /PTOTAL=t1'{{PTOTAL1}}'
    /TABLE={{BANNER}} BY !H !DO !var !IN (!T) !CONCAT('+',!var) !DOEND
    /STATISTICS=VALIDN('{{VALIDN_LABEL}}')
!ENDDEFINE.

















DEFINE cot (x=!CMDEND / a=!CHAREND("/"))
    !LET !H=!HEAD(!x)
    !LET !T=!TAIL(!x)
    TABLES OBS=!x
    /PTOTAL=t1'{{PTOTAL1}}'
    /TABLE={{BANNER}} BY !H !DO !var !IN (!T) !CONCAT('+',!var) !DOEND
    /STATISTICS=VALIDN('업체수' (comma8.0))
    /title=!a.
!ENDDEFINE.











DEFINE sot (x=!CMDEND / a=!CHAREND("/"))
    !LET !H=!HEAD(!x)
    !LET !T=!TAIL(!x)
    TABLES OBS=!x
    /PTOTAL=t1'{{PTOTAL1}}'
    /TABLE={{BANNER}} BY !H !DO !var !IN (!T) !CONCAT('+',!var) !DOEND
    /STATISTICS=sum((comma8.0))
    /title=!a.
!ENDDEFINE.









DEFINE cst (x=!CMDEND / a=!CHAREND("/"))
    !LET !H=!HEAD(!x)
    !LET !T=!TAIL(!x)
    TABLES OBS=!x
    /PTOTAL=t1'{{PTOTAL1}}'
    /TABLE={{BANNER}} BY !H !DO !var !IN (!T) !CONCAT('+',!var) !DOEND
    /STATISTICS= VALIDN('업체수' (comma8.0))  sum((comma8.0))
    /title=!a.
!ENDDEFINE.







DEFINE cm1 (x=!CMD)
    !LET !H=!HEAD(!x)
    !LET !T=!TAIL(!x)
    TABLES OBS=!x
    /PTOTAL=t1'{{PTOTAL1}}'
    /TABLE={{BANNER}} BY !H !DO !var !IN (!T) !CONCAT('+',!var) !DOEND
    /STATISTICS=VALIDN('{{VALIDN_LABEL}}') MEAN((f8.1)).
!ENDDEFINE.











DEFINE cm1t (x=!CMDEND / a=!CHAREND("/"))
    !LET !H=!HEAD(!x)
    !LET !T=!TAIL(!x)
    TABLES OBS=!x
    /PTOTAL=t1'{{PTOTAL1}}'
    /TABLE={{BANNER}} BY !H !DO !var !IN (!T) !CONCAT('+',!var) !DOEND
    /STATISTICS=VALIDN('{{VALIDN_LABEL}}') MEAN(!H !DO !var !IN (!T) !CONCAT('(f8.1)',!var) !DOEND (f8.1))
    /title=!a.
!ENDDEFINE.









DEFINE cm2 (x=!CMD)
    !LET !H=!HEAD(!x)
    !LET !T=!TAIL(!x)
    TABLES OBS=!x
    /PTOTAL=t1'{{PTOTAL1}}'
    /TABLE={{BANNER}} BY !H !DO !var !IN (!T) !CONCAT('+',!var) !DOEND
    /STATISTICS=VALIDN('{{VALIDN_LABEL}}') MEAN((f8.2)).
!ENDDEFINE.











DEFINE cm2t (x=!CMDEND / a=!CHAREND("/"))
    !LET !H=!HEAD(!x)
    !LET !T=!TAIL(!x)
    TABLES OBS=!x
    /PTOTAL=t1'{{PTOTAL1}}'
    /TABLE={{BANNER}} BY !H !DO !var !IN (!T) !CONCAT('+',!var) !DOEND
    /STATISTICS=VALIDN('{{VALIDN_LABEL}}') MEAN(!H !DO !var !IN (!T) !CONCAT('(f8.2)',!var) !DOEND (f8.2))
    /title=!a.
!ENDDEFINE.













DEFINE csm1t (x=!CMDEND / a=!CHAREND("/"))
    !LET !H=!HEAD(!x)
    !LET !T=!TAIL(!x)
    TABLES OBS=!x
    /PTOTAL=t1'{{PTOTAL1}}'
    /TABLE={{BANNER}} BY !H !DO !var !IN (!T) !CONCAT('+',!var) !DOEND
    /STATISTICS=VALIDN('{{VALIDN_LABEL}}')  SUM(!H !DO !var !IN (!T) !CONCAT('(comma8.0)',!var) !DOEND (comma8.0)) MEAN(!H !DO !var !IN (!T) !CONCAT('(f8.1)',!var) !DOEND (f8.1))
    /title=!a.
!ENDDEFINE.













DEFINE cms2 (x=!CMD)
    !LET !H=!HEAD(!x)
    !LET !T=!TAIL(!x)
    TABLES OBS=!x
    /PTOTAL=t1'{{PTOTAL1}}'
    /TABLE={{BANNER}} BY !H !DO !var !IN (!T) !CONCAT('+',!var) !DOEND
    /STATISTICS=VALIDN('{{VALIDN_LABEL}}') MEAN((f8.2)) SUM((f8.0)).
!ENDDEFINE.







DEFINE cms2t (x=!CMDEND / a=!CHAREND("/"))
    !LET !H=!HEAD(!x)
    !LET !T=!TAIL(!x)
    TABLES OBS=!x
    /PTOTAL=t1'{{PTOTAL1}}'
    /TABLE={{BANNER}} BY !H !DO !var !IN (!T) !CONCAT('+',!var) !DOEND
    /STATISTICS=VALIDN('{{VALIDN_LABEL}}') MEAN(!H !DO !var !IN (!T) !CONCAT('(f8.2)',!var) !DOEND (f8.2)) SUM(!H !DO !var !IN (!T) !CONCAT('(comma8.0)',!var) !DOEND (comma8.0))
    /title=!a.
!ENDDEFINE.















DEFINE cms3 (x=!CMD)
    !LET !H=!HEAD(!x)
    !LET !T=!TAIL(!x)
    TABLES OBS=!x
    /PTOTAL=t1'{{PTOTAL1}}'
    /TABLE={{BANNER}} BY !H !DO !var !IN (!T) !CONCAT('+',!var) !DOEND
    /STATISTICS=VALIDN('{{VALIDN_LABEL}}') MEAN((f8.0)) SUM((f8.0)).
!ENDDEFINE.













DEFINE cms1 (x=!CMD)
    !LET !H=!HEAD(!x)
    !LET !T=!TAIL(!x)
    TABLES OBS=!x
    /PTOTAL=t1'{{PTOTAL1}}'
    /TABLE={{BANNER}} BY !H !DO !var !IN (!T) !CONCAT('+',!var) !DOEND
    /STATISTICS=VALIDN('{{VALIDN_LABEL}}') MEAN((comma8.1)) SUM((comma8.0)).
!ENDDEFINE.







DEFINE cms1t (x=!CMDEND / a=!CHAREND("/"))
    !LET !H=!HEAD(!x)
    !LET !T=!TAIL(!x)
    TABLES OBS=!x
    /PTOTAL=t1'{{PTOTAL1}}'
    /TABLE={{BANNER}} BY !H !DO !var !IN (!T) !CONCAT('+',!var) !DOEND
    /STATISTICS=VALIDN('{{VALIDN_LABEL}}') MEAN(!H !DO !var !IN (!T) !CONCAT('(f8.1)',!var) !DOEND (f8.1)) SUM(!H !DO !var !IN (!T) !CONCAT('(comma8.0)',!var) !DOEND (comma8.0))
    /title=!a.
!ENDDEFINE.









DEFINE cms2r (x=!CMD)
    !LET !H=!HEAD(!x)
    !LET !T=!TAIL(!x)
    TABLES OBS=!x
    /PTOTAL=t1'{{PTOTAL1}}'
    /TABLE={{BANNER}} BY !H !DO !var !IN (!T) !CONCAT('+',!var) !DOEND
    /STATISTICS=VALIDN('{{VALIDN_LABEL}}') MEAN((comma8.2)) SUM((comma8.0)).
!ENDDEFINE.









DEFINE cs (x=!CMD)
    !LET !H=!HEAD(!x)
    !LET !T=!TAIL(!x)
    TABLES OBS=!x
    /PTOTAL=t1'{{PTOTAL1}}'
    /TABLE={{BANNER}} BY !H !DO !var !IN (!T) !CONCAT('+',!var) !DOEND
    /STATISTICS=VALIDN('{{VALIDN_LABEL}}')  SUM((comma8.0)).
!ENDDEFINE.







DEFINE ms1 (x=!CMD)
    !LET !H=!HEAD(!x)
    !LET !T=!TAIL(!x)
    TABLES OBS=!x
    /PTOTAL=t1'{{PTOTAL1}}'
    /TABLE={{BANNER}} BY !H !DO !var !IN (!T) !CONCAT('+',!var) !DOEND
    /STATISTICS= MEAN((comma8.1)) SUM((comma8.0)).
!ENDDEFINE.







DEFINE ms1t (x=!CMDEND / a=!CHAREND("/"))
    !LET !H=!HEAD(!x)
    !LET !T=!TAIL(!x)
    TABLES OBS=!x
    /PTOTAL=t1'{{PTOTAL1}}'
    /TABLE={{BANNER}} BY !H !DO !var !IN (!T) !CONCAT('+',!var) !DOEND
    /STATISTICS= MEAN(!H !DO !var !IN (!T) !CONCAT('(comma8.1)',!var) !DOEND (comma8.1)) SUM(!H !DO !var !IN (!T) !CONCAT('(comma8.0)',!var) !DOEND (comma8.0))
    /title=!a.
!ENDDEFINE.









DEFINE ms2r (x=!CMD)
    !LET !H=!HEAD(!x)
    !LET !T=!TAIL(!x)
    TABLES OBS=!x
    /PTOTAL=t1'{{PTOTAL1}}'
    /TABLE={{BANNER}} BY !H !DO !var !IN (!T) !CONCAT('+',!var) !DOEND
    /STATISTICS= MEAN((comma8.2)) SUM((comma8.0)).
!ENDDEFINE.







DEFINE ms2t (x=!CMDEND / a=!CHAREND("/"))
    !LET !H=!HEAD(!x)
    !LET !T=!TAIL(!x)
    TABLES OBS=!x
    /PTOTAL=t1'{{PTOTAL1}}'
    /TABLE={{BANNER}} BY !H !DO !var !IN (!T) !CONCAT('+',!var) !DOEND
    /STATISTICS= MEAN(!H !DO !var !IN (!T) !CONCAT('(f8.2)',!var) !DOEND (f8.2)) SUM(!H !DO !var !IN (!T) !CONCAT('(comma8.0)',!var) !DOEND (comma8.0))
    /title=!a.
!ENDDEFINE.











DEFINE sm1t (x=!CMDEND / a=!CHAREND("/"))
    !LET !H=!HEAD(!x)
    !LET !T=!TAIL(!x)
    TABLES OBS=!x
    /PTOTAL=t1'{{PTOTAL1}}'
    /TABLE={{BANNER}} BY !H !DO !var !IN (!T) !CONCAT('+',!var) !DOEND
    /STATISTICS= SUM(!H !DO !var !IN (!T) !CONCAT('(comma8.0)',!var) !DOEND (comma8.0)) MEAN(!H !DO !var !IN (!T) !CONCAT('(f8.1)',!var) !DOEND (f8.1))
    /title=!a.
!ENDDEFINE.





DEFINE sm2t (x=!CMDEND / a=!CHAREND("/"))
    !LET !H=!HEAD(!x)
    !LET !T=!TAIL(!x)
    TABLES OBS=!x
    /PTOTAL=t1'{{PTOTAL1}}'
    /TABLE={{BANNER}} BY !H !DO !var !IN (!T) !CONCAT('+',!var) !DOEND
    /STATISTICS= SUM(!H !DO !var !IN (!T) !CONCAT('(comma8.0)',!var) !DOEND (comma8.0)) MEAN(!H !DO !var !IN (!T) !CONCAT('(f8.2)',!var) !DOEND (f8.2))
    /title=!a.
!ENDDEFINE.











DEFINE cmmmt (x=!CMDEND / a=!CHAREND("/"))
    !LET !H=!HEAD(!x)
    !LET !T=!TAIL(!x)
    TABLES OBS=!x
    /PTOTAL=t1'{{PTOTAL1}}'
    /TABLE={{BANNER}} BY !H !DO !var !IN (!T) !CONCAT('+',!var) !DOEND
    /STATISTICS=VALIDN('{{VALIDN_LABEL}}')  MEAN(!H !DO !var !IN (!T) !CONCAT('(comma8.0)',!var) !DOEND (comma8.0))
    MIN(!H !DO !var !IN (!T) !CONCAT('(comma8.0)',!var) !DOEND (comma8.0))
    MAX(!H !DO !var !IN (!T) !CONCAT('(comma8.0)',!var) !DOEND (comma8.0))
    /title=!a.
!ENDDEFINE.







