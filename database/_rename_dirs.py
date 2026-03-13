# -*- coding: utf-8 -*-
"""디렉토리 및 파일 리네이밍 스크립트"""
import os

BASE = r"d:\git_rk\database"

renames = [
    (os.path.join(BASE, "company database", "raw data", "factory on"), 
     os.path.join(BASE, "company database", "raw data", "factory_on")),
    (os.path.join(BASE, "company database", "raw data"),
     os.path.join(BASE, "company database", "raw_data")),
    (os.path.join(BASE, "company database"),
     os.path.join(BASE, "company_database")),
    (os.path.join(BASE, "statistical classification"),
     os.path.join(BASE, "statistical_classification")),
    (os.path.join(BASE, "project", "Paju Industrial Complex Demand Survey", "company list", "raw data"),
     os.path.join(BASE, "project", "Paju Industrial Complex Demand Survey", "company list", "raw_data")),
    (os.path.join(BASE, "project", "Paju Industrial Complex Demand Survey", "company list"),
     os.path.join(BASE, "project", "Paju Industrial Complex Demand Survey", "company_list")),
    (os.path.join(BASE, "project", "Paju Industrial Complex Demand Survey"),
     os.path.join(BASE, "project", "Paju_Industrial_Complex_Demand_Survey")),
    (os.path.join(BASE, "project", "Daegu University of Korean Medicine"),
     os.path.join(BASE, "project", "Daegu_University_of_Korean_Medicine")),
    (os.path.join(BASE, "project", "Survey on the Supply and Demand of Personnel", "company list"),
     os.path.join(BASE, "project", "Survey on the Supply and Demand of Personnel", "company_list")),
    (os.path.join(BASE, "project", "Survey on the Supply and Demand of Personnel"),
     os.path.join(BASE, "project", "Survey_on_the_Supply_and_Demand_of_Personnel")),
]

file_renames = [
    (os.path.join(BASE, "project", "Paju_Industrial_Complex_Demand_Survey", "Industries Located in Paju General Industrial Complex.csv"),
     os.path.join(BASE, "project", "Paju_Industrial_Complex_Demand_Survey", "Industries_Located_in_Paju_General_Industrial_Complex.csv")),
    (os.path.join(BASE, "project", "Survey_on_the_Supply_and_Demand_of_Personnel", "Confirmed company List_260305.csv"),
     os.path.join(BASE, "project", "Survey_on_the_Supply_and_Demand_of_Personnel", "Confirmed_company_List_260305.csv")),
]

recycle_bin = os.path.join(BASE, ".recycle bin")

print("=== DIR RENAME ===")
for old, new in renames:
    if os.path.exists(old):
        try:
            os.rename(old, new)
            print(f"  OK: {os.path.basename(old)} -> {os.path.basename(new)}")
        except Exception as e:
            print(f"  FAIL: {os.path.basename(old)} -> {e}")
    elif os.path.exists(new):
        print(f"  SKIP: {os.path.basename(new)}")
    else:
        print(f"  MISS: {old}")

print("\n=== FILE RENAME ===")
for old, new in file_renames:
    if os.path.exists(old):
        try:
            os.rename(old, new)
            print(f"  OK: {os.path.basename(old)} -> {os.path.basename(new)}")
        except Exception as e:
            print(f"  FAIL: {os.path.basename(old)} -> {e}")
    elif os.path.exists(new):
        print(f"  SKIP: {os.path.basename(new)}")
    else:
        print(f"  MISS: {old}")

print("\n=== RECYCLE BIN ===")
if os.path.exists(recycle_bin):
    try:
        os.rmdir(recycle_bin)
        print("  OK: deleted")
    except Exception as e:
        print(f"  FAIL: {e}")
else:
    print("  SKIP: gone")

print("\n=== TMP FILES ===")
for f in ["tmp_check.py"]:
    p = os.path.join(BASE, f)
    if os.path.exists(p):
        os.remove(p)
        print(f"  OK: {f}")
    else:
        print(f"  SKIP: {f}")

# Check for tmp files in company_database after rename
for f in ["tmp_pivot.py", "tmp_pivot2.py"]:
    p = os.path.join(BASE, "company_database", f)
    if os.path.exists(p):
        os.remove(p)
        print(f"  OK: {f}")
    else:
        print(f"  SKIP: {f}")

print("\nDone!")
