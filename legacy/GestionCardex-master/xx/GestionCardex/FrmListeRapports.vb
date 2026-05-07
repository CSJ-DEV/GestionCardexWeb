Public Class FrmListeRapports
    Public langueFr As String
    Public langueAn As String
    Public Art486 As String
    Public Art684 As String
    Public Art672 As String
    Public Mega As String
    Public autre As String
    Public exp As String
    Public dist As Boolean
    Public Alpha As Boolean
    Public AnneB As Boolean
    
    Private Sub Button1_Click(sender As Object, e As EventArgs) Handles Button1.Click
        Dim titreRapport As String
        Dim frmReportViewer As New FrmReportViewer()
        titreRapport = ""
        If RadioButton1.Checked = True Then
            titreRapport = "ListeSom.rpt"
        Else
            If RadioButton2.Checked = True Then
                titreRapport = "ListeDetBar.rpt"

            Else
                If RadioButton3.Checked = True Then
                    titreRapport = "ListeDetDist.rpt"
                Else
                    If RadioButton4.Checked = True Then
                        titreRapport = "ListeDetReg.rpt"
                    End If
                End If
            End If
        End If

        frmReportViewer.afficherRapport(titreRapport, Me)
        frmReportViewer.Show()
    End Sub

    Private Sub btnAnnul_Click(sender As Object, e As EventArgs) Handles btnAnnul.Click
        Me.Close()
    End Sub


    Private Sub RadioButton1_CheckedChanged(sender As Object, e As EventArgs) Handles RadioButton1.CheckedChanged
        If RadioButton1.Checked = True Then
            AlphaCheckBox.Visible = True
            AnneCheckBox.Visible = True
            Label2.Visible = True
        End If
    End Sub

    Private Sub CheckedListBox2_SelectedIndexChanged(sender As Object, e As EventArgs)

    End Sub

    Private Sub FrmListeRapports_Load(sender As Object, e As EventArgs) Handles MyBase.Load

    End Sub

  

    Private Sub FrançaisCheckbox_CheckedChanged(sender As Object, e As EventArgs) Handles FrançaisCheckbox.CheckedChanged
        If FrançaisCheckbox.Checked = True Then
            langueFr = "Français"
        End If

    End Sub

    Private Sub AnglaisCheckBox_CheckedChanged(sender As Object, e As EventArgs) Handles AnglaisCheckBox.CheckedChanged
        If AnglaisCheckBox.Checked = True Then
            langueAn = "Anglais"
        End If
    End Sub

    Private Sub Art486CheckBox5_CheckedChanged(sender As Object, e As EventArgs) Handles Art486CheckBox5.CheckedChanged
        If Art486CheckBox5.Checked = True Then
            Art486 = "Art. 486.3"
        End If
    End Sub

    Private Sub Art684CheckBox_CheckedChanged(sender As Object, e As EventArgs) Handles Art684CheckBox.CheckedChanged
        If Art684CheckBox.Checked = True Then
            Art684 = "Art. 684"
        End If
    End Sub

    Private Sub Art672CheckBox_CheckedChanged(sender As Object, e As EventArgs) Handles Art672CheckBox.CheckedChanged
        If Art672CheckBox.Checked = True Then
            Art672 = "Art. 672.5"
        End If
    End Sub

    Private Sub MegaCheckBox_CheckedChanged(sender As Object, e As EventArgs) Handles MegaCheckBox.CheckedChanged
        If MegaCheckBox.Checked = True Then
            Mega = "Mégaprocès"
        End If
    End Sub

 
    Private Sub TextBox2_TextChanged(sender As Object, e As EventArgs) Handles Experiencetxt.TextChanged
        exp = Experiencetxt.Text
    End Sub

    Private Sub DistCheckBox_CheckedChanged(sender As Object, e As EventArgs) Handles DistCheckBox.CheckedChanged
        If DistCheckBox.Checked = True Then
            dist = True
        End If
    End Sub

    
    Private Sub AlphaCheckBox_CheckedChanged(sender As Object, e As EventArgs) Handles AlphaCheckBox.CheckedChanged
        If AlphaCheckBox.Checked = True Then
            Alpha = True
        End If
    End Sub

    Private Sub AnneCheckBox_CheckedChanged(sender As Object, e As EventArgs) Handles AnneCheckBox.CheckedChanged
        If AnneCheckBox.Checked = True Then
            AnneB = True
        End If
    End Sub

  
    Private Sub Autretxt_TextChanged(sender As Object, e As EventArgs) Handles Autretxt.TextChanged
        autre = Autretxt.Text
    End Sub

    Private Sub CheckedListBox1_SelectedIndexChanged(sender As Object, e As EventArgs) Handles CheckedListBox1.SelectedIndexChanged

    End Sub

    Private Sub RadioButton2_CheckedChanged(sender As Object, e As EventArgs) Handles RadioButton2.CheckedChanged
        If RadioButton2.Checked = True Then
            AlphaCheckBox.Visible = False
            AnneCheckBox.Visible = False
            Label2.Visible = False
        End If
    End Sub

    Private Sub Label2_Click(sender As Object, e As EventArgs) Handles Label2.Click

    End Sub

    Private Sub RadioButton3_CheckedChanged(sender As Object, e As EventArgs) Handles RadioButton3.CheckedChanged
        If RadioButton3.Checked = True Then
            AlphaCheckBox.Visible = False
            AnneCheckBox.Visible = False
            Label2.Visible = False
        End If
    End Sub

    Private Sub RadioButton4_CheckedChanged(sender As Object, e As EventArgs) Handles RadioButton4.CheckedChanged
        If RadioButton4.Checked = True Then
            AlphaCheckBox.Visible = False
            AnneCheckBox.Visible = False
            Label2.Visible = False
        End If
    End Sub
End Class