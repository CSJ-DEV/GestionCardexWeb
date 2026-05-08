import { useEffect, useState } from "react";
import api from "@/lib/api";
import { Badge } from "@/components/ui/badge";

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
};

const fmtDate = (iso) => {
    if (!iso) return "—";
    const d = new Date(iso);
    return d.toLocaleString("fr-CA", { dateStyle: "short", timeStyle: "short" });
};

export const HistoriqueTab = ({ avocatId }) => {
    const [items, setItems] = useState(null);

    useEffect(() => {
        if (!avocatId) {
            setItems([]);
            return;
        }
        let cancelled = false;
        api.get(`/avocats/${avocatId}/audit`)
            .then(({ data }) => { if (!cancelled) setItems(data || []); })
            .catch(() => { if (!cancelled) setItems([]); });
        return () => { cancelled = true; };
    }, [avocatId]);

    if (items === null) {
        return <div className="text-sm text-slate-500 py-6 text-center">Chargement…</div>;
    }
    if (items.length === 0) {
        return (
            <div className="text-sm text-slate-500 text-center py-8 border border-dashed border-slate-300 rounded-md" data-testid="hist-empty">
                Aucune modification enregistrée pour cette fiche.
            </div>
        );
    }

    return (
        <div className="space-y-2" data-testid="hist-list">
            <p className="text-xs text-slate-500">
                {items.length} entrée{items.length > 1 ? "s" : ""} — du plus récent au plus ancien.
            </p>
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
        </div>
    );
};
