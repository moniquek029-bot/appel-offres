# offres/scraping/tasks.py - Version COMPLÈTE avec gestion automatique des offres expirées

from celery import shared_task
from django.utils import timezone
from urllib.parse import urlparse
from django.db import transaction
from django.core.files.base import ContentFile  
import logging
import requests
import time  


from offres.models import SourceScraping, AppelOffre
from offres.scraping.parsers.Oxfam_parser import OxfamParser
from offres.scraping.utils import (
    archive_expired_offres, clean_text, parse_french_date, 
    normalize_url, extract_pdf_from_page, is_valid_pdf_url, 
    download_pdf_file, fetch_and_validate_pdf,
    archive_and_delete_old_offres
)
from offres.services.notifications import check_and_notify_matches
from offres.scraping.site_validator import SiteValidator, is_valid_offer_title, is_rejected_content

from offres.scraping.extraction_helpers import (
    extract_all_details,
    extract_pdf_url,
    is_offer_valid,
    is_offer_expired,
    is_date_unrealistic,
    parse_date_universelle
    
)

from offres.scraping.extraction_helpers import extract_publication_date_from_text, extract_deadline_from_text

from offres.scraping.auth_scrapers import AuthenticatedScraper, SeleniumScraper
from offres.models import SourceCredentials

# ✅ Ajout de l'import pour l'extraction des dates
#from offres.scraping.extraction_helpers import extract_publication_date_from_text, extract_deadline_from_text

# =============================================================================
# CONFIGURATION
# =============================================================================
USE_MOCK_FALLBACK = False
REQUIRE_PDF = False

logger = logging.getLogger(__name__)

# =============================================================================
# IMPORTS DES PARSERS
# =============================================================================
from offres.scraping.parsers.unfpa_parser import UNFPAParser
from offres.scraping.parsers.undp_parser import UNDPParser
from offres.scraping.parsers.agetib_parser import AgetibParser
from offres.scraping.parsers.sonabel_parser import SONABELParser
from offres.scraping.parsers.uemoa_parser import UEMOAParser
from offres.scraping.parsers.joffres_parser import JoffresParser
from offres.scraping.parsers.abf_burkina_parser import ABFBurkinaScraper
from offres.scraping.parsers.smart_parser import SmartParser
from offres.scraping.parsers.afdb_parser import AfDBParser
from offres.scraping.parsers.psimali_parser import PSIMaliParser
from offres.scraping.parsers.jaoguinee_parser import JaoGuineeParser

from offres.scraping.parsers.who_parser import WHOParser
from offres.scraping.parsers.worldbank_parser import WorldBankParser
from offres.scraping.parsers.enabel_parser import EnabelParser
from offres.scraping.parsers.isdb_parser import ISDBParser
from offres.scraping.parsers.marches_securises_parser import MarchesSecurisesParser
from offres.scraping.parsers.talacom_parser import TalaComParser
from offres.scraping.parsers.j360_parser import J360Parser
from offres.scraping.parsers.sangobids_parser import SangoBidsParser
# =============================================================================
# REGISTRE DES PARSERS
# =============================================================================
PARSER_REGISTRY = {
    # === SITES INTERNATIONAUX ===
    "burkinafaso.unfpa.org": UNFPAParser,
    "www.unfpa.org": UNFPAParser,
    "procurement-notices.undp.org": UNDPParser,
    "www.afdb.org": AfDBParser,
    "www.who.int": WHOParser,
    "www.worldbank.org": WorldBankParser,
    "www.psimali.ml": PSIMaliParser,
    "psimali.ml": PSIMaliParser,
    "www.jaoguinee.com": JaoGuineeParser,
    "jaoguinee.com": JaoGuineeParser,
    "www.enabel.be": EnabelParser,
    "enabel.be": EnabelParser,
    "www.isdb.org": ISDBParser,
    "isdb.org": ISDBParser,
    "www.marches-securises.fr": MarchesSecurisesParser,
    "marches-securises.fr": MarchesSecurisesParser,
    "www.tala-com.com": TalaComParser,
    "tala-com.com": TalaComParser,
    # === SITES BURKINA FASO ===
    "www.agetib.net": AgetibParser,
    "www.sonabel.bf": SONABELParser,
    "www.abfburkina.org": ABFBurkinaScraper,
    "abfburkina.org": ABFBurkinaScraper,
    "burkinafaso.oxfam.org": OxfamParser,
    "www.j360.info": J360Parser,
    "j360.info": J360Parser,
    "bf.sangobids.com": SangoBidsParser,
    "sangobids.com": SangoBidsParser,
    # === SITES RÉGIONAUX ===
    "www.uemoa.int": UEMOAParser,
    "uemoa.int": UEMOAParser,
    
    # === SITES D'OFFRES INTERNATIONALES ===
    "www.joffres.net": JoffresParser,

    # === PARSER PAR DÉFAUT ===
    "default": SmartParser,
}

# =============================================================================
# ✅ LISTE BLANCHE : Sites de confiance (validation ignorée)
# =============================================================================
TRUSTED_SOURCES = [
    'unfpa.org',
    'uemoa.int',
    'undp.org',
    'globaltenders.com',  
    'who.int',
    'worldbank.org',
    'agetib.net',
    'sonabel.bf',
    'abfburkina.org',
    'joffres.net',
    'afdb.org',
    'psimali.ml',
    "enabel.be",
    "isdb.org",
    "marches-securises.fr",
    "tala-com.com",
    'jaoguinee.com',
    "j360.info",
    "sangobids.com",
]


def get_parser_for_source(source):
    """
    Retourne le parser approprié pour une source
    ✅ Détecte automatiquement si la source nécessite une authentification
    """
    try:
        parsed = urlparse(source.url_racine)
        domain = parsed.netloc.lower()
        
        JS_REQUIRED_SITES = ['undp.org', 'worldbank.org', 'un.org', 'who.int']
        use_js = any(site in domain for site in JS_REQUIRED_SITES)
        
        # ✅ VÉRIFICATION AUTOMATIQUE : La source a-t-elle des credentials ?
        try:
            credentials = source.credentials
            if credentials and credentials.is_active:
                creds_dict = credentials.get_credentials()
                
                # Choisir le scraper selon le type d'auth
                if credentials.auth_type == 'SELENIUM':
                    logger.info(f"🔐 Source protégée détectée: {source.nom} → SeleniumScraper")
                    return SeleniumScraper(source.url_racine, credentials=creds_dict)
                else:
                    logger.info(f"🔐 Source protégée détectée: {source.nom} → AuthenticatedScraper")
                    return AuthenticatedScraper(source.url_racine, credentials=creds_dict)
        except SourceCredentials.DoesNotExist:
            # Pas de credentials → site public
            pass
        
        # Site public → parser normal
        for key, parser_class in PARSER_REGISTRY.items():
            if key in domain:
                if parser_class is SmartParser or parser_class is None:
                    return SmartParser(source.url_racine, use_js=use_js)
                return parser_class(source.url_racine)
        
        return SmartParser(source.url_racine, use_js=use_js)
        
    except Exception as e:
        logger.error(f"❌ Erreur sélection parser: {e}")
        return SmartParser(source.url_racine)
        
def is_trusted_source(url_racine: str) -> bool:
    """Vérifie si une source est dans la liste blanche"""
    parsed_domain = urlparse(url_racine).netloc.lower()
    return any(trusted in parsed_domain for trusted in TRUSTED_SOURCES)


# =============================================================================
# ✅ FONCTION POUR MARQUER LES OFFRES EXPIRÉES
# =============================================================================

def mark_expired_offres():
    """
    Marque les offres comme expirées lorsque la date de clôture est passée
    """
    today = timezone.now().date()
    
    expired = AppelOffre.objects.filter(
        date_cloture__lt=today,
        statut='Ouvert'
    )
    
    count = expired.count()
    
    if count > 0:
        expired.update(statut='Expiré')
        logger.info(f"📅 {count} offres marquées comme expirées")
    
    return count


# =============================================================================
# ✅ FONCTION POUR SUPPRIMER LES OFFRES EXPIRÉES DÉFINITIVEMENT
# =============================================================================

@shared_task
def delete_expired_offres():
    """
    Supprime définitivement les offres expirées après 7 jours
    """
    logger.info("🗑️ Suppression des offres expirées...")
    
    from datetime import timedelta
    cutoff_date = timezone.now().date() - timedelta(days=7)
    
    # Offres expirées depuis plus de 7 jours
    expired_offres = AppelOffre.objects.filter(
        statut='Expiré',
        date_cloture__lt=cutoff_date
    )
    
    count = expired_offres.count()
    
    if count > 0:
        for offre in expired_offres:
            # Supprimer le PDF physique
            if offre.fichier_pdf:
                try:
                    offre.fichier_pdf.delete(save=False)
                except:
                    pass
            offre.delete()
        
        logger.info(f"✅ {count} offres expirées supprimées définitivement")
        return {"deleted": count}
    
    logger.info("✅ Aucune offre à supprimer")
    return {"deleted": 0}

    
@shared_task(bind=True, max_retries=2, default_retry_delay=60)
def run_scheduled_scraping_task(self, source_id=None):
    """Tâche Celery pour le scraping (PDF optionnel + Fallback intelligent + Validation des sites + Notifications)"""
    
    if source_id:
        sources = SourceScraping.objects.filter(id=source_id, est_actif=True)
        logger.info(f"🕷️ Scraping manuel pour source ID {source_id}")
    else:
        sources = SourceScraping.objects.filter(est_actif=True)
        logger.info("🕷️ Scraping automatique : toutes les sources actives")
    
    if not sources.exists():
        logger.warning("⚠️ Aucune source active trouvée")
        return {"new": 0, "updated": 0, "skipped": 0, "rejected": 0, "sources": 0}
    
    total_new = 0
    total_updated = 0
    total_skipped = 0
    total_rejected = 0

    for source in sources:
        try:
            logger.info(f"🕷️ Scraping RÉEL: {source.nom} ({source.url_racine})")
            
            scraper = get_parser_for_source(source)
            if not scraper:
                logger.warning(f"⚠️ Source ignorée: {source.nom}")
                total_skipped += 1
                continue
            
            # =========================================================================
            # ✅ VALIDATION DU SITE (uniquement pour les sites NON-fiables)
            # =========================================================================
            if is_trusted_source(source.url_racine):
                logger.info(f"✅ Site de confiance, validation ignorée: {source.nom}")
            else:
                logger.info(f"🔍 Validation du site: {source.nom}")
                
                try:
                    validation_soup = scraper.fetch_and_parse(use_js=False)
                    
                    if validation_soup:
                        validator = SiteValidator(soup=validation_soup, url=source.url_racine)
                        validation = validator.validate()
                        
                        if not validation.get('is_valid', False):
                            logger.warning(f"❌ Site REJETÉ: {source.nom}")
                            logger.warning(f"   Score: {validation.get('score', 0)}")
                            logger.warning(f"   Raisons: {validation.get('rejection_reasons', [])}")
                            logger.warning(f"   → Ce site ne semble pas publier d'appels d'offres")
                            total_rejected += 1
                            continue
                        
                        logger.info(f"✅ Site VALIDÉ: {source.nom} (Score: {validation.get('score', 0)}, Confiance: {validation.get('confidence', 'low')})")
                    else:
                        logger.warning(f"⚠️ Impossible de récupérer la page pour validation: {source.nom}")
                
                except Exception as val_err:
                    logger.warning(f"⚠️ Erreur lors de la validation: {val_err}")
            
            # =========================================================================
            # SCRAPING DES OFFRES
            # =========================================================================
            raw_offres = scraper.run()
            
            if not raw_offres:
                logger.warning(f"⚠️ Aucune offre extraite pour {source.nom}")
                continue
            
            logger.info(f"📊 {len(raw_offres)} offres brutes extraites")

            # Détection si le domaine requiert du JS
            parsed_domain = urlparse(source.url_racine).netloc.lower()
            is_js_site = any(site in parsed_domain for site in ['undp.org', 'worldbank.org', 'un.org', 'who.int'])

            for data in raw_offres:
                titre_debug = data.get('titre', '')[:30]
                
                # =========================================================================
                # ✅ VALIDATION DE L'OFFRE INDIVIDUELLE
                # =========================================================================
                titre_offre = data.get('titre', '').strip()
                description_offre = data.get('description', '').strip()
                
                # Vérifier que c'est bien un appel d'offres
                if not is_valid_offer_title(titre_offre):
                    logger.info(f"⏭️ Offre REJETÉE (titre non-valide): '{titre_debug}...'")
                    total_rejected += 1
                    continue
                
                # Vérifier que ce n'est pas du contenu non-offre
                if is_rejected_content(titre_offre + ' ' + description_offre):
                    logger.info(f"⏭️ Offre REJETÉE (contenu non-offre): '{titre_debug}...'")
                    total_rejected += 1
                    continue
                
                # =========================================================================
                # EXTRACTION DU PDF SI ABSENT
                # =========================================================================
                if not data.get('url_tdr') and data.get('url_source'):
                    try:
                        if is_js_site and hasattr(scraper, 'fetch_page'):
                            detail_soup = scraper.fetch_page(data['url_source'], use_js=True)
                            if detail_soup:
                                extracted_pdf = scraper._trouver_pdf_dans_page(detail_soup, data['url_source'])
                                if extracted_pdf:
                                    data['url_tdr'] = extracted_pdf
                                    logger.info(f"📄 PDF extrait via DOM JS: {data['url_tdr'][:80]}...")
                        else:
                            headers = {'User-Agent': 'Mozilla/5.0'}
                            detail_response = requests.get(data['url_source'], headers=headers, timeout=15)
                            if detail_response.status_code == 200:
                                extracted_pdf = extract_pdf_from_page(detail_response.text, source.url_racine)
                                if extracted_pdf:
                                    data['url_tdr'] = extracted_pdf
                                    logger.info(f"📄 PDF extrait via HTTP: {data['url_tdr'][:80]}...")
                    except Exception as pdf_err:
                        logger.debug(f"⚠️ PDF non extrait pour '{titre_debug}': {pdf_err}")
                
                # FALLBACK - Si toujours pas de TDR, utiliser url_source
                if not data.get('url_tdr') and data.get('url_source'):
                    data['url_tdr'] = data['url_source']
                    logger.info(f"🔄 FALLBACK: url_tdr = url_source pour '{titre_debug}...'")
                
                # =========================================================================
                # SAUVEGARDE
                # =========================================================================
                result = save_offre_real(data, source, require_pdf=REQUIRE_PDF)
                
                if result == 'created':
                    total_new += 1
                    logger.info(f"✅ +1 Nouvelle: '{titre_debug}...'")
                elif result == 'updated':
                    total_updated += 1
                    logger.debug(f"🔄 +1 MAJ: '{titre_debug}...'")
                else:
                    total_skipped += 1
                    logger.debug(f"⏭️ Ignorée: '{titre_debug}...'")

            source.last_scraped = timezone.now()
            source.save(update_fields=["last_scraped"])
            logger.info(f"✅ Source {source.nom} traitée avec succès")

        except Exception as e:
            logger.error(f"❌ Échec de la tâche pour la source {source.nom}: {e}")
            if self.request.retries < self.max_retries:
                raise self.retry(exc=e)
            else:
                logger.error(f"❌ Échec définitif pour {source.nom}")

    # =========================================================================
    # ✅ NOTIFICATIONS AUTOMATIQUES (Si de nouvelles offres ont été trouvées)
    # =========================================================================
    if total_new > 0:
        logger.info(f"🔔 {total_new} nouvelles offres détectées → Lancement des notifications...")
        
        # 1. Notifier les experts
        try:
            from offres.services.smart_matching import notifier_tous_les_experts
            notifier_tous_les_experts()
            logger.info("✅ Notifications experts envoyées")
        except Exception as notif_err:
            logger.error(f"❌ Erreur notification experts: {notif_err}")
        
        # 2. Notifier les bureaux d'études
        try:
            from offres.services.smart_matching import notifier_tous_les_bureaux
            notifier_tous_les_bureaux()
            logger.info("✅ Notifications bureaux envoyées")
        except Exception as notif_err:
            logger.error(f"❌ Erreur notification bureaux: {notif_err}")
    else:
        logger.info(" Aucune nouvelle offre → Pas de notification envoyée")

    logger.info(f" Terminé | +{total_new} nouvelles | ~{total_updated} MAJ | {total_skipped} ignorées | ❌ {total_rejected} rejetées")
    
    return {
        "new": total_new, 
        "updated": total_updated, 
        "skipped": total_skipped, 
        "rejected": total_rejected,
        "sources": sources.count()
    }



@shared_task
def daily_scraping_and_verification():
    """Scraping quotidien + vérification des pays"""
    from offres.scraping.tasks import run_scheduled_scraping_task
    
    # 1. Lancer le scraping
    result = run_scheduled_scraping_task()
    
    # 2. Vérifier les pays
    from scripts.verifier_pays import verifier_pays
    is_valid = verifier_pays()
    
    if not is_valid:
        logger.warning("⚠️ Des pays incorrects ont été détectés après le scraping")
    
    return {
        'scraping': result,
        'verification_pays': is_valid
    }

@transaction.atomic
def save_offre_real(data: dict, source: SourceScraping, require_pdf: bool = False) -> str:
    """
    ✅ VERSION STRICTE :
    - Pas de date de clôture → None (pas de J+30)
    - Pas de PDF → url_source comme url_tdr
    - Offres d'emploi → REJET
    """
    titre = clean_text(data.get('titre', '')).strip()
    organisme = clean_text(data.get('organisme', '')).strip()
    description = clean_text(data.get('description', ''))
    
    # =========================================================================
    # ✅ VALIDATION 1 : TITRE ET ORGANISME
    # =========================================================================
    if not titre or len(titre) < 15:
        logger.debug(f"⏭️ Ignorée (titre manquant/court)")
        return 'skipped'
    
    # =========================================================================
    # ✅ VALIDATION 2 : PAS UNE OFFRE D'EMPLOI
    # =========================================================================
    from offres.utils.search_keywords import est_appel_offres
    if not est_appel_offres(titre, description):
        logger.info(f"⏭️ REJETÉE - Pas un appel d'offres: {titre[:50]}...")
        return 'skipped'
    
    # =========================================================================
    # ✅ VALIDATION 3 : CONTENU NON-OFFRE
    # =========================================================================
    if is_rejected_content(titre + ' ' + description):
        logger.info(f"⏭️ REJETÉE - Contenu non-offre: {titre[:50]}...")
        return 'skipped'
    
    url_source = normalize_url(data.get('url_source'), source.url_racine)
    url_tdr = normalize_url(data.get('url_tdr'), source.url_racine)
    
    if not url_source and not url_tdr:
        logger.warning(f"⏭️ Ignorée (pas d'URL): {titre[:50]}...")
        return 'skipped'
    
    # =========================================================================
    # ✅ RÉCUPÉRER LE CONTENU DE LA PAGE DÉTAIL
    # =========================================================================
    detail_texte = ''
    if url_source:
        try:
            import requests
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
            detail_response = requests.get(url_source, headers=headers, timeout=30, verify=False)
            if detail_response.status_code == 200:
                from bs4 import BeautifulSoup
                detail_soup = BeautifulSoup(detail_response.text, 'html.parser')
                detail_texte = detail_soup.get_text(separator=' ')
        except Exception as e:
            logger.warning(f"⚠️ Erreur page détail: {e}")
    
    texte_complet = f"{titre} {description} {detail_texte}"
    
    # =========================================================================
    # ✅ EXTRACTION DES DATES - AUCUN FALLBACK
    # =========================================================================
    
    # Date de publication
    date_pub = parse_french_date(data.get('date_publication'))
    if not date_pub:
        extracted_pub = extract_publication_date_from_text(texte_complet)
        if extracted_pub:
            date_pub = extracted_pub
    
    # ✅ REJET si pas de date de publication
    if not date_pub:
        logger.info(f"⏭️ REJETÉE - Pas de date publication: {titre[:50]}...")
        return 'skipped'
    
    # Date de clôture - ❌ AUCUN FALLBACK J+30
    date_clot = parse_french_date(data.get('date_cloture'))
    if not date_clot:
        extracted_deadline = extract_deadline_from_text(texte_complet)
        if extracted_deadline:
            date_clot = extracted_deadline
    
    # ✅ SI PAS DE DATE DE CLÔTURE → None (pas de J+30 !)
    if not date_clot:
        logger.info(f"⚠️ Offre sans date de clôture: {titre[:50]}... → None")
        date_clot = None  # ✅ Laisser vide
    
    # =========================================================================
    # ✅ DÉTECTION DU PAYS
    # =========================================================================
    pays = data.get('pays')
    if not pays:
        from offres.scraping.country_detector import detecter_pays_smart
        pays = detecter_pays_smart(texte_complet, url=url_source, pays_defaut=None)
    
    if not pays:
        logger.info(f"⏭️ REJETÉE - Pas de pays détecté: {titre[:50]}...")
        return 'skipped'
    
    # =========================================================================
    # ✅ ORGANISME
    # =========================================================================
    if not organisme:
        from offres.scraping.extraction_helpers import extract_organisme
        if url_source:
            try:
                import requests
                response = requests.get(url_source, timeout=30, verify=False)
                if response.status_code == 200:
                    from bs4 import BeautifulSoup
                    org_soup = BeautifulSoup(response.text, 'html.parser')
                    organisme = extract_organisme(org_soup, url_source, titre)
            except:
                pass
        
        if not organisme:
            from urllib.parse import urlparse
            try:
                organisme = urlparse(url_source or url_tdr).netloc.replace('www.', '')
            except:
                organisme = 'Inconnu'
    
    # =========================================================================
    # ✅ DOMAINE
    # =========================================================================
    domaine = data.get('domaine')
    if not domaine or domaine == 'Autres':
        from offres.utils.search_keywords import detecter_domaine
        domaine = detecter_domaine(titre, description) or 'Autres'
    
    # =========================================================================
    # ✅ VALIDATIONS FINALES
    # =========================================================================
    
    # Date pub ne peut pas être dans le futur
    if date_pub > timezone.now().date():
        date_pub = timezone.now().date()
    
    # Offre expirée (seulement si date_clot existe)
    if date_clot and date_clot < timezone.now().date():
        logger.info(f"⏭️ REJETÉE - Expirée: {titre[:50]}... (clôture: {date_clot})")
        return 'skipped'
    
    # Offre trop ancienne
    age_jours = (timezone.now().date() - date_pub).days
    if age_jours > 365:
        logger.info(f"⏭️ REJETÉE - Trop ancienne ({age_jours}j): {titre[:50]}...")
        return 'skipped'
    
    # =========================================================================
    # ✅ TÉLÉCHARGEMENT PDF
    # =========================================================================
    fichier_pdf = None
    pdf_trouve = False
    
    if url_source:
        try:
            import requests
            response = requests.get(url_source, timeout=30, verify=False)
            if response.status_code == 200:
                from bs4 import BeautifulSoup
                detail_soup = BeautifulSoup(response.text, 'html.parser')
                from offres.scraping.extraction_helpers import extract_pdf_url
                pdf_url = extract_pdf_url(detail_soup, url_source)
                
                if pdf_url:
                    # ✅ Vérifier que c'est un vrai PDF
                    pdf_response = requests.get(pdf_url, timeout=30, verify=False, headers={'User-Agent': 'Mozilla/5.0'})
                    if pdf_response.status_code == 200 and pdf_response.content.startswith(b'%PDF'):
                        pdf_content = fetch_and_validate_pdf(pdf_url, titre)
                        if pdf_content:
                            import uuid, re
                            safe_title = re.sub(r'[^a-zA-Z0-9]', '_', titre[:30])
                            filename = f"tdr_{safe_title}_{uuid.uuid4().hex[:8]}.pdf"
                            fichier_pdf = ContentFile(pdf_content, name=filename)
                            url_tdr = pdf_url
                            pdf_trouve = True
                            logger.info(f"📄 PDF téléchargé: {filename}")
                    else:
                        logger.warning(f"⚠️ Lien PDF invalide (retourne du HTML): {pdf_url[:60]}")
        except Exception as e:
            logger.debug(f"⚠️ Erreur PDF: {e}")
    
    # ✅ SI PAS DE PDF → url_tdr = url_source (lien de redirection)
    if not pdf_trouve:
        url_tdr = url_source
        logger.info(f"🔗 Pas de PDF → url_tdr = url_source: {url_tdr[:60]}")
    
    # =========================================================================
    # ✅ SAUVEGARDE
    # =========================================================================
    try:
        offre = AppelOffre.objects.create(
            titre=titre[:300],
            organisme=organisme[:200],
            description=description[:2000],
            pays=pays,
            domaine=domaine,
            date_publication=date_pub,
            date_cloture=date_clot,  # ✅ Peut être None
            url_source=url_source,
            url_tdr=url_tdr,  # ✅ url_source si pas de PDF
            statut='Ouvert',
            mode_acquisition='AUTO',
            source_origine=source,
            fichier_pdf=fichier_pdf,
        )
        
        cloture_info = f"Clôture: {date_clot}" if date_clot else "Clôture: None (vide)"
        logger.info(f"✅ CRÉÉE: {titre[:40]}... | {pays} | {domaine} | {cloture_info}")
        return 'created'
    except Exception as e:
        logger.error(f"❌ Erreur création BDD: {e}")
        return 'skipped'


@shared_task
def daily_archive_task():
    """Tâche quotidienne unifiée : Archive et purge les offres expirées"""
    logger.info("🗑️ Lancement du cycle de vie des offres (Archivage + Purge)...")
    try:
        # 1. Marquer les offres expirées
        marked = mark_expired_offres()
        logger.info(f"📅 {marked} offres marquées comme expirées")
        
        # 2. Supprimer les offres expirées depuis 7 jours
        from datetime import timedelta
        cutoff_date = timezone.now().date() - timedelta(days=7)
        expired_to_delete = AppelOffre.objects.filter(
            statut='Expiré',
            date_cloture__lt=cutoff_date
        )
        deleted_permanent = expired_to_delete.count()
        
        if deleted_permanent > 0:
            for offre in expired_to_delete:
                if offre.fichier_pdf:
                    try:
                        offre.fichier_pdf.delete(save=False)
                    except:
                        pass
                offre.delete()
            logger.info(f"🗑️ {deleted_permanent} offres supprimées définitivement")
        
        # 3. Archive via la fonction existante
        archived, deleted = archive_and_delete_old_offres(days_to_keep=30)
        
        return {
            "status": "success",
            "marked_as_expired": marked,
            "archived_count": archived,
            "deleted_count": deleted,
            "deleted_permanent": deleted_permanent
        }
    except Exception as e:
        logger.error(f"❌ Erreur dans le cycle de vie : {e}")
        return {
            "status": "error", 
            "marked_as_expired": 0, 
            "archived_count": 0, 
            "deleted_count": 0,
            "deleted_permanent": 0,
            "error": str(e)
        }

@shared_task(bind=True, max_retries=2, default_retry_delay=60)
def daily_alert_matching_task(self):
    """Matching intelligent offres ↔ critères experts avec notifications"""
    try:
        logger.info("🔔 Matching intelligent offres ↔ critères experts...")
        
        # 1. Matching classique
        count_classique = check_and_notify_matches()
        logger.info(f"📧 {count_classique} experts notifiés (classique)")
        
        # 2. ✅ NOUVEAU : Matching intelligent par domaine
        from offres.services.smart_matching import notifier_tous_les_experts
        resultats = notifier_tous_les_experts()
        
        logger.info(f"🎯 Matching intelligent:")
        logger.info(f"   • Experts analysés: {resultats['total_experts']}")
        logger.info(f"   • Experts notifiés: {resultats['experts_notifies']}")
        logger.info(f"   • Notifications créées: {resultats['total_notifications']}")
        
        return {
            "notified_classique": count_classique,
            "experts_analyses": resultats['total_experts'],
            "experts_notifies": resultats['experts_notifies'],
            "notifications_creees": resultats['total_notifications']
        }
    except Exception as e:
        logger.error(f"❌ Erreur matching intelligent: {e}")
        if self.request.retries < self.max_retries:
            raise self.retry(exc=e)
        return {"notified": 0, "error": str(e)}


# Dans offres/tasks.py
@shared_task
def daily_maintenance():
    """Maintenance quotidienne : scraping + vérification + nettoyage"""
    results = {}
    
    # 1. Scraping
    results['scraping'] = run_scheduled_scraping_task()
    
    # 2. Marquer les offres expirées
    results['expired'] = mark_expired_offres()
    
    # 3. Vérifier les pays
    results['countries_ok'] = verifier_pays()
    
    # 4. Supprimer les offres expirées depuis 7 jours
    results['deleted'] = delete_expired_offres()
    
    return results




@shared_task
def newsletter_hebdomadaire_task():
    """
    Envoie un récapitulatif hebdomadaire des nouvelles offres aux abonnés newsletter
    """
    # Offres des 7 derniers jours
    sept_jours = timezone.now() - timedelta(days=7)
    nouvelles_offres = AppelOffre.objects.filter(
        date_publication__gte=sept_jours,
        statut='Ouvert',
        type_offre='APPEL_D_OFFRES'
    ).order_by('-date_publication')[:20]  # Top 20
    
    if not nouvelles_offres.exists():
        logger.info("Aucune offre pour la newsletter cette semaine")
        return 0
    
    abonnes = InscriptionNewsletter.objects.filter(est_actif=True)
    
    total_envois = 0
    for abonne in abonnes:
        try:
            EmailService.send_newsletter_hebdomadaire(
                email=abonne.email,
                nom=abonne.nom or abonne.email,
                offres=nouvelles_offres
            )
            total_envois += 1
        except Exception as e:
            logger.error(f"❌ Erreur newsletter pour {abonne.email}: {e}")
    
    logger.info(f"✅ Newsletter envoyée à {total_envois} abonnés ({nouvelles_offres.count()} offres)")
    return total_envois