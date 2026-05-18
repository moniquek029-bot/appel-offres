// src/App.jsx
import React from 'react';
// ✅ IMPORT COMPLET : ajoute Link et Navigate
import { BrowserRouter as Router, Routes, Route, Navigate, Link } from 'react-router-dom';
import Navbar from './components/Navbar';
import { AuthProvider, useAuth } from './context/AuthContext';

// Pages
import Home from './pages/Home';
import JobDetail from './pages/JobDetail';
import Register from './pages/Register';
import Login from './pages/Login';
import Offres from './pages/Offres';
import APropos from './pages/APropos';
import ExpertDashboard from './pages/ExpertDashboard';
import BureauDashboard from './pages/BureauDashboard';
import ExpertProfile from './pages/ExpertProfile';

// =============================================================================
// COMPOSANT DE PROTECTION DE ROUTES
// =============================================================================
const ProtectedRoute = ({ children, allowedRoles = [] }) => {
  const { user, loading } = useAuth();
  
  if (loading) {
    return (
      <div className="container py-5 text-center">
        <div className="spinner-border text-primary" role="status">
          <span className="visually-hidden">Chargement...</span>
        </div>
      </div>
    );
  }
  
  if (!user) {
    return <Navigate to="/login" replace />;
  }
  
  if (allowedRoles.length > 0 && !allowedRoles.includes(user.role)) {
    return <Navigate to="/" replace />;
  }
  
  return children;
};

// =============================================================================
// COMPOSANT DE REDIRECTION DASHBOARD
// =============================================================================
const DashboardRedirect = () => {
  const { user } = useAuth();
  
  if (!user) {
    return <Navigate to="/login" replace />;
  }
  
  if (user.role === 'EXPERT') {
    return <Navigate to="/expert/dashboard" replace />;
  } else if (user.role === 'BUREAU' || user.role === 'BUREAU_ETUDE') {
    return <Navigate to="/bureau/dashboard" replace />;
  }
  
  return <Navigate to="/" replace />;
};

// =============================================================================
// APPLICATION PRINCIPALE
// =============================================================================
function App() {
  return (
    <AuthProvider>
      <Router>
        <div className="d-flex flex-column min-vh-100">
          <Navbar />
          
          <main className="flex-grow-1 bg-light">
            <Routes>
              {/* === ROUTES PUBLIQUES === */}
              <Route path="/" element={<Home />} />
              <Route path="/offres" element={<Offres />} />
              <Route path="/offres/:id" element={<JobDetail />} />
              <Route path="/login" element={<Login />} />
              <Route path="/register" element={<Register />} />
              <Route path="/a-propos" element={<APropos />} />

              {/* === ROUTES EXPERT (PROTÉGÉES) === */}
              <Route 
                path="/expert/dashboard" 
                element={
                  <ProtectedRoute allowedRoles={['EXPERT']}>
                    <ExpertDashboard />
                  </ProtectedRoute>
                } 
              />
              
              <Route 
                path="/expert/profile" 
                element={
                  <ProtectedRoute allowedRoles={['EXPERT']}>
                    <ExpertProfile />
                  </ProtectedRoute>
                } 
              />
              
              <Route 
                path="/expert/criteres" 
                element={
                  <ProtectedRoute allowedRoles={['EXPERT']}>
                    {/* Page fallback avec Link correctement importé */}
                    <div className="container py-5">
                      <h2>🎯 Mes critères de recherche</h2>
                      <p className="text-muted">Fonctionnalité en cours de développement</p>
                      <Link to="/expert/dashboard" className="btn btn-outline-secondary">
                        ← Retour au dashboard
                      </Link>
                    </div>
                  </ProtectedRoute>
                } 
              />

              {/* === ROUTES BUREAU (PROTÉGÉES) === */}
              <Route 
                path="/bureau/dashboard" 
                element={
                  <ProtectedRoute allowedRoles={['BUREAU', 'BUREAU_ETUDE']}>
                    <BureauDashboard />
                  </ProtectedRoute>
                } 
              />

              {/* === REDIRECTION INTELLIGENTE /dashboard === */}
              <Route path="/dashboard" element={<DashboardRedirect />} />

              {/* === ROUTE PAR DÉFAUT === */}
              <Route path="*" element={<Navigate to="/" replace />} />
            </Routes>
          </main>
          
          <footer className="bg-dark text-white py-3 text-center small">
            <div className="container">
              © 2026 Plateforme Appels d'Offres • Expertise-ID
            </div>
          </footer>
        </div>
      </Router>
    </AuthProvider>
  );
}

export default App;