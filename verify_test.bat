@echo off
echo [TEST START %TIME%] > d:\git_rk\verify_result.txt
python -u -c "import time; t=time.time(); print(f'Python OK: {time.time()-t:.3f}s'); import sys; print(f'Version: {sys.version}'); print(f'PYTHONUNBUFFERED: ' + str(__import__('os').environ.get('PYTHONUNBUFFERED','NOT SET')))" >> d:\git_rk\verify_result.txt 2>&1
echo [TEST END %TIME%] >> d:\git_rk\verify_result.txt
