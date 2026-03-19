# -*- coding: utf-8 -*-
import sys, io
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

import pandas as pd

CSV = r"d:\git_rk\data\factory_on\202601\company_list\electronics_iot\260319_1204\company_electronics_iot_employees_10_and_over_F_260319_1204.csv"
df = pd.read_csv(CSV, encoding='utf-8-sig')
print("=== 종업원규모 고유값 ===")
print(df['종업원규모'].value_counts(dropna=False).to_string())
