Attribute VB_Name = "Module3"
Sub 구조변환_비율서식유지()
Attribute 구조변환_비율서식유지.VB_ProcData.VB_Invoke_Func = " \n14"

    Dim src As Range
    Dim ws As Worksheet
    Dim outRow As Long
    Dim c As Long

    Set ws = ActiveSheet
    Set src = Selection   ' 회색 영역 선택

    ' 출력 시작 위치
    outRow = src.Rows(src.Rows.Count).Row + 2

    ' 헤더
    ws.Cells(outRow, 1).Value = "구분"
    ws.Cells(outRow, 2).Value = "빈도"
    ws.Cells(outRow, 3).Value = "비율"
    outRow = outRow + 1

    ' 열 단위 처리
    For c = 1 To src.Columns.Count Step 2

        ' 구분
        ws.Cells(outRow, 1).Value = src.Cells(1, c).Value

        ' 빈도 (값만)
        ws.Cells(outRow, 2).Value = src.Cells(3, c).Value

        ' ?? 비율 (값 + 셀형식 그대로 복사)
        src.Cells(3, c + 1).Copy
        ws.Cells(outRow, 3).PasteSpecial xlPasteValues
        ws.Cells(outRow, 3).PasteSpecial xlPasteFormats
        Application.CutCopyMode = False

        outRow = outRow + 1

    Next c

    MsgBox "비율 셀 형식까지 포함해 정상 변환되었습니다."

End Sub

