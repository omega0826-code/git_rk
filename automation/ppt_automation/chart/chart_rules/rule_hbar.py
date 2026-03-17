# -*- coding: utf-8 -*-
RULE = {"chart_type": "hbar", "priority": 20, "builder_method": "add_hbar"}


def match(title, labels, pcts, freqs, n, **kwargs):
    """항목 6개 이상일 때 가로막대 차트"""
    return len(labels) >= 6
