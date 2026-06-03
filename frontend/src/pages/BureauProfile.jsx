// src/pages/BureauProfile.jsx
import React, { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';

const BureauProfile = () => {
  const navigate = useNavigate();
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

  // Charger les données sauvegardées
  useEffect(() => {
    const savedData = localStorage.getItem('bureau_profile');
    if (savedData) {
      try {
        const data = JSON.parse(savedData);
        setFormData({
          nom_structure: data.nom_structure || '',
          pays: data.pays || 'BF',
          adresse: data.adresse || '',
          domaine_activite: data.domaine_activite || '',
          email_contact: data.email_contact || '',
          telephone: data.telephone || '',
          site_web: data.site_web || ''
        });
      } catch (e) {
        console.error('Erreur chargement:', e);
      }
    }
  }, []);

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSaving(true);
    setError(null);
    setSuccess(null);

    // Simuler un délai réseau
    setTimeout(() => {
      try {
        // Sauvegarder dans localStorage
        localStorage.setItem('bureau_profile', JSON.stringify(formData));
        
        // Sauvegarder un flag pour indiquer que le profil est complété
        const isComplete = formData.nom_structure && formData.email_contact && formData.telephone;
        localStorage.setItem('bureau_profile_complete', isComplete ? 'true' : 'false');
        
        // ✅ Déclencher un événement pour notifier le dashboard
        window.dispatchEvent(new Event('profileUpdated'));
        
        setSuccess('✅ Profil enregistré avec succès !');
        
        setTimeout(() => {
          navigate('/bureau/dashboard');
        }, 1500);
        
      } catch (err) {
        setError('Erreur lors de l\'enregistrement');
        setSaving(false);
      }
    }, 500);
  };

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
              <h4 className="mb-1 fw-bold">🏢 Profil de ma structure</h4>
              <p className="text-muted small">
                Complétez les informations de votre bureau d'études
              </p>
            </div>
            
            <div className="card-body p-4">
              
              {error && (
                <div className="alert alert-danger alert-dismissible fade show" role="alert">
                  ⚠️ {error}
                  <button type="button" className="btn-close" onClick={() => setError(null)}></button>
                </div>
              )}
              
              {success && (
                <div className="alert alert-success alert-dismissible fade show" role="alert">
                  ✅ {success}
                </div>
              )}

              <form onSubmit={handleSubmit}>
                
                <div className="mb-3">
                  <label className="form-label fw-semibold">
                    Nom de la structure <span className="text-danger">*</span>
                  </label>
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

                <div className="row g-3 mb-3">
                  <div className="col-md-6">
                    <label className="form-label fw-semibold">
                      Pays <span className="text-danger">*</span>
                    </label>
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
                  <div className="col-md-6">
                    <label className="form-label fw-semibold">
                      Domaine d'activité <span className="text-danger">*</span>
                    </label>
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

                <div className="mb-3">
                  <label className="form-label fw-semibold">
                    Adresse complète <span className="text-danger">*</span>
                  </label>
                  <textarea 
                    name="adresse"
                    className="form-control" 
                    rows="2"
                    value={formData.adresse}
                    onChange={handleChange}
                    placeholder="Ex: 123 rue XYZ, Ouagadougou"
                    required
                  />
                </div>

                <div className="row g-3 mb-3">
                  <div className="col-md-6">
                    <label className="form-label fw-semibold">
                      Email de contact <span className="text-danger">*</span>
                    </label>
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
                  <div className="col-md-6">
                    <label className="form-label fw-semibold">
                      Téléphone <span className="text-danger">*</span>
                    </label>
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

                <div className="mb-4">
                  <label className="form-label fw-semibold">
                    Site web
                  </label>
                  <input 
                    type="url" 
                    name="site_web"
                    className="form-control" 
                    value={formData.site_web}
                    onChange={handleChange}
                    placeholder="https://www.mon-site.com"
                  />
                </div>

                <hr className="my-4" />

                <div className="d-flex gap-2">
                  <button 
                    type="submit" 
                    className="btn btn-primary"
                    disabled={saving}
                  >
                    {saving ? 'Enregistrement...' : '💾 Enregistrer les modifications'}
                  </button>
                  <Link to="/bureau/dashboard" className="btn btn-outline-secondary">
                    Annuler
                  </Link>
                </div>

                <div className="mt-4 p-3 bg-light rounded-3">
                  <small className="text-muted">
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