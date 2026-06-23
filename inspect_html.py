# inspect_html.py
import requests
from bs4 import BeautifulSoup
import urllib3

urllib3.disable_warnings()

def inspect_joffres():
    url = "https://www.joffres.net/les_appeloffre/filtre"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    
    print("="*70)
    print(f"🔍 INSPECTION : {url}")
    print("="*70)
    
    response = requests.get(url, headers=headers, timeout=15, verify=False)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Chercher les structures typiques d'offres
    print("\n📊 Recherche de structures d'offres :")
    
    # 1. Chercher les liens avec "appel" ou "offre"
    offre_links = []
    for link in soup.find_all('a', href=True):
        text = link.get_text(strip=True)
        if any(kw in text.lower() for kw in ['appel', 'offre', 'marché']) and len(text) > 20:
            offre_links.append({
                'text': text[:80],
                'href': link['href'],
                'parent': link.parent.name,
                'parent_class': link.parent.get('class', [])
            })
    
    print(f"\n🔗 {len(offre_links)} liens d'offres trouvés")
    for i, link in enumerate(offre_links[:5], 1):
        print(f"  {i}. {link['text']}")
        print(f"     → {link['href']}")
        print(f"     → Parent: <{link['parent']}> class={link['parent_class']}")
    
    # 2. Chercher les conteneurs typiques
    print("\n📦 Conteneurs potentiels :")
    for tag in ['article', 'div', 'li', 'tr']:
        elements = soup.find_all(tag)
        if elements:
            print(f"  <{tag}> : {len(elements)} éléments")
            # Afficher les classes les plus courantes
            classes = {}
            for elem in elements[:50]:
                cls = ' '.join(elem.get('class', []))
                if cls:
                    classes[cls] = classes.get(cls, 0) + 1
            if classes:
                top_classes = sorted(classes.items(), key=lambda x: x[1], reverse=True)[:5]
                print(f"     Classes fréquentes : {top_classes}")

def inspect_undp():
    url = "https://procurement-notices.undp.org/search.cfm?country=BF"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    
    print("\n" + "="*70)
    print(f"🔍 INSPECTION : {url}")
    print("="*70)
    
    response = requests.get(url, headers=headers, timeout=15, verify=False)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # UNDP utilise souvent des tableaux ou des listes structurées
    print("\n📊 Recherche de structures d'offres :")
    
    # Chercher les liens vers view_notice
    notice_links = []
    for link in soup.find_all('a', href=True):
        if 'view_notice' in link['href']:
            text = link.get_text(strip=True)
            if text and len(text) > 10:
                notice_links.append({
                    'text': text[:80],
                    'href': link['href'],
                    'parent': link.parent.name,
                    'parent_class': link.parent.get('class', [])
                })
    
    print(f"\n🔗 {len(notice_links)} liens vers notices trouvés")
    for i, link in enumerate(notice_links[:5], 1):
        print(f"  {i}. {link['text']}")
        print(f"     → {link['href']}")
        print(f"     → Parent: <{link['parent']}> class={link['parent_class']}")

if __name__ == "__main__":
    inspect_joffres()
    inspect_undp()