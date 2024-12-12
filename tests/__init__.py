import os
import shutil
import tempfile
import unittest

from src.core.repository import Repository

class TestRepository(unittest.TestCase):
    def setUp(self):
        # Create a temporary directory for each test
        self.test_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        # Remove the temporary directory after each test
        shutil.rmtree(self.test_dir)
    
    def test_initialize_repository(self):
        """
        Test repository initialization creates required directories and files
        """
        repo_path = os.path.join(self.test_dir, 'my_repo')
        
        # Initialize repository
        Repository.init(repo_path)
        
        # Check core directories exist
        dot_dir = os.path.join(repo_path, '.source-control')
        self.assertTrue(os.path.exists(dot_dir), "Dot directory should be created")
        
        # Check specific subdirectories
        expected_subdirs = [
            'commits',
            'staging',
            'branches'
        ]
        for subdir in expected_subdirs:
            self.assertTrue(
                os.path.exists(os.path.join(dot_dir, subdir)), 
                f"{subdir} directory should exist"
            )
        
        # Check configuration files
        config_files = [
            'branches.json',
            'config.json'
        ]
        for config_file in config_files:
            self.assertTrue(
                os.path.exists(os.path.join(dot_dir, config_file)), 
                f"{config_file} should be created"
            )
    
    def test_initialize_existing_repository(self):
        """
        Test initializing an already initialized repository
        """
        repo_path = os.path.join(self.test_dir, 'existing_repo')
        
        # First initialization
        Repository.init(repo_path)
        
        # Second initialization should not raise an error
        try:
            Repository.init(repo_path)
        except Exception as e:
            self.fail(f"Reinitializing repository raised an unexpected error: {e}")
    
    def test_repository_config(self):
        """
        Test repository configuration is correctly set
        """
        repo_path = os.path.join(self.test_dir, 'config_repo')
        
        # Initialize repository
        Repository.init(repo_path)
        
        # Check configuration file contents
        config_path = os.path.join(repo_path, '.source-control', 'config.json')
        self.assertTrue(os.path.exists(config_path), "Config file should exist")
        
        # Optionally, add more specific config content checks here

if __name__ == '__main__':
    unittest.main()