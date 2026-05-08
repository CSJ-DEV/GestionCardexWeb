import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Switch } from "@/components/ui/switch";
import { Textarea } from "@/components/ui/textarea";
import { Separator } from "@/components/ui/separator";
import { Field, QC_DISTRICTS } from "./constants";

const ARTICLES = [
    { k: "art486", l: "Article 486" },
    { k: "art672", l: "Article 672" },
    { k: "art684", l: "Article 684" },
];

export const MegaTab = ({ readOnly, mega, setMega, megaSaving, onSave }) => {
    const toggleDistrict = (id) => {
        const list = mega.districts || [];
        const next = list.includes(id) ? list.filter((x) => x !== id) : [...list, id];
        setMega({ ...mega, districts: next });
    };

    return (
        <div className="space-y-5">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <Field label="Section barreau"><Input value={mega.sectbar || ""} onChange={(e) => setMega({ ...mega, sectbar: e.target.value })} disabled={readOnly} className="rounded-md" data-testid="mega-sectbar" /></Field>
                <Field label="Expérience (années)"><Input type="number" min="0" value={mega.experience || 0} onChange={(e) => setMega({ ...mega, experience: parseInt(e.target.value) || 0 })} disabled={readOnly} className="rounded-md" data-testid="mega-experience" /></Field>
                <Field label="Date inscription"><Input type="date" value={mega.dateinsc || ""} onChange={(e) => setMega({ ...mega, dateinsc: e.target.value })} disabled={readOnly} className="rounded-md" /></Field>
            </div>
            <Separator />
            <div>
                <div className="overline mb-3">Langues</div>
                <div className="grid grid-cols-2 gap-3">
                    <div className="flex items-center justify-between border border-slate-200 rounded-md px-3 py-2"><Label className="text-sm">Français</Label><Switch checked={!!mega.francais} onCheckedChange={(v) => setMega({ ...mega, francais: v })} disabled={readOnly} data-testid="mega-francais" /></div>
                    <div className="flex items-center justify-between border border-slate-200 rounded-md px-3 py-2"><Label className="text-sm">Anglais</Label><Switch checked={!!mega.anglais} onCheckedChange={(v) => setMega({ ...mega, anglais: v })} disabled={readOnly} data-testid="mega-anglais" /></div>
                </div>
                <div className="mt-3"><Field label="Autres langues"><Input value={mega.autres || ""} onChange={(e) => setMega({ ...mega, autres: e.target.value })} disabled={readOnly} placeholder="Espagnol, italien…" className="rounded-md" /></Field></div>
            </div>
            <Separator />
            <div>
                <div className="overline mb-3">Articles habilités</div>
                <div className="grid grid-cols-3 gap-3">
                    {ARTICLES.map((a) => (
                        <div key={a.k} className="flex items-center justify-between border border-slate-200 rounded-md px-3 py-2"><Label className="text-sm">{a.l}</Label><Switch checked={!!mega[a.k]} onCheckedChange={(v) => setMega({ ...mega, [a.k]: v })} disabled={readOnly} data-testid={`mega-${a.k}`} /></div>
                    ))}
                </div>
            </div>
            <Separator />
            <div>
                <div className="flex items-center justify-between mb-3">
                    <div className="overline">Districts habilités ({(mega.districts || []).length})</div>
                    <div className="flex items-center gap-2"><Label className="text-xs text-slate-600">Tous</Label><Switch checked={!!mega.tous_districts} onCheckedChange={(v) => setMega({ ...mega, tous_districts: v, districts: v ? QC_DISTRICTS.map((d) => d.id) : [] })} disabled={readOnly} data-testid="mega-tous-districts" /></div>
                </div>
                <div className="grid grid-cols-2 md:grid-cols-3 gap-2 max-h-56 overflow-y-auto border border-slate-200 rounded-md p-3">
                    {QC_DISTRICTS.map((d) => (
                        <label key={d.id} className="flex items-center gap-2 text-sm cursor-pointer hover:bg-slate-50 rounded px-2 py-1">
                            <input type="checkbox" checked={(mega.districts || []).includes(d.id)} onChange={() => toggleDistrict(d.id)} disabled={readOnly} data-testid={`mega-district-${d.id}`} />
                            <span>{d.nom}</span>
                        </label>
                    ))}
                </div>
            </div>
            <Separator />
            <Field label="Détails"><Textarea value={mega.details || ""} onChange={(e) => setMega({ ...mega, details: e.target.value })} disabled={readOnly} rows={3} className="rounded-md" /></Field>
            <Field label="Commentaire"><Textarea value={mega.commentaire || ""} onChange={(e) => setMega({ ...mega, commentaire: e.target.value })} disabled={readOnly} rows={3} className="rounded-md" /></Field>
            {!readOnly && (
                <div className="flex justify-end pt-2">
                    <Button onClick={onSave} disabled={megaSaving} className="bg-[#0033A0] hover:bg-[#002277] text-white rounded-md" data-testid="save-mega-btn">
                        {megaSaving ? "Enregistrement…" : "Enregistrer le profil Méga"}
                    </Button>
                </div>
            )}
        </div>
    );
};
