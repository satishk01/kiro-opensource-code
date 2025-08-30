"""
Unit tests for spec engine
"""
import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engines.spec_engine import SpecEngine

class TestSpecEngine(unittest.TestCase):
    
    def setUp(self):
        self.spec_engine = SpecEngine()
    
    def test_parse_requirements_format(self):
        """Test parsing of requirements in EARS format"""
        requirements_text = """
        # Requirements Document
        
        ## Requirements
        
        ### Requirement 1
        **User Story:** As a user, I want to login, so that I can access the system
        
        #### Acceptance Criteria
        1. WHEN user enters valid credentials THEN system SHALL authenticate user
        2. IF credentials are invalid THEN system SHALL display error message
        """
        
        parsed = self.spec_engine.parse_requirements(requirements_text)
        
        self.assertEqual(len(parsed), 1)
        self.assertIn('User Story', parsed[0])
        self.assertEqual(len(parsed[0]['acceptance_criteria']), 2)
    
    def test_generate_requirements_structure(self):
        """Test requirements document structure generation"""
        feature_description = "User authentication system"
        
        with patch.object(self.spec_engine.ai_service, 'generate_requirements') as mock_ai:
            mock_ai.return_value = "Generated requirements content"
            
            requirements = self.spec_engine.generate_requirements(feature_description)
            
            self.assertIn("# Requirements Document", requirements)
            self.assertIn("## Introduction", requirements)
            self.assertIn("## Requirements", requirements)
            mock_ai.assert_called_once()
    
    def test_validate_requirements_format(self):
        """Test requirements format validation"""
        valid_requirements = """
        # Requirements Document
        
        ## Introduction
        Test introduction
        
        ## Requirements
        
        ### Requirement 1
        **User Story:** As a user, I want feature, so that benefit
        
        #### Acceptance Criteria
        1. WHEN event THEN system SHALL response
        """
        
        invalid_requirements = """
        # Some Document
        Random content without proper structure
        """
        
        self.assertTrue(self.spec_engine.validate_requirements_format(valid_requirements))
        self.assertFalse(self.spec_engine.validate_requirements_format(invalid_requirements))
    
    def test_generate_design_document(self):
        """Test design document generation"""
        requirements = "Test requirements content"
        codebase_context = {"files": {"test.py": "content"}}
        
        with patch.object(self.spec_engine.ai_service, 'generate_design') as mock_ai:
            mock_ai.return_value = "Generated design content"
            
            design = self.spec_engine.generate_design(requirements, codebase_context)
            
            self.assertIn("# Design Document", design)
            self.assertIn("## Overview", design)
            self.assertIn("## Architecture", design)
            mock_ai.assert_called_once()
    
    def test_create_task_list(self):
        """Test task list creation"""
        design_doc = "Test design document content"
        requirements_doc = "Test requirements content"
        
        with patch.object(self.spec_engine.ai_service, 'generate_tasks') as mock_ai:
            mock_ai.return_value = [
                {"id": "1", "title": "Setup project", "description": "Initialize project structure"},
                {"id": "2", "title": "Implement auth", "description": "Create authentication system"}
            ]
            
            tasks = self.spec_engine.create_task_list(design_doc, requirements_doc)
            
            self.assertIn("# Implementation Plan", tasks)
            self.assertIn("- [ ]", tasks)
            mock_ai.assert_called_once()
    
    def test_update_document_version(self):
        """Test document version management"""
        original_doc = "Original content"
        updated_doc = "Updated content"
        
        version_info = self.spec_engine.update_document_version(
            original_doc, updated_doc, "requirements"
        )
        
        self.assertEqual(version_info['version'], 2)
        self.assertIn('timestamp', version_info)
        self.assertEqual(version_info['doc_type'], 'requirements')
    
    def test_extract_requirements_references(self):
        """Test extraction of requirement references from tasks"""
        task_content = """
        - [ ] 1. Setup authentication system
          - Implement login functionality
          - _Requirements: 1.1, 1.2_
        
        - [ ] 2. Create user management
          - Add user CRUD operations
          - _Requirements: 2.1, 3.1_
        """
        
        references = self.spec_engine.extract_requirements_references(task_content)
        
        expected_refs = ['1.1', '1.2', '2.1', '3.1']
        for ref in expected_refs:
            self.assertIn(ref, references)
    
    def test_validate_task_format(self):
        """Test task format validation"""
        valid_tasks = """
        # Implementation Plan
        
        - [ ] 1. First task
          - Task description
          - _Requirements: 1.1_
        
        - [ ] 2. Second task
          - Another description
          - _Requirements: 2.1_
        """
        
        invalid_tasks = """
        # Random Document
        Some content without proper task format
        """
        
        self.assertTrue(self.spec_engine.validate_task_format(valid_tasks))
        self.assertFalse(self.spec_engine.validate_task_format(invalid_tasks))

if __name__ == '__main__':
    unittest.main()