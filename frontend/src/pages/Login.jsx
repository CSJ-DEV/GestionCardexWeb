import { useState } from "react";
import { useNavigate, Navigate } from "react-router-dom";
import { Scale } from "lucide-react";
import { useAuth } from "@/context/AuthContext";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";

const BG_URL =
    "https://images.unsplash.com/photo-1664813953289-7c3350f040e0?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2Nzd8MHwxfHNlYXJjaHwxfHxtb2Rlcm4lMjBtaW5pbWFsaXN0JTIwYXJjaGl0ZWN0dXJlJTIwd2hpdGV8ZW58MHx8fHwxNzc4MTY5MzcxfDA&ixlib=rb-4.1.0&q=85";

export default function Login() {
    const { user, login } = useAuth();
    const navigate = useNavigate();
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [error, setError] = useState("");
    const [submitting, setSubmitting] = useState(false);

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

    return (
        <div className="min-h-screen grid grid-cols-1 lg:grid-cols-2 bg-white">
            {/* Left - form */}
            <div className="flex items-center justify-center px-6 py-10">
                <div className="w-full max-w-sm">
                    <div className="flex items-center gap-2.5 mb-10">
                        <div className="h-10 w-10 rounded-md bg-[#0033A0] text-white flex items-center justify-center">
                            <Scale size={20} strokeWidth={2.25} />
                        </div>
                        <div>
                            <div className="font-display font-bold text-lg tracking-tight text-slate-900">
                                GestionCardex
                            </div>
                            <div className="overline" style={{ fontSize: 10 }}>Plateforme légale</div>
                        </div>
                    </div>

                    <div className="overline mb-2">Authentification</div>
                    <h1 className="font-display text-3xl sm:text-4xl font-bold tracking-tight text-slate-900 mb-2">
                        Bienvenue.
                    </h1>
                    <p className="text-sm text-slate-600 mb-8">
                        Connectez-vous pour accéder à la gestion des avocats.
                    </p>

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

                    <div className="mt-10 text-xs text-slate-500">
                        © {new Date().getFullYear()} GestionCardex — Édition Web
                    </div>
                </div>
            </div>

            {/* Right - visual */}
            <div className="hidden lg:block relative overflow-hidden border-l border-slate-200">
                <img
                    src={BG_URL}
                    alt="Architecture moderne"
                    className="absolute inset-0 w-full h-full object-cover"
                />
                <div className="absolute inset-0 bg-gradient-to-tr from-[#0033A0]/40 via-transparent to-white/30" />
                <div className="absolute bottom-10 left-10 right-10 text-white">
                    <div className="overline text-white/80 mb-3">Migration Visual Basic → Web</div>
                    <h2 className="font-display text-3xl font-bold leading-tight max-w-md">
                        Une nouvelle ère pour la gestion de vos dossiers d'avocats.
                    </h2>
                </div>
            </div>
        </div>
    );
}
