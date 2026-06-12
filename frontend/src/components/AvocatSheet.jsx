import { useEffect, useMemo, useState } from "react";
import api, { formatApiError } from "@/lib/api";
import { useAuth } from "@/context/AuthContext";
import { Sheet, SheetContent, SheetDescription, SheetHeader, SheetTitle } from "@/components/ui/sheet";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { toast } from "sonner";
import { Lock } from "lucide-react";
import { EMPTY_AVOCAT, EMPTY_MEGA } from "./avocat/constants";
import { IdentificationTab } from "./avocat/IdentificationTab";
import { AdressesTab } from "./avocat/AdressesTab";
import { InhabTab } from "./avocat/InhabTab";
import { MegaTab } from "./avocat/MegaTab";
import { WebTab } from "./avocat/WebTab";
import { HistoriqueTab } from "./avocat/HistoriqueTab";
import { isValidNAS } from "./avocat/formatters";

// Style des onglets : style "classeur" avec distinction nette actif / disponible / verrouillé.
// - Actif : fond blanc, bordure bottom bleue épaisse, texte bleu en gras
// - Disponible (inactif) : texte slate-700, hover bleu pâle
// - Désactivé (disabled) : texte slate-300, fond rayé subtil, cursor not-allowed
const TAB_CLASS = `
    relative inline-flex items-center justify-center
    h-11 px-4 py-2 rounded-md rounded-b-none
    text-xs font-bold uppercase tracking-wider
    border-b-[3px] border-transparent
    text-slate-600 bg-slate-50/50 hover:bg-slate-100 hover:text-slate-900
    transition-all
    data-[state=active]:bg-white
    data-[state=active]:text-[#0033A0]
    data-[state=active]:border-b-[#0033A0]
    data-[state=active]:shadow-sm
    data-[state=active]:-mb-[2px]
    disabled:text-slate-300 disabled:bg-slate-50 disabled:cursor-not-allowed
    disabled:hover:bg-slate-50 disabled:hover:text-slate-300
    disabled:border-b-transparent disabled:opacity-100
`;

// Champs gérés par l'onglet Web (séparés de l'Identification pour les flags dirty)
const WEB_KEYS = ["codeusager", "factweb", "confweb"];

// Sérialisation stable pour comparer deux états (suffisant pour notre forme de state)
const stable = (obj) => JSON.stringify(obj, Object.keys(obj || {}).sort());

const pickIdent = (form) => {
    const out = { ...form };
    WEB_KEYS.forEach((k) => delete out[k]);
    return out;
};
const pickWeb = (form) => {
    const out = {};
    WEB_KEYS.forEach((k) => { out[k] = form[k] ?? ""; });
    return out;
};

// Petit point coloré pour les onglets « modifiés »
const DirtyDot = ({ visible, testId }) => visible ? (
    <span
        className="ml-2 inline-block w-2 h-2 rounded-full bg-amber-500 align-middle"
        aria-label="Modifications non enregistrées"
        data-testid={testId}
    />
) : null;

export default function AvocatSheet({ open, onOpenChange, avocat, onSaved }) {
    const { user } = useAuth();
    const readOnly = user?.role === "lecteur";
    const isAdmin = user?.role === "admin";
    const isEditing = !!(avocat && avocat.id);
    const avocatId = avocat?.id;

    const [form, setForm] = useState(EMPTY_AVOCAT);
    const [saving, setSaving] = useState(false);
    const [adresses, setAdresses] = useState([]);
    const [editAdr, setEditAdr] = useState(null);
    const [inhabs, setInhabs] = useState([]);
    const [editInhab, setEditInhab] = useState(null);
    const [mega, setMega] = useState(EMPTY_MEGA);
    const [megaSaving, setMegaSaving] = useState(false);
    // Taxes (lecture seule) chargées depuis Fvi.avocats sur CSJ-WEB01
    const [taxes, setTaxes] = useState({ tps: "", tvq: "", firme: "", found: false, loading: false });
    // Onglet actif (contrôlé) — utile pour rebasculer hors de Méga si l'utilisateur
    // désactive le flag « Méga » dans Identification.
    const [activeTab, setActiveTab] = useState("ident");

    // Si on est sur l'onglet Méga et que l'avocat persisté n'a plus le flag « Méga »
    // (toggle off + save), retour à Identification. Idem pour l'onglet Web qui dépend
    // de la facturation web persistée côté backend.
    useEffect(() => {
        if (activeTab === "mega" && !avocat?.mega) {
            setActiveTab("ident");
        }
        if (activeTab === "web" && !avocat?.factweb) {
            setActiveTab("ident");
        }
    }, [avocat?.mega, avocat?.factweb, activeTab]);

    // Baselines (= état "propre" après dernier load/save) — useState pour que tout
    // changement déclenche la recomputation des useMemo dirty (sinon useRef reste invisible à React).
    const [baseline, setBaseline] = useState({
        ident: stable(pickIdent(EMPTY_AVOCAT)),
        web: stable(pickWeb(EMPTY_AVOCAT)),
        mega: stable(EMPTY_MEGA),
    });

    // Effet 1 — synchronise le formulaire chaque fois que le parent passe un nouvel avocat
    useEffect(() => {
        // Reset l'onglet actif sur Identification quand on change d'avocat
        setActiveTab("ident");
        if (avocat?.id) {
            const next = { ...EMPTY_AVOCAT, ...avocat, adresse: { ...EMPTY_AVOCAT.adresse, ...(avocat.adresse || {}) } };
            setForm(next);
            setBaseline((b) => ({ ...b, ident: stable(pickIdent(next)), web: stable(pickWeb(next)) }));
        } else if (avocat) {
            setForm(EMPTY_AVOCAT);
            setBaseline((b) => ({ ...b, ident: stable(pickIdent(EMPTY_AVOCAT)), web: stable(pickWeb(EMPTY_AVOCAT)) }));
        }
    }, [avocat]);

    // Effet 2 — charge les données lourdes uniquement quand l'identifiant change
    useEffect(() => {
        if (!avocatId) {
            setAdresses([]);
            setInhabs([]);
            setMega(EMPTY_MEGA);
            setTaxes({ tps: "", tvq: "", firme: "", found: false, loading: false });
            setBaseline((b) => ({ ...b, mega: stable(EMPTY_MEGA) }));
            return;
        }
        api.get(`/avocats/${avocatId}/adresses`).then(({ data }) => setAdresses(data || [])).catch(() => setAdresses([]));
        api.get(`/avocats/${avocatId}/inhabilites`).then(({ data }) => setInhabs(data || [])).catch(() => setInhabs([]));
        api.get(`/avocats/${avocatId}/mega`).then(({ data }) => {
            const next = data && Object.keys(data).length > 0 ? { ...EMPTY_MEGA, ...data } : EMPTY_MEGA;
            setMega(next);
            setBaseline((b) => ({ ...b, mega: stable(next) }));
        }).catch(() => {
            setMega(EMPTY_MEGA);
            setBaseline((b) => ({ ...b, mega: stable(EMPTY_MEGA) }));
        });
        // Taxes (TPS / TVQ) lecture seule depuis Fvi.avocats — non bloquant
        setTaxes((t) => ({ ...t, loading: true }));
        api.get(`/avocats/${avocatId}/taxes`)
            .then(({ data }) => setTaxes({
                tps: data?.tps || "", tvq: data?.tvq || "",
                firme: data?.firme || "", found: !!data?.found, loading: false,
            }))
            .catch(() => setTaxes({ tps: "", tvq: "", firme: "", found: false, loading: false }));
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [avocatId]);

    // Calcul des flags dirty (recomputés quand form/mega OU baseline changent)
    const identDirty = useMemo(() => stable(pickIdent(form)) !== baseline.ident, [form, baseline.ident]);
    const webDirty = useMemo(
        () => stable(pickWeb(form)) !== baseline.web,
        [form, baseline.web],
    );
    const megaDirty = useMemo(() => stable(mega) !== baseline.mega, [mega, baseline.mega]);
    const adresseDirty = editAdr !== null;
    const inhabDirty = editInhab !== null;

    const upd = (k, v) => setForm((f) => ({ ...f, [k]: v }));

    const onTypeChange = (t) => {
        // Plus de pré-fetch — le code définitif est attribué côté serveur au save
        upd("type_code", t);
    };

    const handleSubmit = async (e) => {
        e?.preventDefault?.();
        // En création, le code est attribué côté serveur ; on n'exige plus le champ
        if (!form.nom || !form.prenom) {
            toast.error("Nom et prénom sont requis");
            return;
        }
        if (form.nas && !isValidNAS(form.nas)) {
            toast.error("Numéro d'assurance sociale invalide");
            setActiveTab("ident");
            return;
        }
        if (isEditing && !form.code) {
            toast.error("Code manquant");
            return;
        }
        setSaving(true);
        try {
            let data;
            if (isEditing) {
                const { id: _i, created_at: _c, updated_at: _u, usermodif: _m, ...payload } = form;
                ({ data } = await api.put(`/avocats/${avocat.id}`, payload));
                toast.success("Avocat mis à jour");
            } else {
                ({ data } = await api.post("/avocats", form));
                toast.success("Avocat créé");
            }
            // Reset baseline ident+web après succès → invalide les useMemo dirty
            setBaseline((b) => ({ ...b, ident: stable(pickIdent(form)), web: stable(pickWeb(form)) }));
            onSaved?.({ updatedAvocat: data });
        } catch (err) {
            toast.error(formatApiError(err.response?.data?.detail) || "Erreur");
        } finally {
            setSaving(false);
        }
    };

    const reloadAdresses = async () => {
        const { data } = await api.get(`/avocats/${avocatId}/adresses`);
        setAdresses(data || []);
    };
    const saveAdresse = async (override = null) => {
        // override permet au composant enfant (AdressesTab) de passer une version
        // modifiée de l'adresse (ex. courant=true après confirmation) sans dépendre
        // du re-render React, qui n'est pas synchrone.
        const data = override || editAdr;
        if (!data) return;
        const { id, courant, ...payload } = data;
        try {
            if (id) {
                await api.put(`/avocats/${avocatId}/adresses/${id}?courant=${!!courant}`, payload);
            } else {
                await api.post(`/avocats/${avocatId}/adresses?courant=${!!courant}`, payload);
            }
            toast.success("Adresse enregistrée");
            setEditAdr(null);
            reloadAdresses();
            onSaved?.({ close: false });
        } catch (err) {
            toast.error(formatApiError(err.response?.data?.detail) || "Erreur");
        }
    };
    const deleteAdresse = async (adr) => {
        if (!confirm("Supprimer cette adresse ?")) return;
        try {
            await api.delete(`/avocats/${avocatId}/adresses/${adr.id}`);
            toast.success("Adresse supprimée");
            reloadAdresses();
        } catch (err) {
            toast.error(formatApiError(err.response?.data?.detail) || "Erreur");
        }
    };

    const reloadInhabs = async () => {
        const { data } = await api.get(`/avocats/${avocatId}/inhabilites`);
        setInhabs(data || []);
    };
    const saveInhab = async () => {
        if (!editInhab?.datedeb) { toast.error("Date début requise"); return; }
        const { id, ...payload } = editInhab;
        try {
            if (id) await api.put(`/avocats/${avocatId}/inhabilites/${id}`, payload);
            else await api.post(`/avocats/${avocatId}/inhabilites`, payload);
            toast.success("Période enregistrée");
            setEditInhab(null);
            reloadInhabs();
            onSaved?.({ close: false });
        } catch (err) {
            toast.error(formatApiError(err.response?.data?.detail) || "Erreur");
        }
    };
    const deleteInhab = async (item) => {
        if (!confirm("Supprimer cette période ?")) return;
        try {
            await api.delete(`/avocats/${avocatId}/inhabilites/${item.id}`);
            toast.success("Période supprimée");
            reloadInhabs();
        } catch (err) {
            toast.error(formatApiError(err.response?.data?.detail));
        }
    };
    const saveMega = async () => {
        setMegaSaving(true);
        try {
            await api.put(`/avocats/${avocatId}/mega`, mega);
            setBaseline((b) => ({ ...b, mega: stable(mega) }));
            toast.success("Profil Méga enregistré");
            onSaved?.({ close: false });
        } catch (err) {
            toast.error(formatApiError(err.response?.data?.detail) || "Erreur");
        } finally { setMegaSaving(false); }
    };

    const tabsCount = isAdmin ? 6 : 5;

    return (
        <Sheet open={open} onOpenChange={onOpenChange}>
            <SheetContent className="!w-screen !max-w-none sm:!max-w-none overflow-y-auto" data-testid="avocat-sheet">
                <div className="max-w-7xl mx-auto">
                <SheetHeader>
                    <SheetTitle className="font-display text-2xl tracking-tight">
                        {isEditing ? `${form.prenom} ${form.nom} (${form.code})` : "Nouvel avocat"}
                    </SheetTitle>
                </SheetHeader>

                <Tabs value={activeTab} onValueChange={setActiveTab} className="mt-6">
                    <TabsList
                        className={`
                            grid w-full h-auto p-0 gap-1 bg-transparent
                            border-b-2 border-slate-200 rounded-none
                            ${tabsCount === 6 ? "grid-cols-6" : "grid-cols-5"}
                        `}
                    >
                        <TabsTrigger value="ident" data-testid="tab-ident" className={TAB_CLASS}>
                            Identification
                            <DirtyDot visible={identDirty} testId="dirty-ident" />
                        </TabsTrigger>
                        <TabsTrigger value="adr" disabled={!isEditing} data-testid="tab-adr" className={TAB_CLASS}>
                            Adresses {adresses.length > 0 && (
                                <span className="ml-1 text-[10px] font-bold bg-[#0033A0] text-white px-1.5 py-0.5 rounded-full">
                                    {adresses.length}
                                </span>
                            )}
                            <DirtyDot visible={adresseDirty} testId="dirty-adr" />
                        </TabsTrigger>
                        <TabsTrigger value="inhab" disabled={!isEditing} data-testid="tab-inhab" className={TAB_CLASS}>
                            Inhabilité {inhabs.length > 0 && (
                                <span className="ml-1 text-[10px] font-bold bg-amber-500 text-white px-1.5 py-0.5 rounded-full">
                                    {inhabs.length}
                                </span>
                            )}
                            <DirtyDot visible={inhabDirty} testId="dirty-inhab" />
                        </TabsTrigger>
                        <TabsTrigger value="mega" disabled={!isEditing || !avocat?.mega} data-testid="tab-mega" className={TAB_CLASS}>
                            Méga
                            {!avocat?.mega && isEditing && (
                                <Lock className="w-3 h-3 ml-1 opacity-60" />
                            )}
                            <DirtyDot visible={megaDirty && !!avocat?.mega} testId="dirty-mega" />
                        </TabsTrigger>
                        <TabsTrigger value="web" disabled={!isEditing || !avocat?.factweb} data-testid="tab-web" className={TAB_CLASS}>
                            Web
                            {!avocat?.factweb && isEditing && (
                                <Lock className="w-3 h-3 ml-1 opacity-60" />
                            )}
                            <DirtyDot visible={webDirty && !!avocat?.factweb} testId="dirty-web" />
                        </TabsTrigger>
                        {isAdmin && (
                            <TabsTrigger value="hist" disabled={!isEditing} data-testid="tab-hist" className={TAB_CLASS}>
                                Historique
                            </TabsTrigger>
                        )}
                    </TabsList>

                    <TabsContent value="ident" className="mt-6">
                        <IdentificationTab
                            form={form} upd={upd} isEditing={isEditing} readOnly={readOnly}
                            saving={saving} onTypeChange={onTypeChange}
                            onSubmit={handleSubmit} onCancel={() => onOpenChange(false)}
                            savedMega={!!avocat?.mega}
                            savedFactweb={!!avocat?.factweb}
                            taxes={taxes}
                        />
                    </TabsContent>

                    <TabsContent value="adr" className="mt-6">
                        <AdressesTab
                            readOnly={readOnly} adresses={adresses}
                            editAdr={editAdr} setEditAdr={setEditAdr}
                            onSave={saveAdresse} onDelete={deleteAdresse}
                        />
                    </TabsContent>

                    <TabsContent value="inhab" className="mt-6">
                        <InhabTab
                            readOnly={readOnly} inhabs={inhabs}
                            editInhab={editInhab} setEditInhab={setEditInhab}
                            onSave={saveInhab} onDelete={deleteInhab}
                        />
                    </TabsContent>

                    <TabsContent value="mega" className="mt-6">
                        <MegaTab
                            readOnly={readOnly} mega={mega} setMega={setMega}
                            megaSaving={megaSaving} onSave={saveMega}
                        />
                    </TabsContent>

                    <TabsContent value="web" className="mt-6">
                        <WebTab
                            readOnly={readOnly} form={form} upd={upd}
                            avocatId={avocatId} avocat={avocat}
                            adresses={adresses}
                            onSaved={onSaved}
                        />
                    </TabsContent>

                    {isAdmin && (
                        <TabsContent value="hist" className="mt-6">
                            <HistoriqueTab avocatId={avocatId} />
                        </TabsContent>
                    )}
                </Tabs>
                </div>
            </SheetContent>
        </Sheet>
    );
}
