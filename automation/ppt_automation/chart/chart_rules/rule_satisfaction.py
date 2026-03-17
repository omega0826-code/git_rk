# -*- coding: utf-8 -*-
RULE = {"chart_type": "vbar", "priority": 3, "builder_method": "add_vbar"}


def match(title, labels, pcts, freqs, n, **kwargs):
    """제목에 '만족도'가 포함되면 항목 수와 관계없이 세로막대 우선"""
    return '만족도' in title
