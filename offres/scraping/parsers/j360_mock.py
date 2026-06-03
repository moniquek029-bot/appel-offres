"""
Parser Mock enrichi pour j360.info
"""

import logging
from datetime import date, timedelta
from ..base import BaseScraper
from ..utils import clean_text

logger = logging.getLogger(__name__)


class J360MockParser(BaseScraper):
    
    def __init__(self, source_url: str, base_url: str = "https://app.j360.info", pays_defaut: str = 'BF', **kwargs):
        super().__init__(source_url, delay_seconds=0, base_url=base_url, pays_defaut=pays_defaut, **kwargs)
    
    def parse(self, soup=None):
        mock_offers = [
            {
                "titre": "Recrutement de Consultant pour étude hydraulique",
                "organisme": "Ministère de l'Agriculture",
                "description": "Le Ministère lance un appel d'offres pour le recrutement d'un cabinet spécialisé...",
                "date_publication": date.today() - timedelta(days=3),
                "date_cloture": date.today() + timedelta(days=20),
                "url_source": "https://app.j360.info/#/tender/demo-hydraulique",
                "url_tdr": "https://app.j360.info/docs/hydraulique.pdf",
                "pays": "BF",
                "statut": "Ouvert",
                "mode_acquisition": "AUTO",
            },
            {
                "titre": "Acquisition de Support technique des produits ORACLE",
                "organisme": "Caisse Nationale de Sécurité Sociale (CNSS)",
                "description": "La CNSS sollicite des offres pour la fourniture de services de support technique...",
                "date_publication": date.today() - timedelta(days=2),
                "date_cloture": date.today() + timedelta(days=25),
                "url_source": "https://app.j360.info/#/tender/demo-oracle-cnss",
                "url_tdr": "https://app.j360.info/docs/oracle-support.pdf",
                "pays": "BF",
                "statut": "Ouvert",
                "mode_acquisition": "AUTO",
            },
        ]
        
        logger.info(f"✅ {len(mock_offers)} offre(s) générées")
        return mock_offers
    
    def parse_detail_page(self, soup, base_url):
        return {'url_tdr': "https://app.j360.info/docs/example.pdf"}
    
    def run(self):
        logger.info(f"🕷️ Lancement du parser mock pour {self.source_url}")
        return self.parse()