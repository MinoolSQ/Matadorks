#!/usr/bin/env python3
"""
Dork generator - SQLi focused, multi-region, demographic-targeted.
Now using data/dorks/*.txt files via dork_gen.py
"""

from modules.dork_gen import generate_all, generate_light_dorks

if __name__ == "__main__":
    dorks = generate_all()
    output_file = "sqli_dorks.txt"

    with open(output_file, "w") as f:
        f.write(f"# SQLi + Modern Leak Dorks | Generated: {len(dorks)} dorks\n")
        f.write("# Regions: Loaded from data/dorks/regional/*.txt\n\n")

        for d in dorks:
            f.write(d + "\n")

    print(f"[+] Generisano {len(dorks)} dorkova -> {output_file}")
