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
  
  const [formData, setFormData] = useState({
    telephone: '',
    pays: 'BF',
    competences: '',
    experience: '',
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
        setProfile(data);
        setFormData({
          telephone: data.telephone || '',
          pays: data.pays || 'BF',
          competences: data.competences || '',
          experience: data.experience || '',
          disponibilite: data.disponibilite ?? true
        });
        if (data.cv_fichier) setCvPreview(data.cv_fichier);
      } catch (err) {
        if (err.response?.status !== 404) setError('Impossible de charger votre profil');
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
      if (!file.type.includes('pdf') && !file.type.includes('doc')) {
        setError('Format accepté : PDF ou DOC');
        return;
      }
      setCvFile(file);
      setCvPreview(URL.createObjectURL(file));
      setError(null);
    }
  };

  // ✅ FONCTION DE SAUVEGARDE (handleSubmit)
  // src/pages/ExpertProfile.jsx - Fonction handleSubmit corrigée

const handleSubmit = async (e) => {
  e.preventDefault();
  setSaving(true);
  setError(null);
  setSuccess(null);
  
  try {
    // ✅ UTILISER LE NOUVEL ENDPOINT /update-profile/
    await api.put('/expert/profil/update-profile/', formData);
    
    // Upload du CV si fichier sélectionné
    if (cvFile) {
      const cvFormData = new FormData();
      cvFormData.append('cv_fichier', cvFile);
      await api.post('/expert/profil/upload-cv/', cvFormData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
    }
    
    setSuccess('✅ Profil mis à jour avec succès !');
    setTimeout(() => navigate('/expert/dashboard'), 1500);
    
  } catch (err) {
    console.error('❌ Erreur mise à jour:', err);
    
    if (err.response?.status === 405) {
      setError('❌ Méthode non autorisée');
    } else if (err.response?.status === 401) {
      setError('❌ Session expirée. Veuillez vous reconnecter');
    } else {
      setError(err.response?.data?.error || 'Erreur lors de la mise à jour');
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
          <h2 className="mb-1">👤 Mon Profil Expert</h2>
          <p className="text-muted">Complétez vos informations</p>
        </div>
      </div>

      {error && <div className="alert alert-danger">{error}</div>}
      {success && <div className="alert alert-success">{success}</div>}

      <div className="row g-4">
        <div className="col-lg-8">
          <form onSubmit={handleSubmit} className="card border-0 shadow-sm">
            <div className="card-body p-4">
              
              <h5 className="card-title mb-3">📞 Informations de contact</h5>
              <div className="row g-3 mb-4">
                <div className="col-md-6">
                  <label className="form-label">Téléphone</label>
                  <input type="tel" name="telephone" className="form-control" value={formData.telephone} onChange={handleChange} />
                </div>
                <div className="col-md-6">
                  <label className="form-label">Pays</label>
                  <select name="pays" className="form-select" value={formData.pays} onChange={handleChange}>
                    {countries.map(c => (<option key={c.code} value={c.code}>{c.name}</option>))}
                  </select>
                </div>
              </div>

              <h5 className="card-title mb-3">Compétences</h5>
              <div className="mb-3">
                <label className="form-label">Domaines d'expertise</label>
                <textarea name="competences" className="form-control" rows="2" value={formData.competences} onChange={handleChange} placeholder="Ex: Développement web, Gestion de projet..." />
              </div>
              
              <div className="mb-3">
                <label className="form-label">Expérience</label>
                <textarea name="experience" className="form-control" rows="3" value={formData.experience} onChange={handleChange} placeholder="Décrivez votre parcours..." />
              </div>

              <h5 className="card-title mb-3">📄 Curriculum Vitae</h5>
              <div className="mb-4">
                <label className="form-label">CV (PDF ou DOC, max 5 Mo)</label>
                <input type="file" className="form-control" accept=".pdf,.doc,.docx" onChange={handleFileChange} />
                {cvPreview && (
                  <div className="mt-3 p-3 bg-light rounded">
                    <span className="text-primary"></span> {cvFile?.name || 'CV actuel'}
                  </div>
                )}
              </div>

              <div className="form-check form-switch mb-4">
                <input className="form-check-input" type="checkbox" name="disponibilite" id="dispoCheck" checked={formData.disponibilite} onChange={handleChange} />
                <label className="form-check-label" htmlFor="dispoCheck"> Je suis disponible pour de nouvelles missions</label>
              </div>

              <div className="d-flex gap-2 pt-3 border-top">
                <button type="submit" className="btn btn-primary" disabled={saving}>
                  {saving ? '⏳ Enregistrement...' : '💾 Enregistrer'}
                </button>
                <Link to="/expert/dashboard" className="btn btn-outline-secondary">Annuler</Link>
              </div>
            </div>
          </form>
        </div>

        <div className="col-lg-4">
          <div className="card border-0 shadow-sm">
            <div className="card-body">
              <h5 className="card-title mb-3">Aperçu</h5>
              <div className={`badge ${profile?.cv_fichier ? 'bg-success' : 'bg-warning text-dark'} mb-3`}>
                {profile?.cv_fichier ? '✅ Profil Complet' : 'CV manquant'}
              </div>
              {formData.competences && (
                <div>
                  <small className="text-muted">Expertises</small>
                  <div className="d-flex flex-wrap gap-1 mt-1">
                    {formData.competences.split(',').slice(0, 3).map((c, i) => (
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