
from dataclasses import dataclass, field
from typing import List, Optional
import time
from .cleanliness import Observability

import google.generativeai as genai
from .config import Config

# Initialize logger
logger = Observability().get_logger("analyzer")

@dataclass
class AnalyzeResult:
    """
    Data Transfer Object for analysis results.
    Encapsulates both local metrics and AI-generated insights.
    """
    word_count: int
    char_count: int
    sentence_count: int
    sentiment_score: Optional[float] = None
    keywords: List[str] = field(default_factory=list)
    latency_ms: float = 0.0

class Analyzer:
    """
    Core logic for Analyze Tracker.
    Responsible for local text processing and orchestration of AI analysis.
    """
    
    def calculate_local_metrics(self, text: str) -> AnalyzeResult:
        """
        Calculates deterministic metrics locally.
        
        Args:
            text: The input text to analyze.
            
        Returns:
            AnalyzeResult: Object populated with local metrics.
        """
        start_time = time.time()
        logger.debug("starting_local_analysis", text_length=len(text))
        
        # Basic parsing
        # Antirez style: "Simple is better than complex."
        words = text.split()
        sentences = [s for s in text.replace('!', '.').replace('?', '.').split('.') if s.strip()]
        
        result = AnalyzeResult(
            word_count=len(words),
            char_count=len(text),
            sentence_count=len(sentences)
        )
        
        elapsed = (time.time() - start_time) * 1000
        logger.info("local_analysis_completed", 
                    word_count=result.word_count, 
                    latency_ms=elapsed)
        
        return result

    def analyze_with_gemini(self, text: str) -> AnalyzeResult:
        """
        Orchestrates the full analysis including AI. 
        """
        # Step 1: Local metrics
        result = self.calculate_local_metrics(text)
        
        # Step 2: AI Analysis
        
        try:
            Config.validate()
            genai.configure(api_key=Config.GEMINI_API_KEY)
            model = genai.GenerativeModel('gemini-pro')
            
            logger.info("calling_gemini_api", text_length=len(text))
            start_api = time.time()
            
            # Antirez style: We want a structured response. 
            # Prompt engineering is critical here.
            prompt = f"""
            Analyze the following text and return a JSON object with:
            - sentiment_score: float between -1.0 (negative) and 1.0 (positive)
            - keywords: list of 3-5 main topics/keywords
            
            Text: "{text[:2000]}" 
            """
            # truncated to 2000 chars for MVP safety
            
            response = model.generate_content(prompt)
            latency = (time.time() - start_api) * 1000
            
            # Simple parsing (robustness would require json re-trying or stricter parsing)
            # For now we assume the model obeys well or we fail gracefully.
            import json
            import re
            
            # Extract JSON from potential markdown code blocks
            clean_text = re.sub(r'```json\n|```', '', response.text).strip()
            data = json.loads(clean_text)
            
            result.sentiment_score = data.get('sentiment_score')
            result.keywords = data.get('keywords', [])
            result.latency_ms += latency # Add API latency to total
            
            logger.info("gemini_analysis_completed", 
                        latency_ms=latency, 
                        sentiment=result.sentiment_score)
            
        except Exception as e:
            logger.error("gemini_api_failed", error=str(e))
            # We explicitly do not raise here if we want to return partial results (local metrics)
            # But the user might expect full failure. Let's return local metrics with a warning log.
            
        return result
