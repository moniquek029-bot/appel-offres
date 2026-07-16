# offres/utils/offer_validator.py
"""
Validateur pour identifier les VRAIS appels d'offres
Version 3.0 - Plus permissive et complète
✅ Accepte plus d'offres légitimes
✅ Rejette moins de faux positifs
"""
import re
import logging

logger = logging.getLogger(__name__)


# =============================================================================
# MOTS-CLÉS QUI INDENTIFIENT UN VRAI APPEL D'OFFRES (ÉLARGI)
# =============================================================================
MOTS_CLES_APPEL_OFFRES = [
    # === Français - avec gestion des apostrophes ===
    r"appel[\s'']{0,2}d[\s'']{0,2}offres?",
    r"appels?[\s'']{0,2}d[\s'']{0,2}offres?",
    r"demande[\s'']{0,2}de[\s'']{0,2}cotation",
    r"demande[\s'']{0,2}de[\s'']{0,2}proposition",
    r"demandes?[\s'']{0,2}de[\s'']{0,2}propositions?",
    r"avis[\s'']{0,2}de[\s'']{0,2}recrutement",
    r"avis[\s'']{0,2}[àa][\s'']{0,2}manifestation[\s'']{0,2}d[\s'']{0,2}inter",
    r"recrutement[\s'']{0,2}d[\s'']{0,2}(un|une)?",
    
    # === Achat, Acquisition, Production ===
    r"achat[\s'']{0,2}(de|d[\s''])",
    r"acquisition[\s'']{0,2}de",
    r"fourniture[\s'']{0,2}(de|d[\s''])",
    r"production[\s'']{0,2}de",
    r"travaux[\s'']{0,2}de",
    r"cotation[\s'']{0,2}pour",
    
    # === ✅ Codes UNDP/UNFPA (avec / en plus de espace/tiret) ===
    r"rfp[\s_\-/]",
    r"rfq[\s_\-/]",
    r"itt[\s_\-/]",
    r"sdp[\s_\-/]",
    r"dao[\s_\-/]",
    r"rfo[\s_\-/]",
    r"eois?[\s_\-/]",
    
    # === ✅ Codes spécifiques UNDP (très importants) ===
    r"\bA2J/RFP\b",
    r"\bUNW-[A-Z]{2,3}-\d{4}",  # UNW-BIH-2026, UNW-SEN-2026
    r"\bRFQ[\-_]\d+",
    r"\bRFP[\-_]\d+",
    r"\bSDP[\s\-/]\d+",
    
    # === Autres mots-clés français ===
    r"invitation[\s'']{0,2}[àa][\s'']{0,2}soumissionner",
    r"consultation[\s'']{0,2}(des|pour|d[\s''])",
    r"march[eé][\s'']{0,2}public",
    r"proc[eè]dure[\s'']{0,2}de[\s'']{0,2}passation",
    r"dossier[\s'']{0,2}de[\s'']{0,2}consultation",
    r"demande[\s'']{0,2}de[\s'']{0,2}prix",
    r"bureau[\s'']{0,2}d[\s'']{0,2}[eé]tudes?",
    r"kits?[\s'']{0,2}de[\s'']{0,2}sant[eé]",
    r"mat[eé]riel[\s'']{0,2}informatique",
    r"licences?[\s'']{0,2}de[\s'']{0,2}logiciel",
    
    # === ✅ Anglais - patterns élargis ===
    r"request[\s'']{0,2}for[\s'']{0,2}proposal",
    r"request[\s'']{0,2}for[\s'']{0,2}quotation",
    r"request[\s'']{0,2}for[\s'']{0,2}expression",
    r"invitation[\s'']{0,2}to[\s'']{0,2}bid",
    r"invitation[\s'']{0,2}to[\s'']{0,2}tender",
    r"call[\s'']{0,2}for[\s'']{0,2}tender",
    r"call[\s'']{0,2}for[\s'']{0,2}bids",
    r"call[\s'']{0,2}for[\s'']{0,2}consultant",
    r"call[\s'']{0,2}for[\s'']{0,2}service",
    r"procurement[\s'']{0,2}notice",
    r"procurement[\s'']{0,2}plan",
    r"bid[\s'']{0,2}document",
    r"tender[\s'']{0,2}document",
    r"tender[\s'']{0,2}notice",
    r"expression[\s'']{0,2}of[\s'']{0,2}interest",
    
    # === ✅ Mots-clés anglais courants pour consultants ===
    r"consultant[\s'']{0,2}(for|in|to|en)?",
    r"consultancy[\s'']{0,2}(for|in|to|services)?",
    r"consulting[\s'']{0,2}(services)?",
    r"services[\s'']{0,2}(for|of|to|related)",
    r"individual[\s'']{0,2}consultant",
    r"international[\s'']{0,2}consultant",
    r"national[\s'']{0,2}consultant",
    
    # === ✅ Types de prestations ===
    r"implementation[\s'']{0,2}(of|for)?",
    r"design[\s'']{0,2}(of|and|for)?",
    r"development[\s'']{0,2}(of|for)?",
    r"assessment[\s'']{0,2}(of|for)?",
    r"evaluation[\s'']{0,2}(of|for)?",
    r"analysis[\s'']{0,2}(of|for)?",
    r"optimizing",
    r"production[\s'']{0,2}(of|for)?",
    r"supply[\s'']{0,2}(of|for)?",
    r"provision[\s'']{0,2}(of|for)?",
    r"delivery[\s'']{0,2}(of|for)?",
    r"construction[\s'']{0,2}(of|for)?",
    r"rehabilitation[\s'']{0,2}(of|for)?",
    r"maintenance[\s'']{0,2}(of|for)?",
    r"training[\s'']{0,2}(on|in|of|for)?",
    r"study[\s'']{0,2}(on|of|for)?",
    r"survey[\s'']{0,2}(on|of|for)?",
    r"audit[\s'']{0,2}(of|for)?",
    r"review[\s'']{0,2}(of|for)?",
    
    # === ✅ Objets courants ===
    r"platform",
    r"system[\s'']{0,2}(development|implementation|integration)",
    r"software[\s'']{0,2}(development|implementation)",
    r"database[\s'']{0,2}",
    r"equipment[\s'']{0,2}",
    r"vehicle[\s'']{0,2}",
    r"motorcycle",
    r"laptop",
    r"computer[\s'']{0,2}",
    
    # === ✅ Mots-clés spécifiques à UNFPA ===
    r"spot[\s'']{0,2}check",
    r"v[eé]rification[\s'']{0,2}ponctuelle",
    r"motocyclette",
    r"ordinateur",
    
    # ✅ NOUVEAUX : Candidatures et subventions
    r"candidatures?[\s'']{0,2}ouvertes",
    r"subvention[s]?[\s'']{0,2}(pour|au|aux)?",
    r"rfa[s]?[\s'']{0,2}:",
    r"petites[\s'']{0,2}subventions",
    r"programme[\s'']{0,2}de[\s'']{0,2}subvention",
    r"leaders?[\s'']{0,2}de[\s'']{0,2}demain",
    r"jeunes[\s'']{0,2}leaders",
    
    # ✅ NOUVEAUX : Appels à candidatures
    r"appel[\s'']{0,2}a[\s'']{0,2}candidatures?",
    r"call[\s'']{0,2}for[\s'']{0,2}applications?",
    
    # ... reste des mots-clés ...


]


# =============================================================================
# MOTS-CLÉS QUI EXCLUENT UN APPEL D'OFFRES (RÉDUIT - seulement cas évidents)
# =============================================================================
MOTS_CLES_REJET = [
    # === Résultats d'attribution (PAS des appels d'offres) ===
    r"r[eé]sultats?\s+(de|des)\s+(la\s+)?s[eé]lection",
    r"attribution[\s'']{0,2}du[\s'']{0,2}march[eé]",
    r"avis[\s'']{0,2}d[\s'']{0,2}attribution",
    r"contract[\s'']{0,2}award",  # ✅ Attributions en anglais
    r"award[\s'']{0,2}notice",
    
    # === Actualités et communication ===
    r"actualit[eé]s?",
    r"communiqu[eé][\s'']{0,2}de[\s'']{0,2}presse",
    r"press[\s'']{0,2}release",
    r"news[\s'']{0,2}update",
    
    # === Prix et récompenses ===
    r"prix[\s'']{0,2}journalistique",
    r"r[eé]compense[\s'']{0,2}",
    r"award[\s'']{0,2}(for[\s'']{0,2}best|de[\s'']{0,2}la)",
    
    # === Ventes aux enchères (différent des appels d'offres) ===
    r"auction[\s'']{0,2}(of|for)?\s*(sale|vente)",
    
    # === Pages d'index et navigation ===
    r"live[\s'']{0,2}notices",
    r"showing[\s'']{0,2}\d+\s+to",
    r"420[\s'']{0,2}live",
    
    # === Guides et tutoriels ===
    r"comment[\s'']{0,2}s[\s'']{0,2}enregistrer",
    r"guide[\s'']{0,2}pratique",
    r"tutoriel[\s'']{0,2}",
    r"supplier[\s'']{0,2}profile[\s'']{0,2}change",
    r"editing[\s'']{0,2}your[\s'']{0,2}profile",
    r"information[\s'']{0,2}session",
    r"webinar[\s'']{0,2}(for|sur)",
    
    # === Événements (PAS des offres) ===
    r"(visite|visit)[\s'']{0,2}de[\s'']{0,2}courtoisie",
    r"conf[eé]rence[\s'']{0,2}(de|on|about)[\s'']{0,2}",
    r"workshop[\s'']{0,2}(on|sur|about)",
    r"s[eé]minaire[\s'']{0,2}(de|sur|on)",
]


# =============================================================================
# MOTS-CLÉS NEUTRES (n'influencent pas la décision)
# =============================================================================
MOTS_CLES_NEUTRES = [
    r"rapport[\s'']{0,2}annuel",
    r"publication[\s'']{0,2}",
    r"[ée]tude[\s'']{0,2}de[\s'']{0,2}cas",
    r"analyse[\s'']{0,2}de[\s'']{0,2}",
    r"story[\s'']{0,2}",
    r"feature[\s'']{0,2}",
    r"article[\s'']{0,2}",
]


def normalize_text(texte: str) -> str:
    """Normalise le texte : remplace les apostrophes typographiques"""
    if not texte:
        return ""
    # Remplacer ' ' ' ' par '
    texte = texte.replace(''', "'").replace(''', "'")
    texte = texte.replace(''', "'").replace(''', "'")
    texte = texte.replace(''', "'").replace(''', "'")
    # Normaliser les espaces
    texte = re.sub(r'\s+', ' ', texte)
    return texte.lower()


def is_valid_offer_title(titre: str) -> bool:
    """
    ✅ VERSION 3.0 : Plus permissive, accepte plus d'offres légitimes
    
    Stratégie :
    1. Rejeter seulement les cas ÉVIDEMMENT non-offres
    2. Valider si au moins un mot-clé d'appel d'offres est trouvé
    3. Accepter les titres longs avec des termes génériques
    """
    if not titre or len(titre) < 8:
        return False
    
    titre_norm = normalize_text(titre)
    
    # ÉTAPE 1 : Vérifier les motifs de rejet (UNIQUEMENT les cas évidents)
    for pattern in MOTS_CLES_REJET:
        if re.search(pattern, titre_norm, re.IGNORECASE):
            # ✅ Exception : si le titre contient AUSSI un mot-clé valide, on le garde
            has_valid = any(re.search(p, titre_norm, re.IGNORECASE) 
                          for p in MOTS_CLES_APPEL_OFFRES)
            if has_valid:
                logger.debug(f"   ⚠️ Motif rejet ignoré (contient mot-clé valide): {titre[:60]}")
            else:
                logger.debug(f"   ❌ REJETÉ (motif: '{pattern}'): {titre[:60]}")
                return False
    
    # ÉTAPE 2 : Vérifier la présence d'un mot-clé d'appel d'offres
    for pattern in MOTS_CLES_APPEL_OFFRES:
        if re.search(pattern, titre_norm, re.IGNORECASE):
            logger.debug(f"   ✅ VALIDÉ (motif: '{pattern}'): {titre[:60]}")
            return True
    
    # ✅ ÉTAPE 3 : NOUVEAU - Accepter les titres longs avec mots-clés génériques
    # Exemple: "Development of Mobile Application for Health Centers"
    generic_keywords = [
        'offer', 'offre', 'notice', 'avis', 'appel', 'tender', 'bid',
        'proposal', 'quotation', 'procurement', 'contract'
    ]
    
    if any(kw in titre_norm for kw in generic_keywords) and len(titre) > 25:
        logger.debug(f"   ✅ VALIDÉ (générique): {titre[:60]}")
        return True
    
    # ✅ ÉTAPE 4 : NOUVEAU - Codes spécifiques UNDP dans l'URL/titre
    if re.search(r'(A2J|UNW|UNFPA|PNUD)[\-_/]\w{2,4}[\-/]\d{4}', titre_norm, re.IGNORECASE):
        logger.debug(f"   ✅ VALIDÉ (code UNDP): {titre[:60]}")
        return True
    
    logger.debug(f"   ❌ REJETÉ (pas de mot-clé): {titre[:60]}")
    return False


def is_rejected_content(texte: str) -> bool:
    """
    ✅ VERSION 3.0 : Vérifie si un contenu doit être rejeté
    Plus permissive : rejette seulement si BEAUCOUP de rejets
    """
    if not texte or len(texte) < 30:
        return True
    
    texte_norm = normalize_text(texte)
    
    # Compter les mots-clés
    rejet_count = sum(1 for p in MOTS_CLES_REJET 
                     if re.search(p, texte_norm, re.IGNORECASE))
    appel_count = sum(1 for p in MOTS_CLES_APPEL_OFFRES 
                     if re.search(p, texte_norm, re.IGNORECASE))
    
    # ✅ Assoupli : rejeter seulement si >= 3 rejets ET 0 appel
    # (au lieu de 2 et 0)
    if rejet_count >= 3 and appel_count == 0:
        logger.debug(f"   ❌ Contenu rejeté ({rejet_count} rejets, {appel_count} appels)")
        return True
    
    return False