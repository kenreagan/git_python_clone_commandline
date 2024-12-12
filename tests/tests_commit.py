import os
import tempfile
import shutil
import unittest

from src.core.repository import Repository
from src.core.commit import Commit

class TestCommit(unittest.TestCase):
    def setUp(self):
        # Create a temporary repository for each test
        self.test_dir = tempfile.mkdtemp()
        self.repo_path = os.path.join(self.test_dir, 'test_repo')
        Repository.init(self.repo_path)
        
        # Create some test files
        self.test_files = {
            'file1.txt': 'Hello, world!',
            'subdir/file2.txt': 'Test content'
        }
        
        for path, content in self.test_files.items():
            full_path = os.path.join(self.repo_path, path)
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            with open(full_path, 'w') as f:
                f.write(content)
        
        # Initialize commit manager
        self.commit_manager = Commit(self.repo_path)
    
    def tearDown(self):
        # Remove the temporary directory after each test
        shutil.rmtree(self.test_dir)
    
    def test_stage_file(self):
        """
        Test staging individual files
        """
        file_path = os.path.join(self.repo_path, 'file1.txt')
        self.commit_manager.stage_file(file_path)
        
        staged_files = self.commit_manager.get_staged_files()
        self.assertIn('file1.txt', staged_files, "File should be in staged files")
    
    def test_create_commit(self):
        """
        Test creating a commit with staged files
        """
        # Stage files
        for path in self.test_files:
            file_path = os.path.join(self.repo_path, path)
            self.commit_manager.stage_file(file_path)
        
        # Create commit
        commit = self.commit_manager.create_commit(
            message='Test commit', 
            author='Test User'
        )
        
        # Verify commit metadata
        self.assertIn('hash', commit, "Commit should have a hash")
        self.assertEqual(commit['message'], 'Test commit', "Commit message should match")
        self.assertEqual(commit['author'], 'Test User', "Commit author should match")
        
        # Verify commit files were saved
        commit_path = os.path.join(
            self.repo_path, 
            '.source-control', 
            'commits', 
            commit['hash']
        )
        for path in self.test_files:
            committed_file = os.path.join(commit_path, path)
            self.assertTrue(os.path.exists(committed_file), f"{path} should be in commit")
    
    def test_get_commit_details(self):
        """
        Test retrieving commit details
        """
        # Stage and commit files
        for path in self.test_files:
            file_path = os.path.join(self.repo_path, path)
            self.commit_manager.stage_file(file_path)
        
        # Create commit
        commit = self.commit_manager.create_commit(
            message='Details test', 
            author='Test User'
        )
        
        # Retrieve commit details
        details = self.commit_manager.get_commit_details(commit['hash'])
        
        self.assertIsNotNone(details, "Should retrieve commit details")
        self.assertEqual(details['hash'], commit['hash'], "Commit hash should match")
        self.assertEqual(details['message'], 'Details test', "Commit message should match")
    
    def test_restore_commit_files(self):
        """
        Test restoring files from a previous commit
        """
        # Stage and commit files
        for path, content in self.test_files.items():
            file_path = os.path.join(self.repo_path, path)
            self.commit_manager.stage_file(file_path)
        
        # Create initial commit
        initial_commit = self.commit_manager.create_commit(
            message='Initial commit', 
            author='Test User'
        )
        
        # Modify files
        for path, content in self.test_files.items():
            file_path = os.path.join(self.repo_path, path)
            with open(file_path, 'w') as f:
                f.write(content + ' modified')
        
        # Restore files from initial commit
        restore_dir = os.path.join(self.test_dir, 'restored')
        os.makedirs(restore_dir)
        
        self.commit_manager.restore_commit_files(
            initial_commit['hash'], 
            destination=restore_dir
        )
        
        # Verify restored files
        for path, content in self.test_files.items():
            restored_file = os.path.join(restore_dir, path)
            self.assertTrue(os.path.exists(restored_file), f"{path} should be restored")
            
            with open(restored_file, 'r') as f:
                self.assertEqual(f.read(), content, f"Content of {path} should match")

if __name__ == '__main__':
    unittest.main()