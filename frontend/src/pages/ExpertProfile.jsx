// src/pages/ExpertProfile.jsx
import React, { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import api from '../services/api';

const ExpertProfile = () => {
  const navigate = useNavigate();
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  
  // États du formulaire
  const [formData, setFormData] = useState({
    telephone: '',
    pays: '',
    competences: '',
    experience: '',
    disponibilite: true
  });
  const [cvFile, setCvFile] = useState(null);
  const [cvPreview, setCvPreview] = useState(null);

  // Liste des pays (pour le select)
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

  // Charger le profil au montage
  useEffect(() => {
    const fetchProfile = async () => {
      try {
        // Récupère le profil via l'endpoint dédié
        const response = await api.get('/expert/profil/');
        const data = response.data.results?.[0] || response.data;
        
        setProfile(data);
        setFormData({
          telephone: data.telephone || '',
          pays: data.pays || '',
          competences: data.competences || '',
          experience: data.experience || '',
          disponibilite: data.disponibilite ?? true
        });
        if (data.cv_fichier) {
          setCvPreview(data.cv_fichier);
        }
      } catch (err) {
        console.error('Erreur chargement profil:', err);
        // Si 404 = profil n'existe pas encore, on part de zéro
        if (err.response?.status !== 404) {
          setError('Impossible de charger votre profil');
        }
      } finally {
        setLoading(false);
      }
    };
    fetchProfile();
  }, []);

  // Gestion des champs texte
  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));
  };

  // Gestion du fichier CV
  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      // Vérification type et taille
      if (file.size > 5 * 1024 * 1024) { // 5MB max
        setError('Le CV ne doit pas dépasser 5 Mo');
        return;
      }
      if (!file.type.includes('pdf') && !file.type.includes('doc')) {
        setError('Format accepté : PDF ou DOC');
        return;
      }
      setCvFile(file);
      setCvPreview(URL.createObjectURL(file));
      setError(null);
    }
  };

  // Soumission du formulaire
  const handleSubmit = async (e) => {
    e.preventDefault();
    setSaving(true);
    setError(null);
    setSuccess(null);
    
    try {
      // 1. Mise à jour des infos texte
      await api.patch('/expert/profil/', formData);
      
      // 2. Upload du CV si sélectionné
      if (cvFile) {
        const cvFormData = new FormData();
        cvFormData.append('cv_fichier', cvFile);
        await api.post('/expert/profil/upload-cv/', cvFormData, {
          headers: { 'Content-Type': 'multipart/form-data' }
        });
      }
      
      setSuccess('✅ Profil mis à jour avec succès !');
      
      // Rafraîchir les données
      const response = await api.get('/expert/profil/');
      const data = response.data.results?.[0] || response.data;
      setProfile(data);
      
    } catch (err) {
      console.error('Erreur sauvegarde:', err);
      setError(err.response?.data?.error || 'Erreur lors de la mise à jour');
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div className="container py-5 text-center">
        <div className="spinner-border text-primary" role="status">
          <span className="visually-hidden">Chargement...</span>
        </div>
      </div>
    );
  }

  return (
    <div className="container py-4">
      {/* En-tête */}
      <div className="row mb-4">
        <div className="col-12">
          <nav aria-label="breadcrumb">
            <ol className="breadcrumb">
              <li className="breadcrumb-item"><Link to="/expert/dashboard">Dashboard</Link></li>
              <li className="breadcrumb-item active" aria-current="page">Mon Profil</li>
            </ol>
          </nav>
          <h2 className="mb-1">👤 Mon Profil Expert</h2>
          <p className="text-muted">Complétez vos informations pour être visible auprès des recruteurs</p>
        </div>
      </div>

      {/* Messages */}
      {error && <div className="alert alert-danger alert-dismissible fade show" role="alert">
        ⚠️ {error}
        <button type="button" className="btn-close" onClick={() => setError(null)}></button>
      </div>}
      {success && <div className="alert alert-success alert-dismissible fade show" role="alert">
        {success}
        <button type="button" className="btn-close" onClick={() => setSuccess(null)}></button>
      </div>}

      <div className="row g-4">
        {/* Formulaire principal */}
        <div className="col-lg-8">
          <form onSubmit={handleSubmit} className="card border-0 shadow-sm">
            <div className="card-body p-4">
              
              {/* Section : Informations de contact */}
              <h5 className="card-title mb-3">📞 Informations de contact</h5>
              <div className="row g-3 mb-4">
                <div className="col-md-6">
                  <label className="form-label">Téléphone / WhatsApp *</label>
                  <input 
                    type="tel" 
                    name="telephone"
                    className="form-control" 
                    value={formData.telephone}
                    onChange={handleChange}
                    placeholder="+226 70 12 34 56"
                    required
                  />
                </div>
                <div className="col-md-6">
                  <label className="form-label">Pays de résidence *</label>
                  <select 
                    name="pays"
                    className="form-select" 
                    value={formData.pays}
                    onChange={handleChange}
                    required
                  >
                    <option value="">Sélectionner un pays</option>
                    {countries.map(c => (
                      <option key={c.code} value={c.code}>{c.name}</option>
                    ))}
                  </select>
                </div>
              </div>

              {/* Section : Compétences */}
              <h5 className="card-title mb-3">💼 Compétences & Expérience</h5>
              <div className="mb-3">
                <label className="form-label">Domaines d'expertise (séparés par des virgules)</label>
                <textarea 
                  name="competences"
                  className="form-control" 
                  rows="2"
                  value={formData.competences}
                  onChange={handleChange}
                  placeholder="Ex: Développement web, Gestion de projet, Audit financier..."
                />
              </div>
              <div className="mb-3">
                <label className="form-label">Brève présentation</label>
                <textarea 
                  name="experience"
                  className="form-control" 
                  rows="3"
                  value={formData.experience}
                  onChange={handleChange}
                  placeholder="Décrivez votre parcours en quelques lignes..."
                />
              </div>

              {/* Section : CV */}
              <h5 className="card-title mb-3">📄 Curriculum Vitae</h5>
              <div className="mb-4">
                <label className="form-label">Télécharger votre CV (PDF ou DOC, max 5 Mo)</label>
                <input 
                  type="file" 
                  className="form-control" 
                  accept=".pdf,.doc,.docx"
                  onChange={handleFileChange}
                />
                <div className="form-text">Formats acceptés : PDF, DOC, DOCX</div>
                
                {/* Aperçu du CV */}
                {cvPreview && (
                  <div className="mt-3 p-3 bg-light rounded">
                    <div className="d-flex align-items-center gap-2">
                      <span className="text-primary">📎</span>
                      <span className="small">
                        {cvFile?.name || 'CV actuel'} 
                        {cvFile && ` (${Math.round(cvFile.size / 1024)} Ko)`}
                      </span>
                      {cvFile && (
                        <button 
                          type="button" 
                          className="btn btn-sm btn-outline-danger ms-auto"
                          onClick={() => { setCvFile(null); setCvPreview(null); }}
                        >
                          ✕
                        </button>
                      )}
                    </div>
                  </div>
                )}
              </div>

              {/* Section : Disponibilité */}
              <div className="form-check form-switch mb-4">
                <input 
                  className="form-check-input" 
                  type="checkbox" 
                  name="disponibilite"
                  id="dispoCheck"
                  checked={formData.disponibilite}
                  onChange={handleChange}
                />
                <label className="form-check-label" htmlFor="dispoCheck">
                  ✅ Je suis disponible pour de nouvelles missions
                </label>
              </div>

              {/* Boutons d'action */}
              <div className="d-flex gap-2 pt-3 border-top">
                <button 
                  type="submit" 
                  className="btn btn-primary"
                  disabled={saving}
                >
                  {saving ? (
                    <>
                      <span className="spinner-border spinner-border-sm me-2" role="status"></span>
                      Enregistrement...
                    </>
                  ) : '💾 Enregistrer les modifications'}
                </button>
                <Link to="/expert/dashboard" className="btn btn-outline-secondary">
                  Annuler
                </Link>
              </div>

            </div>
          </form>
        </div>

        {/* Sidebar : Résumé du profil */}
        <div className="col-lg-4">
          <div className="card border-0 shadow-sm sticky-top" style={{top: '2rem'}}>
            <div className="card-body">
              <h5 className="card-title mb-3">📋 Aperçu</h5>
              
              <div className="mb-3">
                <small className="text-muted">Statut du profil</small>
                <div className={`badge ${profile?.cv_fichier ? 'bg-success' : 'bg-warning text-dark'} mt-1`}>
                  {profile?.cv_fichier ? '✅ Complet' : '⚠️ CV manquant'}
                </div>
              </div>
              
              <div className="mb-3">
                <small className="text-muted">Contact</small>
                <p className="mb-0 small">{formData.telephone || 'Non renseigné'}</p>
                <p className="mb-0 small">{formData.pays ? countries.find(c=>c.code===formData.pays)?.name : 'Pays non sélectionné'}</p>
              </div>
              
              {formData.competences && (
                <div className="mb-3">
                  <small className="text-muted">Expertises</small>
                  <div className="d-flex flex-wrap gap-1 mt-1">
                    {formData.competences.split(',').slice(0, 3).map((c, i) => (
                      <span key={i} className="badge bg-light text-dark border small">{c.trim()}</span>
                    ))}
                    {formData.competences.split(',').length > 3 && (
                      <span className="badge bg-secondary small">+{formData.competences.split(',').length - 3}</span>
                    )}
                  </div>
                </div>
              )}
              
              <hr />
              
              <div className="d-grid gap-2">
                <Link to="/offres" className="btn btn-outline-primary btn-sm">
                  🔍 Voir toutes les offres
                </Link>
                <button 
                  className="btn btn-outline-success btn-sm"
                  onClick={() => navigate('/expert/dashboard')}
                >
                  📊 Retour au dashboard
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ExpertProfile;