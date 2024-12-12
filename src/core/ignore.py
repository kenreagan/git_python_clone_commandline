import os
import fnmatch
import re
from pathlib import Path

class IgnoreManager:
    """
    Manages file and directory ignore patterns for the source control system.
    """
    IGNORE_FILE = '.dscsignore'

    def __init__(self, repository):
        """
        Initialize the IgnoreManager for a specific repository.
        
        :param repository: Repository instance
        """
        self.repository = repository
        self.ignore_file_path = os.path.join(repository.path, self.IGNORE_FILE)
        self.ignore_patterns = []
        self._load_ignore_patterns()

    def _load_ignore_patterns(self):
        """
        Load ignore patterns from the .dscsignore file.
        """
        if os.path.exists(self.ignore_file_path):
            with open(self.ignore_file_path, 'r') as f:
                self.ignore_patterns = [
                    line.strip() 
                    for line in f 
                    if line.strip() and not line.startswith('#')
                ]

    def add(self, pattern):
        """
        Add a new ignore pattern.
        
        :param pattern: File or directory pattern to ignore
        """
        # Avoid duplicates
        if pattern not in self.ignore_patterns:
            self.ignore_patterns.append(pattern)
            
            # Append to the ignore file
            with open(self.ignore_file_path, 'a') as f:
                f.write(f"{pattern}\n")

    def should_ignore(self, path):
        """
        Determine if a given path should be ignored.
        
        :param path: File or directory path to check
        :return: Boolean indicating if path should be ignored
        """
        # Convert path to relative path from repository root
        rel_path = os.path.relpath(path, self.repository.path)
        
        # Check against each ignore pattern
        for pattern in self.ignore_patterns:
            # Handle directory patterns
            if pattern.endswith('/'):
                if fnmatch.fnmatch(rel_path + '/', pattern):
                    return True
            
            # Handle file patterns using glob-style matching
            if fnmatch.fnmatch(rel_path, pattern):
                return True
            
            # Handle more complex patterns
            try:
                # Convert glob pattern to regex
                regex_pattern = self._glob_to_regex(pattern)
                if re.match(regex_pattern, rel_path):
                    return True
            except re.error:
                # If regex conversion fails, skip this pattern
                pass
        
        return False

    def _glob_to_regex(self, pattern):
        """
        Convert glob pattern to regex pattern.
        
        :param pattern: Glob-style pattern
        :return: Regex pattern
        """
        # Escape special regex characters
        regex = re.escape(pattern)
        
        # Replace glob wildcards with regex equivalents
        regex = regex.replace(r'\*', '.*')  # * matches any number of characters
        regex = regex.replace(r'\?', '.')   # ? matches single character
        
        # Ensure full path matching
        regex = f'^{regex}$'
        
        return regex

    def list_ignored_files(self, directory=None):
        """
        List all files that would be ignored in a given directory.
        
        :param directory: Directory to search (defaults to repository root)
        :return: List of ignored file paths
        """
        if directory is None:
            directory = self.repository.path
        
        ignored_files = []
        
        # Walk through directory
        for root, dirs, files in os.walk(directory):
            # Check directories
            dirs[:] = [d for d in dirs if not self.should_ignore(os.path.join(root, d))]
            
            # Check files
            for file in files:
                full_path = os.path.join(root, file)
                if self.should_ignore(full_path):
                    ignored_files.append(full_path)
        
        return ignored_files

    def clear_ignore_patterns(self):
        """
        Clear all ignore patterns.
        """
        self.ignore_patterns = []
        
        # Remove the ignore file if it exists
        if os.path.exists(self.ignore_file_path):
            os.remove(self.ignore_file_path)

    def get_ignore_patterns(self):
        """
        Retrieve current ignore patterns.
        
        :return: List of ignore patterns
        """
        return self.ignore_patterns.copy()