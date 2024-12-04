from .base_scraper import BaseScraper
from bs4 import BeautifulSoup
import feedparser
import re

class HealthcareITNewsScraper(BaseScraper):
    def __init__(self):
        super().__init__(rate_limit=2)
        self.feed_url = 'https://www.healthcareitnews.com/rss/topics/artificial-intelligence'
        self.base_url = 'https://www.healthcareitnews.com'
        print(f"Initialized {self.__class__.__name__} with feed URL: {self.feed_url}")

    async def get_articles(self):
        """Fetch articles from Healthcare IT News"""
        print(f"{self.__class__.__name__}: Starting article fetch...")
        try:
            content = await self._make_request(self.feed_url)
            feed = feedparser.parse(content)
            print(f"{self.__class__.__name__}: Found {len(feed.entries)} entries in feed")
            
            articles = []
            for entry in feed.entries:
                # Clean up the URL if needed
                url = entry.link if entry.link.startswith('http') else f"{self.base_url}{entry.link}"
                
                article = {
                    'title': entry.title,
                    'url': url,
                    'published_date': entry.get('published'),
                    'summary': entry.get('summary', '')
                }
                
                # Only add if it's AI/Healthcare related
                if self._is_relevant(article):
                    articles.append(article)
            
            print(f"{self.__class__.__name__}: Found {len(articles)} relevant articles")
            return articles[:5]

        except Exception as e:
            print(f"{self.__class__.__name__}: Error fetching articles - {str(e)}")
            return []

    def _is_relevant(self, article):
        """Check if article is relevant to AI in healthcare"""
        text = f"{article['title']} {article['summary']}".lower()
        
        ai_terms = ['artificial intelligence', 'ai', 'machine learning', 'deep learning',
                   'neural network', 'algorithm', 'automation']
        healthcare_terms = ['health', 'medical', 'clinical', 'hospital', 'patient',
                         'care', 'physician', 'provider']
        
        has_ai = any(term in text for term in ai_terms)
        has_healthcare = any(term in text for term in healthcare_terms)
        
        return has_ai and has_healthcare

    async def extract_content(self, url):
        """Extract content from a Healthcare IT News article"""
        try:
            content = await self._make_request(url)
            soup = BeautifulSoup(content, 'html.parser')
            
            article = soup.find('article') or soup.find('div', class_='article-body')
            if not article:
                return None

            # Extract main content
            text = article.get_text(strip=True)
            
            # Extract key points
            takeaways = self._extract_takeaways(article)

            return {
                'text': text,
                'takeaways': takeaways
            }
            
        except Exception as e:
            print(f"Error extracting content from {url}: {str(e)}")
            return None

    def _extract_takeaways(self, article):
        """Extract key takeaways from article"""
        takeaways = []
        
        # Look for highlighted text, subheadings, or strong points
        key_elements = article.find_all(['h2', 'h3', 'strong', 'b', 'em'])
        
        for element in key_elements:
            text = element.get_text(strip=True)
            if len(text) > 20 and len(text) < 200:  # Reasonable length for a key point
                takeaways.append(text)
                if len(takeaways) == 3:  # Limit to 3 takeaways
                    break
        
        return takeaways