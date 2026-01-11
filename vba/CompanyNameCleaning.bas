Attribute VB_Name = "CompanyNameCleaning"
Option Explicit

'==============================================================================
' 모듈명: CompanyNameCleaning
' 목적: 기업명 중복 검사를 위한 기업명 클리닝 및 표준화
' 작성일: 2026-01-11
' 사용법: 엑셀에서 기업명 셀들을 선택하고 CleanCompanyNames 매크로 실행
'==============================================================================

' 메인 프로시저: 선택된 셀의 기업명을 클리닝
Public Sub CleanCompanyNames()
    Dim rng As Range
    Dim cell As Range
    Dim originalName As String
    Dim cleanedName As String
    Dim resultCol As Long
    Dim startRow As Long
    
    ' 선택 영역 확인
    If Selection.Cells.Count = 0 Then
        MsgBox "기업명이 있는 셀을 선택해주세요.", vbExclamation, "선택 오류"
        Exit Sub
    End If
    
    ' 결과를 표시할 열 결정 (선택 영역의 오른쪽 열)
    resultCol = Selection.Column + 1
    startRow = Selection.Row
    
    ' 헤더 추가
    Cells(startRow, resultCol).Value = "클리닝된 기업명"
    Cells(startRow, resultCol).Font.Bold = True
    
    ' 각 셀에 대해 클리닝 수행
    Application.ScreenUpdating = False
    
    For Each cell In Selection
        If cell.Row >= startRow Then
            originalName = Trim(cell.Value)
            
            If originalName <> "" Then
                cleanedName = CleanCompanyName(originalName)
                Cells(cell.Row, resultCol).Value = cleanedName
            End If
        End If
    Next cell
    
    Application.ScreenUpdating = True
    
    MsgBox "기업명 클리닝이 완료되었습니다." & vbCrLf & _
           "처리된 기업: " & (Selection.Rows.Count) & "개", _
           vbInformation, "완료"
End Sub

' 기업명 클리닝 함수
Public Function CleanCompanyName(ByVal companyName As String) As String
    Dim result As String
    
    result = companyName
    
    ' 1단계: Trim 및 기본 정리
    result = Trim(result)
    
    ' 2단계: 영문 약어를 한글로 변환 (필요시)
    result = ConvertEnglishToKorean(result)
    
    ' 3단계: 법인 형태 표기 제거
    result = RemoveCorporateTypes(result)
    
    ' 4단계: 괄호 안의 내용 제거
    result = RemoveParentheses(result)
    
    ' 5단계: 불필요한 단어 제거 (공장, 지점, 본사 등)
    result = RemoveUnnecessaryWords(result)
    
    ' 6단계: 특수문자 제거
    result = RemoveSpecialCharacters(result)
    
    ' 7단계: 모든 공백 제거
    result = Replace(result, " ", "")
    result = Replace(result, vbTab, "")
    
    ' 8단계: 최종 Trim
    result = Trim(result)
    
    CleanCompanyName = result
End Function

' 영문을 한글로 변환 (주요 기업명 약어)
Private Function ConvertEnglishToKorean(ByVal text As String) As String
    Dim result As String
    result = text
    
    ' 일반적인 영문 약어 변환
    result = Replace(result, "Co.,Ltd.", "", , , vbTextCompare)
    result = Replace(result, "Co., Ltd.", "", , , vbTextCompare)
    result = Replace(result, "Co.Ltd.", "", , , vbTextCompare)
    result = Replace(result, "Corporation", "", , , vbTextCompare)
    result = Replace(result, "Corp.", "", , , vbTextCompare)
    result = Replace(result, "Inc.", "", , , vbTextCompare)
    result = Replace(result, "LLC", "", , , vbTextCompare)
    result = Replace(result, "Ltd.", "", , , vbTextCompare)
    result = Replace(result, "Limited", "", , , vbTextCompare)
    
    ConvertEnglishToKorean = result
End Function

' 법인 형태 표기 제거
Private Function RemoveCorporateTypes(ByVal text As String) As String
    Dim result As String
    result = text
    
    ' 한글 법인 형태
    result = Replace(result, "주식회사", "", , , vbTextCompare)
    result = Replace(result, "유한회사", "", , , vbTextCompare)
    result = Replace(result, "유한책임회사", "", , , vbTextCompare)
    result = Replace(result, "합자회사", "", , , vbTextCompare)
    result = Replace(result, "합명회사", "", , , vbTextCompare)
    result = Replace(result, "재단법인", "", , , vbTextCompare)
    result = Replace(result, "사단법인", "", , , vbTextCompare)
    result = Replace(result, "학교법인", "", , , vbTextCompare)
    result = Replace(result, "의료법인", "", , , vbTextCompare)
    
    ' 약어 형태
    result = Replace(result, "(주)", "")
    result = Replace(result, "㈜", "")
    result = Replace(result, "(유)", "")
    result = Replace(result, "㈜", "")
    result = Replace(result, "(재)", "")
    result = Replace(result, "(사)", "")
    result = Replace(result, "(합)", "")
    
    RemoveCorporateTypes = result
End Function

' 괄호 안의 내용 제거
Private Function RemoveParentheses(ByVal text As String) As String
    Dim result As String
    Dim startPos As Long
    Dim endPos As Long
    
    result = text
    
    ' 소괄호 제거
    Do While InStr(result, "(") > 0 And InStr(result, ")") > 0
        startPos = InStr(result, "(")
        endPos = InStr(startPos, result, ")")
        If endPos > startPos Then
            result = Left(result, startPos - 1) & Mid(result, endPos + 1)
        Else
            Exit Do
        End If
    Loop
    
    ' 대괄호 제거
    Do While InStr(result, "[") > 0 And InStr(result, "]") > 0
        startPos = InStr(result, "[")
        endPos = InStr(startPos, result, "]")
        If endPos > startPos Then
            result = Left(result, startPos - 1) & Mid(result, endPos + 1)
        Else
            Exit Do
        End If
    Loop
    
    ' 중괄호 제거
    Do While InStr(result, "{") > 0 And InStr(result, "}") > 0
        startPos = InStr(result, "{")
        endPos = InStr(startPos, result, "}")
        If endPos > startPos Then
            result = Left(result, startPos - 1) & Mid(result, endPos + 1)
        Else
            Exit Do
        End If
    Loop
    
    RemoveParentheses = result
End Function

' 불필요한 단어 제거
Private Function RemoveUnnecessaryWords(ByVal text As String) As String
    Dim result As String
    result = text
    
    ' 사업장 관련
    result = Replace(result, "본사", "", , , vbTextCompare)
    result = Replace(result, "본점", "", , , vbTextCompare)
    result = Replace(result, "지사", "", , , vbTextCompare)
    result = Replace(result, "지점", "", , , vbTextCompare)
    result = Replace(result, "공장", "", , , vbTextCompare)
    result = Replace(result, "사업소", "", , , vbTextCompare)
    result = Replace(result, "사업장", "", , , vbTextCompare)
    result = Replace(result, "영업소", "", , , vbTextCompare)
    result = Replace(result, "출장소", "", , , vbTextCompare)
    result = Replace(result, "연구소", "", , , vbTextCompare)
    result = Replace(result, "센터", "", , , vbTextCompare)
    
    ' 지역명이 포함된 경우 (필요시 추가)
    result = Replace(result, "서울", "", , , vbTextCompare)
    result = Replace(result, "부산", "", , , vbTextCompare)
    result = Replace(result, "대구", "", , , vbTextCompare)
    result = Replace(result, "인천", "", , , vbTextCompare)
    result = Replace(result, "광주", "", , , vbTextCompare)
    result = Replace(result, "대전", "", , , vbTextCompare)
    result = Replace(result, "울산", "", , , vbTextCompare)
    result = Replace(result, "세종", "", , , vbTextCompare)
    
    RemoveUnnecessaryWords = result
End Function

' 특수문자 제거
Private Function RemoveSpecialCharacters(ByVal text As String) As String
    Dim result As String
    Dim i As Long
    Dim char As String
    
    result = ""
    
    For i = 1 To Len(text)
        char = Mid(text, i, 1)
        
        ' 한글, 영문, 숫자만 유지
        If (char >= "가" And char <= "힣") Or _
           (char >= "A" And char <= "Z") Or _
           (char >= "a" And char <= "z") Or _
           (char >= "0" And char <= "9") Or _
           char = " " Then
            result = result & char
        End If
    Next i
    
    RemoveSpecialCharacters = result
End Function

' 중복 검사 함수 (선택 사항)
Public Sub CheckDuplicates()
    Dim rng As Range
    Dim dict As Object
    Dim cell As Range
    Dim cleanedName As String
    Dim duplicateCount As Long
    Dim resultMsg As String
    
    Set dict = CreateObject("Scripting.Dictionary")
    
    If Selection.Cells.Count = 0 Then
        MsgBox "검사할 기업명 셀을 선택해주세요.", vbExclamation
        Exit Sub
    End If
    
    ' 중복 검사
    For Each cell In Selection
        If cell.Value <> "" Then
            cleanedName = CleanCompanyName(cell.Value)
            
            If dict.exists(cleanedName) Then
                dict(cleanedName) = dict(cleanedName) + 1
            Else
                dict.Add cleanedName, 1
            End If
        End If
    Next cell
    
    ' 중복 항목 찾기
    resultMsg = "=== 중복 기업명 목록 ===" & vbCrLf & vbCrLf
    duplicateCount = 0
    
    Dim key As Variant
    For Each key In dict.Keys
        If dict(key) > 1 Then
            resultMsg = resultMsg & key & " : " & dict(key) & "건" & vbCrLf
            duplicateCount = duplicateCount + 1
        End If
    Next key
    
    If duplicateCount = 0 Then
        MsgBox "중복된 기업명이 없습니다.", vbInformation, "중복 검사 완료"
    Else
        MsgBox resultMsg, vbInformation, "중복 검사 완료 (" & duplicateCount & "개 발견)"
    End If
    
    Set dict = Nothing
End Sub
