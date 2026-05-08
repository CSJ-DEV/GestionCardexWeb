import axios from "axios";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
export const API = `${BACKEND_URL}/api`;

const api = axios.create({
    baseURL: API,
    withCredentials: true,
});

// --- Auto-refresh on 401 -------------------------------------------------
// Si une requête échoue avec 401, on tente un POST /auth/refresh
// puis on rejoue la requête initiale. Une seule tentative par requête.
let refreshPromise = null;

api.interceptors.response.use(
    (resp) => resp,
    async (error) => {
        const original = error.config;
        const status = error.response?.status;
        const url = original?.url || "";

        // Évite la boucle infinie sur les endpoints d'auth eux-mêmes
        const isAuthCall = url.includes("/auth/login")
            || url.includes("/auth/refresh")
            || url.includes("/auth/logout");

        if (status === 401 && !original._retried && !isAuthCall) {
            original._retried = true;
            try {
                // Mutualise les refresh concurrents : un seul appel /refresh à la fois
                if (!refreshPromise) {
                    refreshPromise = api.post("/auth/refresh").finally(() => {
                        refreshPromise = null;
                    });
                }
                await refreshPromise;
                return api(original);
            } catch {
                // Refresh impossible → on laisse remonter le 401 d'origine
            }
        }
        return Promise.reject(error);
    },
);

export function formatApiError(detail) {
    if (detail == null) return "Une erreur est survenue. Veuillez réessayer.";
    if (typeof detail === "string") return detail;
    if (Array.isArray(detail))
        return detail
            .map((e) => (e && typeof e.msg === "string" ? e.msg : JSON.stringify(e)))
            .join(" ");
    if (detail && typeof detail.msg === "string") return detail.msg;
    return String(detail);
}

export default api;
