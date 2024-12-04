from typing import List, Dict
from datetime import datetime
import asyncio
from ..scrapers.auntminnie_scraper import AuntMinnieScraper
from ..scrapers.beckers_scraper import BeckersScraper
from ..scrapers.stat_scraper import StatScraper
from ..scrapers.modern_healthcare_scraper import ModernHealthcareScraper
from ..scrapers.healthcare_it_news_scraper import HealthcareITNewsScraper
from ..scrapers.rsna_ai_scraper import RSNAAIScraper
from ..filters.content_filter import ContentFilter

class NewsAggregator:
    def __init__(self):
        print("Initializing NewsAggregator...")
        self.scrapers = [
            RSNAAIScraper(),  # Place RSNA first as it's most relevant
            AuntMinnieScraper(),
            BeckersScraper(),
            StatScraper(),
            ModernHealthcareScraper(),
            HealthcareITNewsScraper()
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
        
        # Process and categorize articles
        categorized = self._process_articles(all_articles)
        
        # Ensure RSNA articles get priority in radiology section
        if categorized['radiology']:
            rsna_articles = [a for a in categorized['radiology'] if a.get('source') == 'RSNA AI']
            other_articles = [a for a in categorized['radiology'] if a.get('source') != 'RSNA AI']
            
            # Combine with RSNA articles first, maintaining limit of 5 total
            categorized['radiology'] = (rsna_articles + other_articles)[:5]
        
        return categorized

    async def _gather_from_scraper(self, scraper) -> List[Dict]:
        """Gather articles from a single scraper with error handling"""
        try:
            print(f"Fetching articles from {scraper.__class__.__name__}...")
            articles = await scraper.get_articles()
            
            # Add source information to each article
            for article in articles:
                if 'source' not in article:  # Don't override if already set
                    article['source'] = scraper.__class__.__name__.replace('Scraper', '')
            
            print(f"Found {len(articles)} articles from {scraper.__class__.__name__}")
            return articles
            
        except Exception as e:
            print(f'Error gathering news from {scraper.__class__.__name__}: {str(e)}')
            import traceback
            print(traceback.format_exc())
            return []

    def _process_articles(self, articles: List[Dict]) -> Dict[str, List[Dict]]:
        """Process and categorize articles"""
        rad_articles = []
        healthcare_articles = []
        
        print(f"Processing {len(articles)} articles...")
        for article in articles:
            try:
                text = f"{article['title']} {article.get('summary', '')}"
                relevance = self.content_filter.is_relevant(text)
                
                # RSNA AI articles automatically go to radiology section
                if article.get('source') == 'RSNA AI':
                    article['relevance_scores'] = self.content_filter.calculate_relevance_score(text)
                    rad_articles.append(article)
                elif relevance['is_relevant']:
                    article['relevance_scores'] = self.content_filter.calculate_relevance_score(text)
                    
                    if relevance['is_radiology']:
                        rad_articles.append(article)
                    elif relevance['is_general_healthcare']:
                        healthcare_articles.append(article)
                        
            except Exception as e:
                print(f"Error processing article: {str(e)}")
                print(f"Problematic article: {article}")
        
        # Sort articles by relevance score
        rad_articles.sort(key=lambda x: x['relevance_scores']['combined'], reverse=True)
        healthcare_articles.sort(key=lambda x: x['relevance_scores']['combined'], reverse=True)
        
        print(f"Found {len(rad_articles)} radiology AI articles")
        print(f"Found {len(healthcare_articles)} healthcare AI articles")
        
        return {
            'radiology': rad_articles[:5],    # Top 5 radiology AI articles
            'healthcare': healthcare_articles[:5]  # Top 5 general healthcare AI articles
        }