import feedparser
from .base_scraper import BaseScraper
from bs4 import BeautifulSoup

class AuntMinnieScraper(BaseScraper):
    def __init__(self):
        super().__init__(rate_limit=2)
        self.feed_url = 'https://www.auntminnie.com/rss/channels/all'
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
                if self._is_ai_related(entry):
                    articles.append({
                        'title': entry.title,
                        'url': entry.link,
                        'published_date': entry.get('published'),
                        'summary': entry.get('summary', '')
                    })
            
            print(f"{self.__class__.__name__}: Found {len(articles)} AI-related articles")
            return articles[:5]  # Return top 5 articles

        except Exception as e:
            print(f"{self.__class__.__name__}: Error fetching articles - {str(e)}")
            return []

    async def extract_content(self, url):
        """Extract content from an article URL"""
        try:
            content = await self._make_request(url)
            soup = BeautifulSoup(content, 'html.parser')
            
            # Find the main article content
            article = soup.find('article') or soup.find('div', class_='article-content')
            if not article:
                return None

            # Extract text content
            text = article.get_text(strip=True)
            
            # Extract key points/takeaways
            takeaways = []
            key_points = article.find_all(['h2', 'strong', 'b']) 
            for point in key_points[:3]:  # Limit to top 3 points
                if point.text.strip():
                    takeaways.append(point.text.strip())

            return {
                'text': text,
                'takeaways': takeaways
            }
            
        except Exception as e:
            print(f"Error extracting content from {url}: {str(e)}")
            return None

    def _is_ai_related(self, entry):
        """Check if article is AI-related based on keywords"""
        keywords = ['artificial intelligence', 'AI', 'machine learning', 'deep learning',
                   'neural network', 'algorithm', 'computer-aided']
        text = (entry.title + ' ' + entry.get('summary', '')).lower()
        return any(keyword.lower() in text for keyword in keywords)