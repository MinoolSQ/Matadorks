# Graph Report - .  (2026-04-26)

## Corpus Check
- 131 files · ~53,747 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 280 nodes · 462 edges · 44 communities detected
- Extraction: 71% EXTRACTED · 29% INFERRED · 0% AMBIGUOUS · INFERRED: 132 edges (avg confidence: 0.76)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- [[_COMMUNITY_Core Infrastructure|Core Infrastructure]]
- [[_COMMUNITY_Proxy & Scanner Core|Proxy & Scanner Core]]
- [[_COMMUNITY_Search & HTTP Verification|Search & HTTP Verification]]
- [[_COMMUNITY_SQLi Scan Targets|SQLi Scan Targets]]
- [[_COMMUNITY_Dork Generation Logic|Dork Generation Logic]]
- [[_COMMUNITY_Configuration & Exploit Base|Configuration & Exploit Base]]
- [[_COMMUNITY_URL Validation Module|URL Validation Module]]
- [[_COMMUNITY_SQLMap & Ghauri Injectors|SQLMap & Ghauri Injectors]]
- [[_COMMUNITY_SQLi Research & Data|SQLi Research & Data]]
- [[_COMMUNITY_Project Strategy & Roles|Project Strategy & Roles]]
- [[_COMMUNITY_Regional Dorking (FR)|Regional Dorking (FR)]]
- [[_COMMUNITY_Streaming Architecture|Streaming Architecture]]
- [[_COMMUNITY_Backend Performance & Resilience|Backend Performance & Resilience]]
- [[_COMMUNITY_Proxy Strategy|Proxy Strategy]]
- [[_COMMUNITY_Memory & Scaling Reports|Memory & Scaling Reports]]
- [[_COMMUNITY_Workflow & Communications|Workflow & Communications]]
- [[_COMMUNITY_Search Scraper Strategy|Search Scraper Strategy]]
- [[_COMMUNITY_Exploitation Tools|Exploitation Tools]]
- [[_COMMUNITY_Internal Intel (Ostava)|Internal Intel (Ostava)]]
- [[_COMMUNITY_Stealth & Log Analysis|Stealth & Log Analysis]]
- [[_COMMUNITY_Pwned Databases Summary (Community 20)|Pwned Databases Summary (Community 20)]]
- [[_COMMUNITY_WAF Evasion (Community 21)|WAF Evasion (Community 21)]]
- [[_COMMUNITY_Niche Fingerprint Dorks (Community 22)|Niche Fingerprint Dorks (Community 22)]]
- [[_COMMUNITY_Dynamic Dork Generator (Community 33)|Dynamic Dork Generator (Community 33)]]
- [[_COMMUNITY_Smart URL Validator (Community 34)|Smart URL Validator (Community 34)]]
- [[_COMMUNITY_Auto-Looter (Community 35)|Auto-Looter (Community 35)]]
- [[_COMMUNITY_Bugfix Exploiter Task (Community 36)|Bugfix Exploiter Task (Community 36)]]
- [[_COMMUNITY_Dork Files Refactor Task (Community 37)|Dork Files Refactor Task (Community 37)]]
- [[_COMMUNITY_Dashboard TUI Task (Community 38)|Dashboard TUI Task (Community 38)]]
- [[_COMMUNITY_Security Research Exploit Task (Community 39)|Security Research Exploit Task (Community 39)]]
- [[_COMMUNITY_Scanner Engines Task (Community 40)|Scanner Engines Task (Community 40)]]
- [[_COMMUNITY_Exploiter Core Task (Community 41)|Exploiter Core Task (Community 41)]]
- [[_COMMUNITY_Progress Report (Community 42)|Progress Report (Community 42)]]
- [[_COMMUNITY_Matadorks Features Documentation (Community 43)|Matadorks Features Documentation (Community 43)]]
- [[_COMMUNITY_Roadmap and Plan (Community 44)|Roadmap and Plan (Community 44)]]
- [[_COMMUNITY_Claude Project Summary (Community 45)|Claude Project Summary (Community 45)]]
- [[_COMMUNITY_Dorks Eye v2.0 README (Community 46)|Dorks Eye v2.0 README (Community 46)]]
- [[_COMMUNITY_Security Researcher Role (Community 47)|Security Researcher Role (Community 47)]]
- [[_COMMUNITY_Code Reviewer Role (Community 48)|Code Reviewer Role (Community 48)]]
- [[_COMMUNITY_LLM Engineer Role (Community 49)|LLM Engineer Role (Community 49)]]
- [[_COMMUNITY_Code Reviewer Role (Community 50)|Code Reviewer Role (Community 50)]]
- [[_COMMUNITY_Modern Leaks Dorks (Community 51)|Modern Leaks Dorks (Community 51)]]
- [[_COMMUNITY_German Regional Dorks (Community 52)|German Regional Dorks (Community 52)]]
- [[_COMMUNITY_Outlook Office365 Target (Community 53)|Outlook Office365 Target (Community 53)]]

## God Nodes (most connected - your core abstractions)
1. `Standard sqlmap Scan Configuration` - 23 edges
2. `MatadorksApp` - 21 edges
3. `Centralized Config (core/config.py)` - 17 edges
4. `Logger` - 15 edges
5. `info()` - 14 edges
6. `QueueManager` - 13 edges
7. `ProxyPool` - 12 edges
8. `KeyboardListener` - 11 edges
9. `success()` - 11 edges
10. `State` - 11 edges

## Surprising Connections (you probably didn't know these)
- `Gemini (Implementer Role)` --implements--> `Matadorks Project`  [INFERRED]
  CLAUDE.md → README.md
- `Queue-Based Pipeline Refactor` --conceptually_related_to--> `Autonomous SQLi Pipeline`  [INFERRED]
  ostava/tasks/scanner-worker.md → CLAUDE.md
- `Rationale: Centralizing Constants` --rationale_for--> `Centralized Config (core/config.py)`  [EXTRACTED]
  CLAUDE.md → ostava/tasks/config-worker.md
- `Matadorks Workflow Skill` --references--> `Per-Agent Inbox Protocol`  [INFERRED]
  skills/matadorks-workflow/SKILL.md → ostava/inbox/README.md
- `Senior Backend Role` --conceptually_related_to--> `Matadorks Workflow Skill`  [INFERRED]
  ostava/skillovi/senior-backend.md → skills/matadorks-workflow/SKILL.md

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

### Community 0 - "Core Infrastructure"
Cohesion: 0.08
Nodes (19): GitHandler, dork(), error(), info(), Logger, status(), success(), warning() (+11 more)

### Community 1 - "Proxy & Scanner Core"
Cohesion: 0.14
Nodes (15): get_dynamic_sources(), get_google_pool(), ProxyPool, Wrapper da bismo mogli pozvati build() iz sinhronog koda., Paralelno povlacenje listi koristeci threadove za I/O., Ultra-brzi asinhroni port check., classify_result(), is_blacklisted() (+7 more)

### Community 2 - "Search & HTTP Verification"
Cohesion: 0.18
Nodes (23): Standardni HTTP test za proksije koji su prosli TCP ping., bing(), brave(), censys(), _dork_to_censys_query(), _dork_to_shodan_query(), duckduckgo(), get_random_ua() (+15 more)

### Community 3 - "SQLi Scan Targets"
Cohesion: 0.08
Nodes (24): https://bbs.3dmgame.com/forum.php?gid=441, https://www.alib.ru/yaf.php4?author=limnatis&title=manipulirovanie, https://www.beyzam.live/?language=ja, https://www.beyzam.me/misafir?affiliate_ref=4646, https://blog.btstu.cn/?post=214, https://tv.cctv.com/?do=live, https://chatgpt.org/chat?trk=public_post-text, https://cmake.org/Bug/view.php?id=7050 (+16 more)

### Community 4 - "Dork Generation Logic"
Cohesion: 0.2
Nodes (12): generate_all(), generate_light_dorks(), generate_niche_sqli_dorks(), generate_regional_param_dorks(), generate_sqli_error_dorks(), _load_list(), _load_regional(), SQL greska + ranjivi param na istoj stranici. (+4 more)

### Community 5 - "Configuration & Exploit Base"
Cohesion: 0.21
Nodes (8): Centralized Config (core/config.py), Rationale: Centralizing Constants, Exploiter, main(), Dodaje rezultate u summary fajl odmah nakon svakog uspesnog pwn-a., Uklanja ANSI color kodove koji ometaju regex., Izvlaci bitne informacije iz SQLMap outputa koristeci robustniji regex., _setup_logging()

### Community 6 - "URL Validation Module"
Cohesion: 0.2
Nodes (7): main(), Checks if the URL contains any blacklisted keywords or domains., Performs HTTP check to see if the URL is alive., Validates a single URL and handles persistence/queuing., Main loop for the continuous worker., Entry point for the continuous validator worker.     :param in_q: Input queue (u, Validator

### Community 7 - "SQLMap & Ghauri Injectors"
Cohesion: 0.35
Nodes (4): _build_ghauri_args(), _build_sqlmap_args(), main(), SQLMapManager

### Community 8 - "SQLi Research & Data"
Cohesion: 0.25
Nodes (8): SQL Injection (SQLi), SQLMap Automation, Massive Niche Dorks 2026, SQL Injection Dorks List, Security Researcher Role, Target: forums.walla.co.il, Target: help.forumotion.com, Target: images-fio.6play.fr

### Community 9 - "Project Strategy & Roles"
Cohesion: 0.33
Nodes (6): Claude (Planner Role), Gemini (Implementer Role), Matadorks Project, Autonomous SQLi Pipeline, Queue-Based Pipeline Refactor, UV Dependency Manager

### Community 10 - "Regional Dorking (FR)"
Cohesion: 0.5
Nodes (5): French Regional Dorks, SQL Error Fingerprint Dorks, Vulnerable SQLi Parameter Dorks, Impots Gouv FR Target, Le Figaro Target

### Community 11 - "Streaming Architecture"
Cohesion: 0.5
Nodes (4): Reactive Streaming Architecture, Core Orchestrator Task, Injector & Exploiter Worker Task, Queue System V2 Design

### Community 12 - "Backend Performance & Resilience"
Cohesion: 0.5
Nodes (4): Asynchronous I/O, ThreadPoolExecutor, Rationale: Pipeline Resilience, Senior Backend Engineer Role

### Community 13 - "Proxy Strategy"
Cohesion: 0.67
Nodes (3): Adaptive Proxy Engine, Rationale: Mandatory SOCKS5 Proxies, Rationale: Avoiding Tor for Bulk Scanning

### Community 14 - "Memory & Scaling Reports"
Cohesion: 0.67
Nodes (3): MemorySwap Status Report, Bulk Scanner, Proxy Pool System

### Community 15 - "Workflow & Communications"
Cohesion: 0.67
Nodes (3): Per-Agent Inbox Protocol, Matadorks Workflow Skill, Senior Backend Role

### Community 16 - "Search Scraper Strategy"
Cohesion: 1.0
Nodes (2): Rationale: Slowing Rotation for Brave Search, Multi-Engine Search Scraper

### Community 17 - "Exploitation Tools"
Cohesion: 1.0
Nodes (2): Ghauri Fallback Integration, SQLMap Automator

### Community 18 - "Internal Intel (Ostava)"
Cohesion: 1.0
Nodes (2): Agent Communication Channel, Ostava (Private Intelligence)

### Community 19 - "Stealth & Log Analysis"
Cohesion: 1.0
Nodes (2): Gemini CLI Brain Log, Stealth Scanning Techniques

### Community 20 - "Pwned Databases Summary (Community 20)"
Cohesion: 1.0
Nodes (2): Pwned Databases Summary, Test Execution Summary

### Community 21 - "WAF Evasion (Community 21)"
Cohesion: 1.0
Nodes (2): WAF Evasion, Rationale: Evasion is Key

### Community 22 - "Niche Fingerprint Dorks (Community 22)"
Cohesion: 1.0
Nodes (2): Niche Fingerprint Dorks, Danfoss Plus1 Forum Target

### Community 33 - "Dynamic Dork Generator (Community 33)"
Cohesion: 1.0
Nodes (1): Dynamic Dork Generator

### Community 34 - "Smart URL Validator (Community 34)"
Cohesion: 1.0
Nodes (1): Smart URL Validator

### Community 35 - "Auto-Looter (Community 35)"
Cohesion: 1.0
Nodes (1): Auto-Looter

### Community 36 - "Bugfix Exploiter Task (Community 36)"
Cohesion: 1.0
Nodes (1): Bugfix Exploiter Task

### Community 37 - "Dork Files Refactor Task (Community 37)"
Cohesion: 1.0
Nodes (1): Dork Files Refactor Task

### Community 38 - "Dashboard TUI Task (Community 38)"
Cohesion: 1.0
Nodes (1): Dashboard TUI Task

### Community 39 - "Security Research Exploit Task (Community 39)"
Cohesion: 1.0
Nodes (1): Security Research Exploit Task

### Community 40 - "Scanner Engines Task (Community 40)"
Cohesion: 1.0
Nodes (1): Scanner Engines Task

### Community 41 - "Exploiter Core Task (Community 41)"
Cohesion: 1.0
Nodes (1): Exploiter Core Task

### Community 42 - "Progress Report (Community 42)"
Cohesion: 1.0
Nodes (1): Progress Report

### Community 43 - "Matadorks Features Documentation (Community 43)"
Cohesion: 1.0
Nodes (1): Matadorks Features Documentation

### Community 44 - "Roadmap and Plan (Community 44)"
Cohesion: 1.0
Nodes (1): Roadmap and Plan

### Community 45 - "Claude Project Summary (Community 45)"
Cohesion: 1.0
Nodes (1): Claude Project Summary

### Community 46 - "Dorks Eye v2.0 README (Community 46)"
Cohesion: 1.0
Nodes (1): Dorks Eye v2.0 README

### Community 47 - "Security Researcher Role (Community 47)"
Cohesion: 1.0
Nodes (1): Security Researcher Role

### Community 48 - "Code Reviewer Role (Community 48)"
Cohesion: 1.0
Nodes (1): Code Reviewer Role

### Community 49 - "LLM Engineer Role (Community 49)"
Cohesion: 1.0
Nodes (1): LLM Engineer Role

### Community 50 - "Code Reviewer Role (Community 50)"
Cohesion: 1.0
Nodes (1): Code Reviewer Role

### Community 51 - "Modern Leaks Dorks (Community 51)"
Cohesion: 1.0
Nodes (1): Modern Leaks Dorks

### Community 52 - "German Regional Dorks (Community 52)"
Cohesion: 1.0
Nodes (1): German Regional Dorks

### Community 53 - "Outlook Office365 Target (Community 53)"
Cohesion: 1.0
Nodes (1): Outlook Office365 Target

## Knowledge Gaps
- **102 isolated node(s):** `Checks if the URL contains any blacklisted keywords or domains.`, `Performs HTTP check to see if the URL is alive.`, `Validates a single URL and handles persistence/queuing.`, `Main loop for the continuous worker.`, `Entry point for the continuous validator worker.     :param in_q: Input queue (u` (+97 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **Thin community `Search Scraper Strategy`** (2 nodes): `Rationale: Slowing Rotation for Brave Search`, `Multi-Engine Search Scraper`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Exploitation Tools`** (2 nodes): `Ghauri Fallback Integration`, `SQLMap Automator`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Internal Intel (Ostava)`** (2 nodes): `Agent Communication Channel`, `Ostava (Private Intelligence)`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Stealth & Log Analysis`** (2 nodes): `Gemini CLI Brain Log`, `Stealth Scanning Techniques`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Pwned Databases Summary (Community 20)`** (2 nodes): `Pwned Databases Summary`, `Test Execution Summary`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `WAF Evasion (Community 21)`** (2 nodes): `WAF Evasion`, `Rationale: Evasion is Key`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Niche Fingerprint Dorks (Community 22)`** (2 nodes): `Niche Fingerprint Dorks`, `Danfoss Plus1 Forum Target`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Dynamic Dork Generator (Community 33)`** (1 nodes): `Dynamic Dork Generator`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Smart URL Validator (Community 34)`** (1 nodes): `Smart URL Validator`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Auto-Looter (Community 35)`** (1 nodes): `Auto-Looter`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Bugfix Exploiter Task (Community 36)`** (1 nodes): `Bugfix Exploiter Task`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Dork Files Refactor Task (Community 37)`** (1 nodes): `Dork Files Refactor Task`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Dashboard TUI Task (Community 38)`** (1 nodes): `Dashboard TUI Task`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Security Research Exploit Task (Community 39)`** (1 nodes): `Security Research Exploit Task`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Scanner Engines Task (Community 40)`** (1 nodes): `Scanner Engines Task`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Exploiter Core Task (Community 41)`** (1 nodes): `Exploiter Core Task`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Progress Report (Community 42)`** (1 nodes): `Progress Report`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Matadorks Features Documentation (Community 43)`** (1 nodes): `Matadorks Features Documentation`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Roadmap and Plan (Community 44)`** (1 nodes): `Roadmap and Plan`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Claude Project Summary (Community 45)`** (1 nodes): `Claude Project Summary`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Dorks Eye v2.0 README (Community 46)`** (1 nodes): `Dorks Eye v2.0 README`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Security Researcher Role (Community 47)`** (1 nodes): `Security Researcher Role`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Code Reviewer Role (Community 48)`** (1 nodes): `Code Reviewer Role`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `LLM Engineer Role (Community 49)`** (1 nodes): `LLM Engineer Role`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Code Reviewer Role (Community 50)`** (1 nodes): `Code Reviewer Role`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Modern Leaks Dorks (Community 51)`** (1 nodes): `Modern Leaks Dorks`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `German Regional Dorks (Community 52)`** (1 nodes): `German Regional Dorks`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Outlook Office365 Target (Community 53)`** (1 nodes): `Outlook Office365 Target`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Centralized Config (core/config.py)` connect `Configuration & Exploit Base` to `Core Infrastructure`, `Proxy & Scanner Core`, `Dork Generation Logic`, `URL Validation Module`, `SQLMap & Ghauri Injectors`?**
  _High betweenness centrality (0.057) - this node is a cross-community bridge._
- **Why does `State` connect `Dork Generation Logic` to `Core Infrastructure`, `Search & HTTP Verification`?**
  _High betweenness centrality (0.050) - this node is a cross-community bridge._
- **Why does `MatadorksApp` connect `Core Infrastructure` to `Proxy & Scanner Core`, `Dork Generation Logic`?**
  _High betweenness centrality (0.045) - this node is a cross-community bridge._
- **Are the 5 inferred relationships involving `MatadorksApp` (e.g. with `Logger` and `State`) actually correct?**
  _`MatadorksApp` has 5 INFERRED edges - model-reasoned connections that need verification._
- **Are the 13 inferred relationships involving `Logger` (e.g. with `KeyboardListener` and `MatadorksApp`) actually correct?**
  _`Logger` has 13 INFERRED edges - model-reasoned connections that need verification._
- **Are the 12 inferred relationships involving `info()` (e.g. with `.run()` and `.run_pipeline()`) actually correct?**
  _`info()` has 12 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Checks if the URL contains any blacklisted keywords or domains.`, `Performs HTTP check to see if the URL is alive.`, `Validates a single URL and handles persistence/queuing.` to the rest of the system?**
  _102 weakly-connected nodes found - possible documentation gaps or missing edges._