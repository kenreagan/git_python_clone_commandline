import os
import json
import shutil
from pathlib import Path
from .diff import Diff

class Merge:
    """
    Manages branch merging in the distributed source control system.
    """
    MERGE_DIR = 'merges'
    CONFLICTS_FILE = 'conflicts.json'

    def __init__(self, repository):
        """
        Initialize the merge manager for a repository.
        
        :param repository: Repository instance
        """
        self.repository = repository
        self.dscs_path = os.path.join(repository.path, repository.DSCS_DIR)
        self.merge_path = os.path.join(self.dscs_path, self.MERGE_DIR)
        self.conflicts_path = os.path.join(self.merge_path, self.CONFLICTS_FILE)
        
        # Create merge directory if it doesn't exist
        os.makedirs(self.merge_path, exist_ok=True)

    def merge(self, source_branch, target_branch=None):
        """
        Merge a source branch into the target branch.
        
        :param source_branch: Name of the branch to merge from
        :param target_branch: Name of the branch to merge into (defaults to current branch)
        :return: Merge result dictionary
        :raises Exception: If merge conflicts are detected
        """
        # Determine target branch (current branch if not specified)
        if target_branch is None:
            target_branch = self.repository.get_current_branch()
        
        # Get branch paths
        source_branch_path = os.path.join(
            self.dscs_path, 
            self.repository.BRANCHES_DIR, 
            source_branch
        )
        target_branch_path = os.path.join(
            self.dscs_path, 
            self.repository.BRANCHES_DIR, 
            target_branch
        )
        
        # Validate branch existence
        if not os.path.exists(source_branch_path):
            raise ValueError(f"Source branch '{source_branch}' does not exist")
        if not os.path.exists(target_branch_path):
            raise ValueError(f"Target branch '{target_branch}' does not exist")
        
        # Use Diff to compare branches
        diff = Diff(self.repository)
        differences = diff.compare_branches(source_branch, target_branch)
        
        # Detect conflicts
        conflicts = self._detect_conflicts(differences)
        
        # If conflicts exist, raise an exception
        if conflicts:
            # Store conflicts
            self._store_conflicts(conflicts)
            raise MergeConflictError(f"Merge conflicts detected between {source_branch} and {target_branch}")
        
        # Apply changes
        merge_result = self._apply_merge(source_branch, target_branch, differences)
        
        return merge_result

    def _detect_conflicts(self, differences):
        """
        Detect merge conflicts in the differences.
        
        :param differences: List of differences between branches
        :return: List of conflicts
        """
        conflicts = []
        
        for diff_item in differences:
            # Check for conflicting changes
            # This is a simplified conflict detection
            # In a real implementation, you'd do more sophisticated conflict checking
            if diff_item.get('type') == 'modify':
                # Example conflict detection logic
                file_path = diff_item.get('path')
                source_content = diff_item.get('source_content')
                target_content = diff_item.get('target_content')
                
                # Simple content comparison (can be expanded)
                if source_content != target_content:
                    conflicts.append({
                        'path': file_path,
                        'type': 'content_conflict',
                        'source_content': source_content,
                        'target_content': target_content
                    })
        
        return conflicts

    def _store_conflicts(self, conflicts):
        """
        Store merge conflicts for later resolution.
        
        :param conflicts: List of detected conflicts
        """
        with open(self.conflicts_path, 'w') as f:
            json.dump(conflicts, f, indent=2)

    def _apply_merge(self, source_branch, target_branch, differences):
        """
        Apply merge changes to the target branch.
        
        :param source_branch: Name of source branch
        :param target_branch: Name of target branch
        :param differences: List of differences to merge
        :return: Merge result dictionary
        """
        merge_result = {
            'source_branch': source_branch,
            'target_branch': target_branch,
            'changes': []
        }
        
        # Apply each difference
        for diff_item in differences:
            change_type = diff_item.get('type')
            file_path = diff_item.get('path')
            
            if change_type == 'add':
                # Add new file
                content = diff_item.get('content')
                full_path = os.path.join(self.repository.path, file_path)
                
                # Ensure directory exists
                os.makedirs(os.path.dirname(full_path), exist_ok=True)
                
                with open(full_path, 'w') as f:
                    f.write(content)
                
                merge_result['changes'].append({
                    'type': 'add',
                    'path': file_path
                })
            
            elif change_type == 'modify':
                # Modify existing file
                content = diff_item.get('source_content')
                full_path = os.path.join(self.repository.path, file_path)
                
                with open(full_path, 'w') as f:
                    f.write(content)
                
                merge_result['changes'].append({
                    'type': 'modify',
                    'path': file_path
                })
            
            elif change_type == 'delete':
                # Delete file
                full_path = os.path.join(self.repository.path, file_path)
                
                if os.path.exists(full_path):
                    os.remove(full_path)
                
                merge_result['changes'].append({
                    'type': 'delete',
                    'path': file_path
                })
        
        return merge_result

    def list_conflicts(self):
        """
        List current merge conflicts.
        
        :return: List of conflicts
        """
        try:
            with open(self.conflicts_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return []

    def resolve_conflicts(self, resolutions):
        """
        Resolve merge conflicts.
        
        :param resolutions: Dictionary of file paths to resolved content
        """
        # Load existing conflicts
        try:
            with open(self.conflicts_path, 'r') as f:
                conflicts = json.load(f)
        except FileNotFoundError:
            return
        
        # Apply resolutions
        for file_path, content in resolutions.items():
            # Find matching conflict
            conflict = next((c for c in conflicts if c['path'] == file_path), None)
            
            if conflict:
                # Write resolved content
                full_path = os.path.join(self.repository.path, file_path)
                with open(full_path, 'w') as f:
                    f.write(content)
                
                # Remove this conflict
                conflicts = [c for c in conflicts if c['path'] != file_path]
        
        # Update conflicts file
        if conflicts:
            with open(self.conflicts_path, 'w') as f:
                json.dump(conflicts, f, indent=2)
        else:
            # Remove conflicts file if no conflicts remain
            os.remove(self.conflicts_path)

class MergeConflictError(Exception):
    """
    Exception raised when merge conflicts are detected.
    """
    def __init__(self, message):
        """
        Initialize merge conflict error.
        
        :param message: Error message describing the conflicts
        """
        self.message = message
        super().__init__(self.message)