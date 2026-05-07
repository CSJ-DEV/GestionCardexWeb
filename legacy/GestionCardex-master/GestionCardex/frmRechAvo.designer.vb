<Global.Microsoft.VisualBasic.CompilerServices.DesignerGenerated()> _
Partial Class frmRechAvo
    Inherits System.Windows.Forms.Form

    'Form remplace la méthode Dispose pour nettoyer la liste des composants.
    <System.Diagnostics.DebuggerNonUserCode()> _
    Protected Overrides Sub Dispose(ByVal disposing As Boolean)
        Try
            If disposing AndAlso components IsNot Nothing Then
                components.Dispose()
            End If
        Finally
            MyBase.Dispose(disposing)
        End Try
    End Sub

    'Requise par le Concepteur Windows Form
    Private components As System.ComponentModel.IContainer

    'REMARQUE : la procédure suivante est requise par le Concepteur Windows Form
    'Elle peut être modifiée à l'aide du Concepteur Windows Form.  
    'Ne la modifiez pas à l'aide de l'éditeur de code.
    <System.Diagnostics.DebuggerStepThrough()> _
    Private Sub InitializeComponent()
        Me.components = New System.ComponentModel.Container()
        Dim DataGridViewCellStyle1 As System.Windows.Forms.DataGridViewCellStyle = New System.Windows.Forms.DataGridViewCellStyle()
        Dim DataGridViewCellStyle2 As System.Windows.Forms.DataGridViewCellStyle = New System.Windows.Forms.DataGridViewCellStyle()
        Dim resources As System.ComponentModel.ComponentResourceManager = New System.ComponentModel.ComponentResourceManager(GetType(frmRechAvo))
        Me.Label1 = New System.Windows.Forms.Label()
        Me.Label2 = New System.Windows.Forms.Label()
        Me.Label3 = New System.Windows.Forms.Label()
        Me.dgvRech = New System.Windows.Forms.DataGridView()
        Me.btnRech = New System.Windows.Forms.Button()
        Me.btnOuvrir = New System.Windows.Forms.Button()
        Me.cboCodeAvo = New System.Windows.Forms.ComboBox()
        Me.cboNomAvo = New System.Windows.Forms.ComboBox()
        Me.btnCardex = New System.Windows.Forms.Button()
        Me.btnFermer = New System.Windows.Forms.Button()
        Me.Chktous = New System.Windows.Forms.CheckBox()
        Me.btnNouvRech = New System.Windows.Forms.Button()
        Me.ToolTip1 = New System.Windows.Forms.ToolTip(Me.components)
        CType(Me.dgvRech, System.ComponentModel.ISupportInitialize).BeginInit()
        Me.SuspendLayout()
        '
        'Label1
        '
        Me.Label1.AutoSize = True
        Me.Label1.Font = New System.Drawing.Font("Arial", 12.0!, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, CType(0, Byte))
        Me.Label1.ForeColor = System.Drawing.SystemColors.ActiveCaptionText
        Me.Label1.Location = New System.Drawing.Point(12, 11)
        Me.Label1.Name = "Label1"
        Me.Label1.Size = New System.Drawing.Size(141, 18)
        Me.Label1.TabIndex = 7
        Me.Label1.Text = "Rechercher selon..."
        '
        'Label2
        '
        Me.Label2.AutoSize = True
        Me.Label2.Font = New System.Drawing.Font("Arial", 12.0!, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, CType(0, Byte))
        Me.Label2.Location = New System.Drawing.Point(12, 48)
        Me.Label2.Name = "Label2"
        Me.Label2.Size = New System.Drawing.Size(55, 18)
        Me.Label2.TabIndex = 8
        Me.Label2.Text = "Code :"
        '
        'Label3
        '
        Me.Label3.AutoSize = True
        Me.Label3.Font = New System.Drawing.Font("Arial", 12.0!, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, CType(0, Byte))
        Me.Label3.Location = New System.Drawing.Point(12, 82)
        Me.Label3.Name = "Label3"
        Me.Label3.Size = New System.Drawing.Size(49, 18)
        Me.Label3.TabIndex = 9
        Me.Label3.Text = "Nom :"
        '
        'dgvRech
        '
        Me.dgvRech.AllowUserToAddRows = False
        Me.dgvRech.AllowUserToDeleteRows = False
        Me.dgvRech.AllowUserToOrderColumns = True
        Me.dgvRech.Anchor = CType((((System.Windows.Forms.AnchorStyles.Top Or System.Windows.Forms.AnchorStyles.Bottom) _
            Or System.Windows.Forms.AnchorStyles.Left) _
            Or System.Windows.Forms.AnchorStyles.Right), System.Windows.Forms.AnchorStyles)
        Me.dgvRech.BackgroundColor = System.Drawing.SystemColors.ButtonHighlight
        DataGridViewCellStyle1.Alignment = System.Windows.Forms.DataGridViewContentAlignment.MiddleCenter
        DataGridViewCellStyle1.BackColor = System.Drawing.SystemColors.GradientActiveCaption
        DataGridViewCellStyle1.Font = New System.Drawing.Font("Arial", 12.0!, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, CType(0, Byte))
        DataGridViewCellStyle1.ForeColor = System.Drawing.SystemColors.WindowText
        DataGridViewCellStyle1.SelectionBackColor = System.Drawing.SystemColors.ButtonShadow
        DataGridViewCellStyle1.SelectionForeColor = System.Drawing.SystemColors.HighlightText
        DataGridViewCellStyle1.WrapMode = System.Windows.Forms.DataGridViewTriState.[True]
        Me.dgvRech.ColumnHeadersDefaultCellStyle = DataGridViewCellStyle1
        Me.dgvRech.ColumnHeadersHeightSizeMode = System.Windows.Forms.DataGridViewColumnHeadersHeightSizeMode.AutoSize
        DataGridViewCellStyle2.Alignment = System.Windows.Forms.DataGridViewContentAlignment.MiddleLeft
        DataGridViewCellStyle2.BackColor = System.Drawing.SystemColors.ButtonHighlight
        DataGridViewCellStyle2.Font = New System.Drawing.Font("Arial", 12.0!, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, CType(0, Byte))
        DataGridViewCellStyle2.ForeColor = System.Drawing.SystemColors.ControlText
        DataGridViewCellStyle2.SelectionBackColor = System.Drawing.SystemColors.ButtonShadow
        DataGridViewCellStyle2.SelectionForeColor = System.Drawing.SystemColors.HighlightText
        DataGridViewCellStyle2.WrapMode = System.Windows.Forms.DataGridViewTriState.[False]
        Me.dgvRech.DefaultCellStyle = DataGridViewCellStyle2
        Me.dgvRech.EnableHeadersVisualStyles = False
        Me.dgvRech.Location = New System.Drawing.Point(10, 140)
        Me.dgvRech.MultiSelect = False
        Me.dgvRech.Name = "dgvRech"
        Me.dgvRech.ReadOnly = True
        Me.dgvRech.RowHeadersVisible = False
        Me.dgvRech.RowTemplate.Height = 25
        Me.dgvRech.Size = New System.Drawing.Size(836, 188)
        Me.dgvRech.TabIndex = 5
        '
        'btnRech
        '
        Me.btnRech.BackColor = System.Drawing.SystemColors.GradientActiveCaption
        Me.btnRech.Font = New System.Drawing.Font("Arial", 12.0!, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, CType(0, Byte))
        Me.btnRech.Location = New System.Drawing.Point(417, 11)
        Me.btnRech.Name = "btnRech"
        Me.btnRech.Size = New System.Drawing.Size(152, 32)
        Me.btnRech.TabIndex = 2
        Me.btnRech.Text = "Rechercher "
        Me.btnRech.UseVisualStyleBackColor = False
        '
        'btnOuvrir
        '
        Me.btnOuvrir.BackColor = System.Drawing.SystemColors.GradientActiveCaption
        Me.btnOuvrir.Enabled = False
        Me.btnOuvrir.Font = New System.Drawing.Font("Arial", 12.0!, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, CType(0, Byte))
        Me.btnOuvrir.Location = New System.Drawing.Point(417, 88)
        Me.btnOuvrir.Name = "btnOuvrir"
        Me.btnOuvrir.Size = New System.Drawing.Size(152, 32)
        Me.btnOuvrir.TabIndex = 3
        Me.btnOuvrir.Text = "Ouvrir"
        Me.btnOuvrir.UseVisualStyleBackColor = False
        '
        'cboCodeAvo
        '
        Me.cboCodeAvo.AutoCompleteMode = System.Windows.Forms.AutoCompleteMode.Suggest
        Me.cboCodeAvo.AutoCompleteSource = System.Windows.Forms.AutoCompleteSource.ListItems
        Me.cboCodeAvo.BackColor = System.Drawing.SystemColors.ButtonHighlight
        Me.cboCodeAvo.FlatStyle = System.Windows.Forms.FlatStyle.Popup
        Me.cboCodeAvo.Font = New System.Drawing.Font("Arial", 12.0!, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, CType(0, Byte))
        Me.cboCodeAvo.FormattingEnabled = True
        Me.cboCodeAvo.Location = New System.Drawing.Point(74, 46)
        Me.cboCodeAvo.MaxDropDownItems = 12
        Me.cboCodeAvo.MaxLength = 6
        Me.cboCodeAvo.Name = "cboCodeAvo"
        Me.cboCodeAvo.Size = New System.Drawing.Size(94, 26)
        Me.cboCodeAvo.TabIndex = 0
        '
        'cboNomAvo
        '
        Me.cboNomAvo.BackColor = System.Drawing.SystemColors.ButtonHighlight
        Me.cboNomAvo.FlatStyle = System.Windows.Forms.FlatStyle.Popup
        Me.cboNomAvo.Font = New System.Drawing.Font("Arial", 12.0!, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, CType(0, Byte))
        Me.cboNomAvo.FormattingEnabled = True
        Me.cboNomAvo.Location = New System.Drawing.Point(74, 79)
        Me.cboNomAvo.Name = "cboNomAvo"
        Me.cboNomAvo.Size = New System.Drawing.Size(284, 26)
        Me.cboNomAvo.TabIndex = 1
        '
        'btnCardex
        '
        Me.btnCardex.BackColor = System.Drawing.SystemColors.GradientActiveCaption
        Me.btnCardex.Font = New System.Drawing.Font("Arial", 12.0!, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, CType(0, Byte))
        Me.btnCardex.Location = New System.Drawing.Point(654, 27)
        Me.btnCardex.Name = "btnCardex"
        Me.btnCardex.Size = New System.Drawing.Size(152, 32)
        Me.btnCardex.TabIndex = 10
        Me.btnCardex.Text = "Vers Cardex"
        Me.btnCardex.UseVisualStyleBackColor = False
        '
        'btnFermer
        '
        Me.btnFermer.BackColor = System.Drawing.SystemColors.GradientActiveCaption
        Me.btnFermer.Font = New System.Drawing.Font("Arial", 12.0!, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, CType(0, Byte))
        Me.btnFermer.Location = New System.Drawing.Point(654, 68)
        Me.btnFermer.Name = "btnFermer"
        Me.btnFermer.Size = New System.Drawing.Size(152, 32)
        Me.btnFermer.TabIndex = 11
        Me.btnFermer.Text = "Fermer"
        Me.btnFermer.UseVisualStyleBackColor = False
        '
        'Chktous
        '
        Me.Chktous.AutoSize = True
        Me.Chktous.Location = New System.Drawing.Point(180, 48)
        Me.Chktous.Name = "Chktous"
        Me.Chktous.Size = New System.Drawing.Size(208, 22)
        Me.Chktous.TabIndex = 12
        Me.Chktous.Text = "Sans restriction d'adresse"
        Me.ToolTip1.SetToolTip(Me.Chktous, "Tous les avocats avec une adresse courante ou non et les avocats sans adresse")
        Me.Chktous.UseVisualStyleBackColor = True
        '
        'btnNouvRech
        '
        Me.btnNouvRech.BackColor = System.Drawing.SystemColors.GradientActiveCaption
        Me.btnNouvRech.Enabled = False
        Me.btnNouvRech.Font = New System.Drawing.Font("Arial", 12.0!, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, CType(0, Byte))
        Me.btnNouvRech.Location = New System.Drawing.Point(417, 50)
        Me.btnNouvRech.Name = "btnNouvRech"
        Me.btnNouvRech.Size = New System.Drawing.Size(152, 32)
        Me.btnNouvRech.TabIndex = 6
        Me.btnNouvRech.Text = "Nouvelle recherche"
        Me.btnNouvRech.UseVisualStyleBackColor = False
        '
        'frmRechAvo
        '
        Me.AcceptButton = Me.btnRech
        Me.AutoScaleDimensions = New System.Drawing.SizeF(96.0!, 96.0!)
        Me.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Dpi
        Me.BackColor = System.Drawing.SystemColors.GradientInactiveCaption
        Me.ClientSize = New System.Drawing.Size(856, 337)
        Me.Controls.Add(Me.Chktous)
        Me.Controls.Add(Me.btnFermer)
        Me.Controls.Add(Me.btnCardex)
        Me.Controls.Add(Me.cboNomAvo)
        Me.Controls.Add(Me.cboCodeAvo)
        Me.Controls.Add(Me.btnOuvrir)
        Me.Controls.Add(Me.btnNouvRech)
        Me.Controls.Add(Me.btnRech)
        Me.Controls.Add(Me.dgvRech)
        Me.Controls.Add(Me.Label3)
        Me.Controls.Add(Me.Label2)
        Me.Controls.Add(Me.Label1)
        Me.Font = New System.Drawing.Font("Arial", 12.0!, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, CType(0, Byte))
        Me.Icon = CType(resources.GetObject("$this.Icon"), System.Drawing.Icon)
        Me.Name = "frmRechAvo"
        Me.Text = "Recherche avocats/notaires"
        CType(Me.dgvRech, System.ComponentModel.ISupportInitialize).EndInit()
        Me.ResumeLayout(False)
        Me.PerformLayout()

    End Sub
    Friend WithEvents Label1 As System.Windows.Forms.Label
    Friend WithEvents Label2 As System.Windows.Forms.Label
    Friend WithEvents Label3 As System.Windows.Forms.Label
    Friend WithEvents dgvRech As System.Windows.Forms.DataGridView
    Friend WithEvents btnRech As System.Windows.Forms.Button
    Friend WithEvents btnOuvrir As System.Windows.Forms.Button
    Friend WithEvents cboCodeAvo As System.Windows.Forms.ComboBox
    Friend WithEvents cboNomAvo As System.Windows.Forms.ComboBox
    Friend WithEvents btnCardex As System.Windows.Forms.Button
    Friend WithEvents btnFermer As System.Windows.Forms.Button
    Friend WithEvents Chktous As System.Windows.Forms.CheckBox
    Friend WithEvents btnNouvRech As System.Windows.Forms.Button
    Friend WithEvents ToolTip1 As System.Windows.Forms.ToolTip
End Class
