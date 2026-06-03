// src/pages/RegisterBureau.jsx
import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import api from '../services/api';

const RegisterBureau = () => {
  const [step, setStep] = useState(1);
  const [formData, setFormData] = useState({
    // Étape 1 : Identifiants
    email: '',
    password: '',
    password_confirm: '',
    // Étape 2 : Informations structure
    nom_structure: '',
    domaine_activite: '',
    telephone: '',
    email_contact: '',
    pays: 'BF',
    adresse: '',
    site_web: '',
  });
  
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const countries = [
    { code: 'BF', name: '🇧🇫 Burkina Faso' },
    { code: 'CI', name: '🇨🇮 Côte d\'Ivoire' },
    { code: 'SN', name: '🇸🇳 Sénégal' },
    { code: 'ML', name: '🇲🇱 Mali' },
    { code: 'NE', name: '🇳🇪 Niger' },
    { code: 'TG', name: '🇹🇬 Togo' },
    { code: 'BJ', name: '🇧🇯 Bénin' },
    { code: 'CM', name: '🇨🇲 Cameroun' },
  ];

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const nextStep = () => {
    if (step === 1) {
      if (!formData.email) {
        setError('Veuillez entrer votre email');
        return;
      }
      if (formData.password !== formData.password_confirm) {
        setError('Les mots de passe ne correspondent pas');
        return;
      }
      if (formData.password.length < 8) {
        setError('Le mot de passe doit contenir au moins 8 caractères');
        return;
      }
    }
    setError('');
    setStep(step + 1);
    window.scrollTo(0, 0);
  };

  const prevStep = () => {
    setStep(step - 1);
    window.scrollTo(0, 0);
  };
// src/pages/RegisterBureau.jsx - CORRIGÉ

const handleSubmit = async (e) => {
  e.preventDefault();
  setError('');
  setLoading(true);
  
  try {
    // ✅ DONNÉES CORRESPONDANT EXACTEMENT AU BACKEND
    const userData = {
      email: formData.email,
      password: formData.password,
      password_confirm: formData.password_confirm,
      role: 'BUREAU',
      first_name: formData.nom_structure,
      last_name: 'Structure',
      telephone: formData.telephone,
      pays: formData.pays,
      // Champs spécifiques
      adresse: formData.adresse || '',
    };
    
    console.log('📤 Envoi des données:', userData);
    
    const response = await api.post('/auth/register/', userData);
    console.log('✅ Réponse:', response.data);
    
    setSuccess('✅ Compte créé avec succès ! Redirection...');
    setTimeout(() => navigate('/login'), 2000);
    
  } catch (err) {
    console.error('❌ Erreur détaillée:', err.response?.data);
    
    if (err.response?.data) {
      const errors = err.response.data;
      if (errors.email) setError(`Email: ${errors.email.join(', ')}`);
      else if (errors.password) setError(`Mot de passe: ${errors.password.join(', ')}`);
      else if (errors.detail) setError(errors.detail);
      else if (typeof errors === 'object') {
        const firstError = Object.values(errors)[0];
        setError(firstError?.[0] || 'Erreur lors de l\'inscription');
      } else {
        setError('Erreur lors de l\'inscription');
      }
    } else {
      setError('Erreur réseau. Vérifiez que le serveur est démarré.');
    }
  } finally {
    setLoading(false);
  }
};
  return (
    <div className="container py-4">
      <div className="row justify-content-center">
        <div className="col-md-8 col-lg-7">
          
          {/* Barre de progression */}
          <div className="mb-4">
            <div className="d-flex justify-content-between mb-2">
              <span className={`small ${step >= 1 ? 'text-primary fw-bold' : 'text-muted'}`}>
                Étape 1 - Identifiants
              </span>
              <span className={`small ${step >= 2 ? 'text-primary fw-bold' : 'text-muted'}`}>
                Étape 2 - Informations structure
              </span>
            </div>
            <div className="progress" style={{ height: '8px' }}>
              <div className="progress-bar bg-primary" style={{ width: `${(step / 2) * 100}%` }}></div>
            </div>
          </div>

          <div className="card shadow border-0 rounded-4">
            <div className="card-body p-4 p-md-5">
              
              <div className="text-center mb-4">
                <div className="display-1 mb-2"></div>
                <h3 className="fw-bold text-primary">Inscription Bureau d'étude</h3>
              </div>
              
              {error && <div className="alert alert-danger small">{error}</div>}
              {success && <div className="alert alert-success small">{success}</div>}
              
              <form onSubmit={step === 2 ? handleSubmit : (e) => e.preventDefault()}>
                
                {/* ÉTAPE 1 : IDENTIFIANTS */}
                {step === 1 && (
                  <>
                    <div className="mb-4">
                      <label className="form-label fw-semibold">Email de connexion</label>
                      <div className="input-group">
                        <span className="input-group-text bg-white"></span>
                        <input type="email" name="email" className="form-control" value={formData.email} onChange={handleChange} required />
                      </div>
                    </div>
                    
                    <div className="mb-4">
                      <label className="form-label fw-semibold">Mot de passe</label>
                      <div className="input-group">
                        <span className="input-group-text bg-white"></span>
                        <input type={showPassword ? "text" : "password"} name="password" className="form-control" value={formData.password} onChange={handleChange} required />
                        <button type="button" className="btn btn-outline-secondary" onClick={() => setShowPassword(!showPassword)}>
                          {showPassword ? '' : ''}
                        </button>
                      </div>
                      <div className="form-text text-muted small">8 caractères minimum, 1 majuscule, 1 minuscule, 1 chiffre</div>
                    </div>
                    
                    <div className="mb-4">
                      <label className="form-label fw-semibold">Confirmation mot de passe</label>
                      <div className="input-group">
                        <span className="input-group-text bg-white"></span>
                        <input type={showConfirmPassword ? "text" : "password"} name="password_confirm" className="form-control" value={formData.password_confirm} onChange={handleChange} required />
                        <button type="button" className="btn btn-outline-secondary" onClick={() => setShowConfirmPassword(!showConfirmPassword)}>
                          {showConfirmPassword ? '' : ''}
                        </button>
                      </div>
                    </div>
                    
                    <button type="button" className="btn btn-primary w-100 py-2" onClick={nextStep}>
                      Continuer →
                    </button>
                  </>
                )}
                
                {/* ÉTAPE 2 : INFORMATIONS STRUCTURE */}
                {step === 2 && (
                  <>
                    <div className="mb-3">
                      <label className="form-label fw-semibold">Nom de la structure *</label>
                      <input type="text" name="nom_structure" className="form-control" value={formData.nom_structure} onChange={handleChange} required />
                    </div>
                    
                    <div className="mb-3">
                      <label className="form-label fw-semibold">Domaine d'activité *</label>
                      <input type="text" name="domaine_activite" className="form-control" value={formData.domaine_activite} onChange={handleChange} required />
                    </div>
                    
                    <div className="row g-3 mb-3">
                      <div className="col-md-6">
                        <label className="form-label fw-semibold">Téléphone *</label>
                        <input type="tel" name="telephone" className="form-control" value={formData.telephone} onChange={handleChange} required />
                      </div>
                      <div className="col-md-6">
                        <label className="form-label fw-semibold">Email de contact *</label>
                        <input type="email" name="email_contact" className="form-control" value={formData.email_contact} onChange={handleChange} required />
                      </div>
                    </div>
                    
                    <div className="row g-3 mb-3">
                      <div className="col-md-6">
                        <label className="form-label fw-semibold">Pays *</label>
                        <select name="pays" className="form-select" value={formData.pays} onChange={handleChange}>
                          {countries.map(c => (
                            <option key={c.code} value={c.code}>{c.name}</option>
                          ))}
                        </select>
                      </div>
                      <div className="col-md-6">
                        <label className="form-label fw-semibold">Site web</label>
                        <input type="url" name="site_web" className="form-control" value={formData.site_web} onChange={handleChange} placeholder="https://..." />
                      </div>
                    </div>
                    
                    <div className="mb-4">
                      <label className="form-label fw-semibold">Adresse *</label>
                      <textarea name="adresse" className="form-control" rows="2" value={formData.adresse} onChange={handleChange} required />
                    </div>
                    
                    <div className="d-flex gap-2">
                      <button type="button" className="btn btn-outline-secondary" onClick={prevStep}>← Retour</button>
                      <button type="submit" className="btn btn-success flex-grow-1" disabled={loading}>
                        {loading ? 'Création...' : '✅ Créer mon compte'}
                      </button>
                    </div>
                  </>
                )}
              </form>
              
              <div className="text-center mt-4">
                <Link to="/login" className="text-decoration-none small text-primary">J'ai déjà un compte</Link>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default RegisterBureau;