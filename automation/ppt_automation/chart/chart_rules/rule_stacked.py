# -*- coding: utf-8 -*-
RULE = {"chart_type": "stacked", "priority": 20, "builder_method": "add_stacked"}

STACKED_KEYWORDS = ['대학교별', '대학별', '학교별']

def match(title, labels, pcts, freqs, n, **kwargs):
    if any(kw in title for kw in STACKED_KEYWORDS):
        return True
    return False
