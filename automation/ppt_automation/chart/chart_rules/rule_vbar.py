# -*- coding: utf-8 -*-
RULE = {"chart_type": "vbar", "priority": 100, "builder_method": "add_vbar"}


def match(title, labels, pcts, freqs, n, **kwargs):
    """기본 폴백: 항목 6개 이하일 때 세로막대 차트"""
    return True
