from typing import List, Dict
from datetime import datetime
import asyncio
from ..scrapers.auntminnie_scraper import AuntMinnieScraper
from ..scrapers.beckers_scraper import BeckersScraper
from ..filters.content_filter import ContentFilter

class NewsAggregator:
    def __init__(self):
        print("Initializing NewsAggregator...")
        self.scrapers = [
            AuntMinnieScraper(),
            BeckersScraper()
        ]
        self.content_filter = ContentFilter()
        print(f"Initialized {len(self.scrapers)} scrapers")

    async def gather_news(self) -> Dict[str, List[Dict]]:
        """Gather news from all sources"""
        print("Starting news gathering process...")
        all_articles = []
        
        # Gather articles from all sources
        for scraper in self.scrapers:
            try:
                print(f"Fetching articles from {scraper.__class__.__name__}...")
                articles = await scraper.get_articles()  # Make get_articles async
                print(f"Found {len(articles)} articles from {scraper.__class__.__name__}")
                
                for article in articles:
                    # Add source information
                    article['source'] = scraper.__class__.__name__.replace('Scraper', '')
                all_articles.extend(articles)
                
            except Exception as e:
                print(f'Error gathering news from {scraper.__class__.__name__}: {str(e)}')
                print(f'Error type: {type(e).__name__}')
                import traceback
                print(traceback.format_exc())

        print(f"Total articles gathered: {len(all_articles)}")

        # Filter and sort articles
        filtered_articles = self._filter_articles(all_articles)
        print(f"Articles after filtering: {len(filtered_articles)}")
        
        sorted_articles = self._sort_articles(filtered_articles)
        print(f"Articles after sorting: {len(sorted_articles)}")

        # Categorize articles
        categorized = self._categorize_articles(sorted_articles)
        print(f"Final article counts - Applications: {len(categorized['applications'])}, Research: {len(categorized['research'])}")
        
        return categorized

    def _filter_articles(self, articles: List[Dict]) -> List[Dict]:
        """Filter articles based on relevance"""
        filtered = []
        print(f"Filtering {len(articles)} articles...")
        
        for article in articles:
            try:
                text = f"{article.get('title', '')} {article.get('summary', '')}"
                if self.content_filter.is_relevant(text):
                    # Add relevance scores to article metadata
                    article['relevance_scores'] = self.content_filter.calculate_relevance_score(text)
                    filtered.append(article)
            except Exception as e:
                print(f"Error filtering article: {str(e)}")
                print(f"Article data: {article}")
        
        return filtered

    def _sort_articles(self, articles: List[Dict]) -> List[Dict]:
        """Sort articles by relevance and date"""
        try:
            return sorted(
                articles,
                key=lambda x: (x['relevance_scores']['combined'], 
                              x.get('published_date', datetime.min)),
                reverse=True
            )
        except Exception as e:
            print(f"Error sorting articles: {str(e)}")
            return articles

    def _categorize_articles(self, articles: List[Dict]) -> Dict[str, List[Dict]]:
        """Categorize articles into applications and research"""
        applications = []
        research = []

        for article in articles:
            try:
                scores = article['relevance_scores']
                # Categorize based on keyword presence and scores
                if scores['clinical'] > scores['ai']:
                    applications.append(article)
                else:
                    research.append(article)
            except Exception as e:
                print(f"Error categorizing article: {str(e)}")
                print(f"Article data: {article}")

        return {
            'applications': applications[:5],  # Top 5 application articles
            'research': research[:5]  # Top 5 research articles
        }