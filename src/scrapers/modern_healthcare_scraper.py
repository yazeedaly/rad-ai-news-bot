from .base_scraper import BaseScraper
from bs4 import BeautifulSoup
import aiohttp
import os
import json

class ModernHealthcareScraper(BaseScraper):
    def __init__(self):
        super().__init__(rate_limit=2)
        self.base_url = 'https://www.modernhealthcare.com'
        self.login_url = 'https://www.modernhealthcare.com/api/v1/login'
        self.search_url = 'https://www.modernhealthcare.com/api/v1/search'
        self.username = os.getenv('MODERN_HEALTHCARE_USERNAME')
        self.password = os.getenv('MODERN_HEALTHCARE_PASSWORD')
        self.session = None
        print(f"Initialized {self.__class__.__name__}")

    async def _login(self):
        """Login to Modern Healthcare using their API"""
        if not self.username or not self.password:
            raise ValueError("Modern Healthcare credentials not found")

        login_data = {
            'email': self.username,
            'password': self.password
        }

        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.login_url,
                    json=login_data,
                    headers=headers
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        # Store session cookie for subsequent requests
                        self.session = session
                        print(f"{self.__class__.__name__}: Successfully logged in")
                        return session
                    else:
                        raise Exception(f"Login failed with status {response.status}")
        except Exception as e:
            print(f"Login error: {str(e)}")
            raise

    async def get_articles(self):
        """Fetch articles from Modern Healthcare"""
        print(f"{self.__class__.__name__}: Starting article fetch...")
        try:
            session = await self._login()
            
            # Search for AI-related articles
            search_params = {
                'q': 'artificial intelligence OR machine learning',
                'sort': 'date',
                'from': 0,
                'size': 10
            }
            
            headers = {
                'Accept': 'application/json'
            }

            async with session.get(
                self.search_url,
                params=search_params,
                headers=headers
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    articles = []
                    
                    for hit in data.get('hits', []):
                        articles.append({
                            'title': hit.get('title'),
                            'url': f"{self.base_url}{hit.get('url')}",
                            'published_date': hit.get('date'),
                            'summary': hit.get('description', '')
                        })
                    
                    print(f"{self.__class__.__name__}: Found {len(articles)} articles")
                    return articles[:5]
                else:
                    print(f"Search failed with status {response.status}")
                    return []

        except Exception as e:
            print(f"{self.__class__.__name__}: Error fetching articles - {str(e)}")
            return []

    async def extract_content(self, url):
        """Extract content from a Modern Healthcare article"""
        try:
            if not self.session:
                await self._login()

            async with self.session.get(url) as response:
                if response.status == 200:
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
                else:
                    print(f"Failed to fetch article with status {response.status}")
                    return None

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