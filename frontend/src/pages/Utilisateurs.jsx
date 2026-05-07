import { useEffect, useState } from "react";
import api, { formatApiError } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Sheet, SheetContent, SheetHeader, SheetTitle } from "@/components/ui/sheet";
import { Badge } from "@/components/ui/badge";
import { Plus, Pencil, Trash2 } from "lucide-react";
import { toast } from "sonner";
import { useAuth } from "@/context/AuthContext";

const empty = { email: "", name: "", password: "", role: "editeur" };
const roleLabel = { admin: "Administrateur", editeur: "Éditeur", lecteur: "Lecteur" };
const roleBadge = { admin: "bg-violet-100 text-violet-700", editeur: "bg-blue-100 text-blue-700", lecteur: "bg-slate-100 text-slate-700" };

export default function Utilisateurs() {
    const { user: me } = useAuth();
    const [users, setUsers] = useState([]);
    const [loading, setLoading] = useState(true);
    const [editing, setEditing] = useState(null);
    const [form, setForm] = useState(empty);

    const load = async () => {
        setLoading(true);
        try {
            const { data } = await api.get("/users");
            setUsers(data);
        } catch (e) {
            toast.error(formatApiError(e.response?.data?.detail));
        } finally { setLoading(false); }
    };

    useEffect(() => { load(); }, []);

    const openNew = () => { setEditing({}); setForm(empty); };
    const openEdit = (u) => { setEditing(u); setForm({ email: u.email, name: u.name, password: "", role: u.role }); };

    const submit = async (e) => {
        e.preventDefault();
        try {
            if (editing?.id) {
                const { email: _e, ...payload } = form;
                if (!payload.password) delete payload.password;
                await api.put(`/users/${editing.id}`, payload);
                toast.success("Utilisateur mis à jour");
            } else {
                await api.post("/users", form);
                toast.success("Utilisateur créé");
            }
            setEditing(null);
            load();
        } catch (err) {
            toast.error(formatApiError(err.response?.data?.detail));
        }
    };

    const remove = async (u) => {
        if (!confirm(`Supprimer ${u.name} ?`)) return;
        try {
            await api.delete(`/users/${u.id}`);
            toast.success("Utilisateur supprimé");
            load();
        } catch (err) {
            toast.error(formatApiError(err.response?.data?.detail));
        }
    };

    return (
        <div className="space-y-6" data-testid="utilisateurs-page">
            <div className="flex items-end justify-between">
                <div>
                    <div className="overline mb-2">Sécurité</div>
                    <h1 className="font-display text-4xl font-bold tracking-tight text-slate-900">Utilisateurs</h1>
                    <p className="text-sm text-slate-600 mt-1">{users.length} compte(s) — gestion des accès et rôles.</p>
                </div>
                <Button onClick={openNew} className="rounded-md bg-[#0033A0] hover:bg-[#002277] text-white" data-testid="add-user-btn">
                    <Plus size={16} className="mr-2" /> Nouvel utilisateur
                </Button>
            </div>

            <div className="bg-white border border-slate-200 rounded-md overflow-hidden">
                <Table>
                    <TableHeader>
                        <TableRow className="bg-slate-50">
                            <TableHead>Nom</TableHead>
                            <TableHead>Courriel</TableHead>
                            <TableHead>Rôle</TableHead>
                            <TableHead className="text-right">Actions</TableHead>
                        </TableRow>
                    </TableHeader>
                    <TableBody>
                        {loading ? <TableRow><TableCell colSpan={4} className="text-center py-8 text-slate-500">Chargement…</TableCell></TableRow> :
                            users.map((u) => (
                                <TableRow key={u.id} data-testid={`user-row-${u.email}`}>
                                    <TableCell className="font-medium">{u.name}</TableCell>
                                    <TableCell className="font-mono text-xs">{u.email}</TableCell>
                                    <TableCell><Badge className={`${roleBadge[u.role]} hover:${roleBadge[u.role]} rounded-md`}>{roleLabel[u.role]}</Badge></TableCell>
                                    <TableCell className="text-right">
                                        <Button variant="ghost" size="icon" onClick={() => openEdit(u)}><Pencil size={14} /></Button>
                                        {u.id !== me?.id && <Button variant="ghost" size="icon" className="text-red-600" onClick={() => remove(u)}><Trash2 size={14} /></Button>}
                                    </TableCell>
                                </TableRow>
                            ))}
                    </TableBody>
                </Table>
            </div>

            <Sheet open={!!editing} onOpenChange={(o) => !o && setEditing(null)}>
                <SheetContent>
                    <SheetHeader>
                        <SheetTitle className="font-display text-2xl">{editing?.id ? "Modifier l'utilisateur" : "Nouvel utilisateur"}</SheetTitle>
                    </SheetHeader>
                    <form onSubmit={submit} className="space-y-4 mt-6" data-testid="user-form">
                        <div className="space-y-1.5">
                            <Label className="text-xs">Courriel</Label>
                            <Input type="email" value={form.email} disabled={!!editing?.id} onChange={(e) => setForm({ ...form, email: e.target.value })} required className="rounded-md" data-testid="user-input-email" />
                        </div>
                        <div className="space-y-1.5">
                            <Label className="text-xs">Nom</Label>
                            <Input value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} required className="rounded-md" data-testid="user-input-name" />
                        </div>
                        <div className="space-y-1.5">
                            <Label className="text-xs">{editing?.id ? "Nouveau mot de passe (laisser vide pour conserver)" : "Mot de passe"}</Label>
                            <Input type="password" value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })} required={!editing?.id} minLength={6} className="rounded-md" data-testid="user-input-password" />
                        </div>
                        <div className="space-y-1.5">
                            <Label className="text-xs">Rôle</Label>
                            <Select value={form.role} onValueChange={(v) => setForm({ ...form, role: v })}>
                                <SelectTrigger className="rounded-md" data-testid="user-select-role"><SelectValue /></SelectTrigger>
                                <SelectContent>
                                    <SelectItem value="admin">Administrateur</SelectItem>
                                    <SelectItem value="editeur">Éditeur</SelectItem>
                                    <SelectItem value="lecteur">Lecteur (lecture seule)</SelectItem>
                                </SelectContent>
                            </Select>
                        </div>
                        <div className="flex justify-end gap-2 pt-2">
                            <Button type="button" variant="outline" onClick={() => setEditing(null)}>Annuler</Button>
                            <Button type="submit" className="bg-[#0033A0] hover:bg-[#002277] text-white" data-testid="user-submit">Enregistrer</Button>
                        </div>
                    </form>
                </SheetContent>
            </Sheet>
        </div>
    );
}
