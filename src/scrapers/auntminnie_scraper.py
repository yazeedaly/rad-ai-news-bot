import feedparser
from .base_scraper import BaseScraper
from bs4 import BeautifulSoup
import aiohttp
import asyncio

class AuntMinnieScraper(BaseScraper):
    def __init__(self):
        super().__init__(rate_limit=2)
        self.feed_url = 'https://www.auntminnie.com/rss/channels/all'
        print(f"Initialized {self.__class__.__name__} with feed URL: {self.feed_url}")

    async def get_articles(self):
        """Fetch articles asynchronously"""
        print(f"{self.__class__.__name__}: Starting article fetch...")
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(self.feed_url) as response:
                    if response.status == 200:
                        content = await response.text()
                        feed = feedparser.parse(content)
                        print(f"{self.__class__.__name__}: Found {len(feed.entries)} entries in feed")
                        
                        articles = []
                        for entry in feed.entries:
                            if self._is_ai_related(entry):
                                articles.append({
                                    'title': entry.title,
                                    'url': entry.link,
                                    'published_date': entry.get('published'),
                                    'summary': entry.get('summary', '')
                                })
                        
                        print(f"{self.__class__.__name__}: Found {len(articles)} AI-related articles")
                        return articles[:5]  # Return top 5 articles
                    else:
                        print(f"{self.__class__.__name__}: Error fetching feed - Status {response.status}")
                        return []
        except Exception as e:
            print(f"{self.__class__.__name__}: Error fetching articles - {str(e)}")
            return []

    def _is_ai_related(self, entry):
        """Check if article is AI-related based on keywords"""
        keywords = ['artificial intelligence', 'AI', 'machine learning', 'deep learning',
                   'neural network', 'algorithm', 'computer-aided']
        text = (entry.title + ' ' + entry.get('summary', '')).lower()
        return any(keyword.lower() in text for keyword in keywords)