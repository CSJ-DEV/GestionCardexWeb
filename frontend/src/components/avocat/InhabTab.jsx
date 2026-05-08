import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Plus, Pencil, Trash2 } from "lucide-react";
import { Field } from "./constants";
import { DateInput } from "./DateInput";

export const InhabTab = ({ readOnly, inhabs, editInhab, setEditInhab, onSave, onDelete }) => (
    <div className="space-y-4">
        {!readOnly && (
            <Button
                onClick={() => setEditInhab({ datedeb: "", datefin: "", comm: "" })}
                className="rounded-md bg-[#0033A0] hover:bg-[#002277] text-white"
                data-testid="add-inhab-btn"
            >
                <Plus size={14} className="mr-2" /> Nouvelle période
            </Button>
        )}
        <div className="space-y-2">
            {inhabs.length === 0 ? (
                <div className="text-sm text-slate-500 text-center py-8 border border-dashed border-slate-300 rounded-md">
                    Aucune période d'inhabilité.
                </div>
            ) : (
                inhabs.map((it) => (
                    <div key={it.id} className="border border-slate-200 rounded-md p-3 flex items-start justify-between" data-testid={`inhab-row-${it.id}`}>
                        <div className="flex-1">
                            <div className="font-medium text-slate-900">{it.datedeb} → {it.datefin || "en cours"}</div>
                            {it.comm && <div className="text-xs text-slate-600 mt-1">{it.comm}</div>}
                        </div>
                        {!readOnly && (
                            <div className="flex gap-1">
                                <Button variant="ghost" size="icon" onClick={() => setEditInhab(it)}><Pencil size={14} /></Button>
                                <Button variant="ghost" size="icon" className="text-red-600" onClick={() => onDelete(it)}><Trash2 size={14} /></Button>
                            </div>
                        )}
                    </div>
                ))
            )}
        </div>
        {editInhab && (
            <div className="border-2 border-[#0033A0] rounded-md p-4 space-y-3 bg-blue-50/30">
                <div className="font-semibold text-sm">{editInhab.id ? "Modifier la période" : "Nouvelle période"}</div>
                <div className="grid grid-cols-2 gap-3">
                    <Field label="Date début"><DateInput value={editInhab.datedeb || ""} onChange={(v) => setEditInhab({ ...editInhab, datedeb: v })} className="rounded-md font-mono" data-testid="inhab-datedeb" /></Field>
                    <Field label="Date fin"><DateInput value={editInhab.datefin || ""} onChange={(v) => setEditInhab({ ...editInhab, datefin: v })} className="rounded-md font-mono" data-testid="inhab-datefin" /></Field>
                </div>
                <Field label="Commentaire"><Textarea value={editInhab.comm || ""} onChange={(e) => setEditInhab({ ...editInhab, comm: e.target.value })} rows={3} className="rounded-md" /></Field>
                <div className="flex justify-end gap-2">
                    <Button variant="outline" onClick={() => setEditInhab(null)} data-testid="cancel-inhab-btn">Annuler</Button>
                    <Button onClick={onSave} className="bg-[#0033A0] hover:bg-[#002277] text-white" data-testid="save-inhab-btn">Enregistrer</Button>
                </div>
            </div>
        )}
    </div>
);
