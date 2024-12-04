from datetime import datetime
from typing import Dict, List

class PostFormatter:
    def __init__(self):
        self.max_takeaways = 3
        self.max_summary_length = 300

    def format_post(self, news: Dict[str, List[Dict]], current_date: datetime) -> str:
        """Format news into a LinkedIn post"""
        # Header
        post = f"📰 Healthcare AI News Update - {current_date.strftime('%B %d, %Y')}\n\n"

        # Radiology AI Section
        post += "🔬 Radiology AI Highlights:\n\n"
        if news['radiology']:
            post += self._format_articles(news['radiology'])
        else:
            post += "No major radiology AI updates this week.\n\n"

        # Healthcare AI Section
        post += "🏥 Healthcare AI Innovations:\n\n"
        if news['healthcare']:
            post += self._format_articles(news['healthcare'])
        else:
            post += "No major healthcare AI updates this week.\n\n"

        # Add hashtags
        post += self._get_hashtags()
        return post

    def _format_articles(self, articles: List[Dict]) -> str:
        """Format a list of articles"""
        formatted = ""
        for i, article in enumerate(articles, 1):
            # Title and source
            formatted += f"{i}. {article['title']}\n"
            formatted += f"Source: {article['source']}\n"

            # Summary (if available)
            if 'summary' in article:
                summary = article['summary']
                if len(summary) > self.max_summary_length:
                    summary = summary[:self.max_summary_length] + '...'
                formatted += f"{summary}\n"

            # Key takeaways (if available)
            if article.get('takeaways'):
                formatted += "Key takeaways:\n"
                for takeaway in article['takeaways'][:self.max_takeaways]:
                    formatted += f"• {takeaway}\n"

            formatted += "\n"
        return formatted

    def _get_hashtags(self) -> str:
        """Generate relevant hashtags"""
        return (
            "#HealthcareAI #RadiologyAI #ArtificialIntelligence "
            "#HealthTech #DigitalHealth #MedicalImaging #Healthcare "
            "#Innovation #AI #Radiology"
        )