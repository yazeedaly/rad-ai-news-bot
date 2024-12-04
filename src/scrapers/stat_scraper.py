from .base_scraper import BaseScraper
from bs4 import BeautifulSoup
import aiohttp
import feedparser

class StatScraper(BaseScraper):
    def __init__(self):
        super().__init__(rate_limit=2)
        self.feed_url = 'https://www.statnews.com/feed/'
        print(f"Initialized {self.__class__.__name__} with feed URL: {self.feed_url}")

    async def get_articles(self):
        """Fetch articles from STAT News"""
        print(f"{self.__class__.__name__}: Starting article fetch...")
        try:
            content = await self._make_request(self.feed_url)
            feed = feedparser.parse(content)
            print(f"{self.__class__.__name__}: Found {len(feed.entries)} entries in feed")
            
            articles = []
            for entry in feed.entries:
                if self._is_ai_healthcare_related(entry):
                    articles.append({
                        'title': entry.title,
                        'url': entry.link,
                        'published_date': entry.get('published'),
                        'summary': entry.get('summary', ''),
                        'requires_auth': '+' in entry.get('tags', [])
                    })
            
            print(f"{self.__class__.__name__}: Found {len(articles)} AI/healthcare-related articles")
            return articles[:5]

        except Exception as e:
            print(f"{self.__class__.__name__}: Error fetching articles - {str(e)}")
            return []

    async def extract_content(self, url):
        """Extract content from a STAT article"""
        try:
            content = await self._make_request(url)
            soup = BeautifulSoup(content, 'html.parser')
            
            article = soup.find('article')
            if not article:
                return None

            # Extract text content
            text = article.get_text(strip=True)
            
            # Extract key points
            takeaways = self._extract_takeaways(article)

            return {
                'text': text,
                'takeaways': takeaways,
                'paywall': self._is_paywalled(soup)
            }
            
        except Exception as e:
            print(f"Error extracting content from {url}: {str(e)}")
            return None

    def _is_ai_healthcare_related(self, entry):
        """Check if article is related to AI in healthcare"""
        ai_keywords = ['artificial intelligence', 'AI', 'machine learning', 'deep learning',
                    'neural network', 'algorithm']
        healthcare_keywords = ['health', 'medical', 'clinical', 'patient', 'hospital',
                           'doctor', 'physician', 'diagnosis', 'treatment']
        
        text = (entry.title + ' ' + entry.get('summary', '')).lower()
        has_ai = any(keyword.lower() in text for keyword in ai_keywords)
        has_healthcare = any(keyword.lower() in text for keyword in healthcare_keywords)
        
        return has_ai and has_healthcare

    def _extract_takeaways(self, article):
        """Extract key takeaways from article"""
        takeaways = []
        key_sections = article.find_all(['h2', 'h3', 'strong', 'b'])
        
        for section in key_sections:
            text = section.get_text(strip=True)
            if len(text) > 20 and len(text) < 200:
                takeaways.append(text)
                if len(takeaways) == 3:
                    break
        
        return takeaways

    def _is_paywalled(self, soup):
        """Check if article is behind paywall"""
        paywall_indicators = [
            'div.paywall',
            'div.subscription-required',
            'div.stat-plus'
        ]
        return any(soup.select(indicator) for indicator in paywall_indicators)