#!/usr/bin/env python3
"""
Delegate a single task to Gemini CLI in a git worktree, then push and create PR.

Usage:
    python delegate_task.py --task "Fix search import" --branch "fix/search-import"
"""
import argparse
import subprocess
import sys
import os
import tempfile
from pathlib import Path


def run(cmd, cwd=None, check=True):
    result = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True)
    if check and result.returncode != 0:
        print(f"[ERROR] Command failed: {cmd}")
        print(result.stderr)
        sys.exit(1)
    return result.stdout.strip()


def gemini_available():
    nvm_sh = Path.home() / ".nvm" / "nvm.sh"
    if not nvm_sh.exists():
        return False, "nvm not found at ~/.nvm/nvm.sh"
    test = subprocess.run(
        f'export NVM_DIR="$HOME/.nvm" && source "$NVM_DIR/nvm.sh" && nvm use 20 --silent && gemini --version',
        shell=True, capture_output=True, text=True, executable="/bin/bash"
    )
    if test.returncode != 0:
        return False, "gemini CLI not available on Node 20"
    return True, test.stdout.strip()


def delegate(task_name, branch, prompt_file, repo_root):
    ok, info = gemini_available()
    if not ok:
        print(f"[!] {info}")
        print("[!] Run: export NVM_DIR=\"$HOME/.nvm\" && source \"$NVM_DIR/nvm.sh\" && nvm use 20")
        sys.exit(1)

    print(f"[+] Gemini CLI ready: {info}")

    if not os.path.exists(prompt_file):
        print(f"[!] Prompt file not found: {prompt_file}")
        sys.exit(1)

    with open(prompt_file) as f:
        prompt = f.read().strip()

    if not prompt:
        print("[!] Prompt file is empty.")
        sys.exit(1)

    print(f"[*] Delegating task: {task_name}")
    print(f"[*] Branch: {branch}")
    print(f"[*] Prompt preview: {prompt[:120]}...")

    # Run Gemini in worktree
    gemini_cmd = (
        f'export NVM_DIR="$HOME/.nvm" && source "$NVM_DIR/nvm.sh" && nvm use 20 --silent && '
        f'gemini -p {repr(prompt)} --yolo -w {branch}'
    )
    print(f"\n[*] Running Gemini in new worktree '{branch}'...\n")
    result = subprocess.run(gemini_cmd, shell=True, cwd=repo_root, executable="/bin/bash")

    if result.returncode != 0:
        print(f"[!] Gemini exited with code {result.returncode}")
        sys.exit(1)

    # Find the worktree path
    worktrees = run("git worktree list --porcelain", cwd=repo_root)
    worktree_path = None
    for line in worktrees.splitlines():
        if line.startswith("worktree ") and branch in line:
            worktree_path = line.split(" ", 1)[1]
            break

    if not worktree_path:
        print("[!] Could not find worktree path. Gemini may have used a different name.")
        print(run("git worktree list", cwd=repo_root))
        sys.exit(1)

    print(f"\n[+] Worktree at: {worktree_path}")

    # Show what Gemini did
    log = run(f"git log --oneline -5", cwd=worktree_path)
    print(f"\n[*] Recent commits:\n{log}")

    # Push
    print(f"\n[*] Pushing branch '{branch}'...")
    push = subprocess.run(f"git push -u origin {branch}", shell=True, cwd=worktree_path,
                          capture_output=True, text=True)
    if push.returncode != 0:
        print(f"[!] Push failed: {push.stderr}")
        sys.exit(1)

    # Create PR
    print(f"[*] Creating PR...")
    pr_body = f"## Task: {task_name}\n\n{prompt}\n\n---\n*Implemented by Gemini CLI, reviewed by Claude.*"
    pr_result = subprocess.run(
        f'gh pr create --title "{task_name}" --body {repr(pr_body)} --head {branch}',
        shell=True, cwd=worktree_path, capture_output=True, text=True
    )

    if pr_result.returncode != 0:
        print(f"[!] PR creation failed: {pr_result.stderr}")
    else:
        pr_url = pr_result.stdout.strip()
        print(f"\n[+] PR created: {pr_url}")
        print(f"[+] Claude can review with: gh pr diff {branch}")

        # Log to INBOX.MD
        inbox = Path(repo_root) / "ostava" / "INBOX.MD"
        if inbox.exists():
            from datetime import date
            with open(inbox, "a") as f:
                f.write(f"\n[{date.today()}] CLAUDE -> GEMINI: Task '{task_name}' delegated. Branch: {branch}. PR: {pr_url}")

    return pr_result.returncode == 0


def main():
    parser = argparse.ArgumentParser(description="Delegate task to Gemini CLI")
    parser.add_argument("--task", required=True, help="Task name (used as PR title)")
    parser.add_argument("--branch", required=True, help="Git branch name for the worktree")
    parser.add_argument("--prompt-file", default="ostava/GEMINI.MD", help="Path to prompt file")
    parser.add_argument("--repo", default=".", help="Repo root directory")
    args = parser.parse_args()

    repo_root = os.path.abspath(args.repo)
    success = delegate(args.task, args.branch, args.prompt_file, repo_root)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
