"""한글 파일명 터미널 인코딩 우회용 실행 래퍼"""
import subprocess, sys, os

files = [
    r"d:\git_rk\project\26_Korean_Medicine\data\output\report_기업체_대구한의대_rise_260310_송부_260317_2002_cross.md",
    r"d:\git_rk\project\26_Korean_Medicine\data\output\report_재학생_대구한의대_rise_260310_송부_260317_2002_cross.md",
]

script = os.path.join(os.path.dirname(os.path.abspath(__file__)), "generate_wording.py")

for f in files:
    print(f"\n{'='*60}")
    print(f"  Wording: {os.path.basename(f)}")
    print(f"{'='*60}")
    subprocess.run([sys.executable, "-u", script, "--input", f], env={**os.environ, "PYTHONIOENCODING": "utf-8"})
