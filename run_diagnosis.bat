@echo off
echo [DIAG START] > diag_heartbeat.txt
echo Time: %TIME% >> diag_heartbeat.txt
python -u diagnose_delay.py > diag_full_log.txt 2>&1
if %ERRORLEVEL% EQU 0 (
    echo [DIAG SUCCESS] >> diag_heartbeat.txt
) else (
    echo [DIAG ERROR: %ERRORLEVEL%] >> diag_heartbeat.txt
)
echo End Time: %TIME% >> diag_heartbeat.txt
echo [DIAG END] >> diag_heartbeat.txt
