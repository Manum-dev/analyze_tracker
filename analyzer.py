
from dataclasses import dataclass, field
from typing import List, Optional
import time

from cleanliness import Observability
import google.generativeai as genai
from config import Config

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
    sentiment_label: Optional[str] = None
    sentiment_confidence: Optional[float] = None
    summary: Optional[str] = None
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
            model = genai.GenerativeModel('gemini-2.0-flash')
            
            logger.info("calling_gemini_api", text_length=len(text))
            start_api = time.time()
            
            # Antirez style: We want a structured response. 
            # Prompt engineering is critical here.
            prompt = f"""
            Analisi tramite Gemini API per il seguente testo:
            
            1. Sentiment analysis con classificazione (positivo/negativo/neutro) e confidence score (0-1)
            2. Conteggio parole, frasi, caratteri
            3. Estrazione top 5-10 keywords/temi principali
            4. Riassunto breve del contenuto (max 100 parole)
            
            Restituisci un oggetto JSON puro con questa struttura esatta:
            {{
                "sentiment_label": "positivo" | "negativo" | "neutro",
                "sentiment_confidence": float (0.0 - 1.0),
                "word_count": int,
                "sentence_count": int,
                "char_count": int,
                "keywords": [list of strings],
                "summary": "string"
            }}
            
            Text: "{text[:4000]}" 
            """
            # truncated to 4000 chars 
            
            response = model.generate_content(prompt)
            latency = (time.time() - start_api) * 1000
            
            # Simple parsing (robustness would require json re-trying or stricter parsing)
            # For now we assume the model obeys well or we fail gracefully.
            import json
            import re
            
            # Extract JSON from potential markdown code blocks
            clean_text = re.sub(r'```json\n|```', '', response.text).strip()
            data = json.loads(clean_text)
            
            # Map Gemini results to AnalyzeResult
            # Note: We rely on AI for metrics now if successful, or we could overwrite/compare with local
            # For this request, we'll assign what we got.
            
            result.sentiment_label = data.get('sentiment_label')
            result.sentiment_confidence = data.get('sentiment_confidence')
            result.summary = data.get('summary')
            result.keywords = data.get('keywords', [])
            
            # Optional: Use AI counts if reliable, or keep local. 
            # The user asked for "Conteggio... (AI via prompt)", so we can arguably update them.
            # But local is faster/safer. Let's trust local for now or partial update? 
            # Let's fallback to local keys if missing, but update if present to match the prompt request strictly.
            if 'word_count' in data: result.word_count = data['word_count']
            if 'sentence_count' in data: result.sentence_count = data['sentence_count']
            if 'char_count' in data: result.char_count = data['char_count']

            result.latency_ms += latency # Add API latency to total
            
            logger.info("gemini_analysis_completed", 
                        latency_ms=latency, 
                        sentiment=result.sentiment_label)
            
        except Exception as e:
            logger.error("gemini_api_failed", error=str(e))
            # We explicitly do not raise here if we want to return partial results (local metrics)
            # But the user might expect full failure. Let's return local metrics with a warning log.
            
        return result
