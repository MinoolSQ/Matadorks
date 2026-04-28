import subprocess
import os

class GitHandler:
    def __init__(self, repo_path="."):
        self.repo_path = repo_path

    def commit(self, message):
        try:
            # Add all except ignored
            subprocess.run(["git", "add", "."], cwd=self.repo_path, capture_output=True)
            # Check if there are staged changes to commit
            status = subprocess.run(["git", "status", "--porcelain"], cwd=self.repo_path, capture_output=True, text=True)
            
            # Filter status to see if there are actual changes to commit (M, A, D, R, C)
            has_changes = False
            for line in status.stdout.splitlines():
                if line.startswith(('M', 'A', 'D', 'R', 'C', ' M', ' A', ' D', ' R', ' C')):
                    has_changes = True
                    break
            
            if has_changes:
                subprocess.run(["git", "commit", "-m", message], cwd=self.repo_path, capture_output=True, check=True)
                return True
            return False
        except Exception:
            return False

    def push(self, remote="origin", branch="master"):
        try:
            subprocess.run(["git", "push", remote, branch], cwd=self.repo_path, check=True)
            return True
        except Exception as e:
            print(f"Git Push Error: {e}")
            return False
