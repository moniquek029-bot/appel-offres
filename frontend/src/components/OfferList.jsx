import React, { useState, useEffect } from 'react';
import OfferCard from './OfferCard';
import { getOffers } from '../services/api';

const OfferList = () => {
  const [offers, setOffers] = useState([]);
  const [currentPage, setCurrentPage] = useState(1);
  const [loading, setLoading] = useState(true);
  
  const ITEMS_PER_PAGE = 6;

  useEffect(() => {
    getOffers().then(data => {
      setOffers(data);
      setLoading(false);
    });
  }, []);

  // Logique de pagination
  const totalPages = Math.ceil(offers.length / ITEMS_PER_PAGE);
  const indexOfLast = currentPage * ITEMS_PER_PAGE;
  const indexOfFirst = indexOfLast - ITEMS_PER_PAGE;
  const currentOffers = offers.slice(indexOfFirst, indexOfLast);

  const handlePageChange = (page) => {
    if (page >= 1 && page <= totalPages) setCurrentPage(page);
  };

  if (loading) return <div className="text-center py-5"><div className="spinner-border text-primary" /></div>;

  return (
    <div className="container py-4">
      <h2 className="mb-4">Appels d'offres disponibles</h2>
      
      <div className="row g-3">
        {currentOffers.map(offer => (
          <div className="col-md-6 col-lg-4" key={offer.id}>
            <OfferCard offer={offer} />
          </div>
        ))}
      </div>

      {totalPages > 1 && (
        <nav className="mt-4">
          <ul className="pagination justify-content-center">
            <li className={`page-item ${currentPage === 1 ? 'disabled' : ''}`}>
              <button className="page-link" onClick={() => handlePageChange(currentPage - 1)}>Précédent</button>
            </li>
            {[...Array(totalPages)].map((_, i) => (
              <li key={i} className={`page-item ${currentPage === i + 1 ? 'active' : ''}`}>
                <button className="page-link" onClick={() => handlePageChange(i + 1)}>{i + 1}</button>
              </li>
            ))}
            <li className={`page-item ${currentPage === totalPages ? 'disabled' : ''}`}>
              <button className="page-link" onClick={() => handlePageChange(currentPage + 1)}>Suivant</button>
            </li>
          </ul>
        </nav>
      )}
    </div>
  );
};

export default OfferList;