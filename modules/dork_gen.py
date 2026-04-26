import os
import random
from core.config import DORKS_DATA_DIR

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

def generate_all():
    modern_leaks = _load_list("modern_leaks.txt")
    
    all_dorks = set()
    all_dorks.update(modern_leaks)
    all_dorks.update(generate_sqli_error_dorks())
    all_dorks.update(generate_regional_param_dorks())
    all_dorks.update(generate_niche_sqli_dorks())

    # Ukloni preduge dorkove (Google ignorise >128 chars)
    all_dorks = {d for d in all_dorks if len(d) <= 128}

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

    return sorted(list(dorks))

if __name__ == "__main__":
    all_dorks = generate_all()
    random.shuffle(all_dorks)

    with open("massive_niche_dorks_2026.txt", "w") as f:
        f.write(f"# Generated {len(all_dorks)} Dorks from text files\n")
        for dork in all_dorks:
            f.write(dork + "\n")

    print(f"Generisano {len(all_dorks)} dorkova.")
