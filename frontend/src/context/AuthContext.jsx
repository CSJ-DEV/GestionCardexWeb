import { createContext, useContext, useEffect, useState } from "react";
import api, { formatApiError } from "@/lib/api";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
    const [user, setUser] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        let cancelled = false;
        (async () => {
            try {
                const { data } = await api.get("/auth/me");
                if (!cancelled) setUser(data);
            } catch {
                if (!cancelled) setUser(false);
            } finally {
                if (!cancelled) setLoading(false);
            }
        })();
        return () => {
            cancelled = true;
        };
    }, []);

    const login = async (email, password) => {
        try {
            const { data } = await api.post("/auth/login", { email, password });
            setUser(data);
            return { ok: true };
        } catch (e) {
            // Cas 1 : pas de réponse HTTP du tout → problème réseau / CORS / pare-feu
            if (!e.response) {
                console.error("Login network error:", e);
                return {
                    ok: false,
                    error: e.code === "ERR_NETWORK"
                        ? "Connexion au serveur impossible. Vérifiez votre réseau ou les cookies tiers de votre navigateur."
                        : `Erreur réseau : ${e.message}`,
                };
            }
            // Cas 2 : réponse HTTP avec détail (401 invalides, 429 verrou, etc.)
            const detail = e.response?.data?.detail;
            const status = e.response?.status;
            const msg = formatApiError(detail);
            console.error(`Login HTTP ${status}:`, detail);
            return { ok: false, error: msg };
        }
    };

    const logout = async () => {
        try {
            await api.post("/auth/logout");
        } catch {
            /* ignore */
        }
        setUser(false);
    };

    return (
        <AuthContext.Provider value={{ user, loading, login, logout }}>
            {children}
        </AuthContext.Provider>
    );
}

export function useAuth() {
    return useContext(AuthContext);
}
