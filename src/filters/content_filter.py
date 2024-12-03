from typing import Dict, List
import re

class ContentFilter:
    def __init__(self):
        self.rad_keywords = [
            'radiology', 'imaging', 'radiologist', 'x-ray', 'CT', 'MRI', 'PACS',
            'diagnostic imaging', 'nuclear medicine', 'ultrasound', 'mammography',
            'interventional radiology', 'image analysis'
        ]
        
        self.ai_keywords = [
            'artificial intelligence', 'AI', 'machine learning', 'deep learning',
            'neural network', 'computer vision', 'natural language processing',
            'algorithm', 'automated detection', 'computer-aided diagnosis',
            'predictive analytics', 'decision support'
        ]
        
        self.clinical_keywords = [
            'diagnosis', 'treatment', 'patient care', 'clinical workflow',
            'healthcare delivery', 'medical practice', 'patient outcome',
            'clinical decision', 'medical diagnosis', 'therapeutic'
        ]

    def calculate_relevance_score(self, text: str) -> Dict[str, float]:
        """Calculate relevance scores for different categories"""
        text = text.lower()
        
        scores = {
            'radiology': self._calculate_keyword_score(text, self.rad_keywords),
            'ai': self._calculate_keyword_score(text, self.ai_keywords),
            'clinical': self._calculate_keyword_score(text, self.clinical_keywords)
        }
        
        # Calculate combined score
        scores['combined'] = (scores['radiology'] * 0.4 + 
                            scores['ai'] * 0.4 + 
                            scores['clinical'] * 0.2)
        
        return scores

    def _calculate_keyword_score(self, text: str, keywords: List[str]) -> float:
        """Calculate keyword match score"""
        total_matches = 0
        for keyword in keywords:
            matches = len(re.findall(r'\b' + re.escape(keyword) + r'\b', text))
            total_matches += matches
        
        # Normalize score between 0 and 1
        return min(total_matches / 5, 1.0)

    def is_relevant(self, text: str, threshold: float = 0.3) -> bool:
        """Determine if content is relevant based on combined score"""
        scores = self.calculate_relevance_score(text)
        return scores['combined'] >= threshold