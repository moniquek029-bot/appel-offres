# offres/scraping/sources_config.py
"""
Sources actives - Configuration des sites cibles pour le scraping réel
"""

ACTIVE_SOURCES = [
    {
        'nom': 'UNFPA Burkina',
        'url': 'https://burkinafaso.unfpa.org/fr/call-for-submissions',
        'parser': 'unfpa',
        'pays': 'BF',
        'est_actif': True,
        'require_pdf': False,
    },
    {
        'nom': 'AGETIB',
        'url': 'https://www.agetib.net/avis-de-marches',  # 🎯 CORRIGÉ (Évite la 404)
        'parser': 'agetib',
        'pays': 'BF',
        'est_actif': True,
        'require_pdf': False,
    },
    {
        'nom': 'SONABEL',
        'url': 'http://www.sonabel.bf/index.php/marches-publics',
        'parser': 'sonabel',
        'pays': 'BF',
        'est_actif': True,
        'require_pdf': False,
    },
    {
        'nom': 'UEMOA',
        'url': 'https://www.uemoa.int/fr/appel-d-offre',
        'parser': 'uemoa',
        'pays': 'BF',
        'est_actif': True,
        'require_pdf': False,
    },
    {
        'nom': 'JOFFRES',
        'url': 'https://www.joffres.net/burkina-faso',
        'parser': 'joffres', # 🎯 Sera géré par ton JoffresParser ou SmartParser
        'pays': 'BF',
        'est_actif': True,
        'require_pdf': False,
    },
]