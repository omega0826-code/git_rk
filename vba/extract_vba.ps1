# Extract VBA code from Excel file
$excelFile = "d:\git_rk\vba\(실행파일)기업명부 클리닝_V1.00_240618.xlsm"
$outputFile = "d:\git_rk\vba\extracted_vba_code.txt"

try {
    $excel = New-Object -ComObject Excel.Application
    $excel.Visible = $false
    $excel.DisplayAlerts = $false
    
    Write-Host "Opening workbook..."
    $workbook = $excel.Workbooks.Open($excelFile)
    
    $output = ""
    
    Write-Host "Extracting VBA code..."
    foreach ($component in $workbook.VBProject.VBComponents) {
        $output += "=" * 80 + "`r`n"
        $output += "Module: $($component.Name)`r`n"
        $output += "Type: $($component.Type)`r`n"
        $output += "=" * 80 + "`r`n`r`n"
        
        $lineCount = $component.CodeModule.CountOfLines
        if ($lineCount -gt 0) {
            $code = $component.CodeModule.Lines(1, $lineCount)
            $output += $code + "`r`n`r`n"
        }
    }
    
    $output | Out-File -FilePath $outputFile -Encoding UTF8
    
    Write-Host "VBA code extracted to: $outputFile"
    
    $workbook.Close($false)
    $excel.Quit()
    [System.Runtime.Interopservices.Marshal]::ReleaseComObject($workbook) | Out-Null
    [System.Runtime.Interopservices.Marshal]::ReleaseComObject($excel) | Out-Null
    [System.GC]::Collect()
    [System.GC]::WaitForPendingFinalizers()
    
    Write-Host "Done!"
}
catch {
    Write-Host "Error: $_"
    if ($excel) {
        $excel.Quit()
        [System.Runtime.Interopservices.Marshal]::ReleaseComObject($excel) | Out-Null
    }
}
