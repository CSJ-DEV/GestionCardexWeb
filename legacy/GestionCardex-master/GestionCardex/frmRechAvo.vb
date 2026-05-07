Imports System.Reflection
Imports System
Imports System.Diagnostics.Process
Imports System.Data.SqlClient

Public Class frmRechAvo
    Dim funcOutils As New FuncOutils

    Private Sub btnCardex_Click(sender As System.Object, e As System.EventArgs) Handles btnCardex.Click
        Dim frmAvocat As New frmAvocat

        Me.Hide()
        frmAvocat.Show()
    End Sub

    Private Sub btnFermer_Click(sender As System.Object, e As System.EventArgs) Handles btnFermer.Click
        End
    End Sub

    Private Sub btnNouvRech_Click(sender As System.Object, e As System.EventArgs) Handles btnNouvRech.Click
        EffacRech()
        gCodeAvo = ""

    End Sub
    '*******************************
    'Bouton Ouvrir
    '*******************************
    Private Sub btnOuvrir_Click(sender As System.Object, e As System.EventArgs) Handles btnOuvrir.Click
        Dim frmAvocat As New frmAvocat

        If dgvRech.CurrentRow.Cells(0).Value <> Nothing Then
            gCodeAvo = dgvRech.CurrentRow.Cells(0).Value
            If MsgBox("Désirez-vous garder cette recherche?", vbYesNo + vbInformation + vbDefaultButton2, "Recherche") = vbNo Then
                EffacRech()
            End If
            frmAvocat.Show()
            Me.Hide()
        Else
            MsgBox("Vous n'avez pas sélectionné de ligne !", vbCritical, "Donnée manquante")
        End If

    End Sub


    Private Sub btnRech_Click(sender As System.Object, e As System.EventArgs) Handles btnRech.Click
        If cboCodeAvo.Text = "" And cboNomAvo.Text = "" Then
            MsgBox("Vous devez entrer des paramètres avant d'effectuer la recherche", vbOKOnly, "Recherche")
            Exit Sub
        End If

        If cboNomAvo.SelectedValue <> Nothing Then
            cboNomAvo.Text = funcOutils.funcApos(cboNomAvo.SelectedValue)
            RechAvo(cboNomAvo.Text, "", Chktous.Checked)
        ElseIf cboNomAvo.Text <> "" Then
            cboNomAvo.Text = funcOutils.funcApos(cboNomAvo.Text)
            RechAvo(cboNomAvo.Text, "", Chktous.Checked)
        Else
            RechAvo("", cboCodeAvo.Text, Chktous.Checked)
            If dgvRech.RowCount > 0 Then
                btnOuvrir.Focus()
            End If
        End If
    End Sub

    ''Valide le code avocat
    'Private Sub cboCodeAvo_KeyPress(sender As Object, e As System.Windows.Forms.KeyPressEventArgs) Handles cboCodeAvo.KeyPress
    '    'If Asc(e.KeyChar) >= 97 And Asc(e.KeyChar) <= 122 Then
    '    '    e.KeyChar = Chr(Asc(e.KeyChar) - 32)
    '    'End If
    'End Sub

    Private Sub cboNomAvo_LostFocus(sender As Object, e As System.EventArgs) Handles cboNomAvo.LostFocus
        If cboNomAvo.Text <> "" Then
            StrConv(cboNomAvo.Text, VbStrConv.ProperCase)
        End If
    End Sub

    Private Sub dgvRech_DoubleClick(sender As Object, e As System.EventArgs) Handles dgvRech.DoubleClick
        Dim frmAvocat As New frmAvocat

        gCodeAvo = dgvRech.CurrentRow.Cells(0).Value
        If MsgBox("Désirez-vous garder cette recherche?", vbYesNo + vbInformation + vbDefaultButton2, "Recherche") = vbNo Then
            EffacRech()
        End If
        frmAvocat.Show()
        Me.Hide()
    End Sub

    Private Sub frmRechAvo_FormClosing(sender As Object, e As System.Windows.Forms.FormClosingEventArgs) Handles Me.FormClosing
        End
    End Sub

    '********************************
    'Recherche code avocat
    '********************************
    Private Sub frmRechAvo_Load(sender As System.Object, e As System.EventArgs) Handles MyBase.Load
        funcOutils.funcRemplirCombo(cboCodeAvo, "Code")
        funcOutils.funcRemplirCombo(cboNomAvo, "Avocat")
        cboCodeAvo.Focus()
        gCodeAvo = ""
    End Sub

    '************************
    'effacer recherche
    '************************
    Private Sub EffacRech()
        cboCodeAvo.Text = ""
        cboCodeAvo.SelectedValue = ""
        cboCodeAvo.Enabled = True
        cboNomAvo.Text = ""
        cboNomAvo.SelectedValue = ""
        cboNomAvo.Enabled = True
        dgvRech.DataSource = ""
        btnRech.Enabled = True
        btnNouvRech.Enabled = False
        btnOuvrir.Enabled = False
        Me.AcceptButton = btnRech
        cboCodeAvo.Focus()
        Chktous.Checked = False
        Me.Text = "Recherche avocats/notaires"
    End Sub

    Private Sub RechAvo(pstrnomavo As String, pstrcodeavo As String, btous As Boolean)
        Dim dt As New DataTable
        Dim strSql As String = ""

        strSql = "select avocats.code, rtrim(nom) as nom, rtrim(prenom) as prenom, rtrim(adresses.ville) as ville, CASE factweb WHEN 'O' THEN 'O' ELSE 'N' END as factweb,"
        strSql = strSql + " CASE depodirect WHEN 'O' THEN 'O' ELSE 'N' END as depodirect, CASE payable WHEN 'O' THEN 'O' ELSE 'N' END as payable,"
        strSql = strSql + "CASE actpass WHEN 'A' THEN 'A' ELSE 'P' END as actpass FROM dbo.Avocats LEFT OUTER JOIN dbo.Adresses ON dbo.Avocats.code = dbo.Adresses.code "
        If pstrnomavo <> "" Then
            strSql = strSql + "where  upper(rtrim(avocats.nom)) + ' ' + upper(rtrim(avocats.prenom)) like '%" & funcOutils.funcConvertAccent(pstrnomavo) & "%' "
        Else
            strSql = strSql + "where avocats.code like '" & pstrcodeavo & "%' "
        End If
        If btous = True Then
            strSql = strSql + " and (courant = 'O' or ville is NULL OR (courant = 'N' AND ville is not null) ) "
        Else
            strSql = strSql + " and (courant = 'O' ) "
        End If
        strSql = strSql + " order by nom,prenom, avocats.code"
        Try
            Dim da As New SqlDataAdapter(strSql, vstrConnCardAvo)
            da.Fill(dt)
            dgvRech.DataSource = dt
            If dt.Rows.Count > 0 Then
                dgvRech.Columns("code").HeaderText = "Code"
                dgvRech.Columns("nom").HeaderText = "Nom"
                dgvRech.Columns("prenom").HeaderText = "Prénom"
                dgvRech.Columns("ville").HeaderText = "Ville"
                dgvRech.Columns("factweb").HeaderText = "WEB"
                dgvRech.Columns("depodirect").HeaderText = "Dépôt"
                dgvRech.Columns("payable").HeaderText = "Payable"
                dgvRech.Columns("actpass").HeaderText = "Actif"
                dgvRech.Columns("code").Width = 90
                dgvRech.Columns("nom").Width = 220
                dgvRech.Columns("prenom").Width = 200
                dgvRech.Columns("ville").Width = 240
                dgvRech.Columns("factweb").Width = 60
                dgvRech.Columns("depodirect").Width = 70
                dgvRech.Columns("payable").Width = 80
                dgvRech.Columns("actpass").Width = 60
                dgvRech.Columns("code").DefaultCellStyle.Alignment = DataGridViewContentAlignment.MiddleCenter
                dgvRech.Columns("factweb").DefaultCellStyle.Alignment = DataGridViewContentAlignment.MiddleCenter
                dgvRech.Columns("depodirect").DefaultCellStyle.Alignment = DataGridViewContentAlignment.MiddleCenter
                dgvRech.Columns("payable").DefaultCellStyle.Alignment = DataGridViewContentAlignment.MiddleCenter
                dgvRech.Columns("actpass").DefaultCellStyle.Alignment = DataGridViewContentAlignment.MiddleCenter

                btnNouvRech.Enabled = True
                'btnRech.Enabled = False
                btnOuvrir.Enabled = True
                cboCodeAvo.SelectedValue = ""
                'cboCodeAvo.Enabled = False
                cboNomAvo.SelectedValue = ""
                'cboNomAvo.Enabled = False
                'Me.AcceptButton = btnOuvrir

                Me.Text = "Résultat de la recherche : " & dt.Rows.Count & " enregistrement(s) trouvé(s)"

            Else
                MsgBox("Aucun résultat, vérifiez l'orthographe du nom de famille, révisez le code d'avocat ou créez un code pour cet avocat/notaire!", vbInformation, "Aucun résultat")
                btnNouvRech.Enabled = True
                btnRech.Enabled = False
            End If
        Catch ex As Exception
            funcOutils.subErrorMessage(Err.Number, Err.Description, Me.GetType.Name, MethodInfo.GetCurrentMethod.Name)
        End Try

    End Sub

  
End Class