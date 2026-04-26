# Matadorks — Claude Intelligence File

## Šta je projekat

Matadorks je autonomni SQLi pipeline. Unosiš dorkove, na drugom kraju dobijaš listu potvrđenih ranjivih baza podataka. Pipeline faze:

```
Dorking → Proxy Build → Scanning → Validation → Injection → Exploitation
```

Entry point: `python matadorks.py` (ili `uv run python3 matadorks.py`)

---

## Arhitektura

```
matadorks.py          ← Master controller, CLI, pipeline orchestrator
core/
  config.py           ← SVE konstante i putanje (jedino mesto za izmene)
  proxy.py            ← ProxyPool — dual-phase TCP+HTTP validacija
  search.py           ← Multi-engine scraping (Google, Bing, Brave, Yandex, DDG)
  state.py            ← Pipeline state persistenca (data/state.json)
  logger.py           ← Rich terminal logger
  git_handler.py      ← Auto-commit između faza
modules/
  dorker.py           ← generate_all() — kombinator dorkova
  dork_gen.py         ← Generatori dorkova (SQL errors, regional, niche, leaks)
  scanner.py          ← Bulk URL kolekcija iz search engine-a
  validator.py        ← HTTP 200 check + blacklist filter
  injector.py         ← SQLMap automator (detekcija ranjivosti)
  exploiter.py        ← Loot ekstrakcija (DBMS, user, baze)
data/                 ← Runtime output (gitignored)
ostava/               ← AI agent koordinacija (gitignored)
```

### Pravilo za config
**Sve konstante idu u `core/config.py`.** Nikad hardcode u modulima.
Putanje, timeouty, threadovi, SQLMap opcije, blacklista — sve tamo.

---

## Dependency management

Projekat koristi `uv`. Uvek pokreći kroz:
```bash
uv run python3 matadorks.py
uv run python3 -c "from core import config"   # test importa
```

Nikad `python3` direktno — sistem nema pip, paketi su u uv virtualenv-u.

Sync dependencies:
```bash
python3 matadorks.py --sync
# ili
uv sync
```

---

## Claude + Gemini Workflow

### Uloge
- **Claude** — planer, code reviewer, merge master. Handle: `[CLAUDE]`
- **Gemini** — implementer, radi u izolovanim git worktree-ovima. Handle: `[GEMINI:ime-workera]`

### Kako delegirati zadatak Geminiju

1. **Napiši task prompt** u `ostava/GEMINI.MD` (ili `ostava/tasks/<ime>.md`)
2. **Logiraj u INBOX.MD:**
   ```
   [YYYY-MM-DD] [CLAUDE] -> GEMINI:ime-workera: Task delegated. Branch: fix/ime
   ```
3. **Pokreni Gemini u tmux windowu** (UVEK tmux, nikad background):
   ```bash
   cat > /tmp/run_gemini_<ime>.sh << 'SCRIPT'
   #!/bin/bash
   export NVM_DIR="$HOME/.nvm" && source "$NVM_DIR/nvm.sh" && nvm use 20 --silent
   cd /home/minool/Matadorks
   PROMPT=$(cat ostava/GEMINI.MD)
   gemini --yolo -w <branch-name> -p "$PROMPT"
   echo "--- DONE ---"; read
   SCRIPT
   chmod +x /tmp/run_gemini_<ime>.sh
   tmux new-window -t matadorks -n "gemini-<ime>" "bash /tmp/run_gemini_<ime>.sh"
   ```
4. **Korisnik gleda** Ctrl+B W → izaberi window
5. **Claude review-uje** diff kada Gemini završi
6. **Claude merguje** na main

### Pokretanje VIŠE agenata odjednom
```bash
bash ostava/launch_all_agents.sh
```
Task fajlovi su u `ostava/tasks/`. Svaki agent dobija svoju granu i tmux window.

### Merge redosled (važno!)
Kada više agenata kreira `core/config.py`, merguj ovim redosledom:
1. `feat/core-config` (puni config.py) — PRVI
2. Ostali — pri konfliktu na config.py: `git checkout HEAD -- core/config.py`

---

## INBOX.MD protokol

Fajl: `ostava/INBOX.MD`

Svaki agent loguje start i kraj:
```
[YYYY-MM-DD] [CLAUDE] -> GEMINI:ime: Task delegated. Branch: fix/ime. Check ostava/GEMINI.MD.
[YYYY-MM-DD] [GEMINI:ime] -> CLAUDE: Started. Doing X...
[YYYY-MM-DD] [GEMINI:ime] -> CLAUDE: Done. PR ready.
[YYYY-MM-DD] [CLAUDE] -> GEMINI:ime: Merged. OK.
```

---

## Tmux cheat sheet

```bash
tmux attach -t matadorks     # attach na sesiju
Ctrl+B W                     # lista svih windowsa
Ctrl+B broj                  # skoči na window
Ctrl+B [                     # copy mode (skrolovanje)
Q                            # izlaz iz copy mode
```

Mouse scroll je uključen (`~/.tmux.conf: set -g mouse on`).

Node 20 mora biti aktivan za Gemini CLI:
```bash
export NVM_DIR="$HOME/.nvm" && source "$NVM_DIR/nvm.sh" && nvm use 20
```

Gemini settings: `~/.gemini/settings.json` — mora imati `"experimental": {"worktrees": true}`

---

## Gemini CLI quick reference

```bash
# Non-interactive u novom worktree-u (standardni način)
PROMPT=$(cat ostava/GEMINI.MD)
gemini --yolo -w branch-name -p "$PROMPT"

# Interaktivni (za debug)
gemini

# Listaj worktree-ove
git worktree list
```

---

## Dork generator

Dorkovi se generišu u `modules/dork_gen.py` i kombinuju u `modules/dorker.py`.

**Planirano poboljšanje (nije implementirano):** Premestiti izvore dorkova u `data/dorks/*.txt` fajlove (sql_errors.txt, params.txt, regional/de.txt itd.) da korisnici mogu da dodaju dorkove bez editovanja Python koda.

---

## Poznati problemi i rešenja

| Problem | Rešenje |
|---------|---------|
| `ModuleNotFoundError` | Koristi `uv run python3` umesto `python3` |
| Gemini `--worktree` ne radi | Provjeri `~/.gemini/settings.json` — mora biti `"experimental": {"worktrees": true}` |
| Gemini ne vidi tmux window | Sesija nije kreirana: `tmux new-session -d -s matadorks` |
| `sessions should be nested` | Već si unutar tmux sesije, samo `Ctrl+B W` |
| config.py merge konflikt | `git checkout HEAD -- core/config.py` pa `git add` i `git commit` |
| Brave 429 | Normalno — rotacija proksija je automatska |

---

## Planirana poboljšanja (backlog)

- [ ] Telegram notifikacije za SQLi hitove u realnom vremenu
- [ ] Rich/Textual live dashboard (aktivni proxy, broj meta, SQLi count)
- [ ] Shodan/Censys/ZoomEye integracija u scanner (API ključevi kroz config)
- [ ] Dork generator refaktor — data/dorks/*.txt umesto hardcoded lista
- [ ] Retry logika u exploiteru za timeout-ovane mete
