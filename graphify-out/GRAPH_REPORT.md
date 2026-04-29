# Graph Report - Matadorks  (2026-04-29)

## Corpus Check
- 32 files · ~79,681 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 345 nodes · 541 edges · 99 communities detected
- Extraction: 58% EXTRACTED · 42% INFERRED · 0% AMBIGUOUS · INFERRED: 225 edges (avg confidence: 0.74)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- [[_COMMUNITY_Community 0|Community 0]]
- [[_COMMUNITY_Community 1|Community 1]]
- [[_COMMUNITY_Community 2|Community 2]]
- [[_COMMUNITY_Community 3|Community 3]]
- [[_COMMUNITY_Community 4|Community 4]]
- [[_COMMUNITY_Community 5|Community 5]]
- [[_COMMUNITY_Community 6|Community 6]]
- [[_COMMUNITY_Community 7|Community 7]]
- [[_COMMUNITY_Community 8|Community 8]]
- [[_COMMUNITY_Community 9|Community 9]]
- [[_COMMUNITY_Community 10|Community 10]]
- [[_COMMUNITY_Community 11|Community 11]]
- [[_COMMUNITY_Community 12|Community 12]]
- [[_COMMUNITY_Community 13|Community 13]]
- [[_COMMUNITY_Community 14|Community 14]]
- [[_COMMUNITY_Community 15|Community 15]]
- [[_COMMUNITY_Community 16|Community 16]]
- [[_COMMUNITY_Community 17|Community 17]]
- [[_COMMUNITY_Community 18|Community 18]]
- [[_COMMUNITY_Community 19|Community 19]]
- [[_COMMUNITY_Community 20|Community 20]]
- [[_COMMUNITY_Community 21|Community 21]]
- [[_COMMUNITY_Community 22|Community 22]]
- [[_COMMUNITY_Community 23|Community 23]]
- [[_COMMUNITY_Community 24|Community 24]]
- [[_COMMUNITY_Community 25|Community 25]]
- [[_COMMUNITY_Community 34|Community 34]]
- [[_COMMUNITY_Community 35|Community 35]]
- [[_COMMUNITY_Community 36|Community 36]]
- [[_COMMUNITY_Community 37|Community 37]]
- [[_COMMUNITY_Community 38|Community 38]]
- [[_COMMUNITY_Community 39|Community 39]]
- [[_COMMUNITY_Community 40|Community 40]]
- [[_COMMUNITY_Community 41|Community 41]]
- [[_COMMUNITY_Community 42|Community 42]]
- [[_COMMUNITY_Community 43|Community 43]]
- [[_COMMUNITY_Community 44|Community 44]]
- [[_COMMUNITY_Community 45|Community 45]]
- [[_COMMUNITY_Community 46|Community 46]]
- [[_COMMUNITY_Community 47|Community 47]]
- [[_COMMUNITY_Community 48|Community 48]]
- [[_COMMUNITY_Community 49|Community 49]]
- [[_COMMUNITY_Community 50|Community 50]]
- [[_COMMUNITY_Community 51|Community 51]]
- [[_COMMUNITY_Community 52|Community 52]]
- [[_COMMUNITY_Community 53|Community 53]]
- [[_COMMUNITY_Community 54|Community 54]]
- [[_COMMUNITY_Community 55|Community 55]]
- [[_COMMUNITY_Community 56|Community 56]]
- [[_COMMUNITY_Community 57|Community 57]]
- [[_COMMUNITY_Community 58|Community 58]]
- [[_COMMUNITY_Community 59|Community 59]]
- [[_COMMUNITY_Community 60|Community 60]]
- [[_COMMUNITY_Community 61|Community 61]]
- [[_COMMUNITY_Community 62|Community 62]]
- [[_COMMUNITY_Community 63|Community 63]]
- [[_COMMUNITY_Community 64|Community 64]]
- [[_COMMUNITY_Community 65|Community 65]]
- [[_COMMUNITY_Community 66|Community 66]]
- [[_COMMUNITY_Community 67|Community 67]]
- [[_COMMUNITY_Community 68|Community 68]]
- [[_COMMUNITY_Community 69|Community 69]]
- [[_COMMUNITY_Community 70|Community 70]]
- [[_COMMUNITY_Community 71|Community 71]]
- [[_COMMUNITY_Community 72|Community 72]]
- [[_COMMUNITY_Community 73|Community 73]]
- [[_COMMUNITY_Community 74|Community 74]]
- [[_COMMUNITY_Community 75|Community 75]]
- [[_COMMUNITY_Community 76|Community 76]]
- [[_COMMUNITY_Community 77|Community 77]]
- [[_COMMUNITY_Community 78|Community 78]]
- [[_COMMUNITY_Community 79|Community 79]]
- [[_COMMUNITY_Community 80|Community 80]]
- [[_COMMUNITY_Community 81|Community 81]]
- [[_COMMUNITY_Community 82|Community 82]]
- [[_COMMUNITY_Community 83|Community 83]]
- [[_COMMUNITY_Community 84|Community 84]]
- [[_COMMUNITY_Community 85|Community 85]]
- [[_COMMUNITY_Community 86|Community 86]]
- [[_COMMUNITY_Community 87|Community 87]]
- [[_COMMUNITY_Community 88|Community 88]]
- [[_COMMUNITY_Community 89|Community 89]]
- [[_COMMUNITY_Community 90|Community 90]]
- [[_COMMUNITY_Community 91|Community 91]]
- [[_COMMUNITY_Community 92|Community 92]]
- [[_COMMUNITY_Community 93|Community 93]]
- [[_COMMUNITY_Community 94|Community 94]]
- [[_COMMUNITY_Community 95|Community 95]]
- [[_COMMUNITY_Community 96|Community 96]]
- [[_COMMUNITY_Community 97|Community 97]]
- [[_COMMUNITY_Community 98|Community 98]]
- [[_COMMUNITY_Community 99|Community 99]]
- [[_COMMUNITY_Community 100|Community 100]]
- [[_COMMUNITY_Community 101|Community 101]]
- [[_COMMUNITY_Community 102|Community 102]]
- [[_COMMUNITY_Community 103|Community 103]]
- [[_COMMUNITY_Community 104|Community 104]]
- [[_COMMUNITY_Community 105|Community 105]]
- [[_COMMUNITY_Community 106|Community 106]]

## God Nodes (most connected - your core abstractions)
1. `Logger` - 34 edges
2. `Centralized Config (core/config.py)` - 18 edges
3. `MatadorksApp` - 17 edges
4. `info()` - 15 edges
5. `success()` - 13 edges
6. `GitHubProxyFetcher` - 12 edges
7. `ProxyPool` - 12 edges
8. `QueueManager` - 12 edges
9. `State` - 12 edges
10. `KeyboardListener` - 11 edges

## Surprising Connections (you probably didn't know these)
- `Get seed domains for a TLD via Bing search.` --uses--> `Logger`  [INFERRED]
  modules/harvester_wayback.py → .gemini/worktrees/feat/time-range-filter/core/logger.py
- `Query Wayback CDX API for a domain, return SQLi-candidate URLs.` --uses--> `Logger`  [INFERRED]
  modules/harvester_wayback.py → .gemini/worktrees/feat/time-range-filter/core/logger.py
- `Fetch recent domain names from crt.sh for a TLD.` --uses--> `Logger`  [INFERRED]
  modules/harvester_crt.py → .gemini/worktrees/feat/time-range-filter/core/logger.py
- `Probe domain with SQLi paths, add live URLs to queue.` --uses--> `Logger`  [INFERRED]
  modules/harvester_crt.py → .gemini/worktrees/feat/time-range-filter/core/logger.py
- `Thread-safe update of queue sizes from the orchestrator.` --uses--> `Logger`  [INFERRED]
  core/stats.py → .gemini/worktrees/feat/time-range-filter/core/logger.py

## Hyperedges (group relationships)
- **Core SQLi Pipeline Components** — dynamic_dorking, proxy_engine, multi_engine_search, smart_validator, sqlmap_automator, auto_looter [EXTRACTED 1.00]
- **AI Agent Coordination Framework** — claude_role, gemini_role, inbox_communication, ostava_directory [EXTRACTED 1.00]
- **Matadorks Streaming Pipeline** — bulk_scanner, proxy_pool, streaming_architecture, task_core_orchestrator [INFERRED 0.90]
- **Matadorks Role Hierarchy** — skill_senior_backend, skill_security_researcher, skill_code_reviewer, skill_llm_engineer [EXTRACTED 1.00]
- **Matadorks Role Framework** — role_security_researcher, role_code_reviewer, role_senior_backend [EXTRACTED 1.00]
- **SQLi Exploitation Pipeline** — data_sqli_dorks, role_security_researcher, data_pwned_summary [INFERRED 0.95]
- **Batch 4 SQL Injection Scan Targets** — btstu_endpoint, beyzam_live_endpoint, cmake_endpoint, cctv_endpoint, kleinanzeigen_endpoint, xenforo_endpoint, razredna_nastava_endpoint, hackforums_endpoint, beyzam_me_endpoint, meetup_endpoint, snapchat_endpoint, chatgpt_endpoint, alib_endpoint, istockphoto_endpoint, index_hu_endpoint, preservetube_endpoint, dronebydrone_endpoint, sqlinfo_endpoint, 3dmgame_endpoint, rutracker_endpoint, wordreference_endpoint, matheros_endpoint, worlddata_endpoint [INFERRED 0.95]
- **Localized Reconnaissance Pattern** — dork_regional_fr, target_lefigaro, target_impots_gouv [INFERRED 0.85]

## Communities

### Community 0 - "Community 0"
Cohesion: 0.11
Nodes (15): GitHandler, info(), _print(), set_quiet(), status(), success(), warning(), KeyboardListener (+7 more)

### Community 1 - "Community 1"
Cohesion: 0.1
Nodes (16): CommonCrawlHarvester, Fetch the most recent CommonCrawl index ID., Query CommonCrawl CDX for a domain, return SQLi-candidate URLs., HarvesterOrchestrator, Logger, QueueManager, Central nervous system for the Matadorks asynchronous streaming pipeline.     Ma, Central nervous system for the Matadorks streaming pipeline.     Manages queues (+8 more)

### Community 2 - "Community 2"
Cohesion: 0.11
Nodes (8): Centralized Config (core/config.py), Rationale: Centralizing Constants, GitHubProxyFetcher, get_async_session(), get_dynamic_sources(), ProxyPool, Paralelno povlacenje listi koristeci threadove za I/O., Asinhrono povlačenje listi proksija.

### Community 3 - "Community 3"
Cohesion: 0.18
Nodes (16): get_cffi_session(), Async context manager that mimics browser TLS fingerprint via curl-cffi., CRTHarvester, Fetch recent domain names from crt.sh for a TLD., Probe domain with SQLi paths, add live URLs to queue., bing(), brave(), duckduckgo() (+8 more)

### Community 4 - "Community 4"
Cohesion: 0.19
Nodes (18): generate_all(), generate_cve_dorks(), generate_light_dorks(), generate_niche_sqli_dorks(), generate_regional_param_dorks(), generate_sqli_error_dorks(), generate_subdomain_niche_dorks(), generate_taxonomy_dorks() (+10 more)

### Community 5 - "Community 5"
Cohesion: 0.19
Nodes (7): is_blacklisted(), is_sqli_candidate(), normalize_url(), run_worker(), standalone_main(), worker(), State

### Community 6 - "Community 6"
Cohesion: 0.26
Nodes (3): error(), run_mass_injection(), PremiumProxyScraper

### Community 7 - "Community 7"
Cohesion: 0.27
Nodes (3): Get seed domains for a TLD via Bing search., Query Wayback CDX API for a domain, return SQLi-candidate URLs., WaybackHarvester

### Community 8 - "Community 8"
Cohesion: 0.31
Nodes (3): run_mass_validation(), main(), Validator

### Community 9 - "Community 9"
Cohesion: 0.33
Nodes (2): AsyncExploiter, main()

### Community 10 - "Community 10"
Cohesion: 0.43
Nodes (4): AsyncInjector, _build_ghauri_args(), _build_sqlmap_args(), main()

### Community 11 - "Community 11"
Cohesion: 0.46
Nodes (1): GitHubHarvester

### Community 12 - "Community 12"
Cohesion: 0.25
Nodes (8): SQL Injection (SQLi), SQLMap Automation, Massive Niche Dorks 2026, SQL Injection Dorks List, Security Researcher Role, Target: forums.walla.co.il, Target: help.forumotion.com, Target: images-fio.6play.fr

### Community 13 - "Community 13"
Cohesion: 0.33
Nodes (6): Claude (Planner Role), Gemini (Implementer Role), Matadorks Project, Autonomous SQLi Pipeline, Queue-Based Pipeline Refactor, UV Dependency Manager

### Community 14 - "Community 14"
Cohesion: 0.5
Nodes (5): French Regional Dorks, SQL Error Fingerprint Dorks, Vulnerable SQLi Parameter Dorks, Impots Gouv FR Target, Le Figaro Target

### Community 15 - "Community 15"
Cohesion: 0.5
Nodes (4): Reactive Streaming Architecture, Core Orchestrator Task, Injector & Exploiter Worker Task, Queue System V2 Design

### Community 16 - "Community 16"
Cohesion: 0.5
Nodes (4): Asynchronous I/O, ThreadPoolExecutor, Rationale: Pipeline Resilience, Senior Backend Engineer Role

### Community 17 - "Community 17"
Cohesion: 0.67
Nodes (3): Adaptive Proxy Engine, Rationale: Mandatory SOCKS5 Proxies, Rationale: Avoiding Tor for Bulk Scanning

### Community 18 - "Community 18"
Cohesion: 0.67
Nodes (3): Per-Agent Inbox Protocol, Matadorks Workflow Skill, Senior Backend Role

### Community 19 - "Community 19"
Cohesion: 1.0
Nodes (2): Ghauri Fallback Integration, SQLMap Automator

### Community 20 - "Community 20"
Cohesion: 1.0
Nodes (2): Rationale: Slowing Rotation for Brave Search, Multi-Engine Search Scraper

### Community 21 - "Community 21"
Cohesion: 1.0
Nodes (2): Agent Communication Channel, Ostava (Private Intelligence)

### Community 22 - "Community 22"
Cohesion: 1.0
Nodes (2): Gemini CLI Brain Log, Stealth Scanning Techniques

### Community 23 - "Community 23"
Cohesion: 1.0
Nodes (2): Pwned Databases Summary, Test Execution Summary

### Community 24 - "Community 24"
Cohesion: 1.0
Nodes (2): WAF Evasion, Rationale: Evasion is Key

### Community 25 - "Community 25"
Cohesion: 1.0
Nodes (2): Niche Fingerprint Dorks, Danfoss Plus1 Forum Target

### Community 34 - "Community 34"
Cohesion: 1.0
Nodes (1): Checks if the URL contains any blacklisted keywords or domains.

### Community 35 - "Community 35"
Cohesion: 1.0
Nodes (1): Performs non-blocking HTTP check to see if the URL is alive.

### Community 36 - "Community 36"
Cohesion: 1.0
Nodes (1): Validates a single URL and handles persistence/queuing.

### Community 37 - "Community 37"
Cohesion: 1.0
Nodes (1): Main loop for the continuous async worker.

### Community 38 - "Community 38"
Cohesion: 1.0
Nodes (1): Checks if the URL contains any blacklisted keywords or domains.

### Community 39 - "Community 39"
Cohesion: 1.0
Nodes (1): Performs non-blocking HTTP check to see if the URL is alive.

### Community 40 - "Community 40"
Cohesion: 1.0
Nodes (1): Validates a single URL and handles persistence/queuing.

### Community 41 - "Community 41"
Cohesion: 1.0
Nodes (1): Main loop for the continuous async worker.

### Community 42 - "Community 42"
Cohesion: 1.0
Nodes (1): Checks if the URL contains any blacklisted keywords or domains.

### Community 43 - "Community 43"
Cohesion: 1.0
Nodes (1): Performs HTTP check to see if the URL is alive.

### Community 44 - "Community 44"
Cohesion: 1.0
Nodes (1): Validates a single URL and handles persistence/queuing.

### Community 45 - "Community 45"
Cohesion: 1.0
Nodes (1): Main loop for the continuous worker.

### Community 46 - "Community 46"
Cohesion: 1.0
Nodes (1): Entry point for the continuous validator worker.     :param in_q: Input queue (u

### Community 47 - "Community 47"
Cohesion: 1.0
Nodes (1): Helper to wait for some futures to complete.

### Community 48 - "Community 48"
Cohesion: 1.0
Nodes (1): Uklanja ANSI color kodove koji ometaju regex.

### Community 49 - "Community 49"
Cohesion: 1.0
Nodes (1): Izvlaci bitne informacije iz SQLMap outputa koristeci robustniji regex.

### Community 50 - "Community 50"
Cohesion: 1.0
Nodes (1): Dodaje rezultate u summary fajl odmah nakon svakog uspesnog pwn-a.

### Community 51 - "Community 51"
Cohesion: 1.0
Nodes (1): Ultra-brzi asinhroni port check.

### Community 52 - "Community 52"
Cohesion: 1.0
Nodes (1): Standardni HTTP test za proksije koji su prosli TCP ping.

### Community 53 - "Community 53"
Cohesion: 1.0
Nodes (1): Wrapper da bismo mogli pozvati build() iz sinhronog koda.

### Community 54 - "Community 54"
Cohesion: 1.0
Nodes (1): Google pretrazivanje kroz rotacijski proxy pool (free proxy liste).     'proxy'

### Community 55 - "Community 55"
Cohesion: 1.0
Nodes (1): Startpage — proxy za Google rezultate, radi kroz Tor.     Ne podrzava dork opera

### Community 56 - "Community 56"
Cohesion: 1.0
Nodes (1): Prevedi Google dork u Shodan filter sintaksu.

### Community 57 - "Community 57"
Cohesion: 1.0
Nodes (1): Shodan API — zahtijeva SHODAN_API_KEY env varijablu.

### Community 58 - "Community 58"
Cohesion: 1.0
Nodes (1): Prevedi Google dork u Censys filter sintaksu (v2 API).

### Community 59 - "Community 59"
Cohesion: 1.0
Nodes (1): Censys Search API v2 — zahtijeva CENSYS_API_ID i CENSYS_API_SECRET env varijable

### Community 60 - "Community 60"
Cohesion: 1.0
Nodes (1): ZoomEye API — zahtijeva ZOOMEYE_API_KEY env varijablu.

### Community 61 - "Community 61"
Cohesion: 1.0
Nodes (1): PublicWWW — pretražuje source code sajtova.

### Community 62 - "Community 62"
Cohesion: 1.0
Nodes (1): Dynamic Dork Generator

### Community 63 - "Community 63"
Cohesion: 1.0
Nodes (1): Smart URL Validator

### Community 64 - "Community 64"
Cohesion: 1.0
Nodes (1): Auto-Looter

### Community 65 - "Community 65"
Cohesion: 1.0
Nodes (1): Bugfix Exploiter Task

### Community 66 - "Community 66"
Cohesion: 1.0
Nodes (1): Dork Files Refactor Task

### Community 67 - "Community 67"
Cohesion: 1.0
Nodes (1): Dashboard TUI Task

### Community 68 - "Community 68"
Cohesion: 1.0
Nodes (1): Security Research Exploit Task

### Community 69 - "Community 69"
Cohesion: 1.0
Nodes (1): Scanner Engines Task

### Community 70 - "Community 70"
Cohesion: 1.0
Nodes (1): Exploiter Core Task

### Community 71 - "Community 71"
Cohesion: 1.0
Nodes (1): MemorySwap Status Report

### Community 72 - "Community 72"
Cohesion: 1.0
Nodes (1): Progress Report

### Community 73 - "Community 73"
Cohesion: 1.0
Nodes (1): Matadorks Features Documentation

### Community 74 - "Community 74"
Cohesion: 1.0
Nodes (1): Roadmap and Plan

### Community 75 - "Community 75"
Cohesion: 1.0
Nodes (1): Claude Project Summary

### Community 76 - "Community 76"
Cohesion: 1.0
Nodes (1): Dorks Eye v2.0 README

### Community 77 - "Community 77"
Cohesion: 1.0
Nodes (1): Security Researcher Role

### Community 78 - "Community 78"
Cohesion: 1.0
Nodes (1): Code Reviewer Role

### Community 79 - "Community 79"
Cohesion: 1.0
Nodes (1): LLM Engineer Role

### Community 80 - "Community 80"
Cohesion: 1.0
Nodes (1): Code Reviewer Role

### Community 81 - "Community 81"
Cohesion: 1.0
Nodes (1): https://blog.btstu.cn/?post=214

### Community 82 - "Community 82"
Cohesion: 1.0
Nodes (1): https://www.beyzam.live/?language=ja

### Community 83 - "Community 83"
Cohesion: 1.0
Nodes (1): https://cmake.org/Bug/view.php?id=7050

### Community 84 - "Community 84"
Cohesion: 1.0
Nodes (1): https://tv.cctv.com/?do=live

### Community 85 - "Community 85"
Cohesion: 1.0
Nodes (1): https://www.kleinanzeigen.de/s-kategorien.html?msockid=276a4fdafa5760753436589dfb8461f7

### Community 86 - "Community 86"
Cohesion: 1.0
Nodes (1): https://xenforo.com/?page=about

### Community 87 - "Community 87"
Cohesion: 1.0
Nodes (1): https://www.razredna-nastava.net/stranica.php?id=459

### Community 88 - "Community 88"
Cohesion: 1.0
Nodes (1): https://hackforums.net/showthread.php?tid=1179629

### Community 89 - "Community 89"
Cohesion: 1.0
Nodes (1): https://www.beyzam.me/misafir?affiliate_ref=4646

### Community 90 - "Community 90"
Cohesion: 1.0
Nodes (1): https://www.meetup.com/find/?msockid=3112f18cff9e6eec389ae6cbfe9a6f40

### Community 91 - "Community 91"
Cohesion: 1.0
Nodes (1): https://accounts.snapchat.com/v2/login?locale=fr-FR

### Community 92 - "Community 92"
Cohesion: 1.0
Nodes (1): https://chatgpt.org/chat?trk=public_post-text

### Community 93 - "Community 93"
Cohesion: 1.0
Nodes (1): https://www.alib.ru/yaf.php4?author=limnatis&title=manipulirovanie

### Community 94 - "Community 94"
Cohesion: 1.0
Nodes (1): https://www.istockphoto.com/de/fotos/Impfung?msockid=2f1d191d4f226b0815450e5a4e226a50

### Community 95 - "Community 95"
Cohesion: 1.0
Nodes (1): https://forum.index.hu/Article/showArticle?t=9184247

### Community 96 - "Community 96"
Cohesion: 1.0
Nodes (1): https://preservetube.com/watch?v=dl7O-7PjBOA

### Community 97 - "Community 97"
Cohesion: 1.0
Nodes (1): https://www.dronebydrone.com/en/noticia-ver.php/265/index.php?id=265

### Community 98 - "Community 98"
Cohesion: 1.0
Nodes (1): https://sqlinfo.ru/forum/viewtopic.php?id=4839

### Community 99 - "Community 99"
Cohesion: 1.0
Nodes (1): https://bbs.3dmgame.com/forum.php?gid=441

### Community 100 - "Community 100"
Cohesion: 1.0
Nodes (1): https://rutracker.org/forum/viewtopic.php?t=6424229

### Community 101 - "Community 101"
Cohesion: 1.0
Nodes (1): https://www.wordreference.com/es/en/translation.asp?spen=motociclismo

### Community 102 - "Community 102"
Cohesion: 1.0
Nodes (1): https://matheros.fr/eleves/?openLastExo=62

### Community 103 - "Community 103"
Cohesion: 1.0
Nodes (1): https://www.worlddata.info/climate-comparison.php?r1=canada&r2=russia

### Community 104 - "Community 104"
Cohesion: 1.0
Nodes (1): Modern Leaks Dorks

### Community 105 - "Community 105"
Cohesion: 1.0
Nodes (1): German Regional Dorks

### Community 106 - "Community 106"
Cohesion: 1.0
Nodes (1): Outlook Office365 Target

## Knowledge Gaps
- **123 isolated node(s):** `Čita dork fajl, ignorišući komentare i prazne linije.`, `SQL greska + ranjivi param na istoj stranici.`, `Regionalni parametri sa site: operatorom.`, `Niche fingerprint + ranjivi param (demografski targeting).`, `Dorkovi bazirani na specifičnim CVE obrascima (2025-2026).` (+118 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **Thin community `Community 9`** (10 nodes): `AsyncExploiter`, `.exploit()`, `.__init__()`, `.parse_sqlmap_output()`, `._play_pwned_sound()`, `.run()`, `.save_summary()`, `.strip_ansi()`, `main()`, `exploiter.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 11`** (8 nodes): `GitHubHarvester`, `._extract_db_hosts()`, `._extract_from_file()`, `._filter_url()`, `.__init__()`, `._rate_limit()`, `.run()`, `._search_dork()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 19`** (2 nodes): `Ghauri Fallback Integration`, `SQLMap Automator`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 20`** (2 nodes): `Rationale: Slowing Rotation for Brave Search`, `Multi-Engine Search Scraper`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 21`** (2 nodes): `Agent Communication Channel`, `Ostava (Private Intelligence)`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 22`** (2 nodes): `Gemini CLI Brain Log`, `Stealth Scanning Techniques`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 23`** (2 nodes): `Pwned Databases Summary`, `Test Execution Summary`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 24`** (2 nodes): `WAF Evasion`, `Rationale: Evasion is Key`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 25`** (2 nodes): `Niche Fingerprint Dorks`, `Danfoss Plus1 Forum Target`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 34`** (1 nodes): `Checks if the URL contains any blacklisted keywords or domains.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 35`** (1 nodes): `Performs non-blocking HTTP check to see if the URL is alive.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 36`** (1 nodes): `Validates a single URL and handles persistence/queuing.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 37`** (1 nodes): `Main loop for the continuous async worker.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 38`** (1 nodes): `Checks if the URL contains any blacklisted keywords or domains.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 39`** (1 nodes): `Performs non-blocking HTTP check to see if the URL is alive.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 40`** (1 nodes): `Validates a single URL and handles persistence/queuing.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 41`** (1 nodes): `Main loop for the continuous async worker.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 42`** (1 nodes): `Checks if the URL contains any blacklisted keywords or domains.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 43`** (1 nodes): `Performs HTTP check to see if the URL is alive.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 44`** (1 nodes): `Validates a single URL and handles persistence/queuing.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 45`** (1 nodes): `Main loop for the continuous worker.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 46`** (1 nodes): `Entry point for the continuous validator worker.     :param in_q: Input queue (u`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 47`** (1 nodes): `Helper to wait for some futures to complete.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 48`** (1 nodes): `Uklanja ANSI color kodove koji ometaju regex.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 49`** (1 nodes): `Izvlaci bitne informacije iz SQLMap outputa koristeci robustniji regex.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 50`** (1 nodes): `Dodaje rezultate u summary fajl odmah nakon svakog uspesnog pwn-a.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 51`** (1 nodes): `Ultra-brzi asinhroni port check.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 52`** (1 nodes): `Standardni HTTP test za proksije koji su prosli TCP ping.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 53`** (1 nodes): `Wrapper da bismo mogli pozvati build() iz sinhronog koda.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 54`** (1 nodes): `Google pretrazivanje kroz rotacijski proxy pool (free proxy liste).     'proxy'`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 55`** (1 nodes): `Startpage — proxy za Google rezultate, radi kroz Tor.     Ne podrzava dork opera`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 56`** (1 nodes): `Prevedi Google dork u Shodan filter sintaksu.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 57`** (1 nodes): `Shodan API — zahtijeva SHODAN_API_KEY env varijablu.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 58`** (1 nodes): `Prevedi Google dork u Censys filter sintaksu (v2 API).`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 59`** (1 nodes): `Censys Search API v2 — zahtijeva CENSYS_API_ID i CENSYS_API_SECRET env varijable`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 60`** (1 nodes): `ZoomEye API — zahtijeva ZOOMEYE_API_KEY env varijablu.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 61`** (1 nodes): `PublicWWW — pretražuje source code sajtova.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 62`** (1 nodes): `Dynamic Dork Generator`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 63`** (1 nodes): `Smart URL Validator`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 64`** (1 nodes): `Auto-Looter`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 65`** (1 nodes): `Bugfix Exploiter Task`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 66`** (1 nodes): `Dork Files Refactor Task`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 67`** (1 nodes): `Dashboard TUI Task`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 68`** (1 nodes): `Security Research Exploit Task`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 69`** (1 nodes): `Scanner Engines Task`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 70`** (1 nodes): `Exploiter Core Task`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 71`** (1 nodes): `MemorySwap Status Report`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 72`** (1 nodes): `Progress Report`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 73`** (1 nodes): `Matadorks Features Documentation`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 74`** (1 nodes): `Roadmap and Plan`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 75`** (1 nodes): `Claude Project Summary`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 76`** (1 nodes): `Dorks Eye v2.0 README`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 77`** (1 nodes): `Security Researcher Role`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 78`** (1 nodes): `Code Reviewer Role`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 79`** (1 nodes): `LLM Engineer Role`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 80`** (1 nodes): `Code Reviewer Role`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 81`** (1 nodes): `https://blog.btstu.cn/?post=214`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 82`** (1 nodes): `https://www.beyzam.live/?language=ja`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 83`** (1 nodes): `https://cmake.org/Bug/view.php?id=7050`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 84`** (1 nodes): `https://tv.cctv.com/?do=live`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 85`** (1 nodes): `https://www.kleinanzeigen.de/s-kategorien.html?msockid=276a4fdafa5760753436589dfb8461f7`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 86`** (1 nodes): `https://xenforo.com/?page=about`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 87`** (1 nodes): `https://www.razredna-nastava.net/stranica.php?id=459`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 88`** (1 nodes): `https://hackforums.net/showthread.php?tid=1179629`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 89`** (1 nodes): `https://www.beyzam.me/misafir?affiliate_ref=4646`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 90`** (1 nodes): `https://www.meetup.com/find/?msockid=3112f18cff9e6eec389ae6cbfe9a6f40`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 91`** (1 nodes): `https://accounts.snapchat.com/v2/login?locale=fr-FR`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 92`** (1 nodes): `https://chatgpt.org/chat?trk=public_post-text`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 93`** (1 nodes): `https://www.alib.ru/yaf.php4?author=limnatis&title=manipulirovanie`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 94`** (1 nodes): `https://www.istockphoto.com/de/fotos/Impfung?msockid=2f1d191d4f226b0815450e5a4e226a50`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 95`** (1 nodes): `https://forum.index.hu/Article/showArticle?t=9184247`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 96`** (1 nodes): `https://preservetube.com/watch?v=dl7O-7PjBOA`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 97`** (1 nodes): `https://www.dronebydrone.com/en/noticia-ver.php/265/index.php?id=265`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 98`** (1 nodes): `https://sqlinfo.ru/forum/viewtopic.php?id=4839`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 99`** (1 nodes): `https://bbs.3dmgame.com/forum.php?gid=441`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 100`** (1 nodes): `https://rutracker.org/forum/viewtopic.php?t=6424229`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 101`** (1 nodes): `https://www.wordreference.com/es/en/translation.asp?spen=motociclismo`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 102`** (1 nodes): `https://matheros.fr/eleves/?openLastExo=62`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 103`** (1 nodes): `https://www.worlddata.info/climate-comparison.php?r1=canada&r2=russia`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 104`** (1 nodes): `Modern Leaks Dorks`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 105`** (1 nodes): `German Regional Dorks`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 106`** (1 nodes): `Outlook Office365 Target`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Logger` connect `Community 1` to `Community 0`, `Community 2`, `Community 3`, `Community 6`, `Community 7`, `Community 11`?**
  _High betweenness centrality (0.087) - this node is a cross-community bridge._
- **Why does `Centralized Config (core/config.py)` connect `Community 2` to `Community 1`, `Community 3`, `Community 4`, `Community 5`, `Community 7`, `Community 8`, `Community 9`, `Community 10`?**
  _High betweenness centrality (0.048) - this node is a cross-community bridge._
- **Why does `State` connect `Community 5` to `Community 0`, `Community 3`, `Community 4`?**
  _High betweenness centrality (0.028) - this node is a cross-community bridge._
- **Are the 33 inferred relationships involving `Logger` (e.g. with `KeyboardListener` and `MatadorksApp`) actually correct?**
  _`Logger` has 33 INFERRED edges - model-reasoned connections that need verification._
- **Are the 6 inferred relationships involving `MatadorksApp` (e.g. with `Logger` and `State`) actually correct?**
  _`MatadorksApp` has 6 INFERRED edges - model-reasoned connections that need verification._
- **Are the 13 inferred relationships involving `info()` (e.g. with `.run()` and `.run_pipeline()`) actually correct?**
  _`info()` has 13 INFERRED edges - model-reasoned connections that need verification._
- **Are the 11 inferred relationships involving `success()` (e.g. with `.sync_dependencies()` and `._execute_phases()`) actually correct?**
  _`success()` has 11 INFERRED edges - model-reasoned connections that need verification._