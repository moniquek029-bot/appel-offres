// src/components/ErrorBoundary.jsx
import React from 'react';

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { 
      hasError: false, 
      error: null, 
      errorInfo: null,
      retryKey: 0 
    };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    console.error('🚨 ErrorBoundary:', error, errorInfo);
    this.setState({ errorInfo });
  }

  handleRetry = () => {
    this.setState(prev => ({ 
      hasError: false, 
      error: null, 
      errorInfo: null,
      retryKey: prev.retryKey + 1 
    }));
  };

  render() {
    if (this.state.hasError) {
      return (
        <div className="container py-5">
          <div className="alert alert-danger shadow-sm">
            <h5 className="alert-heading">⚠️ Une erreur est survenue</h5>
            <p className="mb-2">{this.state.error?.message || 'Erreur inattendue'}</p>
            
            {process.env.NODE_ENV === 'development' && this.state.errorInfo && (
              <details className="mb-3">
                <summary className="small text-muted">🔧 Détails techniques</summary>
                <pre className="mt-2 p-2 bg-light rounded small" style={{ maxHeight: '200px', overflow: 'auto' }}>
                  {this.state.error?.toString()}
                  {'\n\n'}
                  {this.state.errorInfo?.componentStack}
                </pre>
              </details>
            )}
            
            <div className="d-flex gap-2">
              <button className="btn btn-outline-primary btn-sm" onClick={this.handleRetry}>🔄 Réessayer</button>
              <button className="btn btn-primary btn-sm" onClick={() => window.location.reload()}>🔄 Recharger</button>
            </div>
          </div>
        </div>
      );
    }

    // La clé `retryKey` force React à re-monter les enfants après un retry
    return React.Children.map(this.props.children, child => 
      React.cloneElement(child, { key: this.state.retryKey })
    );
  }
}

export default ErrorBoundary;