import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Switch } from "@/components/ui/switch";
import { Badge } from "@/components/ui/badge";
import {
    AlertDialog, AlertDialogAction, AlertDialogCancel, AlertDialogContent,
    AlertDialogDescription, AlertDialogFooter, AlertDialogHeader, AlertDialogTitle,
} from "@/components/ui/alert-dialog";
import { Plus, Pencil, Trash2, Star } from "lucide-react";
import { toast } from "sonner";
import { Field, EMPTY_ADRESSE } from "./constants";
import {
    formatCodePostal, isValidCodePostal,
    formatTelephone, isValidTelephone,
    isValidEmail,
} from "./formatters";

const FieldError = ({ children, testId }) => (
    <p className="text-xs text-red-600 mt-1" data-testid={testId}>{children}</p>
);

export const AdressesTab = ({ readOnly, adresses, editAdr, setEditAdr, onSave, onDelete }) => {
    const [errors, setErrors] = useState({});
    // Dialog confirmant le changement d'adresse courante (l'ancienne sera rétrogradée)
    const [confirm, setConfirm] = useState(null); // { type: "replace" | "promote", existing? }

    const setField = (key, value) => setEditAdr({ ...editAdr, [key]: value });
    const clearError = (key) => setErrors((e) => ({ ...e, [key]: null }));

    const validateAll = () => {
        const next = {};
        if (!(editAdr?.address || "").trim()) next.address = "L'adresse est obligatoire";
        if (!(editAdr?.ville || "").trim()) next.ville = "La ville est obligatoire";
        if (!isValidCodePostal(editAdr?.codepostal)) next.codepostal = "Format requis : A1A 1A1";
        if (!isValidTelephone(editAdr?.telephone)) next.telephone = "Format requis : 514-555-1234 (10 chiffres)";
        if (!isValidTelephone(editAdr?.telephone2)) next.telephone2 = "Format requis : 514-555-1234 (10 chiffres)";
        if (!isValidTelephone(editAdr?.fax)) next.fax = "Format requis : 514-555-1234 (10 chiffres)";
        if (!(editAdr?.email || "").trim()) next.email = "Le courriel est obligatoire";
        else if (!isValidEmail(editAdr?.email)) next.email = "Adresse courriel invalide";
        setErrors(next);
        return Object.keys(next).length === 0;
    };

    const handleSave = () => {
        if (!validateAll()) {
            toast.error("Veuillez corriger les champs invalides");
            return;
        }
        // Repère une éventuelle adresse courante existante (autre que celle en cours d'édition)
        const existingCourante = adresses.find((a) => a.courant && a.id !== editAdr?.id);

        // Cas 1 : utilisateur veut marquer cette adresse comme courante alors qu'une autre l'est déjà
        if (editAdr?.courant && existingCourante) {
            setConfirm({ type: "replace", existing: existingCourante });
            return;
        }
        // Cas 2 : aucune adresse courante n'est définie (ni ailleurs, ni sur cette adresse)
        //         → on suggère de marquer celle-ci comme courante (workflow legacy VB)
        if (!editAdr?.courant && !existingCourante) {
            setConfirm({ type: "promote" });
            return;
        }
        // Cas 3 : switch OFF + une autre adresse est déjà courante
        //         → on demande quand même si l'utilisateur veut basculer la courante sur celle-ci
        if (!editAdr?.courant && existingCourante) {
            setConfirm({ type: "switch", existing: existingCourante });
            return;
        }
        // Sinon : pas de conflit → save direct
        onSave();
    };

    // Confirmé "Oui" :
    //  - promote / switch : on définit cette adresse comme courante (l'autre sera rétrogradée par le backend)
    //  - replace          : save tel quel (le switch est déjà ON)
    // On passe l'override directement à onSave pour éviter les problèmes de re-render React.
    const confirmYes = () => {
        if (confirm?.type === "promote" || confirm?.type === "switch") {
            const next = { ...editAdr, courant: true };
            setEditAdr(next);
            onSave(next);
        } else {
            onSave(editAdr);
        }
        setConfirm(null);
    };

    // Confirmé "Non" :
    //  - replace : on désactive le switch (l'autre reste courante) puis save
    //  - promote / switch : save sans courante
    const confirmNo = () => {
        if (confirm?.type === "replace") {
            const next = { ...editAdr, courant: false };
            setEditAdr(next);
            onSave(next);
        } else {
            onSave(editAdr);
        }
        setConfirm(null);
    };

    return (
        <div className="space-y-4">
            {!readOnly && (
                <Button
                    onClick={() => { setEditAdr({ ...EMPTY_ADRESSE, courant: adresses.length === 0 }); setErrors({}); }}
                    className="rounded-md bg-[#0033A0] hover:bg-[#002277] text-white"
                    data-testid="add-adresse-btn"
                >
                    <Plus size={14} className="mr-2" /> Nouvelle adresse
                </Button>
            )}

            <div className="space-y-2">
                {adresses.length === 0 ? (
                    <div className="text-sm text-slate-500 text-center py-8 border border-dashed border-slate-300 rounded-md">
                        Aucune adresse. Cliquez sur « Nouvelle adresse ».
                    </div>
                ) : (
                    adresses.map((adr) => (
                        <div key={adr.id} className="border border-slate-200 rounded-md p-3 flex items-start justify-between hover:border-slate-300" data-testid={`adresse-row-${adr.id}`}>
                            <div className="flex-1">
                                <div className="flex items-center gap-2 mb-1">
                                    {adr.courant && <Badge className="bg-amber-100 text-amber-800 hover:bg-amber-100"><Star size={10} className="mr-1" />Courante</Badge>}
                                    <span className="font-medium text-slate-900">{adr.address || "—"}</span>
                                </div>
                                <div className="text-xs text-slate-600">
                                    {[adr.ville, adr.province, adr.codepostal].filter(Boolean).join(", ")}
                                    {adr.telephone && ` • ${adr.telephone}`}
                                    {adr.email && ` • ${adr.email}`}
                                </div>
                            </div>
                            {!readOnly && (
                                <div className="flex gap-1">
                                    <Button variant="ghost" size="icon" onClick={() => { setEditAdr(adr); setErrors({}); }}><Pencil size={14} /></Button>
                                    <Button variant="ghost" size="icon" className="text-red-600" onClick={() => onDelete(adr)}><Trash2 size={14} /></Button>
                                </div>
                            )}
                        </div>
                    ))
                )}
            </div>

            {editAdr && (
                <div className="border-2 border-[#0033A0] rounded-md p-4 space-y-3 bg-blue-50/30">
                    <div className="font-semibold text-sm">{editAdr.id ? "Modifier l'adresse" : "Nouvelle adresse"}</div>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                        <Field label="Adresse" required>
                            <Input
                                value={editAdr.address || ""}
                                onChange={(e) => { setField("address", e.target.value); clearError("address"); }}
                                className={`rounded-md ${errors.address ? "border-red-500" : ""}`}
                                data-testid="adr-address"
                            />
                            {errors.address && <FieldError testId="err-address">{errors.address}</FieldError>}
                        </Field>
                        <Field label="Ville" required>
                            <Input
                                value={editAdr.ville || ""}
                                onChange={(e) => { setField("ville", e.target.value); clearError("ville"); }}
                                className={`rounded-md ${errors.ville ? "border-red-500" : ""}`}
                                data-testid="adr-ville"
                            />
                            {errors.ville && <FieldError testId="err-ville">{errors.ville}</FieldError>}
                        </Field>
                        <Field label="Province">
                            <Input value={editAdr.province || ""} onChange={(e) => setField("province", e.target.value.toUpperCase().slice(0, 2))} maxLength={2} className="rounded-md font-mono" />
                        </Field>
                        <Field label="Code postal (A1A 1A1)">
                            <Input
                                value={editAdr.codepostal || ""}
                                onChange={(e) => { setField("codepostal", formatCodePostal(e.target.value)); clearError("codepostal"); }}
                                maxLength={7}
                                placeholder="A1A 1A1"
                                className={`rounded-md font-mono uppercase ${errors.codepostal ? "border-red-500" : ""}`}
                                data-testid="adr-codepostal"
                            />
                            {errors.codepostal && <FieldError testId="err-codepostal">{errors.codepostal}</FieldError>}
                        </Field>
                        <Field label="Téléphone">
                            <Input
                                value={editAdr.telephone || ""}
                                onChange={(e) => { setField("telephone", formatTelephone(e.target.value)); clearError("telephone"); }}
                                inputMode="numeric"
                                placeholder="514-555-1234"
                                maxLength={12}
                                className={`rounded-md font-mono ${errors.telephone ? "border-red-500" : ""}`}
                                data-testid="adr-telephone"
                            />
                            {errors.telephone && <FieldError testId="err-telephone">{errors.telephone}</FieldError>}
                        </Field>
                        <Field label="Téléphone 2">
                            <Input
                                value={editAdr.telephone2 || ""}
                                onChange={(e) => { setField("telephone2", formatTelephone(e.target.value)); clearError("telephone2"); }}
                                inputMode="numeric"
                                placeholder="514-555-1234"
                                maxLength={12}
                                className={`rounded-md font-mono ${errors.telephone2 ? "border-red-500" : ""}`}
                            />
                            {errors.telephone2 && <FieldError>{errors.telephone2}</FieldError>}
                        </Field>
                        <Field label="Télécopieur">
                            <Input
                                value={editAdr.fax || ""}
                                onChange={(e) => { setField("fax", formatTelephone(e.target.value)); clearError("fax"); }}
                                inputMode="numeric"
                                placeholder="514-555-1234"
                                maxLength={12}
                                className={`rounded-md font-mono ${errors.fax ? "border-red-500" : ""}`}
                            />
                            {errors.fax && <FieldError>{errors.fax}</FieldError>}
                        </Field>
                        <Field label="Courriel" required>
                            <Input
                                type="email"
                                value={editAdr.email || ""}
                                onChange={(e) => { setField("email", e.target.value); clearError("email"); }}
                                placeholder="exemple@domaine.com"
                                className={`rounded-md ${errors.email ? "border-red-500" : ""}`}
                                data-testid="adr-email"
                            />
                            {errors.email && <FieldError testId="err-email">{errors.email}</FieldError>}
                        </Field>
                    </div>
                    <div className="flex items-center justify-between border border-slate-200 rounded-md px-3 py-2 bg-white">
                        <Label>Adresse courante</Label>
                        <Switch checked={!!editAdr.courant} onCheckedChange={(v) => setField("courant", v)} data-testid="adr-courant-switch" />
                    </div>
                    <div className="flex justify-end gap-2">
                        <Button variant="outline" onClick={() => setEditAdr(null)} className="rounded-md" data-testid="cancel-adresse-btn">Annuler</Button>
                        <Button onClick={handleSave} className="rounded-md bg-[#0033A0] hover:bg-[#002277] text-white" data-testid="save-adresse-btn">Enregistrer</Button>
                    </div>
                </div>
            )}

            <AlertDialog open={confirm !== null} onOpenChange={(o) => !o && setConfirm(null)}>
                <AlertDialogContent data-testid="adr-confirm-dialog">
                    {confirm?.type === "replace" && (
                        <>
                            <AlertDialogHeader>
                                <AlertDialogTitle>Remplacer l'adresse courante ?</AlertDialogTitle>
                                <AlertDialogDescription>
                                    L'adresse <span className="font-semibold">{confirm.existing?.address || "—"}</span>
                                    {confirm.existing?.ville ? `, ${confirm.existing.ville}` : ""} est actuellement définie comme courante.
                                    En enregistrant cette adresse comme courante, l'autre cessera de l'être.
                                    Souhaitez-vous continuer ?
                                </AlertDialogDescription>
                            </AlertDialogHeader>
                            <AlertDialogFooter>
                                <AlertDialogCancel onClick={confirmNo} data-testid="adr-confirm-no">Non, garder l'autre comme courante</AlertDialogCancel>
                                <AlertDialogAction onClick={confirmYes} data-testid="adr-confirm-yes" className="bg-[#0033A0] hover:bg-[#002277]">Oui, remplacer</AlertDialogAction>
                            </AlertDialogFooter>
                        </>
                    )}
                    {confirm?.type === "promote" && (
                        <>
                            <AlertDialogHeader>
                                <AlertDialogTitle>Définir comme adresse courante ?</AlertDialogTitle>
                                <AlertDialogDescription>
                                    Aucune adresse courante n'est définie pour cet avocat.
                                    Voulez-vous définir <span className="font-semibold">cette nouvelle adresse</span> comme courante ?
                                </AlertDialogDescription>
                            </AlertDialogHeader>
                            <AlertDialogFooter>
                                <AlertDialogCancel onClick={confirmNo} data-testid="adr-confirm-no">Non, enregistrer sans</AlertDialogCancel>
                                <AlertDialogAction onClick={confirmYes} data-testid="adr-confirm-yes" className="bg-[#0033A0] hover:bg-[#002277]">Oui, la définir comme courante</AlertDialogAction>
                            </AlertDialogFooter>
                        </>
                    )}
                    {confirm?.type === "switch" && (
                        <>
                            <AlertDialogHeader>
                                <AlertDialogTitle>Définir cette adresse comme courante ?</AlertDialogTitle>
                                <AlertDialogDescription>
                                    L'adresse <span className="font-semibold">{confirm.existing?.address || "—"}</span>
                                    {confirm.existing?.ville ? `, ${confirm.existing.ville}` : ""} est actuellement la courante.
                                    Voulez-vous plutôt définir <span className="font-semibold">cette nouvelle adresse</span> comme courante ?
                                </AlertDialogDescription>
                            </AlertDialogHeader>
                            <AlertDialogFooter>
                                <AlertDialogCancel onClick={confirmNo} data-testid="adr-confirm-no">Non, garder l'autre</AlertDialogCancel>
                                <AlertDialogAction onClick={confirmYes} data-testid="adr-confirm-yes" className="bg-[#0033A0] hover:bg-[#002277]">Oui, basculer sur celle-ci</AlertDialogAction>
                            </AlertDialogFooter>
                        </>
                    )}
                </AlertDialogContent>
            </AlertDialog>
        </div>
    );
};
