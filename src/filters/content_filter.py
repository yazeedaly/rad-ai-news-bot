from typing import Dict, List
import re

class ContentFilter:
    def __init__(self):
        # Primary keywords for different healthcare domains
        self.rad_keywords = [
            'radiology', 'imaging', 'radiologist', 'x-ray', 'CT', 'MRI', 'PACS',
            'diagnostic imaging', 'nuclear medicine', 'ultrasound', 'mammography',
            'interventional radiology', 'image analysis', 'scan', 'imaging technology'
        ]
        
        self.healthcare_keywords = [
            'healthcare', 'medical', 'clinical', 'hospital', 'physician',
            'pathology', 'cardiology', 'oncology', 'surgery', 'diagnosis',
            'patient care', 'EMR', 'EHR', 'digital health', 'telemedicine',
            'remote monitoring', 'precision medicine', 'population health'
        ]
        
        self.ai_keywords = [
            'artificial intelligence', 'AI', 'machine learning', 'deep learning',
            'neural network', 'computer vision', 'natural language processing',
            'algorithm', 'automation', 'predictive analytics', 'decision support',
            'automated detection', 'ML', 'generative AI', 'large language model',
            'LLM', 'foundation model', 'computer-aided', 'digital transformation'
        ]

    def calculate_relevance_score(self, text: str) -> Dict[str, float]:
        """Calculate relevance scores with broader healthcare focus"""
        text = text.lower()
        
        # Calculate base scores
        rad_score = self._calculate_keyword_score(text, self.rad_keywords)
        healthcare_score = self._calculate_keyword_score(text, self.healthcare_keywords)
        ai_score = self._calculate_keyword_score(text, self.ai_keywords)
        
        # Apply score modifiers
        has_ai = ai_score > 0
        has_healthcare = healthcare_score > 0 or rad_score > 0
        
        # Boost scores for AI + Healthcare combinations
        if has_ai and has_healthcare:
            ai_score *= 1.2
            healthcare_score *= 1.2
            rad_score *= 1.2
        
        scores = {
            'radiology': rad_score,
            'healthcare': healthcare_score,
            'ai': ai_score
        }
        
        # Calculate combined score with priority for radiology
        scores['combined'] = (
            rad_score * 0.4 +      # Higher weight for radiology
            healthcare_score * 0.3 + # Medium weight for general healthcare
            ai_score * 0.3          # Base weight for AI
        )
        
        return scores

    def _calculate_keyword_score(self, text: str, keywords: List[str]) -> float:
        """Calculate keyword match score with fuzzy matching"""
        total_matches = 0
        unique_matches = set()
        
        for keyword in keywords:
            # Look for exact matches
            exact_matches = len(re.findall(r'\b' + re.escape(keyword) + r'\b', text))
            if exact_matches > 0:
                unique_matches.add(keyword)
                total_matches += exact_matches
            
            # Look for partial matches for longer keywords (3+ words)
            if len(keyword.split()) >= 3 and keyword.lower() in text:
                unique_matches.add(keyword)
                total_matches += 0.5  # Partial match counts less
        
        # Balance between frequency and variety
        frequency_score = min(total_matches / 2, 1.0)
        variety_score = len(unique_matches) / (len(keywords) * 0.25)  # Expect 25% keyword coverage
        
        return min((frequency_score * 0.3 + variety_score * 0.7), 1.0)

    def is_relevant(self, text: str) -> Dict[str, bool]:
        """Determine article relevance and category"""
        scores = self.calculate_relevance_score(text)
        
        # More lenient thresholds
        is_rad_ai = scores['radiology'] > 0.2 and scores['ai'] > 0.2
        is_healthcare_ai = scores['healthcare'] > 0.2 and scores['ai'] > 0.2
        
        return {
            'is_relevant': is_rad_ai or is_healthcare_ai,
            'is_radiology': is_rad_ai,
            'is_general_healthcare': is_healthcare_ai and not is_rad_ai
        }