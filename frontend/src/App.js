import "@/App.css";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { AuthProvider } from "@/context/AuthContext";
import ProtectedRoute from "@/components/ProtectedRoute";
import Layout from "@/components/Layout";
import Login from "@/pages/Login";
import Dashboard from "@/pages/Dashboard";
import AvocatsList from "@/pages/AvocatsList";
import Rapports from "@/pages/Rapports";
import Utilisateurs from "@/pages/Utilisateurs";
import LetterConfig from "@/pages/LetterConfig";
import Mandats from "@/pages/Mandats";
import Profil from "@/pages/Profil";
import { Toaster } from "@/components/ui/sonner";

function App() {
    return (
        <div className="App">
            <AuthProvider>
                <BrowserRouter>
                    <Routes>
                        <Route path="/login" element={<Login />} />
                        <Route
                            path="/"
                            element={
                                <ProtectedRoute>
                                    <Layout />
                                </ProtectedRoute>
                            }
                        >
                            <Route index element={<Dashboard />} />
                            <Route path="avocats" element={<AvocatsList />} />
                            <Route path="rapports" element={<Rapports />} />
                            <Route path="utilisateurs" element={<Utilisateurs />} />
                            <Route path="mandats" element={<Mandats />} />
                            <Route path="parametres/lettres" element={<LetterConfig />} />
                            <Route path="profil" element={<Profil />} />
                        </Route>
                    </Routes>
                </BrowserRouter>
                <Toaster richColors position="top-right" />
            </AuthProvider>
        </div>
    );
}

export default App;
