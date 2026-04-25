#!/usr/bin/env python3
"""
Dork generator - SQLi focused, multi-region, demographic-targeted.
Output: sqli_dorks.txt
"""

# --- SQL greske (uvijek engleski, bez obzira na jezik sajta) ---
SQL_ERRORS = [
    'intext:"You have an error in your SQL syntax"',
    'intext:"Warning: mysql_fetch_array()"',
    'intext:"Warning: mysqli_num_rows()"',
    'intext:"Warning: mysql_num_rows()"',
    'intext:"Warning: pg_query()"',
    'intext:"ORA-01756:"',
    'intext:"Microsoft OLE DB Provider for SQL Server"',
    'intext:"Unclosed quotation mark after the character string"',
    'intext:"supplied argument is not a valid MySQL"',
    'intext:"mysql_connect(): The mysql extension is deprecated"',
    'intext:"mysqli_fetch_assoc() expects"',
]

# --- Ranjivi URL parametri (SQLi entry points) ---
PARAMS = [
    'inurl:"?id="',
    'inurl:"?cat="',
    'inurl:"?user="',
    'inurl:"?article="',
    'inurl:"?page="',
    'inurl:"?topic="',
    'inurl:"?thread="',
    'inurl:"?product="',
    'inurl:"?item="',
    'inurl:"?news_id="',
    'inurl:"?post_id="',
    'inurl:"?profile_id="',
]

# --- Regionalni URL parametri (lokalni jezici) ---
REGIONAL_PARAMS = {
    "de": [
        'inurl:"?artikel="',
        'inurl:"?produkt="',
        'inurl:"?benutzer="',
        'inurl:"?kategorie="',
        'inurl:"?beitrag="',
        'inurl:"?thema="',
    ],
    "it": [
        'inurl:"?articolo="',
        'inurl:"?prodotto="',
        'inurl:"?categoria="',
        'inurl:"?utente="',
        'inurl:"?notizia="',
    ],
    "fr": [
        'inurl:"?article="',
        'inurl:"?produit="',
        'inurl:"?utilisateur="',
        'inurl:"?categorie="',
        'inurl:"?sujet="',
    ],
    "es": [
        'inurl:"?articulo="',
        'inurl:"?producto="',
        'inurl:"?usuario="',
        'inurl:"?categoria="',
        'inurl:"?tema="',
    ],
    "pl": [
        'inurl:"?artykul="',
        'inurl:"?produkt="',
        'inurl:"?uzytkownik="',
        'inurl:"?kategoria="',
        'inurl:"?temat="',
    ],
    "ro": [
        'inurl:"?articol="',
        'inurl:"?produs="',
        'inurl:"?utilizator="',
        'inurl:"?categorie="',
    ],
    "cz": [
        'inurl:"?clanek="',
        'inurl:"?produkt="',
        'inurl:"?uzivatel="',
        'inurl:"?kategorie="',
    ],
    "hu": [
        'inurl:"?cikk="',
        'inurl:"?termek="',
        'inurl:"?felhasznalo="',
    ],
}

# --- Niche fingerprinti (demografija: muski 18-45, trose online) ---
# Kombinujemo sa SQL error dorkovima i parametrima
NICHE_FINGERPRINTS = [
    # Forum software
    '"powered by vbulletin"',
    '"powered by phpbb"',
    '"powered by mybb"',
    '"powered by xenforo"',
    '"powered by smf"',
    # Niche tematike
    '"motoclub"',
    '"motorrad"',        # njemacki moto
    '"motociclismo"',    # italijanski moto
    '"motocykl"',        # poljski moto
    '"paris sportifs"',  # francuski betting
    '"wettanbieter"',    # njemacki betting
    '"scommesse"',       # italijanski betting
    '"zakłady"',         # poljski betting
    '"casino"',
    '"poker forum"',
    '"cryptocurrency"',
    '"crypto forum"',
    '"discord server"',
    # Stari PHP sajtovi (post-2019 deployment, pre-2024 update)
    '"index of" "backup"',
    'inurl:wp-content ext:php',
]

# --- Post-2021 moderna ranjivost (cloud/framework leaks) ---
MODERN_LEAKS = [
    'intext:"DATABASE_URL=postgres" filetype:env',
    'intext:"APP_KEY=base64:" filetype:env',
    'intext:"NEXT_PUBLIC_" filetype:env',
    'intext:"DISCORD_TOKEN" filetype:env',
    'intext:"STRIPE_SECRET_KEY" filetype:env',
    'intext:"supabase.co" intext:"service_role" filetype:env',
    'intext:"mongodb+srv://" filetype:env',
    'intext:"TELEGRAM_BOT_TOKEN" filetype:env',
    'intitle:"Whoops!" intext:"APP_KEY"',
    'intext:"Illuminate\\Database" intext:"password"',
    'inurl:"/.git/config" intext:"url ="',
    'intitle:"index of" "config.php.bak"',
    'intitle:"index of" "wp-config.php.bak"',
    'intitle:"index of" "database.sql"',
    'intitle:"index of" "users.sql"',
    'intitle:"index of" ".env"',
]


def generate_sqli_error_dorks():
    """SQL greska + ranjivi param na istoj stranici."""
    dorks = set()
    for error in SQL_ERRORS:
        dorks.add(error)
        # Error + param kombinacija (visoka preciznost)
        for param in PARAMS[:6]:  # samo top params da ne eksplodira
            dorks.add(f"{error} {param}")
    return dorks


def generate_regional_param_dorks():
    """Regionalni parametri sa site: operatorom."""
    dorks = set()
    for tld, params in REGIONAL_PARAMS.items():
        for param in params:
            dorks.add(f"{param} site:.{tld}")
        # SQL error + regionalni param + site:
        for error in SQL_ERRORS[:4]:  # top 4 greske
            for param in params[:3]:  # top 3 param
                dorks.add(f"{error} {param} site:.{tld}")
    return dorks


def generate_niche_sqli_dorks():
    """Niche fingerprint + ranjivi param (demografski targeting)."""
    dorks = set()
    for niche in NICHE_FINGERPRINTS:
        for param in PARAMS[:5]:
            dorks.add(f"{niche} {param}")
        for error in SQL_ERRORS[:3]:
            dorks.add(f"{niche} {error}")
    return dorks


def generate_all():
    all_dorks = set()
    all_dorks.update(MODERN_LEAKS)
    all_dorks.update(generate_sqli_error_dorks())
    all_dorks.update(generate_regional_param_dorks())
    all_dorks.update(generate_niche_sqli_dorks())

    # Ukloni preduge dorkove (Google ignorise >128 chars)
    all_dorks = {d for d in all_dorks if len(d) <= 128}

    return sorted(all_dorks)


if __name__ == "__main__":
    dorks = generate_all()
    output_file = "sqli_dorks.txt"

    with open(output_file, "w") as f:
        f.write(f"# SQLi + Modern Leak Dorks | Generated: {len(dorks)} dorks\n")
        f.write("# Regions: EN, DE, IT, FR, ES, PL, RO, CZ, HU\n\n")

        f.write("# === MODERN LEAKS (post-2021) ===\n")
        for d in sorted(MODERN_LEAKS):
            f.write(d + "\n")

        f.write("\n# === SQL ERROR DORKS ===\n")
        for d in sorted(generate_sqli_error_dorks()):
            f.write(d + "\n")

        f.write("\n# === REGIONAL PARAM DORKS ===\n")
        for d in sorted(generate_regional_param_dorks()):
            f.write(d + "\n")

        f.write("\n# === NICHE + DEMOGRAPHIC DORKS ===\n")
        for d in sorted(generate_niche_sqli_dorks()):
            f.write(d + "\n")

    print(f"[+] Generisano {len(dorks)} dorkova -> {output_file}")
    print(f"    Modern leaks:    {len(MODERN_LEAKS)}")
    print(f"    SQL error dorks: {len(generate_sqli_error_dorks())}")
    print(f"    Regional dorks:  {len(generate_regional_param_dorks())}")
    print(f"    Niche dorks:     {len(generate_niche_sqli_dorks())}")
