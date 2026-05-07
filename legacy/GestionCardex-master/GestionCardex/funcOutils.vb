Imports System.Reflection
Imports System.Text.RegularExpressions
Imports System.Data.SqlClient
Imports System.Net
Imports System.Windows.Forms
Imports System.Diagnostics.Process

Public Class FuncOutils

    Public Function funcApos(ByVal Chaine) As String
        On Error GoTo Erreur
        funcApos = Replace(Chaine, "'", "''")
        Exit Function
Erreur:
        subErrorMessage(Err.Number, Err.Description, Me.GetType.Name, MethodInfo.GetCurrentMethod.Name)
    End Function
    '***********************************
    'Convertion d'accents
    '***********************************
    Public Function funcConvertAccent(chaine As String) As String
        Dim Cont As Long
        Dim Carac As String
        Dim t As String

        funcConvertAccent = ""
        t = chaine.ToUpper
        For Cont = 1 To Len(t)
            Carac = Mid(t, Cont, 1)
            If InStr("AÄÁÀÃÂ", Carac) Then
                funcConvertAccent = funcConvertAccent & "[AÄÁÀÃÂ]"
            ElseIf InStr("EËÉÈÊ", Carac) Then
                funcConvertAccent = funcConvertAccent & "[EËÉÈÊ]"
            ElseIf InStr("IÏÍÌÎ", Carac) Then
                funcConvertAccent = funcConvertAccent & "[IÏÍÌÎ]"
            ElseIf InStr("OÖÓÒÔ", Carac) Then
                funcConvertAccent = funcConvertAccent & "[OÖÓÒÔ]"
            ElseIf InStr("UÜÚÙÛ", Carac) Then
                funcConvertAccent = funcConvertAccent & "[UÜÚÙÛ]"
            ElseIf InStr("CÇ", Carac) Then
                funcConvertAccent = funcConvertAccent & "[CÇ]"
            ElseIf Carac = " " Then
                funcConvertAccent = funcConvertAccent & "%"
            Else
                funcConvertAccent = funcConvertAccent & Carac
            End If
        Next

    End Function

    Public Function funcEmailAddressCheck(ByVal emailAddress As String) As Boolean
        On Error GoTo Erreur
        Dim patternEx As String = "[ú|í|ó|á|é|à|ì|ò|ù|è|ñ|ê|û|ô|â|î|ü]"
        Dim emailAddressMatchEx As Match = Regex.Match(emailAddress, patternEx)
        Dim pattern As String = "^\w+([-+.]\w+)*@\w+([-.]\w+)*\.\w+([-.]\w+)*$"

        If emailAddressMatchEx.Success Then
            funcEmailAddressCheck = False
        Else
            funcEmailAddressCheck = System.Text.RegularExpressions.Regex.IsMatch(emailAddress, pattern)
        End If
        Exit Function
Erreur:
        subErrorMessage(Err.Number, Err.Description, Me.GetType.Name, MethodInfo.GetCurrentMethod.Name)
    End Function

    '***************************************
    'Vérifie la permision dans Profilu
    '***************************************
    Public Sub funcGetPermissionUtil(ByVal strlogin As String, ByVal strMotPasse As String)
        Dim conn As New ObjConn.ObjConn
        Dim dr As SqlDataReader
        Dim cmd As SqlCommand
        Dim strSQL As String = "SELECT * FROM profilu  WHERE usern = @strlogin "
        Try
            conn.ConnString = strConnStatic

            cmd = New SqlCommand(strSQL, conn.OpenConn())
            cmd.Parameters.AddWithValue("@strlogin", strlogin)
            'Executer la command et assigne le contenu au recordset
            dr = cmd.ExecuteReader()

            '**Lire le recordset 
            If dr.Read = True Then
                If strMotPasse = dr.GetString(4).Trim Then
                    If dr.GetString(3).Trim = "Cardex" Then
                        vgUser = dr.GetString(2).Trim
                        vgPermission = dr.GetString(9).Trim
                        If dr.GetString(10).Trim = "N" Then
                            If vgPermission = "" Then
                                vgGrUtil = LECTURE
                                gReadOnly = 1
                                MsgBox("Aucune modification ne pourra être effectuée!", vbOKOnly + vbInformation, "Cardex")
                            ElseIf InStr(vgPermission, "Mega") Then
                                vgGrUtil = MEGA
                                gReadOnly = 1
                                MsgBox("Aucune modification ne pourra être effectuée sauf dans l'onglet Mégaprocès!", vbOKOnly + vbInformation, "Cardex")
                            End If
                        Else
                            vgGrUtil = GEST
                            gReadOnly = 0
                        End If
                        frmRechAvo.Show()
                        frmMotPasse.Hide()
                    Else
                        MsgBox("Vous n'avez pas la permission d'utiliser le cardex!", vbOKOnly + vbCritical, "Accès refusé")
                        frmMotPasse.txtNomUtil.SelectionStart = 0
                        frmMotPasse.txtNomUtil.SelectionLength = Len(frmMotPasse.txtNomUtil.Text)
                        frmMotPasse.txtNomUtil.Focus()
                    End If
                Else
                    MsgBox("Vot mot de passe est erroné, veuillez le vérifier !", vbOKOnly + vbCritical, "Mot de passe")
                    frmMotPasse.txtMotPasse.Clear()
                    frmMotPasse.txtMotPasse.Focus()
                End If
            Else
                MsgBox("Vous n'avez pas accès à ce logiciel !", vbOKOnly + vbCritical, "Accès refusé")
            End If
            cmd.Connection.Close()
        Catch ex As Exception
            subErrorMessage(Err.Number, Err.Description, Me.GetType.Name, MethodInfo.GetCurrentMethod.Name)
        Finally
            conn.CloseConn()
        End Try

        '*/*********
        'Dim dr As OleDb.OleDbDataReader = Nothing
        'Dim conn As New ObjConn.ObjConnOle(strConnStatic)

        'Dim strSQL As String = "SELECT * FROM profilu  WHERE usern ='" & strlogin & "'"
        'Try
        '    conn.ExecuteSql(strSQL, dr)
        '    If dr.HasRows Then
        '        dr.Read()
        '        If strMotPasse = dr.GetString(4).Trim Then
        '            If dr.GetString(3).Trim = "Cardex" Then
        '                vgUser = dr.GetString(2).Trim
        '                vgPermission = dr.GetString(9).Trim
        '                If dr.GetString(10).Trim = "N" Then
        '                    If vgPermission = "" Then
        '                        vgGrUtil = LECTURE
        '                        gReadOnly = 1
        '                        MsgBox("Aucune modification ne pourra être effectuée!", vbOKOnly + vbInformation, "Cardex")
        '                    ElseIf InStr(vgPermission, "Mega") Then
        '                        vgGrUtil = MEGA
        '                        gReadOnly = 1
        '                        MsgBox("Aucune modification ne pourra être effectuée sauf dans l'onglet Mégaprocès!", vbOKOnly + vbInformation, "Cardex")
        '                    End If
        '                Else
        '                    vgGrUtil = GEST
        '                    gReadOnly = 0
        '                End If
        '                frmRechAvo.Show()
        '                frmMotPasse.Hide()
        '            Else
        '                MsgBox("Vous n'avez pas la permission d'utiliser le cardex!", vbOKOnly + vbCritical, "Accès refusé")
        '                frmMotPasse.txtNomUtil.SelectionStart = 0
        '                frmMotPasse.txtNomUtil.SelectionLength = Len(frmMotPasse.txtNomUtil.Text)
        '                frmMotPasse.txtNomUtil.Focus()
        '            End If
        '        Else
        '            MsgBox("Vot mot de passe est erroné, veuillez le vérifier !", vbOKOnly + vbCritical, "Mot de passe")
        '            frmMotPasse.txtMotPasse.Clear()
        '            frmMotPasse.txtMotPasse.Focus()
        '        End If
        '    Else
        '        MsgBox("Vous n'avez pas accès à ce logiciel !", vbOKOnly + vbCritical, "Accès refusé")
        '    End If
        'Catch ex As Exception
        '    subErrorMessage(Err.Number, Err.Description, Me.GetType.Name, MethodInfo.GetCurrentMethod.Name)
        'Finally
        '    dr.Close()
        '    dr = Nothing
        '    conn.CloseConn()
        '    conn = Nothing
        'End Try
    End Sub

    Public Sub funcGetServeurs()

        Dim conn As New ObjConn.ObjConn
        Dim dr As SqlDataReader
        Dim cmd As SqlCommand
        Dim strSQL As String = "SELECT * FROM ConfigVals"
        Try
            conn.ConnString = strConnArt52

            cmd = New SqlCommand(strSQL, conn.OpenConn())
            'Executer la command et assigne le contenu au recordset
            dr = cmd.ExecuteReader()

            '**Lire le recordset 
            If dr.Read = True Then
                While dr.Read()
                    Select Case (dr.GetString(2).Trim)
                        Case "rptpath"
                            gPathRap = dr.GetString(3).Trim
                        Case "comptpath"
                            gPathCompt = dr.GetString(3).Trim
                        Case "faxdir"
                            gPathPJ = dr.GetString(3).Trim
                        Case "webpath"
                            gPathWeb = dr.GetString(3).Trim
                        Case "infopath"
                            gPathInfo = dr.GetString(3).Trim
                        Case "mailaddress"
                            gEmailServer = dr.GetString(3).Trim
                            gEmailPort = CInt(dr.GetString(4))
                    End Select
                End While
            End If
            cmd.Connection.Close()
        Catch ex As Exception
            subErrorMessage(Err.Number, Err.Description, Me.GetType.Name, MethodInfo.GetCurrentMethod.Name)
        Finally
            conn.CloseConn()
        End Try

        '***********

        'Dim dr As OleDb.OleDbDataReader = Nothing
        'Dim conn As New ObjConn.ObjConnOle(strConnArt52)
        'Dim strSQL As String = "SELECT * FROM ConfigVals"
        'Try
        '    conn.ExecuteSql(strSQL, dr)
        '    If dr.HasRows Then
        '        While dr.Read()
        '            Select Case (dr.GetString(2).Trim)
        '                Case "rptpath"
        '                    gPathRap = dr.GetString(3).Trim
        '                Case "comptpath"
        '                    gPathCompt = dr.GetString(3).Trim
        '                Case "faxdir"
        '                    gPathPJ = dr.GetString(3).Trim
        '                Case "webpath"
        '                    gPathWeb = dr.GetString(3).Trim
        '                Case "infopath"
        '                    gPathInfo = dr.GetString(3).Trim
        '                Case "mailaddress"
        '                    gEmailServer = dr.GetString(3).Trim
        '                    gEmailPort = CInt(dr.GetString(4))
        '            End Select
        '        End While
        '    End If
        'Catch ex As Exception
        '    subErrorMessage(Err.Number, Err.Description, Me.GetType.Name, MethodInfo.GetCurrentMethod.Name)
        'Finally
        '    dr.Close()
        '    dr = Nothing
        '    conn.CloseConn()
        '    conn = Nothing
        'End Try
    End Sub

    Public Function funcGetUserName(ByVal strLogin As String, ByVal strPoste As String) As Boolean
        Dim conn As New ObjConn.ObjConn
        Dim dr As SqlDataReader
        Dim cmd As SqlCommand
        Dim strSQL As String = "SELECT * FROM profilu  WHERE nomposte = @strPoste and groupe='Cardex'"
        Try
            conn.ConnString = vstrStaticPc

            cmd = New SqlCommand(strSQL, conn.OpenConn())
            cmd.Parameters.AddWithValue("@strPoste", strPoste)
            'Executer la command et assigne le contenu au recordset
            dr = cmd.ExecuteReader()

            '**Lire le recordset 
            If dr.Read = True Then

                frmMotPasse.txtNomUtil.Text = dr.GetString(1).Trim
                Return True
            Else
                Return False
            End If
            cmd.Connection.Close()
        Catch ex As Exception
            subErrorMessage(Err.Number, Err.Description, Me.GetType.Name, MethodInfo.GetCurrentMethod.Name)
            Return False
        Finally
            conn.CloseConn()
        End Try

        'Dim dr As OleDb.OleDbDataReader = Nothing
        'Dim conn As New ObjConn.ObjConn 'Dim conn As New ObjConn.ObjConnOle(strConnStatic)
        'Dim strSQL As String = "SELECT * FROM profilu  WHERE nomposte ='" & strPoste & "' and groupe='Cardex'"
        'Try
        '    conn.ConnString = strConnStatic
        '    conn.ExecuteSql(strSQL, dr)
        '    If dr.HasRows Then
        '        dr.Read()
        '        frmMotPasse.txtNomUtil.Text = dr.GetString(1).Trim
        '        Return True
        '    Else
        '        Return False
        '    End If
        'Catch ex As Exception
        '    subErrorMessage(Err.Number, Err.Description, Me.GetType.Name, MethodInfo.GetCurrentMethod.Name)
        '    Return False
        'Finally
        '    dr.Close()
        '    dr = Nothing
        '    conn.CloseConn()
        '    conn = Nothing
        'End Try
    End Function

    '************************************
    'Remplir Combo- code-avocat-ville
    '************************************
    Public Sub funcRemplirCombo(ByVal cbo As ComboBox, ByVal optCombo As String)
        Dim vstrSQL As String = ""
        Dim vstrConn As String = ""

        Select Case optCombo
            Case "Code"
                vstrSQL = "Select code from Avocats where left(code,1)<>'A' and dateinscbarr<>'2020' and actpass='A' order by code"
                vstrConn = "server= CSJ-SQLMI01 ;uid= sa;pwd= a1de!;database= CardAvo; Pooling=true; Min Pool Size=0; Max Pool Size=100; Connection Lifetime=0; Application Name= fillCombo"

                subFillComboBox(vstrConn, cbo, vstrSQL, "code", "code")
            Case "Avocat"
                vstrSQL = "Select distinct rtrim(nom) + ' ' + rtrim(prenom) as nomavo from Avocats where left(code,1)<>'A' and dateinscbarr<>'2020' and actpass='A' order by nomavo"
                vstrConn = "server= CSJ-SQLMI01 ;uid= sa;pwd= a1de!;database= CardAvo; Pooling=true; Min Pool Size=0; Max Pool Size=100; Connection Lifetime=0"

                subFillComboBox(vstrConn, cbo, vstrSQL, "nomavo", "nomavo")
            Case "Ville"
                vstrSQL = "Select distinct rtrim(ville1) as ville from distance union select distinct rtrim(ville2) as ville from distance order by ville"
                vstrConn = "server= CSJ-SQLMI01 ;uid= sa;pwd= a1de!;database= StaticPC; Pooling=true; Min Pool Size=0; Max Pool Size=100; Connection Lifetime=0"

                subFillComboBox(vstrConn, cbo, vstrSQL, "ville", "ville")
        End Select
    End Sub

    Public Function funcRemoveAccent(strDs As String) As String
        On Error GoTo Erreur
        Dim strDsSA As String = strDs
        Dim patternEx As String = "[á|à|â|í|ì|î|ú|ù|û|ü|é|è|ê|ó|ò|ô]"
        Dim emailAddressMatchEx As Match = Regex.Match(strDs, patternEx)
        Dim pattern As String = "^\w+([-+.]\w+)*@\w+([-.]\w+)*\.\w+([-.]\w+)*$"

        If emailAddressMatchEx.Success Then
            funcRemoveAccent = strDsSA
        Else
            funcRemoveAccent = System.Text.RegularExpressions.Regex.IsMatch(strDs, pattern)
        End If
        Exit Function
Erreur:
        subErrorMessage(Err.Number, Err.Description, Me.GetType.Name, MethodInfo.GetCurrentMethod.Name)
    End Function

    Public Function funcRemoveParenthese(strDs As String) As String
        On Error GoTo Erreur
        strDs = Replace(strDs, "(", "")
        strDs = Replace(strDs, ")", "")

        funcRemoveParenthese = strDs
        Exit Function
Erreur:
        subErrorMessage(Err.Number, Err.Description, Me.GetType.Name, MethodInfo.GetCurrentMethod.Name)
    End Function

    Public Function funcReplaceChar(ByVal Chaine As String, strCharacter As String, strNeoChar As String) As String
        On Error GoTo Erreur
        funcReplaceChar = Replace(Chaine, strCharacter, strNeoChar)
        Exit Function
Erreur:
        subErrorMessage(Err.Number, Err.Description, Me.GetType.Name, MethodInfo.GetCurrentMethod.Name)
    End Function

    Public Function funcValidateWeekDay(dDate As Date) As Date
        On Error GoTo Erreur
        Dim iDay As Integer = dDate.DayOfWeek

        If iDay = 6 Or iDay = 0 Then
            Select Case iDay
                Case 0
                    funcValidateWeekDay = dDate.AddDays(1)
                Case 6
                    funcValidateWeekDay = dDate.AddDays(2)
                Case Else
                    funcValidateWeekDay = dDate
            End Select
        Else
            funcValidateWeekDay = dDate
        End If
        Exit Function
Erreur:
        subErrorMessage(Err.Number, Err.Description, Me.GetType.Name, MethodInfo.GetCurrentMethod.Name)
    End Function

    Public Sub subErrorMessage(ByVal ErrNumber As Integer, ByVal ErrDesc As String, ByVal FrmClass As String, ByVal SubFunc As String)
        Dim strMsg As String = ErrNumber & ": " & ErrDesc & " (" & FrmClass & " - " & SubFunc & ")"
        MessageBox.Show(strMsg, vgStrTitreMsgBoxErreur, MessageBoxButtons.OK, MessageBoxIcon.Error)
    End Sub

    Protected Friend Sub subFillComboBox(strConn As String, ByRef cbo As ComboBox, ByVal strSQL As String, ByVal strFieldID As String, ByVal strFieldDs As String)
        Dim dt As New DataSet
        Dim connection As SqlConnection
        Dim command As SqlCommand
        Dim da As New SqlDataAdapter
        connection = New SqlConnection(strConn)

        Try
            connection.Open()
            command = New SqlCommand(strSQL, connection)
            da.SelectCommand = command
            da.Fill(dt)
            da.Dispose()
            command.Dispose()
            connection.Close()

            With cbo
                .DataSource = dt.Tables(0)
                .DisplayMember = strFieldDs
                .ValueMember = strFieldID
                .SelectedIndex = -1
            End With
            dt.Dispose()
        Catch ex As Exception
            subErrorMessage(Err.Number, Err.Description, Me.GetType.Name, MethodInfo.GetCurrentMethod.Name)
        End Try
    End Sub

    Public Sub subStartDefaultMail(ByVal sTo As String, Optional ByVal sSubject As String = "", Optional ByVal sMessage As String = "")
        Try
            'sTo = sTo)
            sSubject = sSubject
            sMessage = sMessage
            Process.Start("mailto:" & sTo & " " & sSubject & " " & sMessage)
            'Process.Start("mailto:" & sTo & "?subject=" & sSubject & "&body=" & sMessage)

        Catch e As Exception
            MessageBox.Show("Couldn't start default email application" & vbCrLf & e.Message)
            'or
            Throw New Exception("Couldn't start default email app", e)
        End Try
    End Sub
    Public Function funcRemoveCharacter(ByVal Chaine As String, strCharacter As String) As String
        On Error GoTo Erreur
        funcRemoveCharacter = Replace(Chaine, strCharacter, "")
        Exit Function
Erreur:
        subErrorMessage(Err.Number, Err.Description, Me.GetType.Name, MethodInfo.GetCurrentMethod.Name)
    End Function

    Public Function formatPhoneNumber(phoneNum As String, phoneFormat As String) As String

        If phoneFormat = "" Then
            ' Default format is (###) ###-####
            phoneFormat = "###-###-####"
        End If

        ' First, remove everything except of numbers
        Dim regexObj As Regex = New Regex("[^\d]")
        phoneNum = regexObj.Replace(phoneNum, "")

        ' Second, format numbers to phone string
        If phoneNum.Length > 0 Then
            phoneNum = Convert.ToInt64(phoneNum).ToString(phoneFormat)
        End If

        Return phoneNum
    End Function
    ''' <summary>
    ''' Empeche de rentrer de caracteres dans textbox (sender, e, Filtre)
    ''' Filtre: 0 - Pas decimal et pas negative; 1 - Pas negative; 2 - Pas decimal; 3 - Tout numéro
    ''' </summary>
    Public Sub subTextBoxNumber(ByRef sender As Object, ByRef e As System.Windows.Forms.KeyPressEventArgs, ByVal iFiltre As Integer)
        Try
            'Valeur iFiltre
            '0 : Pas decimal, Pas negative
            '1 : Decimal, pas negative
            '2 : Pas decimal, negative
            '3 : Decimal et negative
            Dim tb As TextBox = CType(sender, TextBox)
            Dim chr As Char = e.KeyChar
            If IsNumeric(e.KeyChar) And Not e.KeyChar = "-" And (iFiltre = 0 Or iFiltre = 1) Then
                'If adding the character to the end of the current TextBox value results in a numeric value, go on. Otherwise, set e.Handled to True, and don't let the character to be added.
                e.Handled = Not IsNumeric(tb.Text & e.KeyChar)
            ElseIf (IsNumeric(e.KeyChar) Or e.KeyChar = ".") And (iFiltre = 1 Or iFiltre = 3) Then
                'For the decimal character (.) we need a different rule: 
                'If adding a decimal to the end of the current value of the TextBox results in a numeric value, it can be added. If not, this means we already have a decimal in the TextBox value, so we only allow the new decimal to sit in
                'when it is overwriting the previous decimal.
                If Not (tb.SelectedText = "." Or IsNumeric(tb.Text & e.KeyChar)) Then
                    e.Handled = True
                End If
            ElseIf e.KeyChar = "-" And (iFiltre = 2 Or iFiltre = 3) Then
                'A negative sign is prevented if the "-" key is pressed in any location other than the begining of the number, or if the number already has a negative sign 
                If (tb.SelectionStart <> 0 Or Microsoft.VisualBasic.Left(tb.Text, 1) = "-") Then
                    e.Handled = True
                End If
            ElseIf Not Char.IsControl(e.KeyChar) Then
                'IsControl is checked, because without that, keys like BackSpace couldn't work correctly.
                e.Handled = True
            End If
        Catch ex As Exception
            subErrorMessage(Err.Number, Err.Description, Me.GetType.Name, MethodInfo.GetCurrentMethod.Name)
        End Try
    End Sub

    Public Function funcRemplirFiveZero(strChaine As String) As String
        Try
            Select Case strChaine.Trim.Length
                Case 1
                    strChaine = "0000" & strChaine.Trim
                Case 2
                    strChaine = "000" & strChaine.Trim
                Case 3
                    strChaine = "00" & strChaine.Trim
                Case 4
                    strChaine = "0" & strChaine.Trim
                Case 5
                    strChaine = "" & strChaine.Trim
            End Select
            Return strChaine
        Catch ex As Exception
            subErrorMessage(Err.Number, Err.Description, Me.GetType.Name, MethodInfo.GetCurrentMethod.Name)
        End Try
        Return String.Empty
    End Function
End Class
