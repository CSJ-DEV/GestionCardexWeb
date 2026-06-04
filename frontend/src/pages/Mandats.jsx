import { useEffect, useState } from "react";
import { Navigate } from "react-router-dom";
import {
    Search, RotateCcw, RefreshCw, FileSearch, AlertTriangle, CheckCircle2, XCircle, HelpCircle,
} from "lucide-react";
import { toast } from "sonner";
import api, { formatApiError } from "@/lib/api";
import { useAuth } from "@/context/AuthContext";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
    Table, TableHeader, TableBody, TableRow, TableHead, TableCell,
} from "@/components/ui/table";
import {
    Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription, DialogFooter,
} from "@/components/ui/dialog";

/**
 * Page Mandats — TI uniquement.
 * Port du formulaire VB.NET frmMandat. Source : Themis (atattest + megaattest
 * via UNION ALL). Badge Web : présence dans Fvi (CSJ-WEB01).
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
    const [selectedKey, setSelectedKey] = useState("");
    const [searching, setSearching] = useState(false);
    const [limited, setLimited] = useState(false);
    const [fviChecked, setFviChecked] = useState(false);

    // ---- Dialog Réinitialiser ----
    const [reinitOpen, setReinitOpen] = useState(false);
    const [reinitCode, setReinitCode] = useState("");
    const [reiniting, setReiniting] = useState(false);

    useEffect(() => {
        api.get("/avocats?page=1&page_size=500")
            .then((res) => setAvocats(res.data?.items || []))
            .catch(() => setAvocats([]));
    }, []);

    if (user && user.role !== "ti") return <Navigate to="/" replace />;

    const onRecherche = async () => {
        setSearching(true);
        try {
            const { data } = await api.post("/mandats/search", {
                mandat: mandat || null,
                code_avocat: codeAvocat || null,
                nom_client: nomClient || null,
            });
            setResults(data.items || []);
            setLimited(data.limited);
            setFviChecked(data.fvi_checked);
            setSelectedKey("");
            if ((data.items || []).length === 0) {
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
        setSelectedKey("");
    };

    const onOpenReinit = () => {
        if (!selectedKey) {
            toast.warning("Veuillez sélectionner un mandat dans le tableau");
            return;
        }
        setReinitCode("");
        setReinitOpen(true);
    };

    const onConfirmReinit = async () => {
        const sel = results.find((r) => keyOf(r) === selectedKey);
        if (!sel) return;
        try {
            setReiniting(true);
            const { data } = await api.post("/mandats/reinit", {
                noreg: sel.noreg,
                nobur: sel.nobur,
                noref: sel.noref,
                confirmation_code: reinitCode.trim(),
            });
            toast.success(data.message, { duration: 12000 });
            setReinitOpen(false);
            onEffacer();
        } catch (err) {
            toast.error(formatApiError(err.response?.data?.detail) || "Erreur");
        } finally {
            setReiniting(false);
        }
    };

    const selectedRow = results.find((r) => keyOf(r) === selectedKey);
    const expectedCode = selectedRow
        ? `${selectedRow.noreg}-${selectedRow.nobur}-${selectedRow.noref}`
        : "";

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
                            <Search className="w-5 h-5 mr-2" />
                            {searching ? "Recherche..." : "Recherche"}
                        </Button>
                        <Button
                            type="button" variant="outline"
                            onClick={onEffacer}
                            className="rounded-md h-12 px-5"
                            data-testid="mandat-clear-btn"
                        >
                            <RotateCcw className="w-5 h-5 mr-2 text-[#0033A0]" />
                            Effacer
                        </Button>
                    </div>
                </div>
            </div>

            {/* Tableau résultats */}
            <div className="bg-white border border-slate-400 rounded-md overflow-auto flex-1 min-h-0">
                <Table data-testid="mandats-table">
                    <TableHeader className="sticky top-0 bg-slate-50 z-10">
                        <TableRow className="bg-slate-50">
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
                        {results.length === 0 ? (
                            <TableRow>
                                <TableCell colSpan={fviChecked ? 11 : 10} className="text-center py-12 text-sm text-slate-400">
                                    <FileSearch className="w-10 h-10 mx-auto mb-2 text-slate-300" />
                                    Aucun résultat — utilisez les filtres ci-dessus pour rechercher
                                </TableCell>
                            </TableRow>
                        ) : (
                            results.map((m) => {
                                const k = keyOf(m);
                                return (
                                    <TableRow
                                        key={k}
                                        onClick={() => setSelectedKey(k)}
                                        className={`cursor-pointer [&>td]:py-1.5 ${selectedKey === k ? "bg-blue-50" : "hover:bg-slate-50"}`}
                                        data-testid={`mandat-row-${k}`}
                                    >
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
                    disabled={!selectedKey}
                    className="rounded-md h-12 px-5"
                    data-testid="mandat-reinit-btn"
                >
                    <RefreshCw className="w-5 h-5 mr-2 text-[#0033A0]" />
                    Réinitialiser
                </Button>
            </div>

            {/* Dialog Réinitialiser */}
            <Dialog open={reinitOpen} onOpenChange={setReinitOpen}>
                <DialogContent className="sm:max-w-md" data-testid="reinit-dialog">
                    <DialogHeader>
                        <DialogTitle className="flex items-center gap-2">
                            <AlertTriangle className="w-5 h-5 text-amber-600" />
                            Réinitialiser le mandat
                        </DialogTitle>
                        <DialogDescription>
                            Cette action exécutera un UPDATE dans la table <code>atattest</code> pour
                            armer le trigger de synchronisation. <strong>N'oubliez pas de lancer
                            l'importation</strong> après pour vider le trigger.
                        </DialogDescription>
                    </DialogHeader>
                    <div className="py-3 space-y-3">
                        <p className="text-sm text-slate-700">
                            Pour confirmer, saisissez le code mandat complet ci-dessous :
                        </p>
                        <code className="block bg-slate-100 px-3 py-2 rounded font-mono text-sm">
                            {expectedCode}
                        </code>
                        <Input
                            value={reinitCode}
                            onChange={(e) => setReinitCode(e.target.value)}
                            placeholder="Recopiez le code ci-dessus"
                            className="font-mono"
                            data-testid="reinit-confirm-input"
                            autoFocus
                        />
                    </div>
                    <DialogFooter className="gap-2">
                        <Button
                            type="button" variant="outline"
                            onClick={() => setReinitOpen(false)}
                            className="rounded-md"
                            data-testid="reinit-cancel-btn"
                        >
                            Annuler
                        </Button>
                        <Button
                            type="button"
                            onClick={onConfirmReinit}
                            disabled={reiniting || reinitCode.trim() !== expectedCode}
                            className="rounded-md bg-red-600 hover:bg-red-700 text-white"
                            data-testid="reinit-confirm-btn"
                        >
                            {reiniting ? "Réinitialisation..." : "Réinitialiser"}
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
    // Pas sur le Web
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
