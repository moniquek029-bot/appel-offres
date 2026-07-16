// src/components/SearchBar.jsx
import React, { useState } from 'react';

const SearchBar = ({ onSearch }) => {
  const [keyword, setKeyword] = useState('');
  const [isFocused, setIsFocused] = useState(false);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (typeof onSearch === 'function') {
      onSearch(keyword);
    }
  };

  const handleClear = () => {
    setKeyword('');
    if (typeof onSearch === 'function') {
      onSearch('');
    }
  };

  return (
    <div 
      className="py-4 shadow-sm"
      style={{
        background: 'linear-gradient(135deg, #F9FAFB 0%, #E5E7EB 100%)',
        borderBottom: '3px solid #F59E0B'  // ✅ Bordure or comme accent
      }}
    >
      <div className="container">
        {/* Titre optionnel */}
        <div className="text-center mb-3">
          <h2 
            style={{
              color: '#002147',  // ✅ Bleu marine
              fontWeight: '700',
              fontSize: '1.5rem',
              marginBottom: '0.25rem'
            }}
          >
            <i className="bi bi-briefcase-fill me-2" style={{ color: '#F59E0B' }}></i>
            Trouvez votre prochain appel d'offres
          </h2>
          <p style={{ color: '#6B7280', fontSize: '0.9rem', margin: 0 }}>
            Recherchez parmi des milliers d'opportunités
          </p>
        </div>

        <form onSubmit={handleSubmit} className="row g-2 align-items-center">
          <div className="col-md-10">
            <div 
              className="input-group shadow-sm"
              style={{
                borderRadius: '12px',
                overflow: 'hidden',
                border: isFocused ? '2px solid #F59E0B' : '2px solid #E5E7EB',
                transition: 'all 0.3s ease',
                background: 'white'
              }}
            >
              {/* Icône de recherche */}
              <span 
                className="input-group-text border-0"
                style={{
                  background: 'white',
                  color: isFocused ? '#F59E0B' : '#6B7280',
                  transition: 'color 0.3s ease',
                  paddingLeft: '16px'
                }}
              >
                <i className="bi bi-search" style={{ fontSize: '1.1rem' }}></i>
              </span>
              
              {/* Champ de recherche */}
              <input
                type="text"
                className="form-control border-0"
                placeholder="Rechercher un appel d'offres (titre, organisme, mots-clés)..."
                value={keyword}
                onChange={(e) => setKeyword(e.target.value)}
                onFocus={() => setIsFocused(true)}
                onBlur={() => setIsFocused(false)}
                style={{
                  padding: '12px 40px 12px 8px',
                  fontSize: '0.95rem',
                  position: 'relative',
                  boxShadow: 'none',
                  outline: 'none'
                }}
              />
              
              {/* Bouton X pour effacer */}
              {keyword && (
                <button
                  type="button"
                  className="btn position-absolute d-flex align-items-center justify-content-center"
                  onClick={handleClear}
                  title="Effacer la recherche"
                  style={{
                    right: '8px',
                    top: '50%',
                    transform: 'translateY(-50%)',
                    zIndex: 10,
                    width: '32px',
                    height: '32px',
                    padding: 0,
                    background: '#F3F4F6',
                    border: 'none',
                    borderRadius: '50%',
                    color: '#6B7280',
                    transition: 'all 0.2s ease'
                  }}
                  onMouseEnter={(e) => {
                    e.currentTarget.style.background = '#EF4444';
                    e.currentTarget.style.color = 'white';
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.background = '#F3F4F6';
                    e.currentTarget.style.color = '#6B7280';
                  }}
                >
                  <i className="bi bi-x-lg" style={{ fontSize: '0.85rem' }}></i>
                </button>
              )}
            </div>
          </div>
          
          {/* Bouton Rechercher - Dégradé Or */}
          <div className="col-md-2">
            <button 
              type="submit" 
              className="btn w-100 d-flex align-items-center justify-content-center gap-2"
              style={{
                background: 'linear-gradient(135deg, #0839c0 0%, #f5690b 100%)',
                color: 'white',
                border: 'none',
                padding: '12px 24px',
                borderRadius: '12px',
                fontWeight: '600',
                fontSize: '0.95rem',
                transition: 'all 0.3s ease',
                boxShadow: '0 4px 12px rgba(30, 58, 138, 0.3)',
                height: '48px'
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.background = 'linear-gradient(135deg, #172554 0%, #D97706 100%)';
                e.currentTarget.style.transform = 'translateY(-2px)';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.background = 'linear-gradient(135deg, #1E3A8A 0%, #F59E0B 100%)';
                e.currentTarget.style.transform = 'translateY(0)';
S              }}
            >
              <i className="bi bi-search" style={{ fontSize: '1rem' }}></i>
              <span>Rechercher</span>
            </button>
          </div>
        </form>

        {/* Suggestions rapides (optionnel) */}
        <div className="mt-3 text-center">
          <small style={{ color: '#6B7280', fontSize: '0.85rem' }}>
            <strong>Populaires :</strong>{' '}
            {[
              'Travaux', 
              'Informatique', 
              'Consultant', 
              'Construction',
              'Santé'
            ].map((tag, idx) => (
              <span 
                key={idx}
                onClick={() => {
                  setKeyword(tag);
                  if (typeof onSearch === 'function') onSearch(tag);
                }}
                style={{
                  display: 'inline-block',
                  padding: '4px 12px',
                  margin: '2px 4px',
                  background: '#F3F4F6',
                  color: '#002147',
                  borderRadius: '20px',
                  fontSize: '0.8rem',
                  cursor: 'pointer',
                  transition: 'all 0.2s ease',
                  border: '1px solid #E5E7EB'
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.background = '#002147';
                  e.currentTarget.style.color = 'white';
                  e.currentTarget.style.borderColor = '#002147';
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.background = '#F3F4F6';
                  e.currentTarget.style.color = '#002147';
                  e.currentTarget.style.borderColor = '#E5E7EB';
                }}
              >
                {tag}
              </span>
            ))}
          </small>
        </div>
      </div>
    </div>
  );
};

export default SearchBar;