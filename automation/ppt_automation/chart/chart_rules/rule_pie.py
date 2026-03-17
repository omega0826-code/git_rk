# -*- coding: utf-8 -*-
RULE = {"chart_type": "pie", "priority": 5, "builder_method": "add_pie"}


def match(title, labels, pcts, freqs, n, **kwargs):
    """항목 2개 이하일 때 파이 차트"""
    if len(labels) <= 2:
        return True
    return False
