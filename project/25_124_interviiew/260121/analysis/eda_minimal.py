import pandas as pd
import os
import re
from collections import Counter

# Configuration
FILE_PATH = r'd:\git_rk\project\25_124_interviiew\data\(CSV)interview_data_260121.csv'
REPORT_DIR = r'd:\git_rk\project\25_124_interviiew\REPORT'
REPORT_FILE = os.path.join(REPORT_DIR, 'EDA_Report_260205_v1.md')

COLUMN_MAP = {
    '순번': 'ID',
    '업체명': 'Company',
    'Q1': 'PreferredTime',
    'Q2': 'PainPoints',
    'Q3': 'RepeatIntent',
    'Q3_1': 'InstructorImpact',
    'Q3_2': 'UpdateImpact',
    'Q4': 'RequiredTopics',
    'Q5': 'AdditionalSupport',
    'Q6': 'AIUseCases',
    'Q7': 'HybridParticipation',
    'Q7_1': 'HybridProsCons',
    'Q7_2': 'PreferredFormat',
    'Q8': 'DigitalCurriculum',
    'Q_ETC': 'Etc'
}

def clean_text(text):
    if pd.isna(text): return ""
    return re.sub(r'\s+', ' ', str(text)).strip()

def extract_keywords(texts, top_n=10):
    words = []
    stopwords = ['교육', '및', '위한', '통해', '있는', '있습니다', '하는', '하여', '내용', '위해', '관한', '대해', '관련', '그렇다', '아니오', '매우', '등']
    for text in texts:
        if not text: continue
        tokens = re.findall(r'\b\w{2,}\b', text) 
        words.extend([w for w in tokens if w not in stopwords])
    return Counter(words).most_common(top_n)

print("Starting Minimal EDA...")
try:
    df = pd.read_csv(FILE_PATH, encoding='utf-8')
except:
    df = pd.read_csv(FILE_PATH, encoding='cp949')

df.rename(columns=COLUMN_MAP, inplace=True)
for col in df.columns:
    if df[col].dtype == 'object':
        df[col] = df[col].apply(clean_text)

results = ["# 울산지역 기업 재직자 교육(AI/디지털) 수요조사 요약 보고서\n"]
results.append(f"## 1. 전반적인 현황\n- 분석 대상 업체 수: {len(df)}개\n")

results.append("## 2. 주요 니즈 및 애로사항")
pain_keywords = extract_keywords(df['PainPoints'])
results.append("### 주요 애로사항 (Q2)")
for kw, count in pain_keywords:
    results.append(f"- {kw}: {count}회")

ai_keywords = extract_keywords(df['AIUseCases'])
results.append("\n### AI 적용 희망 분야 (Q6)")
for kw, count in ai_keywords:
    results.append(f"- {kw}: {count}회")

with open(REPORT_FILE, 'w', encoding='utf-8') as f:
    f.write("\n".join(results))

print(f"Report saved to {REPORT_FILE}")
print("SUCCESS")
