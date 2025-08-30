"""
Integration tests for the Kiro Streamlit app
"""
import unittest
from unittest.mock import patch, MagicMock
import sys
import os
import tempfile
import json

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class TestAWSBedrockIntegration(unittest.TestCase):
    """Test AWS Bedrock integration"""
    
    @patch('boto3.Session')
    def test_bedrock_connection(self, mock_session):
        """Test AWS Bedrock connection"""
        from services.ai_service import AIService
        
        # Mock successful connection
        mock_client = MagicMock()
        mock_session.return_value.client.return_value = mock_client
        mock_client.list_foundation_models.return_value = {
            'modelSummaries': [
                {'modelId': 'anthropic.claude-3-5-sonnet-20241022-v2:0'},
                {'modelId': 'amazon.nova-pro-v1:0'}
            ]
        }
        
        ai_service = AIService()
        result = ai_service.test_connection()
        
        self.assertTrue(result['connected'])
        mock_client.list_foundation_models.assert_called_once()
    
    @patch('boto3.Session')
    def test_bedrock_model_invocation(self, mock_session):
        """Test model invocation"""
        from services.ai_service import AIService
        
        mock_client = MagicMock()
        mock_session.return_value.client.return_value = mock_client
        
        # Mock successful model response
        mock_response = {
            'body': MagicMock()
        }
        mock_response['body'].read.return_value = json.dumps({
            'content': [{'text': 'Generated response'}]
        }).encode()
        
        mock_client.invoke_model.return_value = mock_response
        
        ai_service = AIService()
        ai_service.select_model('claude-3-5-sonnet')
        
        response = ai_service.generate_text("Test prompt")
        
        self.assertEqual(response, 'Generated response')
        mock_client.invoke_model.assert_called_once()

class TestEndToEndSpecWorkflow(unittest.TestCase):
    """Test complete spec generation workflow"""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir)
    
    @patch('services.ai_service.AIService')
    @patch('services.file_service.FileService')
    def test_complete_spec_workflow(self, mock_file_service, mock_ai_service):
        """Test complete spec generation from idea to tasks"""
        from engines.spec_engine import SpecEngine
        
        # Mock file service
        mock_file_service_instance = mock_file_service.return_value
        mock_file_service_instance.read_folder_files.return_value = {
            'main.py': {'content': 'print("hello")', 'size': 100},
            'utils.py': {'content': 'def helper(): pass', 'size': 50}
        }
        
        # Mock AI service responses
        mock_ai_service_instance = mock_ai_service.return_value
        mock_ai_service_instance.generate_requirements.return_value = """
        # Requirements Document
        
        ## Introduction
        Test feature for user authentication
        
        ## Requirements
        
        ### Requirement 1
        **User Story:** As a user, I want to login, so that I can access the system
        
        #### Acceptance Criteria
        1. WHEN user enters valid credentials THEN system SHALL authenticate user
        """
        
        mock_ai_service_instance.generate_design.return_value = """
        # Design Document
        
        ## Overview
        Authentication system design
        
        ## Architecture
        Simple login flow with validation
        """
        
        mock_ai_service_instance.generate_tasks.return_value = [
            {"title": "Setup authentication", "description": "Create login system"}
        ]
        
        # Test workflow
        spec_engine = SpecEngine()
        
        # Step 1: Generate requirements
        requirements = spec_engine.generate_requirements("User authentication system")
        self.assertIn("Requirements Document", requirements)
        
        # Step 2: Generate design
        codebase = mock_file_service_instance.read_folder_files('/test')
        design = spec_engine.generate_design(requirements, codebase)
        self.assertIn("Design Document", design)
        
        # Step 3: Generate tasks
        tasks = spec_engine.create_task_list(design, requirements)
        self.assertIn("Implementation Plan", tasks)
    
    @patch('integrations.jira_client.JIRAClient')
    def test_jira_integration_workflow(self, mock_jira_client):
        """Test JIRA integration workflow"""
        mock_jira_instance = mock_jira_client.return_value
        mock_jira_instance.test_connection.return_value = True
        mock_jira_instance.create_ticket.return_value = {'key': 'TEST-123'}
        
        # Test JIRA ticket creation
        tasks = [
            {"title": "Setup project", "description": "Initialize project structure"},
            {"title": "Implement auth", "description": "Create authentication system"}
        ]
        
        created_tickets = []
        for task in tasks:
            ticket = mock_jira_instance.create_ticket(
                summary=task['title'],
                description=task['description'],
                issue_type='Task'
            )
            created_tickets.append(ticket)
        
        self.assertEqual(len(created_tickets), 2)
        self.assertEqual(mock_jira_instance.create_ticket.call_count, 2)

class TestFileProcessingIntegration(unittest.TestCase):
    """Test file processing integration"""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        
        # Create test files
        self.test_files = {
            'main.py': 'print("Hello World")\ndef main():\n    pass',
            'utils.js': 'function helper() {\n    return "help";\n}',
            'README.md': '# Test Project\n\nThis is a test project.',
            'config.json': '{"name": "test", "version": "1.0.0"}',
            'binary.jpg': b'\x89PNG\r\n\x1a\n'  # Binary data
        }
        
        for filename, content in self.test_files.items():
            filepath = os.path.join(self.temp_dir, filename)
            mode = 'wb' if isinstance(content, bytes) else 'w'
            with open(filepath, mode) as f:
                f.write(content)
    
    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_folder_analysis_integration(self):
        """Test complete folder analysis"""
        from services.file_service import FileService
        
        file_service = FileService()
        
        # Test folder reading
        files = file_service.read_folder_files(self.temp_dir)
        
        # Should include text files but not binary
        text_files = ['main.py', 'utils.js', 'README.md', 'config.json']
        for filename in text_files:
            self.assertIn(filename, files)
        
        self.assertNotIn('binary.jpg', files)
        
        # Test file statistics
        stats = file_service.get_file_stats(files)
        self.assertEqual(stats['total_files'], 4)
        self.assertIn('py', stats['file_types'])
        self.assertIn('js', stats['file_types'])
        self.assertIn('md', stats['file_types'])
        self.assertIn('json', stats['file_types'])

class TestDiagramGenerationIntegration(unittest.TestCase):
    """Test diagram generation integration"""
    
    @patch('services.ai_service.AIService')
    def test_er_diagram_generation(self, mock_ai_service):
        """Test ER diagram generation from code"""
        from generators.diagram_generator import DiagramGenerator
        
        # Mock AI service for entity extraction
        mock_ai_service_instance = mock_ai_service.return_value
        mock_ai_service_instance.analyze_entities.return_value = [
            {'name': 'User', 'attributes': ['id', 'name', 'email']},
            {'name': 'Post', 'attributes': ['id', 'title', 'content', 'user_id']}
        ]
        
        mock_ai_service_instance.analyze_relationships.return_value = [
            {'from': 'User', 'to': 'Post', 'type': 'one-to-many'}
        ]
        
        diagram_generator = DiagramGenerator()
        
        code_files = {
            'models.py': '''
            class User:
                def __init__(self, id, name, email):
                    self.id = id
                    self.name = name
                    self.email = email
            
            class Post:
                def __init__(self, id, title, content, user_id):
                    self.id = id
                    self.title = title
                    self.content = content
                    self.user_id = user_id
            '''
        }
        
        er_diagram = diagram_generator.generate_er_diagram(code_files)
        
        self.assertIn('erDiagram', er_diagram)
        self.assertIn('User', er_diagram)
        self.assertIn('Post', er_diagram)
    
    @patch('services.ai_service.AIService')
    def test_data_flow_diagram_generation(self, mock_ai_service):
        """Test data flow diagram generation"""
        from generators.diagram_generator import DiagramGenerator
        
        mock_ai_service_instance = mock_ai_service.return_value
        mock_ai_service_instance.analyze_data_flows.return_value = [
            {'from': 'User Input', 'to': 'Validation', 'data': 'form data'},
            {'from': 'Validation', 'to': 'Database', 'data': 'validated data'}
        ]
        
        diagram_generator = DiagramGenerator()
        
        code_files = {
            'api.py': '''
            def create_user(user_data):
                validated_data = validate_user(user_data)
                return save_to_database(validated_data)
            '''
        }
        
        flow_diagram = diagram_generator.generate_data_flow_diagram(code_files)
        
        self.assertIn('flowchart', flow_diagram)
        self.assertIn('User Input', flow_diagram)
        self.assertIn('Validation', flow_diagram)

class TestErrorHandlingIntegration(unittest.TestCase):
    """Test error handling integration"""
    
    @patch('boto3.Session')
    def test_aws_error_handling(self, mock_session):
        """Test AWS error handling"""
        from services.ai_service import AIService
        from botocore.exceptions import ClientError
        
        mock_client = MagicMock()
        mock_session.return_value.client.return_value = mock_client
        
        # Simulate AWS error
        mock_client.invoke_model.side_effect = ClientError(
            {'Error': {'Code': 'AccessDeniedException', 'Message': 'Access denied'}},
            'InvokeModel'
        )
        
        ai_service = AIService()
        
        with self.assertRaises(Exception):
            ai_service.generate_text("Test prompt")
    
    def test_file_system_error_handling(self):
        """Test file system error handling"""
        from services.file_service import FileService
        
        file_service = FileService()
        
        # Test non-existent folder
        result = file_service.validate_folder_path('/non/existent/path')
        self.assertFalse(result['valid'])
        self.assertIn('does not exist', result['error'])

if __name__ == '__main__':
    unittest.main()