# -*- coding: utf-8 -*-
import sys, io
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

import pandas as pd

f = r'd:\git_rk\data\factory_on\202601\company_list\electronics_iot\260318_1634\company_electronics_iot_employees_10_and_over_F_260318_1634.csv'
df = pd.read_csv(f, encoding='utf-8-sig')
sizes = ['10~29인', '30~99인', '100~299인', '300인 이상']

iot = df[df['가전IoT_예상'].isin(['확정(이전조사)', '확정(KEA추가)', '예상', '모호']) & df['종업원규모'].isin(sizes)].copy()

def get_iot_cat(x):
    x = str(x)
    if '지능형 가전' in x: return '지능형 가전'
    if '홈헬스케어' in x: return '홈헬스케어'
    if '홈네트워크' in x or '주거안전' in x: return '홈네트워크 및 주거안전'
    if '홈에너지' in x: return '홈에너지'
    return '미분류'

iot['IoT_cat'] = iot['예상_근거'].apply(get_iot_cat)
iot['grade'] = iot['가전IoT_예상'].apply(lambda x: '확정' if '확정' in str(x) else x)

cats = ['지능형 가전', '홈헬스케어', '홈네트워크 및 주거안전', '홈에너지']
grades = ['확정', '예상', '모호']

for cat in cats:
    print(f"\n[{cat}]")
    for g in grades:
        sub = iot[(iot['IoT_cat'] == cat) & (iot['grade'] == g)]
        vals = []
        for s in sizes:
            vals.append((sub['종업원규모'] == s).sum())
        total = sum(vals)
        print(f"  {g}: {vals[0]}, {vals[1]}, {vals[2]}, {vals[3]} = {total}")
    # subtotal
    sub_all = iot[iot['IoT_cat'] == cat]
    vals = [(sub_all['종업원규모'] == s).sum() for s in sizes]
    print(f"  소계: {vals[0]}, {vals[1]}, {vals[2]}, {vals[3]} = {sum(vals)}")

# totals
print("\n[합계]")
for g in grades:
    sub = iot[iot['grade'] == g]
    vals = [(sub['종업원규모'] == s).sum() for s in sizes]
    print(f"  {g}: {vals[0]}, {vals[1]}, {vals[2]}, {vals[3]} = {sum(vals)}")
vals = [(iot['종업원규모'] == s).sum() for s in sizes]
print(f"  소계: {vals[0]}, {vals[1]}, {vals[2]}, {vals[3]} = {sum(vals)}")
