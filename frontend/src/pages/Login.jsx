import { useState } from "react";
import { useNavigate, Navigate } from "react-router-dom";
import { Scale } from "lucide-react";
import { useAuth } from "@/context/AuthContext";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";

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
        <div className="min-h-screen flex items-center justify-center bg-white px-6 py-10">
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

                <div className="mt-10 text-xs text-slate-500 text-center">
                    © {new Date().getFullYear()} GestionCardex — Édition Web
                </div>
            </div>
        </div>
    );
}
