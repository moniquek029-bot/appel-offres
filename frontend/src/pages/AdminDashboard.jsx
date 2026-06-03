// src/pages/AdminDashboard.jsx
import React, { useState, useEffect } from 'react';
import api from '../services/api';

const AdminDashboard = () => {
  // =============================================================================
  // ÉTATS PRINCIPAUX
  // =============================================================================
  const [stats, setStats] = useState(null);
  const [utilisateurs, setUtilisateurs] = useState([]);
  const [sources, setSources] = useState([]);
  const [suggestions, setSuggestions] = useState([]);
  const [historique, setHistorique] = useState([]);
  const [offres, setOffres] = useState([]);
  const [experts, setExperts] = useState([]);
  const [messages, setMessages] = useState([]);
  
  // Filtre messages : 'all' | 'unread' | 'sent' | 'received'
  const [messageFilter, setMessageFilter] = useState('all');
  
  // États UI
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  const [activeTab, setActiveTab] = useState('dashboard');
  
  const [lastRefresh, setLastRefresh] = useState(Date.now());
  
  // États modals existants
  const [showModal, setShowModal] = useState({ type: null, data: null });
  const [formData, setFormData] = useState({});
  const [selectedItems, setSelectedItems] = useState([]);
  const [confirmText, setConfirmText] = useState('');
  
  // NOUVEAUX ÉTATS : Publication manuelle d'offre
  const [showNewOffreModal, setShowNewOffreModal] = useState(false);
  const [newOffreForm, setNewOffreForm] = useState({
    titre: '',
    organisme: '',
    description: '',
    pays: 'BF',
    date_publication: '',
    date_cloture: '',
    url_source: '',
    url_tdr: '',
    statut: 'Ouvert'
  });
  const [newOffreError, setNewOffreError] = useState(null);
  const [newOffreSuccess, setNewOffreSuccess] = useState(null);

  // =============================================================================
  // FONCTIONS UTILITAIRES POUR LES MESSAGES
  // =============================================================================
  // Extrait l'ID de l'expéditeur quel que soit le format
  const getExpediteurId = (message) => {
    if (message.expediteur && typeof message.expediteur === 'object' && message.expediteur.id) {
      return message.expediteur.id;
    }
    if (message.expediteur_id !== undefined && message.expediteur_id !== null) {
      return message.expediteur_id;
    }
    if (typeof message.expediteur === 'number') {
      return message.expediteur;
    }
    if (message.expediteur?.id) {
      return message.expediteur.id;
    }
    return null;
  };

  // Extrait l'ID du destinataire quel que soit le format
  const getDestinataireId = (message) => {
    if (message.destinataire && typeof message.destinataire === 'object' && message.destinataire.id) {
      return message.destinataire.id;
    }
    if (message.destinataire_id !== undefined && message.destinataire_id !== null) {
      return message.destinataire_id;
    }
    if (typeof message.destinataire === 'number') {
      return message.destinataire;
    }
    if (message.destinataire?.id) {
      return message.destinataire.id;
    }
    return null;
  };

  // Vérifie si l'admin est l'expéditeur
  const isAdminExpediteur = (message) => {
    const expediteurId = getExpediteurId(message);
    // L'admin est généralement l'utilisateur 1 ou a un email admin
    if (expediteurId === 1) return true;
    if (message.expediteur_email && (
        message.expediteur_email.toLowerCase().includes('admin') || 
        message.expediteur_email.toLowerCase().includes('superuser')
    )) return true;
    return false;
  };

  // Vérifie si l'admin est le destinataire
  const isAdminDestinataire = (message) => {
    const destinataireId = getDestinataireId(message);
    if (destinataireId === 1) return true;
    if (message.destinataire_email && (
        message.destinataire_email.toLowerCase().includes('admin') || 
        message.destinataire_email.toLowerCase().includes('superuser')
    )) return true;
    return false;
  };

  // Obtient l'email de l'expéditeur
  const getExpediteurEmail = (message) => {
    if (message.expediteur_email) return message.expediteur_email;
    if (message.expediteur?.email) return message.expediteur.email;
    if (message.expediteur?.email) return message.expediteur.email;
    return 'Inconnu';
  };

  // Obtient le nom de l'expéditeur
  const getExpediteurNom = (message) => {
    if (message.expediteur_nom) return message.expediteur_nom;
    if (message.expediteur?.first_name) {
      return `${message.expediteur.first_name} ${message.expediteur.last_name || ''}`.trim();
    }
    return getExpediteurEmail(message);
  };

  // =============================================================================
  // CHARGEMENT INITIAL
  // =============================================================================
  useEffect(() => {
    loadAllData();
  }, []);

  const loadAllData = async () => {
    try {
      setLoading(true);
      await Promise.all([
        fetchStats(),
        fetchUtilisateurs(),
        fetchSources(),
        fetchSuggestions(),
        fetchHistorique(),
        fetchOffres(),
        fetchExperts(),
        fetchMessages()
      ]);
    } catch (err) {
      console.error('❌ Erreur chargement:', err);
      setError('Impossible de charger le tableau de bord');
    } finally {
      setLoading(false);
    }
  };

  // =============================================================================
  // FETCH API
  // =============================================================================
  const fetchStats = async () => {
    try {
      const res = await api.get('/admin/dashboard/', { params: { _refresh: lastRefresh } });
      setStats(res.data);
    } catch (err) {
      console.error('❌ Erreur stats:', err);
      setStats({
        offres: { total: 0, scrapees: 0, manuelles: 0, actives: 0, par_source: [] },
        utilisateurs: { total: 0, experts: 0, bureaux: 0, admins: 0, nouveaux_30j: 0 },
        connexions: { aujourdhui: 0, semaine: 0 },
        messages: { non_lus: 0, total: 0 },
        suggestions: { envoyees: 0, consultees: 0 }
      });
    }
  };

  const fetchUtilisateurs = async () => {
    try {
      const res = await api.get('/admin/utilisateurs/', { params: { _refresh: lastRefresh } });
      setUtilisateurs(res.data.results || res.data || []);
    } catch (err) {
      console.error('❌ Erreur utilisateurs:', err);
      setUtilisateurs([]);
    }
  };

  const fetchSources = async () => {
    try {
      const res = await api.get('/admin/sources/', { params: { _refresh: lastRefresh } });
      setSources(res.data.results || res.data || []);
    } catch (err) {
      console.error('❌ Erreur sources:', err);
      setSources([]);
    }
  };

  const fetchSuggestions = async () => {
    try {
      const res = await api.get('/admin/suggestions/', { params: { _refresh: lastRefresh } });
      setSuggestions(res.data.results || res.data || []);
    } catch (err) {
      console.error('❌ Erreur suggestions:', err);
      setSuggestions([]);
    }
  };

  const fetchHistorique = async () => {
    try {
      const res = await api.get('/admin/historique/', { params: { _refresh: lastRefresh } });
      setHistorique(res.data.results || res.data || []);
    } catch (err) {
      console.error('❌ Erreur historique:', err);
      setHistorique([]);
    }
  };

  const fetchOffres = async () => {
    try {
      const res = await api.get('/offres/', { params: { _refresh: lastRefresh } });
      setOffres(res.data.results || res.data || []);
    } catch (err) {
      console.error('❌ Erreur offres:', err);
      setOffres([]);
    }
  };

  const fetchExperts = async () => {
    try {
      const res = await api.get('/admin/utilisateurs/?role=EXPERT', { params: { _refresh: lastRefresh } });
      setExperts(res.data.results || res.data || []);
    } catch (err) {
      console.error('❌ Erreur experts:', err);
      setExperts([]);
    }
  };

  // Charger les messages
  const fetchMessages = async () => {
    try {
      const res = await api.get('/messages/', { params: { _refresh: lastRefresh } });
      const messagesData = res.data.results || res.data || [];
      
      // Debug
      if (messagesData.length > 0) {
        console.log('=== MESSAGES ADMIN ===');
        console.log('Premier message:', messagesData[0]);
        console.log('Total messages:', messagesData.length);
      }
      
      setMessages(messagesData);
    } catch (err) {
      console.error('❌ Erreur messages:', err);
      setMessages([]);
    }
  };

  // =============================================================================
  // ACTIONS : PUBLICATION MANUELLE D'OFFRE
  // =============================================================================
  const handlePublishOffre = async (e) => {
    e.preventDefault();
    setNewOffreError(null);
    setNewOffreSuccess(null);
  
    try {
      const res = await api.post('/offres/create-manuel/', newOffreForm);
      setNewOffreSuccess('✅ Offre publiée avec succès !');
    
      setNewOffreForm({
        titre: '', organisme: '', description: '', pays: 'BF',
        date_publication: '', date_cloture: '',
        url_source: '', url_tdr: '', statut: 'Ouvert'
      });
    
      setTimeout(() => {
        setShowNewOffreModal(false);
        setNewOffreSuccess(null);
        fetchOffres();
        fetchStats();
      }, 2000);
    
    } catch (err) {
      console.error('❌ Erreur publication:', err);
      setNewOffreError(err.response?.data || 'Erreur lors de la publication');
    }
  };

  // =============================================================================
  // ACTIONS : SOURCES DE SCRAPPING
  // =============================================================================
  const handleLaunchScraping = async () => {
    if (selectedItems.length === 0) {
      setError('Veuillez sélectionner au moins une source');
      return;
    }

    if (!window.confirm(`Lancer le scraping sur ${selectedItems.length} source(s) ?`)) return;

    try {
      setSuccess('🚀 Scraping en cours...');
    
      const response = await api.post('/admin/sources/run/', { 
        source_ids: selectedItems 
      });
    
      const message = response.data?.message || `✅ Scraping terminé`;
      console.log('📦 Scraping response:', response.data);
    
      setSuccess(message);

      const newTimestamp = Date.now();
      setLastRefresh(newTimestamp);
    
      await Promise.all([
        fetchOffres(),
        fetchStats(),
        fetchSources()
      ]);
    
      setSelectedItems([]);
      setTimeout(() => setSuccess(null), 5000);
    
    } catch (err) {
      console.error('❌ Erreur scraping:', err);
      setError(`❌ Erreur: ${err.response?.data?.error || err.message}`);
      setTimeout(() => setError(null), 5000);
    }
  };

  const handleAddSource = async (e) => {
    e.preventDefault();
    try {
      await api.post('/admin/sources/', formData);
      setShowModal({ type: null, data: null });
      setFormData({});
      setSuccess('✅ Source ajoutée');
      await fetchSources();
    } catch (err) {
      setError(`❌ Erreur: ${err.response?.data?.error || 'Échec de l\'ajout'}`);
    }
  };

  const handleDeleteSource = async (sourceId) => {
    if (!window.confirm('Supprimer cette source ? Les offres existantes seront conservées.')) return;
    
    try {
      await api.delete(`/admin/sources/${sourceId}/`);
      setSuccess('✅ Source supprimée');
      await fetchSources();
    } catch (err) {
      setError(`❌ Erreur: ${err.response?.data?.error || 'Échec de la suppression'}`);
    }
  };

  // =============================================================================
  // ACTIONS : UTILISATEURS
  // =============================================================================
  const handleToggleUserActive = async (userId, currentStatus) => {
    const action = currentStatus ? 'bloquer' : 'débloquer';
    
    if (!window.confirm(`${action} cet utilisateur ?`)) return;

    try {
      await api.patch(`/admin/utilisateurs/${userId}/toggle-active/`, {
        is_active: !currentStatus
      });
      
      setUtilisateurs(utilisateurs.map(user => 
        user.id === userId ? {...user, is_active: !user.is_active} : user
      ));
      
      setSuccess(`✅ Utilisateur ${action} avec succès`);
      setTimeout(() => setSuccess(null), 3000);
      
    } catch (err) {
      console.error(`❌ Erreur lors du ${action}:`, err);
      setError(`❌ Erreur: ${err.response?.data?.error || `Échec du ${action}`}`);
      setTimeout(() => setError(null), 5000);
    }
  };

  const handleDeleteUser = async (userId) => {
    if (confirmText !== 'CONFIRMER') {
      setError('Tapez "CONFIRMER" pour valider la suppression');
      return;
    }
    
    try {
      await api.delete(`/admin/utilisateurs/${userId}/force-delete/`);
      setSuccess('✅ Utilisateur supprimé');
      setShowModal({ type: null, data: null });
      setConfirmText('');
      
      setUtilisateurs(utilisateurs.filter(user => user.id !== userId));
      
      setTimeout(() => setSuccess(null), 3000);
    } catch (err) {
      setError(`❌ Erreur: ${err.response?.data?.error || 'Échec de la suppression'}`);
      setTimeout(() => setError(null), 5000);
    }
  };

  const handleAddUser = async (e) => {
    e.preventDefault();
    
    if (!formData.password || formData.password.length < 6) {
      setError('❌ Le mot de passe doit contenir au moins 6 caractères');
      setTimeout(() => setError(null), 5000);
      return;
    }
    
    try {
      const userData = {
        email: formData.email,
        first_name: formData.first_name,
        last_name: formData.last_name,
        role: formData.role || 'EXPERT',
        password: formData.password,
        is_active: true,
        telephone: formData.telephone || '',
        pays: formData.pays || 'BF'
      };
      
      console.log('📤 Création utilisateur:', { ...userData, password: '***' });
      
      await api.post('/admin/utilisateurs/', userData);
      
      setShowModal({ type: null, data: null });
      setFormData({});
      setSuccess('✅ Utilisateur ajouté avec succès (compte actif)');
      
      await fetchUtilisateurs();
      await fetchStats();
      
      setTimeout(() => setSuccess(null), 4000);
      
    } catch (err) {
      console.error('❌ Erreur création utilisateur:', err);
      const errorMsg = err.response?.data?.error || err.response?.data?.detail || 'Échec de la création';
      setError(`❌ Erreur: ${errorMsg}`);
      setTimeout(() => setError(null), 5000);
    }
  };

  // =============================================================================
  // ACTIONS : SUGGESTIONS
  // =============================================================================
  const handleSendSuggestion = async (e) => {
    e.preventDefault();
    try {
      await api.post('/admin/suggestions/', formData);
      setShowModal({ type: null, data: null });
      setFormData({});
      setSuccess('✅ Suggestion envoyée à l\'expert');
      await fetchSuggestions();
    } catch (err) {
      setError(`❌ Erreur: ${err.response?.data?.error || 'Échec de l\'envoi'}`);
    }
  };

  const handleDeleteSuggestion = async (suggestionId) => {
    if (!window.confirm('Supprimer cette suggestion ?')) return;
    
    try {
      await api.delete(`/admin/suggestions/${suggestionId}/force-delete/`);
      setSuccess('✅ Suggestion supprimée');
      await fetchSuggestions();
    } catch (err) {
      setError(`❌ Erreur: ${err.response?.data?.error || 'Échec de la suppression'}`);
    }
  };

  // =============================================================================
  // ACTIONS : HISTORIQUE
  // =============================================================================
  const handleClearHistory = async () => {
    if (confirmText !== 'EFFACER TOUT') {
      setError('Tapez "EFFACER TOUT" pour valider');
      return;
    }
    
    try {
      await api.post('/admin/historique/clear/', { 
        confirm: 'EFFACER TOUT',
        admin_password: formData.adminPassword || '' 
      });
      setSuccess('✅ Historique effacé');
      setShowModal({ type: null, data: null });
      setConfirmText('');
      setFormData({});
      await fetchHistorique();
    } catch (err) {
      setError(`❌ Erreur: ${err.response?.data?.error || 'Échec de l\'effacement'}`);
    }
  };

  // =============================================================================
  // ACTIONS : MESSAGES CORRIGÉES
  // =============================================================================
  const markMessageAsRead = async (messageId) => {
    try {
      await api.post(`/messages/${messageId}/marquer-lu/`);
      setMessages(prevMessages => prevMessages.map(msg => 
        msg.id === messageId ? {...msg, est_lu: true} : msg
      ));
      fetchStats();
    } catch (err) {
      console.error('❌ Erreur marquage lu:', err);
    }
  };

  const handleReplyMessage = async (messageId, replyContent) => {
    if (!replyContent.trim()) return;
    
    try {
      await markMessageAsRead(messageId);
      const response = await api.post(`/admin/messages/${messageId}/repondre/`, {
        contenu: replyContent
      });
      
      setMessages(prevMessages => prevMessages.map(msg => 
        msg.id === messageId ? {
          ...msg, 
          est_lu: true, 
          est_reponse: true,
          reponse_contenu: replyContent
        } : msg
      ));
      
      setSuccess('✅ Réponse envoyée');
      await Promise.all([fetchMessages(), fetchStats()]);
      setTimeout(() => setSuccess(null), 3000);
    } catch (err) {
      console.error('❌ Erreur envoi réponse:', err);
      setError(`❌ Erreur: ${err.response?.data?.error || 'Échec de l\'envoi'}`);
      setTimeout(() => setError(null), 5000);
    }
  };

  const handleDeleteMessage = async (messageId) => {
    if (!window.confirm('Supprimer ce message ?')) return;
    
    try {
      await api.delete(`/messages/${messageId}/`);
      setSuccess('✅ Message supprimé');
      await Promise.all([fetchMessages(), fetchStats()]);
      setTimeout(() => setSuccess(null), 3000);
    } catch (err) {
      setError(`❌ Erreur: ${err.response?.data?.error || 'Échec de la suppression'}`);
      setTimeout(() => setError(null), 5000);
    }
  };

  // =============================================================================
  // CALCULS POUR LES MESSAGES
  // =============================================================================
  // Messages reçus par l'admin (destinataire = admin)
  const receivedMessages = messages.filter(msg => isAdminDestinataire(msg) && !msg.est_reponse);
  
  // Messages envoyés par l'admin (expéditeur = admin)
  const sentMessages = messages.filter(msg => isAdminExpediteur(msg) || msg.est_reponse);
  
  // Messages non lus (reçus mais pas lus)
  const unreadMessages = messages.filter(msg => isAdminDestinataire(msg) && !msg.est_lu && !msg.est_reponse);
  
  // Compteurs
  const totalCount = messages.length;
  const receivedCount = receivedMessages.length;
  const sentCount = sentMessages.length;
  const unreadCount = unreadMessages.length;

  // Debug
  console.log('=== STATS MESSAGES ADMIN ===');
  console.log('Total messages:', totalCount);
  console.log('Reçus:', receivedCount);
  console.log('Envoyés:', sentCount);
  console.log('Non lus:', unreadCount);
  console.log('Messages bruts:', messages.map(m => ({
    id: m.id,
    sujet: m.sujet,
    expediteur_email: m.expediteur_email,
    destinataire_email: m.destinataire_email,
    est_reponse: m.est_reponse,
    est_lu: m.est_lu
  })));

  // Fonction pour obtenir les messages filtrés
  const getFilteredMessages = () => {
    if (messageFilter === 'received') return receivedMessages;
    if (messageFilter === 'sent') return sentMessages;
    if (messageFilter === 'unread') return unreadMessages;
    return messages;
  };

  // =============================================================================
  // UI HELPERS
  // =============================================================================
  const toggleSelect = (id) => {
    setSelectedItems(prev => 
      prev.includes(id) ? prev.filter(i => i !== id) : [...prev, id]
    );
  };

  const toggleSelectAll = () => {
    if (selectedItems.length === sources.length) {
      setSelectedItems([]);
    } else {
      setSelectedItems(sources.map(s => s.id));
    }
  };

  const openModal = (type, data = null) => {
    setShowModal({ type, data });
    setFormData(data || {});
    setError(null);
  };

  const closeModal = () => {
    setShowModal({ type: null, data: null });
    setFormData({});
    setConfirmText('');
    setError(null);
  };

  // =============================================================================
  // RENDU
  // =============================================================================
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
    <div className="container-fluid py-2">
      {/* Messages globaux */}
      {error && (
        <div className="alert alert-danger alert-dismissible fade show py-1 small" role="alert">
          ⚠️ {error}
          <button type="button" className="btn-close btn-close-sm" onClick={() => setError(null)}></button>
        </div>
      )}
      {success && (
        <div className="alert alert-success alert-dismissible fade show py-1 small" role="alert">
          ✅ {success}
          <button type="button" className="btn-close btn-close-sm" onClick={() => setSuccess(null)}></button>
        </div>
      )}

      {/* En-tête */}
      <div className="row mb-2">
        <div className="col-12 d-flex justify-content-between align-items-center">
          <h3 className="mb-0" style={{ fontSize: '1.5rem' }}>🛡️ Admin</h3>
          <div className="d-flex gap-2">
            <button 
              className="btn btn-success btn-sm" 
              onClick={() => setShowNewOffreModal(true)}
              style={{ padding: '4px 8px', fontSize: '0.7rem' }}
            >
              📝 Publier une offre
            </button>
            <button className="btn btn-outline-secondary btn-sm" onClick={loadAllData} style={{ padding: '4px 8px', fontSize: '0.7rem' }}>
              🔄
            </button>
          </div>
        </div>
      </div>

      {/* Onglets compacts */}
      <div className="mb-2">
        <div className="d-flex gap-2 border-bottom pb-1 flex-nowrap" style={{ overflowX: 'auto' }}>
          {[
            { id: 'dashboard', label: '📊 Dashboard' },
            { id: 'sources', label: '🕷️ Sources' },
            { id: 'utilisateurs', label: '👥 Utilisateurs' },
            { id: 'messages', label: `💬 Messages ${unreadCount > 0 ? `(${unreadCount})` : ''}` },
            { id: 'suggestions', label: '📧 Suggestions' },
            { id: 'historique', label: '📜 Historique' }
          ].map(tab => (
            <button 
              key={tab.id}
              className={`btn btn-sm ${activeTab === tab.id ? 'btn-primary' : 'btn-outline-secondary'}`}
              onClick={() => setActiveTab(tab.id)}
              style={{ 
                borderRadius: '20px', 
                padding: '4px 12px', 
                fontSize: '0.7rem', 
                flexShrink: 0
              }}
            >
              {tab.label}
            </button>
          ))}
        </div>
      </div>

      {/* === ONGLET DASHBOARD === */}
      {activeTab === 'dashboard' && stats && (
        <>
          <div className="row g-2 mb-3">
            {[
              { label: 'Offres', value: stats.offres?.total, bg: 'bg-primary', sub: `🤖${stats.offres?.scrapees}✍️${stats.offres?.manuelles}` },
              { label: 'Users', value: stats.utilisateurs?.total, bg: 'bg-success', sub: `👨‍💼${stats.utilisateurs?.experts}🏢${stats.utilisateurs?.bureaux}` },
              { label: 'Msg', value: unreadCount, bg: 'bg-warning text-dark', sub: `T:${totalCount} 📥${receivedCount} 📤${sentCount}` },
              { label: 'Sug.', value: stats.suggestions?.envoyees, bg: 'bg-info text-white', sub: `✅${stats.suggestions?.consultees}` }
            ].map((card, idx) => (
              <div className="col-6 col-md-3" key={idx}>
                <div className={`card border-0 shadow-sm ${card.bg} text-white`}>
                  <div className="card-body py-1 px-2 text-center">
                    <h4 className="mb-0 fw-bold" style={{ fontSize: '0.95rem' }}>{card.value || 0}</h4>
                    <p className="mb-0" style={{ fontSize: '0.6rem' }}>{card.label}</p>
                    <small style={{ fontSize: '0.55rem', opacity: 0.95 }}>{card.sub}</small>
                  </div>
                </div>
              </div>
            ))}
          </div>

          <div className="row g-2">
            <div className="col-md-6">
              <div className="card border-0 shadow-sm">
                <div className="card-header bg-white py-1 px-2 d-flex justify-content-between">
                  <h6 className="mb-0" style={{ fontSize: '0.75rem' }}>📊 Offres par source</h6>
                  <button className="btn btn-sm btn-outline-primary" onClick={() => setActiveTab('sources')} style={{ padding: '0 3px', fontSize: '0.65rem' }}>Gérer</button>
                </div>
                <div className="card-body p-1">
                  {stats.offres?.par_source?.map((source, idx) => (
                    <div key={idx} className="d-flex justify-content-between mb-1" style={{ fontSize: '0.65rem' }}>
                      <span className="text-truncate" style={{ maxWidth: '120px' }}>{source.nom || '?'}</span>
                      <span className="badge bg-primary" style={{ fontSize: '0.6rem' }}>{source.count}</span>
                    </div>
                  ))}
                  {!stats.offres?.par_source?.length && <p className="text-muted mb-0" style={{ fontSize: '0.65rem' }}>Aucune donnée</p>}
                </div>
              </div>
            </div>
            <div className="col-md-6">
              <div className="card border-0 shadow-sm">
                <div className="card-header bg-white py-1 px-2">
                  <h6 className="mb-0" style={{ fontSize: '0.75rem' }}>📊 Activité</h6>
                </div>
                <div className="card-body p-1">
                  <div className="d-flex justify-content-between mb-1" style={{ fontSize: '0.65rem' }}>
                    <span>Aujourd'hui</span>
                    <span className="badge bg-success">{stats.connexions?.aujourdhui || 0}</span>
                  </div>
                  <div className="d-flex justify-content-between mb-1" style={{ fontSize: '0.65rem' }}>
                    <span>Cette semaine</span>
                    <span className="badge bg-info">{stats.connexions?.semaine || 0}</span>
                  </div>
                  <div className="d-flex justify-content-between" style={{ fontSize: '0.65rem' }}>
                    <span>🆕 Nouveaux (30j)</span>
                    <span className="badge bg-secondary">{stats.utilisateurs?.nouveaux_30j || 0}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </>
      )}

      {/* === ONGLET SOURCES === */}
      {activeTab === 'sources' && (
        <div className="card">
          <div className="card-header bg-white d-flex justify-content-between align-items-center py-1 px-2">
            <h6 className="mb-0" style={{ fontSize: '0.8rem' }}>🕷️ Sources</h6>
            <div className="d-flex gap-1">
              <button className="btn btn-primary btn-sm" onClick={() => openModal('addSource')} style={{ padding: '1px 4px', fontSize: '0.65rem' }}>+ Ajouter</button>
              <button 
                className="btn btn-success btn-sm" 
                onClick={handleLaunchScraping}
                disabled={selectedItems.length === 0}
                style={{ padding: '1px 4px', fontSize: '0.65rem' }}
              >
                🚀 Lancer ({selectedItems.length})
              </button>
            </div>
          </div>
          <div className="table-responsive">
            <table className="table table-hover table-sm mb-0" style={{ fontSize: '0.7rem' }}>
              <thead className="table-light">
                <tr>
                  <th style={{ width: '25px' }}>
                    <input 
                      type="checkbox" 
                      className="form-check-input"
                      style={{ transform: 'scale(0.8)' }}
                      checked={sources.length > 0 && selectedItems.length === sources.length}
                      onChange={toggleSelectAll}
                    />
                  </th>
                  <th>Source</th>
                  <th>URL</th>
                  <th>Statut</th>
                  <th>Dernier</th>
                  <th style={{ width: '50px' }}>Actions</th>
                </tr>
              </thead>
              <tbody>
                {sources.map(source => (
                  <tr key={source.id}>
                    <td>
                      <input 
                        type="checkbox" 
                        className="form-check-input"
                        style={{ transform: 'scale(0.8)' }}
                        checked={selectedItems.includes(source.id)}
                        onChange={() => toggleSelect(source.id)}
                      />
                    </td>
                    <td className="text-truncate" style={{ maxWidth: '100px' }}>{source.nom}</td>
                    <td>
                      <a href={source.url_racine} target="_blank" rel="noopener noreferrer" className="text-truncate d-inline-block text-decoration-none" style={{ maxWidth: '150px', color: '#0d6efd' }}>
                        {source.url_racine?.replace('https://', '').replace('http://', '').substring(0, 25)}...
                      </a>
                    </td>
                    <td><span className={`badge ${source.est_actif ? 'bg-success' : 'bg-secondary'}`} style={{ fontSize: '0.6rem' }}>{source.est_actif ? 'Actif' : 'Inactif'}</span></td>
                    <td>{source.last_scraped ? new Date(source.last_scraped).toLocaleDateString('fr-FR') : '-'}</td>
                    <td>
                      <button className="btn btn-outline-danger btn-sm" onClick={() => handleDeleteSource(source.id)} style={{ padding: '0 3px', fontSize: '0.65rem' }}>🗑️</button>
                    </td>
                  </tr>
                ))}
                {!sources.length && <tr><td colSpan="6" className="text-center py-3 text-muted">Aucune source</td></tr>}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* === ONGLET UTILISATEURS === */}
      {activeTab === 'utilisateurs' && (
        <div className="card">
          <div className="card-header bg-white d-flex justify-content-between align-items-center py-1 px-2">
            <h6 className="mb-0" style={{ fontSize: '0.8rem' }}>👥 Utilisateurs</h6>
            <button className="btn btn-primary btn-sm" onClick={() => openModal('addUser')} style={{ padding: '1px 4px', fontSize: '0.65rem' }}>+ Ajouter</button>
          </div>
          <div className="table-responsive">
            <table className="table table-hover table-sm mb-0" style={{ fontSize: '0.7rem' }}>
              <thead className="table-light">
                <tr>
                  <th>Email</th>
                  <th>Nom</th>
                  <th>Rôle</th>
                  <th>Statut</th>
                  <th style={{ width: '160px' }}>Actions</th>
                </tr>
              </thead>
              <tbody>
                {utilisateurs.map(user => (
                  <tr key={user.id}>
                    <td className="text-truncate" style={{ maxWidth: '150px' }}>{user.email}</td>
                    <td className="text-truncate" style={{ maxWidth: '100px' }}>{user.nom || `${user.first_name} ${user.last_name}`}</td>
                    <td><span className="badge bg-secondary" style={{ fontSize: '0.6rem' }}>{user.role}</span></td>
                    <td>
                      <span className={`badge ${user.is_active ? 'bg-success' : 'bg-secondary'}`} style={{ fontSize: '0.6rem' }}>
                        {user.is_active ? '✅ Actif' : '⏸️ Inactif'}
                      </span>
                    </td>
                    <td>
                      <div className="d-flex gap-1">
                        <button
                          className={`btn btn-sm ${user.is_active ? 'btn-outline-warning' : 'btn-outline-success'}`}
                          onClick={() => handleToggleUserActive(user.id, user.is_active)}
                          style={{ padding: '0 3px', fontSize: '0.65rem' }}
                        >
                          {user.is_active ? '🔒 Bloquer' : '✅ Débloquer'}
                        </button>
                        <button
                          className="btn btn-outline-danger btn-sm"
                          onClick={() => openModal('deleteUser', user)}
                          style={{ padding: '0 3px', fontSize: '0.65rem' }}
                        >
                          🗑️
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
                {!utilisateurs.length && <tr><td colSpan="5" className="text-center py-3 text-muted">Aucun utilisateur</td></tr>}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* === ONGLET MESSAGES CORRIGÉ === */}
      {activeTab === 'messages' && (
        <div className="card">
          <div className="card-header bg-white py-2 px-3">
            <div className="d-flex justify-content-between align-items-center flex-wrap gap-2">
              <h6 className="mb-0" style={{ fontSize: '0.9rem' }}>💬 Messages</h6>
              <div className="btn-group btn-group-sm">
                <button 
                  className={`btn ${messageFilter === 'all' ? 'btn-primary' : 'btn-outline-secondary'}`}
                  onClick={() => setMessageFilter('all')}
                  style={{ fontSize: '0.7rem', padding: '4px 10px' }}
                >
                  📋 Tous ({totalCount})
                </button>
                <button 
                  className={`btn ${messageFilter === 'received' ? 'btn-primary' : 'btn-outline-secondary'}`}
                  onClick={() => setMessageFilter('received')}
                  style={{ fontSize: '0.7rem', padding: '4px 10px' }}
                >
                  📥 Reçus ({receivedCount})
                </button>
                <button 
                  className={`btn ${messageFilter === 'sent' ? 'btn-primary' : 'btn-outline-secondary'}`}
                  onClick={() => setMessageFilter('sent')}
                  style={{ fontSize: '0.7rem', padding: '4px 10px' }}
                >
                  📤 Envoyés ({sentCount})
                </button>
                <button 
                  className={`btn ${messageFilter === 'unread' ? 'btn-primary' : 'btn-outline-secondary'}`}
                  onClick={() => setMessageFilter('unread')}
                  style={{ fontSize: '0.7rem', padding: '4px 10px' }}
                >
                  🔴 Non lus ({unreadCount})
                </button>
              </div>
            </div>
          </div>
          <div className="card-body p-3">
            {getFilteredMessages().length === 0 ? (
              <div className="text-center py-4">
                <p className="text-muted mb-0 small">
                  {messageFilter === 'received' && '📭 Aucun message reçu'}
                  {messageFilter === 'sent' && '✉️ Aucun message envoyé'}
                  {messageFilter === 'unread' && '✅ Aucun message non lu'}
                  {messageFilter === 'all' && '💬 Aucun message'}
                </p>
              </div>
            ) : (
              <div className="list-group">
                {getFilteredMessages().map(msg => {
                  const isReceived = isAdminDestinataire(msg);
                  const isSent = isAdminExpediteur(msg) || msg.est_reponse;
                  const isUnread = !msg.est_lu && isReceived;
                  
                  return (
                    <div 
                      key={msg.id} 
                      className={`list-group-item list-group-item-action mb-2 rounded-3 ${isUnread ? 'bg-light border-primary' : 'border'}`}
                      onClick={() => isUnread && markMessageAsRead(msg.id)}
                      style={{ cursor: 'pointer' }}
                    >
                      <div className="d-flex w-100 justify-content-between align-items-start">
                        <div className="flex-grow-1">
                          <div className="d-flex align-items-center gap-2 mb-1 flex-wrap">
                            {isSent && !isReceived && (
                              <span className="badge bg-info" style={{ fontSize: '0.65rem' }}>📤 Envoyé</span>
                            )}
                            {isReceived && (
                              <span className="badge bg-secondary" style={{ fontSize: '0.65rem' }}>📥 Reçu</span>
                            )}
                            {msg.est_reponse && (
                              <span className="badge bg-success" style={{ fontSize: '0.65rem' }}>✅ Réponse envoyée</span>
                            )}
                            {isUnread && (
                              <span className="badge bg-primary" style={{ fontSize: '0.65rem' }}>🔴 Nouveau</span>
                            )}
                            
                            <strong className="small">{getExpediteurEmail(msg)}</strong>
                            
                            <small className="text-muted">
                              {new Date(msg.date_envoi).toLocaleString('fr-FR')}
                            </small>
                          </div>
                          
                          <h6 className="mb-1 small fw-bold">{msg.sujet}</h6>
                          <p className="mb-2 small text-secondary">{msg.contenu}</p>
                          
                          {/* Réponse existante */}
                          {msg.reponse_contenu && (
                            <div className="mt-2 p-2 bg-light rounded" style={{ borderLeft: '3px solid #198754' }}>
                              <small className="text-success fw-semibold">📨 Votre réponse :</small>
                              <p className="mb-0 small mt-1">{msg.reponse_contenu}</p>
                            </div>
                          )}
                          
                          {/* Formulaire de réponse (uniquement pour les messages reçus non répondu) */}
                          {isReceived && !msg.est_reponse && (
                            <div className="d-flex gap-2 align-items-center flex-wrap mt-2" onClick={(e) => e.stopPropagation()}>
                              <input 
                                type="text" 
                                className="form-control form-control-sm"
                                placeholder="Écrire une réponse..."
                                id={`reply-${msg.id}`}
                                style={{ fontSize: '0.8rem', maxWidth: '300px', minWidth: '150px' }}
                              />
                              <button 
                                className="btn btn-sm btn-primary"
                                onClick={async (e) => {
                                  e.stopPropagation();
                                  const replyInput = document.getElementById(`reply-${msg.id}`);
                                  if (replyInput.value.trim()) {
                                    await handleReplyMessage(msg.id, replyInput.value);
                                    replyInput.value = '';
                                  }
                                }}
                                style={{ fontSize: '0.7rem', padding: '3px 10px' }}
                              >
                                ✉️ Répondre
                              </button>
                              <button 
                                className="btn btn-sm btn-outline-danger"
                                onClick={(e) => {
                                  e.stopPropagation();
                                  handleDeleteMessage(msg.id);
                                }}
                                style={{ fontSize: '0.7rem', padding: '3px 10px' }}
                              >
                                🗑️ Supprimer
                              </button>
                            </div>
                          )}
                          
                          {/* Bouton supprimer pour les messages envoyés */}
                          {isSent && !isReceived && (
                            <button 
                              className="btn btn-sm btn-outline-danger mt-2"
                              onClick={(e) => {
                                e.stopPropagation();
                                handleDeleteMessage(msg.id);
                              }}
                              style={{ fontSize: '0.7rem', padding: '2px 8px' }}
                            >
                              🗑️ Supprimer
                            </button>
                          )}
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        </div>
      )}

      {/* === ONGLET SUGGESTIONS === */}
      {activeTab === 'suggestions' && (
        <div className="card">
          <div className="card-header bg-white d-flex justify-content-between align-items-center py-1 px-2">
            <h6 className="mb-0" style={{ fontSize: '0.8rem' }}>📧 Suggestions</h6>
            <button className="btn btn-primary btn-sm" onClick={() => openModal('sendSuggestion')} style={{ padding: '1px 4px', fontSize: '0.65rem' }}>+ Nouvelle</button>
          </div>
          <div className="table-responsive">
            <table className="table table-hover table-sm mb-0" style={{ fontSize: '0.7rem' }}>
              <thead className="table-light">
                <tr>
                  <th>Expert</th>
                  <th>Offre</th>
                  <th>Date</th>
                  <th>Statut</th>
                  <th style={{ width: '40px' }}>Actions</th>
                </tr>
              </thead>
              <tbody>
                {suggestions.map(sug => (
                  <tr key={sug.id}>
                    <td className="text-truncate" style={{ maxWidth: '120px' }}>{sug.expert_nom}</td>
                    <td className="text-truncate" style={{ maxWidth: '150px' }}>{sug.offre_titre?.substring(0, 30)}...</td>
                    <td>{new Date(sug.date_suggestion).toLocaleDateString('fr-FR')}</td>
                    <td>
                      <span className={`badge ${sug.est_consulte_par_expert ? 'bg-success' : 'bg-warning'}`} style={{ fontSize: '0.6rem' }}>
                        {sug.est_consulte_par_expert ? '✅ Consulté' : '⏳ En attente'}
                      </span>
                    </td>
                    <td>
                      <button 
                        className="btn btn-outline-danger btn-sm"
                        onClick={() => handleDeleteSuggestion(sug.id)}
                        style={{ padding: '0 3px', fontSize: '0.65rem' }}
                      >
                        🗑️
                      </button>
                    </td>
                  </tr>
                ))}
                {!suggestions.length && <tr><td colSpan="5" className="text-center py-3 text-muted">Aucune suggestion</td></tr>}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* === ONGLET HISTORIQUE === */}
      {activeTab === 'historique' && (
        <div className="card">
          <div className="card-header bg-white d-flex justify-content-between align-items-center py-1 px-2">
            <h6 className="mb-0" style={{ fontSize: '0.8rem' }}>📜 Historique</h6>
            <button 
              className="btn btn-outline-danger btn-sm"
              onClick={() => openModal('clearHistory')}
              style={{ padding: '1px 4px', fontSize: '0.65rem' }}
            >
              🗑️ Effacer
            </button>
          </div>
          <div className="table-responsive">
            <table className="table table-hover table-sm mb-0" style={{ fontSize: '0.7rem' }}>
              <thead className="table-light">
                <tr>
                  <th>Action</th>
                  <th>Utilisateur</th>
                  <th>Date</th>
                  <th>Détails</th>
                </tr>
              </thead>
              <tbody>
                {historique.map(entry => (
                  <tr key={entry.id}>
                    <td><span className="badge bg-light text-dark border" style={{ fontSize: '0.6rem' }}>{entry.action_type}</span></td>
                    <td className="text-truncate" style={{ maxWidth: '120px' }}>{entry.utilisateur_email}</td>
                    <td>{new Date(entry.date_action).toLocaleDateString('fr-FR')}</td>
                    <td className="text-truncate text-muted" style={{ maxWidth: '200px' }}>{entry.details?.substring(0, 50)}...</td>
                  </tr>
                ))}
                {!historique.length && (
                  <tr>
                    <td colSpan="4" className="text-center py-3 text-muted">Aucun historique</td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* =============================================================================
          MODAL : PUBLICATION MANUELLE D'OFFRE
          ============================================================================= */}
      {showNewOffreModal && (
        <div className="modal fade show d-block" tabIndex="-1" style={{ backgroundColor: 'rgba(0,0,0,0.5)' }}>
          <div className="modal-dialog modal-dialog-centered modal-lg">
            <div className="modal-content">
              <div className="modal-header py-2 px-3">
                <h6 className="modal-title" style={{ fontSize: '0.85rem' }}>📝 Publier une nouvelle offre</h6>
                <button type="button" className="btn-close btn-close-sm" onClick={() => setShowNewOffreModal(false)}></button>
              </div>
              
              <div className="modal-body py-2 px-3">
                {newOffreError && (
                  <div className="alert alert-danger alert-dismissible fade show py-1 small" role="alert">
                    ⚠️ {JSON.stringify(newOffreError)}
                    <button type="button" className="btn-close btn-close-sm" onClick={() => setNewOffreError(null)}></button>
                  </div>
                )}
                {newOffreSuccess && (
                  <div className="alert alert-success alert-dismissible fade show py-1 small" role="alert">
                    ✅ {newOffreSuccess}
                  </div>
                )}
                
                <form onSubmit={handlePublishOffre}>
                  <div className="row g-2">
                    <div className="col-12">
                      <label className="form-label" style={{ fontSize: '0.7rem' }}>Titre de l'offre *</label>
                      <input 
                        type="text" 
                        className="form-control form-control-sm"
                        value={newOffreForm.titre}
                        onChange={e => setNewOffreForm({...newOffreForm, titre: e.target.value})}
                        required
                        style={{ fontSize: '0.75rem', padding: '2px 4px' }}
                      />
                    </div>
                    
                    <div className="col-6">
                      <label className="form-label" style={{ fontSize: '0.7rem' }}>Organisme *</label>
                      <input 
                        type="text" 
                        className="form-control form-control-sm"
                        value={newOffreForm.organisme}
                        onChange={e => setNewOffreForm({...newOffreForm, organisme: e.target.value})}
                        required
                        style={{ fontSize: '0.75rem', padding: '2px 4px' }}
                      />
                    </div>
                    
                    <div className="col-6">
                      <label className="form-label" style={{ fontSize: '0.7rem' }}>Pays</label>
                      <select 
                        className="form-select form-select-sm"
                        value={newOffreForm.pays}
                        onChange={e => setNewOffreForm({...newOffreForm, pays: e.target.value})}
                        style={{ fontSize: '0.75rem', padding: '2px 4px' }}
                      >
                        <option value="BF">🇧🇫 Burkina Faso</option>
                        <option value="CI">🇨🇮 Côte d'Ivoire</option>
                        <option value="SN">🇸🇳 Sénégal</option>
                        <option value="ML">🇲🇱 Mali</option>
                        <option value="NE">🇳🇪 Niger</option>
                        <option value="TG">🇹🇬 Togo</option>
                        <option value="BJ">🇧🇯 Bénin</option>
                      </select>
                    </div>
                    
                    <div className="col-12">
                      <label className="form-label" style={{ fontSize: '0.7rem' }}>Description *</label>
                      <textarea 
                        className="form-control form-control-sm"
                        rows="3"
                        value={newOffreForm.description}
                        onChange={e => setNewOffreForm({...newOffreForm, description: e.target.value})}
                        required
                        style={{ fontSize: '0.75rem', padding: '2px 4px' }}
                      />
                    </div>
                    
                    <div className="col-6">
                      <label className="form-label" style={{ fontSize: '0.7rem' }}>Date de publication *</label>
                      <input 
                        type="date" 
                        className="form-control form-control-sm"
                        value={newOffreForm.date_publication}
                        onChange={e => setNewOffreForm({...newOffreForm, date_publication: e.target.value})}
                        required
                        style={{ fontSize: '0.75rem', padding: '2px 4px' }}
                      />
                    </div>
                    
                    <div className="col-6">
                      <label className="form-label" style={{ fontSize: '0.7rem' }}>Date de clôture</label>
                      <input 
                        type="date" 
                        className="form-control form-control-sm"
                        value={newOffreForm.date_cloture}
                        onChange={e => setNewOffreForm({...newOffreForm, date_cloture: e.target.value})}
                        style={{ fontSize: '0.75rem', padding: '2px 4px' }}
                      />
                    </div>
                    
                    <div className="col-12">
                      <label className="form-label" style={{ fontSize: '0.7rem' }}>URL source</label>
                      <input 
                        type="url" 
                        className="form-control form-control-sm"
                        value={newOffreForm.url_source}
                        onChange={e => setNewOffreForm({...newOffreForm, url_source: e.target.value})}
                        placeholder="https://..."
                        style={{ fontSize: '0.75rem', padding: '2px 4px' }}
                      />
                    </div>
                    
                    <div className="col-12">
                      <label className="form-label" style={{ fontSize: '0.7rem' }}>URL TDR (PDF)</label>
                      <input 
                        type="url" 
                        className="form-control form-control-sm"
                        value={newOffreForm.url_tdr}
                        onChange={e => setNewOffreForm({...newOffreForm, url_tdr: e.target.value})}
                        placeholder="https://.../document.pdf"
                        style={{ fontSize: '0.75rem', padding: '2px 4px' }}
                      />
                    </div>
                    
                    <div className="col-6">
                      <label className="form-label" style={{ fontSize: '0.7rem' }}>Statut</label>
                      <select 
                        className="form-select form-select-sm"
                        value={newOffreForm.statut}
                        onChange={e => setNewOffreForm({...newOffreForm, statut: e.target.value})}
                        style={{ fontSize: '0.75rem', padding: '2px 4px' }}
                      >
                        <option value="Ouvert">Ouvert</option>
                        <option value="Clôturé">Clôturé</option>
                        <option value="En cours">En cours</option>
                      </select>
                    </div>
                  </div>
                  
                  <div className="d-flex gap-2 mt-3">
                    <button type="submit" className="btn btn-primary btn-sm" style={{ fontSize: '0.7rem', padding: '2px 6px' }}>
                      📢 Publier
                    </button>
                    <button type="button" className="btn btn-secondary btn-sm" onClick={() => setShowNewOffreModal(false)} style={{ fontSize: '0.7rem', padding: '2px 6px' }}>
                      Annuler
                    </button>
                  </div>
                </form>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* =============================================================================
          MODALS EXISTANTS
          ============================================================================= */}
      {showModal.type && (
        <div className="modal fade show d-block" tabIndex="-1" style={{ backgroundColor: 'rgba(0,0,0,0.5)' }}>
          <div className="modal-dialog modal-dialog-centered modal-sm">
            <div className="modal-content">
              <div className="modal-header py-2 px-3">
                <h6 className="modal-title" style={{ fontSize: '0.85rem' }}>
                  {showModal.type === 'addSource' && '➕ Ajouter une source'}
                  {showModal.type === 'deleteUser' && '🗑️ Supprimer un utilisateur'}
                  {showModal.type === 'addUser' && '👥 Ajouter un utilisateur'}
                  {showModal.type === 'sendSuggestion' && '📧 Nouvelle suggestion'}
                  {showModal.type === 'clearHistory' && '⚠️ Effacer l\'historique'}
                </h6>
                <button type="button" className="btn-close btn-close-sm" onClick={closeModal}></button>
              </div>
              
              <div className="modal-body py-2 px-3">
                {/* Modal: Ajouter une source */}
                {showModal.type === 'addSource' && (
                  <form onSubmit={handleAddSource}>
                    <div className="mb-2">
                      <label className="form-label" style={{ fontSize: '0.7rem' }}>Nom *</label>
                      <input type="text" className="form-control form-control-sm" value={formData.nom || ''} onChange={e => setFormData({...formData, nom: e.target.value})} required style={{ fontSize: '0.75rem', padding: '2px 4px' }} />
                    </div>
                    <div className="mb-2">
                      <label className="form-label" style={{ fontSize: '0.7rem' }}>URL *</label>
                      <input type="url" className="form-control form-control-sm" value={formData.url_racine || ''} onChange={e => setFormData({...formData, url_racine: e.target.value})} required style={{ fontSize: '0.75rem', padding: '2px 4px' }} />
                    </div>
                    <div className="mb-2">
                      <label className="form-label" style={{ fontSize: '0.7rem' }}>Fréquence</label>
                      <input type="text" className="form-control form-control-sm" value={formData.frequence_maj || 'Toutes les 12h'} onChange={e => setFormData({...formData, frequence_maj: e.target.value})} style={{ fontSize: '0.75rem', padding: '2px 4px' }} />
                    </div>
                    <button type="submit" className="btn btn-primary btn-sm w-100" style={{ fontSize: '0.7rem', padding: '2px 4px' }}>Ajouter</button>
                  </form>
                )}

                {/* Modal: Supprimer un utilisateur */}
                {showModal.type === 'deleteUser' && (
                  <div>
                    <p className="small mb-2">Supprimer <strong>{showModal.data?.email}</strong> ?<br/><span className="text-danger">Irréversible.</span></p>
                    <div className="mb-2">
                      <label className="form-label" style={{ fontSize: '0.7rem' }}>Tapez "CONFIRMER" :</label>
                      <input type="text" className="form-control form-control-sm" value={confirmText} onChange={e => setConfirmText(e.target.value)} placeholder="CONFIRMER" style={{ fontSize: '0.75rem', padding: '2px 4px' }} />
                    </div>
                    <button className="btn btn-danger btn-sm w-100" onClick={() => handleDeleteUser(showModal.data?.id)} disabled={confirmText !== 'CONFIRMER'} style={{ fontSize: '0.7rem', padding: '2px 4px' }}>Confirmer</button>
                  </div>
                )}

                {/* Modal: Ajouter un utilisateur */}
                {showModal.type === 'addUser' && (
                  <form onSubmit={handleAddUser}>
                    <div className="row g-1">
                      <div className="col-12">
                        <label className="form-label" style={{ fontSize: '0.7rem' }}>Email *</label>
                        <input type="email" className="form-control form-control-sm" value={formData.email || ''} onChange={e => setFormData({...formData, email: e.target.value})} required style={{ fontSize: '0.75rem', padding: '2px 4px' }} />
                      </div>
                      <div className="col-6">
                        <label className="form-label" style={{ fontSize: '0.7rem' }}>Prénom *</label>
                        <input type="text" className="form-control form-control-sm" value={formData.first_name || ''} onChange={e => setFormData({...formData, first_name: e.target.value})} required style={{ fontSize: '0.75rem', padding: '2px 4px' }} />
                      </div>
                      <div className="col-6">
                        <label className="form-label" style={{ fontSize: '0.7rem' }}>Nom *</label>
                        <input type="text" className="form-control form-control-sm" value={formData.last_name || ''} onChange={e => setFormData({...formData, last_name: e.target.value})} required style={{ fontSize: '0.75rem', padding: '2px 4px' }} />
                      </div>
                      <div className="col-6">
                        <label className="form-label" style={{ fontSize: '0.7rem' }}>Rôle *</label>
                        <select className="form-select form-select-sm" value={formData.role || 'EXPERT'} onChange={e => setFormData({...formData, role: e.target.value})} style={{ fontSize: '0.75rem', padding: '2px 4px' }}>
                          <option value="EXPERT">Expert</option>
                          <option value="BUREAU">Bureau</option>
                          <option value="ADMIN">Admin</option>
                        </select>
                      </div>
                      <div className="col-6">
                        <label className="form-label" style={{ fontSize: '0.7rem' }}>Mot de passe *</label>
                        <input type="password" className="form-control form-control-sm" value={formData.password || ''} onChange={e => setFormData({...formData, password: e.target.value})} required style={{ fontSize: '0.75rem', padding: '2px 4px' }} />
                      </div>
                    </div>
                    <div className="mt-2 text-muted small bg-light p-1 rounded">
                      ⚡ L'utilisateur sera créé avec un compte <span className="text-success fw-bold">ACTIF</span>
                    </div>
                    <div className="d-flex gap-2 mt-3">
                      <button type="submit" className="btn btn-primary btn-sm" style={{ fontSize: '0.7rem', padding: '4px 8px' }}>
                        ✅ Créer l'utilisateur
                      </button>
                      <button type="button" className="btn btn-secondary btn-sm" onClick={closeModal} style={{ fontSize: '0.7rem', padding: '4px 8px' }}>
                        Annuler
                      </button>
                    </div>
                  </form>
                )}

                {/* Modal: Envoyer une suggestion */}
                {showModal.type === 'sendSuggestion' && (
                  <form onSubmit={handleSendSuggestion}>
                    <div className="mb-2">
                      <label className="form-label" style={{ fontSize: '0.7rem' }}>Expert *</label>
                      <select className="form-select form-select-sm" value={formData.expert_id || ''} onChange={e => setFormData({...formData, expert_id: e.target.value})} required style={{ fontSize: '0.75rem', padding: '2px 4px' }}>
                        <option value="">Sélectionner</option>
                        {experts.map(exp => (<option key={exp.id} value={exp.id}>{exp.nom || exp.email}</option>))}
                      </select>
                    </div>
                    <div className="mb-2">
                      <label className="form-label" style={{ fontSize: '0.7rem' }}>Offre *</label>
                      <select className="form-select form-select-sm" value={formData.offre_id || ''} onChange={e => setFormData({...formData, offre_id: e.target.value})} required style={{ fontSize: '0.75rem', padding: '2px 4px' }}>
                        <option value="">Sélectionner</option>
                        {offres.map(off => (<option key={off.id} value={off.id}>{off.titre?.substring(0, 40)}...</option>))}
                      </select>
                    </div>
                    <div className="mb-2">
                      <label className="form-label" style={{ fontSize: '0.7rem' }}>Commentaire</label>
                      <textarea className="form-control form-control-sm" rows="2" value={formData.commentaire_admin || ''} onChange={e => setFormData({...formData, commentaire_admin: e.target.value})} placeholder="Pourquoi ?" style={{ fontSize: '0.75rem', padding: '2px 4px' }} />
                    </div>
                    <button type="submit" className="btn btn-primary btn-sm w-100" style={{ fontSize: '0.7rem', padding: '2px 4px' }}>Envoyer</button>
                  </form>
                )}

                {/* Modal: Effacer l'historique */}
                {showModal.type === 'clearHistory' && (
                  <div>
                    <p className="small text-danger mb-2">⚠️ Effacer TOUT l'historique ?<br/>Irréversible.</p>
                    <div className="mb-2">
                      <label className="form-label" style={{ fontSize: '0.7rem' }}>Tapez "EFFACER TOUT" :</label>
                      <input type="text" className="form-control form-control-sm" value={confirmText} onChange={e => setConfirmText(e.target.value)} placeholder="EFFACER TOUT" style={{ fontSize: '0.75rem', padding: '2px 4px' }} />
                    </div>
                    <div className="mb-2">
                      <label className="form-label" style={{ fontSize: '0.7rem' }}>Mot de passe admin *</label>
                      <input type="password" className="form-control form-control-sm" value={formData.adminPassword || ''} onChange={e => setFormData({...formData, adminPassword: e.target.value})} placeholder="••••••••" style={{ fontSize: '0.75rem', padding: '2px 4px' }} />
                    </div>
                    <button className="btn btn-danger btn-sm w-100" onClick={handleClearHistory} disabled={confirmText !== 'EFFACER TOUT' || !formData.adminPassword} style={{ fontSize: '0.7rem', padding: '2px 4px' }}>Confirmer</button>
                  </div>
                )}
              </div>
              
              <div className="modal-footer py-1 px-3">
                <button type="button" className="btn btn-secondary btn-sm" onClick={closeModal} style={{ fontSize: '0.7rem', padding: '1px 4px' }}>Annuler</button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default AdminDashboard;