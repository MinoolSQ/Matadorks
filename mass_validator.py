import os
import sys
from queue import Queue
from modules.validator import Validator

def run_mass_validation():
    # Postavljanje putanja
    sqli_targets_file = "data/test_matadorks_sqli_targets.txt"
    leaks_file = "data/test_matadorks_leaks.txt"
    
    if not os.path.exists(sqli_targets_file):
        print(f"[!] Fajl {sqli_targets_file} ne postoji.")
        return

    # Učitavanje URL-ova
    urls = set()
    for fpath in [sqli_targets_file, leaks_file]:
        if os.path.exists(fpath):
            with open(fpath, "r") as f:
                for line in f:
                    url = line.strip()
                    if url and url.startswith("http"):
                        urls.add(url)
    
    print(f"[*] Učitano {len(urls)} jedinstvenih URL-ova za validaciju.")

    # Postavljanje redova (Queues)
    in_q = Queue()
    out_q = Queue()

    for url in urls:
        in_q.put(url)
    in_q.put(None) # Sentinel

    # Pokretanje validatora
    print(f"[*] Pokretanje masovne validacije...")
    validator = Validator(in_q, out_q)
    validator.run()

    print("[*] Validacija završena.")

if __name__ == "__main__":
    # Dodajemo root u path da bi importi radili
    sys.path.append(os.getcwd())
    run_mass_validation()
