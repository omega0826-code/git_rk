@echo off
chcp 65001 > nul

echo [START] > map_status.txt
echo 지도 생성 시작... >> map_status.txt

python map_visualization.py > map_creation_log.txt 2>&1

if %ERRORLEVEL% EQU 0 (
    echo [SUCCESS] >> map_status.txt
    echo 지도 생성 완료! >> map_status.txt
) else (
    echo [ERROR] >> map_status.txt
    echo 오류 발생! >> map_status.txt
)

echo [END] >> map_status.txt
