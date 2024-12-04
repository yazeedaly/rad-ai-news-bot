import asyncio
import os
from datetime import datetime
import pytz
from src.aggregator.news_aggregator import NewsAggregator
from src.post_formatter import PostFormatter

async def test_news_gathering():
    """Test news gathering functionality with detailed logging"""
    print('\n=== Testing News Gathering ===')
    
    try:
        # Initialize components
        print('Initializing components...')
        aggregator = NewsAggregator()
        formatter = PostFormatter()
        
        # Test credentials
        print('\nChecking credentials...')
        if os.getenv('MODERN_HEALTHCARE_USERNAME'):
            print('Modern Healthcare username is set')
        if os.getenv('MODERN_HEALTHCARE_PASSWORD'):
            print('Modern Healthcare password is set')
            
        # Gather news
        print('\nGathering news from all sources...')
        news = await aggregator.gather_news()
        
        # Generate test post
        print('\nGenerating post preview...')
        current_date = datetime.now(pytz.timezone('US/Eastern'))
        post_content = formatter.format_post(news, current_date)
        
        # Print results summary
        print('\n=== Results Summary ===')
        print(f"Total sources checked: {len(aggregator.scrapers)}")
        print(f"Radiology AI articles found: {len(news.get('radiology', []))}")
        print(f"Healthcare AI articles found: {len(news.get('healthcare', []))}")
        
        print('\n=== Generated Post Preview ===')
        print(post_content)
        
        return True

    except Exception as e:
        print(f'\nError in news gathering: {str(e)}')
        import traceback
        print(traceback.format_exc())
        return False

if __name__ == "__main__":
    success = asyncio.run(test_news_gathering())
    exit(0 if success else 1)