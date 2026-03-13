# 빠른 시작 가이드 (3분)

## 1. 설치
```bash
pip install -r requirements.txt
```

## 2. 바로 실행 (차트 폴더에서)
```bash
cd automation/ppt_automation/chart
python run_chart.py --input "data.xls"
```

## 3. 통합 실행 (ppt_automation 폴더에서)
```bash
cd automation/ppt_automation
python run_ppt.py --module chart --input "data.xls"
```

## 4. 테마 변경
```bash
python run_chart.py --input "data.xls" --theme dark_premium
```

## 5. 정렬 옵션
```bash
# 내림차순 정렬
python run_chart.py --input "data.xls" --sort desc

# 원본 순서
python run_chart.py --input "data.xls" --sort original

# 2종 동시 생성
python run_chart.py --input "data.xls" --sort both
```

## 6. 마크다운 입력
```bash
python run_chart.py --input "report.md"
```

## 결과 확인
- 출력 파일: 입력 파일과 같은 폴더에 `*_차트_정렬_YYMMDD_HHMM.pptx` 생성
- 실행 로그: `ppt_automation/logs/` 폴더에 자동 저장
