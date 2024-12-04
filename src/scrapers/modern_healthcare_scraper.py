from .base_scraper import BaseScraper
from bs4 import BeautifulSoup
import aiohttp
import os

class ModernHealthcareScraper(BaseScraper):
    def __init__(self):
        super().__init__(rate_limit=2)
        self.base_url = 'https://www.modernhealthcare.com'
        self.login_url = 'https://www.modernhealthcare.com/login'
        self.username = os.getenv('MODERN_HEALTHCARE_USERNAME')
        self.password = os.getenv('MODERN_HEALTHCARE_PASSWORD')
        self.session = None
        print(f"Initialized {self.__class__.__name__}")

    async def _login(self):
        """Login to Modern Healthcare"""
        if not self.username or not self.password:
            raise ValueError("Modern Healthcare credentials not found")

        async with aiohttp.ClientSession() as session:
            login_data = {
                'email': self.username,
                'password': self.password
            }
            
            async with session.post(self.login_url, data=login_data) as response:
                if response.status == 200:
                    self.session = session
                    print(f"{self.__class__.__name__}: Successfully logged in")
                else:
                    raise Exception(f"Login failed with status {response.status}")

    async def get_articles(self):
        """Fetch articles from Modern Healthcare"""
        print(f"{self.__class__.__name__}: Starting article fetch...")
        try:
            await self._login()
            articles = []
            # Add specific Modern Healthcare article fetching logic here
            return articles[:5]
        except Exception as e:
            print(f"{self.__class__.__name__}: Error fetching articles - {str(e)}")
            return []

    async def extract_content(self, url):
        """Extract content from a Modern Healthcare article"""
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
        """Extract key takeaways from Modern Healthcare article"""
        takeaways = []
        key_points = article.find_all(['h2', 'strong', 'b'])
        
        for point in key_points[:3]:
            text = point.get_text(strip=True)
            if len(text) > 20:
                takeaways.append(text)
        
        return takeaways