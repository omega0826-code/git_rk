# -*- coding: utf-8 -*-
RULE = {"chart_type": "stacked", "priority": 15, "builder_method": "add_stacked"}


def match(title, labels, pcts, freqs, n, **kwargs):
    """제목에 '누적'이 포함될 때"""
    return '누적' in title
