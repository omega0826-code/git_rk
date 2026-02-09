# -*- coding: utf-8 -*-
"""
01_preprocess.py
인터뷰 데이터 전처리 + 텍스트 코딩
"""
import pandas as pd
import re
import os

# ── 경로 설정 ──
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC  = os.path.join(BASE, "(csv)interview_0209.csv")
OUT  = os.path.join(BASE, "output")
os.makedirs(OUT, exist_ok=True)

# ── 1. 데이터 로딩 ──
print("[1] 데이터 로딩...")
df = pd.read_csv(SRC, encoding="utf-8")
df = df.dropna(how="all")
print(f"    원본 행 수: {len(df)}")

# ── 2. 분석 대상 컬럼 정의 ──
META_COLS = ["순번", "업체명", "근로자수(명)", "규모", "업종", "업종 상세", "사업체 유형"]
Q_COLS = ["Q1", "Q2", "Q3", "Q3_1", "Q3_2", "Q4", "Q5", "Q6", "Q7", "Q7_1", "Q7_2", "Q8", "Q_ETC"]

# ── 3. 텍스트 정제 ──
print("[2] 텍스트 정제...")
def clean_text(val):
    if pd.isna(val):
        return ""
    s = str(val)
    s = s.replace("\r\n", "\n").replace("\r", "\n")
    s = re.sub(r'\n+', '\n', s)
    s = s.strip()
    return s

for col in Q_COLS:
    if col in df.columns:
        df[col] = df[col].apply(clean_text)

# ── 4. 전처리 결과 저장 ──
preprocessed_path = os.path.join(OUT, "preprocessed.csv")
df.to_csv(preprocessed_path, index=False, encoding="utf-8-sig")
print(f"    → {preprocessed_path} 저장 완료 ({len(df)}행)")

# ── 5. 텍스트 코딩 (오픈코딩 + 범주화) ──
print("[3] 텍스트 코딩 시작...")

# 각 문항별 키워드 사전 정의
CODING_RULES = {
    "Q1": {
        "오후(13~17시)": ["오후", "13시", "14시", "15시", "16시", "17시", "점심 이후", "1시", "2시", "3시", "4시", "5시"],
        "오전": ["오전", "10시", "11시", "9시"],
        "퇴근 후(18시 이후)": ["퇴근", "18시", "19시", "야간", "저녁"],
        "주말": ["주말", "토요일", "일요일"],
        "상관없음": ["상관없", "무관", "언제든", "자유"],
        "연초·연말 회피": ["연초", "연말", "12월", "1월", "2월"],
        "월요일 회피": ["월요일"],
        "평일": ["평일"],
        "온라인": ["온라인"],
    },
    "Q2": {
        "시간 확보 어려움": ["시간", "근무시간", "업무시간", "근무 중"],
        "대체 인력 부족": ["대체", "인력", "인원"],
        "교육 콘텐츠 부적합": ["콘텐츠", "내용", "커리큘럼", "맞춤"],
        "직원 참여도 저조": ["참여", "관심", "독려", "의욕"],
        "비용 문제": ["비용", "자부담", "유료"],
        "교통·접근성": ["교통", "이동", "거리", "접근"],
        "정보 부족": ["정보", "홍보", "안내"],
    },
    "Q3": {
        "반복 수강함": ["반복", "재수강", "다시", "매년", "정기"],
        "반복 수강 안 함": ["안 함", "않음", "없음", "아님", "안함"],
        "의무교육만": ["의무", "법정", "안전교육", "보건"],
    },
    "Q4": {
        "안전·보건": ["안전", "보건", "산업안전", "보호"],
        "인사·노무": ["인사", "노무", "인적", "근로", "노동"],
        "법규·규정": ["법규", "법령", "규정", "규제", "세무"],
        "품질·생산": ["품질", "생산", "공정", "제조"],
        "직무역량": ["직무", "역량", "스킬", "실무"],
        "리더십·관리": ["리더십", "관리자", "경영", "조직"],
    },
    "Q5": {
        "자격증 지원": ["자격증", "자격", "면허"],
        "현장 맞춤형": ["현장", "맞춤", "실습"],
        "직무전환 교육": ["전환", "전직", "재취업"],
        "컨설팅 연계": ["컨설팅", "진단"],
        "없음·모름": ["없", "모르", "따로"],
    },
    "Q6": {
        "AI 적용 중": ["적용", "사용", "도입", "활용 중"],
        "AI 미적용": ["미적용", "도입 전", "아직", "없"],
        "AI 교육 희망": ["교육", "배우", "관심", "희망"],
        "ChatGPT": ["챗gpt", "chatgpt", "gpt", "챗봇"],
        "자동화": ["자동화", "자동", "RPA"],
    },
    "Q7": {
        "온+오프 혼합": ["온.*오프", "블렌디드", "혼합", "병행"],
        "오프라인 선호": ["오프라인", "대면", "집합"],
        "온라인 선호": ["온라인", "비대면"],
    },
    "Q8": {
        "데이터·AI 기초": ["데이터", "AI", "인공지능", "빅데이터"],
        "디지털 기초": ["디지털", "컴퓨터", "IT"],
        "보안·개인정보": ["보안", "개인정보", "정보보호"],
        "업무자동화": ["자동화", "엑셀", "문서", "OA", "ERP"],
        "스마트팩토리": ["스마트", "팩토리", "IoT", "MES"],
    },
}

# 코딩 테이블 생성
coding_records = []
for idx, row in df.iterrows():
    for q_col in Q_COLS:
        text = str(row.get(q_col, ""))
        if not text.strip():
            coding_records.append({
                "순번": row["순번"],
                "업체명": row["업체명"],
                "규모": row["규모"],
                "업종": row["업종"],
                "문항": q_col,
                "원문": "",
                "코딩_키워드": "",
                "코딩_범주": "",
            })
            continue

        if q_col in CODING_RULES:
            matched_cats = []
            matched_kws = []
            for category, keywords in CODING_RULES[q_col].items():
                for kw in keywords:
                    if re.search(kw, text, re.IGNORECASE):
                        if category not in matched_cats:
                            matched_cats.append(category)
                            matched_kws.append(kw)
                        break

            coding_records.append({
                "순번": row["순번"],
                "업체명": row["업체명"],
                "규모": row["규모"],
                "업종": row["업종"],
                "문항": q_col,
                "원문": text[:200],
                "코딩_키워드": " | ".join(matched_kws) if matched_kws else "(미분류)",
                "코딩_범주": " | ".join(matched_cats) if matched_cats else "(미분류)",
            })
        else:
            # Q3_1, Q3_2, Q7_1, Q7_2, Q_ETC 등은 원문만 기록
            coding_records.append({
                "순번": row["순번"],
                "업체명": row["업체명"],
                "규모": row["규모"],
                "업종": row["업종"],
                "문항": q_col,
                "원문": text[:200],
                "코딩_키워드": "(원문 참조)",
                "코딩_범주": "(원문 참조)",
            })

coding_df = pd.DataFrame(coding_records)
coding_path = os.path.join(OUT, "coding_table.csv")
coding_df.to_csv(coding_path, index=False, encoding="utf-8-sig")
print(f"    → {coding_path} 저장 완료 ({len(coding_df)}행)")

# ── 6. 요약 통계 ──
print("\n[4] 요약 통계")
print(f"    전체 기업: {len(df)}개")
print(f"    업종 분포: {dict(df['업종'].value_counts())}")
print(f"    규모 분포: {dict(df['규모'].value_counts())}")
print(f"    코딩 테이블 행 수: {len(coding_df)}")
print(f"    문항별 코딩 수:")
for q in Q_COLS:
    sub = coding_df[coding_df["문항"] == q]
    coded = sub[~sub["코딩_범주"].isin(["", "(미분류)", "(원문 참조)"])]
    print(f"      {q}: {len(coded)}/{len(sub)} 코딩 완료")

print("\n완료!")
