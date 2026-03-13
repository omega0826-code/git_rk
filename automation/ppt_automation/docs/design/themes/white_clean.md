# 🎨 테마: White Clean (현재 적용)

> **상위 문서**: [chart_design_master.md](../chart_design_master.md)
> 이 파일은 **색상·배경·장식만** 정의합니다. 레이아웃/라벨/축 규칙은 마스터 참조.

---

## 배경

| 항목          | 값               |
| ------------- | ---------------- |
| 슬라이드 배경 | `#FFFFFF` (흰색) |
| 장식 요소     | **없음**         |

---

## 텍스트 색상

| 용도         | HEX       | RGB           | 설명      |
| ------------ | --------- | ------------- | --------- |
| 제목/축      | `#222222` | (34,34,34)    | 거의 검정 |
| 데이터 라벨  | `#333333` | (51,51,51)    | 진회색    |
| 보조 텍스트  | `#666666` | (102,102,102) | 중회색    |
| 축선/구분선  | `#CCCCCC` | (204,204,204) | 연회색    |
| 파이 내 라벨 | `#FFFFFF` | (255,255,255) | 흰색      |

---

## 차트 팔레트 (10색)

| #   | 이름      | HEX       | 미리보기 |
| --- | --------- | --------- | -------- |
| 1   | Blue      | `#3B82F6` | 🔵        |
| 2   | Green     | `#10B981` | 🟢        |
| 3   | Orange    | `#F59E0B` | 🟠        |
| 4   | Purple    | `#8B5CF6` | 🟣        |
| 5   | Red       | `#EF4444` | 🔴        |
| 6   | Cyan      | `#06B6D4` | 🔵        |
| 7   | Tangerine | `#F97316` | 🟠        |
| 8   | Pink      | `#EC4899` | 🩷        |
| 9   | Teal      | `#14B8A6` | 🟢        |
| 10  | Violet    | `#A855F7` | 🟣        |

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
    black:      Tuple = (0x22, 0x22, 0x22)
    dark:       Tuple = (0x33, 0x33, 0x33)
    gray:       Tuple = (0x66, 0x66, 0x66)
    light_gray: Tuple = (0xCC, 0xCC, 0xCC)
    white:      Tuple = (0xFF, 0xFF, 0xFF)
    font: str = "맑은 고딕"
```
