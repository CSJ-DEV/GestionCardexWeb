import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Switch } from "@/components/ui/switch";
import { Badge } from "@/components/ui/badge";
import { Plus, Pencil, Trash2, Star } from "lucide-react";
import { Field, EMPTY_ADRESSE } from "./constants";

export const AdressesTab = ({ readOnly, adresses, editAdr, setEditAdr, onSave, onDelete }) => (
    <div className="space-y-4">
        {!readOnly && (
            <Button
                onClick={() => setEditAdr({ ...EMPTY_ADRESSE, courant: adresses.length === 0 })}
                className="rounded-md bg-[#0033A0] hover:bg-[#002277] text-white"
                data-testid="add-adresse-btn"
            >
                <Plus size={14} className="mr-2" /> Nouvelle adresse
            </Button>
        )}

        <div className="space-y-2">
            {adresses.length === 0 ? (
                <div className="text-sm text-slate-500 text-center py-8 border border-dashed border-slate-300 rounded-md">
                    Aucune adresse. Cliquez sur « Nouvelle adresse ».
                </div>
            ) : (
                adresses.map((adr) => (
                    <div key={adr.id} className="border border-slate-200 rounded-md p-3 flex items-start justify-between hover:border-slate-300" data-testid={`adresse-row-${adr.id}`}>
                        <div className="flex-1">
                            <div className="flex items-center gap-2 mb-1">
                                {adr.courant && <Badge className="bg-amber-100 text-amber-800 hover:bg-amber-100"><Star size={10} className="mr-1" />Courante</Badge>}
                                <span className="font-medium text-slate-900">{adr.address || "—"}</span>
                            </div>
                            <div className="text-xs text-slate-600">
                                {[adr.ville, adr.province, adr.codepostal].filter(Boolean).join(", ")}
                                {adr.telephone && ` • ${adr.telephone}`}
                                {adr.email && ` • ${adr.email}`}
                            </div>
                        </div>
                        {!readOnly && (
                            <div className="flex gap-1">
                                <Button variant="ghost" size="icon" onClick={() => setEditAdr(adr)}><Pencil size={14} /></Button>
                                <Button variant="ghost" size="icon" className="text-red-600" onClick={() => onDelete(adr)}><Trash2 size={14} /></Button>
                            </div>
                        )}
                    </div>
                ))
            )}
        </div>

        {editAdr && (
            <div className="border-2 border-[#0033A0] rounded-md p-4 space-y-3 bg-blue-50/30">
                <div className="font-semibold text-sm">{editAdr.id ? "Modifier l'adresse" : "Nouvelle adresse"}</div>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                    <Field label="Adresse"><Input value={editAdr.address || ""} onChange={(e) => setEditAdr({ ...editAdr, address: e.target.value })} className="rounded-md" /></Field>
                    <Field label="Ville"><Input value={editAdr.ville || ""} onChange={(e) => setEditAdr({ ...editAdr, ville: e.target.value })} className="rounded-md" /></Field>
                    <Field label="Province"><Input value={editAdr.province || ""} onChange={(e) => setEditAdr({ ...editAdr, province: e.target.value })} className="rounded-md" /></Field>
                    <Field label="Code postal"><Input value={editAdr.codepostal || ""} onChange={(e) => setEditAdr({ ...editAdr, codepostal: e.target.value.toUpperCase() })} maxLength={7} className="rounded-md font-mono" /></Field>
                    <Field label="Téléphone"><Input value={editAdr.telephone || ""} onChange={(e) => setEditAdr({ ...editAdr, telephone: e.target.value })} className="rounded-md" /></Field>
                    <Field label="Téléphone 2"><Input value={editAdr.telephone2 || ""} onChange={(e) => setEditAdr({ ...editAdr, telephone2: e.target.value })} className="rounded-md" /></Field>
                    <Field label="Télécopieur"><Input value={editAdr.fax || ""} onChange={(e) => setEditAdr({ ...editAdr, fax: e.target.value })} className="rounded-md" /></Field>
                    <Field label="Courriel"><Input type="email" value={editAdr.email || ""} onChange={(e) => setEditAdr({ ...editAdr, email: e.target.value })} className="rounded-md" /></Field>
                </div>
                <div className="flex items-center justify-between border border-slate-200 rounded-md px-3 py-2 bg-white">
                    <Label>Adresse courante</Label>
                    <Switch checked={!!editAdr.courant} onCheckedChange={(v) => setEditAdr({ ...editAdr, courant: v })} />
                </div>
                <div className="flex justify-end gap-2">
                    <Button variant="outline" onClick={() => setEditAdr(null)} className="rounded-md" data-testid="cancel-adresse-btn">Annuler</Button>
                    <Button onClick={onSave} className="rounded-md bg-[#0033A0] hover:bg-[#002277] text-white" data-testid="save-adresse-btn">Enregistrer</Button>
                </div>
            </div>
        )}
    </div>
);
