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
    const [inhabs, setInhabs] = useState([]);
    const [editInhab, setEditInhab] = useState(null);
    const [mega, setMega] = useState({ sectbar: "", francais: true, anglais: false, autres: "", experience: 0, details: "", art486: false, art672: false, art684: false, commentaire: "", dateinsc: "", districts: [], tous_districts: false });
    const [megaSaving, setMegaSaving] = useState(false);

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
                    <TabsList className="grid grid-cols-5 w-full">
                        <TabsTrigger value="ident" data-testid="tab-ident">Identification</TabsTrigger>
                        <TabsTrigger value="adr" disabled={!isEditing} data-testid="tab-adr">
                            Adresses {adresses.length > 0 && `(${adresses.length})`}
                        </TabsTrigger>
                        <TabsTrigger value="inhab" disabled={!isEditing} data-testid="tab-inhab">
                            Inhabilité {inhabs.length > 0 && `(${inhabs.length})`}
                        </TabsTrigger>
                        <TabsTrigger value="mega" disabled={!isEditing} data-testid="tab-mega">Méga</TabsTrigger>
                        <TabsTrigger value="web" disabled={!isEditing} data-testid="tab-web">Web</TabsTrigger>
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

                    {/* INHABILITÉ */}
                    <TabsContent value="inhab" className="mt-6 space-y-4">
                        {!readOnly && (
                            <Button onClick={() => setEditInhab({ datedeb: "", datefin: "", comm: "" })} className="rounded-md bg-[#0033A0] hover:bg-[#002277] text-white" data-testid="add-inhab-btn">
                                <Plus size={14} className="mr-2" /> Nouvelle période
                            </Button>
                        )}
                        <div className="space-y-2">
                            {inhabs.length === 0 ? (
                                <div className="text-sm text-slate-500 text-center py-8 border border-dashed border-slate-300 rounded-md">
                                    Aucune période d'inhabilité.
                                </div>
                            ) : (
                                inhabs.map((it) => (
                                    <div key={it.id} className="border border-slate-200 rounded-md p-3 flex items-start justify-between" data-testid={`inhab-row-${it.id}`}>
                                        <div className="flex-1">
                                            <div className="font-medium text-slate-900">{it.datedeb} → {it.datefin || "en cours"}</div>
                                            {it.comm && <div className="text-xs text-slate-600 mt-1">{it.comm}</div>}
                                        </div>
                                        {!readOnly && (
                                            <div className="flex gap-1">
                                                <Button variant="ghost" size="icon" onClick={() => setEditInhab(it)}><Pencil size={14} /></Button>
                                                <Button variant="ghost" size="icon" className="text-red-600" onClick={() => deleteInhab(it)}><Trash2 size={14} /></Button>
                                            </div>
                                        )}
                                    </div>
                                ))
                            )}
                        </div>
                        {editInhab && (
                            <div className="border-2 border-[#0033A0] rounded-md p-4 space-y-3 bg-blue-50/30">
                                <div className="font-semibold text-sm">{editInhab.id ? "Modifier la période" : "Nouvelle période"}</div>
                                <div className="grid grid-cols-2 gap-3">
                                    <F label="Date début"><Input type="date" value={editInhab.datedeb || ""} onChange={(e) => setEditInhab({ ...editInhab, datedeb: e.target.value })} className="rounded-md" data-testid="inhab-datedeb" /></F>
                                    <F label="Date fin"><Input type="date" value={editInhab.datefin || ""} onChange={(e) => setEditInhab({ ...editInhab, datefin: e.target.value })} className="rounded-md" data-testid="inhab-datefin" /></F>
                                </div>
                                <F label="Commentaire"><Textarea value={editInhab.comm || ""} onChange={(e) => setEditInhab({ ...editInhab, comm: e.target.value })} rows={3} className="rounded-md" /></F>
                                <div className="flex justify-end gap-2">
                                    <Button variant="outline" onClick={() => setEditInhab(null)}>Annuler</Button>
                                    <Button onClick={saveInhab} className="bg-[#0033A0] hover:bg-[#002277] text-white" data-testid="save-inhab-btn">Enregistrer</Button>
                                </div>
                            </div>
                        )}
                    </TabsContent>

                    {/* MÉGA */}
                    <TabsContent value="mega" className="mt-6 space-y-5">
                        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                            <F label="Section barreau"><Input value={mega.sectbar || ""} onChange={(e) => setMega({ ...mega, sectbar: e.target.value })} disabled={readOnly} className="rounded-md" data-testid="mega-sectbar" /></F>
                            <F label="Expérience (années)"><Input type="number" min="0" value={mega.experience || 0} onChange={(e) => setMega({ ...mega, experience: parseInt(e.target.value) || 0 })} disabled={readOnly} className="rounded-md" data-testid="mega-experience" /></F>
                            <F label="Date inscription"><Input type="date" value={mega.dateinsc || ""} onChange={(e) => setMega({ ...mega, dateinsc: e.target.value })} disabled={readOnly} className="rounded-md" /></F>
                        </div>
                        <Separator />
                        <div>
                            <div className="overline mb-3">Langues</div>
                            <div className="grid grid-cols-2 gap-3">
                                <div className="flex items-center justify-between border border-slate-200 rounded-md px-3 py-2"><Label className="text-sm">Français</Label><Switch checked={!!mega.francais} onCheckedChange={(v) => setMega({ ...mega, francais: v })} disabled={readOnly} data-testid="mega-francais" /></div>
                                <div className="flex items-center justify-between border border-slate-200 rounded-md px-3 py-2"><Label className="text-sm">Anglais</Label><Switch checked={!!mega.anglais} onCheckedChange={(v) => setMega({ ...mega, anglais: v })} disabled={readOnly} data-testid="mega-anglais" /></div>
                            </div>
                            <div className="mt-3"><F label="Autres langues"><Input value={mega.autres || ""} onChange={(e) => setMega({ ...mega, autres: e.target.value })} disabled={readOnly} placeholder="Espagnol, italien…" className="rounded-md" /></F></div>
                        </div>
                        <Separator />
                        <div>
                            <div className="overline mb-3">Articles habilités</div>
                            <div className="grid grid-cols-3 gap-3">
                                {[{k:"art486",l:"Article 486"},{k:"art672",l:"Article 672"},{k:"art684",l:"Article 684"}].map((a) => (
                                    <div key={a.k} className="flex items-center justify-between border border-slate-200 rounded-md px-3 py-2"><Label className="text-sm">{a.l}</Label><Switch checked={!!mega[a.k]} onCheckedChange={(v) => setMega({ ...mega, [a.k]: v })} disabled={readOnly} data-testid={`mega-${a.k}`} /></div>
                                ))}
                            </div>
                        </div>
                        <Separator />
                        <div>
                            <div className="flex items-center justify-between mb-3">
                                <div className="overline">Districts habilités ({(mega.districts || []).length})</div>
                                <div className="flex items-center gap-2"><Label className="text-xs text-slate-600">Tous</Label><Switch checked={!!mega.tous_districts} onCheckedChange={(v) => setMega({ ...mega, tous_districts: v, districts: v ? QC_DISTRICTS.map((d) => d.id) : [] })} disabled={readOnly} data-testid="mega-tous-districts" /></div>
                            </div>
                            <div className="grid grid-cols-2 md:grid-cols-3 gap-2 max-h-56 overflow-y-auto border border-slate-200 rounded-md p-3">
                                {QC_DISTRICTS.map((d) => (
                                    <label key={d.id} className="flex items-center gap-2 text-sm cursor-pointer hover:bg-slate-50 rounded px-2 py-1">
                                        <input type="checkbox" checked={(mega.districts || []).includes(d.id)} onChange={() => toggleDistrict(d.id)} disabled={readOnly} data-testid={`mega-district-${d.id}`} />
                                        <span>{d.nom}</span>
                                    </label>
                                ))}
                            </div>
                        </div>
                        <Separator />
                        <F label="Détails"><Textarea value={mega.details || ""} onChange={(e) => setMega({ ...mega, details: e.target.value })} disabled={readOnly} rows={3} className="rounded-md" /></F>
                        <F label="Commentaire"><Textarea value={mega.commentaire || ""} onChange={(e) => setMega({ ...mega, commentaire: e.target.value })} disabled={readOnly} rows={3} className="rounded-md" /></F>
                        {!readOnly && (
                            <div className="flex justify-end pt-2">
                                <Button onClick={saveMega} disabled={megaSaving} className="bg-[#0033A0] hover:bg-[#002277] text-white rounded-md" data-testid="save-mega-btn">
                                    {megaSaving ? "Enregistrement…" : "Enregistrer le profil Méga"}
                                </Button>
                            </div>
                        )}
                    </TabsContent>

                    {/* WEB */}
                    <TabsContent value="web" className="mt-6 space-y-5">
                        <div className="text-sm text-slate-600">
                            Accès web de l'avocat (portail extranet) — équivalent du formulaire <code className="font-mono text-xs bg-slate-100 px-1 rounded">frmMotPasse</code> du VB.
                        </div>
                        <Separator />
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            <F label="Code usager">
                                <Input value={form.codeusager || ""} onChange={(e) => upd("codeusager", e.target.value)} disabled={readOnly} className="rounded-md font-mono" data-testid="web-codeusager" />
                            </F>
                            <F label="Ville référence">
                                <Input value={form.villerref || ""} onChange={(e) => upd("villerref", e.target.value)} disabled={readOnly} className="rounded-md" data-testid="web-villerref" />
                            </F>
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
                                <F label="Nouveau mot de passe (min 6 car.)">
                                    <Input type="password" value={form._webpwd || ""} onChange={(e) => upd("_webpwd", e.target.value)} disabled={readOnly} minLength={6} className="rounded-md" data-testid="web-password" />
                                </F>
                                {!readOnly && (
                                    <div className="flex gap-2">
                                        <Button
                                            onClick={async () => {
                                                if (!form._webpwd || form._webpwd.length < 6) { toast.error("Min 6 caractères"); return; }
                                                try {
                                                    await api.put(`/avocats/${avocat.id}/web-password`, { password: form._webpwd });
                                                    upd("_webpwd", "");
                                                    toast.success("Mot de passe web enregistré");
                                                } catch (err) { toast.error(formatApiError(err.response?.data?.detail) || "Erreur"); }
                                            }}
                                            className="bg-[#0033A0] hover:bg-[#002277] text-white rounded-md"
                                            data-testid="save-web-password"
                                        >
                                            Définir
                                        </Button>
                                        <Button
                                            variant="outline"
                                            onClick={async () => {
                                                if (!confirm("Réinitialiser le mot de passe web ?")) return;
                                                await api.delete(`/avocats/${avocat.id}/web-password`);
                                                toast.success("Mot de passe réinitialisé");
                                            }}
                                            className="rounded-md"
                                            data-testid="clear-web-password"
                                        >
                                            Effacer
                                        </Button>
                                    </div>
                                )}
                            </div>
                            <p className="text-xs text-slate-500 mt-2">Le mot de passe est stocké hashé (bcrypt) et n'est jamais affiché.</p>
                        </div>
                        {!readOnly && (
                            <div className="flex justify-end pt-2 border-t border-slate-200">
                                <Button onClick={handleSubmit} className="bg-[#0033A0] hover:bg-[#002277] text-white rounded-md" data-testid="save-web-tab">
                                    Enregistrer code usager + options
                                </Button>
                            </div>
                        )}
                    </TabsContent>
                </Tabs>
            </SheetContent>
        </Sheet>
    );
}
