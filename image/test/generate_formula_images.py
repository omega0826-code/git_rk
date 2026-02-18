# -*- coding: utf-8 -*-
"""
수식 이미지 생성 스크립트
- test.md의 코드를 오류 수정하여 실행 가능하게 변환
"""

import matplotlib
matplotlib.use('Agg')  # GUI 없이 이미지 렌더링

import matplotlib.pyplot as plt
from matplotlib import font_manager
import os
import zipfile
from datetime import datetime

# ── 한글 폰트 설정 (koreanize_matplotlib 대신 직접 설정) ──
font_candidates = [
    'Malgun Gothic',    # Windows
    'NanumGothic',      # Linux/Mac
    'AppleGothic',      # Mac
]

font_set = False
for font_name in font_candidates:
    try:
        font_manager.findfont(font_name, fallback_to_default=False)
        plt.rcParams['font.family'] = font_name
        font_set = True
        print(f"폰트 설정 완료: {font_name}")
        break
    except Exception:
        continue

if not font_set:
    print("경고: 한글 폰트를 찾을 수 없습니다. 기본 폰트를 사용합니다.")

plt.rcParams['axes.unicode_minus'] = False

# ── 저장 경로 설정 ──
BASE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'images')

if not os.path.exists(BASE_DIR):
    os.makedirs(BASE_DIR, exist_ok=True)


def save_image(text, filename, is_formula=False, fontsize=18):
    """
    텍스트(수식 또는 설명)를 이미지로 저장하는 함수
    """
    if is_formula:
        # 수식용 설정 (높이 낮게, 글자 크게)
        fig = plt.figure(figsize=(8, 2))
        content = f"${text}$" if not text.strip().startswith("$") else text
        font_size = fontsize + 6
        align = 'center'
        x_pos = 0.5
    else:
        # 변수 설명용 설정 (줄 수에 따라 높이 자동 조절)
        lines = text.count('\n') + 1
        fig = plt.figure(figsize=(12, lines * 0.8 + 0.5))
        content = text
        font_size = fontsize
        align = 'left'
        x_pos = 0.05

    # 텍스트 배치
    plt.text(x_pos, 0.5, content,
             fontsize=font_size,
             ha=align,
             va='center',
             linespacing=1.8)  # 줄간격

    plt.axis('off')  # 축 및 테두리 제거

    save_path = os.path.join(BASE_DIR, filename)

    # 이미지 저장 (여백 최소화, 고해상도)
    plt.savefig(save_path, dpi=300, bbox_inches='tight', pad_inches=0.1)
    plt.close()

    return save_path


def create_zip_archive(file_paths, zip_name):
    """생성된 이미지들을 zip 파일로 압축"""
    zip_path = os.path.join(BASE_DIR, zip_name)
    with zipfile.ZipFile(zip_path, 'w') as zipf:
        for file in file_paths:
            zipf.write(file, os.path.basename(file))
    return zip_path


# ── 실행 로직 ──
if __name__ == '__main__':
    current_time = datetime.now().strftime("%m%d%H%M")
    generated_files = []

    # 1. 가중치(Weighting)
    f1 = r"W_h = \frac{N_h}{n_h}"
    generated_files.append(save_image(f1, f"1_가중치산식_{current_time}.png", is_formula=True))
    print(f"  [1/6] 가중치 산식 이미지 생성 완료")

    d1 = (
        r"$\bullet$ $W_h$: $h$ 대학의 가중치" + "\n" +
        r"$\bullet$ $N_h$: $h$ 대학의 재학생 모집단 수" + "\n" +
        r"$\bullet$ $n_h$: $h$ 대학의 조사 완료 표본 수"
    )
    generated_files.append(save_image(d1, f"2_가중치설명_{current_time}.png"))
    print(f"  [2/6] 가중치 설명 이미지 생성 완료")

    # 2. 총량 추정(Total Estimation)
    f2 = r"\hat{Y} = \sum_{h=1}^{L} \sum_{i=1}^{n_h} w_{hi} \cdot y_{hi}"
    generated_files.append(save_image(f2, f"3_총량추정산식_{current_time}.png", is_formula=True))
    print(f"  [3/6] 총량추정 산식 이미지 생성 완료")

    d2 = (
        r"$\bullet$ $\hat{Y}$: 특정 조건을 충족하는 울산 지역 전체 대학생 추정 규모" + "\n" +
        r"$\bullet$ $L$: 전체 층(대학)의 수 (4개교)" + "\n" +
        r"$\bullet$ $n_h$: $h$ 대학의 표본 수" + "\n" +
        r"$\bullet$ $w_{hi}$: $h$ 대학 $i$ 번째 응답자의 가중치" + "\n" +
        r"$\bullet$ $y_{hi}$: $h$ 대학 $i$ 번째 응답자의 해당 조건 충족 여부 (충족=1, 미충족=0)"
    )
    generated_files.append(save_image(d2, f"4_총량추정설명_{current_time}.png"))
    print(f"  [4/6] 총량추정 설명 이미지 생성 완료")

    # 3. 일자리 수요(Job Demand) 상세 추정
    f3 = r"\hat{D}_k = \sum_{h=1}^{L} \sum_{i=1}^{n_h} w_{hi} \cdot \delta_{hi}(k)"
    generated_files.append(save_image(f3, f"5_일자리수요산식_{current_time}.png", is_formula=True))
    print(f"  [5/6] 일자리수요 산식 이미지 생성 완료")

    d3 = (
        r"$\bullet$ $\hat{D}_k$: 특정 업종(또는 직종) $k$에 대한 지역 내 추정 일자리 수요 인력 총수" + "\n" +
        r"$\bullet$ $L$: 전체 층(대학)의 수 (4개교)" + "\n" +
        r"$\bullet$ $n_h$: $h$ 대학의 표본 수" + "\n" +
        r"$\bullet$ $w_{hi}$: $h$ 대학 $i$ 번째 응답자의 가중치" + "\n" +
        r"$\bullet$ $\delta_{hi}(k)$: $h$ 대학 $i$ 번째 응답자가 조건 $k$를 희망하면 1, 아니면 0"
    )
    generated_files.append(save_image(d3, f"6_일자리수요설명_{current_time}.png"))
    print(f"  [6/6] 일자리수요 설명 이미지 생성 완료")

    # ZIP 파일 생성
    zip_filename = f"수식모음_formula_images_{current_time}.zip"
    zip_path = create_zip_archive(generated_files, zip_filename)

    print(f"\n생성 완료! 파일 경로: {zip_path}")
    print(f"포함된 파일: {[os.path.basename(f) for f in generated_files]}")
