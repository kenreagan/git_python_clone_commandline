import os
import difflib
import json
from typing import List, Dict, Optional, Tuple

class Diff:
    """
    Manages diff operations for a source control repository.
    Handles comparing files, commits, and generating human-readable diffs.
    """
    
    def __init__(self, repo_path: str):
        """
        Initialize diff management for a repository.
        
        :param repo_path: Path to the root of the repository
        """
        self.repo_path = repo_path
        self.dot_dir = os.path.join(repo_path, '.source-control')
        self.commits_dir = os.path.join(self.dot_dir, 'commits')
    
    def _read_file_lines(self, file_path: str) -> List[str]:
        """
        Read file contents as lines.
        
        :param file_path: Path to the file
        :return: List of file lines
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.readlines()
        except UnicodeDecodeError:
            # Handle binary or non-text files
            return []
    
    def generate_file_diff(self, file1_path: str, file2_path: str) -> Dict:
        """
        Generate a diff between two files.
        
        :param file1_path: Path to the first file
        :param file2_path: Path to the second file
        :return: Diff information dictionary
        """
        # Read file contents
        file1_lines = self._read_file_lines(file1_path)
        file2_lines = self._read_file_lines(file2_path)
        
        # Generate diff
        diff = list(difflib.unified_diff(
            file1_lines, 
            file2_lines, 
            fromfile=os.path.basename(file1_path),
            tofile=os.path.basename(file2_path)
        ))
        
        # Analyze changes
        changes = {
            'added_lines': sum(1 for line in diff if line.startswith('+')),
            'removed_lines': sum(1 for line in diff if line.startswith('-')),
            'total_lines_changed': len(diff)
        }
        
        return {
            'diff_lines': diff,
            'changes': changes,
            'is_different': len(diff) > 0
        }
    
    def diff_commits(self, commit1_hash: str, commit2_hash: str) -> Dict:
        """
        Generate a comprehensive diff between two commits.
        
        :param commit1_hash: Hash of the first commit
        :param commit2_hash: Hash of the second commit
        :return: Commit diff information
        :raises ValueError: If commits do not exist
        """
        commit1_path = os.path.join(self.commits_dir, commit1_hash)
        commit2_path = os.path.join(self.commits_dir, commit2_hash)
        
        # Validate commits exist
        if not os.path.exists(commit1_path) or not os.path.exists(commit2_path):
            raise ValueError("One or both commits do not exist")
        
        # Load commit metadata
        with open(os.path.join(commit1_path, 'metadata.json'), 'r') as f:
            commit1_metadata = json.load(f)
        
        with open(os.path.join(commit2_path, 'metadata.json'), 'r') as f:
            commit2_metadata = json.load(f)
        
        # Track file changes
        file_diffs = {}
        all_files = set()
        
        # Get files from both commits
        commit1_files = {f['path'] for f in commit1_metadata['files']}
        commit2_files = {f['path'] for f in commit2_metadata['files']}
        all_files = commit1_files.union(commit2_files)
        
        # Compare files
        for file_path in all_files:
            file1_full_path = os.path.join(commit1_path, file_path)
            file2_full_path = os.path.join(commit2_path, file_path)
            
            # Determine file status
            if file_path not in commit1_files:
                file_status = 'added'
                file1_full_path = '/dev/null'  # Simulate empty file for diff
            elif file_path not in commit2_files:
                file_status = 'deleted'
                file2_full_path = '/dev/null'  # Simulate empty file for diff
            else:
                file_status = 'modified'
            
            # Generate file diff
            try:
                file_diff = self.generate_file_diff(file1_full_path, file2_full_path)
                file_diff['status'] = file_status
                file_diffs[file_path] = file_diff
            except Exception:
                # Handle any file reading errors
                file_diffs[file_path] = {
                    'status': file_status,
                    'error': 'Unable to generate diff'
                }
        
        # Summarize changes
        total_changes = sum(
            diff.get('changes', {}).get('total_lines_changed', 0) 
            for diff in file_diffs.values() 
            if isinstance(diff, dict)
        )
        
        return {
            'commit1': commit1_hash,
            'commit2': commit2_hash,
            'file_diffs': file_diffs,
            'total_changes': total_changes,
            'files_changed': len(file_diffs)
        }
    
    def diff_working_directory(self, commit_hash: Optional[str] = None) -> Dict:
        """
        Generate a diff between the working directory and a specific commit.
        
        :param commit_hash: Optional commit hash to compare against
        :return: Diff information for changed files
        """
        # If no commit specified, compare with latest commit logic would go here
        # For this implementation, we'll compare with the most recent commit
        
        # If commit specified, load its files
        if commit_hash:
            commit_path = os.path.join(self.commits_dir, commit_hash)
            if not os.path.exists(commit_path):
                raise ValueError(f"Commit {commit_hash} does not exist")
            
            with open(os.path.join(commit_path, 'metadata.json'), 'r') as f:
                commit_metadata = json.load(f)
        else:
            commit_metadata = {'files': []}
        
        # Track working directory differences
        working_diffs = {}
        
        # Walk through repository files
        for root, _, files in os.walk(self.repo_path):
            for file in files:
                # Skip dot directories
                if '.source-control' in root:
                    continue
                
                # Get full and relative paths
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, self.repo_path)
                
                # Skip if in .gitignore equivalent
                if any(part.startswith('.') for part in rel_path.split(os.path.sep)):
                    continue
                
                # Check if file exists in commit
                commit_file = next(
                    (f for f in commit_metadata['files'] if f['path'] == rel_path), 
                    None
                )
                
                # Generate diff if file has changed
                if not commit_file:
                    # New file
                    working_diffs[rel_path] = {
                        'status': 'added',
                        'diff': self.generate_file_diff('/dev/null', full_path)
                    }
                else:
                    # Compare with commit version
                    commit_file_path = os.path.join(self.commits_dir, commit_hash, rel_path)
                    try:
                        diff = self.generate_file_diff(commit_file_path, full_path)
                        if diff['is_different']:
                            working_diffs[rel_path] = {
                                'status': 'modified',
                                'diff': diff
                            }
                    except Exception:
                        # Handle any file reading errors
                        working_diffs[rel_path] = {
                            'status': 'error',
                            'error': 'Unable to generate diff'
                        }
        
        return {
            'working_diffs': working_diffs,
            'total_changes': len(working_diffs)
        }