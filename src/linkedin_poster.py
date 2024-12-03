import os
from linkedin_api import Linkedin
from datetime import datetime

class LinkedInPoster:
    def __init__(self):
        self.username = os.getenv('LINKEDIN_USERNAME')
        self.password = os.getenv('LINKEDIN_PASSWORD')
        self.api = None

    def _connect(self):
        """Initialize LinkedIn API connection"""
        if not self.api:
            if not self.username or not self.password:
                raise ValueError("LinkedIn credentials not found in environment")
            
            try:
                self.api = Linkedin(self.username, self.password)
            except Exception as e:
                raise Exception(f"Failed to connect to LinkedIn: {str(e)}")

    def post(self, content, image_path=None):
        """Post content to LinkedIn"""
        self._connect()

        try:
            # Upload image if provided
            media_id = None
            if image_path and os.path.exists(image_path):
                with open(image_path, 'rb') as image:
                    media_id = self.api.upload_image(image.read())

            # Create post
            self.api.create_post(
                text=content,
                media_id=media_id if media_id else None
            )

        except Exception as e:
            raise Exception(f"Failed to post to LinkedIn: {str(e)}")
