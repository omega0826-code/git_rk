# PowerShell script - CSV extract + Excel
# Run: powershell -ExecutionPolicy Bypass -File scripts\extract_csv_xlsx.ps1

$ErrorActionPreference = "Continue"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

$base = "d:\git_rk\project\25_124_interviiew\260209\REPORT"
$src = Join-Path $base "00_integrated_report.md"
$outCsv = Join-Path $base "output\csv_tables"
$outXlsx = Join-Path $base "output\분석결과_전체표.xlsx"

if (!(Test-Path $outCsv)) { New-Item -ItemType Directory -Path $outCsv -Force | Out-Null }

$lines = Get-Content $src -Encoding UTF8
Write-Host "[INFO] Lines: $($lines.Count)"

# Parse tables
$tables = @()
$sec = ""
$sub = ""
$i = 0

while ($i -lt $lines.Count) {
    $line = $lines[$i].TrimEnd()
    if ($line -match "^## ") { $sec = $line -replace "^#+\s*", "" }
    elseif ($line -match "^### ") { $sub = $line -replace "^#+\s*", "" }
    elseif ($line -match "^#### ") { $sub = $line -replace "^#+\s*", "" }
    
    if ($line -match "^\|" -and $line -match "\|.*\|") {
        $tl = @()
        $title = if ($sub) { $sub } else { $sec }
        while ($i -lt $lines.Count -and $lines[$i].TrimEnd() -match "^\|") {
            $tl += $lines[$i].TrimEnd()
            $i++
        }
        if ($tl.Count -ge 3) {
            $tables += [PSCustomObject]@{ Title = $title; Lines = $tl }
        }
        continue
    }
    $i++
}

Write-Host "[INFO] Tables: $($tables.Count)"

function ConvertTo-Rows($tl) {
    $rows = @()
    foreach ($l in $tl) {
        $cells = $l -split "\|" | ForEach-Object { $_.Trim() }
        if ($cells[0] -eq "") { $cells = $cells[1..($cells.Count - 1)] }
        if ($cells[-1] -eq "") { $cells = $cells[0..($cells.Count - 2)] }
        $isSep = $true
        foreach ($c in $cells) { if ($c -notmatch "^[-:]+$" -and $c -ne "") { $isSep = $false; break } }
        if (-not $isSep) { $rows += , @($cells) }
    }
    return $rows
}

function Get-Part($t) {
    if ($t -match "A-\d") { return "A" }
    if ($t -match "B-\d") { return "B" }
    if ($t -match "C-\d") { return "C" }
    if ($t -match "D-\d") { return "D" }
    if ($t -match "E-\d") { return "E" }
    return "Z"
}

function Clean-Name($n) {
    $n = $n -replace '[<>:"/\\|?*]', ''
    $n = $n -replace '\s+', '_'
    if ($n.Length -gt 50) { $n = $n.Substring(0, 50) }
    return $n
}

$cnt = 0
foreach ($t in $tables) {
    $rows = ConvertTo-Rows $t.Lines
    if ($rows.Count -lt 2) { continue }
    $p = Get-Part $t.Title
    $fn = "${p}_$(Clean-Name $t.Title).csv"
    $fp = Join-Path $outCsv $fn
    $csv = @()
    foreach ($r in $rows) {
        $csv += ($r | ForEach-Object { if ($_ -match ",") { "`"$_`"" } else { $_ } }) -join ","
    }
    [System.IO.File]::WriteAllLines($fp, $csv, (New-Object System.Text.UTF8Encoding $true))
    Write-Host "  [CSV] $fn"
    $cnt++
}
Write-Host "[INFO] CSV: $cnt files"

# Excel via COM
try {
    if (Test-Path $outXlsx) { Remove-Item $outXlsx -Force }
    $excel = New-Object -ComObject Excel.Application
    $excel.Visible = $false
    $excel.DisplayAlerts = $false
    $wb = $excel.Workbooks.Add()
    while ($wb.Sheets.Count -gt 1) { $wb.Sheets.Item($wb.Sheets.Count).Delete() }
    
    $csvFiles = Get-ChildItem $outCsv -Filter "*.csv" | Sort-Object Name
    $groups = $csvFiles | Group-Object { $_.Name.Substring(0, 1) } | Sort-Object Name
    
    $si = 0
    foreach ($g in $groups) {
        $sn = switch ($g.Name) {
            "A" { "A_education_ops" }
            "B" { "B_repeat_learning" }
            "C" { "C_content" }
            "D" { "D_method" }
            "Z" { "Z_summary" }
            default { $g.Name }
        }
        
        if ($si -eq 0) { $ws = $wb.Sheets.Item(1); $ws.Name = $sn }
        else { $ws = $wb.Sheets.Add([System.Reflection.Missing]::Value, $wb.Sheets.Item($wb.Sheets.Count)); $ws.Name = $sn }
        
        $cr = 1
        foreach ($cf in $g.Group) {
            $cls = Get-Content $cf.FullName -Encoding UTF8
            $tt = $cf.BaseName -replace "^[A-Z]_", "" -replace "_", " "
            $ws.Cells.Item($cr, 1) = $tt
            $ws.Cells.Item($cr, 1).Font.Bold = $true
            $cr++
            foreach ($cl in $cls) {
                if ([string]::IsNullOrWhiteSpace($cl)) { continue }
                $vals = $cl -split ","
                $col = 1
                foreach ($v in $vals) {
                    $v = $v.Trim().Trim('"')
                    $ws.Cells.Item($cr, $col) = $v
                    $col++
                }
                $cr++
            }
            $cr++
        }
        $ws.UsedRange.Columns.AutoFit() | Out-Null
        $si++
    }
    
    $wb.SaveAs($outXlsx, 51)
    $wb.Close()
    $excel.Quit()
    [System.Runtime.Interopservices.Marshal]::ReleaseComObject($excel) | Out-Null
    Write-Host "[SUCCESS] Excel saved: $outXlsx"
}
catch {
    Write-Host "[ERROR] $_"
    Write-Host "[INFO] CSV files available in $outCsv"
}
Write-Host "[DONE]"
