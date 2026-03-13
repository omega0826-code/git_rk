# -*- coding: utf-8 -*-
RULE = {"chart_type": "radar", "priority": 15, "builder_method": "add_radar"}

RADAR_KEYWORDS = ['인식 수준', '평균 점수', '만족도 평균', '역량 수준']

def match(title, labels, pcts, freqs, n, **kwargs):
    if any(kw in title for kw in RADAR_KEYWORDS):
        return True
    return False
