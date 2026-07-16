# offres/scraping/parsers/undp_parser.py
import re
import logging
from datetime import date, timedelta
from bs4 import BeautifulSoup

from offres.scraping.base import BaseScraper
from offres.scraping.utils import clean_text, normalize_url
from offres.scraping.extraction_helpers import extract_all_details, extract_pdf_url, is_offer_valid
from offres.utils.search_keywords import detecter_domaine, est_appel_offres

logger = logging.getLogger(__name__)


# =============================================================================
# MAPPING COMPLET DES PAYS POUR UNDP
# =============================================================================
PAYS_UNDP_MAP = {
    # Afrique
    'BURKINA FASO': 'BF', 'BFA': 'BF',
    'SENEGAL': 'SN', 'SEN': 'SN',
    'MALI': 'ML', 'MLI': 'ML',
    'NIGER': 'NE', 'NER': 'NE',
    "COTE D'IVOIRE": 'CI', 'CIV': 'CI',
    'TOGO': 'TG', 'TGO': 'TG',
    'BENIN': 'BJ', 'BEN': 'BJ',
    'GUINEA': 'GN', 'GIN': 'GN',
    'GHANA': 'GH', 'GHA': 'GH',
    'CAMEROON': 'CM', 'CMR': 'CM',
    'CHAD': 'TD', 'TCD': 'TD',
    'NIGERIA': 'NG', 'NGA': 'NG',
    'KENYA': 'KE', 'KEN': 'KE',
    'ETHIOPIA': 'ET', 'ETH': 'ET',
    'CENTRAL AFRICAN REPUBLIC': 'CF', 'CAF': 'CF',
    'DEMOCRATIC REPUBLIC OF THE CONGO': 'CD', 'COD': 'CD',
    'RWANDA': 'RW', 'RWA': 'RW',
    'BURUNDI': 'BI', 'BDI': 'BI',
    'TANZANIA': 'TZ', 'TZA': 'TZ',
    'UGANDA': 'UG', 'UGA': 'UG',
    'MOZAMBIQUE': 'MZ', 'MOZ': 'MZ',
    'MADAGASCAR': 'MG', 'MDG': 'MG',
    'MALAWI': 'MW', 'MWI': 'MW',
    'ZAMBIA': 'ZM', 'ZMB': 'ZM',
    'ZIMBABWE': 'ZW', 'ZWE': 'ZW',
    'SOUTH AFRICA': 'ZA', 'ZAF': 'ZA',
    'MOROCCO': 'MA', 'MAR': 'MA',
    'TUNISIA': 'TN', 'TUN': 'TN',
    'ALGERIA': 'DZ', 'DZA': 'DZ',
    'EGYPT': 'EG', 'EGY': 'EG',
    'SOMALIA': 'SO', 'SOM': 'SO',
    'SUDAN': 'SD', 'SDN': 'SD',
    'SOUTH SUDAN': 'SS', 'SSD': 'SS',
    
    # Amérique
    'ARGENTINA': 'AR', 'ARG': 'AR',
    'BRAZIL': 'BR', 'BRA': 'BR',
    'COLOMBIA': 'CO', 'COL': 'CO',
    'PERU': 'PE', 'PER': 'PE',
    'CHILE': 'CL', 'CHL': 'CL',
    'MEXICO': 'MX', 'MEX': 'MX',
    'BOLIVIA': 'BO', 'BOL': 'BO',
    'ECUADOR': 'EC', 'ECU': 'EC',
    'PARAGUAY': 'PY', 'PRY': 'PY',
    'URUGUAY': 'UY', 'URY': 'UY',
    'VENEZUELA': 'VE', 'VEN': 'VE',
    'HAITI': 'HT', 'HTI': 'HT',
    'DOMINICAN REPUBLIC': 'DO', 'DOM': 'DO',
    'CUBA': 'CU', 'CUB': 'CU',
    'HONDURAS': 'HN', 'HND': 'HN',
    'GUATEMALA': 'GT', 'GTM': 'GT',
    'EL SALVADOR': 'SV', 'SLV': 'SV',
    'NICARAGUA': 'NI', 'NIC': 'NI',
    'PANAMA': 'PA', 'PAN': 'PA',
    'COSTA RICA': 'CR', 'CRI': 'CR',
    
    # Asie
    'NEPAL': 'NP', 'NPL': 'NP',
    'INDIA': 'IN', 'IND': 'IN',
    'PAKISTAN': 'PK', 'PAK': 'PK',
    'BANGLADESH': 'BD', 'BGD': 'BD',
    'SRI LANKA': 'LK', 'LKA': 'LK',
    'AFGHANISTAN': 'AF', 'AFG': 'AF',
    'CHINA': 'CN', 'CHN': 'CN',
    'JAPAN': 'JP', 'JPN': 'JP',
    'KOREA': 'KR', 'KOR': 'KR',
    'VIETNAM': 'VN', 'VNM': 'VN',
    'THAILAND': 'TH', 'THA': 'TH',
    'INDONESIA': 'ID', 'IDN': 'ID',
    'MALAYSIA': 'MY', 'MYS': 'MY',
    'PHILIPPINES': 'PH', 'PHL': 'PH',
    'MYANMAR': 'MM', 'MMR': 'MM',
    'CAMBODIA': 'KH', 'KHM': 'KH',
    'LAOS': 'LA', 'LAO': 'LA',
    'MONGOLIA': 'MN', 'MNG': 'MN',
    'TURKEY': 'TR', 'TUR': 'TR',
    'IRAN': 'IR', 'IRN': 'IR',
    'IRAQ': 'IQ', 'IRQ': 'IQ',
    'JORDAN': 'JO', 'JOR': 'JO',
    'LEBANON': 'LB', 'LBN': 'LB',
    'SYRIA': 'SY', 'SYR': 'SY',
    'YEMEN': 'YE', 'YEM': 'YE',
    'SAUDI ARABIA': 'SA', 'SAU': 'SA',
    
    # Europe
    'SERBIA': 'RS', 'SRB': 'RS',
    'BOSNIA AND HERZEGOVINA': 'BA', 'BIH': 'BA',
    'BOSNIA': 'BA', 'HERZEGOVINA': 'BA',
    'KOSOVO': 'XK', 'XKK': 'XK',
    'MONTENEGRO': 'ME', 'MNE': 'ME',
    'NORTH MACEDONIA': 'MK', 'MKD': 'MK',
    'MACEDONIA': 'MK',
    'ALBANIA': 'AL', 'ALB': 'AL',
    'UKRAINE': 'UA', 'UKR': 'UA',
    'MOLDOVA': 'MD', 'MDA': 'MD',
    'GEORGIA': 'GE', 'GEO': 'GE',
    'ARMENIA': 'AM', 'ARM': 'AM',
    'AZERBAIJAN': 'AZ', 'AZE': 'AZ',
    'BELARUS': 'BY', 'BLR': 'BY',
    'RUSSIA': 'RU', 'RUS': 'RU',
    'POLAND': 'PL', 'POL': 'PL',
    'ROMANIA': 'RO', 'ROU': 'RO',
    'BULGARIA': 'BG', 'BGR': 'BG',
    'HUNGARY': 'HU', 'HUN': 'HU',
    'CZECH REPUBLIC': 'CZ', 'CZE': 'CZ',
    'SLOVAKIA': 'SK', 'SVK': 'SK',
    'CROATIA': 'HR', 'HRV': 'HR',
    'SLOVENIA': 'SI', 'SVN': 'SI',
    'GREECE': 'GR', 'GRC': 'GR',
    'ITALY': 'IT', 'ITA': 'IT',
    'SPAIN': 'ES', 'ESP': 'ES',
    'PORTUGAL': 'PT', 'PRT': 'PT',
    'FRANCE': 'FR', 'FRA': 'FR',
    'GERMANY': 'DE', 'DEU': 'DE',
    'UNITED KINGDOM': 'GB', 'GBR': 'GB',
    'IRELAND': 'IE', 'IRL': 'IE',
    'SWEDEN': 'SE', 'SWE': 'SE',
    'NORWAY': 'NO', 'NOR': 'NO',
    'DENMARK': 'DK', 'DNK': 'DK',
    'FINLAND': 'FI', 'FIN': 'FI',
    'SWITZERLAND': 'CH', 'CHE': 'CH',
    'AUSTRIA': 'AT', 'AUT': 'AT',
    'BELGIUM': 'BE', 'BEL': 'BE',
    'NETHERLANDS': 'NL', 'NLD': 'NL',
    
    # Océanie
    'AUSTRALIA': 'AU', 'AUS': 'AU',
    'NEW ZEALAND': 'NZ', 'NZL': 'NZ',
    'PAPUA NEW GUINEA': 'PG', 'PNG': 'PG',
    'FIJI': 'FJ', 'FJI': 'FJ',
    
    # Régional/Mondial
    'GLOBAL': 'GLOBAL', 'MONDIAL': 'GLOBAL', 'WORLD': 'GLOBAL',
    'REGIONAL': 'REGIONAL',
}


class UNDPParser(BaseScraper):
    """Parser UNDP - Dates et pays extraits UNIQUEMENT du contenu réel"""
    
    def __init__(self, source_url: str, base_url: str = "https://procurement-notices.undp.org", 
                 pays_defaut: str = 'BF', **kwargs):
        delay = kwargs.pop('delay_seconds', 2)
        super().__init__(
            source_url, 
            delay_seconds=delay,
            base_url=base_url, 
            pays_defaut=pays_defaut, 
            **kwargs
        )
    
    def _detecter_pays_undp(self, contenu_texte: str, url_source: str) -> str:
        """
        ✅ Détecte le pays depuis le contenu UNDP et l'URL
        Format UNDP typique : "UNDP Office/CountryArgentina/ARGENTINAProcessRFP"
        """
        try:
            # 1️⃣ Chercher dans le texte le format UNDP : "CountryXXX/XXX"
            match = re.search(r'Country([A-Za-z\s]+)/([A-Z]{2,3})', contenu_texte)
            if match:
                country_name = match.group(1).strip().upper()
                country_code = match.group(2).strip().upper()
                
                # Chercher dans le mapping
                if country_name in PAYS_UNDP_MAP:
                    pays = PAYS_UNDP_MAP[country_name]
                    logger.info(f"   🌍 Pays UNDP détecté (nom): {pays} ({country_name})")
                    return pays
                elif country_code in PAYS_UNDP_MAP.values():
                    logger.info(f"   🌍 Pays UNDP détecté (code): {country_code}")
                    return country_code
                elif len(country_code) == 2:
                    logger.info(f"   🌍 Pays UNDP détecté (code 2 lettres): {country_code}")
                    return country_code
            
            # 2️⃣ Pattern alternatif : "UNDP Office/CountryXXX/XXX"
            match = re.search(r'UNDP\s+Office/Country([A-Za-z\s/]+?)(?:Process|$)', contenu_texte)
            if match:
                country_part = match.group(1).strip().upper()
                # Chercher chaque pays dans le mapping
                for pays_nom, pays_code in PAYS_UNDP_MAP.items():
                    if pays_nom in country_part:
                        logger.info(f"   🌍 Pays UNDP détecté (Office): {pays_code} ({pays_nom})")
                        return pays_code
            
            # 3️⃣ Chercher les noms de pays directement dans le texte
            contenu_upper = contenu_texte.upper()
            for pays_nom, pays_code in PAYS_UNDP_MAP.items():
                if pays_nom in contenu_upper and pays_code not in ['BF', 'GLOBAL', 'REGIONAL']:
                    # Vérifier que c'est bien un pays (pas un mot commun)
                    if len(pays_nom) > 4:  # Éviter les mots courts
                        logger.info(f"   🌍 Pays UNDP détecté (texte): {pays_code} ({pays_nom})")
                        return pays_code
            
            # 4️⃣ Chercher dans l'URL
            url_upper = url_source.upper()
            for pays_nom, pays_code in PAYS_UNDP_MAP.items():
                if pays_nom in url_upper:
                    logger.info(f"   🌍 Pays UNDP détecté (URL): {pays_code} ({pays_nom})")
                    return pays_code
            
            # 5️⃣ Fallback : pays par défaut
            logger.warning(f"   ⚠️ Pays UNDP non détecté, utilisation de {self.pays_defaut}")
            return self.pays_defaut
            
        except Exception as e:
            logger.error(f"   ❌ Erreur détection pays: {e}")
            return self.pays_defaut
    
    def detecter_domaine(self, titre, description=""):
        texte = (titre + " " + (description or "")).lower()
        
        mapping = {
            'IT & Digital': ['informatique', 'digital', 'ordinateur', 'logiciel', 'plateforme', 'data', 'système', 'it', 'technology', 'software', 'hardware', 'réseau', 'internet', 'cloud', 'cyber'],
            'Ingénierie & Construction': ['construction', 'réhabilitation', 'bâtiment', 'génie', 'infrastructure', 'travaux', 'rénovation', 'génie civil', 'architecte', 'chantier'],
            'Santé & Médical': ['santé', 'médical', 'hôpital', 'clinique', 'pharmaceutique', 'laboratoire', 'soins', 'médecine', 'health', 'medical'],
            'Transport & Logistique': ['transport', 'logistique', 'véhicule', 'motocyclette', 'livraison', 'camion', 'bus', 'car', 'fret', 'logistics', 'delivery', 'vehicle'],
            'Éducation & Formation': ['éducation', 'formation', 'enseignement', 'apprentissage', 'training', 'cours', 'études', 'pédagogie', 'education', 'learning'],
            'Environnement & Climat': ['environnement', 'climat', 'énergie', 'renouvelable', 'durable', 'écologie', 'développement durable', 'environment', 'climate', 'energy'],
            'Finance & Comptabilité': ['finance', 'comptabilité', 'audit', 'budget', 'compte', 'financier', 'fiscal', 'financial', 'accounting'],
            'Communication & Médias': ['communication', 'média', 'vidéo', 'documentaire', 'publicité', 'journal', 'radio', 'tv', 'media', 'video'],
            'Agriculture & Alimentation': ['agriculture', 'alimentation', 'agro', 'élevage', 'cultures', 'récolte', 'nourriture', 'agriculture', 'farming', 'food'],
            'Juridique & Droit': ['juridique', 'droit', 'loi', 'réglementation', 'légal', 'contrat', 'legal', 'law'],
            'Ressources Humaines': ['ressources humaines', 'rh', 'recrutement', 'embauche', 'personnel', 'staff', 'human resources', 'hr', 'recruitment'],
            'Sécurité & Protection': ['sécurité', 'protection', 'défense', 'armée', 'militaire', 'garde', 'sûreté', 'security', 'safety'],
            'Social & Égalité': ['social', 'égalité', 'femme', 'jeune', 'égalité des genres', 'pauvreté', 'humanitaire', 'gender', 'women', 'youth', 'humanitarian'],
            'Biens & Équipements': ['bien', 'équipement', 'matériel', 'fourniture', 'achat', 'acquisition', 'equipment', 'supplies', 'procurement', 'purchase'],
            'Services & Conseil': ['service', 'conseil', 'consulting', 'consultant', 'étude', 'expertise', 'services', 'consultancy', 'advisory'],
        }
        
        for domaine, mots in mapping.items():
            for mot in mots:
                if mot in texte:
                    return domaine
        
        if any(mot in texte for mot in ['achat', 'fourniture', 'purchase', 'supply']):
            return 'Biens & Équipements'
        if any(mot in texte for mot in ['étude', 'consultant', 'consultancy', 'advisory']):
            return 'Services & Conseil'
        return 'Autres'
    
    def parse(self, soup: BeautifulSoup) -> list[dict]:
        offres = []
        
        notice_links = []
        for link in soup.find_all('a', href=True):
            href = link['href']
            if 'view_notice' not in href:
                continue
            
            titre = clean_text(link.get_text(strip=True))
            if titre.lower().startswith('title'):
                titre = titre[5:].strip()
            
            if len(titre) < 10:
                continue
            
            url_source = normalize_url(href, self.base_url)
            notice_links.append({'titre': titre, 'url_source': url_source})
        
        logger.info(f"🔍 {len(notice_links)} notices trouvées")
        
        for i, notice in enumerate(notice_links[:15], 1):
            logger.info(f"  [{i}/{len(notice_links)}] {notice['titre'][:50]}...")
            
            try:
                detail_soup = self.fetch_page(notice['url_source'])
                if not detail_soup:
                    continue
                
                # ✅ Extraire le PDF
                pdf_url = extract_pdf_url(detail_soup, self.base_url)
                
                # ✅ Extraire les détails (dates réelles uniquement)
                details = extract_all_details(
                    detail_soup,
                    url=notice['url_source'],
                    pays_defaut=self.pays_defaut,
                    titre=notice['titre'],
                    description=notice['titre']
                )
                
                titre = notice['titre']
                description = notice['titre']
                
                # ✅ REJET STRICT : uniquement les appels d'offres
                if not est_appel_offres(titre, description):
                    logger.info(f"     ⏭️ REJETÉ (pas un appel d'offres)")
                    continue
                
                domaine = self.detecter_domaine(titre, description)
                if details.get('domaine') and details.get('domaine') != 'Autres':
                    domaine = details.get('domaine')
                
                # ✅ Fallback URL source
                url_tdr = pdf_url or details.get('url_tdr') or notice['url_source']
                
                # ✅ Récupérer les dates extraites (peuvent être None)
                date_pub = details.get('date_publication')
                date_cloture = details.get('date_cloture')
                
                # ✅ DÉTECTION DU PAYS AMÉLIORÉE
                # Priorité 1 : Pays détecté par extract_all_details
                pays_final = details.get('pays')
                
                # Priorité 2 : Détection spécifique UNDP si pays par défaut
                if not pays_final or pays_final == self.pays_defaut:
                    contenu_texte = detail_soup.get_text()
                    pays_final = self._detecter_pays_undp(
                        contenu_texte + ' ' + titre,
                        notice['url_source']
                    )
                
                offre = {
                    'titre': titre[:300],
                    'organisme': "UNDP",
                    'description': description[:1000],
                    'date_publication': date_pub,      # ✅ Peut être None
                    'date_cloture': date_cloture,      # ✅ Peut être None
                    'url_source': notice['url_source'],
                    'url_tdr': url_tdr,
                    'pays': pays_final,                # ✅ Pays correctement détecté
                    'domaine': domaine,
                    'statut': 'Ouvert',
                    'type_offre': 'APPEL_D_OFFRES',
                    'mode_acquisition': 'AUTO',
                }
                
                # ✅ Validation finale : rejette si pas de dates
                is_valid, reason = is_offer_valid(offre)
                if not is_valid:
                    logger.info(f"     ⏭️ REJETÉ: {reason}")
                    continue
                
                if not any(o['url_source'] == offre['url_source'] for o in offres):
                    offres.append(offre)
                    logger.info(f"     ✅ AJOUTÉE (pays: {pays_final}, pub: {date_pub}, cloture: {date_cloture}, domaine: {domaine})")
                
            except Exception as e:
                logger.warning(f"     ⚠️ Erreur: {e}")
                import traceback
                logger.error(traceback.format_exc())
                continue
        
        logger.info(f"✅ UNDP: {len(offres)} appel(s) d'offres extrait(s)")
        return offres
    
    def run(self) -> list[dict]:
        logger.info(f"🕷️ UNDP scraping: {self.source_url}")
        try:
            soup = self.fetch_and_parse(use_js=False)
            if not soup:
                return []
            return self.parse(soup)
        except Exception as e:
            logger.error(f"❌ Erreur UNDP: {e}")
            return []