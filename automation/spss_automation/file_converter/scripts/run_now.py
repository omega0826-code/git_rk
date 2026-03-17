"""한글 파일명 터미널 인코딩 우회용 실행 래퍼"""
import subprocess, sys, os

files = [
    r"d:\git_rk\project\26_Korean_Medicine\data\(output)기업체_대구한의대 rise_260310_송부.xls",
    r"d:\git_rk\project\26_Korean_Medicine\data\(output)재학생_대구한의대 rise_260310_송부.xls",
]

script = os.path.join(os.path.dirname(os.path.abspath(__file__)), "spss_excel_to_md.py")

for f in files:
    print(f"\n{'='*60}")
    print(f"  Converting: {os.path.basename(f)}")
    print(f"{'='*60}")
    subprocess.run([sys.executable, "-u", script, "--input", f], env={**os.environ, "PYTHONIOENCODING": "utf-8"})
