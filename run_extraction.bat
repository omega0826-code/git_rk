
@echo off
echo [LOG START] > heartbeat.txt
echo Start Time: %TIME% >> heartbeat.txt
echo Directory: %CD% >> heartbeat.txt

echo Running Gangnam Extraction Script...
python -u process_gangnam_data.py > run_log.txt 2>&1

if %ERRORLEVEL% EQU 0 (
    echo [SUCCESS] >> heartbeat.txt
) else (
    echo [ERROR: %ERRORLEVEL%] >> heartbeat.txt
)
echo End Time: %TIME% >> heartbeat.txt
echo [LOG END] >> heartbeat.txt
