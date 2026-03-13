# HWPX 빌드 트러블슈팅

## 1. mimetype 압축 방식 에러

**증상**: `validate.py` 실행 시 `mimetype should use ZIP_STORED (0), got compress_type=8`

**원인**: `zipfile.ZIP_DEFLATED`로 모든 파일을 일괄 압축하면 mimetype도 압축됨

**해결**:
```python
if name == 'mimetype':
    zout.writestr(name, data, compress_type=zipfile.ZIP_STORED)
```

---

## 2. charPr itemCnt 불일치

**증상**: 한컴오피스에서 파일이 깨지거나 스타일이 적용되지 않음

**원인**: 새 charPr을 추가했으나 `<hh:charProperties itemCnt="N">`을 갱신하지 않음

**해결**: charPr 추가 후 반드시 `itemCnt += 1` 갱신
```python
char_props.set('itemCnt', str(current_cnt + 1))
```

---

## 3. 표 내부 텍스트 잘못 수정

**증상**: 의도하지 않은 표 셀의 텍스트가 변경됨

**원인**: `tree.findall('.//hp:p')` 사용 시 표 안의 문단까지 매칭됨

**해결**: 직접 자식(Direct Child)만 순회
```python
for child in tree:
    tag = etree.QName(child.tag).localname
    if tag == 'p':  # 직접 자식 p만 대상
        ...
```

---

## 4. 문단 삽입 시 인덱스 밀림

**증상**: 삽입 위치가 의도한 곳이 아님 (점점 밀림)

**원인**: 순방향으로 반복하면서 삽입하면 인덱스가 하나씩 밀림

**해결**: 삽입 목록을 수집한 뒤 역순(reversed)으로 처리
```python
for idx, quote, para in reversed(insert_ops):
    parent.insert(para_idx + 1, new_para)
```

---

## 5. XML 네임스페이스 누락

**증상**: `lxml`이 `{None}p` 또는 빈 네임스페이스로 요소를 생성

**원인**: `etree.Element()` 호출 시 `nsmap`을 전달하지 않음

**해결**: 원본 트리의 `nsmap`을 복사하여 새 요소 생성 시 전달
```python
new_p = etree.Element('{...}p', nsmap=tree.nsmap)
```
