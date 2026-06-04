import { useEffect, useState } from "react";
import api, { formatApiError } from "@/lib/api";
import { useAuth } from "@/context/AuthContext";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Switch } from "@/components/ui/switch";
import { Separator } from "@/components/ui/separator";
import {
    Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription, DialogFooter,
} from "@/components/ui/dialog";
import { toast } from "sonner";
import { Eye, EyeOff, RefreshCw, Copy, Trash2, Mail, FileText } from "lucide-react";
import { Field } from "./constants";

// --- Sous-composant : un champ mot de passe (motpasse1 ou motpasse2) ---
const PasswordRow = ({ label, isSet, value, visible, isTI, onToggle, onCopy }) => (
    <div className="flex items-center gap-2">
        <Label className="text-xs font-medium text-slate-700 w-24">{label}</Label>
        <Input
            value={visible && value ? value : (isSet ? "••••••" : "—")}
            disabled
            readOnly
            className="rounded-md font-mono flex-1 bg-slate-50"
            data-testid={`web-${label.toLowerCase().replace(/[^a-z0-9]/g, "")}-value`}
        />
        {isTI && isSet && (
            <Button
                type="button"
                size="icon"
                variant="outline"
                onClick={onToggle}
                title={visible ? "Masquer" : "Révéler (TI)"}
                className="rounded-md"
                data-testid={`web-${label.toLowerCase().replace(/[^a-z0-9]/g, "")}-eye`}
            >
                {visible ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
            </Button>
        )}
        {visible && value && (
            <Button
                type="button"
                size="icon"
                variant="outline"
                onClick={onCopy}
                title="Copier"
                className="rounded-md"
                data-testid={`web-${label.toLowerCase().replace(/[^a-z0-9]/g, "")}-copy`}
            >
                <Copy className="w-4 h-4" />
            </Button>
        )}
    </div>
);

export const WebTab = ({ readOnly, form, upd, avocatId, avocat, onSaved }) => {
    const { user } = useAuth();
    const isTI = user?.role === "ti";
    // TI est super-utilisateur technique (peut tout faire en plus de révéler les mdp).
    // Cohérent avec require_role() côté backend qui ajoute auto 'ti' à 'admin'.
    const canReset = !readOnly && (user?.role === "admin" || user?.role === "editeur" || isTI);

    const [reveal1, setReveal1] = useState(false);
    const [reveal2, setReveal2] = useState(false);
    const [pwd1, setPwd1] = useState(""); // clear values fetched from TI endpoint
    const [pwd2, setPwd2] = useState("");
    const [busy, setBusy] = useState(false);

    // Dialog d'envoi par courriel
    const [emailEnabled, setEmailEnabled] = useState(false);
    const [resetDialogOpen, setResetDialogOpen] = useState(false);
    const [sendByEmail, setSendByEmail] = useState(true);
    const defaultEmail = (avocat?.adresse?.email || "").trim();
    const [emailTarget, setEmailTarget] = useState(defaultEmail);

    // Vérifie si le service ACS est configuré côté serveur
    useEffect(() => {
        api.get("/system/email-status")
            .then((res) => setEmailEnabled(Boolean(res.data?.enabled)))
            .catch(() => setEmailEnabled(false));
    }, []);

    const openResetDialog = () => {
        setEmailTarget(defaultEmail);
        setSendByEmail(emailEnabled && Boolean(defaultEmail));
        setResetDialogOpen(true);
    };

    // ---- Aperçu de la lettre officielle (PDF dans un nouvel onglet) ----
    const previewLetter = async () => {
        try {
            // On utilise axios pour traverser le proxy avec les cookies, puis
            // on ouvre le PDF dans un nouvel onglet via un Blob URL.
            const response = await api.get(`/avocats/${avocatId}/letter-preview`, {
                responseType: "blob",
            });
            const url = URL.createObjectURL(new Blob([response.data], { type: "application/pdf" }));
            window.open(url, "_blank", "noopener,noreferrer");
            // Libère le blob après 60s
            setTimeout(() => URL.revokeObjectURL(url), 60000);
        } catch (err) {
            console.error("letter-preview erreur:", err);
            const status = err.response?.status;
            toast.error(status
                ? `Erreur HTTP ${status} lors de la génération de la lettre`
                : `Erreur réseau : ${err.message}`);
        }
    };

    const motpasse1Set = !!avocat?.motpasse1_set;
    const motpasse2Set = !!avocat?.motpasse2_set;

    const copyToClipboard = async (text, label) => {
        try {
            await navigator.clipboard.writeText(text);
            toast.success(`${label} copié`);
        } catch {
            toast.error("Copie impossible");
        }
    };

    const fetchPasswordsTI = async (which) => {
        try {
            const { data } = await api.get(`/avocats/${avocatId}/passwords`);
            setPwd1(data.motpasse1 || "");
            setPwd2(data.motpasse2 || "");
            if (which === 1) setReveal1(true);
            else setReveal2(true);
        } catch (err) {
            toast.error(formatApiError(err.response?.data?.detail) || "Erreur");
        }
    };

    const toggleReveal = async (which) => {
        if (which === 1) {
            if (reveal1) { setReveal1(false); return; }
            if (!pwd1) await fetchPasswordsTI(1); else setReveal1(true);
        } else {
            if (reveal2) { setReveal2(false); return; }
            if (!pwd2) await fetchPasswordsTI(2); else setReveal2(true);
        }
    };

    const resetPasswords = async () => {
        setResetDialogOpen(false);
        try {
            setBusy(true);
            const payload = sendByEmail && emailTarget
                ? { send_email: true, email: emailTarget.trim() }
                : {};
            const { data } = await api.post(`/avocats/${avocatId}/reset-passwords`, payload);
            let successMsg = `Mots de passe générés — MdP 1 : ${data.motpasse1} · MdP 2 : ${data.motpasse2}`;
            if (data.email_sent_to) {
                successMsg += `\n📧 Courriel envoyé à ${data.email_sent_to}`;
            } else if (data.email_error) {
                toast.warning(`Mots de passe générés mais courriel non envoyé : ${data.email_error}`);
            }
            toast.success(successMsg, {
                duration: 20000,
                action: { label: "Copier les deux", onClick: () => copyToClipboard(`${data.motpasse1} / ${data.motpasse2}`, "Mots de passe") },
            });
            // Si TI : pré-charge les valeurs pour révélation immédiate
            if (isTI) { setPwd1(data.motpasse1); setPwd2(data.motpasse2); }
            onSaved?.();
        } catch (err) {
            // Log détaillé pour le débuggage (visible en console F12)
            console.error("reset-passwords erreur:", {
                status: err.response?.status,
                data: err.response?.data,
                message: err.message,
                url: err.config?.url,
            });
            const status = err.response?.status;
            const detail = err.response?.data?.detail;
            const debug = err.response?.data?.debug;
            let msg;
            if (detail) {
                msg = formatApiError(detail);
            } else if (status) {
                msg = `Erreur HTTP ${status}${err.response?.statusText ? ` — ${err.response.statusText}` : ""}`;
            } else {
                msg = `Erreur réseau : ${err.message || "Connexion impossible"}`;
            }
            // Pour les TI : afficher le détail technique de l'exception
            if (isTI && debug) {
                msg += `\n\n[TI] ${debug.exception_type}: ${debug.exception_message}`;
                if (Array.isArray(debug.traceback_tail) && debug.traceback_tail.length > 0) {
                    msg += `\n${debug.traceback_tail[debug.traceback_tail.length - 1]}`;
                }
            }
            toast.error(msg, { duration: isTI ? 30000 : 6000 });
        } finally {
            setBusy(false);
        }
    };

    const clearPasswords = async () => {
        if (!confirm("Effacer les mots de passe Web de l'avocat ?")) return;
        try {
            setBusy(true);
            await api.post(`/avocats/${avocatId}/clear-passwords`);
            setPwd1(""); setPwd2(""); setReveal1(false); setReveal2(false);
            toast.success("Mots de passe effacés");
            onSaved?.();
        } catch (err) {
            toast.error(formatApiError(err.response?.data?.detail) || "Erreur");
        } finally {
            setBusy(false);
        }
    };

    return (
        <div className="space-y-5">
            <div className="text-sm text-slate-600">
                Accès web de l'avocat (portail extranet) — équivalent du formulaire <code className="font-mono text-xs bg-slate-100 px-1 rounded">frmAvocat</code> du VB.
            </div>
            <Separator />

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <Field label="Code usager (auto = code avocat)">
                    <Input
                        value={form.codeusager || ""}
                        disabled
                        readOnly
                        placeholder={form.factweb ? "—" : "— activez Facturation web —"}
                        className="rounded-md font-mono bg-slate-50"
                        data-testid="web-codeusager"
                    />
                </Field>
                <Field label="Ville référence">
                    <Input
                        value={form.villerref || ""}
                        onChange={(e) => upd("villerref", e.target.value)}
                        disabled={readOnly}
                        className="rounded-md"
                        data-testid="web-villerref"
                    />
                </Field>
            </div>

            <Separator />
            <div>
                <div className="overline mb-3">Options Web</div>
                <div className="grid grid-cols-2 gap-3">
                    <div className="flex items-center justify-between border border-slate-200 rounded-md px-3 py-2">
                        <Label className="text-sm">Facturation web</Label>
                        <Switch checked={!!form.factweb} onCheckedChange={(v) => upd("factweb", v)} disabled={readOnly} data-testid="web-factweb" />
                    </div>
                    <div className="flex items-center justify-between border border-slate-200 rounded-md px-3 py-2">
                        <Label className="text-sm">Confirmation web</Label>
                        <Switch checked={!!form.confweb} onCheckedChange={(v) => upd("confweb", v)} disabled={readOnly} data-testid="web-confweb" />
                    </div>
                </div>
            </div>

            <Separator />
            <div className="space-y-3">
                <div className="overline">Mots de passe Web (legacy)</div>
                <p className="text-xs text-slate-500">
                    Deux mots de passe numériques (5–6 chiffres) générés automatiquement, équivalent du
                    <code className="font-mono text-xs bg-slate-100 px-1 mx-1 rounded">subCreerPwd()</code> VB.
                    Stockés dans <code className="font-mono text-xs bg-slate-100 px-1 rounded">Avocats.motpasse1</code> / <code className="font-mono text-xs bg-slate-100 px-1 rounded">motpasse2</code>.
                </p>

                <div className="space-y-2 max-w-xl">
                    <PasswordRow
                        label="MdP 1"
                        isSet={motpasse1Set}
                        value={pwd1}
                        visible={reveal1}
                        isTI={isTI}
                        onToggle={() => toggleReveal(1)}
                        onCopy={() => copyToClipboard(pwd1, "MdP 1")}
                    />
                    <PasswordRow
                        label="MdP 2"
                        isSet={motpasse2Set}
                        value={pwd2}
                        visible={reveal2}
                        isTI={isTI}
                        onToggle={() => toggleReveal(2)}
                        onCopy={() => copyToClipboard(pwd2, "MdP 2")}
                    />
                </div>

                {canReset && (
                    <div className="flex gap-2 pt-2 flex-wrap">
                        <Button
                            type="button"
                            onClick={openResetDialog}
                            disabled={busy || !form.factweb}
                            className="rounded-md bg-[#0033A0] hover:bg-[#002277] text-white"
                            data-testid="web-reset-passwords"
                        >
                            <RefreshCw className="w-4 h-4 mr-2" />
                            {motpasse1Set || motpasse2Set ? "Réinitialiser les mots de passe" : "Générer les mots de passe"}
                        </Button>
                        {(motpasse1Set || motpasse2Set) && (
                            <>
                                <Button
                                    type="button"
                                    variant="outline"
                                    onClick={previewLetter}
                                    disabled={busy}
                                    className="rounded-md"
                                    data-testid="web-preview-letter"
                                    title="Ouvre la lettre officielle (PDF) dans un nouvel onglet"
                                >
                                    <FileText className="w-4 h-4 mr-2" />
                                    Aperçu de la lettre
                                </Button>
                                <Button
                                    type="button"
                                    variant="outline"
                                    onClick={clearPasswords}
                                    disabled={busy}
                                    className="rounded-md"
                                    data-testid="web-clear-passwords"
                                >
                                    <Trash2 className="w-4 h-4 mr-2" />
                                    Effacer
                                </Button>
                            </>
                        )}
                    </div>
                )}
                {!form.factweb && (
                    <p className="text-xs text-amber-700">
                        ⚠ Activez « Facturation web » et enregistrez avant de générer des mots de passe.
                    </p>
                )}
            </div>

            {/* Dialog de confirmation de réinitialisation + envoi courriel */}
            <Dialog open={resetDialogOpen} onOpenChange={setResetDialogOpen}>
                <DialogContent className="sm:max-w-md" data-testid="reset-pwd-dialog">
                    <DialogHeader>
                        <DialogTitle>Réinitialiser les mots de passe</DialogTitle>
                        <DialogDescription>
                            Deux nouveaux mots de passe seront générés et remplaceront les
                            mots de passe actuels. Cette action est irréversible.
                        </DialogDescription>
                    </DialogHeader>

                    {emailEnabled ? (
                        <div className="space-y-4 py-2">
                            <div className="flex items-start gap-3 rounded-md bg-slate-50 border border-slate-200 p-3">
                                <Mail className="w-5 h-5 text-[#0033A0] mt-0.5 shrink-0" />
                                <div className="flex-1">
                                    <div className="flex items-center justify-between gap-2">
                                        <Label htmlFor="send-by-email" className="text-sm font-medium text-slate-900">
                                            Envoyer par courriel à l'avocat
                                        </Label>
                                        <Switch
                                            id="send-by-email"
                                            checked={sendByEmail}
                                            onCheckedChange={setSendByEmail}
                                            data-testid="reset-pwd-send-email-toggle"
                                        />
                                    </div>
                                    {sendByEmail && (
                                        <div className="mt-3">
                                            <Label htmlFor="email-target" className="text-xs text-slate-600">
                                                Adresse de destination
                                            </Label>
                                            <Input
                                                id="email-target"
                                                type="email"
                                                value={emailTarget}
                                                onChange={(e) => setEmailTarget(e.target.value)}
                                                placeholder="avocat@exemple.qc.ca"
                                                className="mt-1 rounded-md"
                                                data-testid="reset-pwd-email-input"
                                            />
                                            {!defaultEmail && (
                                                <p className="text-xs text-amber-700 mt-1">
                                                    ⚠ Aucune adresse courriel n'est enregistrée pour cet avocat — saisissez-la manuellement.
                                                </p>
                                            )}
                                            <p className="text-xs text-slate-500 mt-2">
                                                Un PDF avec les nouveaux mots de passe sera joint au courriel.
                                            </p>
                                        </div>
                                    )}
                                </div>
                            </div>
                        </div>
                    ) : (
                        <p className="text-xs text-slate-500 py-2">
                            Le service courriel n'est pas configuré sur ce serveur. Les mots de passe
                            seront affichés à l'écran après génération (à copier manuellement).
                        </p>
                    )}

                    <DialogFooter className="gap-2">
                        <Button
                            type="button"
                            variant="outline"
                            onClick={() => setResetDialogOpen(false)}
                            className="rounded-md"
                            data-testid="reset-pwd-cancel"
                        >
                            Annuler
                        </Button>
                        <Button
                            type="button"
                            onClick={resetPasswords}
                            disabled={busy || (sendByEmail && emailEnabled && !emailTarget.trim())}
                            className="rounded-md bg-[#0033A0] hover:bg-[#002277] text-white"
                            data-testid="reset-pwd-confirm"
                        >
                            {sendByEmail && emailEnabled ? "Réinitialiser et envoyer" : "Réinitialiser"}
                        </Button>
                    </DialogFooter>
                </DialogContent>
            </Dialog>
        </div>
    );
};
