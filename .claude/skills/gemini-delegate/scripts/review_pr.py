#!/usr/bin/env python3
"""
Fetch and format a PR diff for Claude to review.

Usage:
    python review_pr.py --pr 3
    python review_pr.py --list
"""
import argparse
import subprocess
import sys


def run(cmd):
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return r.stdout.strip(), r.stderr.strip(), r.returncode


def list_prs():
    out, err, code = run("gh pr list --json number,title,headRefName,state --limit 20")
    if code != 0:
        print(f"[!] gh pr list failed: {err}")
        sys.exit(1)
    import json
    prs = json.loads(out)
    if not prs:
        print("[*] No open PRs.")
        return
    print(f"\n{'#':<6} {'Branch':<35} {'Title'}")
    print("-" * 70)
    for pr in prs:
        print(f"#{pr['number']:<5} {pr['headRefName']:<35} {pr['title']}")


def review_pr(number):
    # Get PR info
    out, err, code = run(f"gh pr view {number} --json title,body,headRefName,author")
    if code != 0:
        print(f"[!] Could not fetch PR #{number}: {err}")
        sys.exit(1)

    import json
    info = json.loads(out)
    print(f"\n{'='*60}")
    print(f"PR #{number}: {info['title']}")
    print(f"Branch: {info['headRefName']} | Author: {info['author']['login']}")
    print(f"{'='*60}")
    print(f"\n{info.get('body', '(no description)')}")
    print(f"\n{'─'*60}\nDIFF:\n{'─'*60}\n")

    diff_out, diff_err, diff_code = run(f"gh pr diff {number}")
    if diff_code != 0:
        print(f"[!] Could not get diff: {diff_err}")
        sys.exit(1)

    print(diff_out)

    print(f"\n{'─'*60}")
    print("Review options:")
    print(f"  Approve:  gh pr review {number} --approve")
    print(f"  Comment:  gh pr review {number} --comment -b 'feedback'")
    print(f"  Merge:    gh pr merge {number} --squash")
    print(f"  Close:    gh pr close {number}")


def main():
    parser = argparse.ArgumentParser(description="Review a Gemini-created PR")
    parser.add_argument("--pr", type=int, help="PR number to review")
    parser.add_argument("--list", action="store_true", help="List all open PRs")
    args = parser.parse_args()

    if args.list:
        list_prs()
    elif args.pr:
        review_pr(args.pr)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
