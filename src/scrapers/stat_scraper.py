from .base_scraper import BaseScraper
from bs4 import BeautifulSoup
import aiohttp
import os

class StatScraper(BaseScraper):
    def __init__(self):
        super().__init__(rate_limit=2)
        self.base_url = 'https://www.statnews.com'
        self.login_url = 'https://www.statnews.com/login'
        self.username = os.getenv('STAT_USERNAME')
        self.password = os.getenv('STAT_PASSWORD')
        self.session = None
        print(f"Initialized {self.__class__.__name__}")

    async def _login(self):
        """Login to STAT+"""
        if not self.username or not self.password:
            raise ValueError("STAT+ credentials not found")

        async with aiohttp.ClientSession() as session:
            # Get CSRF token
            async with session.get(self.login_url) as response:
                text = await response.text()
                soup = BeautifulSoup(text, 'html.parser')
                csrf_token = soup.find('input', {'name': 'csrf_token'})['value']

            # Login
            login_data = {
                'username': self.username,
                'password': self.password,
                'csrf_token': csrf_token
            }
            async with session.post(self.login_url, data=login_data) as response:
                if response.status == 200:
                    self.session = session
                    print(f"{self.__class__.__name__}: Successfully logged in")
                else:
                    raise Exception(f"Login failed with status {response.status}")

    async def get_articles(self):
        """Fetch articles from STAT+"""
        print(f"{self.__class__.__name__}: Starting article fetch...")
        try:
            await self._login()
            articles = []
            # Add specific STAT+ article fetching logic here
            return articles[:5]
        except Exception as e:
            print(f"{self.__class__.__name__}: Error fetching articles - {str(e)}")
            return []

    async def extract_content(self, url):
        """Extract content from a STAT+ article"""
        try:
            if not self.session:
                await self._login()
            
            async with self.session.get(url) as response:
                text = await response.text()
                soup = BeautifulSoup(text, 'html.parser')
                
                article = soup.find('article')
                if not article:
                    return None

                content = article.get_text(strip=True)
                takeaways = self._extract_takeaways(article)

                return {
                    'text': content,
                    'takeaways': takeaways
                }

        except Exception as e:
            print(f"Error extracting content from {url}: {str(e)}")
            return None

    def _extract_takeaways(self, article):
        """Extract key takeaways from STAT+ article"""
        takeaways = []
        key_points = article.find_all(['h2', 'strong', 'em'])
        
        for point in key_points[:3]:
            text = point.get_text(strip=True)
            if len(text) > 20:
                takeaways.append(text)
        
        return takeaways