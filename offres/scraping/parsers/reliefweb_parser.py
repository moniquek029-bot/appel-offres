# offres/scraping/parsers/reliefweb_parser.py
import logging
import requests
from datetime import date, timedelta

from offres.scraping.base import BaseScraper
from offres.scraping.utils import clean_text, detecter_pays

logger = logging.getLogger(__name__)


class ReliefWebParser(BaseScraper):
    """Parser pour ReliefWeb (humanitaire) - API publique fiable"""
    
    API_URL = "https://api.reliefweb.int/v1/reports"
    
    def __init__(self, source_url: str = "https://reliefweb.int", **kwargs):
        super().__init__(source_url, **kwargs)
        self.pays_defaut = 'GL'
    
    def run(self) -> list[dict]:
        """Récupère les dernières offres via l'API ReliefWeb"""
        logger.info(f"🌍 ReliefWeb API: Récupération des offres...")
        
        try:
            # Paramètres de l'API
            params = {
                'appname': 'votre-app-name',  # Peut être n'importe quoi
                'filter[field]': 'title,body,format,country,date',
                'filter[value]': 'job OR training OR "call for proposals"',
                'sort[date]': 'desc',
                'limit': 50,
            }
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'application/json'
            }
            
            response = requests.get(self.API_URL, params=params, headers=headers, timeout=30)
            
            if response.status_code != 200:
                logger.error(f"❌ API error: {response.status_code}")
                return []
            
            data = response.json()
            reports = data.get('data', [])
            
            offres = []
            for report in reports:
                try:
                    offre = self._parse_report(report)
                    if offre:
                        offres.append(offre)
                except Exception as e:
                    logger.debug(f"⚠️ Erreur parsing report: {e}")
                    continue
            
            logger.info(f"✅ ReliefWeb API: {len(offres)} offre(s) extraite(s)")
            return offres
            
        except Exception as e:
            logger.error(f"❌ Erreur ReliefWeb API: {e}")
            return []
    
    def _parse_report(self, report: dict) -> dict | None:
        """Parse un rapport de l'API"""
        fields = report.get('fields', {})
        
        titre = fields.get('title', '')
        if not titre or len(titre) < 10:
            return None
        
        # URL
        url_source = report.get('href', '')
        if not url_source:
            return None
        
        # Dates
        date_pub_str = fields.get('date', {}).get('created', '')
        try:
            if date_pub_str:
                date_pub = date.fromisoformat(date_pub_str.split('T')[0])
            else:
                date_pub = date.today()
        except:
            date_pub = date.today()
        
        date_cloture = date_pub + timedelta(days=60)
        
        # Pays
        countries = fields.get('country', [])
        if countries:
            country_name = countries[0].get('name', '')
            pays = detecter_pays(country_name, self.pays_defaut)
        else:
            pays = self.pays_defaut
        
        # Description
        description = fields.get('body', '')
        if not description:
            description = titre
        
        # Organisme
        sources = fields.get('source', [])
        if sources:
            organisme = sources[0].get('name', 'ReliefWeb')
        else:
            organisme = 'ReliefWeb'
        
        offre = {
            'titre': clean_text(titre)[:300],
            'organisme': organisme,
            'description': clean_text(description)[:1000],
            'date_publication': date_pub,
            'date_cloture': date_cloture,
            'url_source': url_source,
            'url_tdr': None,
            'pays': pays,
            'statut': 'Ouvert',
            'mode_acquisition': 'AUTO',
        }
        
        return offre