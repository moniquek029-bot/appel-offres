# offres/utils/offer_validator.py
"""
Validateur pour identifier les VRAIS appels d'offres
Version corrigée - accepte DEMANDE DE PRODUCTION, ACHAT, ACQUISITION
"""
import re
import logging

logger = logging.getLogger(__name__)


# =============================================================================
# MOTS-CLÉS QUI INDENTIFIENT UN VRAI APPEL D'OFFRES
# =============================================================================
MOTS_CLES_APPEL_OFFRES = [
    # Français
    r'appel\s+d\'?offres?',
    r'appels?\s+d\'?offres?',
    r'demande\s+de\s+cotation',
    r'demande\s+de\s+proposition',
    r'demandes?\s+de\s+propositions?',
    r'avis\s+de\s+recrutement',
    r'avis\s+a?\s+manifestation\s+d\'?inter',
    r'recrutement\s+d\'?un\s+bureau',
    r'recrutement\s+d\'?un\s+cabinet',
    # ✅ AJOUTÉ : Achat, Acquisition, Production, Fourniture
    r'achat\s+de',
    r'achat\s+d\'?e?quipement',
    r'acquisition\s+de',
    r'fourniture\s+de',
    r'production\s+de',
    r'travaux\s+de',
    r'cotation\s+pour',
    r'rfp\s+',
    r'rfq\s+',
    r'itt\s+',
    r'sdp\s+',
    r'invitation\s+a\s+soumissionner',
    r'consultation\s+des\s+entreprises',
    r'march[eé]\s+public',
    r'proc[eè]dure\s+de\s+passation',
    r'dossier\s+de\s+consultation',
    r'demande\s+de\s+prix',
    
    # Anglais
    r'request\s+for\s+proposal',
    r'request\s+for\s+quotation',
    r'invitation\s+to\s+bid',
    r'call\s+for\s+tender',
    r'call\s+for\s+bids',
    r'procurement\s+notice',
    r'bid\s+document',
    r'tender\s+document',
    r'expression\s+of\s+interest',
]


# =============================================================================
# MOTS-CLÉS QUI EXCLUENT UN APPEL D'OFFRES
# =============================================================================
MOTS_CLES_REJET = [
    # ✅ SUPPRIMÉ : "résultats des appels d'offres" (c'est valide pour voir les résultats)
    # Résultats et bilans
    r'attribution\s+du\s+march[eé]',
    r'avis\s+d\'?attribution',
    r'r[eé]sultats?\s+de\s+la\s+s[eé]lection',
    r'rapport\s+d\'?activit[eé]',
    r'rapport\s+annuel',
    r'bilan\s+',
    
    # Actualités et nouvelles
    r'actualit[eé]',
    r'apr[eè]s\s+niamey',
    r'met\s+le\s+cap\s+sur',
    r'd[eé]ploie\s+son\s+expertise',
    r'nouvelle\s+',
    r'news\s+',
    r'communiqu[eé]\s+de\s+presse',
    r'press\s+release',
    r'annonce\s+de\s+',
    
    # Prix et récompenses
    r'prix\s+de\s+l\'?association',
    r'prix\s+de\s+la\s+meilleure',
    r'r[eé]compense',
    r'award',
    r'prix\s+journalistique',
    r'couverture\s+journalistique',
    
    # Défis et concours (pas des appels d'offres)
    r'd[eé]fi\s+d\'?innovation',
    r'concours\s+',
    r'challenge\s+',
    r'contest\s+',
    r'cr[eé]atif',
    r'#creatives',
    
    # Appels à projets / candidatures (différent des appels d'offres)
    r'appel\s+[àa]\s+projets?',
    r'call\s+for\s+projects?',
    r'appel\s+ouvert\s+pour',
    r'programme\s+de\s+leadership',
    r'candidatures?\s+ouvertes',
    r'soumettre\s+des?\s+candidatures',
    r'submit\s+applications?',
    r'grant\s+',
    r'subvention\s+',
    
    # Événements et formations
    r'formation\s+des?\s+organisations',
    r'session\s+intensive',
    r'atelier\s+',
    r'workshop\s+',
    r'conf[eé]rence\s+',
    r'[ée]v[eé]nement\s+',
    r's[eé]minaire\s+',
    
    # Rapports et études (pas des appels)
    r'[ée]tude\s+de\s+cas',
    r'analyse\s+de\s+',
    r'publication\s+',
    r'article\s+',
    r'story\s+',
    r'feature\s+',
    
    # ✅ AJOUTÉ : Pages d'index
    r'live\s+notices',
    r'showing\s+1\s+to',
]


def is_valid_offer_title(titre: str) -> bool:
    """
    Vérifie si un titre correspond à un VRAI appel d'offres
    Retourne True si c'est un appel d'offres valide, False sinon
    """
    if not titre or len(titre) < 15:
        logger.debug(f"⏭️ Rejeté (titre trop court): {titre}")
        return False
    
    titre_lower = titre.lower()
    
    # ÉTAPE 1 : Vérifier les motifs de rejet (priorité haute)
    for pattern in MOTS_CLES_REJET:
        if re.search(pattern, titre_lower, re.IGNORECASE):
            logger.info(f"   ❌ REJETÉ (motif: '{pattern}'): {titre[:60]}")
            return False
    
    # ÉTAPE 2 : Vérifier la présence d'un mot-clé d'appel d'offres
    has_valid_keyword = False
    for pattern in MOTS_CLES_APPEL_OFFRES:
        if re.search(pattern, titre_lower, re.IGNORECASE):
            has_valid_keyword = True
            break
    
    if not has_valid_keyword:
        logger.info(f"   ❌ REJETÉ (pas de mot-clé valide): {titre[:60]}")
        return False
    
    logger.info(f"   ✅ VALIDÉ: {titre[:60]}")
    return True


def is_rejected_content(texte: str) -> bool:
    """Vérifie si un contenu complet doit être rejeté"""
    if not texte or len(texte) < 50:
        return True
    
    texte_lower = texte.lower()
    
    # Compter les mots-clés de rejet
    rejet_count = sum(1 for pattern in MOTS_CLES_REJET if re.search(pattern, texte_lower, re.IGNORECASE))
    
    # Compter les mots-clés d'appel d'offres
    appel_count = sum(1 for pattern in MOTS_CLES_APPEL_OFFRES if re.search(pattern, texte_lower, re.IGNORECASE))
    
    # Rejeter si beaucoup de rejets et peu d'appels d'offres
    if rejet_count >= 2 and appel_count == 0:
        return True
    
    return False