# -*- coding: utf-8 -*-
RULE = {"chart_type": "pie", "priority": 10, "builder_method": "add_pie"}

PIE_KEYWORDS = ['일반현황', '인지 여부', '전반 만족도', '희망 지역', '성별', '학년', '소속 대학', '거주지']

def match(title, labels, pcts, freqs, n, **kwargs):
    if len(labels) <= 6 and 95 <= sum(pcts) <= 105:
        return True
    if any(kw in title for kw in PIE_KEYWORDS):
        return True
    return False
