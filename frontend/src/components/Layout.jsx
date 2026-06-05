import { NavLink, Outlet, useNavigate } from "react-router-dom";
import { useEffect, useState } from "react";
import { LayoutGrid, Users, LogOut, Search, ShieldCheck, FileText, Database, UserCircle2, PenLine, FileSearch } from "lucide-react";
import { useAuth } from "@/context/AuthContext";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import api from "@/lib/api";
import logo from "@/assets/logo.png";

const roleLabel = { admin: "Administrateur", ti: "Technicien TI", editeur: "Éditeur", lecteur: "Lecteur" };

export default function Layout() {
    const { user, logout } = useAuth();
    const navigate = useNavigate();
    const isAdminLike = user?.role === "admin" || user?.role === "ti";
    const isTi = user?.role === "ti";
    const [versionInfo, setVersionInfo] = useState(null);

    // Charge la version applicative (visible TI uniquement)
    useEffect(() => {
        if (!isTi) return;
        let cancelled = false;
        api.get("/system/version")
            .then(({ data }) => { if (!cancelled) setVersionInfo(data); })
            .catch(() => { /* silencieux */ });
        return () => { cancelled = true; };
    }, [isTi]);

    const navItems = [
        { to: "/", icon: LayoutGrid, label: "Tableau de bord", testId: "nav-dashboard" },
        { to: "/avocats", icon: Users, label: "Avocats", testId: "nav-avocats" },
        { to: "/rapports", icon: FileText, label: "Rapports", testId: "nav-rapports" },
        ...(isAdminLike ? [{ to: "/utilisateurs", icon: ShieldCheck, label: "Utilisateurs", testId: "nav-users" }] : []),
        ...(isTi ? [{ to: "/connexions", icon: Database, label: "Connexions", testId: "nav-connexions" }] : []),
        ...(isTi ? [{ to: "/mandats", icon: FileSearch, label: "Mandats", testId: "nav-mandats" }] : []),
        ...(isTi ? [{ to: "/parametres/lettres", icon: PenLine, label: "Lettre — signataire", testId: "nav-letter-config" }] : []),
    ];

    const handleLogout = async () => {
        await logout();
        navigate("/login", { replace: true });
    };

    return (
        <div className="h-screen flex bg-slate-50 overflow-hidden">
            {/* Sidebar */}
            <aside className="w-64 border-r border-slate-200 bg-white flex flex-col" data-testid="sidebar">
                <div className="px-6 py-6 border-b border-slate-200">
                    <div className="flex items-center gap-2.5">
                        <img src={logo} alt="GestionCardex" className="h-10 w-10 object-contain" data-testid="sidebar-logo" />
                        <div>
                            <div className="font-display font-bold text-[15px] tracking-tight text-slate-900">
                                GestionCardex
                            </div>
                            <div className="overline" style={{ fontSize: 10 }}>Édition Web</div>
                        </div>
                    </div>
                </div>
                <nav className="flex-1 px-3 py-5 space-y-1">
                    {navItems.map((item) => (
                        <NavLink
                            key={item.to}
                            to={item.to}
                            end={item.to === "/"}
                            data-testid={item.testId}
                            className={({ isActive }) =>
                                `flex items-center gap-3 px-3 py-2 rounded-md text-sm font-medium transition-colors duration-200 ${
                                    isActive
                                        ? "bg-slate-900 text-white"
                                        : "text-slate-700 hover:bg-slate-100"
                                }`
                            }
                        >
                            <item.icon size={16} strokeWidth={2} />
                            {item.label}
                        </NavLink>
                    ))}
                </nav>
                <div className="px-4 py-4 border-t border-slate-200">
                    <NavLink
                        to="/profil"
                        data-testid="nav-profil"
                        className={({ isActive }) =>
                            `flex items-center gap-3 px-3 py-2 rounded-md text-sm font-medium transition-colors duration-200 mb-3 ${
                                isActive
                                    ? "bg-slate-900 text-white"
                                    : "text-slate-700 hover:bg-slate-100"
                            }`
                        }
                    >
                        <UserCircle2 size={16} strokeWidth={2} />
                        Mon profil
                    </NavLink>
                    <div className="text-xs text-slate-500 mb-2 truncate" data-testid="current-user-email">
                        {user?.email}
                    </div>
                    {user?.role && (
                        <Badge className="mb-3 bg-slate-100 text-slate-700 hover:bg-slate-100 rounded-md text-[10px]">
                            {roleLabel[user.role] || user.role}
                        </Badge>
                    )}
                    <Button
                        variant="outline"
                        size="sm"
                        className="w-full justify-start rounded-md"
                        onClick={handleLogout}
                        data-testid="logout-button"
                    >
                        <LogOut size={14} className="mr-2" /> Déconnexion
                    </Button>
                    {isTi && versionInfo && (
                        <div
                            className="mt-3 pt-3 border-t border-slate-200 text-[10px] text-slate-400 leading-tight"
                            data-testid="ti-version-info"
                            title="Visible uniquement par le rôle TI"
                        >
                            <div>Version {versionInfo.version}</div>
                            <div>
                                Déployé le{" "}
                                {versionInfo.deployed_at
                                    ? new Date(versionInfo.deployed_at).toLocaleString("fr-CA", {
                                          dateStyle: "short",
                                          timeStyle: "short",
                                      })
                                    : "—"}
                            </div>
                        </div>
                    )}
                </div>
            </aside>

            {/* Main */}
            <div className="flex-1 flex flex-col min-w-0">
                <header className="h-14 border-b border-slate-200 bg-white/80 backdrop-blur-xl sticky top-0 z-10 flex items-center justify-between px-8">
                    <div className="flex items-center gap-2 text-slate-500 text-sm">
                        <Search size={14} />
                        <span className="overline">Aide juridique du Québec</span>
                    </div>
                    <div className="text-xs text-slate-500">
                        {new Date().toLocaleDateString("fr-CA", { dateStyle: "full" })}
                    </div>
                </header>
                <main className="flex-1 p-6 md:p-8 overflow-auto">
                    <Outlet />
                </main>
            </div>
        </div>
    );
}
