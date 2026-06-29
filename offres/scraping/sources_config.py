# offres/scraping/sources_config.py
"""
Sources actives - URLs corrigées et testées
"""

ACTIVE_SOURCES = [
    # =========================================================================
    # ✅ SOURCES ACTIVES
    # =========================================================================
    {
        'nom': 'UNFPA Burkina Faso',
        'url': 'https://burkinafaso.unfpa.org/fr/submissions',  # ✅ URL corrigée
        'parser': 'unfpa',
        'pays': 'BF',
        'est_actif': True,
        'use_js': False,
        'delay': 2,
    },
    {
        'nom': 'UNDP Procurement',
        'url': 'https://procurement-notices.undp.org/',
        'parser': 'undp',
        'pays': 'GLOBAL',
        'est_actif': True,
        'use_js': False,
        'delay': 2,
    },
    
    # =========================================================================
    # ❌ SOURCES DÉSACTIVÉES (ne fonctionnent pas)
    # =========================================================================
    {
        'nom': 'Joffres.net',
        'url': 'https://www.joffres.net/burkina-faso',
        'parser': 'smart',
        'pays': 'BF',
        'est_actif': False,
        'use_js': False,
        'delay': 2,
    },
    {
        'nom': 'SONABEL Burkina',
        'url': 'http://www.sonabel.bf/index.php/marches-publics',
        'parser': 'smart',
        'pays': 'BF',
        'est_actif': False,
        'use_js': False,
        'delay': 2,
    },
    {
        'nom': 'UEMOA Appels d\'offres',
        'url': 'https://www.uemoa.int/fr/appel-d-offre',
        'parser': 'smart',
        'pays': 'BF',
        'est_actif': False,
        'use_js': False,
        'delay': 2,
    },
    {
        'nom': 'UNICEF',
        'url': 'https://www.unicef.org/supply/index_76578.html',
        'parser': 'smart',
        'pays': 'GLOBAL',
        'est_actif': False,
        'use_js': False,
        'delay': 2,
    },
    {
        'nom': 'PNUD Burkina',
        'url': 'https://burkinafaso.undp.org/content/burkinafaso/fr/home/operations.html',
        'parser': 'smart',
        'pays': 'BF',
        'est_actif': False,
        'use_js': False,
        'delay': 2,
    },
    {
        'nom': 'ARMP Burkina',
        'url': 'http://www.armp.bf/',
        'parser': 'smart',
        'pays': 'BF',
        'est_actif': False,
        'use_js': False,
        'delay': 2,
    },
    {
        'nom': 'Marchés publics Sénégal',
        'url': 'https://www.marchespublics.sn/',
        'parser': 'smart',
        'pays': 'SN',
        'est_actif': False,
        'use_js': False,
        'delay': 2,
    },
    {
        'nom': 'BAD',
        'url': 'https://www.afdb.org/fr/projects-and-operations/procurement',
        'parser': 'smart',
        'pays': 'GLOBAL',
        'est_actif': False,
        'use_js': False,
        'delay': 2,
    },
    {
        'nom': 'ABF Burkina Faso',
        'url': 'https://www.abfburkina.org/appels-a-projets/',
        'parser': 'smart',
        'pays': 'BF',
        'est_actif': False,
        'use_js': False,
        'delay': 2,
    },
]