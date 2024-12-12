import os
import hashlib
import json
import shutil
from datetime import datetime
from typing import List, Dict, Optional

class Commit:
    """
    Manages commits for a source control repository.
    Handles creating commits, tracking changes, and managing commit objects.
    """
    
    def __init__(self, repo_path: str):
        """
        Initialize commit management for a repository.
        
        :param repo_path: Path to the root of the repository
        """
        self.repo_path = repo_path
        self.dot_dir = os.path.join(repo_path, '.source-control')
        self.staging_dir = os.path.join(self.dot_dir, 'staging')
        self.commits_dir = os.path.join(self.dot_dir, 'commits')
        
        # Create necessary directories
        os.makedirs(self.staging_dir, exist_ok=True)
        os.makedirs(self.commits_dir, exist_ok=True)
    
    def _calculate_file_hash(self, file_path: str) -> str:
        """
        Calculate SHA-256 hash of a file.
        
        :param file_path: Path to the file
        :return: Hexadecimal hash of the file
        """
        hasher = hashlib.sha256()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hasher.update(chunk)
        return hasher.hexdigest()
    
    def stage_file(self, file_path: str):
        """
        Stage a file for commit.
        
        :param file_path: Path to the file to be staged
        :raises ValueError: If file is outside repository or doesn't exist
        """
        # Ensure file is within the repository
        abs_file_path = os.path.abspath(file_path)
        if not abs_file_path.startswith(os.path.abspath(self.repo_path)):
            raise ValueError("Cannot stage files outside the repository")
        
        if not os.path.exists(abs_file_path):
            raise ValueError(f"File does not exist: {file_path}")
        
        # Create staging path
        rel_path = os.path.relpath(abs_file_path, self.repo_path)
        staged_path = os.path.join(self.staging_dir, rel_path)
        
        # Ensure staging subdirectory exists
        os.makedirs(os.path.dirname(staged_path), exist_ok=True)
        
        # Copy file to staging area
        shutil.copy2(abs_file_path, staged_path)
    
    def get_staged_files(self) -> List[str]:
        """
        Get list of staged files.
        
        :return: List of relative paths of staged files
        """
        staged_files = []
        for root, _, files in os.walk(self.staging_dir):
            for file in files:
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, self.staging_dir)
                staged_files.append(rel_path)
        return staged_files
    
    def create_commit(self, message: str, author: str = 'Anonymous') -> Dict:
        """
        Create a new commit from staged files.
        
        :param message: Commit message
        :param author: Author of the commit
        :return: Commit metadata dictionary
        :raises ValueError: If no files are staged
        """
        staged_files = self.get_staged_files()
        if not staged_files:
            raise ValueError("No files staged for commit")
        
        # Generate commit hash
        commit_hash = hashlib.sha256(
            f"{message}{author}{datetime.now().isoformat()}".encode()
        ).hexdigest()[:8]
        
        # Create commit directory
        commit_dir = os.path.join(self.commits_dir, commit_hash)
        os.makedirs(commit_dir)
        
        # Track changed files
        files_metadata = []
        for staged_file in staged_files:
            # Copy staged file to commit directory
            src_path = os.path.join(self.staging_dir, staged_file)
            dest_path = os.path.join(commit_dir, staged_file)
            
            # Ensure destination directory exists
            os.makedirs(os.path.dirname(dest_path), exist_ok=True)
            shutil.copy2(src_path, dest_path)
            
            # Calculate file hash
            file_hash = self._calculate_file_hash(src_path)
            
            # Store file metadata
            files_metadata.append({
                'path': staged_file,
                'hash': file_hash
            })
        
        # Create commit metadata
        commit_metadata = {
            'hash': commit_hash,
            'message': message,
            'author': author,
            'timestamp': datetime.now().isoformat(),
            'files': files_metadata
        }
        
        # Write commit metadata
        with open(os.path.join(commit_dir, 'metadata.json'), 'w') as f:
            json.dump(commit_metadata, f, indent=2)
        
        # Clear staging area
        self._clear_staging_area()
        
        return commit_metadata
    
    def _clear_staging_area(self):
        """
        Clear all files from the staging area.
        """
        for root, dirs, files in os.walk(self.staging_dir):
            for file in files:
                os.unlink(os.path.join(root, file))
            for dir in dirs:
                os.rmdir(os.path.join(root, dir))
    
    def get_commit_details(self, commit_hash: str) -> Optional[Dict]:
        """
        Retrieve details of a specific commit.
        
        :param commit_hash: Hash of the commit to retrieve
        :return: Commit metadata or None if not found
        """
        commit_path = os.path.join(self.commits_dir, commit_hash)
        metadata_path = os.path.join(commit_path, 'metadata.json')
        
        if not os.path.exists(metadata_path):
            return None
        
        with open(metadata_path, 'r') as f:
            return json.load(f)
    
    def restore_commit_files(self, commit_hash: str, destination: Optional[str] = None):
        """
        Restore files from a specific commit.
        
        :param commit_hash: Hash of the commit to restore
        :param destination: Optional destination path (defaults to repository root)
        :raises ValueError: If commit does not exist
        """
        commit_path = os.path.join(self.commits_dir, commit_hash)
        
        if not os.path.exists(commit_path):
            raise ValueError(f"Commit {commit_hash} does not exist")
        
        # Use repository root if no destination specified
        destination = destination or self.repo_path
        
        # Copy files from commit to destination
        for root, _, files in os.walk(commit_path):
            # Skip metadata file
            if 'metadata.json' in files:
                files.remove('metadata.json')
            
            for file in files:
                src_file = os.path.join(root, file)
                rel_path = os.path.relpath(src_file, commit_path)
                dest_file = os.path.join(destination, rel_path)
                
                # Ensure destination directory exists
                os.makedirs(os.path.dirname(dest_file), exist_ok=True)
                
                # Copy file
                shutil.copy2(src_file, dest_file)