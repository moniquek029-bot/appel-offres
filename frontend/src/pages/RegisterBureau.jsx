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

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    
    try {
      const userData = {
        email: formData.email,
        password: formData.password,
        password_confirm: formData.password_confirm,
        role: 'BUREAU',
        first_name: formData.nom_structure,
        last_name: 'Structure',
        telephone: formData.telephone,
        pays: formData.pays,
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
    <div className="container-fluid p-0">
      {/* ✅ EN-TÊTE COLORÉ AVEC DÉGRADÉ */}
      <div 
        className="py-4 px-4 text-center"
        style={{ 
          background: 'linear-gradient(135deg, #1E3A8A 0%, #172554 100%)',
          color: 'white',
          minHeight: '140px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center'
        }}
      >
        <div>
          <div className="d-flex justify-content-center mb-2">
            <div 
              className="d-flex align-items-center justify-content-center rounded-circle"
              style={{ 
                width: '65px', 
                height: '65px',
                background: 'linear-gradient(135deg, #F59E0B, #1E3A8A)',
                boxShadow: '0 4px 15px rgba(245, 158, 11, 0.4)'
              }}
            >
              <i className="bi bi-building-fill text-white" style={{ fontSize: '1.8rem' }}></i>
            </div>
          </div>
          <h2 className="h3 mb-1 fw-bold">Inscription Bureau d'étude</h2>
          <p className="mb-0 opacity-75" style={{ fontSize: '0.9rem' }}>
            Créez votre compte professionnel
          </p>
        </div>
      </div>

      {/* Corps du formulaire */}
      <div className="container py-4">
        <div className="row justify-content-center">
          <div className="col-md-8 col-lg-7">
            
            {/* Barre de progression */}
            <div className="mb-4">
              <div className="d-flex justify-content-between mb-2">
                <span className={`small ${step >= 1 ? 'fw-bold' : 'text-muted'}`} style={{ color: step >= 1 ? '#1E3A8A' : '' }}>
                  <i className="bi bi-key-fill me-1"></i>
                  Étape 1 - Identifiants
                </span>
                <span className={`small ${step >= 2 ? 'fw-bold' : 'text-muted'}`} style={{ color: step >= 2 ? '#1E3A8A' : '' }}>
                  <i className="bi bi-building me-1"></i>
                  Étape 2 - Informations structure
                </span>
              </div>
              <div className="progress" style={{ height: '8px' }}>
                <div 
                  className="progress-bar" 
                  style={{ 
                    width: `${(step / 2) * 100}%`,
                    background: 'linear-gradient(135deg, #1E3A8A, #F59E0B)'
                  }}
                ></div>
              </div>
            </div>

            <div className="card shadow border-0 rounded-4">
              <div className="card-body p-4 p-md-5">
                
                <div className="text-center mb-4">
                  <h3 className="fw-bold" style={{ color: '#1E3A8A' }}>
                    {step === 1 ? (
                      <><i className="bi bi-person-lock me-2"></i>Vos identifiants</>
                    ) : (
                      <><i className="bi bi-building me-2"></i>Votre structure</>
                    )}
                  </h3>
                </div>
                
                {error && (
                  <div className="alert alert-danger small d-flex align-items-center">
                    <i className="bi bi-exclamation-triangle-fill me-2"></i>
                    {error}
                  </div>
                )}
                {success && (
                  <div className="alert alert-success small d-flex align-items-center">
                    <i className="bi bi-check-circle-fill me-2"></i>
                    {success}
                  </div>
                )}
                
                <form onSubmit={step === 2 ? handleSubmit : (e) => e.preventDefault()} autoComplete="off">
                  
                  {/* ÉTAPE 1 : IDENTIFIANTS */}
                  {step === 1 && (
                    <>
                      {/* ✅ EMAIL AVEC ICÔNE */}
                      <div className="mb-4">
                        <label className="form-label fw-semibold" style={{ color: '#334155' }}>
                          {/*<i className="bi bi-envelope-fill me-1" style={{ color: '#1E3A8A' }}></i>*/}
                          Email de connexion
                        </label>
                        <div className="input-group">
                          <span 
                            className="input-group-text"
                            style={{ 
                              backgroundColor: '#f1f5f9',
                              border: '1px solid #e2e8f0',
                              borderRight: 'none',
                              borderRadius: '8px 0 0 8px',
                              color: '#1E3A8A'
                            }}
                          >
                            <i className="bi bi-envelope-fill"></i>
                          </span>
                          <input 
                            type="email" 
                            name="email" 
                            className="form-control" 
                            placeholder="exemple@email.com"
                            value={formData.email} 
                            onChange={handleChange} 
                            autoComplete="off" 
                            required 
                            style={{ 
                              borderRadius: '0 8px 8px 0',
                              borderColor: '#e2e8f0',
                              borderLeft: 'none'
                            }}
                          />
                        </div>
                      </div>
                      
                      {/* ✅ MOT DE PASSE AVEC ICÔNE */}
                      <div className="mb-4">
                        <label className="form-label fw-semibold" style={{ color: '#334155' }}>
                          {/*<i className="bi bi-lock-fill me-1" style={{ color: '#1E3A8A' }}></i>*/}
                          Mot de passe
                        </label>
                        <div className="input-group">
                          <span 
                            className="input-group-text"
                            style={{ 
                              backgroundColor: '#f1f5f9',
                              border: '1px solid #e2e8f0',
                              borderRight: 'none',
                              borderRadius: '8px 0 0 8px',
                              color: '#1E3A8A'
                            }}
                          >
                            <i className="bi bi-lock-fill"></i>
                          </span>
                          <input 
                            type={showPassword ? "text" : "password"} 
                            name="password" 
                            className="form-control" 
                            placeholder="••••••••"
                            value={formData.password} 
                            onChange={handleChange} 
                            autoComplete="new-password" 
                            required 
                            style={{ 
                              borderRadius: '0',
                              borderColor: '#e2e8f0',
                              borderLeft: 'none',
                              borderRight: 'none'
                            }}
                          />
                          <button 
                            type="button" 
                            className="btn btn-outline-secondary"
                            onClick={() => setShowPassword(!showPassword)}
                            style={{ 
                              borderRadius: '0 8px 8px 0',
                              borderColor: '#e2e8f0',
                              borderLeft: 'none',
                              backgroundColor: '#f1f5f9',
                              color: '#1E3A8A'
                            }}
                          >
                            <i className={`bi ${showPassword ? 'bi-eye-slash-fill' : 'bi-eye-fill'}`}></i>
                          </button>
                        </div>
                        <div className="form-text text-muted small">
                          {/*<i className="bi bi-info-circle me-1"></i>*/}
                          8 caractères minimum, 1 majuscule, 1 minuscule, 1 chiffre
                        </div>
                      </div>
                      
                      {/* ✅ CONFIRMATION MOT DE PASSE AVEC ICÔNE */}
                      <div className="mb-4">
                        <label className="form-label fw-semibold" style={{ color: '#334155' }}>
                          {/*<i className="bi bi-shield-lock-fill me-1" style={{ color: '#1E3A8A' }}></i>*/}
                          Confirmation mot de passe
                        </label>
                        <div className="input-group">
                          <span 
                            className="input-group-text"
                            style={{ 
                              backgroundColor: '#f1f5f9',
                              border: '1px solid #e2e8f0',
                              borderRight: 'none',
                              borderRadius: '8px 0 0 8px',
                              color: '#1E3A8A'
                            }}
                          >
                            <i className="bi bi-shield-lock-fill"></i>
                          </span>
                          <input 
                            type={showConfirmPassword ? "text" : "password"} 
                            name="password_confirm" 
                            className="form-control" 
                            placeholder="••••••••"
                            value={formData.password_confirm} 
                            onChange={handleChange} 
                            required 
                            style={{ 
                              borderRadius: '0',
                              borderColor: '#e2e8f0',
                              borderLeft: 'none',
                              borderRight: 'none'
                            }}
                          />
                          <button 
                            type="button" 
                            className="btn btn-outline-secondary"
                            onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                            style={{ 
                              borderRadius: '0 8px 8px 0',
                              borderColor: '#e2e8f0',
                              borderLeft: 'none',
                              backgroundColor: '#f1f5f9',
                              color: '#1E3A8A'
                            }}
                          >
                            <i className={`bi ${showConfirmPassword ? 'bi-eye-slash-fill' : 'bi-eye-fill'}`}></i>
                          </button>
                        </div>
                      </div>
                      
                      <button 
                        type="button" 
                        className="btn w-100 py-2 fw-semibold shadow-sm"
                        onClick={nextStep}
                        style={{ 
                          borderRadius: '8px',
                          fontSize: '1rem',
                          background: 'linear-gradient(135deg, #1E3A8A, #172554)',
                          border: 'none',
                          color: 'white'
                        }}
                      >
                        <i className="bi bi-arrow-right me-1"></i>
                        Continuer
                      </button>
                    </>
                  )}
                  
                  {/* ÉTAPE 2 : INFORMATIONS STRUCTURE */}
                  {step === 2 && (
                    <>
                      {/* ✅ NOM DE LA STRUCTURE */}
                      <div className="mb-3">
                        <label className="form-label fw-semibold" style={{ color: '#334155' }}>
                          {/*<i className="bi bi-building-fill me-1" style={{ color: '#1E3A8A' }}></i>*/}
                          Nom de la structure <span className="text-danger">*</span>
                        </label>
                        <div className="input-group">
                          <span 
                            className="input-group-text"
                            style={{ 
                              backgroundColor: '#f1f5f9',
                              border: '1px solid #e2e8f0',
                              borderRight: 'none',
                              borderRadius: '8px 0 0 8px',
                              color: '#1E3A8A'
                            }}
                          >
                            <i className="bi bi-building-fill"></i>
                          </span>
                          <input 
                            type="text" 
                            name="nom_structure" 
                            className="form-control" 
                            placeholder="Ex: Expertise Consulting"
                            value={formData.nom_structure} 
                            onChange={handleChange} 
                            required 
                            style={{ 
                              borderRadius: '0 8px 8px 0',
                              borderColor: '#e2e8f0',
                              borderLeft: 'none'
                            }}
                          />
                        </div>
                      </div>
                      
                      {/* ✅ DOMAINE D'ACTIVITÉ */}
                      <div className="mb-3">
                        <label className="form-label fw-semibold" style={{ color: '#334155' }}>
                          {/*<i className="bi bi-briefcase-fill me-1" style={{ color: '#1E3A8A' }}></i>*/}
                          Domaine d'activité <span className="text-danger">*</span>
                        </label>
                        <div className="input-group">
                          <span 
                            className="input-group-text"
                            style={{ 
                              backgroundColor: '#f1f5f9',
                              border: '1px solid #e2e8f0',
                              borderRight: 'none',
                              borderRadius: '8px 0 0 8px',
                              color: '#1E3A8A'
                            }}
                          >
                            <i className="bi bi-briefcase-fill"></i>
                          </span>
                          <input 
                            type="text" 
                            name="domaine_activite" 
                            className="form-control" 
                            placeholder="Ex: Informatique, BTP, Conseil..."
                            value={formData.domaine_activite} 
                            onChange={handleChange} 
                            required 
                            style={{ 
                              borderRadius: '0 8px 8px 0',
                              borderColor: '#e2e8f0',
                              borderLeft: 'none'
                            }}
                          />
                        </div>
                      </div>
                      
                      {/* ✅ TÉLÉPHONE ET EMAIL DE CONTACT */}
                      <div className="row g-3 mb-3">
                        <div className="col-md-6">
                          <label className="form-label fw-semibold" style={{ color: '#334155' }}>
                            {/*<i className="bi bi-telephone-fill me-1" style={{ color: '#1E3A8A' }}></i>*/}
                            Téléphone <span className="text-danger">*</span>
                          </label>
                          <div className="input-group">
                            <span 
                              className="input-group-text"
                              style={{ 
                                backgroundColor: '#f1f5f9',
                                border: '1px solid #e2e8f0',
                                borderRight: 'none',
                                borderRadius: '8px 0 0 8px',
                                color: '#1E3A8A'
                              }}
                            >
                              <i className="bi bi-telephone-fill"></i>
                            </span>
                            <input 
                              type="tel" 
                              name="telephone" 
                              className="form-control" 
                              placeholder="+226 XX XX XX XX"
                              value={formData.telephone} 
                              onChange={handleChange} 
                              required 
                              style={{ 
                                borderRadius: '0 8px 8px 0',
                                borderColor: '#e2e8f0',
                                borderLeft: 'none'
                              }}
                            />
                          </div>
                        </div>
                        <div className="col-md-6">
                          <label className="form-label fw-semibold" style={{ color: '#334155' }}>
                            {/*<i className="bi bi-envelope-fill me-1" style={{ color: '#1E3A8A' }}></i>*/}
                            Email de contact <span className="text-danger">*</span>
                          </label>
                          <div className="input-group">
                            <span 
                              className="input-group-text"
                              style={{ 
                                backgroundColor: '#f1f5f9',
                                border: '1px solid #e2e8f0',
                                borderRight: 'none',
                                borderRadius: '8px 0 0 8px',
                                color: '#1E3A8A'
                              }}
                            >
                              <i className="bi bi-envelope-fill"></i>
                            </span>
                            <input 
                              type="email" 
                              name="email_contact" 
                              className="form-control" 
                              placeholder="contact@structure.com"
                              value={formData.email_contact} 
                              onChange={handleChange} 
                              required 
                              style={{ 
                                borderRadius: '0 8px 8px 0',
                                borderColor: '#e2e8f0',
                                borderLeft: 'none'
                              }}
                            />
                          </div>
                        </div>
                      </div>
                      
                      {/* ✅ PAYS ET SITE WEB */}
                      <div className="row g-3 mb-3">
                        <div className="col-md-6">
                          <label className="form-label fw-semibold" style={{ color: '#334155' }}>
                           {/*<i className="bi bi-globe-americas me-1" style={{ color: '#1E3A8A' }}></i>*/}
                            Pays <span className="text-danger">*</span>
                          </label>
                          <div className="input-group">
                            <span 
                              className="input-group-text"
                              style={{ 
                                backgroundColor: '#f1f5f9',
                                border: '1px solid #e2e8f0',
                                borderRight: 'none',
                                borderRadius: '8px 0 0 8px',
                                color: '#1E3A8A'
                              }}
                            >
                              <i className="bi bi-globe-americas"></i>
                            </span>
                            <select 
                              name="pays" 
                              className="form-select" 
                              value={formData.pays} 
                              onChange={handleChange}
                              style={{ 
                                borderRadius: '0 8px 8px 0',
                                borderColor: '#e2e8f0',
                                borderLeft: 'none'
                              }}
                            >
                              {countries.map(c => (
                                <option key={c.code} value={c.code}>{c.name}</option>
                              ))}
                            </select>
                          </div>
                        </div>
                        <div className="col-md-6">
                          <label className="form-label fw-semibold" style={{ color: '#334155' }}>
                            {/*<i className="bi bi-link-45deg me-1" style={{ color: '#1E3A8A' }}></i>*/}
                            Site web
                          </label>
                          <div className="input-group">
                            <span 
                              className="input-group-text"
                              style={{ 
                                backgroundColor: '#f1f5f9',
                                border: '1px solid #e2e8f0',
                                borderRight: 'none',
                                borderRadius: '8px 0 0 8px',
                                color: '#1E3A8A'
                              }}
                            >
                              <i className="bi bi-link-45deg"></i>
                            </span>
                            <input 
                              type="url" 
                              name="site_web" 
                              className="form-control" 
                              placeholder="https://..."
                              value={formData.site_web} 
                              onChange={handleChange} 
                              style={{ 
                                borderRadius: '0 8px 8px 0',
                                borderColor: '#e2e8f0',
                                borderLeft: 'none'
                              }}
                            />
                          </div>
                        </div>
                      </div>
                      
                      {/* ✅ ADRESSE */}
                      <div className="mb-4">
                        <label className="form-label fw-semibold" style={{ color: '#334155' }}>
                          {/*<i className="bi bi-geo-alt-fill me-1" style={{ color: '#1E3A8A' }}></i>*/}
                          Adresse <span className="text-danger">*</span>
                        </label>
                        <div className="input-group">
                          <span 
                            className="input-group-text align-items-start pt-3"
                            style={{ 
                              backgroundColor: '#f1f5f9',
                              border: '1px solid #e2e8f0',
                              borderRight: 'none',
                              borderRadius: '8px 0 0 8px',
                              color: '#1E3A8A'
                            }}
                          >
                            <i className="bi bi-geo-alt-fill"></i>
                          </span>
                          <textarea 
                            name="adresse" 
                            className="form-control" 
                            rows="2" 
                            placeholder="Adresse complète de la structure"
                            value={formData.adresse} 
                            onChange={handleChange} 
                            required 
                            style={{ 
                              borderRadius: '0 8px 8px 0',
                              borderColor: '#e2e8f0',
                              borderLeft: 'none'
                            }}
                          />
                        </div>
                      </div>
                      
                      <div className="d-flex gap-2">
                        <button 
                          type="button" 
                          className="btn btn-outline-secondary"
                          onClick={prevStep}
                          style={{ borderRadius: '8px' }}
                        >
                          <i className="bi bi-arrow-left me-1"></i>
                          Retour
                        </button>
                        <button 
                          type="submit" 
                          className="btn flex-grow-1 fw-semibold shadow-sm" 
                          disabled={loading}
                          style={{ 
                            borderRadius: '8px',
                            background: 'linear-gradient(135deg, #402a0a, #b09d0d)',
                            border: 'none',
                            color: 'white'
                          }}
                        >
                          {loading ? (
                            <>
                              <span className="spinner-border spinner-border-sm me-2"></span>
                              Création...
                            </>
                          ) : (
                            <>
                              <i className="bi bi-check-circle me-1"></i>
                              Créer mon compte
                            </>
                          )}
                        </button>
                      </div>
                    </>
                  )}
                </form>
                
                <div className="text-center mt-4 pt-3 border-top" style={{ borderColor: '#e2e8f0' }}>
                  <Link 
                    to="/login" 
                    className="text-decoration-none small"
                    style={{ color: '#1E3A8A', fontWeight: '500' }}
                  >
                    <i className="bi bi-arrow-left me-1"></i>
                    J'ai déjà un compte
                  </Link>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default RegisterBureau;