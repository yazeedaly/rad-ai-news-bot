from typing import List, Dict
from datetime import datetime
import asyncio
from ..scrapers.auntminnie_scraper import AuntMinnieScraper
from ..scrapers.beckers_scraper import BeckersScraper
from ..filters.content_filter import ContentFilter

class NewsAggregator:
    def __init__(self):
        self.scrapers = [
            AuntMinnieScraper(),
            BeckersScraper()
        ]
        self.content_filter = ContentFilter()

    async def gather_news(self) -> Dict[str, List[Dict]]:
        """Gather news from all sources"""
        all_articles = []
        
        # Gather articles from all sources
        for scraper in self.scrapers:
            try:
                articles = scraper.get_articles()
                for article in articles:
                    # Add source information
                    article['source'] = scraper.__class__.__name__.replace('Scraper', '')
                    all_articles.extend(articles)
            except Exception as e:
                print(f'Error gathering news from {scraper.__class__.__name__}: {str(e)}')

        # Filter and sort articles
        filtered_articles = self._filter_articles(all_articles)
        sorted_articles = self._sort_articles(filtered_articles)

        # Categorize articles
        return self._categorize_articles(sorted_articles)

    def _filter_articles(self, articles: List[Dict]) -> List[Dict]:
        """Filter articles based on relevance"""
        filtered = []
        for article in articles:
            text = f"{article['title']} {article['summary']}"
            if self.content_filter.is_relevant(text):
                # Add relevance scores to article metadata
                article['relevance_scores'] = self.content_filter.calculate_relevance_score(text)
                filtered.append(article)
        return filtered

    def _sort_articles(self, articles: List[Dict]) -> List[Dict]:
        """Sort articles by relevance and date"""
        return sorted(
            articles,
            key=lambda x: (x['relevance_scores']['combined'], x['published_date']),
            reverse=True
        )

    def _categorize_articles(self, articles: List[Dict]) -> Dict[str, List[Dict]]:
        """Categorize articles into applications and research"""
        applications = []
        research = []

        for article in articles:
            scores = article['relevance_scores']
            # Categorize based on keyword presence and scores
            if scores['clinical'] > scores['ai']:
                applications.append(article)
            else:
                research.append(article)

        return {
            'applications': applications[:5],  # Top 5 application articles
            'research': research[:5]  # Top 5 research articles
        }