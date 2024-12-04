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
            'patient', 'diagnosis', 'treatment', 'care', 'health system',
            'ehr', 'emr', 'digital health', 'telemedicine', 'medical records',
            'health system', 'medical practice', 'clinician', 'health data',
            'medical device', 'fda', 'health tech', 'digital medicine'
        ]
        
        self.ai_keywords = [
            'artificial intelligence', 'machine learning', 'deep learning',
            'neural network', 'algorithm', 'ai-powered', 'ml', 'nlp',
            'predictive analytics', 'computer vision', 'decision support',
            'automated detection', 'ai model', 'ai system', 'ai technology',
            'ai solution', 'ai software', 'ai tool', 'ai platform'
        ]

        # Must have one of these exact phrases for healthcare AI articles
        self.required_ai_phrases = [
            'artificial intelligence',
            'machine learning',
            'ai-powered',
            'ai system',
            'ai technology',
            'deep learning',
            'neural network',
            'ai model'
        ]

    def calculate_relevance_score(self, text: str) -> Dict[str, float]:
        """Calculate relevance scores with more lenient matching"""
        text = text.lower()
        
        # Calculate base scores
        rad_score = self._calculate_keyword_score(text, self.rad_keywords)
        healthcare_score = self._calculate_keyword_score(text, self.healthcare_keywords)
        ai_score = self._calculate_keyword_score(text, self.ai_keywords)
        
        # Check for required AI phrases for healthcare articles
        has_required_ai = any(phrase in text for phrase in self.required_ai_phrases)
        if not has_required_ai:
            ai_score *= 0.5  # Significantly reduce AI score if no required phrases found
        
        scores = {
            'radiology': min(rad_score, 1.0),
            'healthcare': min(healthcare_score, 1.0),
            'ai': min(ai_score, 1.0),
            'has_required_ai': has_required_ai
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
            if exact_matches > 0:
                unique_matches.add(keyword)
                total_matches += exact_matches
        
        # Calculate scores
        frequency_score = min(total_matches / 2, 1.0)
        variety_score = len(unique_matches) / (len(keywords) * 0.2)  # Only need 20% of keywords
        
        return min((frequency_score * 0.3 + variety_score * 0.7), 1.0)

    def is_relevant(self, text: str) -> Dict[str, bool]:
        """Determine article relevance with stricter AI requirements"""
        text = text.lower()
        scores = self.calculate_relevance_score(text)
        
        # For healthcare articles, must have a required AI phrase
        is_healthcare_ai = scores['healthcare'] > 0.15 and scores['ai'] > 0.15 and scores['has_required_ai']
        
        # Radiology articles can be slightly more lenient but still need good AI relevance
        is_rad_ai = (scores['radiology'] > 0.15 and scores['ai'] > 0.15 and 
                    (scores['has_required_ai'] or 
                     any(term in text for term in ['ai', 'algorithm', 'automated', 'computer-aided'])))
        
        return {
            'is_relevant': is_rad_ai or is_healthcare_ai,
            'is_radiology': is_rad_ai,
            'is_general_healthcare': is_healthcare_ai and not is_rad_ai
        }