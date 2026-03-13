# -*- coding: utf-8 -*-
"""울산 일자리 미스매치 — 마크다운 기반 차트 생성 예시"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'chart'))

from run_chart import generate

INPUT = r"d:\git_rk\project\25_121_ulsan\output\(OUTPUT)울산 일자리 미스매치_260205_1822.md"

if __name__ == "__main__":
    generate(INPUT, theme="white_clean", sort="both")
