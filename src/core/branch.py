import os
import json
from typing import List, Dict, Optional
import datetime

class Branch:
    """
    Manages branches for a source control repository.
    Handles branch creation, switching, listing, and tracking.
    """
    
    def __init__(self, repo_path: str):
        """
        Initialize branch management for a repository.
        
        :param repo_path: Path to the root of the repository
        """
        self.repo_path = repo_path
        self.dot_dir = os.path.join(repo_path, '.source-control')
        self.branches_file = os.path.join(self.dot_dir, 'branches.json')
        
        # Ensure branches file exists
        if not os.path.exists(self.branches_file):
            self._initialize_branches_file()
        
        # Ensure a default branch exists
        self._create_default_branch_if_not_exists()
    
    def _initialize_branches_file(self):
        """
        Create an initial branches configuration file.
        """
        os.makedirs(os.path.dirname(self.branches_file), exist_ok=True)
        
        # Initial branch configuration
        initial_branches = {
            'current_branch': 'main',
            'branches': {
                'main': {
                    'head_commit': None,
                    'created_at': None,
                    'base_branch': None
                }
            }
        }
        
        with open(self.branches_file, 'w') as f:
            json.dump(initial_branches, f, indent=2)
    
    def _create_default_branch_if_not_exists(self):
        """
        Ensure the default 'main' branch exists.
        """
        with open(self.branches_file, 'r+') as f:
            branches_config = json.load(f)
            
            if 'main' not in branches_config['branches']:
                branches_config['branches']['main'] = {
                    'head_commit': None,
                    'created_at': datetime.now().isoformat(),
                    'base_branch': None
                }
                
                # Reset file pointer and write updated config
                f.seek(0)
                json.dump(branches_config, f, indent=2)
                f.truncate()
    
    def create_branch(self, branch_name: str, base_branch: Optional[str] = None) -> Dict:
        """
        Create a new branch.
        
        :param branch_name: Name of the new branch
        :param base_branch: Branch to base the new branch on (defaults to current branch)
        :return: Branch configuration dictionary
        :raises ValueError: If branch already exists or name is invalid
        """
        # Validate branch name
        if not branch_name or '/' in branch_name:
            raise ValueError("Invalid branch name. Must be non-empty and cannot contain '/'.")
        
        with open(self.branches_file, 'r+') as f:
            branches_config = json.load(f)
            
            # Check if branch already exists
            if branch_name in branches_config['branches']:
                raise ValueError(f"Branch '{branch_name}' already exists.")
            
            # Use current branch as base if not specified
            base_branch = base_branch or branches_config['current_branch']
            
            # Get base branch head commit
            base_branch_info = branches_config['branches'].get(base_branch)
            if not base_branch_info:
                raise ValueError(f"Base branch '{base_branch}' does not exist.")
            
            # Create new branch
            new_branch_config = {
                'head_commit': base_branch_info['head_commit'],
                'created_at': datetime.now().isoformat(),
                'base_branch': base_branch
            }
            
            branches_config['branches'][branch_name] = new_branch_config
            
            # Reset file pointer and write updated config
            f.seek(0)
            json.dump(branches_config, f, indent=2)
            f.truncate()
        
        return new_branch_config
    
    def switch_branch(self, branch_name: str) -> str:
        """
        Switch to an existing branch.
        
        :param branch_name: Name of the branch to switch to
        :return: The name of the branch switched to
        :raises ValueError: If branch does not exist
        """
        with open(self.branches_file, 'r+') as f:
            branches_config = json.load(f)
            
            # Validate branch exists
            if branch_name not in branches_config['branches']:
                raise ValueError(f"Branch '{branch_name}' does not exist.")
            
            # Update current branch
            branches_config['current_branch'] = branch_name
            
            # Reset file pointer and write updated config
            f.seek(0)
            json.dump(branches_config, f, indent=2)
            f.truncate()
        
        return branch_name
    
    def list_branches(self) -> Dict[str, Dict]:
        """
        List all branches in the repository.
        
        :return: Dictionary of branches with their configurations
        """
        with open(self.branches_file, 'r') as f:
            branches_config = json.load(f)
        
        return {
            'current_branch': branches_config['current_branch'],
            'branches': branches_config['branches']
        }
    
    def update_branch_head(self, branch_name: str, commit_hash: str):
        """
        Update the head commit of a specific branch.
        
        :param branch_name: Name of the branch
        :param commit_hash: Hash of the new head commit
        :raises ValueError: If branch does not exist
        """
        with open(self.branches_file, 'r+') as f:
            branches_config = json.load(f)
            
            # Validate branch exists
            if branch_name not in branches_config['branches']:
                raise ValueError(f"Branch '{branch_name}' does not exist.")
            
            # Update branch head commit
            branches_config['branches'][branch_name]['head_commit'] = commit_hash
            
            # Reset file pointer and write updated config
            f.seek(0)
            json.dump(branches_config, f, indent=2)
            f.truncate()
    
    def get_current_branch(self) -> str:
        """
        Get the name of the current branch.
        
        :return: Name of the current branch
        """
        with open(self.branches_file, 'r') as f:
            branches_config = json.load(f)
        
        return branches_config['current_branch']
    
    def get_branch_head(self, branch_name: Optional[str] = None) -> Optional[str]:
        """
        Get the head commit hash for a branch.
        
        :param branch_name: Name of the branch (defaults to current branch)
        :return: Head commit hash or None if no commits
        """
        with open(self.branches_file, 'r') as f:
            branches_config = json.load(f)
        
        # Use current branch if not specified
        branch_name = branch_name or branches_config['current_branch']
        
        # Validate branch exists
        if branch_name not in branches_config['branches']:
            raise ValueError(f"Branch '{branch_name}' does not exist.")
        
        return branches_config['branches'][branch_name]['head_commit']