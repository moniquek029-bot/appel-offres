// src/components/Messagerie.jsx
import React, { useState, useEffect } from 'react';
import api from '../services/api';
import { useAuth } from '../context/AuthContext';

const Messagerie = () => {
  const { user } = useAuth();
  const [messages, setMessages] = useState([]);
  const [newMessage, setNewMessage] = useState({ sujet: '', contenu: '' });
  const [reponseMessage, setReponseMessage] = useState(null);
  const [reponseContenu, setReponseContenu] = useState('');
  const [loading, setLoading] = useState(true);
  const [sending, setSending] = useState(false);
  const [success, setSuccess] = useState('');
  const [error, setError] = useState('');
  const [messageFilter, setMessageFilter] = useState('all');

  useEffect(() => {
    fetchMessages();
  }, []);

  const fetchMessages = async () => {
    try {
      const res = await api.get('/messages/');
      let messagesData = res.data.results || res.data;
      
      // Debug détaillé
      if (messagesData && messagesData.length > 0) {
        console.log('=== STRUCTURE DU MESSAGE ===');
        console.log('Premier message:', messagesData[0]);
        console.log('Toutes les clés:', Object.keys(messagesData[0]));
      }
      
      setMessages(messagesData);
    } catch (err) {
      console.error('Erreur chargement messages:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleSend = async (e) => {
    e.preventDefault();
    if (!newMessage.sujet || !newMessage.contenu) return;
    
    setSending(true);
    setError('');
    setSuccess('');
    
    try {
      await api.post('/messages/envoyer-admin/', newMessage);
      setSuccess('✅ Message envoyé avec succès');
      setNewMessage({ sujet: '', contenu: '' });
      await fetchMessages();
      setTimeout(() => setSuccess(''), 3000);
    } catch (err) {
      console.error(err);
      setError('❌ Erreur lors de l\'envoi du message');
    } finally {
      setSending(false);
    }
  };

  const marquerLu = async (id) => {
    try {
      await api.post(`/messages/${id}/marquer-lu/`);
      fetchMessages();
    } catch (err) {
      console.error(err);
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm('Supprimer ce message ?')) return;
    try {
      await api.delete(`/messages/${id}/`);
      fetchMessages();
    } catch (err) {
      console.error(err);
    }
  };

  // FONCTION CORRIGÉE - Extrait l'ID de l'expéditeur quel que soit le format
  const getExpediteurId = (message) => {
    // Cas 1: expediteur est un objet avec id
    if (message.expediteur && typeof message.expediteur === 'object' && message.expediteur.id) {
      return message.expediteur.id;
    }
    // Cas 2: expediteur_id existe directement
    if (message.expediteur_id !== undefined) {
      return message.expediteur_id;
    }
    // Cas 3: expediteur est directement l'ID (nombre)
    if (typeof message.expediteur === 'number') {
      return message.expediteur;
    }
    return null;
  };

  // FONCTION CORRIGÉE - Extrait l'ID du destinataire quel que soit le format
  const getDestinataireId = (message) => {
    // Cas 1: destinataire est un objet avec id
    if (message.destinataire && typeof message.destinataire === 'object' && message.destinataire.id) {
      return message.destinataire.id;
    }
    // Cas 2: destinataire_id existe directement
    if (message.destinataire_id !== undefined) {
      return message.destinataire_id;
    }
    // Cas 3: destinataire est directement l'ID (nombre)
    if (typeof message.destinataire === 'number') {
      return message.destinataire;
    }
    return null;
  };

  // Vérifie si l'utilisateur est l'expéditeur
  const isUserExpediteur = (message) => {
    const expediteurId = getExpediteurId(message);
    return expediteurId === user?.id;
  };

  // Vérifie si l'utilisateur est le destinataire
  const isUserDestinataire = (message) => {
    const destinataireId = getDestinataireId(message);
    return destinataireId === user?.id;
  };

  // Obtient l'email de l'expéditeur
  const getExpediteurEmail = (message) => {
    if (message.expediteur_email) return message.expediteur_email;
    if (message.expediteur?.email) return message.expediteur.email;
    return null;
  };

  // Obtient le nom de l'expéditeur
  const getExpediteurNom = (message) => {
    if (message.expediteur_nom) return message.expediteur_nom;
    if (message.expediteur?.first_name) {
      return `${message.expediteur.first_name} ${message.expediteur.last_name || ''}`.trim();
    }
    return getExpediteurEmail(message) || 'Inconnu';
  };

  if (loading) return <div className="text-center py-4">Chargement des messages...</div>;

  // Filtrage CORRIGÉ
  const filteredMessages = messages.filter(msg => {
    if (messageFilter === 'sent') {
      return isUserExpediteur(msg);
    }
    if (messageFilter === 'received') {
      return isUserDestinataire(msg) && !msg.est_reponse;
    }
    if (messageFilter === 'unread') {
      return isUserDestinataire(msg) && !msg.est_lu;
    }
    return true;
  });

  const sentCount = messages.filter(msg => isUserExpediteur(msg)).length;
  const receivedCount = messages.filter(msg => isUserDestinataire(msg) && !msg.est_reponse).length;
  const nonLusCount = messages.filter(msg => isUserDestinataire(msg) && !msg.est_lu).length;

  // Debug
  console.log('=== DEBUG FINAL ===');
  console.log('User ID:', user?.id);
  console.log('Messages analysés:', messages.map(m => ({
    id: m.id,
    sujet: m.sujet,
    expediteurId: getExpediteurId(m),
    destinataireId: getDestinataireId(m),
    isExpediteur: isUserExpediteur(m),
    isDestinataire: isUserDestinataire(m),
    expediteur_nom: getExpediteurNom(m)
  })));
  console.log('Sent count:', sentCount);
  console.log('Received count:', receivedCount);
  console.log('Non lus count:', nonLusCount);

  return (
    <div className="card border-0 shadow-sm">
      <div className="card-header bg-white border-0 py-3">
        <div className="d-flex justify-content-between align-items-center flex-wrap gap-2">
          <h5 className="mb-0"> Messagerie</h5>
          {nonLusCount > 0 && (
            <span className="badge bg-danger rounded-pill">{nonLusCount} non lu(s)</span>
          )}
        </div>
        
        <div className="btn-group btn-group-sm mt-3 w-100">
          <button 
            className={`btn ${messageFilter === 'all' ? 'btn-primary' : 'btn-outline-secondary'}`}
            onClick={() => setMessageFilter('all')}
            style={{ fontSize: '0.75rem' }}
          >
            <i className="bi bi-chat-dots-fill me-1"></i>
            Tous ({messages.length})
          </button>
          <button 
            className={`btn ${messageFilter === 'received' ? 'btn-primary' : 'btn-outline-secondary'}`}
            onClick={() => setMessageFilter('received')}
            style={{ fontSize: '0.75rem' }}
          >
            <i className="bi bi-inbox-fill me-1"></i>
             Reçus ({receivedCount})
          </button>
          <button 
            className={`btn ${messageFilter === 'sent' ? 'btn-primary' : 'btn-outline-secondary'}`}
            onClick={() => setMessageFilter('sent')}
            style={{ fontSize: '0.75rem' }}
          >
            <i className="bi bi-send-fill me-1"></i>
             Envoyés ({sentCount})
          </button>
          <button 
            className={`btn ${messageFilter === 'unread' ? 'btn-primary' : 'btn-outline-secondary'}`}
            onClick={() => setMessageFilter('unread')}
            style={{ fontSize: '0.75rem' }}
          >
            <i className="bi bi-envelope-fill ms-1"></i>
             Non lus ({nonLusCount})
             
          </button>
        </div>
      </div>
      
      <div className="card-body">
        
        {/* Formulaire d'envoi */}
        <div className="mb-4 p-3 bg-light rounded">
          <h6 className="mb-3"> Nouveau message à l'administrateur</h6>
          <form onSubmit={handleSend}>
            {error && <div className="alert alert-danger small py-1">{error}</div>}
            {success && <div className="alert alert-success small py-1">{success}</div>}
            <div className="mb-2">
              <input
                type="text"
                className="form-control"
                placeholder="Sujet"
                value={newMessage.sujet}
                onChange={(e) => setNewMessage({...newMessage, sujet: e.target.value})}
                required
              />
            </div>
            <div className="mb-2">
              <textarea
                className="form-control"
                rows="3"
                placeholder="Votre message..."
                value={newMessage.contenu}
                onChange={(e) => setNewMessage({...newMessage, contenu: e.target.value})}
                required
              />
            </div>
            <button type="submit" className="btn btn-primary btn-sm" disabled={sending}>
              {sending ? 'Envoi...' : ' Envoyer'}
              <i className="bi bi-send ms-1"></i>
            </button>
          </form>
        </div>

        <h6 className="mb-3"> Historique des messages</h6>
        {filteredMessages.length === 0 ? (
          <div className="text-center py-4">
            <p className="text-muted mb-0 small">
              {messageFilter === 'sent' ? ' Aucun message envoyé' : 
               messageFilter === 'received' ? ' Aucun message reçu' :
               messageFilter === 'unread' ? ' Aucun message non lu' :
               ' Aucun message'}
            </p>
          </div>
        ) : (
          <div className="list-group">
            {filteredMessages.map(msg => {
              const isSentByMe = isUserExpediteur(msg);
              const isUnread = !msg.est_lu && !isSentByMe;
              const isReply = msg.est_reponse;
              
              return (
                <div 
                  key={msg.id} 
                  className={`list-group-item list-group-item-action mb-2 rounded-3 ${isUnread ? 'bg-light border-primary' : ''}`}
                  onClick={() => isUnread && marquerLu(msg.id)}
                  style={{ cursor: 'pointer' }}
                >
                  <div className="d-flex justify-content-between align-items-start">
                    <div className="flex-grow-1">
                      <div className="d-flex align-items-center gap-2 mb-1 flex-wrap">
                        <strong className="small">
                          {isSentByMe ? (
                            <> <span className="text-success">Vous (message envoyé)</span></>
                          ) : (
                            <> {getExpediteurNom(msg) || 'Admin'}</>
                          )}
                        </strong>
                        {!isSentByMe && isUserDestinataire(msg) && (
                          <span className="badge bg-secondary">Reçu</span>
                        )}
                        {isReply && <span className="badge bg-success"> Réponse</span>}
                        {isUnread && <span className="badge bg-primary"> Nouveau</span>}
                        <small className="text-muted">
                          {new Date(msg.date_envoi).toLocaleString('fr-FR')}
                        </small>
                      </div>
                      <h6 className="mb-1 small fw-bold">{msg.sujet}</h6>
                      <p className="mb-2 small text-secondary">{msg.contenu}</p>
                      
                      {msg.reponse_contenu && (
                        <div className="mt-2 p-2 bg-light rounded" style={{ borderLeft: '3px solid #198754' }}>
                          <small className="text-success fw-semibold"> Réponse :</small>
                          <p className="mb-0 small mt-1">{msg.reponse_contenu}</p>
                        </div>
                      )}
                    </div>
                    {!isSentByMe && (
                      <button 
                        className="btn btn-sm btn-outline-danger ms-2"
                        onClick={(e) => {
                          e.stopPropagation();
                          handleDelete(msg.id);
                        }}
                        title="Supprimer"
                      >
                        <i className="bi bi-trash"></i>
                      </button>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
};

export default Messagerie;