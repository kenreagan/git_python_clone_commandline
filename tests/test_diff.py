import os
import tempfile
import shutil
import unittest

from src.core.repository import Repository
from src.core.commit import Commit
from src.core.diff import Diff

class TestDiffManager(unittest.TestCase):
    def setUp(self):
        # Create a temporary repository for each test
        self.test_dir = tempfile.mkdtemp()
        self.repo_path = os.path.join(self.test_dir, 'test_repo')
        Repository.init(self.repo_path)
        
        # Create some test files
        self.test_files = {
            'file1.txt': 'First version of content',
            'file2.txt': 'Another initial content',
            'subdir/file3.txt': 'Subdirectory file content'
        }
        
        # Create test files
        for path, content in self.test_files.items():
            full_path = os.path.join(self.repo_path, path)
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            with open(full_path, 'w') as f:
                f.write(content)
        
        # Initialize managers
        self.commit_manager = Commit(self.repo_path)
        self.diff_manager = Diff(self.repo_path)
    
    def tearDown(self):
        # Remove the temporary directory after each test
        shutil.rmtree(self.test_dir)
    
    def test_file_diff(self):
        """
        Test generating diff between two files
        """
        # Create first version of a file
        file_path = os.path.join(self.repo_path, 'diff_test.txt')
        with open(file_path, 'w') as f:
            f.write('Initial content\nMultiple lines\nTest file')
        
        # Create second version
        with open(file_path, 'w') as f:
            f.write('Modified content\nMultiple lines\nUpdated test file')
        
        # Generate diff
        diff = self.diff_manager.generate_file_diff(
            os.path.join(self.repo_path, 'diff_test.txt'),
            os.path.join(self.repo_path, 'diff_test.txt')
        )
        
        # Verify diff properties
        self.assertIn('diff_lines', diff, "Diff should have lines")
        self.assertIn('changes', diff, "Diff should have change statistics")
        self.assertTrue(diff['is_different'], "Files should be different")
    