// src/pages/RegisterExpert.jsx - VERSION CORRIGÉE
import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import api from '../services/api';

const RegisterExpert = () => {
  const [step, setStep] = useState(1);
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    password_confirm: '',
    last_name: '',
    first_name: '',
    genre: '',
    date_naissance: '',
    telephone: '',
    pays: 'BF',
    adresse: '',
    competences: '',
    experience: '',
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
    { code: 'CD', name: '🇨🇩 RDC' },
    { code: 'GA', name: '🇬🇦 Gabon' },
    { code: 'TD', name: '🇹🇩 Tchad' },
    { code: 'LR', name: '🇱🇷 Liberia' },
    { code: 'NG', name: '🇳🇬 Nigeria' },
    { code: 'GH', name: '🇬🇭 Ghana' },
    { code: 'SL', name: '🇸🇱 Sierra Leone' },
    { code: 'GW', name: '🇬🇼 Guinée-Bissau' },
  ];

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
    // Clear error when user types
    if (error) setError('');
  };

  const validateStep1 = () => {
    if (!formData.email || !formData.email.includes('@')) {
      setError('Veuillez entrer un email valide');
      return false;
    }
    if (formData.password !== formData.password_confirm) {
      setError('Les mots de passe ne correspondent pas');
      return false;
    }
    if (formData.password.length < 8) {
      setError('Le mot de passe doit contenir au moins 8 caractères');
      return false;
    }
    return true;
  };

  const validateStep2 = () => {
    if (!formData.last_name || !formData.first_name) {
      setError('Veuillez entrer votre nom et prénom');
      return false;
    }
    if (!formData.genre) {
      setError('Veuillez sélectionner votre sexe');
      return false;
    }
    if (!formData.date_naissance) {
      setError('Veuillez entrer votre date de naissance');
      return false;
    }
    if (!formData.telephone) {
      setError('Veuillez entrer votre numéro de téléphone');
      return false;
    }
    return true;
  };

  const nextStep = () => {
    // ✅ Valider l'étape courante avant de passer à la suivante
    if (step === 1 && !validateStep1()) return;
    if (step === 2 && !validateStep2()) return;
    
    setError('');
    
    // ✅ Utiliser setTimeout pour éviter les erreurs de réconciliation React
    setTimeout(() => {
      setStep(prev => prev + 1);
      window.scrollTo({ top: 0, behavior: 'smooth' });
    }, 50);
  };

  const prevStep = () => {
    setError('');
    setTimeout(() => {
      setStep(prev => prev - 1);
      window.scrollTo({ top: 0, behavior: 'smooth' });
    }, 50);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    
    try {
      const userData = {
        email: formData.email,
        password: formData.password,
        password_confirm: formData.password_confirm,
        role: 'EXPERT',
        first_name: formData.first_name,
        last_name: formData.last_name,
        telephone: formData.telephone,
        pays: formData.pays,
        adresse: formData.adresse || '',
        // Champs optionnels pour le profil expert
        date_naissance: formData.date_naissance || null,
        genre: formData.genre || '',
        competences: formData.competences || '',
        experience: formData.experience || '',
      };
      
      const response = await api.post('/auth/register/', userData);
      console.log('✅ Inscription réussie:', response.data);
      
      setSuccess('✅ Compte créé avec succès ! Redirection...');
      
      // ✅ Redirection avec délai pour éviter les erreurs React
      setTimeout(() => {
        navigate('/login', { state: { registered: true } });
      }, 1500);
      
    } catch (err) {
      console.error('❌ Erreur inscription:', err.response?.data || err.message);
      
      if (err.response?.data) {
        const errors = err.response.data;
        if (errors.email) setError(`Email: ${Array.isArray(errors.email) ? errors.email.join(', ') : errors.email}`);
        else if (errors.password) setError(`Mot de passe: ${Array.isArray(errors.password) ? errors.password.join(', ') : errors.password}`);
        else if (errors.detail) setError(errors.detail);
        else if (typeof errors === 'object' && Object.keys(errors).length > 0) {
          const firstError = Object.values(errors)[0];
          setError(Array.isArray(firstError) ? firstError[0] : String(firstError));
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

  // ✅ Composant helper pour les labels (évite d'utiliser <Text>)
  const Label = ({ children, htmlFor, required = false }) => (
    <label htmlFor={htmlFor} className="form-label fw-semibold">
      {children}{required && <span className="text-danger ms-1">*</span>}
    </label>
  );

  return (
    <div className="container py-4">
      <div className="row justify-content-center">
        <div className="col-md-8 col-lg-7">
          
          {/* Barre de progression */}
          <div className="mb-4">
            <div className="d-flex justify-content-between mb-2">
              <span className={`small ${step >= 1 ? 'text-primary fw-bold' : 'text-muted'}`}>
                Étape 1
              </span>
              <span className={`small ${step >= 2 ? 'text-primary fw-bold' : 'text-muted'}`}>
                Étape 2
              </span>
              <span className={`small ${step >= 3 ? 'text-primary fw-bold' : 'text-muted'}`}>
                Étape 3
              </span>
            </div>
            <div className="progress" style={{ height: '8px' }}>
              <div 
                className="progress-bar bg-primary transition-width" 
                style={{ width: `${(step / 3) * 100}%`, transition: 'width 0.3s ease' }}
              ></div>
            </div>
            <p className="text-muted small mt-2 mb-0">
              {step === 1 && 'Choix de vos identifiants'}
              {step === 2 && 'Vos informations personnelles'}
              {step === 3 && 'Votre profil professionnel'}
            </p>
          </div>

          <div className="card shadow border-0 rounded-4">
            <div className="card-body p-4 p-md-5">
              
              <h3 className="text-center mb-4 fw-bold text-primary">
                {step === 1 && '🔐 Créer un compte'}
                {step === 2 && '👤 Informations personnelles'}
                {step === 3 && '💼 Profil professionnel'}
              </h3>
              
              {error && (
                <div className="alert alert-danger alert-dismissible fade show small py-2" role="alert">
                  ⚠️ {error}
                  <button type="button" className="btn-close btn-close-sm" onClick={() => setError('')}></button>
                </div>
              )}
              {success && (
                <div className="alert alert-success small py-2" role="alert">
                  ✅ {success}
                </div>
              )}
              
              <form onSubmit={step === 3 ? handleSubmit : (e) => e.preventDefault()}>
                
                {/* ÉTAPE 1 : IDENTIFIANTS */}
                {step === 1 && (
                  <>
                    <div className="mb-4">
                      <Label htmlFor="email" required>Email</Label>
                      <div className="input-group">
                        <span className="input-group-text bg-white">@</span>
                        <input 
                          type="email" 
                          id="email"
                          name="email" 
                          className="form-control" 
                          value={formData.email} 
                          onChange={handleChange} 
                          placeholder="exemple@domaine.com" 
                          required 
                          disabled={loading}
                        />
                      </div>
                    </div>
                    
                    <div className="mb-4">
                      <Label htmlFor="password" required>Mot de passe</Label>
                      <div className="input-group">
                        <span className="input-group-text bg-white">🔑</span>
                        <input 
                          type={showPassword ? "text" : "password"} 
                          id="password"
                          name="password" 
                          className="form-control" 
                          value={formData.password} 
                          onChange={handleChange} 
                          placeholder="••••••••"
                          required 
                          disabled={loading}
                        />
                        <button 
                          type="button" 
                          className="btn btn-outline-secondary" 
                          onClick={() => setShowPassword(!showPassword)}
                          title={showPassword ? "Masquer" : "Afficher"}
                        >
                          {showPassword ? '' : ''}
                        </button>
                      </div>
                      <div className="form-text text-muted small">8 caractères minimum, avec lettres et chiffres</div>
                    </div>
                    
                    <div className="mb-4">
                      <Label htmlFor="password_confirm" required>Confirmation</Label>
                      <div className="input-group">
                        <span className="input-group-text bg-white">🔑</span>
                        <input 
                          type={showConfirmPassword ? "text" : "password"} 
                          id="password_confirm"
                          name="password_confirm" 
                          className="form-control" 
                          value={formData.password_confirm} 
                          onChange={handleChange} 
                          placeholder="••••••••"
                          required 
                          disabled={loading}
                        />
                        <button 
                          type="button" 
                          className="btn btn-outline-secondary" 
                          onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                          title={showConfirmPassword ? "Masquer" : "Afficher"}
                        >
                          {showConfirmPassword ? '' : ''}
                        </button>
                      </div>
                    </div>
                    
                    <button 
                      type="button" 
                      className="btn btn-primary w-100 py-2" 
                      onClick={nextStep}
                      disabled={loading}
                    >
                      Continuer →
                    </button>
                  </>
                )}
                
                {/* ÉTAPE 2 : INFORMATIONS PERSONNELLES */}
                {step === 2 && (
                  <>
                    <div className="row g-3 mb-3">
                      <div className="col-md-6">
                        <Label htmlFor="last_name" required>Nom</Label>
                        <input 
                          type="text" 
                          id="last_name"
                          name="last_name" 
                          className="form-control" 
                          value={formData.last_name} 
                          onChange={handleChange} 
                          required 
                          disabled={loading}
                        />
                      </div>
                      <div className="col-md-6">
                        <Label htmlFor="first_name" required>Prénom(s)</Label>
                        <input 
                          type="text" 
                          id="first_name"
                          name="first_name" 
                          className="form-control" 
                          value={formData.first_name} 
                          onChange={handleChange} 
                          required 
                          disabled={loading}
                        />
                      </div>
                    </div>
                    
                    <div className="row g-3 mb-3">
                      <div className="col-md-6">
                        <Label htmlFor="genre" required>Sexe</Label>
                        <select 
                          id="genre"
                          name="genre" 
                          className="form-select" 
                          value={formData.genre} 
                          onChange={handleChange} 
                          required
                          disabled={loading}
                        >
                          <option value="">Sélectionner</option>
                          <option value="M">Masculin</option>
                          <option value="F">Féminin</option>
                        </select>
                      </div>
                      <div className="col-md-6">
                        <Label htmlFor="date_naissance" required>Date de naissance</Label>
                        <input 
                          type="date" 
                          id="date_naissance"
                          name="date_naissance" 
                          className="form-control" 
                          value={formData.date_naissance} 
                          onChange={handleChange} 
                          required 
                          disabled={loading}
                        />
                      </div>
                    </div>
                    
                    <div className="row g-3 mb-3">
                      <div className="col-md-6">
                        <Label htmlFor="telephone" required>Téléphone</Label>
                        <input 
                          type="tel" 
                          id="telephone"
                          name="telephone" 
                          className="form-control" 
                          value={formData.telephone} 
                          onChange={handleChange} 
                          placeholder="+226 XX XX XX XX" 
                          required 
                          disabled={loading}
                        />
                      </div>
                      <div className="col-md-6">
                        <Label htmlFor="pays">Pays</Label>
                        <select 
                          id="pays"
                          name="pays" 
                          className="form-select" 
                          value={formData.pays} 
                          onChange={handleChange}
                          disabled={loading}
                        >
                          {countries.map(c => (
                            <option key={c.code} value={c.code}>{c.name}</option>
                          ))}
                        </select>
                      </div>
                    </div>
                    
                    <div className="mb-4">
                      <Label htmlFor="adresse">Adresse</Label>
                      <textarea 
                        id="adresse"
                        name="adresse" 
                        className="form-control" 
                        rows="2" 
                        value={formData.adresse} 
                        onChange={handleChange} 
                        placeholder="Votre adresse complète"
                        disabled={loading}
                      />
                    </div>
                    
                    <div className="d-flex gap-2">
                      <button 
                        type="button" 
                        className="btn btn-outline-secondary" 
                        onClick={prevStep}
                        disabled={loading}
                      >
                        ← Retour
                      </button>
                      <button 
                        type="button" 
                        className="btn btn-primary flex-grow-1" 
                        onClick={nextStep}
                        disabled={loading}
                      >
                        Continuer →
                      </button>
                    </div>
                  </>
                )}
                
                {/* ÉTAPE 3 : COMPÉTENCES */}
                {step === 3 && (
                  <>
                    <div className="mb-3">
                      <Label htmlFor="competences">Domaines de compétence</Label>
                      <textarea 
                        id="competences"
                        name="competences" 
                        className="form-control" 
                        rows="3" 
                        value={formData.competences} 
                        onChange={handleChange} 
                        placeholder="Ex: Développement web, Audit financier, Gestion de projet..."
                        disabled={loading}
                      />
                      <div className="form-text text-muted small">Séparez vos compétences par des virgules</div>
                    </div>
                    
                    <div className="mb-4">
                      <Label htmlFor="experience">Expérience professionnelle</Label>
                      <textarea 
                        id="experience"
                        name="experience" 
                        className="form-control" 
                        rows="4" 
                        value={formData.experience} 
                        onChange={handleChange} 
                        placeholder="Décrivez votre parcours, vos réalisations..."
                        disabled={loading}
                      />
                    </div>
                    
                    <div className="d-flex gap-2">
                      <button 
                        type="button" 
                        className="btn btn-outline-secondary" 
                        onClick={prevStep}
                        disabled={loading}
                      >
                      ← Retour
                      </button>
                      <button 
                        type="submit" 
                        className="btn btn-success flex-grow-1" 
                        disabled={loading}
                      >
                        {loading ? (
                          <>
                            <span className="spinner-border spinner-border-sm me-2" role="status"></span>
                            Création...
                          </>
                        ) : '✅ Créer mon compte'}
                      </button>
                    </div>
                  </>
                )}
                
              </form>
              
              <div className="text-center mt-4">
                <span className="text-muted small">Vous avez déjà un compte ? </span>
                <Link to="/login" className="text-decoration-none fw-semibold text-primary">
                Se connecter
                </Link>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default RegisterExpert;