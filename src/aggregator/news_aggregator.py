from typing import List, Dict
from datetime import datetime
import asyncio
from ..scrapers.auntminnie_scraper import AuntMinnieScraper
from ..scrapers.beckers_scraper import BeckersScraper
from ..scrapers.stat_scraper import StatScraper
from ..scrapers.modern_healthcare_scraper import ModernHealthcareScraper
from ..scrapers.healthcare_it_news_scraper import HealthcareITNewsScraper
from ..scrapers.rsna_ai_scraper import RSNAAIScraper
from ..scrapers.acr_scraper import ACRScraper
from ..filters.content_filter import ContentFilter

class NewsAggregator:
    def __init__(self):
        print("Initializing NewsAggregator...")
        # Define source priorities
        self.source_priorities = {
            'RSNA AI': 1,          # Highest priority - academic research
            'ACR News': 2,          # Professional organization news
            'ACR AI-LAB': 2,        # ACR AI initiatives
            'ACR AI Central': 2,    # ACR AI policy/advocacy
            'AuntMinnie': 3,        # Radiology industry news
            'STAT': 4,              # General healthcare news
            'ModernHealthcare': 4,
            'HealthcareITNews': 4,
            'Beckers': 4
        }
        
        # Initialize scrapers in priority order
        self.scrapers = [
            RSNAAIScraper(),    # Priority 1
            ACRScraper(),       # Priority 2
            AuntMinnieScraper(), # Priority 3
            StatScraper(),       # Priority 4
            ModernHealthcareScraper(),
            HealthcareITNewsScraper(),
            BeckersScraper()
        ]
        self.content_filter = ContentFilter()
        print(f"Initialized {len(self.scrapers)} scrapers")

    async def gather_news(self) -> Dict[str, List[Dict]]:
        """Gather and categorize healthcare AI news"""
        print("Starting news gathering process...")
        all_articles = []
        
        # Gather articles from all sources concurrently
        tasks = [self._gather_from_scraper(scraper) for scraper in self.scrapers]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        for result in results:
            if isinstance(result, list):
                all_articles.extend(result)
            elif isinstance(result, Exception):
                print(f"Error during gathering: {str(result)}")

        print(f"Total articles gathered: {len(all_articles)}")
        return self._process_articles(all_articles)

    async def _gather_from_scraper(self, scraper) -> List[Dict]:
        """Gather articles from a single scraper with error handling"""
        try:
            print(f"Fetching articles from {scraper.__class__.__name__}...")
            articles = await scraper.get_articles()
            
            # Add source information and priority to each article
            for article in articles:
                source = scraper.__class__.__name__.replace('Scraper', '')
                if 'source' not in article:
                    article['source'] = source
                article['priority'] = self.source_priorities.get(article['source'], 5)
            
            print(f"Found {len(articles)} articles from {scraper.__class__.__name__}")
            return articles
            
        except Exception as e:
            print(f'Error gathering news from {scraper.__class__.__name__}: {str(e)}')
            import traceback
            print(traceback.format_exc())
            return []

    def _process_articles(self, articles: List[Dict]) -> Dict[str, List[Dict]]:
        """Process and categorize articles with priority weighting"""
        rad_articles = []
        healthcare_articles = []
        
        print(f"Processing {len(articles)} articles...")
        for article in articles:
            try:
                text = f"{article['title']} {article.get('summary', '')}"
                relevance = self.content_filter.is_relevant(text)
                
                # Calculate base relevance scores
                article['relevance_scores'] = self.content_filter.calculate_relevance_score(text)
                
                # Apply priority weighting
                priority_multiplier = self._get_priority_multiplier(article['priority'])
                for key in article['relevance_scores']:
                    article['relevance_scores'][key] *= priority_multiplier
                
                # Categorize articles
                if self._is_priority_source(article['source']):
                    # Priority sources automatically go to radiology section
                    rad_articles.append(article)
                elif relevance['is_relevant']:
                    if relevance['is_radiology']:
                        rad_articles.append(article)
                    elif relevance['is_general_healthcare']:
                        healthcare_articles.append(article)
                        
            except Exception as e:
                print(f"Error processing article: {str(e)}")
                print(f"Problematic article: {article}")
        
        # Sort articles by weighted relevance score
        rad_articles.sort(key=lambda x: (
            x['priority'],  # First sort by priority (lower number = higher priority)
            x['relevance_scores']['combined']  # Then by relevance score
        ))
        healthcare_articles.sort(key=lambda x: x['relevance_scores']['combined'], reverse=True)
        
        print(f"Found {len(rad_articles)} radiology AI articles")
        print(f"Found {len(healthcare_articles)} healthcare AI articles")
        
        return {
            'radiology': rad_articles[:5],    # Top 5 radiology AI articles
            'healthcare': healthcare_articles[:5]  # Top 5 general healthcare AI articles
        }

    def _is_priority_source(self, source: str) -> bool:
        """Check if source is a priority radiology source"""
        return source in ['RSNA AI', 'ACR News', 'ACR AI-LAB', 'ACR AI Central']

    def _get_priority_multiplier(self, priority: int) -> float:
        """Get relevance score multiplier based on source priority"""
        # Priority 1 (RSNA) gets highest boost, decreasing for lower priorities
        multipliers = {
            1: 1.5,  # RSNA gets 50% boost
            2: 1.3,  # ACR gets 30% boost
            3: 1.2,  # AuntMinnie gets 20% boost
            4: 1.0,  # No boost for general sources
            5: 0.9   # Slight penalty for unknown sources
        }
        return multipliers.get(priority, 1.0)