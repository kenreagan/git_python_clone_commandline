import os
import tempfile
import shutil
import unittest

from src.core.repository import RepositoryInitializer
from src.core.branch import BranchManager

class TestBranchManager(unittest.TestCase):
    def setUp(self):
        # Create a temporary repository for each test
        self.test_dir = tempfile.mkdtemp()
        self.repo_path = os.path.join(self.test_dir, 'test_repo')
        RepositoryInitializer.init(self.repo_path)
        
        # Initialize branch manager
        self.branch_manager = BranchManager(self.repo_path)
    
    def tearDown(self):
        # Remove the temporary directory after each test
        shutil.rmtree(self.test_dir)
    
    def test_create_branch(self):
        """
        Test creating a new branch
        """
        # Create a new branch
        branch_name = 'feature-test'
        branch_info = self.branch_manager.create_branch(branch_name)
        
        # Verify branch creation
        self.assertIsNotNone(branch_info, "Branch should be created")
        
        # List branches to confirm
        branches = self.branch_manager.list_branches()
        self.assertIn(branch_name, branches['branches'], "New branch should be in branch list")
    
    def test_switch_branch(self):
        """
        Test switching between branches
        """
        # Create a new branch
        branch_name = 'feature-switch'
        self.branch_manager.create_branch(branch_name)
        
        # Switch to the new branch
        switched_branch = self.branch_manager.switch_branch(branch_name)
        
        # Verify current branch
        self.assertEqual(switched_branch, branch_name, "Should switch to the new branch")
        self.assertEqual(
            self.branch_manager.get_current_branch(), 
            branch_name, 
            "Current branch should be updated"
        )
    
    def test_branch_head_management(self):
        """
        Test updating and retrieving branch head commits
        """
        # Create a new branch
        branch_name = 'feature-head'
        self.branch_manager.create_branch(branch_name)
        
        # Update branch head
        test_commit_hash = 'abc123'
        self.branch_manager.update_branch_head(branch_name, test_commit_hash)
        
        # Retrieve branch head
        head_commit = self.branch_manager.get_branch_head(branch_name)
        
        self.assertEqual(head_commit, test_commit_hash, "Branch head should be updated")
    
    def test_multiple_branch_creation(self):
        """
        Test creating multiple branches
        """
        branch_names = ['feature1', 'feature2', 'feature3']
        
        # Create multiple branches
        for branch in branch_names:
            self.branch_manager.create_branch(branch)
        
        # List branches
        branches = self.branch_manager.list_branches()
        
        # Verify all branches were created
        for branch in branch_names:
            self.assertIn(branch, branches['branches'], f"{branch} should exist")
    
    def test_branch_creation_errors(self):
        """
        Test error handling for branch creation
        """
        # Create initial branch
        initial_branch = 'feature-initial'
        self.branch_manager.create_branch(initial_branch)
        
        # Try creating a branch with the same name
        with self.assertRaises(ValueError, msg="Should raise error for duplicate branch"):
            self.branch_manager.create_branch(initial_branch)
        
        # Test invalid branch name
        with self.assertRaises(ValueError, msg="Should raise error for invalid branch name"):
            self.branch_manager.create_branch('invalid/branch/name')
    
    def test_default_branch_exists(self):
        """
        Verify that a default 'main' branch exists on repository initialization
        """
        branches = self.branch_manager.list_branches()
        self.assertIn('main', branches['branches'], "Default 'main' branch should exist")
        self.assertEqual(
            branches['current_branch'], 
            'main', 
            "Current branch should be 'main' by default"
        )

if __name__ == '__main__':
    unittest.main()