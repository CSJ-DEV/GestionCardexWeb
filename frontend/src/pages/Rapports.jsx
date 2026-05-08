import { useState, useEffect } from "react";
import api, { API, formatApiError } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { FileText, Download, Plus, Trash2 } from "lucide-react";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Sheet, SheetContent, SheetHeader, SheetTitle } from "@/components/ui/sheet";
import { toast } from "sonner";
import { useAuth } from "@/context/AuthContext";

export default function Rapports() {
    const { user } = useAuth();
    const canEdit = user?.role === "admin" || user?.role === "editeur";
    const today = new Date().toISOString().slice(0, 10);
    const [dateDebut, setDateDebut] = useState(today);
    const [dateFin, setDateFin] = useState(today);
    const [mandats, setMandats] = useState([]);
    const [avocats, setAvocats] = useState([]);
    const [editing, setEditing] = useState(null);
    const [form, setForm] = useState({ avocat_id: "", requerant: "", article: "486.3", date_ordonnance: today, date_emission: today, numero: "", groupe: "Pratique Privée" });

    const loadAvocats = async () => {
        const { data } = await api.get("/avocats?page_size=200");
        setAvocats(data.items || []);
    };
    const loadMandats = async () => {
        const { data } = await api.get("/mandats");
        setMandats(data || []);
    };
    useEffect(() => { loadAvocats(); loadMandats(); }, []);

    const downloadRegistre97 = () => {
        const url = `${API}/rapports/registre97?date_debut=${dateDebut}&date_fin=${dateFin}`;
        window.open(url, "_blank");
    };

    const submit = async (e) => {
        e.preventDefault();
        if (!form.avocat_id) { toast.error("Sélectionnez un avocat"); return; }
        try {
            if (editing?.id) await api.put(`/mandats/${editing.id}`, form);
            else await api.post("/mandats", form);
            toast.success("Mandat enregistré");
            setEditing(null);
            loadMandats();
        } catch (err) { toast.error(formatApiError(err.response?.data?.detail)); }
    };

    const remove = async (m) => {
        if (!confirm(`Supprimer le mandat ${m.numero} ?`)) return;
        try { await api.delete(`/mandats/${m.id}`); toast.success("Supprimé"); loadMandats(); }
        catch (err) { toast.error(formatApiError(err.response?.data?.detail)); }
    };

    const avoName = (id) => {
        const a = avocats.find((x) => x.id === id);
        return a ? `${a.nom}, ${a.prenom}` : "—";
    };

    return (
        <div className="space-y-6" data-testid="rapports-page">
            <div>
                <div className="overline mb-2">Production</div>
                <h1 className="font-display text-4xl font-bold tracking-tight text-slate-900">Rapports</h1>
                <p className="text-sm text-slate-600 mt-1">Génération des registres officiels (PDF) et gestion des mandats.</p>
            </div>

            {/* Generation Registre97 */}
            <div className="bg-white border border-slate-200 rounded-md p-6">
                <div className="flex items-center gap-2 mb-1"><FileText size={18} className="text-[#0033A0]" /><h2 className="font-display text-xl font-bold">Registre Article 97</h2></div>
                <p className="text-sm text-slate-600 mb-4">Registre tenu en vertu de l'article 97 du Règlement sur l'aide juridique.</p>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-3 items-end">
                    <div className="space-y-1.5"><Label className="text-xs">Date début</Label><Input type="date" value={dateDebut} onChange={(e) => setDateDebut(e.target.value)} className="rounded-md" data-testid="report-date-debut" /></div>
                    <div className="space-y-1.5"><Label className="text-xs">Date fin</Label><Input type="date" value={dateFin} onChange={(e) => setDateFin(e.target.value)} className="rounded-md" data-testid="report-date-fin" /></div>
                    <Button onClick={downloadRegistre97} className="bg-[#0033A0] hover:bg-[#002277] text-white rounded-md" data-testid="download-registre97">
                        <Download size={14} className="mr-2" /> Générer Registre97 (PDF)
                    </Button>
                </div>
                <div className="mt-4 grid grid-cols-2 md:grid-cols-5 gap-2">
                    <Button variant="outline" onClick={() => window.open(`${API}/rapports/registre98?date_debut=${dateDebut}&date_fin=${dateFin}`, "_blank")} className="rounded-md" data-testid="dl-registre98"><Download size={12} className="mr-1" /> Registre98</Button>
                    <Button variant="outline" onClick={() => window.open(`${API}/rapports/liste-det-bar`, "_blank")} className="rounded-md" data-testid="dl-detbar"><Download size={12} className="mr-1" /> Liste Bar.</Button>
                    <Button variant="outline" onClick={() => window.open(`${API}/rapports/liste-det-dist`, "_blank")} className="rounded-md" data-testid="dl-detdist"><Download size={12} className="mr-1" /> Liste Dist.</Button>
                    <Button variant="outline" onClick={() => window.open(`${API}/rapports/liste-det-reg`, "_blank")} className="rounded-md" data-testid="dl-detreg"><Download size={12} className="mr-1" /> Liste Reg.</Button>
                    <Button variant="outline" onClick={() => window.open(`${API}/rapports/liste-som`, "_blank")} className="rounded-md" data-testid="dl-listesom"><Download size={12} className="mr-1" /> Liste Som.</Button>
                </div>
            </div>

            {/* Mandats CRUD */}
            <div className="bg-white border border-slate-200 rounded-md">
                <div className="p-4 flex items-center justify-between border-b border-slate-200">
                    <div><div className="overline">Saisie</div><h3 className="font-display text-lg font-bold">Mandats ({mandats.length})</h3></div>
                    {canEdit && <Button onClick={() => { setEditing({}); setForm({ avocat_id: "", requerant: "", article: "486.3", date_ordonnance: today, date_emission: today, numero: "", groupe: "Pratique Privée" }); }} className="bg-[#0033A0] hover:bg-[#002277] text-white rounded-md" data-testid="add-mandat-btn"><Plus size={14} className="mr-2" /> Nouveau mandat</Button>}
                </div>
                <Table>
                    <TableHeader><TableRow className="bg-slate-50"><TableHead>Avocat</TableHead><TableHead>Requérant</TableHead><TableHead>Article</TableHead><TableHead>Date ord.</TableHead><TableHead>Mandat</TableHead><TableHead>Groupe</TableHead><TableHead className="text-right"></TableHead></TableRow></TableHeader>
                    <TableBody>
                        {mandats.length === 0 ? <TableRow><TableCell colSpan={7} className="text-center py-8 text-slate-500">Aucun mandat saisi.</TableCell></TableRow> :
                            mandats.map((m) => (
                                <TableRow key={m.id} data-testid={`mandat-row-${m.numero}`}>
                                    <TableCell className="font-medium">{avoName(m.avocat_id)}</TableCell>
                                    <TableCell>{m.requerant}</TableCell>
                                    <TableCell><span className="font-mono text-xs bg-blue-100 text-blue-800 rounded px-2 py-0.5">{m.article}</span></TableCell>
                                    <TableCell className="text-xs">{m.date_ordonnance}</TableCell>
                                    <TableCell className="font-mono text-xs">{m.numero}</TableCell>
                                    <TableCell className="text-xs">{m.groupe}</TableCell>
                                    <TableCell className="text-right">{canEdit && <Button variant="ghost" size="icon" className="text-red-600" onClick={() => remove(m)}><Trash2 size={14} /></Button>}</TableCell>
                                </TableRow>
                            ))}
                    </TableBody>
                </Table>
            </div>

            {/* Sheet form */}
            <Sheet open={!!editing} onOpenChange={(o) => !o && setEditing(null)}>
                <SheetContent>
                    <SheetHeader><SheetTitle className="font-display text-2xl">{editing?.id ? "Modifier mandat" : "Nouveau mandat"}</SheetTitle></SheetHeader>
                    <form onSubmit={submit} className="space-y-4 mt-6" data-testid="mandat-form">
                        <div className="space-y-1.5"><Label className="text-xs">Avocat</Label>
                            <Select value={form.avocat_id} onValueChange={(v) => setForm({ ...form, avocat_id: v })}>
                                <SelectTrigger className="rounded-md" data-testid="mandat-select-avocat"><SelectValue placeholder="Sélectionner…" /></SelectTrigger>
                                <SelectContent>{avocats.map((a) => <SelectItem key={a.id} value={a.id}>{a.code} — {a.nom}, {a.prenom}</SelectItem>)}</SelectContent>
                            </Select>
                        </div>
                        <div className="space-y-1.5"><Label className="text-xs">Nom du requérant</Label><Input value={form.requerant} onChange={(e) => setForm({ ...form, requerant: e.target.value })} required className="rounded-md" data-testid="mandat-requerant" /></div>
                        <div className="grid grid-cols-2 gap-3">
                            <div className="space-y-1.5"><Label className="text-xs">Article</Label>
                                <Select value={form.article} onValueChange={(v) => setForm({ ...form, article: v })}>
                                    <SelectTrigger className="rounded-md" data-testid="mandat-article"><SelectValue /></SelectTrigger>
                                    <SelectContent><SelectItem value="486.3">486.3 C.cr.</SelectItem><SelectItem value="486.7">486.7 C.cr.</SelectItem><SelectItem value="672">672 C.cr.</SelectItem><SelectItem value="684">684 C.cr.</SelectItem></SelectContent>
                                </Select>
                            </div>
                            <div className="space-y-1.5"><Label className="text-xs">Groupe</Label>
                                <Select value={form.groupe} onValueChange={(v) => setForm({ ...form, groupe: v })}>
                                    <SelectTrigger className="rounded-md"><SelectValue /></SelectTrigger>
                                    <SelectContent><SelectItem value="Pratique Privée">Pratique Privée</SelectItem><SelectItem value="Permanent">Permanent</SelectItem></SelectContent>
                                </Select>
                            </div>
                        </div>
                        <div className="grid grid-cols-2 gap-3">
                            <div className="space-y-1.5"><Label className="text-xs">Date ordonnance</Label><Input type="date" value={form.date_ordonnance} onChange={(e) => setForm({ ...form, date_ordonnance: e.target.value })} required className="rounded-md" /></div>
                            <div className="space-y-1.5"><Label className="text-xs">Date émission</Label><Input type="date" value={form.date_emission} onChange={(e) => setForm({ ...form, date_emission: e.target.value })} className="rounded-md" /></div>
                        </div>
                        <div className="space-y-1.5"><Label className="text-xs">Numéro mandat</Label><Input value={form.numero} onChange={(e) => setForm({ ...form, numero: e.target.value })} required className="rounded-md font-mono" data-testid="mandat-numero" /></div>
                        <div className="flex justify-end gap-2 pt-2">
                            <Button type="button" variant="outline" onClick={() => setEditing(null)}>Annuler</Button>
                            <Button type="submit" className="bg-[#0033A0] hover:bg-[#002277] text-white" data-testid="mandat-submit">Enregistrer</Button>
                        </div>
                    </form>
                </SheetContent>
            </Sheet>
        </div>
    );
}
