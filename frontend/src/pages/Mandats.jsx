import { useEffect, useState } from "react";
import { Navigate } from "react-router-dom";
import { Search, RotateCcw, RefreshCw, FileSearch } from "lucide-react";
import api from "@/lib/api";
import { useAuth } from "@/context/AuthContext";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
    Select, SelectTrigger, SelectValue, SelectContent, SelectItem,
} from "@/components/ui/select";
import {
    Table, TableHeader, TableBody, TableRow, TableHead, TableCell,
} from "@/components/ui/table";

/**
 * Page Mandats — TI uniquement.
 * Pour l'instant : interface seulement (pas de logique de recherche backend).
 * Le tableau reste vide tant qu'aucune recherche n'est lancée.
 */
export default function Mandats() {
    const { user } = useAuth();

    // ---- Filtres de recherche ----
    const [mandat, setMandat] = useState("");
    const [codeAvocat, setCodeAvocat] = useState("");
    const [nomClient, setNomClient] = useState("");

    // ---- Données ----
    const [avocats, setAvocats] = useState([]); // pour le Select Code avocat
    const [results] = useState([]); // résultats de recherche (vide pour l'instant)

    // Charge la liste des avocats pour le dropdown Code
    useEffect(() => {
        api.get("/avocats?page=1&page_size=500")
            .then((res) => setAvocats(res.data?.items || []))
            .catch(() => setAvocats([]));
    }, []);

    // TI seulement
    if (user && user.role !== "ti") return <Navigate to="/" replace />;

    // ---- Actions ----
    const onRecherche = () => {
        // Pour l'instant : interface seulement. À brancher au backend plus tard.
    };

    const onEffacer = () => {
        setMandat("");
        setCodeAvocat("");
        setNomClient("");
    };

    const onReinitialiser = () => {
        // Placeholder — sera branché au backend pour réinitialiser un mandat
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
                    Recherche et gestion des mandats d'aide juridique.
                </p>
            </div>

            {/* Barre de filtres */}
            <div className="bg-slate-100 border border-slate-300 rounded-md p-4 shrink-0">
                <div className="flex items-end gap-4 flex-wrap">
                    {/* Mandat */}
                    <div className="flex flex-col">
                        <Label htmlFor="mandat" className="text-sm text-slate-700 mb-1">
                            Mandat
                        </Label>
                        <Input
                            id="mandat"
                            value={mandat}
                            onChange={(e) => setMandat(e.target.value)}
                            className="rounded-md h-9 w-56"
                            data-testid="mandat-input"
                        />
                        <span className="text-[10px] text-slate-500 mt-0.5">
                            ( Format RR-BB-NNNNNNNN-NN )
                        </span>
                    </div>

                    {/* Code avocat */}
                    <div className="flex flex-col">
                        <Label htmlFor="code-avocat" className="text-sm text-slate-700 mb-1">
                            Code avocat
                        </Label>
                        <Select value={codeAvocat} onValueChange={setCodeAvocat}>
                            <SelectTrigger
                                id="code-avocat"
                                className="rounded-md h-9 w-28"
                                data-testid="code-avocat-select"
                            >
                                <SelectValue placeholder="" />
                            </SelectTrigger>
                            <SelectContent className="max-h-80">
                                {avocats.map((a) => (
                                    <SelectItem key={a.code} value={a.code}>
                                        {a.code}
                                    </SelectItem>
                                ))}
                            </SelectContent>
                        </Select>
                        <span className="text-[10px] text-slate-500 mt-0.5">&nbsp;</span>
                    </div>

                    {/* Nom client */}
                    <div className="flex flex-col">
                        <Label htmlFor="nom-client" className="text-sm text-slate-700 mb-1">
                            Nom client
                        </Label>
                        <Input
                            id="nom-client"
                            value={nomClient}
                            onChange={(e) => setNomClient(e.target.value)}
                            className="rounded-md h-9 w-64"
                            data-testid="nom-client-input"
                        />
                        <span className="text-[10px] text-slate-500 mt-0.5">&nbsp;</span>
                    </div>

                    <div className="flex-1" />

                    {/* Boutons droite */}
                    <div className="flex items-start gap-2 pb-5">
                        <Button
                            type="button"
                            variant="outline"
                            onClick={onRecherche}
                            className="rounded-md h-12 px-5 border-2 border-[#0033A0]"
                            data-testid="mandat-search-btn"
                        >
                            <Search className="w-5 h-5 mr-2" />
                            Recherche
                        </Button>
                        <Button
                            type="button"
                            variant="outline"
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
                            <TableHead className="h-9 py-1">Mandat</TableHead>
                            <TableHead className="h-9 py-1">Code avocat</TableHead>
                            <TableHead className="h-9 py-1">Nom client</TableHead>
                            <TableHead className="h-9 py-1">Date émission</TableHead>
                            <TableHead className="h-9 py-1">Article</TableHead>
                            <TableHead className="h-9 py-1">Statut</TableHead>
                        </TableRow>
                    </TableHeader>
                    <TableBody>
                        {results.length === 0 ? (
                            <TableRow>
                                <TableCell colSpan={6} className="text-center py-12 text-sm text-slate-400">
                                    <FileSearch className="w-10 h-10 mx-auto mb-2 text-slate-300" />
                                    Aucun résultat — utilisez les filtres ci-dessus pour rechercher
                                </TableCell>
                            </TableRow>
                        ) : (
                            results.map((m) => (
                                <TableRow key={m.id} className="[&>td]:py-1.5">
                                    <TableCell className="font-mono text-xs">{m.mandat}</TableCell>
                                    <TableCell className="font-mono text-xs">{m.code_avocat}</TableCell>
                                    <TableCell>{m.nom_client}</TableCell>
                                    <TableCell className="text-slate-600">{m.date_emission}</TableCell>
                                    <TableCell className="text-slate-600">{m.article}</TableCell>
                                    <TableCell className="text-slate-600">{m.statut}</TableCell>
                                </TableRow>
                            ))
                        )}
                    </TableBody>
                </Table>
            </div>

            {/* Bouton Réinitialiser bas-droit */}
            <div className="flex justify-end shrink-0">
                <Button
                    type="button"
                    variant="outline"
                    onClick={onReinitialiser}
                    className="rounded-md h-12 px-5"
                    data-testid="mandat-reinit-btn"
                >
                    <RefreshCw className="w-5 h-5 mr-2 text-[#0033A0]" />
                    Réinitialiser
                </Button>
            </div>
        </div>
    );
}
