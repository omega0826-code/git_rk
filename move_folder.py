import shutil
import pathlib

src = pathlib.Path(r'd:\git_rk\project\Survey_on_the_Supply_and_Demand_of_Personnel')
dst = pathlib.Path(r'd:\git_rk\project\26_supply_demand\data\company_list')

if src.exists():
    print(f"원본 폴더 확인: {src.name}")
    shutil.move(str(src), str(dst))
    print(f"이동 완료: {dst}")
else:
    print(f"원본 폴더를 찾을 수 없습니다: {src}")
