import { useEffect, useMemo, useState } from "react";
import { Navigate } from "react-router-dom";
import {
    Search, RotateCcw, RefreshCw, FileSearch, AlertTriangle, CheckCircle2,
    XCircle, HelpCircle, Loader2,
} from "lucide-react";
import { toast } from "sonner";
import api, { formatApiError } from "@/lib/api";
import { useAuth } from "@/context/AuthContext";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Checkbox } from "@/components/ui/checkbox";
import {
    Table, TableHeader, TableBody, TableRow, TableHead, TableCell,
} from "@/components/ui/table";
import {
    Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription, DialogFooter,
} from "@/components/ui/dialog";

/**
 * Page Mandats — TI uniquement.
 * Port du formulaire VB.NET frmMandat. Source : Themis (atattest + megaattest
 * requêtes séparées). Badge Web : présence dans Fvi (CSJ-WEB01).
 *
 * Fonctionnalités :
 *  - Indicateur visuel pendant la recherche (overlay + spinner sur bouton)
 *  - Sélection multiple via checkboxes + "Tout sélectionner"
 *  - Réinitialisation en lot avec confirmation par case à cocher (pas de retape)
 */
export default function Mandats() {
    const { user } = useAuth();

    // ---- Filtres ----
    const [mandat, setMandat] = useState("");
    const [codeAvocat, setCodeAvocat] = useState("");
    const [nomClient, setNomClient] = useState("");

    // ---- Données ----
    const [avocats, setAvocats] = useState([]);
    const [results, setResults] = useState([]);
    const [selectedKeys, setSelectedKeys] = useState(() => new Set());
    const [searching, setSearching] = useState(false);
    const [limited, setLimited] = useState(false);
    const [fviChecked, setFviChecked] = useState(false);

    // ---- Dialog Réinitialiser (batch) ----
    const [reinitOpen, setReinitOpen] = useState(false);
    const [reinitConfirmed, setReinitConfirmed] = useState(false);
    const [reiniting, setReiniting] = useState(false);

    // ---- Dialog Diagnostic ----
    const [diagOpen, setDiagOpen] = useState(false);
    const [diagData, setDiagData] = useState(null);
    const [diagLoading, setDiagLoading] = useState(false);

    useEffect(() => {
        api.get("/avocats?page=1&page_size=500")
            .then((res) => setAvocats(res.data?.items || []))
            .catch(() => setAvocats([]));
    }, []);

    // Lignes sélectionnées (objets MandatRow complets) — DOIT être avant tout early return
    const selectedRows = useMemo(
        () => results.filter((r) => selectedKeys.has(keyOf(r))),
        [results, selectedKeys],
    );

    if (user && user.role !== "ti") return <Navigate to="/" replace />;

    const allSelected = results.length > 0 && selectedKeys.size === results.length;
    const someSelected = selectedKeys.size > 0 && !allSelected;

    const toggleOne = (k) => {
        setSelectedKeys((prev) => {
            const next = new Set(prev);
            if (next.has(k)) next.delete(k);
            else next.add(k);
            return next;
        });
    };

    const toggleAll = () => {
        setSelectedKeys((prev) => {
            if (prev.size === results.length) return new Set();
            return new Set(results.map(keyOf));
        });
    };

    const onRecherche = async () => {
        setSearching(true);
        setSelectedKeys(new Set());
        try {
            const { data } = await api.post("/mandats/search", {
                mandat: mandat || null,
                code_avocat: codeAvocat || null,
                nom_client: nomClient || null,
            });
            setResults(data.items || []);
            setLimited(data.limited);
            setFviChecked(data.fvi_checked);

            // Erreurs SQL côté serveur (debug TI)
            const errs = data.errors || {};
            Object.entries(errs).forEach(([table, msg]) => {
                toast.error(
                    `Erreur SQL sur ${table} : ${String(msg).slice(0, 240)}`,
                    { duration: 15000 }
                );
            });

            if ((data.items || []).length === 0 && Object.keys(errs).length === 0) {
                toast.info("Aucun mandat trouvé");
            } else if (data.limited) {
                toast.warning(`Limite de 500 résultats atteinte — affinez votre recherche.`);
            }
        } catch (err) {
            toast.error(formatApiError(err.response?.data?.detail) || "Erreur de recherche");
        } finally {
            setSearching(false);
        }
    };

    const onEffacer = () => {
        setMandat("");
        setCodeAvocat("");
        setNomClient("");
        setResults([]);
        setSelectedKeys(new Set());
    };

    const onOpenReinit = () => {
        if (selectedKeys.size === 0) {
            toast.warning("Veuillez sélectionner au moins un mandat dans le tableau");
            return;
        }
        setReinitConfirmed(false);
        setReinitOpen(true);
    };

    const onConfirmReinit = async () => {
        if (!reinitConfirmed || selectedRows.length === 0) return;
        try {
            setReiniting(true);
            const { data } = await api.post("/mandats/reinit-batch", {
                items: selectedRows.map((r) => ({
                    source: r.source,
                    noreg: r.noreg,
                    nobur: r.nobur,
                    noref: r.noref,
                })),
                confirmed: true,
            });

            const msg = `${data.success_count} mandat(s) réinitialisé(s)`
                + (data.error_count > 0 ? `, ${data.error_count} en erreur` : "")
                + ". N'oubliez pas de lancer l'importation pour vider le trigger !";
            if (data.error_count === 0) {
                toast.success(msg, { duration: 12000 });
            } else {
                toast.warning(msg, { duration: 15000 });
                // Détail des erreurs en toasts séparés
                data.results.filter((r) => !r.ok).forEach((r) => {
                    toast.error(`${r.mandat} : ${r.error}`, { duration: 12000 });
                });
            }
            setReinitOpen(false);
            // On vide la sélection mais on garde les résultats pour audit visuel
            setSelectedKeys(new Set());
        } catch (err) {
            toast.error(formatApiError(err.response?.data?.detail) || "Erreur");
        } finally {
            setReiniting(false);
        }
    };

    const onDiagnostic = async () => {
        setDiagLoading(true);
        try {
            const { data } = await api.get("/mandats/diagnostic");
            setDiagData(data);
            setDiagOpen(true);
        } catch (err) {
            toast.error(formatApiError(err.response?.data?.detail) || "Erreur diagnostic");
        } finally {
            setDiagLoading(false);
        }
    };

    return (
        <div className="h-full flex flex-col gap-4 -m-6 md:-m-8 p-6 md:p-8" data-testid="mandats-page">
            {/* En-tête */}
            <div className="shrink-0">
                <div className="overline mb-2">Administration</div>
                <h1 className="font-display text-4xl font-bold tracking-tight text-slate-900">
                    Mandats
                </h1>
                <p className="text-sm text-slate-600 mt-1">
                    Recherche et gestion des mandats d'aide juridique (source : Themis).
                </p>
            </div>

            {/* Barre de filtres */}
            <div className="bg-slate-100 border border-slate-300 rounded-md p-4 shrink-0">
                <div className="flex items-end gap-4 flex-wrap">
                    <div className="flex flex-col">
                        <Label htmlFor="mandat" className="text-sm text-slate-700 mb-1">Mandat</Label>
                        <Input
                            id="mandat" value={mandat}
                            onChange={(e) => setMandat(e.target.value)}
                            onKeyDown={(e) => { if (e.key === "Enter") onRecherche(); }}
                            placeholder="02-15-12345678-99"
                            className="rounded-md h-9 w-56"
                            data-testid="mandat-input"
                            autoFocus
                            disabled={searching}
                        />
                        <span className="text-[10px] text-slate-500 mt-0.5">( Format RR-BB-NNNNNNNN-NN )</span>
                    </div>
                    <div className="flex flex-col">
                        <Label htmlFor="code-avocat" className="text-sm text-slate-700 mb-1">Code avocat</Label>
                        <Input
                            id="code-avocat"
                            list="avocats-codes-list"
                            value={codeAvocat}
                            onChange={(e) => setCodeAvocat(e.target.value.toUpperCase())}
                            onKeyDown={(e) => { if (e.key === "Enter") onRecherche(); }}
                            placeholder="ex: P00963"
                            className="rounded-md h-9 w-32 font-mono"
                            data-testid="code-avocat-input"
                            maxLength={10}
                            disabled={searching}
                        />
                        <datalist id="avocats-codes-list">
                            {avocats.map((a) => (
                                <option key={a.code} value={a.code}>
                                    {a.nom}, {a.prenom}
                                </option>
                            ))}
                        </datalist>
                        <span className="text-[10px] text-slate-500 mt-0.5">&nbsp;</span>
                    </div>
                    <div className="flex flex-col">
                        <Label htmlFor="nom-client" className="text-sm text-slate-700 mb-1">Nom client</Label>
                        <Input
                            id="nom-client" value={nomClient}
                            onChange={(e) => setNomClient(e.target.value)}
                            onKeyDown={(e) => { if (e.key === "Enter") onRecherche(); }}
                            className="rounded-md h-9 w-64"
                            data-testid="nom-client-input"
                            disabled={searching}
                        />
                        <span className="text-[10px] text-slate-500 mt-0.5">&nbsp;</span>
                    </div>

                    <div className="flex-1" />

                    <div className="flex items-start gap-2 pb-5">
                        <Button
                            type="button" variant="outline"
                            onClick={onRecherche} disabled={searching}
                            className="rounded-md h-12 px-5 border-2 border-[#0033A0]"
                            data-testid="mandat-search-btn"
                        >
                            {searching ? (
                                <Loader2 className="w-5 h-5 mr-2 animate-spin" />
                            ) : (
                                <Search className="w-5 h-5 mr-2" />
                            )}
                            {searching ? "Recherche en cours…" : "Recherche"}
                        </Button>
                        <Button
                            type="button" variant="outline"
                            onClick={onEffacer}
                            disabled={searching}
                            className="rounded-md h-12 px-5"
                            data-testid="mandat-clear-btn"
                        >
                            <RotateCcw className="w-5 h-5 mr-2 text-[#0033A0]" />
                            Effacer
                        </Button>
                        <Button
                            type="button" variant="outline"
                            onClick={onDiagnostic} disabled={diagLoading || searching}
                            className="rounded-md h-12 px-5"
                            data-testid="mandat-diag-btn"
                            title="Vérifier l'état des tables Themis/Fvi"
                        >
                            <FileSearch className="w-5 h-5 mr-2 text-amber-600" />
                            {diagLoading ? "..." : "Diagnostic"}
                        </Button>
                    </div>
                </div>
            </div>

            {/* Tableau résultats avec overlay loading */}
            <div className="bg-white border border-slate-400 rounded-md overflow-auto flex-1 min-h-0 relative">
                {searching && (
                    <div
                        className="absolute inset-0 bg-white/70 backdrop-blur-[1px] z-20 flex items-center justify-center"
                        data-testid="mandats-loading-overlay"
                    >
                        <div className="flex flex-col items-center gap-2 text-[#0033A0]">
                            <Loader2 className="w-10 h-10 animate-spin" />
                            <p className="text-sm font-medium">Recherche en cours dans Themis…</p>
                            <p className="text-xs text-slate-500">Cela peut prendre quelques secondes</p>
                        </div>
                    </div>
                )}
                <Table data-testid="mandats-table">
                    <TableHeader className="sticky top-0 bg-slate-50 z-10">
                        <TableRow className="bg-slate-50">
                            <TableHead className="h-9 py-1 w-[44px] text-center">
                                <Checkbox
                                    checked={allSelected || (someSelected ? "indeterminate" : false)}
                                    onCheckedChange={toggleAll}
                                    disabled={results.length === 0}
                                    aria-label="Tout sélectionner"
                                    data-testid="mandat-select-all"
                                />
                            </TableHead>
                            <TableHead className="h-9 py-1 text-center w-[70px]">Région</TableHead>
                            <TableHead className="h-9 py-1 text-center w-[70px]">Bureau</TableHead>
                            <TableHead className="h-9 py-1">Mandat</TableHead>
                            <TableHead className="h-9 py-1 text-center">Code avocat</TableHead>
                            <TableHead className="h-9 py-1 w-[200px]">Nom avocat</TableHead>
                            <TableHead className="h-9 py-1 text-center">Date émis</TableHead>
                            <TableHead className="h-9 py-1 text-center">Date rétro</TableHead>
                            <TableHead className="h-9 py-1 text-center w-[100px]">Conditionnel</TableHead>
                            <TableHead className="h-9 py-1 w-[150px]">Nom requérant</TableHead>
                            <TableHead className="h-9 py-1 w-[150px]">Prénom requérant</TableHead>
                            {fviChecked && (
                                <TableHead className="h-9 py-1 text-center w-[90px]">Web</TableHead>
                            )}
                        </TableRow>
                    </TableHeader>
                    <TableBody>
                        {results.length === 0 && !searching ? (
                            <TableRow>
                                <TableCell colSpan={fviChecked ? 12 : 11} className="text-center py-12 text-sm text-slate-400">
                                    <FileSearch className="w-10 h-10 mx-auto mb-2 text-slate-300" />
                                    Aucun résultat — utilisez les filtres ci-dessus pour rechercher
                                </TableCell>
                            </TableRow>
                        ) : (
                            results.map((m) => {
                                const k = keyOf(m);
                                const isChecked = selectedKeys.has(k);
                                return (
                                    <TableRow
                                        key={k}
                                        onClick={(e) => {
                                            // Ne pas toggle si on clique directement sur la checkbox
                                            if (e.target.closest("[data-checkbox-cell]")) return;
                                            toggleOne(k);
                                        }}
                                        className={`cursor-pointer [&>td]:py-1.5 ${isChecked ? "bg-blue-50" : "hover:bg-slate-50"}`}
                                        data-testid={`mandat-row-${k}`}
                                    >
                                        <TableCell className="text-center" data-checkbox-cell>
                                            <Checkbox
                                                checked={isChecked}
                                                onCheckedChange={() => toggleOne(k)}
                                                aria-label="Sélectionner ce mandat"
                                                data-testid={`mandat-check-${k}`}
                                            />
                                        </TableCell>
                                        <TableCell className="text-center font-mono text-xs">{m.noreg}</TableCell>
                                        <TableCell className="text-center font-mono text-xs">{m.nobur}</TableCell>
                                        <TableCell className="font-mono text-xs">
                                            {m.noref}
                                            {m.daj_manquant && (
                                                <span title="Référence absente de atattdaj/megaattdaj" className="ml-1 text-amber-600">
                                                    <AlertTriangle className="w-3 h-3 inline" />
                                                </span>
                                            )}
                                        </TableCell>
                                        <TableCell className="text-center font-mono text-xs">{m.code_avocat}</TableCell>
                                        <TableCell>{m.nom_avocat}</TableCell>
                                        <TableCell className="text-center text-xs">{fmtDate(m.date_emis)}</TableCell>
                                        <TableCell className="text-center text-xs">{fmtDate(m.date_retro)}</TableCell>
                                        <TableCell className="text-center">
                                            <span className={`inline-block w-6 ${m.conditionnel === "O" ? "text-orange-600 font-bold" : "text-slate-400"}`}>
                                                {m.conditionnel}
                                            </span>
                                        </TableCell>
                                        <TableCell>{m.nom_requerant}</TableCell>
                                        <TableCell>{m.prenom_requerant}</TableCell>
                                        {fviChecked && (
                                            <TableCell className="text-center">
                                                <WebBadge sur_web={m.sur_web} conditionnel={m.conditionnel} />
                                            </TableCell>
                                        )}
                                    </TableRow>
                                );
                            })
                        )}
                    </TableBody>
                </Table>
            </div>

            {/* Pied : compteur + bouton Réinitialiser */}
            <div className="flex items-center justify-between shrink-0">
                <div className="text-xs text-slate-500">
                    {results.length > 0 && (
                        <>
                            {results.length} mandat{results.length > 1 ? "s" : ""} trouvé{results.length > 1 ? "s" : ""}
                            {selectedKeys.size > 0 && (
                                <span className="ml-2 text-[#0033A0] font-semibold">
                                    — {selectedKeys.size} sélectionné{selectedKeys.size > 1 ? "s" : ""}
                                </span>
                            )}
                            {limited && <span className="text-amber-600 ml-2">(limité à 500)</span>}
                            {!fviChecked && results.length > 0 && (
                                <span className="text-slate-400 ml-2">— Fvi non disponible</span>
                            )}
                        </>
                    )}
                </div>
                <Button
                    type="button" variant="outline"
                    onClick={onOpenReinit}
                    disabled={selectedKeys.size === 0 || searching}
                    className="rounded-md h-12 px-5"
                    data-testid="mandat-reinit-btn"
                >
                    <RefreshCw className="w-5 h-5 mr-2 text-[#0033A0]" />
                    Réinitialiser{selectedKeys.size > 0 ? ` (${selectedKeys.size})` : ""}
                </Button>
            </div>

            {/* Dialog Réinitialiser (batch) */}
            <Dialog open={reinitOpen} onOpenChange={(open) => {
                if (!reiniting) setReinitOpen(open);
            }}>
                <DialogContent className="sm:max-w-2xl max-h-[85vh] flex flex-col" data-testid="reinit-dialog">
                    <DialogHeader>
                        <DialogTitle className="flex items-center gap-2">
                            <AlertTriangle className="w-5 h-5 text-amber-600" />
                            Réinitialiser {selectedRows.length} mandat{selectedRows.length > 1 ? "s" : ""}
                        </DialogTitle>
                        <DialogDescription>
                            Cette action exécutera un UPDATE dans la table <code>atattest</code>
                            {" "}(ou <code>megaattest</code>) pour armer le trigger de synchronisation.
                            <br />
                            <strong>N'oubliez pas de lancer l'importation</strong> après pour vider le trigger.
                        </DialogDescription>
                    </DialogHeader>

                    {/* Liste des mandats sélectionnés */}
                    <div className="flex-1 overflow-auto border border-slate-200 rounded-md my-2"
                         data-testid="reinit-list">
                        <table className="w-full text-xs">
                            <thead className="bg-slate-50 sticky top-0">
                                <tr>
                                    <th className="px-3 py-2 text-left font-medium text-slate-600">Source</th>
                                    <th className="px-3 py-2 text-left font-medium text-slate-600">Mandat</th>
                                    <th className="px-3 py-2 text-left font-medium text-slate-600">Avocat</th>
                                    <th className="px-3 py-2 text-left font-medium text-slate-600">Requérant</th>
                                </tr>
                            </thead>
                            <tbody>
                                {selectedRows.map((r) => (
                                    <tr key={keyOf(r)} className="border-t border-slate-100">
                                        <td className="px-3 py-1.5">
                                            <span className={`inline-block px-1.5 py-0.5 rounded text-[10px] font-mono ${
                                                r.source === "megaattest" ? "bg-purple-100 text-purple-700" : "bg-blue-100 text-blue-700"
                                            }`}>
                                                {r.source}
                                            </span>
                                        </td>
                                        <td className="px-3 py-1.5 font-mono">
                                            {r.noreg}-{r.nobur}-{r.noref}
                                        </td>
                                        <td className="px-3 py-1.5">
                                            <span className="font-mono">{r.code_avocat}</span>
                                            {r.nom_avocat && (
                                                <span className="text-slate-500 ml-1">— {r.nom_avocat}</span>
                                            )}
                                        </td>
                                        <td className="px-3 py-1.5">
                                            {[r.nom_requerant, r.prenom_requerant].filter(Boolean).join(", ")}
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>

                    {/* Case à cocher de confirmation */}
                    <div className="flex items-start gap-2 py-2 px-3 bg-amber-50 border border-amber-200 rounded-md">
                        <Checkbox
                            id="reinit-confirm-chk"
                            checked={reinitConfirmed}
                            onCheckedChange={(v) => setReinitConfirmed(!!v)}
                            data-testid="reinit-confirm-chk"
                            className="mt-0.5"
                        />
                        <label htmlFor="reinit-confirm-chk" className="text-sm text-slate-800 cursor-pointer select-none">
                            Je confirme la réinitialisation des {selectedRows.length} mandat{selectedRows.length > 1 ? "s" : ""} ci-dessus.
                        </label>
                    </div>

                    <DialogFooter className="gap-2 shrink-0">
                        <Button
                            type="button" variant="outline"
                            onClick={() => setReinitOpen(false)}
                            disabled={reiniting}
                            className="rounded-md"
                            data-testid="reinit-cancel-btn"
                        >
                            Annuler
                        </Button>
                        <Button
                            type="button"
                            onClick={onConfirmReinit}
                            disabled={reiniting || !reinitConfirmed}
                            className="rounded-md bg-red-600 hover:bg-red-700 text-white"
                            data-testid="reinit-confirm-btn"
                        >
                            {reiniting ? (
                                <><Loader2 className="w-4 h-4 mr-2 animate-spin" />Réinitialisation…</>
                            ) : (
                                `Réinitialiser ${selectedRows.length} mandat${selectedRows.length > 1 ? "s" : ""}`
                            )}
                        </Button>
                    </DialogFooter>
                </DialogContent>
            </Dialog>

            {/* Dialog Diagnostic Themis/Fvi (TI debug) */}
            <Dialog open={diagOpen} onOpenChange={setDiagOpen}>
                <DialogContent className="sm:max-w-3xl max-h-[80vh] overflow-auto" data-testid="diag-dialog">
                    <DialogHeader>
                        <DialogTitle className="flex items-center gap-2">
                            <FileSearch className="w-5 h-5 text-amber-600" />
                            Diagnostic Themis / Fvi
                        </DialogTitle>
                        <DialogDescription>
                            État des tables, comptes de lignes et exemples de données pour
                            aider à comprendre pourquoi une recherche ne renvoie rien.
                        </DialogDescription>
                    </DialogHeader>
                    {diagData ? (
                        <pre className="text-xs bg-slate-100 p-3 rounded overflow-auto max-h-[55vh]"
                             data-testid="diag-content">
{JSON.stringify(diagData, null, 2)}
                        </pre>
                    ) : (
                        <p className="text-sm text-slate-500">Chargement…</p>
                    )}
                    <DialogFooter>
                        <Button
                            type="button" variant="outline"
                            onClick={() => setDiagOpen(false)}
                            className="rounded-md"
                            data-testid="diag-close-btn"
                        >
                            Fermer
                        </Button>
                    </DialogFooter>
                </DialogContent>
            </Dialog>
        </div>
    );
}

function keyOf(row) {
    return `${row.source}|${row.noreg}|${row.nobur}|${row.noref}`;
}

function fmtDate(iso) {
    if (!iso) return "—";
    return iso.slice(0, 10);
}

function WebBadge({ sur_web, conditionnel }) {
    if (sur_web === undefined || sur_web === null) {
        return (
            <span title="Vérification impossible" className="inline-flex items-center gap-1 text-slate-400">
                <HelpCircle className="w-4 h-4" />
                <span className="text-[10px]">?</span>
            </span>
        );
    }
    if (sur_web) {
        return (
            <span title="Mandat présent dans Fvi" className="inline-flex items-center gap-1 text-green-600">
                <CheckCircle2 className="w-4 h-4" />
            </span>
        );
    }
    const cls = conditionnel === "O" ? "text-red-600" : "text-amber-600";
    const titre = conditionnel === "O"
        ? "Conditionnel mais ABSENT du Web — incohérence"
        : "Pas dans Fvi";
    return (
        <span title={titre} className={`inline-flex items-center gap-1 ${cls}`}>
            <XCircle className="w-4 h-4" />
        </span>
    );
}
