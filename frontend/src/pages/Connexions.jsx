import { useEffect, useState } from "react";
import api, { formatApiError } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import { Textarea } from "@/components/ui/textarea";
import {
    Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle,
} from "@/components/ui/dialog";
import {
    Select, SelectContent, SelectItem, SelectTrigger, SelectValue,
} from "@/components/ui/select";
import {
    AlertDialog, AlertDialogAction, AlertDialogCancel, AlertDialogContent,
    AlertDialogDescription, AlertDialogFooter, AlertDialogHeader, AlertDialogTitle,
} from "@/components/ui/alert-dialog";
import { Database, Plus, Pencil, Trash2, CheckCircle2, XCircle, Lock, Server } from "lucide-react";
import { toast } from "sonner";

const TYPE_LABEL = { mongodb: "MongoDB", sqlserver: "SQL Server" };
const DEFAULT_PORT = { mongodb: 27017, sqlserver: 1433 };
const EMPTY = { name: "", type: "sqlserver", server: "", port: 1433, database: "", user: "", password: "", description: "" };

export default function Connexions() {
    const [items, setItems] = useState([]);
    const [loading, setLoading] = useState(true);
    const [editing, setEditing] = useState(null);
    const [testing, setTesting] = useState(false);
    const [testResult, setTestResult] = useState(null);
    const [confirmDelete, setConfirmDelete] = useState(null);

    const fetchAll = async () => {
        setLoading(true);
        try {
            const { data } = await api.get("/connexions");
            setItems(data);
        } catch (err) {
            toast.error(formatApiError(err.response?.data?.detail));
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => { fetchAll(); }, []);

    const openNew = () => {
        setEditing({ ...EMPTY });
        setTestResult(null);
    };
    const openEdit = (item) => {
        setEditing({ ...item, password: "" });
        setTestResult(null);
    };

    const upd = (k, v) => setEditing({ ...editing, [k]: v });

    const onTypeChange = (t) => {
        setEditing({ ...editing, type: t, port: DEFAULT_PORT[t] || null });
        setTestResult(null);
    };

    const handleTest = async () => {
        setTesting(true);
        setTestResult(null);
        try {
            // Si on édite et qu'aucun nouveau mot de passe n'est saisi, on teste l'entrée stockée
            if (editing?.id && !editing.password) {
                const { data } = await api.post(`/connexions/${editing.id}/test`);
                setTestResult(data);
            } else {
                const { data } = await api.post("/connexions/test", {
                    type: editing.type,
                    server: editing.server,
                    port: editing.port ? parseInt(editing.port, 10) : null,
                    user: editing.user,
                    password: editing.password,
                    database: editing.database,
                });
                setTestResult(data);
            }
        } catch (err) {
            setTestResult({ ok: false, message: formatApiError(err.response?.data?.detail) || "Erreur" });
        } finally {
            setTesting(false);
        }
    };

    const handleSave = async () => {
        if (!editing.name || !editing.server) {
            toast.error("Nom et serveur sont requis");
            return;
        }
        try {
            const payload = {
                name: editing.name,
                type: editing.type,
                server: editing.server,
                port: editing.port ? parseInt(editing.port, 10) : null,
                user: editing.user,
                database: editing.database,
                description: editing.description,
                ...(editing.password ? { password: editing.password } : {}),
            };
            if (editing.id) {
                await api.put(`/connexions/${editing.id}`, payload);
                toast.success("Connexion mise à jour");
            } else {
                await api.post("/connexions", payload);
                toast.success("Connexion créée");
            }
            setEditing(null);
            fetchAll();
        } catch (err) {
            toast.error(formatApiError(err.response?.data?.detail) || "Erreur");
        }
    };

    const handleDelete = async () => {
        try {
            await api.delete(`/connexions/${confirmDelete.id}`);
            toast.success("Connexion supprimée");
            setConfirmDelete(null);
            fetchAll();
        } catch (err) {
            toast.error(formatApiError(err.response?.data?.detail) || "Erreur");
        }
    };

    const isPrimary = !!editing?.is_primary;
    const restricted = editing?.id && isPrimary; // primaire : seule la description est éditable

    return (
        <div className="space-y-6" data-testid="connexions-page">
            <header className="flex items-center justify-between">
                <div>
                    <div className="overline mb-1">CONFIGURATION SYSTÈME</div>
                    <h1 className="font-display text-3xl tracking-tight text-slate-900">Connexions</h1>
                    <p className="text-sm text-slate-500 mt-1">
                        Gestion des bases de données et services externes utilisés par l'application.
                    </p>
                </div>
                <Button onClick={openNew} className="rounded-md bg-[#0033A0] hover:bg-[#002277] text-white" data-testid="add-connexion-btn">
                    <Plus size={14} className="mr-2" /> Nouvelle connexion
                </Button>
            </header>

            <div className="bg-white border border-slate-200 rounded-md divide-y divide-slate-100">
                {loading ? (
                    <div className="p-8 text-center text-sm text-slate-500">Chargement…</div>
                ) : items.length === 0 ? (
                    <div className="p-8 text-center text-sm text-slate-500">Aucune connexion.</div>
                ) : (
                    items.map((c) => (
                        <div key={c.id} className="p-4 flex items-start justify-between hover:bg-slate-50" data-testid={`connexion-row-${c.id}`}>
                            <div className="flex items-start gap-3 flex-1 min-w-0">
                                <div className={`h-9 w-9 rounded-md flex items-center justify-center shrink-0 ${c.type === "mongodb" ? "bg-emerald-100 text-emerald-700" : "bg-blue-100 text-blue-700"}`}>
                                    {c.type === "mongodb" ? <Database size={16} /> : <Server size={16} />}
                                </div>
                                <div className="flex-1 min-w-0">
                                    <div className="flex items-center gap-2 flex-wrap">
                                        <span className="font-medium text-slate-900">{c.name}</span>
                                        <Badge className="bg-slate-100 text-slate-700 hover:bg-slate-100 rounded-md text-[10px]">
                                            {TYPE_LABEL[c.type] || c.type}
                                        </Badge>
                                        {c.is_primary && (
                                            <Badge className="bg-amber-100 text-amber-800 hover:bg-amber-100 rounded-md text-[10px]" data-testid="primary-badge">
                                                <Lock size={10} className="mr-1" /> En service (lecture seule)
                                            </Badge>
                                        )}
                                        {c.has_password && (
                                            <Badge className="bg-slate-100 text-slate-500 hover:bg-slate-100 rounded-md text-[10px]">
                                                <Lock size={10} className="mr-1" /> Mot de passe configuré
                                            </Badge>
                                        )}
                                    </div>
                                    <div className="text-xs text-slate-500 mt-1 truncate font-mono">
                                        {c.server}{c.port ? `:${c.port}` : ""}{c.database ? ` / ${c.database}` : ""}
                                        {c.user ? ` • ${c.user}` : ""}
                                    </div>
                                    {c.description && <div className="text-xs text-slate-500 mt-1">{c.description}</div>}
                                </div>
                            </div>
                            <div className="flex items-center gap-1 shrink-0">
                                <Button variant="ghost" size="icon" onClick={() => openEdit(c)} data-testid={`edit-connexion-${c.id}`}>
                                    <Pencil size={14} />
                                </Button>
                                {!c.is_primary && (
                                    <Button variant="ghost" size="icon" className="text-red-600" onClick={() => setConfirmDelete(c)} data-testid={`delete-connexion-${c.id}`}>
                                        <Trash2 size={14} />
                                    </Button>
                                )}
                            </div>
                        </div>
                    ))
                )}
            </div>

            <Dialog open={editing !== null} onOpenChange={(o) => !o && setEditing(null)}>
                <DialogContent className="sm:max-w-2xl" data-testid="connexion-dialog">
                    <DialogHeader>
                        <DialogTitle>{editing?.id ? "Modifier la connexion" : "Nouvelle connexion"}</DialogTitle>
                        <DialogDescription>
                            {restricted
                                ? "Cette connexion est en service — seule la description est modifiable."
                                : "Les modifications sont stockées en BDD pour référence et n'affectent pas la connexion active de l'application."}
                        </DialogDescription>
                    </DialogHeader>
                    {editing && (
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                            <div className="space-y-1.5 md:col-span-2">
                                <Label className="text-xs font-medium text-slate-700">Nom</Label>
                                <Input value={editing.name} onChange={(e) => upd("name", e.target.value)} disabled={restricted} placeholder="Ex. Cardex production" className="rounded-md" data-testid="conn-name" />
                            </div>
                            <div className="space-y-1.5">
                                <Label className="text-xs font-medium text-slate-700">Type</Label>
                                <Select value={editing.type} onValueChange={onTypeChange} disabled={restricted || !!editing.id}>
                                    <SelectTrigger className="rounded-md" data-testid="conn-type"><SelectValue /></SelectTrigger>
                                    <SelectContent>
                                        <SelectItem value="sqlserver">SQL Server</SelectItem>
                                        <SelectItem value="mongodb">MongoDB</SelectItem>
                                    </SelectContent>
                                </Select>
                            </div>
                            <div className="space-y-1.5">
                                <Label className="text-xs font-medium text-slate-700">Serveur</Label>
                                <Input value={editing.server} onChange={(e) => upd("server", e.target.value)} disabled={restricted} placeholder="srv.exemple.local" className="rounded-md font-mono" data-testid="conn-server" />
                            </div>
                            <div className="space-y-1.5">
                                <Label className="text-xs font-medium text-slate-700">Port</Label>
                                <Input type="number" value={editing.port || ""} onChange={(e) => upd("port", e.target.value)} disabled={restricted} placeholder={String(DEFAULT_PORT[editing.type] || "")} className="rounded-md font-mono" data-testid="conn-port" />
                            </div>
                            <div className="space-y-1.5">
                                <Label className="text-xs font-medium text-slate-700">Base de données</Label>
                                <Input value={editing.database || ""} onChange={(e) => upd("database", e.target.value)} disabled={restricted} placeholder="Ex. sCardAvo" className="rounded-md font-mono" data-testid="conn-database" />
                            </div>
                            <div className="space-y-1.5">
                                <Label className="text-xs font-medium text-slate-700">Utilisateur</Label>
                                <Input value={editing.user || ""} onChange={(e) => upd("user", e.target.value)} disabled={restricted} placeholder="Ex. sa" className="rounded-md font-mono" data-testid="conn-user" />
                            </div>
                            <div className="space-y-1.5">
                                <Label className="text-xs font-medium text-slate-700">
                                    Mot de passe {editing.id && <span className="text-slate-400 font-normal">(laisser vide pour conserver)</span>}
                                </Label>
                                <Input type="password" value={editing.password || ""} onChange={(e) => upd("password", e.target.value)} disabled={restricted} placeholder={editing.id ? "••••••••" : ""} className="rounded-md" data-testid="conn-password" />
                            </div>
                            <div className="space-y-1.5 md:col-span-2">
                                <Label className="text-xs font-medium text-slate-700">Description</Label>
                                <Textarea value={editing.description || ""} onChange={(e) => upd("description", e.target.value)} rows={2} className="rounded-md" data-testid="conn-description" />
                            </div>
                            {testResult && (
                                <div className={`md:col-span-2 flex items-start gap-2 rounded-md px-3 py-2 text-sm ${testResult.ok ? "bg-emerald-50 text-emerald-800 border border-emerald-200" : "bg-red-50 text-red-800 border border-red-200"}`} data-testid="test-result">
                                    {testResult.ok ? <CheckCircle2 size={16} className="mt-0.5 shrink-0" /> : <XCircle size={16} className="mt-0.5 shrink-0" />}
                                    <span>{testResult.message}</span>
                                </div>
                            )}
                        </div>
                    )}
                    <DialogFooter className="gap-2">
                        <Button variant="outline" onClick={() => setEditing(null)} className="rounded-md" data-testid="conn-cancel">Annuler</Button>
                        <Button variant="outline" onClick={handleTest} disabled={testing || restricted || !editing?.server} className="rounded-md" data-testid="conn-test-btn">
                            {testing ? "Test en cours…" : "Tester la connexion"}
                        </Button>
                        <Button onClick={handleSave} className="rounded-md bg-[#0033A0] hover:bg-[#002277] text-white" data-testid="conn-save-btn">
                            Enregistrer
                        </Button>
                    </DialogFooter>
                </DialogContent>
            </Dialog>

            <AlertDialog open={confirmDelete !== null} onOpenChange={(o) => !o && setConfirmDelete(null)}>
                <AlertDialogContent>
                    <AlertDialogHeader>
                        <AlertDialogTitle>Supprimer la connexion ?</AlertDialogTitle>
                        <AlertDialogDescription>
                            La connexion <span className="font-semibold">{confirmDelete?.name}</span> sera définitivement retirée du catalogue.
                            Cette action n'affecte pas la connexion principale active.
                        </AlertDialogDescription>
                    </AlertDialogHeader>
                    <AlertDialogFooter>
                        <AlertDialogCancel data-testid="conn-confirm-no">Annuler</AlertDialogCancel>
                        <AlertDialogAction onClick={handleDelete} className="bg-red-600 hover:bg-red-700" data-testid="conn-confirm-yes">Supprimer</AlertDialogAction>
                    </AlertDialogFooter>
                </AlertDialogContent>
            </AlertDialog>
        </div>
    );
}
