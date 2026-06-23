// src/App.jsx
import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Navbar from './components/Navbar';
import Footer from './components/Footer';
import { AuthProvider, useAuth } from './context/AuthContext';
import ErrorBoundary from './components/ErrorBoundary'; 

import ForgotPassword from './pages/ForgotPassword';  
import ResetPassword from './pages/ResetPassword';     
// Pages principales
import Home from './pages/Home';
import JobDetail from './pages/JobDetail';
import Login from './pages/Login';
import Offres from './pages/Offres';
import APropos from './pages/APropos';

// Pages d'inscription
import ChooseRole from './pages/ChooseRole';
import RegisterExpert from './pages/RegisterExpert';
import RegisterBureau from './pages/RegisterBureau';

// Pages Dashboard
import ExpertDashboard from './pages/ExpertDashboard';
import BureauDashboard from './pages/BureauDashboard';
import BureauProfile from './pages/BureauProfile';
import ExpertProfile from './pages/ExpertProfile';
import ExpertCriteres from './pages/ExpertCriteres';
import AdminDashboard from './pages/AdminDashboard';
import ExpertSuggestions from './pages/ExpertSuggestions';

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
  } else if (user.role === 'ADMIN') {
    return <Navigate to="/admin/dashboard" replace />;
  }
  
  return <Navigate to="/" replace />;
};

// =============================================================================
// APPLICATION PRINCIPALE - CORRIGÉE AVEC ERRORBOUNDARY
// =============================================================================
function App() {
  return (
    <AuthProvider>
      {/* ✅ ErrorBoundary DOIT envelopper le Router pour capturer TOUTES les erreurs */}
      <ErrorBoundary>
        <Router>
          <div className="d-flex flex-column min-vh-100">
            <Navbar />
            
            <main className="flex-grow-1">
              <Routes>
                {/* Routes publiques */}
                <Route path="/" element={<Home />} />
                <Route path="/offres" element={<Offres />} />
                <Route path="/offres/:id" element={<JobDetail />} />
                <Route path="/login" element={<Login />} />
                <Route path="/a-propos" element={<APropos />} />

                <Route path="/expert/suggestions" element={<ProtectedRoute><ExpertSuggestions /></ProtectedRoute>} />

                <Route path="/forgot-password" element={<ForgotPassword />} />      
                <Route path="/reset-password/:token" element={<ResetPassword />} />

                {/* Routes d'inscription */}
                <Route path="/register" element={<ChooseRole />} />
                <Route path="/register/expert" element={<RegisterExpert />} />
                <Route path="/register/bureau" element={<RegisterBureau />} />

                {/* Routes Expert */}
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
                  path="/bureau/profile" 
                  element={
                    <ProtectedRoute allowedRoles={['BUREAU', 'BUREAU_ETUDE']}>
                      <BureauProfile />
                    </ProtectedRoute>
                  } 
                />  


                <Route 
                  path="/expert/criteres" 
                  element={
                    <ProtectedRoute allowedRoles={['EXPERT']}>
                      <ExpertCriteres />
                    </ProtectedRoute>
                  } 
                />

                {/* Routes Bureau */}
                <Route 
                  path="/bureau/dashboard" 
                  element={
                    <ProtectedRoute allowedRoles={['BUREAU', 'BUREAU_ETUDE']}>
                      <BureauDashboard />
                    </ProtectedRoute>
                  } 
                />

                {/* Routes Admin */}
                <Route 
                  path="/admin/dashboard" 
                  element={
                    <ProtectedRoute allowedRoles={['ADMIN']}>
                      <AdminDashboard />
                    </ProtectedRoute>
                  } 
                />

                {/* Redirection dashboard */}
                <Route path="/dashboard" element={<DashboardRedirect />} />

                {/* 404 */}
                <Route path="*" element={<Navigate to="/" replace />} />
              </Routes>
            </main>
            
            {/* ✅ Footer global - présent sur toutes les pages */}
            <Footer />
          </div>
        </Router>
      </ErrorBoundary>
    </AuthProvider>
  );


  
}

export default App;