import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False
import os
import re
from collections import Counter

# Configuration
FILE_PATH = r'd:\git_rk\project\25_124_interviiew\data\(CSV)interview_data_260121.csv'
REPORT_DIR = r'd:\git_rk\project\25_124_interviiew\REPORT'
IMAGE_DIR = os.path.join(REPORT_DIR, 'images')

if not os.path.exists(IMAGE_DIR):
    os.makedirs(IMAGE_DIR)

# Column Mapping based on coloumn.md
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
    if pd.isna(text):
        return ""
    # Remove excessive newlines and spaces
    text = re.sub(r'\s+', ' ', str(text)).strip()
    return text

def extract_keywords(texts, top_n=10):
    words = []
    # Simplified keyword extraction using space split (can be improved with NLP if needed)
    # Removing common Korean particles/stop words manually
    stopwords = ['교육', '및', '위한', '통해', '있는', '있습니다', '하는', '하여', '내용', '위해', '관한', '대해', '관련', '그렇다', '아니오', '매우', '등']
    for text in texts:
        if not text: continue
        # Simple split by whitespace and punctuation
        tokens = re.findall(r'\b\w{2,}\b', text) 
        words.extend([w for w in tokens if w not in stopwords])
    return Counter(words).most_common(top_n)

def run_eda():
    print("Starting EDA...")
    # Load data
    try:
        print(f"Loading CSV from {FILE_PATH}...")
        df = pd.read_csv(FILE_PATH, encoding='utf-8')
    except Exception as e:
        print(f"UTF-8 failed, trying CP949: {e}")
        df = pd.read_csv(FILE_PATH, encoding='cp949')
    
    print("Renaming columns...")
    df.rename(columns=COLUMN_MAP, inplace=True)
    
    # Preprocessing
    print("Preprocessing text data...")
    for col in df.columns:
        if df[col].dtype == 'object':
            df[col] = df[col].apply(clean_text)

    analysis_results = []

    # 1. Total Companies
    total_companies = len(df)
    print(f"Total companies: {total_companies}")
    analysis_results.append(f"## 1. 전반적인 현황\n- 분석 대상 업체 수: {total_companies}개\n")

    # 2. Preferred Time (Q1) Analysis
    print("Analyzing Q1...")
    analysis_results.append("## 2. 교육 운영 선호도 (Q1, Q7, Q7_2)")
    time_keywords = extract_keywords(df['PreferredTime'])
    analysis_results.append("### 선호 교육 시간 키워드")
    for kw, count in time_keywords:
        analysis_results.append(f"- {kw}: {count}회")

    # 3. Repeat Intent (Q3, Q3_1, Q3_2)
    print("Analyzing Q3 series...")
    analysis_results.append("\n## 3. 반복 수강 및 강사/기술 영향 (Q3, Q3_1, Q3_2)")
    
    # Simple categorization for binary-like responses
    repeat_yes = df['RepeatIntent'].str.contains('예|그렇다|반복|수강함', na=False).sum()
    analysis_results.append(f"- 반복 수강 의향(긍정): {repeat_yes} / {total_companies}")

    # Visualization: Repeat Intent Impact
    print("Generating visualizations...")
    fig, axes = plt.subplots(1, 2, figsize=(15, 6))
    
    # Instructor Impact
    instructor_count = df['InstructorImpact'].str.contains('예|높아짐|영향|그렇다', na=False).sum()
    instructor_data = [instructor_count, total_companies - instructor_count]
    axes[0].pie(instructor_data, labels=['영향 있음', '영향 적음/없음'], autopct='%1.1f%%', startangle=140, colors=['#ff9999','#66b3ff'])
    axes[0].set_title('강사 변경이 수강 결정에 미치는 영향')

    # Update Impact
    update_count = df['UpdateImpact'].str.contains('예|그렇다|필요|중시', na=False).sum()
    update_data = [update_count, total_companies - update_count]
    axes[1].pie(update_data, labels=['기술 업데이트 중시', '영향 적음/기타'], autopct='%1.1f%%', startangle=140, colors=['#99ff99','#ffcc99'])
    axes[1].set_title('최신 기술/법규 업데이트의 수강 영향')
    
    plt.tight_layout()
    img_path = os.path.join(IMAGE_DIR, 'q3_analysis.png')
    plt.savefig(img_path)
    print(f"Saved visualization to {img_path}")
    analysis_results.append("\n![반복수강 영향 분석](./images/q3_analysis.png)")

    # 4. Pain Points & Support Needs (Q2, Q5)
    print("Analyzing Q2, Q5...")
    analysis_results.append("\n## 4. 애로사항 및 지원 필요사항 (Q2, Q5)")
    pain_keywords = extract_keywords(df['PainPoints'])
    support_keywords = extract_keywords(df['AdditionalSupport'])
    
    analysis_results.append("### 주요 애로사항")
    for kw, count in pain_keywords:
        analysis_results.append(f"- {kw}: {count}회")
    
    # 5. AI Use Cases (Q6)
    print("Analyzing Q6, Q8...")
    analysis_results.append("\n## 5. AI 적용 분야 및 교육 수요 (Q6, Q8)")
    ai_keywords = extract_keywords(df['AIUseCases'])
    digital_keywords = extract_keywords(df['DigitalCurriculum'])
    
    analysis_results.append("### AI 적용 희망 분야")
    for kw, count in ai_keywords:
        analysis_results.append(f"- {kw}: {count}회")

    # Final Report Synthesis
    report_path = os.path.join(REPORT_DIR, 'EDA_Report_260205.md')
    print(f"Writing report to {report_path}...")
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write("# 울산지역 기업 재직자 교육(AI/디지털) 수요조사 EDA 분석 보고서\n\n")
        f.write("\n".join(analysis_results))
    
    print("EDA completed successfully.")
    
    print("EDA completed and report generated at:", os.path.join(REPORT_DIR, 'EDA_Report_260205.md'))

if __name__ == "__main__":
    run_eda()
