
# HTML to Excel Conversion Plan

## Goal Description
Convert `data/075_115800.html` to an Excel file using `html_to_excel.py`. The HTML file contains absolute-positioned text that represents a table. The script parses parsing these coordinates to reconstruct the table structure.

## Proposed Changes
### [HTML Processing]
#### [MODIFY] [html_to_excel.py](file:///d:/git_rk/project/25_121_ulsan/html_to_excel.py)
- Currently, the script exists. I will run it first to check for any errors or incorrect parsing.
- If the column alignment or data extraction is incorrect (especially with the complex headers seen in the HTML), I will adjust the `parse_html_to_table` and `merge_row_cells` functions.
- Specifically, the HTML contains headers for multiple years (2024, 2025, 2026) and sub-columns like "전체 종사자 수" and "향상훈련 수요". The current script headers might need adjustment to match the actual data.

## Verification Plan
### Automated Tests
- Run the script: `python html_to_excel.py`
- Check if `data/075_115800.xlsx` is created.

### Manual Verification
- Open the generated Excel file.
- Compare the data with the visual representation of the HTML file (or the raw text content).
- Check if columns are correctly aligned (Code, Name, Counts for each year).
