import { NavLink, Outlet, useNavigate } from "react-router-dom";
import { LayoutGrid, Users, LogOut, Scale, Search, ShieldCheck, FileText, Database } from "lucide-react";
import { useAuth } from "@/context/AuthContext";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";

const roleLabel = { admin: "Administrateur", ti: "Technicien TI", editeur: "Éditeur", lecteur: "Lecteur" };

export default function Layout() {
    const { user, logout } = useAuth();
    const navigate = useNavigate();
    const isAdminLike = user?.role === "admin" || user?.role === "ti";

    const navItems = [
        { to: "/", icon: LayoutGrid, label: "Tableau de bord", testId: "nav-dashboard" },
        { to: "/avocats", icon: Users, label: "Avocats", testId: "nav-avocats" },
        { to: "/rapports", icon: FileText, label: "Rapports", testId: "nav-rapports" },
        ...(isAdminLike ? [{ to: "/utilisateurs", icon: ShieldCheck, label: "Utilisateurs", testId: "nav-users" }] : []),
        ...(isAdminLike ? [{ to: "/connexions", icon: Database, label: "Connexions", testId: "nav-connexions" }] : []),
    ];

    const handleLogout = async () => {
        await logout();
        navigate("/login", { replace: true });
    };

    return (
        <div className="min-h-screen flex bg-slate-50">
            {/* Sidebar */}
            <aside className="w-64 border-r border-slate-200 bg-white flex flex-col" data-testid="sidebar">
                <div className="px-6 py-6 border-b border-slate-200">
                    <div className="flex items-center gap-2.5">
                        <div className="h-9 w-9 rounded-md bg-[#0033A0] text-white flex items-center justify-center">
                            <Scale size={18} strokeWidth={2.25} />
                        </div>
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
                </div>
            </aside>

            {/* Main */}
            <div className="flex-1 flex flex-col min-w-0">
                <header className="h-14 border-b border-slate-200 bg-white/80 backdrop-blur-xl sticky top-0 z-10 flex items-center justify-between px-8">
                    <div className="flex items-center gap-2 text-slate-500 text-sm">
                        <Search size={14} />
                        <span className="overline">Quebec • Barreau</span>
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
