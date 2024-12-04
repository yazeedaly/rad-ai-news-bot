from typing import Dict, List
import re

class ContentFilter:
    def __init__(self):
        self.rad_keywords = [
            'radiology', 'imaging', 'radiologist', 'x-ray', 'CT', 'MRI', 'PACS',
            'diagnostic imaging', 'nuclear medicine', 'ultrasound', 'mammography',
            'interventional radiology', 'image analysis', 'scan', 'imaging technology'
        ]
        
        self.ai_keywords = [
            'artificial intelligence', 'AI', 'machine learning', 'deep learning',
            'neural network', 'computer vision', 'natural language processing',
            'algorithm', 'automated detection', 'computer-aided diagnosis',
            'predictive analytics', 'decision support', 'automation', 'ML'
        ]
        
        self.clinical_keywords = [
            'diagnosis', 'treatment', 'patient care', 'clinical workflow',
            'healthcare delivery', 'medical practice', 'patient outcome',
            'clinical decision', 'medical diagnosis', 'therapeutic', 'health tech',
            'digital health', 'medical technology', 'health system'
        ]

    def calculate_relevance_score(self, text: str) -> Dict[str, float]:
        """Calculate relevance scores for different categories with more lenient scoring"""
        text = text.lower()
        
        # Calculate individual scores
        rad_score = self._calculate_keyword_score(text, self.rad_keywords)
        ai_score = self._calculate_keyword_score(text, self.ai_keywords)
        clinical_score = self._calculate_keyword_score(text, self.clinical_keywords)
        
        # Boost scores when multiple categories are present
        if rad_score > 0 and ai_score > 0:
            rad_score *= 1.2
            ai_score *= 1.2
        
        if clinical_score > 0 and (rad_score > 0 or ai_score > 0):
            clinical_score *= 1.2
        
        scores = {
            'radiology': rad_score,
            'ai': ai_score,
            'clinical': clinical_score
        }
        
        # Calculate combined score with weighted importance
        scores['combined'] = (rad_score * 0.35 + 
                            ai_score * 0.35 + 
                            clinical_score * 0.3)
        
        return scores

    def _calculate_keyword_score(self, text: str, keywords: List[str]) -> float:
        """Calculate keyword match score with more lenient matching"""
        total_matches = 0
        unique_matches = set()
        
        for keyword in keywords:
            matches = len(re.findall(r'\b' + re.escape(keyword) + r'\b', text))
            if matches > 0:
                unique_matches.add(keyword)
                total_matches += matches
        
        # Consider both frequency and variety of matches
        frequency_score = min(total_matches / 3, 1.0)  # Normalized by expected frequency
        variety_score = len(unique_matches) / (len(keywords) * 0.3)  # Expect 30% keyword coverage for max score
        
        # Combine scores with more weight on variety
        return min((frequency_score * 0.4 + variety_score * 0.6), 1.0)

    def is_relevant(self, text: str, threshold: float = 0.15) -> bool:
        """Determine if content is relevant based on combined score with lower threshold"""
        scores = self.calculate_relevance_score(text)
        
        # Article is relevant if it either:
        # 1. Has a good combined score
        # 2. Has both AI and radiology mentions
        # 3. Has a very high score in either AI or radiology
        return (scores['combined'] >= threshold or
                (scores['ai'] > 0.3 and scores['radiology'] > 0.3) or
                scores['ai'] >= 0.6 or
                scores['radiology'] >= 0.6)