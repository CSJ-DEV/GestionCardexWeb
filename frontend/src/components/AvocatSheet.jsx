import { useEffect, useState } from "react";
import api, { formatApiError } from "@/lib/api";
import {
    Sheet,
    SheetContent,
    SheetDescription,
    SheetHeader,
    SheetTitle,
} from "@/components/ui/sheet";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Switch } from "@/components/ui/switch";
import { Textarea } from "@/components/ui/textarea";
import { Separator } from "@/components/ui/separator";
import { toast } from "sonner";

const emptyAvocat = {
    code: "",
    nom: "",
    prenom: "",
    sectbar: "",
    mega: false,
    actif: true,
    dateinscbarr: "",
    payable: true,
    codebar: "",
    nas: "",
    neq: "",
    villerref: "",
    depodirect: false,
    factweb: false,
    confweb: false,
    surveil: false,
    comm: "",
    adresse: {
        address: "",
        ville: "",
        province: "QC",
        codepostal: "",
        telephone: "",
        telephone2: "",
        fax: "",
        email: "",
    },
};

const Field = ({ label, children, testId }) => (
    <div className="space-y-1.5">
        <Label className="text-xs font-medium text-slate-700" data-testid={testId ? `${testId}-label` : undefined}>
            {label}
        </Label>
        {children}
    </div>
);

export default function AvocatSheet({ open, onOpenChange, avocat, onSaved }) {
    const isEditing = !!(avocat && avocat.id);
    const [form, setForm] = useState(emptyAvocat);
    const [saving, setSaving] = useState(false);

    useEffect(() => {
        if (avocat && avocat.id) {
            setForm({ ...emptyAvocat, ...avocat, adresse: { ...emptyAvocat.adresse, ...(avocat.adresse || {}) } });
        } else if (avocat) {
            setForm(emptyAvocat);
        }
    }, [avocat]);

    const update = (key, value) => setForm((f) => ({ ...f, [key]: value }));
    const updateAdresse = (key, value) =>
        setForm((f) => ({ ...f, adresse: { ...f.adresse, [key]: value } }));

    const handleSubmit = async (e) => {
        e.preventDefault();
        if (!form.code || !form.nom || !form.prenom) {
            toast.error("Code, nom et prénom sont requis.");
            return;
        }
        setSaving(true);
        try {
            if (isEditing) {
                const { id: _id, created_at: _ca, updated_at: _ua, usermodif: _u, ...payload } = form;
                await api.put(`/avocats/${avocat.id}`, payload);
                toast.success("Avocat mis à jour");
            } else {
                await api.post("/avocats", form);
                toast.success("Avocat créé");
            }
            onSaved?.();
        } catch (err) {
            toast.error(formatApiError(err.response?.data?.detail) || "Erreur lors de l'enregistrement");
        } finally {
            setSaving(false);
        }
    };

    return (
        <Sheet open={open} onOpenChange={onOpenChange}>
            <SheetContent
                className="sm:max-w-2xl w-full overflow-y-auto"
                data-testid="avocat-sheet"
            >
                <SheetHeader>
                    <SheetTitle className="font-display text-2xl tracking-tight">
                        {isEditing ? "Modifier l'avocat" : "Nouvel avocat"}
                    </SheetTitle>
                    <SheetDescription>
                        {isEditing
                            ? "Mettre à jour les informations de la fiche."
                            : "Remplir les informations pour créer une nouvelle fiche."}
                    </SheetDescription>
                </SheetHeader>

                <form onSubmit={handleSubmit} className="mt-6 space-y-6" data-testid="avocat-form">
                    <div>
                        <div className="overline mb-3">Identité</div>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            <Field label="Code (unique)">
                                <Input
                                    value={form.code}
                                    onChange={(e) => update("code", e.target.value.toUpperCase())}
                                    disabled={isEditing}
                                    required
                                    maxLength={10}
                                    className="rounded-md font-mono"
                                    data-testid="avocat-input-code"
                                />
                            </Field>
                            <Field label="Section barreau">
                                <Input
                                    value={form.sectbar}
                                    onChange={(e) => update("sectbar", e.target.value)}
                                    className="rounded-md"
                                    data-testid="avocat-input-sectbar"
                                />
                            </Field>
                            <Field label="Nom">
                                <Input
                                    value={form.nom}
                                    onChange={(e) => update("nom", e.target.value)}
                                    required
                                    className="rounded-md"
                                    data-testid="avocat-input-nom"
                                />
                            </Field>
                            <Field label="Prénom">
                                <Input
                                    value={form.prenom}
                                    onChange={(e) => update("prenom", e.target.value)}
                                    required
                                    className="rounded-md"
                                    data-testid="avocat-input-prenom"
                                />
                            </Field>
                            <Field label="Date d'inscription au barreau">
                                <Input
                                    type="date"
                                    value={form.dateinscbarr || ""}
                                    onChange={(e) => update("dateinscbarr", e.target.value)}
                                    className="rounded-md"
                                    data-testid="avocat-input-dateinsc"
                                />
                            </Field>
                            <Field label="Code barreau">
                                <Input
                                    value={form.codebar}
                                    onChange={(e) => update("codebar", e.target.value)}
                                    className="rounded-md font-mono"
                                    data-testid="avocat-input-codebar"
                                />
                            </Field>
                            <Field label="NAS">
                                <Input
                                    value={form.nas}
                                    onChange={(e) => update("nas", e.target.value)}
                                    maxLength={9}
                                    className="rounded-md font-mono"
                                    data-testid="avocat-input-nas"
                                />
                            </Field>
                            <Field label="NEQ">
                                <Input
                                    value={form.neq}
                                    onChange={(e) => update("neq", e.target.value)}
                                    maxLength={10}
                                    className="rounded-md font-mono"
                                    data-testid="avocat-input-neq"
                                />
                            </Field>
                        </div>
                    </div>

                    <Separator />

                    <div>
                        <div className="overline mb-3">Adresse courante</div>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            <Field label="Adresse">
                                <Input
                                    value={form.adresse.address}
                                    onChange={(e) => updateAdresse("address", e.target.value)}
                                    className="rounded-md"
                                    data-testid="avocat-input-address"
                                />
                            </Field>
                            <Field label="Ville">
                                <Input
                                    value={form.adresse.ville}
                                    onChange={(e) => updateAdresse("ville", e.target.value)}
                                    className="rounded-md"
                                    data-testid="avocat-input-ville"
                                />
                            </Field>
                            <Field label="Province">
                                <Input
                                    value={form.adresse.province}
                                    onChange={(e) => updateAdresse("province", e.target.value)}
                                    className="rounded-md"
                                    data-testid="avocat-input-province"
                                />
                            </Field>
                            <Field label="Code postal">
                                <Input
                                    value={form.adresse.codepostal}
                                    onChange={(e) => updateAdresse("codepostal", e.target.value)}
                                    className="rounded-md font-mono"
                                    data-testid="avocat-input-codepostal"
                                />
                            </Field>
                            <Field label="Téléphone">
                                <Input
                                    value={form.adresse.telephone}
                                    onChange={(e) => updateAdresse("telephone", e.target.value)}
                                    className="rounded-md"
                                    data-testid="avocat-input-telephone"
                                />
                            </Field>
                            <Field label="Téléphone (2)">
                                <Input
                                    value={form.adresse.telephone2}
                                    onChange={(e) => updateAdresse("telephone2", e.target.value)}
                                    className="rounded-md"
                                    data-testid="avocat-input-telephone2"
                                />
                            </Field>
                            <Field label="Courriel">
                                <Input
                                    type="email"
                                    value={form.adresse.email}
                                    onChange={(e) => updateAdresse("email", e.target.value)}
                                    className="rounded-md"
                                    data-testid="avocat-input-email"
                                />
                            </Field>
                            <Field label="Télécopieur">
                                <Input
                                    value={form.adresse.fax}
                                    onChange={(e) => updateAdresse("fax", e.target.value)}
                                    className="rounded-md"
                                    data-testid="avocat-input-fax"
                                />
                            </Field>
                        </div>
                    </div>

                    <Separator />

                    <div>
                        <div className="overline mb-3">Statuts & options</div>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-y-3 gap-x-6">
                            {[
                                { key: "actif", label: "Actif" },
                                { key: "mega", label: "Méga" },
                                { key: "payable", label: "Payable" },
                                { key: "depodirect", label: "Dépôt direct" },
                                { key: "factweb", label: "Facturation web" },
                                { key: "confweb", label: "Confirmation web" },
                                { key: "surveil", label: "Sous surveillance" },
                            ].map((opt) => (
                                <div
                                    key={opt.key}
                                    className="flex items-center justify-between border border-slate-200 rounded-md px-3 py-2"
                                >
                                    <Label className="text-sm text-slate-700">{opt.label}</Label>
                                    <Switch
                                        checked={!!form[opt.key]}
                                        onCheckedChange={(v) => update(opt.key, v)}
                                        data-testid={`avocat-switch-${opt.key}`}
                                    />
                                </div>
                            ))}
                        </div>
                    </div>

                    <Separator />

                    <Field label="Commentaires">
                        <Textarea
                            value={form.comm}
                            onChange={(e) => update("comm", e.target.value)}
                            rows={4}
                            className="rounded-md"
                            data-testid="avocat-input-comm"
                        />
                    </Field>

                    <div className="flex justify-end gap-2 pt-2">
                        <Button
                            type="button"
                            variant="outline"
                            onClick={() => onOpenChange(false)}
                            className="rounded-md"
                            data-testid="avocat-cancel"
                        >
                            Annuler
                        </Button>
                        <Button
                            type="submit"
                            disabled={saving}
                            className="rounded-md bg-[#0033A0] hover:bg-[#002277] text-white"
                            data-testid="avocat-submit"
                        >
                            {saving ? "Enregistrement…" : isEditing ? "Mettre à jour" : "Créer la fiche"}
                        </Button>
                    </div>
                </form>
            </SheetContent>
        </Sheet>
    );
}
