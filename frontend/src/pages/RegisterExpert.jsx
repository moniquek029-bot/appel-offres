// src/pages/RegisterExpert.jsx - VERSION CORRIGÉE AVEC ICÔNES
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
    if (step === 1 && !validateStep1()) return;
    if (step === 2 && !validateStep2()) return;
    
    setError('');
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
        date_naissance: formData.date_naissance || null,
        genre: formData.genre || '',
        competences: formData.competences || '',
        experience: formData.experience || '',
      };
      
      const response = await api.post('/auth/register/', userData);
      console.log('✅ Inscription réussie:', response.data);
      
      setSuccess('✅ Compte créé avec succès ! Redirection...');
      
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

  // ✅ Style commun pour les icônes dans les champs
  const iconStyle = {
    backgroundColor: '#f1f5f9',
    border: '1px solid #e2e8f0',
    borderRight: 'none',
    borderRadius: '8px 0 0 8px',
    color: '#1E3A8A',
    width: '45px',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center'
  };

  const inputStyle = {
    borderColor: '#e2e8f0',
    borderLeft: 'none'
  };

  const inputStyleMiddle = {
    borderColor: '#e2e8f0',
    borderLeft: 'none',
    borderRight: 'none',
    borderRadius: '0'
  };

  const btnEyeStyle = {
    borderColor: '#e2e8f0',
    borderLeft: 'none',
    backgroundColor: '#f1f5f9',
    color: '#1E3A8A',
    borderRadius: '0 8px 8px 0'
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
            {/*<div 
              className="d-flex align-items-center justify-content-center rounded-circle"
              style={{ 
                width: '65px', 
                height: '65px',
                background: 'linear-gradient(135deg, #F59E0B, #1E3A8A)',
                boxShadow: '0 4px 15px rgba(245, 158, 11, 0.4)'
              }}
            >
              <i className="bi bi-person-badge-fill text-white" style={{ fontSize: '1.8rem' }}></i>
            </div>*/}
          </div>
          <h2 className="h3 mb-1 fw-bold">Inscription Expert</h2>
          <p className="mb-0 opacity-75" style={{ fontSize: '0.9rem' }}>
            Rejoignez notre plateforme d'expertise
          </p>
        </div>
      </div>

      {/* Corps du formulaire */}
      <div className="container py-4">
        <div className="row justify-content-center">
          <div className="col-md-8 col-lg-7">
            
            {/* Barre de progression avec dégradé */}
            <div className="mb-4">
              <div className="d-flex justify-content-between mb-2">
                <span 
                  className="small" 
                  style={{ 
                    fontWeight: step >= 1 ? 'bold' : 'normal',
                    color: step >= 1 ? '#1E3A8A' : '#6c757d'
                  }}
                >
                  <i className="bi bi-key-fill me-1"></i>
                  Étape 1 - Identifiants
                </span>
                <span 
                  className="small" 
                  style={{ 
                    fontWeight: step >= 2 ? 'bold' : 'normal',
                    color: step >= 2 ? '#1E3A8A' : '#6c757d'
                  }}
                >
                  <i className="bi bi-person-fill me-1"></i>
                  Étape 2 - Informations
                </span>
                <span 
                  className="small" 
                  style={{ 
                    fontWeight: step >= 3 ? 'bold' : 'normal',
                    color: step >= 3 ? '#1E3A8A' : '#6c757d'
                  }}
                >
                  <i className="bi bi-briefcase-fill me-1"></i>
                  Étape 3 - Profil
                </span>
              </div>
              <div className="progress" style={{ height: '8px' }}>
                <div 
                  className="progress-bar" 
                  style={{ 
                    width: `${(step / 3) * 100}%`, 
                    background: 'linear-gradient(135deg, #1E3A8A, #F59E0B)',
                    transition: 'width 0.3s ease'
                  }}
                ></div>
              </div>
            </div>

            <div className="card shadow border-0 rounded-4">
              <div className="card-body p-4 p-md-5">
                
                <h3 className="text-center mb-4 fw-bold" style={{ color: '#1E3A8A' }}>
                  {step === 1 && <><i className="bi bi-person-lock me-2"></i>Vos identifiants</>}
                  {step === 2 && <><i className="bi bi-person-lines-fill me-2"></i>Informations personnelles</>}
                  {step === 3 && <><i className="bi bi-briefcase-fill me-2"></i>Votre profil professionnel</>}
                </h3>
                
                {error && (
                  <div className="alert alert-danger alert-dismissible fade show small py-2 d-flex align-items-center" role="alert">
                    <i className="bi bi-exclamation-triangle-fill me-2"></i>
                    <span className="flex-grow-1">{error}</span>
                    <button type="button" className="btn-close btn-close-sm" onClick={() => setError('')}></button>
                  </div>
                )}
                {success && (
                  <div className="alert alert-success small py-2 d-flex align-items-center" role="alert">
                    <i className="bi bi-check-circle-fill me-2"></i>
                    {success}
                  </div>
                )}
                
                <form onSubmit={step === 3 ? handleSubmit : (e) => e.preventDefault()} autoComplete="off">
                  
                  {/* ============================================ */}
                  {/* ÉTAPE 1 : IDENTIFIANTS                       */}
                  {/* ============================================ */}
                  {step === 1 && (
                    <>
                      {/* ✅ EMAIL AVEC ICÔNE */}
                      <div className="mb-4">
                        <label className="form-label fw-semibold" style={{ color: '#334155' }}>
                          {/*<i className="bi bi-envelope-fill me-1" style={{ color: '#1E3A8A' }}></i>*/}
                          Email de connexion <span className="text-danger">*</span>
                        </label>
                        <div className="input-group">
                          <span className="input-group-text" style={iconStyle}>
                            <i className="bi bi-envelope-fill"></i>
                          </span>
                          <input 
                            type="email" 
                            name="email" 
                            className="form-control" 
                            placeholder="exemple@domaine.com"
                            value={formData.email} 
                            onChange={handleChange} 
                            autoComplete="off"
                            required 
                            disabled={loading}
                            style={{ borderRadius: '0 8px 8px 0', ...inputStyle }}
                          />
                        </div>
                      </div>
                      
                      {/* ✅ MOT DE PASSE AVEC ICÔNE */}
                      <div className="mb-4">
                        <label className="form-label fw-semibold" style={{ color: '#334155' }}>
                          {/*<i className="bi bi-lock-fill me-1" style={{ color: '#1E3A8A' }}></i>*/}
                          Mot de passe <span className="text-danger">*</span>
                        </label>
                        <div className="input-group">
                          <span className="input-group-text" style={iconStyle}>
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
                            disabled={loading}
                            style={inputStyleMiddle}
                          />
                          <button 
                            type="button" 
                            className="btn btn-outline-secondary" 
                            onClick={() => setShowPassword(!showPassword)}
                            title={showPassword ? "Masquer" : "Afficher"}
                            style={btnEyeStyle}
                          >
                            <i className={`bi ${showPassword ? 'bi-eye-slash-fill' : 'bi-eye-fill'}`}></i>
                          </button>
                        </div>
                        <div className="form-text text-muted small">
                          {/*<i className="bi bi-info-circle me-1"></i>*/}
                          8 caractères minimum, avec lettres et chiffres
                        </div>
                      </div>
                      
                      {/* ✅ CONFIRMATION MOT DE PASSE AVEC ICÔNE */}
                      <div className="mb-4">
                        <label className="form-label fw-semibold" style={{ color: '#334155' }}>
                          {/*<i className="bi bi-shield-lock-fill me-1" style={{ color: '#1E3A8A' }}></i>*/}
                          Confirmation <span className="text-danger">*</span>
                        </label>
                        <div className="input-group">
                          <span className="input-group-text" style={iconStyle}>
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
                            disabled={loading}
                            style={inputStyleMiddle}
                          />
                          <button 
                            type="button" 
                            className="btn btn-outline-secondary" 
                            onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                            title={showConfirmPassword ? "Masquer" : "Afficher"}
                            style={btnEyeStyle}
                          >
                            <i className={`bi ${showConfirmPassword ? 'bi-eye-slash-fill' : 'bi-eye-fill'}`}></i>
                          </button>
                        </div>
                      </div>
                      
                      <button 
                        type="button" 
                        className="btn w-100 py-2 fw-semibold shadow-sm"
                        onClick={nextStep}
                        disabled={loading}
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
                  
                  {/* ============================================ */}
                  {/* ÉTAPE 2 : INFORMATIONS PERSONNELLES          */}
                  {/* ============================================ */}
                  {step === 2 && (
                    <>
                      {/* ✅ NOM ET PRÉNOM */}
                      <div className="row g-3 mb-3">
                        <div className="col-md-6">
                          <label className="form-label fw-semibold" style={{ color: '#334155' }}>
                            {/*<i className="bi bi-person-fill me-1" style={{ color: '#1E3A8A' }}></i>*/}
                            Nom <span className="text-danger">*</span>
                          </label>
                          <div className="input-group">
                            <span className="input-group-text" style={iconStyle}>
                              <i className="bi bi-person-fill"></i>
                            </span>
                            <input 
                              type="text" 
                              name="last_name" 
                              className="form-control" 
                              placeholder="Votre nom"
                              value={formData.last_name} 
                              onChange={handleChange} 
                              required 
                              disabled={loading}
                              style={{ borderRadius: '0 8px 8px 0', ...inputStyle }}
                            />
                          </div>
                        </div>
                        <div className="col-md-6">
                          <label className="form-label fw-semibold" style={{ color: '#334155' }}>
                            {/*<i className="bi bi-person me-1" style={{ color: '#1E3A8A' }}></i>*/}
                            Prénom(s) <span className="text-danger">*</span>
                          </label>
                          <div className="input-group">
                            <span className="input-group-text" style={iconStyle}>
                              <i className="bi bi-person"></i>
                            </span>
                            <input 
                              type="text" 
                              name="first_name" 
                              className="form-control" 
                              placeholder="Votre prénom"
                              value={formData.first_name} 
                              onChange={handleChange} 
                              required 
                              disabled={loading}
                              style={{ borderRadius: '0 8px 8px 0', ...inputStyle }}
                            />
                          </div>
                        </div>
                      </div>
                      
                      {/* ✅ SEXE ET DATE DE NAISSANCE */}
                      <div className="row g-3 mb-3">
                        <div className="col-md-6">
                          <label className="form-label fw-semibold" style={{ color: '#334155' }}>
                            {/*<i className="bi bi-gender-ambiguous me-1" style={{ color: '#1E3A8A' }}></i>*/}
                            Sexe <span className="text-danger">*</span>
                          </label>
                          <div className="input-group">
                            {/*<span className="input-group-text" style={iconStyle}>
                              <i className="bi bi-gender-ambiguous"></i>
                            </span>*/}
                            <select 
                              name="genre" 
                              className="form-select" 
                              value={formData.genre} 
                              onChange={handleChange} 
                              required
                              disabled={loading}
                              style={{ borderRadius: '0 8px 8px 0', ...inputStyle }}
                            >
                              <option value="">Sélectionner</option>
                              <option value="M">Masculin</option>
                              <option value="F">Féminin</option>
                            </select>
                          </div>
                        </div>
                        <div className="col-md-6">
                          <label className="form-label fw-semibold" style={{ color: '#334155' }}>
                            {/*<i className="bi bi-calendar-event me-1" style={{ color: '#1E3A8A' }}></i>*/}
                            Date de naissance <span className="text-danger">*</span>
                          </label>
                          <div className="input-group">
                            <span className="input-group-text" style={iconStyle}>
                              <i className="bi bi-calendar-event"></i>
                            </span>
                            <input 
                              type="date" 
                              name="date_naissance" 
                              className="form-control" 
                              value={formData.date_naissance} 
                              onChange={handleChange} 
                              required 
                              disabled={loading}
                              style={{ borderRadius: '0 8px 8px 0', ...inputStyle }}
                            />
                          </div>
                        </div>
                      </div>
                      
                      {/* ✅ TÉLÉPHONE ET PAYS */}
                      <div className="row g-3 mb-3">
                        <div className="col-md-6">
                          <label className="form-label fw-semibold" style={{ color: '#334155' }}>
                            {/*<i className="bi bi-telephone-fill me-1" style={{ color: '#1E3A8A' }}></i>*/}
                            Téléphone <span className="text-danger">*</span>
                          </label>
                          <div className="input-group">
                            <span className="input-group-text" style={iconStyle}>
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
                              disabled={loading}
                              style={{ borderRadius: '0 8px 8px 0', ...inputStyle }}
                            />
                          </div>
                        </div>
                        <div className="col-md-6">
                          <label className="form-label fw-semibold" style={{ color: '#334155' }}>
                            {/*<i className="bi bi-globe-americas me-1" style={{ color: '#1E3A8A' }}></i>*/}
                            Pays
                          </label>
                          <div className="input-group">
                            <span className="input-group-text" style={iconStyle}>
                              <i className="bi bi-globe-americas"></i>
                            </span>
                            <select 
                              name="pays" 
                              className="form-select" 
                              value={formData.pays} 
                              onChange={handleChange}
                              disabled={loading}
                              style={{ borderRadius: '0 8px 8px 0', ...inputStyle }}
                            >
                              {countries.map(c => (
                                <option key={c.code} value={c.code}>{c.name}</option>
                              ))}
                            </select>
                          </div>
                        </div>
                      </div>
                      
                      {/* ✅ ADRESSE */}
                      <div className="mb-4">
                        <label className="form-label fw-semibold" style={{ color: '#334155' }}>
                          {/*<i className="bi bi-geo-alt-fill me-1" style={{ color: '#1E3A8A' }}></i>*/}
                          Adresse
                        </label>
                        <div className="input-group">
                          <span 
                            className="input-group-text align-items-start pt-3" 
                            style={iconStyle}
                          >
                            <i className="bi bi-geo-alt-fill"></i>
                          </span>
                          <textarea 
                            name="adresse" 
                            className="form-control" 
                            rows="2" 
                            placeholder="Votre adresse complète"
                            value={formData.adresse} 
                            onChange={handleChange} 
                            disabled={loading}
                            style={{ borderRadius: '0 8px 8px 0', ...inputStyle }}
                          />
                        </div>
                      </div>
                      
                      <div className="d-flex gap-2">
                        <button 
                          type="button" 
                          className="btn btn-outline-secondary" 
                          onClick={prevStep}
                          disabled={loading}
                          style={{ borderRadius: '8px' }}
                        >
                          <i className="bi bi-arrow-left me-1"></i>
                          Retour
                        </button>
                        <button 
                          type="button" 
                          className="btn flex-grow-1 fw-semibold shadow-sm" 
                          onClick={nextStep}
                          disabled={loading}
                          style={{ 
                            borderRadius: '8px',
                            background: 'linear-gradient(135deg, #1E3A8A, #172554)',
                            border: 'none',
                            color: 'white'
                          }}
                        >
                          <i className="bi bi-arrow-right me-1"></i>
                          Continuer
                        </button>
                      </div>
                    </>
                  )}
                  
                  {/* ============================================ */}
                  {/* ÉTAPE 3 : PROFIL PROFESSIONNEL               */}
                  {/* ============================================ */}
                  {step === 3 && (
                    <>
                      {/* ✅ COMPÉTENCES */}
                      <div className="mb-3">
                        <label className="form-label fw-semibold" style={{ color: '#334155' }}>
                          {/*<i className="bi bi-lightbulb-fill me-1" style={{ color: '#1E3A8A' }}></i>*/}
                          Domaines de compétence
                        </label>
                        <div className="input-group">
                          <span 
                            className="input-group-text align-items-start pt-3" 
                            style={iconStyle}
                          >
                            {/*<i className="bi bi-lightbulb-fill"></i>*/}
                          </span>
                          <textarea 
                            name="competences" 
                            className="form-control" 
                            rows="3" 
                            placeholder="Ex: Développement web, Audit financier, Gestion de projet..."
                            value={formData.competences} 
                            onChange={handleChange} 
                            disabled={loading}
                            style={{ borderRadius: '0 8px 8px 0', ...inputStyle }}
                          />
                        </div>
                        <div className="form-text text-muted small">
                          {/*<i className="bi bi-info-circle me-1"></i>*/}
                          Séparez vos compétences par des virgules
                        </div>
                      </div>
                      
                      {/* ✅ EXPÉRIENCE */}
                      <div className="mb-4">
                        <label className="form-label fw-semibold" style={{ color: '#334155' }}>
                          {/*<i className="bi bi-briefcase-fill me-1" style={{ color: '#1E3A8A' }}></i>*/}
                          Expérience professionnelle
                        </label>
                        <div className="input-group">
                          <span 
                            className="input-group-text align-items-start pt-3" 
                            style={iconStyle}
                          >
                            {/*<i className="bi bi-briefcase-fill"></i>*/}
                          </span>
                          <textarea 
                            name="experience" 
                            className="form-control" 
                            rows="4" 
                            placeholder="Décrivez votre parcours, vos réalisations..."
                            value={formData.experience} 
                            onChange={handleChange} 
                            disabled={loading}
                            style={{ borderRadius: '0 8px 8px 0', ...inputStyle }}
                          />
                        </div>
                      </div>
                      
                      <div className="d-flex gap-2">
                        <button 
                          type="button" 
                          className="btn btn-outline-secondary" 
                          onClick={prevStep}
                          disabled={loading}
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
                            background: 'linear-gradient(135deg, #907a10, #63501c)',
                            border: 'none',
                            color: 'white'
                          }}
                        >
                          {loading ? (
                            <>
                              <span className="spinner-border spinner-border-sm me-2" role="status"></span>
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
                  <span className="text-muted small">Vous avez déjà un compte ? </span>
                  <Link 
                    to="/login" 
                    className="text-decoration-none fw-semibold text-nowrap"
                    style={{ color: '#1E3A8A', whiteSpace: 'nowrap' }}
                  >
                    <i className="bi bi-box-arrow-in-right me-1"></i>
                    Se connecter
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

export default RegisterExpert;