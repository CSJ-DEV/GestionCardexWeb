Imports System.Data
Imports System.Data.SqlClient
Imports System.Reflection

Public Class InhPra
    Private _ID As Integer
    Dim funcOutils As New FuncOutils

    Property ID() As Integer
        Get
            Return _ID
        End Get
        Set(ByVal value As Integer)
            _ID = value
        End Set
    End Property

    Sub New()

    End Sub

    
    Sub Load(ByVal strCodeAvo As String)
        Dim objConn As New ObjConn.ObjConn(vstrConnCardAvo)
        Dim myread As SqlClient.SqlDataReader = Nothing
        Dim strSQL As String = ""

        strSQL = "set dateformat ymd SELECT code,datedeb,datefin,isnull(comm, '') as comm, id FROM inhpra WHERE code='" & strCodeAvo & "'"

        Try

            objConn.ExecuteSql(strSQL, myread)
            myread.Read()
            _code = myread("code").ToString.Trim
            _datedeb = myread("datedeb")
            _datefin = myread("datefin")
            _comm = myread("comm").ToString.Trim
        Catch ex As Exception
            funcOutils.subErrorMessage(Err.Number, Err.Description, Me.GetType.Name, MethodInfo.GetCurrentMethod.Name)
        Finally
            myread.Close()
            myread = Nothing
            objConn.CloseConn()
            objConn = Nothing
        End Try
    End Sub

    'Public Function FuncvalidateExist(ByVal StrcodeAvo As String, ByVal Ddeb As Date, ByVal Dfin As Date) As Boolean
    '    Dim conn As New ObjConn.ObjConn
    '    Dim cmd As SqlCommand
    '    Dim myread As SqlClient.SqlDataReader = Nothing
    '    Dim strSQL As String = "SELECT * FROM imhpra where datedeb = @Ddeb and datefin = @Dfin and code = @StrcodeAvo"
    '    Dim bReturn As Boolean = False
    '    Try
    '        conn.ConnString = vstrConnCardAvo

    '        cmd = New SqlCommand(strSQL, conn.OpenConn())
    '        cmd.Parameters.AddWithValue("@Ddeb", Ddeb)
    '        cmd.Parameters.AddWithValue("@Dfin", Dfin)
    '        cmd.Parameters.AddWithValue("@StrcodeAvo", StrcodeAvo)
    '        'Executer la command et assigne le contenu au recordset
    '        myread = cmd.ExecuteReader()

    '        If myread.Read = True Then
    '            bReturn = True
    '        End If
    '        cmd.Connection.Close()
    '        Return bReturn
    '    Catch ex As Exception
    '        Return False
    '    End Try
    'End Function

    Public Function FuncdeleteCommInh(ByVal StrcodeAvo As String, ByVal Strcommen As String) As Boolean
        Dim conn As New ObjConn.ObjConn
        Try
            Dim cmd As SqlCommand
            Dim sql As String = ""
            Dim intResultat As Integer
            Dim strSQL As String = "DELETE FROM inhpra WHERE code= @Code and comm like @Comm"
            conn.ConnString = vstrConnCardAvo

            cmd = New SqlCommand(strSQL, conn.OpenConn())
            cmd.Parameters.AddWithValue("@code", StrcodeAvo.Trim)
            cmd.Parameters.AddWithValue("@comm", Strcommen.Trim)
            'Executer la command
            intResultat = cmd.ExecuteNonQuery()
            'MsgBox("Supprimé!")
            cmd.Connection.Close()
            Return True
        Catch ex As Exception
            funcOutils.subErrorMessage(Err.Number, Err.Description, Me.GetType.Name, MethodInfo.GetCurrentMethod.Name)
            Return False
        Finally
            conn.CloseConn()
        End Try

        'Dim objConn As New ObjConn.ObjConn(vstrConnCardAvo)

        'Dim strSQL As String = ""
        ''maj table 

        'strSQL = "DELETE FROM inhpra WHERE code='" & StrcodeAvo & "' and comm='" & funcOutils.funcApos(Strcommen) & "' "

        'Try
        '    objConn.ExecuteSql(strSQL)
        '    Return True

        'Catch ex As Exception
        '    funcOutils.subErrorMessage(Err.Number, Err.Description, Me.GetType.Name, MethodInfo.GetCurrentMethod.Name)
        '    Return False
        'Finally
        '    objConn.CloseConn()
        '    objConn = Nothing 'vider la variable
        'End Try


    End Function

    Public Function funcValidateDatePeriode(ByVal strCode As String, ByVal dDateDebut As Date, ByVal dDateFin As Date, ByVal iId As Integer) As Boolean
        Dim conn As New ObjConn.ObjConn
        Dim bReturn As Boolean
        Try
            Dim dr As SqlDataReader
            Dim cmd As SqlCommand
            Dim strSQL As String = "SELECT  id from inhpra WHERE code = @code AND Id <> @Id AND ((DateDeb <= @DDebut AND DateFin >= @DDebut) OR " & _
                " (DateDeb <= @DFIN AND DateFin >= @Dfin))"

            conn.ConnString = vstrConnCardAvo
            'Égal le command à la sentence SQl 
            cmd = New SqlCommand(strSQL, conn.OpenConn())
            cmd.Parameters.AddWithValue("@code", strCode.Trim)
            cmd.Parameters.AddWithValue("@Id", iId)
            cmd.Parameters.AddWithValue("@DDebut", dDateDebut)
            cmd.Parameters.AddWithValue("@DFIN", dDateFin)
            'Executer la command
            dr = cmd.ExecuteReader()
            '**Lire le recordset 
            While dr.Read = True
                If IsDBNull(dr("Id")) = True Then
                    bReturn = False
                Else
                    bReturn = True
                End If
            End While

            cmd.Connection.Close()
            cmd.Dispose()
            Return bReturn
        Catch ex As Exception
            funcOutils.subErrorMessage(Err.Number, Err.Description, Me.GetType.Name, MethodInfo.GetCurrentMethod.Name)
            Return False
        Finally
            conn.CloseConn()
        End Try
    End Function

    Sub Save(ByVal bnew As Boolean)
        Dim conn As New ObjConn.ObjConn
        Dim strSQL As String = ""
        Dim cmd As SqlCommand
        Dim intResultat As Integer

        Try

            If bnew = False Then
                ''strSQL = "set dateformat ymd UPDATE cardavo.dbo.inhpra set datedeb='" & _datedeb & "',"
                'strSQL = "set dateformat ymd UPDATE inhpra set datedeb='" & _datedeb & "',"
                'strSQL = strSQL + "datefin='" & _datefin & "',comm='" & funcOutils.funcApos(_comm) & "' "
                'strSQL = strSQL + "WHERE id= " & _ID

                strSQL = "SET DATEFORMAT ymd UPDATE inhpra SET datedeb = @datedeb, datefin = @datefin, comm = @comm " & _
                    "where id = @id "

            Else
                'strSQL = "set dateformat ymd INSERT INTO cardavo.dbo.inhpra(code,datedeb,datefin,comm) "
                'strSQL = "set dateformat ymd INSERT INTO inhpra(code,datedeb,datefin,comm) "
                'strSQL = strSQL + "VALUES('" & _code & "','" & _datedeb & "','" & _datefin & "','" & funcOutils.funcApos(_comm) & "')"

                strSQL = "SET DATEFORMAT ymd INSERT INTO inhpra (code,datedeb,datefin,comm )" & _
                    "VALUES (@code,@datedeb, @datefin, @comm)"


            End If

            conn.ConnString = vstrConnCardAvo

            cmd = New SqlCommand(strSQL, conn.OpenConn())

            If bnew = False Then
                cmd.Parameters.AddWithValue("@id", _ID)
            Else
                cmd.Parameters.AddWithValue("@code", _code.Trim)
            End If

            cmd.Parameters.AddWithValue("@datedeb", _datedeb)
            cmd.Parameters.AddWithValue("@datefin", _datefin)
            cmd.Parameters.AddWithValue("@comm", _comm.Trim)





            intResultat = cmd.ExecuteNonQuery()
        Catch ex As Exception
            funcOutils.subErrorMessage(Err.Number, Err.Description, Me.GetType.Name, MethodInfo.GetCurrentMethod.Name)
        Finally
            conn.CloseConn()

        End Try
    End Sub

    Protected Overrides Sub Finalize()
        MyBase.Finalize()
    End Sub
End Class


