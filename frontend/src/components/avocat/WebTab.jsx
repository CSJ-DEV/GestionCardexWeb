import { useState } from "react";
import api, { formatApiError } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Switch } from "@/components/ui/switch";
import { Separator } from "@/components/ui/separator";
import { toast } from "sonner";
import { Field } from "./constants";

export const WebTab = ({ readOnly, form, upd, avocatId, onSubmit }) => {
    const [errCodeUsager, setErrCodeUsager] = useState(null);

    const trimmedCodeUsager = (form.codeusager || "").trim();
    const codeUsagerInvalid = trimmedCodeUsager.length === 0;

    const setPassword = async () => {
        if (codeUsagerInvalid) {
            setErrCodeUsager("Vous devez d'abord définir un code usager");
            toast.error("Code usager requis avant de définir un mot de passe");
            return;
        }
        if (!form._webpwd || form._webpwd.length < 6) {
            toast.error("Min 6 caractères");
            return;
        }
        try {
            await api.put(`/avocats/${avocatId}/web-password`, { password: form._webpwd });
            upd("_webpwd", "");
            toast.success("Mot de passe web enregistré");
        } catch (err) {
            toast.error(formatApiError(err.response?.data?.detail) || "Erreur");
        }
    };
    const clearPassword = async () => {
        if (!confirm("Réinitialiser le mot de passe web ?")) return;
        try {
            await api.delete(`/avocats/${avocatId}/web-password`);
            toast.success("Mot de passe réinitialisé");
        } catch (err) {
            toast.error(formatApiError(err.response?.data?.detail) || "Erreur");
        }
    };

    const handleSaveWebTab = (e) => {
        if (codeUsagerInvalid) {
            e?.preventDefault?.();
            setErrCodeUsager("Le code usager est obligatoire pour enregistrer cet onglet");
            toast.error("Veuillez saisir un code usager avant d'enregistrer");
            return;
        }
        setErrCodeUsager(null);
        onSubmit?.(e);
    };

    return (
        <div className="space-y-5">
            <div className="text-sm text-slate-600">
                Accès web de l'avocat (portail extranet) — équivalent du formulaire <code className="font-mono text-xs bg-slate-100 px-1 rounded">frmMotPasse</code> du VB.
            </div>
            <Separator />
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <Field label="Code usager *">
                    <Input
                        value={form.codeusager || ""}
                        onChange={(e) => { upd("codeusager", e.target.value); if (e.target.value.trim()) setErrCodeUsager(null); }}
                        disabled={readOnly}
                        placeholder="Obligatoire"
                        className={`rounded-md font-mono ${errCodeUsager ? "border-red-500" : ""}`}
                        data-testid="web-codeusager"
                    />
                    {errCodeUsager && (
                        <p className="text-xs text-red-600 mt-1" data-testid="err-codeusager">{errCodeUsager}</p>
                    )}
                </Field>
                <Field label="Ville référence">
                    <Input value={form.villerref || ""} onChange={(e) => upd("villerref", e.target.value)} disabled={readOnly} className="rounded-md" data-testid="web-villerref" />
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
            <div>
                <div className="overline mb-3">Mot de passe Web</div>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3 items-end">
                    <Field label="Nouveau mot de passe (min 6 car.)">
                        <Input
                            type="password"
                            value={form._webpwd || ""}
                            onChange={(e) => upd("_webpwd", e.target.value)}
                            disabled={readOnly || codeUsagerInvalid}
                            minLength={6}
                            placeholder={codeUsagerInvalid ? "— code usager requis —" : ""}
                            className="rounded-md"
                            data-testid="web-password"
                        />
                    </Field>
                    {!readOnly && (
                        <div className="flex gap-2">
                            <Button
                                onClick={setPassword}
                                disabled={codeUsagerInvalid}
                                className="bg-[#0033A0] hover:bg-[#002277] text-white rounded-md"
                                data-testid="save-web-password"
                            >
                                Définir
                            </Button>
                            <Button variant="outline" onClick={clearPassword} className="rounded-md" data-testid="clear-web-password">
                                Effacer
                            </Button>
                        </div>
                    )}
                </div>
                <p className="text-xs text-slate-500 mt-2">
                    Le mot de passe est stocké hashé (bcrypt) et n'est jamais affiché.
                    {codeUsagerInvalid && <> Le mot de passe ne peut pas être défini sans code usager.</>}
                </p>
            </div>
            {!readOnly && (
                <div className="flex justify-end pt-2 border-t border-slate-200">
                    <Button onClick={handleSaveWebTab} className="bg-[#0033A0] hover:bg-[#002277] text-white rounded-md" data-testid="save-web-tab">
                        Enregistrer code usager + options
                    </Button>
                </div>
            )}
        </div>
    );
};
