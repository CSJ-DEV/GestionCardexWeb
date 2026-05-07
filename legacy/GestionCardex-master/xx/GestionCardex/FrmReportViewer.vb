
Imports CrystalDecisions.CrystalReports.Engine
Imports CrystalDecisions.Shared
Imports System.Windows.Forms

Public Class FrmReportViewer

    Private reportPath As String = "\\CSJ-ART52\Art52\Rapports\Cardex\"
    Private myReportDocument As ReportDocument
    Private gparam As String

    Private Sub frmRapport_Load(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles MyBase.Load
        Me.WindowState = FormWindowState.Maximized
    End Sub
    Public Sub afficherRapport(titre As String, Optional frmlisterapports As FrmListeRapports = Nothing)

        Dim strFormula As String
        strFormula = ""
        Dim s As String
        reportPath = reportPath & titre
        myReportDocument = New ReportDocument()
        Try

            myReportDocument.Load(reportPath)
            Select Case titre
                Case "ListeDetBar.rpt", "ListeDetDist.rpt", "ListeDetReg.rpt"

                    s = getParameters(frmlisterapports)
                    strFormula = s

                    myReportDocument.RecordSelectionFormula = strFormula

                Case "ListeSom.rpt"
                    s = getParameters(frmlisterapports)
                    strFormula = s

                    If frmlisterapports.Alpha = True Then
                        strFormula = s

                        gparam = gparam + ", par ordre alphabétique"
                        myReportDocument.SetParameterValue("tri", "Alpha")

                    End If
                    If frmlisterapports.AnneB = True Then
                        strFormula = s

                        gparam = gparam + ", par ordre d'année de barreau"
                        myReportDocument.SetParameterValue("tri", "anneb")


                    End If
                    myReportDocument.RecordSelectionFormula = strFormula

            End Select



            CrystalReportViewer1.ReportSource = myReportDocument
            CrystalReportViewer1.Show() 'affiche le rappport




        Catch ex As Exception
            MsgBox(ex.Message)
        End Try


    End Sub


    Public Function getParameters(frmlisterapports As FrmListeRapports)


        Dim s
        Dim i%



        s = "{Avocats.mega}='O' and {Adresses.courant}='O'  "
        gparam = "Selon les paramètres suivants :  "

        'Langues

        If FrmListeRapports.langueFr = "Français" Or FrmListeRapports.langueAn = "Anglais" Or FrmListeRapports.autre <> "" Then
            s = s + "and ("
            If frmlisterapports.langueFr = "Français" Then
                s = s + "{infomega.francais}='O' or "
                gparam = gparam + "parle français, "



            End If
            If FrmListeRapports.langueAn = "Anglais" Then
                s = s + "{infomega.anglais}='O' or "
                gparam = gparam + "parle anglais, "
            End If
            If FrmListeRapports.autre <> "" Then
                s = s + "instr({infomega.autres},'" & Trim(FrmListeRapports.autre) & "')>0 "
                gparam = gparam + "parle " + Trim(FrmListeRapports.autre) + ", "
            End If
            If Microsoft.VisualBasic.Right(s, 3) = "or " Then
                i% = Len(s)
                s = Microsoft.VisualBasic.Left(Trim(s), i% - 4) + ") "
            Else
                s = s + ") "    'afiche tous {Avocats.mega}='O' and {Adresses.courant}='O' 
            End If

        End If

        'Articles
        If FrmListeRapports.Art486 = "Art. 486.3" Or FrmListeRapports.Art684 = "Art. 684" Or FrmListeRapports.Art672 = "Art. 672.5" Or FrmListeRapports.Mega = "Mégaprocès" Then
            s = s + "and ("
            If FrmListeRapports.Art486 = "Art. 486.3" Then
                s = s + "{infomega.art486}='O' or "
                gparam = gparam + "art. 486.3, "
            End If
            If FrmListeRapports.Art684 = "Art. 684" Then
                s = s + "{infomega.art672}='O' or "
                gparam = gparam + "art. 672, "
            End If
            If FrmListeRapports.Art672 = "Art. 672.5" Then
                s = s + "{infomega.art684}='O' or "
                gparam = gparam + "art. 684, "
            End If
            If FrmListeRapports.Mega = "Mégaprocès" Then
                s = s + "{infomega.mega}='O'"
                gparam = gparam + "cause longue et complexe, "
            End If
            If Microsoft.VisualBasic.Right(s, 3) = "or " Then
                i% = Len(s)
                s = Microsoft.VisualBasic.Left(Trim(s), i% - 4) + ") "
            Else
                s = s + ") "
            End If
        End If
        If FrmListeRapports.exp <> "" Then
            s = s + "and {infomega.experience}>=" & Trim(FrmListeRapports.exp)
            gparam = gparam + "au moins " + Trim(FrmListeRapports.exp) + " ans d'expérience, "
        End If

        'Districts
        If FrmListeRapports.dist = True Then
            s = s + "and ({infodistrict.nodist}=0 or "
            gparam = gparam + " dans tous les districts ou "
        Else
            s = s + "and ("
            gparam = gparam + " dans "
        End If
        For i = 0 To 35
            If FrmListeRapports.CheckedListBox1.GetItemChecked(i) = True Then
                s = s + "{infodistrict.nodist}=" & i + 1 & " or "
                'gparam = gparam + gTablDistrict(0, i%, 0, 0) + ", "
            End If
        Next i
        If Microsoft.VisualBasic.Right(gparam, 2) = ", " Then
            gparam = Microsoft.VisualBasic.Left(gparam, (Len(gparam) - 2))
        ElseIf Microsoft.VisualBasic.Right(gparam, 3) = "et " Then
            gparam = Microsoft.VisualBasic.Left(gparam, (Len(gparam) - 3))
        ElseIf Microsoft.VisualBasic.Right(gparam, 5) = "dans " Then
            gparam = Microsoft.VisualBasic.Left(gparam, (Len(gparam) - 5))
        End If

        If Microsoft.VisualBasic.Right(s, 3) = "or " Then
            i% = Len(s)
            s = Microsoft.VisualBasic.Left(Trim(s), i% - 4) + ")"
        ElseIf Microsoft.VisualBasic.Right(s, 5) = "and (" Then
            i% = Len(s)
            s = Microsoft.VisualBasic.Left(s, i% - 6)
        End If

        getParameters = s

    End Function

    Private Sub CrystalReportViewer1_Load(sender As Object, e As EventArgs) Handles CrystalReportViewer1.Load

    End Sub
End Class