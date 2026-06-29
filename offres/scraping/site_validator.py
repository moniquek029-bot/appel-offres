# offres/scraping/site_validator.py
"""
Validateur de sites d'appels d'offres
Détecte automatiquement si un site publie des appels d'offres
"""

import re
import logging
from bs4 import BeautifulSoup
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

# =============================================================================
# MOTS-CLÉS INDICATEURS D'UN SITE D'APPELS D'OFFRES
# =============================================================================

# Mots-clés français (score élevé)
MOTS_CLES_FR_STRONG = [
    'appel d\'offres', 'appel d\'offre', 'appels d\'offres',
    'avis d\'attribution', 'avis de marché', 'avis de consultation',
    'avis de manifestation d\'intérêt', 'avis à manifestation d\'intérêt',
    'avis de manifestation d\'interet', 'avis à manifestation d\'interet',
    'manifestation d\'intérêt', 'manifestation d\'interet',
    'recrutement d\'un', 'recrutement d\'un bureau', 'recrutement d\'un cabinet',
    'marché public', 'marchés publics',
    'cahier des charges', 'termes de référence', 'termes de reference',
    'dossier de consultation', 'règlement de consultation',
    'procédure de passation', 'passation de marché',
    'consultation des entreprises', 'mise en concurrence',
    'soumission', 'soumissionnaire',
    'bureau d\'études', 'bureau d\'etudes',
    'cabinet d\'expertise', 'cabinet d\'études',
    'consultant', 'consultants',
    'prestation de service', 'prestation de services',
]

# Mots-clés anglais (score élevé)
MOTS_CLES_EN_STRONG = [
    'call for tender', 'call for tenders', 'call for bids',
    'call for proposal', 'call for proposals',
    'call for expression of interest',
    'call for bid', 'call for bids',
    'invitation to bid', 'invitation to tender', 'itt',
    'request for proposal', 'request for quotation', 'rfp', 'rfq',
    'bidding document', 'bid document', 'tender document',
    'procurement notice', 'procurement opportunity',
    'terms of reference', 'tor',
    'request for information', 'rfi',
    'expression of interest', 'eoi',
    'contract notice', 'contract award',
    'bid submission', 'bid opening',
    'consulting firm', 'consulting services',
    'advisory services',
]

# Mots-clés français (score moyen)
MOTS_CLES_FR_MEDIUM = [
    'offre', 'offres', 'tender', 'tenders',
    'consultation', 'consultations',
    'recrutement', 'recrutements',
    'projet', 'projets',
    'subvention', 'subventions',
    'financement', 'financements',
    'marché', 'marchés',
    'contrat', 'contrats',
    'attribution', 'attributions',
    'mission', 'missions',
    'expertise',
]

# Mots-clés anglais (score moyen)
MOTS_CLES_EN_MEDIUM = [
    'tender', 'tenders', 'bids', 'bidding',
    'procurement', 'procurements',
    'contract', 'contracts',
    'proposal', 'proposals',
    'grant', 'grants',
    'funding', 'fundings',
    'vacancy', 'vacancies',
    'job', 'jobs', 'career', 'careers',
    'position', 'positions',
    'consultancy', 'consulting',
    'assignment', 'assignments',
    'service', 'services',
]

# Mots-clés indicateurs de NON-offre (score négatif)
MOTS_CLES_REJET = [
    'actualité', 'actualités', 'news', 'blog', 'article',
    'événement', 'événements', 'event', 'events',
    'galerie', 'gallery', 'photo', 'photos',
    'vidéo', 'video', 'videos',
    'témoignage', 'testimonial',
    'recette', 'recipe',
    'podcast',
    'forum', 'discussion',
    'commentaire', 'comment',
    'earthquake', 'flood', 'cyclone', 'outbreak',
    'tsunami', 'landslide', 'drought', 'famine',
    'cholera', 'ebola', 'measles', 'dengue', 'diphtheria',
    'press release', 'communiqué de presse',
    'annual report', 'rapport annuel',
    'story', 'stories', 'feature',
    'world news', 'news in brief',
]

# URLs typiques de pages d'appels d'offres
URLS_OFFRES_PATTERNS = [
    r'appel.*offre',
    r'avis.*march',
    r'march.*public',
    r'tender',
    r'procurement',
    r'bid',
    r'rfp',
    r'rfq',
    r'consultation',
    r'vacancy',
    r'vacancies',
    r'career',
    r'job',
    r'opportunity',
    r'call-for',
    r'submission',
    r'manifestation.*interet',
    r'recrutement',
]

# =============================================================================
# CLASSE DE VALIDATION
# =============================================================================

class SiteValidator:
    """Valide si un site/publique est lié aux appels d'offres"""
    
    def __init__(self, html_content: str = None, url: str = None, soup: BeautifulSoup = None):
        self.html_content = html_content or ''
        self.url = url or ''
        self.soup = soup
        self.score = 0
        self.indicators = []
        self.rejection_reasons = []
        
        if html_content and not soup:
            self.soup = BeautifulSoup(html_content, 'html.parser')
    
    def validate(self) -> dict:
        """
        Effectue la validation complète
        Retourne: {
            'is_valid': bool,
            'score': int,
            'indicators': list,
            'rejection_reasons': list,
            'confidence': str  # 'high', 'medium', 'low'
        }
        """
        self.score = 0
        self.indicators = []
        self.rejection_reasons = []
        
        # 1. Validation de l'URL
        self._validate_url()
        
        # 2. Validation du contenu HTML
        if self.soup:
            self._validate_content()
        
        # 3. Détermination du résultat
        is_valid = self.score >= 10 and len(self.rejection_reasons) == 0
        confidence = self._get_confidence()
        
        result = {
            'is_valid': is_valid,
            'score': self.score,
            'indicators': self.indicators,
            'rejection_reasons': self.rejection_reasons,
            'confidence': confidence
        }
        
        logger.info(f"🔍 Validation: Score={self.score}, Valid={is_valid}, Confiance={confidence}")
        if self.indicators:
            logger.info(f"   ✅ Indicateurs: {', '.join(self.indicators[:5])}")
        if self.rejection_reasons:
            logger.warning(f"   ❌ Rejets: {', '.join(self.rejection_reasons[:5])}")
        
        return result
    
    def _validate_url(self):
        """Valide l'URL pour détecter des patterns d'appels d'offres"""
        if not self.url:
            return
        
        url_lower = self.url.lower()
        
        # Patterns d'URL positifs
        for pattern in URLS_OFFRES_PATTERNS:
            if re.search(pattern, url_lower):
                self.score += 15
                self.indicators.append(f"URL pattern: {pattern}")
                break
        
        # Domaines connus d'appels d'offres
        known_domains = [
            'undp.org', 'unfpa.org', 'worldbank.org', 'who.int',
            'uemoa.int', 'afdb.org', 'un.org',
            'agetib.net', 'sonabel.bf', 'joffres.net',
            'developmentaid.org', 'dgmarket.com', 'ted.europa.eu',
        ]
        
        # ⚠️ EXCLURE reliefweb.int (catastrophes, pas appels d'offres)
        excluded_domains = ['reliefweb.int']
        
        parsed = urlparse(self.url)
        domain = parsed.netloc.lower()
        
        # Vérifier d'abord si c'est un domaine exclu
        for excluded in excluded_domains:
            if excluded in domain:
                self.score -= 30
                self.rejection_reasons.append(f"Domaine exclu (catastrophes): {excluded}")
                return
        
        for known in known_domains:
            if known in domain:
                self.score += 20
                self.indicators.append(f"Domaine connu: {known}")
                break
    
    def _validate_content(self):
        """Valide le contenu HTML pour détecter des indicateurs d'appels d'offres"""
        if not self.soup:
            return
        
        # Extraire le texte de la page
        text = self.soup.get_text().lower()
        title = self.soup.title.string.lower() if self.soup.title else ''
        
        # Compter les occurrences de mots-clés
        self._count_keywords(text, title)
        
        # Vérifier la présence de liens vers des documents
        self._check_document_links()
        
        # Vérifier la présence de dates limites
        self._check_deadlines()
    
    def _count_keywords(self, text: str, title: str):
        """Compte les occurrences de mots-clés"""
        # Mots-clés forts français
        for kw in MOTS_CLES_FR_STRONG:
            count = text.count(kw.lower())
            if count > 0:
                self.score += 10 * min(count, 3)
                self.indicators.append(f"FR strong: '{kw}' ({count}x)")
        
        # Mots-clés forts anglais
        for kw in MOTS_CLES_EN_STRONG:
            count = text.count(kw.lower())
            if count > 0:
                self.score += 10 * min(count, 3)
                self.indicators.append(f"EN strong: '{kw}' ({count}x)")
        
        # Mots-clés moyens français
        for kw in MOTS_CLES_FR_MEDIUM:
            count = text.count(kw.lower())
            if count >= 2:
                self.score += 3 * min(count, 5)
                self.indicators.append(f"FR medium: '{kw}' ({count}x)")
        
        # Mots-clés moyens anglais
        for kw in MOTS_CLES_EN_MEDIUM:
            count = text.count(kw.lower())
            if count >= 2:
                self.score += 3 * min(count, 5)
                self.indicators.append(f"EN medium: '{kw}' ({count}x)")
        
        # Mots-clés de rejet
        for kw in MOTS_CLES_REJET:
            count = text.count(kw.lower())
            if count >= 5:  # ✅ AUGMENTÉ : Seulement si TRÈS fréquent (5+ au lieu de 3)
                self.score -= 5
                self.rejection_reasons.append(f"Contenu non-offre: '{kw}' ({count}x)")
        
        # Bonus si le titre contient des mots-clés
        for kw in MOTS_CLES_FR_STRONG + MOTS_CLES_EN_STRONG:
            if kw in title:
                self.score += 15
                self.indicators.append(f"Titre: '{kw}'")
                break
    
    def _check_document_links(self):
        """Vérifie la présence de liens vers des documents PDF/DOC"""
        if not self.soup:
            return
        
        doc_links = 0
        for link in self.soup.find_all('a', href=True):
            href = link['href'].lower()
            if href.endswith(('.pdf', '.doc', '.docx')):
                doc_links += 1
        
        if doc_links >= 3:
            self.score += 10
            self.indicators.append(f"Documents: {doc_links} liens PDF/DOC")
        elif doc_links >= 1:
            self.score += 5
            self.indicators.append(f"Documents: {doc_links} lien(s) PDF/DOC")
    
    def _check_deadlines(self):
        """Vérifie la présence de dates limites"""
        if not self.soup:
            return
        
        deadline_patterns = [
            r'date\s*limite',
            r'date\s*de\s*clôture',
            r'deadline',
            r'closing\s*date',
            r'soumission\s*avant',
            r'submit\s*by',
        ]
        
        text = self.soup.get_text().lower()
        for pattern in deadline_patterns:
            if re.search(pattern, text):
                self.score += 8
                self.indicators.append(f"Date limite détectée: {pattern}")
                break
    
    def _get_confidence(self) -> str:
        """Détermine le niveau de confiance"""
        if self.score >= 30:
            return 'high'
        elif self.score >= 15:
            return 'medium'
        else:
            return 'low'


# =============================================================================
# FONCTIONS UTILITAIRES
# =============================================================================

def validate_site(html_content: str, url: str = None) -> dict:
    """Fonction simplifiée pour valider un site"""
    validator = SiteValidator(html_content=html_content, url=url)
    return validator.validate()


def validate_page(soup: BeautifulSoup, url: str = None) -> dict:
    """Valide une page déjà parsée"""
    validator = SiteValidator(soup=soup, url=url)
    return validator.validate()


def is_valid_offer_title(title: str) -> bool:
    """
    Vérifie si un titre correspond à un appel d'offres
    ✅ VERSION AMÉLIORÉE avec plus de mots-clés et logs
    """
    if not title or len(title) < 15:
        logger.debug(f"⏭️ Rejeté (titre trop court): {title}")
        return False
    
    title_lower = title.lower()
    
    # ❌ MOTIFS DE REJET IMMÉDIAT
    rejet_patterns = [
        r'earthquake', r'flood', r'cyclone', r'typhoon', r'hurricane',
        r'tsunami', r'landslide', r'drought', r'famine', r'wildfire',
        r'tremor', r'volcano', r'eruption',
        r'outbreak', r'epidemic', r'pandemic',
        r'cholera', r'ebola', r'measles', r'dengue', r'diphtheria',
        r'malaria', r'tuberculosis', r'polio',
        r'world news', r'news in brief', r'press release',
        r'communiqué de presse', r'annual report', r'rapport annuel',
        r'quarterly report', r'year in review',
        r'trending data', r'feature story',
        r'environmental & social policies',
        r'financing products & advisory',
        r'bonds & investment',
        r'about us', r'careers', r'jobs', r'vacancies',
        r'mission', r'vision', r'our work',
        r'conference', r'summit', r'workshop', r'seminar',
        r'webinar', r'meeting', r'forum',
        r'program launch', r'initiative launch',
        r'partnership announced', r'memorandum of understanding',
    ]
    
    for pattern in rejet_patterns:
        if re.search(pattern, title_lower):
            logger.debug(f"⏭️ Rejeté (motif rejet): {title[:50]}")
            return False
    
    # ✅ MOTS-CLÉS OBLIGATOIRES (liste ÉLARGIE)
    mots_cles_obligatoires = [
        # Français
        'appel d\'offre', 'appel d\'offres', 'appels d\'offres',
        'avis de marché', 'avis d\'attribution', 'avis de consultation',
        'manifestation d\'intérêt', 'manifestation d\'interet',
        'recrutement d\'un', 'recrutement d\'une', 'recrutement d\'un bureau',
        'marché public', 'marchés publics',
        'cahier des charges', 'termes de référence',
        'dossier de consultation', 'consultation des',
        'bureau d\'études', 'bureau d\'etudes',
        'cabinet', 'consultant', 'expertise',
        'prestation de service', 'prestation de services',
        # ✅ NOUVEAUX MOTS-CLÉS AJOUTÉS
        'cotation', 'cotations', 'demande de cotation',
        'achat de', 'acquisition de', 'fourniture de',
        'recrutement', 'embauche', 'sélection',
        'avis de', 'annonce de',
        'travaux de', 'étude de', 'mission de',
        
        # Anglais
        'call for tender', 'call for tenders', 'call for bids',
        'call for proposal', 'call for proposals',
        'invitation to bid', 'invitation to tender',
        'request for proposal', 'request for quotation',
        'bidding document', 'tender document',
        'procurement notice', 'procurement opportunity',
        'terms of reference', 'expression of interest',
        'consulting firm', 'consulting services',
        'advisory services', 'consultancy services',
        'contract award', 'contract notice',
        # ✅ NOUVEAUX MOTS-CLÉS AJOUTÉS
        'rfp', 'rfq', 'rfi',
        'request for', 'invitation for',
        'notice of', 'announcement of',
    ]
    
    # Vérifier si au moins un mot-clé obligatoire est présent
    has_valid_keyword = any(kw in title_lower for kw in mots_cles_obligatoires)
    
    if not has_valid_keyword:
        logger.debug(f"⏭️ Rejeté (pas de mot-clé valide): {title[:50]}")
        return False
    
    # ✅ Vérifications supplémentaires
    if len(title) < 20:
        logger.debug(f"⏭️ Rejeté (titre trop court): {title}")
        return False
    
    # Ne doit pas être trop générique
    generic_terms = ['news', 'update', 'report', 'story', 'article']
    if all(term not in title_lower for term in generic_terms):
        return True
    
    logger.debug(f"⏭️ Rejeté (trop générique): {title[:50]}")
    return False


def is_rejected_content(text: str) -> bool:
    """
    Vérifie si un contenu doit être rejeté (non-offre)
    ✅ VERSION UNIQUE (suppression du doublon)
    """
    if not text or len(text) < 50:
        return True
    
    text_lower = text.lower()
    
    # ❌ MOTIFS DE REJET FORTS
    rejet_fort = [
        r'earthquake and tsunami',
        r'floods and landslides',
        r'cyclone.*\d{4}',
        r'outbreak.*\d{4}',
        r'cholera outbreak',
        r'ebola outbreak',
        r'measles outbreak',
        r'world news in brief',
        r'press release',
        r'news update',
        r'annual report',
        r'disaster', r'emergency', r'humanitarian',
        r'affected people', r'displaced',
    ]
    
    for pattern in rejet_fort:
        if re.search(pattern, text_lower):
            logger.debug(f"⏭️ Contenu rejeté (motif fort): {text[:50]}")
            return True
    
    # Compter les mots-clés de rejet
    mots_rejet = [
        'actualité', 'actualités', 'news', 'blog', 'article',
        'événement', 'événements', 'event', 'events',
        'galerie', 'gallery', 'photo', 'photos',
        'vidéo', 'video', 'videos',
        'podcast', 'forum', 'discussion',
        'earthquake', 'flood', 'cyclone', 'outbreak',
        'tsunami', 'landslide', 'drought',
    ]
    
    rejection_count = sum(1 for kw in mots_rejet if kw in text_lower)
    
    # Compter les mots-clés d'offre
    mots_offre = [
        'appel d\'offre', 'call for tender', 'call for proposal',
        'terms of reference', 'procurement', 'tender',
        'bidding', 'consultant', 'consulting',
        'cotation', 'achat', 'fourniture', 'recrutement',
    ]
    
    offer_count = sum(1 for kw in mots_offre if kw in text_lower)
    
    # ✅ AUGMENTÉ : Rejeter seulement si BEAUCOUP de rejets (5+) et peu d'offres
    if rejection_count >= 5 and offer_count == 0:
        logger.debug(f"⏭️ Contenu rejeté (trop de rejets, pas d'offres): {text[:50]}")
        return True
    
    return False