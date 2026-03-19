# -*- coding: utf-8 -*-
import sys, io
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

import pandas as pd
import json

# ========================================
# 파일 로드
# ========================================
f = r'd:\git_rk\data\factory_on\202601\company_list\electronics_iot\260318_1622\company_electronics_iot_employees_10_and_over_F_260318_1622.csv'
df = pd.read_csv(f, encoding='utf-8-sig')
print(f"Total rows: {len(df)}")

# 종업원규모 컬럼 확인
print(f"\n종업원규모 분포:")
print(df['종업원규모'].value_counts().to_string())

# 가전IoT_예상 분포
print(f"\n가전IoT_예상 분포:")
print(df['가전IoT_예상'].value_counts().to_string())

# ========================================
# 전자산업 대분류 매핑
# ========================================
# 대표업종명(대) 기준으로 전자산업 6개 대분류 매핑
print(f"\n대표업종명(대) 분포:")
print(df['대표업종명(대)'].value_counts().to_string())

print(f"\n대표업종명(중) 분포 (상위 20):")
print(df['대표업종명(중)'].value_counts().head(20).to_string())

# 업종_전자산업 컬럼 확인
print(f"\n업종_전자산업 분포:")
if '업종_전자산업' in df.columns:
    print(df['업종_전자산업'].value_counts(dropna=False).head(10).to_string())

# 입지유형 확인
print(f"\n입지유형 분포:")
if '입지유형' in df.columns:
    print(df['입지유형'].value_counts(dropna=False).head(10).to_string())

# ========================================
# 전자산업 할당표 기준 집계
# ========================================
# 전자산업 6대분류: 전자부품, 컴퓨터주변기기, 방송통신장비, 영상음향기기, 측정제어분석기기, 전기장비
# 대표업종명(대) 또는 대표업종명(중)으로 매핑
print("\n" + "="*80)
print("전자산업 업종별-규모별 집계")
print("="*80)

# 대표업종코드(대) 확인
print(f"\n대표업종코드(대) 분포:")
print(df['대표업종코드(대)'].value_counts().head(20).to_string())

# 전자산업 대분류 매핑 (업종코드 기준)
def map_electronics_category(row):
    code = str(row.get('대표업종코드(대)', ''))
    name = str(row.get('대표업종명(대)', ''))
    name_m = str(row.get('대표업종명(중)', ''))
    
    if '전자부품' in name:
        return '전자부품'
    elif '컴퓨터' in name or '컴퓨터' in name_m:
        return '컴퓨터주변기기'
    elif '방송' in name or '통신' in name or '방송' in name_m or '통신' in name_m:
        return '방송통신장비'
    elif '영상' in name or '음향' in name or '영상' in name_m or '음향' in name_m:
        return '영상음향기기'
    elif '측정' in name or '제어' in name or '분석' in name or '측정' in name_m or '제어' in name_m:
        return '측정제어분석기기'
    elif '전기' in name or '장비' in name or '전기' in name_m:
        return '전기장비'
    else:
        return '기타'

df['전자산업_대분류'] = df.apply(map_electronics_category, axis=1)
print(f"\n전자산업_대분류 매핑 결과:")
print(df['전자산업_대분류'].value_counts().to_string())

# 규모 4분류
size_labels = ['10~29인', '30~99인', '100~299인', '300인 이상']
size_map = {
    '10~29인': '10~29인',
    '30~99인': '30~99인',
    '100~299인': '100~299인',
    '300인 이상': '300인 이상',
    '10인 미만': '10인 미만'
}

def map_size(val):
    v = str(val).strip()
    return size_map.get(v, v)

df['규모_4분류'] = df['종업원규모'].apply(map_size)

# 전자산업 크로스탭 (10인 이상만)
df_elec = df[df['규모_4분류'].isin(size_labels)]
print(f"\n전자산업 대상 (10인 이상): {len(df_elec)}")

ct_elec = pd.crosstab(df_elec['전자산업_대분류'], df_elec['규모_4분류'], margins=True)
ct_elec = ct_elec.reindex(columns=['10~29인', '30~99인', '100~299인', '300인 이상', 'All'], fill_value=0)
print("\n전자산업 업종별-규모별 크로스탭:")
print(ct_elec.to_string())

# ========================================
# IoT가전 할당표 기준 집계 (가전IoT_예상 기준)
# ========================================
print("\n" + "="*80)
print("IoT가전 업종별-규모별 집계 (가전IoT_예상 기준)")
print("="*80)

# 가전IoT_예상이 '확정(이전조사)', '확정(KEA추가)', '예상'인 기업만 대상
iot_targets = df[df['가전IoT_예상'].isin(['확정(이전조사)', '확정(KEA추가)', '예상', '모호'])]
print(f"\nIoT가전 관련 기업: {len(iot_targets)}")

# 예상_근거에서 대분류 추출
def extract_iot_category(reason):
    reason = str(reason)
    if '지능형 가전' in reason:
        return '지능형 가전'
    elif '홈헬스케어' in reason:
        return '홈헬스케어'
    elif '홈네트워크' in reason or '주거안전' in reason:
        return '홈네트워크 및 주거안전'
    elif '홈에너지' in reason:
        return '홈에너지'
    else:
        return '미분류'

iot_targets = iot_targets.copy()
iot_targets['IoT_대분류'] = iot_targets['예상_근거'].apply(extract_iot_category)

print(f"\nIoT 대분류 분포:")
print(iot_targets['IoT_대분류'].value_counts().to_string())

# 예상분류 등급별 IoT 대분류
for grade in ['확정(이전조사)', '확정(KEA추가)', '예상', '모호']:
    subset = iot_targets[iot_targets['가전IoT_예상'] == grade]
    print(f"\n  [{grade}] ({len(subset)}건)")
    print(f"  {subset['IoT_대분류'].value_counts().to_string()}")

# 크로스탭
iot_10plus = iot_targets[iot_targets['규모_4분류'].isin(size_labels)]
ct_iot = pd.crosstab(iot_10plus['IoT_대분류'], iot_10plus['규모_4분류'], margins=True)
ct_iot = ct_iot.reindex(columns=['10~29인', '30~99인', '100~299인', '300인 이상', 'All'], fill_value=0)
print(f"\nIoT가전 업종별-규모별 크로스탭 (전체):")
print(ct_iot.to_string())

# 확정+예상만
iot_confirmed = iot_targets[iot_targets['가전IoT_예상'].isin(['확정(이전조사)', '확정(KEA추가)', '예상'])]
iot_10_conf = iot_confirmed[iot_confirmed['규모_4분류'].isin(size_labels)]
ct_iot_conf = pd.crosstab(iot_10_conf['IoT_대분류'], iot_10_conf['규모_4분류'], margins=True)
ct_iot_conf = ct_iot_conf.reindex(columns=['10~29인', '30~99인', '100~299인', '300인 이상', 'All'], fill_value=0)
print(f"\nIoT가전 업종별-규모별 (확정+예상만):")
print(ct_iot_conf.to_string())

# 결과를 JSON으로 저장 (리포트용)
result = {
    'elec_crosstab': ct_elec.to_dict(),
    'iot_crosstab_all': ct_iot.to_dict(),
    'iot_crosstab_confirmed': ct_iot_conf.to_dict()
}

print("\n[DONE]")
