
import unittest
from unittest.mock import patch, MagicMock
from analyzer import Analyzer, AnalyzeResult
from config import Config

class TestAnalyzer(unittest.TestCase):
    
    def setUp(self):
        self.analyzer = Analyzer()
        # Mock the valid config validation to avoid environment error during tests
        # We patch where it is defined because it is imported inside the method
        self.config_patcher = patch('config.Config.validate')
        self.mock_validate = self.config_patcher.start()
        Config.GEMINI_API_KEY = "test_key" # Dummy key

    def tearDown(self):
        self.config_patcher.stop()

    @patch('analyzer.genai')
    def test_analyze_with_gemini_success(self, mock_genai):
        # Setup mock response
        mock_model = MagicMock()
        mock_response = MagicMock()
        
        # Simulated JSON response from Gemini
        mock_response.text = '''
        ```json
        {
            "sentiment_score": 0.85,
            "keywords": ["python", "testing", "ai"]
        }
        ```
        '''
        mock_model.generate_content.return_value = mock_response
        
        # Setup the chain: genai.GenerativeModel('...') -> returns mock_model
        mock_genai.GenerativeModel.return_value = mock_model
        
        # Execute
        result = self.analyzer.analyze_with_gemini("I love coding with Python and AI!")
        
        # Verify
        self.assertIsInstance(result, AnalyzeResult)
        self.assertEqual(result.word_count, 7) # Local metric verification
        self.assertEqual(result.sentiment_score, 0.85)
        self.assertEqual(result.keywords, ["python", "testing", "ai"])
        
        # Verify API was called correcty
        mock_genai.configure.assert_called_with(api_key="test_key")
        mock_model.generate_content.assert_called_once()
    
    @patch('analyzer.genai')
    def test_analyze_with_gemini_failure(self, mock_genai):
        # Simulate an API error (e.g. 429 or network)
        mock_genai.GenerativeModel.side_effect = Exception("API Quota Exceeded")
        
        result = self.analyzer.analyze_with_gemini("Some text")
        
        # Should fail gracefully and return local metrics, logging the error (check logs manually or mock logger)
        self.assertIsInstance(result, AnalyzeResult)
        self.assertEqual(result.word_count, 2)
        self.assertIsNone(result.sentiment_score) # API failed, so None

if __name__ == '__main__':
    unittest.main()
