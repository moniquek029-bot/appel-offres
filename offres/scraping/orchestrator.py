# offres/scraping/orchestrator.py
"""
Orchestrateur de scraping
Gère toutes les sources : fixes (ACTIVE_SOURCES) + dynamiques (admin)
"""
import logging
from typing import Optional

from offres.scraping.sources_config import ACTIVE_SOURCES
from offres.scraping.parsers.undp_parser import UNDPParser
from offres.scraping.parsers.unfpa_parser import UNFPAParser
from offres.scraping.parsers.agetib_parser import AGETIBParser
from offres.scraping.parsers.sonabel_parser import SONABELParser
from offres.scraping.parsers.uemoa_parser import UEMOAParser
from offres.scraping.parsers.joffres_parser import JOFFRESParser
from offres.scraping.parsers.smart_parser import SmartParser
from offres.scraping.extraction_helpers import is_offer_expired

logger = logging.getLogger(__name__)


# Mapping des parsers disponibles
PARSER_REGISTRY = {
    'undp': UNDPParser,
    'unfpa': UNFPAParser,
    'agetib': AGETIBParser,
    'sonabel': SONABELParser,
    'uemoa': UEMOAParser,
    'joffres': JOFFRESParser,
    'smart': SmartParser,
}


class ScrapingOrchestrator:
    """Orchestre le scraping de toutes les sources"""
    
    def __init__(self):
        self.sources = self._load_all_sources()
    
    def _load_all_sources(self) -> list:
        """
        Charge toutes les sources :
        1. Sources fixes (ACTIVE_SOURCES)
        2. Sources dynamiques (modèle SourceScraping en base)
        """
        sources = list(ACTIVE_SOURCES)
        
        # Charger les sources depuis la base de données (admin)
        try:
            from offres.models import SourceScraping
            for source_db in SourceScraping.objects.filter(est_actif=True):
                # Éviter les doublons avec les sources fixes
                if not any(s['url'] == source_db.url for s in sources):
                    sources.append({
                        'nom': source_db.nom,
                        'url': source_db.url,
                        'parser': source_db.parser or self._auto_detect_parser(source_db.url),
                        'pays': source_db.pays or 'BF',
                        'est_actif': True,
                        'require_pdf': False,
                        'use_js': source_db.use_js if hasattr(source_db, 'use_js') else False,
                        'delay': source_db.delay if hasattr(source_db, 'delay') else 2,
                    })
                    logger.info(f"📥 Source dynamique chargée : {source_db.nom}")
        except Exception as e:
            logger.warning(f"⚠️ Impossible de charger les sources dynamiques : {e}")
        
        return sources
    
    def _auto_detect_parser(self, url: str) -> str:
        """Détecte automatiquement le parser à utiliser selon l'URL"""
        url_lower = url.lower()
        
        if 'undp.org' in url_lower:
            return 'undp'
        elif 'unfpa.org' in url_lower:
            return 'unfpa'
        elif 'agetib.net' in url_lower:
            return 'agetib'
        elif 'sonabel.bf' in url_lower:
            return 'sonabel'
        elif 'uemoa.int' in url_lower:
            return 'uemoa'
        elif 'joffres.net' in url_lower:
            return 'joffres'
        else:
            return 'smart'  # Parser générique par défaut
    
    def _get_parser_class(self, parser_name: str):
        """Récupère la classe du parser"""
        return PARSER_REGISTRY.get(parser_name, SmartParser)
    
    def run_all_sources(self, source_name: Optional[str] = None) -> dict:
        """
        Lance le scraping de toutes les sources (ou une seule si source_name spécifié)
        Retourne un dict {source_name: {'offres': [...], 'expired_rejected': int}}
        """
        results = {}
        
        sources_to_run = self.sources
        if source_name:
            sources_to_run = [s for s in self.sources if source_name.lower() in s['nom'].lower()]
            if not sources_to_run:
                logger.warning(f"⚠️ Source '{source_name}' non trouvée")
                return results
        
        for source in sources_to_run:
            if not source.get('est_actif', True):
                logger.info(f"⏭️ Source inactive : {source['nom']}")
                continue
            
            result = self._run_single_source(source)
            results[source['nom']] = result
        
        return results
    
    def _run_single_source(self, source: dict) -> dict:
        """Lance le scraping d'une seule source"""
        source_name = source['nom']
        parser_name = source.get('parser', 'smart')
        
        logger.info(f"\n{'='*70}")
        logger.info(f"🌐 SOURCE : {source_name}")
        logger.info(f"🔧 Parser : {parser_name}")
        logger.info(f"🔗 URL : {source['url']}")
        logger.info(f"{'='*70}")
        
        try:
            # Récupérer la classe du parser
            parser_class = self._get_parser_class(parser_name)
            
            # Instancier le parser avec les paramètres de la source
            parser = parser_class(
                source_url=source['url'],
                pays_defaut=source.get('pays', 'BF'),
                use_js=source.get('use_js', False),
                delay_seconds=source.get('delay', 2),
            )
            
            # Lancer le scraping
            offres = parser.run()
            
            # ✅ FILTRAGE FINAL : rejet des offres expirées
            offres_valides = []
            expired_rejected = 0
            
            for offre in offres:
                if is_offer_expired(offre.get('date_cloture')):
                    expired_rejected += 1
                    logger.info(f"   ⏭️ EXPIRÉE rejetée : {offre.get('titre', '')[:50]}...")
                else:
                    offres_valides.append(offre)
            
            # Sauvegarder en base
            saved_count = self._save_offres(offres_valides, source_name)
            
            logger.info(f"✅ {source_name} : {saved_count} offres sauvegardées ({expired_rejected} expirées rejetées)")
            
            return {
                'offres': offres_valides,
                'saved': saved_count,
                'expired_rejected': expired_rejected,
            }
            
        except Exception as e:
            logger.error(f"❌ Erreur sur {source_name} : {e}")
            import traceback
            logger.error(traceback.format_exc())
            return {'offres': [], 'saved': 0, 'expired_rejected': 0}
    
    def _save_offres(self, offres: list, source_name: str) -> int:
        """Sauvegarde les offres en base (évite les doublons)"""
        from offres.models import AppelOffre
        
        saved = 0
        for offre in offres:
            try:
                # Vérifier si l'offre existe déjà (par url_source)
                url_source = offre.get('url_source')
                if not url_source:
                    continue
                
                if AppelOffre.objects.filter(url_source=url_source).exists():
                    logger.debug(f"   ⏭️ Doublon ignoré : {url_source[:60]}...")
                    continue
                
                # Créer l'offre
                AppelOffre.objects.create(
                    titre=offre.get('titre', '')[:300],
                    organisme=offre.get('organisme', '')[:200],
                    description=offre.get('description', ''),
                    date_publication=offre.get('date_publication'),
                    date_cloture=offre.get('date_cloture'),
                    url_source=url_source[:500],
                    url_tdr=(offre.get('url_tdr') or '')[:500] or None,
                    pays=offre.get('pays', 'BF'),
                    domaine=offre.get('domaine', 'Autres'),
                    statut=offre.get('statut', 'Ouvert'),
                    mode_acquisition=offre.get('mode_acquisition', 'AUTO'),
                )
                saved += 1
                logger.info(f"   💾 Sauvegardée : {offre.get('titre', '')[:50]}...")
                
            except Exception as e:
                logger.warning(f"   ⚠️ Erreur sauvegarde : {e}")
        
        return saved# offres/scraping/orchestrator.py
"""
Orchestrateur de scraping
Gère toutes les sources : fixes (ACTIVE_SOURCES) + dynamiques (admin)
"""
import logging
from typing import Optional

from offres.scraping.sources_config import ACTIVE_SOURCES
from offres.scraping.parsers.undp_parser import UNDPParser
from offres.scraping.parsers.unfpa_parser import UNFPAParser
from offres.scraping.parsers.agetib_parser import AGETIBParser
from offres.scraping.parsers.sonabel_parser import SONABELParser
from offres.scraping.parsers.uemoa_parser import UEMOAParser
from offres.scraping.parsers.joffres_parser import JOFFRESParser
from offres.scraping.parsers.smart_parser import SmartParser
from offres.scraping.extraction_helpers import is_offer_expired

logger = logging.getLogger(__name__)


# Mapping des parsers disponibles
PARSER_REGISTRY = {
    'undp': UNDPParser,
    'unfpa': UNFPAParser,
    'agetib': AGETIBParser,
    'sonabel': SONABELParser,
    'uemoa': UEMOAParser,
    'joffres': JOFFRESParser,
    'smart': SmartParser,
}


class ScrapingOrchestrator:
    """Orchestre le scraping de toutes les sources"""
    
    def __init__(self):
        self.sources = self._load_all_sources()
    
    def _load_all_sources(self) -> list:
        """
        Charge toutes les sources :
        1. Sources fixes (ACTIVE_SOURCES)
        2. Sources dynamiques (modèle SourceScraping en base)
        """
        sources = list(ACTIVE_SOURCES)
        
        # Charger les sources depuis la base de données (admin)
        try:
            from offres.models import SourceScraping
            for source_db in SourceScraping.objects.filter(est_actif=True):
                # ✅ Utiliser url_racine au lieu de url
                url = source_db.url_racine
                
                # Éviter les doublons avec les sources fixes
                if not any(s['url'] == url for s in sources):
                    sources.append({
                        'nom': source_db.nom,
                        'url': url,  # ✅ url_racine mappé vers url
                        'parser': source_db.parser or self._auto_detect_parser(url),
                        'pays': source_db.pays or 'BF',
                        'est_actif': True,
                        'require_pdf': False,
                        'use_js': source_db.use_js,
                        'delay': source_db.delay,
                    })
                    logger.info(f"📥 Source dynamique chargée : {source_db.nom} ({url})")
        except Exception as e:
            logger.warning(f"⚠️ Impossible de charger les sources dynamiques : {e}")
        
        return sources
    
    def _auto_detect_parser(self, url: str) -> str:
        """Détecte automatiquement le parser à utiliser selon l'URL"""
        url_lower = url.lower()
        
        if 'undp.org' in url_lower:
            return 'undp'
        elif 'unfpa.org' in url_lower:
            return 'unfpa'
        elif 'agetib.net' in url_lower:
            return 'agetib'
        elif 'sonabel.bf' in url_lower:
            return 'sonabel'
        elif 'uemoa.int' in url_lower:
            return 'uemoa'
        elif 'joffres.net' in url_lower:
            return 'joffres'
        else:
            return 'smart'  # Parser générique par défaut
    
    def _get_parser_class(self, parser_name: str):
        """Récupère la classe du parser"""
        return PARSER_REGISTRY.get(parser_name, SmartParser)
    
    def run_all_sources(self, source_name: Optional[str] = None) -> dict:
        """
        Lance le scraping de toutes les sources (ou une seule si source_name spécifié)
        Retourne un dict {source_name: {'offres': [...], 'expired_rejected': int}}
        """
        results = {}
        
        sources_to_run = self.sources
        if source_name:
            sources_to_run = [s for s in self.sources if source_name.lower() in s['nom'].lower()]
            if not sources_to_run:
                logger.warning(f"⚠️ Source '{source_name}' non trouvée")
                return results
        
        for source in sources_to_run:
            if not source.get('est_actif', True):
                logger.info(f"⏭️ Source inactive : {source['nom']}")
                continue
            
            result = self._run_single_source(source)
            results[source['nom']] = result
        
        return results
    
    def _run_single_source(self, source: dict) -> dict:
        """Lance le scraping d'une seule source"""
        source_name = source['nom']
        parser_name = source.get('parser', 'smart')
        
        logger.info(f"\n{'='*70}")
        logger.info(f"🌐 SOURCE : {source_name}")
        logger.info(f"🔧 Parser : {parser_name}")
        logger.info(f"🔗 URL : {source['url']}")
        logger.info(f"{'='*70}")
        
        try:
            # Récupérer la classe du parser
            parser_class = self._get_parser_class(parser_name)
            
            # Instancier le parser avec les paramètres de la source
            parser = parser_class(
                source_url=source['url'],
                pays_defaut=source.get('pays', 'BF'),
                use_js=source.get('use_js', False),
                delay_seconds=source.get('delay', 2),
            )
            
            # Lancer le scraping
            offres = parser.run()
            
            # ✅ FILTRAGE FINAL : rejet des offres expirées
            offres_valides = []
            expired_rejected = 0
            
            for offre in offres:
                if is_offer_expired(offre.get('date_cloture')):
                    expired_rejected += 1
                    logger.info(f"   ⏭️ EXPIRÉE rejetée : {offre.get('titre', '')[:50]}...")
                else:
                    offres_valides.append(offre)
            
            # Sauvegarder en base
            saved_count = self._save_offres(offres_valides, source_name)
            
            # ✅ Mettre à jour last_scraped
            self._update_last_scraped(source_name)
            
            logger.info(f"✅ {source_name} : {saved_count} offres sauvegardées ({expired_rejected} expirées rejetées)")
            
            return {
                'offres': offres_valides,
                'saved': saved_count,
                'expired_rejected': expired_rejected,
            }
            
        except Exception as e:
            logger.error(f"❌ Erreur sur {source_name} : {e}")
            import traceback
            logger.error(traceback.format_exc())
            return {'offres': [], 'saved': 0, 'expired_rejected': 0}
    
    def _save_offres(self, offres: list, source_name: str) -> int:
        """Sauvegarde les offres en base (évite les doublons)"""
        from offres.models import AppelOffre, SourceScraping
        
        saved = 0
        
        # Récupérer la source pour le lien
        source_obj = None
        try:
            source_obj = SourceScraping.objects.get(nom=source_name)
        except SourceScraping.DoesNotExist:
            pass
        
        for offre in offres:
            try:
                # Vérifier si l'offre existe déjà (par url_source)
                url_source = offre.get('url_source')
                if not url_source:
                    continue
                
                if AppelOffre.objects.filter(url_source=url_source).exists():
                    logger.debug(f"   ⏭️ Doublon ignoré : {url_source[:60]}...")
                    continue
                
                # Créer l'offre
                AppelOffre.objects.create(
                    titre=offre.get('titre', '')[:300],
                    organisme=offre.get('organisme', '')[:200],
                    description=offre.get('description', ''),
                    date_publication=offre.get('date_publication'),
                    date_cloture=offre.get('date_cloture'),
                    url_source=url_source[:500],
                    url_tdr=(offre.get('url_tdr') or '')[:500] or None,
                    pays=offre.get('pays', 'BF'),
                    domaine=offre.get('domaine', 'Autres'),
                    statut=offre.get('statut', 'Ouvert'),
                    mode_acquisition=offre.get('mode_acquisition', 'AUTO'),
                    source_origine=source_obj,  # ✅ Lien vers la source
                )
                saved += 1
                logger.info(f"   💾 Sauvegardée : {offre.get('titre', '')[:50]}...")
                
            except Exception as e:
                logger.warning(f"   ⚠️ Erreur sauvegarde : {e}")
        
        return saved
    
    def _update_last_scraped(self, source_name: str):
        """Met à jour la date du dernier scraping"""
        from offres.models import SourceScraping
        from django.utils import timezone
        
        try:
            source = SourceScraping.objects.get(nom=source_name)
            source.last_scraped = timezone.now()
            source.save(update_fields=['last_scraped'])
        except SourceScraping.DoesNotExist:
            pass