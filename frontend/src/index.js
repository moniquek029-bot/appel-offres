// src/index.js
import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
// ✅ IMPORT CORRECT : seulement le CSS de Bootstrap
import 'bootstrap/dist/css/bootstrap.min.css';
import './index.css';
import 'bootstrap-icons/font/bootstrap-icons.css';

// ⚠️ NE PAS importer bootstrap.bundle.min.js ou tout autre JS Bootstrap

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  //<React.StrictMode>
    <App />
  //</React.StrictMode>
);