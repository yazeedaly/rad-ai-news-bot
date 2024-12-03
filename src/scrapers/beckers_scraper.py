import feedparser
from .base_scraper import BaseScraper
from bs4 import BeautifulSoup

class BeckersScraper(BaseScraper):
    def __init__(self):
        super().__init__(rate_limit=2)
        self.rss_url = 'https://www.beckershospitalreview.com/rss/healthcare-information-technology.xml'

    def get_articles(self):
        feed = feedparser.parse(self.rss_url)
        articles = []
        
        for entry in feed.entries:
            if self._is_radiology_ai_related(entry):
                articles.append({
                    'title': entry.title,
                    'url': entry.link,
                    'published_date': entry.published,
                    'summary': entry.summary
                })
        
        return articles[:5]

    def _is_radiology_ai_related(self, entry):
        """Check if article is related to radiology and AI"""
        rad_keywords = ['radiology', 'imaging', 'radiologist', 'x-ray', 'CT', 'MRI']
        ai_keywords = ['artificial intelligence', 'AI', 'machine learning', 'deep learning']
        
        text = (entry.title + ' ' + entry.summary).lower()
        has_rad = any(keyword.lower() in text for keyword in rad_keywords)
        has_ai = any(keyword.lower() in text for keyword in ai_keywords)
        
        return has_rad and has_ai

    def extract_content(self, url):
        response = self._make_request(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        article = soup.find('article')
        if not article:
            return None

        return {
            'text': article.get_text(strip=True),
            'takeaways': self._extract_key_points(article)
        }

    def _extract_key_points(self, article):
        """Extract key points from article"""
        key_points = []
        bullet_points = article.find_all(['li', 'p'])
        
        for point in bullet_points:
            text = point.get_text(strip=True)
            if len(text) > 50 and len(text) < 200:  # Reasonable length for a key point
                key_points.append(text)
                if len(key_points) == 3:  # Limit to 3 key points
                    break
        
        return key_points