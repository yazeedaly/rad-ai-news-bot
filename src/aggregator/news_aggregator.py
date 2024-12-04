from typing import List, Dict
from datetime import datetime
import asyncio
from ..scrapers.auntminnie_scraper import AuntMinnieScraper
from ..scrapers.beckers_scraper import BeckersScraper
from ..scrapers.stat_scraper import StatScraper
from ..filters.content_filter import ContentFilter

class NewsAggregator:
    def __init__(self):
        print("Initializing NewsAggregator...")
        self.scrapers = [
            AuntMinnieScraper(),
            BeckersScraper(),
            StatScraper()
        ]
        self.content_filter = ContentFilter()
        print(f"Initialized {len(self.scrapers)} scrapers")

    async def gather_news(self) -> Dict[str, List[Dict]]:
        """Gather and categorize healthcare AI news"""
        print("Starting news gathering process...")
        all_articles = []
        
        # Gather articles from all sources
        for scraper in self.scrapers:
            try:
                print(f"Fetching articles from {scraper.__class__.__name__}...")
                articles = await scraper.get_articles()
                
                for article in articles:
                    article['source'] = scraper.__class__.__name__.replace('Scraper', '')
                all_articles.extend(articles)
                
                print(f"Found {len(articles)} articles from {scraper.__class__.__name__}")
            except Exception as e:
                print(f'Error gathering news from {scraper.__class__.__name__}: {str(e)}')

        print(f"Total articles gathered: {len(all_articles)}")

        # Process and categorize articles
        categorized_articles = self._process_articles(all_articles)
        
        # Ensure both categories exist in the output
        return {
            'radiology': categorized_articles.get('radiology', []),
            'healthcare': categorized_articles.get('healthcare', [])
        }

    def _process_articles(self, articles: List[Dict]) -> Dict[str, List[Dict]]:
        """Process and categorize articles"""
        rad_articles = []
        healthcare_articles = []
        
        for article in articles:
            try:
                text = f"{article['title']} {article.get('summary', '')}"
                relevance = self.content_filter.is_relevant(text)
                
                if relevance['is_relevant']:
                    article['relevance_scores'] = self.content_filter.calculate_relevance_score(text)
                    
                    if relevance['is_radiology']:
                        rad_articles.append(article)
                    elif relevance['is_general_healthcare']:
                        healthcare_articles.append(article)
                        
            except Exception as e:
                print(f"Error processing article: {str(e)}")
        
        # Sort articles by relevance score
        rad_articles.sort(key=lambda x: x['relevance_scores']['combined'], reverse=True)
        healthcare_articles.sort(key=lambda x: x['relevance_scores']['combined'], reverse=True)
        
        print(f"Found {len(rad_articles)} radiology AI articles")
        print(f"Found {len(healthcare_articles)} healthcare AI articles")
        
        return {
            'radiology': rad_articles[:5],    # Top 5 radiology AI articles
            'healthcare': healthcare_articles[:5]  # Top 5 general healthcare AI articles
        }