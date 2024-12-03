import asyncio
from datetime import datetime
import pytz
from aggregator.news_aggregator import NewsAggregator
from image_generator import create_cover_image
from linkedin_poster import LinkedInPoster

def format_linkedin_post(news, current_date):
    """Format the news into a LinkedIn post"""
    post = f"🔬 Weekly Radiology AI News Update - {current_date.strftime('%B %d, %Y')}\n\n"
    
    # AI Applications Section
    post += "🏥 Top AI Applications in Healthcare:\n\n"
    for i, article in enumerate(news['applications'], 1):
        post += f"{i}. {article['title']}\n"
        post += f"{article['summary']}\n"
        if article.get('takeaways'):
            post += "Key takeaways:\n"
            for point in article['takeaways']:
                post += f"• {point}\n"
        post += f"Source: {article['source']}\n\n"
    
    # AI Research Section
    post += "🧪 Latest in Radiology AI Research:\n\n"
    for i, article in enumerate(news['research'], 1):
        post += f"{i}. {article['title']}\n"
        post += f"{article['summary']}\n"
        if article.get('takeaways'):
            post += "Key takeaways:\n"
            for point in article['takeaways']:
                post += f"• {point}\n"
        post += f"Source: {article['source']}\n\n"
    
    post += "#RadiologyAI #Healthcare #ArtificialIntelligence #MedicalImaging"
    return post

async def main():
    # Initialize components
    aggregator = NewsAggregator()
    linkedin_poster = LinkedInPoster()

    # Get current date in ET
    et_tz = pytz.timezone('US/Eastern')
    current_date = datetime.now(et_tz)

    try:
        # Gather news
        print("Gathering news...")
        news = await aggregator.gather_news()

        # Generate cover image
        print("Generating cover image...")
        image_path = create_cover_image(current_date)

        # Format post content
        print("Formatting post...")
        post_content = format_linkedin_post(news, current_date)

        # Post to LinkedIn
        print("Posting to LinkedIn...")
        linkedin_poster.post(post_content, image_path)

        print("Successfully posted weekly update")

    except Exception as e:
        print(f"Error in main execution: {str(e)}")
        raise

if __name__ == "__main__":
    asyncio.run(main())