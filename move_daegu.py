import shutil
import os
import pathlib

src = pathlib.Path(r'd:\git_rk\project\Daegu_University_of_Korean_Medicine')
dst = pathlib.Path(r'd:\git_rk\project\26_Korean_Medicine\data\daegu_univ')

if src.exists():
    print(f"Source folder found: {src}")
    # Create parent directory if it doesn't exist
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(str(src), str(dst))
    print(f"Successfully moved to: {dst}")
else:
    print(f"Source folder not found: {src}")
