Public Class frmMotPasse

    Dim funcOutils As New FuncOutils

    Private Sub frmMotPasse_Load(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles MyBase.Load
        Dim nomPoste As String

        vgStrLogin = Environment.UserName
        nomPoste = My.Computer.Name
        If funcOutils.funcGetUserName(vgStrLogin, nomPoste) = True Then
            txtMotPasse.Select()
        Else
            txtNomUtil.Select()
        End If
    End Sub

    'Bouton ok, valide le mot de passe
    Private Sub btnOk_Click(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles btnOk.Click
        If txtNomUtil.Text <> "" Then
            If txtMotPasse.Text <> "" Then
                funcOutils.funcGetPermissionUtil(txtNomUtil.Text.Trim, txtMotPasse.Text.Trim)
            Else
                MsgBox("Vous devez inscrire votre mot de passe !", vbOKOnly + vbInformation, "Mot de passe")
                txtMotPasse.Select()
            End If
        Else
            MsgBox("Vous devez inscrire votre nom d'utilisateur !", vbOKOnly + vbInformation, "Nom d'utilisateur")
            txtNomUtil.Select()
        End If
    End Sub

    Private Sub btnQuitter_Click(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles btnQuitter.Click
        Me.Close()
    End Sub

    Private Sub txtMotPasse_KeyPress(ByVal sender As Object, ByVal e As System.Windows.Forms.KeyPressEventArgs) Handles txtMotPasse.KeyPress
        If Asc(e.KeyChar) = 13 Then
            If txtNomUtil.Text <> "" Then
                If txtMotPasse.Text <> "" Then
                    funcOutils.funcGetPermissionUtil(txtNomUtil.Text.Trim, txtMotPasse.Text.Trim)
                Else
                    MsgBox("Vous devez inscrire votre mot de passe !", vbOKOnly + vbInformation, "Mot de passe")
                    txtMotPasse.Select()
                End If
            Else
                MsgBox("Vous devez inscrire votre nom d'utilisateur !", vbOKOnly + vbInformation, "Nom d'utilisateur")
                txtNomUtil.Select()
            End If
        End If
    End Sub

End Class
