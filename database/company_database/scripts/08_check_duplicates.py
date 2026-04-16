# -*- coding: utf-8 -*-
"""
08_check_duplicates.py - 범용 중복업체 검사 모듈 v1.0

판정 기준:
  [중복_확정]  : 회사명(A) + 전화번호(B) + 공장주소(C) 모두 일치
  [중복_예상]  : (A+B) 또는 (A+C) 또는 (B+C) 일치
  [중복_확인필요]: B만 일치 또는 C만 일치
  (A만 일치)   : 동명이인 사업장 빈번 → 판정 제외

결과 컬럼 (한글):
  중복판정    : 판정값 또는 빈칸
  중복_상대nid: 중복 상대 nid 목록 (쉼표 구분)
  중복_근거   : 판정 근거 (예: 회사명+전화+주소일치)
  중복_그룹   : 그룹 식별자 (확정·예상만, 예: G0001)
"""

import re
import sys
import io
from collections import defaultdict

import pandas as pd

if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# ──────────────────────────────────────────
# 정규화 함수
# ──────────────────────────────────────────

# 무효 전화번호 패턴 (특수번호 15XX, 16XX, 18XX)
_SPECIAL_PHONE = re.compile(r'^(15|16|18)\d{2}')
_DIGITS = re.compile(r'\D')

def normalize_phone(raw: str) -> str:
    """
    전화번호에서 숫자만 추출. 빈칸·특수번호·자릿수 부족은 None 반환.
    """
    if not isinstance(raw, str) or not raw.strip():
        return None
    digits = _DIGITS.sub('', raw.strip())
    if len(digits) < 9:
        return None
    if _SPECIAL_PHONE.match(digits):
        return None
    return digits


def normalize_address(raw: str) -> str:
    """
    주소 문자열에서 공백·특수문자를 제거한 정규화 문자열 반환.
    빈칸이면 None 반환.
    """
    if not isinstance(raw, str) or not raw.strip():
        return None
    normalized = re.sub(r'[\s\-(),.\[\]·]', '', raw.strip())
    return normalized if normalized else None


def normalize_name(raw: str) -> str:
    """
    이미 정규화된 회사명_정규화 컬럼을 받아 빈칸 처리.
    """
    if not isinstance(raw, str) or not raw.strip():
        return None
    return raw.strip()


# ──────────────────────────────────────────
# 판정 엔진
# ──────────────────────────────────────────

def judge(a_match: bool, b_match: bool, c_match: bool) -> tuple:
    """
    A(회사명), B(전화), C(주소) 일치 여부로 판정 결과와 근거 반환.
    Returns: (판정문자열 or None, 근거문자열)
    """
    signals = []
    if a_match:
        signals.append('회사명')
    if b_match:
        signals.append('전화')
    if c_match:
        signals.append('주소')

    if a_match and b_match and c_match:
        return '[중복_확정]', '+'.join(signals) + '일치'
    elif (a_match and b_match) or (a_match and c_match) or (b_match and c_match):
        return '[중복_예상]', '+'.join(signals) + '일치'
    elif b_match or c_match:
        return '[중복_확인필요]', '+'.join(signals) + '일치'
    else:
        return None, ''


# ──────────────────────────────────────────
# 메인 검사 함수
# ──────────────────────────────────────────

def check_duplicates(
    df: pd.DataFrame,
    name_col: str = '회사명_정규화',
    phone_col: str = '전화번호',
    addr_col: str = '공장주소',
    nid_col: str = 'nid',
) -> tuple:
    """
    중복업체 검사를 수행하고 결과 컬럼 4개를 추가한 DataFrame과 통계 dict를 반환.

    블록킹 전략:
      - 전화번호 앞 6자리가 같은 쌍끼리만 비교 (지역번호+국번 수준)
      - 또는 공장주소 정규화의 앞 10자 (시군구 수준)로 블록 구성

    Args:
        df: 입력 DataFrame
        name_col: 회사명 정규화 컬럼명
        phone_col: 전화번호 컬럼명
        addr_col: 공장주소 컬럼명
        nid_col: 고유 식별자 컬럼명

    Returns:
        (결과_df, stats_dict)
    """
    n = len(df)
    print(f'[INFO] 중복 검사 시작: {n}행')

    # --- 정규화 벡터 준비 ---
    has_name  = name_col in df.columns
    has_phone = phone_col in df.columns
    has_addr  = addr_col in df.columns
    has_nid   = nid_col in df.columns

    names  = [normalize_name(v)    for v in (df[name_col]  if has_name  else [''] * n)]
    phones = [normalize_phone(v)   for v in (df[phone_col] if has_phone else [''] * n)]
    addrs  = [normalize_address(v) for v in (df[addr_col]  if has_addr  else [''] * n)]
    nids   = list(df[nid_col] if has_nid else range(n))

    # --- 결과 저장용 ---
    dup_type_list   = [''] * n
    dup_nid_list    = [''] * n
    dup_reason_list = [''] * n
    dup_group_list  = [''] * n

    # --- 블록 구성: 전화번호 앞6자리 + 주소 앞10자 ---
    # key → list of row indices
    phone_blocks = defaultdict(list)
    addr_blocks  = defaultdict(list)

    for i in range(n):
        if phones[i]:
            key = phones[i][:6]
            phone_blocks[key].append(i)
        if addrs[i]:
            key = addrs[i][:10]
            addr_blocks[key].append(i)

    # --- 쌍(pair) 수집: 중복 없이 (i < j) ---
    pairs = set()
    for block in phone_blocks.values():
        if len(block) > 1:
            for ii in range(len(block)):
                for jj in range(ii + 1, len(block)):
                    pairs.add((block[ii], block[jj]))
    for block in addr_blocks.values():
        if len(block) > 1:
            for ii in range(len(block)):
                for jj in range(ii + 1, len(block)):
                    pairs.add((block[ii], block[jj]))

    print(f'[INFO] 비교 쌍 수: {len(pairs):,}')

    # --- 판정 ---
    # 관계 저장: idx → list of (상대idx, 판정, 근거)
    relations = defaultdict(list)

    for i, j in pairs:
        a = bool(names[i]  and names[i]  == names[j])
        b = bool(phones[i] and phones[i] == phones[j])
        c = bool(addrs[i]  and addrs[i]  == addrs[j])

        verdict, reason = judge(a, b, c)
        if verdict:
            relations[i].append((j, verdict, reason))
            relations[j].append((i, verdict, reason))

    # --- 그룹 할당 (Union-Find 방식으로 연결 컴포넌트 묶기) ---
    # 확정·예상만 같은 그룹으로 묶기
    parent = list(range(n))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(x, y):
        px, py = find(x), find(y)
        if px != py:
            parent[px] = py

    for i, rels in relations.items():
        for j, verdict, _ in rels:
            if verdict in ('[중복_확정]', '[중복_예상]'):
                union(i, j)

    # 각 인덱스의 최강 판정 결정 (확정 > 예상 > 확인필요)
    PRIORITY = {'[중복_확정]': 3, '[중복_예상]': 2, '[중복_확인필요]': 1}

    for i, rels in relations.items():
        best_verdict = None
        best_priority = 0
        reasons = []
        peer_nids = []

        for j, verdict, reason in sorted(rels, key=lambda x: -PRIORITY.get(x[1], 0)):
            prio = PRIORITY.get(verdict, 0)
            if prio > best_priority:
                best_priority = prio
                best_verdict = verdict
            peer_nids.append(str(nids[j]))
            if reason not in reasons:
                reasons.append(reason)

        if best_verdict:
            dup_type_list[i]   = best_verdict
            dup_nid_list[i]    = ', '.join(peer_nids)
            dup_reason_list[i] = '; '.join(reasons)

    # --- 그룹 ID 부여 (확정·예상만) ---
    root_to_gid = {}
    gid_counter = 1
    for i in range(n):
        if dup_type_list[i] in ('[중복_확정]', '[중복_예상]'):
            root = find(i)
            if root not in root_to_gid:
                root_to_gid[root] = f'G{gid_counter:04d}'
                gid_counter += 1
            dup_group_list[i] = root_to_gid[root]

    # --- 결과 컬럼 추가 ---
    result = df.copy()
    result['중복판정']     = dup_type_list
    result['중복_상대nid'] = dup_nid_list
    result['중복_근거']    = dup_reason_list
    result['중복_그룹']    = dup_group_list

    # --- 통계 ---
    cnt_confirmed = sum(1 for v in dup_type_list if v == '[중복_확정]')
    cnt_expected  = sum(1 for v in dup_type_list if v == '[중복_예상]')
    cnt_review    = sum(1 for v in dup_type_list if v == '[중복_확인필요]')
    cnt_normal    = n - cnt_confirmed - cnt_expected - cnt_review

    # 확정 삭제 후 기업수: 각 확정 그룹에서 대표(최솟값 인덱스) 1건만 유지
    confirmed_groups = defaultdict(list)
    for i in range(n):
        if dup_type_list[i] == '[중복_확정]':
            confirmed_groups[dup_group_list[i]].append(i)
    confirmed_remove = set()
    for gid, idxs in confirmed_groups.items():
        for idx in sorted(idxs)[1:]:   # 첫 번째(대표)는 유지, 나머지 제거
            confirmed_remove.add(idx)
    after_confirmed = n - len(confirmed_remove)

    # 예상 삭제 후 기업수: 확정+예상 그룹 모두 처리
    conf_exp_groups = defaultdict(list)
    for i in range(n):
        if dup_type_list[i] in ('[중복_확정]', '[중복_예상]'):
            conf_exp_groups[dup_group_list[i]].append(i)
    conf_exp_remove = set()
    for gid, idxs in conf_exp_groups.items():
        for idx in sorted(idxs)[1:]:
            conf_exp_remove.add(idx)
    after_expected = n - len(conf_exp_remove)

    stats = {
        '전체_기업수':          n,
        '중복_확정':            cnt_confirmed,
        '중복_예상':            cnt_expected,
        '중복_확인필요':         cnt_review,
        '정상':                 cnt_normal,
        '확정삭제후_기업수':      after_confirmed,
        '예상삭제후_기업수':      after_expected,
        '확정_그룹수':           len(confirmed_groups),
        '확정예상_그룹수':        len(conf_exp_groups),
    }

    print(f'[OK] 판정 완료')
    print(f'     중복_확정:     {cnt_confirmed}건')
    print(f'     중복_예상:     {cnt_expected}건')
    print(f'     중복_확인필요: {cnt_review}건')
    print(f'     정상:          {cnt_normal}건')
    print(f'     확정 삭제후 기업수: {after_confirmed}건')
    print(f'     예상 삭제후 기업수: {after_expected}건')

    return result, stats


# ──────────────────────────────────────────
# 단위 테스트
# ──────────────────────────────────────────

if __name__ == '__main__':
    print('=== 08_check_duplicates.py 단위 테스트 ===')

    test_data = {
        'nid': [
            'FC-001', 'FC-002', 'FC-003', 'FC-004',
            'FC-005', 'FC-006', 'FC-007', 'FC-008',
        ],
        '회사명_정규화': [
            '삼성전자',    # 001
            '삼성전자',    # 002 - A만 일치 (정상 예상)
            '삼성전자',    # 003 - A+B 일치
            'LG전자',      # 004
            'LG전자',      # 005 - A+C 일치
            '현대모비스',  # 006
            '현대모비스',  # 007 - B+C 일치
            '한화에어로',  # 008 - 독립
        ],
        '전화번호': [
            '031-200-0001',   # 001
            '031-500-9999',   # 002 - 다름
            '031-200-0001',   # 003 - B 일치 (001과)
            '02-3777-1000',   # 004
            '02-9999-0000',   # 005 - 다름
            '032-571-9100',   # 006
            '032-571-9100',   # 007 - B 일치 (006과)
            '051-328-2400',   # 008
        ],
        '공장주소': [
            '경기도수원시장안구정자동100',   # 001
            '경기도수원시장안구정자동100',   # 002 - C 일치 (001과) → A+C=[중복_예상]
            '부산시해운대구우동200',         # 003
            '서울시강남구역삼동300',         # 004
            '서울시강남구역삼동300',         # 005 - A+C 일치 (004와) → [중복_예상]
            '인천시부평구부평동400',         # 006
            '인천시부평구부평동400',         # 007 - B+C 일치 (006과) → [중복_예상]
            '경남창원시의창구팔용동500',     # 008
        ],
    }

    test_df = pd.DataFrame(test_data)
    result_df, stats = check_duplicates(test_df)

    print()
    print('--- 판정 결과 ---')
    cols = ['nid', '회사명_정규화', '전화번호', '중복판정', '중복_근거', '중복_그룹', '중복_상대nid']
    for _, row in result_df[cols].iterrows():
        print(f"  {row['nid']} | {row['회사명_정규화']:8s} | {row['전화번호']:15s} | "
              f"{row['중복판정']:10s} | {row['중복_근거']:20s} | {row['중복_그룹']:6s} | {row['중복_상대nid']}")

    print()
    expected = {
        # FC-001: FC-002와 A+C, FC-003과 A+B 일치 → [중복_예상]
        'FC-001': '[중복_예상]',
        # FC-002: FC-001과 A+C 일치 → [중복_예상]
        'FC-002': '[중복_예상]',
        # FC-003: FC-001과 A+B 일치 → [중복_예상] (A+B는 예상 조건)
        'FC-003': '[중복_예상]',
        # FC-004: FC-005와 A+C 일치 → [중복_예상]
        'FC-004': '[중복_예상]',
        # FC-005: FC-004와 A+C 일치 → [중복_예상]
        'FC-005': '[중복_예상]',
        # FC-006: FC-007과 A+B+C 모두 일치 → [중복_확정]
        'FC-006': '[중복_확정]',
        # FC-007: FC-006과 A+B+C 모두 일치 → [중복_확정]
        'FC-007': '[중복_확정]',
        'FC-008': '',
    }
    print('--- 자동 검증 ---')
    all_pass = True
    for _, row in result_df.iterrows():
        nid = row['nid']
        ex = expected.get(nid, '')
        got = row['중복판정']
        ok = (ex == got)
        if not ok:
            all_pass = False
        print(f"  {nid}: 예상={ex!r:20s} 실제={got!r:20s} {'[OK]' if ok else '[FAIL]'}")
    print()
    print(f'통계: {stats}')
    print(f"\n{'[ALL PASS]' if all_pass else '[일부 실패 있음]'}")
