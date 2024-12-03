from PIL import Image, ImageDraw, ImageFont
import os
from datetime import datetime

def create_cover_image(date):
    """Create a professional cover image for the news update"""
    # Create directory if it doesn't exist
    os.makedirs('images', exist_ok=True)
    
    # Create new image with white background
    img = Image.new('RGB', (1200, 630), color='white')
    draw = ImageDraw.Draw(img)
    
    # Load fonts (using default font as fallback)
    try:
        title_font = ImageFont.truetype('DejaVuSans-Bold.ttf', 60)
        date_font = ImageFont.truetype('DejaVuSans.ttf', 40)
    except:
        title_font = ImageFont.load_default()
        date_font = ImageFont.load_default()
    
    # Add gradient background
    for y in range(630):
        color = int(255 * (1 - y/630))  # Gradient from white to light blue
        draw.line([(0, y), (1200, y)], fill=(color, color, 255))
    
    # Add title
    draw.text(
        (100, 100),
        'Weekly Radiology AI News Update',
        font=title_font,
        fill='navy'
    )
    
    # Add date
    draw.text(
        (100, 200),
        date.strftime('%B %d, %Y'),
        font=date_font,
        fill='navy'
    )
    
    # Save image
    filename = f'images/cover_{date.strftime("%Y%m%d")}.png'
    img.save(filename)
    return filename