"""
database 내 rawdata/output 폴더를 root 레벨로 이동하는 스크립트
- rawdata: data/company_database/raw_data/ (스크립트 제외)
- output(company_database): output/company_database/
- output(database): output/database/
- 빈 폴더 삭제
- 원래 위치에 이동 안내 README 생성
"""
import shutil
import os
from pathlib import Path

ROOT = Path(r"d:\git_rk")
DB = ROOT / "database"

def log(msg):
    print(f"  [OK] {msg}")

def move_tree(src: Path, dst: Path, exclude_dirs=None):
    """src 디렉토리의 내용을 dst로 이동 (exclude_dirs는 이동하지 않음)"""
    exclude_dirs = exclude_dirs or []
    if not src.exists():
        print(f"  [SKIP] 소스 없음: {src}")
        return 0
    dst.mkdir(parents=True, exist_ok=True)
    count = 0
    for item in src.iterdir():
        if item.name in exclude_dirs:
            print(f"  [SKIP] 제외: {item}")
            continue
        target = dst / item.name
        if item.is_dir():
            if target.exists():
                # 재귀적으로 병합
                for child in item.rglob("*"):
                    if child.is_file():
                        rel = child.relative_to(item)
                        dest_file = target / rel
                        dest_file.parent.mkdir(parents=True, exist_ok=True)
                        shutil.move(str(child), str(dest_file))
                        count += 1
                # 빈 디렉토리 정리
                shutil.rmtree(str(item), ignore_errors=True)
            else:
                shutil.move(str(item), str(target))
                count += sum(1 for _ in target.rglob("*") if _.is_file())
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(item), str(target))
            count += 1
    return count

def remove_empty_dir(path: Path):
    """빈 디렉토리 삭제"""
    if path.exists() and path.is_dir():
        # 모든 하위가 비어있는지 확인
        files = list(path.rglob("*"))
        has_files = any(f.is_file() for f in files)
        if not has_files:
            shutil.rmtree(str(path), ignore_errors=True)
            log(f"빈 폴더 삭제: {path}")
            return True
    return False

def create_readme(path: Path, content: str):
    """이동 안내 README 생성"""
    path.mkdir(parents=True, exist_ok=True)
    readme = path / "README_이동안내.md"
    readme.write_text(content, encoding="utf-8")
    log(f"안내 파일 생성: {readme}")

print("=" * 60)
print("database rawdata/output → root 이동 시작")
print("=" * 60)

# ===== 1단계: rawdata 이동 (scripts 제외) =====
print("\n[1/3] rawdata 이동 (scripts 제외)")
src1 = DB / "company_database" / "raw_data" / "factory_on"
dst1 = ROOT / "data" / "company_database" / "raw_data" / "factory_on"
n1 = move_tree(src1, dst1, exclude_dirs=["scripts"])
log(f"이동 파일 수: {n1}")

# ===== 2단계: company_database/output 이동 =====
print("\n[2/3] company_database/output 이동")
# 빈 폴더(factory_on/202601) 삭제
empty_dir = DB / "company_database" / "output" / "factory_on"
remove_empty_dir(empty_dir)

# target_extraction 이동
src2 = DB / "company_database" / "output" / "target_extraction"
dst2 = ROOT / "output" / "company_database" / "target_extraction"
n2 = move_tree(src2, dst2)
log(f"이동 파일 수: {n2}")

# ===== 3단계: database/output 이동 =====
print("\n[3/3] database/output 이동")
src3 = DB / "output"
dst3 = ROOT / "output" / "database"
n3 = move_tree(src3, dst3)
log(f"이동 파일 수: {n3}")

# ===== 빈 폴더 정리 =====
print("\n[정리] 빈 폴더 삭제")
for empty_candidate in [
    DB / "company_database" / "raw_data",
    DB / "company_database" / "output",
    DB / "output",
]:
    remove_empty_dir(empty_candidate)

# ===== 이동 안내 README 생성 =====
print("\n[안내] 이동 안내 파일 생성")

readme_content_raw = """# 📁 데이터 이동 안내

이 폴더의 **raw_data** 데이터가 아래 위치로 이동되었습니다.

## 이동 내역

| 원래 경로 | 이동 후 경로 |
|-----------|-------------|
| `database/company_database/raw_data/factory_on/202601/` | `data/company_database/raw_data/factory_on/202601/` |

> **scripts/** 폴더는 이동하지 않고 현재 위치에 유지됩니다.

📅 이동 일시: 2026-03-10
"""

readme_content_output_cd = """# 📁 데이터 이동 안내

이 폴더의 **output** 데이터가 아래 위치로 이동되었습니다.

## 이동 내역

| 원래 경로 | 이동 후 경로 |
|-----------|-------------|
| `database/company_database/output/target_extraction/` | `output/company_database/target_extraction/` |

📅 이동 일시: 2026-03-10
"""

readme_content_output_db = """# 📁 데이터 이동 안내

이 폴더의 **output** 데이터가 아래 위치로 이동되었습니다.

## 이동 내역

| 원래 경로 | 이동 후 경로 |
|-----------|-------------|
| `database/output/20260305/` | `output/database/20260305/` |

📅 이동 일시: 2026-03-10
"""

# raw_data 폴더에 README (scripts가 남아있으므로 raw_data 폴더는 존재)
raw_data_dir = DB / "company_database" / "raw_data"
if raw_data_dir.exists():
    create_readme(raw_data_dir, readme_content_raw)

# company_database/output 폴더에 README
output_cd_dir = DB / "company_database" / "output"
create_readme(output_cd_dir, readme_content_output_cd)

# database/output 폴더에 README
output_db_dir = DB / "output"
create_readme(output_db_dir, readme_content_output_db)

# ===== 결과 요약 =====
print("\n" + "=" * 60)
print("이동 완료!")
print(f"  총 이동 파일: {n1 + n2 + n3}개")
print("=" * 60)

# 이동 후 확인
print("\n[확인] 이동 후 파일 목록:")
for check_dir in [
    ROOT / "data" / "company_database",
    ROOT / "output" / "company_database",
    ROOT / "output" / "database",
]:
    if check_dir.exists():
        files = list(check_dir.rglob("*"))
        file_count = sum(1 for f in files if f.is_file())
        print(f"  {check_dir}: {file_count}개 파일")
