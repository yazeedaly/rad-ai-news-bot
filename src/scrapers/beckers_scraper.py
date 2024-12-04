import feedparser
from .base_scraper import BaseScraper
from bs4 import BeautifulSoup

class BeckersScraper(BaseScraper):
    def __init__(self):
        super().__init__(rate_limit=2)
        self.feed_url = 'https://www.beckershospitalreview.com/rss/healthcare-information-technology.xml'
        print(f"Initialized {self.__class__.__name__} with feed URL: {self.feed_url}")

    async def get_articles(self):
        """Fetch articles asynchronously"""
        print(f"{self.__class__.__name__}: Starting article fetch...")
        try:
            content = await self._make_request(self.feed_url)
            feed = feedparser.parse(content)
            print(f"{self.__class__.__name__}: Found {len(feed.entries)} entries in feed")
            
            articles = []
            for entry in feed.entries:
                if self._is_radiology_ai_related(entry):
                    articles.append({
                        'title': entry.title,
                        'url': entry.link,
                        'published_date': entry.get('published'),
                        'summary': entry.get('summary', '')
                    })
            
            print(f"{self.__class__.__name__}: Found {len(articles)} AI-related articles")
            return articles[:5]

        except Exception as e:
            print(f"{self.__class__.__name__}: Error fetching articles - {str(e)}")
            return []

    async def extract_content(self, url):
        """Extract content from an article URL"""
        try:
            content = await self._make_request(url)
            soup = BeautifulSoup(content, 'html.parser')
            
            article = soup.find('article')
            if not article:
                return None

            # Extract text content
            text = article.get_text(strip=True)
            
            # Extract key points
            takeaways = []
            points = article.find_all(['li', 'p'])
            for point in points:
                text = point.get_text(strip=True)
                if len(text) > 50 and len(text) < 200:  # Reasonable length for a key point
                    takeaways.append(text)
                    if len(takeaways) == 3:  # Limit to 3 key points
                        break

            return {
                'text': text,
                'takeaways': takeaways
            }
            
        except Exception as e:
            print(f"Error extracting content from {url}: {str(e)}")
            return None

    def _is_radiology_ai_related(self, entry):
        """Check if article is related to radiology and AI"""
        rad_keywords = ['radiology', 'imaging', 'radiologist', 'x-ray', 'CT', 'MRI']
        ai_keywords = ['artificial intelligence', 'AI', 'machine learning', 'deep learning']
        
        text = (entry.title + ' ' + entry.get('summary', '')).lower()
        has_rad = any(keyword.lower() in text for keyword in rad_keywords)
        has_ai = any(keyword.lower() in text for keyword in ai_keywords)
        
        return has_rad and has_ai