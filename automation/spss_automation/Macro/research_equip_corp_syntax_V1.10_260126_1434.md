# 연구장비(기업) 명령문 V1.10

> 원본 파일: 연구장비(기업)_명령문_V1.10_260126_1434.sps

`sps

* Encoding: UTF-8.

VARIABLE LABELS
SQ0 '귀하께서는 개인정보 수집·이용에 대해 동의하십니까?'
   /SQ1 '기업명'
   /SQ2 '부서/직위'
   /SQ3 '성명'
   /SQ4 '휴대폰번호'
   /SQ5 '이메일주소'
   /A2 '주요생산품'
   /A3 '주력산업분야'
   /A4 '주소'
   /A5 '대표자명'
   /A6 '매출액'
   /A7 '종업원수'
   /A8 '기업부설연구소'
   /A9 '연구전담부서'
   /A10 '연구인력(R&amp;D)'
   /A11_1 '연구장비보유현황\n[]'
   /A11_2 '연구장비보유현황\n[]'
   /B1 '공동활용 연구장비 이용 경험 여부'
   /B1a_1 '공동활용 연구장비 최초 인지 경로'
   /B1a_2 '공동활용 연구장비 연평균 이용 횟수'
   /B1a_3_1 '공동활용 연구장비 이용 주 목적(1순위)'
   /B2 '공동활용 연구장비 주 이용 검색 채널'
   /C1 '연구장비 정보시스템 이용 경험 여부'
   /C1a_1 '연구장비 정보시스템 만족도'
   /C3 '연구장비 정보시스템 접근성 향상 홍보 방식'
   /C4 '신규 시험기관 선정 기준'
   /E1 '지원 수혜 경험 여부'
   /E2 '정부 지원사업 필요성'
   /E3 '지원사업 유무에 따른 이용 의향'
   /F1 '추가 장비 도입 필요성'
   /F2_1 '장비명(국문)'
   /F2_2 '장비명(영문)'
   /F2_3 '모델명'
   /F2_4 '제작사'
   /F2_7 '장비도입희망사유'.
.


VALUE LABELS
   /SQ0
      1  '동의'
      2  '동의하지 않음'
   /A3
      1  '신소재부품가공'
      2  '첨단디지털부품'
      3  '라이프케어소재'
      4  '기타'
   /A8
      1  '유'
      2  '무'
   /A9
      1  '유'
      2  '무'
   /B1
      1  '있음'
      2  '없음'
   /B1a_1
      1  '홍보자료'
      2  '전문(지원)기관의 안내'
      3  '직접서치'
      4  '지인의 소개'
      5  '기타'
   /B1a_2
      1  '3회 미만'
      2  '3회 이상~6회 미만'
      3  '6회 이상~9회 미만'
      4  '10회 이상'
      5  '기타'
   /B1a_3_1 TO B1a_3_2
      1  '선행연구단계-성능시험 / 목표치 정립 등'
      2  '개발단계-개발제품(서비스)기술수준확인 및 평가'
      3  '표준화단계-제품(서비스)의 표준화 또는 인증 획득'
      4  '사업화단계-양산 및 사업화관련 마케팅(홍보)'
      5  '기타'
   /B1a_4_1 TO B1a_4_5
      1  '공동활용 연구장비 인지도 부족'
      2  '이용절차의 복잡성'
      3  '장비 사용료에 대한 부담'
      4  '최신 장비 수요 대응 미흡'
      5  '기타'
   /B2
      1  '시스템 직접검색(Zeus, i-tube등)'
      2  '시험분석 전문기관 문의'
      3  '연구·기업지원기관 문의'
      4  '이용하지 않음'
      5  '기타'
   /C1
      1  '있음'
      2  '없음'
   /C1a_1
      1  '매우 만족'
      2  '만족'
      3  '보통'
      4  '불만족'
      5  '매우 불만족'
   /C1a_2_1 TO C1a_2_5
      1  '장비정보 부족'
      2  '서비스의 다양성 부족'
      3  '사용 편의성 부족'
      4  '타 시스템과의 중복성'
      5  '기타'
   /C1a_3_1 TO C1a_3_5
      1  '시스템에 대한 인지도 부족'
      2  '이용절차의 복잡성'
      3  '장비 사용료에 대한 부담'
      4  '이용 필요성 없음'
      5  '기타'
   /C2_1 TO C2_5
      1  '시험,평가,인증 정보제공'
      2  '분야별 구체적인 장비상담'
      3  '기업지원 사업안내'
      4  '다양한 상담채널'
      5  '기타'
   /C3
      1  'e-mail, 문자'
      2  'SNS 광고'
      3  '인쇄 홍보물'
      4  '대면홍보'
      5  '기타'
   /C4
      1  '접근성 (거리)'
      2  '가격'
      3  '신속'
      4  '친절'
      5  '기타'
   /D1_1 TO D1_6
      1  '활용목적에 적합한 장비 서치의 어려움'
      2  '필요한 장비 보유기관 서치의 어려움'
      3  '장비설명 및 활용사례등에 대한 정보부족'
      4  '예약경쟁 또는 장비 가용성 부족'
      5  '어려움 없음'
      6  '기타'
   /D2_1 TO D2_5
      1  '활용목적에 적합한 장비 추천'
      2  '장비별 활용사례(예시) 정보제공'
      3  '장비 활용방법 교육 및 컨설팅'
      4  '장비 안내, 홍보자료의 정기적 제공'
      5  '기타'
   /E1
      1  '있음'
      2  '없음'
   /E2
      1  '필요함'
      2  '필요없음'
   /E2a_1_1 TO E2a_1_5
      1  '사용료 직접지원'
      2  '(선행연구/개발 등)연구개발 사업연계'
      3  '(시제품/고급화 등) 기업지원 사업연계'
      4  '(인증/표준화 등) 획득지원 사업연계'
      5  '기타'
   /E3
      1  '있음'
      2  '없음'
   /F1
      1  '매우 필요함'
      2  '필요함'
      3  '잘 모르겠음'
      4  '필요없음'
      5  '전혀 필요없음'
   /F2_5_1 TO F2_5_6
      1  '시험'
      2  '분석'
      3  '교육'
      4  '계측'
      5  '생산'
      6  '기타'
   /F2_6_1 TO F2_6_4
      1  '신소재부품가공'
      2  '첨단디지털부품'
      3  '라이프케어소재'
      4  '기타'
.



******변수 생성 




RECODE a6 (lo THRU 999..9999 =1) (1000 thru 4999.9999 = 2) (5000 thru 9999.9999 =3) (10000 thru hi =4) into a6r.

VARIABLE LABELS
 a6r '매출액'
. 

VALUE LABELS
 a6r
  1 '10억원 미만'
   2 '10~50억원 미만'
   3 '50~100억원 미만'
   4 '100억원 이상'.





RECODE a7 (lo THRU 9 =1) (10 thru 49 = 2) (50 thru 99 =3) (100 thru hi =4) into a7r.

VARIABLE LABELS
 a7r '종업원수'.
. 

VALUE LABELS
 a7r
  1 '10인 미만'
   2 '10~50인 미만'
   3 '50~100인 미만'
   4 '100인 이상'.




RECODE a10 (0 = 1) (1 thru 4 = 2) (5 thru 9 =3) (10 thru hi =4) into a10r.

VARIABLE LABELS
 a10r '연구인력수'
. 

VALUE LABELS
 a10r
  1 '연구인력 없음 '
   2 '5인 미만'
   3 '5~10인 미만'
   4 '10인 이상'.


FREQUENCIES a11_1.

FREQUENCIES a11_2.





RECODE a11_1 (0 = 1) (1 thru 4 = 2) (5 thru 9 =3) (10 thru hi =4) into a11_1r.


VARIABLE LABELS
a11_1r  '연구장비 종류'.
. 
VALUE LABELS
 a11_1r
 1 '연구장비 없음 '
 2 '5종 이하'
 3 '5~10종  미만'
 4 '10종  이상'.



RECODE a11_2 (0 = 1) (1 thru 4 = 2) (5 thru 9 =3) (10 thru hi =4) into a11_2r.

VARIABLE LABELS
a11_2r  '연구장비수'.
. 
VALUE LABELS
 a11_2r
 1 '연구장비 없음 '
 2 '5대  미만'
 3 '5대~10대  미만'
 4 '10대 이상'.



****************************







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
    /PTOTAL=t1'전 체' t2'구 분'
    /TABLE=t1+a3+a6r+a7r+a8+a9+a10r+a11_1r+ a11_2r BY t2+!x
    /STATISTICS=COUNT(t2'' !x'빈도') CPCT(!x'비율' : a3 a6r a7r a8 a9 a10r a11_1r  a11_2r )
!ENDDEFINE.







DEFINE freqt (x=!CMDEND / a=!CHAREND("/"))
    TABLES
    /PTOTAL=t1'전 체' t2'구 분'
    /TABLE=t1+a3+a6r+a7r+a8+a9+a10r+a11_1r+ a11_2r BY t2+!x
    /STATISTICS=COUNT(t2'' !x'빈도') CPCT(!x'비율' : a3 a6r a7r a8 a9 a10r a11_1r  a11_2r )
    /title=!a.
!ENDDEFINE.





DEFINE freqm2t (x=!TOKENS(1) / y=!TOKENS(1) / a=!CHAREND('/'))
    TABLES OBS = !y
    /PTOTAL=t1'전 체' t2'구 분'
    /TABLE=t1+a3+a6r+a7r+a8+a9+a10r+a11_1r+ a11_2r BY t2+ !y + !x
    /STATISTICS=COUNT(t2'' !x'빈도') mean( !y (f8.2)) CPCT(!x'비율' : a3 a6r a7r a8 a9 a10r a11_1r  a11_2r )
    /title=!a.
!ENDDEFINE.





DEFINE m1t (x=!CMDEND / a=!CHAREND("/"))
    !LET !H=!HEAD(!x)
    !LET !T=!TAIL(!x)
    TABLES OBS=!x
    /PTOTAL=t1'전 체'
    /TABLE=t1+a3+a6r+a7r+a8+a9+a10r+a11_1r+ a11_2r BY !H !DO !var !IN (!T) !CONCAT('+',!var) !DOEND
    /STATISTICS=MEAN(!H !DO !var !IN (!T) !CONCAT('(f8.1)',!var) !DOEND (f8.1))
    /title=!a.
!ENDDEFINE.







*객관식(빈도 제외)

DEFINE freq2 (x=!TOKENS(1))
    TABLES
    /PTOTAL=t1'전 체' t2'구 분'
    /TABLE=t1+a3+a6r+a7r+a8+a9+a10r+a11_1r+ a11_2r BY t2+!x
    /STATISTICS=COUNT(t2'' ) CPCT(!x'' (Pct8.1) : a3 a6r a7r a8 a9 a10r a11_1r  a11_2r).
!ENDDEFINE.




DEFINE freq2t (x=!TOKENS(1) / a=!CHAREND('/'))
    TABLES
    /PTOTAL=t1'전 체' t2'구 분'
    /TABLE=t1+a3+a6r+a7r+a8+a9+a10r+a11_1r+ a11_2r BY t2+!x
    /STATISTICS=COUNT(t2'') CPCT(!x'%' (Pct8.1) : a3 a6r a7r a8 a9 a10r a11_1r  a11_2r )
    /title=!a.
!ENDDEFINE.



*중복응답

DEFINE PR (x=!TOKENS(1) / y=!TOKENS(1) / z=!TOKENS(1) / a=!CHAREND('/'))
    TABLES
    /PTOTAL=t1'전 체' t2'구 분'
    /MRGROUP=!z !a !x TO !y
    /TABLE=t1+a3+a6r+a7r+a8+a9+a10r+a11_1r+ a11_2r BY t2+!z
    /STATISTICS=COUNT(t2'' !z'빈도') CPCT(!z'비율': a3 a6r a7r a8 a9 a10r a11_1r  a11_2r).
!ENDDEFINE.


*prt  b='하자보수 처리 시 불편사항' / x=b5_1 y=b5_5 z=aa a='eeeee'.
DEFINE PRT (x=!TOKENS(1) / y=!TOKENS(1) / z=!TOKENS(1) / a=!CHAREND('/')  / b=!CHAREND('/'))
    TABLES
    /PTOTAL=t1'전 체' t2'구 분'
    /MRGROUP=!z !a !x TO !y
    /TABLE=t1+a3+a6r+a7r+a8+a9+a10r+a11_1r+ a11_2r BY t2+!z
    /STATISTICS=COUNT(t2''  !z'빈도') CPCT(!z'비율': a3 a6r a7r a8 a9 a10r a11_1r  a11_2r)
    /title=!b.
!ENDDEFINE.







DEFINE PR2 (x=!TOKENS(1) / y=!TOKENS(1) / z=!TOKENS(1) / a=!CHAREND('/'))
    TABLES
    /PTOTAL=t1'전 체' t2'구 분'
    /MRGROUP=!z !a !x TO !y
    /TABLE=t1+a3+a6r+a7r+a8+a9+a10r+a11_1r+ a11_2r BY t2+!z
    /STATISTICS=COUNT(t2'' ) CPCT(!z'%' (Pct8.1): a3 a6r a7r a8 a9 a10r a11_1r  a11_2r).
!ENDDEFINE.




DEFINE PR2T (x=!TOKENS(1) / y=!TOKENS(1) / z=!TOKENS(1) / a=!CHAREND('/')  / b=!CHAREND('/'))
    TABLES
    /PTOTAL=t1'전 체' t2'구 분'
    /MRGROUP=!z !a !x TO !y
    /TABLE=t1+a3+a6r+a7r+a8+a9+a10r+a11_1r+ a11_2r BY t2+!z
    /STATISTICS=COUNT(t2'' (comma8.0) ) CPCT(!z'%'(Pct8.1): a3 a6r a7r a8 a9 a10r a11_1r  a11_2r)
    /title=!b.
!ENDDEFINE.






*중복응답(빈도 제외) 그래프

DEFINE PRG (x=!TOKENS(1) / y=!TOKENS(1) / z=!TOKENS(1) / a=!CHAREND('/'))
    TABLES
    /PTOTAL=t1'전 체' t2'구 분'
    /MRGROUP=!z !a !x TO !y
    /TABLE=t1+a3+a6r+a7r+a8+a9+a10r+a11_1r+ a11_2r BY t2+!z
    /STATISTICS=COUNT(t2'' ) CPCT(!z'비율': a3 a6r a7r a8 a9 a10r a11_1r  a11_2r)
    /corner ='그래프(비율)' .
    
    
    TABLES
    /PTOTAL=t1'전 체' t2'구 분'
    /MRGROUP=!z !a !x TO !y
    /TABLE=t1+a3+a6r+a7r+a8+a9+a10r+a11_1r+ a11_2r BY t2+!z
    /STATISTICS=COUNT(t2'' !z'빈도')
    /corner ='그래프(빈도)' .
!ENDDEFINE.




*우선순위(100%)

DEFINE PR3T (x=!TOKENS(1) / y=!TOKENS(1) / z=!TOKENS(1) / a=!CHAREND('/')  / b=!CHAREND('/'))
    TABLES
    /PTOTAL=t1'전 체' t2'구 분'
    /MRGROUP=!z !a !x TO !y
    /GBASE=RESPONSE
    /TABLE=t1+a3+a6r+a7r+a8+a9+a10r+a11_1r+ a11_2r BY t2+!z
    /STATISTICS=COUNT(t2'' !z'빈도') CPCT(!z'비율': a3 a6r a7r a8 a9 a10r a11_1r  a11_2r)
    /title=!b.
!ENDDEFINE.


*우선순위(빈도 제외) 그래프(100%)

DEFINE PR4 (x=!TOKENS(1) / y=!TOKENS(1) / z=!TOKENS(1) / a=!CHAREND('/'))
    TABLES
    /PTOTAL=t1'전 체' t2'구 분'
    /MRGROUP=!z !a !x TO !y
    /GBASE=RESPONSE
    /TABLE=t1+a3+a6r+a7r+a8+a9+a10r+a11_1r+ a11_2r BY t2+!z
    /STATISTICS=COUNT(t2'' ) CPCT(!z'비율': a3 a6r a7r a8 a9 a10r a11_1r  a11_2r).
!ENDDEFINE.


DEFINE PR4T (x=!TOKENS(1) / y=!TOKENS(1) / z=!TOKENS(1) / a=!CHAREND('/')  / b=!CHAREND('/'))
    TABLES
    /PTOTAL=t1'전 체' t2'구 분'
    /MRGROUP=!z !a !x TO !y
    /GBASE=RESPONSE
    /TABLE=t1+a3+a6r+a7r+a8+a9+a10r+a11_1r+ a11_2r BY t2+!z
    /STATISTICS=COUNT(t2''(comma8.1) ) CPCT(!z'%': a3 a6r a7r a8 a9 a10r a11_1r  a11_2r)
    /title=!b.
!ENDDEFINE.









*평균




DEFINE m1 (x=!CMD)
    !LET !H=!HEAD(!x)
    !LET !T=!TAIL(!x)
    TABLES OBS=!x
    /PTOTAL=t1'전 체'
    /TABLE=t1+a3+a6r+a7r+a8+a9+a10r+a11_1r+ a11_2r BY !H !DO !var !IN (!T) !CONCAT('+',!var) !DOEND
    /STATISTICS=MEAN('(100점)' (f8.1)).
!ENDDEFINE.




DEFINE m1t (x=!CMDEND / a=!CHAREND("/"))
    !LET !H=!HEAD(!x)
    !LET !T=!TAIL(!x)
    TABLES OBS=!x
    /PTOTAL=t1'전 체'
    /TABLE=t1+a3+a6r+a7r+a8+a9+a10r+a11_1r+ a11_2r BY !H !DO !var !IN (!T) !CONCAT('+',!var) !DOEND
    /STATISTICS=MEAN(!H !DO !var !IN (!T) !CONCAT('(f8.1)',!var) !DOEND (f8.1))
    /title=!a.
!ENDDEFINE.




*참고 : PCT는 표시형식만 %추가 *100 필요

DEFINE m1pt (x=!CMDEND / a=!CHAREND("/"))
    !LET !H=!HEAD(!x)
    !LET !T=!TAIL(!x)
    TABLES OBS=!x
    /PTOTAL=t1'전 체'
    /TABLE=t1+a3+a6r+a7r+a8+a9+a10r+a11_1r+ a11_2r BY !H !DO !var !IN (!T) !CONCAT('+',!var) !DOEND
    /STATISTICS=MEAN(!H !DO !var !IN (!T) !CONCAT('(PCT8.1)',!var) !DOEND (PCT8.1))
    /title=!a.
!ENDDEFINE.









DEFINE m2 (x=!CMD)
    !LET !H=!HEAD(!x)
    !LET !T=!TAIL(!x)
    TABLES OBS=!x
    /PTOTAL=t1'전 체'
    /TABLE=t1+a3+a6r+a7r+a8+a9+a10r+a11_1r+ a11_2r BY !H !DO !var !IN (!T) !CONCAT('+',!var) !DOEND
    /STATISTICS=MEAN((f8.2)).
!ENDDEFINE.



*예제 m2t  a = '부대별 차원 만족도' / x = TT a2h a4h a6h a8h.
DEFINE m2t (x=!CMDEND / a=!CHAREND("/"))
    !LET !H=!HEAD(!x)
    !LET !T=!TAIL(!x)
    TABLES OBS=!x
    /PTOTAL=t1'전 체'
    /TABLE=t1+a3+a6r+a7r+a8+a9+a10r+a11_1r+ a11_2r BY !H !DO !var !IN (!T) !CONCAT('+',!var) !DOEND
    /STATISTICS=MEAN(!H !DO !var !IN (!T) !CONCAT('(f8.2)',!var) !DOEND (f8.2))
    /title=!a.
!ENDDEFINE.







DEFINE co (x=!CMD)
    !LET !H=!HEAD(!x)
    !LET !T=!TAIL(!x)
    TABLES OBS=!x
    /PTOTAL=t1'전 체'
    /TABLE=t1+a3+a6r+a7r+a8+a9+a10r+a11_1r+ a11_2r BY !H !DO !var !IN (!T) !CONCAT('+',!var) !DOEND
    /STATISTICS=VALIDN('업체수')
!ENDDEFINE.








DEFINE cot (x=!CMDEND / a=!CHAREND("/"))
    !LET !H=!HEAD(!x)
    !LET !T=!TAIL(!x)
    TABLES OBS=!x
    /PTOTAL=t1'전 체'
    /TABLE=t1+a3+a6r+a7r+a8+a9+a10r+a11_1r+ a11_2r BY !H !DO !var !IN (!T) !CONCAT('+',!var) !DOEND
    /STATISTICS=VALIDN('업체수' (comma8.0))
    /title=!a.
!ENDDEFINE.





DEFINE sot (x=!CMDEND / a=!CHAREND("/"))
    !LET !H=!HEAD(!x)
    !LET !T=!TAIL(!x)
    TABLES OBS=!x
    /PTOTAL=t1'전 체'
    /TABLE=t1+a3+a6r+a7r+a8+a9+a10r+a11_1r+ a11_2r BY !H !DO !var !IN (!T) !CONCAT('+',!var) !DOEND
    /STATISTICS=sum((comma8.0))
    /title=!a.
!ENDDEFINE.




DEFINE cst (x=!CMDEND / a=!CHAREND("/"))
    !LET !H=!HEAD(!x)
    !LET !T=!TAIL(!x)
    TABLES OBS=!x
    /PTOTAL=t1'전 체'
    /TABLE=t1+a3+a6r+a7r+a8+a9+a10r+a11_1r+ a11_2r BY !H !DO !var !IN (!T) !CONCAT('+',!var) !DOEND
    /STATISTICS= VALIDN('업체수' (comma8.0))  sum((comma8.0))
    /title=!a.
!ENDDEFINE.



DEFINE cm1 (x=!CMD)
    !LET !H=!HEAD(!x)
    !LET !T=!TAIL(!x)
    TABLES OBS=!x
    /PTOTAL=t1'전 체'
    /TABLE=t1+a3+a6r+a7r+a8+a9+a10r+a11_1r+ a11_2r BY !H !DO !var !IN (!T) !CONCAT('+',!var) !DOEND
    /STATISTICS=VALIDN('업체수') MEAN((f8.1)).
!ENDDEFINE.





DEFINE cm1t (x=!CMDEND / a=!CHAREND("/"))
    !LET !H=!HEAD(!x)
    !LET !T=!TAIL(!x)
    TABLES OBS=!x
    /PTOTAL=t1'전 체'
    /TABLE=t1+a3+a6r+a7r+a8+a9+a10r+a11_1r+ a11_2r BY !H !DO !var !IN (!T) !CONCAT('+',!var) !DOEND
    /STATISTICS=VALIDN('업체수') MEAN(!H !DO !var !IN (!T) !CONCAT('(f8.1)',!var) !DOEND (f8.1))
    /title=!a.
!ENDDEFINE.




DEFINE cm2 (x=!CMD)
    !LET !H=!HEAD(!x)
    !LET !T=!TAIL(!x)
    TABLES OBS=!x
    /PTOTAL=t1'전 체'
    /TABLE=t1+a3+a6r+a7r+a8+a9+a10r+a11_1r+ a11_2r BY !H !DO !var !IN (!T) !CONCAT('+',!var) !DOEND
    /STATISTICS=VALIDN('업체수') MEAN((f8.2)).
!ENDDEFINE.





DEFINE cm2t (x=!CMDEND / a=!CHAREND("/"))
    !LET !H=!HEAD(!x)
    !LET !T=!TAIL(!x)
    TABLES OBS=!x
    /PTOTAL=t1'전 체'
    /TABLE=t1+a3+a6r+a7r+a8+a9+a10r+a11_1r+ a11_2r BY !H !DO !var !IN (!T) !CONCAT('+',!var) !DOEND
    /STATISTICS=VALIDN('업체수') MEAN(!H !DO !var !IN (!T) !CONCAT('(f8.2)',!var) !DOEND (f8.2))
    /title=!a.
!ENDDEFINE.






DEFINE csm1t (x=!CMDEND / a=!CHAREND("/"))
    !LET !H=!HEAD(!x)
    !LET !T=!TAIL(!x)
    TABLES OBS=!x
    /PTOTAL=t1'전 체'
    /TABLE=t1+a3+a6r+a7r+a8+a9+a10r+a11_1r+ a11_2r BY !H !DO !var !IN (!T) !CONCAT('+',!var) !DOEND
    /STATISTICS=VALIDN('업체수')  SUM(!H !DO !var !IN (!T) !CONCAT('(comma8.0)',!var) !DOEND (comma8.0)) MEAN(!H !DO !var !IN (!T) !CONCAT('(f8.1)',!var) !DOEND (f8.1))
    /title=!a.
!ENDDEFINE.






DEFINE cms2 (x=!CMD)
    !LET !H=!HEAD(!x)
    !LET !T=!TAIL(!x)
    TABLES OBS=!x
    /PTOTAL=t1'전 체'
    /TABLE=t1+a3+a6r+a7r+a8+a9+a10r+a11_1r+ a11_2r BY !H !DO !var !IN (!T) !CONCAT('+',!var) !DOEND
    /STATISTICS=VALIDN('업체수') MEAN((f8.2)) SUM((f8.0)).
!ENDDEFINE.



DEFINE cms2t (x=!CMDEND / a=!CHAREND("/"))
    !LET !H=!HEAD(!x)
    !LET !T=!TAIL(!x)
    TABLES OBS=!x
    /PTOTAL=t1'전 체'
    /TABLE=t1+a3+a6r+a7r+a8+a9+a10r+a11_1r+ a11_2r BY !H !DO !var !IN (!T) !CONCAT('+',!var) !DOEND
    /STATISTICS=VALIDN('업체수') MEAN(!H !DO !var !IN (!T) !CONCAT('(f8.2)',!var) !DOEND (f8.2)) SUM(!H !DO !var !IN (!T) !CONCAT('(comma8.0)',!var) !DOEND (comma8.0))
    /title=!a.
!ENDDEFINE.







DEFINE cms3 (x=!CMD)
    !LET !H=!HEAD(!x)
    !LET !T=!TAIL(!x)
    TABLES OBS=!x
    /PTOTAL=t1'전 체'
    /TABLE=t1+a3+a6r+a7r+a8+a9+a10r+a11_1r+ a11_2r BY !H !DO !var !IN (!T) !CONCAT('+',!var) !DOEND
    /STATISTICS=VALIDN('업체수') MEAN((f8.0)) SUM((f8.0)).
!ENDDEFINE.






DEFINE cms1 (x=!CMD)
    !LET !H=!HEAD(!x)
    !LET !T=!TAIL(!x)
    TABLES OBS=!x
    /PTOTAL=t1'전 체'
    /TABLE=t1+a3+a6r+a7r+a8+a9+a10r+a11_1r+ a11_2r BY !H !DO !var !IN (!T) !CONCAT('+',!var) !DOEND
    /STATISTICS=VALIDN('업체수') MEAN((comma8.1)) SUM((comma8.0)).
!ENDDEFINE.



DEFINE cms1t (x=!CMDEND / a=!CHAREND("/"))
    !LET !H=!HEAD(!x)
    !LET !T=!TAIL(!x)
    TABLES OBS=!x
    /PTOTAL=t1'전 체'
    /TABLE=t1+a3+a6r+a7r+a8+a9+a10r+a11_1r+ a11_2r BY !H !DO !var !IN (!T) !CONCAT('+',!var) !DOEND
    /STATISTICS=VALIDN('업체수') MEAN(!H !DO !var !IN (!T) !CONCAT('(f8.1)',!var) !DOEND (f8.1)) SUM(!H !DO !var !IN (!T) !CONCAT('(comma8.0)',!var) !DOEND (comma8.0))
    /title=!a.
!ENDDEFINE.




DEFINE cms2r (x=!CMD)
    !LET !H=!HEAD(!x)
    !LET !T=!TAIL(!x)
    TABLES OBS=!x
    /PTOTAL=t1'전 체'
    /TABLE=t1+a3+a6r+a7r+a8+a9+a10r+a11_1r+ a11_2r BY !H !DO !var !IN (!T) !CONCAT('+',!var) !DOEND
    /STATISTICS=VALIDN('업체수') MEAN((comma8.2)) SUM((comma8.0)).
!ENDDEFINE.




DEFINE cs (x=!CMD)
    !LET !H=!HEAD(!x)
    !LET !T=!TAIL(!x)
    TABLES OBS=!x
    /PTOTAL=t1'전 체'
    /TABLE=t1+a3+a6r+a7r+a8+a9+a10r+a11_1r+ a11_2r BY !H !DO !var !IN (!T) !CONCAT('+',!var) !DOEND
    /STATISTICS=VALIDN('업체수')  SUM((comma8.0)).
!ENDDEFINE.



DEFINE ms1 (x=!CMD)
    !LET !H=!HEAD(!x)
    !LET !T=!TAIL(!x)
    TABLES OBS=!x
    /PTOTAL=t1'전 체'
    /TABLE=t1+a3+a6r+a7r+a8+a9+a10r+a11_1r+ a11_2r BY !H !DO !var !IN (!T) !CONCAT('+',!var) !DOEND
    /STATISTICS= MEAN((comma8.1)) SUM((comma8.0)).
!ENDDEFINE.



DEFINE ms1t (x=!CMDEND / a=!CHAREND("/"))
    !LET !H=!HEAD(!x)
    !LET !T=!TAIL(!x)
    TABLES OBS=!x
    /PTOTAL=t1'전 체'
    /TABLE=t1+a3+a6r+a7r+a8+a9+a10r+a11_1r+ a11_2r BY !H !DO !var !IN (!T) !CONCAT('+',!var) !DOEND
    /STATISTICS= MEAN(!H !DO !var !IN (!T) !CONCAT('(comma8.1)',!var) !DOEND (comma8.1)) SUM(!H !DO !var !IN (!T) !CONCAT('(comma8.0)',!var) !DOEND (comma8.0))
    /title=!a.
!ENDDEFINE.




DEFINE ms2r (x=!CMD)
    !LET !H=!HEAD(!x)
    !LET !T=!TAIL(!x)
    TABLES OBS=!x
    /PTOTAL=t1'전 체'
    /TABLE=t1+a3+a6r+a7r+a8+a9+a10r+a11_1r+ a11_2r BY !H !DO !var !IN (!T) !CONCAT('+',!var) !DOEND
    /STATISTICS= MEAN((comma8.2)) SUM((comma8.0)).
!ENDDEFINE.



DEFINE ms2t (x=!CMDEND / a=!CHAREND("/"))
    !LET !H=!HEAD(!x)
    !LET !T=!TAIL(!x)
    TABLES OBS=!x
    /PTOTAL=t1'전 체'
    /TABLE=t1+a3+a6r+a7r+a8+a9+a10r+a11_1r+ a11_2r BY !H !DO !var !IN (!T) !CONCAT('+',!var) !DOEND
    /STATISTICS= MEAN(!H !DO !var !IN (!T) !CONCAT('(f8.2)',!var) !DOEND (f8.2)) SUM(!H !DO !var !IN (!T) !CONCAT('(comma8.0)',!var) !DOEND (comma8.0))
    /title=!a.
!ENDDEFINE.





DEFINE sm1t (x=!CMDEND / a=!CHAREND("/"))
    !LET !H=!HEAD(!x)
    !LET !T=!TAIL(!x)
    TABLES OBS=!x
    /PTOTAL=t1'전 체'
    /TABLE=t1+a3+a6r+a7r+a8+a9+a10r+a11_1r+ a11_2r BY !H !DO !var !IN (!T) !CONCAT('+',!var) !DOEND
    /STATISTICS= SUM(!H !DO !var !IN (!T) !CONCAT('(comma8.0)',!var) !DOEND (comma8.0)) MEAN(!H !DO !var !IN (!T) !CONCAT('(f8.1)',!var) !DOEND (f8.1))
    /title=!a.
!ENDDEFINE.


DEFINE sm2t (x=!CMDEND / a=!CHAREND("/"))
    !LET !H=!HEAD(!x)
    !LET !T=!TAIL(!x)
    TABLES OBS=!x
    /PTOTAL=t1'전 체'
    /TABLE=t1+a3+a6r+a7r+a8+a9+a10r+a11_1r+ a11_2r BY !H !DO !var !IN (!T) !CONCAT('+',!var) !DOEND
    /STATISTICS= SUM(!H !DO !var !IN (!T) !CONCAT('(comma8.0)',!var) !DOEND (comma8.0)) MEAN(!H !DO !var !IN (!T) !CONCAT('(f8.2)',!var) !DOEND (f8.2))
    /title=!a.
!ENDDEFINE.





DEFINE cmmmt (x=!CMDEND / a=!CHAREND("/"))
    !LET !H=!HEAD(!x)
    !LET !T=!TAIL(!x)
    TABLES OBS=!x
    /PTOTAL=t1'전 체'
    /TABLE=t1+a3+a6r+a7r+a8+a9+a10r+a11_1r+ a11_2r BY !H !DO !var !IN (!T) !CONCAT('+',!var) !DOEND
    /STATISTICS=VALIDN('업체수')  MEAN(!H !DO !var !IN (!T) !CONCAT('(comma8.0)',!var) !DOEND (comma8.0))
    MIN(!H !DO !var !IN (!T) !CONCAT('(comma8.0)',!var) !DOEND (comma8.0))
    MAX(!H !DO !var !IN (!T) !CONCAT('(comma8.0)',!var) !DOEND (comma8.0))
    /title=!a.
!ENDDEFINE.



*********************************


COMPUTE X=1.
VARIABLE LABELS X ''.

variable labels X ''.
tables observation=X
 /pto=total'전 체'
 /table= total+a3+a6r+a7r+a8+a9+a10r+a11_1r+ a11_2r  by X
 /sta=count(X'기업 수') cpct(X'비율')
 /title='기업 일반현황'.





ms1t a='기업현황' / x=a6 a7.





***Part B. 공동활용연구장비 활용현황

freqt a='B1. 귀하(귀사)는 처음 공동활용 연구장비를 어떻게 알게 되어 활용하셨습니까?' / x=b1.



TEMPORARY.
SELECT IF(b1=1).
freqt a='B1-1. 귀하(귀사)는 처음 공동활용 연구장비를 어떻게 알게 되어 활용하셨습니까?' / x=b1a_1.

TEMPORARY.
SELECT IF(b1=1).
freqt a='B1-2. 귀하(귀사)가 연평균 공동활용 연구장비를 이용하는 횟수는 어떻게 되십니까?' / x=b1a_2.

TEMPORARY.
SELECT IF(b1=1).
freqt a='B1-3. 귀하(귀사)가 공동활용 연구장비를 이용하시는 주목적은 무엇입니까?(*2순위까지 선택)' / x=B1a_3_1.

TEMPORARY.
SELECT IF(b1=1).
prt b='B1-3. 귀하(귀사)가 공동활용 연구장비를 이용하시는 주목적은 무엇입니까?(*2순위까지 선택)' / x=B1a_3_1 y=B1a_3_2  z=aa a='공동활용 연구장비 이용 주 목적(1순위+2순위)'.

TEMPORARY.
SELECT IF(b1=2).
prt b='B1-4. 귀하(귀사)가 공동활용 연구장비를 이용하신 경험이 없으시다면, 그 이유는 무엇입니까?(*중복응답 가능)' /  x=B1a_4_1 y=B1a_4_5  z=aa a= '공동활용 연구장비 미이용 사유(중복응답)'.




freqt a='B2. 귀하(귀사)는 평소 공동활용 연구장비 검색을 위해 어떤 채널을 가장 많이 이용하십니까?' / x=b2.



***Part C. 연구장비 정보시스템 활용현황 

freqt a='C1. 귀하(귀사)는 공동활용 연구장비 정보시스템을 이용하신 경험이 있으십니까?'/ x=c1.


TEMPORARY.
SELECT IF(c1=1).
freqt a='C1-1. 공동활용 연구장비 시스템에 대한 귀하(귀사)의 만족도는 어느정도 입니까?'/ x=c1a_1.


RECODE c1a_1 (1 =5) (2=4)( 3=3) (4=2) (5=1) into c1a_1r.

TEMPORARY.
SELECT IF(c1=1).
freqm2t a='C1-1. 공동활용 연구장비 시스템에 대한 귀하(귀사)의 만족도는 어느정도 입니까?'/ x=c1a_1 y=c1a_1r.


TEMPORARY.
SELECT IF(c1a_1>3).
prt b='C1-2. 시스템의 서비스 및 컨텐츠에 대해 불만족 하시는 이유는 무엇입니까?(*중복응답 가능)' / x=C1a_2_1 y=C1a_2_5  z=aa a= '연구장비 정보시스템 불만족 사유(중복응답)'.


TEMPORARY.
SELECT IF(c1=2).
prt b='C1-3. 이용하신 경험이 없으시다면, 그 이유는 무엇입니까?(*중복응답 가능)' / x=C1a_3_1 y=C1a_3_5  z=aa a= '연구장비 정보시스템 미이용 사유(중복응답)'.


prt b='C2. 연구장비 정보시스템에서 제공되었으면 하는 서비스 또는 컨텐츠는 무엇입니까?(*중복응답 가능)'/ x=C2_1 y=C2_5  z=aa a= '연구장비 정보시스템 희망 제공 서비스 및 콘텐츠(중복응답)'.


freqt a='C3. 연구장비 정보시스템의 홍보가 어떤 방식으로 이루어졌을 때,사용자의 접근성이 가장 높다고 생각하십니까?'/x=c3.

freqt a='C4. 귀하(귀사)는 신규 연구장비 시험기관을 의뢰할 때 선택하는 기준은 무엇입니까?'/x=c4.





***Part D. 장비활용 애로사항

 prt b='D1. 귀하(귀사)는 공동활용 연구장비를 활용하는 데 있어 어떤 어려움이 있으십니까?(*중복응답 가능)'/ x=D1_1 y=D1_6  z=aa a= '공동활용 연구장비 활용 시 애로사항(중복응답)'.

 prt b='D2. 귀하(귀사)는 어떤 서비스가 제공된다면 연구장비를 보다 더 적극적으로 활용할 것 같으십니까?(*중복응답 가능)'/ x=D2_1 y=D2_5  z=aa a= '공동활용 연구장비 활성화 필요 서비스(중복응답)'.






***Part E. 기업지원사업의 필요성`

freqt a='E1. 귀하(귀사)에서는 정부, 지자체, 기업지원기관 등으로부터연구장비 사용료 또는 연계지원사업 등 지원을 받은 경험이 있으십니까?'/ x=e1.

freqt a='E2. 귀하(귀사)에서는 공동활용 연구장비 활용촉진을 위해 정부지원사업이 필요하다고 생각하십니까?'/ x=e2.

prt b='E2-1. 정부지원사업이 필요하다면, 어떤 방식의 지원이 필요하다고 생각하십니까?(*중복응답 가능)'/ x=E2a_1_1 y=E2a_1_5  z=aa a= '희망 지원 방식(중복응답)'.

freqt a='E3. 정부지원사업이 있는 경우, 공동활용 연구장비를 이용할 의향이 있으십니까?'/ x=e3.





***Part F. 공동활용 연구장비 추가 도입

freqt a='F1. 귀하(귀사)에서는 현재 보유한 경북지역 공동활용 연구장비 이외에 추가 장비 도입이 필요하다고 생각하십니까?'/ x=f1.

RECODE f1 (1 =5) (2=4)( 3=3) (4=2) (5=1) into f1r.

freqm2t a='F1. 귀하(귀사)에서는 현재 보유한 경북지역 공동활용 연구장비 이외에 추가 장비 도입이 필요하다고 생각하십니까?'/ x=f1 y=f1r.


prt b='F2a. 활용용도(*중복응답 가능)'/ x=f2_5_1 y=f2_5_6  z=aa a= '추가 도입 장비 활용?도(중복응답)'.

prt b='F2b. 장비활용분야[경북 주력산업] (*중복응답 가능)'/ x=f2_6_1 y=f2_6_4  z=aa a= '추가 도입 장비 활용?도(중복응답)'.



`
