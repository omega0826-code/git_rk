
@echo off
echo [V2 START] > heartbeat_v2.txt
echo Start Time: %TIME% >> heartbeat_v2.txt
python -u process_gangnam_data_v2.py > run_log_v2.txt 2>&1
if %ERRORLEVEL% EQU 0 (
    echo [V2 SUCCESS] >> heartbeat_v2.txt
) else (
    echo [V2 ERROR: %ERRORLEVEL%] >> heartbeat_v2.txt
)
echo End Time: %TIME% >> heartbeat_v2.txt
echo [V2 END] >> heartbeat_v2.txt
