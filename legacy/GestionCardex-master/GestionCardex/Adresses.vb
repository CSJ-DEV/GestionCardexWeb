Imports System.Data
Imports System.Data.SqlClient
Imports System.Reflection

Partial Public Class Adresses
    Private _datemodif As Date
    Private _usermodif As String
    Property datemodif() As Date
        Get
            Return _datemodif
        End Get
        Set(ByVal value As Date)
            _datemodif = value
        End Set
    End Property
    Property usermodif() As String
        Get
            Return _usermodif
        End Get
        Set(ByVal value As String)
            _usermodif = value
        End Set
    End Property


    Dim funcOutils As New FuncOutils
    Private _adremail As String
    Sub New()

    End Sub
    
    Sub Load(ByVal strCodeAvo As String, ByVal iNoseq As Integer)
        Dim objConn As New ObjConn.ObjConn(vstrConnCardAvo) 'connexion a la table Cardavo
        Dim myread As SqlClient.SqlDataReader = Nothing
        Dim strSQL As String = ""

        strSQL = "set dateformat ymd SELECT code,adresse,ville,province,codepostal,telephone,telephone2,fax,adremail,"
        strSQL = strSQL + "noseq,adresse2,adresse3,CASE courant WHEN 'O' THEN 'C' ELSE '' END as courant,  dateadr,"
        strSQL = strSQL + "isnull(poste1,'') as poste1,isnull(poste2,'') as poste2, RowID, datemodif, usermodif FROM adresses WHERE code='" & strCodeAvo & "' and noseq=" & iNoseq
        objConn.ExecuteSql(strSQL, myread)

        Try
            myread.Read()
            _code = myread("code").ToString.Trim
            _adresse = myread("adresse").ToString.Trim
            _ville = myread("ville").ToString.Trim
            _province = myread("province").ToString.Trim
            _codepostal = myread("codepostal").ToString.Trim
            _telephone = myread("telephone").ToString.Trim
            _telephone2 = myread("telephone2").ToString.Trim
            _fax = myread("fax").ToString.Trim
            _adremail = myread("adremail").ToString.Trim
            _noseq = myread("noseq").ToString.Trim
            _adresse2 = myread("adresse2").ToString.Trim
            _adresse3 = myread("adresse3").ToString.Trim
            _courant = myread("courant").ToString.Trim
            If IsDBNull(myread("dateadr")) = True Then _dateadr = Nothing Else _dateadr = myread("dateadr")
            _poste1 = myread.GetString(14).Trim
            _poste2 = myread.GetString(15).Trim
            _RowId = myread("RowID")
            If IsDBNull(myread("datemodif")) = True Then _datemodif = Nothing Else _datemodif = myread("datemodif").ToString.Trim
            If IsDBNull(myread("usermodif")) = True Then _usermodif = "" Else _usermodif = myread("usermodif").ToString.Trim
        Catch ex As Exception
            funcOutils.subErrorMessage(Err.Number, Err.Description, Me.GetType.Name, MethodInfo.GetCurrentMethod.Name)
        Finally
            myread.Close()
            myread = Nothing 'vide pour la prochaine lecture
            objConn.CloseConn() 'ferme la connexion
            objConn = Nothing
        End Try

    End Sub

    Public Function FuncSetcourantNbyAvocat(ByVal StrCode As String) As Boolean
        Dim objConn As New ObjConn.ObjConn(vstrConnCardAvo)
        Dim strSQL As String = ""
        'maj table 

        strSQL = "UPDATE adresses SET courant = 'N' where code = '" & StrCode & "'"

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

    Public Function FuncSetAdremail(ByVal StrCode As String, ByVal strEmail As String) As Boolean
        Dim objConn As New ObjConn.ObjConn(vstrConnCardAvo)
        Dim strSQL As String = ""
        'maj table 

        strSQL = "UPDATE adresses SET adremail = '" & strEmail & "' where code = '" & StrCode & "' AND courant = 'O'"

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

    Public Function FuncGetMaxSeq(ByVal Strcode As String) As Integer
        Dim conn As New ObjConn.ObjConn
        Dim dr As SqlDataReader
        Dim cmd As SqlCommand
        Dim iReturn As Integer
        Dim strSQL As String = "SELECT MAX(noseq) as MaxNoSeq FROM Adresses WHERE code= @Strcode "

        Try
            conn.ConnString = vstrConnCardAvo

            cmd = New SqlCommand(strSQL, conn.OpenConn())
            cmd.Parameters.AddWithValue("@Strcode", Strcode)
            'Executer la command et assigne le contenu au recordset
            dr = cmd.ExecuteReader()

            '**Lire le recordset 
            If dr.Read = True Then
                If IsDBNull(dr("MaxNoSeq")) = True Then
                    iReturn = 0
                Else
                    iReturn = dr("MaxNoSeq")
                End If

            End If
            cmd.Connection.Close()
            Return iReturn
        Catch ex As Exception
            funcOutils.subErrorMessage(Err.Number, Err.Description, Me.GetType.Name, MethodInfo.GetCurrentMethod.Name)
            Return -1
        Finally
            conn.CloseConn()
        End Try

    End Function

    Public Function FuncExistAdrCourant(ByVal Strcode As String) As Boolean
        Dim conn As New ObjConn.ObjConn
        Dim dr As SqlDataReader
        Dim cmd As SqlCommand
        Dim bReturn As Boolean
        Dim strSQL As String = "SELECT code FROM Adresses WHERE courant = 'O' AND code= @Strcode "

        Try
            conn.ConnString = vstrConnCardAvo

            cmd = New SqlCommand(strSQL, conn.OpenConn())
            cmd.Parameters.AddWithValue("@Strcode", Strcode)
            'Executer la command et assigne le contenu au recordset
            dr = cmd.ExecuteReader()

            '**Lire le recordset 
            If dr.Read = True Then
                If IsDBNull(dr("code")) = True Then
                    bReturn = False
                Else
                    bReturn = True
                End If

            End If
            cmd.Connection.Close()
            Return bReturn
        Catch ex As Exception
            funcOutils.subErrorMessage(Err.Number, Err.Description, Me.GetType.Name, MethodInfo.GetCurrentMethod.Name)
            Return True
        Finally
            conn.CloseConn()
        End Try

    End Function


    Public Function FuncdeleteAdr(ByVal growID As Guid) As Boolean
        Dim conn As New ObjConn.ObjConn
        'Dim objConn As New ObjConn.ObjConn(vstrConnCardAvo)
        Try
            Dim cmd As SqlCommand
            Dim intResultat As Integer
            Dim strSQL As String = "DELETE FROM Adresses WHERE ROWID = @ID"
            conn.ConnString = vstrConnCardAvo

            cmd = New SqlCommand(strSQL, conn.OpenConn())
            cmd.Parameters.AddWithValue("@ID", growID)
            'Executer la command
            intResultat = cmd.ExecuteNonQuery()
            'MsgBox("Supprimé!")
            cmd.Connection.Close()
            Return True
        Catch ex As Exception
            Return False
        Finally
            conn.CloseConn()

        End Try
    End Function

    'Sub update(ByVal strCodeAvo As String, Optional ByVal iNoSeq As Integer = 0)
    '    Dim objConn As New ObjConn.ObjConn(vstrConnCardAvo)
    '    Dim strSQL As String = ""
    '    Dim cmd As SqlCommand
    '    Dim intResultat As Integer
    '    'maj table 

    '    'strSQL = "set dateformat ymd UPDATE adresses SET adresse = '" & funcOutils.funcApos(_adresse) & "',"
    '    'strSQL = strSQL + "ville='" & funcOutils.funcApos(_ville) & "', "
    '    'strSQL = strSQL + "province='" & _province & "',"
    '    'strSQL = strSQL + "codepostal='" & _codepostal & "',"
    '    'strSQL = strSQL + "telephone='" & _telephone & "',"
    '    'strSQL = strSQL + "telephone2='" & _telephone2 & "',"
    '    'strSQL = strSQL + "fax='" & _fax & "',"
    '    'strSQL = strSQL + "adremail='" & _adremail & "',"
    '    'strSQL = strSQL + "noseq='" & _noseq & "',"
    '    'strSQL = strSQL + "adresse2='" & funcOutils.funcApos(_adresse2) & "',"
    '    'strSQL = strSQL + "adresse3='" & funcOutils.funcApos(_adresse3) & "',"
    '    'strSQL = strSQL + "courant='" & _courant & "',"
    '    'strSQL = strSQL + "dateadr='" & _dateadr & "',"
    '    'strSQL = strSQL + "poste1='" & _poste1 & "',"
    '    'strSQL = strSQL + "poste2='" & _poste2 & "',"
    '    'strSQL = strSQL + "usermodif='" & _usermodif & "',"
    '    'strSQL = strSQL + "datemodif='" & Now & "'"
    '    'strSQL = strSQL + " WHERE code= '" & strCodeAvo & "' and noseq = '" & iNoSeq & "'"
    '    'strSQL = "set dateformat ymd UPDATE adresses SET code,adresse,ville,province,codepostal,telephone,telephone2,fax,adremail,"
    '    'strSQL = strSQL + "noseq,adresse2,adresse3,courant,dateadr,poste1,poste2) "
    '    'strSQL = strSQL + "VALUES('" & _code & "'," & funcOutils.funcApos(_adresse) & ",'" & funcOutils.funcApos(_ville) & "','" & _province & "','" & _codepostal & "',"
    '    'strSQL = strSQL + "'" & _telephone & "','" & _telephone2 & "','" & _fax & "'," & _adremail & "'," '
    '    'strSQL = strSQL + _noseq & "','" & funcOutils.funcApos(_adresse2) & "','" & funcOutils.funcApos(_adresse3) & "','" & _courant & "','"
    '    'strSQL = strSQL + "'" & _dateadr & "','" & _poste1 & "','" & _poste2 & "',')"

    '    Try
    '        strSQL = "set dateformat ymd update adresses set adresse = @adresse, ville = @ville, province = @province, codepostal = @codepostal, " & _
    '       "telephone = @telephone, telephone2 = @telephone2, fax = @fax, adremail = @adremail, noseq = @noseq, adresse2 = @adresse2," & _
    '   "adresse3 = @adresse3, courant = @courant, dateadr = @dateadr, poste1 = @poste1, poste2 = @poste2, usermodif = @usermodif," & _
    '   "datemodif = @datemodif where code = @code and noseq = @noseq "

    '        'conn.ConnString = vgStrConn

    '        cmd = New SqlCommand(strSQL, objConn.OpenConn())
    '        cmd.Parameters.AddWithValue("@adresse", _adresse)
    '        cmd.Parameters.AddWithValue("@ville", _ville)
    '        cmd.Parameters.AddWithValue("@province", _province)
    '        cmd.Parameters.AddWithValue("@codepostal", _codepostal)
    '        cmd.Parameters.AddWithValue("@telephone", _telephone)
    '        cmd.Parameters.AddWithValue("@telephone2", _telephone2)
    '        cmd.Parameters.AddWithValue("@fax", _fax)
    '        cmd.Parameters.AddWithValue("@adremail", _adremail)
    '        cmd.Parameters.AddWithValue("@noseq", _noseq)
    '        cmd.Parameters.AddWithValue("@adresse2", _adresse2)
    '        cmd.Parameters.AddWithValue("@adresse3", _adresse3)
    '        cmd.Parameters.AddWithValue("@PROVINCE", _province)
    '        cmd.Parameters.AddWithValue("@courant", _courant)

    '        cmd.Parameters.AddWithValue("@poste1", _poste1)
    '        cmd.Parameters.AddWithValue("@poste2", _poste2)
    '        cmd.Parameters.AddWithValue("@usermodif", _usermodif)
    '        cmd.Parameters.AddWithValue("@datemodif", _datemodif)
    '        cmd.Parameters.AddWithValue("@code", _code)
    '        cmd.Parameters.AddWithValue("@noseq", iNoSeq)
    '        If _dateadr Is Nothing Then
    '            cmd.Parameters.AddWithValue("@dateadr", DBNull.Value)
    '        Else
    '            cmd.Parameters.AddWithValue("@dateadr", _dateadr)
    '        End If

    '        'Executer la command
    '        intResultat = cmd.ExecuteNonQuery()

    '        cmd.Connection.Close()
    '    Catch ex As Exception
    '        funcOutils.subErrorMessage(Err.Number, Err.Description, Me.GetType.Name, MethodInfo.GetCurrentMethod.Name)
    '    Finally
    '        objConn.CloseConn()
    '        objConn = Nothing 'vider la variable
    '    End Try

    'End Sub

    Sub Save(ByVal bIsNew As Boolean)
        Dim conn As New ObjConn.ObjConn
        Dim strSQL As String = ""
        Dim cmd As SqlCommand
        Dim intResultat As Integer
        Try
            'maj table 

            If bIsNew = False Then ' SI NE PAS NOUVELLE ADRESSE
                strSQL = "set dateformat ymd update adresses set adresse = @adresse, ville = @ville, province = @province, codepostal = @codepostal, " & _
               "telephone = @telephone, telephone2 = @telephone2, fax = @fax, adremail = @adremail, noseq = @noseq, adresse2 = @adresse2," & _
                   "adresse3 = @adresse3, courant = @courant, dateadr = @dateadr, poste1 = @poste1, poste2 = @poste2, usermodif = @usermodif," & _
                   "datemodif = @datemodif where code = @code and noseq = @noseq "
            Else
                strSQL = "set dateformat ymd INSERT INTO cardavo.dbo.Adresses (code,adresse,ville,province,codepostal,telephone,telephone2,fax,adremail, " & _
                "noseq,adresse2,adresse3,courant,dateadr,poste1,poste2,usermodif,datemodif) " & _
                " Values (@code, @adresse, @ville, @province, @codepostal, @telephone, @telephone2, @fax, @adremail, @noseq, @adresse2, @adresse3, @courant, @dateadr, @poste1, @poste2, @usermodif, @datemodif)"
            End If
            conn.ConnString = vstrConnCardAvo

            cmd = New SqlCommand(strSQL, conn.OpenConn())
            cmd.Parameters.AddWithValue("@adresse", _adresse.Trim)
            cmd.Parameters.AddWithValue("@ville", _ville.Trim)
            cmd.Parameters.AddWithValue("@province", _province.Trim)
            cmd.Parameters.AddWithValue("@codepostal", _codepostal.Trim)
            cmd.Parameters.AddWithValue("@telephone", _telephone.Trim)
            cmd.Parameters.AddWithValue("@telephone2", _telephone2.Trim)
            cmd.Parameters.AddWithValue("@fax", _fax.Trim)
            cmd.Parameters.AddWithValue("@adremail", _adremail.Trim)
            cmd.Parameters.AddWithValue("@adresse2", _adresse2.Trim)
            cmd.Parameters.AddWithValue("@adresse3", _adresse3.Trim)
            cmd.Parameters.AddWithValue("@courant", _courant.Trim)
            cmd.Parameters.AddWithValue("@poste1", _poste1.Trim)
            cmd.Parameters.AddWithValue("@poste2", _poste2.Trim)
            cmd.Parameters.AddWithValue("@usermodif", _usermodif.Trim)
            cmd.Parameters.AddWithValue("@datemodif", Now)
            cmd.Parameters.AddWithValue("@code", _code.Trim)
            cmd.Parameters.AddWithValue("@noseq", _noseq)
            If _dateadr Is Nothing Then
                cmd.Parameters.AddWithValue("@dateadr", DBNull.Value)
            Else
                cmd.Parameters.AddWithValue("@dateadr", _dateadr)
            End If

            'Executer la command
            intResultat = cmd.ExecuteNonQuery()

        Catch ex As Exception
            funcOutils.subErrorMessage(Err.Number, Err.Description, Me.GetType.Name, MethodInfo.GetCurrentMethod.Name)
        Finally
            conn.CloseConn()
        End Try

    End Sub

    ''' <summary>
    ''' Function UPDATE VilleRef sur Avocats(StrCodeAvocat)
    ''' </summary>
    Public Function FuncUpdateVilleref(ByVal StrCode As String) As Boolean
        Dim conn As New ObjConn.ObjConn
        Dim strSQL As String = ""
        Dim intResultat As Integer
        Dim cmd As SqlCommand

        'maj table 
        Try

            strSQL = "set dateformat ymd UPDATE avocats SET villeref = @villeref, adrcour = @adrcour  where code = @code"


            'strSQL = "UPDATE avocats SET villeref = '" & _ville & "', adrcour = " & _noseq & " where code = '" & StrCode & "'"
            'strSQL = "UPDATE avocats SET villeref = '" & _ville & "', adrcour = " & _noseq & " where code = '" & StrCode & "' and factweb = 'O' "


            conn.ConnString = vstrConnCardAvo

            cmd = New SqlCommand(strSQL, conn.OpenConn())
            cmd.Parameters.AddWithValue("@villeref", _ville.Trim)
            cmd.Parameters.AddWithValue("@adrcour", _noseq)
            cmd.Parameters.AddWithValue("@code", StrCode.Trim)


            'Executer la commande
            intResultat = cmd.ExecuteNonQuery()
            'MsgBox("Ajouté!")

            cmd.Connection.Close()

            Return True
        Catch ex As Exception
            funcOutils.subErrorMessage(Err.Number, Err.Description, Me.GetType.Name, MethodInfo.GetCurrentMethod.Name)
            Return False
        Finally
            conn.CloseConn()
            conn = Nothing 'vider la variable
        End Try


    End Function

End Class