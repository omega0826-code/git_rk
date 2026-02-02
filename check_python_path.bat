@echo off
chcp 65001 > nul

echo ============================================================
echo Python 경로 확인 스크립트
echo ============================================================
echo.

echo [1] where python 명령 실행
where python > python_path_info.txt 2>&1

echo [2] Python 버전 확인
python --version >> python_path_info.txt 2>&1

echo [3] Python 실행 파일 경로 확인
python -c "import sys; print('Python 경로:', sys.executable)" >> python_path_info.txt 2>&1

echo [4] 가상 환경 확인
if exist ".venv\Scripts\python.exe" (
    echo 가상 환경 발견: .venv\Scripts\python.exe >> python_path_info.txt
    .venv\Scripts\python.exe --version >> python_path_info.txt 2>&1
) else (
    echo 가상 환경 없음 >> python_path_info.txt
)

echo.
echo ============================================================
echo 결과가 python_path_info.txt에 저장되었습니다.
echo ============================================================
echo.

type python_path_info.txt

pause
