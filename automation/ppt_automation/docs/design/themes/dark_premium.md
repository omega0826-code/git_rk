# 🎨 테마: Dark Premium

> **상위 문서**: [chart_design_master.md](../chart_design_master.md)
> 이 파일은 **색상·배경·장식만** 정의합니다. 레이아웃/라벨/축 규칙은 마스터 참조.

---

## 배경

| 항목          | 값                                                |
| ------------- | ------------------------------------------------- |
| 슬라이드 배경 | `#1B2A4A` (진남색)                                |
| 장식 요소     | 상단 악센트 바 (`#3B82F6`, 0.06"), 좌측 악센트 바 |

---

## 텍스트 색상

| 용도         | HEX       | RGB           | 설명        |
| ------------ | --------- | ------------- | ----------- |
| 제목         | `#FFFFFF` | (255,255,255) | 흰색        |
| 데이터 라벨  | `#CBD5E1` | (203,213,225) | 밝은 회색   |
| 보조 텍스트  | `#94A3B8` | (148,163,184) | 중간 회색   |
| 축선/구분선  | `#334E7A` | (51,78,122)   | 어두운 파란 |
| 파이 내 라벨 | `#FFFFFF` | (255,255,255) | 흰색        |

---

## 차트 팔레트 (동일 10색)

White Clean과 동일 — 어두운 배경에서 더 선명하게 보임

---

## 코드 적용

```python
@dataclass
class Theme:
    accent:  Tuple = (0x3B, 0x82, 0xF6)
    accent2: Tuple = (0x10, 0xB9, 0x81)
    accent3: Tuple = (0xF5, 0x9E, 0x0B)
    accent4: Tuple = (0x8B, 0x5C, 0xF6)
    accent5: Tuple = (0xEF, 0x44, 0x44)
    black:      Tuple = (0xFF, 0xFF, 0xFF)   # ← 제목/축 (흰색)
    dark:       Tuple = (0xCB, 0xD5, 0xE1)   # ← 라벨
    gray:       Tuple = (0x94, 0xA3, 0xB8)   # ← 보조
    light_gray: Tuple = (0x33, 0x4E, 0x7A)   # ← 축선
    white:      Tuple = (0x1B, 0x2A, 0x4A)   # ← 값축 투명용 (=배경색)
    font: str = "맑은 고딕"
```

### 장식 추가 (Builder._slide)
```python
def _slide(self):
    s = self.prs.slides.add_slide(self.prs.slide_layouts[6])
    bg = s.background.fill; bg.solid()
    bg.fore_color.rgb = RGBColor(0x1B, 0x2A, 0x4A)
    # 상단 악센트 바
    sh = s.shapes.add_shape(MSO_SHAPE.RECTANGLE,
        Inches(0), Inches(0), self.prs.slide_width, Inches(0.06))
    sh.fill.solid(); sh.fill.fore_color.rgb = T.rgb(T.accent)
    sh.line.fill.background()
    return s
```
