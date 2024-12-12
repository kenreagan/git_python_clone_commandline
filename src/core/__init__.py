"""
Distributed Source Control System (DSCS)

A lightweight, Python-based version control system inspired by Git.
"""

# Version information
__version__ = "0.1.0"
__author__ = "Lumuli Ken Reagan"
__email__ = "lumulikenreagan@gmail.com"

# Import key components to make them easily accessible
from .repository import Repository
from .staging import Staging
from .commit import Commit
from .branch import Branch
from .merge import Merge
from .diff import Diff
from .history import History
from .ignore import IgnoreManager

# Expose package-level exceptions
class DSCSError(Exception):
    """Base exception for all DSCS-related errors."""
    pass

class RepositoryNotFoundError(DSCSError):
    """Raised when no repository is found in the current or parent directories."""
    pass

class CommitError(DSCSError):
    """Raised when there's an issue with committing changes."""
    pass

class MergeConflictError(DSCSError):
    """Raised when merge conflicts are detected."""
    pass

# Optional package-level configuration
class DSCSConfig:
    """
    Global configuration for the Core Version Control package.
    
    This can be used to set default behaviors or global settings.
    """
    # Default configuration
    _config = {
        'default_branch': 'main',
        'auto_initialize': False,
        'verbose_logging': False
    }

    @classmethod
    def get(cls, key, default=None):
        """
        Retrieve a configuration value.
        
        :param key: Configuration key
        :param default: Default value if key is not found
        :return: Configuration value
        """
        return cls._config.get(key, default)

    @classmethod
    def set(cls, key, value):
        """
        Set a configuration value.
        
        :param key: Configuration key
        :param value: Configuration value
        """
        cls._config[key] = value

def init_repo(path='.', auto_create=False):
    """
    Convenience function to initialize a repository.
    
    :param path: Path to initialize repository
    :param auto_create: Automatically create repository if not exists
    :return: Repository instance
    :raises RepositoryNotFoundError: If repository doesn't exist and auto_create is False
    """
    try:
        return Repository.find_repo_root(path)
    except Exception:
        if auto_create or DSCSConfig.get('auto_initialize', False):
            return Repository(path).initialize()
        raise RepositoryNotFoundError(f"No DSCS repository found in {path}")

# Optional logging setup
import logging

def setup_logging(level=logging.INFO):
    """
    Configure logging for the DSCS package.
    
    :param level: Logging level
    """
    logging.basicConfig(
        level=level,
        format='%(asctime)s - DSCS - %(levelname)s - %(message)s'
    )
    return logging.getLogger('dscs')

# Expose package-level functionality
__all__ = [
    'Repository', 
    'Staging', 
    'Commit', 
    'Branch', 
    'Merge', 
    'Diff', 
    'History', 
    'IgnoreManager',
    'DSCSError',
    'RepositoryNotFoundError',
    'CommitError',
    'MergeConflictError',
    'init_repo',
    'setup_logging'
]