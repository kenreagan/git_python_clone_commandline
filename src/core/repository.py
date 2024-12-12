import os
import shutil
import json
from pathlib import Path
import uuid

class Repository:
    """
    Manages repository initialization, configuration, and basic repository operations.
    """
    CORE_DIR = '.core'
    CONFIG_FILE = 'config.json'
    HEAD_FILE = 'HEAD'
    BRANCHES_DIR = 'branches'
    COMMITS_DIR = 'commits'
    OBJECTS_DIR = 'objects'

    def __init__(self, path='.'):
        """
        Initialize a Repository instance.
        
        :param path: Path to the repository (default is current directory)
        """
        self.path = os.path.abspath(path)
        self.core_path = os.path.join(self.path, self.CORE_DIR)
        self.name = os.path.basename(self.path)

    @classmethod
    def find_repo_root(cls, start_path=None):
        """
        Find the root of the core repository by traversing up the directory tree.
        
        :param start_path: Starting path to search from (default is current directory)
        :return: Path to the repository root
        :raises Exception: If no repository is found
        """
        if start_path is None:
            start_path = os.getcwd()
        
        current_path = os.path.abspath(start_path)
        
        while current_path != os.path.dirname(current_path):
            core_path = os.path.join(current_path, cls.CORE_DIR)
            if os.path.exists(core_path) and os.path.isdir(core_path):
                return current_path
            current_path = os.path.dirname(current_path)
        
        raise Exception("Not a core repository (or any parent up to root)")

    def initialize(self):
        """
        Initialize a new repository by creating the necessary directory structure.
        """
        # Create core directory
        os.makedirs(self.core_path, exist_ok=True)
        
        # Create subdirectories
        subdirs = [
            self.BRANCHES_DIR,
            self.COMMITS_DIR,
            self.OBJECTS_DIR
        ]
        for subdir in subdirs:
            os.makedirs(os.path.join(self.core_path, subdir), exist_ok=True)
        
        # Create initial configuration
        config = {
            'version': '0.1.0',
            'id': str(uuid.uuid4()),
            'created_at': str(os.path.getctime(self.path))
        }
        
        # Write config file
        config_path = os.path.join(self.core_path, self.CONFIG_FILE)
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
        
        # Create initial HEAD file pointing to main branch
        head_path = os.path.join(self.core_path, self.HEAD_FILE)
        with open(head_path, 'w') as f:
            f.write('refs/branches/main')
        
        # Create initial main branch
        main_branch_path = os.path.join(self.core_path, self.BRANCHES_DIR, 'main')
        with open(main_branch_path, 'w') as f:
            f.write('')  # Empty initial branch
        
        return self

    def clone(self, destination):
        """
        Clone the repository to a new location.
        
        :param destination: Path to clone the repository to
        :return: New Repository instance
        """
        # Create destination directory
        dest_path = os.path.abspath(destination)
        os.makedirs(dest_path, exist_ok=True)
        
        # Copy entire repository contents
        shutil.copytree(self.path, dest_path, dirs_exist_ok=True)
        
        # Return new Repository instance
        return Repository(dest_path)

    def get_current_branch(self):
        """
        Get the current active branch.
        
        :return: Name of the current branch
        """
        head_path = os.path.join(self.core_path, self.HEAD_FILE)
        with open(head_path, 'r') as f:
            branch_ref = f.read().strip()
        
        return os.path.basename(branch_ref)

    def set_current_branch(self, branch_name):
        """
        Set the current active branch.
        
        :param branch_name: Name of the branch to set as current
        """
        head_path = os.path.join(self.core_path, self.HEAD_FILE)
        with open(head_path, 'w') as f:
            f.write(f'refs/branches/{branch_name}')

    def get_config(self):
        """
        Read repository configuration.
        
        :return: Dictionary of repository configuration
        """
        config_path = os.path.join(self.core_path, self.CONFIG_FILE)
        with open(config_path, 'r') as f:
            return json.load(f)

    def store_object(self, content, object_type='blob'):
        """
        Store an object in the repository's object store.
        
        :param content: Content to store
        :param object_type: Type of object (blob, tree, commit)
        :return: Object hash
        """
        # Generate a unique hash for the object
        object_hash = str(uuid.uuid4())
        
        # Create object file
        object_path = os.path.join(
            self.core_path, 
            self.OBJECTS_DIR, 
            object_hash
        )
        
        # Store object metadata
        object_metadata = {
            'type': object_type,
            'size': len(content)
        }
        
        with open(object_path, 'wb') as f:
            json.dump(object_metadata, f)
            f.write(b'\n')  # Separator
            f.write(content.encode() if isinstance(content, str) else content)
        
        return object_hash

    def get_object(self, object_hash):
        """
        Retrieve an object from the object store.
        
        :param object_hash: Hash of the object to retrieve
        :return: Object content and metadata
        """
        object_path = os.path.join(
            self.core_path, 
            self.OBJECTS_DIR, 
            object_hash
        )
        
        with open(object_path, 'rb') as f:
            # Read metadata
            metadata = json.loads(f.readline().decode())
            
            # Read content (skip the newline)
            content = f.read()
        
        return {
            'metadata': metadata,
            'content': content.decode()
        }