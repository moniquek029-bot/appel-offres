# offres/scraping/parsers/globaltenders_parser.py
"""
Parser GlobalTenders - DÉSACTIVÉ (trop complexe/non fiable)
"""
import logging
logger = logging.getLogger(__name__)

class GlobalTendersParser:
    """Parser désactivé - site trop complexe pour scraping fiable"""
    def __init__(self, *args, **kwargs):
        pass
    def run(self):
        logger.warning("⚠️ GlobalTendersParser désactivé - site non supporté")
        return []

# offres/scraping/parsers/j360_parser.py
"""
Parser J360 - DÉSACTIVÉ (SPA trop complexe)
"""
import logging
logger = logging.getLogger(__name__)

class J360Parser:
    """Parser désactivé - site SPA non supporté"""
    def __init__(self, *args, **kwargs):
        pass
    def run(self):
        logger.warning("⚠️ J360Parser désactivé - site SPA non supporté")
        return []