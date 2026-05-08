import { useEffect, useState, useCallback } from "react";
import { Plus, Search, Pencil, Trash2 } from "lucide-react";
import api, { formatApiError } from "@/lib/api";
import { useAuth } from "@/context/AuthContext";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from "@/components/ui/select";
import { Badge } from "@/components/ui/badge";
import {
    Table,
    TableBody,
    TableCell,
    TableHead,
    TableHeader,
    TableRow,
} from "@/components/ui/table";
import {
    AlertDialog,
    AlertDialogAction,
    AlertDialogCancel,
    AlertDialogContent,
    AlertDialogDescription,
    AlertDialogFooter,
    AlertDialogHeader,
    AlertDialogTitle,
} from "@/components/ui/alert-dialog";
import { toast } from "sonner";
import AvocatSheet from "@/components/AvocatSheet";

const PAGE_SIZE = 25;

export default function AvocatsList() {
    const { user } = useAuth();
    const canEdit = user?.role === "admin" || user?.role === "editeur";
    const isAdmin = user?.role === "admin";
    const [items, setItems] = useState([]);
    const [total, setTotal] = useState(0);
    const [page, setPage] = useState(1);
    const [loading, setLoading] = useState(true);
    const [q, setQ] = useState("");
    const [statut, setStatut] = useState("all");
    const [editing, setEditing] = useState(null); // null = closed, {} = creating, {...avocat} = editing
    const [deleting, setDeleting] = useState(null);

    const fetchData = useCallback(async () => {
        setLoading(true);
        try {
            const params = { page, page_size: PAGE_SIZE };
            if (q.trim()) params.q = q.trim();
            if (statut !== "all") params.statut = statut;
            const { data } = await api.get("/avocats", { params });
            setItems(data.items);
            setTotal(data.total);
        } catch (e) {
            toast.error(formatApiError(e.response?.data?.detail) || "Erreur de chargement");
        } finally {
            setLoading(false);
        }
    }, [page, q, statut]);

    useEffect(() => {
        const id = setTimeout(fetchData, 300);
        return () => clearTimeout(id);
    }, [fetchData]);

    // close=true → ferme le Sheet (annulation, ou choix explicite)
    // updatedAvocat fourni → garde le Sheet ouvert, mais bascule sur la fiche persistée (utile après création)
    // sinon → garde le Sheet ouvert tel quel et rafraîchit la liste en arrière-plan
    const handleSaved = ({ close = false, updatedAvocat = null } = {}) => {
        fetchData();
        if (close) {
            setEditing(null);
        } else if (updatedAvocat) {
            setEditing(updatedAvocat);
        }
    };

    const handleDelete = async () => {
        if (!deleting) return;
        try {
            await api.delete(`/avocats/${deleting.id}`);
            toast.success("Avocat supprimé");
            setDeleting(null);
            fetchData();
        } catch (e) {
            toast.error(formatApiError(e.response?.data?.detail) || "Erreur de suppression");
        }
    };

    const totalPages = Math.max(1, Math.ceil(total / PAGE_SIZE));

    return (
        <div className="space-y-6" data-testid="avocats-page">
            <div className="flex items-end justify-between gap-4 flex-wrap">
                <div>
                    <div className="overline mb-2">Répertoire</div>
                    <h1 className="font-display text-4xl font-bold tracking-tight text-slate-900">
                        Avocats
                    </h1>
                    <p className="text-sm text-slate-600 mt-1">
                        {total} {total > 1 ? "fiches" : "fiche"} • Gérer le registre central des avocats.
                    </p>
                </div>
                {canEdit && (
                    <Button
                        onClick={() => setEditing({})}
                        className="rounded-md bg-[#0033A0] hover:bg-[#002277] text-white"
                        data-testid="add-avocat-button"
                    >
                        <Plus size={16} className="mr-2" /> Nouvel avocat
                    </Button>
                )}
            </div>

            {/* Filters */}
            <div className="bg-white border border-slate-200 rounded-md p-4 flex items-center gap-3 flex-wrap">
                <div className="relative flex-1 min-w-[240px]">
                    <Search
                        size={14}
                        className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400"
                    />
                    <Input
                        value={q}
                        onChange={(e) => {
                            setPage(1);
                            setQ(e.target.value);
                        }}
                        placeholder="Recherche par code, nom ou prénom…"
                        className="pl-9 h-10 rounded-md"
                        data-testid="avocat-search-input"
                    />
                </div>
                <Select
                    value={statut}
                    onValueChange={(v) => {
                        setPage(1);
                        setStatut(v);
                    }}
                >
                    <SelectTrigger className="w-[180px] h-10 rounded-md" data-testid="avocat-status-filter">
                        <SelectValue placeholder="Statut" />
                    </SelectTrigger>
                    <SelectContent>
                        <SelectItem value="all">Tous les statuts</SelectItem>
                        <SelectItem value="actif">Actifs</SelectItem>
                        <SelectItem value="inactif">Inactifs</SelectItem>
                    </SelectContent>
                </Select>
            </div>

            {/* Table */}
            <div className="bg-white border border-slate-200 rounded-md overflow-hidden">
                <Table data-testid="avocats-table">
                    <TableHeader>
                        <TableRow className="bg-slate-50">
                            <TableHead className="w-[100px]">Code</TableHead>
                            <TableHead>Nom</TableHead>
                            <TableHead>Prénom</TableHead>
                            <TableHead>Section barreau</TableHead>
                            <TableHead>Ville</TableHead>
                            <TableHead>Statut</TableHead>
                            <TableHead className="text-right">Actions</TableHead>
                        </TableRow>
                    </TableHeader>
                    <TableBody>
                        {loading ? (
                            Array.from({ length: 6 }).map((_, i) => (
                                <TableRow key={i}>
                                    {Array.from({ length: 7 }).map((_, j) => (
                                        <TableCell key={j}>
                                            <div className="h-4 bg-slate-100 rounded animate-pulse" />
                                        </TableCell>
                                    ))}
                                </TableRow>
                            ))
                        ) : items.length === 0 ? (
                            <TableRow>
                                <TableCell colSpan={7} className="text-center py-12 text-slate-500">
                                    Aucun avocat trouvé.
                                </TableCell>
                            </TableRow>
                        ) : (
                            items.map((a) => (
                                <TableRow
                                    key={a.id}
                                    className="hover:bg-slate-50 cursor-pointer"
                                    onClick={() => setEditing(a)}
                                    data-testid={`avocat-row-${a.code}`}
                                >
                                    <TableCell className="font-mono text-xs text-slate-700">
                                        {a.code}
                                    </TableCell>
                                    <TableCell className="font-medium text-slate-900">{a.nom}</TableCell>
                                    <TableCell>{a.prenom}</TableCell>
                                    <TableCell className="text-slate-600">{a.sectbar || "—"}</TableCell>
                                    <TableCell className="text-slate-600">
                                        {a.adresse?.ville || "—"}
                                    </TableCell>
                                    <TableCell>
                                        {a.actif ? (
                                            <Badge className="bg-green-100 text-green-700 hover:bg-green-100 rounded-md font-medium">
                                                Actif
                                            </Badge>
                                        ) : (
                                            <Badge className="bg-red-100 text-red-700 hover:bg-red-100 rounded-md font-medium">
                                                Inactif
                                            </Badge>
                                        )}
                                        {a.mega && (
                                            <Badge className="ml-1 bg-violet-100 text-violet-700 hover:bg-violet-100 rounded-md font-medium">
                                                Méga
                                            </Badge>
                                        )}
                                    </TableCell>
                                    <TableCell
                                        className="text-right space-x-1"
                                        onClick={(e) => e.stopPropagation()}
                                    >
                                        {canEdit && (
                                            <Button
                                                variant="ghost"
                                                size="icon"
                                                onClick={() => setEditing(a)}
                                                data-testid={`edit-avocat-${a.code}`}
                                            >
                                                <Pencil size={14} />
                                            </Button>
                                        )}
                                        {isAdmin && (
                                            <Button
                                                variant="ghost"
                                                size="icon"
                                                className="text-red-600 hover:text-red-700"
                                                onClick={() => setDeleting(a)}
                                                data-testid={`delete-avocat-${a.code}`}
                                            >
                                                <Trash2 size={14} />
                                            </Button>
                                        )}
                                    </TableCell>
                                </TableRow>
                            ))
                        )}
                    </TableBody>
                </Table>
            </div>

            {/* Pagination */}
            <div className="flex items-center justify-between text-sm">
                <div className="text-slate-500">
                    Page {page} sur {totalPages}
                </div>
                <div className="flex gap-2">
                    <Button
                        variant="outline"
                        size="sm"
                        disabled={page <= 1}
                        onClick={() => setPage((p) => p - 1)}
                        data-testid="pagination-prev"
                        className="rounded-md"
                    >
                        Précédent
                    </Button>
                    <Button
                        variant="outline"
                        size="sm"
                        disabled={page >= totalPages}
                        onClick={() => setPage((p) => p + 1)}
                        data-testid="pagination-next"
                        className="rounded-md"
                    >
                        Suivant
                    </Button>
                </div>
            </div>

            <AvocatSheet
                open={editing !== null}
                onOpenChange={(open) => !open && setEditing(null)}
                avocat={editing}
                onSaved={handleSaved}
            />

            <AlertDialog open={!!deleting} onOpenChange={(open) => !open && setDeleting(null)}>
                <AlertDialogContent data-testid="delete-confirm-dialog">
                    <AlertDialogHeader>
                        <AlertDialogTitle>Supprimer cet avocat ?</AlertDialogTitle>
                        <AlertDialogDescription>
                            Cette action est irréversible. La fiche de{" "}
                            <strong>
                                {deleting?.prenom} {deleting?.nom}
                            </strong>{" "}
                            sera supprimée.
                        </AlertDialogDescription>
                    </AlertDialogHeader>
                    <AlertDialogFooter>
                        <AlertDialogCancel data-testid="delete-cancel">Annuler</AlertDialogCancel>
                        <AlertDialogAction
                            onClick={handleDelete}
                            className="bg-red-600 hover:bg-red-700"
                            data-testid="delete-confirm"
                        >
                            Supprimer
                        </AlertDialogAction>
                    </AlertDialogFooter>
                </AlertDialogContent>
            </AlertDialog>
        </div>
    );
}
