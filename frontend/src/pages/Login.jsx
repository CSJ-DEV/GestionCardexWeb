import { useEffect, useState } from "react";
import { useNavigate, Navigate, useSearchParams } from "react-router-dom";
import { useAuth } from "@/context/AuthContext";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import logo from "@/assets/logo-ajq.jpg";
import axios from "axios";

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

export default function Login() {
    const { user, login } = useAuth();
    const navigate = useNavigate();
    const [searchParams, setSearchParams] = useSearchParams();
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [error, setError] = useState("");
    const [submitting, setSubmitting] = useState(false);
    const [entraEnabled, setEntraEnabled] = useState(false);

    // Détecte si l'authentification Microsoft est activée côté backend.
    useEffect(() => {
        axios.get(`${API}/auth/entra/status`)
            .then((res) => setEntraEnabled(Boolean(res.data?.enabled)))
            .catch(() => setEntraEnabled(false));
    }, []);

    // Récupère un éventuel message d'erreur renvoyé par le flow OAuth.
    useEffect(() => {
        const entraError = searchParams.get("entra_error");
        const msg = searchParams.get("msg");
        if (entraError) {
            setError(msg || `Erreur Microsoft : ${entraError}`);
            // Nettoie l'URL pour éviter de réafficher l'erreur sur refresh.
            const params = new URLSearchParams(searchParams);
            params.delete("entra_error");
            params.delete("msg");
            setSearchParams(params, { replace: true });
        }
    }, [searchParams, setSearchParams]);

    if (user) return <Navigate to="/" replace />;

    const onSubmit = async (e) => {
        e.preventDefault();
        setError("");
        setSubmitting(true);
        const res = await login(email, password);
        setSubmitting(false);
        if (res.ok) navigate("/", { replace: true });
        else setError(res.error || "Échec de connexion");
    };

    const onEntraLogin = () => {
        // Redirection full-page vers le backend → Microsoft (le navigateur gère les cookies).
        window.location.href = `${API}/auth/entra/login`;
    };

    return (
        <div className="min-h-screen flex items-center justify-center bg-white px-6 py-10">
            <div className="w-full max-w-sm">
                <div className="mb-10">
                    <img
                        src={logo}
                        alt="Aide juridique du Québec — Commission des services juridiques"
                        className="w-full h-auto block"
                        data-testid="login-logo"
                    />
                </div>

                <div className="overline mb-2">Authentification</div>
                <h1 className="font-display text-3xl sm:text-4xl font-bold tracking-tight text-slate-900 mb-2">
                    Gestion Cardex et FVI
                </h1>
                <p className="text-sm text-slate-600 mb-8">
                    Connectez-vous pour accéder à la gestion des avocats.
                </p>

                {entraEnabled && (
                    <>
                        <Button
                            type="button"
                            onClick={onEntraLogin}
                            className="w-full h-10 rounded-md bg-white hover:bg-slate-50 text-slate-900 border border-slate-300 flex items-center justify-center gap-2 mb-4"
                            data-testid="login-entra-button"
                        >
                            <MicrosoftLogo />
                            Se connecter avec Microsoft
                        </Button>
                        <div className="flex items-center gap-3 my-4">
                            <div className="flex-1 h-px bg-slate-200" />
                            <span className="text-xs text-slate-500 uppercase tracking-wider">ou</span>
                            <div className="flex-1 h-px bg-slate-200" />
                        </div>
                    </>
                )}

                <form onSubmit={onSubmit} className="space-y-5" data-testid="login-form">
                    <div className="space-y-1.5">
                        <Label htmlFor="email" className="text-xs font-medium text-slate-700">
                            Courriel
                        </Label>
                        <Input
                            id="email"
                            type="email"
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                            placeholder="admin@gestioncardex.qc"
                            required
                            className="rounded-md h-10"
                            data-testid="login-email-input"
                        />
                    </div>
                    <div className="space-y-1.5">
                        <Label htmlFor="password" className="text-xs font-medium text-slate-700">
                            Mot de passe
                        </Label>
                        <Input
                            id="password"
                            type="password"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            required
                            className="rounded-md h-10"
                            data-testid="login-password-input"
                        />
                    </div>
                    {error && (
                        <div
                            className="text-sm text-red-600 bg-red-50 border border-red-200 rounded-md px-3 py-2"
                            data-testid="login-error"
                        >
                            {error}
                        </div>
                    )}
                    <Button
                        type="submit"
                        disabled={submitting}
                        className="w-full h-10 rounded-md bg-[#0033A0] hover:bg-[#002277] text-white"
                        data-testid="login-submit-button"
                    >
                        {submitting ? "Connexion…" : "Se connecter"}
                    </Button>
                </form>

                <div className="mt-10 text-xs text-slate-500 text-center">
                    © {new Date().getFullYear()} GestionCardex — Édition Web
                </div>
            </div>
        </div>
    );
}

// Logo Microsoft officiel (4 carrés colorés)
function MicrosoftLogo() {
    return (
        <svg width="18" height="18" viewBox="0 0 23 23" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
            <rect x="1" y="1" width="10" height="10" fill="#F25022" />
            <rect x="12" y="1" width="10" height="10" fill="#7FBA00" />
            <rect x="1" y="12" width="10" height="10" fill="#00A4EF" />
            <rect x="12" y="12" width="10" height="10" fill="#FFB900" />
        </svg>
    );
}
