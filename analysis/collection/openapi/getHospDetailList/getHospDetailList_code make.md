# 요청사항
 - 건강보험심사평가원_의료기관별상세정보서비스 다운로드를 위해 실행 파이썬 코드를 참고하여 유사한 구조로 스크립트를 작성
    - OPENAPI 실행 코드(유사코드) : D:\git_rk\openapi\getHospBasisList\병원정보_조회_v1.00F_260113.py
 - 강남지역 피부과 병원정보를 활용하여 상세정보를 다운로드 받기 위한 스크립트를 작성
    - 강남지역 피부과 병원정보(병원정보서비스 병원기본목록에서 다운로드)  : D:\git_rk\openapi\getHospBasisList\data\서울_강남구_피부과_20260113_205835.xlsx
 
# 다운로드 받을 데이터 설명
 - 건강보험심사평가원에서 수집·관리하는 의료기관의 상세정보를 제공하는 서비스입니다.
 - 시설정보, 세부정보, 진료과목정보, 교통정보, 의료장비정보, 식대가산정보, 간호등급정보, 특수진료정보(진료가능분야조회), 전문병원지정분야, 전문과목별전문의수, 기타인력수 정보 조회 가능
 - 요양기호는 1:1로 매칭한 암호화된 요양기호로 제공하고 있으며, 별도의 복호화 방법 또는 요양기호는 제공하고 있지 않습니다.
 - 암호화된 요양기호는 건강보험심사평가원 '병원정보서비스' Open API > 병원기본목록에서 확인 가능합니다.

# 스크립트 작성 활용
 - 데이터명 : 건강보험심사평가원_의료기관별상세정보서비스
 - 데이터 상세설명 : https://www.data.go.kr/data/15001699/openapi.do
 - End point : https://apis.data.go.kr/B551182/MadmDtlInfoService2.7
 - 메타 데이터 :
        This XML file does not appear to have any style information associated with it. The document tree is shown below.
        <rdf:RDF xmlns:foaf="http://xmlns.com/foaf/0.1/" xmlns:dct="http://purl.org/dc/terms/" xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#" xmlns:dcat="http://www.w3.org/ns/dcat#" xmlns:vcard="http://www.w3.org/2006/vcard/ns#">
        <script/>
        <dcat:Catalog>
        <dcat:service>
        <dcat:DataService>
        <dcat:contactPoint>
        <vcard:Organization>
        <vcard:organization-unit>빅데이터실</vcard:organization-unit>
        <vcard:hasTelephone rdf:resource="033-739-1008"/>
        </vcard:Organization>
        </dcat:contactPoint>
        <dct:description>건강보험심사평가원에서 수집·관리하는 의료기관의 상세정보를 제공하는 서비스입니다. - 시설정보, 세부정보, 진료과목정보, 교통정보, 의료장비정보, 식대가산정보, 간호등급정보, 특수진료정보(진료가능분야조회), 전문병원지정분야, 전문과목별전문의수, 기타인력수 정보 조회 가능 ※ 요양기호는 1:1로 매칭한 암호화된 요양기호로 제공하고 있으며, 별도의 복호화 방법 또는 요양기호는 제공하고 있지 않습니다. · 암호화된 요양기호는 건강보험심사평가원 '병원정보서비스' Open API > 병원기본목록에서 확인 가능합니다.</dct:description>
        <dct:title>건강보험심사평가원_의료기관별상세정보서비스</dct:title>
        <dct:issued rdf:datatype="http://www.w3.org/2001/XMLSchema#date">2016-12-31</dct:issued>
        <dct:modified rdf:datatype="http://www.w3.org/2001/XMLSchema#date">2025-07-08</dct:modified>
        <dct:publisher>
        <foaf:Organization>
        <foaf:name>건강보험심사평가원</foaf:name>
        </foaf:Organization>
        </dct:publisher>
        <dcat:format>JSON+XML</dcat:format>
        <dcat:theme>보건 - 건강보험</dcat:theme>
        <dcat:keyword>건강보험,보건의료자원,의료시설,의료인력,보건의료빅데이터</dcat:keyword>
        <dcat:keyword>Health Insurance,Health and Medical Resources,Medical facilities,Medical personnel,Health and Medical Big Data</dcat:keyword>
        <dct:rights>공공저작물_출처표시</dct:rights>
        <dcat:landingPage rdf:resource="https://www.data.go.kr/data/15001699/openapi.do"/>
        <dcat:endpointURL/>
        <dcat:accessURL/>
        <dct:spatial/>
        <dct:temporal/>
        </dcat:DataService>
        </dcat:service>
        </dcat:Catalog>
        </rdf:RDF>
 

# 스크립트 작성 참고파일
 - 실행 파이썬 코드를 참고하여 유사한 구조로 스크립트를 작성 : 실제 다운로드 성공함 
    - OPENAPI 실행 코드(유사코드) : D:\git_rk\openapi\getHospBasisList\병원정보_조회_v1.00F_260113.py

 

# 산출물
 - 모든 산출물은 폴더 내에 포함 
 - 스크립트 작성에 검토한 내용은 마크다운 형태로 모두 저장 => 기존 마크 다운이 있는 경우에는 업데이트된 내용을
   반영하고 업데이트된 내용을 기록
 - 추후 다른 개발자들이 스크립트 내용을 이해할 수 있도록 주석을 추가
 - 다른 openapi를 스크립트 작성에 활용할 수 있도록 가이드라인을 제작

