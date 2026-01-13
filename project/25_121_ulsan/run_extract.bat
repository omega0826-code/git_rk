@echo off
echo ===== PDF 표 추출 스크립트 실행 =====
echo.

REM Python 버전 확인
python --version
echo.

REM 필요한 라이브러리 설치
echo 필요한 라이브러리 설치 중...
python -m pip install --upgrade pdfplumber openpyxl
echo.

REM 스크립트 실행
echo PDF 표 추출 시작...
python extract_tables_from_pdf.py
echo.

echo ===== 완료 =====
pause
