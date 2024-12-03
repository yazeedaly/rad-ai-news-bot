import feedparser
from .base_scraper import BaseScraper
from bs4 import BeautifulSoup

class AuntMinnieScraper(BaseScraper):
    def __init__(self):
        super().__init__(rate_limit=2)
        self.rss_url = 'https://www.auntminnie.com/rss/channels/artificial-intelligence.xml'

    def get_articles(self):
        feed = feedparser.parse(self.rss_url)
        articles = []
        
        for entry in feed.entries:
            if self._is_ai_related(entry):
                articles.append({
                    'title': entry.title,
                    'url': entry.link,
                    'published_date': entry.published,
                    'summary': entry.summary
                })
        
        return articles[:5]  # Return top 5 articles

    def _is_ai_related(self, entry):
        """Check if article is AI-related based on keywords"""
        keywords = ['artificial intelligence', 'AI', 'machine learning', 'deep learning',
                   'neural network', 'algorithm', 'computer-aided']
        text = (entry.title + ' ' + entry.summary).lower()
        return any(keyword.lower() in text for keyword in keywords)

    def extract_content(self, url):
        response = self._make_request(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract main content (customize selectors based on site structure)
        article = soup.find('article') or soup.find('div', class_='article-content')
        if not article:
            return None

        return {
            'text': article.get_text(strip=True),
            'takeaways': self._extract_takeaways(article)
        }

    def _extract_takeaways(self, article):
        """Extract key takeaways from article content"""
        # Look for specific sections or extract important sentences
        takeaways = []
        key_sections = article.find_all(['h2', 'strong', 'b'])
        for section in key_sections[:3]:  # Limit to top 3 takeaways
            if section.text.strip():
                takeaways.append(section.text.strip())
        return takeaways