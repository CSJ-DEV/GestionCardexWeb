import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Switch } from "@/components/ui/switch";
import { Textarea } from "@/components/ui/textarea";
import { Separator } from "@/components/ui/separator";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Field } from "./constants";

const STATUTS = [
    { k: "actif", l: "Actif" }, { k: "attente", l: "En attente" },
    { k: "payable", l: "Payable" }, { k: "depodirect", l: "Dépôt direct" },
    { k: "factweb", l: "Facturation web" }, { k: "confweb", l: "Confirmation web" },
    { k: "mega", l: "Méga" }, { k: "surveil", l: "Sous surveillance" },
];

export const IdentificationTab = ({
    form, upd, isEditing, readOnly, saving, onTypeChange,
    onSubmit, onCancel,
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
                <Input type="date" value={form.dateinscbarr || ""} onChange={(e) => upd("dateinscbarr", e.target.value)} disabled={readOnly} className="rounded-md" />
            </Field>
            <Field label="Taxes">
                <Input value={form.taxes} onChange={(e) => upd("taxes", e.target.value)} disabled={readOnly} className="rounded-md" />
            </Field>
            <Field label="Ville référence">
                <Input value={form.villerref} onChange={(e) => upd("villerref", e.target.value)} disabled={readOnly} className="rounded-md" />
            </Field>
        </div>

        <Separator />
        <div className="overline">Statuts</div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {STATUTS.map((o) => (
                <div key={o.k} className="flex items-center justify-between border border-slate-200 rounded-md px-3 py-2">
                    <Label className="text-sm">{o.l}</Label>
                    <Switch checked={!!form[o.k]} onCheckedChange={(v) => upd(o.k, v)} disabled={readOnly} data-testid={`avocat-switch-${o.k}`} />
                </div>
            ))}
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
