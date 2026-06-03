// src/pages/Login.jsx
import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

const Login = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [rememberMe, setRememberMe] = useState(false);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { login, user } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    const result = await login(email, password);
    
    if (result.success) {
      if (user?.role === 'EXPERT') {
        navigate('/expert/dashboard');
      } else if (user?.role === 'BUREAU') {
        navigate('/bureau/dashboard');
      } else {
        navigate('/');
      }
    } else {
      setError(result.error || 'Email ou mot de passe incorrect');
    }
    setLoading(false);
  };

  return (
    <div className="container py-5">
      <div className="row justify-content-center">
        {/* ✅ CONTENEUR PLUS LARGE : col-md-6 col-lg-5 (au lieu de col-md-5 col-lg-4) */}
        <div className="col-md-6 col-lg-5">
          
          <div className="text-center mb-4">
            <div className="bg-primary bg-opacity-10 rounded-circle d-inline-flex p-3 mb-2">
              <span className="display-6">🔐</span>
            </div>
            <h1 className="display-6 fw-bold text-primary">Carrière</h1>
            <p className="text-muted">Accédez à votre espace personnel</p>
          </div>
          
          <div className="card shadow-lg border-0 rounded-4">
            <div className="card-body p-4 p-md-5">
              
              {error && <div className="alert alert-danger small mb-3">{error}</div>}
              
              <form onSubmit={handleSubmit}>
                <div className="mb-3">
                  <label className="form-label text-muted small fw-semibold">E-mail</label>
                  <div className="input-group">
                    <span className="input-group-text bg-white border-end-0 text-muted">📧</span>
                    <input 
                      type="email" 
                      className="form-control border-start-0 ps-0" 
                      placeholder="exemple@email.com" 
                      value={email} 
                      onChange={e => setEmail(e.target.value)} 
                      required 
                    />
                  </div>
                </div>
                
                <div className="mb-3">
                  <label className="form-label text-muted small fw-semibold">Mot de passe</label>
                  <div className="input-group">
                    <span className="input-group-text bg-white border-end-0 text-muted">🔒</span>
                    <input 
                      type={showPassword ? "text" : "password"} 
                      className="form-control border-start-0 ps-0 border-end-0" 
                      placeholder="••••••••" 
                      value={password} 
                      onChange={e => setPassword(e.target.value)} 
                      required 
                      style={{ backgroundColor: '#f8f9fa' }}
                    />
                    {/* ✅ BOUTON ŒIL : Même fond que le champ (#f8f9fa) */}
                    <button 
                      type="button" 
                      className="btn btn-outline-secondary border-start-0" 
                      onClick={() => setShowPassword(!showPassword)}
                      style={{ backgroundColor: '#f8f9fa' }}
                    >
                      {showPassword ? '🙈' : '👁️'}
                    </button>
                  </div>
                </div>
                
                <div className="d-flex justify-content-between align-items-center mb-4">
                  <div className="form-check">
                    <input 
                      type="checkbox" 
                      className="form-check-input" 
                      id="rememberMe" 
                      checked={rememberMe} 
                      onChange={(e) => setRememberMe(e.target.checked)} 
                    />
                    <label className="form-check-label small text-muted" htmlFor="rememberMe">
                      Gardez-moi connecté
                    </label>
                  </div>
                  <button 
                    type="button" 
                    className="btn btn-link text-primary text-decoration-none small p-0" 
                    onClick={() => alert('Fonctionnalité à venir')}
                  >
                    Mot de passe oublié ?
                  </button>
                </div>
                
                <button 
                  type="submit" 
                  className="btn btn-primary w-100 py-2 fw-semibold mb-3" 
                  disabled={loading}
                >
                  {loading ? 'Connexion...' : 'Se connecter'}
                </button>
                
                <div className="text-center">
                  <span className="text-muted small">Vous n'avez pas de compte ? </span>
                  <Link to="/register" className="text-decoration-none fw-semibold small text-primary">
                    Inscrivez-vous
                  </Link>
                </div>
              </form>
            </div>
          </div>
          
          <p className="text-center text-muted small mt-4">© 2026 Plateforme Appels d'Offres</p>
        </div>
      </div>
    </div>
  );
};

export default Login;