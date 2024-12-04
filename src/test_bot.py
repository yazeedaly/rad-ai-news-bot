import asyncio
import os
from datetime import datetime
import pytz
from aggregator.news_aggregator import NewsAggregator
from image_generator import create_cover_image
from linkedin_poster import LinkedInPoster

def print_debug(message):
    """Print debug message if debug mode is enabled"""
    if os.getenv('DEBUG_MODE', 'false').lower() == 'true':
        print(f'[DEBUG] {message}')

async def test_news_gathering():
    """Test news gathering functionality"""
    print('\n=== Testing News Gathering ===')
    aggregator = NewsAggregator()
    
    try:
        news = await aggregator.gather_news()
        print('✓ Successfully gathered news')
        
        # Print gathered news details
        print(f'\nFound {len(news["applications"])} application articles')
        print(f'Found {len(news["research"])} research articles')
        
        # Print article details if in debug mode
        for category, articles in news.items():
            print_debug(f'\n{category.upper()} ARTICLES:')
            for i, article in enumerate(articles, 1):
                print_debug(f'{i}. {article["title"]}')
                print_debug(f'   Source: {article["source"]}')
                print_debug(f'   Relevance: {article["relevance_scores"]["combined"]:.2f}')
        
        return news
    except Exception as e:
        print(f'✗ Error gathering news: {str(e)}')
        raise

def test_image_generation():
    """Test cover image generation"""
    print('\n=== Testing Image Generation ===')
    current_date = datetime.now(pytz.timezone('US/Eastern'))
    
    try:
        image_path = create_cover_image(current_date)
        print(f'✓ Successfully generated image: {image_path}')
        return image_path
    except Exception as e:
        print(f'✗ Error generating image: {str(e)}')
        raise

def test_linkedin_connection():
    """Test LinkedIn API connection"""
    print('\n=== Testing LinkedIn Connection ===')
    poster = LinkedInPoster()
    
    try:
        poster._connect()
        print('✓ Successfully connected to LinkedIn')
    except Exception as e:
        print(f'✗ Error connecting to LinkedIn: {str(e)}')
        raise

def format_test_post(news, current_date):
    """Format post content for testing"""
    post = f"[TEST] Weekly Radiology AI News Update - {current_date.strftime('%B %d, %Y')}\n\n"
    
    # Add application news
    post += "AI Applications in Healthcare:\n"
    for i, article in enumerate(news['applications'][:2], 1):  # Only include first 2 for test
        post += f"{i}. {article['title']}\n"
        if article.get('takeaways'):
            post += f"   Key point: {article['takeaways'][0]}\n"
    
    # Add research news
    post += "\nRadiology AI Research:\n"
    for i, article in enumerate(news['research'][:2], 1):  # Only include first 2 for test
        post += f"{i}. {article['title']}\n"
        if article.get('takeaways'):
            post += f"   Key point: {article['takeaways'][0]}\n"
    
    post += "\n[TEST POST - Please ignore]"
    return post

async def main():
    try:
        # Test news gathering
        news = await test_news_gathering()
        
        # Test image generation
        image_path = test_image_generation()
        
        # Test LinkedIn connection
        test_linkedin_connection()
        
        # Test post formatting
        current_date = datetime.now(pytz.timezone('US/Eastern'))
        post_content = format_test_post(news, current_date)
        print('\n=== Test Post Preview ===')
        print(post_content)
        
        # Test posting if not skipped
        if os.getenv('SKIP_POSTING', 'true').lower() != 'true':
            print('\n=== Testing LinkedIn Posting ===')
            poster = LinkedInPoster()
            poster.post(post_content, image_path)
            print('✓ Successfully posted to LinkedIn')
        else:
            print('\n=== Skipping LinkedIn Posting ===')
            print('ℹ Set SKIP_POSTING=false to test posting')
        
        print('\n✅ All tests completed successfully!')
        
    except Exception as e:
        print(f'\n❌ Test failed: {str(e)}')
        raise

if __name__ == "__main__":
    asyncio.run(main())