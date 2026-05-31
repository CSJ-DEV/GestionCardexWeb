import { useState } from "react";
import api, { formatApiError } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { KeyRound, UserCircle2, Eye, EyeOff } from "lucide-react";
import { toast } from "sonner";
import { useAuth } from "@/context/AuthContext";

const roleLabel = { admin: "Administrateur", ti: "Technicien TI", editeur: "Éditeur", lecteur: "Lecteur" };
const roleBadge = {
    admin: "bg-violet-100 text-violet-700",
    ti: "bg-orange-100 text-orange-700",
    editeur: "bg-blue-100 text-blue-700",
    lecteur: "bg-slate-100 text-slate-700",
};

export default function Profil() {
    const { user } = useAuth();
    const isSSO = (user?.auth_provider || "local") === "entra";
    const [current, setCurrent] = useState("");
    const [next, setNext] = useState("");
    const [confirm, setConfirm] = useState("");
    const [showCurrent, setShowCurrent] = useState(false);
    const [showNext, setShowNext] = useState(false);
    const [submitting, setSubmitting] = useState(false);

    const submit = async (e) => {
        e.preventDefault();
        if (next.length < 8) {
            toast.error("Le nouveau mot de passe doit comporter au moins 8 caractères");
            return;
        }
        if (next !== confirm) {
            toast.error("Les deux saisies du nouveau mot de passe ne correspondent pas");
            return;
        }
        if (next === current) {
            toast.error("Le nouveau mot de passe doit être différent de l'actuel");
            return;
        }
        setSubmitting(true);
        try {
            await api.put("/auth/change-password", {
                current_password: current,
                new_password: next,
            });
            toast.success("Mot de passe mis à jour. Conservez-le en lieu sûr.");
            setCurrent("");
            setNext("");
            setConfirm("");
        } catch (err) {
            toast.error(formatApiError(err.response?.data?.detail));
        } finally {
            setSubmitting(false);
        }
    };

    return (
        <div className="space-y-8 max-w-3xl" data-testid="profil-page">
            <div>
                <div className="overline mb-2">Compte</div>
                <h1 className="font-display text-4xl font-bold tracking-tight text-slate-900">Mon profil</h1>
                <p className="text-sm text-slate-600 mt-1">Gérez vos informations personnelles et votre mot de passe.</p>
            </div>

            <Card className="rounded-md border-slate-200">
                <CardHeader className="pb-3">
                    <CardTitle className="flex items-center gap-2 text-lg font-display">
                        <UserCircle2 size={20} className="text-slate-600" />
                        Informations
                    </CardTitle>
                </CardHeader>
                <CardContent className="grid grid-cols-1 md:grid-cols-4 gap-6 text-sm">
                    <div>
                        <div className="overline mb-1.5" style={{ fontSize: 10 }}>Nom</div>
                        <div className="font-medium text-slate-900" data-testid="profil-name">{user?.name || "—"}</div>
                    </div>
                    <div>
                        <div className="overline mb-1.5" style={{ fontSize: 10 }}>Courriel</div>
                        <div className="font-mono text-xs text-slate-700" data-testid="profil-email">{user?.email}</div>
                    </div>
                    <div>
                        <div className="overline mb-1.5" style={{ fontSize: 10 }}>Rôle</div>
                        <Badge className={`${roleBadge[user?.role] || ""} hover:${roleBadge[user?.role] || ""} rounded-md`} data-testid="profil-role">
                            {roleLabel[user?.role] || user?.role || "—"}
                        </Badge>
                    </div>
                    <div>
                        <div className="overline mb-1.5" style={{ fontSize: 10 }}>Méthode d'authentification</div>
                        <Badge
                            className={`rounded-md ${isSSO ? "bg-sky-100 text-sky-700" : "bg-slate-100 text-slate-700"}`}
                            data-testid="profil-auth-provider"
                        >
                            {isSSO ? "Microsoft Entra ID" : "Compte local"}
                        </Badge>
                    </div>
                </CardContent>
            </Card>

            {isSSO ? (
                <Card className="rounded-md border-slate-200" data-testid="profil-sso-info">
                    <CardHeader className="pb-3">
                        <CardTitle className="flex items-center gap-2 text-lg font-display">
                            <KeyRound size={20} className="text-slate-600" />
                            Sécurité du compte
                        </CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className="rounded-md bg-sky-50 border border-sky-200 px-4 py-3 text-sm text-slate-700">
                            Votre compte est géré par <strong>Microsoft Entra ID</strong>. Le mot de passe,
                            l'authentification multifacteur et les paramètres de sécurité se gèrent directement
                            dans votre compte Microsoft, pas ici.
                            <div className="mt-3">
                                <a
                                    href="https://myaccount.microsoft.com/security-info"
                                    target="_blank"
                                    rel="noopener noreferrer"
                                    className="text-[#0033A0] hover:underline font-medium"
                                    data-testid="profil-ms-security-link"
                                >
                                    Gérer mes informations de sécurité Microsoft →
                                </a>
                            </div>
                        </div>
                    </CardContent>
                </Card>
            ) : (
            <Card className="rounded-md border-slate-200">
                <CardHeader className="pb-3">
                    <CardTitle className="flex items-center gap-2 text-lg font-display">
                        <KeyRound size={20} className="text-slate-600" />
                        Changer mon mot de passe
                    </CardTitle>
                </CardHeader>
                <CardContent>
                    <form onSubmit={submit} className="space-y-5" data-testid="change-password-form">
                        <div className="space-y-1.5">
                            <Label htmlFor="current" className="text-xs">Mot de passe actuel</Label>
                            <div className="relative">
                                <Input
                                    id="current"
                                    type={showCurrent ? "text" : "password"}
                                    value={current}
                                    onChange={(e) => setCurrent(e.target.value)}
                                    required
                                    autoComplete="current-password"
                                    className="rounded-md pr-10"
                                    data-testid="profil-input-current"
                                />
                                <button
                                    type="button"
                                    onClick={() => setShowCurrent(!showCurrent)}
                                    className="absolute right-2 top-1/2 -translate-y-1/2 text-slate-500 hover:text-slate-900"
                                    tabIndex={-1}
                                    aria-label={showCurrent ? "Masquer" : "Afficher"}
                                >
                                    {showCurrent ? <EyeOff size={16} /> : <Eye size={16} />}
                                </button>
                            </div>
                        </div>

                        <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
                            <div className="space-y-1.5">
                                <Label htmlFor="next" className="text-xs">Nouveau mot de passe</Label>
                                <div className="relative">
                                    <Input
                                        id="next"
                                        type={showNext ? "text" : "password"}
                                        value={next}
                                        onChange={(e) => setNext(e.target.value)}
                                        required
                                        autoComplete="new-password"
                                        className="rounded-md pr-10"
                                        data-testid="profil-input-new"
                                    />
                                    <button
                                        type="button"
                                        onClick={() => setShowNext(!showNext)}
                                        className="absolute right-2 top-1/2 -translate-y-1/2 text-slate-500 hover:text-slate-900"
                                        tabIndex={-1}
                                        aria-label={showNext ? "Masquer" : "Afficher"}
                                    >
                                        {showNext ? <EyeOff size={16} /> : <Eye size={16} />}
                                    </button>
                                </div>
                            </div>
                            <div className="space-y-1.5">
                                <Label htmlFor="confirm" className="text-xs">Confirmer le nouveau mot de passe</Label>
                                <Input
                                    id="confirm"
                                    type={showNext ? "text" : "password"}
                                    value={confirm}
                                    onChange={(e) => setConfirm(e.target.value)}
                                    required
                                    autoComplete="new-password"
                                    className="rounded-md"
                                    data-testid="profil-input-confirm"
                                />
                            </div>
                        </div>

                        <div className="rounded-md bg-slate-50 border border-slate-200 px-4 py-3 text-xs text-slate-600">
                            <div className="font-medium text-slate-800 mb-1.5">Recommandations</div>
                            <ul className="list-disc list-inside space-y-0.5">
                                <li>Minimum 8 caractères</li>
                                <li>Évitez d'utiliser un mot de passe déjà employé ailleurs</li>
                                <li>Mélangez lettres, chiffres et caractères spéciaux</li>
                            </ul>
                        </div>

                        <div className="flex justify-end">
                            <Button
                                type="submit"
                                disabled={submitting || !current || !next || !confirm}
                                className="rounded-md bg-[#0033A0] hover:bg-[#002277] text-white"
                                data-testid="profil-submit-btn"
                            >
                                {submitting ? "Enregistrement…" : "Mettre à jour le mot de passe"}
                            </Button>
                        </div>
                    </form>
                </CardContent>
            </Card>
            )}
        </div>
    );
}
