# -*- coding: utf-8 -*-
"""테스트 런처: 건의사항_종합표.md → HWPX 변환"""
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from md_to_hwpx import convert

input_path = os.path.join(os.path.dirname(__file__), "건의사항_종합표.md")
result = convert(input_path, visible=True)
print(f"결과: {result}")
