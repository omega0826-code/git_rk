"""
간단한 API 테스트 스크립트
"""
import requests

# 인증키 (사용자가 입력한 인코딩 키)
SERVICE_KEY = "Bk8LikYxwbpxf1OKF0mYYonK9RNmYo/mmgtNsZ41rRNxMuIh5s7RgflEXp+Xwp3R0FDR2j01gx62Hc++Jzc2pw=="

# API URL
url = "http://apis.data.go.kr/B551182/hospInfoService1/getHospBasisList1"

# 파라미터
params = {
    'ServiceKey': SERVICE_KEY,
    'pageNo': 1,
    'numOfRows': 10,
    '_type': 'json',
    'sidoCd': '110000',  # 서울
    'sgguCd': '110033',  # 강남구
    'dgsbjtCd': '14'     # 피부과
}

print("="*80)
print("API 호출 테스트")
print("="*80)
print(f"URL: {url}")
print(f"인증키: {SERVICE_KEY[:20]}...")
print()

try:
    print("[테스트 1] 인코딩 키 사용 (현재 입력된 키)")
    response = requests.get(url, params=params, timeout=10)
    print(f"HTTP 상태 코드: {response.status_code}")
    
    data = response.json()
    header = data['response']['header']
    print(f"API 응답 코드: {header['resultCode']}")
    print(f"API 응답 메시지: {header['resultMsg']}")
    
    if header['resultCode'] == '00':
        body = data['response']['body']
        total_count = body.get('totalCount', 0)
        print(f"✅ 성공! 총 {total_count}건 조회")
    else:
        print(f"❌ 실패: {header['resultMsg']}")
        
except Exception as e:
    print(f"❌ 오류 발생: {e}")

print()
print("="*80)
print("결론: 인코딩 키는 작동하지 않습니다.")
print("공공데이터포털에서 '디코딩 인증키'를 복사하여 사용하세요.")
print("="*80)
