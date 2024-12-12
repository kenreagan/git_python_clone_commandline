import os
import hashlib
import shutil
from pathlib import Path
from .ignore import IgnoreManager

class Staging:
    """
    Manages the staging area for files in the distributed source control system.
    """
    STAGING_DIR = 'staged'
    INDEX_FILE = 'index'

    def __init__(self, repository):
        """
        Initialize the staging area for a repository.
        
        :param repository: Repository instance
        """
        self.repository = repository
        self.dscs_path = os.path.join(repository.path, repository.DSCS_DIR)
        self.staging_path = os.path.join(self.dscs_path, self.STAGING_DIR)
        self.index_path = os.path.join(self.dscs_path, self.INDEX_FILE)
        
        # Create staging directory if it doesn't exist
        os.makedirs(self.staging_path, exist_ok=True)
        
        # Initialize ignore manager
        self.ignore_manager = IgnoreManager(repository)

    def _calculate_file_hash(self, filepath):
        """
        Calculate SHA-256 hash of a file.
        
        :param filepath: Path to the file
        :return: File hash
        """
        hasher = hashlib.sha256()
        with open(filepath, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hasher.update(chunk)
        return hasher.hexdigest()

    def add(self, filepath):
        """
        Stage a file or directory.
        
        :param filepath: Path to file or directory to stage
        :raises ValueError: If file/directory doesn't exist or is ignored
        """
        # Resolve absolute path
        abs_filepath = os.path.abspath(filepath)
        
        # Check if path exists
        if not os.path.exists(abs_filepath):
            raise ValueError(f"Path does not exist: {abs_filepath}")
        
        # Check if path is ignored
        if self.ignore_manager.should_ignore(abs_filepath):
            print(f"Skipping ignored path: {abs_filepath}")
            return

        # If it's a directory, stage all non-ignored files recursively
        if os.path.isdir(abs_filepath):
            for root, _, files in os.walk(abs_filepath):
                for file in files:
                    full_file_path = os.path.join(root, file)
                    if not self.ignore_manager.should_ignore(full_file_path):
                        self._stage_single_file(full_file_path)
        else:
            # Stage single file
            self._stage_single_file(abs_filepath)

    def _stage_single_file(self, filepath):
        """
        Stage a single file.
        
        :param filepath: Path to the file to stage
        """
        # Calculate file hash
        file_hash = self._calculate_file_hash(filepath)
        
        # Create staging path
        rel_path = os.path.relpath(filepath, self.repository.path)
        staged_path = os.path.join(self.staging_path, file_hash)
        
        # Copy file to staging area
        os.makedirs(os.path.dirname(staged_path), exist_ok=True)
        shutil.copy2(filepath, staged_path)
        
        # Update index
        self._update_index(rel_path, file_hash)

    def _update_index(self, rel_path, file_hash):
        """
        Update the staging index.
        
        :param rel_path: Relative path of the file
        :param file_hash: Hash of the staged file
        """
        # Read existing index
        index = self._read_index()
        
        # Update or add file entry
        index[rel_path] = {
            'hash': file_hash,
            'staged_at': os.path.getctime(os.path.join(self.staging_path, file_hash))
        }
        
        # Write updated index
        with open(self.index_path, 'w') as f:
            import json
            json.dump(index, f, indent=2)

    def _read_index(self):
        """
        Read the staging index.
        
        :return: Dictionary of staged files
        """
        try:
            with open(self.index_path, 'r') as f:
                import json
                return json.load(f)
        except FileNotFoundError:
            return {}

    def status(self):
        """
        Get the status of files in the repository.
        
        :return: Dictionary of file statuses
        """
        # Get current index
        index = self._read_index()
        
        # Prepare status report
        status = {
            'staged': [],
            'modified': [],
            'untracked': []
        }
        
        # Check all files in the repository
        for root, _, files in os.walk(self.repository.path):
            for file in files:
                full_path = os.path.join(root, file)
                
                # Skip .dscs directory and ignored files
                if (self.dscs_path in full_path or 
                    self.ignore_manager.should_ignore(full_path)):
                    continue
                
                # Get relative path
                rel_path = os.path.relpath(full_path, self.repository.path)
                
                # Check file status
                if rel_path in index:
                    # File is tracked
                    current_hash = self._calculate_file_hash(full_path)
                    if current_hash != index[rel_path]['hash']:
                        status['modified'].append(rel_path)
                    else:
                        status['staged'].append(rel_path)
                else:
                    # Untracked file
                    status['untracked'].append(rel_path)
        
        return status

    def reset(self, filepath=None):
        """
        Unstage files.
        
        :param filepath: Specific file to unstage (optional)
        """
        # Read current index
        index = self._read_index()
        
        if filepath:
            # Unstage specific file
            rel_path = os.path.relpath(filepath, self.repository.path)
            if rel_path in index:
                # Remove from index
                file_hash = index[rel_path]['hash']
                del index[rel_path]
                
                # Remove from staging area
                staged_file_path = os.path.join(self.staging_path, file_hash)
                if os.path.exists(staged_file_path):
                    os.remove(staged_file_path)
        else:
            # Unstage all files
            for rel_path, file_info in list(index.items()):
                staged_file_path = os.path.join(self.staging_path, file_info['hash'])
                if os.path.exists(staged_file_path):
                    os.remove(staged_file_path)
                del index[rel_path]
        
        # Write updated index
        with open(self.index_path, 'w') as f:
            import json
            json.dump(index, f, indent=2)

    def get_staged_files(self):
        """
        Get list of staged files.
        
        :return: List of staged file paths
        """
        index = self._read_index()
        return list(index.keys())