# -*- coding: utf-8 -*-
"""검증 스크립트 — 대구한의대 XLS 34장 생성 확인"""
import sys, os, io

if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'chart'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from run_chart import generate

INPUT = r"d:\git_rk\project\26_Korean_Medicine\data\(output)재학생_대구한의대 rise_260310_송부.xls"

if __name__ == "__main__":
    results = generate(INPUT, theme="white_clean", sort="desc")
    print(f"\n생성된 파일: {results}")
