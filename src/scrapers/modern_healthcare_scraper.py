from .base_scraper import BaseScraper
from bs4 import BeautifulSoup
import aiohttp
import os
import json

class ModernHealthcareScraper(BaseScraper):
    def __init__(self):
        super().__init__(rate_limit=2)
        self.base_url = 'https://www.modernhealthcare.com'
        self.login_url = 'https://www.modernhealthcare.com/user/login'
        self.search_url = 'https://www.modernhealthcare.com/search'
        self.username = os.getenv('MODERN_HEALTHCARE_USERNAME')
        self.password = os.getenv('MODERN_HEALTHCARE_PASSWORD')
        self.session = None
        print(f"Initialized {self.__class__.__name__}")

    async def _login(self):
        """Login to Modern Healthcare using form-based authentication"""
        if not self.username or not self.password:
            raise ValueError("Modern Healthcare credentials not found")

        try:
            # Create a persistent session
            if not self.session:
                self.session = aiohttp.ClientSession()

            # First get the login page to get any CSRF token
            async with self.session.get(self.login_url) as response:
                if response.status != 200:
                    raise Exception(f"Failed to get login page: {response.status}")
                text = await response.text()
                soup = BeautifulSoup(text, 'html.parser')
                
                # Find the login form and extract any hidden fields
                form = soup.find('form', {'id': 'user-login-form'})
                if not form:
                    raise Exception("Login form not found")
                
                # Build login data including any hidden fields
                login_data = {
                    'name': self.username,
                    'pass': self.password,
                    'form_id': 'user_login_form'
                }
                
                # Add any hidden fields from the form
                for hidden in form.find_all('input', type='hidden'):
                    login_data[hidden.get('name')] = hidden.get('value', '')

            # Submit login form
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded',
                'Referer': self.login_url
            }
            
            async with self.session.post(
                self.login_url,
                data=login_data,
                headers=headers,
                allow_redirects=True
            ) as response:
                if response.status == 200:
                    print(f"{self.__class__.__name__}: Successfully logged in")
                    return self.session
                else:
                    raise Exception(f"Login failed with status {response.status}")

        except Exception as e:
            print(f"Login error: {str(e)}")
            if self.session:
                await self.session.close()
            raise

    async def get_articles(self):
        """Fetch articles from Modern Healthcare"""
        print(f"{self.__class__.__name__}: Starting article fetch...")
        try:
            session = await self._login()
            
            # Search for AI-related articles
            params = {
                'q': 'artificial intelligence',
                'sort': 'date',
                'date_range': 'last_week'
            }
            
            async with session.get(self.search_url, params=params) as response:
                if response.status == 200:
                    text = await response.text()
                    soup = BeautifulSoup(text, 'html.parser')
                    
                    articles = []
                    for article in soup.find_all('article', class_='search-result'):
                        title_elem = article.find('h2')
                        if title_elem and title_elem.find('a'):
                            articles.append({
                                'title': title_elem.text.strip(),
                                'url': f"{self.base_url}{title_elem.find('a')['href']}",
                                'published_date': article.find('time').get('datetime') if article.find('time') else None,
                                'summary': article.find('p', class_='summary').text.strip() if article.find('p', class_='summary') else ''
                            })
                    
                    print(f"{self.__class__.__name__}: Found {len(articles)} articles")
                    return articles[:5]
                else:
                    print(f"Search failed with status {response.status}")
                    return []

        except Exception as e:
            print(f"{self.__class__.__name__}: Error fetching articles - {str(e)}")
            return []
        finally:
            if self.session:
                await self.session.close()
                self.session = None

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
        finally:
            if self.session:
                await self.session.close()
                self.session = None

    def _extract_takeaways(self, article):
        """Extract key takeaways from Modern Healthcare article"""
        takeaways = []
        key_points = article.find_all(['h2', 'strong', 'b'])
        
        for point in key_points[:3]:
            text = point.get_text(strip=True)
            if len(text) > 20:
                takeaways.append(text)
        
        return takeaways