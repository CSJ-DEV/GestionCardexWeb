Imports System
Imports Microsoft.VisualBasic
Imports System.Reflection
Imports System.Data
Imports System.Data.SqlClient
Imports System.Text.RegularExpressions


Public Class frmAvocat
    Dim da As New SqlDataAdapter
    Dim dt As New DataTable
    Dim funcOutils As New FuncOutils
    Dim objAvocat As New Avocats
    Dim objAdresse As New Adresses
    Dim objInh As New inhpra
    Dim objinfomega As New infomega
    Public FrmListeRapport As FrmListeRapports
    Dim bNewAvocat As Boolean = False 'Pour determiner si c'est un nouveau avocat

#Region "*** TOOLBAR ***"

    'Bouton nouveau pour les 5 ongles

    Private Sub tsbNouveau_Click(sender As System.Object, e As System.EventArgs) Handles tsbNouveau.Click
        subBloqueTabPage(tbAvocat.SelectedIndex)
        Select Case tbAvocat.SelectedIndex
            Case 0
                bNewAvocat = True
                ReqNouveau()
            Case 1
                NouvAdrAvo()
            Case 2
                NouvInhAvo()
            Case 3
                NouvWebAvo()
            Case 4
                NouvMegaAvo()
        End Select
        tsbNouveau.Enabled = False
        tsbModifier.Enabled = False
        tsbSave.Enabled = True
        tsbDelete.Enabled = False
        tsbCancel.Enabled = True

    End Sub

    'Bouton modifier pour les 5 onglets

    Private Sub tsbMofier_Click(sender As Object, e As EventArgs) Handles tsbModifier.Click
        subBloqueTabPage(tbAvocat.SelectedIndex)
        Select Case tbAvocat.SelectedIndex
            Case 0
                EnaAvo()
                txtNom.Focus()
                gAvoStatus = DOSSIER_MODIF
            Case 1
                EnaAdrAvo()
                txtAdresse.Focus()
                gAvoAdrStatus = DOSSIER_MODIF
                dgvAdresse.Enabled = False
            Case 2
                EnaInhAvo()
                dtpDateDebInh.Focus()
                gAvoInhStatus = DOSSIER_MODIF
            Case 3
                EnaWebAvo()
                btnMotPasse.Enabled = True
                'btnMotPasse.Visible = True
                'btnMotPasse2.Visible = True
                gAvoWebStatus = DOSSIER_MODIF

                'Bouton modifier megaprocés
            Case 4
                EnaMegaAvo()
                'btnCalModifMega.Enabled = True    'btn visible
                'mskDateModifMega.Enabled = True   'dmskdate visible
                'mskDateModifMega.Focus()
                gAvoMegaStatus = DOSSIER_MODIF
        End Select
        tsbNouveau.Enabled = False
        tsbModifier.Enabled = False
        tsbSave.Enabled = True
        tsbCancel.Enabled = True
        If tbAvocat.SelectedTab Is tpAdr Or tbAvocat.SelectedTab Is tpInh Then
            tsbDelete.Enabled = True
        Else
            tsbDelete.Enabled = False
        End If

    End Sub

    'Bouton sauvegarder pour les 5 onglets

    Private Sub tsbSave_Click(sender As Object, e As EventArgs) Handles tsbSave.Click
        Me.Cursor = Cursors.AppStarting 'Pointeur de la souris
        Select Case tbAvocat.SelectedIndex
            Case 0
                If gAnyChg = 1 Then
                    ReqEnrAvo()

                Else
                    MsgBox("Il n'y a aucun champ modifié!", vbOKOnly + vbInformation, "Adresse")
                End If

            Case 1
                If gAnyChgAdr = 1 Then
                    ReqEnrAdrAvo()
                Else
                    MsgBox("Il n'y a aucun champ modifié!", vbOKOnly + vbInformation, "Adresse")
                End If
            Case 2
                If gAnyChgInh = 1 Then
                    ReqEnrInhAvo()
                Else
                    MsgBox("Il n'y a aucun champ modifié!", vbOKOnly + vbInformation, "Inhabilité")
                End If
            Case 3
                If gAnyChgWeb = 1 Then
                    ReqEnrWebAvo()
                Else
                    MsgBox("Il n'y a aucun champ modifié!", vbOKOnly + vbInformation, "WEB")
                End If
                'bouton enregistrer megaprocès
            Case 4
                If gAnyChgMega = 1 Then
                    ReqEnrMegaAvo()
                Else
                    MsgBox("Il n'y a aucun champ modifié!", vbOKOnly + vbInformation, "Mega")
                End If
        End Select
        Me.Cursor = Cursors.Default
    End Sub

    'Bouton supprimer pour Inhabilite et Adresse

    Private Sub tsbDelete_Click(sender As Object, e As EventArgs) Handles tsbDelete.Click
        If MsgBox("Confirmer l'effacement des données...", vbOKCancel + vbQuestion, "EFFACER") = vbOK Then
            Select Case tbAvocat.SelectedIndex
                'Case 1
                '   DelGridAdrAvoc(frmChild.grdAdrAvo.RowSel)
                'Case 2
                '   DelGridPratAvoc(frmChild.grdPratAvo.RowSel)

                Case 1 '*** ADRESSE
                    ' If 
                    Dim gRowID As Guid    'utilise le RowID pour effacer le record
                    gRowID = New Guid(txtAdrRowID.Text)
                    If objAdresse.FuncdeleteAdr(gRowID) = True Then
                        InitAdrAvo()
                        LoadAdr(txtCode.Text.Trim)
                        tsbNouveau.Enabled = True
                        tsbModifier.Enabled = False
                        tsbSave.Enabled = False
                        tsbCancel.Enabled = False
                        tsbDelete.Enabled = False
                        DisAdrAvo()
                    End If

                Case 2 '*** INH
                    objInh.FuncdeleteCommInh(txtCode.Text, txtCommInh.Text)
                    InitInhAvo()
                    LoadInh(txtCode.Text)
                    tsbNouveau.Enabled = True
                    tsbModifier.Enabled = False
                    tsbSave.Enabled = False
                    tsbDelete.Enabled = False
                    tsbCancel.Enabled = False
                    DisInhAvo()
            End Select
            subDebloqueTabPage()
        End If
    End Sub

    Private Sub tsbOuvrir_Click(sender As System.Object, e As System.EventArgs) Handles tsbOuvrir.Click
        ReqOuvrir()
    End Sub

    Private Sub ReqOuvrir()

        If ChkChange() = True Then

            gAvoStatus = DOSSIER_LOAD
            frmRechAvo.Show()
            gAnyChg = 0
            Me.Close()
        End If


    End Sub

    Private Sub tsbQuitter_Click(sender As System.Object, e As System.EventArgs) Handles tsbQuitter.Click
        If ChkChange() = True Then
            Me.Close()
            End
        End If
    End Sub

    'Liste deroulante des rapports

    Private Sub ListeToolStripMenuItem_Click(sender As Object, e As EventArgs) Handles ListeToolStripMenuItem.Click
        FrmListeRapport = New FrmListeRapports
        FrmListeRapport.Show()
    End Sub

    'Rapport Art98

    Private Sub RegistreArt98ToolStripMenuItem_Click(sender As Object, e As EventArgs) Handles RegistreArt98ToolStripMenuItem.Click
        Dim frmReportViewer As New FrmReportViewer()
        frmReportViewer.afficherRapport("Registre98.rpt")
        frmReportViewer.Show()
    End Sub

    'Rapport Art97

    Private Sub RegistreArt97ToolStripMenuItem_Click(sender As Object, e As EventArgs) Handles RegistreArt97ToolStripMenuItem.Click
        Dim frmReportViewer As New FrmReportViewer()
        frmReportViewer.afficherRapport("Registre97.rpt")
        frmReportViewer.Show()
    End Sub

    'Bouton Cancel

    Private Sub tsbCancel_Click(sender As Object, e As EventArgs) Handles tsbCancel.Click
        SubCancel()
    End Sub

    'Procedure bouton Cancel pour les 5 onglets

    Private Sub SubCancel()
        If gCodeAvo <> Nothing Then LoadAvo()
        subDebloqueTabPage()
        Select Case tbAvocat.SelectedIndex
            Case 0 '*****IDENTIFICATION
                If gCodeAvo = Nothing Then
                    InitAvo()
                    gbAvocat.Enabled = False
                    tsbNouveau.Enabled = True
                    tsbModifier.Enabled = False
                    tsbSave.Enabled = False
                    tsbDelete.Enabled = False
                    tsbCancel.Enabled = False
                    If txtCode.Text = "" Then
                        tpAdr.Enabled = False
                        tpInh.Enabled = False
                        tpWeb.Enabled = False
                        tpMega.Enabled = False
                    Else
                        tpAdr.Enabled = True
                        tpInh.Enabled = True
                        tpWeb.Enabled = True
                        tpMega.Enabled = True
                    End If
                Else
                    gbAvocat.Enabled = False
                    tsbNouveau.Enabled = True
                    tsbModifier.Enabled = True
                    tsbSave.Enabled = False
                    tsbDelete.Enabled = False
                    tsbCancel.Enabled = False
                End If
            Case 1 '*******ADRESSE
                DisAdrAvo()
                InitAdrAvo()
                tsbNouveau.Enabled = True
                tsbModifier.Enabled = False
                tsbSave.Enabled = False
                tsbDelete.Enabled = False
                tsbCancel.Enabled = False
                dgvAdresse.Enabled = True
                dgvAdresse.Focus()
            Case 2 '******INH
                DisInhAvo()
                InitInhAvo()
                tsbNouveau.Enabled = True
                tsbModifier.Enabled = False
                tsbSave.Enabled = False
                tsbDelete.Enabled = False
                tsbCancel.Enabled = False
            Case 3 '******WEB
                DisWebAvo()
                LoadWeb()
                tsbNouveau.Enabled = True
                tsbModifier.Enabled = True
                tsbSave.Enabled = False
                tsbDelete.Enabled = False
                tsbCancel.Enabled = False
            Case 4 '******MEGA
                DisMegaAvo()
                LoadMega(gCodeAvo)
                If objinfomega.datemodif IsNot Nothing Then
                    tsbNouveau.Enabled = False
                    tsbModifier.Enabled = True
                Else
                    tsbNouveau.Enabled = True
                    tsbModifier.Enabled = False
                End If

                tsbSave.Enabled = False
                tsbDelete.Enabled = False
                tsbCancel.Enabled = False
        End Select

        'If tbAvocat.SelectedTab Is tpIdent And gCodeAvo = Nothing Then
        '    InitAvo()
        '    gbAvocat.Enabled = False
        '    tsbNouveau.Enabled = True
        '    tsbModifier.Enabled = False
        '    tsbSave.Enabled = False
        '    tsbDelete.Enabled = False
        '    tsbCancel.Enabled = False
        'Else
        '    gbAvocat.Enabled = False
        '    tsbNouveau.Enabled = True
        '    tsbModifier.Enabled = True
        '    tsbSave.Enabled = False
        '    tsbDelete.Enabled = False
        '    tsbCancel.Enabled = False

        'End If
        cklbDist.ClearSelected()
        txtCommMega.Text = Nothing

        'Véfifie les check l'index qui sont cochés

        While cklbDist.CheckedIndices.Count > 0
            cklbDist.SetItemChecked(cklbDist.CheckedIndices(0), False)
        End While
        If gCodeAvo <> Nothing Then LoadDistrictAvo()
    End Sub

    Private Sub tbAvocat_Click(sender As Object, e As System.EventArgs) Handles tbAvocat.Click
        'SetToolStrip()
    End Sub

    'Private Sub SetToolStrip()
    '    If gReadOnly = 1 Then
    '        If tbAvocat.SelectedTab Is tpMega And vgGrUtil = MEGA Then
    '            'pnlBoutons.Visible = True
    '            TsMenu.Enabled = True
    '            tsbNouveau.Enabled = True
    '            tsbModifier.Enabled = True
    '            tsbSave.Enabled = False
    '            tsbDelete.Enabled = False
    '            If gMega = True Then
    '                tsbNouveau.Enabled = False
    '                tsbModifier.Enabled = True
    '                tsbSave.Enabled = False
    '                tsbDelete.Enabled = False
    '                tsbCancel.Enabled = False
    '            Else
    '                tsbNouveau.Enabled = True
    '                tsbModifier.Enabled = False
    '                tsbSave.Enabled = False
    '                tsbDelete.Enabled = False
    '                tsbCancel.Enabled = False
    '            End If
    '        Else
    '            TsMenu.Enabled = False
    '            'pnlBoutons.Visible = False
    '        End If
    '    Else

    '    End If
    '    If tbAvocat.SelectedTab Is tpIdent Then
    '        tsbNouveau.Enabled = True
    '        tsbOuvrir.Enabled = True
    '        'tsbNouveau.Enabled = False
    '        If gAvoStatus = DOSSIER_NOUVEAU Then
    '            tsbModifier.Enabled = False
    '            tsbSave.Enabled = False ' true
    '            tsbDelete.Enabled = False
    '            tsbCancel.Enabled = True
    '        ElseIf gAvoStatus <> DOSSIER_NOUVEAU Then
    '            tsbModifier.Enabled = True
    '            tsbSave.Enabled = False
    '            tsbDelete.Enabled = False
    '            tsbCancel.Enabled = False
    '        End If
    '    Else
    '        tsbNouveau.Enabled = False
    '        tsbOuvrir.Enabled = False

    '        If (tbAvocat.SelectedTab Is tpWeb And gWeb = True) Then   'onglet web
    '            tsbNouveau.Enabled = False
    '            tsbModifier.Enabled = True
    '            tsbDelete.Enabled = False


    '        ElseIf (tbAvocat.SelectedTab Is tpMega And gMega = True) Then  'onglet megaprocès
    '            tsbNouveau.Enabled = False
    '            tsbModifier.Enabled = True
    '            tsbDelete.Enabled = True

    '            'If (tbAvocat.SelectedTab Is tpWeb And gWeb = True) _
    '            '        Or (tbAvocat.SelectedTab Is tpMega And gMega = True) Then
    '            '    tsbNouveau.Enabled = False
    '            '    tsbModifier.Enabled = True
    '            '    tsbDelete.Enabled = True
    '        ElseIf tbAvocat.SelectedTab Is tpAdr And gAvoStatus <> DOSSIER_NOUVEAU Then
    '            tsbNouveau.Enabled = True
    '            tsbModifier.Enabled = True
    '            tsbDelete.Enabled = False
    '        Else
    '            tsbNouveau.Enabled = True
    '            tsbModifier.Enabled = False
    '            tsbDelete.Enabled = False
    '        End If
    '        tsbSave.Enabled = False
    '        tsbCancel.Enabled = False
    '    End If
    'End Sub

#End Region ' "*** TOOLBAR ***"


#Region "*** Identification ***"

    'Private Sub lblFermCalAdr_Click(sender As System.Object, e As System.EventArgs) Handles lblFermCalAdr.Click
    '    pnlCalAdr.Visible = False
    'End Sub

    'Private Sub lblFermCalModif_Click(sender As System.Object, e As System.EventArgs)
    '    pnlCalModif.Visible = False
    'End Sub

    'Private Sub mskDateModif_MouseClick(sender As Object, e As System.Windows.Forms.MouseEventArgs) Handles mskDateModif.MouseClick
    '    pnlCalModif.Visible = True
    '    If Information.IsDate(mskDateModif.Text) Then
    '        calDateModif.SetDate(Convert.ToDateTime(mskDateModif.Text))
    '    Else
    '        calDateModif.SetDate(DateTime.Now)
    '    End If
    'End Sub

    'Private Sub mskDateModif_TextChanged(sender As Object, e As System.EventArgs) Handles mskDateModif.TextChanged
    '    gAnyChg = 1
    'End Sub

    'Procedure validation NAS

    Private Sub mskNAS_LostFocus(sender As Object, e As System.EventArgs) Handles mskNAS.LostFocus
        If mskNAS.TextLength = 9 Then
            If funcValidNoAssSoc(mskNAS.Text) = False Then ' If ValidNAS(mskNAS.Text) = False Then
                MsgBox("Le numéro de NAS est invalide, veuillez le vérifier!", vbOKOnly + vbInformation, "NAS")
                mskNAS.Focus()
            End If
        ElseIf mskNAS.Text.Trim <> "" Then
            MsgBox("Le numéro de NAS est invalide, veuillez le vérifier!", vbOKOnly + vbInformation, "NAS")
            mskNAS.Focus()

        End If
    End Sub

    'Radio bouton Actif Oui
    Private Sub rbActifO_CheckedChanged(sender As System.Object, e As System.EventArgs) Handles rbActifO.CheckedChanged
        gAnyChg = 1
    End Sub

    'Radio bouton Actif Non
    Private Sub rbActifN_CheckedChanged(sender As System.Object, e As System.EventArgs) Handles rbActifN.CheckedChanged
        gAnyChg = 1
    End Sub

    'Radio bouton en attente Oui
    Private Sub rbAttO_CheckedChanged(sender As System.Object, e As System.EventArgs) Handles rbAttO.CheckedChanged
        gAnyChg = 1
    End Sub

    'Radio bouton en attente Non
    Private Sub rbAttN_CheckedChanged(sender As System.Object, e As System.EventArgs) Handles rbAttN.CheckedChanged
        gAnyChg = 1
    End Sub

    'Radio bouton Dépôt Oui et Radio bouton en attente Non
    Private Sub rbDepoO_CheckedChanged(sender As System.Object, e As System.EventArgs) Handles rbDepoO.CheckedChanged
        If gAvoStatus <> DOSSIER_LOAD Then
            'If gAvoStatus <> DOSSIER_LOAD And gVerifDepo = False Then
            If rbDepoO.Checked = True Then
                If MsgBox("Voulez-vous vraiment mettre cet avocat sous dépôt direct?", _
                            vbYesNo + vbInformation + vbDefaultButton2, "Dépôt direct") = vbYes Then
                    gAnyChg = 1
                Else
                    'gVerifDepo = True
                    rbDepoO.Checked = False
                End If
            Else
                If txtCode.Text <> "" Then
                    If MsgBox("Voulez-vous vraiment enlever cet avocat du dépôt direct?", _
                            vbYesNo + vbInformation + vbDefaultButton2, "Dépôt direct") = vbYes Then
                        gAnyChg = 1
                    Else
                        'gVerifDepo = True
                        rbDepoO.Checked = True
                    End If
                Else
                    gAnyChg = 0
                End If
            End If
        End If
    End Sub

    'Radio bouton Web Oui
    Private Sub rbFacWebO_CheckedChanged(sender As System.Object, e As System.EventArgs) Handles rbFacWebO.CheckedChanged
        gAnyChg = 1
    End Sub

    'Radio bouton Web Non
    Private Sub rbFacWebN_CheckedChanged(sender As System.Object, e As System.EventArgs) Handles rbFacWebN.CheckedChanged
        gAnyChg = 1
    End Sub


    'Radio bouton Mega Oui
    Private Sub rbMegaO_CheckedChanged(sender As System.Object, e As System.EventArgs) Handles rbMegaO.CheckedChanged
        gAnyChg = 1
    End Sub

    'Radio bouton Mega Oui
    Private Sub rbMegaN_CheckedChanged(sender As System.Object, e As System.EventArgs) Handles rbMegaN.CheckedChanged
        gAnyChg = 1
        If rbMegaN.Checked = True And objAvocat.mega = "O" Then
            MessageBox.Show("Toute l'information déjà enregistrée sera supprimée", "Megaprocès", MessageBoxButtons.OK, MessageBoxIcon.Warning)
        End If
    End Sub


    'Private Sub rbMegaprocesO_CheckedChanged(sender As System.Object, e As System.EventArgs)
    '    gAnyChgMega = 1
    'End Sub

    'Private Sub rbMegaprocesN_CheckedChanged(sender As System.Object, e As System.EventArgs)
    '    gAnyChgMega = 1
    'End Sub


    'Radio bouton Payable 
    Private Sub rbPayO_CheckedChanged(sender As System.Object, e As System.EventArgs) Handles rbPayO.CheckedChanged
        If gAvoStatus <> DOSSIER_LOAD Then
            'If gAvoStatus <> DOSSIER_LOAD And gVerifPay = False Then
            If rbPayO.Checked = True Then
                If MsgBox("Voulez-vous vraiment mettre cet avocat payable?", _
                            vbYesNo + vbInformation + vbDefaultButton2, "Payable") = vbYes Then
                    gAnyChg = 1
                Else
                    'gVerifPay = True
                    rbPayO.Checked = False
                End If
            Else
                If MsgBox("Voulez-vous vraiment mettre cet avocat non payable?", _
                            vbYesNo + vbInformation + vbDefaultButton2, "Payable") = vbYes Then
                    gAnyChg = 1
                Else
                    'gVerifPay = True
                    rbPayO.Checked = True
                End If
            End If
        End If
    End Sub

    'Validation Adresse courriel
    Private Sub txtAdremail_LostFocus(sender As Object, e As System.EventArgs) Handles txtAdremail.LostFocus
        If txtAdremail.Text.Trim <> "" Then
            If txtAdremail.Text.IndexOf("@") > -1 Then
                If txtAdremail.Text.IndexOf(".", txtAdremail.Text.IndexOf("@")) = txtAdremail.Text.IndexOf("@") - 1 _
                Or txtAdremail.Text.IndexOf(".") = -1 Then
                    MsgBox("L'adresse courriel est invalide, il manque le point ou il est juste avant l'arobas!", vbOKOnly + vbCritical, "Adresse erronée")
                    txtAdremail.Focus()
                ElseIf txtAdremail.Text.IndexOf(",") > -1 Then
                    MsgBox("L'adresse courriel est invalide, veuillez enlevez la virgule!", vbOKOnly + vbCritical, "Adresse erronée")
                    txtAdremail.Focus()
                ElseIf txtAdremail.Text.IndexOf(" ") > -1 Then
                    MsgBox("L'adresse courriel est invalide, veuillez enlevez l'espace!", vbOKOnly + vbCritical, "Adresse erronée")
                    txtAdremail.Focus()
                End If
            Else
                MsgBox("L'adresse courriel est invalide, il manque l'arobas @!", vbOKOnly + vbCritical, "Adresse erronée")
                txtAdremail.Focus()
            End If
        End If
        gAnyChg = 1


        'Déjà en commentaire
        'If gAvoStatus <> DOSSIER_LOAD Then
        '    mskDateModif.Text = Today
        '    If MsgBox("La date modification a été changée pour la date du jour. Désirez-vous mettre une autre date ?", vbYesNo + vbIgnore, "Date modif") = vbYes Then
        '        mskDateModif.Focus()
        '    End If
        'End If
        'gAnyChg = 1
    End Sub

    Private Sub txtAnnBar_TextChanged(sender As System.Object, e As System.EventArgs) Handles txtAnnBar.TextChanged
        gAnyChg = 1
    End Sub

    Private Sub txtCode_TextChanged(sender As System.Object, e As System.EventArgs) Handles txtCode.TextChanged
        gAnyChg = 1
    End Sub

    Private Sub txtCodeBar_TextChanged(sender As System.Object, e As System.EventArgs) Handles txtCodeBar.TextChanged
        gAnyChg = 1
    End Sub

    Private Sub txtComm_TextChanged(sender As System.Object, e As System.EventArgs) Handles txtComm.TextChanged
        gAnyChg = 1
    End Sub

    Private Sub txtNom_TextChanged(sender As System.Object, e As System.EventArgs) Handles txtNom.TextChanged
        gAnyChg = 1
    End Sub

    Private Sub txtPrenom_TextChanged(sender As System.Object, e As System.EventArgs) Handles txtPrenom.TextChanged
        gAnyChg = 1
    End Sub

    Private Sub txtTaxes_TextChanged(sender As System.Object, e As System.EventArgs) Handles txtTaxes.TextChanged
        gAnyChg = 1
    End Sub

    Private Sub DisAvo()
        gbAvocat.Enabled = False
        'txtCode.Enabled = False
        'txtNom.Enabled = False
        'txtPrenom.Enabled = False
        'txtAnnBar.Enabled = False
        'txtCodeBar.Enabled = False
        'mskNAS.Enabled = False
        'txtAdremail.Enabled = False
        'pnlFactWeb.Enabled = False
        'pnlPayable.Enabled = False
        'pnlActif.Enabled = False
        'pnlDepo.Enabled = False
        'pnlMega.Enabled = False
        'btnCalModif.Enabled = False
        'mskDateModif.Enabled = False
    End Sub

    Private Sub EnaAvo()

        gbAvocat.Enabled = True
        txtCode.Enabled = False ' True 'false pour que bouton inactive impossible de modifier
        'txtNom.Enabled = True
        'txtPrenom.Enabled = True
        'txtAnnBar.Enabled = True
        'txtCodeBar.Enabled = True
        'mskNAS.Enabled = True
        'txtAdremail.Enabled = True
        'pnlFactWeb.Enabled = True
        'pnlPayable.Enabled = True
        'pnlActif.Enabled = True
        'pnlDepo.Enabled = True
        'pnlMega.Enabled = True
        'btnCalModif.Enabled = True
        'mskDateModif.Enabled = True
        'txtComm.Enabled = True
        'tbAvocat.Enabled = True
    End Sub

    'Enregistrer Avocat
    Public Function EnrAvo() As Boolean
        EnrAvo = False

        SetObjAvo()
        If gAvoStatus = DOSSIER_NOUVEAU Then
            objAvocat.Save("", "avocat")
            gCodeAvo = txtCode.Text
            EnrAvo = True
        ElseIf gAvoStatus = DOSSIER_MODIF Then
            objAvocat.Save(gCodeAvo, "avocat")
            EnrAvo = True
        End If
        If EnrAvo = True Then
            objAdresse.FuncSetAdremail(gCodeAvo, txtAdremail.Text.Trim)
        End If
        If EnrAvo = True And rbMegaN.Checked = True Then
            If objinfomega.funcDeleteINfoMega(gCodeAvo) = True Then
                InitMegaAvo()
            End If
        End If
        objAvocat.Load(gCodeAvo)
        gAvoStatus = DOSSIER_MODIF
        LoadAvo()
        gAnyChg = 0
    End Function

    'Initialise Avocat
    Private Sub InitAvo()
        objAvocat = New Avocats
        CbotypeCode.Text = ""
        txtCode.Clear()
        chkIsJordan.Enabled = True
        chkIsJordan.Checked = False
        txtNom.Clear()
        txtPrenom.Clear()
        txtAnnBar.Clear()
        txtCodeBar.Clear()
        mskNAS.Text = ""
        txtAdremail.Clear()
        txtTaxes.Clear()
        'rbFacWebO.Checked = False
        rbFacWebN.Checked = True
        rbPayO.Checked = True
        rbAttN.Checked = True
        rbActifO.Checked = True
        'rbDepoO.Checked = False
        rbDepoN.Checked = True
        rbMegaN.Checked = True

        dtpDateModifAvo.Value = DateTime.Now.Date  'pour qui n'affiche pas les minutes avant Now.Date
        'mskDateModif.Text = DateTime.Now.Date
        txtUserModif.Clear()
        txtComm.Clear()
        InitAdrAvo()
        txtNbAdr.Clear()
        dgvInh.DataSource = Nothing
        dgvInh.Rows.Clear()
        dgvAdresse.DataSource = Nothing
        dgvAdresse.Rows.Clear()
        InitInhAvo()
        InitWebAvo()
        InitMegaAvo()
        gAnyChg = 0
    End Sub

    'Nouveau Avocat
    Private Sub NouvAvo()
        gAvoStatus = DOSSIER_NOUVEAU
        tbAvocat.SelectedTab = tpIdent
        'SetToolStrip()
        EnaAvo()
        pnlFactWeb.Enabled = True
        txtCode.Focus()
        CbotypeCode.Visible = True
    End Sub

    'Enregistrer Avocat
    Public Function ReqEnrAvo() As Boolean

        ReqEnrAvo = False

        If gAvoStatus = DOSSIER_NOUVEAU Then
            If VerifSiNomExiste() Then
                txtCode.Focus()
                Exit Function
            End If
        End If

        If txtCode.Text <> "" And txtNom.Text <> "" And txtPrenom.Text <> "" Then
            Me.Text = "Enregistrement en cours de l'avocat..."
            If EnrAvo() = False Then 'S'IL Y A UN ERREUR AU MOMENT D'ENREGISTRER L'AVOCAT
                MsgBox("L'enregistrement a échoué, veuillez vérifier vos données!", vbCritical + vbOKOnly, "Avocat")
                txtCode.Focus()
                Exit Function
            Else
                bNewAvocat = False
            End If
            ReqEnrAvo = True
            gAnyChg = 0
        Else
            MsgBox("Le code, le nom et le prénom  de l'avocat sont obligatoires...", vbOKOnly + vbInformation, "Cardex avocat")
            txtCode.Focus()
            Exit Function
        End If
        'SEND INFORMATION TO WEB TABPAGE
        rbinternetOui.Checked = rbFacWebO.Checked

        Me.Text = txtPrenom.Text.Trim & " " & txtNom.Text.Trim & " (" & txtCode.Text.Trim & ")"
        DisAvo() 'disable
        subDebloqueTabPage()
        tsbNouveau.Enabled = True
        tsbModifier.Enabled = True
        tsbSave.Enabled = False
        tsbCancel.Enabled = False



    End Function

    Private Sub ReqNouveau()
        'If ChkChange() = True Then
        gCodeAvo = Nothing
        InitAvo()
        NouvAvo()
        InitAdrAvo()
        InitInhAvo()
        InitMegaAvo()
        InitWebAvo()
        'End If
    End Sub

    Private Sub TrouveEmailCour()
        Dim i As Integer

        For i = 0 To dgvAdresse.Rows.Count - 1
            If dgvAdresse.Rows(i).Cells(1).Value = "C" Then
                If dgvAdresse.Rows(i).Cells(12).Value <> txtAdremail.Text Then
                    txtAdremail.Text = dgvAdresse.Rows(i).Cells(12).Value
                    Exit Sub
                End If
            End If
        Next
    End Sub


    '***************************************
    'Validation NAS
    '***************************************
    Public Function ValidNAS(strNas As String) As Boolean
        Dim i As Integer
        Dim tot As Integer
        Dim c As Integer
        Dim v As Integer

        ValidNAS = False

        For i = 1 To Len(strNas) - 1
            If i Mod 2 = 1 Then
                c = Val(Mid(strNas, i, 1))
            Else
                c = 2 * (Val(Mid(strNas, i, 1)))
                If c > 9 Then
                    c = Val(Mid(c, 1, 1)) + Val(Mid(c, 2, 1))
                End If
            End If
            tot = tot + c
        Next
        v = (10 - (tot Mod 10)) Mod 10

        If v = Mid(strNas, Len(strNas) - 1, 1) Then ValidNAS = True


    End Function
#Region "****** VALIDER NAS ******"
    Private Function funcValu(ByVal LeNombre As Object) As Double

        Dim Virgule As Long
        Dim LePoint As String
        Virgule = 0
        LeNombre = IIf(IsDBNull(LeNombre), 0, LeNombre)
        Virgule = InStr(1, LeNombre, ",")
        If Virgule > 0 Then
            LePoint = Microsoft.VisualBasic.Left(LeNombre, Virgule - 1) + "." + Mid(LeNombre, Virgule + 1)
            funcValu = Val(LePoint)
        Else
            funcValu = Format(Val(LeNombre), "0.00")
        End If
    End Function
    ''' <summary>
    ''' Verifie si le NAS rentrer est valide (strNAS)
    ''' </summary>
    Public Function funcValidNoAssSoc(ByVal no As String) As Boolean



        Dim i, tot, C, v As Integer
        Dim temp As String = no
        funcValidNoAssSoc = True
        'no = no.Replace("-", "")
        If Len(no) = 9 Then
            If Trim(no) <> "" Then
                For i = 1 To Len(no) - 1
                    If i Mod 2 = 1 Then
                        C = funcValu(Mid(no, i, 1))
                    Else
                        C = 2 * (funcValu(Mid(no, i, 1)))
                        If C > 9 Then
                            C = funcValu(Mid(C, 1, 1)) + funcValu(Mid(C, 2, 1))
                        End If
                    End If
                    tot = tot + C
                Next

                v = (10 - (tot Mod 10)) Mod 10

                If v <> Microsoft.VisualBasic.Right(no, 1) Then
                    'MsgBox("Numéro d'assurance sociale incorrect" & Chr(13) & " Veuillez vérifier..", vbOKOnly + vbCritical, "Validations")
                    funcValidNoAssSoc = False
                End If
            End If
        ElseIf Trim(no) <> "" Then
            'MsgBox("Le numéro d'assurance sociale doit être composé de 9 caractères")
            funcValidNoAssSoc = False
        End If
    End Function
#End Region '"****** VALIDER NAS ******"
    '*****************************************
    'Validation Taxes
    '*****************************************
    Private Function ValidRegTaxes() As String
        Dim conn As New ObjConn.ObjConn
        Dim dr As SqlDataReader
        Dim cmd As SqlCommand
        Dim strSQL As String = "select cfirme, cnotax1, cnotax2 from avocats where cart52uid= @Code and cnotax1<>''"
        ValidRegTaxes = "Non"
        Try
            conn.ConnString = vstrFVI

            cmd = New SqlCommand(strSQL, conn.OpenConn())
            cmd.Parameters.AddWithValue("@Code", objAvocat.code)
            'Executer la command et assigne le contenu au recordset
            dr = cmd.ExecuteReader()

            '**Lire le recordset 
            If dr.Read = True Then
                If IsDBNull(dr("cfirme")) = False Then
                    ValidRegTaxes = "Oui"
                End If
            End If
            cmd.Connection.Close()
        Catch ex As Exception
            funcOutils.subErrorMessage(Err.Number, Err.Description, Me.GetType.Name, MethodInfo.GetCurrentMethod.Name)
        Finally
            conn.CloseConn()
        End Try

        'Dim strSql As String
        'Dim Conn As New ObjConn.ObjConnOle(strConnFVI)
        'Dim MyDataRead As OleDb.OleDbDataReader = Nothing

        'ValidRegTaxes = "Non"
        'Try
        '    strSql = "select cfirme, cnotax1, cnotax2 from avocats where cart52uid='" & objAvocat.code & "' and cnotax1<>''"

        '    Conn.ExecuteSql(strSql, MyDataRead)
        '    If MyDataRead.HasRows Then
        '        ValidRegTaxes = "Oui"
        '    End If

        'Catch ex As Exception
        '    funcOutils.subErrorMessage(Err.Number, Err.Description, Me.GetType.Name, MethodInfo.GetCurrentMethod.Name)
        'End Try

        '        Conn.CloseConn()

    End Function

    'Vérification si le nom existe
    Public Function VerifSiNomExiste() As Boolean

        Dim conn As New ObjConn.ObjConn
        Dim dr As SqlDataReader
        Dim cmd As SqlCommand
        Dim strSQL As String = "select a.code, a.actpass, b.ville from avocats a, adresses b where a.code=b.code and b.courant='O' and nom=  @strNom and prenom=  @strPrenom "
        Dim strActif As String = ""
        Dim strNom As String = ""
        Dim strPrenom As String = ""
        Dim gListeCode As String = ""
        Dim tablCodeAvo() As String
        Dim iCompt As Integer = 0
        Dim i As Integer

        VerifSiNomExiste = False
        Try
            conn.ConnString = strConnCardAvo
            strNom = funcOutils.funcApos(funcOutils.funcConvertAccent(txtNom.Text)) 'convertion d'accent dans le nom
            strPrenom = funcOutils.funcApos(funcOutils.funcConvertAccent(txtPrenom.Text)) 'convertion d'accent dans le premon


            cmd = New SqlCommand(strSQL, conn.OpenConn())
            cmd.Parameters.AddWithValue("@strNom", strNom)
            cmd.Parameters.AddWithValue("@strPrenom", strPrenom)
            'Executer la command et assigne le contenu au recordset
            dr = cmd.ExecuteReader()

            '**Lire le recordset 
            If dr.Read = True Then
                ReDim tablCodeAvo(conn.NbRows)
                VerifSiNomExiste = True
                While dr.Read()
                    strActif = IIf(dr.GetString(1) = "A", "Actif", "Passif")
                    tablCodeAvo(iCompt) = dr.GetString(0) & Space(6) & dr.GetString(2).Trim & strActif & Space(3)
                    iCompt = iCompt + 1
                End While
            Else
                Exit Function
            End If
            For i% = 0 To UBound(tablCodeAvo, 1) - 1
                gListeCode = gListeCode + tablCodeAvo(i%) & Chr(13)
            Next

            If MsgBox("Un code a déjà été créé avec ce nom. Voulez-vous quand même en créer un nouveau?" & Chr(13) & Chr(13) & _
                   gListeCode, vbYesNo + vbInformation, "Cardex") = vbYes Then
                VerifSiNomExiste = False
            End If
            cmd.Connection.Close()
        Catch ex As Exception
            funcOutils.subErrorMessage(Err.Number, Err.Description, Me.GetType.Name, MethodInfo.GetCurrentMethod.Name)
        Finally
            conn.CloseConn()
        End Try

        'Dim Conn As New ObjConn.ObjConnOle(strConnCardAvo) 'connexion a la base Cardavo
        'Dim dr As OleDb.OleDbDataReader = Nothing
        'Dim strActif As String = ""
        'Dim strNom As String = ""
        'Dim strPrenom As String = ""
        'Dim strSql As String
        'Dim gListeCode As String = ""
        'Dim tablCodeAvo() As String
        'Dim iCompt As Integer = 0
        'Dim i As Integer

        'VerifSiNomExiste = False

        'Try
        '    strNom = funcOutils.funcApos(funcOutils.funcConvertAccent(txtNom.Text)) 'convertion d'accent dans le nom
        '    strPrenom = funcOutils.funcApos(funcOutils.funcConvertAccent(txtPrenom.Text)) 'convertion d'accent dans le premon

        '    strSql = "select a.code, a.actpass, b.ville from avocats a, adresses b where a.code=b.code and b.courant='O'"
        '    strSql = strSql + "and nom='" & strNom & "' and prenom='" & strPrenom & "'"

        '    Conn.ExecuteSql(strSql, dr)
        '    If dr.HasRows Then
        '        ReDim tablCodeAvo(Conn.NbRows)
        '        VerifSiNomExiste = True
        '        While dr.Read()
        '            strActif = IIf(dr.GetString(1) = "A", "Actif", "Passif")
        '            tablCodeAvo(iCompt) = dr.GetString(0) & Space(6) & dr.GetString(2).Trim & strActif & Space(3)
        '            iCompt = iCompt + 1
        '        End While
        '    Else
        '        Exit Function
        '    End If

        '    For i% = 0 To UBound(tablCodeAvo, 1) - 1
        '        gListeCode = gListeCode + tablCodeAvo(i%) & Chr(13)
        '    Next

        '    If MsgBox("Un code a déjà été créé avec ce nom. Voulez-vous quand même en créer un nouveau?" & Chr(13) & Chr(13) & _
        '           gListeCode, vbYesNo + vbInformation, "Cardex") = vbYes Then
        '        VerifSiNomExiste = False
        '    End If
        'Catch ex As Exception
        '    funcOutils.subErrorMessage(Err.Number, Err.Description, Me.GetType.Name, MethodInfo.GetCurrentMethod.Name)
        'End Try

        'Conn.CloseConn()

    End Function

    Private Sub mskNAS_MaskInputRejected(sender As Object, e As MaskInputRejectedEventArgs) Handles mskNAS.MaskInputRejected

        If mskNAS.Text <> "" Then
            If funcValidNoAssSoc(mskNAS.Text) = False Then
                MsgBox("Le numéro de NAS est invalide, veuillez le vérifier!", vbOKOnly + vbInformation, "NAS")
                mskNAS.Focus()
            End If
        End If

    End Sub

    Private Sub mskNAS_TextChanged(sender As Object, e As System.EventArgs) Handles mskNAS.TextChanged
        gAnyChg = 1
    End Sub

    'type code A,N,P
    Private Sub CbotypeCode_SelectedIndexChanged(sender As Object, e As EventArgs) Handles CbotypeCode.SelectedIndexChanged
        subCalculateCode()
    End Sub

    Private Sub subCalculateCode()
        Try
            If CbotypeCode.Text <> "" Then
                If CbotypeCode.Text = "A" Then
                    chkIsJordan.Enabled = True
                Else
                    chkIsJordan.Checked = False
                    chkIsJordan.Enabled = False
                End If

                txtCode.Clear()
                txtCode.Text = CbotypeCode.Text

                Dim conn As New ObjConn.ObjConn(strConnCardAvo)
                Dim binding1 As New BindingSource
                Dim dr As OleDb.OleDbDataReader = Nothing
                Dim strSql As String = ""

                txtCode.Text = objAvocat.FuncGetAvoCode(CbotypeCode.Text.Trim, chkIsJordan.Checked)

            End If
        Catch ex As Exception

        End Try
    End Sub

    Private Sub LoadAvo()
        objAvocat.Load(gCodeAvo)
        SetTxtAvo()
        Me.Text = objAvocat.prenom & "  " & objAvocat.nom & "  " & objAvocat.code

        LoadAdr(objAvocat.code)
        LoadInh(objAvocat.code)
        If objAvocat.factweb <> "" Then
            LoadWeb()
            gWeb = True
        End If
        LoadMega(objAvocat.code)
        gAnyChg = 0
        gAnyChgAdr = 0

    End Sub

#End Region  ' "***  Identification   ***"


#Region "***  Mega  ***"

    'Private Sub btnCalModifMega_Click(sender As Object, e As System.EventArgs)
    '    pnlCalModifMega.Visible = True
    '    If mskDateModifMega.Text <> "" Then
    '        calDateModifMega.SetDate(DateTime.Now)
    '        '(Convert.ToDateTime(mskDateModifMega.Text))
    '    Else
    '        calDateModifMega.SetDate(DateTime.Now)
    '    End If
    'End Sub

    'Private Sub calDateModifMega_DateSelected(sender As Object, e As System.Windows.Forms.DateRangeEventArgs)
    '    mskDateModifMega.Text = e.Start
    '    pnlCalModifMega.Visible = False
    'End Sub

    'Private Sub calDateModif_DateSelected(sender As Object, e As System.Windows.Forms.DateRangeEventArgs)
    '    mskDateModif.Text = e.Start
    '    pnlCalModif.Visible = False
    'End Sub

    'Private Sub cboVilleRef_SelectedIndexChanged(sender As System.Object, e As System.EventArgs) Handles cboVilleRef.SelectedIndexChanged
    '    gAnyChgWeb = 1
    'End Sub

    Private Sub ckbFrancais_CheckedChanged(sender As System.Object, e As System.EventArgs) Handles ckbFrancais.CheckedChanged
        gAnyChgMega = 1
    End Sub

    Private Sub ckbAnglais_CheckedChanged(sender As System.Object, e As System.EventArgs) Handles ckbAnglais.CheckedChanged
        gAnyChgMega = 1
    End Sub


    'Vérifier si les districts sont cochées
    Private Sub ckbTousDist_CheckedChanged(sender As System.Object, e As System.EventArgs) Handles ckbTousDist.CheckedChanged
        If ckbTousDist.Checked = True Then
            While cklbDist.CheckedIndices.Count > 0
                cklbDist.SetItemChecked(cklbDist.CheckedIndices(0), False)
            End While
        End If
        gAnyChgMega = 1
    End Sub

    Private Sub cklbDist_SelectedIndexChanged(sender As System.Object, e As System.EventArgs) Handles cklbDist.SelectedIndexChanged

        If ckbTousDist.Checked = True Then
            ckbTousDist.Checked = False
        End If
        gAnyChgMega = 1
    End Sub


    'Private Sub mskDateModifMega_MouseClick(sender As Object, e As System.Windows.Forms.MouseEventArgs)
    '    pnlCalModifMega.Visible = True
    '    If Information.IsDate(mskDateModifMega.Text) Then
    '        calDateModifMega.SetDate(Convert.ToDateTime(mskDateModifMega.Text))
    '    Else
    '        calDateModifMega.SetDate(DateTime.Now)
    '    End If
    'End Sub

    Private Sub mskDateModifMega_TextChanged(sender As Object, e As System.EventArgs)
        gAnyChgMega = 1
    End Sub

    Private Sub rb486O_CheckedChanged(sender As System.Object, e As System.EventArgs) Handles rb486O.CheckedChanged
        gAnyChgMega = 1
    End Sub

    Private Sub rb486N_CheckedChanged(sender As System.Object, e As System.EventArgs) Handles rb486N.CheckedChanged
        gAnyChgMega = 1
    End Sub

    Private Sub rb672O_CheckedChanged(sender As System.Object, e As System.EventArgs) Handles rb672O.CheckedChanged
        gAnyChgMega = 1
    End Sub

    Private Sub rb672N_CheckedChanged(sender As System.Object, e As System.EventArgs) Handles rb672N.CheckedChanged
        gAnyChgMega = 1
    End Sub

    Private Sub rb684O_CheckedChanged(sender As System.Object, e As System.EventArgs) Handles rb684O.CheckedChanged
        gAnyChgMega = 1
    End Sub

    Private Sub rb684N_CheckedChanged(sender As System.Object, e As System.EventArgs) Handles rb684N.CheckedChanged
        gAnyChgMega = 1
    End Sub

    Private Sub txtAutres_TextChanged(sender As System.Object, e As System.EventArgs) Handles txtAutres.TextChanged
        gAnyChgMega = 1
    End Sub

    Private Sub txtCommMega_TextChanged(sender As System.Object, e As System.EventArgs) Handles txtCommMega.TextChanged
        gAnyChgMega = 1
    End Sub


    Private Sub txtDetails_TextChanged(sender As System.Object, e As System.EventArgs) Handles txtDetails.TextChanged
        gAnyChgMega = 1
    End Sub

    Private Sub txtDistrict_TextChanged(sender As System.Object, e As System.EventArgs) Handles txtDistrict.TextChanged
        gAnyChgMega = 1
    End Sub

    Private Sub txtExp_LostFocus(sender As Object, e As System.EventArgs) Handles txtExp.LostFocus
        If txtExp.TextLength < 4 And txtExp.Text <> "" Then
            MsgBox("Veuillez inscrire l'année sous le format YYYY!", vbOKOnly + vbInformation, "Expérience")
            txtExp.Focus()
        End If
    End Sub

    Private Sub txtExp_TextChanged(sender As System.Object, e As System.EventArgs) Handles txtExp.TextChanged
        gAnyChgMega = 1
    End Sub

    Private Sub txtSectBar_TextChanged(sender As System.Object, e As System.EventArgs) Handles txtSectBar.TextChanged
        gAnyChgMega = 1
    End Sub

    Public Function ChkChangeMega()
        ChkChangeMega = True

        'Déjà en commentaires

        'If gAnyChgMega = 1 And gVerifTablMega = False Then
        '    If MsgBox("Mettre les changements à jour ?", vbYesNo + vbQuestion, "Mégaprocès") = vbYes Then
        '        AddTablMega()
        '    End If
        'End If
    End Function

    Private Sub DisMegaAvo()
        'btnCalModifMega.Enabled = False
        'mskDateModifMega.Enabled = True
        dtpDateInsc.Enabled = False
        txtSectBar.Enabled = False
        txtDistrict.Enabled = False
        ckbFrancais.Enabled = False
        ckbAnglais.Enabled = False
        txtAutres.Enabled = False
        txtExp.Enabled = False
        txtDetails.Enabled = False
        pnlArt486.Enabled = False
        pnlArt672.Enabled = False
        pnlArt684.Enabled = False
        'pnlMegaProces.Enabled = False
        ckbTousDist.Enabled = False
        cklbDist.Enabled = False
        txtCommMega.Enabled = False
        'btnCalModifMega.Enabled = True
    End Sub

    Private Sub EnaMegaAvo()
        dtpDateInsc.Enabled = True
        txtSectBar.Enabled = True
        txtDistrict.Enabled = True
        ckbFrancais.Enabled = True
        ckbAnglais.Enabled = True
        txtAutres.Enabled = True
        txtExp.Enabled = True
        txtDetails.Enabled = True
        pnlArt486.Enabled = True
        pnlArt672.Enabled = True
        pnlArt684.Enabled = True     'false gris pas active
        'pnlMegaProces.Enabled = True
        ckbTousDist.Enabled = True
        cklbDist.Enabled = True
        txtCommMega.Enabled = True
    End Sub

    'Enregistrer Disctirct Avocat
    Private Sub EnrDistrictAvo()

        'Dim strSql As String
        Dim Conn As New ObjConn.ObjConn(strConnCardAvo)
        Dim indexchecked As Integer = Nothing



        Try
            'strSql = "select code,nodist from cardavo.dbo.infodistrict where code='" & objAvocat.code & "'"
            'Conn.ExecuteSql(strSql)

            'If Conn.NbRows > 0 Then
            Conn.ExecuteSql("DELETE from cardavo.dbo.infodistrict where code='" & objAvocat.code & "'")
            'End If
            For Each indexchecked In cklbDist.CheckedIndices
                Conn.ExecuteSql(" INSERT into infodistrict(code, nodist) VALUES('" & objAvocat.code & "'," & indexchecked + 1 & ")")
            Next
            If ckbTousDist.Checked = True Then
                Conn.ExecuteSql(" INSERT into infodistrict(code, nodist) VALUES('" & objAvocat.code & "',0)")
            End If


        Catch ex As Exception
            funcOutils.subErrorMessage(Err.Number, Err.Description, Me.GetType.Name, MethodInfo.GetCurrentMethod.Name)
        End Try

        Conn.CloseConn()

    End Sub

    'Enregistrer Mega
    Public Function EnrMega() As Boolean
        EnrMega = False

        SetObjMega()
        If gAvoMegaStatus = DOSSIER_NOUVEAU Then
            objinfomega.Save("")
        ElseIf gAvoMegaStatus = DOSSIER_MODIF Then
            objinfomega.Save(gCodeAvo)
        End If
        'rbMegaO.Checked = True
        'objAvocat.mega = "O"
        'objAvocat.Save(gCodeAvo, "web")
        EnrDistrictAvo()
        EnrMega = True

        'objAvocat.Load(gCodeAvo)
        gAvoMegaStatus = Nothing

        gAnyChgMega = 0
    End Function

    Private Sub InitMegaAvo()
        'mskDateModifMega.Text = "AAAA/MM/JJ"
        dtpdatemofifMega.Value = Now
        txtSectBar.Text = ""
        txtDistrict.Text = ""
        ckbFrancais.Checked = True
        ckbAnglais.Checked = False
        txtAutres.Text = ""
        txtExp.Text = ""
        txtDetails.Text = ""
        rb486N.Checked = False
        rb486O.Checked = False
        rb672N.Checked = False
        rb672O.Checked = False
        rb684N.Checked = False
        rb684O.Checked = False
        'rbMegaprocesN.Checked = False
        'rbMegaprocesO.Checked = False
        cklbDist.ClearSelected()
        txtCommMega.Text = Nothing
        'initilise check liste box
        While cklbDist.CheckedIndices.Count > 0
            cklbDist.SetItemChecked(cklbDist.CheckedIndices(0), False)
        End While
        gAnyChgMega = 0
    End Sub

    Private Sub LoadDistrictAvo()

        Dim conn As New ObjConn.ObjConn
        Dim dr As SqlDataReader
        Dim cmd As SqlCommand
        Dim strSQL As String = "select code,nodist from infodistrict where code= @code "
        Try
            conn.ConnString = strConnCardAvo

            cmd = New SqlCommand(strSQL, conn.OpenConn())
            cmd.Parameters.AddWithValue("@code", objAvocat.code)
            'Executer la command et assigne le contenu au recordset
            dr = cmd.ExecuteReader()

            '**Lire le recordset 
            While dr.Read
                If dr.GetInt32(1) = 0 Then
                    ckbTousDist.Checked = True
                Else
                    cklbDist.SetItemChecked(dr.GetInt32(1) - 1, True)
                End If
            End While

            'If dr.Read = True Then
            '    For i = 0 To dr.FieldCount - 1
            '        If dr.GetInt32(1) = 0 Then
            '            ckbTousDist.Checked = True
            '        Else
            '            cklbDist.SetItemChecked(dr.GetInt32(1) - 1, True)
            '        End If
            '    Next i
            'End If
            cmd.Connection.Close()
        Catch ex As Exception
            funcOutils.subErrorMessage(Err.Number, Err.Description, Me.GetType.Name, MethodInfo.GetCurrentMethod.Name)
        Finally
            conn.CloseConn()
        End Try

        '**********

        'Dim strSql As String
        'Dim i As Integer = 0
        'Dim Conn As New ObjConn.ObjConnOle(strConnCardAvo)
        'Dim MyDataRead As OleDb.OleDbDataReader = Nothing

        'Try
        '    strSql = "select code,nodist from infodistrict where code='" & objAvocat.code & "'"

        '    Conn.ExecuteSql(strSql, MyDataRead)
        '    If MyDataRead.HasRows Then
        '        For i = 0 To Conn.NbRows - 1
        '            MyDataRead.Read()
        '            If MyDataRead.GetInt32(1) = 0 Then
        '                ckbTousDist.Checked = True
        '            Else
        '                cklbDist.SetItemChecked(MyDataRead.GetInt32(1) - 1, True)
        '            End If
        '        Next i
        '    End If

        'Catch ex As Exception
        '    funcOutils.subErrorMessage(Err.Number, Err.Description, Me.GetType.Name, MethodInfo.GetCurrentMethod.Name)
        'End Try

        'Conn.CloseConn()

    End Sub


    Private Sub LoadMega(codeavo As String)
        objinfomega.Load(codeavo)
        If gMega = True Then
            SetTxtMega()
            LoadDistrictAvo()
            gAnyChgMega = 0
        End If
    End Sub

    Public Sub NouvMegaAvo()
        EnaMegaAvo()

        gAvoMegaStatus = DOSSIER_NOUVEAU

        ckbFrancais.Checked = 1
        ckbAnglais.Checked = 0
    End Sub

    Public Function ReqEnrMegaAvo() As Boolean

        ReqEnrMegaAvo = False

        Me.Text = "Enregistrement en cours..."
        If EnrMega() = False Then
            MsgBox("L'enregistrement a échoué, veuillez vérifier vos données!", vbCritical + vbOKOnly, "Méga")
            txtSectBar.Focus()
            Exit Function
        End If
        ReqEnrMegaAvo = True
        gAnyChgMega = 0
        LoadMega(txtCode.Text)
        DisMegaAvo()
        subDebloqueTabPage()
        tsbNouveau.Enabled = False
        tsbModifier.Enabled = True
        tsbSave.Enabled = False
        tsbCancel.Enabled = False

        Me.Text = txtPrenom.Text.Trim & " " & txtNom.Text.Trim & " (" & txtCode.Text.Trim & ")"

    End Function

    Private Sub SetObjMega()
        objinfomega.code = txtCode.Text
        If ckbFrancais.Checked = True Then
            objinfomega.francais = "O"
        Else
            objinfomega.francais = "N"
        End If
        If ckbAnglais.Checked = True Then
            objinfomega.anglais = "O"
        Else
            objinfomega.anglais = "N"
        End If
        objinfomega.autres = txtAutres.Text.Trim
        objinfomega.experience = Val(txtExp.Text)
        objinfomega.details = txtDetails.Text.Trim
        'If rbMegaprocesO.Checked = True Then
        '    objinfomega.mega = "O"
        'Else
        '    objinfomega.mega = "N"
        'End If
        objinfomega.tarification = ""
        If rb486O.Checked = True Then
            objinfomega.art486 = "O"
        Else
            objinfomega.art486 = "N"
        End If
        If rb672O.Checked = True Then
            objinfomega.art672 = "O"
        Else
            objinfomega.art672 = "N"
        End If
        If rb684O.Checked = True Then
            objinfomega.art684 = "O"
        Else
            objinfomega.art684 = "N"
        End If
        objinfomega.districthab = txtDistrict.Text.Trim
        objinfomega.commentaire = txtCommMega.Text.Trim
        objinfomega.dateinsc = dtpDateInsc.Value
        objinfomega.usermodif = vgUser
        dtpdatemofifMega.Value = Now
        If gAvoWebStatus = DOSSIER_MODIF Then
            'objinfomega.datemodif = mskDateModifMega.Text
        End If
        objinfomega.sectbar = txtSectBar.Text.Trim

    End Sub

    Private Sub SetTxtMega()
        dtpDateInsc.Value = objinfomega.dateinsc
        txtSectBar.Text = objinfomega.sectbar
        txtDistrict.Text = objinfomega.districthab
        ckbFrancais.Checked = IIf(objinfomega.francais = "O", True, False)
        ckbAnglais.Checked = IIf(objinfomega.anglais = "O", True, False)
        txtAutres.Text = objinfomega.autres
        txtExp.Text = objinfomega.experience
        txtDetails.Text = objinfomega.details
        dtpdatemofifMega.Value = objinfomega.datemodif
        If objinfomega.art486 = "O" Then
            rb486O.Checked = True
            rb486N.Checked = False
        Else
            rb486O.Checked = False
            rb486N.Checked = True
        End If
        If objinfomega.art672 = "O" Then
            rb672O.Checked = True
            rb672N.Checked = False
        Else
            rb672O.Checked = False
            rb672N.Checked = True
        End If
        If objinfomega.art684 = "O" Then
            rb684O.Checked = True
            rb684N.Checked = False
        Else
            rb684O.Checked = False
            rb684N.Checked = True
        End If
        'If objinfomega.mega = "O" Then
        '    rbMegaprocesO.Checked = True
        '    rbMegaprocesN.Checked = False
        'Else
        '    rbMegaprocesO.Checked = False
        '    rbMegaprocesN.Checked = True
        'End If
        txtCommMega.Text = objinfomega.commentaire

    End Sub

#End Region ' "***  Mega  ***"


#Region "***  Adresse  ***"

    Private Function funvalidateadresse() As Boolean
        Dim bReturn As Boolean = True
        If txtAdresse.Text = "" Then
        End If
        Return True
    End Function


    Private Sub dgvAdresse_Click(sender As Object, e As System.EventArgs) Handles dgvAdresse.Click
        If dgvAdresse.RowCount > 0 And IsDBNull(dgvAdresse.CurrentRow.Cells(0).Value) = False Then
            If ChkChangeAdr() = True Then
                If dgvAdresse.CurrentRow.Cells(0).Value <> "" Then
                    InitAdrAvo()
                    SetTxtAdr()
                    'DisAdrAvo()
                    tsbNouveau.Enabled = True
                    tsbModifier.Enabled = True
                    tsbSave.Enabled = False
                    tsbDelete.Enabled = True
                    tsbCancel.Enabled = False

                End If
            End If
        End If

    End Sub

    'Private Sub lblFermCalMega_Click(sender As System.Object, e As System.EventArgs)
    '    pnlCalModifMega.Visible = False
    'End Sub


    Private Sub mskCodePostal_KeyPress(sender As Object, e As System.Windows.Forms.KeyPressEventArgs) Handles mskCodePostal.KeyPress
        If Asc(e.KeyChar) >= 97 And Asc(e.KeyChar) <= 122 Then
            e.KeyChar = Chr(Asc(e.KeyChar) - 32)
        End If
    End Sub

    Private Sub mskCodePostal_LostFocus(sender As Object, e As EventArgs) Handles mskCodePostal.LostFocus
        Try
            Dim strCP As String = mskCodePostal.Text.Trim
            strCP = funcOutils.funcRemoveCharacter(strCP, " ")
            Dim iLen As Integer = 0
            If strCP <> "" Then iLen = strCP.Length
            If iLen > 0 And iLen < 6 Then
                MessageBox.Show("Le code postal n'est pas valide!", "Validation", MessageBoxButtons.OK, MessageBoxIcon.Exclamation)
                tbAvocat.SelectedTab = tpAdr
                mskCodePostal.Focus()
            End If
        Catch ex As Exception

        End Try
    End Sub

    Private Sub mskCodePostal_TextChanged(sender As Object, e As System.EventArgs) Handles mskCodePostal.TextChanged
        gAnyChgAdr = 1
    End Sub



    'Private Sub mskDateAdr_TextChanged(sender As Object, e As System.EventArgs) Handles mskDateAdr.TextChanged
    '    gAnyChgAdr = 1
    'End Sub

    'Private Sub mskFax_KeyPress(sender As Object, e As System.Windows.Forms.KeyPressEventArgs) Handles mskFax.KeyPress
    '    If mskFax.SelectionStart = 0 Then
    '        If Asc(e.KeyChar) = 49 Then
    '            mskFax.Mask = "#-###-###-####"
    '        Else
    '            mskFax.Mask = "###-###-####"
    '        End If
    '    End If
    'End Sub

    ''Private Sub mskFax_LostFocus(sender As Object, e As System.EventArgs) Handles mskFax.LostFocus
    ''    Dim sTel As String
    ''    If Mid(mskFax.Text, 1, 3) = "800" Or Mid(mskFax.Text, 1, 3) = "855" Or Mid(mskFax.Text, 1, 3) = "866" Or _
    ''            Mid(mskFax.Text, 1, 3) = "877" Or Mid(mskFax.Text, 1, 3) = "888" Then
    ''        sTel = "1-" + mskFax.Text
    ''        mskFax.Mask = "#-###-###-####"
    ''        mskFax.Text = sTel
    ''    End If
    ''End Sub

    'Private Sub mskFax_TextChanged(sender As Object, e As System.EventArgs) Handles mskFax.TextChanged
    '    gAnyChgAdr = 1
    'End Sub

    'Private Sub mskTel_KeyDown(sender As Object, e As KeyEventArgs) Handles mskTel.KeyDown, mskTel2.KeyDown, mskFax.KeyDown
    '    Dim tTel = CType(sender, MaskedTextBox)
    '    If e.KeyCode = Keys.Back Or e.KeyCode = Keys.Delete Then
    '        Dim strTmpTel As String = funcOutils.funcRemoveCharacter(funcOutils.funcRemoveCharacter(tTel.Text, "("), ")")
    '        strTmpTel = funcOutils.funcRemoveCharacter(funcOutils.funcRemoveCharacter(strTmpTel, "-"), " ")
    '        'tTel.Mask = "###-###-####"
    '        tTel.Text = strTmpTel
    '    End If
    '    If e.KeyCode = Keys.Back Then
    '        tTel.SelectionStart = 0
    '    End If
    'End Sub

    'Private Sub mskTel_KeyPress(sender As Object, e As System.Windows.Forms.KeyPressEventArgs) Handles mskTel.KeyPress
    '    If mskTel.SelectionStart = 0 Then

    '        If Asc(e.KeyChar) = 49 Then
    '            mskTel.Mask = "#-###-###-####"
    '        Else
    '            mskTel.Mask = "###-###-####"
    '        End If
    '    End If
    'End Sub

    'Private Sub mskTel_LostFocus(sender As Object, e As System.EventArgs) Handles mskTel.LostFocus, mskTel2.LostFocus, mskFax.LostFocus
    '    Dim tTel = CType(sender, MaskedTextBox)
    '    Dim sTel As String

    '    Dim strTmpTel As String = funcOutils.funcRemoveCharacter(funcOutils.funcRemoveCharacter(tTel.Text, "("), ")")
    '    strTmpTel = funcOutils.funcRemoveCharacter(funcOutils.funcRemoveCharacter(strTmpTel, "-"), " ")
    '    If strTmpTel.Length <= 10 Then tTel.Mask = "###-###-####"
    '    tTel.Text = strTmpTel

    '    Dim vTel As String = tTel.Text.Trim
    '    vTel = funcOutils.funcRemoveCharacter(vTel, " ")
    '    Dim iLen As Integer = vTel.Length
    '    If iLen > 2 And iLen < 12 Then
    '        MessageBox.Show("Le numéro n'est pas valide!", "Validation", MessageBoxButtons.OK, MessageBoxIcon.Exclamation)
    '        tTel.Focus()
    '    Else
    '        If Mid(tTel.Text, 1, 3) = "800" Or Mid(tTel.Text, 1, 3) = "855" Or Mid(tTel.Text, 1, 3) = "866" Or _
    '            Mid(tTel.Text, 1, 3) = "877" Or Mid(tTel.Text, 1, 3) = "888" Then
    '            sTel = "1-" + tTel.Text
    '            tTel.Mask = "#-###-###-####"
    '            tTel.Text = sTel
    '        End If
    '    End If

    'End Sub

    'Private Sub mskTel_TextChanged(sender As Object, e As System.EventArgs) Handles mskTel.TextChanged
    '    Dim strTmpTel As String = mskTel.Text
    '    strTmpTel = funcOutils.funcRemoveCharacter(funcOutils.funcRemoveCharacter(mskTel.Text, "("), ")")
    '    strTmpTel = funcOutils.funcRemoveCharacter(funcOutils.funcRemoveCharacter(strTmpTel, "-"), " ")
    '    If strTmpTel.Length <= 10 Then mskTel.Mask = "###-###-####" Else mskTel.Mask = "#-###-###-####"
    '    mskTel.Text = strTmpTel
    '    gAnyChgAdr = 1
    'End Sub

    'Private Sub mskTel2_KeyPress(sender As Object, e As System.Windows.Forms.KeyPressEventArgs) Handles mskTel2.KeyPress
    '    If mskTel2.SelectionStart = 0 Then
    '        If Asc(e.KeyChar) = 49 Then
    '            mskTel2.Mask = "#-###-###-####"
    '        Else
    '            mskTel2.Mask = "###-###-####"
    '        End If
    '    End If
    'End Sub

    ''Private Sub mskTel2_LostFocus(sender As Object, e As System.EventArgs) Handles mskTel2.LostFocus
    ''    Dim sTel As String

    ''    If Mid(mskTel2.Text, 1, 3) = "800" Or Mid(mskTel2.Text, 1, 3) = "855" Or Mid(mskTel2.Text, 1, 3) = "866" Or _
    ''            Mid(mskTel2.Text, 1, 3) = "877" Or Mid(mskTel2.Text, 1, 3) = "888" Then
    ''        sTel = "1-" + mskTel2.Text
    ''        mskTel2.Mask = "#-###-###-####"
    ''        mskTel2.Text = sTel
    ''    End If
    ''End Sub

    'Private Sub mskTel2_TextChanged(sender As Object, e As System.EventArgs) Handles mskTel2.TextChanged
    '    gAnyChgAdr = 1
    'End Sub

    Private Sub txtAdresse_LostFocus(sender As Object, e As System.EventArgs) Handles txtAdresse.LostFocus
        txtAdresse.Text = funcOutils.funcReplaceChar(txtAdresse.Text, ",", " ")
    End Sub

    Private Sub txtAdresse_TextChanged(sender As System.Object, e As System.EventArgs) Handles txtAdresse.TextChanged
        gAnyChgAdr = 1
    End Sub

    Private Sub txtAdresse2_LostFocus(sender As Object, e As System.EventArgs) Handles txtAdresse2.LostFocus
        txtAdresse2.Text = funcOutils.funcReplaceChar(txtAdresse2.Text, ",", " ")
    End Sub

    Private Sub txtAdresse2_TextChanged(sender As System.Object, e As System.EventArgs) Handles txtAdresse2.TextChanged
        gAnyChgAdr = 1
    End Sub

    Private Sub txtAdresse3_LostFocus(sender As Object, e As System.EventArgs) Handles txtAdresse3.LostFocus
        txtAdresse3.Text = funcOutils.funcReplaceChar(txtAdresse3.Text, ",", " ")
    End Sub

    Private Sub txtAdresse3_TextChanged(sender As System.Object, e As System.EventArgs) Handles txtAdresse3.TextChanged
        gAnyChgAdr = 1
    End Sub

    Private Sub txtPoste_TextChanged(sender As System.Object, e As System.EventArgs) Handles txtPoste.TextChanged
        gAnyChgAdr = 1
    End Sub

    Private Sub txtPoste2_TextChanged(sender As System.Object, e As System.EventArgs) Handles txtPoste2.TextChanged
        gAnyChgAdr = 1
    End Sub

    Private Sub txtProvince_TextChanged(sender As System.Object, e As System.EventArgs)
        gAnyChgAdr = 1
    End Sub

    Private Sub txtType_TextChanged(sender As System.Object, e As System.EventArgs)
        gAnyChgAdr = 1
    End Sub

    Private Sub cboVille_TextChanged(sender As System.Object, e As System.EventArgs) Handles Cboville.TextChanged
        gAnyChgAdr = 1
    End Sub


    'Change adresse
    Public Function ChkChangeAdr()
        ChkChangeAdr = True

        If gAnyChgAdr = 1 Then
            If MsgBox("Mettre les changements à jour ?", vbYesNo + vbQuestion, "Adresses") = vbYes Then
                If ReqEnrAdrAvo() = False Then
                    ChkChangeAdr = False
                    Exit Function
                End If
            End If
            gAnyChgAdr = 0
        End If
    End Function

    Private Sub DisAdrAvo()
        gbAdresse.Enabled = False
        'Chktype.Enabled = False
        'txtAdresse.Enabled = False
        'txtAdresse2.Enabled = False
        'txtAdresse3.Enabled = False
        'Cboville.Enabled = False
        'CboProvince.Enabled = False
        'mskCodePostal.Enabled = False
        'txtTel.Enabled = False
        'txtPoste.Enabled = False
        'txtTel2.Enabled = False
        'txtPoste2.Enabled = False
        'txtFax.Enabled = False
        'dtpdateAdr.Enabled = False
    End Sub

    Private Sub EnaAdrAvo()
        gbAdresse.Enabled = True
        'Chktype.Enabled = True
        'txtAdresse.Enabled = True
        'txtAdresse2.Enabled = True
        'txtAdresse3.Enabled = True
        'Cboville.Enabled = True
        'CboProvince.Enabled = True
        'mskCodePostal.Enabled = True
        'txtTel.Enabled = True
        'txtPoste.Enabled = True
        'txtTel2.Enabled = True
        'txtPoste2.Enabled = True
        'txtFax.Enabled = True
        'dtpdateadr.Enabled = True
    End Sub

    Public Function EnrAdr() As Boolean
        EnrAdr = False

        SetObjAdrAvo()
        'SetObjAvo()
        If gAvoAdrStatus = DOSSIER_NOUVEAU Then ' SI C'EST UNE NOUVELLE ADRESSE
            objAdresse.Save(True) 'INSERT
            EnrAdr = True
        Else
            objAdresse.Save(False) 'UPDATE
            EnrAdr = True
        End If

        If Chktype.Checked = True Then
            objAdresse.FuncUpdateVilleref(txtCode.Text) '(objAdresse.code)propiete de la classe adresse (gCodeavo) variable global 
            objAvocat.Load(gCodeAvo) 'Refresh
            LoadWeb() 'Show the information got in the Avocat.Load to control
        End If

        'La ligne mega va être effacer si on enleve l'option mega 
        'If rbMegaN.Checked = True Then
        '    objinfomega.FuncUpdateMegaNon(txtCode.Text)
        '    LoadMega(gCodeAvo)
        'End If

        LoadAdr(gCodeAvo)
        InitAdrAvo() 'Clean fields adresse
        gAvoAdrStatus = Nothing
    End Function

    Private Sub InitAdrAvo()
        Chktype.Checked = True
        txtNoSeq.Text = ""
        txtAdresse.Text = ""
        txtAdresse2.Text = ""
        txtAdresse3.Text = ""
        Cboville.Text = ""
        CboProvince.Text = "QC"   'QC par default
        mskCodePostal.Text = ""
        txtTel.Text = ""
        txtPoste.Text = ""
        txtTel2.Text = ""
        txtPoste2.Text = ""
        txtFax.Text = ""
        txtAdrRowID.Clear()
        txtusermadr.Clear()
        txtdatemadr.Clear()
        dtpdateadr.Checked = True
        dtpdateadr.Text = DateTime.Now.Date '*****"AAAA/MM/JJ"
        ''Clean datagrid
        'dgvAdresse.Rows.Clear()         '******
        'dgvAdresse.DataSource = Nothing   '****
        gAnyChgAdr = 0
    End Sub

    Private Sub LoadAdr(strCodeAvo As String)
        Dim strSQL As String
        Dim dt As New DataTable

        Try
            strSQL = "select code, CASE courant WHEN 'O' THEN 'C' ELSE '' END as courant, rtrim(adresse) + ' ' + rtrim(ville) + ' ' + rtrim(province) as adr, "
            strSQL = strSQL + "adresse, ville, province, codepostal, telephone, telephone2, poste1, poste2, fax, "
            strSQL = strSQL + "adremail, noseq, adresse2, adresse3, dateadr from adresses where code= @strCodeAvo "
            strSQL = strSQL + "order by courant desc, noseq desc"

            Dim da As New SqlDataAdapter(strSQL, strConnCardAvo)
            da.SelectCommand.Parameters.Add("@strCodeAvo", SqlDbType.Char).Value = strCodeAvo

            da.Fill(dt)

            'txtNbAdr.Text = conn.NbRows

            With dgvAdresse

                .DataSource = dt

                .Columns("code").HeaderText = "code"
                .Columns("courant").HeaderText = "Type"
                .Columns("adr").HeaderText = "Adresse"
                .Columns("telephone").HeaderText = "Téléphone"
                .Columns("poste1").HeaderText = "Poste"
                .Columns("adremail").HeaderText = "Courriel"


                .Columns("code").Visible = False
                .Columns("adresse").Visible = False
                .Columns("ville").Visible = False
                .Columns("province").Visible = False
                .Columns("codepostal").Visible = False
                .Columns("telephone2").Visible = False
                .Columns("poste2").Visible = False
                .Columns("fax").Visible = False
                .Columns("noseq").Visible = False
                .Columns("adresse2").Visible = False
                .Columns("adresse3").Visible = False
                .Columns("dateadr").Visible = False


                .Columns("courant").Width = 50
                .Columns("adr").Width = 520
                .Columns("telephone").Width = 160
                .Columns("poste1").Width = 60
                .Columns("adremail").Width = 370

                .Columns("courant").DefaultCellStyle.Alignment = DataGridViewContentAlignment.MiddleCenter
                .Columns("poste1").DefaultCellStyle.Alignment = DataGridViewContentAlignment.MiddleCenter
                '.CurrentCell = .Rows(0).Cells(1)
                .Rows(0).Selected = True

                '.RowHeadersVisible = True

                .RowHeadersWidth = 10
            End With

            da.Dispose()
            dt.Dispose()

        Catch ex As Exception
            funcOutils.subErrorMessage(Err.Number, Err.Description, Me.GetType.Name, MethodInfo.GetCurrentMethod.Name)
        Finally

        End Try

        TrouveEmailCour()
        txtTaxes.Text = ValidRegTaxes()

        '****

        'Dim conn As New ObjConn.ObjConnOle(strConnCardAvo)
        'Dim binding1 As New BindingSource
        'Dim dr As OleDb.OleDbDataReader = Nothing
        'Dim strSql As String = ""


        'strSql = "select code, CASE courant WHEN 'O' THEN 'C' ELSE '' END as courant, rtrim(adresse) + ' ' + rtrim(ville) + ' ' + rtrim(province) as adr, "
        'strSql = strSql + "adresse, ville, province, codepostal, telephone, telephone2, poste1, poste2, fax, "
        'strSql = strSql + "adremail, noseq, adresse2, adresse3, dateadr from adresses where code='" & strCodeAvo & "' "
        'strSql = strSql + "order by courant desc, noseq desc"

        'Try
        '    conn.ExecuteSql(strSql, dr)
        '    If dr.HasRows Then
        '        binding1.DataSource = dr
        '        txtNbAdr.Text = conn.NbRows
        '        dgvAdresse.DataSource = binding1
        '        dgvAdresse.Columns("code").Visible = False
        '        dgvAdresse.Columns("courant").HeaderText = "Type"
        '        dgvAdresse.Columns("adr").HeaderText = "Adresse"
        '        dgvAdresse.Columns("adresse").Visible = False
        '        dgvAdresse.Columns("ville").Visible = False
        '        dgvAdresse.Columns("province").Visible = False
        '        dgvAdresse.Columns("codepostal").Visible = False
        '        dgvAdresse.Columns("telephone").HeaderText = "Téléphone"
        '        dgvAdresse.Columns("telephone2").Visible = False
        '        dgvAdresse.Columns("poste1").HeaderText = "Poste"
        '        dgvAdresse.Columns("poste2").Visible = False
        '        dgvAdresse.Columns("fax").Visible = False
        '        dgvAdresse.Columns("adremail").HeaderText = "Courriel"
        '        dgvAdresse.Columns("noseq").Visible = False
        '        dgvAdresse.Columns("adresse2").Visible = False
        '        dgvAdresse.Columns("adresse3").Visible = False
        '        dgvAdresse.Columns("dateadr").Visible = False
        '        dgvAdresse.Columns("courant").Width = 50
        '        dgvAdresse.Columns("adr").Width = 520
        '        dgvAdresse.Columns("telephone").Width = 160
        '        dgvAdresse.Columns("poste1").Width = 60
        '        dgvAdresse.Columns("adremail").Width = 370
        '        dgvAdresse.Columns("courant").DefaultCellStyle.Alignment = DataGridViewContentAlignment.MiddleCenter
        '        dgvAdresse.Columns("poste1").DefaultCellStyle.Alignment = DataGridViewContentAlignment.MiddleCenter
        '        dgvAdresse.CurrentCell = dgvAdresse.Rows(0).Cells(1)
        '        dgvAdresse.Rows(0).Selected = True
        '    End If
        'Catch ex As Exception
        '    funcOutils.subErrorMessage(Err.Number, Err.Description, Me.GetType.Name, MethodInfo.GetCurrentMethod.Name)
        'Finally
        '    dr.Close()
        '    dr = Nothing
        '    conn.CloseConn()
        '    conn = Nothing
        'End Try

        'TrouveEmailCour()
        'txtTaxes.Text = ValidRegTaxes()

    End Sub

    'Public Sub DelAdrAvo()
    '    Try
    '        Dim gRowID As Guid
    '        gRowID = New Guid(txtAdrRowID.Text)
    '        If objAdresse.Funcdelete(gRowID) = True Then
    '            InitAdrAvo()
    '        End If



    '    Catch ex As Exception
    '        funcOutils.subErrorMessage(Err.Number, Err.Description, Me.GetType.Name, MethodInfo.GetCurrentMethod.Name)
    '    End Try


    'End Sub

    Public Sub NouvAdrAvo()

        Dim adremail As String = ""

        If gAnyChgAdr = 1 Then
            If MsgBox("Vous avez effectué des changements... Voulez-vous les enregistrer...", vbYesNo + vbQuestion, "Adresses") = vbYes Then
                If ReqEnrAdrAvo() = False Then
                    txtAdresse.Focus()
                    Exit Sub
                End If


            End If
        End If

        gAvoAdrStatus = DOSSIER_NOUVEAU
        If txtAdremail.Text <> "" Then adremail = txtAdremail.Text.Trim
        InitAdrAvo()
        EnaAdrAvo()
        Chktype.Checked = "True"
        Chktype.Enabled = True

        dtpDateModifAvo.Value = Now.Date
        'mskDateModif.Text = Today
        txtAdremail.Text = adremail
        txtAdresse.Focus()
    End Sub


    '*****************************************
    'Enregistrer adresse avocat
    '*****************************************
    Public Function ReqEnrAdrAvo() As Boolean
        Dim i As Integer = 0

        ReqEnrAdrAvo = False



        If Trim(txtAdresse.Text) <> "" And Trim(Cboville.Text) <> "" Then
            Me.Text = "Enregistrement en cours de l'adresse..."
            If gAvoAdrStatus = DOSSIER_NOUVEAU And Chktype.Checked = True Then
                If MsgBox("Enregistrer cette adresse comme nouvelle adresse courante ?", vbYesNo + vbQuestion, "Adresses") = vbYes Then
                    'vérifie ligne par ligne
                    'For i = 0 To dgvAdresse.Rows.Count - 1
                    '    If dgvAdresse.Rows(i).Cells(1).Value = "C" Then
                    '        dgvAdresse.Rows(i).Cells(1).Value = ""
                    '        objAdresse.Load(dgvAdresse.Rows(i).Cells(0).Value, dgvAdresse.Rows(i).Cells(13).Value)
                    '        objAdresse.courant = "N"
                    '        objAdresse.update(dgvAdresse.Rows(i).Cells(0).Value, dgvAdresse.Rows(i).Cells(13).Value)
                    '        Exit For
                    '    End If
                    'Next
                    If objAdresse.FuncSetcourantNbyAvocat(txtCode.Text) = False Then
                        Return False
                        Exit Function
                    End If

                Else
                    Chktype.Checked = False
                End If
            ElseIf Chktype.Checked = True And objAdresse.courant <> "C" Then
                If objAdresse.FuncExistAdrCourant(txtCode.Text.Trim) = True Then
                    Dim strReponse As String = MessageBox.Show("Il existe une adresse courante, voulez-vous la remplacer?", "Confirmation", MessageBoxButtons.YesNo, MessageBoxIcon.Question, MessageBoxDefaultButton.Button2)
                    If strReponse = vbYes Then
                        If objAdresse.FuncSetcourantNbyAvocat(txtCode.Text) = False Then
                            Return False
                            Exit Function
                        End If
                    Else
                        Chktype.Checked = False
                    End If
                End If
            End If
            Me.Text = txtPrenom.Text.Trim & " " & txtNom.Text.Trim & " (" & txtCode.Text.Trim & ")"
            'If ValidAdrAvo(txtType.Text) = True Then
            gCodeAvo = txtCode.Text

            If EnrAdr() = False Then
                MsgBox("L'enregistrement a échoué, veuillez vérifier vos données!", vbCritical + vbOKOnly, "Adresse")
                txtAdresse.Focus()
                Exit Function
            End If
            'Else
            '    Exit Function
            'End If
        Else
            MsgBox("L'adresse et la ville de l'avocat sont obligatoires...", vbOKOnly + vbInformation, "Cardex avocat")
            Exit Function
        End If

        ReqEnrAdrAvo = True
        gAnyChgAdr = 0 'Initilize flag from modify
        DisAdrAvo() 'Set disable field adresse
        subDebloqueTabPage()
        tsbNouveau.Enabled = True
        tsbModifier.Enabled = False
        tsbSave.Enabled = False
        tsbCancel.Enabled = False
        dgvAdresse.Enabled = True

    End Function


    Public Sub SetObjAdrAvo()
        objAdresse.code = txtCode.Text ' txtType.Text

        objAdresse.adresse = txtAdresse.Text.Trim
        objAdresse.ville = Cboville.Text.Trim
        'If UCase(CboProvince.Text) = "QUÉBEC" Or UCase(txtProvince.Text) = "QUEBEC" Then
        '    txtProvince.Text = "QC"
        'End If
        objAdresse.province = CboProvince.Text.Trim
        objAdresse.codepostal = mskCodePostal.Text
        objAdresse.telephone = txtTel.Text
        objAdresse.telephone2 = txtTel2.Text
        objAdresse.fax = txtFax.Text
        objAdresse.adremail = txtAdremail.Text.Trim
        objAdresse.usermodif = vgUser
        If gAvoAdrStatus = DOSSIER_NOUVEAU Then
            'txtNoSeq.Text = ValidNoSeqAdr(Val(1))
            Dim iNewSeq As Integer = objAdresse.FuncGetMaxSeq(txtCode.Text.Trim)
            If iNewSeq < 0 Then
                'MessageBox.Show("Erreur")
                Exit Sub
            Else
                objAdresse.noseq = iNewSeq + 1
            End If
        Else
            objAdresse.noseq = Val(txtNoSeq.Text)
        End If

        objAdresse.adresse2 = txtAdresse2.Text.Trim
        objAdresse.adresse3 = txtAdresse3.Text.Trim
        If Chktype.Checked = True Then
            objAdresse.courant = "O"
            '    objAvocat.adrcour = Val(txtNoSeq.Text)
            '    SetObjAvo()
            '    objAvocat.Save(txtCode.Text, "avocat")
            '    objAvocat.Load(txtCode.Text)
        Else
            objAdresse.courant = "N"
        End If
        objAdresse.adremail = txtAdremail.Text
        If dtpdateadr.Checked = True Then
            objAdresse.dateadr = dtpdateadr.Value.Date
        Else
            objAdresse.dateadr = Nothing
        End If
        objAdresse.poste1 = txtPoste.Text.Trim
        objAdresse.poste2 = txtPoste2.Text.Trim
    End Sub


    '**********************
    'Adresse
    '**********************
    Private Sub SetTxtAdr()

        objAdresse.Load(dgvAdresse.CurrentRow.Cells(0).Value, dgvAdresse.CurrentRow.Cells(13).Value)


        If objAdresse.courant = "C" Then Chktype.Checked = True Else Chktype.Checked = False
        txtNoSeq.Text = objAdresse.noseq
        txtAdresse.Text = objAdresse.adresse
        txtAdresse2.Text = objAdresse.adresse2
        txtAdresse3.Text = objAdresse.adresse3
        Cboville.Text = objAdresse.ville
        CboProvince.Text = objAdresse.province
        mskCodePostal.Text = objAdresse.codepostal
        txtdatemadr.Text = objAdresse.datemodif
        txtusermadr.Text = objAdresse.usermodif
        'TELEPHONE 1
        Dim strTel As String = objAdresse.telephone.Trim
        strTel = funcOutils.funcRemoveParenthese(strTel)
        strTel = funcOutils.funcRemoveCharacter(strTel, "-")
        strTel = funcOutils.funcRemoveCharacter(strTel, " ")

        If strTel <> Nothing Then
            If strTel.Length = 10 Then
                txtTel.Text = funcOutils.formatPhoneNumber(strTel, "")
            ElseIf strTel.Length = 11 Then
                txtTel.Text = funcOutils.formatPhoneNumber(strTel, "#-###-###-####")
            End If
        Else
            txtTel.Clear()
        End If
        txtPoste.Text = objAdresse.poste1

        'TELEPHONE 2
        strTel = objAdresse.telephone2.Trim
        strTel = funcOutils.funcRemoveParenthese(strTel)
        strTel = funcOutils.funcRemoveCharacter(strTel, "-")
        strTel = funcOutils.funcRemoveCharacter(strTel, " ")

        If strTel <> Nothing Then
            If strTel.Length = 10 Then
                txtTel2.Text = funcOutils.formatPhoneNumber(strTel, "")
            ElseIf strTel.Length = 11 Then
                txtTel2.Text = funcOutils.formatPhoneNumber(strTel, "#-###-###-####")
            End If
        Else
            txtTel2.Clear()
        End If
        txtPoste2.Text = objAdresse.poste2
        'FAX
        strTel = objAdresse.fax.Trim
        strTel = funcOutils.funcRemoveParenthese(strTel)
        strTel = funcOutils.funcRemoveCharacter(strTel, "-")
        strTel = funcOutils.funcRemoveCharacter(strTel, " ")

        If strTel <> Nothing Then
            If strTel.Length = 10 Then
                txtFax.Text = funcOutils.formatPhoneNumber(strTel, "")
            ElseIf strTel.Length = 11 Then
                txtFax.Text = funcOutils.formatPhoneNumber(strTel, "#-###-###-####")
            End If
        Else
            txtFax.Clear()
        End If
        'If Mid(objAdresse.telephone, 1, 1) = "1" Then
        '    'mskTel.Mask = "#-###-###-####"
        'Else
        '    mskTel.Mask = "###-###-####"
        'End If
        'If Mid(objAdresse.telephone2, 1, 1) = "1" Then
        '    mskTel2.Mask = "#-###-###-####"
        'Else
        '    mskTel2.Mask = "###-###-####"
        'End If
        'If Mid(objAdresse.fax, 1, 1) = "1" Then
        '    mskFax.Mask = "#-###-###-####"
        'Else
        '    mskFax.Mask = "###-###-####"
        'End If
        'Dim strTmpTel1 As String = funcOutils.funcRemoveCharacter(funcOutils.funcRemoveCharacter(objAdresse.telephone, "("), ")")
        'strTmpTel1 = funcOutils.funcRemoveCharacter(funcOutils.funcRemoveCharacter(strTmpTel1, "-"), " ")
        'mskTel.Text = strTmpTel1
        'txtPoste.Text = objAdresse.poste1
        'Dim strTmpTel2 As String = funcOutils.funcRemoveCharacter(funcOutils.funcRemoveCharacter(objAdresse.telephone2, "("), ")") 'objAdresse.telephone2
        'strTmpTel2 = funcOutils.funcRemoveCharacter(funcOutils.funcRemoveCharacter(strTmpTel2, "-"), " ")
        'mskTel2.Text = strTmpTel2
        'txtPoste2.Text = objAdresse.poste2
        'Dim strTmpFax As String = funcOutils.funcRemoveCharacter(funcOutils.funcRemoveCharacter(objAdresse.fax, "("), ")") 'objAdresse.fax
        'strTmpFax = funcOutils.funcRemoveCharacter(funcOutils.funcRemoveCharacter(strTmpFax, "-"), " ")
        'mskFax.Text = strTmpFax
        If objAdresse.dateadr Is Nothing Then
            dtpdateadr.Checked = False
        Else
            dtpdateadr.Value = objAdresse.dateadr
            dtpdateadr.Checked = True
        End If
        gAnyChgAdr = 0
        txtAdrRowID.Text = objAdresse.RowId.ToString
    End Sub


    '***************************
    'Validation adresse courrant
    '***************************
    Public Function ValidAdrAvo(t As String) As Boolean

        Dim i As Integer
        Dim courant As Boolean

        ValidAdrAvo = True

        If t = "C" Then
            For i = 0 To dgvAdresse.Rows.Count - 1
                If dgvAdresse.Rows(i).Cells(1).Value = "C" And i <> dgvAdresse.CurrentRow.Index Then
                    MsgBox("Il ne peut y avoir qu'une seule adresse courante...", vbOKOnly + vbInformation, "Adresses")
                    ValidAdrAvo = False
                    Exit Function
                End If
            Next
        Else
            courant = False
            For i = 0 To dgvAdresse.Rows.Count - 1
                If dgvAdresse.Rows(i).Cells(1).Value = "C" Then
                    courant = True
                    Exit For
                End If
            Next
            If dgvAdresse.Rows.Count >= 1 And courant = False Then
                MsgBox("Vous devez spécifier une adresse courante...", vbOKOnly + vbInformation, "Adresses")
                ValidAdrAvo = False
            End If
        End If

    End Function


    '************************************************
    'Validation NoseqAdresse
    '************************************************
    Public Function ValidNoSeqAdr(iNoseq As Integer) As Integer
        Dim i As Integer
        For i = 0 To dgvAdresse.RowCount - 1
            If iNoseq = dgvAdresse.Rows(i).Cells(13).Value Then
                iNoseq = iNoseq + 1
                ValidNoSeqAdr(iNoseq)
            End If
        Next

        ValidNoSeqAdr = iNoseq
    End Function

    Private Sub dgvAdresse_DataError(sender As Object, e As DataGridViewDataErrorEventArgs) Handles dgvAdresse.DataError
        Dim str As String
        str = e.Context.ToString

    End Sub

#End Region ' "***  Adresse  ***"

#Region "***  Web  ***"

    Private Sub btnMotPasse1_Click(sender As System.Object, e As System.EventArgs) Handles btnMotPasse.Click
        Dim strReponse As String = MessageBox.Show("Voulez-vous reinitialiser les mot de passes de l'avocat?", "Confirmation", MessageBoxButtons.YesNo, MessageBoxIcon.Question, MessageBoxDefaultButton.Button2)
        If strReponse = vbYes Then
            subCreerPwd()
            If objAvocat.funcSavePwd(txtCodeWeb.Text.Trim, gMotPasse1, gMotPasse2, vgUser) = True Then
                objAvocat.motpasse1 = gMotPasse1
                objAvocat.motpasse2 = gMotPasse2
                MessageBox.Show("Les mot de passes ont été reinitialisés avec succés", "Confirmation", MessageBoxButtons.OK, MessageBoxIcon.Information)
                txtUserModif.Text = vgUser
            End If
        End If

    End Sub
    Private Sub subCreerPwd()
        Try
            Dim motpasse1 As String
            Dim motpasse2 As String

            Randomize()

            Do
                motpasse1 = Trim(Int((160000 * Rnd()) + 10000))
            Loop Until VerifMotPasseWeb(motpasse1, 1) = True And Len(motpasse1) > 4

            gMotPasse1 = motpasse1
            gAnyChgWeb = 1


            Randomize()

            Do
                motpasse2$ = Trim(Int((160000 * Rnd()) + 10000))
            Loop Until VerifMotPasseWeb(motpasse2, 2) = True And Len(motpasse2) > 4

            gMotPasse2 = motpasse2
            gAnyChgWeb = 1
        Catch ex As Exception
            funcOutils.subErrorMessage(Err.Number, Err.Description, Me.Name, MethodInfo.GetCurrentMethod.Name)
        End Try
    End Sub
    Private Sub txtCodeWeb_TextChanged(sender As System.Object, e As System.EventArgs) Handles txtCodeWeb.TextChanged
        gAnyChg = 1
    End Sub


    Public Function ChkChangeWeb()
        ChkChangeWeb = True

        If gAnyChg = 1 Then
            If MsgBox("Mettre les changements à jour ?", vbYesNo + vbQuestion, "Internet") = vbYes Then
                If ReqEnrWebAvo() = False Then
                    ChkChangeWeb = False
                    Exit Function
                End If
            End If
        End If
    End Function

    Private Sub DisWebAvo()
        gbparcourriel.Enabled = False
        gbparInternet.Enabled = False
        cboVilleRef.Enabled = False
        btnMotPasse.Visible = False
        'btnMotPasse2.Visible = False
    End Sub

    Private Sub EnaWebAvo()
        gbparcourriel.Enabled = True
        If rbinternetOui.Checked = True Then
            gbparInternet.Enabled = False
            btnMotPasse.Visible = True
        Else
            gbparInternet.Enabled = True
            btnMotPasse.Visible = False
        End If

        cboVilleRef.Enabled = False  'We cannot change the villeRef

        'btnMotPasse2.Visible = True
    End Sub

    Public Function EnrWeb() As Boolean
        EnrWeb = False

        objAvocat.datemodif = Today
        objAvocat.codeusager = txtCodeWeb.Text

        If rbinternetOui.Checked = True And objAvocat.factweb = "N" Then
            objAvocat.factweb = "O"
            subCreerPwd()
            objAvocat.motpasse1 = gMotPasse1
            objAvocat.motpasse2 = gMotPasse2
        ElseIf rbinternetNon.Checked = True Then
            objAvocat.factweb = "N"
        End If

        If rbcourrielOui.Checked = True Then
            objAvocat.confweb = "O"
        Else
            objAvocat.confweb = "N"
        End If

        objAvocat.villeref = cboVilleRef.SelectedValue
        objAvocat.usermodif = vgUser
        objAvocat.Save(gCodeAvo, "web")
        If gMotPasse1 <> "" Then
            rbFacWebO.Checked = True
        End If
        EnrWeb = True

        objAvocat.Load(gCodeAvo)
        gAvoWebStatus = Nothing    'was ""

        gAnyChgWeb = 0
    End Function

    Private Sub InitWebAvo()
        txtCodeWeb.Clear()
        rbcourrielNon.Checked = False
        rbcourrielOui.Checked = False
        rbinternetNon.Checked = False
        rbinternetOui.Checked = False
        cboVilleRef.SelectedValue = ""
        btnMotPasse.Visible = False
        'btnMotPasse2.Visible = False
    End Sub

    Private Sub LoadWeb()
        txtCodeWeb.Text = objAvocat.code
        gAnyChg = False
        If objAvocat.factweb = "O" Then
            rbinternetOui.Checked = True
            btnMotPasse.Visible = True
        Else
            rbinternetNon.Checked = True
            btnMotPasse.Visible = False
        End If

        If objAvocat.confweb = "O" Then
            rbcourrielOui.Checked = True
        Else
            rbcourrielNon.Checked = True
        End If
        If IsDBNull(objAvocat.villeref) = False Then
            If objAvocat.villeref <> Nothing Then
                cboVilleRef.SelectedValue = objAvocat.villeref.Trim
            End If
        End If
        gAnyChgWeb = 0
        'If objAvocat.factweb = "O" Then
        '    gbparInternet.Enabled = False
        'Else
        '    gbparInternet.Enabled = True
        'End If
    End Sub

    Public Sub NouvWebAvo()
        Randomize()

        txtCodeWeb.Text = txtCode.Text
        Do
            gMotPasse1 = Int((160000 * Rnd()) + 10000)
        Loop Until VerifMotPasseWeb(gMotPasse1, 1) = True
        Do
            gMotPasse2 = Int((160000 * Rnd()) + 10000)
        Loop Until VerifMotPasseWeb(gMotPasse2, 2) = True

        btnMotPasse.Enabled = False
        'btnMotPasse2.Enabled = False

        rbinternetOui.Checked = True
        rbcourrielOui.Checked = True
        gbparInternet.Enabled = False
        gbparcourriel.Enabled = True
        'cboVilleRef.Enabled = True

        gAvoWebStatus = DOSSIER_NOUVEAU
    End Sub

    Public Function ReqEnrWebAvo() As Boolean

        ReqEnrWebAvo = False

        Me.Text = "Enregistrement en cours..."
        If EnrWeb() = False Then
            MsgBox("L'enregistrement a échoué, veuillez vérifier vos données!", vbCritical + vbOKOnly, "Web")
            Exit Function
        End If
        ReqEnrWebAvo = True
        gAnyChgWeb = 0
        subDebloqueTabPage()
        DisWebAvo()

        Me.Text = txtPrenom.Text.Trim & " " & txtNom.Text.Trim & " (" & txtCode.Text.Trim & ")"

        tsbNouveau.Enabled = False
        tsbModifier.Enabled = True

        tsbSave.Enabled = False
        tsbCancel.Enabled = False
    End Function

    '*****************************************************************
    'Vérification mot de passe
    '*****************************************************************
    Public Function VerifMotPasseWeb(strMp As String, strO As Integer) As Boolean

        Dim conn As New ObjConn.ObjConn
        Dim dr As SqlDataReader
        Dim cmd As SqlCommand
        Dim strSQL As String = "select * from avocats "

        VerifMotPasseWeb = True

        Try
            conn.ConnString = strConnCardAvo

            If strO = 1 Then
                strSQL = strSQL & "where motpasse1 = @strMp "
            Else
                strSQL = strSQL & "where motpasse2 = @strMp "
            End If

            cmd = New SqlCommand(strSQL, conn.OpenConn())
            cmd.Parameters.AddWithValue("@strMp", strMp)
            'Executer la command et assigne le contenu au recordset
            dr = cmd.ExecuteReader()

            '**Lire le recordset 
            If dr.Read = True Then
                VerifMotPasseWeb = False
            End If
            cmd.Connection.Close()
        Catch ex As Exception
            funcOutils.subErrorMessage(Err.Number, Err.Description, Me.GetType.Name, MethodInfo.GetCurrentMethod.Name)
        Finally
            conn.CloseConn()
        End Try

        '**************************

        'Dim strSql As String
        'Dim Conn As New ObjConn.ObjConnOle(strConnCardAvo)
        'Dim MyDataRead As OleDb.OleDbDataReader = Nothing

        'VerifMotPasseWeb = True
        'Try
        '    strSql = "select * from avocats "
        '    If strO = 1 Then
        '        strSql = strSql & "where motpasse1='" & strMp & "'"
        '    Else
        '        strSql = strSql & "where motpasse2='" & strMp & "'"
        '    End If

        '    Conn.ExecuteSql(strSql, MyDataRead)
        '    If MyDataRead.HasRows Then
        '        VerifMotPasseWeb = False
        '    End If
        'Catch ex As Exception
        '    funcOutils.subErrorMessage(Err.Number, Err.Description, Me.GetType.Name, MethodInfo.GetCurrentMethod.Name)
        'End Try

        'Conn.CloseConn()

    End Function

#End Region ' "***  Web  ***"






#Region "***  Inhabilité ***"

    Private Sub dgvInh_Click(sender As Object, e As System.EventArgs) Handles dgvInh.Click
        If ChkChangeInh() = True Then
            If dgvInh.CurrentRow.Cells(0).Value <> "" Then
                SetTxtInh()
                DisInhAvo()
                tsbNouveau.Enabled = True
                tsbModifier.Enabled = True
                tsbSave.Enabled = False
                tsbDelete.Enabled = False  'false pour que la personne ne supprime pas le boutton est inactive dans inhabillité
                tsbCancel.Enabled = False
                gAnyChgInh = 0
            End If
        End If
    End Sub

    Private Sub dtpDateDebInh_ValueChanged(sender As System.Object, e As System.EventArgs) Handles dtpDateDebInh.ValueChanged
        If dtpDateDebInh.Value.Date > dtpDateFinInh.Value.Date Then
            dtpDateFinInh.Value = dtpDateDebInh.Value
        End If
        gAnyChgInh = 1
    End Sub

    Private Sub dtpDateFinInh_ValueChanged(sender As System.Object, e As System.EventArgs) Handles dtpDateFinInh.ValueChanged
        If dtpDateFinInh.Value.Date < dtpDateDebInh.Value.Date Then
            dtpDateDebInh.Value = dtpDateFinInh.Value
        End If
        gAnyChgInh = 1
    End Sub

    Private Sub txtCommInh_TextChanged(sender As System.Object, e As System.EventArgs) Handles txtCommInh.TextChanged
        gAnyChgInh = 1
    End Sub

    Public Function ChkChangeInh()
        ChkChangeInh = True

        If gAnyChgInh = 1 Then
            If MsgBox("Mettre les changements à jour ?", vbYesNo + vbQuestion, "Inhabilité") = vbYes Then
                Dim iId As Integer = Nothing
                If txtInhID.Text <> "" Then iId = txtInhID.Text
                If objInh.funcValidateDatePeriode(txtCode.Text.Trim, dtpDateDebInh.Value.Date, dtpDateFinInh.Value.Date, iId) = True Then
                    MessageBox.Show("xxxxxx")
                    Exit Function
                End If

                If ReqEnrInhAvo() = False Then
                    ChkChangeInh = False
                    Exit Function
                End If
            End If
            gAnyChgInh = 0
        End If
    End Function

    Private Sub DisInhAvo()
        dtpDateDebInh.Enabled = False
        dtpDateFinInh.Enabled = False
        txtCommInh.Enabled = False
    End Sub

    Private Sub EnaInhAvo()
        dtpDateDebInh.Enabled = True
        dtpDateFinInh.Enabled = True
        txtCommInh.Enabled = True
    End Sub

    Public Function EnrInh() As Boolean
        EnrInh = False
        Dim bNew As Boolean = False
        If gAvoInhStatus = DOSSIER_NOUVEAU Then
            bNew = True
            objInh.ID = Nothing
        Else
            objInh.ID = txtInhID.Text
        End If
        objInh.code = txtCode.Text
        objInh.datedeb = dtpDateDebInh.Value.Date
        objInh.datefin = dtpDateFinInh.Value.Date
        objInh.comm = txtCommInh.Text.Trim
        objInh.Save(bNew)
        EnrInh = True

        subDebloqueTabPage()
        LoadInh(gCodeAvo)
        InitInhAvo()
        gAvoInhStatus = 0    'erreur ok corrigé sql
    End Function

    Private Sub InitInhAvo()
        dtpDateDebInh.Text = Now.Date
        dtpDateFinInh.Text = Now.Date
        txtCommInh.Clear()
        txtInhID.Clear()
        'dgvInh.Rows.Clear()    mit en commentaire pour voir data grid avec l'information
        'dgvInh.DataSource = Nothing    mit en commentaire pour voir data grid avec l'information
        gAnyChgInh = 0
    End Sub

    Private Sub LoadInh(strCodeAvo As String)
        Dim strSQL As String
        Dim dt As New DataTable

        Try
            strSQL = "set dateformat ymd select code, datedeb, datefin, isnull(comm,'') as comm, id from inhpra where code= @strCodeAvo order by datedeb "

            Dim da As New SqlDataAdapter(strSQL, strConnCardAvo)
            da.SelectCommand.Parameters.Add("@strCodeAvo", SqlDbType.VarChar).Value = strCodeAvo

            da.Fill(dt)

            With dgvInh
                .DataSource = dt

                .Columns("code").Visible = False
                .Columns("datedeb").HeaderText = "Date début"
                .Columns("datefin").HeaderText = "Date fin"
                .Columns("comm").HeaderText = "Commentaires"
                .Columns("datedeb").Width = 170
                .Columns("datefin").Width = 170
                .Columns("comm").Width = 590
                .Columns("id").Width = 60
                .Columns("datedeb").DefaultCellStyle.Alignment = DataGridViewContentAlignment.MiddleCenter
                .Columns("datefin").DefaultCellStyle.Alignment = DataGridViewContentAlignment.MiddleCenter
                .ClearSelection()
                .RowHeadersWidth = 10
            End With

            da.Dispose()
            dt.Dispose()

        Catch ex As Exception
            funcOutils.subErrorMessage(Err.Number, Err.Description, Me.GetType.Name, MethodInfo.GetCurrentMethod.Name)
        Finally

        End Try




        'Dim strSQL As String
        'Dim dt As New DataTable

        'Dim binding1 As New BindingSource
        'Dim conn As New ObjConn.ObjConn
        'Dim dr As SqlDataReader
        'Dim cmd As SqlCommand
        'Dim strSQL As String = "set dateformat ymd select code, datedeb, datefin, isnull(comm,'') as comm, id from inhpra where code= @strCodeAvo order by datedeb "
        'Try
        '    conn.ConnString = strConnCardAvo

        '    cmd = New SqlCommand(strSQL, conn.OpenConn())
        '    cmd.Parameters.AddWithValue("@strCodeAvo", strCodeAvo)
        '    'Executer la command et assigne le contenu au recordset
        '    dr = cmd.ExecuteReader()

        '    '**Lire le recordset 
        '    If dr.Read = True Then
        '        binding1.DataSource = dr
        '        dgvInh.DataSource = binding1
        '        dgvInh.Columns("code").Visible = False
        '        dgvInh.Columns("datedeb").HeaderText = "Date début"
        '        dgvInh.Columns("datefin").HeaderText = "Date fin"
        '        dgvInh.Columns("comm").HeaderText = "Commentaires"
        '        dgvInh.Columns("datedeb").Width = 170
        '        dgvInh.Columns("datefin").Width = 170
        '        dgvInh.Columns("comm").Width = 590
        '        dgvInh.Columns("id").Width = 60
        '        dgvInh.Columns("datedeb").DefaultCellStyle.Alignment = DataGridViewContentAlignment.MiddleCenter
        '        dgvInh.Columns("datefin").DefaultCellStyle.Alignment = DataGridViewContentAlignment.MiddleCenter
        '        dgvInh.ClearSelection()
        '    End If
        '    cmd.Connection.Close()
        'Catch ex As Exception
        '    funcOutils.subErrorMessage(Err.Number, Err.Description, Me.GetType.Name, MethodInfo.GetCurrentMethod.Name)
        'Finally
        '    conn.CloseConn()
        'End Try

        '99999999999999999999999999999999999999999

        'Dim conn As New ObjConn.ObjConnOle(strConnCardAvo)
        'Dim binding1 As New BindingSource
        'Dim MyDataRead As OleDb.OleDbDataReader = Nothing
        'Dim strSql As String = ""

        'strSql = "set dateformat ymd select code, datedeb, datefin, isnull(comm,'') as comm, id from inhpra where code='" & strCodeAvo & "' order by datedeb"

        'Try
        '    conn.ExecuteSql(strSql, MyDataRead)
        '    If MyDataRead.HasRows Then
        '        binding1.DataSource = MyDataRead
        '        dgvInh.DataSource = binding1
        '        dgvInh.Columns("code").Visible = False
        '        dgvInh.Columns("datedeb").HeaderText = "Date début"
        '        dgvInh.Columns("datefin").HeaderText = "Date fin"
        '        dgvInh.Columns("comm").HeaderText = "Commentaires"
        '        dgvInh.Columns("datedeb").Width = 170
        '        dgvInh.Columns("datefin").Width = 170
        '        dgvInh.Columns("comm").Width = 590
        '        dgvInh.Columns("id").Width = 60
        '        dgvInh.Columns("datedeb").DefaultCellStyle.Alignment = DataGridViewContentAlignment.MiddleCenter
        '        dgvInh.Columns("datefin").DefaultCellStyle.Alignment = DataGridViewContentAlignment.MiddleCenter
        '        dgvInh.ClearSelection()
        '    End If
        'Catch ex As Exception
        '    funcOutils.subErrorMessage(Err.Number, Err.Description, Me.GetType.Name, MethodInfo.GetCurrentMethod.Name)
        'End Try

        'conn.CloseConn()

    End Sub



    Public Sub NouvInhAvo()
        If gAnyChgInh = 1 Then
            If MsgBox("Vous avez effectué des changements... Voulez-vous les enregistrer...", vbYesNo + vbQuestion, "Dates pratique") = vbYes Then
                If ReqEnrInhAvo() = False Then
                    txtCommInh.Focus()
                    Exit Sub
                End If
            End If
        End If

        gAvoInhStatus = DOSSIER_NOUVEAU
        InitInhAvo()
        EnaInhAvo()
        'dtpDateDebInh.Focus()
        txtCommInh.Focus()
    End Sub

    Public Function ReqEnrInhAvo() As Boolean

        ReqEnrInhAvo = False
        Dim iId As Integer = Nothing
        If txtInhID.Text <> "" Then iId = txtInhID.Text
        If objInh.funcValidateDatePeriode(txtCode.Text.Trim, dtpDateDebInh.Value.Date, dtpDateFinInh.Value.Date, iId) = True Then
            MessageBox.Show("Il existe déjà une periode pour cette date")
            Exit Function
        End If

        Me.Text = "Enregistrement en cours..." '.text = prenom nom P16911
        If EnrInh() = False Then
            MsgBox("L'enregistrement a échoué, veuillez vérifier vos données!", vbCritical + vbOKOnly, "Inhabilité")
            dtpDateDebInh.Focus()
            Exit Function
        End If
        ReqEnrInhAvo = True
        gAnyChgInh = 0

        DisInhAvo()

        Me.Text = txtPrenom.Text.Trim & " " & txtNom.Text.Trim & " (" & txtCode.Text.Trim & ")"

        tsbNouveau.Enabled = True
        tsbModifier.Enabled = False

        tsbSave.Enabled = False
        tsbCancel.Enabled = False
        tsbDelete.Enabled = False 'desactive le button dans onglet inabilité
    End Function

    Private Sub SetTxtInh()
        objInh.Load(dgvInh.CurrentRow.Cells(0).Value)
        dtpDateDebInh.Value = dgvInh.CurrentRow.Cells(1).Value
        dtpDateFinInh.Value = dgvInh.CurrentRow.Cells(2).Value
        txtCommInh.Text = dgvInh.CurrentRow.Cells(3).Value
        txtInhID.Text = dgvInh.CurrentRow.Cells(4).Value
    End Sub

#End Region ' "***  Inhabilité ***"  



    Private Sub frmAvocat_FormClosing(sender As Object, e As System.Windows.Forms.FormClosingEventArgs) Handles Me.FormClosing
        'If ChkChange() = True Then
        '    End
        'End If
    End Sub

    Private Sub frmAvocat_Load(sender As Object, e As System.EventArgs) Handles Me.Load
        'ToolStipStatusLabael
        TsslUser.Text = vgUser
        TsslServer.Text = vgServer
        TsslDB.Text = vgBD

        dtpDateInsc.MinDate = "2010-05-01"
        funcOutils.funcRemplirCombo(cboVilleRef, "Ville")
        funcOutils.funcRemplirCombo(Cboville, "Ville")
        'funcOutils.funcGetServeurs()

        InitAvo()
        If gCodeAvo <> "" Then
            LoadAvo()
        Else
            tpAdr.Enabled = False
            tpInh.Enabled = False
            tpWeb.Enabled = False
            tpMega.Enabled = False
        End If
        'SetToolStrip()
        tbAvocat.SelectedTab = tpIdent

    End Sub

#Region "*** tbavocat ***"
    Private Sub tbAvocat_Deselecting(sender As Object, e As System.Windows.Forms.TabControlCancelEventArgs) Handles tbAvocat.Deselecting
        Select Case tbAvocat.SelectedIndex
            Case 0 'IDENTIFICATION
                If tpAdr.Enabled = False Then e.Cancel = True
                If tpInh.Enabled = False Then e.Cancel = True
                If tpWeb.Enabled = False Then e.Cancel = True
                If tpMega.Enabled = False Then e.Cancel = True
            Case 1 'ADRESSES
                If tpIdent.Enabled = False Then e.Cancel = True
                If tpInh.Enabled = False Then e.Cancel = True
                If tpWeb.Enabled = False Then e.Cancel = True
                If tpMega.Enabled = False Then e.Cancel = True
            Case 2 'INH
                If tpAdr.Enabled = False Then e.Cancel = True
                If tpIdent.Enabled = False Then e.Cancel = True
                If tpWeb.Enabled = False Then e.Cancel = True
                If tpMega.Enabled = False Then e.Cancel = True
            Case 3 'WEB
                If tpAdr.Enabled = False Then e.Cancel = True
                If tpInh.Enabled = False Then e.Cancel = True
                If tpIdent.Enabled = False Then e.Cancel = True
                If tpMega.Enabled = False Then e.Cancel = True
            Case 4 'MEGA
                If tpAdr.Enabled = False Then e.Cancel = True
                If tpInh.Enabled = False Then e.Cancel = True
                If tpWeb.Enabled = False Then e.Cancel = True
                If tpIdent.Enabled = False Then e.Cancel = True
        End Select

    End Sub
    'tableau s
    'Private Sub tbAvocat_Selected(sender As Object, e As System.Windows.Forms.TabControlEventArgs) Handles tbAvocat.Selected
    '    'If e.TabPage Is tpIdent Then
    '    '    tsbNouveau.Enabled = True
    '    '    If gCodeAvo = Nothing Then tsbModifier.Enabled = False Else tsbModifier.Enabled = True
    '    '    tsbSave.Enabled = False
    '    '    tsbCancel.Enabled = False
    '    'ElseIf e.TabPage Is tpAdr Then
    '    '    'tsbNouveau.Enabled = True
    '    '    'If gAvoAdrStatus = DOSSIER_MODIF Then
    '    '    '    SetTxtAdr()
    '    '    '    DisAdrAvo()
    '    '    'End If

    '    'ElseIf e.TabPage Is tpInh Then
    '    '    'DisInhAvo()
    '    'ElseIf e.TabPage Is tpWeb Then
    '    '    'DisWebAvo()
    '    'ElseIf e.TabPage Is tpMega Then
    '    '    'DisMegaAvo()
    '    'End If
    'End Sub

    Private Sub tbAvocat_Selecting(sender As Object, e As System.Windows.Forms.TabControlCancelEventArgs) Handles tbAvocat.Selecting
        Dim dateform As String = ""

        Select Case tbAvocat.SelectedIndex
            Case 0 'INFO
                tsbNouveau.Enabled = True
                tsbModifier.Enabled = True
                tsbSave.Enabled = False
                tsbDelete.Enabled = False
                tsbCancel.Enabled = False
            Case 1 'ADRESSE
                tsbNouveau.Enabled = True
                tsbModifier.Enabled = False
                tsbSave.Enabled = False
                tsbDelete.Enabled = False
                tsbCancel.Enabled = False
            Case 2 'INH
                tsbNouveau.Enabled = True
                tsbModifier.Enabled = False
                tsbSave.Enabled = False
                tsbDelete.Enabled = False
                tsbCancel.Enabled = False
            Case 3 'WEB
                tsbNouveau.Enabled = False
                tsbModifier.Enabled = True
                tsbSave.Enabled = False
                tsbDelete.Enabled = False
                tsbCancel.Enabled = False
            Case 4 'MEGA
                If rbMegaO.Checked = True Then
                    If objinfomega.datemodif IsNot Nothing Then
                        tsbNouveau.Enabled = False
                        tsbModifier.Enabled = True
                    Else
                        tsbNouveau.Enabled = True
                        tsbModifier.Enabled = False
                    End If


                    tsbSave.Enabled = False
                    tsbDelete.Enabled = False
                    tsbCancel.Enabled = False
                Else
                    MessageBox.Show("L'avocat ne fait pas de Chapitre III", "Accès non valide", MessageBoxButtons.OK, MessageBoxIcon.Exclamation)
                    e.Cancel = True
                End If

        End Select

        'If e.TabPage Is tpIdent Then tsbSave.Enabled = False
        'tsbDelete.Enabled = False

        ''If e.TabPage Is tpWeb Or e.TabPage Is tpMega Or e.TabPage Is tpIdent Then
        ''    tsbDelete.Enabled = False
        ''ElseIf e.TabPage Is tpAdr Then
        ''    If dgvAdresse.RowCount > 0 Then tsbDelete.Enabled = True Else tsbDelete.Enabled = False
        ''Else
        ''    tsbDelete.Enabled = True
        ''End If


        ' ''WEB
        ''If e.TabPage Is tpWeb Then
        ''    If rbActifN.Checked = True Then
        ''        MsgBox("Vous ne pouvez pas accéder aux renseignements de l'onglet WEB" & Chr(13) & _
        ''                "puisque cet avocat est passif !", vbOKOnly + vbInformation, "Accès défendu")
        ''        e.Cancel = True
        ''    End If
        ''ElseIf e.TabPage Is tpMega And rbMegaN.Checked = True And gMega = False And vgGrUtil >= MEGA Then
        ''    If MsgBox("Cet avocat n'est pas inscrit à la facturation mégaprocès." & Chr(13) & _
        ''            "Désirez-vous l'ajouter? !", vbYesNo + vbInformation, "Accès défendu") = vbNo Then
        ''        e.Cancel = True
        ''        Exit Sub
        ''    Else
        ''        dateform = InputBox("Inscrivez la date de signature du formulaire" & Chr(13) & _
        ''                                  "sous le format yyyy/mm/dd", "Date d'inscription")
        ''        If dateform <> "" Then
        ''            dtpDateInsc.Text = dateform
        ''            rbMegaO.Checked = True
        ''        Else
        ''            MsgBox("Vous n'avez pas inscrit la date du formulaire", vbOKOnly, "Données manquantes")
        ''            e.Cancel = True
        ''        End If
        ''    End If
        ''    tsbDelete.Visible = False
        ''End If
    End Sub

#End Region '*** tbavocat ****

    Public Function ChkChange()
        ChkChange = True
        Dim strReponse As String = vbNo

        If gAnyChg = 1 Then
            strReponse = MessageBox.Show("Vous avez effectué des changements... Voulez-vous les enregistrer...", "Cardex avocats", MessageBoxButtons.YesNo, MessageBoxIcon.Exclamation, MessageBoxDefaultButton.Button2)
            If strReponse = vbYes Then
                Cursor.Current = System.Windows.Forms.Cursors.WaitCursor
                If ReqEnrAvo() = False Then
                    ChkChange = False
                    Exit Function
                End If
                Cursor.Current = System.Windows.Forms.Cursors.Arrow
            Else
                SubCancel()
            End If
            gAnyChg = 0
        End If

        'gVerifDepo = True
        'gVerifPay = True

    End Function

    Public Sub SetObjAvo()
        objAvocat.code = txtCode.Text
        If rbMegaO.Checked = True Then
            objAvocat.mega = "O"
        Else
            objAvocat.mega = "N"
        End If
        objAvocat.nom = txtNom.Text.Trim
        objAvocat.prenom = txtPrenom.Text.Trim
        If rbActifO.Checked = True Then
            objAvocat.actpass = "A"
        Else
            objAvocat.actpass = "P"
        End If
        objAvocat.dateinscbarr = txtAnnBar.Text
        If rbPayO.Checked = True Then
            objAvocat.payable = "O"
        Else
            objAvocat.payable = "N"
        End If
        objAvocat.codebar = txtCodeBar.Text.Trim
        objAvocat.comm = txtComm.Text.Trim.Trim
        objAvocat.datemodif = DateTime.Now.Date 'pour qui n'affiche pas les minutes avant Now.Date
        objAvocat.nas = mskNAS.Text

        If bNewAvocat = True And rbFacWebO.Checked = True Then
            subCreerPwd()
            objAvocat.motpasse1 = gMotPasse1
            objAvocat.motpasse2 = gMotPasse2
            bNewAvocat = False
            ' objAvocat.confweb = "N"     ********effacer cette ligne si mot passe fonctionne************************
        ElseIf bNewAvocat = False And objAvocat.factweb = "N" And rbFacWebO.Checked = True Then
            subCreerPwd()
            objAvocat.motpasse1 = gMotPasse1
            objAvocat.motpasse2 = gMotPasse2
        ElseIf rbFacWebN.Checked = True Then ' Nous avons mit les mot de passe a "" (quelle que chose) car le message dit que est NULL
            objAvocat.motpasse1 = ""
            objAvocat.motpasse2 = ""
        End If

        If rbDepoO.Checked = True Then
            objAvocat.depodirect = "O"
        Else
            objAvocat.depodirect = "N"
        End If
        If rbFacWebO.Checked = True Then
            objAvocat.factweb = "O"
        Else
            objAvocat.factweb = "N"
        End If
        objAvocat.usermodif = vgUser
    End Sub

    Private Sub SetTxtAvo()
        txtCode.Text = objAvocat.code
        txtNom.Text = objAvocat.nom
        txtPrenom.Text = objAvocat.prenom
        txtAnnBar.Text = objAvocat.dateinscbarr
        txtCodeBar.Text = objAvocat.codebar
        mskNAS.Text = objAvocat.nas

        If txtCode.Text.Substring(0, 2) = "A1" Then
            chkIsJordan.Checked = True
        Else
            chkIsJordan.Checked = False
        End If
        chkIsJordan.Enabled = False
        If objAvocat.factweb = "O" Then
            rbFacWebO.Checked = True
            rbFacWebN.Checked = False
            rbFacWebO.Enabled = False
            rbFacWebN.Enabled = False
        Else
            rbFacWebO.Checked = False
            rbFacWebN.Checked = True
            pnlFactWeb.Enabled = True
            rbFacWebO.Enabled = True
            rbFacWebN.Enabled = True
        End If
        If objAvocat.payable = "O" Then
            rbPayO.Checked = True
            rbPayN.Checked = False
        Else
            rbPayO.Checked = False
            rbPayN.Checked = True
        End If
        If objAvocat.surveil = "O" Then
            rbAttO.Checked = True
            rbAttN.Checked = False
            pnlAtt.Enabled = False  'pour desactiver car l'information viens de la table avocats>surveil Odette met a OUI>NON a partir de l'Article 52
        Else
            rbAttO.Checked = False
            rbAttN.Checked = True
            pnlAtt.Enabled = False   'pour desactiver car l'information viens de la table avocats>surveil Odette met a OUI>NON a partir de l'Article 52
        End If
        If objAvocat.actpass = "A" Then
            rbActifO.Checked = True
            rbActifN.Checked = False
        Else
            rbActifO.Checked = False
            rbActifN.Checked = True
        End If
        If objAvocat.depodirect = "O" Then
            rbDepoO.Checked = True
            rbDepoN.Checked = False
        Else
            rbDepoO.Checked = False
            rbDepoN.Checked = True
        End If
        If objAvocat.mega = "O" Then
            rbMegaO.Checked = True
            rbMegaN.Checked = False
        Else
            rbMegaO.Checked = False
            rbMegaN.Checked = True
        End If
        If objAvocat.datemodif <> "2001/01/01" Then
            dtpDateModifAvo.Value = objAvocat.datemodif
            'mskDateModif.Text = objAvocat.datemodif
        Else
            dtpDateModifAvo.Value = Now.Date
            'mskDateModif.Text = "AAAA/MM/JJ"
        End If
        txtUserModif.Text = objAvocat.usermodif
        txtComm.Text = objAvocat.comm
    End Sub






    ' ''' <summary>
    ' ''' Procedure qui bloque les autres onglets au moment qu'on modifie l'information d'un onglet (Index de tcDemande, index de Client)
    ' ''' </summary>
    Private Sub subBloqueTabPage(iIndex As Integer)
        If iIndex <> 0 Then tpIdent.Enabled = False
        If iIndex <> 1 Then tpAdr.Enabled = False
        If iIndex <> 2 Then tpInh.Enabled = False
        If iIndex <> 3 Then tpWeb.Enabled = False
        If iIndex <> 4 Then tpMega.Enabled = False
    End Sub

    Private Sub subDebloqueTabPage()
        tpIdent.Enabled = True
        tpAdr.Enabled = True
        tpInh.Enabled = True
        tpWeb.Enabled = True
        tpMega.Enabled = True
    End Sub


    Private Sub Chktype_CheckedChanged(sender As Object, e As EventArgs) Handles Chktype.CheckedChanged
        gAnyChgAdr = 1
    End Sub


    Private Sub dtpDateInsc_ValueChanged(sender As Object, e As EventArgs) Handles dtpDateInsc.ValueChanged
        gAnyChgMega = 1
    End Sub

    Private Sub txtTel_GotFocus(sender As Object, e As EventArgs) Handles txtTel.GotFocus, txtTel2.GotFocus, txtFax.GotFocus
        Dim tTel = CType(sender, TextBox)
        Dim strTel As String = tTel.Text.Trim
        strTel = funcOutils.funcRemoveParenthese(strTel)
        strTel = funcOutils.funcRemoveCharacter(strTel, "-")
        strTel = funcOutils.funcRemoveCharacter(strTel, " ")
        tTel.Text = strTel

    End Sub

    Private Sub txtTel_KeyPress(sender As Object, e As KeyPressEventArgs) Handles txtTel.KeyPress, txtTel2.KeyPress, txtFax.KeyPress
        funcOutils.subTextBoxNumber(sender, e, 0)
    End Sub

    Private Sub txtTel_LostFocus(sender As Object, e As EventArgs) Handles txtTel.LostFocus, txtTel2.LostFocus, txtFax.LostFocus
        Try
            Dim tTel = CType(sender, TextBox)
            If tTel.Text.Trim <> "" Then
                Dim strTel As String = tTel.Text.Trim
                strTel = funcOutils.funcRemoveParenthese(strTel)
                strTel = funcOutils.funcRemoveCharacter(strTel, "-")
                strTel = funcOutils.funcRemoveCharacter(strTel, " ")

                If strTel.Length = 10 Then
                    If Mid(strTel, 1, 3) = "800" Or Mid(strTel, 1, 3) = "855" Or Mid(strTel, 1, 3) = "866" Or Mid(strTel, 1, 3) = "877" Or Mid(strTel, 1, 3) = "888" Then
                        strTel = "1" & strTel.Trim
                        strTel = funcOutils.formatPhoneNumber(strTel, "#-###-###-####")
                        txtTel.Text = strTel
                    Else
                        strTel = funcOutils.formatPhoneNumber(strTel, "")
                        tTel.Text = strTel
                    End If
                ElseIf strTel.Length = 11 Then
                    strTel = funcOutils.formatPhoneNumber(strTel, "#-###-###-####")
                    tTel.Text = strTel
                Else
                    MessageBox.Show("Erreur")
                End If
            End If
        Catch ex As Exception

        End Try
    End Sub

    Private Sub dtpdateadr_ValueChanged(sender As Object, e As EventArgs) Handles dtpdateadr.ValueChanged
        gAnyChgAdr = 1
    End Sub

    Private Sub txtTel_TextChanged(sender As Object, e As EventArgs) Handles txtTel.TextChanged
        gAnyChgAdr = 1
    End Sub

    Private Sub txtTel2_TextChanged(sender As Object, e As EventArgs) Handles txtTel2.TextChanged
        gAnyChgAdr = 1
    End Sub

    Private Sub txtFax_TextChanged(sender As Object, e As EventArgs) Handles txtFax.TextChanged
        gAnyChgAdr = 1
    End Sub

    Private Sub txtusermadr_TextChanged(sender As Object, e As EventArgs) Handles txtusermadr.TextChanged
        gAnyChgAdr = 1
    End Sub

    Private Sub txtdatemadr_TextChanged(sender As Object, e As EventArgs) Handles txtdatemadr.TextChanged
        gAnyChgAdr = 1
    End Sub

    Private Sub mskCodePostal_MaskInputRejected(sender As Object, e As MaskInputRejectedEventArgs) Handles mskCodePostal.MaskInputRejected
        gAnyChgAdr = 1
    End Sub

    Private Sub txtAdremail_TextChanged(sender As Object, e As EventArgs) Handles txtAdremail.TextChanged
        gAnyChg = 1
    End Sub

    Private Sub rbPayN_CheckedChanged(sender As Object, e As EventArgs) Handles rbPayN.CheckedChanged
        gAnyChg = 1
    End Sub

    Private Sub rbDepoN_CheckedChanged(sender As Object, e As EventArgs) Handles rbDepoN.CheckedChanged
        gAnyChg = 1
    End Sub

    Private Sub chkIsJordan_CheckedChanged(sender As Object, e As EventArgs) Handles chkIsJordan.CheckedChanged
        subCalculateCode()
    End Sub

    Private Sub rbcourrielOui_CheckedChanged(sender As Object, e As EventArgs) Handles rbcourrielOui.CheckedChanged
        gAnyChgWeb = 1
    End Sub

    Private Sub rbinternetOui_CheckedChanged(sender As Object, e As EventArgs) Handles rbinternetOui.CheckedChanged
        gAnyChgWeb = 1
    End Sub

    

End Class