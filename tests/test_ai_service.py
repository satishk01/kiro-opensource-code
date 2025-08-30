import unittest
from unittest.mock import Mock, patch, MagicMock
import json
from services.ai_service import AIService

class TestAIService(unittest.TestCase):
    
    def setUp(self):
        self.ai_service = AIService()
    
    def test_model_configs_exist(self):
        """Test that model configurations are properly defined"""
        self.assertIn("Claude Sonnet 3.5 v2", self.ai_service.model_configs)
        self.assertIn("Amazon Nova Pro", self.ai_service.model_configs)
        
        for model_name, config in self.ai_service.model_configs.items():
            self.assertIn("model_id", config)
            self.assertIn("max_tokens", config)
            self.assertIn("temperature", config)
    
    @patch('boto3.Session')
    def test_initialize_bedrock_client_success(self, mock_session):
        """Test successful Bedrock client initialization"""
        mock_client = Mock()
        mock_client.list_foundation_models.return_value = {"models": []}
        mock_session.return_value.client.return_value = mock_client
        
        result = self.ai_service.initialize_bedrock_client()
        
        self.assertTrue(result)
        self.assertIsNotNone(self.ai_service.bedrock_client)
    
    @patch('boto3.Session')
    def test_initialize_bedrock_client_failure(self, mock_session):
        """Test Bedrock client initialization failure"""
        mock_session.side_effect = Exception("Connection failed")
        
        result = self.ai_service.initialize_bedrock_client()
        
        self.assertFalse(result)
        self.assertIsNone(self.ai_service.bedrock_client)
    
    def test_select_model_invalid(self):
        """Test selecting an invalid model"""
        result = self.ai_service.select_model("Invalid Model")
        self.assertFalse(result)
    
    @patch.object(AIService, 'initialize_bedrock_client')
    def test_select_model_valid(self, mock_init):
        """Test selecting a valid model"""
        mock_init.return_value = True
        
        result = self.ai_service.select_model("Claude Sonnet 3.5 v2")
        
        self.assertTrue(result)
        self.assertEqual(self.ai_service.current_model, "Claude Sonnet 3.5 v2")
    
    def test_prepare_claude_payload(self):
        """Test Claude payload preparation"""
        self.ai_service.current_model = "Claude Sonnet 3.5 v2"
        
        payload = self.ai_service._prepare_claude_payload("Test prompt", "System prompt")
        
        self.assertIn("anthropic_version", payload)
        self.assertIn("max_tokens", payload)
        self.assertIn("temperature", payload)
        self.assertIn("messages", payload)
        self.assertIn("system", payload)
        self.assertEqual(payload["system"], "System prompt")
    
    def test_prepare_nova_payload(self):
        """Test Nova payload preparation"""
        self.ai_service.current_model = "Amazon Nova Pro"
        
        payload = self.ai_service._prepare_nova_payload("Test prompt", "System prompt")
        
        self.assertIn("inputText", payload)
        self.assertIn("textGenerationConfig", payload)
        self.assertTrue(payload["inputText"].startswith("System prompt"))
    
    def test_detect_languages(self):
        """Test programming language detection"""
        files = {
            "main.py": "print('hello')",
            "app.js": "console.log('hello')",
            "style.css": "body { margin: 0; }",
            "README.md": "# Project"
        }
        
        languages = self.ai_service._detect_languages(files)
        
        self.assertIn("Python", languages)
        self.assertIn("JavaScript", languages)
        self.assertIn("CSS", languages)
        self.assertIn("Markdown", languages)

if __name__ == '__main__':
    unittest.main()