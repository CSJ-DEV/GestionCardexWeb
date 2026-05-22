import { useEffect, useState } from "react";
import api from "@/lib/api";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Download } from "lucide-react";
import { toast } from "sonner";

const PAGE_SIZE = 20;

const ACTION_LABEL = {
    create: { label: "Création", className: "bg-green-100 text-green-800 hover:bg-green-100" },
    update: { label: "Modification", className: "bg-blue-100 text-blue-800 hover:bg-blue-100" },
    delete: { label: "Suppression", className: "bg-red-100 text-red-800 hover:bg-red-100" },
    adresse_create: { label: "Adresse +", className: "bg-emerald-100 text-emerald-800 hover:bg-emerald-100" },
    adresse_update: { label: "Adresse ✎", className: "bg-emerald-100 text-emerald-800 hover:bg-emerald-100" },
    adresse_delete: { label: "Adresse ✕", className: "bg-red-100 text-red-800 hover:bg-red-100" },
    mega_update: { label: "Méga", className: "bg-violet-100 text-violet-800 hover:bg-violet-100" },
    mega_delete: { label: "Méga ✕", className: "bg-red-100 text-red-800 hover:bg-red-100" },
    inhab_create: { label: "Inhab +", className: "bg-amber-100 text-amber-800 hover:bg-amber-100" },
    inhab_update: { label: "Inhab ✎", className: "bg-amber-100 text-amber-800 hover:bg-amber-100" },
    inhab_delete: { label: "Inhab ✕", className: "bg-red-100 text-red-800 hover:bg-red-100" },
    web_password_set: { label: "MdP web", className: "bg-slate-200 text-slate-800 hover:bg-slate-200" },
    web_password_clear: { label: "MdP web ✕", className: "bg-slate-200 text-slate-800 hover:bg-slate-200" },
    pwd_reset: { label: "MdP régénérés", className: "bg-blue-100 text-blue-800 hover:bg-blue-100" },
    pwd_clear: { label: "MdP effacés", className: "bg-slate-200 text-slate-800 hover:bg-slate-200" },
    pwd_view: { label: "MdP consultés (TI)", className: "bg-amber-100 text-amber-800 hover:bg-amber-100" },
};

const fmtDate = (iso) => {
    if (!iso) return "—";
    const d = new Date(iso);
    return d.toLocaleString("fr-CA", { dateStyle: "short", timeStyle: "short" });
};

export const HistoriqueTab = ({ avocatId }) => {
    const [items, setItems] = useState(null);
    const [total, setTotal] = useState(0);
    const [page, setPage] = useState(1);
    const [actionFilter, setActionFilter] = useState("all");
    const [exporting, setExporting] = useState(false);

    const handleExportCsv = async () => {
        if (!avocatId) return;
        setExporting(true);
        try {
            const params = actionFilter !== "all" ? { action: actionFilter } : {};
            const res = await api.get(`/avocats/${avocatId}/audit/export.csv`, {
                responseType: "blob",
                params,
            });
            const cd = res.headers["content-disposition"] || "";
            const m = cd.match(/filename="([^"]+)"/);
            const filename = m ? m[1] : `historique_${avocatId}.csv`;
            const url = window.URL.createObjectURL(new Blob([res.data], { type: "text/csv;charset=utf-8" }));
            const a = document.createElement("a");
            a.href = url;
            a.download = filename;
            document.body.appendChild(a);
            a.click();
            a.remove();
            window.URL.revokeObjectURL(url);
            toast.success("Historique exporté");
        } catch (err) {
            console.error("Export CSV failed:", err);
            toast.error("Export impossible");
        } finally {
            setExporting(false);
        }
    };

    useEffect(() => {
        if (!avocatId) {
            setItems([]);
            setTotal(0);
            return;
        }
        let cancelled = false;
        setItems(null);
        const params = { page, page_size: PAGE_SIZE };
        if (actionFilter !== "all") params.action = actionFilter;
        api.get(`/avocats/${avocatId}/audit`, { params })
            .then(({ data }) => {
                if (cancelled) return;
                const t = data.total || 0;
                setItems(data.items || []);
                setTotal(t);
                // Clamp si la page courante a été vidée (entrées supprimées entre temps)
                const tp = Math.max(1, Math.ceil(t / PAGE_SIZE));
                if (page > tp) setPage(tp);
            })
            .catch((err) => {
                if (cancelled) return;
                console.warn("Audit fetch failed:", err);
                setItems([]);
                setTotal(0);
            });
        return () => { cancelled = true; };
    }, [avocatId, page, actionFilter]);

    // Reset à la page 1 quand on change d'avocat ou de filtre
    useEffect(() => { setPage(1); }, [avocatId, actionFilter]);

    if (items === null) {
        return <div className="text-sm text-slate-500 py-6 text-center">Chargement…</div>;
    }

    const totalPages = Math.max(1, Math.ceil(total / PAGE_SIZE));

    return (
        <div className="space-y-3" data-testid="hist-list">
            <div className="flex flex-wrap items-center justify-between gap-2">
                <div className="flex items-center gap-2">
                    <Select value={actionFilter} onValueChange={setActionFilter}>
                        <SelectTrigger className="h-8 rounded-md text-xs w-48" data-testid="hist-filter-action">
                            <SelectValue placeholder="Toutes les actions" />
                        </SelectTrigger>
                        <SelectContent>
                            <SelectItem value="all">Toutes les actions</SelectItem>
                            {Object.entries(ACTION_LABEL).map(([k, v]) => (
                                <SelectItem key={k} value={k}>{v.label}</SelectItem>
                            ))}
                        </SelectContent>
                    </Select>
                    <p className="text-xs text-slate-500" data-testid="hist-count">
                        {total} entrée{total > 1 ? "s" : ""}
                        {actionFilter !== "all" && " (filtré)"}
                        {total > 0 && ` — page ${page} sur ${totalPages}`}
                    </p>
                </div>
                <Button
                    variant="outline"
                    size="sm"
                    onClick={handleExportCsv}
                    disabled={exporting || total === 0}
                    className="rounded-md h-7 text-xs"
                    data-testid="hist-export-csv"
                >
                    <Download size={12} className="mr-1.5" />
                    {exporting ? "Préparation…" : "Exporter CSV"}
                </Button>
            </div>

            {total === 0 ? (
                <div className="text-sm text-slate-500 text-center py-8 border border-dashed border-slate-300 rounded-md" data-testid="hist-empty">
                    {actionFilter === "all"
                        ? "Aucune modification enregistrée pour cette fiche."
                        : "Aucune entrée pour ce type d'action."}
                </div>
            ) : (<>
            <div className="border border-slate-200 rounded-md divide-y divide-slate-100 overflow-hidden">
                {items.map((it) => {
                    const meta = ACTION_LABEL[it.action] || { label: it.action, className: "bg-slate-100 text-slate-800" };
                    return (
                        <div key={it.id} className="flex items-start gap-3 px-3 py-2 hover:bg-slate-50" data-testid={`hist-row-${it.id}`}>
                            <Badge className={`${meta.className} rounded-md text-[10px] mt-0.5 shrink-0`}>{meta.label}</Badge>
                            <div className="flex-1 min-w-0">
                                <div className="text-sm text-slate-900 truncate">{it.summary || "—"}</div>
                                <div className="text-xs text-slate-500 mt-0.5">
                                    {fmtDate(it.timestamp)} • <span className="font-medium">{it.user_email || "système"}</span>
                                </div>
                            </div>
                        </div>
                    );
                })}
            </div>

            {totalPages > 1 && (
                <div className="flex items-center justify-between text-sm pt-1">
                    <Button
                        variant="outline"
                        size="sm"
                        disabled={page <= 1}
                        onClick={() => setPage((p) => Math.max(1, p - 1))}
                        data-testid="hist-prev"
                        className="rounded-md"
                    >
                        Précédent
                    </Button>
                    <span className="text-xs text-slate-500">Page {page} / {totalPages}</span>
                    <Button
                        variant="outline"
                        size="sm"
                        disabled={page >= totalPages}
                        onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
                        data-testid="hist-next"
                        className="rounded-md"
                    >
                        Suivant
                    </Button>
                </div>
            )}
            </>)}
        </div>
    );
};
