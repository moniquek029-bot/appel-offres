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
  
  const [formData, setFormData] = useState({
    telephone: '',
    pays: 'BF',
    competences: '',       // Sera mappé à 'domaines_competence'
    experience: '',        // Sera mappé à 'autres_competences'
    disponibilite: true
  });
  
  const [cvFile, setCvFile] = useState(null);
  const [cvPreview, setCvPreview] = useState(null);

  const countries = [
    { code: 'BF', name: '🇧🇫 Burkina Faso' },
    { code: 'CI', name: '🇨🇮 Côte d\'Ivoire' },
    { code: 'SN', name: '🇸🇳 Sénégal' },
    { code: 'ML', name: '🇲🇱 Mali' },
    { code: 'NE', name: '🇳🇪 Niger' },
  ];

  useEffect(() => {
    const fetchProfile = async () => {
      try {
        const response = await api.get('/expert/profil/');
        const data = response.data.results?.[0] || response.data;
        
        if (data) {
          setProfile(data);
          setFormData({
            telephone: data.telephone || '',
            pays: data.pays || 'BF',
            competences: data.domaines_competence || '',      // ✅ Mapping correct
            experience: data.autres_competences || '',        // ✅ Mapping correct
            disponibilite: data.disponible ?? true            // ✅ Mapping correct
          });
          if (data.cv_fichier) setCvPreview(data.cv_fichier);
        }
      } catch (err) {
        if (err.response?.status !== 404) {
          setError('Impossible de charger votre profil');
        }
      } finally {
        setLoading(false);
      }
    };
    fetchProfile();
  }, []);

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData(prev => ({ ...prev, [name]: type === 'checkbox' ? checked : value }));
  };

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      if (file.size > 5 * 1024 * 1024) {
        setError('Le CV ne doit pas dépasser 5 Mo');
        return;
      }
      if (!file.type.includes('pdf') && !file.type.includes('doc') && !file.type.includes('docx')) {
        setError('Format accepté : PDF ou DOC/DOCX');
        return;
      }
      setCvFile(file);
      setCvPreview(URL.createObjectURL(file));
      setError(null);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSaving(true);
    setError(null);
    setSuccess(null);
    
    try {
      // ✅ 1. Envoyer les données texte avec les noms de champs attendus par le modèle Django
      const payload = {
        domaines_competence: formData.competences,
        autres_competences: formData.experience,
        disponible: formData.disponibilite,
        telephone: formData.telephone,
        pays: formData.pays
      };
      
      await api.put('/expert/profil/update/', payload);

      // ✅ 2. Upload du CV séparément si un nouveau fichier a été sélectionné
      if (cvFile) {
        const cvFormData = new FormData();
        cvFormData.append('cv_fichier', cvFile);
        await api.post('/expert/profil/upload-cv/', cvFormData, {
          headers: { 'Content-Type': 'multipart/form-data' }
        });
      }
      
      setSuccess('✅ Profil mis à jour avec succès !');
      
      // Notifier le dashboard si besoin
      window.dispatchEvent(new Event('profileUpdated'));
      
      setTimeout(() => navigate('/expert/dashboard'), 1500);
      
    } catch (err) {
      console.error('❌ Erreur mise à jour:', err.response?.data || err.message);
      
      // ✅ Afficher les erreurs de validation Django de manière lisible
      const errors = err.response?.data;
      if (typeof errors === 'object' && !Array.isArray(errors)) {
        const errorMessages = Object.entries(errors)
          .map(([field, messages]) => `${field}: ${Array.isArray(messages) ? messages.join(', ') : messages}`)
          .join(' | ');
        setError(`Erreur de validation : ${errorMessages}`);
      } else {
        setError(errors?.error || errors?.detail || 'Erreur lors de la mise à jour');
      }
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
      <div className="row mb-4">
        <div className="col-12">
          <nav aria-label="breadcrumb">
            <ol className="breadcrumb">
              <li className="breadcrumb-item"><Link to="/expert/dashboard">Dashboard</Link></li>
              <li className="breadcrumb-item active">Mon Profil</li>
            </ol>
          </nav>
          <h2 className="mb-1"><i className="bi bi-person me-1"></i> Mon Profil Expert</h2>
          <p className="text-muted"><i className="bi bi-info-circle me-1"></i> Complétez vos informations</p>
        </div>
      </div>

      {error && <div className="alert alert-danger">{error}</div>}
      {success && <div className="alert alert-success">{success}</div>}

      <div className="row g-4">
        <div className="col-lg-8">
          <form onSubmit={handleSubmit} className="card border-0 shadow-sm">
            <div className="card-body p-4">
              
              <h5 className="card-title mb-3">Informations de contact</h5>
              <div className="row g-3 mb-4">
                <div className="col-md-6">
                  <label className="form-label"><i className="bi bi-telephone me-1"></i> Téléphone</label>
                  <input type="tel" name="telephone" className="form-control" value={formData.telephone} onChange={handleChange} />
                </div>
                <div className="col-md-6">
                  <label className="form-label"><i className="bi bi-geo-alt me-1"></i> Pays</label>
                  <select name="pays" className="form-select" value={formData.pays} onChange={handleChange}>
                    {countries.map(c => (<option key={c.code} value={c.code}>{c.name}</option>))}
                  </select>
                </div>
              </div>

              <h5 className="card-title mb-3"><i className="bi bi-star me-1"></i> Compétences</h5>
              <div className="mb-3">
                <label className="form-label"><i className="bi bi-lightning me-1"></i> Domaines d'expertise</label>
                <textarea name="competences" className="form-control" rows="2" value={formData.competences} onChange={handleChange} placeholder="Ex: Développement web, Gestion de projet, Santé..." />
              </div>
              
              <div className="mb-3">
                <label className="form-label"><i className="bi bi-clock me-1"></i> Expérience</label>
                <textarea name="experience" className="form-control" rows="3" value={formData.experience} onChange={handleChange} placeholder="Décrivez votre parcours..." />
              </div>

              <h5 className="card-title mb-3">Curriculum Vitae</h5>
              <div className="mb-4">
                <label className="form-label">CV (PDF ou DOC, max 5 Mo)</label>
                <input type="file" className="form-control" accept=".pdf,.doc,.docx" onChange={handleFileChange} />
                {cvPreview && (
                  <div className="mt-3 p-3 bg-light rounded d-flex align-items-center">
                    <i className="bi bi-file-earmark-pdf text-danger me-2 fs-4"></i>
                    <span className="text-primary">{cvFile?.name || 'CV actuel chargé'}</span>
                  </div>
                )}
              </div>

              <div className="form-check form-switch mb-4">
                <input className="form-check-input" type="checkbox" name="disponibilite" id="dispoCheck" checked={formData.disponibilite} onChange={handleChange} />
                <label className="form-check-label" htmlFor="dispoCheck"> Je suis disponible pour de nouvelles missions</label>
              </div>

              <div className="d-flex gap-2 pt-3 border-top">
                <button 
                  type="submit" 
                  className="btn text-white fw-semibold"
                  style={{ 
                    background: 'linear-gradient(135deg, #059669, #047857)', // Vert émeraude
                    border: 'none',
                    borderRadius: '8px',
                    padding: '10px 24px',
                    boxShadow: '0 4px 6px rgba(5, 150, 105, 0.2)',
                    transition: 'all 0.2s ease'
                  }}
                  onMouseEnter={(e) => e.currentTarget.style.transform = 'translateY(-1px)'}
                  onMouseLeave={(e) => e.currentTarget.style.transform = 'translateY(0)'}
                >
                  <i className="bi bi-check-circle me-2"></i>
                  Enregistrer
                </button>
                <Link to="/expert/dashboard" className="btn btn-outline-secondary">Annuler</Link>
              </div>
            </div>
          </form>
        </div>

        <div className="col-lg-4">
          <div className="card border-0 shadow-sm sticky-top" style={{ top: '20px' }}>
            <div className="card-body">
              <h5 className="card-title mb-3"><i className="bi bi-person-badge me-1"></i> Aperçu</h5>
              <div className={`badge ${profile?.cv_fichier ? 'bg-success' : 'bg-warning text-dark'} mb-3`}>
                {profile?.cv_fichier ? 'Profil Complet' : 'CV manquant'}
              </div>
              {formData.competences && (
                <div>
                  <small className="text-muted">Expertises</small>
                  <div className="d-flex flex-wrap gap-1 mt-1">
                    {formData.competences.split(',').slice(0, 4).map((c, i) => (
                      <span key={i} className="badge bg-light text-dark border">{c.trim()}</span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ExpertProfile;