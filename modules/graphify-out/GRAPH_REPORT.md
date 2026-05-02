# Graph Report - modules  (2026-05-02)

## Corpus Check
- 19 files · ~6,762 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 168 nodes · 243 edges · 12 communities detected
- Extraction: 87% EXTRACTED · 13% INFERRED · 0% AMBIGUOUS · INFERRED: 32 edges (avg confidence: 0.63)
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

## God Nodes (most connected - your core abstractions)
1. `GHDBProvider` - 20 edges
2. `ExploiterService` - 11 edges
3. `ScannerService` - 11 edges
4. `_load_list()` - 10 edges
5. `AsyncExploiter` - 10 edges
6. `GitHubHarvester` - 10 edges
7. `WaybackHarvester` - 9 edges
8. `ValidatorService` - 9 edges
9. `InjectorService` - 9 edges
10. `CRTHarvester` - 9 edges

## Surprising Connections (you probably didn't know these)
- `Independent service for dork scanning and URL discovery.     Refactored from mod` --uses--> `GHDBProvider`  [INFERRED]
  modules/scanner_service.py → modules/ghdb_provider.py
- `Processes a single dork by querying a random search engine.         Returns a li` --uses--> `GHDBProvider`  [INFERRED]
  modules/scanner_service.py → modules/ghdb_provider.py
- `run_worker()` --calls--> `GHDBProvider`  [INFERRED]
  modules/scanner.py → modules/ghdb_provider.py
- `HarvesterOrchestrator` --uses--> `WaybackHarvester`  [INFERRED]
  modules/harvester.py → modules/harvester_wayback.py
- `HarvesterOrchestrator` --uses--> `CRTHarvester`  [INFERRED]
  modules/harvester.py → modules/harvester_crt.py

## Communities

### Community 0 - "Community 0"
Cohesion: 0.13
Nodes (23): generate_all(), generate_cve_dorks(), generate_ghdb_dorks(), generate_niche_sqli_dorks(), generate_regional_param_dorks(), generate_sqli_error_dorks(), generate_subdomain_niche_dorks(), generate_taxonomy_dorks() (+15 more)

### Community 1 - "Community 1"
Cohesion: 0.11
Nodes (7): Clones or pulls the latest exploit-database from GitLab., Play a success sound notification (CHA-CHING)., CommonCrawlHarvester, Fetch the most recent CommonCrawl index ID., Query CommonCrawl CDX for a domain, return SQLi-candidate URLs., GitHubHarvester, HarvesterOrchestrator

### Community 2 - "Community 2"
Cohesion: 0.18
Nodes (5): EDBSync, Searches for exploits related to a specific CVE., Returns the local path to the exploit file., AsyncExploiter, main()

### Community 3 - "Community 3"
Cohesion: 0.16
Nodes (6): ExploiterService, Attempts to exploit a confirmed vulnerability.         Extracts DB info and save, Independent service for SQL injection exploitation and data extraction.     Refa, Ensure data directory exists and prepare for exploitation., Parse raw SQLMap output for key database information., Save a formatted summary of the pwned target.

### Community 4 - "Community 4"
Cohesion: 0.16
Nodes (7): BaseService, Independent service for URL validation and availability checking.     Refactored, Initialize async session for HTTP requests., Check if URL returns a 200 OK status., Validates a URL item.         Returns the item if valid, otherwise None., Close the async session., ValidatorService

### Community 5 - "Community 5"
Cohesion: 0.29
Nodes (3): Get seed domains for a TLD via Bing search., Query Wayback CDX API for a domain, return SQLi-candidate URLs., WaybackHarvester

### Community 6 - "Community 6"
Cohesion: 0.24
Nodes (3): InjectorService, Independent service for SQL injection detection using SQLMap and Ghauri.     Ref, Tests a target for SQL injection vulnerability.         Returns vulnerability da

### Community 7 - "Community 7"
Cohesion: 0.27
Nodes (3): CRTHarvester, Fetch recent domain names from crt.sh for a TLD., Probe domain with SQLi paths, add live URLs to queue.

### Community 8 - "Community 8"
Cohesion: 0.27
Nodes (3): Independent service for dork scanning and URL discovery.     Refactored from mod, Processes a single dork by querying a random search engine.         Returns a li, ScannerService

### Community 9 - "Community 9"
Cohesion: 0.39
Nodes (2): main(), Validator

### Community 10 - "Community 10"
Cohesion: 0.43
Nodes (4): AsyncInjector, _build_ghauri_args(), _build_sqlmap_args(), main()

### Community 11 - "Community 11"
Cohesion: 0.48
Nodes (6): is_blacklisted(), is_sqli_candidate(), normalize_url(), run_worker(), standalone_main(), worker()

## Knowledge Gaps
- **24 isolated node(s):** `Get seed domains for a TLD via Bing search.`, `Query Wayback CDX API for a domain, return SQLi-candidate URLs.`, `Independent service for SQL injection exploitation and data extraction.     Refa`, `Ensure data directory exists and prepare for exploitation.`, `Play a success sound notification (CHA-CHING).` (+19 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **Thin community `Community 9`** (8 nodes): `main()`, `validator.py`, `Validator`, `.__init__()`, `.is_blacklisted()`, `.process_url()`, `.run()`, `.validate_url()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `ExploiterService` connect `Community 3` to `Community 1`, `Community 4`?**
  _High betweenness centrality (0.459) - this node is a cross-community bridge._
- **Why does `ScannerService` connect `Community 8` to `Community 0`, `Community 4`?**
  _High betweenness centrality (0.358) - this node is a cross-community bridge._
- **Why does `GHDBProvider` connect `Community 0` to `Community 8`, `Community 11`?**
  _High betweenness centrality (0.304) - this node is a cross-community bridge._
- **Are the 16 inferred relationships involving `GHDBProvider` (e.g. with `Čita dork fajl, ignorišući komentare i prazne linije.` and `SQL greska + ranjivi param na istoj stranici.`) actually correct?**
  _`GHDBProvider` has 16 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Get seed domains for a TLD via Bing search.`, `Query Wayback CDX API for a domain, return SQLi-candidate URLs.`, `Independent service for SQL injection exploitation and data extraction.     Refa` to the rest of the system?**
  _24 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Community 0` be split into smaller, more focused modules?**
  _Cohesion score 0.13 - nodes in this community are weakly interconnected._
- **Should `Community 1` be split into smaller, more focused modules?**
  _Cohesion score 0.11 - nodes in this community are weakly interconnected._