import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';

const Register = () => {
  const [formData, setFormData] = useState({
    nom: '',
    email: '',
    password: '',
    confirmPassword: '',
    role: 'EXPERT'
  });
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleChange = (e) => {
    setFormData({...formData, [e.target.name]: e.target.value});
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    
    if (formData.password !== formData.confirmPassword) {
      setError(' Les mots de passe ne correspondent pas');
      return;
    }
    
    if (formData.password.length < 6) {
      setError(' Le mot de passe doit contenir au moins 6 caractères');
      return;
    }

    // 🔹 Simulation d'inscription (à connecter à l'API Django plus tard)
    try {
      // Exemple d'appel API futur :
      // const response = await api.post('/auth/register/', formData);
      
      console.log(' Données envoyées :', formData);
      
      // Redirection vers login après "inscription"
      alert(' Compte créé avec succès ! Connectez-vous maintenant.');
      navigate('/login');
      
    } catch (err) {
      setError(' Erreur lors de l\'inscription. Réessayez.');
    }
  };

  return (
    <div className="container py-5">
      <div className="row justify-content-center">
        <div className="col-md-6 col-lg-5">
          <div className="card shadow border-0">
            <div className="card-body p-4 p-md-5">
              <h3 className="text-center mb-4 fw-bold"> Créer un compte</h3>
              
              {error && <div className="alert alert-danger small">{error}</div>}
              
              <form onSubmit={handleSubmit}>
                {/* Nom */}
                <div className="mb-3">
                  <label className="form-label fw-medium">Nom complet</label>
                  <input 
                    type="text" 
                    name="nom"
                    className="form-control" 
                    placeholder="Ex: Kabré Monique"
                    value={formData.nom}
                    onChange={handleChange}
                    required 
                  />
                </div>
                
                {/* Email */}
                <div className="mb-3">
                  <label className="form-label fw-medium">Email</label>
                  <input 
                    type="email" 
                    name="email"
                    className="form-control" 
                    placeholder="vous@exemple.com"
                    value={formData.email}
                    onChange={handleChange}
                    required 
                  />
                </div>
                
                {/* Mot de passe */}
                <div className="mb-3">
                  <label className="form-label fw-medium">Mot de passe</label>
                  <input 
                    type="password" 
                    name="password"
                    className="form-control" 
                    placeholder="••••••••"
                    value={formData.password}
                    onChange={handleChange}
                    minLength="6"
                    required 
                  />
                </div>
                
                {/* Confirmation */}
                <div className="mb-4">
                  <label className="form-label fw-medium">Confirmer le mot de passe</label>
                  <input 
                    type="password" 
                    name="confirmPassword"
                    className="form-control" 
                    placeholder="••••••••"
                    value={formData.confirmPassword}
                    onChange={handleChange}
                    required 
                  />
                </div>
                
                {/* Rôle (caché pour la démo) */}
                <input type="hidden" name="role" value="EXPERT" />
                
                {/* Boutons */}
                <button type="submit" className="btn btn-primary w-100 py-2 fw-semibold mb-3">
                   Créer mon compte
                </button>
                
                <div className="text-center">
                  <span className="text-muted">Déjà un compte ? </span>
                  <Link to="/login" className="text-decoration-none fw-medium">Se connecter</Link>
                </div>
              </form>
            </div>
          </div>
          
          {/* Note CDC */}
          <p className="text-center text-muted small mt-3">
             Vos données sont protégées • Conformité RGPD • 2026
          </p>
        </div>
      </div>
    </div>
  );
};

export default Register;