import { useEffect, useState } from "react";
import api, { formatApiError } from "@/lib/api";
import { useAuth } from "@/context/AuthContext";
import { Sheet, SheetContent, SheetDescription, SheetHeader, SheetTitle } from "@/components/ui/sheet";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Switch } from "@/components/ui/switch";
import { Textarea } from "@/components/ui/textarea";
import { Separator } from "@/components/ui/separator";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Badge } from "@/components/ui/badge";
import { Plus, Pencil, Trash2, Star } from "lucide-react";
import { toast } from "sonner";

const emptyAvocat = {
    code: "", type_code: "A", nom: "", prenom: "",
    sectbar: "", annee_barreau: "", codebar: "", nas: "", neq: "", taxes: "",
    dateinscbarr: "", villerref: "", comm: "",
    actif: true, attente: false, payable: true, mega: false,
    depodirect: false, factweb: false, confweb: false, surveil: false,
    adresse: { address: "", ville: "", province: "QC", codepostal: "", telephone: "", email: "" },
};

const emptyAdresse = { address: "", adresse2: "", adresse3: "", ville: "", province: "QC", codepostal: "", telephone: "", telephone2: "", fax: "", email: "" };

const F = ({ label, children, testId }) => (
    <div className="space-y-1.5">
        <Label className="text-xs font-medium text-slate-700">{label}</Label>
        {children}
    </div>
);

export default function AvocatSheet({ open, onOpenChange, avocat, onSaved }) {
    const { user } = useAuth();
    const readOnly = user?.role === "lecteur";
    const isEditing = !!(avocat && avocat.id);
    const [form, setForm] = useState(emptyAvocat);
    const [saving, setSaving] = useState(false);
    const [adresses, setAdresses] = useState([]);
    const [editAdr, setEditAdr] = useState(null);

    useEffect(() => {
        if (avocat?.id) {
            setForm({ ...emptyAvocat, ...avocat, adresse: { ...emptyAvocat.adresse, ...(avocat.adresse || {}) } });
            api.get(`/avocats/${avocat.id}/adresses`).then(({ data }) => setAdresses(data || []));
        } else if (avocat) {
            setForm(emptyAvocat);
            setAdresses([]);
            // Auto-fetch suggested code
            api.get(`/avocats/next-code?type=A`).then(({ data }) => setForm((f) => ({ ...f, code: data.code })));
        }
    }, [avocat]);

    const upd = (k, v) => setForm((f) => ({ ...f, [k]: v }));

    const onTypeChange = async (t) => {
        upd("type_code", t);
        if (!isEditing) {
            try {
                const { data } = await api.get(`/avocats/next-code?type=${t}`);
                upd("code", data.code);
            } catch { /* ignore */ }
        }
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        if (!form.code || !form.nom || !form.prenom) {
            toast.error("Code, nom et prénom sont requis");
            return;
        }
        setSaving(true);
        try {
            if (isEditing) {
                const { id: _i, created_at: _c, updated_at: _u, usermodif: _m, ...payload } = form;
                await api.put(`/avocats/${avocat.id}`, payload);
                toast.success("Avocat mis à jour");
            } else {
                await api.post("/avocats", form);
                toast.success("Avocat créé");
            }
            onSaved?.();
        } catch (err) {
            toast.error(formatApiError(err.response?.data?.detail) || "Erreur");
        } finally {
            setSaving(false);
        }
    };

    const reloadAdresses = async () => {
        const { data } = await api.get(`/avocats/${avocat.id}/adresses`);
        setAdresses(data || []);
    };

    const saveAdresse = async () => {
        if (!editAdr) return;
        const { id, courant, ...payload } = editAdr;
        try {
            if (id) {
                await api.put(`/avocats/${avocat.id}/adresses/${id}?courant=${!!courant}`, payload);
            } else {
                await api.post(`/avocats/${avocat.id}/adresses?courant=${!!courant}`, payload);
            }
            toast.success("Adresse enregistrée");
            setEditAdr(null);
            reloadAdresses();
            onSaved?.();
        } catch (err) {
            toast.error(formatApiError(err.response?.data?.detail) || "Erreur");
        }
    };

    const deleteAdresse = async (adr) => {
        if (!confirm("Supprimer cette adresse ?")) return;
        try {
            await api.delete(`/avocats/${avocat.id}/adresses/${adr.id}`);
            toast.success("Adresse supprimée");
            reloadAdresses();
        } catch (err) {
            toast.error(formatApiError(err.response?.data?.detail) || "Erreur");
        }
    };

    return (
        <Sheet open={open} onOpenChange={onOpenChange}>
            <SheetContent className="sm:max-w-3xl w-full overflow-y-auto" data-testid="avocat-sheet">
                <SheetHeader>
                    <SheetTitle className="font-display text-2xl tracking-tight">
                        {isEditing ? `${form.prenom} ${form.nom} (${form.code})` : "Nouvel avocat"}
                    </SheetTitle>
                    <SheetDescription>Fiche complète — fidèle à GestionCardex VB</SheetDescription>
                </SheetHeader>

                <Tabs defaultValue="ident" className="mt-6">
                    <TabsList className="grid grid-cols-2 w-full">
                        <TabsTrigger value="ident" data-testid="tab-ident">Identification</TabsTrigger>
                        <TabsTrigger value="adr" disabled={!isEditing} data-testid="tab-adr">
                            Adresses {adresses.length > 0 && `(${adresses.length})`}
                        </TabsTrigger>
                    </TabsList>

                    {/* IDENTIFICATION */}
                    <TabsContent value="ident" className="mt-6">
                        <form onSubmit={handleSubmit} className="space-y-6" data-testid="avocat-form">
                            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                                <F label="Type de code">
                                    <Select value={form.type_code} onValueChange={onTypeChange} disabled={isEditing || readOnly}>
                                        <SelectTrigger className="rounded-md" data-testid="avocat-type-code"><SelectValue /></SelectTrigger>
                                        <SelectContent>
                                            <SelectItem value="A">A — Avocat permanent</SelectItem>
                                            <SelectItem value="P">P — Avocat privé</SelectItem>
                                            <SelectItem value="N">N — Notaire</SelectItem>
                                        </SelectContent>
                                    </Select>
                                </F>
                                <F label="Code (auto-généré)">
                                    <Input value={form.code} disabled className="rounded-md font-mono" data-testid="avocat-input-code" />
                                </F>
                                <F label="Section barreau">
                                    <Input value={form.sectbar} onChange={(e) => upd("sectbar", e.target.value)} disabled={readOnly} className="rounded-md" />
                                </F>
                                <F label="Nom">
                                    <Input value={form.nom} onChange={(e) => upd("nom", e.target.value)} disabled={readOnly} required className="rounded-md" data-testid="avocat-input-nom" />
                                </F>
                                <F label="Prénom">
                                    <Input value={form.prenom} onChange={(e) => upd("prenom", e.target.value)} disabled={readOnly} required className="rounded-md" data-testid="avocat-input-prenom" />
                                </F>
                                <F label="Année barreau">
                                    <Input value={form.annee_barreau} onChange={(e) => upd("annee_barreau", e.target.value)} disabled={readOnly} maxLength={4} className="rounded-md font-mono" />
                                </F>
                                <F label="Code barreau">
                                    <Input value={form.codebar} onChange={(e) => upd("codebar", e.target.value)} disabled={readOnly} className="rounded-md font-mono" />
                                </F>
                                <F label="NAS (validation Luhn)">
                                    <Input value={form.nas} onChange={(e) => upd("nas", e.target.value.replace(/\D/g, "").slice(0, 9))} disabled={readOnly} maxLength={9} className="rounded-md font-mono" data-testid="avocat-input-nas" />
                                </F>
                                <F label="NEQ">
                                    <Input value={form.neq} onChange={(e) => upd("neq", e.target.value)} disabled={readOnly} maxLength={10} className="rounded-md font-mono" />
                                </F>
                                <F label="Date inscription barreau">
                                    <Input type="date" value={form.dateinscbarr || ""} onChange={(e) => upd("dateinscbarr", e.target.value)} disabled={readOnly} className="rounded-md" />
                                </F>
                                <F label="Taxes">
                                    <Input value={form.taxes} onChange={(e) => upd("taxes", e.target.value)} disabled={readOnly} className="rounded-md" />
                                </F>
                                <F label="Ville référence">
                                    <Input value={form.villerref} onChange={(e) => upd("villerref", e.target.value)} disabled={readOnly} className="rounded-md" />
                                </F>
                            </div>

                            <Separator />
                            <div className="overline">Statuts</div>
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                                {[
                                    { k: "actif", l: "Actif" }, { k: "attente", l: "En attente" },
                                    { k: "payable", l: "Payable" }, { k: "depodirect", l: "Dépôt direct" },
                                    { k: "factweb", l: "Facturation web" }, { k: "confweb", l: "Confirmation web" },
                                    { k: "mega", l: "Méga" }, { k: "surveil", l: "Sous surveillance" },
                                ].map((o) => (
                                    <div key={o.k} className="flex items-center justify-between border border-slate-200 rounded-md px-3 py-2">
                                        <Label className="text-sm">{o.l}</Label>
                                        <Switch checked={!!form[o.k]} onCheckedChange={(v) => upd(o.k, v)} disabled={readOnly} data-testid={`avocat-switch-${o.k}`} />
                                    </div>
                                ))}
                            </div>

                            <Separator />
                            <F label="Commentaires">
                                <Textarea value={form.comm} onChange={(e) => upd("comm", e.target.value)} disabled={readOnly} rows={4} className="rounded-md" />
                            </F>

                            <div className="flex justify-end gap-2 pt-2">
                                <Button type="button" variant="outline" onClick={() => onOpenChange(false)} className="rounded-md">Annuler</Button>
                                {!readOnly && (
                                    <Button type="submit" disabled={saving} className="rounded-md bg-[#0033A0] hover:bg-[#002277] text-white" data-testid="avocat-submit">
                                        {saving ? "Enregistrement…" : isEditing ? "Mettre à jour" : "Créer"}
                                    </Button>
                                )}
                            </div>
                        </form>
                    </TabsContent>

                    {/* ADRESSES */}
                    <TabsContent value="adr" className="mt-6 space-y-4">
                        {!readOnly && (
                            <Button onClick={() => setEditAdr({ ...emptyAdresse, courant: adresses.length === 0 })} className="rounded-md bg-[#0033A0] hover:bg-[#002277] text-white" data-testid="add-adresse-btn">
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
                                                <Button variant="ghost" size="icon" onClick={() => setEditAdr(adr)}><Pencil size={14} /></Button>
                                                <Button variant="ghost" size="icon" className="text-red-600" onClick={() => deleteAdresse(adr)}><Trash2 size={14} /></Button>
                                            </div>
                                        )}
                                    </div>
                                ))
                            )}
                        </div>

                        {/* Inline adresse editor */}
                        {editAdr && (
                            <div className="border-2 border-[#0033A0] rounded-md p-4 space-y-3 bg-blue-50/30">
                                <div className="font-semibold text-sm">{editAdr.id ? "Modifier l'adresse" : "Nouvelle adresse"}</div>
                                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                                    <F label="Adresse"><Input value={editAdr.address || ""} onChange={(e) => setEditAdr({ ...editAdr, address: e.target.value })} className="rounded-md" /></F>
                                    <F label="Ville"><Input value={editAdr.ville || ""} onChange={(e) => setEditAdr({ ...editAdr, ville: e.target.value })} className="rounded-md" /></F>
                                    <F label="Province"><Input value={editAdr.province || ""} onChange={(e) => setEditAdr({ ...editAdr, province: e.target.value })} className="rounded-md" /></F>
                                    <F label="Code postal"><Input value={editAdr.codepostal || ""} onChange={(e) => setEditAdr({ ...editAdr, codepostal: e.target.value.toUpperCase() })} maxLength={7} className="rounded-md font-mono" /></F>
                                    <F label="Téléphone"><Input value={editAdr.telephone || ""} onChange={(e) => setEditAdr({ ...editAdr, telephone: e.target.value })} className="rounded-md" /></F>
                                    <F label="Téléphone 2"><Input value={editAdr.telephone2 || ""} onChange={(e) => setEditAdr({ ...editAdr, telephone2: e.target.value })} className="rounded-md" /></F>
                                    <F label="Télécopieur"><Input value={editAdr.fax || ""} onChange={(e) => setEditAdr({ ...editAdr, fax: e.target.value })} className="rounded-md" /></F>
                                    <F label="Courriel"><Input type="email" value={editAdr.email || ""} onChange={(e) => setEditAdr({ ...editAdr, email: e.target.value })} className="rounded-md" /></F>
                                </div>
                                <div className="flex items-center justify-between border border-slate-200 rounded-md px-3 py-2 bg-white">
                                    <Label>Adresse courante</Label>
                                    <Switch checked={!!editAdr.courant} onCheckedChange={(v) => setEditAdr({ ...editAdr, courant: v })} />
                                </div>
                                <div className="flex justify-end gap-2">
                                    <Button variant="outline" onClick={() => setEditAdr(null)} className="rounded-md">Annuler</Button>
                                    <Button onClick={saveAdresse} className="rounded-md bg-[#0033A0] hover:bg-[#002277] text-white" data-testid="save-adresse-btn">Enregistrer</Button>
                                </div>
                            </div>
                        )}
                    </TabsContent>
                </Tabs>
            </SheetContent>
        </Sheet>
    );
}
