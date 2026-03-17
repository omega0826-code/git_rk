@echo off
chcp 65001 >nul
echo ============================================
echo  SPSS 엑셀 → 마크다운 변환
echo ============================================
echo.

REM 좀비 프로세스 정리
taskkill /F /IM python.exe /T 2>nul

REM 입력 파일 경로 (수정하여 사용)
set INPUT_FILE=d:\git_rk\project\26_Korean_Medicine\data\(output)기업체_대구한의대 rise_260310_송부.xls

echo 입력: %INPUT_FILE%
echo.

python "%~dp0spss_excel_to_md.py" --input "%INPUT_FILE%"

echo.
pause
