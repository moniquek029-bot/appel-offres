"""
offres/scraping/parsers/j360_mock.py
Parser Mock enrichi : Génère des descriptions longues et détaillées 
pour simuler un scraping complet et réduire le besoin de redirection.
"""

import logging
from datetime import date, timedelta
from ..base import BaseScraper
from ..utils import clean_text

logger = logging.getLogger(__name__)

class J360MockParser(BaseScraper):
    """Génère 5 offres avec descriptions riches pour la démo."""
    
    def parse(self, soup=None):
        # Données mockées avec descriptions détaillées (Aperçu enrichi)
        mock_offers = [
            {
                "titre": "Recrutement de Consultant pour étude hydraulique - Région des Hauts-Bassins",
                "organisme": "Ministère de l'Agriculture et de l'Aménagement Hydraulique",
                "description": "Le Ministère lance un appel d'offres ouvert pour le recrutement d'un cabinet spécialisé en hydraulique agricole.\n\nOBJECTIFS DE LA MISSION :\n1. Réaliser une étude technique approfondie sur l'extension du périmètre irrigué de la zone Sud.\n2. Évaluer les impacts environnementaux et sociaux du projet sur les communautés locales.\n3. Proposer un plan de gestion durable des ressources en eau pour les 10 prochaines années.\n\nDURÉE : La mission est estimée à 6 mois à compter de la signature du contrat.\nLIEU D'EXÉCUTION : Bobo-Dioulasso et environs.",
                "date_publication": date.today() - timedelta(days=3),
                "date_cloture": date.today() + timedelta(days=20),
                "url_tdr": "https://app.j360.info/#/tender/demo-hydraulique",
                "pays": "BF",
            },
            {
                "titre": "Acquisition de Support technique des produits ORACLE installé à la CNSS",
                "organisme": "Caisse Nationale de Sécurité Sociale (CNSS)",
                "description": "La CNSS sollicite des offres pour la fourniture de services de support technique et de maintenance évolutive pour ses bases de données Oracle critiques.\n\nPÉRIMÈTRE DU SERVICE :\n- Support Niveau 2 et 3 pour les bases de données en production (24h/24, 7j/7).\n- Installation des mises à jour de sécurité (Patchs) trimestrielles.\n- Optimisation des performances et tuning des requêtes SQL complexes.\n- Formation de 5 administrateurs internes aux nouvelles fonctionnalités de la version 19c.\n\nCRITÈRES D'ÉVALUATION : Expérience technique (40%), Méthodologie (30%), Coût (30%).",
                "date_publication": date.today() - timedelta(days=2),
                "date_cloture": date.today() + timedelta(days=25),
                "url_tdr": "https://app.j360.info/#/tender/demo-oracle-cnss",
                "pays": "BF",
            },
            {
                "titre": "Travaux de réhabilitation de la route Bobo-Dioulasso - Banfora (45 km)",
                "organisme": "Ministère des Infrastructures et du Désenclavement",
                "description": "Appel d'offres national ouvert pour les travaux de réhabilitation de la route reliant Bobo-Dioulasso à Banfora.\n\nNATURE DES TRAVAUX :\n- Terrassement et reprofilage de la chaussée existante sur 45 km.\n- Fourniture et mise en œuvre de couches de roulement en béton bitumineux.\n- Construction de dalots et buses pour le drainage des eaux pluviales.\n- Signalisation horizontale et verticale conforme aux normes OHADA.\n\nGARANTIE : L'entrepreneur devra assurer l'entretien de la route pendant une période de 12 mois après la réception provisoire.",
                "date_publication": date.today() - timedelta(days=5),
                "date_cloture": date.today() + timedelta(days=30),
                "url_tdr": "https://app.j360.info/#/tender/demo-route-bobo",
                "pays": "BF",
            },
            {
                "titre": "Fourniture de matériel informatique pour 30 écoles primaires",
                "organisme": "Ministère de l'Éducation Nationale",
                "description": "Dans le cadre du programme 'École Numérique', le Ministère souhaite équiper 30 écoles primaires situées en zone rurale.\n\nLOT 1 : MATÉRIEL HARDWARE\n- 300 ordinateurs portables (i5, 8Go RAM, SSD 256Go).\n- 30 vidéoprojecteurs interactifs.\n- 150 onduleurs pour la protection du matériel.\n\nLOT 2 : LOGICIELS ET SERVICES\n- Licences bureautiques pour 3 ans.\n- Installation, configuration et mise en réseau local.\n- Formation des enseignants à l'utilisation pédagogique des outils numériques.\n\nLIVRAISON : Les équipements doivent être livrés et installés sous 60 jours.",
                "date_publication": date.today() - timedelta(days=1),
                "date_cloture": date.today() + timedelta(days=15),
                "url_tdr": "https://app.j360.info/#/tender/demo-ecoles-informatique",
                "pays": "BF",
            },
            {
                "titre": "Prestation de services : Audit financier d'une institution publique",
                "organisme": "Autorité Supérieure de Contrôle d'État (ASCE)",
                "description": "L'ASCE recrute un cabinet d'audit pour la vérification des comptes de l'exercice 2025.\n\nMISSIONS SPÉCIFIQUES :\n- Audit de régularité et de sincérité des états financiers.\n- Contrôle de la conformité des dépenses avec les lois de finances.\n- Évaluation du système de contrôle interne et recommandations d'amélioration.\n- Rédaction du rapport général d'audit avec avis certifié.\n\nQUALIFICATIONS REQUISES : Le cabinet doit justifier d'au moins 5 missions similaires dans le secteur public au cours des 3 dernières années.",
                "date_publication": date.today() - timedelta(days=7),
                "date_cloture": date.today() + timedelta(days=10),
                "url_tdr": "https://app.j360.info/#/tender/demo-audit-asce",
                "pays": "BF",
            },
        ]
        
        logger.info(f"✅ {len(mock_offers)} offre(s) générées (Mode Aperçu Enrichi)")
        return mock_offers
    
    def run(self):
        logger.info(f"🕷️ Lancement du parser mock enrichi pour {self.source_url}")
        return self.parse()