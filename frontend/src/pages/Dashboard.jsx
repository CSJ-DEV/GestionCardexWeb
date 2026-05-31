import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { Users, ShieldCheck, ShieldAlert, Sparkles, ArrowRight } from "lucide-react";
import api from "@/lib/api";
import { Button } from "@/components/ui/button";

// Format français : "99 999" (espace insécable pour les milliers)
const fmt = (n) => Number(n ?? 0).toLocaleString("fr-CA").replace(/\u00A0/g, " ").replace(/,/g, " ");

const StatCard = ({ icon: Icon, label, value, accent, testId }) => (
    <div
        className="bg-white border border-slate-200 rounded-md p-5 hover:shadow-sm transition-shadow"
        data-testid={testId}
    >
        <div className="flex items-start justify-between">
            <div>
                <div className="overline mb-3">{label}</div>
                <div className="font-display text-3xl font-bold tracking-tight text-slate-900">
                    {value}
                </div>
            </div>
            <div
                className="h-9 w-9 rounded-md flex items-center justify-center"
                style={{ background: accent + "1A", color: accent }}
            >
                <Icon size={18} strokeWidth={2} />
            </div>
        </div>
    </div>
);

export default function Dashboard() {
    const [stats, setStats] = useState({ total: 0, actifs: 0, inactifs: 0, mega: 0, nouveaux_30j: 0 });
    const [loading, setLoading] = useState(true);
    const navigate = useNavigate();

    useEffect(() => {
        (async () => {
            try {
                const { data } = await api.get("/avocats/stats");
                setStats(data);
            } catch {
                /* ignore */
            } finally {
                setLoading(false);
            }
        })();
    }, []);

    return (
        <div className="space-y-8" data-testid="dashboard-page">
            <div className="flex items-end justify-between">
                <div>
                    <div className="overline mb-2">Tableau de bord</div>
                    <h1 className="font-display text-4xl sm:text-5xl font-bold tracking-tight text-slate-900">
                        Vue d'ensemble.
                    </h1>
                    <p className="text-sm text-slate-600 mt-2 max-w-lg">
                        Suivi en temps réel des avocats inscrits, statuts et activités récentes.
                    </p>
                </div>
                <Button
                    onClick={() => navigate("/avocats")}
                    className="rounded-md bg-[#0033A0] hover:bg-[#002277] text-white"
                    data-testid="dashboard-go-avocats"
                >
                    Voir tous les avocats <ArrowRight size={16} className="ml-2" />
                </Button>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                <StatCard
                    icon={Users}
                    label="Total Avocats"
                    value={loading ? "…" : fmt(stats.total)}
                    accent="#0033A0"
                    testId="stat-total"
                />
                <StatCard
                    icon={ShieldCheck}
                    label="Actifs"
                    value={loading ? "…" : fmt(stats.actifs)}
                    accent="#16A34A"
                    testId="stat-actifs"
                />
                <StatCard
                    icon={ShieldAlert}
                    label="Inactifs"
                    value={loading ? "…" : fmt(stats.inactifs)}
                    accent="#DC2626"
                    testId="stat-inactifs"
                />
                <StatCard
                    icon={Sparkles}
                    label="Méga"
                    value={loading ? "…" : fmt(stats.mega)}
                    accent="#7C3AED"
                    testId="stat-mega"
                />
            </div>

            <div className="bg-white border border-slate-200 rounded-md p-8">
                <div className="overline mb-2">Activité</div>
                <h2 className="font-display text-2xl font-bold tracking-tight text-slate-900 mb-1">
                    {fmt(stats.nouveaux_30j)} {stats.nouveaux_30j > 1 ? "nouveaux avocats" : "nouvel avocat"}{" "}
                    sur les 30 derniers jours
                </h2>
                <p className="text-sm text-slate-600">
                    Les inscriptions récentes sont synchronisées en temps réel avec la base centrale.
                </p>
            </div>
        </div>
    );
}
