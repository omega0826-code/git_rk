@echo off
chcp 65001 > nul
echo ============================================================
echo 서울시 주요 82장소 영역 인터랙티브 지도 생성
echo ============================================================
echo.

python map_visualization.py > map_creation_log.txt 2>&1

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ============================================================
    echo 지도 생성 완료!
    echo ============================================================
    echo.
    echo 결과 파일: d:\git_rk\output\서울시_82장소_지도.html
    echo 로그 파일: map_creation_log.txt
    echo.
    echo 브라우저에서 HTML 파일을 열어보세요.
    echo.
) else (
    echo.
    echo ============================================================
    echo 오류 발생!
    echo ============================================================
    echo.
    echo 로그 파일을 확인해주세요: map_creation_log.txt
    echo.
)

pause
