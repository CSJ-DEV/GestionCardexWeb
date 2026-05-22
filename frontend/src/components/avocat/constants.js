// Données et helpers partagés par les onglets de l'AvocatSheet
import { Label } from "@/components/ui/label";

export const QC_DISTRICTS = [
    { id: 1, nom: "Montréal" }, { id: 2, nom: "Québec" }, { id: 3, nom: "Laval" },
    { id: 4, nom: "Longueuil" }, { id: 5, nom: "Gatineau" }, { id: 6, nom: "Sherbrooke" },
    { id: 7, nom: "Trois-Rivières" }, { id: 8, nom: "Saguenay" }, { id: 9, nom: "Lévis" },
    { id: 10, nom: "Terrebonne" }, { id: 11, nom: "Saint-Jean-sur-Richelieu" }, { id: 12, nom: "Repentigny" },
    { id: 13, nom: "Drummondville" }, { id: 14, nom: "Saint-Jérôme" }, { id: 15, nom: "Granby" },
    { id: 16, nom: "Beauharnois" }, { id: 17, nom: "Mirabel" }, { id: 18, nom: "Joliette" },
];

export const EMPTY_AVOCAT = {
    code: "", type_code: "A", nom: "", prenom: "",
    sectbar: "", annee_barreau: "", codebar: "", nas: "", neq: "", taxes: "",
    dateinscbarr: "", villerref: "", comm: "",
    actif: true, payable: true, mega: false,
    depodirect: false, factweb: false, confweb: false, surveil: false,
    adresse: { address: "", ville: "", province: "QC", codepostal: "", telephone: "", email: "" },
};

export const EMPTY_ADRESSE = {
    address: "", adresse2: "", adresse3: "", ville: "", province: "QC",
    codepostal: "", telephone: "", telephone2: "", fax: "", email: "",
};

export const EMPTY_MEGA = {
    sectbar: "", francais: true, anglais: false, autres: "", experience: 0,
    details: "", art486: false, art672: false, art684: false,
    commentaire: "", dateinsc: "", districts: [], tous_districts: false,
};

// Petit composant Field — label + enfant (input/select/etc.)
export const Field = ({ label, children }) => (
    <div className="space-y-1.5">
        <Label className="text-xs font-medium text-slate-700">{label}</Label>
        {children}
    </div>
);
