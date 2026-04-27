import os
import random
from core.config import DORKS_DATA_DIR, SEARCH_TIME_FILTER, SEARCH_AFTER_YEAR

def _load_list(filename):
    """Čita dork fajl, ignorišući komentare i prazne linije."""
    path = os.path.join(DORKS_DATA_DIR, filename)
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as f:
        return [line.strip() for line in f 
                if line.strip() and not line.startswith("#")]

def _load_regional(tld):
    return _load_list(os.path.join("regional", f"{tld}.txt"))

def generate_sqli_error_dorks():
    """SQL greska + ranjivi param na istoj stranici."""
    sql_errors = _load_list("sql_errors.txt")
    params = _load_list("params.txt")
    
    dorks = set()
    for error in sql_errors:
        dorks.add(error)
        # Error + param kombinacija (visoka preciznost)
        for param in params[:6]:  # samo top params da ne eksplodira
            dorks.add(f"{error} {param}")
    return dorks

def generate_regional_param_dorks():
    """Regionalni parametri sa site: operatorom."""
    regional_dir = os.path.join(DORKS_DATA_DIR, "regional")
    if not os.path.exists(regional_dir):
        return set()
    
    tlds = [f[:-4] for f in os.listdir(regional_dir) if f.endswith(".txt")]
    sql_errors = _load_list("sql_errors.txt")
    
    dorks = set()
    for tld in tlds:
        params = _load_regional(tld)
        for param in params:
            dorks.add(f"{param} site:.{tld}")
        # SQL error + regionalni param + site:
        for error in sql_errors[:4]:  # top 4 greske
            for param in params[:3]:  # top 3 param
                dorks.add(f"{error} {param} site:.{tld}")
    return dorks

def generate_niche_sqli_dorks():
    """Niche fingerprint + ranjivi param (demografski targeting)."""
    niche_fingerprints = _load_list("niche.txt")
    params = _load_list("params.txt")
    sql_errors = _load_list("sql_errors.txt")
    
    dorks = set()
    for niche in niche_fingerprints:
        for param in params[:5]:
            dorks.add(f"{niche} {param}")
        for error in sql_errors[:3]:
            dorks.add(f"{niche} {error}")
    return dorks

def generate_cve_dorks():
    """Dorkovi bazirani na specifičnim CVE obrascima (2025-2026)."""
    return _load_list("cve_patterns.txt")

def generate_subdomain_niche_dorks():
    """Kombinuje subdomene sa nišama za otkrivanje nezaštićenih dev/test okruženja."""
    subdomains = _load_list("subdomains.txt")
    niches = _load_list("niche.txt")
    
    dorks = set()
    for sub in subdomains:
        # Nasumično biramo par niša da ne bi imali previše dorkova
        selected_niches = random.sample(niches, min(len(niches), 5))
        for niche in selected_niches:
            dorks.add(f"{sub} {niche}")
    return dorks

def generate_taxonomy_dorks():
    """Generiše 'monster' dorkove iz taksonomije."""
    try:
        from modules.taxonomy_data import TAXONOMY
    except ImportError:
        return set()

    sql_errors = _load_list("sql_errors.txt")
    dorks = set()

    for category, items in TAXONOMY.items():
        for cluster in items:
            # 1. Usko i Child (Visoko specifično) - kombinujemo sa logistickim operatorima
            high_confidence_terms = cluster["usko"] + cluster["child"]
            for term in high_confidence_terms:
                dorks.add(f'inurl:login "{term}"')
                dorks.add(f'inurl:portal "{term}"')
                dorks.add(f'intitle:"index of" "{term}"')
                # dorks.add(f'filetype:env "{term}"') # Previse rizicno za ban, ostavicemo samo za neke

            # 2. Onako (Srednje specifično) - kombinujemo sa forum/community
            for term in cluster["onako"]:
                dorks.add(f'inurl:forum "{term}"')
                dorks.add(f'inurl:community "{term}"')
                dorks.add(f'intext:"password" "{term}"')

            # 3. Opsirno (Široko) - kombinujemo sa specifičnim SQL greškama (maksimalno 2 greske da ne uđe noise)
            if sql_errors:
                for term in cluster["opsirno"]:
                    dorks.add(f'"{term}" "{sql_errors[0]}"')
                    if len(sql_errors) > 1:
                        dorks.add(f'"{term}" "{sql_errors[1]}"')

    return dorks

def generate_all():
    """Generiše isključivo High-Confidence dorkove (CS > 60)."""
    modern_leaks = _load_list("modern_leaks.txt")
    cve_dorks = generate_cve_dorks()
    taxonomy_dorks = generate_taxonomy_dorks()
    
    all_dorks = set()
    all_dorks.update(modern_leaks)
    all_dorks.update(cve_dorks)
    all_dorks.update(taxonomy_dorks)
    
    # Zadržavamo samo NIŠNE SQL dorkove (povećava preciznost)
    all_dorks.update(generate_niche_sqli_dorks())
    
    # Zadržavamo subdomene ali samo za najkritičnije platforme (ručno filtrirano)
    subdomains = _load_list("subdomains.txt")
    critical_niches = [
        '"powered by SportMember"', '"Membership software by VeryConnect"', 
        '"GymMaster Member Portal"', "motoclub", "vbulletin", "xenforo"
    ]
    
    for sub in subdomains:
        for niche in critical_niches:
            all_dorks.add(f"{sub} {niche}")

    # Ukloni preduge dorkove
    all_dorks = {d for d in all_dorks if len(d) <= 128}

    if SEARCH_TIME_FILTER:
        all_dorks = {f"{d} after:{SEARCH_AFTER_YEAR}" for d in all_dorks}

    return sorted(all_dorks)

def generate_light_dorks():
    # Legacy function or simplified version
    operators = [
        'intitle:"index of"', 'filetype:env', 'filetype:log',
        'ext:sql', 'ext:xlsx', 'intext:"password"', 'inurl:admin'
    ]

    niches = [
        'onlyfans', 'fansly', 'patreon', 'creator', 'subscription', 
        'premium', 'stripe', 'payout', 'vbulletin', 'mybb'
    ]

    universal = [
        'intitle:"index of" "users.sql"',
        'intitle:"index of" "backup.sql"',
        'filetype:env "DB_PASSWORD"',
        'inurl:admin/login.php "subscription"',
        'intext:"Index of" "config.php.bak"',
        'intext:"Index of" "database.sql.gz"'
    ]

    dorks = set(universal)

    for op in operators:
        for niche in niches:
            dorks.add(f'{op} "{niche}"')
    
    regions = {
        'de': ['Passwort', 'Auszahlung', 'Sicherung'],
        'fr': ['mot_de_passe', 'paiement'],
        'es': ['contraseña', 'pago'],
        'cz': ['heslo', 'platba']
    }

    for tld, terms in regions.items():
        for term in terms:
            for niche in niches:
                dorks.add(f'"{niche}" "{term}" site:.{tld}')

    if SEARCH_TIME_FILTER:
        dorks = {f"{d} after:{SEARCH_AFTER_YEAR}" for d in dorks}

    return sorted(list(dorks))

if __name__ == "__main__":
    all_dorks = generate_all()
    random.shuffle(all_dorks)

    with open("massive_niche_dorks_2026.txt", "w") as f:
        f.write(f"# Generated {len(all_dorks)} Dorks from text files\n")
        for dork in all_dorks:
            f.write(dork + "\n")

    print(f"Generisano {len(all_dorks)} dorkova.")
