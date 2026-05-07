Imports System.Data
Imports System.Data.SqlClient
Imports System.Reflection

Public Class infomega

    Dim funcOutils As New FuncOutils

    Sub New()

    End Sub

    Sub Load(ByVal strCodeAvo As String)
        Dim conn As New ObjConn.ObjConn
        Dim cmd As SqlCommand
        Dim myread As SqlDataReader = Nothing
        Dim strSQL As String = ""

        'strSQL = "set dateformat ymd SELECT code,francais,anglais,autres,experience,details,mega,tarification,art486,art672,art684,"
        'strSQL = strSQL + "districthab,commentaire,dateinsc,usermodif,isnull(datemodif,'1900/01/01') as datemodif,sectbar "
        'strSQL = strSQL + "FROM infomega WHERE code='" & strCodeAvo & "'"

        strSQL = "SET DATEFORMAT ymd SELECT code,francais,anglais,autres,experience,details,mega,tarification,art486,art672,art684," & _
            "districthab,commentaire,dateinsc,usermodif,isnull(datemodif,'1900/01/01') as datemodif,sectbar " & _
            "FROM infomega where code = @code"

        Try
            conn.ConnString = vstrConnCardAvo

            cmd = New SqlCommand(strSQL, conn.OpenConn())
            cmd.Parameters.AddWithValue("@code", strCodeAvo)
            'Executer la command et assigne le contenu au recordset
            myread = cmd.ExecuteReader()

            If myread.HasRows Then
                gMega = True
                myread.Read()
                _code = myread("code").ToString.Trim
                _francais = myread("francais").ToString.Trim
                _anglais = myread("anglais").ToString.Trim
                _autres = myread("autres").ToString.Trim
                _experience = myread("experience")
                _details = myread("details").ToString.Trim
                _mega = myread("mega").ToString.Trim
                _tarification = myread("tarification").ToString.Trim
                _art486 = myread("art486").ToString.Trim
                _art672 = myread("art672").ToString.Trim
                _art684 = myread("art684").ToString.Trim
                _districthab = myread("districthab").ToString.Trim
                _commentaire = myread("commentaire").ToString.Trim
                _dateinsc = myread("dateinsc")
                _usermodif = myread("usermodif").ToString.Trim
                _datemodif = myread("datemodif")
                _sectbar = myread("sectbar").ToString.Trim
            Else
                gMega = False
            End If
        Catch ex As Exception
            funcOutils.subErrorMessage(Err.Number, Err.Description, Me.GetType.Name, MethodInfo.GetCurrentMethod.Name)
        Finally
            myread.Close()
            myread = Nothing
            conn.CloseConn()
        End Try

    End Sub

    Sub Save(ByVal strCodeAvo As String)
        Dim conn As New ObjConn.ObjConn
        Dim strSQL As String = ""
        Dim cmd As SqlCommand
        Dim intResultat As Integer

        Try

            If strCodeAvo <> "" Then
                'strSQL = "set dateformat ymd UPDATE infomega SET francais='" & _francais & "',anglais='" & _anglais & "',autres='" & _autres & "',experience=" & _experience & ","
                'strSQL = strSQL + "details='" & funcOutils.funcApos(_details) & "',mega='" & _mega & "',tarification='" & _tarification & "',art486='" & _art486 & "',"
                'strSQL = strSQL + "art672='" & _art672 & "',art684='" & _art684 & "',districthab='" & funcOutils.funcApos(_districthab) & "',commentaire='" & funcOutils.funcApos(_commentaire) & "',"
                'strSQL = strSQL + "dateinsc='" & _dateinsc & "',usermodif='" & _usermodif & "',datemodif='" & Now & "',sectbar='" & funcOutils.funcApos(_sectbar) & "' "
                'strSQL = strSQL + "WHERE code='" & strCodeAvo & "'"

                strSQL = "SET DATEFORMAT ymd UPDATE infomega SET francais = @francais, anglais = @anglais, autres = @autres, experience = @experience, " & _
                    "details = @details, mega = @mega, tarification = @tarification, art486 = @art486, art672 = @art672, art684 = @art684, " & _
                "districthab = @districthab, commentaire = @commentaire, dateinsc = @dateinsc, usermodif = @usermodif, datemodif = @datemodif, sectbar = @sectbar " & _
                "where code = @code "

            Else
                'strSQL = "set dateformat ymd INSERT INTO infomega(code,francais,anglais,autres,experience,details,mega,tarification,art486,art672,art684,"
                'strSQL = strSQL + "districthab,commentaire,dateinsc,usermodif,datemodif,sectbar)"
                'strSQL = strSQL + "VALUES('" & _code & "','" & _francais & "','" & _anglais & "','" & _autres & "'," & _experience & ",'" & funcOutils.funcApos(_details) & "',"
                'strSQL = strSQL + "'" & _mega & "','" & _tarification & "','" & _art486 & "','" & _art672 & "','" & _art684 & "','" & funcOutils.funcApos(_districthab) & "',"
                'strSQL = strSQL + "'" & funcOutils.funcApos(_commentaire) & "','" & _dateinsc & "','" & _usermodif & "','" & Now & "','" & funcOutils.funcApos(_sectbar) & "')"

                strSQL = "SET DATEFORMAT ymd INSERT INTO infomega (code,francais,anglais,autres,experience,details,mega,tarification,art486,art672,art684, " & _
                    "districthab,commentaire,dateinsc,usermodif,datemodif,sectbar) " & _
                "VALUES (@code, @francais, @anglais, @autres, @experience, @details, @mega, @tarification, @art486, @art672, @art684, @districthab, " & _
                " @commentaire, @dateinsc, @usermodif, @datemodif, @sectbar)"
            End If

            conn.ConnString = vstrConnCardAvo

            cmd = New SqlCommand(strSQL, conn.OpenConn())
            cmd.Parameters.AddWithValue("@code", _code.Trim)
            cmd.Parameters.AddWithValue("@francais", _francais.Trim)
            cmd.Parameters.AddWithValue("@anglais", _anglais.Trim)
            cmd.Parameters.AddWithValue("@autres", _autres.Trim)
            cmd.Parameters.AddWithValue("@experience", _experience)
            cmd.Parameters.AddWithValue("@details", _details.Trim)
            cmd.Parameters.AddWithValue("@mega", "O")
            cmd.Parameters.AddWithValue("@tarification", _tarification.Trim)
            cmd.Parameters.AddWithValue("@art486", _art486.Trim)
            cmd.Parameters.AddWithValue("@art672", _art672.Trim)
            cmd.Parameters.AddWithValue("@art684", _art684.Trim)
            cmd.Parameters.AddWithValue("@districthab", _districthab.Trim)
            cmd.Parameters.AddWithValue("@commentaire", _commentaire.Trim)
            cmd.Parameters.AddWithValue("@dateinsc", _dateinsc)
            cmd.Parameters.AddWithValue("@usermodif", _usermodif.Trim)
            cmd.Parameters.AddWithValue("@datemodif", Now)
            cmd.Parameters.AddWithValue("@sectbar", _sectbar.Trim)
           
            intResultat = cmd.ExecuteNonQuery()
        Catch ex As Exception
            funcOutils.subErrorMessage(Err.Number, Err.Description, Me.GetType.Name, MethodInfo.GetCurrentMethod.Name)
        Finally
            conn.CloseConn()

        End Try
    End Sub
    Public Function funcDeleteINfoMega(ByVal strCodeAvo As String)
        Dim conn As New ObjConn.ObjConn
        Try
            Dim cmd As SqlCommand
            Dim sql As String = ""
            Dim intResultat As Integer
            Dim strSQL As String = "DELETE FROM infomega WHERE code= @strCodeAvo "

            conn.ConnString = vstrConnCardAvo
            'Égal le command à la sentence SQl 
            cmd = New SqlCommand(strSQL, conn.OpenConn())
            cmd.Parameters.AddWithValue("@strCodeAvo", strCodeAvo)
            'Executer la command
            intResultat = cmd.ExecuteNonQuery()
            'MsgBox("Supprimé!")          

            cmd.Connection.Close()
            cmd.Dispose()
            Return True
        Catch ex As Exception
            funcOutils.subErrorMessage(Err.Number, Err.Description, Me.GetType.Name, MethodInfo.GetCurrentMethod.Name)
            Return False
        Finally
            conn.CloseConn()
        End Try
    End Function


    ''' <summary>
    ''' Function UPDATE MegaNon sur Avocats(StrCodeAvocat)
    ''' </summary>
    Public Function FuncUpdateMegaNon(ByVal StrCode As String) As Boolean
        Dim objConn As New ObjConn.ObjConn(vstrConnCardAvo)
        Dim strSQL As String = ""
        'maj table 


        strSQL = "UPDATE infomega SET mega = 'N' where code = '" & StrCode & "' "

        Try
            objConn.ExecuteSql(strSQL) 'sauvegarder les donnes dans la table adresse
            Return True
        Catch ex As Exception
            funcOutils.subErrorMessage(Err.Number, Err.Description, Me.GetType.Name, MethodInfo.GetCurrentMethod.Name)
            Return False
        Finally
            objConn.CloseConn()
            objConn = Nothing 'vider la variable
        End Try


    End Function


End Class
