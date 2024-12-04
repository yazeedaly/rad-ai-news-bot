from .base_scraper import BaseScraper
from bs4 import BeautifulSoup
from datetime import datetime
import re

class ACRScraper(BaseScraper):
    def __init__(self):
        super().__init__(rate_limit=2)
        self.base_url = 'https://www.acr.org'
        self.news_endpoints = [
            '/Media-Center/ACR-News-Releases',
            '/Practice-Management-Quality-Informatics/Artificial-Intelligence',
            '/Clinical-Resources/Informatics',
            '/Research/AI-LAB/News'
        ]
        print(f"Initialized {self.__class__.__name__}")

    async def get_articles(self):
        """Fetch articles from ACR website"""
        print(f"{self.__class__.__name__}: Starting article fetch...")
        all_articles = []

        for endpoint in self.news_endpoints:
            try:
                url = f"{self.base_url}{endpoint}"
                content = await self._make_request(url)
                soup = BeautifulSoup(content, 'html.parser')

                # Find content area
                content_area = soup.find('div', class_=['content', 'main-content', 'news-listing'])
                if not content_area:
                    continue

                # Look for articles/news items in different formats
                articles = content_area.find_all(['article', 'div'], class_=[
                    'news-item', 'list-item', 'content-item', 'media-item'
                ])

                for article in articles:
                    try:
                        # Find title and link
                        title_elem = article.find(['h2', 'h3', 'h4', 'a'], class_=['title', 'heading'])
                        if not title_elem:
                            continue

                        title = title_elem.get_text(strip=True)
                        
                        # Get link
                        link = None
                        if title_elem.name == 'a':
                            link = title_elem['href']
                        else:
                            link_elem = title_elem.find('a')
                            if link_elem:
                                link = link_elem['href']

                        if not link:
                            continue

                        # Make link absolute
                        if not link.startswith('http'):
                            link = f"{self.base_url}{link}"

                        # Check if AI-related
                        if self._is_ai_related(title):
                            # Get date if available
                            date_elem = article.find(['time', 'span'], class_=['date', 'timestamp'])
                            pub_date = date_elem.get_text(strip=True) if date_elem else None

                            # Get summary/description
                            summary_elem = article.find(['p', 'div'], class_=['summary', 'description', 'excerpt'])
                            summary = summary_elem.get_text(strip=True) if summary_elem else ''

                            all_articles.append({
                                'title': title,
                                'url': link,
                                'published_date': pub_date,
                                'summary': summary,
                                'source': 'ACR News'
                            })

                    except Exception as e:
                        print(f"Error processing ACR article: {str(e)}")
                        continue

            except Exception as e:
                print(f"Error fetching ACR endpoint {endpoint}: {str(e)}")
                continue

        print(f"{self.__class__.__name__}: Found {len(all_articles)} articles")
        return all_articles[:5]

    def _is_ai_related(self, text):
        """Check if content is AI-related"""
        ai_terms = [
            'artificial intelligence', 'ai', 'machine learning', 'deep learning',
            'neural network', 'algorithm', 'automation', 'computer-aided',
            'ai lab', 'data science'
        ]
        text = text.lower()
        return any(term in text for term in ai_terms)

    async def extract_content(self, url):
        """Extract content from an ACR article"""
        try:
            content = await self._make_request(url)
            soup = BeautifulSoup(content, 'html.parser')

            # Find article content
            article = soup.find(['article', 'div'], class_=['article', 'content', 'news-content'])
            if not article:
                return None

            # Get main content
            text = article.get_text(strip=True)

            # Extract key points
            takeaways = []

            # Look for highlighted sections
            highlights = article.find_all(['h2', 'h3', 'strong', 'b'])
            for highlight in highlights:
                point = highlight.get_text(strip=True)
                if len(point) > 20 and len(point) < 200:
                    takeaways.append(point)
                    if len(takeaways) == 3:
                        break

            # If no highlights found, use first few paragraphs
            if not takeaways:
                paragraphs = article.find_all('p')
                for p in paragraphs[:3]:
                    text = p.get_text(strip=True)
                    if len(text) > 20:
                        takeaways.append(text)

            return {
                'text': text,
                'takeaways': takeaways
            }

        except Exception as e:
            print(f"Error extracting content from {url}: {str(e)}")
            return None