import asyncio
import os
from datetime import datetime
import pytz
from src.aggregator.news_aggregator import NewsAggregator
from src.post_formatter import PostFormatter

async def test_news_gathering():
    """Test news gathering functionality"""
    print('\n=== Testing News Gathering ===')
    
    try:
        aggregator = NewsAggregator()
        news = await aggregator.gather_news()
        
        # Create test post
        formatter = PostFormatter()
        current_date = datetime.now(pytz.timezone('US/Eastern'))
        post_content = formatter.format_post(news, current_date)
        
        print('\n=== Generated Post Preview ===')
        print(post_content)
        
        return True

    except Exception as e:
        print(f'Error in news gathering: {str(e)}')
        import traceback
        print(traceback.format_exc())
        return False

if __name__ == "__main__":
    success = asyncio.run(test_news_gathering())
    exit(0 if success else 1)