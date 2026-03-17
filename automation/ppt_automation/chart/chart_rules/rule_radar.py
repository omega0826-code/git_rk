# -*- coding: utf-8 -*-
RULE = {"chart_type": "radar", "priority": 10, "builder_method": "add_radar"}


def match(title, labels, pcts, freqs, n, **kwargs):
    """제목에 '레이더'가 포함될 때"""
    return '레이더' in title
