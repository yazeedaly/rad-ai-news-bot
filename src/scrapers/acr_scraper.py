from .base_scraper import BaseScraper
from bs4 import BeautifulSoup
from datetime import datetime
import re

class ACRScraper(BaseScraper):
    def __init__(self):
        super().__init__(rate_limit=2)
        self.base_url = 'https://www.acr.org'
        self.news_url = 'https://www.acr.org/News'
        self.ai_lab_url = 'https://www.acr.org/Research/ACR-AI-LAB'
        self.advocacy_url = 'https://www.acr.org/Advocacy/AI-Central'
        print(f"Initialized {self.__class__.__name__}")

    async def get_articles(self):
        """Fetch articles from ACR website"""
        print(f"{self.__class__.__name__}: Starting article fetch...")
        articles = []

        try:
            # Fetch general news
            news_articles = await self._fetch_news_articles()
            articles.extend(news_articles)

            # Fetch AI Lab updates
            ai_lab_articles = await self._fetch_ai_lab_content()
            articles.extend(ai_lab_articles)

            # Fetch AI advocacy updates
            advocacy_articles = await self._fetch_advocacy_content()
            articles.extend(advocacy_articles)

            print(f"{self.__class__.__name__}: Found total of {len(articles)} articles")
            
            # Sort by date and return most recent
            articles.sort(key=lambda x: x.get('published_date', ''), reverse=True)
            return articles[:5]

        except Exception as e:
            print(f"{self.__class__.__name__}: Error fetching articles - {str(e)}")
            return []

    async def _fetch_news_articles(self):
        """Fetch articles from ACR news section"""
        articles = []
        try:
            content = await self._make_request(self.news_url)
            soup = BeautifulSoup(content, 'html.parser')

            # Find all news items
            news_items = soup.find_all('div', class_='news-item')
            for item in news_items:
                try:
                    # Check if AI/ML related
                    text = item.get_text().lower()
                    if any(keyword in text for keyword in ['artificial intelligence', 'ai', 'machine learning', 'deep learning', 'algorithm']):
                        title_elem = item.find('h2') or item.find('h3')
                        link_elem = item.find('a')
                        date_elem = item.find('span', class_='date')

                        if title_elem and link_elem:
                            url = link_elem.get('href')
                            if not url.startswith('http'):
                                url = self.base_url + url

                            articles.append({
                                'title': title_elem.get_text(strip=True),
                                'url': url,
                                'published_date': self._parse_date(date_elem.get_text(strip=True)) if date_elem else None,
                                'summary': self._extract_summary(item),
                                'source': 'ACR News'
                            })

                except Exception as e:
                    print(f"Error processing news item: {str(e)}")
                    continue

        except Exception as e:
            print(f"Error fetching news articles: {str(e)}")

        return articles

    async def _fetch_ai_lab_content(self):
        """Fetch content from ACR AI-LAB section"""
        articles = []
        try:
            content = await self._make_request(self.ai_lab_url)
            soup = BeautifulSoup(content, 'html.parser')

            # Find AI-LAB updates and announcements
            updates = soup.find_all(['div', 'section'], class_=['update', 'announcement'])
            for update in updates:
                try:
                    title_elem = update.find(['h2', 'h3', 'h4'])
                    if title_elem:
                        articles.append({
                            'title': title_elem.get_text(strip=True),
                            'url': self.ai_lab_url,
                            'summary': self._extract_summary(update),
                            'source': 'ACR AI-LAB'
                        })

                except Exception as e:
                    print(f"Error processing AI-LAB update: {str(e)}")
                    continue

        except Exception as e:
            print(f"Error fetching AI-LAB content: {str(e)}")

        return articles

    async def _fetch_advocacy_content(self):
        """Fetch content from ACR AI Central advocacy section"""
        articles = []
        try:
            content = await self._make_request(self.advocacy_url)
            soup = BeautifulSoup(content, 'html.parser')

            # Find advocacy updates
            updates = soup.find_all(['div', 'article'], class_=['policy-update', 'advocacy-item'])
            for update in updates:
                try:
                    title_elem = update.find(['h2', 'h3', 'h4'])
                    if title_elem:
                        articles.append({
                            'title': title_elem.get_text(strip=True),
                            'url': self.advocacy_url,
                            'summary': self._extract_summary(update),
                            'source': 'ACR AI Central'
                        })

                except Exception as e:
                    print(f"Error processing advocacy update: {str(e)}")
                    continue

        except Exception as e:
            print(f"Error fetching advocacy content: {str(e)}")

        return articles

    def _extract_summary(self, element):
        """Extract a summary from the element"""
        # Try to find a dedicated summary/description element
        summary_elem = element.find(['p', 'div'], class_=['summary', 'description', 'excerpt'])
        if summary_elem:
            return summary_elem.get_text(strip=True)

        # Otherwise, use the first paragraph
        first_p = element.find('p')
        if first_p:
            return first_p.get_text(strip=True)

        return ''

    def _parse_date(self, date_str):
        """Parse date string into standard format"""
        try:
            # Handle various ACR date formats
            date_formats = [
                '%B %d, %Y',
                '%m/%d/%Y',
                '%Y-%m-%d'
            ]
            
            for fmt in date_formats:
                try:
                    return datetime.strptime(date_str.strip(), fmt).strftime('%Y-%m-%d')
                except:
                    continue

            return None
        except:
            return None

    async def extract_content(self, url):
        """Extract content from an ACR article"""
        try:
            content = await self._make_request(url)
            soup = BeautifulSoup(content, 'html.parser')

            # Find article content
            article = soup.find(['article', 'div'], class_=['article', 'content', 'news-content'])
            if not article:
                return None

            # Extract text content
            text = article.get_text(strip=True)

            # Extract key takeaways
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

        # Look for key points in various formats
        key_elements = article.find_all(['h2', 'h3', 'strong', 'b', 
                                       'div', 'p'], class_=['key-point', 'highlight'])

        # Also look for bullet points
        bullet_points = article.find_all('li')

        # Process key elements
        for elem in key_elements:
            text = elem.get_text(strip=True)
            if len(text) > 20 and len(text) < 200:
                takeaways.append(text)
                if len(takeaways) == 3:
                    break

        # If we don't have enough takeaways, check bullet points
        if len(takeaways) < 3:
            for point in bullet_points:
                text = point.get_text(strip=True)
                if len(text) > 20 and len(text) < 200:
                    takeaways.append(text)
                    if len(takeaways) == 3:
                        break

        return takeaways