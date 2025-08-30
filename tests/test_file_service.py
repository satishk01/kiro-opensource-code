"""
Unit tests for file service
"""
import unittest
from unittest.mock import patch, mock_open, MagicMock
import tempfile
import os
import sys

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.file_service import FileService

class TestFileService(unittest.TestCase):
    
    def setUp(self):
        self.file_service = FileService()
    
    def test_filter_text_files(self):
        """Test filtering of text files"""
        files = {
            'test.py': {'content': 'print("hello")', 'size': 100},
            'image.jpg': {'content': b'binary data', 'size': 1000},
            'readme.md': {'content': '# Title', 'size': 50},
            'data.bin': {'content': b'binary', 'size': 200}
        }
        
        filtered = self.file_service.filter_text_files(files)
        
        self.assertIn('test.py', filtered)
        self.assertIn('readme.md', filtered)
        self.assertNotIn('image.jpg', filtered)
        self.assertNotIn('data.bin', filtered)
    
    def test_get_file_stats(self):
        """Test file statistics calculation"""
        files = {
            'file1.py': {'content': 'content1', 'size': 100},
            'file2.js': {'content': 'content2', 'size': 200},
            'file3.md': {'content': 'content3', 'size': 150}
        }
        
        stats = self.file_service.get_file_stats(files)
        
        self.assertEqual(stats['total_files'], 3)
        self.assertEqual(stats['total_size'], 450)
        self.assertIn('py', stats['file_types'])
        self.assertIn('js', stats['file_types'])
        self.assertIn('md', stats['file_types'])
    
    @patch('os.path.exists')
    @patch('os.path.isdir')
    def test_validate_folder_path(self, mock_isdir, mock_exists):
        """Test folder path validation"""
        mock_exists.return_value = True
        mock_isdir.return_value = True
        
        result = self.file_service.validate_folder_path('/valid/path')
        self.assertTrue(result['valid'])
        
        mock_exists.return_value = False
        result = self.file_service.validate_folder_path('/invalid/path')
        self.assertFalse(result['valid'])
    
    @patch('builtins.open', new_callable=mock_open, read_data='file content')
    @patch('os.walk')
    def test_read_folder_files(self, mock_walk, mock_file):
        """Test reading files from folder"""
        mock_walk.return_value = [
            ('/test', [], ['file1.py', 'file2.txt']),
            ('/test/sub', [], ['file3.js'])
        ]
        
        with patch.object(self.file_service, 'is_text_file', return_value=True):
            files = self.file_service.read_folder_files('/test')
            
            self.assertEqual(len(files), 3)
            self.assertIn('file1.py', files)
            self.assertIn('file2.txt', files)
            self.assertIn('file3.js', files)
    
    def test_is_text_file(self):
        """Test text file detection"""
        self.assertTrue(self.file_service.is_text_file('test.py'))
        self.assertTrue(self.file_service.is_text_file('readme.md'))
        self.assertTrue(self.file_service.is_text_file('config.json'))
        self.assertFalse(self.file_service.is_text_file('image.jpg'))
        self.assertFalse(self.file_service.is_text_file('data.bin'))
    
    def test_analyze_code_structure(self):
        """Test code structure analysis"""
        python_code = '''
import os
import sys

class TestClass:
    def __init__(self):
        self.value = 42
    
    def method(self):
        return self.value

def function():
    return "hello"
'''
        
        analysis = self.file_service.analyze_code_structure(python_code, 'test.py')
        
        self.assertEqual(analysis['language'], 'python')
        self.assertIn('TestClass', analysis['classes'])
        self.assertIn('function', analysis['functions'])
        self.assertIn('os', analysis['imports'])
        self.assertIn('sys', analysis['imports'])

if __name__ == '__main__':
    unittest.main()