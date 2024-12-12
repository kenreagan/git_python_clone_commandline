import os
import json
from typing import List, Dict, Optional
from datetime import datetime

class History:
    """
    Manages the commit history for a source control repository.
    Stores commit information in a JSON-based log within the repository's dot directory.
    """
    
    def __init__(self, repo_path: str):
        """
        Initialize the commit history for a repository.
        
        :param repo_path: Path to the root of the repository
        """
        self.repo_path = repo_path
        self.dot_dir = os.path.join(repo_path, '.source-control')
        self.history_file = os.path.join(self.dot_dir, 'commit_history.json')
        
        # Ensure history file exists
        if not os.path.exists(self.history_file):
            self._initialize_history_file()
    
    def _initialize_history_file(self):
        """
        Create an empty commit history file.
        """
        os.makedirs(os.path.dirname(self.history_file), exist_ok=True)
        with open(self.history_file, 'w') as f:
            json.dump([], f)
    
    def record_commit(self, commit_hash: str, branch: str, message: str, 
                      files_changed: List[str], parent_hash: Optional[str] = None) -> Dict:
        """
        Record a new commit in the history.
        
        :param commit_hash: Unique hash for the commit
        :param branch: Branch where the commit was made
        :param message: Commit message
        :param files_changed: List of files changed in this commit
        :param parent_hash: Hash of the parent commit (if any)
        :return: Commit record dictionary
        """
        commit_record = {
            'hash': commit_hash,
            'branch': branch,
            'message': message,
            'timestamp': datetime.now().isoformat(),
            'files_changed': files_changed,
            'parent': parent_hash
        }
        
        # Read existing history
        with open(self.history_file, 'r') as f:
            history = json.load(f)
        
        # Add new commit
        history.append(commit_record)
        
        # Write updated history
        with open(self.history_file, 'w') as f:
            json.dump(history, f, indent=2)
        
        return commit_record
    
    def get_commit_history(self, branch: Optional[str] = None, 
                            limit: Optional[int] = None) -> List[Dict]:
        """
        Retrieve commit history, optionally filtered by branch.
        
        :param branch: Optional branch name to filter commits
        :param limit: Optional limit on number of commits to return
        :return: List of commit records
        """
        with open(self.history_file, 'r') as f:
            history = json.load(f)
        
        # Filter by branch if specified
        if branch:
            history = [commit for commit in history if commit['branch'] == branch]
        
        # Sort by timestamp, most recent first
        history.sort(key=lambda x: x['timestamp'], reverse=True)
        
        # Apply optional limit
        if limit:
            history = history[:limit]
        
        return history
    
    def get_commit_by_hash(self, commit_hash: str) -> Optional[Dict]:
        """
        Retrieve a specific commit by its hash.
        
        :param commit_hash: Hash of the commit to retrieve
        :return: Commit record or None if not found
        """
        with open(self.history_file, 'r') as f:
            history = json.load(f)
        
        for commit in history:
            if commit['hash'] == commit_hash:
                return commit
        
        return None
    
    def get_branch_commits(self, branch: str) -> List[Dict]:
        """
        Get all commits for a specific branch.
        
        :param branch: Branch name
        :return: List of commits for the branch
        """
        return [commit for commit in self.get_commit_history() if commit['branch'] == branch]
    
    def get_latest_commit(self, branch: Optional[str] = None) -> Optional[Dict]:
        """
        Get the most recent commit, optionally for a specific branch.
        
        :param branch: Optional branch name
        :return: Most recent commit record or None
        """
        history = self.get_commit_history(branch)
        return history[0] if history else None