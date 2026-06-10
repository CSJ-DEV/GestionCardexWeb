import { useEffect, useState } from "react";
import { Navigate } from "react-router-dom";
import { PenLine, Upload, Trash2, Save, Mail, RotateCcw } from "lucide-react";
import { toast } from "sonner";
import api, { formatApiError } from "@/lib/api";
import { useAuth } from "@/context/AuthContext";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

// Valeurs par défaut côté frontend (identiques à celles du backend, utilisées
// pour le bouton "Restaurer le modèle par défaut")
const DEFAULT_EMAIL_SUBJECT = "Réinitialisation de vos mots de passe — Aide juridique du Québec";
const DEFAULT_EMAIL_BODY = `Bonjour Me {nom},

Vos mots de passe Web de l'application GestionCardex ont été réinitialisés à votre demande.

Vous trouverez en pièce jointe (PDF) vos nouveaux identifiants (Mot de passe 1 et Mot de passe 2).

Pour des raisons de sécurité, conservez ce document en lieu sûr et ne le transférez pas par courriel.

Ceci est un message automatique — merci de ne pas y répondre.`;

export default function LetterConfig() {
    const { user } = useAuth();

    const [config, setConfig] = useState(null);
    const [nom, setNom] = useState("");
    const [titre, setTitre] = useState("");
    const [affiliation, setAffiliation] = useState("");
    const [emailSubject, setEmailSubject] = useState("");
    const [emailBody, setEmailBody] = useState("");
    const [signaturePreview, setSignaturePreview] = useState(null);
    const [newSignatureFile, setNewSignatureFile] = useState(null);
    const [clearFlag, setClearFlag] = useState(false);
    const [saving, setSaving] = useState(false);

    const load = async () => {
        try {
            const { data } = await api.get("/letter-config");
            setConfig(data);
            setNom(data.signataire_nom || "");
            setTitre(data.signataire_titre || "");
            setAffiliation(data.signataire_affiliation || "");
            setEmailSubject(data.email_subject || DEFAULT_EMAIL_SUBJECT);
            setEmailBody(data.email_body || DEFAULT_EMAIL_BODY);
            // Charge l'image courante via endpoint dédié (avec cookies)
            if (data.has_signature) {
                const imgRes = await api.get("/letter-config/signature-image", { responseType: "blob" });
                setSignaturePreview(URL.createObjectURL(imgRes.data));
            } else {
                setSignaturePreview(null);
            }
        } catch (err) {
            toast.error(formatApiError(err.response?.data?.detail) || "Erreur de chargement");
        }
    };

    useEffect(() => { load(); }, []);

    // TI seulement
    if (user && user.role !== "ti") return <Navigate to="/" replace />;

    const onFileChange = (e) => {
        const f = e.target.files?.[0];
        if (!f) return;
        if (!["image/png", "image/jpeg"].includes(f.type)) {
            toast.error("Format invalide : PNG ou JPEG uniquement");
            return;
        }
        if (f.size > 150 * 1024) {
            toast.error("Image trop volumineuse (max 150 KB)");
            return;
        }
        setNewSignatureFile(f);
        setClearFlag(false);
        const reader = new FileReader();
        reader.onload = (ev) => setSignaturePreview(ev.target.result);
        reader.readAsDataURL(f);
    };

    const onClearSignature = () => {
        setNewSignatureFile(null);
        setSignaturePreview(null);
        setClearFlag(true);
    };

    const fileToBase64NoPrefix = (file) =>
        new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.onload = () => {
                // result = "data:image/png;base64,XXXX" → on garde uniquement XXXX
                const s = reader.result;
                const comma = s.indexOf(",");
                resolve(comma >= 0 ? s.slice(comma + 1) : s);
            };
            reader.onerror = reject;
            reader.readAsDataURL(file);
        });

    const onSave = async () => {
        try {
            setSaving(true);
            const payload = {
                signataire_nom: nom.trim(),
                signataire_titre: titre.trim(),
                signataire_affiliation: affiliation.trim() || "Commission des services juridiques",
                clear_signature: clearFlag,
                email_subject: emailSubject.trim() || DEFAULT_EMAIL_SUBJECT,
                email_body: emailBody.trim() || DEFAULT_EMAIL_BODY,
            };
            if (newSignatureFile && !clearFlag) {
                payload.signature_image_base64 = await fileToBase64NoPrefix(newSignatureFile);
                payload.signature_mime = newSignatureFile.type;
            }
            await api.put("/letter-config", payload);
            toast.success("Configuration enregistrée");
            setNewSignatureFile(null);
            setClearFlag(false);
            await load();
        } catch (err) {
            toast.error(formatApiError(err.response?.data?.detail) || "Erreur d'enregistrement");
        } finally {
            setSaving(false);
        }
    };

    const previewExample = async () => {
        try {
            // Génère un PDF d'exemple en cherchant le premier avocat ayant des mdp
            const listRes = await api.get("/avocats?page=1&page_size=1");
            const first = listRes.data?.items?.[0];
            if (!first) {
                toast.error("Aucun avocat disponible pour générer un aperçu");
                return;
            }
            const res = await api.get(`/avocats/${first.code}/letter-preview`, { responseType: "blob" });
            const url = URL.createObjectURL(new Blob([res.data], { type: "application/pdf" }));
            window.open(url, "_blank", "noopener,noreferrer");
            setTimeout(() => URL.revokeObjectURL(url), 60000);
        } catch (err) {
            toast.error(formatApiError(err.response?.data?.detail) || "Erreur d'aperçu");
        }
    };

    return (
        <div className="space-y-6" data-testid="letter-config-page">
            <div>
                <div className="overline mb-2">Paramètres</div>
                <h1 className="font-display text-4xl font-bold tracking-tight text-slate-900">
                    Lettre — Signataire
                </h1>
                <p className="text-sm text-slate-600 mt-1">
                    Personnalisez le nom, le titre et la signature manuscrite imprimés au bas
                    de la lettre officielle « Code d'utilisateur et mots de passe ».
                </p>
            </div>

            <Card className="rounded-md border-slate-200">
                <CardHeader className="pb-3">
                    <CardTitle className="flex items-center gap-2 text-lg font-display">
                        <PenLine size={20} className="text-slate-600" />
                        Identité du signataire
                    </CardTitle>
                </CardHeader>
                <CardContent className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                        <Label htmlFor="nom" className="text-xs font-medium text-slate-700">Nom complet et titres</Label>
                        <Input
                            id="nom" value={nom} onChange={(e) => setNom(e.target.value)}
                            placeholder="M. Yves Boisvert, CPA, CGA"
                            className="rounded-md mt-1"
                            data-testid="letter-nom-input"
                        />
                    </div>
                    <div>
                        <Label htmlFor="titre" className="text-xs font-medium text-slate-700">Fonction</Label>
                        <Input
                            id="titre" value={titre} onChange={(e) => setTitre(e.target.value)}
                            placeholder="Directeur des services financiers"
                            className="rounded-md mt-1"
                            data-testid="letter-titre-input"
                        />
                    </div>
                    <div className="md:col-span-2">
                        <Label htmlFor="aff" className="text-xs font-medium text-slate-700">Affiliation</Label>
                        <Input
                            id="aff" value={affiliation} onChange={(e) => setAffiliation(e.target.value)}
                            placeholder="Commission des services juridiques"
                            className="rounded-md mt-1"
                            data-testid="letter-aff-input"
                        />
                    </div>
                </CardContent>
            </Card>

            <Card className="rounded-md border-slate-200">
                <CardHeader className="pb-3">
                    <CardTitle className="text-lg font-display">Signature manuscrite</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                    <p className="text-xs text-slate-600">
                        Téléversez une image PNG ou JPEG de la signature scannée (max 150 KB).
                        L'image sera positionnée au-dessus du nom imprimé dans la lettre.
                    </p>

                    {signaturePreview ? (
                        <div className="border border-slate-200 rounded-md p-4 bg-slate-50 inline-block">
                            <img
                                src={signaturePreview}
                                alt="Aperçu signature"
                                className="max-h-24 max-w-xs"
                                data-testid="signature-preview"
                            />
                        </div>
                    ) : (
                        <div className="border border-dashed border-slate-300 rounded-md p-6 text-center text-xs text-slate-500 bg-slate-50">
                            Aucune signature configurée — la lettre n'affichera que le nom imprimé.
                        </div>
                    )}

                    <div className="flex gap-3 flex-wrap">
                        <label className="cursor-pointer">
                            <input
                                type="file"
                                accept="image/png,image/jpeg"
                                onChange={onFileChange}
                                className="hidden"
                                data-testid="signature-file-input"
                            />
                            <span className="inline-flex items-center gap-2 px-3 py-2 text-sm rounded-md border border-slate-300 hover:bg-slate-50">
                                <Upload className="w-4 h-4" />
                                Téléverser une nouvelle signature
                            </span>
                        </label>
                        {config?.has_signature && !clearFlag && (
                            <Button
                                type="button" variant="outline"
                                onClick={onClearSignature}
                                className="rounded-md text-red-600 hover:text-red-700"
                                data-testid="signature-clear-btn"
                            >
                                <Trash2 className="w-4 h-4 mr-2" />
                                Retirer la signature
                            </Button>
                        )}
                    </div>
                </CardContent>
            </Card>

            <Card className="rounded-md border-slate-200">
                <CardHeader className="pb-3">
                    <CardTitle className="flex items-center gap-2 text-lg font-display">
                        <Mail size={20} className="text-slate-600" />
                        Modèle du courriel d&apos;envoi de la lettre
                    </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                    <p className="text-xs text-slate-600">
                        Personnalisez le sujet et le contenu du courriel envoyé automatiquement
                        aux avocats lors de la réinitialisation de leurs mots de passe ou de
                        l&apos;envoi de la lettre depuis l&apos;onglet Web.
                        <br />
                        <span className="text-slate-500">
                            Placeholders disponibles dans les 2 champs :
                            <code className="mx-1 px-1 bg-slate-100 rounded text-[10px]">{"{nom}"}</code>
                            <code className="mx-1 px-1 bg-slate-100 rounded text-[10px]">{"{prenom}"}</code>
                            <code className="mx-1 px-1 bg-slate-100 rounded text-[10px]">{"{code}"}</code>
                        </span>
                    </p>

                    <div>
                        <Label htmlFor="email-subject" className="text-xs font-medium text-slate-700">
                            Sujet
                        </Label>
                        <Input
                            id="email-subject"
                            value={emailSubject}
                            onChange={(e) => setEmailSubject(e.target.value)}
                            placeholder={DEFAULT_EMAIL_SUBJECT}
                            className="rounded-md mt-1"
                            data-testid="letter-email-subject-input"
                        />
                    </div>

                    <div>
                        <Label htmlFor="email-body" className="text-xs font-medium text-slate-700">
                            Contenu du courriel (texte simple — les retours à la ligne sont préservés)
                        </Label>
                        <Textarea
                            id="email-body"
                            value={emailBody}
                            onChange={(e) => setEmailBody(e.target.value)}
                            placeholder={DEFAULT_EMAIL_BODY}
                            className="rounded-md mt-1 font-mono text-sm leading-relaxed"
                            rows={10}
                            data-testid="letter-email-body-input"
                        />
                    </div>

                    <div className="flex justify-end">
                        <Button
                            type="button" variant="outline" size="sm"
                            onClick={() => {
                                setEmailSubject(DEFAULT_EMAIL_SUBJECT);
                                setEmailBody(DEFAULT_EMAIL_BODY);
                                toast.info("Modèle par défaut restauré (cliquez Enregistrer pour appliquer)");
                            }}
                            className="rounded-md text-xs"
                            data-testid="letter-email-reset-btn"
                        >
                            <RotateCcw className="w-3.5 h-3.5 mr-1.5" />
                            Restaurer le modèle par défaut
                        </Button>
                    </div>
                </CardContent>
            </Card>

            <div className="flex items-center justify-between gap-3 sticky bottom-0 bg-slate-50 -mx-6 md:-mx-8 px-6 md:px-8 py-4 border-t border-slate-200">
                <Button
                    type="button" variant="outline"
                    onClick={previewExample}
                    className="rounded-md"
                    data-testid="letter-preview-btn"
                >
                    Aperçu d'un exemple
                </Button>
                <Button
                    type="button"
                    onClick={onSave}
                    disabled={saving}
                    className="rounded-md bg-[#0033A0] hover:bg-[#002277] text-white"
                    data-testid="letter-save-btn"
                >
                    <Save className="w-4 h-4 mr-2" />
                    {saving ? "Enregistrement..." : "Enregistrer"}
                </Button>
            </div>

            {config?.updated_at && (
                <p className="text-xs text-slate-500">
                    Dernière modification : {new Date(config.updated_at).toLocaleString("fr-CA")}
                    {config.updated_by ? ` — ${config.updated_by}` : ""}
                </p>
            )}
        </div>
    );
}
