# hwpx_agent

HWPX 문서를 AI 멀티에이전트가 다루기 쉬운 자산 구조로 분해하는 1차 통합 패키지입니다.

현재 범위:

- HWPX 패키지 인벤토리 수집
- `header.xml`, `section*.xml`, `masterpage*.xml`, `content.hpf` 추출
- 문단, 표, 이미지 배치, 이미지 바이너리, 스타일, 페이지 추정 정보 자산화
- 테스트 파일 1건 기준 실행 결과 생성

아직 하지 않는 범위:

- 자산만으로 100% 동일한 새 HWPX 생성
- 오타 검사기 통합
- 완전한 페이지 정합 보장

## 빠른 시작

```powershell
cd D:\git_rk\automation\hwp_automation\hwpx_agent
python run_assetize.py --input D:\git_rk\automation\hwp_automation\test\2023_mei_workforce.hwpx
```

기본 출력 위치:

```text
D:\git_rk\automation\hwp_automation\hwpx_agent\runs\<run_name>\
```
