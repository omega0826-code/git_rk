# -*- coding: utf-8 -*-
"""차트 규칙 자동 로드 엔진 — rule_*.py 파일을 플러그인으로 자동 등록"""
import importlib, pathlib


def load_rules():
    rules = []
    for f in pathlib.Path(__file__).parent.glob("rule_*.py"):
        mod = importlib.import_module(f".{f.stem}", package=__package__)
        rules.append({"match": mod.match, **mod.RULE})
    return sorted(rules, key=lambda r: r["priority"])


def detect_chart_type(title, labels, pcts, freqs, n, **kwargs):
    """데이터 특성과 제목을 보고 적합한 차트 유형을 판별"""
    for rule in load_rules():
        if rule["match"](title, labels, pcts, freqs, n, **kwargs):
            return rule["chart_type"], rule["builder_method"]
    return "hbar", "add_hbar"
