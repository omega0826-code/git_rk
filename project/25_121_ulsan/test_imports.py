#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
간단한 테스트: 라이브러리 import 확인
"""

print("=== 라이브러리 확인 시작 ===")

try:
    import pdfplumber
    print(f"✓ pdfplumber 버전: {pdfplumber.__version__}")
except ImportError as e:
    print(f"✗ pdfplumber 없음: {e}")
    print("  설치 명령: pip install pdfplumber")

try:
    import openpyxl
    print(f"✓ openpyxl 버전: {openpyxl.__version__}")
except ImportError as e:
    print(f"✗ openpyxl 없음: {e}")
    print("  설치 명령: pip install openpyxl")

print("\n=== 확인 완료 ===")
