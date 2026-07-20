import React, { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import api from '../services/api';

const BureauProfile = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  
  const [formData, setFormData] = useState({
    nom_structure: '',
    pays: 'BF',
    adresse: '',
    domaine_activite: '',
    email_contact: '',
    telephone: '',
    site_web: ''
  });

  const countries = [
    { code: 'BF', name: '🇧🇫 Burkina Faso' },
    { code: 'CI', name: '🇨🇮 Côte d\'Ivoire' },
    { code: 'SN', name: '🇸🇳 Sénégal' },
    { code: 'ML', name: '🇲🇱 Mali' },
    { code: 'NE', name: '🇳🇪 Niger' },
    { code: 'TG', name: '🇹🇬 Togo' },
    { code: 'BJ', name: '🇧🇯 Bénin' },
  ];

  // Charger les données depuis l'API
  useEffect(() => {
    const fetchProfile = async () => {
      try {
        const response = await api.get('/bureau/profil/my-profile/');
        const data = response.data.profile;
      
        if (data) {
          setFormData({
            nom_structure: data.nom_structure || '',
            pays: data.pays || 'BF',
            adresse: data.adresse || '',
            domaine_activite: data.domaine_activite || '',
            email_contact: data.email_contact || '',
            telephone: data.telephone || '',
            site_web: data.site_web || ''
          });
        }
      } catch (err) {
        console.error('❌ Erreur chargement profil:', err.response?.data || err.message);
        setError('Impossible de charger le profil.');
      } finally {
        setLoading(false);
      }
    };
    fetchProfile();
  }, []);

  // ✅ AJOUTÉ : Fonction manquante pour gérer les changements dans les champs
  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSaving(true);
    setError(null);
    setSuccess(null);

    try {
      const response = await api.put('/bureau/profil/update/', formData);
    
      // Sauvegarder dans localStorage pour le dashboard
      localStorage.setItem('bureau_profile', JSON.stringify(response.data.profile));
      const isComplete = response.data.profile.nom_structure && response.data.profile.email_contact && response.data.profile.telephone;
      localStorage.setItem('bureau_profile_complete', isComplete ? 'true' : 'false');
    
      // Notifier le dashboard
      window.dispatchEvent(new Event('profileUpdated'));
    
      setSuccess('✅ Profil enregistré avec succès !');
    
      setTimeout(() => {
        navigate('/bureau/dashboard');
      }, 1500);
    
    } catch (err) {
      console.error('❌ Erreur sauvegarde:', err.response?.data || err.message);
    
      const errors = err.response?.data;
      if (typeof errors === 'object') {
        const errorMessages = Object.entries(errors)
          .map(([field, messages]) => `${field}: ${Array.isArray(messages) ? messages.join(', ') : messages}`)
          .join(' | ');
        setError(`Erreur de validation: ${errorMessages}`);
      } else {
        setError(errors?.error || 'Erreur lors de l\'enregistrement');
      }
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
      <div className="row justify-content-center">
        <div className="col-lg-8">
          
          <nav aria-label="breadcrumb" className="mb-4">
            <ol className="breadcrumb">
              <li className="breadcrumb-item">
                <Link to="/bureau/dashboard">Tableau de bord</Link>
              </li>
              <li className="breadcrumb-item active">Mon Profil Bureau</li>
            </ol>
          </nav>

          <div className="card border-0 shadow-sm rounded-4">
            <div className="card-header bg-white border-0 pt-4 pb-0">
              <h4 className="mb-1 fw-bold">
                <i className="bi bi-building me-2 text-primary"></i>
                Profil de ma structure
              </h4>
              <p className="text-muted small">
                Complétez les informations de votre bureau d'études
              </p>
            </div>
            
            <div className="card-body p-4">
              {error && (
                <div className="alert alert-danger alert-dismissible fade show" role="alert">
                  <i className="bi bi-exclamation-triangle-fill me-2"></i>
                  {error}
                  <button type="button" className="btn-close" onClick={() => setError(null)}></button>
                </div>
              )}
              
              {success && (
                <div className="alert alert-success alert-dismissible fade show" role="alert">
                  <i className="bi bi-check-circle-fill me-2"></i>
                  {success}
                </div>
              )}

              <form onSubmit={handleSubmit}>
                <div className="mb-3">
                  <label className="form-label fw-semibold">
                    Nom de la structure <span className="text-danger">*</span>
                  </label>
                  <div className="input-group">
                    <span className="input-group-text bg-light">
                      <i className="bi bi-building text-primary"></i>
                    </span>
                    <input 
                      type="text" 
                      name="nom_structure"
                      className="form-control" 
                      value={formData.nom_structure}
                      onChange={handleChange}
                      placeholder="Ex: Cabinet d'Études X"
                      required
                    />
                  </div>
                </div>

                <div className="row g-3 mb-3">
                  <div className="col-md-6">
                    <label className="form-label fw-semibold">
                      Pays <span className="text-danger">*</span>
                    </label>
                    <div className="input-group">
                      <span className="input-group-text bg-light">
                        <i className="bi bi-geo-alt text-primary"></i>
                      </span>
                      <select 
                        name="pays"
                        className="form-select" 
                        value={formData.pays}
                        onChange={handleChange}
                        required
                      >
                        {countries.map(c => (
                          <option key={c.code} value={c.code}>{c.name}</option>
                        ))}
                      </select>
                    </div>
                  </div>
                  <div className="col-md-6">
                    <label className="form-label fw-semibold">
                      Domaine d'activité <span className="text-danger">*</span>
                    </label>
                    <div className="input-group">
                      <span className="input-group-text bg-light">
                        <i className="bi bi-briefcase text-primary"></i>
                      </span>
                      <input 
                        type="text" 
                        name="domaine_activite"
                        className="form-control" 
                        value={formData.domaine_activite}
                        onChange={handleChange}
                        placeholder="Ex: BTP, Informatique, Conseil..."
                        required
                      />
                    </div>
                  </div>
                </div>

                <div className="mb-3">
                  <label className="form-label fw-semibold">
                    Adresse complète
                  </label>
                  <div className="input-group">
                    <span className="input-group-text bg-light">
                      <i className="bi bi-geo-alt-fill text-primary"></i>
                    </span>
                    <textarea 
                      name="adresse"
                      className="form-control" 
                      rows="2"
                      value={formData.adresse}
                      onChange={handleChange}
                      placeholder="Ex: 123 rue XYZ, Ouagadougou"
                    />
                  </div>
                </div>

                <div className="row g-3 mb-3">
                  <div className="col-md-6">
                    <label className="form-label fw-semibold">
                      Email de contact <span className="text-danger">*</span>
                    </label>
                    <div className="input-group">
                      <span className="input-group-text bg-light">
                        <i className="bi bi-envelope text-primary"></i>
                      </span>
                      <input 
                        type="email" 
                        name="email_contact"
                        className="form-control" 
                        value={formData.email_contact}
                        onChange={handleChange}
                        placeholder="contact@monbureau.com"
                        required
                      />
                    </div>
                  </div>
                  <div className="col-md-6">
                    <label className="form-label fw-semibold">
                      Téléphone <span className="text-danger">*</span>
                    </label>
                    <div className="input-group">
                      <span className="input-group-text bg-light">
                        <i className="bi bi-telephone text-primary"></i>
                      </span>
                      <input 
                        type="tel" 
                        name="telephone"
                        className="form-control" 
                        value={formData.telephone}
                        onChange={handleChange}
                        placeholder="+226 XX XX XX XX"
                        required
                      />
                    </div>
                  </div>
                </div>

                <div className="mb-4">
                  <label className="form-label fw-semibold">
                    Site web
                  </label>
                  <div className="input-group">
                    <span className="input-group-text bg-light">
                      <i className="bi bi-globe text-primary"></i>
                    </span>
                    <input 
                      type="url" 
                      name="site_web"
                      className="form-control" 
                      value={formData.site_web}
                      onChange={handleChange}
                      placeholder="https://www.mon-site.com"
                    />
                  </div>
                </div>

                <hr className="my-4" />

                <div className="d-flex gap-3">
                  <button 
                    type="submit" 
                    className="btn text-white fw-semibold px-4 rounded-pill"
                    disabled={saving}
                    style={{ 
                      background: 'linear-gradient(135deg, #059669, #047857)', // 🟢 VERT ÉMERAUDE
                      border: 'none',
                      boxShadow: '0 4px 6px rgba(5, 150, 105, 0.2)',
                      transition: 'all 0.2s ease'
                    }}
                    onMouseEnter={(e) => !saving && (e.currentTarget.style.transform = 'translateY(-1px)')}
                    onMouseLeave={(e) => e.currentTarget.style.transform = 'translateY(0)'}
                  >
                    {saving ? (
                      <><span className="spinner-border spinner-border-sm me-2" role="status"></span>Enregistrement...</>
                    ) : (
                      <><i className="bi bi-check-circle me-2"></i>Enregistrer les modifications</>
                    )}
                  </button>
                  <Link to="/bureau/dashboard" className="btn btn-outline-secondary rounded-pill px-4">
                    Annuler
                  </Link>
                </div>

                <div className="mt-4 p-3 bg-light rounded-3">
                  <small className="text-muted">
                    <i className="bi bi-info-circle me-1"></i>
                    Tous les champs marqués d'un <span className="text-danger">*</span> sont obligatoires.
                  </small>
                </div>
              </form>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default BureauProfile;