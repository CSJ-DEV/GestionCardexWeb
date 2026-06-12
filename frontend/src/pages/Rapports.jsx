import { useState } from "react";
import { API } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { FileText, Download } from "lucide-react";

export default function Rapports() {
    const today = new Date().toISOString().slice(0, 10);
    const [dateDebut, setDateDebut] = useState(today);
    const [dateFin, setDateFin] = useState(today);
    // Filtre Crystal legacy : « » (toutes), « Fisher », « Désignation »,
    // « Rowbotham ». La valeur "" est ré-encodée côté URL ; on utilise
    // le sentinel "ALL" en interne pour Radix Select qui interdit "".
    const [ordonnance, setOrdonnance] = useState("ALL");

    const buildRegistre97Url = () => {
        const params = new URLSearchParams({ date_debut: dateDebut, date_fin: dateFin });
        if (ordonnance && ordonnance !== "ALL") params.set("ordonnance", ordonnance);
        return `${API}/rapports/registre97?${params.toString()}`;
    };

    const downloadRegistre97 = () => window.open(buildRegistre97Url(), "_blank");

    return (
        <div className="space-y-6" data-testid="rapports-page">
            <div>
                <div className="overline mb-2">Production</div>
                <h1 className="font-display text-4xl font-bold tracking-tight text-slate-900">Rapports</h1>
                <p className="text-sm text-slate-600 mt-1">Génération des registres officiels (PDF).</p>
            </div>

            {/* Génération Registre 97 (source : Megaattest sur Themis) */}
            <div className="bg-white border border-slate-200 rounded-md p-6">
                <div className="flex items-center gap-2 mb-1">
                    <FileText size={18} className="text-[#0033A0]" />
                    <h2 className="font-display text-xl font-bold">Registre Article 97</h2>
                </div>
                <p className="text-sm text-slate-600 mb-4">
                    Registre tenu en vertu de l'article 97 du Règlement sur l'aide juridique.
                    Source : <span className="font-mono">Megaattest</span> (Themis).
                </p>
                <div className="grid grid-cols-1 md:grid-cols-4 gap-3 items-end">
                    <div className="space-y-1.5">
                        <Label className="text-xs">Date début</Label>
                        <Input type="date" value={dateDebut} onChange={(e) => setDateDebut(e.target.value)} className="rounded-md" data-testid="report-date-debut" />
                    </div>
                    <div className="space-y-1.5">
                        <Label className="text-xs">Date fin</Label>
                        <Input type="date" value={dateFin} onChange={(e) => setDateFin(e.target.value)} className="rounded-md" data-testid="report-date-fin" />
                    </div>
                    <div className="space-y-1.5">
                        <Label className="text-xs">Ordonnance</Label>
                        <Select value={ordonnance} onValueChange={setOrdonnance}>
                            <SelectTrigger className="rounded-md" data-testid="report-ordonnance">
                                <SelectValue />
                            </SelectTrigger>
                            <SelectContent>
                                <SelectItem value="ALL">Toutes</SelectItem>
                                <SelectItem value="Fisher">Fisher</SelectItem>
                                <SelectItem value="Désignation">Désignation</SelectItem>
                                <SelectItem value="Rowbotham">Rowbotham</SelectItem>
                            </SelectContent>
                        </Select>
                    </div>
                    <Button onClick={downloadRegistre97} className="bg-[#0033A0] hover:bg-[#002277] text-white rounded-md" data-testid="download-registre97">
                        <Download size={14} className="mr-2" /> Générer Registre97 (PDF)
                    </Button>
                </div>
            </div>

            {/* Autres rapports */}
            <div className="bg-white border border-slate-200 rounded-md p-6">
                <div className="flex items-center gap-2 mb-1">
                    <FileText size={18} className="text-[#0033A0]" />
                    <h2 className="font-display text-xl font-bold">Autres rapports</h2>
                </div>
                <p className="text-sm text-slate-600 mb-4">Registres et listes annexes.</p>
                <div className="grid grid-cols-2 md:grid-cols-5 gap-2">
                    <Button variant="outline" onClick={() => window.open(`${API}/rapports/registre98?date_debut=${dateDebut}&date_fin=${dateFin}`, "_blank")} className="rounded-md" data-testid="dl-registre98"><Download size={12} className="mr-1" /> Registre98</Button>
                    <Button variant="outline" onClick={() => window.open(`${API}/rapports/liste-det-bar`, "_blank")} className="rounded-md" data-testid="dl-detbar"><Download size={12} className="mr-1" /> Liste Bar.</Button>
                    <Button variant="outline" onClick={() => window.open(`${API}/rapports/liste-det-dist`, "_blank")} className="rounded-md" data-testid="dl-detdist"><Download size={12} className="mr-1" /> Liste Dist.</Button>
                    <Button variant="outline" onClick={() => window.open(`${API}/rapports/liste-det-reg`, "_blank")} className="rounded-md" data-testid="dl-detreg"><Download size={12} className="mr-1" /> Liste Reg.</Button>
                    <Button variant="outline" onClick={() => window.open(`${API}/rapports/liste-som`, "_blank")} className="rounded-md" data-testid="dl-listesom"><Download size={12} className="mr-1" /> Liste Som.</Button>
                </div>
            </div>
        </div>
    );
}
