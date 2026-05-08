import { useEffect, useState } from "react";
import api, { formatApiError } from "@/lib/api";
import { useAuth } from "@/context/AuthContext";
import { Sheet, SheetContent, SheetDescription, SheetHeader, SheetTitle } from "@/components/ui/sheet";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { toast } from "sonner";
import { EMPTY_AVOCAT, EMPTY_MEGA } from "./avocat/constants";
import { IdentificationTab } from "./avocat/IdentificationTab";
import { AdressesTab } from "./avocat/AdressesTab";
import { InhabTab } from "./avocat/InhabTab";
import { MegaTab } from "./avocat/MegaTab";
import { WebTab } from "./avocat/WebTab";

export default function AvocatSheet({ open, onOpenChange, avocat, onSaved }) {
    const { user } = useAuth();
    const readOnly = user?.role === "lecteur";
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

    // Effet 1 — synchronise le formulaire chaque fois que le parent passe un nouvel avocat
    useEffect(() => {
        if (avocat?.id) {
            setForm({ ...EMPTY_AVOCAT, ...avocat, adresse: { ...EMPTY_AVOCAT.adresse, ...(avocat.adresse || {}) } });
        } else if (avocat) {
            setForm(EMPTY_AVOCAT);
        }
    }, [avocat]);

    // Effet 2 — charge les données lourdes (adresses / inhabilités / méga) UNIQUEMENT
    // quand l'identifiant change. Évite des refetches inutiles après un PUT
    // quand le parent reassigne `editing = updatedAvocat` (même id, nouvelle référence).
    useEffect(() => {
        if (!avocatId) {
            setAdresses([]);
            setInhabs([]);
            setMega(EMPTY_MEGA);
            // Pré-remplit le code suggéré pour un nouvel avocat
            if (avocat) {
                api.get(`/avocats/next-code?type=A`).then(({ data }) => setForm((f) => ({ ...f, code: data.code }))).catch(() => {});
            }
            return;
        }
        api.get(`/avocats/${avocatId}/adresses`).then(({ data }) => setAdresses(data || [])).catch(() => setAdresses([]));
        api.get(`/avocats/${avocatId}/inhabilites`).then(({ data }) => setInhabs(data || [])).catch(() => setInhabs([]));
        api.get(`/avocats/${avocatId}/mega`).then(({ data }) => {
            setMega(data && Object.keys(data).length > 0 ? { ...EMPTY_MEGA, ...data } : EMPTY_MEGA);
        }).catch(() => setMega(EMPTY_MEGA));
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [avocatId]);

    const upd = (k, v) => setForm((f) => ({ ...f, [k]: v }));

    const onTypeChange = async (t) => {
        upd("type_code", t);
        if (!isEditing) {
            try {
                const { data } = await api.get(`/avocats/next-code?type=${t}`);
                upd("code", data.code);
            } catch { /* ignore */ }
        }
    };

    const handleSubmit = async (e) => {
        e?.preventDefault?.();
        if (!form.code || !form.nom || !form.prenom) {
            toast.error("Code, nom et prénom sont requis");
            return;
        }
        setSaving(true);
        try {
            if (isEditing) {
                const { id: _i, created_at: _c, updated_at: _u, usermodif: _m, ...payload } = form;
                const { data } = await api.put(`/avocats/${avocat.id}`, payload);
                toast.success("Avocat mis à jour");
                onSaved?.({ updatedAvocat: data });
            } else {
                const { data } = await api.post("/avocats", form);
                toast.success("Avocat créé");
                onSaved?.({ updatedAvocat: data });
            }
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
    const saveAdresse = async () => {
        if (!editAdr) return;
        const { id, courant, ...payload } = editAdr;
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
            toast.success("Profil Méga enregistré");
            onSaved?.({ close: false });
        } catch (err) {
            toast.error(formatApiError(err.response?.data?.detail) || "Erreur");
        } finally { setMegaSaving(false); }
    };

    return (
        <Sheet open={open} onOpenChange={onOpenChange}>
            <SheetContent className="sm:max-w-3xl w-full overflow-y-auto" data-testid="avocat-sheet">
                <SheetHeader>
                    <SheetTitle className="font-display text-2xl tracking-tight">
                        {isEditing ? `${form.prenom} ${form.nom} (${form.code})` : "Nouvel avocat"}
                    </SheetTitle>
                    <SheetDescription>Fiche complète — fidèle à GestionCardex VB</SheetDescription>
                </SheetHeader>

                <Tabs defaultValue="ident" className="mt-6">
                    <TabsList className="grid grid-cols-5 w-full">
                        <TabsTrigger value="ident" data-testid="tab-ident">Identification</TabsTrigger>
                        <TabsTrigger value="adr" disabled={!isEditing} data-testid="tab-adr">
                            Adresses {adresses.length > 0 && `(${adresses.length})`}
                        </TabsTrigger>
                        <TabsTrigger value="inhab" disabled={!isEditing} data-testid="tab-inhab">
                            Inhabilité {inhabs.length > 0 && `(${inhabs.length})`}
                        </TabsTrigger>
                        <TabsTrigger value="mega" disabled={!isEditing} data-testid="tab-mega">Méga</TabsTrigger>
                        <TabsTrigger value="web" disabled={!isEditing} data-testid="tab-web">Web</TabsTrigger>
                    </TabsList>

                    <TabsContent value="ident" className="mt-6">
                        <IdentificationTab
                            form={form} upd={upd} isEditing={isEditing} readOnly={readOnly}
                            saving={saving} onTypeChange={onTypeChange}
                            onSubmit={handleSubmit} onCancel={() => onOpenChange(false)}
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
                            avocatId={avocatId} onSubmit={handleSubmit}
                        />
                    </TabsContent>
                </Tabs>
            </SheetContent>
        </Sheet>
    );
}
