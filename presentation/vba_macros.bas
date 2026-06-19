Option Explicit

Private Const API_BASE As String = "http://127.0.0.1:5001"
Private Const AUTH_TOKEN As String = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTc4MDU2OTY2MCwianRpIjoiNWU3ZjQ4MWUtYWI2YS00MjFmLWIwYWItYTUzMzA0M2ZhMjMwIiwidHlwZSI6ImFjY2VzcyIsInN1YiI6IjEiLCJuYmYiOjE3ODA1Njk2NjAsImNzcmYiOiIxMTc0YThkNC1iZDNiLTQ3YjctOGU4Ni0zNmJhMTQ2YjA0M2EiLCJleHAiOjE3ODA1OTg0NjAsInJvbGUiOiJ0ZWFjaGVyIn0.DCELTEiWbodu0fLW2qya2wSzk5iYoKGUiwyyBg-5RDQ"

Public Function HttpJson(ByVal method As String, ByVal url As String, Optional ByVal jsonBody As String = "") As String
    Dim http As Object
    Set http = CreateObject("MSXML2.XMLHTTP")

    http.Open method, url, False
    http.setRequestHeader "Content-Type", "application/json"
    http.setRequestHeader "Authorization", "Bearer " & AUTH_TOKEN
    http.Send jsonBody

    If http.Status < 200 Or http.Status >= 300 Then
        MsgBox "HTTP Error: " & http.Status & vbCrLf & http.responseText
        Exit Function
    End If

    HttpJson = http.responseText
End Function

Public Sub RunCreateSession()

    Dim slideId As Long
    slideId = 1

    Dim body As String
    body = "{""slide_id"":" & slideId & "}"

    Dim resp As String
    resp = HttpJson("POST", API_BASE & "/api/sessions", body)
    If resp = "" Then Exit Sub

    Dim JSON As Object
    Set JSON = JsonConverter.ParseJson(resp)

    Dim sid As String
    sid = CStr(JSON("session_id"))

    ActivePresentation.tags.Add "pollpoint_session_id", sid

    Dim url As String
    url = API_BASE & "/poll.html?session=" & sid

    On Error Resume Next
    ActivePresentation.SlideShowWindow.View.Slide.Shapes("PollLink").TextFrame.TextRange.text = url
    On Error GoTo 0

    MsgBox "Сессия создана!" & vbCrLf & url

End Sub

Public Sub RunRefreshStats()

    Dim slideId As Long
    slideId = 5

    Dim resp As String
    resp = HttpJson("GET", API_BASE & "/api/ppt/slide/" & slideId & "/stats")
    If resp = "" Then Exit Sub

    Dim JSON As Object
    Set JSON = JsonConverter.ParseJson(resp)

    Dim sld As Slide
    Set sld = ActivePresentation.SlideShowWindow.View.Slide

    Dim question As String
    question = CStr(JSON("question"))

    Dim total As Long
    total = CLng(JSON("total"))

    On Error Resume Next
    sld.Shapes("QuestionBox").TextFrame.TextRange.text = question
    sld.Shapes("TotalBox").TextFrame.TextRange.text = "Ответов: " & total
    On Error GoTo 0

    Dim items As Object
    Dim tags As Object

    On Error Resume Next
    Set items = JSON("items")
    Set tags = JSON("tags")
    On Error GoTo 0

    Dim i As Long

    If Not items Is Nothing And items.Count > 0 Then

        On Error Resume Next
        sld.Shapes("TagsBox").Visible = False
        On Error GoTo 0

        For i = 1 To 5
            On Error Resume Next
            sld.Shapes("Bar" & i).Visible = True
            sld.Shapes("Label" & i).Visible = True
            sld.Shapes("Percent" & i).Visible = True
            sld.Shapes("Bar" & i).Width = 1
            sld.Shapes("Percent" & i).TextFrame.TextRange.text = ""
            sld.Shapes("Label" & i).TextFrame.TextRange.text = ""
            On Error GoTo 0
        Next i

        Dim idx As Long
        idx = 1

        Dim it As Variant
        For Each it In items
            If idx > 5 Then Exit For

            Dim percent As Double
            percent = CDbl(it("percent"))

            Dim maxWidth As Double
            maxWidth = 500

            Dim newWidth As Double
            newWidth = maxWidth * (percent / 100)

            On Error Resume Next
            sld.Shapes("Label" & idx).TextFrame.TextRange.text = it("label")
            sld.Shapes("Percent" & idx).TextFrame.TextRange.text = percent & "%"
            sld.Shapes("Bar" & idx).Width = newWidth
            On Error GoTo 0

            idx = idx + 1
        Next it

    ElseIf Not tags Is Nothing And tags.Count > 0 Then

        For i = 1 To 5
            On Error Resume Next
            sld.Shapes("Bar" & i).Visible = False
            sld.Shapes("Label" & i).Visible = False
            sld.Shapes("Percent" & i).Visible = False
            On Error GoTo 0
        Next i

        On Error Resume Next
        sld.Shapes("TagsBox").Visible = True
        On Error GoTo 0

        Dim output As String
        output = ""

        Dim t As Variant
        For Each t In tags
            output = output & t("word") & " (" & t("count") & ")" & vbCrLf
        Next t

        On Error Resume Next
        sld.Shapes("TagsBox").TextFrame.TextRange.text = output
        On Error GoTo 0

    End If

End Sub
