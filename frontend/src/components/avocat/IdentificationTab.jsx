import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Switch } from "@/components/ui/switch";
import { Textarea } from "@/components/ui/textarea";
import { Separator } from "@/components/ui/separator";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Field } from "./constants";
import { DateInput } from "./DateInput";

const STATUTS = [
    { k: "actif", l: "Actif" }, { k: "payable", l: "Payable" },
    { k: "depodirect", l: "Dépôt direct" }, { k: "factweb", l: "Facturation web" },
    { k: "confweb", l: "Confirmation web" }, { k: "mega", l: "Méga" },
    { k: "surveil", l: "En attente" },
];

export const IdentificationTab = ({
    form, upd, isEditing, readOnly, saving, onTypeChange,
    onSubmit, onCancel, savedMega, savedFactweb,
}) => (
    <form onSubmit={onSubmit} className="space-y-6" data-testid="avocat-form">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Field label="Type de code">
                <Select value={form.type_code} onValueChange={onTypeChange} disabled={isEditing || readOnly}>
                    <SelectTrigger className="rounded-md" data-testid="avocat-type-code"><SelectValue /></SelectTrigger>
                    <SelectContent>
                        <SelectItem value="A">A — Avocat permanent</SelectItem>
                        <SelectItem value="P">P — Avocat privé</SelectItem>
                        <SelectItem value="N">N — Notaire</SelectItem>
                    </SelectContent>
                </Select>
            </Field>
            <Field label={isEditing ? "Code" : "Code (généré à la sauvegarde)"}>
                <Input
                    value={isEditing ? (form.code || "") : ""}
                    placeholder={isEditing ? "" : "— attribué automatiquement —"}
                    disabled
                    className="rounded-md font-mono"
                    data-testid="avocat-input-code"
                />
            </Field>
            <Field label="Section barreau">
                <Input value={form.sectbar} onChange={(e) => upd("sectbar", e.target.value)} disabled={readOnly} className="rounded-md" />
            </Field>
            <Field label="Nom">
                <Input value={form.nom} onChange={(e) => upd("nom", e.target.value)} disabled={readOnly} required className="rounded-md" data-testid="avocat-input-nom" />
            </Field>
            <Field label="Prénom">
                <Input value={form.prenom} onChange={(e) => upd("prenom", e.target.value)} disabled={readOnly} required className="rounded-md" data-testid="avocat-input-prenom" />
            </Field>
            <Field label="Année barreau">
                <Input value={form.annee_barreau} onChange={(e) => upd("annee_barreau", e.target.value)} disabled={readOnly} maxLength={4} className="rounded-md font-mono" />
            </Field>
            <Field label="Code barreau">
                <Input value={form.codebar} onChange={(e) => upd("codebar", e.target.value)} disabled={readOnly} className="rounded-md font-mono" />
            </Field>
            <Field label="NAS (validation Luhn)">
                <Input value={form.nas} onChange={(e) => upd("nas", e.target.value.replace(/\D/g, "").slice(0, 9))} disabled={readOnly} maxLength={9} className="rounded-md font-mono" data-testid="avocat-input-nas" />
            </Field>
            <Field label="NEQ">
                <Input value={form.neq} onChange={(e) => upd("neq", e.target.value)} disabled={readOnly} maxLength={10} className="rounded-md font-mono" />
            </Field>
            <Field label="Date inscription barreau">
                <DateInput value={form.dateinscbarr || ""} onChange={(v) => upd("dateinscbarr", v)} disabled={readOnly} className="rounded-md font-mono" />
            </Field>
            <Field label="Taxes (lecture seule — autre serveur)">
                <Input value={form.taxes || ""} disabled placeholder="— provient de la BDD taxes —" className="rounded-md text-slate-500" data-testid="avocat-input-taxes" />
            </Field>
            <Field label="Ville référence">
                <Input value={form.villerref} onChange={(e) => upd("villerref", e.target.value)} disabled={readOnly} className="rounded-md" />
            </Field>
        </div>

        <Separator />
        <div className="overline">Statuts</div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {STATUTS.map((o) => {
                // Cas spéciaux Méga & Facturation web : l'onglet correspondant
                // ne sera accessible qu'après sauvegarde de l'identification.
                const megaPendingSave = o.k === "mega" && isEditing && !!form.mega && !savedMega;
                const megaPendingDisable = o.k === "mega" && isEditing && !form.mega && !!savedMega;
                const webPendingSave = o.k === "factweb" && isEditing && !!form.factweb && !savedFactweb;
                const webPendingDisable = o.k === "factweb" && isEditing && !form.factweb && !!savedFactweb;
                return (
                    <div key={o.k} className="flex flex-col border border-slate-200 rounded-md px-3 py-2">
                        <div className="flex items-center justify-between">
                            <Label className="text-sm">{o.l}</Label>
                            <Switch checked={!!form[o.k]} onCheckedChange={(v) => upd(o.k, v)} disabled={readOnly} data-testid={`avocat-switch-${o.k}`} />
                        </div>
                        {megaPendingSave && (
                            <p className="text-xs text-amber-700 mt-1.5" data-testid="mega-pending-hint">
                                ⚠ Cliquez sur « Mettre à jour » pour activer l'onglet Méga.
                            </p>
                        )}
                        {megaPendingDisable && (
                            <p className="text-xs text-amber-700 mt-1.5" data-testid="mega-pending-hint">
                                ⚠ Cliquez sur « Mettre à jour » pour désactiver l'onglet Méga.
                            </p>
                        )}
                        {webPendingSave && (
                            <p className="text-xs text-amber-700 mt-1.5" data-testid="web-pending-hint">
                                ⚠ Cliquez sur « Mettre à jour » pour activer l'onglet Web.
                            </p>
                        )}
                        {webPendingDisable && (
                            <p className="text-xs text-amber-700 mt-1.5" data-testid="web-pending-hint">
                                ⚠ Cliquez sur « Mettre à jour » pour désactiver l'onglet Web.
                            </p>
                        )}
                    </div>
                );
            })}
        </div>

        <Separator />
        <Field label="Commentaires">
            <Textarea value={form.comm} onChange={(e) => upd("comm", e.target.value)} disabled={readOnly} rows={4} className="rounded-md" />
        </Field>

        <div className="flex justify-end gap-2 pt-2">
            <Button type="button" variant="outline" onClick={onCancel} className="rounded-md" data-testid="avocat-cancel">Annuler</Button>
            {!readOnly && (
                <Button type="submit" disabled={saving} className="rounded-md bg-[#0033A0] hover:bg-[#002277] text-white" data-testid="avocat-submit">
                    {saving ? "Enregistrement…" : isEditing ? "Mettre à jour" : "Créer"}
                </Button>
            )}
        </div>
    </form>
);
