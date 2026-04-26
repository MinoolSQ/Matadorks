import random

def generate_light_dorks():
    operators = [
        'intitle:"index of"', 'filetype:env', 'filetype:log',
        'ext:sql', 'ext:xlsx', 'intext:"password"', 'inurl:admin'
    ]

    niches = [
        'onlyfans', 'fansly', 'patreon', 'creator', 'subscription', 
        'premium', 'stripe', 'payout', 'vbulletin', 'mybb'
    ]

    # Dodajemo univerzalne dorkove za ove niche
    universal = [
        'intitle:"index of" "users.sql"',
        'intitle:"index of" "backup.sql"',
        'filetype:env "DB_PASSWORD"',
        'inurl:admin/login.php "subscription"',
        'intext:"Index of" "config.php.bak"',
        'intext:"Index of" "database.sql.gz"'
    ]

    dorks = set(universal)

    # Pravimo jednostavnije kombinacije (samo 2 elementa)
    for op in operators:
        for niche in niches:
            dorks.add(f'{op} "{niche}"')
    
    # Dodajemo regionalne ali sa samo jednim kljucnim terminom
    regions = {
        'Germany': ['Passwort', 'Auszahlung', 'Sicherung'],
        'France': ['mot_de_passe', 'paiement'],
        'Spain': ['contraseña', 'pago'],
        'Czech': ['heslo', 'platba']
    }

    for reg, terms in regions.items():
        tld = {'Germany':'.de', 'France':'.fr', 'Spain':'.es', 'Czech':'.cz'}[reg]
        for term in terms:
            for niche in niches:
                dorks.add(f'"{niche}" "{term}" site:{tld}')

    return sorted(list(dorks))

if __name__ == "__main__":
    all_dorks = generate_light_dorks()
    random.shuffle(all_dorks)

    with open("massive_niche_dorks_2026.txt", "w") as f:
        f.write(f"# Generated {len(all_dorks)} LIGHTWEIGHT Dorks\n")
        for dork in all_dorks:
            f.write(dork + "\n")

    print(f"Generisano {len(all_dorks)} laksih dorkova.")
