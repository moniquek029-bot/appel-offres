// src/pages/AdminDashboard.jsx - VERSION CORRIGÉE
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
  
  const [messageFilter, setMessageFilter] = useState('all');
  
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  const [activeTab, setActiveTab] = useState('dashboard');
  
  const [lastRefresh, setLastRefresh] = useState(Date.now());
  
  const [showModal, setShowModal] = useState({ type: null, data: null });
  const [formData, setFormData] = useState({});
  const [selectedItems, setSelectedItems] = useState([]);
  const [confirmText, setConfirmText] = useState('');

  const [showUserDetailsModal, setShowUserDetailsModal] = useState(false);
  const [userDetails, setUserDetails] = useState(null);
  const [userDetailsLoading, setUserDetailsLoading] = useState(false);
  const [userDetailsError, setUserDetailsError] = useState(null);
  
  const [editSourceModal, setEditSourceModal] = useState({ show: false, source: null });
  const [editSourceForm, setEditSourceForm] = useState({
    nom: '',
    url_racine: '',
    frequence_maj: '',
    est_actif: true
  });
  
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
  const [fichierPdf, setFichierPdf] = useState(null);
  const [fichierPdfError, setFichierPdfError] = useState(null);
    // =============================================================================
  // ÉTATS POUR LE SCRAPING
  // =============================================================================
  const [isScraping, setIsScraping] = useState(false);
  const [scrapingMessage, setScrapingMessage] = useState('');
  const [scrapingResult, setScrapingResult] = useState(null);

  // =============================================================================
  // FONCTIONS POUR LA MODIFICATION DE SOURCE
  // =============================================================================
  const openEditSourceModal = (source) => {
    setEditSourceForm({
      nom: source.nom || '',
      url_racine: source.url_racine || '',
      frequence_maj: source.frequence_maj || 'Toutes les 12h',
      est_actif: source.est_actif !== undefined ? source.est_actif : true
    });
    setEditSourceModal({ show: true, source: source });
  };

  const closeEditSourceModal = () => {
    setEditSourceModal({ show: false, source: null });
    setEditSourceForm({
      nom: '',
      url_racine: '',
      frequence_maj: 'Toutes les 12h',
      est_actif: true
    });
  };

  const handleUpdateSource = async (e) => {
    e.preventDefault();
    try {
      await api.put(`/admin/sources/${editSourceModal.source.id}/`, editSourceForm);
      setSuccess('✅ Source modifiée avec succès');
      closeEditSourceModal();
      await fetchSources();
      await fetchStats();
      setTimeout(() => setSuccess(null), 3000);
    } catch (err) {
      console.error('❌ Erreur modification source:', err);
      setError(`❌ Erreur: ${err.response?.data?.error || 'Échec de la modification'}`);
      setTimeout(() => setError(null), 5000);
    }
  };

  const handleToggleSourceActive = async (sourceId, currentStatus) => {
    const action = currentStatus ? 'désactiver' : 'activer';
    
    if (!window.confirm(`Voulez-vous ${action} cette source ?`)) return;

    try {
      await api.patch(`/admin/sources/${sourceId}/`, {
        est_actif: !currentStatus
      });
      
      setSources(sources.map(s => 
        s.id === sourceId ? {...s, est_actif: !s.est_actif} : s
      ));
      
      setSuccess(`✅ Source ${action}e avec succès`);
      setTimeout(() => setSuccess(null), 3000);
      
    } catch (err) {
      console.error(`❌ Erreur lors de l'${action}:`, err);
      setError(`❌ Erreur: ${err.response?.data?.error || `Échec de l'${action}`}`);
      setTimeout(() => setError(null), 5000);
    }
  };

  // =============================================================================
  // FONCTIONS UTILITAIRES POUR LES MESSAGES
  // =============================================================================
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

  const isAdminExpediteur = (message) => {
    const expediteurId = getExpediteurId(message);
    if (expediteurId === 1) return true;
    if (message.expediteur_email && (
        message.expediteur_email.toLowerCase().includes('admin') || 
        message.expediteur_email.toLowerCase().includes('superuser')
    )) return true;
    return false;
  };

  const isAdminDestinataire = (message) => {
    const destinataireId = getDestinataireId(message);
    if (destinataireId === 1) return true;
    if (message.destinataire_email && (
        message.destinataire_email.toLowerCase().includes('admin') || 
        message.destinataire_email.toLowerCase().includes('superuser')
    )) return true;
    return false;
  };

  const getExpediteurEmail = (message) => {
    if (message.expediteur_email) return message.expediteur_email;
    if (message.expediteur?.email) return message.expediteur.email;
    return 'Inconnu';
  };

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

  const fetchUserDetails = async (userId) => {
    setUserDetailsLoading(true);
    setUserDetailsError(null);
    setUserDetails(null);
    setShowUserDetailsModal(true);
  
    try {
      const res = await api.get(`/admin/utilisateurs/${userId}/details/`);
      setUserDetails(res.data);
    } catch (err) {
      console.error('❌ Erreur détails utilisateur:', err);
      setUserDetailsError(err.response?.data?.error || 'Impossible de charger les détails');
    } finally {
      setUserDetailsLoading(false);
    }
  };

  const closeUserDetailsModal = () => {
    setShowUserDetailsModal(false);
    setUserDetails(null);
    setUserDetailsError(null);
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

  const fetchExperts = async () => {
    try {
      const res = await api.get('/admin/utilisateurs/?role=EXPERT', { 
        params: { _refresh: lastRefresh } 
      });
      const users = res.data.results || res.data || [];
    
      const expertsWithProfile = [];
      for (const user of users) {
        try {
          const profilRes = await api.get(`/admin/utilisateurs/${user.id}/details/`);
          
          if (profilRes.data.profil) {
            expertsWithProfile.push({
              id: profilRes.data.profil.id || user.id,
              user_id: user.id,
              nom: `${user.first_name} ${user.last_name}`.trim() || user.email,
              email: user.email,
              disponible: profilRes.data.profil.disponible,
              profil_complet: profilRes.data.profil.profil_complet
            });
          } else {
            expertsWithProfile.push({
              id: user.id,
              user_id: user.id,
              nom: `${user.first_name} ${user.last_name}`.trim() || user.email,
              email: user.email,
              disponible: false,
              profil_complet: false
            });
          }
        } catch (err) {
          console.warn(`⚠️ Pas de profil pour l'utilisateur ${user.id}`);
          expertsWithProfile.push({
            id: user.id,
            user_id: user.id,
            nom: `${user.first_name} ${user.last_name}`.trim() || user.email,
            email: user.email,
            disponible: false,
            profil_complet: false
          });
        }
      }
    
      setExperts(expertsWithProfile);
    } catch (err) {
      console.error('❌ Erreur experts:', err);
      setExperts([]);
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

  const fetchMessages = async () => {
    try {
      const res = await api.get('/messages/', { params: { _refresh: lastRefresh } });
      const messagesData = res.data.results || res.data || [];
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
    setFichierPdfError(null);

    try {
      const formDataToSend = new FormData();
    
      Object.keys(newOffreForm).forEach(key => {
        if (newOffreForm[key] !== '' && newOffreForm[key] !== null) {
          formDataToSend.append(key, newOffreForm[key]);
        }
      });
    
      if (fichierPdf) {
        if (fichierPdf.type !== 'application/pdf' && !fichierPdf.name.toLowerCase().endsWith('.pdf')) {
          setFichierPdfError('Seuls les fichiers PDF sont acceptés');
          return;
        }
      
        if (fichierPdf.size > 10 * 1024 * 1024) {
          setFichierPdfError('Le fichier ne doit pas dépasser 10 MB');
          return;
        }
      
        formDataToSend.append('fichier_pdf', fichierPdf);
      }
    
      if (!fichierPdf && !newOffreForm.url_tdr) {
        console.log('Aucun PDF fourni (URL ou fichier)');
      }

      await api.post('/offres/create-manuel/', formDataToSend, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
    
      setNewOffreSuccess(' Offre publiée avec succès !');
  
      setNewOffreForm({
        titre: '', organisme: '', description: '', pays: 'BF',
        date_publication: '', date_cloture: '',
        url_source: '', url_tdr: '', statut: 'Ouvert'
      });
      setFichierPdf(null);
  
      setTimeout(() => {
        setShowNewOffreModal(false);
        setNewOffreSuccess(null);
        fetchOffres();
        fetchStats();
      }, 2000);
  
    } catch (err) {
      console.error('❌ Erreur publication:', err);
      const errorMsg = err.response?.data 
        ? (typeof err.response.data === 'string' 
            ? err.response.data 
            : Object.entries(err.response.data).map(([key, val]) => `${key}: ${Array.isArray(val) ? val.join(', ') : val}`).join(' | '))
        : 'Erreur lors de la publication';
      setNewOffreError(errorMsg);
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

    if (!window.confirm(`Lancer le scraping sur ${selectedItems.length} source(s) ?\n\n⏱️ Cela peut prendre plusieurs minutes.`)) return;

    // ✅ Démarrer le scraping
    setIsScraping(true);
    setScrapingMessage(' Scraping en cours... Cela peut prendre plusieurs minutes.');
    setScrapingResult(null);
    setError(null);
    setSuccess(null);

    try {
      // ✅ Augmenter le timeout à 10 minutes (600000 ms)
      const response = await api.post('/admin/sources/run/', 
        { source_ids: selectedItems },
        { timeout: 600000 }  // 10 minutes
      );
      
      setScrapingResult(response.data);
      setScrapingMessage(' Scraping terminé avec succès !');
      
      const newTimestamp = Date.now();
      setLastRefresh(newTimestamp);
    
      await Promise.all([
        fetchOffres(),
        fetchStats(),
        fetchSources()
      ]);
    
      setSelectedItems([]);
      
      // Masquer le résultat après 15 secondes
      setTimeout(() => {
        setScrapingResult(null);
        setScrapingMessage('');
      }, 15000);
    
    } catch (err) {
      console.error(' Erreur scraping:', err);
      
      if (err.code === 'ECONNABORTED') {
        setScrapingMessage('⏱ Le scraping a pris trop de temps. Veuillez réessayer avec moins de sources.');
      } else {
        setScrapingMessage(` Erreur: ${err.response?.data?.error || err.message}`);
      }
      
      // Masquer l'erreur après 10 secondes
      setTimeout(() => {
        setScrapingMessage('');
        setScrapingResult(null);
      }, 10000);
      
    } finally {
      setIsScraping(false);
    }
  };

  const handleAddSource = async (e) => {
    e.preventDefault();

    try {
      let urlRacine = formData.url_racine?.trim() || '';
      if (urlRacine && !urlRacine.startsWith('http://') && !urlRacine.startsWith('https://')) {
        urlRacine = 'https://' + urlRacine;
      }
      
      const sourceData = {
        nom: formData.nom?.trim(),
        url_racine: urlRacine,
        frequence_maj: formData.frequence_maj || 'Toutes les 24h',
        est_actif: true
      };
      
      console.log(' Données envoyées:', sourceData);
      
      const response = await api.post('/admin/sources/', sourceData);
      
      setShowModal({ type: null, data: null });
      setFormData({});
      setSuccess('✅ Source ajoutée avec succès (active par défaut)');
      
      await fetchSources();
      
      setTimeout(() => setSuccess(null), 3000);
      
    } catch (err) {
      console.error('❌ Erreur complète:', err);
      console.error('❌ Réponse backend:', err.response?.data);
      
      const errorMsg = err.response?.data?.details 
        ? Object.values(err.response.data.details).join(', ')
        : err.response?.data?.error || 'Échec de l\'ajout';
        
      setError(`❌ Erreur: ${errorMsg}`);
      
      setTimeout(() => setError(null), 5000);
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
  
    if (!formData.expert || !formData.offre) {
      setError('❌ Veuillez sélectionner un expert et une offre');
      setTimeout(() => setError(null), 5000);
      return;
    }
  
    try {
      const suggestionData = {
        expert: formData.expert,
        offre: formData.offre,
        commentaire_admin: formData.commentaire_admin || ''
      };
    
      console.log(' Données envoyées:', suggestionData);
    
      const response = await api.post('/admin/suggestions/', suggestionData);
      console.log(' Réponse:', response.data);
    
      setShowModal({ type: null, data: null });
      setFormData({});
      setSuccess('Suggestion envoyée à l\'expert');
      await fetchSuggestions();
    
      setTimeout(() => setSuccess(null), 3000);
    
    } catch (err) {
      console.error(' Erreur envoi suggestion:', err);
      console.error(' Réponse backend:', err.response?.data);
    
      let errorMsg = 'Échec de l\'envoi';
      if (err.response?.data) {
        if (typeof err.response.data === 'object') {
          errorMsg = Object.entries(err.response.data)
            .map(([key, val]) => `${key}: ${Array.isArray(val) ? val.join(', ') : val}`)
            .join(' | ');
        } else {
          errorMsg = String(err.response.data);
        }
      }
    
      setError(`❌ Erreur: ${errorMsg}`);
      setTimeout(() => setError(null), 5000);
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

  const handleClearHistory = async () => {
    if (confirmText !== 'EFFACER TOUT') {
      setError('Tapez "EFFACER TOUT" pour valider');
      return;
    }
    
    try {
      await api.post('/admin/historique/clear/', { 
        confirm: 'EFFACER TOUT'
      });
      
      setSuccess(' Historique effacé avec succès');
      setShowModal({ type: null, data: null });
      setConfirmText('');
      setFormData({});
      await fetchHistorique();
      
      setTimeout(() => setSuccess(null), 3000);
    } catch (err) {
      console.error(' Erreur effacement historique:', err);
      console.error(' Réponse backend:', err.response?.data);
      
      const errorMsg = err.response?.data?.error || 'Échec de l\'effacement';
      setError(` Erreur: ${errorMsg}`);
      setTimeout(() => setError(null), 5000);
    }
  };

  // =============================================================================
  // ACTIONS : MESSAGES
  // =============================================================================
  const markMessageAsRead = async (messageId) => {
    try {
      // ✅ URL correcte : /messages/{id}/marquer-lu/
      await api.post(`/messages/${messageId}/marquer-lu/`);
      setMessages(prevMessages => prevMessages.map(msg => 
        msg.id === messageId ? {...msg, est_lu: true} : msg
      ));
      fetchStats();
    } catch (err) {
      console.error(' Erreur marquage lu:', err);
    }
  };

  const handleReplyMessage = async (messageId, replyContent) => {
    if (!replyContent.trim()) return;
  
    try {
     // ✅ Étape 1 : Marquer comme lu
      await api.post(`/messages/${messageId}/marquer-lu/`);
    
      // ✅ Étape 2 : Envoyer la réponse (NOUVELLE URL !)
      const response = await api.post(`/messages/${messageId}/repondre/`, {
        contenu: replyContent
      });
    
      // ✅ Étape 3 : Mettre à jour l'état local
      setMessages(prevMessages => prevMessages.map(msg => 
        msg.id === messageId ? {
          ...msg, 
          est_lu: true, 
          est_reponse: true,
          reponse_contenu: replyContent
        } : msg
      ));
    
      setSuccess(' Réponse envoyée');
      await Promise.all([fetchMessages(), fetchStats()]);
      setTimeout(() => setSuccess(null), 3000);
    
    } catch (err) {
      console.error(' Erreur envoi réponse:', err);
      setError(` Erreur: ${err.response?.data?.error || 'Échec de l\'envoi'}`);
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
  const receivedMessages = messages.filter(msg => isAdminDestinataire(msg) && !msg.est_reponse);
  const sentMessages = messages.filter(msg => isAdminExpediteur(msg) || msg.est_reponse);
  const unreadMessages = messages.filter(msg => isAdminDestinataire(msg) && !msg.est_lu && !msg.est_reponse);
  
  const totalCount = messages.length;
  const receivedCount = receivedMessages.length;
  const sentCount = sentMessages.length;
  const unreadCount = unreadMessages.length;

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
        <div className="alert alert-danger alert-dismissible fade show py-1 small d-flex align-items-center" role="alert">
          <i className="bi bi-exclamation-triangle-fill me-2"></i>
          <span className="flex-grow-1">{error}</span>
          <button type="button" className="btn-close btn-close-sm" onClick={() => setError(null)}></button>
        </div>
      )}
      {success && (
        <div className="alert alert-success alert-dismissible fade show py-1 small d-flex align-items-center" role="alert">
          <i className="bi bi-check-circle-fill me-2"></i>
          <span className="flex-grow-1">{success}</span>
          <button type="button" className="btn-close btn-close-sm" onClick={() => setSuccess(null)}></button>
        </div>
      )}

      {/* En-tête */}
      <div className="row mb-2">
        <div className="col-12 d-flex justify-content-between align-items-center">
          <h3 className="mb-0" style={{ fontSize: '1.5rem' }}>
            <i className="bi bi-speedometer2 me-2"></i>
            Administrateur
          </h3>
          <div className="d-flex gap-2">
            <button 
              className="btn btn-success btn-sm" 
              onClick={() => setShowNewOffreModal(true)}
              style={{ padding: '4px 8px', fontSize: '0.7rem' }}
            >
              <i className="bi bi-plus-circle me-1"></i>
              Publier une offre
            </button>
          </div>
        </div>
      </div>

      {/* Onglets compacts */}
      <div className="mb-2">
        <div className="d-flex gap-2 border-bottom pb-1 flex-nowrap" style={{ overflowX: 'auto' }}>
          {[
            { id: 'dashboard', label: 'Dashboard', icon: 'bi-speedometer2' },
            { id: 'sources', label: 'Sources', icon: 'bi-database' },
            { id: 'utilisateurs', label: 'Utilisateurs', icon: 'bi-people' },
            { id: 'messages', label: `Messages ${unreadCount > 0 ? `(${unreadCount})` : ''}`, icon: 'bi-chat-dots' },
            { id: 'suggestions', label: 'Suggestions', icon: 'bi-lightbulb' },
            { id: 'historique', label: 'Historique', icon: 'bi-clock-history' }
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
              <i className={`bi ${tab.icon} me-1`}></i>
              {tab.label}
            </button>
          ))}
        </div>
      </div>

      {/* === ONGLET DASHBOARD === */}
      {activeTab === 'dashboard' && stats && (
        <>
          {/* Cartes KPI - Version professionnelle */}
          <div className="row g-2 mb-3">
            {[
              { label: 'Offres', value: stats.offres?.total, sub: `Total: ${stats.offres?.total || 0}`, icon: 'bi-file-earmark-text', variant: 'offres' },
              { label: 'Users', value: stats.utilisateurs?.total, sub: `Total: ${stats.utilisateurs?.total || 0}`, icon: 'bi-people', variant: 'users' },
              { label: 'Msg', value: unreadCount, sub: `Total: ${totalCount}`, icon: 'bi-chat-dots', variant: 'messages' },
              { label: 'Sug.', value: stats.suggestions?.envoyees, sub: `Consultées: ${stats.suggestions?.consultees || 0}`, icon: 'bi-lightbulb', variant: 'suggestions' }
            ].map((card, idx) => (
              <div className="col-6 col-md-3" key={idx}>
                <div className={`kpi-card kpi-card-${card.variant}`}>
                  <div className="kpi-card-body">
                    <div className="kpi-icon">
                      <i className={`bi ${card.icon}`}></i>
                    </div>
                    <h4 className="kpi-value">{card.value || 0}</h4>
                    <p className="kpi-label">{card.label}</p>
                    <small className="kpi-sub">{card.sub}</small>
                  </div>
                </div>
              </div>
            ))}
          </div>

          {/* Section basse */}
          <div className="row g-2">
            <div className="col-md-6">
              <div className="card border-0 shadow-sm h-100">
                <div className="card-header bg-white py-2 px-3 d-flex justify-content-between align-items-center">
                  <h6 className="mb-0" style={{ fontSize: '0.8rem' }}>
                    <i className="bi bi-database me-1"></i>
                    Sources des offres
                  </h6>
                  <button 
                    className="btn btn-sm btn-outline-primary" 
                    onClick={() => setActiveTab('sources')} 
                    style={{ padding: '2px 8px', fontSize: '0.65rem' }}
                  >
                    <i className="bi bi-gear me-1"></i>
                    Gérer
                  </button>
                </div>
                <div className="card-body p-2">
                  {stats.offres?.par_source && stats.offres.par_source.length > 0 ? (
                    stats.offres.par_source.map((source, idx) => {
                      const total = stats.offres?.total || 1;
                      const percent = Math.round((source.count / total) * 100);
                      
                      return (
                        <div key={idx} className="mb-2">
                          <div className="d-flex justify-content-between align-items-center mb-1">
                            <span style={{ fontSize: '0.7rem' }} className="text-truncate" style={{ maxWidth: '150px' }}>
                              <i className="bi bi-globe me-1 text-primary"></i>
                              {source.nom}
                            </span>
                            <div className="d-flex align-items-center gap-2">
                              <span className="badge bg-primary me-1" style={{ fontSize: '0.6rem' }}>
                                {source.count}
                              </span>
                              <span className="text-muted" style={{ fontSize: '0.55rem' }}>
                                ({percent}%)
                              </span>
                              <button
                                className="btn btn-sm btn-outline-secondary"
                                onClick={() => openEditSourceModal(source)}
                                style={{ padding: '0 3px', fontSize: '0.55rem' }}
                                title="Modifier cette source"
                              >
                                <i className="bi bi-pencil"></i>
                              </button>
                            </div>
                          </div>
                          <div className="progress" style={{ height: '3px' }}>
                            <div 
                              className="progress-bar bg-primary" 
                              style={{ width: `${percent}%` }}
                              role="progressbar"
                            />
                          </div>
                        </div>
                      );
                    })
                  ) : (
                    <p className="text-muted text-center py-3 small">Aucune source avec offres</p>
                  )}
                  <div className="mt-2 pt-1 border-top text-center">
                    <small className="text-muted" style={{ fontSize: '0.6rem' }}>
                      <i className="bi bi-bar-chart me-1"></i>
                      Total: {stats.offres?.total || 0} offres
                    </small>
                  </div>
                </div>
              </div>
            </div>

            <div className="col-md-6">
              <div className="card border-0 shadow-sm h-100">
                <div className="card-header bg-white py-2 px-3">
                  <h6 className="mb-0" style={{ fontSize: '0.8rem' }}>
                    <i className="bi bi-activity me-1"></i>
                    Activité récente
                  </h6>
                </div>
                <div className="card-body p-2">
                  <div className="d-flex justify-content-between align-items-center mb-2">
                    <div>
                      <i className="bi bi-calendar-check" style={{ fontSize: '1rem' }}></i>
                      <span className="ms-1" style={{ fontSize: '0.7rem' }}>Connexions aujourd'hui</span>
                    </div>
                    <span className={`badge fs-6 px-2 py-1 ${stats.connexions?.aujourdhui > 0 ? 'bg-success' : 'bg-secondary'}`}>
                      {stats.connexions?.aujourdhui || 0}
                    </span>
                  </div>
                  
                  <div className="d-flex justify-content-between align-items-center mb-2">
                    <div>
                      <i className="bi bi-calendar-week" style={{ fontSize: '1rem' }}></i>
                      <span className="ms-1" style={{ fontSize: '0.7rem' }}>Connexions cette semaine</span>
                    </div>
                    <span className="badge bg-info px-2 py-1">
                      {stats.connexions?.semaine || 0}
                    </span>
                  </div>
                  
                  <div className="d-flex justify-content-between align-items-center">
                    <div>
                      <i className="bi bi-person-plus" style={{ fontSize: '1rem' }}></i>
                      <span className="ms-1" style={{ fontSize: '0.7rem' }}>Nouveaux inscrits (30j)</span>
                    </div>
                    <span className="badge bg-warning text-dark px-2 py-1">
                      {stats.utilisateurs?.nouveaux_30j || 0}
                    </span>
                  </div>
                  
                  {stats.connexions?.semaine > 0 && (
                    <div className="mt-2 pt-2 border-top text-center">
                      <small className="text-success" style={{ fontSize: '0.6rem' }}>
                        <i className="bi bi-graph-up-arrow me-1"></i>
                        Activité en hausse cette semaine
                      </small>
                    </div>
                  )}
                  {stats.connexions?.semaine === 0 && stats.connexions?.aujourdhui === 0 && (
                    <div className="mt-2 pt-2 border-top text-center">
                      <small className="text-muted" style={{ fontSize: '0.6rem' }}>
                        <i className="bi bi-moon me-1"></i>
                        Aucune activité récente
                      </small>
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>
        </>
      )}

      {/* === ONGLET SOURCES - ✅ CORRIGÉ AVEC SCROLL === */}
      {activeTab === 'sources' && (
        <div className="card" style={{ maxHeight: '75vh', display: 'flex', flexDirection: 'column' }}>
          <div className="card-header bg-white d-flex justify-content-between align-items-center py-1 px-2" style={{ flexShrink: 0 }}>
            <h6 className="mb-0" style={{ fontSize: '0.8rem' }}>
              <i className="bi bi-database me-1"></i>
              Sources de scraping
            </h6>
            <div className="d-flex gap-1">
              <button className="btn btn-primary btn-sm" onClick={() => openModal('addSource')} style={{ padding: '1px 4px', fontSize: '0.65rem' }}>
                <i className="bi bi-plus me-1"></i>Ajouter
              </button>
              <button 
                className="btn btn-success btn-sm" 
                onClick={handleLaunchScraping}
                disabled={selectedItems.length === 0 || isScraping}
                style={{ padding: '1px 4px', fontSize: '0.65rem' }}
              >
                {isScraping ? (
                  <>
                    <span className="spinner-border spinner-border-sm me-1" role="status" style={{ width: '0.7rem', height: '0.7rem' }}></span>
                    Scraping...
                  </>
                ) : (
                  <>
                    <i className="bi bi-play-fill me-1"></i>
                    Lancer ({selectedItems.length})
                  </>
                )}
              </button>
            </div>
          </div>
          
          {/* ✅ EN-TÊTE DYNAMIQUE AVEC LE COMPTEUR TOTAL */}
          <div className="d-flex justify-content-between align-items-center mb-2 px-1">
            <span className="fw-bold text-secondary" style={{ fontSize: '0.8rem' }}>
              <i className="bi bi-list-nested me-1"></i>
              Total des sources de scraping : <span className="badge bg-primary ms-1">{sources.length}</span>
            </span>
          </div>

          {/* ✅ TABLEAU AVEC SCROLL VERTICAL ET HORIZONTAL */}
          <div 
            className="table-responsive border rounded" 
            style={{ 
              maxHeight: '400px', 
              overflowY: 'auto', 
              overflowX: 'auto',
              flex: 1 
            }}
          >
            <table className="table table-hover table-sm align-middle mb-0" style={{ fontSize: '0.75rem' }}>
              <thead className="table-light sticky-top" style={{ top: 0, zIndex: 10, backgroundColor: '#f8f9fa' }}>
                <tr>
                  <th style={{ width: '30px', paddingLeft: '10px' }}>
                    <input 
                      type="checkbox" 
                      className="form-check-input"
                      style={{ transform: 'scale(0.85)', cursor: 'pointer' }}
                      checked={sources.length > 0 && selectedItems.length === sources.length}
                      onChange={toggleSelectAll}
                    />
                  </th>
                  <th>Source</th>
                  <th>URL Site Cible</th>
                  <th>Statut</th>
                  <th>Dernier scraping</th>
                  <th style={{ width: '80px', textAlign: 'center' }}>Actions</th>
                </tr>
              </thead>
              <tbody>
                {sources.map(source => (
                  <tr key={source.id}>
                    <td style={{ paddingLeft: '10px' }}>
                      <input 
                        type="checkbox" 
                        className="form-check-input"
                        style={{ transform: 'scale(0.85)', cursor: 'pointer' }}
                        checked={selectedItems.includes(source.id)}
                        onChange={() => toggleSelect(source.id)}
                      />
                    </td>
                    <td className="fw-semibold text-dark text-truncate" style={{ maxWidth: '120px' }}>
                      <i className="bi bi-globe me-1 text-primary"></i>
                      {source.nom}
                    </td>
                    <td>
                      <a 
                        href={source.url_racine} 
                        target="_blank" 
                        rel="noopener noreferrer" 
                        className="text-truncate d-inline-block text-decoration-none" 
                        style={{ maxWidth: '180px', color: 'var(--bs-primary)' }}
                        title={source.url_racine}
                      >
                        <i className="bi bi-link-45deg me-1"></i>
                        {source.url_racine?.replace('https://', '').replace('http://', '').substring(0, 28)}...
                      </a>
                    </td>
                    <td>
                      <button
                        onClick={() => handleToggleSourceActive(source.id, source.est_actif)}
                        className={`badge d-inline-flex align-items-center gap-1 ${source.est_actif ? 'bg-success' : 'bg-secondary'}`}
                        style={{ 
                          fontSize: '0.65rem', 
                          cursor: 'pointer',
                          border: 'none',
                          padding: '4px 8px',
                          borderRadius: '4px',
                          transition: 'all 0.2s ease'
                        }}
                        title={source.est_actif ? 'Cliquez pour désactiver' : 'Cliquez pour activer'}
                      >
                        {source.est_actif ? (
                          <><i className="bi bi-check-circle"></i>Actif</>
                        ) : (
                          <><i className="bi bi-x-circle"></i>Inactif</>
                        )}
                      </button>
                    </td>
                    <td className="text-muted">
                      <i className="bi bi-clock me-1" style={{ fontSize: '0.7rem' }}></i>
                      {source.last_scraped ? new Date(source.last_scraped).toLocaleDateString('fr-FR') : '-'}
                    </td>
                    <td>
                      <div className="d-flex gap-1 justify-content-center">
                        <button 
                          className="btn btn-sm btn-outline-primary" 
                          onClick={() => openEditSourceModal(source)}
                          style={{ padding: '2px 6px', fontSize: '0.7rem' }}
                          title="Modifier la source"
                        >
                          <i className="bi bi-pencil"></i>
                        </button>
                        <button 
                          className="btn btn-sm btn-outline-danger" 
                          onClick={() => handleDeleteSource(source.id)} 
                          style={{ padding: '2px 6px', fontSize: '0.7rem' }}
                          title="Supprimer la source"
                        >
                          <i className="bi bi-trash"></i>
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
      
                {!sources.length && (
                  <tr>
                    <td colSpan="6" className="text-center py-4 text-muted bg-light">
                      <i className="bi bi-folder-x me-1 fs-5 d-block mb-1"></i>
                      Aucune source de scraping configurée.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* === ONGLET UTILISATEURS === */}
      {activeTab === 'utilisateurs' && (
        <div className="card">
          <div className="card-header bg-white d-flex justify-content-between align-items-center py-1 px-2">
            <h6 className="mb-0" style={{ fontSize: '0.8rem' }}>
              <i className="bi bi-people me-1"></i>
              Utilisateurs
            </h6>
            <button className="btn btn-primary btn-sm" onClick={() => openModal('addUser')} style={{ padding: '1px 4px', fontSize: '0.65rem' }}>
              <i className="bi bi-person-plus me-1"></i>Ajouter
            </button>
          </div>
          <div className="table-responsive">
            <table className="table table-hover table-sm mb-0" style={{ fontSize: '0.7rem' }}>
              <thead className="table-light">
                <tr>
                  <th>Email</th>
                  <th>Nom</th>
                  <th>Rôle</th>
                  <th>Statut</th>
                  <th style={{ width: '220px' }}>Actions</th>
                </tr>
              </thead>
              <tbody>
                {utilisateurs.map(user => (
                  <tr key={user.id}>
                    <td className="text-truncate" style={{ maxWidth: '150px' }}>
                      <i className="bi bi-envelope me-1 text-muted"></i>
                      {user.email}
                    </td>
                    <td className="text-truncate" style={{ maxWidth: '100px' }}>
                      <i className="bi bi-person me-1 text-muted"></i>
                      {user.nom || `${user.first_name} ${user.last_name}`}
                    </td>
                    <td>
                      <span className="badge bg-secondary" style={{ fontSize: '0.6rem' }}>
                        {user.role === 'EXPERT' && <i className="bi bi-person-badge me-1"></i>}
                        {user.role === 'BUREAU' && <i className="bi bi-building me-1"></i>}
                        {user.role === 'ADMIN' && <i className="bi bi-shield-lock me-1"></i>}
                        {user.role}
                      </span>
                    </td>
                    <td>
                      <span className={`badge ${user.is_active ? 'bg-success' : 'bg-secondary'}`} style={{ fontSize: '0.6rem' }}>
                        {user.is_active ? (
                          <><i className="bi bi-check-circle-fill me-1"></i>Actif</>
                        ) : (
                          <><i className="bi bi-x-circle-fill me-1"></i>Inactif</>
                        )}
                      </span>
                    </td>
                    <td>
                      <div className="d-flex gap-1 flex-wrap">
                        <button
                          className="btn btn-outline-info btn-sm"
                          onClick={() => fetchUserDetails(user.id)}
                          style={{ padding: '0 3px', fontSize: '0.65rem' }}
                          title="Voir les détails complets"
                        >
                          <i className="bi bi-eye me-1"></i>Détails
                        </button>
                  
                        <button
                          className={`btn btn-sm ${user.is_active ? 'btn-outline-warning' : 'btn-outline-success'}`}
                          onClick={() => handleToggleUserActive(user.id, user.is_active)}
                          style={{ padding: '0 3px', fontSize: '0.65rem' }}
                          title={user.is_active ? 'Bloquer' : 'Débloquer'}
                        >
                          {user.is_active ? (
                            <i className="bi bi-lock"></i>
                          ) : (
                            <i className="bi bi-unlock"></i>
                          )}
                        </button>
                  
                        <button
                          className="btn btn-outline-danger btn-sm"
                          onClick={() => openModal('deleteUser', user)}
                          style={{ padding: '0 3px', fontSize: '0.65rem' }}
                          title="Supprimer"
                        >
                          <i className="bi bi-trash"></i>
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

      {/* === ONGLET MESSAGES === */}
      {activeTab === 'messages' && (
        <div className="card">
          <div className="card-header bg-white py-2 px-3">
            <div className="d-flex justify-content-between align-items-center flex-wrap gap-2">
              <h6 className="mb-0" style={{ fontSize: '0.9rem' }}>
                <i className="bi bi-chat-dots me-1"></i>
                Messages
              </h6>
              <div className="btn-group btn-group-sm">
                <button 
                  className={`btn ${messageFilter === 'all' ? 'btn-primary' : 'btn-outline-secondary'}`}
                  onClick={() => setMessageFilter('all')}
                  style={{ fontSize: '0.7rem', padding: '4px 10px' }}
                >
                  <i className="bi bi-inbox me-1"></i>Tous ({totalCount})
                </button>
                <button 
                  className={`btn ${messageFilter === 'received' ? 'btn-primary' : 'btn-outline-secondary'}`}
                  onClick={() => setMessageFilter('received')}
                  style={{ fontSize: '0.7rem', padding: '4px 10px' }}
                >
                  <i className="bi bi-inbox-fill me-1"></i>Reçus ({receivedCount})
                </button>
                <button 
                  className={`btn ${messageFilter === 'sent' ? 'btn-primary' : 'btn-outline-secondary'}`}
                  onClick={() => setMessageFilter('sent')}
                  style={{ fontSize: '0.7rem', padding: '4px 10px' }}
                >
                  <i className="bi bi-send me-1"></i>Envoyés ({sentCount})
                </button>
                <button 
                  className={`btn ${messageFilter === 'unread' ? 'btn-primary' : 'btn-outline-secondary'}`}
                  onClick={() => setMessageFilter('unread')}
                  style={{ fontSize: '0.7rem', padding: '4px 10px' }}
                >
                  <i className="bi bi-envelope me-1"></i>Non lus ({unreadCount})
                </button>
              </div>
            </div>
          </div>
          <div className="card-body p-3">
            {getFilteredMessages().length === 0 ? (
              <div className="text-center py-4">
                <i className="bi bi-chat-square-text" style={{ fontSize: '2rem', color: '#ccc' }}></i>
                <p className="text-muted mb-0 small mt-2">
                  {messageFilter === 'received' && 'Aucun message reçu'}
                  {messageFilter === 'sent' && 'Aucun message envoyé'}
                  {messageFilter === 'unread' && 'Aucun message non lu'}
                  {messageFilter === 'all' && 'Aucun message'}
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
                            {isSent && !isReceived && <span className="badge bg-info" style={{ fontSize: '0.65rem' }}><i className="bi bi-send me-1"></i>Envoyé</span>}
                            {isReceived && <span className="badge bg-secondary" style={{ fontSize: '0.65rem' }}><i className="bi bi-inbox me-1"></i>Reçu</span>}
                            {msg.est_reponse && <span className="badge bg-success" style={{ fontSize: '0.65rem' }}><i className="bi bi-reply me-1"></i>Réponse envoyée</span>}
                            {isUnread && <span className="badge bg-primary" style={{ fontSize: '0.65rem' }}><i className="bi bi-circle-fill me-1"></i>Nouveau</span>}
                            
                            <strong className="small">
                              <i className="bi bi-person me-1"></i>
                              {getExpediteurEmail(msg)}
                            </strong>
                            
                            <small className="text-muted">
                              <i className="bi bi-clock me-1"></i>
                              {new Date(msg.date_envoi).toLocaleString('fr-FR')}
                            </small>
                          </div>
                          
                          <h6 className="mb-1 small fw-bold">
                            <i className="bi bi-chat-left-text me-1"></i>
                            {msg.sujet}
                          </h6>
                          <p className="mb-2 small text-secondary">{msg.contenu}</p>
                          
                          {msg.reponse_contenu && (
                            <div className="mt-2 p-2 bg-light rounded" style={{ borderLeft: '3px solid #198754' }}>
                              <small className="text-success fw-semibold">
                                <i className="bi bi-reply-fill me-1"></i>
                                Votre réponse :
                              </small>
                              <p className="mb-0 small mt-1">{msg.reponse_contenu}</p>
                            </div>
                          )}
                          
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
                                <i className="bi bi-reply me-1"></i>
                                Répondre
                              </button>
                              <button 
                                className="btn btn-sm btn-outline-danger"
                                onClick={(e) => {
                                  e.stopPropagation();
                                  handleDeleteMessage(msg.id);
                                }}
                                style={{ fontSize: '0.7rem', padding: '3px 10px' }}
                              >
                                <i className="bi bi-trash me-1"></i>
                                Supprimer
                              </button>
                            </div>
                          )}
                          
                          {isSent && !isReceived && (
                            <button 
                              className="btn btn-sm btn-outline-danger mt-2"
                              onClick={(e) => {
                                e.stopPropagation();
                                handleDeleteMessage(msg.id);
                              }}
                              style={{ fontSize: '0.7rem', padding: '2px 8px' }}
                            >
                              <i className="bi bi-trash me-1"></i>
                              Supprimer
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
            <h6 className="mb-0" style={{ fontSize: '0.8rem' }}>
              <i className="bi bi-lightbulb me-1"></i>
              Suggestions
            </h6>
            <button className="btn btn-primary btn-sm" onClick={() => openModal('sendSuggestion')} style={{ padding: '1px 4px', fontSize: '0.65rem' }}>
              <i className="bi bi-plus me-1"></i>Nouvelle
            </button>
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
                    <td className="text-truncate" style={{ maxWidth: '120px' }}>
                      <i className="bi bi-person-badge me-1 text-primary"></i>
                      {sug.expert_nom}
                    </td>
                    <td className="text-truncate" style={{ maxWidth: '150px' }}>
                      <i className="bi bi-file-earmark-text me-1 text-muted"></i>
                      {sug.offre_titre?.substring(0, 30)}...
                    </td>
                    <td>
                      <i className="bi bi-calendar me-1 text-muted"></i>
                      {new Date(sug.date_suggestion).toLocaleDateString('fr-FR')}
                    </td>
                    <td>
                      <span className={`badge ${sug.est_consulte_par_expert ? 'bg-success' : 'bg-warning'}`} style={{ fontSize: '0.6rem' }}>
                        {sug.est_consulte_par_expert ? (
                          <><i className="bi bi-check-circle me-1"></i>Consulté</>
                        ) : (
                          <><i className="bi bi-hourglass-split me-1"></i>En attente</>
                        )}
                      </span>
                    </td>
                    <td>
                      <button 
                        className="btn btn-outline-danger btn-sm"
                        onClick={() => handleDeleteSuggestion(sug.id)}
                        style={{ padding: '0 3px', fontSize: '0.65rem' }}
                        title="Supprimer"
                      >
                        <i className="bi bi-trash"></i>
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
            <h6 className="mb-0" style={{ fontSize: '0.8rem' }}>
              <i className="bi bi-clock-history me-1"></i>
              Historique
            </h6>
            <button 
              className="btn btn-outline-danger btn-sm"
              onClick={() => openModal('clearHistory')}
              style={{ padding: '1px 4px', fontSize: '0.65rem' }}
            >
              <i className="bi bi-trash me-1"></i>Effacer
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
                    <td>
                      <span className="badge bg-light text-dark border" style={{ fontSize: '0.6rem' }}>
                        <i className="bi bi-gear me-1"></i>
                        {entry.action_type}
                      </span>
                    </td>
                    <td className="text-truncate" style={{ maxWidth: '120px' }}>
                      <i className="bi bi-person me-1 text-muted"></i>
                      {entry.utilisateur_email}
                    </td>
                    <td>
                      <i className="bi bi-calendar me-1 text-muted"></i>
                      {new Date(entry.date_action).toLocaleDateString('fr-FR')}
                    </td>
                    <td className="text-truncate text-muted" style={{ maxWidth: '200px' }}>
                      <i className="bi bi-info-circle me-1"></i>
                      {entry.details?.substring(0, 50)}...
                    </td>
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
          <div className="modal-dialog modal-dialog-centered modal-lg modal-dialog-scrollable">
            <div className="modal-content">
              <div 
                className="modal-header py-2 px-3 text-white"
                style={{
                  background: '#032b9a',
                  borderBottom: '3px solid #4d94f7',
                  boxShadow: '0 2px 8px rgba(239, 199, 130, 0.3)'
                }}
              >
                <h6 className="modal-title" style={{ fontSize: '0.85rem' }}>
                  <i className="bi bi-plus-circle me-2"></i>
                  Publier une nouvelle offre
                </h6>
                <button type="button" className="btn-close btn-close-white btn-close-sm" onClick={() => setShowNewOffreModal(false)}></button>
              </div>
        
              <div className="modal-body py-2 px-3">
                {newOffreError && (
                  <div className="alert alert-danger alert-dismissible fade show py-1 small d-flex align-items-center" role="alert">
                    <i className="bi bi-exclamation-triangle-fill me-2"></i>
                    <span className="flex-grow-1">{typeof newOffreError === 'string' ? newOffreError : JSON.stringify(newOffreError)}</span>
                    <button type="button" className="btn-close btn-close-sm" onClick={() => setNewOffreError(null)}></button>
                  </div>
                )}
                {newOffreSuccess && (
                  <div className="alert alert-success alert-dismissible fade show py-1 small d-flex align-items-center" role="alert">
                    <i className="bi bi-check-circle-fill me-2"></i>
                    {newOffreSuccess}
                  </div>
                )}
          
                <form onSubmit={handlePublishOffre}>
                  <div className="row g-2">
                    <div className="col-12">
                      <label className="form-label" style={{ fontSize: '0.7rem' }}>
                        <i className="bi bi-file-earmark-text me-1"></i>
                        Titre de l'offre <span className="text-danger">*</span>
                      </label>
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
                      <label className="form-label" style={{ fontSize: '0.7rem' }}>
                        <i className="bi bi-building me-1"></i>
                        Organisme <span className="text-danger">*</span>
                      </label>
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
                      <label className="form-label" style={{ fontSize: '0.7rem' }}>
                        <i className="bi bi-geo-alt me-1"></i>
                        Pays
                      </label>
                      <select 
                        className="form-select form-select-sm"
                        value={newOffreForm.pays}
                        onChange={e => setNewOffreForm({...newOffreForm, pays: e.target.value})}
                        style={{ fontSize: '0.75rem', padding: '2px 4px' }}
                      >
                        <option value="BF">🇧🇫 Burkina Faso</option>
                        <option value="CI">🇨 Côte d'Ivoire</option>
                        <option value="SN">🇸🇳 Sénégal</option>
                        <option value="ML">🇲🇱 Mali</option>
                        <option value="NE">🇳 Niger</option>
                        <option value="TG">🇹🇬 Togo</option>
                        <option value="BJ">🇧🇯 Bénin</option>
                        <option value="GH">🇬🇭 Ghana</option>
                        <option value="NA">🇳🇦 Nigeria</option>
                        <option value="LR">🇱🇷 Liberia</option>
                        <option value="SL">🇸 Sierra Leone</option>
                        <option value="GM">🇬 Gambie</option>
                      </select>
                    </div>
              
                    <div className="col-12">
                      <label className="form-label" style={{ fontSize: '0.7rem' }}>
                        <i className="bi bi-card-text me-1"></i>
                        Description
                        <span className="text-muted small ms-1">(optionnel)</span>
                      </label>
                      <textarea 
                        className="form-control form-control-sm"
                        rows="3"
                        value={newOffreForm.description}
                        onChange={e => setNewOffreForm({...newOffreForm, description: e.target.value})}
                        placeholder="Décrivez l'offre (optionnel)..."
                        style={{ fontSize: '0.75rem', padding: '2px 4px' }}
                      />
                    </div>
              
                    <div className="col-6">
                      <label className="form-label" style={{ fontSize: '0.7rem' }}>
                        <i className="bi bi-calendar-event me-1"></i>
                        Date de publication <span className="text-danger">*</span>
                      </label>
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
                      <label className="form-label" style={{ fontSize: '0.7rem' }}>
                        <i className="bi bi-calendar-x me-1"></i>
                        Date de clôture
                      </label>
                      <input 
                        type="date" 
                        className="form-control form-control-sm"
                        value={newOffreForm.date_cloture}
                        onChange={e => setNewOffreForm({...newOffreForm, date_cloture: e.target.value})}
                        style={{ fontSize: '0.75rem', padding: '2px 4px' }}
                      />
                    </div>
              
                    <div className="col-12">
                      <label className="form-label" style={{ fontSize: '0.7rem' }}>
                        <i className="bi bi-link-45deg me-1"></i>
                        URL source
                      </label>
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
                      <div className="card bg-light border-0 mb-2">
                        <div className="card-body py-2 px-3">
                          <h6 className="mb-2" style={{ fontSize: '0.75rem' }}>
                            <i className="bi bi-file-earmark-pdf me-1 text-danger"></i>
                            Document de l'offre (TDR)
                          </h6>
                          {/*<p className="mb-2 text-muted" style={{ fontSize: '0.65rem' }}>
                            Choisissez une option (ou les deux) :
                          </p>*/}
                    
                          <div className="mb-2">
                            {/*<label className="form-label small fw-semibold mb-1" style={{ fontSize: '0.65rem' }}>
                              <i className="bi bi-link-45deg me-1"></i>
                              Option 1 : URL vers le PDF
                            </label>*/}
                            {/*<input 
                              type="url" 
                              className="form-control form-control-sm"
                              value={newOffreForm.url_tdr}
                              onChange={e => setNewOffreForm({...newOffreForm, url_tdr: e.target.value})}
                              placeholder="https://.../document.pdf"
                              style={{ fontSize: '0.75rem', padding: '2px 4px' }}
                            />*/}
                          </div>

                          <div>
                            {/*<label className="form-label small fw-semibold mb-1" style={{ fontSize: '0.65rem' }}>
                              <i className="bi bi-upload me-1"></i>
                              Option 2 : Télécharger un fichier PDF
                            </label>*/}
                            <input 
                              type="file"
                              className={`form-control form-control-sm ${fichierPdfError ? 'is-invalid' : ''}`}
                              accept=".pdf,application/pdf"
                              onChange={(e) => {
                                const file = e.target.files[0];
                                setFichierPdfError(null);
                          
                                if (file) {
                                  if (file.type !== 'application/pdf' && !file.name.toLowerCase().endsWith('.pdf')) {
                                    setFichierPdfError('Seuls les fichiers PDF sont acceptés');
                                    setFichierPdf(null);
                                    return;
                                  }
                            
                                  if (file.size > 10 * 1024 * 1024) {
                                    setFichierPdfError('Le fichier ne doit pas dépasser 10 MB');
                                    setFichierPdf(null);
                                    return;
                                  }
                            
                                  setFichierPdf(file);
                                } else {
                                  setFichierPdf(null);
                                }
                              }}
                              style={{ fontSize: '0.75rem', padding: '2px 4px' }}
                            />
                            {fichierPdfError && (
                              <div className="invalid-feedback" style={{ fontSize: '0.65rem' }}>
                                {fichierPdfError}
                              </div>
                            )}
                      
                            {fichierPdf && (
                              <div className="alert alert-success mt-2 py-1 px-2 mb-0 d-flex align-items-center justify-content-between" style={{ fontSize: '0.65rem' }}>
                                <span>
                                  <i className="bi bi-file-earmark-check-fill me-1"></i>
                                  <strong>{fichierPdf.name}</strong> ({(fichierPdf.size / 1024).toFixed(0)} KB)
                                </span>
                                <button
                                  type="button"
                                  className="btn btn-sm btn-outline-danger"
                                  onClick={() => {
                                    setFichierPdf(null);
                                    const fileInput = document.querySelector('input[type="file"]');
                                    if (fileInput) fileInput.value = '';
                                  }}
                                  style={{ fontSize: '0.6rem', padding: '0 4px' }}
                                >
                                  <i className="bi bi-x"></i>
                                </button>
                              </div>
                            )}
                          </div>
                        </div>
                      </div>
                    </div>
              
                    <div className="col-6">
                      <label className="form-label" style={{ fontSize: '0.7rem' }}>
                        Statut
                      </label>
                      <select 
                        className="form-select form-select-sm"
                        value={newOffreForm.statut}
                        onChange={e => setNewOffreForm({...newOffreForm, statut: e.target.value})}
                        style={{ fontSize: '0.75rem', padding: '2px 4px' }}
                      >
                        <option value="Ouvert">Ouvert</option>
                      </select>
                    </div>
                  </div>
            
                  <div className="d-flex gap-2 mt-3">
                    <button type="submit" className="btn btn-sm" 
                      style={{ 
                        fontSize: '0.7rem', 
                        padding: '2px 6px',
                        background: '#058328',
                        color: 'white',
                        border: 'none',
                        fontWeight: '600'
                      }}
                    >
                      <i className="bi bi-check-circle me-1"></i>
                      Publier
                    </button>
                    <button 
                      type="button" 
                      className="btn btn-secondary btn-sm" 
                      onClick={() => {
                        setShowNewOffreModal(false);
                        setFichierPdf(null);
                        setFichierPdfError(null);
                      }} 
                      style={{ fontSize: '0.7rem', padding: '2px 6px' }}
                    >
                      <i className="bi bi-x-circle me-1"></i>
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
          MODAL : MODIFIER UNE SOURCE
          ============================================================================= */}
      {editSourceModal.show && editSourceModal.source && (
        <div className="modal fade show d-block" tabIndex="-1" style={{ backgroundColor: 'rgba(0,0,0,0.5)' }}>
          <div className="modal-dialog modal-dialog-centered">
            <div className="modal-content">
              <div className="modal-header py-2 px-3">
                <h6 className="modal-title" style={{ fontSize: '0.85rem' }}>
                  <i className="bi bi-pencil-square me-2"></i>
                  Modifier la source: {editSourceModal.source.nom}
                </h6>
                <button type="button" className="btn-close btn-close-sm" onClick={closeEditSourceModal}></button>
              </div>
              
              <div className="modal-body py-2 px-3">
                <form onSubmit={handleUpdateSource}>
                  <div className="mb-2">
                    <label className="form-label" style={{ fontSize: '0.7rem' }}>
                      <i className="bi bi-tag me-1"></i>
                      Nom <span className="text-danger">*</span>
                    </label>
                    <input 
                      type="text" 
                      className="form-control form-control-sm" 
                      value={editSourceForm.nom} 
                      onChange={e => setEditSourceForm({...editSourceForm, nom: e.target.value})} 
                      required 
                      style={{ fontSize: '0.75rem', padding: '2px 4px' }} 
                    />
                  </div>
                  <div className="mb-2">
                    <label className="form-label" style={{ fontSize: '0.7rem' }}>
                      <i className="bi bi-link-45deg me-1"></i>
                      URL <span className="text-danger">*</span>
                    </label>
                    <input 
                      type="url" 
                      className="form-control form-control-sm" 
                      value={editSourceForm.url_racine} 
                      onChange={e => setEditSourceForm({...editSourceForm, url_racine: e.target.value})} 
                      required 
                      style={{ fontSize: '0.75rem', padding: '2px 4px' }} 
                    />
                  </div>
                  <div className="mb-2">
                    <label className="form-label" style={{ fontSize: '0.7rem' }}>
                      <i className="bi bi-clock me-1"></i>
                      Fréquence
                    </label>
                    <input 
                      type="text" 
                      className="form-control form-control-sm" 
                      value={editSourceForm.frequence_maj} 
                      onChange={e => setEditSourceForm({...editSourceForm, frequence_maj: e.target.value})} 
                      style={{ fontSize: '0.75rem', padding: '2px 4px' }} 
                    />
                  </div>
                  <div className="mb-2">
                    <div className="form-check">
                      <input 
                        type="checkbox" 
                        className="form-check-input" 
                        id="est_actif_edit"
                        checked={editSourceForm.est_actif}
                        onChange={e => setEditSourceForm({...editSourceForm, est_actif: e.target.checked})}
                        style={{ transform: 'scale(0.8)' }}
                      />
                      <label className="form-check-label" style={{ fontSize: '0.7rem' }} htmlFor="est_actif_edit">
                        <i className="bi bi-power me-1"></i>
                        Source active (scraping automatique)
                      </label>
                    </div>
                  </div>
                  
                  <div className="d-flex gap-2 mt-3">
                    <button type="submit" className="btn btn-primary btn-sm" style={{ fontSize: '0.7rem', padding: '2px 6px' }}>
                      <i className="bi bi-check-circle me-1"></i>
                      Enregistrer
                    </button>
                    <button type="button" className="btn btn-secondary btn-sm" onClick={closeEditSourceModal} style={{ fontSize: '0.7rem', padding: '2px 6px' }}>
                      <i className="bi bi-x-circle me-1"></i>
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
          MODALS EXISTANTS (AJOUT, SUPPRESSION, etc.)
          ============================================================================= */}
      {showModal.type && (
        <div className="modal fade show d-block" tabIndex="-1" style={{ backgroundColor: 'rgba(0,0,0,0.5)' }}>
          <div className={`modal-dialog modal-dialog-centered ${showModal.type === 'sendSuggestion' ? 'modal-lg' : 'modal-sm'}`}>
            <div className="modal-content">
              <div className="modal-header py-2 px-3">
                <h6 className="modal-title" style={{ fontSize: '0.85rem' }}>
                  {showModal.type === 'addSource' && <><i className="bi bi-plus-circle me-2"></i>Ajouter une source</>}
                  {showModal.type === 'deleteUser' && <><i className="bi bi-exclamation-triangle me-2"></i>Supprimer un utilisateur</>}
                  {showModal.type === 'addUser' && <><i className="bi bi-person-plus me-2"></i>Ajouter un utilisateur</>}
                  {showModal.type === 'sendSuggestion' && <><i className="bi bi-lightbulb me-2"></i>Nouvelle suggestion</>}
                  {showModal.type === 'clearHistory' && <><i className="bi bi-trash me-2"></i>Effacer l'historique</>}
                </h6>
                <button type="button" className="btn-close btn-close-sm" onClick={closeModal}></button>
              </div>
              
              <div className="modal-body py-2 px-3">
                {/* Modal: Ajouter une source */}
                {showModal.type === 'addSource' && (
                  <form onSubmit={handleAddSource}>
                    <div className="mb-2">
                      <label className="form-label" style={{ fontSize: '0.7rem' }}>
                        <i className="bi bi-tag me-1"></i>
                        Nom <span className="text-danger">*</span>
                      </label>
                      <input type="text" className="form-control form-control-sm" value={formData.nom || ''} onChange={e => setFormData({...formData, nom: e.target.value})} required style={{ fontSize: '0.75rem', padding: '2px 4px' }} />
                    </div>
                    <div className="mb-2">
                      <label className="form-label" style={{ fontSize: '0.7rem' }}>
                        <i className="bi bi-link-45deg me-1"></i>
                        URL <span className="text-danger">*</span>
                      </label>
                      <input type="url" className="form-control form-control-sm" value={formData.url_racine || ''} onChange={e => setFormData({...formData, url_racine: e.target.value})} required style={{ fontSize: '0.75rem', padding: '2px 4px' }} />
                    </div>
                    <div className="mb-2">
                      <label className="form-label" style={{ fontSize: '0.7rem' }}>
                        <i className="bi bi-clock me-1"></i>
                        Fréquence
                      </label>
                      <input type="text" className="form-control form-control-sm" value={formData.frequence_maj || 'Toutes les 12h'} onChange={e => setFormData({...formData, frequence_maj: e.target.value})} style={{ fontSize: '0.75rem', padding: '2px 4px' }} />
                    </div>
                    <div className="mb-2">
                      <div className="form-check">
                        <input 
                          type="checkbox" 
                          className="form-check-input" 
                          id="est_actif_add"
                          checked={formData.est_actif !== undefined ? formData.est_actif : true}
                          onChange={e => setFormData({...formData, est_actif: e.target.checked})}
                          style={{ transform: 'scale(0.8)' }}
                        />
                        <label className="form-check-label" style={{ fontSize: '0.7rem' }} htmlFor="est_actif_add">
                          <i className="bi bi-power me-1"></i>
                          Source active (coché par défaut)
                        </label>
                      </div>
                    </div>
                    <button type="submit" className="btn btn-primary btn-sm w-100" style={{ fontSize: '0.7rem', padding: '2px 4px' }}>
                      <i className="bi bi-plus-circle me-1"></i>
                      Ajouter
                    </button>
                  </form>
                )}

                {/* Modal: Supprimer un utilisateur */}
                {showModal.type === 'deleteUser' && (
                  <div>
                    <p className="small mb-2">
                      <i className="bi bi-exclamation-triangle-fill me-1 text-danger"></i>
                      Supprimer <strong>{showModal.data?.email}</strong> ?<br/>
                      <span className="text-danger">Irréversible.</span>
                    </p>
                    <div className="mb-2">
                      <label className="form-label" style={{ fontSize: '0.7rem' }}>
                        <i className="bi bi-keyboard me-1"></i>
                        Tapez "CONFIRMER" :
                      </label>
                      <input type="text" className="form-control form-control-sm" value={confirmText} onChange={e => setConfirmText(e.target.value)} placeholder="CONFIRMER" style={{ fontSize: '0.75rem', padding: '2px 4px' }} />
                    </div>
                    <button className="btn btn-danger btn-sm w-100" onClick={() => handleDeleteUser(showModal.data?.id)} disabled={confirmText !== 'CONFIRMER'} style={{ fontSize: '0.7rem', padding: '2px 4px' }}>
                      <i className="bi bi-trash me-1"></i>
                      Confirmer
                    </button>
                  </div>
                )}

                {/* Modal: Ajouter un utilisateur */}
                {showModal.type === 'addUser' && (
                  <form onSubmit={handleAddUser}>
                    <div className="row g-1">
                      <div className="col-12">
                        <label className="form-label" style={{ fontSize: '0.7rem' }}>
                          <i className="bi bi-envelope me-1"></i>
                          Email <span className="text-danger">*</span>
                        </label>
                        <input type="email" className="form-control form-control-sm" value={formData.email || ''} onChange={e => setFormData({...formData, email: e.target.value})} required style={{ fontSize: '0.75rem', padding: '2px 4px' }} />
                      </div>
                      <div className="col-6">
                        <label className="form-label" style={{ fontSize: '0.7rem' }}>
                          <i className="bi bi-person me-1"></i>
                          Prénom <span className="text-danger">*</span>
                        </label>
                        <input type="text" className="form-control form-control-sm" value={formData.first_name || ''} onChange={e => setFormData({...formData, first_name: e.target.value})} required style={{ fontSize: '0.75rem', padding: '2px 4px' }} />
                      </div>
                      <div className="col-6">
                        <label className="form-label" style={{ fontSize: '0.7rem' }}>
                          <i className="bi bi-person-fill me-1"></i>
                          Nom <span className="text-danger">*</span>
                        </label>
                        <input type="text" className="form-control form-control-sm" value={formData.last_name || ''} onChange={e => setFormData({...formData, last_name: e.target.value})} required style={{ fontSize: '0.75rem', padding: '2px 4px' }} />
                      </div>
                      <div className="col-6">
                        <label className="form-label" style={{ fontSize: '0.7rem' }}>
                          <i className="bi bi-shield me-1"></i>
                          Rôle <span className="text-danger">*</span>
                        </label>
                        <select className="form-select form-select-sm" value={formData.role || 'EXPERT'} onChange={e => setFormData({...formData, role: e.target.value})} style={{ fontSize: '0.75rem', padding: '2px 4px' }}>
                          <option value="EXPERT">Expert</option>
                          <option value="BUREAU">Bureau</option>
                          <option value="ADMIN">Admin</option>
                        </select>
                      </div>
                      <div className="col-6">
                        <label className="form-label" style={{ fontSize: '0.7rem' }}>
                          <i className="bi bi-key me-1"></i>
                          Mot de passe <span className="text-danger">*</span>
                        </label>
                        <input type="password" className="form-control form-control-sm" value={formData.password || ''} onChange={e => setFormData({...formData, password: e.target.value})} required style={{ fontSize: '0.75rem', padding: '2px 4px' }} />
                      </div>
                    </div>
                    <div className="mt-2 text-muted small bg-light p-1 rounded">
                      <i className="bi bi-info-circle me-1"></i>
                      L'utilisateur sera créé avec un compte <span className="text-success fw-bold">ACTIF</span>
                    </div>
                    <div className="d-flex gap-2 mt-3">
                      <button type="submit" className="btn btn-primary btn-sm" style={{ fontSize: '0.7rem', padding: '4px 8px' }}>
                        <i className="bi bi-person-plus me-1"></i>
                        Créer l'utilisateur
                      </button>
                      <button type="button" className="btn btn-secondary btn-sm" onClick={closeModal} style={{ fontSize: '0.7rem', padding: '4px 8px' }}>
                        <i className="bi bi-x-circle me-1"></i>
                        Annuler
                      </button>
                    </div>
                  </form>
                )}

                {/* Modal: Envoyer une suggestion */}
                {showModal.type === 'sendSuggestion' && (
                  <form onSubmit={handleSendSuggestion}>
                    <div className="row g-3">
                      <div className="col-md-6">
                        <label className="form-label fw-semibold" style={{ fontSize: '0.8rem' }}>
                          <i className="bi bi-person-badge me-1 text-primary"></i>
                          Expert <span className="text-danger">*</span>
                        </label>
                        <select 
                          className="form-select" 
                          value={formData.expert || ''} 
                          onChange={e => setFormData({...formData, expert: e.target.value})} 
                          required 
                          style={{ fontSize: '0.85rem' }}
                        >
                          <option value="">-- Sélectionner un expert --</option>
                          {experts.map(exp => (
                            <option key={exp.id} value={exp.id}>
                              {exp.nom} ({exp.email})
                              {exp.disponible ? ' ✅' : ' ⏸️'}
                            </option>
                          ))}
                        </select>
                        {experts.length === 0 && (
                          <small className="text-muted d-block mt-1">
                            <i className="bi bi-info-circle me-1"></i>
                            Aucun expert disponible
                          </small>
                        )}
                      </div>
                      
                      <div className="col-md-6">
                        <label className="form-label fw-semibold" style={{ fontSize: '0.8rem' }}>
                          <i className="bi bi-file-earmark-text me-1 text-primary"></i>
                          Offre <span className="text-danger">*</span>
                        </label>
                        <select 
                          className="form-select" 
                          value={formData.offre || ''} 
                          onChange={e => setFormData({...formData, offre: e.target.value})} 
                          required 
                          style={{ fontSize: '0.85rem' }}
                        >
                          <option value="">-- Sélectionner une offre --</option>
                          {offres.map(off => (
                            <option key={off.id} value={off.id}>
                              {off.titre?.substring(0, 60)}...
                            </option>
                          ))}
                        </select>
                      </div>
                      
                      <div className="col-12">
                        <label className="form-label fw-semibold" style={{ fontSize: '0.8rem' }}>
                          <i className="bi bi-chat-left-text me-1 text-primary"></i>
                          Commentaire
                        </label>
                        <textarea 
                          className="form-control" 
                          rows="4" 
                          value={formData.commentaire_admin || ''} 
                          onChange={e => setFormData({...formData, commentaire_admin: e.target.value})} 
                          placeholder="Pourquoi suggérer cet expert pour cette offre ?"
                          style={{ fontSize: '0.85rem' }}
                        />
                      </div>
                    </div>
                    
                    <div className="d-flex gap-2 mt-3">
                      <button 
                        type="button" 
                        className="btn btn-secondary btn-sm"
                        onClick={closeModal}
                        style={{ fontSize: '0.8rem', padding: '6px 12px' }}
                      >
                        <i className="bi bi-x-circle me-1"></i>
                        Annuler
                      </button>
                      <button 
                        type="submit" 
                        className="btn btn-primary btn-sm flex-grow-1"
                        style={{ fontSize: '0.8rem', padding: '6px 12px' }}
                      >
                        <i className="bi bi-send me-1"></i>
                        Envoyer la suggestion
                      </button>
                    </div>
                  </form>
                )}

                {/* Modal: Effacer l'historique */}
                {showModal.type === 'clearHistory' && (
                  <div>
                    <p className="small text-danger mb-2">
                      <i className="bi bi-exclamation-triangle-fill me-1"></i>
                      Effacer TOUT l'historique ?<br/>
                      <span className="fw-bold">Irréversible.</span>
                    </p>
                    <div className="mb-2">
                      <label className="form-label" style={{ fontSize: '0.7rem' }}>
                        <i className="bi bi-keyboard me-1"></i>
                        Tapez "EFFACER TOUT" pour confirmer :
                      </label>
                      <input 
                        type="text" 
                        className="form-control form-control-sm" 
                        value={confirmText} 
                        onChange={e => setConfirmText(e.target.value)} 
                        placeholder="EFFACER TOUT" 
                        style={{ fontSize: '0.75rem', padding: '2px 4px' }} 
                      />
                      <small className="text-muted mt-1 d-block">
                        <i className="bi bi-info-circle me-1"></i>
                        Cette action supprimera toutes les entrées de l'historique.
                      </small>
                    </div>
                    <button 
                      className="btn btn-danger btn-sm w-100" 
                      onClick={handleClearHistory} 
                      disabled={confirmText !== 'EFFACER TOUT'} 
                      style={{ fontSize: '0.7rem', padding: '2px 4px' }}
                    >
                      <i className="bi bi-trash me-1"></i>
                      {confirmText === 'EFFACER TOUT' ? 'Confirmer l\'effacement' : 'Tapez "EFFACER TOUT" pour activer'}
                    </button>
                  </div>
                )}
              </div>
              
              <div className="modal-footer py-1 px-3">
                <button type="button" className="btn btn-secondary btn-sm" onClick={closeModal} style={{ fontSize: '0.7rem', padding: '1px 4px' }}>
                  <i className="bi bi-x-circle me-1"></i>
                  Fermer
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* =============================================================================
          MODAL : DÉTAILS UTILISATEUR
          ============================================================================= */}
      {showUserDetailsModal && (
        <div className="modal fade show d-block" tabIndex="-1" style={{ backgroundColor: 'rgba(0,0,0,0.5)' }}>
          <div className="modal-dialog modal-dialog-centered modal-lg modal-dialog-scrollable">
            <div className="modal-content">
              <div className="modal-header py-2 px-3 bg-primary text-white">
                <h6 className="modal-title" style={{ fontSize: '0.85rem' }}>
                  <i className="bi bi-person-lines-fill me-2"></i>
                  {userDetailsLoading ? 'Chargement...' : 'Détails utilisateur'}
                </h6>
                <button type="button" className="btn-close btn-close-white btn-close-sm" onClick={closeUserDetailsModal}></button>
              </div>
  
              <div className="modal-body py-2 px-3">
                {userDetailsLoading && (
                  <div className="text-center py-4">
                    <div className="spinner-border text-primary" role="status">
                      <span className="visually-hidden">Chargement...</span>
                    </div>
                    <p className="mt-2 small text-muted">Chargement des informations...</p>
                  </div>
                )}
    
                {userDetailsError && (
                  <div className="alert alert-danger py-2 small d-flex align-items-center">
                    <i className="bi bi-exclamation-triangle-fill me-2"></i>
                    {userDetailsError}
                  </div>
                )}
    
                {userDetails && !userDetailsLoading && (
                  <>
                    {/* Carte d'identité */}
                    <div className="card border-0 shadow-sm mb-3">
                      <div className="card-body py-2 px-3">
                        <div className="d-flex align-items-center gap-3">
                          <div 
                            className="d-flex align-items-center justify-content-center rounded-circle"
                            style={{ 
                              width: '60px', 
                              height: '60px',
                              background: userDetails.role === 'EXPERT' 
                                ? 'linear-gradient(135deg, #1E3A8A, #172554)' 
                                : userDetails.role === 'BUREAU' 
                                ? 'linear-gradient(135deg, #059669, #047857)'
                                : 'linear-gradient(135deg, #dc3545, #c82333)',
                              color: 'white',
                              fontSize: '1.5rem'
                            }}
                          >
                            {userDetails.role === 'EXPERT' ? 
                              <i className="bi bi-person-badge"></i> :
                            userDetails.role === 'BUREAU' ? 
                              <i className="bi bi-building"></i> :
                              <i className="bi bi-person-circle"></i>}
                          </div>
                          <div className="flex-grow-1">
                            <h5 className="mb-0 fw-bold" style={{ fontSize: '0.95rem' }}>
                              {userDetails.first_name} {userDetails.last_name}
                            </h5>
                            <p className="mb-1 small text-muted">
                              <i className="bi bi-envelope me-1"></i>
                              {userDetails.email}
                            </p>
                            <div className="d-flex gap-2 flex-wrap">
                              <span className={`badge ${
                                userDetails.role === 'EXPERT' ? 'bg-primary' : 
                                userDetails.role === 'BUREAU' ? 'bg-success' : 'bg-danger'
                              }`} style={{ fontSize: '0.65rem' }}>
                                {userDetails.role}
                              </span>
                              <span className={`badge ${userDetails.is_active ? 'bg-success' : 'bg-secondary'}`} style={{ fontSize: '0.65rem' }}>
                                {userDetails.is_active ? (
                                  <><i className="bi bi-check-circle-fill me-1"></i>Actif</>
                                ) : (
                                  <><i className="bi bi-x-circle-fill me-1"></i>Inactif</>
                                )}
                              </span>
                              {userDetails.est_certifie && (
                                <span className="badge bg-warning text-dark" style={{ fontSize: '0.65rem' }}>
                                  <i className="bi bi-shield-check me-1"></i>
                                  Certifié
                                </span>
                              )}
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
        
                    {/* Informations personnelles */}
                    <div className="card border-0 shadow-sm mb-3">
                      <div className="card-header bg-light py-2 px-3">
                        <h6 className="mb-0" style={{ fontSize: '0.8rem' }}>
                          <i className="bi bi-person-fill me-2"></i>
                          Informations personnelles
                        </h6>
                      </div>
                      <div className="card-body py-2 px-3">
                        <div className="row g-2">
                          <div className="col-6">
                            <small className="text-muted d-block" style={{ fontSize: '0.65rem' }}>
                              <i className="bi bi-telephone me-1"></i>Téléphone
                            </small>
                            <span style={{ fontSize: '0.75rem' }}>{userDetails.telephone || 'Non renseigné'}</span>
                          </div>
                          <div className="col-6">
                            <small className="text-muted d-block" style={{ fontSize: '0.65rem' }}>
                              <i className="bi bi-geo-alt me-1"></i>Pays
                            </small>
                            <span style={{ fontSize: '0.75rem' }}>{userDetails.pays || 'Non renseigné'}</span>
                          </div>
                          <div className="col-6">
                            <small className="text-muted d-block" style={{ fontSize: '0.65rem' }}>
                              <i className="bi bi-calendar me-1"></i>Date d'inscription
                            </small>
                            <span style={{ fontSize: '0.75rem' }}>
                              {userDetails.date_inscription ? new Date(userDetails.date_inscription).toLocaleDateString('fr-FR') : 'N/A'}
                            </span>
                          </div>
                          <div className="col-6">
                            <small className="text-muted d-block" style={{ fontSize: '0.65rem' }}>
                              <i className="bi bi-clock me-1"></i>Dernière connexion
                            </small>
                            <span style={{ fontSize: '0.75rem' }}>
                              {userDetails.derniere_connexion ? new Date(userDetails.derniere_connexion).toLocaleString('fr-FR') : 'Jamais connecté'}
                            </span>
                          </div>
                        </div>
                      </div>
                    </div>
        
                    {/* Profil EXPERT */}
                    {userDetails.role === 'EXPERT' && userDetails.profil && (
                      <div className="card border-0 shadow-sm mb-3">
                        <div className="card-header bg-light py-2 px-3">
                          <h6 className="mb-0" style={{ fontSize: '0.8rem' }}>
                            <i className="bi bi-briefcase-fill me-2 text-primary"></i>
                            Profil Expert
                          </h6>
                        </div>
                        <div className="card-body py-2 px-3">
                          <div className="row g-2">
                            <div className="col-12">
                              <small className="text-muted d-block" style={{ fontSize: '0.65rem' }}>
                                <i className="bi bi-lightbulb-fill me-1"></i>Domaines de compétence
                              </small>
                              <div className="d-flex flex-wrap gap-1 mt-1">
                                {userDetails.profil.domaines_competence && userDetails.profil.domaines_competence.length > 0 ? (
                                  userDetails.profil.domaines_competence.map((domaine, idx) => (
                                    <span 
                                      key={idx} 
                                      className="badge bg-primary bg-opacity-10 text-primary border border-primary"
                                      style={{ fontSize: '0.65rem' }}
                                    >
                                      {domaine}
                                    </span>
                                  ))
                                ) : (
                                  <span className="text-muted" style={{ fontSize: '0.75rem' }}>Aucun domaine sélectionné</span>
                                )}
                              </div>
                            </div>

                            {userDetails.profil.autres_competences && (
                              <div className="col-12">
                                <small className="text-muted d-block" style={{ fontSize: '0.65rem' }}>
                                  <i className="bi bi-stars me-1"></i>Autres compétences
                                </small>
                                <p className="mb-0 small" style={{ fontSize: '0.75rem' }}>
                                  {userDetails.profil.autres_competences}
                                </p>
                              </div>
                            )}

                            <div className="col-6">
                              <small className="text-muted d-block" style={{ fontSize: '0.65rem' }}>
                                <i className="bi bi-clock-fill me-1"></i>Disponibilité
                              </small>
                              <span 
                                className={`badge ${userDetails.profil.disponible ? 'bg-success' : 'bg-secondary'}`}
                                style={{ fontSize: '0.7rem' }}
                              >
                                {userDetails.profil.disponible ? '✅ Disponible pour mission' : '⏸️ Non disponible'}
                              </span>
                            </div>

                            <div className="col-6">
                              <small className="text-muted d-block" style={{ fontSize: '0.65rem' }}>
                                <i className="bi bi-check-circle-fill me-1"></i>Statut du profil
                              </small>
                              <span 
                                className={`badge ${userDetails.profil.profil_complet ? 'bg-success' : 'bg-warning text-dark'}`}
                                style={{ fontSize: '0.7rem' }}
                              >
                                {userDetails.profil.profil_complet ? '✅ Complet' : '⚠️ Incomplet'}
                              </span>
                            </div>

                            <div className="col-12 mt-2">
                              <small className="text-muted d-block" style={{ fontSize: '0.65rem' }}>
                                <i className="bi bi-file-earmark-pdf me-1"></i>CV (Curriculum Vitae)
                              </small>
                              {userDetails.profil.cv ? (
                                <div className="d-flex align-items-center gap-2 mt-1">
                                  <a 
                                    href={userDetails.profil.cv_url || userDetails.profil.cv} 
                                    target="_blank" 
                                    rel="noopener noreferrer"
                                    download
                                    onClick={(e) => e.stopPropagation()}
                                    className="btn btn-sm btn-outline-primary"
                                    style={{ fontSize: '0.7rem', padding: '4px 10px' }}
                                  >
                                    <i className="bi bi-download me-1"></i>
                                    Télécharger le CV
                                  </a>
                                  <a 
                                    href={userDetails.profil.cv_url || userDetails.profil.cv} 
                                    target="_blank" 
                                    rel="noopener noreferrer"
                                    className="btn btn-sm btn-outline-secondary"
                                    style={{ fontSize: '0.7rem', padding: '4px 10px' }}
                                    title="Voir le CV"
                                  >
                                    <i className="bi bi-eye me-1"></i>
                                    Voir
                                  </a>
                                </div>
                              ) : (
                                <span className="text-muted small">
                                  <i className="bi bi-exclamation-circle me-1"></i>
                                  Aucun CV uploadé
                                </span>
                              )}
                            </div>

                            {userDetails.profil.date_creation && (
                              <div className="col-12 mt-2">
                                <small className="text-muted d-block" style={{ fontSize: '0.6rem' }}>
                                  <i className="bi bi-calendar-event me-1"></i>
                                  Profil créé le {new Date(userDetails.profil.date_creation).toLocaleDateString('fr-FR')}
                                  {userDetails.profil.date_mise_a_jour && (
                                    <> • Mis à jour le {new Date(userDetails.profil.date_mise_a_jour).toLocaleDateString('fr-FR')}</>
                                  )}
                                </small>
                              </div>
                            )}
                          </div>
                        </div>
                      </div>
                    )}
        
                    {/* Profil BUREAU */}
                    {userDetails.role === 'BUREAU' && userDetails.profil && (
                      <div className="card border-0 shadow-sm mb-3">
                        <div className="card-header bg-light py-2 px-3">
                          <h6 className="mb-0" style={{ fontSize: '0.8rem' }}>
                            <i className="bi bi-building me-2 text-success"></i>
                            Profil Bureau d'Étude
                          </h6>
                        </div>
                        <div className="card-body py-2 px-3">
                          <div className="row g-2">
                            <div className="col-12">
                              <small className="text-muted d-block" style={{ fontSize: '0.65rem' }}>
                                <i className="bi bi-building-fill me-1"></i>Nom de la structure
                              </small>
                              <span className="fw-semibold" style={{ fontSize: '0.8rem' }}>
                                {userDetails.profil.nom_structure || 'Non renseigné'}
                              </span>
                            </div>

                            <div className="col-12">
                              <small className="text-muted d-block" style={{ fontSize: '0.65rem' }}>
                                <i className="bi bi-briefcase-fill me-1"></i>Domaine d'activité
                              </small>
                              <span style={{ fontSize: '0.75rem' }}>
                                {userDetails.profil.domaine_activite || 'Non renseigné'}
                              </span>
                            </div>

                            <div className="col-6">
                              <small className="text-muted d-block" style={{ fontSize: '0.65rem' }}>
                                <i className="bi bi-geo-alt me-1"></i>Pays
                              </small>
                              <span style={{ fontSize: '0.75rem' }}>
                                {userDetails.profil.pays || 'Non renseigné'}
                              </span>
                            </div>
                            <div className="col-6">
                              <small className="text-muted d-block" style={{ fontSize: '0.65rem' }}>
                                <i className="bi bi-telephone me-1"></i>Téléphone
                              </small>
                              <span style={{ fontSize: '0.75rem' }}>
                                {userDetails.profil.telephone || 'Non renseigné'}
                              </span>
                            </div>

                            <div className="col-12">
                              <small className="text-muted d-block" style={{ fontSize: '0.65rem' }}>
                                <i className="bi bi-envelope me-1"></i>Email de contact
                              </small>
                              <span style={{ fontSize: '0.75rem' }}>
                                {userDetails.profil.email_contact ? (
                                  <a href={`mailto:${userDetails.profil.email_contact}`} style={{ color: '#1E3A8A' }}>
                                    {userDetails.profil.email_contact}
                                  </a>
                                ) : 'Non renseigné'}
                              </span>
                            </div>

                            <div className="col-12">
                              <small className="text-muted d-block" style={{ fontSize: '0.65rem' }}>
                                <i className="bi bi-map me-1"></i>Adresse
                              </small>
                              <p className="mb-0 small" style={{ fontSize: '0.75rem' }}>
                                {userDetails.profil.adresse || 'Non renseignée'}
                              </p>
                            </div>

                            <div className="col-12">
                              <small className="text-muted d-block" style={{ fontSize: '0.65rem' }}>
                                <i className="bi bi-link-45deg me-1"></i>Site web
                              </small>
                              {userDetails.profil.site_web ? (
                                <a 
                                  href={userDetails.profil.site_web} 
                                  target="_blank" 
                                  rel="noopener noreferrer"
                                  style={{ fontSize: '0.75rem' }}
                                >
                                  <i className="bi bi-box-arrow-up-right me-1"></i>
                                  {userDetails.profil.site_web}
                                </a>
                              ) : (
                                <span className="text-muted" style={{ fontSize: '0.75rem' }}>Non renseigné</span>
                              )}
                            </div>

                            <div className="col-12 mt-2">
                              <small className="text-muted d-block" style={{ fontSize: '0.65rem' }}>
                                <i className="bi bi-check-circle-fill me-1"></i>Statut du profil
                              </small>
                              <span 
                                className={`badge ${userDetails.profil.profil_complet ? 'bg-success' : 'bg-warning text-dark'}`}
                                style={{ fontSize: '0.7rem' }}
                              >
                                {userDetails.profil.profil_complet ? '✅ Complet' : '⚠️ Incomplet'}
                              </span>
                            </div>

                            {userDetails.profil.date_creation && (
                              <div className="col-12 mt-2">
                                <small className="text-muted d-block" style={{ fontSize: '0.6rem' }}>
                                  <i className="bi bi-calendar-event me-1"></i>
                                  Profil créé le {new Date(userDetails.profil.date_creation).toLocaleDateString('fr-FR')}
                                  {userDetails.profil.date_mise_a_jour && (
                                    <> • Mis à jour le {new Date(userDetails.profil.date_mise_a_jour).toLocaleDateString('fr-FR')}</>
                                  )}
                                </small>
                              </div>
                            )}
                          </div>
                        </div>
                      </div>
                    )}
        
                    {userDetails.profil_message && (
                      <div className="alert alert-warning py-2 small d-flex align-items-center">
                        <i className="bi bi-exclamation-triangle-fill me-2"></i>
                        {userDetails.profil_message}
                      </div>
                    )}
        
                    {userDetails.activites && (
                      <div className="card border-0 shadow-sm mb-3">
                        <div className="card-header bg-light py-2 px-3">
                          <h6 className="mb-0" style={{ fontSize: '0.8rem' }}>
                            <i className="bi bi-graph-up me-2"></i>
                            Activités
                          </h6>
                        </div>
                        <div className="card-body py-2 px-3">
                          <div className="row g-2">
                            <div className="col-6">
                              <div className="text-center p-2 bg-primary bg-opacity-10 rounded">
                                <h4 className="mb-0 fw-bold text-primary" style={{ fontSize: '1rem' }}>
                                  {userDetails.activites.suggestions_recues || 0}
                                </h4>
                                <small className="text-muted" style={{ fontSize: '0.65rem' }}>Suggestions reçues</small>
                              </div>
                            </div>
                            <div className="col-6">
                              <div className="text-center p-2 bg-success bg-opacity-10 rounded">
                                <h4 className="mb-0 fw-bold text-success" style={{ fontSize: '1rem' }}>
                                  {userDetails.activites.suggestions_consultees || 0}
                                </h4>
                                <small className="text-muted" style={{ fontSize: '0.65rem' }}>Suggestions consultées</small>
                              </div>
                            </div>
                          </div>
                        </div>
                      </div>
                    )}
                  </>
                )}
              </div>
  
              <div className="modal-footer py-1 px-3">
                <button type="button" className="btn btn-secondary btn-sm" onClick={closeUserDetailsModal} style={{ fontSize: '0.7rem', padding: '2px 6px' }}>
                  <i className="bi bi-x-circle me-1"></i>
                  Fermer
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default AdminDashboard;