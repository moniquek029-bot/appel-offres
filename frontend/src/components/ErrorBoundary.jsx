// src/components/ErrorBoundary.jsx - VERSION CORRIGÉE
import React from 'react';

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { 
      hasError: false, 
      error: null,
      errorCount: 0
    };
    this.recoveryTimeout = null;
  }

  static getDerivedStateFromError(error) {
    // Ne pas capturer les erreurs DOM insertBefore/appendChild (non-critiques)
    if (error?.message?.includes('insertBefore') || error?.message?.includes('appendChild') || error?.message?.includes('is not a child')) {
      return { hasError: false, error: null };
    }
    
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    // Ignorer les erreurs non-critiques de DOM manipulation
    if (error?.message?.includes('insertBefore') || error?.message?.includes('appendChild') || error?.message?.includes('is not a child')) {
      console.warn('⚠️ Non-critical DOM error caught (insertBefore), ignoring...');
      return;
    }
    
    // Log l'erreur pour le débogage
    console.error(' ErrorBoundary caught an error:', error);
    console.error('Component stack:', errorInfo?.componentStack);
    
    this.setState(prev => ({
      errorCount: prev.errorCount + 1
    }));
  }

  handleReload = () => {
    // Recharge simplement la page pour réinitialiser l'état React/DOM
    window.location.reload();
  };

  render() {
    if (this.state.hasError) {
      return (
        <div className="container py-5 d-flex justify-content-center align-items-center" 
             style={{ minHeight: '80vh' }}>
          <div className="card border-0 shadow-lg" style={{ maxWidth: '500px', width: '100%' }}>
            <div className="card-body text-center p-4">
              <div className="mb-3" style={{ fontSize: '3rem' }}>⚠️</div>
              <h4 className="mb-3">Une erreur est survenue</h4>
              <p className="text-muted mb-4">
                {this.state.error?.message || 'Erreur inattendue lors du chargement.'}
              </p>
              
              {/* Affiche les détails uniquement en développement */}
              {process.env.NODE_ENV === 'development' && this.state.error && (
                <details className="mb-3 text-start">
                  <summary className="small text-muted cursor-pointer">
                    🔧 Détails techniques (développement)
                  </summary>
                  <pre className="mt-2 p-2 bg-light rounded small" 
                       style={{ 
                         maxHeight: '150px', 
                         overflow: 'auto',
                         fontSize: '0.7rem'
                       }}>
                    {this.state.error.toString()}
                  </pre>
                </details>
              )}
              
              <div className="d-flex gap-2 justify-content-center">
                <button 
                  className="btn btn-outline-secondary btn-sm" 
                  onClick={() => window.history.back()}
                >
                  ← Retour
                </button>
                <button 
                  className="btn btn-primary btn-sm" 
                  onClick={this.handleReload}
                >
                  🔄 Recharger la page
                </button>
              </div>
            </div>
          </div>
        </div>
      );
    }

    // ✅ CORRECTION CRITIQUE: Rend les enfants SANS cloneElement ni key dynamique
    // Cela évite de forcer un re-mount qui pourrait désynchroniser le DOM
    return this.props.children;
  }
}

export default ErrorBoundary;