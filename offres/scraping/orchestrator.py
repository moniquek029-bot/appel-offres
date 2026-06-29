# offres/scraping/orchestrator.py
import logging
from typing import Optional

from offres.scraping.sources_config import ACTIVE_SOURCES
from offres.scraping.parsers.undp_parser import UNDPParser
from offres.scraping.parsers.smart_parser import SmartParser
from offres.scraping.extraction_helpers import is_offer_expired

logger = logging.getLogger(__name__)

PARSER_REGISTRY = {
    'undp': UNDPParser,
    'smart': SmartParser,
}


class ScrapingOrchestrator:
    """Orchestre le scraping de toutes les sources"""
    
    def __init__(self):
        self.sources = self._load_all_sources()
    
    def _load_all_sources(self) -> list:
        """Charge toutes les sources (fixes + dynamiques)"""
        sources = list(ACTIVE_SOURCES)
        
        try:
            from offres.models import SourceScraping
            for source_db in SourceScraping.objects.filter(est_actif=True):
                url = source_db.url_racine
                if not any(s['url'] == url for s in sources):
                    sources.append({
                        'nom': source_db.nom,
                        'url': url,
                        'parser': source_db.parser or self._auto_detect_parser(url),
                        'pays': source_db.pays or 'BF',
                        'est_actif': True,
                        'use_js': source_db.use_js,
                        'delay': source_db.delay,
                    })
                    logger.info(f"📥 Source dynamique chargée : {source_db.nom}")
        except Exception as e:
            logger.warning(f"⚠️ Impossible de charger les sources dynamiques : {e}")
        
        return sources
    
    def _auto_detect_parser(self, url: str) -> str:
        """Détecte automatiquement le parser"""
        url_lower = url.lower()
        if 'undp.org' in url_lower:
            return 'undp'
        return 'smart'
    
    def run_all_sources(self, source_name: Optional[str] = None) -> dict:
        """Lance le scraping de toutes les sources"""
        results = {}
        
        sources_to_run = self.sources
        if source_name:
            sources_to_run = [s for s in self.sources if source_name.lower() in s['nom'].lower()]
        
        for source in sources_to_run:
            if not source.get('est_actif', True):
                continue
            
            result = self._run_single_source(source)
            results[source['nom']] = result
        
        return results
    
    # Dans orchestrator.py, méthode _run_single_source
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
            parser_class = PARSER_REGISTRY.get(parser_name, SmartParser)
        
            # ✅ CORRECTION : Gérer les paramètres SSL
            parser_kwargs = {
                'source_url': source['url'],
                'pays_defaut': source.get('pays', 'BF'),
                'use_js': source.get('use_js', False),
                'delay_seconds': source.get('delay', 2),
            }
        
            # ✅ Désactiver SSL pour les sites problématiques
            if 'uemoa.int' in source['url'].lower():
                parser_kwargs['verify_ssl'] = False
        
            parser = parser_class(**parser_kwargs)
        
            offres = parser.run()
        
            # ✅ FILTRAGE FINAL
            offres_valides = []
            expired_rejected = 0
        
            for offre in offres:
                if is_offer_expired(offre.get('date_cloture')):
                    expired_rejected += 1
                else:
                    offres_valides.append(offre)
        
            saved_count = self._save_offres(offres_valides, source_name)
        
            logger.info(f"✅ {source_name} : {saved_count} sauvegardées ({expired_rejected} expirées)")
        
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
        """Sauvegarde les offres en base"""
        from offres.models import AppelOffre, SourceScraping
        
        saved = 0
        source_obj = None
        
        try:
            source_obj = SourceScraping.objects.get(nom=source_name)
        except SourceScraping.DoesNotExist:
            pass
        
        for offre in offres:
            try:
                url_source = offre.get('url_source')
                if not url_source:
                    continue
                
                if AppelOffre.objects.filter(url_source=url_source).exists():
                    continue
                
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
                    source_origine=source_obj,
                )
                saved += 1
                logger.info(f"   💾 {offre.get('titre', '')[:50]}...")
                
            except Exception as e:
                logger.warning(f"   ⚠️ Erreur sauvegarde : {e}")
        
        return saved