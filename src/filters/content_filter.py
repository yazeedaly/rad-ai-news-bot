from typing import Dict, List
import re

class ContentFilter:
    def __init__(self):
        # Primary keywords for different healthcare domains
        self.rad_keywords = [
            'radiology', 'imaging', 'radiologist', 'x-ray', 'ct', 'mri', 'pacs',
            'diagnostic imaging', 'nuclear medicine', 'ultrasound', 'mammography',
            'interventional radiology', 'image analysis', 'scan', 'chest x-ray',
            'medical imaging', 'image recognition', 'radiograph', 'imaging systems'
        ]
        
        self.healthcare_keywords = [
            'healthcare', 'medical', 'clinical', 'hospital', 'physician',
            'patient', 'diagnosis', 'treatment', 'care', 'health', 'provider',
            'ehr', 'emr', 'digital health', 'telemedicine', 'medical records',
            'health system', 'medical practice', 'clinician', 'doctor',
            'medical device', 'fda', 'health tech', 'medicine'
        ]
        
        self.ai_keywords = [
            'artificial intelligence', 'ai', 'machine learning', 'deep learning',
            'neural network', 'algorithm', 'automation', 'ml', 'nlp',
            'predictive analytics', 'computer vision', 'decision support',
            'automated detection', 'ai model', 'ai system', 'ai technology',
            'ai solution', 'ai software', 'ai tool', 'ai platform'
        ]

    def calculate_relevance_score(self, text: str) -> Dict[str, float]:
        """Calculate relevance scores with more lenient matching"""
        text = text.lower()
        
        # Calculate base scores
        rad_score = self._calculate_keyword_score(text, self.rad_keywords)
        healthcare_score = self._calculate_keyword_score(text, self.healthcare_keywords)
        ai_score = self._calculate_keyword_score(text, self.ai_keywords)
        
        # Check for compound terms that should boost scores
        compound_boosts = [
            ('ai', 'imaging'),
            ('artificial intelligence', 'imaging'),
            ('machine learning', 'diagnosis'),
            ('algorithm', 'detection'),
            ('ai', 'radiology'),
            ('ai', 'healthcare')
        ]
        
        for term1, term2 in compound_boosts:
            if term1 in text and term2 in text:
                if term2 in self.rad_keywords:
                    rad_score *= 1.2
                if term2 in self.healthcare_keywords:
                    healthcare_score *= 1.2
                ai_score *= 1.2
        
        scores = {
            'radiology': min(rad_score, 1.0),
            'healthcare': min(healthcare_score, 1.0),
            'ai': min(ai_score, 1.0)
        }
        
        # Calculate combined score
        scores['combined'] = min((
            rad_score * 0.4 +      # Higher weight for radiology
            healthcare_score * 0.3 + # Medium weight for healthcare
            ai_score * 0.3          # Base weight for AI
        ), 1.0)
        
        return scores

    def _calculate_keyword_score(self, text: str, keywords: List[str]) -> float:
        """Calculate keyword match score with more lenient matching"""
        total_matches = 0
        unique_matches = set()
        
        # Look for exact matches first
        for keyword in keywords:
            # Count both exact matches and matches within words
            exact_matches = len(re.findall(r'\b' + re.escape(keyword) + r'\b', text))
            partial_matches = len(re.findall(re.escape(keyword), text)) - exact_matches
            
            if exact_matches > 0:
                unique_matches.add(keyword)
                total_matches += exact_matches
            if partial_matches > 0:
                unique_matches.add(keyword)
                total_matches += partial_matches * 0.5  # Partial matches count less
        
        # Calculate scores
        frequency_score = min(total_matches / 2, 1.0)
        variety_score = len(unique_matches) / (len(keywords) * 0.2)  # Only need 20% of keywords
        
        # Combine scores with more weight on variety
        return min((frequency_score * 0.3 + variety_score * 0.7), 1.0)

    def is_relevant(self, text: str) -> Dict[str, bool]:
        """Determine article relevance with more lenient thresholds"""
        scores = self.calculate_relevance_score(text)
        
        # Lower thresholds and more flexible conditions
        is_rad_ai = (scores['radiology'] > 0.15 and scores['ai'] > 0.15) or \
                    (scores['radiology'] > 0.3) or \
                    (scores['ai'] > 0.3 and 'radiology' in text.lower())
                    
        is_healthcare_ai = (scores['healthcare'] > 0.15 and scores['ai'] > 0.15) or \
                          (scores['healthcare'] > 0.3 and 'ai' in text.lower()) or \
                          (scores['ai'] > 0.3 and any(term in text.lower() for term in ['health', 'medical', 'clinical']))
        
        return {
            'is_relevant': is_rad_ai or is_healthcare_ai,
            'is_radiology': is_rad_ai,
            'is_general_healthcare': is_healthcare_ai and not is_rad_ai
        }