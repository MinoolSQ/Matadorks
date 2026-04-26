---
name: gemini-delegate
description: Delegates implementation tasks to Gemini CLI in isolated git worktrees, then creates PRs for Claude to review. Use when: you have a written plan with discrete tasks, want parallel execution, or want Gemini to implement while Claude reviews. Requires Node 20 via nvm and authenticated Gemini CLI.
---

# Gemini Delegate

Orchestrates Claude (planer/reviewer) + Gemini (implementer) workflow.

## Workflow Overview

```
Claude writes plan → splits into tasks → Gemini implements each in worktree → PR created → Claude reviews
```

## Step-by-Step Execution

### 1. Prepare Task File

Before calling Gemini, write a focused task prompt to `ostava/GEMINI.MD`:

```markdown
# Task: <task name>

## Context
<brief description of what the project does and what files are affected>

## Your Job
<exact changes to make — be specific about file paths, function names, what to add/remove>

## Constraints
- Do not change files outside the scope of this task
- Commit with message: "gemini: <task name>"
- Run: python3 -c "from core import config" to verify imports work after changes
```

### 2. Run Gemini in Worktree (via tmux — user sees live output)

ALWAYS use tmux so the user can watch the agent work in real time:

```bash
export NVM_DIR="$HOME/.nvm" && source "$NVM_DIR/nvm.sh" && nvm use 20 --silent

tmux new-window -n "gemini-<task-name>" \
  "bash -c 'export NVM_DIR=\"\$HOME/.nvm\" && source \"\$NVM_DIR/nvm.sh\" && nvm use 20 --silent && gemini -p \"$(cat ostava/GEMINI.MD)\" --yolo -w <branch-name>; echo DONE; read'"
```

User can switch to the Gemini window with **Ctrl+B + window number**.
The `-w` flag creates an isolated git worktree automatically.

### 3. Check Output

```bash
# List worktrees created by Gemini
git worktree list

# Check what Gemini did
git -C <worktree-path> log --oneline -5
git -C <worktree-path> diff HEAD~1
```

### 4. Push & Create PR

```bash
cd <worktree-path>
git push -u origin <branch-name>
gh pr create --title "<task name>" --body "$(cat ostava/GEMINI.MD)"
cd -
```

### 5. Claude Reviews

```bash
gh pr diff <pr-number>
gh pr view <pr-number>
# If OK:
gh pr merge <pr-number> --squash
# If needs changes:
gh pr review <pr-number> --comment -b "<feedback>"
```

---

## Multi-Task Parallel Execution

For a plan with N tasks, run them sequentially or in parallel:

```bash
# Sequential (safer, each task builds on previous)
for task in task1 task2 task3; do
    python scripts/delegate_task.py $task
done

# Parallel (for independent tasks only)
python scripts/delegate_parallel.py plan.md
```

---

## Helper Scripts

### `scripts/delegate_task.py`
Takes a task name, writes prompt to GEMINI.MD, calls Gemini, pushes PR.

```bash
python .claude/skills/gemini-delegate/scripts/delegate_task.py \
    --task "Fix search import" \
    --branch "fix/search-import" \
    --prompt-file ostava/GEMINI.MD
```

### `scripts/review_pr.py`
Fetches PR diff and formats it for Claude review.

```bash
python .claude/skills/gemini-delegate/scripts/review_pr.py --pr <number>
```

---

## Communication Protocol (ostava/)

| Fajl | Svrha |
|------|-------|
| `ostava/GEMINI.MD` | Aktivan zadatak koji Gemini treba da uradi |
| `ostava/CLAUDE.MD` | Instrukcije za Claude (standardi, pravila) |
| `ostava/INBOX.MD` | Poruke između agenata (format: `[DATE] [AGENT] -> [TARGET]: msg`) |

After each task, both agents log to INBOX.MD using their handle:
```
[2026-04-26] [CLAUDE] -> GEMINI: Task "Fix search import" delegated. Branch: fix/search-import
[2026-04-26] [GEMINI:fix-search-worker] -> CLAUDE: Started. Fixing import on line 85...
[2026-04-26] [GEMINI:fix-search-worker] -> CLAUDE: Done. PR #3 ready for review.
[2026-04-26] [CLAUDE] -> GEMINI:fix-search-worker: PR #3 approved and merged.
```

**Claude's handle:** `CLAUDE`  
**Gemini handle format:** `GEMINI:<task-name>` (e.g. `GEMINI:banner-worker`, `GEMINI:config-worker`)

---

## Gemini CLI Quick Reference

```bash
# Non-interactive with auto-approve + new worktree
gemini -p "prompt" --yolo -w branch-name

# Non-interactive, stays in current dir
gemini -p "prompt" --yolo

# Interactive mode (for debugging)
gemini -i "initial prompt"

# Resume previous session
gemini --resume latest

# JSON output (for scripting)
gemini -p "prompt" --yolo -o json
```

---

## Troubleshooting

**Gemini CLI not found / SyntaxError:**
```bash
export NVM_DIR="$HOME/.nvm" && source "$NVM_DIR/nvm.sh" && nvm use 20
```

**Worktree conflict:**
```bash
git worktree prune
git worktree list
```

**Gemini hangs / no response:**
- Check `~/.gemini/` for auth credentials
- Run `gemini` interactively first to re-authenticate
