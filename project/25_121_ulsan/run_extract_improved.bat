@echo off
echo ===== PDF 표 추출 스크립트 실행 (개선 버전) =====
echo.

REM Python 버전 확인
python --version
echo.

REM 필수 라이브러리 설치
echo [1/3] 필수 라이브러리 설치 중...
python -m pip install --upgrade pdfplumber openpyxl
echo.

REM 선택적 라이브러리 설치 (정확도 향상)
echo [2/3] 추가 라이브러리 설치 중 (정확도 향상용)...
echo Camelot 설치 시도...
python -m pip install camelot-py[cv] 2>nul
if errorlevel 1 (
    echo   - Camelot 설치 실패 (선택사항, 건너뜀^)
) else (
    echo   - Camelot 설치 성공
)

echo Tabula 설치 시도...
python -m pip install tabula-py 2>nul
if errorlevel 1 (
    echo   - Tabula 설치 실패 (선택사항, 건너뜀^)
) else (
    echo   - Tabula 설치 성공
)
echo.

REM 개선된 스크립트 실행
echo [3/3] PDF 표 추출 시작 (개선 버전^)...
python extract_tables_improved.py
echo.

echo ===== 완료 =====
echo.
echo 생성된 파일: 울산지역_인력훈련조사_표추출_개선.xlsx
echo.
pause
