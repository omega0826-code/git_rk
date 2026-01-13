"""
병원정보조회 웹 애플리케이션 - 로컬 실행 서버
CORS 문제를 해결하기 위한 간단한 HTTP 서버
"""

import http.server
import socketserver
import webbrowser
import os

PORT = 8080
DIRECTORY = os.path.dirname(os.path.abspath(__file__))

class MyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)
    
    def end_headers(self):
        # CORS 헤더 추가
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate')
        super().end_headers()

def main():
    print("=" * 60)
    print("병원정보조회 웹 애플리케이션 - 로컬 서버")
    print("=" * 60)
    print(f"서버 실행 중: http://localhost:{PORT}")
    print("")
    print("브라우저에서 다음 주소로 접속하세요:")
    print(f"  http://localhost:{PORT}/병원정보조회_웹앱.html")
    print("")
    print("종료하려면 Ctrl+C를 누르세요.")
    print("=" * 60)
    print("")
    
    # 브라우저 자동 열기
    webbrowser.open(f"http://localhost:{PORT}/병원정보조회_웹앱.html")
    
    # 서버 시작
    with socketserver.TCPServer(("", PORT), MyHTTPRequestHandler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n서버를 종료합니다...")
            httpd.shutdown()

if __name__ == "__main__":
    main()
