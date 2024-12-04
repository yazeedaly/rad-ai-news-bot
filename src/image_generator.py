from PIL import Image, ImageDraw, ImageFont
import os
from datetime import datetime

def create_cover_image(date: datetime) -> str:
    """Create a professional cover image for the news update"""
    # Create directory if it doesn't exist
    os.makedirs('images', exist_ok=True)
    
    # Create new image with gradient background
    img = Image.new('RGB', (1200, 630))
    draw = ImageDraw.Draw(img)
    
    # Create gradient background (professional blue)
    for y in range(630):
        color = int(255 * (1 - y/630))  # Gradient from light to darker blue
        draw.line([(0, y), (1200, y)], fill=(color, color + 20, 255))
    
    try:
        # Try to use a professional font
        title_font = ImageFont.truetype('DejaVuSans-Bold.ttf', 60)
        date_font = ImageFont.truetype('DejaVuSans.ttf', 40)
    except:
        # Fallback to default font
        title_font = ImageFont.load_default()
        date_font = ImageFont.load_default()
    
    # Add title
    draw.text(
        (100, 100),
        'Healthcare AI News Update',
        font=title_font,
        fill='white'
    )
    
    # Add date
    draw.text(
        (100, 200),
        date.strftime('%B %d, %Y'),
        font=date_font,
        fill='white'
    )
    
    # Add icons representing different sections
    # (You might want to add small medical/AI-related icons here)
    
    # Save image
    filename = f'images/cover_{date.strftime("%Y%m%d")}.png'
    img.save(filename)
    return filename