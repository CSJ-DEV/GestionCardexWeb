Module modVariables
    Public vstrConnCardAvo As String = "server= CSJ-Art52 ;uid= sa;pwd= a1de!;database= CardAvo; Pooling=true; Min Pool Size=0; Max Pool Size=100; Connection Lifetime=0"
    'Public vstrConnCardAvo As String = "server= CSJ-Themis ;uid= sa;pwd= a1de!;database= CardAvo; Pooling=true; Min Pool Size=0; Max Pool Size=100; Connection Lifetime=0"
    Public vstrStaticPc As String = "server= CSJ-Art52 ;uid= sa;pwd= a1de!;database= StaticPc; Pooling=true; Min Pool Size=0; Max Pool Size=100; Connection Lifetime=0"
    'Public vstrStaticPc As String = "server= CSJ-Themis ;uid= sa;pwd= a1de!;database= StaticPc; Pooling=true; Min Pool Size=0; Max Pool Size=100; Connection Lifetime=0"
    Public vstrArt52 As String = "server= CSJ-Art52 ;uid= sa;pwd= a1de!;database= Art52; Pooling=true; Min Pool Size=0; Max Pool Size=100; Connection Lifetime=0"
    'Public vstrArt52 As String = "server= CSJ-Themis ;uid= sa;pwd= a1de!;database= Art52; Pooling=true; Min Pool Size=0; Max Pool Size=100; Connection Lifetime=0"
    Public vstrFVI As String = "server= CSJ-WEB01 ;uid= sa;pwd= a1de!;database= Fvi; Pooling=true; Min Pool Size=0; Max Pool Size=100; Connection Lifetime=0"
    Public strConnArt52 As String = vstrArt52 ' My.Settings.ConnArt52.ToString
    Public strConnStatic As String = vstrStaticPc ' My.Settings.ConnStaticPC.ToString
    Public strConnCardAvo As String = vstrConnCardAvo ' My.Settings.ConnCardAvo.ToString
    Public strConnFVI As String = vstrFVI 'My.Settings.ConnFVI.ToString

    'Public vstrConnArt52 As String = "server= CSJ-Themis ;uid= sa;pwd= a1de!;database= Art52; Pooling=true; Min Pool Size=0; Max Pool Size=100; Connection Lifetime=0"


    Public vgServer As String = "CSJ-Art52"
    Public vgBD As String = "CardAvo"

    Public vgUser As String = Nothing
    Public vgGrUtil As String = Nothing
    Public vgStrLogin As String = Nothing
    Public vgPermission As String = Nothing
    Public vgStrTitreMsgBoxErreur As String = "Application CardAvo: Erreur"
    Public vgStrTitreMsgValiderChamps As String = "Application CardAvo: Valider champs obligatoires"

    Public gAnyChg As Integer
    Public gCodeAvo As String
    Public gEmail As String
    Public gEmailServer As String
    Public gEmailPort As Integer
    Public gPathCompt As String
    Public gPathInfo As String
    Public gPathPJ As String
    Public gPathRap As String
    Public gPathWeb As String
    Public gReadOnly As Integer

    Public Const DOSSIER_LOAD = 0
    Public Const DOSSIER_NOUVEAU = 1
    Public Const DOSSIER_MODIF = 2
    Public Const LECTURE = 0
    Public Const MEGA = 1
    Public Const GEST = 2

    Public gAnyChgAdr As Integer
    Public gAnyChgInh As Integer
    Public gAnyChgWeb As Integer
    Public gAnyChgMega As Integer
    Public gAvoStatus As Integer
    'Public gAvocDocID As Long
    Public gAvoAdrStatus As Integer
    Public gAvoInhStatus As Integer
    Public gAvoWebStatus As Integer
    Public gAvoMegaStatus As Integer
    'Public gDepot As String
    Public gEditAdrAvo As Integer
    Public gEditInhAvo As Integer
    Public gMega As Boolean
    'Public gMotPasse As Boolean
    Public gMotPasse1 As String
    Public gMotPasse2 As String
    'Public gPayable As String
    'Public gTablWebAvoc(5) As String
    'Public gTablMegaAvoc(14) As String
    'Public gTablDistAvo() As String
    'Public gTablDistrict() As String
    'Public gVerifDepo As Boolean
    'Public gVerifPay As Boolean
    'Public gVerifTablMega As Boolean
    Public gWeb As Boolean

End Module
