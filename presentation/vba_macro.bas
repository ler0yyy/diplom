Option Explicit

' Требуется подключить модуль VBA-JSON (JsonConverter) в проект VBA.
' Требуется добавить ссылку на "Microsoft XML, v6.0" (или использовать late binding как ниже).
'
' Логика:
' - На слайде с QR лектор вызывает CreateSessionForSlide(slideId), сохраняем session_id в Tags презентации
' - На слайде статистики вызываем RefreshStatsFromSession() и обновляем текстовые поля (и при желании Chart)

Private Const API_BASE As String = "http://localhost:5000"

Public Function HttpJson(ByVal method As String, ByVal url As String, Optional ByVal jsonBody As String = "") As String
    Dim http As Object
    Set http = CreateObject("MSXML2.XMLHTTP")

    http.Open method, url, False
    http.setRequestHeader "Content-Type", "application/json"
    http.Send jsonBody

    If http.Status < 200 Or http.Status >= 300 Then
        Err.Raise vbObjectError + 513, "HttpJson", "HTTP " & http.Status & ": " & http.responseText
    End If

    HttpJson = http.responseText
End Function

Public Function CreateSession(ByVal slideId As Long) As String
    Dim body As String
    body = "{""slide_id"":" & CStr(slideId) & "}"

    Dim resp As String
    resp = HttpJson("POST", API_BASE & "/api/sessions", body)

    Dim JSON As Object
    Set JSON = JsonConverter.ParseJson(resp)

    CreateSession = CStr(JSON("session_id"))
End Function

Private Function GetCurrentShowSlide() As Slide
    On Error Resume Next
    Set GetCurrentShowSlide = ActivePresentation.SlideShowWindow.View.Slide
    On Error GoTo 0
End Function

Public Function PollUrlForSession(ByVal sessionId As String) As String
    PollUrlForSession = API_BASE & "/poll.html?session=" & sessionId
End Function

Public Sub CreateSessionForSlide(ByVal slideId As Long)
    Dim sid As String
    sid = CreateSession(slideId)

    On Error Resume Next
    ActivePresentation.Tags.Delete "pollpoint_session_id"
    On Error GoTo 0
    ActivePresentation.Tags.Add "pollpoint_session_id", sid
    ActivePresentation.Tags.Add "pollpoint_slide_id", CStr(slideId)

    Dim url As String
    url = PollUrlForSession(sid)

    Dim sld As Slide
    Set sld = GetCurrentShowSlide()
    If sld Is Nothing Then
        MsgBox "Сессия создана: " & sid & vbCrLf & "Ссылка: " & url, vbInformation
        Exit Sub
    End If

    On Error Resume Next
    sld.Shapes("PollLink").TextFrame.TextRange.Text = url
    On Error GoTo 0

    MsgBox "Сессия создана: " & sid & vbCrLf & "Ссылка: " & url, vbInformation
End Sub

Public Function GetCurrentSessionId() As String
    Dim sid As String
    sid = ""
    On Error Resume Next
    sid = ActivePresentation.Tags("pollpoint_session_id")
    On Error GoTo 0
    GetCurrentSessionId = sid
End Function

Public Sub RefreshStatsFromSession()
    Dim sid As String
    sid = GetCurrentSessionId()
    If sid = "" Then
        MsgBox "Нет session_id. Сначала создайте сессию на QR-слайде.", vbExclamation
        Exit Sub
    End If

    Dim resp As String
    resp = HttpJson("GET", API_BASE & "/api/sessions/" & sid & "/stats")

    Dim JSON As Object
    Set JSON = JsonConverter.ParseJson(resp)

    Dim question As String
    question = CStr(JSON("question"))

    Dim total As Long
    total = CLng(JSON("total"))

    Dim sld As Slide
    Set sld = GetCurrentShowSlide()
    If sld Is Nothing Then
        MsgBox question & vbCrLf & "Всего ответов: " & CStr(total), vbInformation
        Exit Sub
    End If

    On Error Resume Next
    sld.Shapes("QuestionBox").TextFrame.TextRange.Text = question
    sld.Shapes("TotalBox").TextFrame.TextRange.Text = CStr(total)
    On Error GoTo 0

    ' Если это choice — заполним Option1..Option5 (если есть)
    Dim items As Object
    Set items = Nothing
    On Error Resume Next
    Set items = JSON("items")
    On Error GoTo 0

    If Not items Is Nothing Then
        Dim i As Long
        For i = 1 To 5
            On Error Resume Next
            sld.Shapes("Option" & CStr(i)).TextFrame.TextRange.Text = ""
            On Error GoTo 0
        Next i

        Dim idx As Long
        idx = 1

        Dim it As Variant
        For Each it In items
            If idx > 5 Then Exit For
            Dim line As String
            line = CStr(it("label")) & " — " & CStr(it("votes")) & " (" & CStr(it("percent")) & "%)"
            On Error Resume Next
            sld.Shapes("Option" & CStr(idx)).TextFrame.TextRange.Text = line
            On Error GoTo 0
            idx = idx + 1
        Next it
    End If

    ' Если tags — можно вывести в TagsBox
    Dim tags As Object
    Set tags = Nothing
    On Error Resume Next
    Set tags = JSON("tags")
    On Error GoTo 0

    If Not tags Is Nothing Then
        Dim out As String
        out = ""
        Dim t As Variant
        For Each t In tags
            out = out & CStr(t("word")) & " (" & CStr(t("count")) & ")" & vbCrLf
        Next t
        If out <> "" Then
            On Error Resume Next
            sld.Shapes("TagsBox").TextFrame.TextRange.Text = out
            On Error GoTo 0
        End If
    End If
End Sub

Public Sub RefreshStatsBySlideId(ByVal slideId As Long)
    Dim resp As String
    resp = HttpJson("GET", API_BASE & "/api/ppt/slide/" & CStr(slideId) & "/stats")

    Dim JSON As Object
    Set JSON = JsonConverter.ParseJson(resp)

    MsgBox CStr(JSON("question")) & vbCrLf & "Всего: " & CStr(JSON("total")), vbInformation
End Sub

