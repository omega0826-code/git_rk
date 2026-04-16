# -*- coding: utf-8 -*-
"""
09_remove_duplicates.py - 중복업체 삭제 모듈 v1.0

삭제 모드: 확정+예상 (all) — 두 판정 유형 모두 그룹 내 대표 1건만 유지

대표 선정 우선순위:
  1. 원천자료 컬럼에 '기존자료' 포함 행 (절대 보호)
  2. 회사명_정규화 값이 있는 행
  3. 전화번호 유효한 행 (숫자 9자리+)
  4. 공장주소 문자열이 긴 행
  5. nid 오름차순 (가장 먼저 등록된 행)

규칙:
  - '기존자료' 행은 절대 삭제하지 않음 → 같은 그룹의 비기존자료만 삭제
  - [중복_확인필요]는 자동 삭제 대상 제외

산출물:
  (정상_df, 중복삭제_df, stats_dict)
  - 중복삭제_df의 행에는 '삭제사유' 컬럼에 [삭제:중복] 태그 부여
"""

import sys
import io
import re
import pandas as pd
from collections import defaultdict

if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# ──────────────────────────────────────────
# 상수
# ──────────────────────────────────────────
REMOVE_TYPES   = {'[중복_확정]', '[중복_예상]'}   # 자동 삭제 대상 판정 유형
_DIGITS        = re.compile(r'\D')


def _is_legacy(row, source_col='원천자료') -> bool:
    """원천자료 컬럼에 '기존자료' 문자열이 포함되면 True."""
    val = row.get(source_col, '')
    if pd.isna(val):
        return False
    return '기존자료' in str(val)


def _phone_valid(val) -> bool:
    """전화번호가 유효하면 True (숫자 9자리 이상)."""
    if pd.isna(val) or not str(val).strip():
        return False
    digits = _DIGITS.sub('', str(val))
    return len(digits) >= 9


def _score_row(row, source_col='원천자료',
               name_col='회사명_정규화', phone_col='전화번호', addr_col='공장주소') -> tuple:
    """
    우선순위 점수를 내림차순 정렬용 튜플로 반환.
    튜플 값이 클수록 대표로 선정될 가능성 높음.
    """
    is_legacy  = int(_is_legacy(row, source_col))                                    # 1순위
    has_name   = int(bool(str(row.get(name_col, '') or '').strip()))                 # 2순위
    has_phone  = int(_phone_valid(row.get(phone_col, '')))                           # 3순위
    addr_len   = len(str(row.get(addr_col, '') or '').strip())                       # 4순위
    return (is_legacy, has_name, has_phone, addr_len)


def select_representative(group_df: pd.DataFrame,
                           source_col='원천자료',
                           name_col='회사명_정규화',
                           phone_col='전화번호',
                           addr_col='공장주소',
                           nid_col='nid') -> pd.Index:
    """
    그룹 내에서 대표 행 인덱스를 반환하고,
    삭제 대상 인덱스 목록도 반환.

    Returns:
        (대표_idx, 삭제_idx_list)
    """
    scored = []
    for idx in group_df.index:
        row   = group_df.loc[idx]
        score = _score_row(row, source_col, name_col, phone_col, addr_col)
        nid   = str(row.get(nid_col, idx))
        scored.append((score, nid, idx))

    # 점수 내림차순 → nid 오름차순 (동점 처리)
    scored.sort(key=lambda x: (-x[0][0], -x[0][1], -x[0][2], -x[0][3], x[1]))

    rep_idx    = scored[0][2]
    delete_idx = [s[2] for s in scored[1:]]
    return rep_idx, delete_idx


# ──────────────────────────────────────────
# 메인 삭제 함수
# ──────────────────────────────────────────

def remove_duplicates(
    df: pd.DataFrame,
    dup_type_col: str = '중복판정',
    group_col:    str = '중복_그룹',
    source_col:   str = '원천자료',
    name_col:     str = '회사명_정규화',
    phone_col:    str = '전화번호',
    addr_col:     str = '공장주소',
    nid_col:      str = 'nid',
) -> tuple:
    """
    중복 판정 결과를 바탕으로 확정+예상 그룹에서 대표 1건만 유지하고
    나머지를 삭제 처리합니다.

    기존자료('기존자료' 포함) 행은 절대 삭제하지 않습니다.

    Args:
        df: 08_check_duplicates.check_duplicates() 결과 DataFrame
            (중복판정, 중복_그룹 컬럼 포함)

    Returns:
        (정상_df, 중복삭제_df, stats_dict)
    """
    n = len(df)
    print(f'[INFO] 중복 삭제 시작: {n}행 (모드: 확정+예상)')

    # 삭제 대상 그룹 수집
    target_mask = df[dup_type_col].isin(REMOVE_TYPES) if dup_type_col in df.columns else pd.Series(False, index=df.index)
    group_col_exists = group_col in df.columns

    # 그룹별 인덱스 수집
    groups = defaultdict(list)
    for idx in df.index:
        if not target_mask[idx]:
            continue
        gid = str(df.at[idx, group_col]) if group_col_exists else ''
        if gid and gid != 'nan':
            groups[gid].append(idx)

    # 삭제 대상 인덱스 수집
    delete_set            = set()
    protected_legacy      = 0   # 기존자료로 인해 대표 선정된 건수
    group_legacy_conflict = 0   # 그룹 내 기존자료 2건 이상인 그룹 수

    for gid, idxs in groups.items():
        if len(idxs) < 2:
            continue

        group_df = df.loc[idxs]

        # 기존자료 행 수 확인
        legacy_rows = [i for i in idxs if _is_legacy(df.loc[i], source_col)]

        if len(legacy_rows) >= 2:
            group_legacy_conflict += 1

        rep_idx, del_idxs = select_representative(
            group_df, source_col, name_col, phone_col, addr_col, nid_col
        )

        # 기존자료 보호: del_idxs 중 기존자료 행 제거 (절대 삭제 안 함)
        protected = [i for i in del_idxs if _is_legacy(df.loc[i], source_col)]
        actual_del = [i for i in del_idxs if i not in protected]

        if rep_idx in legacy_rows or (not legacy_rows):
            if df.at[rep_idx, source_col] if source_col in df.columns else False:
                if _is_legacy(df.loc[rep_idx], source_col):
                    protected_legacy += 1

        delete_set.update(actual_del)

    # 결과 분리
    delete_mask = df.index.isin(delete_set)
    normal_df   = df[~delete_mask].copy()
    deleted_df  = df[delete_mask].copy()

    # 삭제사유 부여
    reasons = []
    for idx in deleted_df.index:
        판정  = deleted_df.at[idx, dup_type_col] if dup_type_col in deleted_df.columns else ''
        그룹  = deleted_df.at[idx, group_col]    if group_col    in deleted_df.columns else ''
        nid_v = deleted_df.at[idx, nid_col]      if nid_col      in deleted_df.columns else str(idx)
        reasons.append(f'[삭제:중복] {판정} - {그룹} 내 {nid_v}의 중복')

    deleted_df['삭제사유'] = reasons

    # 통계
    cnt_confirmed_del = int((deleted_df[dup_type_col] == '[중복_확정]').sum()) if dup_type_col in deleted_df.columns else 0
    cnt_expected_del  = int((deleted_df[dup_type_col] == '[중복_예상]').sum())  if dup_type_col in deleted_df.columns else 0

    stats = {
        '삭제_전_기업수':     n,
        '삭제_후_기업수':     len(normal_df),
        '삭제_건수':          len(deleted_df),
        '확정_삭제':          cnt_confirmed_del,
        '예상_삭제':          cnt_expected_del,
        '기존자료_보호_그룹':  protected_legacy,
        '기존자료_충돌_그룹':  group_legacy_conflict,
        '처리_그룹수':        len(groups),
    }

    print(f'[OK] 삭제 완료')
    print(f'     삭제 전: {n}건')
    print(f'     삭제 후: {len(normal_df)}건 (-{len(deleted_df)}건)')
    print(f'     확정 삭제: {cnt_confirmed_del}건')
    print(f'     예상 삭제: {cnt_expected_del}건')
    print(f'     기존자료 충돌 그룹: {group_legacy_conflict}개')

    return normal_df, deleted_df, stats


# ──────────────────────────────────────────
# 단위 테스트
# ──────────────────────────────────────────

if __name__ == '__main__':
    print('=== 09_remove_duplicates.py 단위 테스트 ===')
    import sys
    sys.path.insert(0, r'd:\git_rk\database\company_database\scripts')
    from importlib import import_module
    dup_mod = import_module('08_check_duplicates')

    test_data = {
        'nid': ['FC-001', 'FC-002', 'FC-003',   # 확정 그룹 (기존자료 없음)
                'FC-004', 'FC-005',              # 예상 그룹 (FC-004=기존자료)
                'FC-006', 'FC-007',              # 예상 그룹 (둘 다 기존자료)
                'FC-008', 'FC-009',              # 확인필요 → 삭제 안 함
                'FC-010'],                       # 정상
        '회사명_정규화': [
            '현대모비스', '현대모비스', '현대모비스',
            'LG전자',     'LG전자',
            '삼성전자',    '삼성전자',
            '기아자동차',  '기아자동차',
            '한화에어로',
        ],
        '전화번호': [
            '032-571-9100', '032-571-9100', '032-571-9100',
            '02-3777-1000', '02-9999-0000',
            '031-200-0001', '031-200-0001',
            '031-200-0001', '031-999-9999',
            '051-328-2400',
        ],
        '공장주소': [
            '인천시부평구부평동400', '인천시부평구부평동400', '인천시부평구부평동400',
            '서울시강남구역삼동300', '서울시강남구역삼동300',
            '경기도수원시정자동100', '경기도수원시정자동100',
            '경기도수원시정자동100', '서울시마포구공덕동200',
            '경남창원시팔용동500',
        ],
        '원천자료': [
            '',    '',    '',                    # 그룹1: 기존자료 없음
            '기존자료(전자)', '',                 # 그룹2: FC-004=기존자료
            '기존자료(전자)', '기존자료(가전IoT)', # 그룹3: 둘 다 기존자료
            '',    '',                           # 그룹4: 확인필요
            '',                                  # 정상
        ],
    }

    test_df = pd.DataFrame(test_data)
    result_df, _ = dup_mod.check_duplicates(test_df, nid_col='nid')

    print()
    print('[중복 탐지 결과]')
    for _, r in result_df[['nid', '회사명_정규화', '중복판정', '중복_그룹']].iterrows():
        print(f"  {r['nid']} | {r['회사명_정규화']:8s} | {r['원천자료'] if '원천자료' in r else '':15s} | {r['중복판정']:15s} | {r['중복_그룹']}")

    normal_df, deleted_df, stats = remove_duplicates(result_df)

    print()
    print('[삭제 결과]')
    print(f'  정상: {len(normal_df)}건 / 삭제: {len(deleted_df)}건')
    print()

    # 검증
    cases = {
        # 그룹1 (확정, 기존자료 없음): FC-001 대표 유지, FC-002·003 삭제
        'FC-001': '유지',
        'FC-002': '삭제',
        'FC-003': '삭제',
        # 그룹2 (예상, FC-004=기존자료): FC-004 반드시 유지, FC-005 삭제
        'FC-004': '유지',
        'FC-005': '삭제',
        # 그룹3 (예상, 둘 다 기존자료): 우선순위 따라 1건 유지 1건 삭제
        'FC-006': '유지',   # 회사명 동일, 전화 동일, nid 오름차순 → FC-006 대표
        'FC-007': '삭제',
        # 그룹4 (확인필요): 모두 유지
        'FC-008': '유지',
        'FC-009': '유지',
        # 정상
        'FC-010': '유지',
    }

    normal_nids  = set(normal_df['nid'])
    deleted_nids = set(deleted_df['nid'])
    all_pass = True
    print('[자동 검증]')
    for nid, expected in cases.items():
        if expected == '유지':
            ok = nid in normal_nids
        else:
            ok = nid in deleted_nids
        if not ok:
            all_pass = False
        print(f"  {nid}: 예상={expected} {'[OK]' if ok else '[FAIL]'}")

    print()
    print(f'통계: {stats}')
    print(f"\n{'[ALL PASS]' if all_pass else '[일부 실패]'}")
