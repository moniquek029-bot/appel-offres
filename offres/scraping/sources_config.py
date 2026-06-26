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
        'use_js': False,
        'delay': 0,
    },
    {
        'nom': 'AGETIB',
        'url': 'https://www.agetib.net/avis-de-marches',
        'parser': 'agetib',
        'pays': 'BF',
        'est_actif': True,
        'require_pdf': False,
        'use_js': False,
        'delay': 0,
    },
    {
        'nom': 'SONABEL',
        'url': 'http://www.sonabel.bf/index.php/marches-publics',
        'parser': 'sonabel',
        'pays': 'BF',
        'est_actif': True,
        'require_pdf': False,
        'use_js': False,
        'delay': 0,
    },
    {
        'nom': 'UEMOA',
        'url': 'https://www.uemoa.int/fr/appel-d-offre',
        'parser': 'uemoa',
        'pays': 'BF',
        'est_actif': True,
        'require_pdf': False,
        'use_js': False,
        'delay': 0,
    },
    {
        'nom': 'JOFFRES',
        'url': 'https://www.joffres.net/burkina-faso',
        'parser': 'joffres',
        'pays': 'BF',
        'est_actif': True,
        'require_pdf': False,
        'use_js': False,
        'delay': 0,
    },
    
    # 🌍 NOUVELLES SOURCES INTERNATIONALES (Intégrées proprement)
    {
        'nom': 'OMS (WHO) Careers',
        'url': 'https://www.who.int/careers/vacancies',
        'parser': 'smart',           # Appelle ton SmartParser V2
        'pays': 'GLOBAL',
        'est_actif': True,
        'require_pdf': False,
        'use_js': True,              # Active le moteur JS (Playwright/Selenium)
        'delay': 3,
    },
    {
        'nom': 'World Bank Jobs',
        'url': 'https://www.worldbank.org/en/about/jobs',
        'parser': 'smart',
        'pays': 'US',
        'est_actif': True,
        'require_pdf': False,
        'use_js': True,
        'delay': 4,
    },
    {
        'nom': 'UN Careers (Inspira)',
        'url': 'https://careers.un.org/lbw/home.aspx',
        'parser': 'smart',
        'pays': 'GLOBAL',
        'est_actif': True,
        'require_pdf': False,
        'use_js': True,
        'delay': 5,
    }
]