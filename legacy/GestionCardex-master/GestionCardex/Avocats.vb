Imports System.Data
Imports System.Data.SqlClient
Imports System.Reflection

Partial Public Class Avocats

    Dim funcOutils As New FuncOutils

    Sub New()

    End Sub

    Sub Load(ByVal strCodeAvo As String)
        Dim conn As New ObjConn.ObjConn
        Dim dr As SqlDataReader
        Dim cmd As SqlCommand
        Dim strSQL As String = ""
        strSQL = "set dateformat ymd SELECT code,isnull(sectbar,'') as sectbar,mega,nom,prenom,actpass,dateinscbarr,payable,adrcour,isnull(adrnonpay,0) as adrnonpay,codebar,comm,"
        strSQL = strSQL + "isnull(datemodif,'2001/01/01') as datemodif,isnull(nas,'') as nas,depodirect,codeusager,motpasse1,motpasse2,factweb,confweb,isnull(villeref,'') as villeref,"
        strSQL = strSQL + "isnull(usermodif,'') as usermodif,surveil,isnull(neq,'') as neq "
        strSQL = strSQL + "FROM avocats WHERE code= @strCodeAvo"

        Try
            conn.ConnString = vstrConnCardAvo

            cmd = New SqlCommand(strSQL, conn.OpenConn())
            cmd.Parameters.AddWithValue("@strCodeAvo", strCodeAvo)
            'Executer la command et assigne le contenu au recordset
            dr = cmd.ExecuteReader()

            '**Lire le recordset 
            If dr.Read = True Then

                _code = dr("code").ToString.Trim
                _sectbar = dr("sectbar").ToString.Trim
                If IsDBNull(dr("mega")) = True Then _mega = "N" Else _mega = dr("mega").ToString.Trim
                _nom = dr("nom").ToString.Trim
                _prenom = dr("prenom").ToString.Trim
                _actpass = dr("actpass").ToString.Trim
                _dateinscbarr = dr("dateinscbarr").ToString.Trim
                _payable = dr("payable").ToString.Trim
                _adrcour = dr("adrcour").ToString.Trim
                _adrnonpay = dr("adrnonpay").ToString.Trim
                _codebar = dr("codebar").ToString.Trim
                _comm = dr("comm").ToString.Trim
                _datemodif = dr("datemodif")
                _nas = dr("nas").ToString.Trim
                _depodirect = dr("depodirect").ToString.Trim
                If IsDBNull(dr("codeusager")) = True Then _codeusager = "" Else _codeusager = dr("codeusager").ToString.Trim
                If IsDBNull(dr("motpasse1")) = True Then _motpasse1 = "" Else _motpasse1 = dr("motpasse1").ToString.Trim
                If IsDBNull(dr("motpasse2")) = True Then _motpasse2 = "" Else _motpasse2 = dr("motpasse2").ToString.Trim
                If dr("factweb").ToString.Trim = "" Then _factweb = "N" Else _factweb = dr("factweb").ToString.Trim 'ajout "" en cas que le champ est vide "" 
                If dr("confweb").ToString.Trim = "" Then _confweb = "N" Else _confweb = dr("confweb").ToString.Trim 'ajout "" en cas que le champ est vide "" 
                _villeref = dr("villeref").ToString.Trim
                _usermodif = dr("usermodif").ToString.Trim
                _surveil = dr("surveil").ToString.Trim

                '_neq = dr("neq")

            End If
            cmd.Connection.Close()
        Catch ex As Exception
            funcOutils.subErrorMessage(Err.Number, Err.Description, Me.GetType.Name, MethodInfo.GetCurrentMethod.Name)
        Finally
            conn.CloseConn()
        End Try



    End Sub

    Sub Save(ByVal strCodeAvo As String, ByVal strOpt As String)
        Dim conn As New ObjConn.ObjConn
        Dim strSQL As String = ""
        Dim cmd As SqlCommand
        Dim intResultat As Integer

        Try

            If strOpt = "avocat" Then
                If strCodeAvo <> "" Then 'MODFIFY AVOCAT
                    'strSQL = "set dateformat ymd UPDATE avocats SET code='" & _code & "',mega='" & _mega & "', nom='" & _nom & "',prenom='" & _prenom & "',"
                    'strSQL = strSQL + "actpass='" & _actpass & "',dateinscbarr='" & _dateinscbarr & "',payable='" & _payable & "', adrcour=" & _adrcour & ","
                    'strSQL = strSQL + "adrnonpay=" & _adrnonpay & ",codebar='" & _codebar & "',comm='" & _comm & "',datemodif='" & _datemodif & "',"
                    'strSQL = strSQL + "nas='" & _nas & "',depodirect='" & _depodirect & "',factweb='" & _factweb & "',usermodif='" & _usermodif & "' "
                    'strSQL = strSQL + "WHERE code='" & strCodeAvo & "'"


                    strSQL = "set dateformat ymd UPDATE avocats SET mega = @mega, nom = @nom, prenom = @prenom, actpass = @actpass, dateinscbarr = @dateinscbarr, " & _
                        " payable = @payable, adrcour = @adrcour, adrnonpay = @adrnonpay, codebar = @codebar, comm = @comm, datemodif = @datemodif, nas = @nas, depodirect = @depodirect, " & _
                        " factweb = @factweb, motpasse1 = @motpasse1, motpasse2 = @motpasse2,  usermodif = @usermodif where code= @code "

                    conn.ConnString = vstrConnCardAvo

                    cmd = New SqlCommand(strSQL, conn.OpenConn())
                    cmd.Parameters.AddWithValue("@mega", _mega.Trim)
                    cmd.Parameters.AddWithValue("@nom", _nom.Trim)
                    cmd.Parameters.AddWithValue("@prenom", _prenom.Trim)
                    cmd.Parameters.AddWithValue("@actpass", _actpass.Trim)
                    cmd.Parameters.AddWithValue("@dateinscbarr", _dateinscbarr.Trim)
                    cmd.Parameters.AddWithValue("@payable", _payable.Trim)
                    cmd.Parameters.AddWithValue("@adrcour", _adrcour)
                    cmd.Parameters.AddWithValue("@adrnonpay", _adrnonpay)
                    cmd.Parameters.AddWithValue("@codebar", _codebar.Trim)
                    cmd.Parameters.AddWithValue("@comm", _comm.Trim)
                    cmd.Parameters.AddWithValue("@datemodif", _datemodif)
                    cmd.Parameters.AddWithValue("@nas", _nas.Trim)
                    cmd.Parameters.AddWithValue("@depodirect", _depodirect.Trim)
                    cmd.Parameters.AddWithValue("@factweb", _factweb.Trim)
                    cmd.Parameters.AddWithValue("@usermodif", _usermodif.Trim)
                    cmd.Parameters.AddWithValue("@code", _code.Trim)
                    cmd.Parameters.AddWithValue("@motpasse1", _motpasse1)
                    cmd.Parameters.AddWithValue("@motpasse2", _motpasse2)


                    'Executer la command
                    intResultat = cmd.ExecuteNonQuery()


                Else 'SQL ok 'NEW AVOCAT
                    'strSQL = "set dateformat ymd INSERT INTO avocats(code,sectbar,mega,nom,prenom,actpass,dateinscbarr,payable,adrcour,adrnonpay,codebar,comm,"
                    'strSQL = strSQL + "datemodif,nas,depodirect,codeusager,motpasse1,motpasse2,factweb,confweb,villeref,usermodif,surveil,neq) "
                    'strSQL = strSQL + "VALUES('" & _code & "','','" & _mega & "','" & funcOutils.funcApos(_nom) & "','" & funcOutils.funcApos(_prenom) & "',"
                    'strSQL = strSQL + "'" & _actpass & "','" & _dateinscbarr & "','" & _payable & "',0,0,"
                    'strSQL = strSQL + "'" & _codebar & "','" & funcOutils.funcApos(_comm) & "','" & _datemodif & "','" & _nas & "','" & _depodirect & "',"
                    'strSQL = strSQL + "'','','','" & _factweb & "','','','" & _usermodif & "','','')"

                    strSQL = "SET DATEFORMAT ymd INSERT INTO avocats (code,sectbar,mega,nom,prenom,actpass,dateinscbarr,payable,adrcour,adrnonpay,codebar,comm, " & _
                    "datemodif,nas,depodirect,codeusager,motpasse1,motpasse2,factweb,confweb,villeref,usermodif,surveil,neq) " & _
                    "VALUES (@code, @sectbar, @mega, @nom, @prenom, @actpass, @dateinscbarr, @payable, @adrcour, @adrnonpay, @codebar, @comm, " & _
                    " @datemodif, @nas, @depodirect, @codeusager, @motpasse1, @motpasse2, @factweb, @confweb, @villeref, @usermodif, @surveil, @neq )"

                    conn.ConnString = vstrConnCardAvo

                    cmd = New SqlCommand(strSQL, conn.OpenConn())
                    cmd.Parameters.AddWithValue("@code", _code.Trim)
                    cmd.Parameters.AddWithValue("@sectbar", "")
                    cmd.Parameters.AddWithValue("@mega", _mega.Trim)
                    cmd.Parameters.AddWithValue("@nom", _nom.Trim)
                    cmd.Parameters.AddWithValue("@prenom", _prenom.Trim)
                    cmd.Parameters.AddWithValue("@actpass", _actpass.Trim)
                    cmd.Parameters.AddWithValue("@dateinscbarr", _dateinscbarr.Trim)
                    cmd.Parameters.AddWithValue("@payable", _payable.Trim)
                    cmd.Parameters.AddWithValue("@adrcour", 0)
                    cmd.Parameters.AddWithValue("@adrnonpay", 0)
                    cmd.Parameters.AddWithValue("@codebar", _codebar.Trim)
                    cmd.Parameters.AddWithValue("@comm", _comm.Trim)
                    cmd.Parameters.AddWithValue("@datemodif", _datemodif)
                    cmd.Parameters.AddWithValue("@nas", _nas.Trim)
                    cmd.Parameters.AddWithValue("@depodirect", _depodirect.Trim)
                    cmd.Parameters.AddWithValue("@codeusager", _code.Trim)
                    cmd.Parameters.AddWithValue("@motpasse1", _motpasse1)
                    'If _motpasse1 Is Nothing Then cmd.Parameters.AddWithValue("@motpasse1", "      ") Else cmd.Parameters.AddWithValue("@motpasse1", _motpasse1)
                    cmd.Parameters.AddWithValue("@motpasse2", _motpasse2)
                    'If _motpasse2 Is Nothing Then cmd.Parameters.AddWithValue("@motpasse2", "      ") Else cmd.Parameters.AddWithValue("@motpasse2", _motpasse2)
                    cmd.Parameters.AddWithValue("@factweb", _factweb.Trim)
                    cmd.Parameters.AddWithValue("@confweb", "N") '****** Donne le valeur N car insert nouveau avocat ********
                    cmd.Parameters.AddWithValue("@villeref", "")
                    cmd.Parameters.AddWithValue("@usermodif", _usermodif.Trim)
                    cmd.Parameters.AddWithValue("@surveil", "")
                    cmd.Parameters.AddWithValue("@neq", "")


                    'Executer la command
                    intResultat = cmd.ExecuteNonQuery()

                End If
            ElseIf strOpt = "web" Then
                'strSQL = "set dateformat ymd UPDATE avocats SET sectbar='" & _sectbar & "',mega='" & _mega & "',codeusager='" & _codeusager & "',"
                'strSQL = strSQL + "datemodif='" & _datemodif & "',motpasse1='" & _motpasse1 & "',"
                'strSQL = strSQL + "motpasse2='" & _motpasse2 & "', factweb='" & _factweb & "', confweb='" & _confweb & "',"
                'strSQL = strSQL + "villeref='" & funcOutils.funcApos(_villeref) & "',usermodif='" & _usermodif & "' "
                'strSQL = strSQL + "WHERE code='" & strCodeAvo & "'"


                strSQL = "set dateformat ymd UPDATE avocats SET sectbar = @sectbar, mega = @mega, codeusager = @codeusager, datemodif = @datemodif, " & _
                    " factweb = @factweb, confweb = @confweb, villeref = @villeref,  usermodif = @usermodif, motpasse1 = @motpasse1, motpasse2 = @motpasse2 where code = @code "


                conn.ConnString = vstrConnCardAvo

                cmd = New SqlCommand(strSQL, conn.OpenConn())
                cmd.Parameters.AddWithValue("@code", _code.Trim)
                cmd.Parameters.AddWithValue("@sectbar", _sectbar.Trim)
                cmd.Parameters.AddWithValue("@mega", _mega.Trim)
                cmd.Parameters.AddWithValue("@codeusager", _codeusager.Trim)
                cmd.Parameters.AddWithValue("@datemodif", _datemodif)
                cmd.Parameters.AddWithValue("@factweb", _factweb.Trim)
                cmd.Parameters.AddWithValue("@confweb", _confweb.Trim)
                '*******Condition pour que ville peut étre vide ***********
                If _villeref = Nothing Then
                    cmd.Parameters.AddWithValue("@villeref", "") '***vide " " *******
                Else
                    cmd.Parameters.AddWithValue("@villeref", _villeref.Trim) '****valeur de ville *****
                End If

                cmd.Parameters.AddWithValue("@usermodif", _usermodif.Trim)
                cmd.Parameters.AddWithValue("@motpasse1", _motpasse1.Trim)
                cmd.Parameters.AddWithValue("@motpasse2", _motpasse2.Trim)

                'Executer la command
                intResultat = cmd.ExecuteNonQuery()
            End If


        Catch ex As Exception
            funcOutils.subErrorMessage(Err.Number, Err.Description, Me.GetType.Name, MethodInfo.GetCurrentMethod.Name)
        Finally
            conn.CloseConn()
        End Try


    End Sub

    Function funcSavePwd(ByVal strCodeAvo As String, ByVal strPwd1 As String, ByVal strPwd2 As String, ByVal struser As String) As Boolean
        Dim conn As New ObjConn.ObjConn
        Dim strSQL As String = ""
        Dim cmd As SqlCommand
        Dim intResultat As Integer
        Dim bReturn As Boolean = False
        Try

            strSQL = "set dateformat ymd UPDATE avocats SET  datemodif = @datemodif, motpasse1= @motpasse1, motpasse2 = @motpasse2, usermodif = @usermodif  where code= @code"

            conn.ConnString = vstrConnCardAvo

            cmd = New SqlCommand(strSQL, conn.OpenConn())

            cmd.Parameters.AddWithValue("@datemodif", Now)
            cmd.Parameters.AddWithValue("@motpasse1", strPwd1)
            cmd.Parameters.AddWithValue("@motpasse2", strPwd2)
            cmd.Parameters.AddWithValue("@code", strCodeAvo)
            cmd.Parameters.AddWithValue("@usermodif", struser)
            'Executer la command

            intResultat = cmd.ExecuteNonQuery()
            bReturn = True

            Return bReturn
        Catch ex As Exception
            funcOutils.subErrorMessage(Err.Number, Err.Description, Me.GetType.Name, MethodInfo.GetCurrentMethod.Name)
            Return bReturn
        Finally
            conn.CloseConn()
        End Try

    End Function

    Public Function FuncGetAvoCode(ByVal strtype As String, ByVal bJordan As Boolean) As String
        Dim conn As New ObjConn.ObjConn
        Dim dr As SqlDataReader
        Dim cmd As SqlCommand
        Dim strReturn As String = ""
        'Dim strSQL As String = "SELECT  max( code ) as code    FROM [CardAvo].[dbo].[Avocats] where code like @strcode "
        Dim strSQL As String = "SELECT  max( code ) as code FROM Avocats where code like @strcode "

        Dim cp As Integer = 0
        Try
            conn.ConnString = vstrConnCardAvo

            cmd = New SqlCommand(strSQL, conn.OpenConn())
            If bJordan = False Then 'SINON JORDAN
                If strtype = "A" Then 'SI C'EST AVOCAT
                    cmd.Parameters.AddWithValue("@Strcode", strtype.Trim & "0%")
                Else 'SI C'EST NOTAIRE OU PRIVÉ
                    cmd.Parameters.AddWithValue("@Strcode", strtype.Trim & "%")
                End If
            Else
                'C'EST JORDAN
                cmd.Parameters.AddWithValue("@Strcode", strtype.Trim & "1%")
            End If

            'Executer la command et assigne le contenu au recordset
            dr = cmd.ExecuteReader()

            '**Lire le recordset 
            If dr.Read = True Then
                If IsDBNull(dr("code")) = True Then
                    strReturn = 0
                Else
                    cp = dr("code").ToString.Substring(1, Len(dr("code")) - 1)
                    cp = cp + 1
                    strReturn = strtype & funcOutils.funcRemplirFiveZero(cp.ToString.Trim)

                End If

            End If
            cmd.Connection.Close()
            Return strReturn
        Catch ex As Exception
            funcOutils.subErrorMessage(Err.Number, Err.Description, Me.GetType.Name, MethodInfo.GetCurrentMethod.Name)
            Return -1
        Finally
            conn.CloseConn()
        End Try
        Return String.Empty
    End Function

End Class