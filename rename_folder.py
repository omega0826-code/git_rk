import os
import pathlib

project_dir = pathlib.Path(r'd:\git_rk\project')

# Find the folder with & in name
for item in project_dir.iterdir():
    if item.is_dir() and 'supply' in item.name and 'demand' in item.name:
        new_name = '26_supply_demand'
        new_path = project_dir / new_name
        print(f"Found: {item.name}")
        item.rename(new_path)
        print(f"Renamed to: {new_name}")
        break
else:
    print("Target folder not found. Current folders:")
    for item in project_dir.iterdir():
        if item.is_dir():
            print(f"  {item.name}")
