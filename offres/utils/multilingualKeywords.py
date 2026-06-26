# offres/utils/multilingualKeywords.py

MULTILINGUAL_KEYWORDS = {
    'santé': ['health', 'medical', 'healthcare', 'hôpital', 'hospital', 'UNICEF', 'WHO', 'OMS'],
    'health': ['santé', 'medical', 'healthcare', 'hôpital', 'hospital'],
    'informatique': ['IT', 'technology', 'computer', 'software', 'digital', 'tech'],
    'IT': ['informatique', 'technology', 'tech', 'computer'],
    'éducation': ['education', 'teaching', 'training', 'école', 'school', 'UNESCO'],
    'education': ['éducation', 'enseignement', 'teaching', 'formation'],
}

def getRelatedKeywords(keyword):
    """Obtient tous les mots-clés associés (français + anglais)"""
    if not keyword:
        return []
    
    keyword = keyword.lower().strip()
    related = set([keyword])
    
    for key, values in MULTILINGUAL_KEYWORDS.items():
        if key == keyword:
            related.update(values)
        if keyword in values:
            related.add(key)
            related.update(values)
    
    return list(related)