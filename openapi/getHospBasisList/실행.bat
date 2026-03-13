@echo off
chcp 65001 >nul
echo ============================================================
echo 병원정보조회 웹 애플리케이션 - 간편 실행
echo ============================================================
echo.
echo Python이 설치되어 있는지 확인 중...
python --version >nul 2>&1
if errorlevel 1 (
    echo [오류] Python이 설치되어 있지 않습니다.
    echo.
    echo Python을 설치하려면:
    echo 1. https://www.python.org 방문
    echo 2. Python 3.x 다운로드 및 설치
    echo 3. 설치 시 "Add Python to PATH" 체크
    echo 4. 설치 후 이 파일을 다시 실행하세요.
    echo.
    pause
    exit /b 1
)

echo Python 버전:
python --version
echo.
echo 웹 서버를 시작하고 브라우저를 엽니다...
echo.

python 서버실행.py

pause
