# -*- coding: utf-8 -*-
RULE = {"chart_type": "hbar", "priority": 100, "builder_method": "add_hbar"}

def match(title, labels, pcts, freqs, n, **kwargs):
    """기본 폴백: 다른 규칙에 매칭되지 않으면 수평막대로"""
    return True
