# -*- coding: utf-8 -*-
import csv, os, glob

CSV_DIR = r"d:\git_rk\project\25_124_interviiew\260209\REPORT\csv_tables"

for fp in glob.glob(os.path.join(CSV_DIR, "*.csv")):
    with open(fp, "r", encoding="utf-8-sig") as f:
        reader = list(csv.reader(f))
    
    if not reader:
        continue
    
    header = reader[0]
    # Find column indices to KEEP (not ending with _비율)
    keep_idx = [i for i, h in enumerate(header) if not h.endswith("_비율")]
    
    # Clean header: remove _기업수 suffix
    new_header = [header[i].replace("_기업수", "") for i in keep_idx]
    
    # Filter all rows
    new_rows = [new_header]
    for row in reader[1:]:
        new_rows.append([row[i] if i < len(row) else "" for i in keep_idx])
    
    with open(fp, "w", encoding="utf-8-sig", newline="") as f:
        csv.writer(f).writerows(new_rows)
    
    print(f"OK: {os.path.basename(fp)}  ({len(header)} cols -> {len(new_header)} cols)")

print("Done!")
