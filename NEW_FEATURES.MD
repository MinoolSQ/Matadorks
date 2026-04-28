# Matadorks New Features & Upgrades (April 2026)

## 1. Monster Dork Generator (v2.0)
- **Deep Taxonomy Integration:** Sistem sada koristi troslojnu asocijativnu mrežu (Usko, Onako, Opširno) za generisanje dorkova.
- **Niche Focus:** Implementirane specijalizovane niše za Incele, Trade radnike (kamiondžije, naftaši) i oštećene potrošače.
- **Volume:** Baza povećana sa 500 na **1255 hirurški preciznih dorkova**.
- **Confidence Scoring:** Svaki dork je filtriran i očišćen od "noise-a", zadržavajući samo one sa CS > 60.

## 2. Asynchronous Pipeline (Zver Edition)
- **Full Async Core:** Skener, Validator i Injector sada rade potpuno asinhrono koristeći `asyncio` i `aiohttp`.
- **Parallel Proxy Validation:** Masovni fetch i testiranje hiljada proksija u sekundi.
- **TUI Live Dashboard:** Vizuelni prikaz progresa, queue statusa i "pwned" statistike u realnom vremenu.

## 3. Advanced Evasion (U pripremi)
- **AWS API Gateway Rotation:** Planirana integracija REST API Gateway-a za neograničenu IP rotaciju.
- **Time-Range Filtering:** Svi dorkovi automatski filtriraju rezultate **nakon 2020. godine** (`tbs=cdr` i `after:2020`).
- **JA3 Fingerprinting:** Planiran prelazak na `curl-cffi` za imitaciju TLS handshake-a modernih browsera.
