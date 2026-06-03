# offres/scraping/sources_config.py
"""
Sources actives - UNIQUEMENT les sites fonctionnels
"""

ACTIVE_SOURCES = [
    {
        'nom': 'UNFPA Burkina',
        'url': 'https://burkinafaso.unfpa.org/fr/call-for-submissions',
        'parser': 'unfpa',
        'pays': 'BF',
        'est_actif': True,
        'require_pdf': True,
    },
    {
        'nom': 'AGETIB',
        'url': 'https://www.agetib.net/appels-offres',
        'parser': 'agetib',
        'pays': 'BF',
        'est_actif': True,
        'require_pdf': True,
    },
    {
        'nom': 'SONABEL',
        'url': 'http://www.sonabel.bf/index.php/marches-publics',
        'parser': 'sonabel',
        'pays': 'BF',
        'est_actif': True,
        'require_pdf': True,
    },
    {
        'nom': 'UEMOA',
        'url': 'https://www.uemoa.int/fr/appel-d-offre',
        'parser': 'uemoa',
        'pays': 'BF',
        'est_actif': True,
        'require_pdf': True,
    },
    {
        'nom': 'JOFFRES',
        'url': 'https://www.joffres.net/burkina-faso',
        'parser': 'joffres',
        'pays': 'BF',
        'est_actif': True,
        'require_pdf': True,
    },
]