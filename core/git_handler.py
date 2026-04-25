import subprocess
import os

class GitHandler:
    def __init__(self, repo_path="."):
        self.repo_path = repo_path

    def commit(self, message):
        try:
            # Add all except ignored
            subprocess.run(["git", "add", "."], cwd=self.repo_path, check=True)
            # Check if there are changes to commit
            status = subprocess.run(["git", "status", "--porcelain"], cwd=self.repo_path, capture_output=True, text=True)
            if status.stdout.strip():
                subprocess.run(["git", "commit", "-m", message], cwd=self.repo_path, check=True)
                return True
            return False
        except Exception as e:
            print(f"Git Error: {e}")
            return False

    def push(self, remote="origin", branch="master"):
        try:
            subprocess.run(["git", "push", remote, branch], cwd=self.repo_path, check=True)
            return True
        except Exception as e:
            print(f"Git Push Error: {e}")
            return False
